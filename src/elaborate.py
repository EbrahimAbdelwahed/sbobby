"""
Elaborazione SSOT: trasforma ogni segmento in sbobina strutturata via LLM.
"""

from pathlib import Path

from api_client import chat

PROJECT_ROOT = Path(__file__).parent.parent
DEFAULT_SAMPLE_SSOT_PATH = PROJECT_ROOT / "SAMPLE_SSOT.md"


def load_ssot_prompt(subject: str) -> str:
    """Carica il prompt SSOT per la materia, inserendo il sample."""
    prompt_path = PROJECT_ROOT / "config" / subject / "prompt_ssot.md"
    prompt = prompt_path.read_text(encoding="utf-8")

    # Sample specifico per materia, fallback al default
    subject_sample = PROJECT_ROOT / "config" / subject / "SAMPLE_SSOT.md"
    sample_path = subject_sample if subject_sample.exists() else DEFAULT_SAMPLE_SSOT_PATH
    sample = sample_path.read_text(encoding="utf-8")
    prompt = prompt.replace("{{SAMPLE_SSOT}}", sample)

    return prompt


def elaborate(segment_text: str, subject: str) -> str:
    """Elabora un singolo segmento in formato SSOT."""
    system_prompt = load_ssot_prompt(subject)
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": segment_text},
    ]

    return chat(messages, temperature=0.3)


def elaborate_segments(segment_paths: list[Path], subject: str, output_dir: Path) -> list[Path]:
    """Elabora una lista di segmenti e salva i risultati."""
    output_dir.mkdir(parents=True, exist_ok=True)

    # Pulisci vecchi elaborati per evitare residui di run precedenti
    for old in output_dir.glob("elaborato_*.md"):
        old.unlink()
    results = []

    for i, seg_path in enumerate(segment_paths):
        print(f"[elaborate] Elaboro segmento {i+1}/{len(segment_paths)}: {seg_path.name}")
        segment_text = seg_path.read_text(encoding="utf-8")
        elaborated = elaborate(segment_text, subject)

        out_path = output_dir / f"elaborato_{i+1:02d}.md"
        out_path.write_text(elaborated, encoding="utf-8")
        results.append(out_path)

    return results


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Uso: python elaborate.py <materia> <segmento_1> [segmento_2] ...")
        print("  Esempio: python elaborate.py anatomia workspace/anatomia/lezione_01/segmenti/*.txt")
        sys.exit(1)

    subject = sys.argv[1]
    seg_paths = [Path(p) for p in sys.argv[2:]]
    output_d = seg_paths[0].parent.parent / "elaborati"
    elaborate_segments(seg_paths, subject, output_d)
    print(f"[elaborate] Output in {output_d}")
