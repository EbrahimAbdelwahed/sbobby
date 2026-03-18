"""
Parser per sbobine vecchie: DOC/DOCX/PDF → plaintext.

Uso:
    python parse_doc.py <file_o_directory> [output_dir]
"""

import subprocess
from pathlib import Path


def parse_pdf(path: Path) -> str:
    """Estrae testo da PDF via PyMuPDF."""
    import fitz

    doc = fitz.open(str(path))
    pages = []
    for page in doc:
        text = page.get_text().strip()
        if text:
            pages.append(text)
    doc.close()

    return "\n\n---\n\n".join(pages)


def parse_docx(path: Path) -> str:
    """Estrae testo da DOCX via python-docx."""
    from docx import Document

    doc = Document(str(path))
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]

    return "\n\n".join(paragraphs)


def parse_doc(path: Path) -> str:
    """Estrae testo da DOC legacy via textutil (macOS built-in)."""
    result = subprocess.run(
        ["textutil", "-convert", "txt", "-stdout", str(path)],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"textutil fallito per {path}: {result.stderr}")

    return result.stdout.strip()


def parse_file(path: Path) -> str:
    """Dispatcha al parser giusto in base all'estensione."""
    ext = path.suffix.lower()
    if ext == ".pdf":
        return parse_pdf(path)
    elif ext == ".docx":
        return parse_docx(path)
    elif ext == ".doc":
        return parse_doc(path)
    else:
        raise ValueError(f"Formato non supportato: {ext} (supportati: .pdf, .docx, .doc)")


def parse_directory(input_dir: Path, output_dir: Path) -> list[Path]:
    """Parsa tutti i documenti in una directory."""
    output_dir.mkdir(parents=True, exist_ok=True)
    results = []

    files = sorted(
        f for f in input_dir.iterdir()
        if f.suffix.lower() in (".pdf", ".docx", ".doc")
    )

    if not files:
        print(f"[parse_doc] Nessun documento trovato in {input_dir}")
        return results

    for f in files:
        print(f"[parse_doc] Parsing {f.name}...")
        try:
            text = parse_file(f)
            out_path = output_dir / (f.stem + ".txt")
            out_path.write_text(text, encoding="utf-8")
            word_count = len(text.split())
            print(f"  → {out_path.name} (~{word_count} parole)")
            results.append(out_path)
        except Exception as e:
            print(f"  ✗ Errore: {e}")

    return results


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Uso: python parse_doc.py <file_o_directory> [output_dir]")
        sys.exit(1)

    input_p = Path(sys.argv[1])
    if input_p.is_dir():
        output_d = Path(sys.argv[2]) if len(sys.argv) > 2 else input_p.parent / "parsed"
        parse_directory(input_p, output_d)
    else:
        text = parse_file(input_p)
        if len(sys.argv) > 2:
            out = Path(sys.argv[2])
            out.write_text(text, encoding="utf-8")
            print(f"[parse_doc] Output: {out}")
        else:
            print(text)
