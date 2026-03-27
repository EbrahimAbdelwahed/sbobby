#!/usr/bin/env python3
"""
Phase 1 — Legacy PDF Image Indexer

Extracts text hierarchy, images, and embeddings from legacy sbobina PDFs.
Produces a JSON index for downstream image injection into new sbobine.

Usage:
    python scripts/index_legacy.py <subject> <pdf_path> [--lesson-id L05] [--date "08/10/2024"] [--prof "Cusella"]
"""

import argparse
import hashlib
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from api_client import chat  # noqa: E402

# ---------------------------------------------------------------------------
# OpenRouter embedding client (lazy init)
# ---------------------------------------------------------------------------

_openrouter_client = None
EMBEDDING_MODEL = "openai/text-embedding-3-large"


def _get_openrouter():
    global _openrouter_client
    if _openrouter_client is None:
        from openai import OpenAI

        key = os.environ.get("OPENROUTER_API_KEY")
        if not key:
            raise ValueError("Imposta la variabile d'ambiente OPENROUTER_API_KEY")
        _openrouter_client = OpenAI(
            base_url="https://openrouter.ai/api/v1", api_key=key
        )
    return _openrouter_client


def _embed_single_batch(client, batch: list[str]) -> list[list[float]]:
    """Embed a single batch with retry on 429."""
    batch = [t if t.strip() else "empty" for t in batch]
    retries = 0
    while True:
        try:
            resp = client.embeddings.create(model=EMBEDDING_MODEL, input=batch)
            return [d.embedding for d in resp.data]
        except Exception as e:
            err_str = str(e)
            if "429" in err_str and retries < 5:
                wait = 2 ** retries
                print(f"[index] Rate limit, attendo {wait}s...")
                time.sleep(wait)
                retries += 1
            else:
                raise


def compute_embeddings(texts: list[str], batch_size: int = 20) -> list[list[float]]:
    """Compute embeddings via OpenRouter, batching with parallel workers."""
    from concurrent.futures import ThreadPoolExecutor

    client = _get_openrouter()
    batches = []
    for i in range(0, len(texts), batch_size):
        batches.append(texts[i : i + batch_size])

    if len(batches) <= 1:
        # Single batch, no need for threading
        return _embed_single_batch(client, batches[0]) if batches else []

    all_embeddings: list[list[float]] = [[] for _ in batches]
    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = {pool.submit(_embed_single_batch, client, b): idx for idx, b in enumerate(batches)}
        for future in futures:
            idx = futures[future]
            all_embeddings[idx] = future.result()

    # Flatten in order
    return [emb for batch_embs in all_embeddings for emb in batch_embs]


# ---------------------------------------------------------------------------
# Step 1 — Text extraction with pdfplumber
# ---------------------------------------------------------------------------


def extract_text_with_hints(
    pdf_path: str, page_start: int | None = None, page_end: int | None = None
) -> list[dict]:
    """Extract text from each page with font metadata hints.

    Args:
        pdf_path: Path to PDF file.
        page_start: First page to process (1-based, inclusive). None = first page.
        page_end: Last page to process (1-based, inclusive). None = last page.

    Returns a list of dicts, one per page:
        {"page": int, "lines": [{"text": str, "hint": str, "y_top": float, "y_bottom": float}]}
    """
    import pdfplumber

    pages_data = []
    with pdfplumber.open(pdf_path) as pdf:
        total = len(pdf.pages)
        start = (page_start or 1) - 1  # convert to 0-based
        end = page_end or total
        selected = pdf.pages[start:end]
        for i, page in enumerate(selected):
            page_num = start + i + 1  # 1-based page number
            print(f"[index] Extracting text from page {page_num}/{total}...")
            lines = _extract_page_lines(page)
            pages_data.append({"page": page_num, "lines": lines})
    return pages_data


def _extract_page_lines(page) -> list[dict]:
    """Group chars into lines and determine formatting hints."""
    chars = page.chars
    if not chars:
        return []

    # Sort chars by vertical then horizontal position
    chars_sorted = sorted(chars, key=lambda c: (round(float(c["top"]), 1), float(c["x0"])))

    # Group into lines by y-proximity (within 3pt)
    lines = []
    current_line_chars = [chars_sorted[0]]
    for ch in chars_sorted[1:]:
        if abs(float(ch["top"]) - float(current_line_chars[-1]["top"])) < 3:
            current_line_chars.append(ch)
        else:
            lines.append(_build_line(current_line_chars))
            current_line_chars = [ch]
    if current_line_chars:
        lines.append(_build_line(current_line_chars))

    return lines


def _build_line(chars: list[dict]) -> dict:
    """Build a line dict from a group of characters."""
    # Join chars, inserting spaces where there's a gap between glyphs
    parts = [chars[0]["text"]]
    for prev, cur in zip(chars, chars[1:]):
        gap = float(cur["x0"]) - float(prev.get("x1", prev["x0"]))
        avg_width = float(cur.get("width", float(cur.get("size", 10)) * 0.5))
        # If gap > 30% of average char width, insert a space
        if gap > max(avg_width * 0.3, 1.5) and not prev["text"].endswith(" "):
            parts.append(" ")
        parts.append(cur["text"])
    text = "".join(parts).strip()
    y_top = min(float(c["top"]) for c in chars)
    y_bottom = max(float(c["bottom"]) for c in chars)

    # Determine formatting hint
    fontnames = [c.get("fontname", "") for c in chars if c["text"].strip()]
    sizes = [float(c.get("size", 12)) for c in chars if c["text"].strip()]

    is_bold = any("Bold" in fn or "bold" in fn or "BD" in fn for fn in fontnames) if fontnames else False
    avg_size = sum(sizes) / len(sizes) if sizes else 12.0
    is_large = avg_size > 13.0
    is_upper = text == text.upper() and len(text) > 3 and text.strip()

    if is_bold and is_upper:
        hint = "BOLD_UPPERCASE"
    elif is_bold:
        hint = "BOLD"
    elif is_large:
        hint = "LARGE"
    elif is_upper and len(text) > 5:
        hint = "UPPERCASE"
    else:
        hint = "NORMAL"

    return {"text": text, "hint": hint, "y_top": y_top, "y_bottom": y_bottom}


# ---------------------------------------------------------------------------
# Step 2 — LLM hierarchy classification
# ---------------------------------------------------------------------------

HIERARCHY_PROMPT = """\
Sei un parser di sbobine mediche. Ricevi il testo di una pagina PDF con hint tipografici.
Classifica il testo in blocchi gerarchici:
- L1: argomento principale (es. "ARTICOLAZIONE DELLA SPALLA")
- L2: sotto-argomento (es. "Superfici articolari")
- L3: dettaglio (es. "Capsula fibrosa")
- body: testo ordinario

Rispondi SOLO con JSON valido, formato:
[{"level": "L1"|"L2"|"L3"|"body", "title": "..." (solo per L1/L2/L3), "text": "contenuto completo..."}]

Hint tipografici per ogni riga:
- BOLD UPPERCASE = probabile L1
- Bold mixed case = probabile L2
- Bold lowercase = probabile L2 o L3
- Normal text = body

Ma la formattazione è inconsistente: usa il CONTENUTO SEMANTICO come guida principale.
"""


def _classify_batch(batch: list[dict], total_pages: int) -> list[dict]:
    """Classify a single batch of pages (used by thread pool)."""
    page_range = f"{batch[0]['page']}-{batch[-1]['page']}"
    print(f"[index] Classifying hierarchy for pages {page_range}/{total_pages}...")
    input_text = _format_pages_for_llm(batch)
    if not input_text.strip():
        return []
    return _call_llm_classify(input_text, batch)


def classify_hierarchy(pages_data: list[dict], batch_size: int = 4) -> list[dict]:
    """Send pages to LLM in batches for hierarchy classification.

    Returns flat list of blocks: {"level", "title" (optional), "text", "page", "y_top", "y_bottom"}
    """
    from concurrent.futures import ThreadPoolExecutor, as_completed

    total_pages = len(pages_data)
    batches = []
    for i in range(0, total_pages, batch_size):
        batches.append(pages_data[i : i + batch_size])

    if len(batches) <= 1:
        blocks = _classify_batch(batches[0], total_pages) if batches else []
        return _merge_body_into_l2(blocks)

    # Parallel classification, preserve order
    results: list[list[dict]] = [[] for _ in batches]
    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = {pool.submit(_classify_batch, b, total_pages): idx for idx, b in enumerate(batches)}
        for future in as_completed(futures):
            idx = futures[future]
            results[idx] = future.result()

    all_blocks = [block for batch_blocks in results for block in batch_blocks]

    # Merge consecutive body blocks into nearest L2 above
    merged = _merge_body_into_l2(all_blocks)
    return merged


def _format_pages_for_llm(batch: list[dict]) -> str:
    """Format pages as text with hints for the LLM."""
    parts = []
    for page_data in batch:
        parts.append(f"--- PAGINA {page_data['page']} ---")
        for line in page_data["lines"]:
            if line["text"]:
                parts.append(f"[{line['hint']}] {line['text']}")
    return "\n".join(parts)


def _call_llm_classify(input_text: str, batch: list[dict], max_retries: int = 3) -> list[dict]:
    """Call LLM to classify text blocks, with JSON parsing retry."""
    messages = [
        {"role": "system", "content": HIERARCHY_PROMPT},
        {"role": "user", "content": input_text},
    ]

    for attempt in range(max_retries):
        try:
            response = chat(messages, temperature=0.1, max_tokens=8192)
            blocks = _parse_llm_json(response)
            # Attach page/position metadata (approximate: use first page in batch)
            _attach_positions(blocks, batch)
            return blocks
        except (json.JSONDecodeError, ValueError) as e:
            if attempt < max_retries - 1:
                print(f"[index] JSON parsing error (attempt {attempt+1}), retrying...")
                messages.append({"role": "assistant", "content": response})
                messages.append(
                    {
                        "role": "user",
                        "content": "Errore di parsing. Rispondi SOLO con JSON valido, senza testo aggiuntivo.",
                    }
                )
            else:
                print(f"[index] WARNING: Could not parse LLM response after {max_retries} attempts: {e}")
                # Fallback: treat entire batch as a single body block
                all_text = "\n".join(
                    line["text"]
                    for p in batch
                    for line in p["lines"]
                    if line["text"]
                )
                return [
                    {
                        "level": "body",
                        "text": all_text,
                        "page": batch[0]["page"],
                        "y_top": 0,
                        "y_bottom": 0,
                    }
                ]
    return []


def _parse_llm_json(response: str) -> list[dict]:
    """Extract JSON array from LLM response."""
    # Try to find JSON array in the response
    text = response.strip()
    # Remove markdown code fences if present
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*\n?", "", text)
        text = re.sub(r"\n?```\s*$", "", text)

    # Find the JSON array
    start = text.find("[")
    end = text.rfind("]")
    if start == -1 or end == -1:
        raise json.JSONDecodeError("No JSON array found", text, 0)

    blocks = json.loads(text[start : end + 1])
    if not isinstance(blocks, list):
        raise ValueError("Expected JSON array")
    return blocks


def _attach_positions(blocks: list[dict], batch: list[dict]):
    """Attach approximate page and y-position to classified blocks."""
    # Build a flat list of lines across all pages in the batch
    all_lines = []
    for page_data in batch:
        for line in page_data["lines"]:
            all_lines.append({"page": page_data["page"], **line})

    line_idx = 0
    for block in blocks:
        block_text = block.get("text", "") or block.get("title", "")
        if not block_text:
            block["page"] = batch[0]["page"]
            block["y_top"] = 0
            block["y_bottom"] = 0
            continue

        # Find best matching line by text overlap
        best_idx = line_idx
        best_score = 0
        search_end = min(line_idx + 30, len(all_lines))
        first_words = block_text[:60].lower()

        for j in range(line_idx, search_end):
            score = _text_overlap(first_words, all_lines[j]["text"].lower())
            if score > best_score:
                best_score = score
                best_idx = j

        if best_idx < len(all_lines):
            matched = all_lines[best_idx]
            block["page"] = matched["page"]
            block["y_top"] = matched["y_top"]
            block["y_bottom"] = matched["y_bottom"]
            line_idx = best_idx + 1
        else:
            block["page"] = batch[-1]["page"]
            block["y_top"] = 0
            block["y_bottom"] = 0


def _text_overlap(a: str, b: str) -> float:
    """Simple word overlap ratio."""
    words_a = set(a.split())
    words_b = set(b.split())
    if not words_a:
        return 0.0
    return len(words_a & words_b) / len(words_a)


def _merge_body_into_l2(blocks: list[dict]) -> list[dict]:
    """Merge consecutive body blocks into the nearest L2 block above them."""
    if not blocks:
        return blocks

    merged = []
    for block in blocks:
        if block["level"] == "body":
            # Find nearest L2 or L3 above to append to
            target = None
            for prev in reversed(merged):
                if prev["level"] in ("L2", "L3"):
                    target = prev
                    break
            if target is not None:
                target["text"] = target.get("text", "") + "\n" + block.get("text", "")
            else:
                # No L2/L3 above; keep as standalone
                merged.append(block)
        else:
            merged.append(block)

    return merged


# ---------------------------------------------------------------------------
# Step 3 — Image extraction with PyMuPDF
# ---------------------------------------------------------------------------


def extract_images(
    pdf_path: str,
    subject: str,
    lesson_id: str,
    page_start: int | None = None,
    page_end: int | None = None,
) -> list[dict]:
    """Extract raster images from PDF, save as PNG, return metadata.

    Args:
        page_start: First page to process (1-based, inclusive). None = first page.
        page_end: Last page to process (1-based, inclusive). None = last page.
    """
    import fitz

    output_dir = PROJECT_ROOT / "legacy_images" / subject / lesson_id
    output_dir.mkdir(parents=True, exist_ok=True)

    doc = fitz.open(pdf_path)
    all_images = []
    total_pages = len(doc)
    start_0 = (page_start or 1) - 1  # 0-based
    end_0 = page_end or total_pages    # exclusive for range()

    for page_num in range(start_0, end_0):
        page = doc[page_num]
        page_width = page.rect.width
        image_list = page.get_images(full=True)

        print(f"[index] Extracting images from page {page_num+1}/{total_pages} ({len(image_list)} images)...")

        for idx, img_info in enumerate(image_list):
            xref = img_info[0]
            try:
                base_image = doc.extract_image(xref)
            except Exception as e:
                print(f"[index] WARNING: Could not extract image xref={xref} on page {page_num+1}: {e}")
                continue

            if not base_image or not base_image.get("image"):
                continue

            image_bytes = base_image["image"]
            img_width = base_image.get("width", 0)
            img_height = base_image.get("height", 0)

            if img_width < 20 or img_height < 20:
                continue  # Skip tiny images (decorative)

            # Determine position on page (approximate via image rects)
            bbox = _find_image_bbox(page, xref)

            # Size class
            width_ratio = img_width / page_width if page_width > 0 else 0.5
            if width_ratio < 0.3:
                size_class = "small"
            elif width_ratio < 0.6:
                size_class = "medium"
            else:
                size_class = "large"

            aspect_ratio = round(img_width / img_height, 2) if img_height > 0 else 1.0

            # Save image
            content_hash = hashlib.sha256(image_bytes).hexdigest()[:16]
            filename = f"img_p{page_num+1}_{idx}.png"
            filepath = output_dir / filename
            _save_as_png(image_bytes, base_image.get("ext", "png"), filepath)

            rel_path = str(filepath.relative_to(PROJECT_ROOT))
            all_images.append(
                {
                    "file": rel_path,
                    "content_hash": content_hash,
                    "page": page_num + 1,
                    "bbox": bbox,
                    "size_class": size_class,
                    "aspect_ratio": aspect_ratio,
                    "img_width": img_width,
                    "img_height": img_height,
                }
            )

    doc.close()
    print(f"[index] Extracted {len(all_images)} images total.")
    return all_images


def _find_image_bbox(page, xref: int) -> list[float]:
    """Find the bounding box of an image on a page by xref."""
    # Search in page's image instances
    for img_instance in page.get_image_rects(xref):
        return [
            round(img_instance.x0, 1),
            round(img_instance.y0, 1),
            round(img_instance.x1, 1),
            round(img_instance.y1, 1),
        ]
    # Fallback: unknown position
    return [0, 0, 0, 0]


def _save_as_png(image_bytes: bytes, ext: str, filepath: Path):
    """Save image bytes as PNG, converting if needed."""
    from PIL import Image
    import io

    try:
        img = Image.open(io.BytesIO(image_bytes))
        img.save(str(filepath), "PNG")
    except Exception:
        # If PIL fails, just write raw bytes (may already be PNG)
        filepath.write_bytes(image_bytes)


# ---------------------------------------------------------------------------
# Step 4 — Associate images to L2 blocks
# ---------------------------------------------------------------------------


def associate_images_to_blocks(
    blocks: list[dict], images: list[dict], pages_data: list[dict]
) -> list[dict]:
    """Assign each image to the L2 block active at its vertical position."""
    if not images:
        return blocks

    # Build a linearized sequence of block boundaries: (page, y_top, block_index)
    block_spans = []
    for i, block in enumerate(blocks):
        if block["level"] in ("L1", "L2", "L3"):
            block_spans.append((block.get("page", 0), block.get("y_top", 0), i))

    # Ensure figures lists exist
    for block in blocks:
        if "figures" not in block:
            block["figures"] = []

    for img in images:
        img_page = img["page"]
        img_y = img["bbox"][1] if img["bbox"][1] > 0 else 0

        # Find the block that's "active" at this image position
        # (the last block whose start is before or at the image position)
        best_block_idx = None
        for page_num, y_top, block_idx in block_spans:
            if (page_num < img_page) or (page_num == img_page and y_top <= img_y + 10):
                best_block_idx = block_idx

        # If we found a heading block, walk up to find nearest L2
        if best_block_idx is not None:
            target_idx = _find_nearest_l2(blocks, best_block_idx)
            if target_idx is not None:
                blocks[target_idx]["figures"].append(img)
            else:
                # Attach to the block itself
                blocks[best_block_idx]["figures"].append(img)
        elif blocks:
            # No matching block found; attach to first L2 or first block
            target_idx = _find_nearest_l2(blocks, 0) or 0
            blocks[target_idx]["figures"].append(img)

    return blocks


def _find_nearest_l2(blocks: list[dict], start_idx: int) -> int | None:
    """From start_idx, search backward for the nearest L2 block."""
    for i in range(start_idx, -1, -1):
        if blocks[i]["level"] == "L2":
            return i
    # If no L2 found, search forward
    for i in range(start_idx, len(blocks)):
        if blocks[i]["level"] == "L2":
            return i
    return None


# ---------------------------------------------------------------------------
# Step 5 — Semantic signatures
# ---------------------------------------------------------------------------

VISION_MODEL = "google/gemini-3.1-flash-lite-preview"

CAPTION_RE = re.compile(
    r"(?:Figura|Fig\.?|Figure|Immagine)\s*\d+[.:\-—–]?\s*.*",
    re.IGNORECASE,
)


def compute_semantic_signatures(
    blocks: list[dict], pages_data: list[dict]
) -> list[dict]:
    """For each image in blocks, compute caption + context = semantic_signature."""
    # Build a flat text index: list of (page, y_center, text_line)
    flat_lines = []
    for page_data in pages_data:
        for line in page_data["lines"]:
            y_center = (line["y_top"] + line["y_bottom"]) / 2
            flat_lines.append((page_data["page"], y_center, line["text"]))

    for block in blocks:
        for fig in block.get("figures", []):
            fig_page = fig["page"]
            fig_y_center = (fig["bbox"][1] + fig["bbox"][3]) / 2 if fig["bbox"][3] > 0 else 0

            # Find nearby lines (same page, within 300px vertical)
            nearby = []
            fig_line_idx = None
            for idx, (pg, yc, text) in enumerate(flat_lines):
                if pg == fig_page and abs(yc - fig_y_center) < 300:
                    nearby.append(text)
                    if fig_line_idx is None or abs(yc - fig_y_center) < abs(
                        flat_lines[fig_line_idx][1] - fig_y_center
                    ):
                        fig_line_idx = idx

            # Also grab 5 lines before/after by index
            if fig_line_idx is not None:
                start = max(0, fig_line_idx - 5)
                end = min(len(flat_lines), fig_line_idx + 6)
                context_lines = [flat_lines[j][2] for j in range(start, end)]
            else:
                context_lines = nearby[:10]

            # Search for caption
            caption = ""
            has_caption = False
            all_nearby_text = nearby + context_lines
            for line_text in all_nearby_text:
                m = CAPTION_RE.search(line_text)
                if m:
                    caption = m.group(0).strip()
                    has_caption = True
                    break

            # Build semantic signature
            context_text = "\n".join(dict.fromkeys(context_lines))  # deduplicate preserving order
            signature = f"{caption}\n{context_text}".strip() if caption else context_text.strip()

            fig["caption"] = caption
            fig["has_caption"] = has_caption
            fig["semantic_signature"] = signature

    return blocks


# ---------------------------------------------------------------------------
# Step 5b — Visual captioning with Gemini Flash Lite
# ---------------------------------------------------------------------------


VISION_PROMPT = (
    "Descrivi brevemente questa immagine tratta da un testo universitario di medicina. "
    "Cosa rappresenta? Includi strutture anatomiche, grafici, diagrammi o schemi visibili. "
    "Rispondi in italiano, massimo 2-3 frasi."
)


def _caption_single_image(client, fig: dict, img_path: str, idx: int, total: int) -> None:
    """Caption a single image with vision model (used by thread pool)."""
    import base64

    print(f"[index]   [{idx}/{total}] {Path(img_path).name}...", end=" ", flush=True)
    try:
        with open(img_path, "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode("utf-8")

        resp = client.chat.completions.create(
            model=VISION_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{img_b64}",
                            },
                        },
                        {"type": "text", "text": VISION_PROMPT},
                    ],
                }
            ],
            max_tokens=300,
            temperature=0.2,
        )
        caption = resp.choices[0].message.content.strip()
        fig["visual_caption"] = caption
        existing_sig = fig.get("semantic_signature", "")
        fig["semantic_signature"] = (
            f"{existing_sig}\n[Contenuto visuale: {caption}]" if existing_sig
            else f"[Contenuto visuale: {caption}]"
        )
        display = caption[:80] + "..." if len(caption) > 80 else caption
        print(f"OK — {display}")
    except Exception as e:
        print(f"ERRORE — {e}")
        fig["visual_caption"] = ""


def caption_images_with_vision(blocks: list[dict]) -> list[dict]:
    """Generate visual captions for each figure using a vision model.

    Sends each image to Gemini Flash Lite via OpenRouter with parallel workers.
    Stores the caption in fig['visual_caption'] and appends to fig['semantic_signature'].
    """
    from concurrent.futures import ThreadPoolExecutor, as_completed

    all_figs: list[tuple[dict, str]] = []
    for block in blocks:
        for fig in block.get("figures", []):
            img_path = PROJECT_ROOT / fig["file"]
            if img_path.exists():
                all_figs.append((fig, str(img_path)))

    if not all_figs:
        print("[index] No images to caption.")
        return blocks

    total = len(all_figs)
    print(f"[index] Captioning {total} images with {VISION_MODEL}...")
    client = _get_openrouter()

    with ThreadPoolExecutor(max_workers=10) as pool:
        futures = []
        for i, (fig, img_path) in enumerate(all_figs, 1):
            futures.append(pool.submit(_caption_single_image, client, fig, img_path, i, total))
        for future in as_completed(futures):
            future.result()  # propagate exceptions

    captioned = sum(1 for fig, _ in all_figs if fig.get("visual_caption"))
    print(f"[index] {captioned}/{total} images captioned successfully.")
    return blocks


# ---------------------------------------------------------------------------
# Step 6 — Compute embeddings for blocks and figures
# ---------------------------------------------------------------------------


def _first_n_sentences(text: str, n: int = 3) -> str:
    """Extract approximately the first n sentences from text."""
    if not text:
        return ""
    # Split on sentence-ending punctuation
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    return " ".join(sentences[:n]).strip()


def embed_blocks_and_figures(blocks: list[dict]) -> list[dict]:
    """Compute embeddings for L2/L3 block text and figure signatures."""
    # Collect texts to embed
    embed_tasks = []  # (block_idx, field, text)

    for i, block in enumerate(blocks):
        if block["level"] in ("L2", "L3"):
            text_3s = _first_n_sentences(block.get("text", ""), 3)
            block["text_first_3_sentences"] = text_3s
            if text_3s:
                embed_tasks.append((i, "embedding", text_3s))

        for fig in block.get("figures", []):
            sig = fig.get("semantic_signature", "")
            if sig:
                embed_tasks.append((i, f"fig_{id(fig)}", sig))

    if not embed_tasks:
        print("[index] No texts to embed.")
        return blocks

    print(f"[index] Computing {len(embed_tasks)} embeddings...")
    texts = [t[2] for t in embed_tasks]
    embeddings = compute_embeddings(texts)

    # Assign embeddings back
    fig_map = {}  # id(fig) -> fig dict, for assignment
    for block in blocks:
        for fig in block.get("figures", []):
            fig_map[id(fig)] = fig

    for (block_idx, field, _), embedding in zip(embed_tasks, embeddings):
        if field == "embedding":
            blocks[block_idx]["embedding"] = embedding
        elif field.startswith("fig_"):
            fig_id = int(field[4:])
            if fig_id in fig_map:
                fig_map[fig_id]["signature_embedding"] = embedding

    return blocks


# ---------------------------------------------------------------------------
# Step 7 — Build and save JSON index
# ---------------------------------------------------------------------------


def build_lesson_index(
    blocks: list[dict],
    subject: str,
    lesson_id: str,
    source_pdf: str,
    date: str = "",
    prof: str = "",
) -> dict:
    """Build the lesson index structure from classified blocks."""
    # Organize blocks into L1 > L2 hierarchy
    l1_blocks = []
    current_l1 = None

    for block in blocks:
        level = block["level"]

        if level == "L1":
            current_l1 = {
                "level": "L1",
                "title": block.get("title", ""),
                "sub_blocks": [],
            }
            l1_blocks.append(current_l1)

        elif level in ("L2", "L3"):
            sub = {
                "level": level,
                "title": block.get("title", ""),
                "text_first_3_sentences": block.get("text_first_3_sentences", ""),
                "embedding": block.get("embedding", []),
                "figures": _format_figures(block.get("figures", []), block),
            }
            if current_l1 is not None:
                current_l1["sub_blocks"].append(sub)
            else:
                # No L1 parent; create a synthetic one
                current_l1 = {
                    "level": "L1",
                    "title": "(senza titolo)",
                    "sub_blocks": [sub],
                }
                l1_blocks.append(current_l1)

        elif level == "body":
            # Standalone body (not merged); create synthetic L2
            sub = {
                "level": "L2",
                "title": "(corpo testo)",
                "text_first_3_sentences": _first_n_sentences(block.get("text", ""), 3),
                "embedding": block.get("embedding", []),
                "figures": _format_figures(block.get("figures", []), block),
            }
            if current_l1 is not None:
                current_l1["sub_blocks"].append(sub)
            else:
                current_l1 = {"level": "L1", "title": "(senza titolo)", "sub_blocks": [sub]}
                l1_blocks.append(current_l1)

    return {
        "id": lesson_id,
        "source_pdf": Path(source_pdf).name,
        "date": date,
        "prof": prof,
        "blocks": l1_blocks,
    }


def _format_figures(figures: list[dict], parent_block: dict) -> list[dict]:
    """Format figure entries for JSON output."""
    formatted = []
    total = len(figures)
    for i, fig in enumerate(figures):
        formatted.append(
            {
                "file": fig["file"],
                "content_hash": fig["content_hash"],
                "size_class": fig["size_class"],
                "aspect_ratio": fig["aspect_ratio"],
                "caption": fig.get("caption", ""),
                "has_caption": fig.get("has_caption", False),
                "visual_caption": fig.get("visual_caption", ""),
                "semantic_signature": fig.get("semantic_signature", ""),
                "signature_embedding": fig.get("signature_embedding", []),
                "position_in_block": round((i + 1) / (total + 1), 2) if total > 0 else 0.0,
            }
        )
    return formatted


def save_index(
    lesson_data: dict, subject: str
):
    """Save or update the JSON index for a subject."""
    index_dir = PROJECT_ROOT / "legacy_index"
    index_dir.mkdir(parents=True, exist_ok=True)
    index_path = index_dir / f"{subject}.json"

    if index_path.exists():
        print(f"[index] Loading existing index: {index_path}")
        with open(index_path, "r", encoding="utf-8") as f:
            index = json.load(f)
    else:
        index = {
            "subject": subject,
            "indexed_at": "",
            "embedding_model": EMBEDDING_MODEL,
            "lessons": [],
        }

    # Replace existing lesson with same id, or append
    lesson_id = lesson_data["id"]
    replaced = False
    for i, existing in enumerate(index["lessons"]):
        if existing["id"] == lesson_id:
            index["lessons"][i] = lesson_data
            replaced = True
            print(f"[index] Replaced existing lesson '{lesson_id}' in index.")
            break

    if not replaced:
        index["lessons"].append(lesson_data)
        print(f"[index] Added lesson '{lesson_id}' to index.")

    index["indexed_at"] = datetime.now(timezone.utc).isoformat()

    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)

    print(f"[index] Index saved: {index_path}")
    return index_path


# ---------------------------------------------------------------------------
# Lesson ID auto-detection
# ---------------------------------------------------------------------------


def derive_lesson_id(pdf_path: str) -> str:
    """Try to derive a lesson ID from the filename."""
    stem = Path(pdf_path).stem.lower()
    # Look for patterns like "lezione_05", "lez05", "l05", "lezione 5"
    m = re.search(r"(?:lezione|lez|l)[_\s-]*(\d+)", stem)
    if m:
        return f"L{int(m.group(1)):02d}"
    # Look for just a number
    m = re.search(r"(\d+)", stem)
    if m:
        return f"L{int(m.group(1)):02d}"
    # Fallback: use sanitized filename
    return re.sub(r"[^a-zA-Z0-9_]", "_", stem)[:20]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(
        description="Index legacy sbobina PDFs: extract text hierarchy, images, and embeddings."
    )
    parser.add_argument("subject", help="Subject name (e.g. anatomia, biochimica)")
    parser.add_argument("pdf_path", help="Path to the legacy PDF file")
    parser.add_argument("--lesson-id", default=None, help="Lesson ID override (default: auto-detect from filename)")
    parser.add_argument("--date", default="", help="Lesson date (e.g. '08/10/2024')")
    parser.add_argument("--prof", default="", help="Professor name")
    parser.add_argument("--page-start", type=int, default=None, help="First page to process (1-based, inclusive)")
    parser.add_argument("--page-end", type=int, default=None, help="Last page to process (1-based, inclusive)")
    args = parser.parse_args()

    pdf_path = str(Path(args.pdf_path).resolve())
    if not Path(pdf_path).exists():
        print(f"[index] ERROR: File not found: {pdf_path}")
        sys.exit(1)

    subject = args.subject.lower()
    lesson_id = args.lesson_id or derive_lesson_id(pdf_path)

    print(f"[index] === Indexing legacy PDF ===")
    print(f"[index] Subject: {subject}")
    print(f"[index] Lesson ID: {lesson_id}")
    print(f"[index] PDF: {pdf_path}")
    print()

    page_start = args.page_start
    page_end = args.page_end

    if page_start or page_end:
        print(f"[index] Page range: {page_start or 1} — {page_end or 'end'}")
        print()

    # Step 1: Extract text with font hints
    print("[index] --- Step 1: Text extraction ---")
    pages_data = extract_text_with_hints(pdf_path, page_start, page_end)
    total_lines = sum(len(p["lines"]) for p in pages_data)
    print(f"[index] Extracted {total_lines} lines from {len(pages_data)} pages.\n")

    # Step 2: LLM hierarchy classification
    print("[index] --- Step 2: Hierarchy classification ---")
    blocks = classify_hierarchy(pages_data)
    level_counts = {}
    for b in blocks:
        level_counts[b["level"]] = level_counts.get(b["level"], 0) + 1
    print(f"[index] Classified {len(blocks)} blocks: {level_counts}\n")

    # Step 3: Extract images
    print("[index] --- Step 3: Image extraction ---")
    images = extract_images(pdf_path, subject, lesson_id, page_start, page_end)
    print()

    # Step 4: Associate images to blocks
    print("[index] --- Step 4: Image-block association ---")
    blocks = associate_images_to_blocks(blocks, images, pages_data)
    img_assigned = sum(len(b.get("figures", [])) for b in blocks)
    print(f"[index] Assigned {img_assigned} images to blocks.\n")

    # Step 5: Semantic signatures
    print("[index] --- Step 5: Semantic signatures ---")
    blocks = compute_semantic_signatures(blocks, pages_data)
    captioned = sum(
        1
        for b in blocks
        for f in b.get("figures", [])
        if f.get("has_caption")
    )
    print(f"[index] {captioned}/{img_assigned} images have captions.\n")

    # Step 5b: Visual captioning
    print("[index] --- Step 5b: Visual captioning (Gemini Flash Lite) ---")
    blocks = caption_images_with_vision(blocks)
    print()

    # Step 6: Embeddings
    print("[index] --- Step 6: Computing embeddings ---")
    blocks = embed_blocks_and_figures(blocks)
    print()

    # Step 7: Build and save index
    print("[index] --- Step 7: Saving index ---")
    lesson_data = build_lesson_index(
        blocks,
        subject=subject,
        lesson_id=lesson_id,
        source_pdf=pdf_path,
        date=args.date,
        prof=args.prof,
    )
    index_path = save_index(lesson_data, subject)

    print(f"\n[index] === Done! ===")
    print(f"[index] Index: {index_path}")
    print(f"[index] Images: {PROJECT_ROOT / 'legacy_images' / subject / lesson_id}/")


if __name__ == "__main__":
    main()
