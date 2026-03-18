"""
Wrapper per whisper-cli: preprocessing audio → split in chunk → trascrizione.

Pipeline:
1. Preprocessing: highpass + lowpass + denoise + loudnorm → WAV 16kHz mono
2. Split in chunk da ~15 min (evita loop whisper su audio lunghi)
3. Trascrizione chunk per chunk con whisper-cli
4. Concatenazione VTT e TXT
5. Rilevamento loop e ri-trascrizione automatica dei segmenti corrotti
   - Tentativo locale (whisper-cli con parametri aggressivi) x2
   - Fallback cloud: Groq Whisper API (turbo, poi v3)
"""

import json
import os
import re
import subprocess
import urllib.request
import urllib.error
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
DEFAULT_MODEL = PROJECT_ROOT / "models" / "ggml-large-v3.bin"
FALLBACK_MODEL = PROJECT_ROOT / "models" / "ggml-medium.bin"

CHUNK_DURATION_S = 900  # 15 minuti per chunk
RETRY_CHUNK_S = 300  # 5 minuti per ri-trascrizione dei loop
MAX_RETRIES = 2  # tentativi locali per ogni loop

# Groq Whisper API
GROQ_API_URL = "https://api.groq.com/openai/v1/audio/transcriptions"
GROQ_MODELS = ["whisper-large-v3-turbo", "whisper-large-v3"]
GROQ_MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 MB (dev tier)


def preprocess_audio(input_path: Path, output_path: Path) -> Path:
    """Preprocessing audio: filtri + normalizzazione → WAV 16kHz mono."""
    cmd = [
        "ffmpeg", "-y",
        "-i", str(input_path),
        "-af", "highpass=f=200,lowpass=f=3000,afftdn=nf=-25,loudnorm",
        "-ar", "16000",
        "-ac", "1",
        "-c:a", "pcm_s16le",
        str(output_path),
    ]
    print(f"[transcribe] Preprocessing {input_path.name} (filtri + normalizzazione)...")
    subprocess.run(cmd, check=True, capture_output=True)
    return output_path


def get_audio_duration(wav_path: Path) -> float:
    """Restituisce la durata in secondi di un file audio."""
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(wav_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return float(result.stdout.strip())


def split_audio(wav_path: Path, output_dir: Path, chunk_duration: int = CHUNK_DURATION_S) -> list[Path]:
    """Splitta l'audio in chunk. Restituisce lista di path ordinati."""
    duration = get_audio_duration(wav_path)
    if duration <= chunk_duration * 1.2:  # margine 20% — non splittare se poco più lungo
        return [wav_path]

    n_chunks = int(duration // chunk_duration) + (1 if duration % chunk_duration > 0 else 0)
    print(f"[transcribe] Audio {duration/60:.0f} min → {n_chunks} chunk da ~{chunk_duration//60} min")

    chunks = []
    for i in range(n_chunks):
        start = i * chunk_duration
        chunk_path = output_dir / f"chunk_{i+1:02d}.wav"
        cmd = [
            "ffmpeg", "-y",
            "-i", str(wav_path),
            "-ss", str(start),
            "-t", str(chunk_duration),
            "-c:a", "copy",
            str(chunk_path),
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        chunks.append(chunk_path)

    return chunks


def transcribe_chunk(
    wav_path: Path,
    output_base: Path,
    model_path: Path,
    language: str,
    initial_prompt: str | None,
) -> tuple[Path, Path]:
    """Trascrive un singolo chunk. Restituisce (vtt_path, txt_path)."""
    cmd = [
        "whisper-cli",
        "-m", str(model_path),
        "-l", language,
        "-ovtt",
        "-otxt",
        "-of", str(output_base),
        "--no-prints",
        # Anti-loop: soglia entropia più bassa per rilevare ripetizioni
        "--entropy-thold", "2.0",
        # best-of già default 5, beam-size default 5
    ]
    if initial_prompt:
        cmd.extend(["--prompt", initial_prompt])
    cmd.append(str(wav_path))

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"whisper-cli fallito su {wav_path.name}:\n{result.stderr}")

    vtt_path = Path(str(output_base) + ".vtt")
    txt_path = Path(str(output_base) + ".txt")
    return vtt_path, txt_path


def concat_txt(txt_paths: list[Path], output_path: Path) -> Path:
    """Concatena i file TXT dei chunk."""
    parts = []
    for p in txt_paths:
        if p.exists():
            parts.append(p.read_text(encoding="utf-8").strip())
    output_path.write_text("\n".join(parts), encoding="utf-8")
    return output_path


def concat_vtt(vtt_paths: list[Path], output_path: Path, chunk_duration: int = CHUNK_DURATION_S) -> Path:
    """Concatena i file VTT dei chunk, aggiustando i timestamp."""
    lines = ["WEBVTT", ""]
    for i, vtt_path in enumerate(vtt_paths):
        if not vtt_path.exists():
            continue
        offset_s = i * chunk_duration
        for line in vtt_path.read_text(encoding="utf-8").splitlines():
            if line.strip() == "WEBVTT" or not line.strip():
                continue
            if "-->" in line:
                line = _offset_vtt_timestamp_line(line, offset_s)
            lines.append(line)
        lines.append("")

    output_path.write_text("\n".join(lines), encoding="utf-8")
    return output_path


def _offset_vtt_timestamp_line(line: str, offset_s: int) -> str:
    """Aggiunge offset ai timestamp VTT (HH:MM:SS.mmm --> HH:MM:SS.mmm)."""
    parts = line.split("-->")
    if len(parts) != 2:
        return line
    start = _offset_ts(parts[0].strip(), offset_s)
    end = _offset_ts(parts[1].strip(), offset_s)
    return f"{start} --> {end}"


def _offset_ts(ts: str, offset_s: int) -> str:
    """Aggiunge secondi a un timestamp VTT."""
    # Formato: HH:MM:SS.mmm o MM:SS.mmm
    parts = ts.split(":")
    if len(parts) == 3:
        h, m, rest = int(parts[0]), int(parts[1]), parts[2]
    elif len(parts) == 2:
        h, m, rest = 0, int(parts[0]), parts[1]
    else:
        return ts

    s_parts = rest.split(".")
    s = int(s_parts[0])
    ms = s_parts[1] if len(s_parts) > 1 else "000"

    total_s = h * 3600 + m * 60 + s + offset_s
    new_h = total_s // 3600
    new_m = (total_s % 3600) // 60
    new_s = total_s % 60

    return f"{new_h:02d}:{new_m:02d}:{new_s:02d}.{ms}"


# --- Loop detection and retranscription ---

def _parse_ts_seconds(ts: str) -> float:
    """Converte un timestamp VTT (HH:MM:SS.mmm) in secondi."""
    parts = ts.strip().split(":")
    if len(parts) == 3:
        h, m, rest = int(parts[0]), int(parts[1]), parts[2]
    elif len(parts) == 2:
        h, m, rest = 0, int(parts[0]), parts[1]
    else:
        return 0.0
    s_parts = rest.split(".")
    s = int(s_parts[0])
    ms = int(s_parts[1]) if len(s_parts) > 1 else 0
    return h * 3600 + m * 60 + s + ms / 1000


def _parse_vtt_entries(vtt_text: str) -> list[dict]:
    """Parsa un VTT in lista di {start_s, end_s, text, raw_ts}."""
    entries = []
    lines = vtt_text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if "-->" in line:
            parts = line.split("-->")
            start_s = _parse_ts_seconds(parts[0])
            end_s = _parse_ts_seconds(parts[1])
            text_lines = []
            i += 1
            while i < len(lines) and lines[i].strip() and "-->" not in lines[i]:
                text_lines.append(lines[i].strip())
                i += 1
            entries.append({
                "start_s": start_s,
                "end_s": end_s,
                "text": " ".join(text_lines),
                "raw_ts": line,
            })
        else:
            i += 1
    return entries


def _detect_loop_ranges(entries: list[dict], min_repeat: int = 3) -> list[tuple[float, float, int, int]]:
    """Rileva i range temporali dei loop nel VTT.

    Usa la stessa logica di correct.py ma opera sugli entry VTT per estrarre i timestamp.

    Returns:
        Lista di (start_seconds, end_seconds, entry_idx_start, entry_idx_end)
    """
    def normalize(text: str) -> str:
        t = text.lower().strip()
        t = re.sub(r"[^\w\s]", "", t)
        t = re.sub(r"\s+", " ", t)
        return t

    def similarity(a: str, b: str) -> float:
        wa, wb = set(a.split()), set(b.split())
        if not wa or not wb:
            return 0.0
        return len(wa & wb) / max(len(wa), len(wb))

    def is_intra_loop(norm_text: str) -> bool:
        words = norm_text.split()
        if len(words) < min_repeat * 2:
            return False
        for plen in range(2, min(9, len(words) // min_repeat + 1)):
            pattern = " ".join(words[:plen])
            if not pattern:
                continue
            count = 0
            pos = 0
            full = " ".join(words)
            while True:
                idx = full.find(pattern, pos)
                if idx == -1:
                    break
                count += 1
                pos = idx + len(pattern)
            if count >= min_repeat and (count * plen) / len(words) > 0.6:
                return True
        return False

    loop_entries = set()

    # Check 1: entry consecutive identiche
    i = 0
    while i < len(entries):
        norm = normalize(entries[i]["text"])
        if not norm:
            i += 1
            continue
        j = i + 1
        count = 1
        while j < len(entries):
            next_norm = normalize(entries[j]["text"])
            if not next_norm:
                j += 1
                continue
            if next_norm == norm or similarity(norm, next_norm) > 0.85:
                count += 1
                j += 1
            else:
                break
        if count >= min_repeat:
            for k in range(i, j):
                loop_entries.add(k)
        i = j if count >= min_repeat else i + 1

    # Check 2: pattern multi-entry
    for pattern_len in range(2, 5):
        i = 0
        while i <= len(entries) - pattern_len:
            norms = []
            valid = True
            for k in range(pattern_len):
                n = normalize(entries[i + k]["text"])
                if not n:
                    valid = False
                    break
                norms.append(n)
            if not valid:
                i += 1
                continue
            repeats = 1
            j = i + pattern_len
            while j + pattern_len <= len(entries):
                match = True
                for k in range(pattern_len):
                    n = normalize(entries[j + k]["text"])
                    if n != norms[k] and similarity(n, norms[k]) < 0.85:
                        match = False
                        break
                if match:
                    repeats += 1
                    j += pattern_len
                else:
                    break
            if repeats >= min_repeat:
                for k in range(i, j):
                    loop_entries.add(k)
                i = j
            else:
                i += 1

    # Check 3: intra-entry loop
    for i, entry in enumerate(entries):
        norm = normalize(entry["text"])
        if norm and is_intra_loop(norm):
            loop_entries.add(i)

    if not loop_entries:
        return []

    # Raggruppa in range contigui
    sorted_indices = sorted(loop_entries)
    ranges = []
    range_start = sorted_indices[0]
    range_end = sorted_indices[0]

    for idx in sorted_indices[1:]:
        if idx <= range_end + 3:  # tollera piccoli gap (fino a 3 entry non-loop)
            range_end = idx
        else:
            ranges.append((
                entries[range_start]["start_s"],
                entries[range_end]["end_s"],
                range_start,
                range_end,
            ))
            range_start = idx
            range_end = idx

    ranges.append((
        entries[range_start]["start_s"],
        entries[range_end]["end_s"],
        range_start,
        range_end,
    ))

    return ranges


def _extract_audio_segment(wav_path: Path, start_s: float, end_s: float, output_path: Path) -> Path:
    """Estrae un segmento audio dal file WAV."""
    duration = end_s - start_s
    cmd = [
        "ffmpeg", "-y",
        "-i", str(wav_path),
        "-ss", str(start_s),
        "-t", str(duration),
        "-c:a", "copy",
        str(output_path),
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    return output_path


def _wav_to_flac(wav_path: Path, flac_path: Path) -> Path:
    """Converte WAV in FLAC per ridurre la dimensione (richiesto per Groq <25MB)."""
    cmd = [
        "ffmpeg", "-y",
        "-i", str(wav_path),
        "-c:a", "flac",
        str(flac_path),
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    return flac_path


def transcribe_groq(
    audio_path: Path,
    language: str = "it",
    initial_prompt: str | None = None,
    model: str | None = None,
) -> str | None:
    """Trascrive audio via Groq Whisper API.

    Prova whisper-large-v3-turbo, poi whisper-large-v3 come fallback.

    Args:
        audio_path: Path del file audio (WAV, FLAC, MP3, etc.)
        language: Codice lingua ISO-639-1
        initial_prompt: Prompt per guidare il riconoscimento (max 224 token)
        model: Modello specifico da usare (default: prova turbo poi v3)

    Returns:
        Testo trascritto o None se fallisce.
    """
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        print("[groq] GROQ_API_KEY non impostata, skip fallback cloud")
        return None

    # Converti in FLAC se il file è troppo grande
    upload_path = audio_path
    if audio_path.stat().st_size > GROQ_MAX_FILE_SIZE:
        flac_path = audio_path.with_suffix(".flac")
        _wav_to_flac(audio_path, flac_path)
        if flac_path.stat().st_size > GROQ_MAX_FILE_SIZE:
            # Ancora troppo grande — splitta in pezzi
            print(f"[groq] File troppo grande ({flac_path.stat().st_size / 1024 / 1024:.1f}MB), split necessario")
            flac_path.unlink(missing_ok=True)
            return _transcribe_groq_chunked(audio_path, language, initial_prompt, model)
        upload_path = flac_path

    models_to_try = [model] if model else GROQ_MODELS
    result = None

    for m in models_to_try:
        result = _call_groq(upload_path, m, language, initial_prompt, api_key)
        if result is not None:
            break

    # Pulizia FLAC temporaneo
    if upload_path != audio_path:
        upload_path.unlink(missing_ok=True)

    return result


def _transcribe_groq_chunked(
    wav_path: Path,
    language: str,
    initial_prompt: str | None,
    model: str | None,
) -> str | None:
    """Splitta l'audio e trascrive via Groq chunk per chunk."""
    chunks_dir = wav_path.parent / "groq_chunks"
    chunks_dir.mkdir(exist_ok=True)

    duration = get_audio_duration(wav_path)
    # Chunk da 4 min per stare sotto 25MB in FLAC
    chunk_s = 240
    n_chunks = int(duration // chunk_s) + (1 if duration % chunk_s > 0 else 0)

    parts = []
    for i in range(n_chunks):
        chunk_wav = chunks_dir / f"groq_chunk_{i+1:02d}.wav"
        _extract_audio_segment(wav_path, i * chunk_s, min((i + 1) * chunk_s, duration), chunk_wav)

        chunk_flac = chunk_wav.with_suffix(".flac")
        _wav_to_flac(chunk_wav, chunk_flac)

        text = transcribe_groq(chunk_flac, language, initial_prompt, model)
        chunk_wav.unlink(missing_ok=True)
        chunk_flac.unlink(missing_ok=True)

        if text is None:
            # Pulizia e fallimento
            for f in chunks_dir.glob("*"):
                f.unlink()
            chunks_dir.rmdir()
            return None
        parts.append(text)

    for f in chunks_dir.glob("*"):
        f.unlink()
    chunks_dir.rmdir()

    return "\n".join(parts)


def _call_groq(
    audio_path: Path,
    model: str,
    language: str,
    initial_prompt: str | None,
    api_key: str,
) -> str | None:
    """Singola call all'API Groq via curl (urllib bloccato da Cloudflare)."""
    cmd = [
        "curl", "-s", "-w", "\n%{http_code}",
        "-X", "POST", GROQ_API_URL,
        "-H", f"Authorization: Bearer {api_key}",
        "-F", f"file=@{audio_path}",
        "-F", f"model={model}",
        "-F", f"language={language}",
        "-F", "response_format=text",
        "-F", "temperature=0",
    ]
    if initial_prompt:
        cmd.extend(["-F", f"prompt={initial_prompt[:800]}"])

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        lines = result.stdout.strip().rsplit("\n", 1)
        if len(lines) == 2:
            body, http_code = lines[0], lines[1]
        else:
            body, http_code = result.stdout.strip(), "000"

        if http_code == "200" and body.strip():
            print(f"[groq] {model}: trascritto {len(body.split())} parole")
            return body.strip()
        else:
            print(f"[groq] {model} HTTP {http_code}: {body[:200]}")
            return None
    except subprocess.TimeoutExpired:
        print(f"[groq] {model} timeout (180s)")
        return None
    except Exception as e:
        print(f"[groq] {model} errore: {e}")
        return None


def retranscribe_loops(
    wav_path: Path,
    vtt_path: Path,
    txt_path: Path,
    output_dir: Path,
    model_path: Path,
    language: str = "it",
    initial_prompt: str | None = None,
) -> int:
    """Rileva loop nel VTT, ri-trascrive quei segmenti audio, aggiorna VTT e TXT.

    Returns:
        Numero di loop ri-trascritti con successo (0 se nessun loop trovato).
    """
    vtt_text = vtt_path.read_text(encoding="utf-8")
    entries = _parse_vtt_entries(vtt_text)
    loop_ranges = _detect_loop_ranges(entries)

    if not loop_ranges:
        print("[retranscribe] Nessun loop rilevato nel VTT")
        return 0

    total_lost_s = sum(end - start for start, end, _, _ in loop_ranges)
    print(f"[retranscribe] Trovati {len(loop_ranges)} loop ({total_lost_s/60:.1f} min di audio da ri-trascrivere)")

    retry_dir = output_dir / "retries"
    retry_dir.mkdir(exist_ok=True)

    MARKER = "[LOOP WHISPER — audio non trascritto]"
    replacements = []  # (entry_start_idx, entry_end_idx, new_txt_lines, new_vtt_lines)

    for loop_i, (start_s, end_s, e_start, e_end) in enumerate(loop_ranges):
        duration = end_s - start_s
        print(f"[retranscribe] Loop {loop_i+1}/{len(loop_ranges)}: "
              f"{start_s/60:.1f}min → {end_s/60:.1f}min ({duration/60:.1f} min)")

        # Estrai segmento audio
        seg_wav = retry_dir / f"loop_{loop_i+1:02d}.wav"
        _extract_audio_segment(wav_path, start_s, end_s, seg_wav)

        # Ri-trascrivi in micro-chunk
        retry_chunks = []
        if duration > RETRY_CHUNK_S * 1.2:
            n = int(duration // RETRY_CHUNK_S) + (1 if duration % RETRY_CHUNK_S > 0 else 0)
            for ci in range(n):
                chunk_start = ci * RETRY_CHUNK_S
                chunk_wav = retry_dir / f"loop_{loop_i+1:02d}_chunk_{ci+1:02d}.wav"
                _extract_audio_segment(seg_wav, chunk_start, min(chunk_start + RETRY_CHUNK_S, duration), chunk_wav)
                retry_chunks.append(chunk_wav)
        else:
            retry_chunks = [seg_wav]

        # Trascrivi ogni micro-chunk con entropia ancora più bassa
        new_txt_parts = []
        new_vtt_parts = []
        success = False

        for attempt in range(MAX_RETRIES):
            new_txt_parts = []
            new_vtt_parts = []
            all_clean = True

            for ci, chunk_wav in enumerate(retry_chunks):
                label = f"loop{loop_i+1}_attempt{attempt+1}_chunk{ci+1}"
                out_base = retry_dir / label
                # Parametri più aggressivi anti-loop
                cmd = [
                    "whisper-cli",
                    "-m", str(model_path),
                    "-l", language,
                    "-ovtt", "-otxt",
                    "-of", str(out_base),
                    "--no-prints",
                    "--entropy-thold", str(1.8 - attempt * 0.3),  # più aggressivo ad ogni tentativo
                ]
                if initial_prompt:
                    cmd.extend(["--prompt", initial_prompt])
                cmd.append(str(chunk_wav))

                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    print(f"[retranscribe]   whisper-cli fallito: {result.stderr[:200]}")
                    all_clean = False
                    break

                retry_txt_path = Path(str(out_base) + ".txt")
                retry_vtt_path = Path(str(out_base) + ".vtt")

                if retry_txt_path.exists():
                    chunk_txt = retry_txt_path.read_text(encoding="utf-8").strip()
                    # Verifica che non ci sia ancora un loop
                    chunk_entries = _parse_vtt_entries(
                        retry_vtt_path.read_text(encoding="utf-8")
                    ) if retry_vtt_path.exists() else []
                    chunk_loops = _detect_loop_ranges(chunk_entries)
                    if chunk_loops:
                        print(f"[retranscribe]   Chunk {ci+1}: loop ancora presente (tentativo {attempt+1})")
                        all_clean = False
                        break
                    new_txt_parts.append(chunk_txt)
                    if retry_vtt_path.exists():
                        new_vtt_parts.append(retry_vtt_path.read_text(encoding="utf-8"))

            if all_clean and new_txt_parts:
                success = True
                break
            print(f"[retranscribe]   Tentativo {attempt+1} fallito, riprovo...")

        if success:
            new_text = "\n".join(new_txt_parts)
            word_count = len(new_text.split())
            print(f"[retranscribe]   Recuperate ~{word_count} parole (locale)")
            replacements.append((e_start, e_end, new_text, start_s))
        else:
            # Fallback cloud: Groq Whisper API
            print(f"[retranscribe]   Locale fallito, provo Groq cloud...")
            groq_text = transcribe_groq(seg_wav, language, initial_prompt)
            if groq_text and len(groq_text.split()) > 5:
                word_count = len(groq_text.split())
                print(f"[retranscribe]   Recuperate ~{word_count} parole (Groq cloud)")
                replacements.append((e_start, e_end, groq_text, start_s))
            else:
                print(f"[retranscribe]   Anche Groq fallito, lascio marcatore")
                replacements.append((e_start, e_end, MARKER, start_s))

    # Applica le sostituzioni al TXT
    # Ricostruiamo il TXT dalle entry VTT originali + sostituzioni
    txt_lines = []
    replaced_ranges = set()
    for e_start, e_end, new_text, _ in replacements:
        for k in range(e_start, e_end + 1):
            replaced_ranges.add(k)

    replacement_map = {r[0]: r for r in replacements}
    i = 0
    while i < len(entries):
        if i in replacement_map:
            _, e_end, new_text, _ = replacement_map[i]
            txt_lines.append(new_text)
            i = e_end + 1
        elif i in replaced_ranges:
            i += 1  # skip (part of a replaced range)
        else:
            txt_lines.append(entries[i]["text"])
            i += 1

    txt_path.write_text("\n".join(txt_lines), encoding="utf-8")

    # Aggiorna anche il VTT (semplificato: riscriviamo con i testi aggiornati)
    vtt_lines = ["WEBVTT", ""]
    i = 0
    while i < len(entries):
        if i in replacement_map:
            _, e_end, new_text, start_s_loop = replacement_map[i]
            if new_text == MARKER:
                # Mantieni un solo entry con il marcatore
                vtt_lines.append(entries[i]["raw_ts"])
                vtt_lines.append(MARKER)
                vtt_lines.append("")
            else:
                # Inserisci il testo ri-trascritto come entry singola
                # (perde i timestamp granulari, ma il contenuto è corretto)
                start_ts = entries[i]["raw_ts"].split("-->")[0].strip()
                end_ts = entries[e_end]["raw_ts"].split("-->")[1].strip()
                vtt_lines.append(f"{start_ts} --> {end_ts}")
                for line in new_text.split("\n"):
                    if line.strip():
                        vtt_lines.append(line.strip())
                vtt_lines.append("")
            i = e_end + 1
        elif i in replaced_ranges:
            i += 1
        else:
            vtt_lines.append(entries[i]["raw_ts"])
            vtt_lines.append(entries[i]["text"])
            vtt_lines.append("")
            i += 1

    vtt_path.write_text("\n".join(vtt_lines), encoding="utf-8")

    # Pulizia file temporanei
    for f in retry_dir.glob("*"):
        f.unlink()
    retry_dir.rmdir()

    recovered = sum(1 for _, _, text, _ in replacements if text != MARKER)
    print(f"[retranscribe] Risultato: {recovered}/{len(loop_ranges)} loop recuperati")
    return recovered


def transcribe(
    audio_path: Path,
    output_dir: Path,
    language: str = "it",
    initial_prompt: str | None = None,
    model_path: Path | None = None,
    backend: str = "local",
) -> Path:
    """Trascrive un file audio con preprocessing, chunking e whisper-cli o Groq.

    Args:
        audio_path: Path del file audio (M4A, WAV, MP3, etc.)
        output_dir: Directory per i file di output
        language: Codice lingua (default: it)
        initial_prompt: Prompt iniziale per guidare il riconoscimento
        model_path: Path del modello GGML (default: large-v3, solo backend local)
        backend: "local" (whisper-cli) o "groq" (Groq Whisper API)

    Returns:
        Path del file VTT (local) o TXT (groq) generato
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    if backend == "groq":
        return _transcribe_groq_full(audio_path, output_dir, language, initial_prompt)

    # --- Backend locale (whisper-cli) ---

    # Scegli il modello
    if model_path is None:
        model_path = DEFAULT_MODEL if DEFAULT_MODEL.exists() else FALLBACK_MODEL
    if not model_path.exists():
        raise FileNotFoundError(f"Modello non trovato: {model_path}")

    # Step 1: Preprocessing (filtri + conversione WAV 16kHz mono)
    wav_path = output_dir / (audio_path.stem + ".wav")
    preprocess_audio(audio_path, wav_path)

    # Step 2: Split in chunk
    chunks_dir = output_dir / "chunks"
    chunks_dir.mkdir(exist_ok=True)
    chunk_paths = split_audio(wav_path, chunks_dir)

    # Step 3: Trascrizione chunk per chunk
    vtt_parts = []
    txt_parts = []
    for i, chunk_path in enumerate(chunk_paths):
        label = f"chunk {i+1}/{len(chunk_paths)}" if len(chunk_paths) > 1 else "audio"
        print(f"[transcribe] Trascrizione {label} con {model_path.name}...")
        out_base = chunks_dir / f"out_{i+1:02d}"
        vtt_p, txt_p = transcribe_chunk(chunk_path, out_base, model_path, language, initial_prompt)
        vtt_parts.append(vtt_p)
        txt_parts.append(txt_p)

    # Step 4: Concatenazione output
    final_vtt = output_dir / (audio_path.stem + ".vtt")
    final_txt = output_dir / (audio_path.stem + ".txt")

    if len(chunk_paths) == 1:
        # Singolo chunk — sposta direttamente
        if vtt_parts[0].exists():
            final_vtt.write_text(vtt_parts[0].read_text(encoding="utf-8"), encoding="utf-8")
        if txt_parts[0].exists():
            final_txt.write_text(txt_parts[0].read_text(encoding="utf-8"), encoding="utf-8")
    else:
        concat_vtt(vtt_parts, final_vtt)
        concat_txt(txt_parts, final_txt)

    # Step 5: Rilevamento e ri-trascrizione loop
    if final_vtt.exists() and final_txt.exists():
        retranscribe_loops(
            wav_path, final_vtt, final_txt, output_dir,
            model_path, language, initial_prompt,
        )

    # Pulizia
    wav_path.unlink(missing_ok=True)
    for p in chunk_paths:
        p.unlink(missing_ok=True)

    print(f"[transcribe] VTT: {final_vtt}")
    if final_txt.exists():
        word_count = len(final_txt.read_text().split())
        print(f"[transcribe] TXT: {final_txt} (~{word_count} parole)")

    return final_vtt


def _transcribe_groq_full(
    audio_path: Path,
    output_dir: Path,
    language: str = "it",
    initial_prompt: str | None = None,
) -> Path:
    """Trascrizione completa via Groq: preprocessing → chunking → Groq API → TXT.

    Returns:
        Path del file TXT generato.
    """
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY non impostata")

    # Step 1: Preprocessing (filtri + conversione WAV 16kHz mono)
    wav_path = output_dir / (audio_path.stem + ".wav")
    preprocess_audio(audio_path, wav_path)

    # Step 2: Split in chunk da 15 min
    chunks_dir = output_dir / "chunks"
    chunks_dir.mkdir(exist_ok=True)
    chunk_paths = split_audio(wav_path, chunks_dir)

    # Step 2b: Converti chunk WAV → FLAC (riduce ~28MB → ~12MB, evita 413)
    flac_paths = []
    for cp in chunk_paths:
        flac_p = cp.with_suffix(".flac")
        _wav_to_flac(cp, flac_p)
        cp.unlink(missing_ok=True)  # libera subito il WAV
        flac_paths.append(flac_p)

    # Step 3: Trascrizione chunk per chunk via Groq
    txt_parts = []
    for i, flac_path in enumerate(flac_paths):
        label = f"chunk {i+1}/{len(flac_paths)}" if len(flac_paths) > 1 else "audio"
        size_mb = flac_path.stat().st_size / 1024 / 1024
        print(f"[transcribe-groq] Trascrizione {label} ({size_mb:.1f}MB FLAC) via Groq...")

        text = transcribe_groq(flac_path, language, initial_prompt, model="whisper-large-v3-turbo")
        if text is None:
            print(f"[transcribe-groq] Chunk {i+1} turbo fallito, provo whisper-large-v3...")
            text = transcribe_groq(flac_path, language, initial_prompt, model="whisper-large-v3")
        if text is None:
            print(f"[transcribe-groq] ERRORE: chunk {i+1} non trascritto")
            text = "[AUDIO NON TRASCRIVIBILE]"

        txt_parts.append(text)

    # Step 4: Concatenazione output
    final_txt = output_dir / (audio_path.stem + ".txt")
    final_txt.write_text("\n".join(txt_parts), encoding="utf-8")

    # Pulizia
    wav_path.unlink(missing_ok=True)
    for p in flac_paths:
        p.unlink(missing_ok=True)
    if chunks_dir.exists() and not list(chunks_dir.iterdir()):
        chunks_dir.rmdir()

    word_count = len(final_txt.read_text().split())
    print(f"[transcribe-groq] TXT: {final_txt} (~{word_count} parole)")

    return final_txt


def extract_text_from_vtt(vtt_path: Path) -> str:
    """Estrae il testo puro da un file VTT, rimuovendo timestamp e header."""
    lines = vtt_path.read_text(encoding="utf-8").splitlines()
    text_lines = []
    for line in lines:
        line = line.strip()
        # Salta header WEBVTT, righe vuote, timestamp
        if not line or line == "WEBVTT" or "-->" in line:
            continue
        text_lines.append(line)
    return " ".join(text_lines)


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Uso: python transcribe.py <audio.m4a> [output_dir] [initial_prompt]")
        sys.exit(1)

    audio_p = Path(sys.argv[1])
    output_d = Path(sys.argv[2]) if len(sys.argv) > 2 else audio_p.parent
    prompt = sys.argv[3] if len(sys.argv) > 3 else None
    transcribe(audio_p, output_d, initial_prompt=prompt)
