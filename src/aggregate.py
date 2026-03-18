"""
Aggregazione estrazioni multi-anno in dossier esaminatore.

Uso:
    python aggregate.py <extractions_dir> <output_dir> [initial_prompts_dir]
"""

import json
from pathlib import Path
from collections import defaultdict

from api_client import chat

PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "aggregazione_dossier.md"


def load_system_prompt() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8")


def load_extractions(extractions_dir: Path) -> list[dict]:
    """Carica tutte le estrazioni JSON da una directory."""
    files = sorted(extractions_dir.glob("*.json"))
    extractions = []
    for f in files:
        data = json.loads(f.read_text(encoding="utf-8"))
        data["_source"] = f.name
        extractions.append(data)
    return extractions


def group_by_topic(extractions: list[dict]) -> dict[str, list[dict]]:
    """Raggruppa le estrazioni per argomento.

    Usa matching esatto sugli argomenti_trattati.
    Per argomenti simili ma non identici, li tiene separati
    (l'aggregazione LLM li fonderà se necessario).
    """
    topic_data = defaultdict(list)

    for ext in extractions:
        topics = ext.get("argomenti_trattati", [])
        if not topics:
            # Se nessun argomento, metti in "Generale"
            topic_data["Generale"].append(ext)
            continue

        for topic in topics:
            topic_data[topic].append(ext)

    return dict(topic_data)


def aggregate_topic(topic: str, extractions: list[dict]) -> str:
    """Aggrega le estrazioni di un singolo argomento via LLM."""
    system_prompt = load_system_prompt()

    # Prepara il contenuto: tutte le estrazioni per questo argomento
    parts = []
    for i, ext in enumerate(extractions):
        source = ext.get("_source", f"estrazione_{i+1}")
        # Rimuovi _source prima di serializzare
        clean = {k: v for k, v in ext.items() if k != "_source"}
        parts.append(f"=== Fonte: {source} ===\n{json.dumps(clean, ensure_ascii=False, indent=2)}")

    user_content = (
        f"Argomento: {topic}\n"
        f"Numero estrazioni: {len(extractions)}\n\n"
        + "\n\n".join(parts)
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content},
    ]

    return chat(messages, temperature=0.2)


def build_dossier(extractions_dir: Path, output_dir: Path) -> list[Path]:
    """Pipeline completa: carica estrazioni, raggruppa, aggrega."""
    output_dir.mkdir(parents=True, exist_ok=True)

    extractions = load_extractions(extractions_dir)
    if not extractions:
        print(f"[aggregate] Nessuna estrazione trovata in {extractions_dir}")
        return []

    print(f"[aggregate] Caricate {len(extractions)} estrazioni")

    grouped = group_by_topic(extractions)
    print(f"[aggregate] {len(grouped)} argomenti trovati")

    results = []
    for i, (topic, exts) in enumerate(sorted(grouped.items())):
        # Crea nome file safe
        safe_name = topic.lower().replace(" ", "_").replace("/", "_")
        safe_name = "".join(c for c in safe_name if c.isalnum() or c == "_")[:60]

        print(f"[aggregate] [{i+1}/{len(grouped)}] {topic} ({len(exts)} estrazioni)...")

        try:
            dossier = aggregate_topic(topic, exts)
            out_path = output_dir / f"{safe_name}.md"
            out_path.write_text(dossier, encoding="utf-8")
            results.append(out_path)
        except Exception as e:
            print(f"  ✗ Errore: {e}")

    return results


def generate_initial_prompts(dossier_dir: Path, output_dir: Path) -> list[Path]:
    """Estrae la sezione 'Initial Prompt Whisper' da ogni dossier e salva come .txt."""
    output_dir.mkdir(parents=True, exist_ok=True)
    results = []

    for dossier_path in sorted(dossier_dir.glob("*.md")):
        text = dossier_path.read_text(encoding="utf-8")

        # Cerca la sezione Initial Prompt Whisper
        marker = "## Initial Prompt Whisper"
        idx = text.find(marker)
        if idx == -1:
            continue

        # Estrai il contenuto fino alla prossima sezione ## o fine file
        content = text[idx + len(marker):]
        next_section = content.find("\n## ")
        if next_section != -1:
            content = content[:next_section]

        content = content.strip()
        if not content:
            continue

        out_path = output_dir / (dossier_path.stem + ".txt")
        out_path.write_text(content, encoding="utf-8")
        results.append(out_path)
        print(f"[aggregate] Initial prompt: {out_path.name}")

    return results


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Uso: python aggregate.py <extractions_dir> <output_dir> [initial_prompts_dir]")
        sys.exit(1)

    extr_dir = Path(sys.argv[1])
    out_dir = Path(sys.argv[2])

    dossier_paths = build_dossier(extr_dir, out_dir)
    print(f"[aggregate] {len(dossier_paths)} dossier generati in {out_dir}")

    if len(sys.argv) > 3:
        prompts_dir = Path(sys.argv[3])
        prompt_paths = generate_initial_prompts(out_dir, prompts_dir)
        print(f"[aggregate] {len(prompt_paths)} initial prompts generati")
