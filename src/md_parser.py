"""
Parser Markdown per sbobine: identifica blocchi e punti di inserimento validi.

Usato dal pipeline di inserimento immagini (stage A3 e A4).
Componente critico per la correttezza del posizionamento.
"""

import re
from dataclasses import dataclass, field

# ── Pattern ─────────────────────────────────────────────────────

BLOCK_RE = re.compile(r'^##\s+BLOCCO\s+(\d+)\s*[—–-]\s*(.+)$', re.MULTILINE)
APPENDIX_RE = re.compile(r'^##\s+APPENDICE\b', re.MULTILINE)


# ── Data structures ─────────────────────────────────────────────

@dataclass
class Block:
    index: int          # N for BLOCCO N
    title: str
    start_line: int     # 0-indexed in full document (the ## BLOCCO line)
    end_line: int       # exclusive


@dataclass
class InsertionPoint:
    id: str             # e.g. "block_07.after_paragraph:2"
    line: int           # line number in document AFTER which to insert
    context: str        # last ~50 chars of preceding element


# ── Block identification ────────────────────────────────────────

def parse_blocks(lines: list[str]) -> list[Block]:
    """Split sbobina lines into BLOCCO sections.

    Returns only numbered BLOCCO blocks (not pre-block header or appendix).
    """
    block_starts: list[tuple[int, int, str]] = []  # (line_idx, block_num, title)
    appendix_line = len(lines)

    for i, line in enumerate(lines):
        m = BLOCK_RE.match(line)
        if m:
            block_starts.append((i, int(m.group(1)), m.group(2).strip()))
        if APPENDIX_RE.match(line):
            appendix_line = i
            break

    if not block_starts:
        return []

    blocks = []
    for idx, (start, num, title) in enumerate(block_starts):
        if start >= appendix_line:
            break

        # End at next BLOCCO header or appendix
        if idx + 1 < len(block_starts):
            end = block_starts[idx + 1][0]
            # If preceded by ---, don't include it (it belongs to the gap between blocks)
            if end > 0 and lines[end - 1].strip() == '---':
                end = end - 1
        else:
            end = appendix_line
            if end > 0 and lines[end - 1].strip() == '---':
                end = end - 1

        blocks.append(Block(index=num, title=title, start_line=start, end_line=end))

    return blocks


# ── Line classification ─────────────────────────────────────────

def _classify_line(line: str) -> str:
    """Classify a single line by its markdown type."""
    stripped = line.strip()
    if not stripped:
        return "blank"
    if stripped == '---':
        return "separator"
    if re.match(r'^#{2,6}\s', line):
        return "header"
    if re.match(r'^\s*[-*]\s', line):
        return "list"
    if re.match(r'^\s*\d+\.\s', line):
        return "list"
    if line.startswith('>'):
        return "callout"
    if stripped.startswith('```'):
        return "code_fence"
    if stripped.startswith('|') and '|' in stripped[1:]:
        return "table"
    return "text"


# ── Element parsing within a block ──────────────────────────────

def _parse_elements(block_lines: list[str]) -> list[tuple[str, int, int]]:
    """Parse block lines into elements: (type, start_line, end_line) relative to block.

    Elements: header, paragraph, list, callout, table, code, separator.
    """
    elements: list[tuple[str, int, int]] = []
    i = 0
    n = len(block_lines)
    in_code = False

    while i < n:
        line = block_lines[i]
        cls = _classify_line(line)

        # Inside code block — accumulate until closing fence
        if in_code:
            if cls == "code_fence":
                in_code = False
                if elements and elements[-1][0] == "code":
                    elements[-1] = ("code", elements[-1][1], i)
            i += 1
            continue

        # Skip blank lines (they're gaps between elements)
        if cls == "blank":
            i += 1
            continue

        # Code fence opens
        if cls == "code_fence":
            in_code = True
            elements.append(("code", i, i))
            i += 1
            continue

        # Separator (--- within block)
        if cls == "separator":
            elements.append(("separator", i, i))
            i += 1
            continue

        # Header (## or ### etc.)
        if cls == "header":
            elements.append(("header", i, i))
            i += 1
            continue

        # Callout (> [!...] or > text)
        if cls == "callout":
            start = i
            while i < n and block_lines[i].startswith('>'):
                i += 1
            elements.append(("callout", start, i - 1))
            continue

        # List (- or * or 1. items, possibly nested/continued)
        if cls == "list":
            start = i
            i += 1
            while i < n:
                lcls = _classify_line(block_lines[i])
                if lcls == "list":
                    i += 1
                elif lcls == "text" and (block_lines[i].startswith('    ') or
                                         block_lines[i].startswith('\t')):
                    # Indented continuation of list item
                    i += 1
                elif lcls == "blank":
                    # Blank line: check if list continues after
                    j = i + 1
                    while j < n and _classify_line(block_lines[j]) == "blank":
                        j += 1
                    if j < n and _classify_line(block_lines[j]) == "list":
                        i = j  # skip blanks, continue list
                    else:
                        break  # list ended
                else:
                    break
            elements.append(("list", start, i - 1))
            continue

        # Table
        if cls == "table":
            start = i
            while i < n and _classify_line(block_lines[i]) == "table":
                i += 1
            elements.append(("table", start, i - 1))
            continue

        # Paragraph (default: continuous text until blank/special)
        start = i
        i += 1
        while i < n:
            lcls = _classify_line(block_lines[i])
            if lcls in ("blank", "header", "list", "callout", "code_fence",
                         "separator", "table"):
                break
            i += 1
        elements.append(("paragraph", start, i - 1))

    return elements


# ── Insertion point generation ──────────────────────────────────

def find_insertion_points(block: Block, doc_lines: list[str]) -> list[InsertionPoint]:
    """Find valid insertion points within a block.

    Points are placed between block-level elements.
    NOT inside lists, callouts, or code blocks.
    """
    block_lines = doc_lines[block.start_line:block.end_line]
    if not block_lines:
        return []

    elements = _parse_elements(block_lines)
    if not elements:
        return []

    points: list[InsertionPoint] = []
    type_counts: dict[str, int] = {}

    for etype, estart, eend in elements:
        # Skip separator and code — no insertion point after these
        if etype in ("separator", "code"):
            continue

        type_counts[etype] = type_counts.get(etype, 0) + 1

        ip_type = {
            "header": "after_header",
            "paragraph": "after_paragraph",
            "list": "after_list",
            "callout": "after_callout",
            "table": "after_table",
        }.get(etype)

        if not ip_type:
            continue

        count = type_counts[etype]
        ip_id = f"block_{block.index:02d}.{ip_type}:{count}"

        # Line in the full document
        doc_line = block.start_line + eend

        # Context: last ~50 chars of the element's last line
        context_text = block_lines[eend].strip()
        context = context_text[-50:] if len(context_text) > 50 else context_text

        points.append(InsertionPoint(id=ip_id, line=doc_line, context=context))

    # Add end_of_block
    if elements:
        last_end = elements[-1][2]
        doc_line = block.start_line + last_end
        points.append(InsertionPoint(
            id=f"block_{block.index:02d}.end_of_block",
            line=doc_line,
            context="[fine blocco]",
        ))

    return points


# ── Public API ──────────────────────────────────────────────────

def build_insertion_map(text: str) -> tuple[list[Block], dict[str, InsertionPoint]]:
    """Parse sbobina and return blocks + insertion point map.

    Returns:
        blocks: list of Block objects (only BLOCCO sections)
        ip_map: dict of insertion_point_id → InsertionPoint
    """
    lines = text.split('\n')
    blocks = parse_blocks(lines)

    ip_map: dict[str, InsertionPoint] = {}
    for block in blocks:
        points = find_insertion_points(block, lines)
        for pt in points:
            ip_map[pt.id] = pt

    return blocks, ip_map


def word_count(text: str) -> int:
    """Count words in text (for short block detection)."""
    return len(text.split())
