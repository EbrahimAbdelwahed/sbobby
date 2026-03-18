"""
Estrazione enfasi e pattern docente dalle sbobine vecchie via LLM.

Uso:
    python extract_emphasis.py <file_parsed.txt> [output_dir]
"""

import json
from pathlib import Path

from api_client import chat

PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "estrazione_enfasi.md"


def load_system_prompt() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8")


def chunk_text(text: str, chunk_words: int = 9000, overlap_words: int = 500) -> list[str]:
    """Splitta il testo in chunk a confini di pagina (---) con overlap.

    Cerca di rispettare i separatori di pagina come punti di taglio.
    """
    pages = text.split("\n\n---\n\n")

    # Se non ci sono separatori di pagina, splitta per parole
    if len(pages) <= 1:
        words = text.split()
        chunks = []
        start = 0
        while start < len(words):
            end = min(start + chunk_words, len(words))
            chunks.append(" ".join(words[start:end]))
            start = end - overlap_words if end < len(words) else end
        return chunks

    # Accumula pagine fino a raggiungere chunk_words
    chunks = []
    current_pages = []
    current_word_count = 0

    for page in pages:
        page_words = len(page.split())

        if current_word_count + page_words > chunk_words and current_pages:
            chunks.append("\n\n---\n\n".join(current_pages))

            # Overlap: tieni le ultime pagine fino a overlap_words
            overlap_pages = []
            overlap_count = 0
            for p in reversed(current_pages):
                pw = len(p.split())
                if overlap_count + pw > overlap_words:
                    break
                overlap_pages.insert(0, p)
                overlap_count += pw

            current_pages = overlap_pages
            current_word_count = overlap_count

        current_pages.append(page)
        current_word_count += page_words

    if current_pages:
        chunks.append("\n\n---\n\n".join(current_pages))

    return chunks


def extract_emphasis(chunk: str) -> dict:
    """Estrae enfasi da un singolo chunk via LLM."""
    system_prompt = load_system_prompt()
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": chunk},
    ]

    response = chat(messages, temperature=0.2)

    # Estrai JSON dalla risposta
    text = response.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1]
        text = text.rsplit("```", 1)[0]

    return json.loads(text)


def extract_emphasis_file(
    input_path: Path,
    output_dir: Path,
    chunk_words: int = 9000,
) -> list[Path]:
    """Processa un file intero in chunk, salva le estrazioni JSON."""
    output_dir.mkdir(parents=True, exist_ok=True)
    text = input_path.read_text(encoding="utf-8")
    chunks = chunk_text(text, chunk_words=chunk_words)

    print(f"[extract] {input_path.name}: {len(chunks)} chunk da processare")

    results = []
    for i, chunk in enumerate(chunks):
        word_count = len(chunk.split())
        print(f"[extract] Chunk {i+1}/{len(chunks)} (~{word_count} parole)...")

        try:
            data = extract_emphasis(chunk)
            out_path = output_dir / f"{input_path.stem}_chunk_{i+1:02d}.json"
            out_path.write_text(
                json.dumps(data, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            results.append(out_path)

            topics = data.get("argomenti_trattati", [])
            if topics:
                print(f"  Argomenti: {', '.join(topics[:3])}{'...' if len(topics) > 3 else ''}")
        except Exception as e:
            print(f"  ✗ Errore chunk {i+1}: {e}")

    return results


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Uso: python extract_emphasis.py <file_parsed.txt> [output_dir]")
        sys.exit(1)

    input_p = Path(sys.argv[1])
    output_d = Path(sys.argv[2]) if len(sys.argv) > 2 else input_p.parent / "extractions"
    extract_emphasis_file(input_p, output_d)
    print(f"[extract] Output in {output_d}")
