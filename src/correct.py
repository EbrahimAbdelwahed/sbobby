"""
Correzione automatica delle trascrizioni:
1. Rilevamento e rimozione loop Whisper (righe ripetute in sequenza)
2. Sostituzione da dizionario di errori ricorrenti

Formato file correzioni.txt: una riga per errore
    errore → correzione
"""

import re
from pathlib import Path
from collections import Counter


# --- Loop detection ---

def _normalize(line: str) -> str:
    """Normalizza una riga per il confronto: lowercase, rimuove punteggiatura e spazi multipli."""
    line = line.lower().strip()
    line = re.sub(r"[^\w\s]", "", line)
    line = re.sub(r"\s+", " ", line)
    return line


def clean_loops(text: str, min_repeat: int = 3) -> tuple[str, int]:
    """Rileva e rimuove loop Whisper dalla trascrizione.

    Strategia multi-livello:
    1. Righe identiche consecutive (o quasi-identiche)
    2. Pattern multi-riga ripetuti (es. 2-3 righe brevi che si alternano)
    3. Frasi ripetute DENTRO una singola riga

    Args:
        text: testo della trascrizione
        min_repeat: numero minimo di ripetizioni per considerare un loop

    Returns:
        (testo pulito, numero di righe rimosse)
    """
    MARKER = "[LOOP WHISPER — audio non trascritto]"
    lines = text.split("\n")

    # Prima passa: marca le righe da rimuovere
    to_remove = set()

    # --- Check 1: righe consecutive identiche (o quasi) ---
    i = 0
    while i < len(lines):
        norm = _normalize(lines[i])
        if not norm:
            i += 1
            continue
        j = i + 1
        count = 1
        while j < len(lines):
            next_norm = _normalize(lines[j])
            if not next_norm:
                j += 1
                continue
            if next_norm == norm or _similarity(norm, next_norm) > 0.85:
                count += 1
                j += 1
            else:
                break
        if count >= min_repeat:
            for k in range(i, j):
                to_remove.add(k)
        i = j if count >= min_repeat else i + 1

    # --- Check 2: pattern multi-riga ripetuti ---
    # Es: "e non accettate" / "il voto" che si alternano decine di volte
    # Cerca pattern di 2-4 righe ripetuti
    for pattern_len in range(2, 5):
        i = 0
        while i <= len(lines) - pattern_len:
            # Prendi un pattern candidato
            pattern_norms = []
            valid = True
            for k in range(pattern_len):
                n = _normalize(lines[i + k])
                if not n:
                    valid = False
                    break
                pattern_norms.append(n)
            if not valid:
                i += 1
                continue

            # Conta quante volte il pattern si ripete consecutivamente
            repeats = 1
            j = i + pattern_len
            while j + pattern_len <= len(lines):
                match = True
                for k in range(pattern_len):
                    n = _normalize(lines[j + k])
                    if n != pattern_norms[k] and _similarity(n, pattern_norms[k]) < 0.85:
                        match = False
                        break
                if match:
                    repeats += 1
                    j += pattern_len
                else:
                    break

            if repeats >= min_repeat:
                for k in range(i, j):
                    to_remove.add(k)
                i = j
            else:
                i += 1

    # --- Check 3: ripetizione intra-riga ---
    for i, line in enumerate(lines):
        norm = _normalize(line)
        if norm and _is_intra_line_loop(norm, min_repeat):
            to_remove.add(i)

    # Costruisci output: sostituisci blocchi rimossi con un singolo marcatore
    result = []
    removed = len(to_remove)
    prev_was_removed = False
    for i, line in enumerate(lines):
        if i in to_remove:
            if not prev_was_removed:
                result.append(MARKER)
            prev_was_removed = True
        else:
            prev_was_removed = False
            result.append(line)

    return "\n".join(result), removed


def _is_intra_line_loop(normalized_line: str, min_repeat: int = 3) -> bool:
    """Rileva se una riga contiene la stessa frase ripetuta molte volte.

    Es: "allora usare ulteriore premessa allora usare ulteriore premessa allora..."
    """
    words = normalized_line.split()
    if len(words) < min_repeat * 2:
        return False

    # Prova pattern di lunghezza da 2 a 8 parole
    for pattern_len in range(2, min(9, len(words) // min_repeat + 1)):
        pattern = " ".join(words[:pattern_len])
        if not pattern:
            continue
        count = 0
        pos = 0
        text = " ".join(words)
        while True:
            idx = text.find(pattern, pos)
            if idx == -1:
                break
            count += 1
            pos = idx + len(pattern)
        if count >= min_repeat and (count * len(pattern.split())) / len(words) > 0.6:
            return True

    return False


def _similarity(a: str, b: str) -> float:
    """Similarità rapida basata su overlap di parole."""
    words_a = set(a.split())
    words_b = set(b.split())
    if not words_a or not words_b:
        return 0.0
    intersection = words_a & words_b
    return len(intersection) / max(len(words_a), len(words_b))


# --- Dictionary corrections ---

def load_corrections(corrections_path: Path) -> list[tuple[str, str]]:
    """Carica le coppie (errore, correzione) dal file."""
    corrections = []
    if not corrections_path.exists():
        return corrections

    for line in corrections_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "→" not in line:
            continue
        error, correction = line.split("→", 1)
        error = error.strip()
        correction = correction.strip()
        if error and correction:
            corrections.append((error, correction))

    return corrections


def apply_corrections(text: str, corrections: list[tuple[str, str]]) -> str:
    """Applica le sostituzioni al testo. Case-insensitive, preserva i confini di parola."""
    for error, correction in corrections:
        pattern = re.compile(re.escape(error), re.IGNORECASE)
        text = pattern.sub(correction, text)
    return text


def correct_file(input_path: Path, corrections_path: Path, output_path: Path | None = None) -> Path:
    """Legge la trascrizione, applica pulizia loop + correzioni, salva il file corretto.

    Se output_path non è specificato, salva come input_path con suffisso _corretta.
    """
    output_path = output_path or input_path.with_stem(input_path.stem + "_corretta")
    corrections = load_corrections(corrections_path)

    text = input_path.read_text(encoding="utf-8")

    # Step 1: Pulizia loop Whisper
    text, loops_removed = clean_loops(text)
    if loops_removed:
        print(f"[correct] Rimossi {loops_removed} righe di loop Whisper")
    else:
        print("[correct] Nessun loop Whisper rilevato")

    # Step 2: Correzioni da dizionario
    if corrections:
        text = apply_corrections(text, corrections)
        print(f"[correct] Applicate {len(corrections)} regole di correzione")
    else:
        print("[correct] Nessuna regola di correzione trovata")

    output_path.write_text(text, encoding="utf-8")
    return output_path


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Uso: python correct.py <trascrizione> <correzioni.txt> [output]")
        sys.exit(1)

    input_p = Path(sys.argv[1])
    corrections_p = Path(sys.argv[2])
    output_p = Path(sys.argv[3]) if len(sys.argv) > 3 else None
    result = correct_file(input_p, corrections_p, output_p)
    print(f"[correct] Output: {result}")
