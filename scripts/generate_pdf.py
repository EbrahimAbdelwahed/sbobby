#!/usr/bin/env python3
"""
Markdown (enriched sbobina) -> Typst -> PDF converter.

Usage:
    python scripts/generate_pdf.py <subject> <lesson> [--input path_to_md]

Output:
    pdf_output/{subject}/{lesson}.pdf
"""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_REL = "templates/sbobina.typ"

# ─────────────────────────── data structures ──────────────────────────────

@dataclass
class ImageMeta:
    """Metadata extracted from <!-- img:... --> HTML comments."""
    filename: str = ""
    caption: str = ""
    size_class: str = "medium"   # small | medium | large
    aspect_ratio: float = 1.0


@dataclass
class Element:
    """One parsed block from the markdown."""
    kind: str          # heading1 heading2 heading3 paragraph table image
                       # callout list hrule recap blank
    text: str = ""
    level: int = 0     # heading level
    rows: list = field(default_factory=list)       # table rows (list of lists)
    image: Optional[ImageMeta] = None
    items: list = field(default_factory=list)       # list items
    raw_lines: list = field(default_factory=list)   # original lines


# ─────────────────────────── escape helper ────────────────────────────────

_TYPST_SPECIAL = ['#', '*', '_', '[', ']', '@', '<', '>', '~']

def escape_typst(text: str) -> str:
    """Escape Typst special characters in plain text."""
    text = text.replace("\\", "\\\\")
    for ch in _TYPST_SPECIAL:
        text = text.replace(ch, f"\\{ch}")
    return text


def _inline_format(text: str) -> str:
    """Convert markdown inline formatting to Typst, then escape remaining."""
    placeholders: list[tuple[str, str]] = []

    def _save_raw(key_hint: str, typst_markup: str) -> str:
        key = f"\x00PH{len(placeholders)}\x00"
        placeholders.append((key, typst_markup))
        return key

    def _save(m, fmt):
        key = f"\x00PH{len(placeholders)}\x00"
        inner = m.group(1)
        placeholders.append((key, fmt.format(_inline_escape_only(inner))))
        return key

    # --- pre-processing: convert special markup before escaping ---

    # Strip inline UNRESOLVED comments: <!-- UNRESOLVED: ... -->
    text = _RE_UNRESOLVED_INLINE.sub('', text)

    # LaTeX inline math: \(expr\) -> $expr$
    text = _RE_LATEX_INLINE.sub(
        lambda m: _save_raw('math', f'${m.group(1)}$'), text
    )

    # Color spans: <span style="color:#XXXX">text</span> -> #text(fill: ...)[text]
    def _color_span(m):
        color = m.group(1)
        inner = _inline_format(m.group(2))  # recurse for nested formatting
        return _save_raw('color', f'#text(fill: rgb("{color}"))[{inner}]')
    text = _RE_COLOR_SPAN.sub(_color_span, text)

    # Highlight marks: <mark style="background: #XXX; ...">text</mark>
    def _mark_highlight(m):
        bg = m.group(1)
        inner = _inline_format(m.group(2))
        return _save_raw('mark', f'#highlight(fill: rgb("{bg}"))[{inner}]')
    text = _RE_MARK_HIGHLIGHT.sub(_mark_highlight, text)

    # Replace <br> with linebreak before stripping other HTML tags
    text = re.sub(r'<br\s*/?>', ' #linebreak() ', text)
    # Convert <sub>text</sub> and <sup>text</sup> to Typst
    text = re.sub(r'<sub>(.*?)</sub>', lambda m: _save_raw('sub', f'#sub[{_inline_escape_only(m.group(1))}]'), text)
    text = re.sub(r'<sup>(.*?)</sup>', lambda m: _save_raw('sup', f'#super[{_inline_escape_only(m.group(1))}]'), text)
    # Strip any remaining HTML tags (stray </span>, <mark>, <div>, etc.)
    text = re.sub(r'</?(?:span|mark|div)[^>]*>', '', text)

    # Bold+italic: ***text***
    text = re.sub(r'\*\*\*(.+?)\*\*\*', lambda m: _save(m, '*_{}_*'), text)
    # Bold: **text** — use #text(weight:"bold") when adjacent to word chars
    def _bold_replace(m):
        inner = _inline_escape_only(m.group(1))
        # Check if bold end is immediately followed by a word char
        end_pos = m.end()
        if end_pos < len(text) and text[end_pos:end_pos+1].isalnum():
            return _save_raw('bold', f'#text(weight: "bold")[{inner}]')
        return _save_raw('bold', f'*{inner}*')
    text = re.sub(r'\*\*(.+?)\*\*', _bold_replace, text)
    # Italic: *text* — use #emph when adjacent to word chars
    def _italic_replace(m):
        inner = _inline_escape_only(m.group(1))
        end_pos = m.end()
        if end_pos < len(text) and text[end_pos:end_pos+1].isalnum():
            return _save_raw('italic', f'#emph[{inner}]')
        return _save_raw('italic', f'_{inner}_')
    text = re.sub(r'\*(\w+)\*', _italic_replace, text)
    # Inline code: `text`
    text = re.sub(r'`(.+?)`', lambda m: _save(m, '`{}`'), text)

    # Escape remaining plain text
    text = escape_typst(text)

    # Restore placeholders
    for key, val in placeholders:
        text = text.replace(key, val)

    return text


def _inline_escape_only(text: str) -> str:
    """Escape only truly special chars inside already-formatted spans."""
    text = text.replace("\\", "\\\\")
    for ch in ['#', '[', ']', '@', '<', '>', '~']:
        text = text.replace(ch, f"\\{ch}")
    return text


# ─────────────────────────── markdown parser ──────────────────────────────

_RE_HEADING = re.compile(r'^(#{1,4})\s+(.+)$')
_RE_TABLE_ROW = re.compile(r'^\|(.+)\|$')
_RE_TABLE_SEP = re.compile(r'^\|[\s\-:|]+\|$')
_RE_IMG_COMMENT = re.compile(r'^<!--\s*(img:.+?)\s*-->$')
_RE_IMG_EMBED = re.compile(r'^!\[\[([^|\]]+?)(?:\|\d+)?\]\]$')
_RE_CALLOUT_WARNING = re.compile(r'^>\s*(?:\u26a0\ufe0f?\s*)?\*\*Enfasi docente:?\*\*\s*(.*)$')
_RE_CALLOUT_OBS = re.compile(r'^>\s*\[!warning\]\s*(.*)$')
_RE_LIST_ITEM = re.compile(r'^(\s*)[-*]\s+(.+)$')
_RE_NUMBERED_ITEM = re.compile(r'^(\s*)\d+[.)]\s+(.+)$')
_RE_HRULE = re.compile(r'^-{3,}\s*$')
_RE_RECAP_HEADING = re.compile(r'^###\s+Riepilogo\s+rapido', re.IGNORECASE)
_RE_IMG_PLACEHOLDER = re.compile(r'^>\s*\[immagine di:.*\]', re.IGNORECASE)
_RE_UNRESOLVED = re.compile(r'^<!--\s*UNRESOLVED:.*-->$', re.IGNORECASE)
_RE_UNRESOLVED_INLINE = re.compile(r'<!--\s*UNRESOLVED:.*?-->', re.IGNORECASE)
_RE_BLOCKQUOTE_BULLET = re.compile(r'^>\s*[-*]\s+(.+)$')
_RE_COLOR_SPAN = re.compile(
    r'<span\s+style=["\u00ab]color:\s*(#[0-9a-fA-F]{3,8})["\u00bb]\s*>(.*?)</span>',
    re.DOTALL,
)
_RE_MARK_HIGHLIGHT = re.compile(
    r'<mark\s+style=["\u00ab]background:\s*(#[0-9a-fA-F]{3,8})'
    r'(?:;\s*color:\s*#[0-9a-fA-F]{3,8})?["\u00bb]\s*>(.*?)</mark>',
    re.DOTALL,
)
_RE_LATEX_INLINE = re.compile(r'\\\((.+?)\\\)')  # \(expr\) -> $expr$


def parse_markdown(text: str) -> list[Element]:
    """Parse enriched markdown into a list of Element blocks."""
    lines = text.split('\n')
    elements: list[Element] = []
    i = 0
    n = len(lines)
    pending_img_meta: Optional[ImageMeta] = None

    while i < n:
        line = lines[i].rstrip()

        # ── blank line ──
        if not line.strip():
            i += 1
            continue

        # ── horizontal rule ──
        if _RE_HRULE.match(line):
            elements.append(Element(kind='hrule'))
            i += 1
            continue

        # ── skip image placeholder lines: > [immagine di: ...] ──
        if _RE_IMG_PLACEHOLDER.match(line.strip()):
            i += 1
            continue

        # ── skip UNRESOLVED comments: <!-- UNRESOLVED: ... --> ──
        if _RE_UNRESOLVED.match(line.strip()):
            i += 1
            continue

        # ── image metadata comment ──
        m = _RE_IMG_COMMENT.match(line.strip())
        if m:
            pending_img_meta = _parse_img_comment(m.group(1))
            i += 1
            continue

        # ── image embed (single or multiple on same line) ──
        stripped = line.strip()
        # Handle multiple ![[...]] on one line (e.g., side-by-side SVGs from chem renderer)
        multi_imgs = re.findall(r'!\[\[([^|\]]+?)(?:\|\d+)?\]\]', stripped)
        if multi_imgs and stripped.startswith('![['):
            for fname in multi_imgs:
                meta = pending_img_meta or ImageMeta()
                meta.filename = fname
                elements.append(Element(kind='image', image=meta))
                pending_img_meta = None
            i += 1
            continue

        # ── heading (check recap first) ──
        m = _RE_HEADING.match(line)
        if m:
            lvl = len(m.group(1))
            title = m.group(2).strip()

            # Riepilogo rapido: collect following bullet list
            if lvl == 3 and _RE_RECAP_HEADING.match(line):
                i += 1
                items = []
                while i < n:
                    lm = _RE_LIST_ITEM.match(lines[i].rstrip())
                    if lm:
                        items.append(lm.group(2))
                        i += 1
                    elif not lines[i].strip():
                        i += 1  # skip blanks inside list
                    else:
                        break
                elements.append(Element(kind='recap', items=items))
                continue

            kind = f'heading{lvl}'
            elements.append(Element(kind=kind, text=title, level=lvl))
            i += 1
            continue

        # ── callout (enfasi docente) ──
        mc = _RE_CALLOUT_WARNING.match(line) or _RE_CALLOUT_OBS.match(line)
        if mc:
            callout_lines = [mc.group(1)]
            i += 1
            while i < n and lines[i].startswith('>'):
                callout_lines.append(lines[i].lstrip('> '))
                i += 1
            elements.append(Element(kind='callout', text=' '.join(l for l in callout_lines if l)))
            continue

        # ── table ──
        if _RE_TABLE_ROW.match(line):
            rows = []
            raw = []
            while i < n and _RE_TABLE_ROW.match(lines[i].rstrip()):
                raw.append(lines[i].rstrip())
                if not _RE_TABLE_SEP.match(lines[i].rstrip()):
                    cells = [c.strip() for c in lines[i].strip().strip('|').split('|')]
                    rows.append(cells)
                i += 1
            elements.append(Element(kind='table', rows=rows, raw_lines=raw))
            continue

        # ── blockquote bullet list: > * text / > - text ──
        bqm = _RE_BLOCKQUOTE_BULLET.match(line)
        if bqm:
            items = []
            while i < n:
                bqm2 = _RE_BLOCKQUOTE_BULLET.match(lines[i].rstrip())
                if bqm2:
                    items.append(bqm2.group(1))
                    i += 1
                elif not lines[i].strip():
                    i += 1
                else:
                    break
            if items:
                elements.append(Element(kind='list', items=items))
            continue

        # ── plain blockquote line: > text (without bullet) ──
        if line.startswith('>') and not _RE_CALLOUT_WARNING.match(line) and not _RE_CALLOUT_OBS.match(line) and not _RE_IMG_PLACEHOLDER.match(line.strip()):
            bq_text = line.lstrip('> ').strip()
            if bq_text:
                elements.append(Element(kind='paragraph', text=bq_text, raw_lines=[bq_text]))
            i += 1
            continue

        # ── unordered list ──
        lm = _RE_LIST_ITEM.match(line)
        if lm:
            items = []
            while i < n:
                lm2 = _RE_LIST_ITEM.match(lines[i].rstrip())
                if lm2:
                    items.append(lm2.group(2))
                    i += 1
                elif not lines[i].strip():
                    i += 1
                else:
                    break
            elements.append(Element(kind='list', items=items))
            continue

        # ── numbered list ──
        nm = _RE_NUMBERED_ITEM.match(line)
        if nm:
            items = []
            while i < n:
                nm2 = _RE_NUMBERED_ITEM.match(lines[i].rstrip())
                if nm2:
                    items.append(nm2.group(2))
                    i += 1
                elif _RE_LIST_ITEM.match(lines[i].rstrip()):
                    # Sub-bullet inside numbered list
                    items.append(lines[i].rstrip().lstrip().lstrip('-* '))
                    i += 1
                elif not lines[i].strip():
                    i += 1
                else:
                    break
            elements.append(Element(kind='numbered_list', items=items))
            continue

        # ── paragraph (default) ──
        para_lines = []
        while i < n:
            l = lines[i].rstrip()
            if (not l.strip() or _RE_HEADING.match(l) or _RE_TABLE_ROW.match(l)
                    or _RE_HRULE.match(l) or _RE_IMG_COMMENT.match(l.strip())
                    or _RE_IMG_EMBED.match(l.strip()) or _RE_CALLOUT_WARNING.match(l)
                    or _RE_CALLOUT_OBS.match(l)
                    or _RE_LIST_ITEM.match(l)
                    or _RE_NUMBERED_ITEM.match(l)
                    or _RE_IMG_PLACEHOLDER.match(l.strip())
                    or _RE_UNRESOLVED.match(l.strip())
                    or _RE_BLOCKQUOTE_BULLET.match(l)
                    or (l.startswith('>') and not l.startswith('> [!') and not _RE_IMG_PLACEHOLDER.match(l.strip()))):
                break
            para_lines.append(l)
            i += 1
        if para_lines:
            elements.append(Element(kind='paragraph', text='\n'.join(para_lines),
                                    raw_lines=para_lines))

    return elements


def _parse_img_comment(raw: str) -> ImageMeta:
    """Parse img:key=\"value\" pairs from an HTML comment."""
    meta = ImageMeta()
    for m in re.finditer(r'img:(\w+)="([^"]*)"', raw):
        key, val = m.group(1), m.group(2)
        if key == 'caption':
            meta.caption = val
        elif key == 'size_class':
            meta.size_class = val
        elif key == 'aspect_ratio':
            try:
                meta.aspect_ratio = float(val)
            except ValueError:
                pass
    return meta


# ─────────────────────────── layout decision tree ─────────────────────────

def _decide_layout(elements: list[Element]) -> list[tuple[Element, str]]:
    """
    Walk elements and annotate each image with a layout decision:
        'centered'   -> #figure(image(...))
        'float-right' -> #float-right(...)
        'float-left'  -> #float-left(...)

    Returns list of (element, layout) where layout is '' for non-images.
    """
    result: list[tuple[Element, str]] = []
    last_image_idx = -100
    float_side_toggle = True  # True = right next, False = left next

    for idx, el in enumerate(elements):
        if el.kind != 'image':
            result.append((el, ''))
            continue

        img = el.image
        layout = _image_layout_decision(
            img=img,
            idx=idx,
            elements=elements,
            last_image_idx=last_image_idx,
            float_side_toggle=float_side_toggle,
        )

        if layout.startswith('float'):
            float_side_toggle = not float_side_toggle
        result.append((el, layout))
        last_image_idx = idx

    return result


def _image_layout_decision(
    img: ImageMeta,
    idx: int,
    elements: list[Element],
    last_image_idx: int,
    float_side_toggle: bool,
) -> str:
    """Apply the decision tree for a single image."""

    # Rule 1: large images -> centered
    if img.size_class == 'large':
        return 'centered'

    # Rule 2: taller-than-wide -> centered
    if img.aspect_ratio < 0.8:
        return 'centered'

    # Rule 3: next element is table/recap/heading -> centered
    nxt = _next_content(elements, idx)
    if nxt and nxt.kind in ('table', 'recap', 'heading1', 'heading2', 'heading3'):
        return 'centered'

    # Rule 4: near end of block (position > 0.85)
    block_total, pos_in_block = _block_position(elements, idx)
    if block_total > 0 and (pos_in_block / block_total) > 0.85:
        return 'centered'

    # Rule 5: block too short
    if 0 < block_total < 10:
        return 'centered'

    # Rule 6: too close to previous image
    if (idx - last_image_idx) < 5:
        return 'centered'

    # Rule 7 & 8 handled implicitly by rules above

    # Count text lines after image until next heading/image
    lines_after = _lines_after(elements, idx)

    # Rule 9: medium + enough text
    if img.size_class == 'medium' and lines_after >= 8:
        return 'float-right' if float_side_toggle else 'float-left'

    # Rule 10: small + enough text
    if img.size_class == 'small' and lines_after >= 5:
        return 'float-right' if float_side_toggle else 'float-left'

    # Rule 11: fallback
    return 'centered'


def _next_content(elements: list[Element], idx: int) -> Optional[Element]:
    """Return the next non-blank element after idx, or None."""
    for j in range(idx + 1, len(elements)):
        if elements[j].kind != 'blank':
            return elements[j]
    return None


def _block_position(elements: list[Element], idx: int) -> tuple[int, int]:
    """
    Find the "block" around idx (between headings) and return
    (total_elements_in_block, position_of_idx_in_block).
    """
    # Walk back to previous heading
    start = idx
    for j in range(idx - 1, -1, -1):
        if elements[j].kind.startswith('heading'):
            start = j + 1
            break
    else:
        start = 0

    # Walk forward to next heading
    end = len(elements)
    for j in range(idx + 1, len(elements)):
        if elements[j].kind.startswith('heading'):
            end = j
            break

    total = end - start
    pos = idx - start
    return total, pos


def _lines_after(elements: list[Element], idx: int) -> int:
    """Count approximate text lines between image and next heading/image."""
    count = 0
    for j in range(idx + 1, len(elements)):
        el = elements[j]
        if el.kind.startswith('heading') or el.kind == 'image':
            break
        if el.kind == 'paragraph':
            count += len(el.raw_lines) if el.raw_lines else el.text.count('\n') + 1
        elif el.kind in ('list', 'numbered_list'):
            count += len(el.items)
        elif el.kind == 'table':
            count += len(el.rows)
        elif el.kind == 'callout':
            count += 2
    return count


# ─────────────────────────── typst generation ─────────────────────────────

def generate_typst(
    elements: list[Element],
    subject: str,
    lesson: str,
    image_dir: Path,
) -> str:
    """Generate a complete .typ file string from parsed elements."""

    template_path = PROJECT_ROOT / TEMPLATE_REL
    # Typst import path: absolute relative to --root (prefix with /)
    template_import = "/" + TEMPLATE_REL

    parts: list[str] = []

    # ── preamble ──
    parts.append(f'#import "{template_import}": quick-recap, float-right, float-left\n')
    parts.append(_preamble(subject, lesson))
    parts.append('')

    # ── layout decisions ──
    annotated = _decide_layout(elements)

    for i_el, (el, layout) in enumerate(annotated):
        rendered = _render_element(el, layout, image_dir)

        # Group short paragraph with following table (keep title+table on same page)
        if (el.kind == 'paragraph'
                and len(el.text.splitlines()) <= 2
                and i_el + 1 < len(annotated)
                and annotated[i_el + 1][0].kind == 'table'):
            rendered = f'#block(breakable: false)[\n{rendered}'
            # The closing ] will be added after the table
            parts.append(rendered)
            continue

        # Close the title+table group
        if (el.kind == 'table'
                and i_el > 0
                and annotated[i_el - 1][0].kind == 'paragraph'
                and len(annotated[i_el - 1][0].text.splitlines()) <= 2):
            rendered = f'{rendered}]\n'

        parts.append(rendered)

    return '\n'.join(parts)


def _preamble(subject: str, lesson: str) -> str:
    subj_display = subject.replace('_', ' ').title()
    lesson_display = lesson.replace('_', ' ').title()
    return f'''#set page(
  paper: "a4",
  margin: (top: 2.5cm, bottom: 2.5cm, left: 2.5cm, right: 2cm),
  numbering: "1",
  number-align: center + bottom,
  header: context [
    #set text(8pt, fill: luma(120))
    #smallcaps[{_inline_escape_only(subj_display)} \\— {_inline_escape_only(lesson_display)}]
    #h(1fr)
    #datetime.today().display("[day]/[month]/[year]")
  ],
)

#set text(font: "Linux Libertine", size: 11pt, lang: "it")
#set par(leading: 0.75em, spacing: 1.2em, justify: true, linebreaks: "optimized")

#show heading.where(level: 1): it => {{
  pagebreak(weak: true)
  v(0.5em)
  block(width: 100%, fill: rgb("#003366"), inset: (x: 10pt, y: 8pt), radius: 3pt,
    text(fill: white, size: 16pt, weight: "bold", it.body))
  v(0.5em)
}}

#show heading.where(level: 2): it => {{
  v(0.4em)
  text(size: 13pt, weight: "bold", fill: rgb("#003366"), it.body)
  v(0.2em)
}}

#show heading.where(level: 3): it => {{
  v(0.3em)
  text(size: 11pt, weight: "bold", it.body)
  v(0.1em)
}}

#show heading.where(level: 4): it => {{
  v(0.2em)
  text(size: 10.5pt, weight: "bold", style: "italic", it.body)
  v(0.1em)
}}

// Keep headings with the content that follows them (avoid orphan titles)
#show heading: set block(sticky: true)

#show table: set block(breakable: false)
'''


def _render_element(el: Element, layout: str, image_dir: Path) -> str:
    """Render a single element to Typst markup."""

    if el.kind == 'heading1':
        return f'= {_inline_format(el.text)}\n'

    if el.kind == 'heading2':
        # Force pagebreak before APPENDICE TABELLARE so title stays with tables
        prefix = ''
        if 'APPENDICE' in el.text.upper() and 'TABELLARE' in el.text.upper():
            prefix = '#pagebreak(weak: true)\n'
        return f'{prefix}== {_inline_format(el.text)}\n'

    if el.kind == 'heading3':
        return f'=== {_inline_format(el.text)}\n'

    if el.kind == 'heading4':
        return f'==== {_inline_format(el.text)}\n'

    if el.kind == 'paragraph':
        return _inline_format(el.text) + '\n'

    if el.kind == 'hrule':
        return '#line(length: 100%, stroke: 0.5pt + luma(180))\n'

    if el.kind == 'callout':
        return _render_callout(el.text)

    if el.kind == 'list':
        return _render_list(el.items)

    if el.kind == 'numbered_list':
        return _render_numbered_list(el.items)

    if el.kind == 'table':
        return _render_table(el.rows)

    if el.kind == 'recap':
        return _render_recap(el.items)

    if el.kind == 'image':
        return _render_image(el, layout, image_dir)

    return ''


def _render_callout(text: str) -> str:
    escaped = _inline_format(text)
    return (
        '#block(\n'
        '  breakable: false,\n'
        '  fill: rgb("#fff3e0"),\n'
        '  inset: (left: 12pt, right: 10pt, top: 10pt, bottom: 10pt),\n'
        '  stroke: (left: 4pt + rgb("#e65100")),\n'
        '  width: 100%,\n'
        '  [\n'
        '    #text(weight: "bold", fill: rgb("#e65100"))[Enfasi docente]\n'
        '    #v(0.3em)\n'
        f'    {escaped}\n'
        '  ]\n'
        ')\n'
    )


def _render_list(items: list[str]) -> str:
    lines = []
    for item in items:
        lines.append(f'- {_inline_format(item)}')
    return '\n'.join(lines) + '\n'


def _render_numbered_list(items: list[str]) -> str:
    lines = []
    for idx, item in enumerate(items, 1):
        lines.append(f'+ {_inline_format(item)}')
    return '\n'.join(lines) + '\n'


def _render_table(rows: list[list[str]]) -> str:
    if not rows:
        return ''
    ncols = max(len(r) for r in rows)
    parts = [
        '#table(',
        f'  columns: {ncols},',
        '  inset: 7pt,',
        '  stroke: 0.6pt + luma(100),',
        '  fill: (x, y) => if y == 0 { rgb("#003366") } else if calc.odd(y) { luma(245) } else { white },',
    ]

    # Header row
    if rows:
        header_cells = ', '.join(
            f'text(fill: white, weight: "bold")[{_inline_format(c)}]'
            for c in _pad_row(rows[0], ncols)
        )
        parts.append(f'  table.header({header_cells}),')

    # Data rows
    for row in rows[1:]:
        cells = ', '.join(f'[{_inline_format(c)}]' for c in _pad_row(row, ncols))
        parts.append(f'  {cells},')

    parts.append(')\n')
    return '\n'.join(parts)


def _pad_row(row: list[str], ncols: int) -> list[str]:
    """Ensure row has exactly ncols cells."""
    padded = list(row)
    while len(padded) < ncols:
        padded.append('')
    return padded[:ncols]


def _render_recap(items: list[str]) -> str:
    bullet_lines = '\n'.join(f'    - {_inline_format(it)}' for it in items)
    return (
        '#quick-recap[\n'
        f'{bullet_lines}\n'
        ']\n'
    )


def _render_image(el: Element, layout: str, image_dir: Path) -> str:
    img = el.image
    if not img or not img.filename:
        return ''

    # Build path relative to PROJECT_ROOT (used with --root)
    img_path_on_disk = image_dir / img.filename
    if not img_path_on_disk.exists():
        print(f'  [pdf] WARNING: image not found: {img_path_on_disk}')
        return f'// [MISSING IMAGE: {img.filename}]\n'

    try:
        rel_path = img_path_on_disk.relative_to(PROJECT_ROOT)
    except ValueError:
        # Image outside project root — use absolute
        rel_path = img_path_on_disk
    # Prefix with / so Typst resolves relative to --root
    img_typst = "/" + str(rel_path).replace('\\', '/')

    caption_arg = ''
    if img.caption:
        caption_arg = f', caption-text: [{_inline_format(img.caption)}]'

    if layout == 'centered':
        if img.caption:
            return (
                f'#figure(\n'
                f'  image("{img_typst}", width: 80%),\n'
                f'  caption: [{_inline_format(img.caption)}],\n'
                f')\n'
            )
        else:
            return f'#figure(image("{img_typst}", width: 80%))\n'

    if layout == 'float-right':
        # Collect text after this image until next structural break
        # We use a placeholder — actual text is embedded at generation time
        width = '35%' if img.size_class == 'small' else '38%'
        return (
            f'// float-right placeholder — requires manual text wrapping\n'
            f'#float-right("{img_typst}", img-width: {width}{caption_arg})[\n'
            f'  // Text flows here (filled by surrounding paragraphs)\n'
            f']\n'
        )

    if layout == 'float-left':
        width = '35%' if img.size_class == 'small' else '38%'
        return (
            f'#float-left("{img_typst}", img-width: {width}{caption_arg})[\n'
            f'  // Text flows here\n'
            f']\n'
        )

    # Fallback
    return f'#figure(image("{img_typst}", width: 80%))\n'


# ─────────────────────── float text absorption ────────────────────────────

def _absorb_float_text(typst_source: str) -> str:
    """
    Post-process: when we have a float-right/float-left followed by a paragraph,
    move the paragraph text into the float's body bracket.
    """
    lines = typst_source.split('\n')
    result = []
    i = 0
    while i < len(lines):
        line = lines[i]

        # Detect float placeholder
        if '// Text flows here' in line and line.strip() == '// Text flows here (filled by surrounding paragraphs)':
            # Look ahead: next meaningful line after the closing ] should be paragraph text
            # The pattern is:
            #   #float-right(...)[
            #     // Text flows here ...
            #   ]
            #   <paragraph text>
            # We want to replace the comment + ] with the paragraph text + ]
            result.append(line)  # keep for now, will be replaced below
            i += 1
            continue

        # Simpler approach: find float blocks and absorb next paragraph
        if (line.strip().startswith('#float-right(') or line.strip().startswith('#float-left(')) and line.rstrip().endswith('['):
            float_line = line
            # Skip comment line
            i += 1
            if i < len(lines) and '// Text flows here' in lines[i]:
                i += 1  # skip comment
            # Skip closing ]
            if i < len(lines) and lines[i].strip() == ']':
                i += 1
            # Now collect the next paragraph
            para_lines = []
            while i < len(lines) and lines[i].strip() and not lines[i].strip().startswith('#') and not lines[i].strip().startswith('='):
                para_lines.append(lines[i])
                i += 1

            if para_lines:
                result.append(float_line)
                for pl in para_lines:
                    result.append(f'  {pl}')
                result.append(']')
            else:
                # No paragraph to absorb — convert to centered figure
                # Extract image path from the float call
                m = re.search(r'#float-(?:right|left)\("([^"]+)"', float_line)
                if m:
                    result.append(f'#figure(image("{m.group(1)}", width: 80%))')
                else:
                    result.append(float_line)
                    result.append(']')
            continue

        result.append(line)
        i += 1

    return '\n'.join(result)


# ─────────────────────────── main pipeline ────────────────────────────────

def resolve_image_dir(subject: str, lesson: str) -> Path:
    """Find directory containing images for this sbobina."""
    # Primary: assets dir created by inject_images.py
    assets_dir = PROJECT_ROOT / 'sbobine' / subject / 'assets' / lesson
    if assets_dir.is_dir():
        return assets_dir
    # Fallbacks
    candidates = [
        PROJECT_ROOT / 'workspace' / subject / lesson / 'images',
        PROJECT_ROOT / 'sbobine' / 'strutture',
        PROJECT_ROOT / 'sbobine' / subject,
        PROJECT_ROOT,
    ]
    for c in candidates:
        if c.is_dir():
            return c
    return PROJECT_ROOT


def generate_pdf_for_pipeline(
    subject: str,
    lesson: str,
    input_path: Optional[Path] = None,
) -> Optional[Path]:
    """
    Main entry point (importable from pipeline.py).

    Returns the output PDF path on success, None on failure.
    """
    # ── resolve input ──
    if input_path is None:
        test_path = PROJECT_ROOT / 'sbobine' / subject / f'{lesson}_test.md'
        normal_path = PROJECT_ROOT / 'sbobine' / subject / f'{lesson}.md'
        if test_path.exists():
            input_path = test_path
        elif normal_path.exists():
            input_path = normal_path
        else:
            print(f'[pdf] ERROR: no input file found for {subject}/{lesson}')
            return None

    if not input_path.exists():
        print(f'[pdf] ERROR: input file not found: {input_path}')
        return None

    # ── check typst ──
    if not shutil.which('typst'):
        print('[pdf] ERROR: typst is not installed. Install with: brew install typst')
        return None

    # ── output paths ──
    out_dir = PROJECT_ROOT / 'pdf_output' / subject
    out_dir.mkdir(parents=True, exist_ok=True)
    typ_path = out_dir / f'{lesson}.typ'
    pdf_path = out_dir / f'{lesson}.pdf'

    image_dir = resolve_image_dir(subject, lesson)

    # ── step 1: parse ──
    print(f'[pdf] Parsing markdown: {input_path}')
    md_text = input_path.read_text(encoding='utf-8')
    elements = parse_markdown(md_text)
    print(f'[pdf]   -> {len(elements)} elements parsed')

    # ── step 2: generate typst ──
    print('[pdf] Generating Typst...')
    typst_source = generate_typst(elements, subject, lesson, image_dir)

    # Post-process: absorb text into float blocks
    typst_source = _absorb_float_text(typst_source)

    typ_path.write_text(typst_source, encoding='utf-8')
    print(f'[pdf]   -> {typ_path}')

    # ── step 3: compile ──
    print('[pdf] Compiling PDF...')
    result = subprocess.run(
        ['typst', 'compile', '--root', str(PROJECT_ROOT), str(typ_path), str(pdf_path)],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print(f'[pdf] ERROR: typst compile failed:\n{result.stderr}')
        return None

    if result.stderr:
        # Warnings (non-fatal)
        for line in result.stderr.strip().split('\n'):
            print(f'[pdf] typst: {line}')

    print(f'[pdf] Done: {pdf_path}')
    return pdf_path


# ─────────────────────────── CLI ──────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description='Convert enriched markdown sbobina to PDF via Typst.',
    )
    parser.add_argument('subject', help='Subject name (e.g., anatomia)')
    parser.add_argument('lesson', help='Lesson name (e.g., lezione_01)')
    parser.add_argument('--input', type=Path, default=None,
                        help='Path to input markdown (default: sbobine/{subject}/{lesson}.md)')

    args = parser.parse_args()

    pdf = generate_pdf_for_pipeline(args.subject, args.lesson, args.input)
    if pdf is None:
        sys.exit(1)


if __name__ == '__main__':
    main()
