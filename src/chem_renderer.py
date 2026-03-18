"""
Modulo per rendering strutture chimiche nella sbobina.

Risolve marker [CHEM:nome] e [REACTION:...] in immagini SVG/PNG
renderizzate con RDKit, iniettate come HTML nel markdown.

Uso standalone:
    python src/chem_renderer.py input.md output.md [--structures-dir DIR]
"""

import hashlib
import json
import logging
import re
import sys
from pathlib import Path
from typing import Optional

import pubchempy as pcp
from rdkit import Chem
from rdkit.Chem import AllChem, Draw, rdChemReactions
from rdkit.Chem.Draw import rdMolDraw2D

PROJECT_ROOT = Path(__file__).parent.parent
CONFIG_DIR = PROJECT_ROOT / "config" / "biochimica"
CACHE_PATH = CONFIG_DIR / "smiles_cache.json"
DICT_PATH = CONFIG_DIR / "chem_dictionary.json"

CHEM_RE = re.compile(r"\[CHEM:(.+?)\]")
REACTION_RE = re.compile(r"\[REACTION:(.+?)\]")

logger = logging.getLogger(__name__)


# ── Cache ──────────────────────────────────────────────────────────

def _load_json(path: Path) -> dict:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


def _save_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


# ── Resolver: nome → SMILES ────────────────────────────────────────

def _pubchem_lookup(name: str) -> Optional[str]:
    """Cerca SMILES su PubChem per nome."""
    try:
        results = pcp.get_compounds(name, "name")
        if results:
            return results[0].smiles
    except Exception as e:
        logger.debug(f"PubChem lookup fallito per '{name}': {e}")
    return None


def resolve_name(name: str, cache: dict, dictionary: dict) -> Optional[str]:
    """Risolve un nome italiano in SMILES. Fallback chain:
    1. Cache locale
    2. Dizionario IT→EN + PubChem
    3. PubChem diretto
    """
    key = name.strip().lower()

    # 1. Cache
    if key in cache:
        return cache[key] if cache[key] else None

    # 2. Dizionario IT→EN → PubChem
    en_name = dictionary.get(key)
    if en_name:
        smiles = _pubchem_lookup(en_name)
        if smiles:
            cache[key] = smiles
            return smiles

    # 3. PubChem diretto col nome italiano
    smiles = _pubchem_lookup(key)
    if smiles:
        cache[key] = smiles
        return smiles

    # Non trovato — segna in cache come None per non riprovare
    cache[key] = ""
    return None


# ── Renderer: SMILES → immagine ────────────────────────────────────

def _file_hash(content: str) -> str:
    return hashlib.sha256(content.encode()).hexdigest()[:16]


def render_molecule(smiles: str, output_dir: Path, name: str = "") -> Optional[Path]:
    """Renderizza una molecola come SVG con nome sotto. Ritorna il path del file."""
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        logger.warning(f"SMILES non valido: {smiles}")
        return None

    AllChem.Compute2DCoords(mol)
    # Hash include il nome così SVG viene rigenerato se il nome cambia
    h = _file_hash(smiles + "|" + name)
    out_path = output_dir / f"{h}.svg"

    if out_path.exists():
        return out_path

    mol_w, mol_h = 250, 200
    label_h = 30 if name else 0
    total_h = mol_h + label_h

    drawer = rdMolDraw2D.MolDraw2DSVG(mol_w, mol_h)
    drawer.DrawMolecule(mol)
    drawer.FinishDrawing()
    svg = drawer.GetDrawingText()

    if name:
        # Espandi il viewBox/height per includere il nome
        svg = svg.replace(
            f"width='{mol_w}px' height='{mol_h}px'",
            f"width='{mol_w}px' height='{total_h}px'"
        )
        svg = svg.replace(
            f"viewBox='0 0 {mol_w} {mol_h}'",
            f"viewBox='0 0 {mol_w} {total_h}'"
        )
        # Inietta il testo prima di </svg>
        label_svg = (
            f'<text x="{mol_w // 2}" y="{mol_h + 20}" '
            f'text-anchor="middle" '
            f'font-family="Helvetica, Arial, sans-serif" '
            f'font-size="14px" font-weight="bold" '
            f'fill="#333333">{name}</text>'
        )
        svg = svg.replace("</svg>", f"{label_svg}\n</svg>")

    output_dir.mkdir(parents=True, exist_ok=True)
    out_path.write_text(svg, encoding="utf-8")
    return out_path


def render_reaction(reaction_smarts: str, output_dir: Path) -> Optional[Path]:
    """Renderizza una reazione come PNG. Ritorna il path del file."""
    rxn = rdChemReactions.ReactionFromSmarts(reaction_smarts, useSmiles=True)
    if rxn is None:
        logger.warning(f"Reazione non valida: {reaction_smarts}")
        return None

    h = _file_hash(reaction_smarts)
    out_path = output_dir / f"{h}.png"

    if out_path.exists():
        return out_path

    output_dir.mkdir(parents=True, exist_ok=True)
    img = Draw.ReactionToImage(rxn, subImgSize=(250, 200))
    img.save(str(out_path))
    return out_path


# ── Injector: marker → Obsidian embed ─────────────────────────────

def _obsidian_embed_single(img_path: Path) -> str:
    """Embed singolo (nome già nell'SVG)."""
    return f"![[{img_path.name}|250]]"


def _obsidian_embed_group(items: list[tuple[str, Path]]) -> str:
    """Embed multipli affiancati (nomi già negli SVG)."""
    if len(items) == 1:
        return _obsidian_embed_single(items[0][1])
    return " ".join(f"![[{img.name}|200]]" for _, img in items)


def _resolve_reaction_smiles(reaction_text: str, cache: dict, dictionary: dict,
                              unresolved: list) -> Optional[str]:
    """Converte testo reazione in SMARTS: 'A + B -> C + D' → 'smilesA.smilesB>>smilesC.smilesD'"""
    parts = re.split(r"\s*->\s*", reaction_text, maxsplit=1)
    if len(parts) != 2:
        logger.warning(f"Formato reazione non valido (manca '->'): {reaction_text}")
        return None

    sides = []
    for side in parts:
        compounds = [c.strip() for c in side.split("+")]
        smiles_list = []
        for compound in compounds:
            smiles = resolve_name(compound, cache, dictionary)
            if not smiles:
                unresolved.append(compound)
                return None
            smiles_list.append(smiles)
        sides.append(".".join(smiles_list))

    return ">>".join(sides)


# ── Processamento file ─────────────────────────────────────────────

def process_file(input_md: Path, output_md: Path, structures_dir: Path) -> None:
    """Processa un file markdown, risolvendo [CHEM:] e [REACTION:] in immagini."""
    text = input_md.read_text(encoding="utf-8")

    cache = _load_json(CACHE_PATH)
    dictionary = _load_json(DICT_PATH)
    # Normalizza chiavi dizionario a lowercase
    dictionary = {k.lower(): v for k, v in dictionary.items()}

    unresolved = []
    lines = text.split("\n")
    output_lines = []

    i = 0
    while i < len(lines):
        line = lines[i]

        # ── REACTION marker ──
        rmatch = REACTION_RE.search(line)
        if rmatch:
            reaction_text = rmatch.group(1)
            smarts = _resolve_reaction_smiles(reaction_text, cache, dictionary, unresolved)

            if smarts:
                img_path = render_reaction(smarts, structures_dir)
                if img_path:
                    clean_line = REACTION_RE.sub("", line).strip()
                    if clean_line:
                        output_lines.append(clean_line)
                    output_lines.append("")
                    output_lines.append(_obsidian_embed_single(img_path))
                    output_lines.append("")
                    i += 1
                    continue

            # Fallback: non risolto
            output_lines.append(line.replace(rmatch.group(0),
                                             f"<!-- UNRESOLVED: {reaction_text} -->"))
            i += 1
            continue

        # ── CHEM marker (possibili multipli sulla stessa riga o consecutivi) ──
        cmatches = list(CHEM_RE.finditer(line))
        if cmatches:
            mol_batch = []
            batch_start = i

            while i < len(lines):
                cms = list(CHEM_RE.finditer(lines[i]))
                if not cms and i > batch_start:
                    break
                if not cms:
                    break
                for cm in cms:
                    mol_batch.append((cm.group(1), cm.group(0), i))
                i += 1

            # Risolvi e renderizza
            rendered = []
            for name, marker, line_idx in mol_batch:
                smiles = resolve_name(name, cache, dictionary)
                if smiles:
                    img_path = render_molecule(smiles, structures_dir, name=name)
                    if img_path:
                        rendered.append((name, img_path, marker, line_idx))
                    else:
                        unresolved.append(name)
                else:
                    unresolved.append(name)

            if not rendered:
                for li in range(batch_start, i):
                    cleaned = lines[li]
                    for name, marker, line_idx in mol_batch:
                        if line_idx == li:
                            cleaned = cleaned.replace(marker,
                                                      f"<!-- UNRESOLVED: {name} -->")
                    output_lines.append(cleaned)
                continue

            # Output: testo del paragrafo (senza marker) + embed sotto
            for li in range(batch_start, max(i, batch_start + 1)):
                cleaned = lines[li]
                for n, m, lidx in mol_batch:
                    if lidx == li:
                        cleaned = cleaned.replace(m, "").strip()
                if cleaned:
                    output_lines.append(cleaned)

            output_lines.append("")
            group_items = [(name, img_path) for name, img_path, marker, line_idx in rendered]
            output_lines.append(_obsidian_embed_group(group_items))
            output_lines.append("")

            # Placeholder per molecole non renderizzate
            for name, marker, line_idx in mol_batch:
                if not any(r[0] == name for r in rendered):
                    output_lines.append(f"<!-- UNRESOLVED: {name} -->")

            continue

        # ── Riga normale ──
        output_lines.append(line)
        i += 1

    # Salva output
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text("\n".join(output_lines), encoding="utf-8")

    # Salva cache aggiornata
    _save_json(CACHE_PATH, cache)

    # Log unresolved
    if unresolved:
        log_path = structures_dir / "unresolved.log"
        structures_dir.mkdir(parents=True, exist_ok=True)
        with open(log_path, "a", encoding="utf-8") as f:
            for name in unresolved:
                f.write(f"{name}\n")
        print(f"[chem_renderer] {len(unresolved)} composti non risolti → {log_path}")

    resolved_count = len(list(structures_dir.glob("*"))) if structures_dir.exists() else 0
    print(f"[chem_renderer] Completato. Strutture renderizzate: {resolved_count}")


# ── CLI ────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 3:
        print("Uso: python src/chem_renderer.py input.md output.md [--structures-dir DIR]")
        sys.exit(1)

    input_md = Path(sys.argv[1])
    output_md = Path(sys.argv[2])

    structures_dir = output_md.parent / "structures"
    if "--structures-dir" in sys.argv:
        idx = sys.argv.index("--structures-dir")
        structures_dir = Path(sys.argv[idx + 1])

    if not input_md.exists():
        print(f"File non trovato: {input_md}")
        sys.exit(1)

    process_file(input_md, output_md, structures_dir)


if __name__ == "__main__":
    main()
