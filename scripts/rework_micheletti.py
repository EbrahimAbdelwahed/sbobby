"""
Rielaborazione sbobine Micheletti da PDF esterno.

Estrae testo dal PDF 'MICHELETTI UNIFICATO.pdf' (23 lezioni, L12-L34b),
lo segmenta, elabora in formato SSOT, fonde e compatta.

Uso:
    # Singola lezione (test)
    python scripts/rework_micheletti.py --lesson 02

    # Tutte le lezioni (02-23)
    python scripts/rework_micheletti.py --all

    # Range di lezioni
    python scripts/rework_micheletti.py --from 05 --to 10

    # Solo estrazione testo (debug)
    python scripts/rework_micheletti.py --extract-only --lesson 02

    # Workers paralleli per elaborazione (default 5)
    python scripts/rework_micheletti.py --all --workers 3
"""

import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import fitz  # PyMuPDF

# Setup path per import moduli src/
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from segment import segment
from elaborate import elaborate, load_ssot_prompt
from merge import merge_to_file
from compact import compact_to_file

SUBJECT = "anatomia"
PDF_PATH = PROJECT_ROOT / "MICHELETTI UNIFICATO.pdf"

# Mapping: (lesson_number, pdf_label, start_page, end_page, topic)
# Pages are 1-indexed inclusive, matching the plan table
LESSONS = [
    (1,  "L12",  1,   5,   "Sistema vascolare (intro, tonache, arterie)"),
    (2,  "L13",  6,   18,  "Letto capillare, reti mirabili, sistema portale"),
    (3,  "L14",  19,  28,  "Circolo cerebrale (poligono di Willis)"),
    (4,  "L15",  29,  34,  "Placche di Peyer, sistema linfatico"),
    (5,  "L16",  35,  42,  "Distribuzione linfonodi"),
    (6,  "L17",  43,  49,  "Timo"),
    (7,  "L18",  50,  58,  "Sistema endocrino"),
    (8,  "L19",  59,  68,  "Ghiandola tiroide"),
    (9,  "L20",  69,  76,  "Surrene, ritmi cortisolo"),
    (10, "L21",  77,  87,  "Stress"),
    (11, "L22",  88,  97,  "Drenaggio linfatico mammella"),
    (12, "L23",  98,  107, "Muscolatura respiratoria"),
    (13, "L24",  108, 115, "Componente venosa parete toracica"),
    (14, "L25",  116, 126, "Linee di riflessione pleuriche"),
    (15, "L26",  127, 136, "Trachea vascolarizzazione"),
    (16, "L27",  137, 148, "Polmoni (rapporti, vascolarizzazione)"),
    (17, "L28",  149, 155, "Polmoni (linfonodi, completamento)"),
    (18, "L29",  156, 174, "Bronchite cronica, patologie"),
    (19, "L31",  175, 188, "Drenaggio linfatico parete parietale"),
    (20, "L32",  189, 200, "Cuore (atrio destro)"),
    (21, "L33",  201, 207, "Difetti settali"),
    (22, "L34a", 208, 218, "Drenaggio linfatico cuore"),
    (23, "L34b", 219, 228, "Sistema di conduzione del cuore"),
]


def extract_text_from_pdf(pdf_path: Path, start_page: int, end_page: int) -> str:
    """Estrae testo da un range di pagine del PDF (1-indexed inclusive)."""
    doc = fitz.open(str(pdf_path))
    pages_text = []
    for page_num in range(start_page - 1, min(end_page, len(doc))):
        page = doc[page_num]
        text = page.get_text("text")
        if text.strip():
            pages_text.append(text.strip())
    doc.close()
    return "\n\n".join(pages_text)


def elaborate_parallel(
    segment_data: list[dict],
    subject: str,
    output_dir: Path,
    max_workers: int = 5,
) -> list[Path]:
    """Elabora segmenti in parallelo via thread pool.

    Restituisce lista ordinata di path degli elaborati.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # Pulisci vecchi elaborati
    for old in output_dir.glob("elaborato_*.md"):
        old.unlink()

    results = [None] * len(segment_data)

    def _elaborate_one(idx: int, seg: dict) -> Path:
        text = f"# {seg['titolo']}\n\n{seg['testo']}"
        print(f"  [elaborate] Segmento {idx + 1}/{len(segment_data)}: {seg['titolo']}")
        elaborated = elaborate(text, subject)
        out = output_dir / f"elaborato_{idx + 1:02d}.md"
        out.write_text(elaborated, encoding="utf-8")
        return out

    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {
            pool.submit(_elaborate_one, i, seg): i
            for i, seg in enumerate(segment_data)
        }
        for future in as_completed(futures):
            idx = futures[future]
            try:
                results[idx] = future.result()
            except Exception as e:
                print(f"  [elaborate] ERRORE segmento {idx + 1}: {e}")
                raise

    return results


def process_lesson(
    lesson_num: int,
    pdf_label: str,
    start_page: int,
    end_page: int,
    topic: str,
    max_workers: int = 5,
    extract_only: bool = False,
) -> None:
    """Processa una singola lezione: estrazione → segmentazione → elaborazione → merge → compact."""
    lesson_id = f"lezione_micheletti_{lesson_num:02d}"
    ws = PROJECT_ROOT / "workspace" / SUBJECT / lesson_id
    ws.mkdir(parents=True, exist_ok=True)

    print(f"\n{'=' * 60}")
    print(f"  {lesson_id} ({pdf_label}) — {topic}")
    print(f"  Pagine {start_page}–{end_page}")
    print(f"{'=' * 60}\n")

    # --- STEP 1: Estrazione testo dal PDF ---
    print("--- Estrazione testo dal PDF ---")
    raw_text = extract_text_from_pdf(PDF_PATH, start_page, end_page)
    word_count = len(raw_text.split())
    print(f"  Estratte {end_page - start_page + 1} pagine, ~{word_count} parole")

    raw_path = ws / f"{lesson_id}_raw.txt"
    raw_path.write_text(raw_text, encoding="utf-8")

    if extract_only:
        print(f"  Testo salvato in: {raw_path}")
        return

    # --- STEP 2: Segmentazione LLM ---
    print("\n--- Segmentazione ---")
    segments = segment(raw_text)

    seg_dir = ws / "segmenti"
    seg_dir.mkdir(parents=True, exist_ok=True)
    for old in seg_dir.glob("segmento_*.txt"):
        old.unlink()

    for i, seg in enumerate(segments):
        seg_path = seg_dir / f"segmento_{i + 1:02d}.txt"
        seg_path.write_text(f"# {seg['titolo']}\n\n{seg['testo']}", encoding="utf-8")

    # --- STEP 3: Elaborazione parallela ---
    print("\n--- Elaborazione SSOT (parallela) ---")
    elab_dir = ws / "elaborati"
    elab_paths = elaborate_parallel(segments, SUBJECT, elab_dir, max_workers=max_workers)

    # --- STEP 4: Merge ---
    print("\n--- Fusione ---")
    sbobina_path = PROJECT_ROOT / "sbobine" / SUBJECT / f"{lesson_id}.md"
    merge_to_file(elab_paths, sbobina_path)

    # --- STEP 5: Compact ---
    print("\n--- Documento studio compatto ---")
    compact_path = PROJECT_ROOT / "sbobine" / SUBJECT / f"{lesson_id}_studio.md"
    compact_to_file(sbobina_path, compact_path, SUBJECT)

    print(f"\n  Sbobina archivio: {sbobina_path}")
    print(f"  Documento studio: {compact_path}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Rielaborazione sbobine Micheletti da PDF")
    parser.add_argument("--lesson", type=str, help="Numero lezione (es. 02, 15)")
    parser.add_argument("--all", action="store_true", help="Processa tutte le lezioni (02-23)")
    parser.add_argument("--from", dest="from_num", type=int, help="Lezione iniziale (inclusa)")
    parser.add_argument("--to", dest="to_num", type=int, help="Lezione finale (inclusa)")
    parser.add_argument("--workers", type=int, default=5, help="Workers paralleli per elaborazione (default 5)")
    parser.add_argument("--extract-only", action="store_true", help="Solo estrazione testo (no LLM)")

    args = parser.parse_args()

    if not PDF_PATH.exists():
        print(f"PDF non trovato: {PDF_PATH}")
        sys.exit(1)

    # Determina quali lezioni processare
    if args.lesson:
        num = int(args.lesson)
        lessons_to_process = [l for l in LESSONS if l[0] == num]
        if not lessons_to_process:
            print(f"Lezione {num} non trovata (range: 1-23)")
            sys.exit(1)
    elif args.all:
        # Skip lezione 01 (gia' processata da audio)
        lessons_to_process = [l for l in LESSONS if l[0] >= 2]
    elif args.from_num or args.to_num:
        start = args.from_num or 2
        end = args.to_num or 23
        lessons_to_process = [l for l in LESSONS if start <= l[0] <= end]
    else:
        parser.print_help()
        sys.exit(1)

    print(f"Lezioni da processare: {len(lessons_to_process)}")
    print(f"Workers elaborazione: {args.workers}")
    print(f"PDF: {PDF_PATH.name}")

    for lesson_num, pdf_label, start_page, end_page, topic in lessons_to_process:
        try:
            process_lesson(
                lesson_num, pdf_label, start_page, end_page, topic,
                max_workers=args.workers,
                extract_only=args.extract_only,
            )
        except Exception as e:
            print(f"\n[ERRORE] {pdf_label} (lezione_micheletti_{lesson_num:02d}): {e}")
            print("  Continuo con la prossima lezione...\n")
            continue

    print(f"\n{'=' * 60}")
    print(f"  Batch completato!")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
