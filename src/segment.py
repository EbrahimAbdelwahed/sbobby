"""
Segmentazione della trascrizione in blocchi tematici via LLM.
"""

import json
import re
from pathlib import Path

from api_client import chat

PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "segmentazione.md"


def load_system_prompt() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8")


def split_into_units(text: str) -> list[str]:
    """Splitta il testo in unità per il riferimento.

    Usa le righe del file (Whisper genera ~1 riga per frase/segmento temporale).
    Se il file ha poche righe, fa fallback su split per punteggiatura.
    """
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    if len(lines) >= 20:
        return lines

    # Fallback: split per punteggiatura
    raw = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in raw if s.strip()]


def number_units(units: list[str]) -> str:
    """Crea il testo con unità numerate per il LLM."""
    return "\n".join(f"[{i+1}] {s}" for i, s in enumerate(units))


def segment(transcript: str) -> list[dict]:
    """Segmenta la trascrizione in blocchi tematici.

    Restituisce una lista di dict con chiavi 'titolo' e 'testo'.
    """
    system_prompt = load_system_prompt()
    sentences = split_into_units(transcript)
    numbered = number_units(sentences)

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": numbered},
    ]

    # Output breve (solo boundaries JSON), DeepSeek 8K basta
    response = chat(messages, temperature=0.2)

    # Estrai JSON dalla risposta (potrebbe essere wrappato in ```json ... ```)
    text = response.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1]  # rimuovi prima riga ```json
        text = text.rsplit("```", 1)[0]  # rimuovi ultimo ```

    data = json.loads(text)
    boundaries = data["segmenti"]

    # Ricostruisci i segmenti dal testo originale
    segments = []
    for seg in boundaries:
        start = seg["frase_inizio"] - 1  # 1-indexed → 0-indexed
        end = seg["frase_fine"]  # inclusive → exclusive slice
        start = max(0, start)
        end = min(len(sentences), end)
        seg_text = " ".join(sentences[start:end])
        segments.append({"titolo": seg["titolo"], "testo": seg_text})

    print(f"[segment] Trovati {len(segments)} segmenti ({len(sentences)} frasi totali)")
    for i, seg in enumerate(segments):
        word_count = len(seg["testo"].split())
        print(f"  [{i+1}] {seg['titolo']} (~{word_count} parole)")

    return segments


def segment_file(input_path: Path, output_dir: Path) -> list[Path]:
    """Segmenta un file di trascrizione e salva i segmenti come file separati."""
    output_dir.mkdir(parents=True, exist_ok=True)

    # Pulisci vecchi segmenti per evitare residui di run precedenti
    for old in output_dir.glob("segmento_*.txt"):
        old.unlink()

    transcript = input_path.read_text(encoding="utf-8")
    segments = segment(transcript)

    paths = []
    for i, seg in enumerate(segments):
        out_path = output_dir / f"segmento_{i+1:02d}.txt"
        header = f"# {seg['titolo']}\n\n"
        out_path.write_text(header + seg["testo"], encoding="utf-8")
        paths.append(out_path)

    return paths


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Uso: python segment.py <trascrizione_corretta> [output_dir]")
        sys.exit(1)

    input_p = Path(sys.argv[1])
    output_d = Path(sys.argv[2]) if len(sys.argv) > 2 else input_p.parent / "segmenti"
    paths = segment_file(input_p, output_d)
    print(f"[segment] Segmenti salvati in {output_d}")
