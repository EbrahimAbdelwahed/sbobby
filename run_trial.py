"""
Trial run per test del nuovo formato flashcard (Anki + brain dump).

Lancia la generazione per anatomia/05, biochimica/05, istologia/01.
Output salvato in trial_output/ — nessuna card inviata ad Anki.

Uso:
    conda activate sbobine
    python run_trial.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from flashcards_llm import generate_flashcards

PROJECT_ROOT = Path(__file__).parent
OUTPUT_DIR = PROJECT_ROOT / "trial_output"

RUNS = [
    ("anatomia", "lezione_05"),
    ("biochimica", "lezione_05"),
    ("istologia", "lezione_01"),
]


def main():
    results = []
    for subject, lesson in RUNS:
        sbobina = PROJECT_ROOT / "sbobine" / subject / f"{lesson}.md"
        if not sbobina.exists():
            print(f"[trial] SKIP: {sbobina} non trovata")
            continue

        print(f"\n{'='*60}")
        print(f"[trial] {subject} / {lesson}")
        print(f"{'='*60}")

        try:
            generate_flashcards(
                sbobina_path=sbobina,
                subject=subject,
                lesson=lesson,
                dry_run=True,
                output_dir=OUTPUT_DIR,
            )
            results.append((subject, lesson, "OK"))
        except Exception as e:
            print(f"[trial] ERRORE: {e}")
            results.append((subject, lesson, f"ERRORE: {e}"))

    print(f"\n{'='*60}")
    print("[trial] Riepilogo:")
    for subject, lesson, status in results:
        print(f"  {subject}/{lesson}: {status}")
    print(f"\nOutput in: {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
