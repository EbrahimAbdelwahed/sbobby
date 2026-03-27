"""
Iniettore di immagini legacy nelle sbobine pipeline.

Fase 2: matching semantico cross-lezione tra blocchi L2 della sbobina
e blocchi L2 dell'indice legacy, con posizionamento intra-blocco.

Uso:
    python scripts/inject_images.py anatomia lezione_05
    python scripts/inject_images.py anatomia lezione_05 --threshold 0.65
    python scripts/inject_images.py anatomia lezione_05 --output _imgtest
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# Cosine similarity
# ---------------------------------------------------------------------------

def cosine_sim(a: list[float], b: list[float]) -> float:
    """Cosine similarity between two embedding vectors."""
    va, vb = np.asarray(a, dtype=np.float32), np.asarray(b, dtype=np.float32)
    return float(np.dot(va, vb) / (np.linalg.norm(va) * np.linalg.norm(vb) + 1e-9))


# ---------------------------------------------------------------------------
# Embedding via OpenRouter
# ---------------------------------------------------------------------------

_EMB_CLIENT = None

def _get_emb_client():
    global _EMB_CLIENT
    if _EMB_CLIENT is None:
        from openai import OpenAI
        api_key = os.environ.get("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("Variabile d'ambiente OPENROUTER_API_KEY non impostata")
        _EMB_CLIENT = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)
    return _EMB_CLIENT


EMB_MODEL = "openai/text-embedding-3-large"
_MAX_BATCH = 64  # max texts per embedding call


# ---------------------------------------------------------------------------
# Embedding cache
# ---------------------------------------------------------------------------

_emb_cache: dict[str, list[float]] = {}
_emb_cache_path: Optional[Path] = None
_emb_cache_dirty: bool = False


def _text_hash(text: str) -> str:
    """Stable hash for cache key."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def load_emb_cache(subject: str, lesson: str) -> None:
    """Load embedding cache from workspace."""
    global _emb_cache, _emb_cache_path, _emb_cache_dirty
    _emb_cache_path = PROJECT_ROOT / "workspace" / subject / lesson / "emb_cache.json"
    _emb_cache_dirty = False
    if _emb_cache_path.exists():
        with open(_emb_cache_path, "r", encoding="utf-8") as f:
            _emb_cache = json.load(f)
        print(f"[inject] Loaded {len(_emb_cache)} cached embeddings")
    else:
        _emb_cache = {}


def save_emb_cache() -> None:
    """Persist embedding cache if changed."""
    global _emb_cache_dirty
    if not _emb_cache_dirty or _emb_cache_path is None:
        return
    _emb_cache_path.parent.mkdir(parents=True, exist_ok=True)
    with open(_emb_cache_path, "w", encoding="utf-8") as f:
        json.dump(_emb_cache, f)
    _emb_cache_dirty = False
    print(f"[inject] Saved {len(_emb_cache)} embeddings to cache")


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed a list of texts via OpenRouter, with caching."""
    global _emb_cache_dirty
    if not texts:
        return []

    results: list[Optional[list[float]]] = [None] * len(texts)
    uncached_indices: list[int] = []
    uncached_texts: list[str] = []

    for i, t in enumerate(texts):
        h = _text_hash(t)
        if h in _emb_cache:
            results[i] = _emb_cache[h]
        else:
            uncached_indices.append(i)
            uncached_texts.append(t)

    if uncached_texts:
        cached_count = len(texts) - len(uncached_texts)
        if cached_count > 0:
            print(f"[inject] {cached_count} embeddings from cache, {len(uncached_texts)} to compute")
        client = _get_emb_client()
        all_new: list[list[float]] = []
        for i in range(0, len(uncached_texts), _MAX_BATCH):
            batch = uncached_texts[i : i + _MAX_BATCH]
            batch = [t if t.strip() else " " for t in batch]
            resp = client.embeddings.create(model=EMB_MODEL, input=batch)
            sorted_data = sorted(resp.data, key=lambda d: d.index)
            all_new.extend([d.embedding for d in sorted_data])

        for idx, emb in zip(uncached_indices, all_new):
            results[idx] = emb
            h = _text_hash(texts[idx])
            _emb_cache[h] = emb
            _emb_cache_dirty = True
    else:
        print(f"[inject] All {len(texts)} embeddings from cache")

    return results  # type: ignore[return-value]


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class PipelineBlock:
    """A block parsed from the pipeline sbobina."""
    index: int              # 1-based BLOCCO number (0 for preamble)
    heading: str            # Full heading line
    title: str              # Extracted title after "BLOCCO N — "
    raw_text: str           # Full text content (without heading)
    first_3_sentences: str  # For embedding
    embedding: list[float] = field(default_factory=list)


@dataclass
class LegacyFigure:
    """A figure from the legacy index."""
    file: str
    content_hash: str
    size_class: str
    aspect_ratio: float
    caption: str
    has_caption: bool
    semantic_signature: str
    signature_embedding: list[float]
    position_in_block: float
    source_lesson: str = ""
    source_block_title: str = ""


@dataclass
class LegacyL2Block:
    """An L2 block from the legacy index."""
    lesson_id: str
    parent_title: str
    title: str
    text_first_3_sentences: str
    embedding: list[float]
    figures: list[LegacyFigure]


@dataclass
class MatchResult:
    """Result of matching a pipeline block to a legacy block."""
    pipeline_block_idx: int
    pipeline_block_title: str
    legacy_lesson: str
    legacy_block_title: str
    similarity: float
    figures: list[LegacyFigure]
    review_flag: Optional[str] = None  # None=ok, "titoli divergenti"=excluded


# ---------------------------------------------------------------------------
# Sbobina parser
# ---------------------------------------------------------------------------

_BLOCK_RE = re.compile(r"^##\s+BLOCCO\s+(\d+)\s*[—–-]\s*(.+)$", re.MULTILINE)
_HEADING_RE = re.compile(r"^##\s+(.+)$", re.MULTILINE)
_SENTENCE_END = re.compile(r"(?<=[.!?])\s+")

# Regex to extract visual content from semantic signature
_VISUAL_RE = re.compile(r"\[Contenuto visuale:\s*(.*?)\]", re.DOTALL)


def _extract_visual_content(signature: str) -> tuple[str, bool]:
    """Extract the [Contenuto visuale: ...] portion from a semantic signature.

    Returns (extracted_text, tag_found). If tag not found, returns full
    signature as fallback.
    """
    m = _VISUAL_RE.search(signature)
    if m:
        return m.group(1).strip(), True
    return signature, False


def _first_n_sentences(text: str, n: int = 3) -> str:
    """Extract the first n sentences from text."""
    # Strip markdown formatting for embedding
    clean = re.sub(r">\s*\[immagine di:.*?\]", "", text)
    clean = re.sub(r">\s*\[!.*?\].*", "", clean)
    clean = re.sub(r"[*_`#>|]", "", clean)
    clean = re.sub(r"\n+", " ", clean).strip()
    if not clean:
        return ""
    parts = _SENTENCE_END.split(clean, maxsplit=n)
    return " ".join(parts[:n]).strip()


def parse_sbobina(md_text: str) -> list[PipelineBlock]:
    """Parse a pipeline sbobina into blocks.

    Looks for ## BLOCCO N headings. Falls back to any ## heading if
    no BLOCCO headings are found.
    """
    blocks: list[PipelineBlock] = []

    # Find all BLOCCO headings
    matches = list(_BLOCK_RE.finditer(md_text))

    if not matches:
        # Fallback: use any ## heading
        matches_generic = list(_HEADING_RE.finditer(md_text))
        if not matches_generic:
            return blocks
        for i, m in enumerate(matches_generic):
            title = m.group(1).strip()
            # Skip meta sections
            if title.upper() in ("INFORMAZIONI SUL CORSO", "APPENDICE", "BRAIN DUMP"):
                continue
            start = m.end()
            end = matches_generic[i + 1].start() if i + 1 < len(matches_generic) else len(md_text)
            raw = md_text[start:end].strip()
            # Remove trailing ---
            raw = re.sub(r"\n---\s*$", "", raw).strip()
            blocks.append(PipelineBlock(
                index=i + 1,
                heading=m.group(0),
                title=title,
                raw_text=raw,
                first_3_sentences=_first_n_sentences(raw),
            ))
        return blocks

    for i, m in enumerate(matches):
        block_num = int(m.group(1))
        title = m.group(2).strip()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(md_text)
        raw = md_text[start:end].strip()
        raw = re.sub(r"\n---\s*$", "", raw).strip()
        blocks.append(PipelineBlock(
            index=block_num,
            heading=m.group(0),
            title=title,
            raw_text=raw,
            first_3_sentences=_first_n_sentences(raw),
        ))

    return blocks


# ---------------------------------------------------------------------------
# Legacy index loader
# ---------------------------------------------------------------------------

def load_legacy_index(subject: str) -> list[LegacyL2Block]:
    """Load and flatten the legacy index into L2 blocks."""
    index_path = PROJECT_ROOT / "legacy_index" / f"{subject}.json"
    if not index_path.exists():
        print(f"[inject] Indice legacy non trovato per {subject}, skip")
        return []

    with open(index_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    l2_blocks: list[LegacyL2Block] = []
    for lesson in data.get("lessons", []):
        lesson_id = lesson.get("id", "")
        for l1 in lesson.get("blocks", []):
            parent_title = l1.get("title", "")
            for l2 in l1.get("sub_blocks", []):
                figures = []
                for fig_data in l2.get("figures", []):
                    figures.append(LegacyFigure(
                        file=fig_data.get("file", ""),
                        content_hash=fig_data.get("content_hash", ""),
                        size_class=fig_data.get("size_class", "medium"),
                        aspect_ratio=fig_data.get("aspect_ratio", 1.0),
                        caption=fig_data.get("caption", ""),
                        has_caption=fig_data.get("has_caption", False),
                        semantic_signature=fig_data.get("semantic_signature", ""),
                        signature_embedding=fig_data.get("signature_embedding", []),
                        position_in_block=fig_data.get("position_in_block", 0.5),
                        source_lesson=lesson_id,
                        source_block_title=l2.get("title", ""),
                    ))
                l2_blocks.append(LegacyL2Block(
                    lesson_id=lesson_id,
                    parent_title=parent_title,
                    title=l2.get("title", ""),
                    text_first_3_sentences=l2.get("text_first_3_sentences", ""),
                    embedding=l2.get("embedding", []),
                    figures=figures,
                ))
    return l2_blocks


# ---------------------------------------------------------------------------
# Block matching
# ---------------------------------------------------------------------------

_IT_STOPWORDS = frozenset({
    "il", "lo", "la", "i", "gli", "le", "un", "uno", "una",
    "di", "del", "dello", "della", "dei", "degli", "delle",
    "a", "al", "allo", "alla", "ai", "agli", "alle",
    "da", "dal", "dallo", "dalla", "dai", "dagli", "dalle",
    "in", "nel", "nello", "nella", "nei", "negli", "nelle",
    "su", "sul", "sullo", "sulla", "sui", "sugli", "sulle",
    "con", "per", "tra", "fra",
    "e", "ed", "o", "od", "ma", "se", "che", "non",
    "è", "sono", "come", "più", "anche",
})


def _tokenize_title(title: str) -> set[str]:
    """Tokenize a title for overlap check: lowercase, remove stopwords, min 3 chars."""
    tokens = re.findall(r"[a-zàèéìòù]+", title.lower())
    return {t for t in tokens if t not in _IT_STOPWORDS and len(t) >= 3}


def match_blocks(
    pipeline_blocks: list[PipelineBlock],
    legacy_blocks: list[LegacyL2Block],
    threshold: float,
) -> tuple[list[MatchResult], list[dict]]:
    """Match each pipeline block to best legacy L2 block.

    Returns (matches, unmatched_info).
    """
    matches: list[MatchResult] = []
    unmatched: list[dict] = []

    for pb in pipeline_blocks:
        if not pb.embedding:
            unmatched.append({
                "block_index": pb.index,
                "title": pb.title,
                "reason": "no embedding",
            })
            continue

        best_sim = -1.0
        best_legacy: Optional[LegacyL2Block] = None

        for lb in legacy_blocks:
            if not lb.embedding or not lb.figures:
                continue
            sim = cosine_sim(pb.embedding, lb.embedding)
            if sim > best_sim:
                best_sim = sim
                best_legacy = lb

        if best_legacy is not None and best_sim >= threshold:
            # --- Title divergence check ---
            review_flag: Optional[str] = None
            pipe_tokens = _tokenize_title(pb.title)
            legacy_tokens = _tokenize_title(best_legacy.title)
            if pipe_tokens and legacy_tokens and not (pipe_tokens & legacy_tokens):
                review_flag = "titoli divergenti"
                print(
                    f'[inject] BLOCCO {pb.index} "{pb.title[:50]}" → '
                    f'{best_legacy.lesson_id} L2 "{best_legacy.title[:50]}" '
                    f"(sim={best_sim:.2f}) — ESCLUSO: titoli divergenti"
                )
            else:
                print(
                    f"[inject] Matched BLOCCO {pb.index} "
                    f'"{pb.title[:50]}" → '
                    f'{best_legacy.lesson_id} L2 "{best_legacy.title[:50]}" '
                    f"(sim={best_sim:.2f}, {len(best_legacy.figures)} fig)"
                )

            matches.append(MatchResult(
                pipeline_block_idx=pb.index,
                pipeline_block_title=pb.title,
                legacy_lesson=best_legacy.lesson_id,
                legacy_block_title=best_legacy.title,
                similarity=best_sim,
                figures=list(best_legacy.figures),
                review_flag=review_flag,
            ))
        else:
            sim_str = f"{best_sim:.2f}" if best_sim >= 0 else "N/A"
            unmatched.append({
                "block_index": pb.index,
                "title": pb.title,
                "best_sim": sim_str,
                "best_legacy_title": best_legacy.title if best_legacy else None,
                "reason": f"below threshold ({sim_str} < {threshold})",
            })
            print(
                f"[inject] BLOCCO {pb.index} "
                f'"{pb.title[:50]}" — no match (best sim={sim_str})'
            )

    return matches, unmatched


# ---------------------------------------------------------------------------
# Intra-block positioning
# ---------------------------------------------------------------------------

_PARA_SPLIT = re.compile(r"\n{2,}")

# Minimum cosine similarity for intra-block placement
_INTRA_THRESHOLD = 0.4


def _split_paragraphs(text: str) -> list[str]:
    """Split block text into paragraphs on double newlines."""
    paras = _PARA_SPLIT.split(text.strip())
    return [p.strip() for p in paras if p.strip()]


def _first_n_words(text: str, n: int = 50) -> str:
    """Extract first n words from text."""
    words = text.split()
    return " ".join(words[:n])


_ATTRACTOR_PREFIXES = (
    "**Bullet riepilogo",
    "**Riepilogo rapido",
    "### Riepilogo rapido",
    "### Bullet riepilogo",
    "### Concetto chiave",
    "**Concetto chiave",
)


def _is_attractor_para(text: str) -> bool:
    """Check if paragraph is an attractor that should be excluded from matching."""
    stripped = text.strip()
    for prefix in _ATTRACTOR_PREFIXES:
        if stripped.startswith(prefix):
            return True
    if stripped.startswith("> [!"):
        return True
    return False


def position_figures_in_block(
    block_text: str,
    figures: list[LegacyFigure],
    paragraph_embeddings: Optional[list[list[float]]] = None,
    paragraphs: Optional[list[str]] = None,
    diagnostic: bool = False,
) -> tuple[list[tuple[int, LegacyFigure]], list[dict]]:
    """Decide where each figure goes within a block.

    Returns (placements, diagnostics) where placements is a list of
    (paragraph_index, figure) and diagnostics is per-figure diagnostic info
    (empty list if diagnostic=False).
    """
    if paragraphs is None:
        paragraphs = _split_paragraphs(block_text)
    if not paragraphs:
        return [(-1, fig) for fig in figures], []

    # --- Identify attractor paragraphs to exclude from scoring ---
    attractor_set = {j for j, p in enumerate(paragraphs) if _is_attractor_para(p)}
    candidate_indices = [j for j in range(len(paragraphs)) if j not in attractor_set]
    # Fallback: if all paragraphs are attractors, use all
    if not candidate_indices:
        candidate_indices = list(range(len(paragraphs)))
        attractor_set = set()

    placements: list[tuple[int, LegacyFigure]] = []
    diag_list: list[dict] = []

    for fig in figures:
        if not fig.signature_embedding or paragraph_embeddings is None:
            placements.append((len(paragraphs) - 1, fig))
            if diagnostic:
                diag_list.append({
                    "top_3_paragrafi": [],
                    "gap_1_2": 0.0,
                    "fallback_used": {
                        "triggered": True,
                        "action": "fine blocco (no embedding disponibile)",
                    },
                    "stacking_resolved": False,
                })
            continue

        # Score only candidate (non-attractor) paragraphs
        scored: list[tuple[int, float]] = []
        for j in candidate_indices:
            sim = cosine_sim(paragraph_embeddings[j], fig.signature_embedding)
            scored.append((j, sim))
        scored.sort(key=lambda x: x[1], reverse=True)

        best_idx = scored[0][0]
        best_sim = scored[0][1]
        gap = round(scored[0][1] - scored[1][1], 4) if len(scored) > 1 else 0.0

        fallback_used = {"triggered": False, "action": ""}

        if best_sim < _INTRA_THRESHOLD:
            # Below absolute threshold → end of block
            fallback_used = {
                "triggered": True,
                "action": f"fine blocco (best score {best_sim:.3f} < threshold {_INTRA_THRESHOLD})",
            }
            best_idx = len(paragraphs) - 1
        elif gap < 0.03 and len(scored) > 1:
            # Gap too small → proportional position fallback
            prop = fig.position_in_block  # 0.0–1.0 in legacy block
            target_idx = round(prop * (len(paragraphs) - 1))
            target_idx = max(0, min(target_idx, len(paragraphs) - 1))
            fallback_used = {
                "triggered": True,
                "action": (
                    f"posizione proporzionale (gap={gap:.4f} < 0.03, "
                    f"position_in_block={prop:.2f} → para {target_idx})"
                ),
            }
            best_idx = target_idx

        placements.append((best_idx, fig))

        if diagnostic:
            top3 = []
            for rank, (pidx, psim) in enumerate(scored[:3]):
                chosen = (pidx == best_idx) if not fallback_used["triggered"] else False
                top3.append({
                    "para_index": pidx,
                    "prime_50_parole": _first_n_words(paragraphs[pidx]),
                    "cosine_similarity": round(psim, 4),
                    "scelto": chosen,
                })
            diag_list.append({
                "top_3_paragrafi": top3,
                "gap_1_2": gap,
                "fallback_used": fallback_used,
                "stacking_resolved": False,  # updated below if needed
            })

    # --- Anti-stacking: redistribute if multiple figures on same paragraph ---
    from collections import Counter
    para_counts = Counter(idx for idx, _ in placements if idx >= 0)
    has_stacking = any(c >= 2 for c in para_counts.values())

    if has_stacking and len(candidate_indices) > 0:
        new_placements: list[tuple[int, LegacyFigure]] = []
        for i, (orig_idx, fig) in enumerate(placements):
            if i < len(candidate_indices):
                new_idx = candidate_indices[i]
            else:
                new_idx = candidate_indices[-1]
            moved = (new_idx != orig_idx)
            new_placements.append((new_idx, fig))
            if diagnostic and i < len(diag_list):
                diag_list[i]["stacking_resolved"] = moved
        placements = new_placements

    return placements, diag_list


# ---------------------------------------------------------------------------
# Dense block handling
# ---------------------------------------------------------------------------

_MAX_INLINE_PER_4_LINES = 1  # If exceeded, block is "dense"
_MAX_INLINE_IMAGES = 2


def _is_dense(block_text: str, n_figures: int) -> bool:
    """Check if block is too dense for all images inline."""
    line_count = len(block_text.strip().splitlines())
    if line_count == 0:
        return n_figures > 0
    max_inline = (line_count // 4) * _MAX_INLINE_PER_4_LINES
    return n_figures > max(max_inline, _MAX_INLINE_IMAGES)


# ---------------------------------------------------------------------------
# Markdown injection
# ---------------------------------------------------------------------------

def _image_markup(fig: LegacyFigure) -> str:
    """Generate Obsidian-compatible image markup for a figure."""
    filename = Path(fig.file).name
    # Clean caption: remove double quotes (break HTML comment parsing), limit length
    caption_str = fig.caption.replace('"', "'").replace('\n', ' ') if fig.caption else ""
    if len(caption_str) > 200:
        caption_str = caption_str[:197] + "..."
    lines = []
    lines.append(
        f'<!-- img:caption="{caption_str}" '
        f'img:size_class="{fig.size_class}" '
        f'img:aspect_ratio="{fig.aspect_ratio}" -->'
    )
    lines.append(f"![[{filename}]]")
    return "\n".join(lines)


def inject_images_into_block(
    block_text: str,
    placements: list[tuple[int, LegacyFigure]],
) -> str:
    """Inject image markup into block text respecting placement positions.

    Handles dense blocks by putting excess images into a Tavole section.
    """
    paragraphs = _split_paragraphs(block_text)
    if not paragraphs:
        # Nothing to inject into — just return markup
        parts = [block_text]
        for _, fig in placements:
            parts.append("")
            parts.append(_image_markup(fig))
        return "\n".join(parts)

    dense = _is_dense(block_text, len(placements))

    # Separate inline vs tavole images
    if dense:
        inline_placements = placements[:_MAX_INLINE_IMAGES]
        tavole_placements = placements[_MAX_INLINE_IMAGES:]
    else:
        inline_placements = placements
        tavole_placements = []

    # Group inline placements by paragraph index
    para_images: dict[int, list[LegacyFigure]] = {}
    for para_idx, fig in inline_placements:
        para_images.setdefault(para_idx, []).append(fig)

    # Build output paragraph by paragraph
    result_parts: list[str] = []
    last_was_image = False

    for i, para in enumerate(paragraphs):
        result_parts.append(para)
        last_was_image = False

        if i in para_images:
            for fig in para_images[i]:
                # Blank line before image
                result_parts.append("")
                result_parts.append(_image_markup(fig))
                last_was_image = True

        # Ensure blank line between paragraphs (unless last thing was image)
        if i < len(paragraphs) - 1 and not last_was_image:
            result_parts.append("")

    # Add Tavole section if needed
    if tavole_placements:
        result_parts.append("")
        result_parts.append("### Tavole")
        result_parts.append("")
        for _, fig in tavole_placements:
            result_parts.append(_image_markup(fig))
            result_parts.append("")

    return "\n".join(result_parts)


# ---------------------------------------------------------------------------
# Full document reconstruction
# ---------------------------------------------------------------------------

def reconstruct_document(
    original_md: str,
    pipeline_blocks: list[PipelineBlock],
    block_injections: dict[int, str],  # block_index -> new block text with images
) -> str:
    """Reconstruct the full markdown, replacing block text for blocks with images."""
    if not block_injections:
        return original_md

    # Find block heading positions in original
    matches = list(_BLOCK_RE.finditer(original_md))
    if not matches:
        matches = list(_HEADING_RE.finditer(original_md))

    if not matches:
        return original_md

    # Build list of (heading_match, block_index)
    heading_map: dict[int, re.Match] = {}
    for m in _BLOCK_RE.finditer(original_md):
        block_num = int(m.group(1))
        heading_map[block_num] = m

    # If no BLOCCO headings found, use generic headings
    if not heading_map:
        generic_matches = list(_HEADING_RE.finditer(original_md))
        idx = 0
        for gm in generic_matches:
            title = gm.group(1).strip()
            if title.upper() in ("INFORMAZIONI SUL CORSO", "APPENDICE", "BRAIN DUMP"):
                continue
            idx += 1
            heading_map[idx] = gm

    # Sort by position in text
    sorted_blocks = sorted(heading_map.items(), key=lambda x: x[1].start())

    # Reconstruct: go through original text, replacing block bodies
    result_parts: list[str] = []
    prev_end = 0

    for i, (block_idx, m) in enumerate(sorted_blocks):
        # Content after heading until next heading/end
        body_start = m.end()
        if i + 1 < len(sorted_blocks):
            body_end = sorted_blocks[i + 1][1].start()
        else:
            body_end = len(original_md)

        if block_idx in block_injections:
            # Copy everything up to (and including) the heading
            result_parts.append(original_md[prev_end:body_start])

            # Find the --- separator before next block (if any)
            body_text = original_md[body_start:body_end]
            # Strip trailing --- (will be added back by original structure)
            stripped = body_text.rstrip()
            trailing = ""
            if stripped.endswith("---"):
                trailing = body_text[len(stripped) - 3:]
                body_text_clean = stripped[:-3].rstrip()
            else:
                trailing = body_text[len(stripped):]

            # Replace body content
            new_body = "\n\n" + block_injections[block_idx]
            if trailing.strip():
                new_body += "\n\n---"
            new_body += "\n"

            result_parts.append(new_body)

            # Account for the trailing whitespace/separator
            prev_end = body_end
        else:
            # No injection — keep original
            result_parts.append(original_md[prev_end:body_end])
            prev_end = body_end

    # Append anything after the last block
    if prev_end < len(original_md):
        result_parts.append(original_md[prev_end:])

    return "".join(result_parts)


# ---------------------------------------------------------------------------
# Main injection pipeline
# ---------------------------------------------------------------------------

def inject_images(
    subject: str,
    lesson: str,
    threshold: float = 0.7,
    output_suffix: str = "_test",
    diagnostic: bool = False,
) -> Optional[Path]:
    """Full injection pipeline: parse, embed, match, position, inject.

    Returns the path to the output file, or None if nothing was injected.
    """
    sbobina_path = PROJECT_ROOT / "sbobine" / subject / f"{lesson}.md"
    if not sbobina_path.exists():
        print(f"[inject] Sbobina non trovata: {sbobina_path}")
        return None

    # --- 0. Load embedding cache ---
    load_emb_cache(subject, lesson)

    # --- 1. Load legacy index ---
    print(f"[inject] Caricamento indice legacy per {subject}...")
    legacy_blocks = load_legacy_index(subject)
    if not legacy_blocks:
        return None

    legacy_with_figures = [lb for lb in legacy_blocks if lb.figures]
    print(f"[inject] Indice legacy: {len(legacy_blocks)} blocchi L2, "
          f"{len(legacy_with_figures)} con figure, "
          f"{sum(len(lb.figures) for lb in legacy_blocks)} figure totali")

    # --- 2. Parse sbobina ---
    print(f"[inject] Parsing sbobina {sbobina_path.name}...")
    md_text = sbobina_path.read_text(encoding="utf-8")
    pipeline_blocks = parse_sbobina(md_text)
    if not pipeline_blocks:
        print("[inject] Nessun blocco trovato nella sbobina")
        return None
    print(f"[inject] {len(pipeline_blocks)} blocchi trovati")

    # --- 3. Embed pipeline blocks ---
    print(f"[inject] Embedding di {len(pipeline_blocks)} blocchi pipeline...")
    texts_to_embed = []
    for pb in pipeline_blocks:
        # Combine title + first 3 sentences for embedding
        embed_text = pb.title
        if pb.first_3_sentences:
            embed_text += ". " + pb.first_3_sentences
        texts_to_embed.append(embed_text)

    embeddings = embed_texts(texts_to_embed)
    for pb, emb in zip(pipeline_blocks, embeddings):
        pb.embedding = emb

    # --- 4. Match L2 → L2 ---
    print(f"[inject] Matching blocchi (threshold={threshold})...")
    matches, unmatched = match_blocks(pipeline_blocks, legacy_blocks, threshold)

    if not matches:
        print("[inject] Nessun match trovato — nessun file di output creato")
        _save_unmatched(subject, lesson, unmatched)
        save_emb_cache()
        return None

    # --- 4b. Split clean vs flagged matches ---
    flagged_matches = [m for m in matches if m.review_flag is not None]
    clean_matches = [m for m in matches if m.review_flag is None]

    total_all = sum(len(m.figures) for m in matches)
    total_flagged = sum(len(m.figures) for m in flagged_matches)
    print(f"[inject] {len(clean_matches)} blocchi matchati, "
          f"{total_all - total_flagged} figure candidate"
          + (f" ({len(flagged_matches)} esclusi per review)" if flagged_matches else ""))

    if not clean_matches:
        print("[inject] Nessun match valido — nessun file di output creato")
        # Still save diagnostic for flagged matches
        if diagnostic and flagged_matches:
            all_diagnostics: list[dict] = []
            for m in flagged_matches:
                for fig in m.figures:
                    all_diagnostics.append({
                        "image_filename": Path(fig.file).name,
                        "firma_semantica": fig.semantic_signature,
                        "blocco_L2_match": {
                            "titolo": m.pipeline_block_title,
                            "legacy_lesson": m.legacy_lesson,
                            "legacy_block_title": m.legacy_block_title,
                            "cosine_similarity_L1": round(m.similarity, 4),
                        },
                        "review_flag": m.review_flag,
                        "stacking_resolved": False,
                    })
            output_path = PROJECT_ROOT / "sbobine" / subject / f"{lesson}{output_suffix}.md"
            diag_path = output_path.parent / f"{lesson}{output_suffix}_diagnostic.json"
            with open(diag_path, "w", encoding="utf-8") as f:
                json.dump(all_diagnostics, f, ensure_ascii=False, indent=2)
            print(f"[inject] Diagnostic → {diag_path.relative_to(PROJECT_ROOT)} ({len(all_diagnostics)} figure)")
        _save_unmatched(subject, lesson, unmatched)
        save_emb_cache()
        return None

    # --- 5. Dedup figures (clean matches only) ---
    seen_hashes: set[str] = set()
    for match in clean_matches:
        deduped: list[LegacyFigure] = []
        for fig in match.figures:
            if fig.content_hash not in seen_hashes:
                seen_hashes.add(fig.content_hash)
                deduped.append(fig)
        match.figures = deduped

    total_figures = sum(len(m.figures) for m in clean_matches)
    deduped_total = total_figures  # already deduped
    pre_dedup = total_all - total_flagged
    if total_figures < pre_dedup:
        print(f"[inject] Dedup: {pre_dedup} → {total_figures} figure")

    # Remove matches with no figures after dedup
    clean_matches = [m for m in clean_matches if m.figures]
    if not clean_matches:
        print("[inject] Nessuna figura dopo dedup — nessun file di output creato")
        _save_unmatched(subject, lesson, unmatched)
        save_emb_cache()
        return None

    # --- 5b. Extract visual content and re-embed figure signatures ---
    all_figs: list[LegacyFigure] = []
    for match in clean_matches:
        all_figs.extend(match.figures)

    visual_texts: list[str] = []
    figs_to_embed: list[LegacyFigure] = []
    for fig in all_figs:
        visual, found = _extract_visual_content(fig.semantic_signature)
        if not found:
            print(f"[inject] WARN: [Contenuto visuale: ...] non trovato per {Path(fig.file).name}, uso firma completa")
        fig.semantic_signature = visual
        visual_texts.append(visual)
        figs_to_embed.append(fig)

    if visual_texts:
        print(f"[inject] Re-embedding {len(visual_texts)} firme visuali...")
        visual_embeddings = embed_texts(visual_texts)
        for fig, emb in zip(figs_to_embed, visual_embeddings):
            fig.signature_embedding = emb

    # --- 6. Intra-block positioning ---
    print("[inject] Posizionamento intra-blocco...")
    # Collect all paragraphs that need embedding
    block_paragraphs: dict[int, list[str]] = {}
    para_texts_flat: list[str] = []
    para_map: list[tuple[int, int]] = []  # (block_idx, para_idx)

    block_by_idx = {pb.index: pb for pb in pipeline_blocks}

    for match in clean_matches:
        pb = block_by_idx.get(match.pipeline_block_idx)
        if pb is None:
            continue
        paras = _split_paragraphs(pb.raw_text)
        block_paragraphs[match.pipeline_block_idx] = paras
        for j, para in enumerate(paras):
            para_texts_flat.append(para)
            para_map.append((match.pipeline_block_idx, j))

    # Batch embed paragraphs
    if para_texts_flat:
        print(f"[inject] Embedding di {len(para_texts_flat)} paragrafi...")
        para_embeddings_flat = embed_texts(para_texts_flat)
    else:
        para_embeddings_flat = []

    # Rebuild per-block paragraph embeddings
    para_embeddings_by_block: dict[int, list[list[float]]] = {}
    for (block_idx, para_idx), emb in zip(para_map, para_embeddings_flat):
        para_embeddings_by_block.setdefault(block_idx, []).append(emb)

    # Position figures in each matched block
    block_injections: dict[int, str] = {}  # block_index -> new body text
    all_diagnostics: list[dict] = []

    for match in clean_matches:
        pb = block_by_idx.get(match.pipeline_block_idx)
        if pb is None:
            continue

        paras = block_paragraphs.get(match.pipeline_block_idx, [])
        para_embs = para_embeddings_by_block.get(match.pipeline_block_idx)

        placements, fig_diags = position_figures_in_block(
            pb.raw_text,
            match.figures,
            paragraph_embeddings=para_embs,
            paragraphs=paras,
            diagnostic=diagnostic,
        )

        new_body = inject_images_into_block(pb.raw_text, placements)
        block_injections[match.pipeline_block_idx] = new_body

        for i_fig, (para_idx, fig) in enumerate(placements):
            pos_label = f"after para {para_idx + 1}" if para_idx >= 0 else "end of block"
            print(
                f"[inject]   BLOCCO {match.pipeline_block_idx}: "
                f"{Path(fig.file).name} → {pos_label}"
            )

            if diagnostic and i_fig < len(fig_diags):
                all_diagnostics.append({
                    "image_filename": Path(fig.file).name,
                    "firma_semantica": fig.semantic_signature,
                    "blocco_L2_match": {
                        "titolo": match.pipeline_block_title,
                        "legacy_lesson": match.legacy_lesson,
                        "legacy_block_title": match.legacy_block_title,
                        "cosine_similarity_L1": round(match.similarity, 4),
                    },
                    "review_flag": None,
                    **fig_diags[i_fig],
                })

    # --- 6b. Add flagged matches to diagnostic ---
    if diagnostic:
        for m in flagged_matches:
            for fig in m.figures:
                all_diagnostics.append({
                    "image_filename": Path(fig.file).name,
                    "firma_semantica": fig.semantic_signature,
                    "blocco_L2_match": {
                        "titolo": m.pipeline_block_title,
                        "legacy_lesson": m.legacy_lesson,
                        "legacy_block_title": m.legacy_block_title,
                        "cosine_similarity_L1": round(m.similarity, 4),
                    },
                    "review_flag": m.review_flag,
                    "stacking_resolved": False,
                })

    # --- 7. Reconstruct document ---
    print("[inject] Ricostruzione documento...")
    output_md = reconstruct_document(md_text, pipeline_blocks, block_injections)

    # --- 8. Copy images to assets ---
    assets_dir = PROJECT_ROOT / "sbobine" / subject / "assets" / lesson
    assets_dir.mkdir(parents=True, exist_ok=True)

    copied_count = 0
    for match in clean_matches:
        for fig in match.figures:
            src = PROJECT_ROOT / fig.file
            if not src.exists():
                print(f"[inject] WARN: immagine non trovata: {src}")
                continue
            dst = assets_dir / src.name
            if not dst.exists() or dst.stat().st_size != src.stat().st_size:
                shutil.copy2(src, dst)
            copied_count += 1

    print(f"[inject] {copied_count} immagini copiate in {assets_dir.relative_to(PROJECT_ROOT)}")

    # --- 9. Write output ---
    output_path = PROJECT_ROOT / "sbobine" / subject / f"{lesson}{output_suffix}.md"
    output_path.write_text(output_md, encoding="utf-8")
    print(f"[inject] Output salvato: {output_path.relative_to(PROJECT_ROOT)}")

    # --- 10. Save debug info ---
    _save_unmatched(subject, lesson, unmatched)
    _save_match_log(subject, lesson, clean_matches + flagged_matches)

    # --- 10b. Save diagnostic ---
    if diagnostic and all_diagnostics:
        diag_path = output_path.parent / f"{lesson}{output_suffix}_diagnostic.json"
        with open(diag_path, "w", encoding="utf-8") as f:
            json.dump(all_diagnostics, f, ensure_ascii=False, indent=2)
        print(f"[inject] Diagnostic → {diag_path.relative_to(PROJECT_ROOT)} ({len(all_diagnostics)} figure)")

    # --- 11. Save embedding cache ---
    save_emb_cache()

    return output_path


# ---------------------------------------------------------------------------
# Debug output
# ---------------------------------------------------------------------------

def _save_unmatched(subject: str, lesson: str, unmatched: list[dict]) -> None:
    """Save unmatched blocks for debugging."""
    if not unmatched:
        return
    ws = PROJECT_ROOT / "workspace" / subject / lesson
    ws.mkdir(parents=True, exist_ok=True)
    out = ws / "unmatched.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(unmatched, f, ensure_ascii=False, indent=2)
    print(f"[inject] {len(unmatched)} blocchi senza match → {out.relative_to(PROJECT_ROOT)}")


def _save_match_log(subject: str, lesson: str, matches: list[MatchResult]) -> None:
    """Save all match results for debugging."""
    ws = PROJECT_ROOT / "workspace" / subject / lesson
    ws.mkdir(parents=True, exist_ok=True)
    out = ws / "inject_matches.json"
    log = []
    for m in matches:
        log.append({
            "pipeline_block": m.pipeline_block_idx,
            "pipeline_title": m.pipeline_block_title,
            "legacy_lesson": m.legacy_lesson,
            "legacy_title": m.legacy_block_title,
            "similarity": round(m.similarity, 4),
            "figures": [
                {"file": Path(f.file).name, "caption": f.caption}
                for f in m.figures
            ],
        })
    with open(out, "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)
    print(f"[inject] Match log → {out.relative_to(PROJECT_ROOT)}")


# ---------------------------------------------------------------------------
# Public API for pipeline.py
# ---------------------------------------------------------------------------

def inject_for_pipeline(subject: str, lesson: str, **kwargs) -> Optional[Path]:
    """Entry point for pipeline.py integration.

    Accepts the same kwargs as inject_images().
    Returns the output path or None.
    """
    return inject_images(subject, lesson, **kwargs)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Inietta immagini legacy nelle sbobine pipeline"
    )
    parser.add_argument("subject", help="Materia (es. anatomia)")
    parser.add_argument("lesson", help="Lezione (es. lezione_05)")
    parser.add_argument(
        "--threshold", type=float, default=0.7,
        help="Soglia minima di similarita per il match L2 (default: 0.7)",
    )
    parser.add_argument(
        "--output", default="_test",
        help="Suffisso per il file di output (default: _test)",
    )
    parser.add_argument(
        "--diagnostic", action="store_true",
        help="Genera diagnostic.json con dettagli matching per ogni immagine",
    )
    args = parser.parse_args()

    result = inject_images(
        subject=args.subject,
        lesson=args.lesson,
        threshold=args.threshold,
        output_suffix=args.output,
        diagnostic=args.diagnostic,
    )

    if result is None:
        print("[inject] Nessun output generato")
        sys.exit(1)
    else:
        print(f"[inject] Completato: {result}")


if __name__ == "__main__":
    main()
