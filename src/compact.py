"""
Secondo passaggio LLM: sbobina archivio → documento di studio compatto.

La sbobina completa viene passata al modello che produce un documento
condensato mantenendo tutti i concetti, eliminando solo ridondanza e filler.
"""

from pathlib import Path

from api_client import chat

PROJECT_ROOT = Path(__file__).parent.parent


def load_compact_prompt(subject: str) -> str:
    """Carica il prompt di compattazione per la materia."""
    prompt_path = PROJECT_ROOT / "config" / subject / "prompt_compact.md"
    if not prompt_path.exists():
        raise FileNotFoundError(
            f"Prompt compatto non trovato: {prompt_path}\n"
            f"Crea config/{subject}/prompt_compact.md prima di eseguire questo step."
        )
    return prompt_path.read_text(encoding="utf-8")


def compact(sbobina_text: str, subject: str) -> str:
    """Genera il documento di studio compatto dalla sbobina archivio."""
    system_prompt = load_compact_prompt(subject)

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": sbobina_text},
    ]

    print(f"[compact] Generazione documento compatto ({subject})...")
    # Output lungo — usa DeepSeek Reasoner (max 64K), Kimi come fallback
    return chat(messages, provider="deepseek-reasoner", max_tokens=61440)


def compact_to_file(sbobina_path: Path, output_path: Path, subject: str) -> Path:
    """Legge la sbobina archivio e salva il documento compatto."""
    sbobina_text = sbobina_path.read_text(encoding="utf-8")
    result = compact(sbobina_text, subject)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(result, encoding="utf-8")
    print(f"[compact] Documento compatto: {output_path}")
    return output_path


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 4:
        print("Uso: python compact.py <subject> <sbobina.md> <output.md>")
        sys.exit(1)

    subj = sys.argv[1]
    sbobina_p = Path(sys.argv[2])
    output_p = Path(sys.argv[3])
    compact_to_file(sbobina_p, output_p, subj)
