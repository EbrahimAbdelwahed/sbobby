"""
Fusione dei segmenti SSOT elaborati in un unico documento coerente via LLM.
"""

from pathlib import Path

from api_client import chat

PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "fusione.md"


def load_system_prompt() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8")


def merge(elaborated_paths: list[Path]) -> str:
    """Fonde i segmenti elaborati in un unico documento SSOT."""
    system_prompt = load_system_prompt()

    # Assembla i segmenti con separatori
    parts = []
    for i, path in enumerate(elaborated_paths):
        content = path.read_text(encoding="utf-8")
        parts.append(f"=== SEGMENTO {i+1} ===\n{content}")

    user_content = "\n\n".join(parts)

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content},
    ]

    print(f"[merge] Fondo {len(elaborated_paths)} segmenti...")
    # Il merge richiede output lungo — usa DeepSeek Reasoner (max 64K output),
    # con Kimi come fallback automatico in api_client.
    # Nota: deepseek-reasoner ignora temperature (sempre greedy).
    return chat(messages, provider="deepseek-reasoner", max_tokens=61440)


def merge_to_file(elaborated_paths: list[Path], output_path: Path) -> Path:
    """Fonde i segmenti e salva il risultato."""
    result = merge(elaborated_paths)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(result, encoding="utf-8")
    print(f"[merge] Sbobina finale: {output_path}")
    return output_path


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Uso: python merge.py <output.md> <elaborato_1> <elaborato_2> ...")
        sys.exit(1)

    output_p = Path(sys.argv[1])
    elab_paths = sorted(Path(p) for p in sys.argv[2:])
    merge_to_file(elab_paths, output_p)
