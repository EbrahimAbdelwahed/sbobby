#!/usr/bin/env python3
"""
Batch indexer for unified (multi-lesson) legacy PDF sbobine.

Detects lesson boundaries via header pattern L{NN}_{date}, splits into page
ranges, and calls index_legacy functions for each lesson.

Usage:
    # Single PDF
    python scripts/batch_index_legacy.py anatomia "ANATOMIA 1_CUSELLA_2024-25.pdf"

    # All configured PDFs
    python scripts/batch_index_legacy.py --all

    # Dry-run (show boundaries only)
    python scripts/batch_index_legacy.py --dry-run anatomia "ANATOMIA 1_CUSELLA_2024-25.pdf"

    # Force re-index already indexed lessons
    python scripts/batch_index_legacy.py --force anatomia "ANATOMIA 1_CUSELLA_2024-25.pdf"
"""

import argparse
import json
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

# ---------------------------------------------------------------------------
# PDF configuration
# ---------------------------------------------------------------------------

PDF_CONFIG = {
    "ANATOMIA 1_CUSELLA_2024-25.pdf": {
        "subject": "anatomia",
        "lesson_prefix": "",
        "prof_default": "Cusella",
    },
    "Canzi 2024-2025.pdf": {
        "subject": "anatomia",
        "lesson_prefix": "canzi_",
        "prof_default": "Canzi",
        "skip_pages": [1],  # cover page
    },
    "MICHELETTI UNIFICATO.pdf": {
        "subject": "anatomia",
        "lesson_prefix": "micheletti_",
        "prof_default": "Micheletti",
    },
    "BIOCHIMICA UNIFICATO.pdf": {
        "subject": "biochimica",
        "lesson_prefix": "",
        "prof_default": "",
        "skip_pages": [1, 2],  # TOC + cover
    },
    "ISTO-CITO-EMBRIO AL UNIFICATO.pdf": {
        "subject": "istologia",
        "lesson_prefix": "",
        "embrio_prefix": "emb_",
        "prof_default": "",
    },
}

# Pattern: L01_01/10/2024 or L01_3/03/2025 (single-digit day)
BOUNDARY_RE = re.compile(r"^L(\d{2})[_\s]+(\d{1,2}/\d{2}/\d{4})")

# Professor extraction from header
PROF_RE = re.compile(
    r"PROF\.?\s*\.?S?S?A?\s+(.+?)(?:\s*\||\s*\n|$)", re.IGNORECASE
)


# ---------------------------------------------------------------------------
# Boundary detection
# ---------------------------------------------------------------------------


def detect_boundaries(pdf_path: str, config: dict) -> list[dict]:
    """Scan PDF pages and detect lesson boundaries.

    Returns list of dicts:
        {"lesson_num": int, "date": str, "page_start": int, "page_end": int,
         "lesson_id": str, "prof": str, "is_embrio": bool}
    """
    import pdfplumber

    skip_pages = set(config.get("skip_pages", []))
    boundaries = []

    with pdfplumber.open(pdf_path) as pdf:
        total = len(pdf.pages)
        for page_idx, page in enumerate(pdf.pages):
            page_num = page_idx + 1
            if page_num in skip_pages:
                continue

            text = page.extract_text() or ""
            first_chars = text[:500]

            m = BOUNDARY_RE.search(first_chars)
            if m:
                lesson_num = int(m.group(1))
                date = m.group(2)

                # Detect professor from header
                prof = config.get("prof_default", "")
                pm = PROF_RE.search(first_chars)
                if pm:
                    prof = pm.group(1).strip().rstrip(",.")

                # Detect embriologia
                is_embrio = "EMBRIOLOGIA" in first_chars.upper()

                # Determine lesson_id prefix
                if is_embrio and config.get("embrio_prefix"):
                    prefix = config["embrio_prefix"]
                else:
                    prefix = config.get("lesson_prefix", "")

                lesson_id = f"{prefix}L{lesson_num:02d}"

                boundaries.append({
                    "lesson_num": lesson_num,
                    "date": date,
                    "page_start": page_num,
                    "page_end": None,  # filled later
                    "lesson_id": lesson_id,
                    "prof": prof,
                    "is_embrio": is_embrio,
                })

        # Fill page_end: each lesson ends at the page before the next lesson starts
        for i in range(len(boundaries)):
            if i + 1 < len(boundaries):
                boundaries[i]["page_end"] = boundaries[i + 1]["page_start"] - 1
            else:
                boundaries[i]["page_end"] = total

    # Deduplicate lesson IDs: append suffix _b, _c etc. for collisions
    seen: dict[str, int] = {}
    for b in boundaries:
        lid = b["lesson_id"]
        if lid in seen:
            seen[lid] += 1
            suffix = chr(ord("a") + seen[lid])  # b, c, d...
            b["lesson_id"] = f"{lid}{suffix}"
        else:
            seen[lid] = 0

    return boundaries


# ---------------------------------------------------------------------------
# Index check (resume support)
# ---------------------------------------------------------------------------


def get_indexed_lessons(subject: str) -> set[str]:
    """Return set of lesson IDs already in the index."""
    index_path = PROJECT_ROOT / "legacy_index" / f"{subject}.json"
    if not index_path.exists():
        return set()
    with open(index_path, "r", encoding="utf-8") as f:
        index = json.load(f)
    return {lesson["id"] for lesson in index.get("lessons", [])}


# ---------------------------------------------------------------------------
# Process single lesson
# ---------------------------------------------------------------------------


def index_lesson(
    pdf_path: str,
    subject: str,
    lesson_id: str,
    date: str,
    prof: str,
    page_start: int,
    page_end: int,
) -> None:
    """Run the full index_legacy pipeline for a single lesson page range."""
    from index_legacy import (
        extract_text_with_hints,
        classify_hierarchy,
        extract_images,
        associate_images_to_blocks,
        compute_semantic_signatures,
        caption_images_with_vision,
        embed_blocks_and_figures,
        build_lesson_index,
        save_index,
    )

    print(f"\n{'='*70}")
    print(f"[batch] Indexing {lesson_id} — pages {page_start}-{page_end}")
    print(f"[batch] Subject: {subject} | Date: {date} | Prof: {prof}")
    print(f"{'='*70}\n")

    # Step 1: Text extraction
    print("[batch] --- Step 1: Text extraction ---")
    pages_data = extract_text_with_hints(pdf_path, page_start, page_end)
    total_lines = sum(len(p["lines"]) for p in pages_data)
    print(f"[batch] Extracted {total_lines} lines from {len(pages_data)} pages.\n")

    # Step 2: Hierarchy classification
    print("[batch] --- Step 2: Hierarchy classification ---")
    blocks = classify_hierarchy(pages_data)
    level_counts = {}
    for b in blocks:
        level_counts[b["level"]] = level_counts.get(b["level"], 0) + 1
    print(f"[batch] Classified {len(blocks)} blocks: {level_counts}\n")

    # Step 3: Image extraction
    print("[batch] --- Step 3: Image extraction ---")
    images = extract_images(pdf_path, subject, lesson_id, page_start, page_end)
    print()

    # Step 4: Image-block association
    print("[batch] --- Step 4: Image-block association ---")
    blocks = associate_images_to_blocks(blocks, images, pages_data)
    img_assigned = sum(len(b.get("figures", [])) for b in blocks)
    print(f"[batch] Assigned {img_assigned} images to blocks.\n")

    # Step 5: Semantic signatures
    print("[batch] --- Step 5: Semantic signatures ---")
    blocks = compute_semantic_signatures(blocks, pages_data)
    captioned = sum(
        1
        for b in blocks
        for f in b.get("figures", [])
        if f.get("has_caption")
    )
    print(f"[batch] {captioned}/{img_assigned} images have captions.\n")

    # Step 5b: Visual captioning
    print("[batch] --- Step 5b: Visual captioning ---")
    blocks = caption_images_with_vision(blocks)
    print()

    # Step 6: Embeddings
    print("[batch] --- Step 6: Computing embeddings ---")
    blocks = embed_blocks_and_figures(blocks)
    print()

    # Step 7: Save index
    print("[batch] --- Step 7: Saving index ---")
    lesson_data = build_lesson_index(
        blocks,
        subject=subject,
        lesson_id=lesson_id,
        source_pdf=pdf_path,
        date=date,
        prof=prof,
    )
    save_index(lesson_data, subject)
    print(f"[batch] Done: {lesson_id}\n")


# ---------------------------------------------------------------------------
# Process single PDF
# ---------------------------------------------------------------------------


def process_pdf(pdf_name: str, config: dict, dry_run: bool = False, force: bool = False) -> None:
    """Detect boundaries and index all lessons in a unified PDF."""
    pdf_path = str((PROJECT_ROOT / pdf_name).resolve())
    if not Path(pdf_path).exists():
        print(f"[batch] ERROR: File not found: {pdf_path}")
        return

    subject = config["subject"]
    print(f"\n{'#'*70}")
    print(f"[batch] PDF: {pdf_name}")
    print(f"[batch] Subject: {subject}")
    print(f"{'#'*70}\n")

    # Detect lesson boundaries
    boundaries = detect_boundaries(pdf_path, config)
    if not boundaries:
        print("[batch] WARNING: No lesson boundaries detected!")
        return

    print(f"[batch] Detected {len(boundaries)} lessons:\n")
    for b in boundaries:
        embrio_tag = " [EMBRIOLOGIA]" if b["is_embrio"] else ""
        print(
            f"  {b['lesson_id']:20s}  pages {b['page_start']:4d}-{b['page_end']:4d}  "
            f"({b['page_end'] - b['page_start'] + 1:3d} pp)  "
            f"date={b['date']:10s}  prof={b['prof']}{embrio_tag}"
        )
    print()

    if dry_run:
        print("[batch] Dry-run mode — skipping indexing.")
        return

    # Resume support: check which lessons are already indexed
    indexed = get_indexed_lessons(subject)
    skipped = 0

    for b in boundaries:
        if b["lesson_id"] in indexed and not force:
            print(f"[batch] Skipping {b['lesson_id']} (already indexed, use --force to re-index)")
            skipped += 1
            continue

        index_lesson(
            pdf_path=pdf_path,
            subject=subject,
            lesson_id=b["lesson_id"],
            date=b["date"],
            prof=b["prof"],
            page_start=b["page_start"],
            page_end=b["page_end"],
        )

    total = len(boundaries)
    processed = total - skipped
    print(f"\n[batch] === PDF complete: {pdf_name} ===")
    print(f"[batch] {processed} lessons indexed, {skipped} skipped (already in index).")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(
        description="Batch index unified (multi-lesson) legacy PDF sbobine."
    )
    parser.add_argument("subject", nargs="?", help="Subject name (e.g. anatomia)")
    parser.add_argument("pdf_name", nargs="?", help="PDF filename (must be in PDF_CONFIG)")
    parser.add_argument("--all", action="store_true", help="Process all configured PDFs")
    parser.add_argument("--dry-run", action="store_true", help="Show boundaries without indexing")
    parser.add_argument("--force", action="store_true", help="Re-index already indexed lessons")
    args = parser.parse_args()

    if args.all:
        for pdf_name, config in PDF_CONFIG.items():
            process_pdf(pdf_name, config, dry_run=args.dry_run, force=args.force)
    elif args.pdf_name:
        if args.pdf_name not in PDF_CONFIG:
            print(f"[batch] ERROR: '{args.pdf_name}' not in PDF_CONFIG.")
            print(f"[batch] Available PDFs: {', '.join(PDF_CONFIG.keys())}")
            sys.exit(1)
        config = PDF_CONFIG[args.pdf_name]
        if args.subject and args.subject != config["subject"]:
            print(f"[batch] WARNING: subject arg '{args.subject}' overridden by config '{config['subject']}'")
        process_pdf(args.pdf_name, config, dry_run=args.dry_run, force=args.force)
    else:
        parser.print_help()
        print("\nConfigured PDFs:")
        for name, cfg in PDF_CONFIG.items():
            print(f"  {name:45s}  subject={cfg['subject']}")
        sys.exit(1)


if __name__ == "__main__":
    main()
