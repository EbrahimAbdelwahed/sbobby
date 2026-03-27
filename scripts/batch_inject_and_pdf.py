#!/usr/bin/env python3
"""
Batch inject images + generate PDFs for all available studio lessons.

Usage:
    python scripts/batch_inject_and_pdf.py              # all studio lessons
    python scripts/batch_inject_and_pdf.py anatomia      # single subject
    python scripts/batch_inject_and_pdf.py --dry-run     # list lessons only
    python scripts/batch_inject_and_pdf.py --pdf-only    # skip injection, just generate PDFs
"""

import argparse
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from inject_images import inject_images
from generate_pdf import generate_pdf_for_pipeline


THRESHOLD = 0.65  # calibrated threshold


def find_studio_lessons(subject_filter: str = None) -> list[tuple[str, str]]:
    """Find all *_studio.md files. Returns list of (subject, lesson_name)."""
    sbobine_dir = PROJECT_ROOT / "sbobine"
    lessons = []
    for subject_dir in sorted(sbobine_dir.iterdir()):
        if not subject_dir.is_dir() or subject_dir.name == "strutture":
            continue
        if subject_filter and subject_dir.name != subject_filter:
            continue
        for md_file in sorted(subject_dir.glob("*_studio.md")):
            lesson_name = md_file.stem  # e.g., lezione_01_studio
            lessons.append((subject_dir.name, lesson_name))
    return lessons


def main():
    parser = argparse.ArgumentParser(
        description="Batch inject images and generate PDFs for studio lessons."
    )
    parser.add_argument("subject", nargs="?", help="Filter by subject (e.g., anatomia)")
    parser.add_argument("--dry-run", action="store_true", help="List lessons only")
    parser.add_argument("--pdf-only", action="store_true", help="Skip injection, just generate PDFs")
    parser.add_argument("--threshold", type=float, default=THRESHOLD,
                        help=f"Similarity threshold (default: {THRESHOLD})")
    parser.add_argument("--diagnostic", action="store_true",
                        help="Generate diagnostic.json for each lesson")
    args = parser.parse_args()

    lessons = find_studio_lessons(args.subject)
    if not lessons:
        print("[batch] No studio lessons found.")
        sys.exit(1)

    print(f"[batch] Found {len(lessons)} studio lessons:\n")
    for subj, lesson in lessons:
        print(f"  {subj:15s}  {lesson}")
    print()

    if args.dry_run:
        return

    results = {"injected": [], "pdf_ok": [], "inject_fail": [], "pdf_fail": []}
    t0 = time.time()

    # Pre-load legacy indices to avoid reloading per-lesson
    # (inject_images loads it each time, but the JSON is cached by OS)

    for i, (subj, lesson) in enumerate(lessons, 1):
        print(f"\n{'='*70}")
        print(f"[batch] [{i}/{len(lessons)}] {subj}/{lesson}")
        print(f"{'='*70}\n")

        injected_path = None

        if not args.pdf_only:
            # --- Inject ---
            try:
                injected_path = inject_images(
                    subject=subj,
                    lesson=lesson,
                    threshold=args.threshold,
                    output_suffix="_test",
                    diagnostic=args.diagnostic,
                )
                if injected_path:
                    results["injected"].append(f"{subj}/{lesson}")
                else:
                    results["inject_fail"].append(f"{subj}/{lesson} (no matches)")
            except Exception as e:
                print(f"[batch] ERROR injecting {subj}/{lesson}: {e}")
                results["inject_fail"].append(f"{subj}/{lesson} ({e})")
                continue

        # --- Generate PDF ---
        # Use the injected file if available, otherwise the original studio file
        if injected_path is None and not args.pdf_only:
            # Injection returned None (no matches) — generate PDF from original
            input_path = PROJECT_ROOT / "sbobine" / subj / f"{lesson}.md"
        elif args.pdf_only:
            # Check for _test.md first (previously injected), then original
            test_path = PROJECT_ROOT / "sbobine" / subj / f"{lesson}_test.md"
            input_path = test_path if test_path.exists() else PROJECT_ROOT / "sbobine" / subj / f"{lesson}.md"
        else:
            input_path = injected_path

        try:
            pdf_path = generate_pdf_for_pipeline(
                subject=subj,
                lesson=lesson,
                input_path=input_path,
            )
            if pdf_path:
                results["pdf_ok"].append(f"{subj}/{lesson}")
            else:
                results["pdf_fail"].append(f"{subj}/{lesson}")
        except Exception as e:
            print(f"[batch] ERROR generating PDF {subj}/{lesson}: {e}")
            results["pdf_fail"].append(f"{subj}/{lesson} ({e})")

    # --- Summary ---
    elapsed = time.time() - t0
    print(f"\n{'#'*70}")
    print(f"[batch] DONE in {elapsed:.0f}s")
    print(f"[batch] Injected: {len(results['injected'])}/{len(lessons)}")
    print(f"[batch] PDFs OK:  {len(results['pdf_ok'])}/{len(lessons)}")
    if results["inject_fail"]:
        print(f"[batch] Inject failures:")
        for f in results["inject_fail"]:
            print(f"  - {f}")
    if results["pdf_fail"]:
        print(f"[batch] PDF failures:")
        for f in results["pdf_fail"]:
            print(f"  - {f}")
    print(f"{'#'*70}")


if __name__ == "__main__":
    main()
