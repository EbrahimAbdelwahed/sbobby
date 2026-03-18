"""
Orchestratore batch per processing sbobine vecchie.

Uso:
    python batch_sbobine.py parse anatomia
    python batch_sbobine.py extract anatomia
    python batch_sbobine.py aggregate anatomia
    python batch_sbobine.py prompts anatomia
    python batch_sbobine.py run anatomia          # tutti gli step
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from parse_doc import parse_directory
from extract_emphasis import extract_emphasis_file
from aggregate import build_dossier, generate_initial_prompts

PROJECT_ROOT = Path(__file__).parent.parent


def get_paths(subject: str) -> dict:
    """Restituisce tutti i path per una materia."""
    base = PROJECT_ROOT / "sbobine_vecchie" / subject
    return {
        "originali": base / "originali",
        "parsed": base / "parsed",
        "extractions": base / "extractions",
        "dossier": base / "dossier",
        "initial_prompts": PROJECT_ROOT / "config" / subject / "initial_prompts",
    }


def step_parse(subject: str) -> None:
    paths = get_paths(subject)
    if not paths["originali"].exists():
        print(f"[batch] Directory originali non trovata: {paths['originali']}")
        print(f"  Metti i file DOC/DOCX/PDF in {paths['originali']}")
        sys.exit(1)

    results = parse_directory(paths["originali"], paths["parsed"])
    print(f"\n[batch] Parsati {len(results)} file → {paths['parsed']}")


def step_extract(subject: str) -> None:
    paths = get_paths(subject)
    parsed_dir = paths["parsed"]

    if not parsed_dir.exists():
        print(f"[batch] Directory parsed non trovata: {parsed_dir}")
        print("  Esegui prima: python batch_sbobine.py parse {subject}")
        sys.exit(1)

    files = sorted(parsed_dir.glob("*.txt"))
    if not files:
        print(f"[batch] Nessun file .txt in {parsed_dir}")
        sys.exit(1)

    print(f"[batch] Estrazione enfasi da {len(files)} file...")
    all_results = []
    for f in files:
        print(f"\n--- {f.name} ---")
        results = extract_emphasis_file(f, paths["extractions"])
        all_results.extend(results)

    print(f"\n[batch] {len(all_results)} estrazioni salvate → {paths['extractions']}")


def step_aggregate(subject: str) -> None:
    paths = get_paths(subject)

    if not paths["extractions"].exists():
        print(f"[batch] Directory estrazioni non trovata: {paths['extractions']}")
        print(f"  Esegui prima: python batch_sbobine.py extract {subject}")
        sys.exit(1)

    results = build_dossier(paths["extractions"], paths["dossier"])
    print(f"\n[batch] {len(results)} dossier generati → {paths['dossier']}")


def step_prompts(subject: str) -> None:
    paths = get_paths(subject)

    if not paths["dossier"].exists():
        print(f"[batch] Directory dossier non trovata: {paths['dossier']}")
        print(f"  Esegui prima: python batch_sbobine.py aggregate {subject}")
        sys.exit(1)

    results = generate_initial_prompts(paths["dossier"], paths["initial_prompts"])
    print(f"\n[batch] {len(results)} initial prompts → {paths['initial_prompts']}")


def run_all(subject: str) -> None:
    """Esegue tutti gli step in sequenza."""
    print(f"\n{'='*60}")
    print(f"  Batch sbobine vecchie: {subject}")
    print(f"{'='*60}\n")

    print("--- STEP 1: Parsing documenti ---")
    step_parse(subject)

    print("\n--- STEP 2: Estrazione enfasi ---")
    step_extract(subject)

    print("\n--- STEP 3: Aggregazione dossier ---")
    step_aggregate(subject)

    print("\n--- STEP 4: Generazione initial prompts ---")
    step_prompts(subject)

    paths = get_paths(subject)
    print(f"\n{'='*60}")
    print(f"  Dossier in: {paths['dossier']}")
    print(f"  Initial prompts in: {paths['initial_prompts']}")
    print(f"{'='*60}\n")


STEPS = {
    "parse": step_parse,
    "extract": step_extract,
    "aggregate": step_aggregate,
    "prompts": step_prompts,
    "run": run_all,
}


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1]
    subject = sys.argv[2]

    if command not in STEPS:
        print(f"Comando sconosciuto: {command}")
        print(f"Comandi disponibili: {', '.join(STEPS.keys())}")
        sys.exit(1)

    STEPS[command](subject)


if __name__ == "__main__":
    main()
