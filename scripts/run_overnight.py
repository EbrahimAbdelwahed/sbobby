"""
Script batch overnight.

Fase 1 — Flashcard + brain dump per tutte le sbobine esistenti.
Fase 2 — Pipeline completa (trascrizione Groq + elaborazione + flashcard) per i nuovi audio.
Fase 3 — Aggregazione brain dump per materia + sync vault.

Uso:
    conda activate sbobine
    python run_overnight.py

Log salvato in: overnight.log
"""

import sys
import time
import traceback
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from pipeline import (
    step_flashcards,
    run_full,
    step_sync_vault,
    aggregate_brain_dumps_file,
)

PROJECT_ROOT = Path(__file__).parent
LOG_PATH = PROJECT_ROOT / "overnight.log"

# ─── Configurazione ───────────────────────────────────────────────────────────

# Sbobine già elaborate — genera solo flashcard + brain dump
EXISTING_SBOBINE = []  # skip Fase 1

# Nuovi audio — pipeline completa con Groq (no micheletti, no image injection)
NEW_AUDIO = [
    # Anatomia
    ("anatomia",   "lezione_08",       "audio/anatomia/lezione_8.m4a"),
    ("anatomia",   "lezione_09",       "audio/anatomia/lezione_9.m4a"),
    ("anatomia",   "lezione_canzi_02", "audio/anatomia/lezione_canzi_02.m4a"),
    # Biochimica
    ("biochimica", "lezione_10",       "audio/biochimica/lezione_10.m4a"),
    ("biochimica", "lezione_11",       "audio/biochimica/lezione_11.m4a"),
    ("biochimica", "lezione_12",       "audio/biochimica/lezione_12.m4a"),
    ("biochimica", "lezione_13",       "audio/biochimica/lezione_13.m4a"),
    ("biochimica", "lezione_14",       "audio/biochimica/lezione_14.m4a"),
    ("biochimica", "lezione_15",       "audio/biochimica/lezione_15.m4a"),
    # Istologia
    ("istologia",  "lezione_04",       "audio/istologia/lezione_4.m4a"),
]

# Materie per aggregazione finale
ALL_SUBJECTS = ["anatomia", "biochimica", "istologia"]

# ─── Logger ───────────────────────────────────────────────────────────────────

class Tee:
    """Scrive su stdout e su file contemporaneamente."""
    def __init__(self, log_path: Path):
        self.log = log_path.open("a", encoding="utf-8")
        self.stdout = sys.stdout

    def write(self, msg):
        self.stdout.write(msg)
        self.log.write(msg)

    def flush(self):
        self.stdout.flush()
        self.log.flush()

    def close(self):
        self.log.close()


def banner(msg: str) -> None:
    line = "=" * 65
    print(f"\n{line}")
    print(f"  {msg}")
    print(f"{line}\n")


def ts() -> str:
    return datetime.now().strftime("%H:%M:%S")


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    tee = Tee(LOG_PATH)
    sys.stdout = tee

    started = time.time()
    print(f"\n{'='*65}")
    print(f"  run_overnight.py — avviato {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*65}\n")

    results: list[tuple[str, str]] = []

    # ── FASE 1: Flashcard per sbobine esistenti ──────────────────────────────
    banner("FASE 1 — Flashcard + brain dump sbobine esistenti")

    for subject, lesson in EXISTING_SBOBINE:
        label = f"{subject}/{lesson}"
        print(f"[{ts()}] >>> {label}")
        try:
            step_flashcards(subject, lesson)
            results.append((label, "OK - flashcards"))
            print(f"[{ts()}] <<< {label} completato\n")
        except Exception:
            tb = traceback.format_exc()
            print(f"[{ts()}] ERRORE {label}:\n{tb}")
            results.append((label, f"ERRORE: {tb.splitlines()[-1]}"))

    # ── FASE 2: Pipeline completa per nuovi audio ────────────────────────────
    banner("FASE 2 — Pipeline completa (Groq) per nuovi audio")

    for subject, lesson, audio_rel in NEW_AUDIO:
        label = f"{subject}/{lesson}"
        audio_path = PROJECT_ROOT / audio_rel
        if not audio_path.exists():
            print(f"[{ts()}] SKIP {label}: audio non trovato ({audio_path})")
            results.append((label, f"SKIP - audio non trovato"))
            continue

        print(f"[{ts()}] >>> {label} ({audio_path.name})")
        try:
            run_full(subject, lesson, str(audio_path), backend="groq")
            results.append((label, "OK - pipeline completa"))
            print(f"[{ts()}] <<< {label} completato\n")
        except Exception:
            tb = traceback.format_exc()
            print(f"[{ts()}] ERRORE {label}:\n{tb}")
            results.append((label, f"ERRORE: {tb.splitlines()[-1]}"))

    # ── FASE 3: Aggregazione brain dump + sync vault ─────────────────────────
    banner("FASE 3 — Aggregazione brain dump + sync vault")

    for subject in ALL_SUBJECTS:
        print(f"[{ts()}] Aggregazione brain dump: {subject}")
        try:
            aggregate_brain_dumps_file(subject)
        except Exception:
            tb = traceback.format_exc()
            print(f"[{ts()}] ERRORE aggregazione {subject}:\n{tb}")

    # Sync vault per tutte le lezioni (esistenti + nuove)
    all_lessons = [(s, l) for s, l in EXISTING_SBOBINE]
    all_lessons += [(s, l) for s, l, _ in NEW_AUDIO]

    for subject, lesson in all_lessons:
        label = f"vault sync {subject}/{lesson}"
        try:
            step_sync_vault(subject, lesson)
        except Exception:
            tb = traceback.format_exc()
            print(f"[{ts()}] ERRORE {label}:\n{tb}")

    # ── Riepilogo finale ─────────────────────────────────────────────────────
    elapsed = time.time() - started
    banner(f"RIEPILOGO — {len(results)} task, {elapsed/60:.0f} min totali")

    ok = [r for r in results if r[1].startswith("OK")]
    err = [r for r in results if r[1].startswith("ERRORE")]
    skip = [r for r in results if r[1].startswith("SKIP")]

    print(f"  OK:    {len(ok)}")
    print(f"  ERRORI: {len(err)}")
    print(f"  SKIP:  {len(skip)}")
    print()
    for label, status in results:
        icon = "✓" if status.startswith("OK") else ("⚠" if status.startswith("SKIP") else "✗")
        print(f"  {icon}  {label:45s}  {status[:60]}")

    print(f"\nLog completo: {LOG_PATH}\n")

    sys.stdout = tee.stdout
    tee.close()

    return 0 if not err else 1


if __name__ == "__main__":
    sys.exit(main())
