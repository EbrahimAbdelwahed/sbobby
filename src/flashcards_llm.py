"""
Generazione flashcard Basic (front/back) via LLM dalla sbobina studio.

Ogni sezione ## viene inviata separatamente a DeepSeek Reasoner per massimizzare
la qualità delle card generate.
"""

import json
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date
from difflib import SequenceMatcher
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from api_client import chat
from anki import send_basic_to_anki, DECK_PREFIX

PROJECT_ROOT = Path(__file__).parent.parent


def strip_summaries(section_text: str, subject: str = "") -> str:
    """Rimuove i blocchi 'Riepilogo rapido' da una sezione.

    Biochimica: **Riepilogo rapido:** + bullet list fino alla riga vuota.
    Altre materie: formato originale **Riepilogo rapido — Titolo** inline.
    """
    if subject == "biochimica":
        pattern = r"\*\*Riepilogo rapido:\*\*.*?(?:\n\s*\n|\Z)"
    else:
        pattern = r"\*\*Riepilogo rapido\s*[—–-][^*]*\*\*.*?(?:\n\s*\n|\Z)"
    return re.sub(pattern, "\n", section_text, flags=re.DOTALL).strip()


def deduplicate_cards(cards: list[dict], threshold: float = 0.80) -> list[dict]:
    """Rimuove card troppo simili usando fuzzy matching sul campo 'front'."""
    kept = []
    for card in cards:
        front = card["front"]
        if not any(SequenceMatcher(None, front, k["front"]).ratio() >= threshold for k in kept):
            kept.append(card)
    return kept


def split_sections(text: str) -> list[tuple[str, str]]:
    """Splitta il testo per sezioni ##, escludendo intro e appendice tabellare.

    Returns:
        Lista di (titolo, contenuto_completo) dove contenuto_completo include il titolo.
    """
    sections = []
    # Split per ## (heading livello 2)
    parts = re.split(r"(?=^## )", text, flags=re.MULTILINE)

    for part in parts:
        part = part.strip()
        if not part.startswith("## "):
            continue  # Salta tutto prima del primo ##

        # Estrai titolo
        first_line = part.split("\n", 1)[0]
        title = first_line.lstrip("# ").strip()

        # Escludi appendice tabellare
        if re.match(r"appendice\s+tabellare", title, re.IGNORECASE):
            break  # Tutto dopo l'appendice viene ignorato

        # Escludi sezioni informative sul corso (non generano card utili)
        if re.search(r"presentazione.*corso|informazioni.*corso|organizzazione.*corso", title, re.IGNORECASE):
            print(f"[flashcards_llm] Sezione '{title}' esclusa (info corso)")
            continue

        sections.append((title, part))

    return sections


def load_prompt(subject: str) -> str:
    """Carica il prompt flashcards per la materia specificata."""
    prompt_path = PROJECT_ROOT / "config" / subject / "prompt_flashcards.md"
    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt flashcards non trovato: {prompt_path}")
    return prompt_path.read_text(encoding="utf-8")


def parse_json_response(response: str) -> dict:
    """Estrae il JSON dalla risposta LLM, gestendo markdown code blocks.

    Returns:
        dict con campi 'anki' (list di card) e 'brain_dumps' (list di topic).
    """
    cleaned = re.sub(r"^```(?:json)?\s*\n?", "", response.strip())
    cleaned = re.sub(r"\n?```\s*$", "", cleaned)

    # Prova formato oggetto {anki: [...], brain_dumps: [...]}
    obj_start = cleaned.find("{")
    obj_end = cleaned.rfind("}")
    if obj_start != -1 and obj_end != -1:
        try:
            obj = json.loads(cleaned[obj_start:obj_end + 1])
            if isinstance(obj, dict) and "anki" in obj:
                return {
                    "anki": obj.get("anki") or [],
                    "brain_dumps": obj.get("brain_dumps") or [],
                }
        except json.JSONDecodeError:
            pass

    # Fallback: vecchio formato array (solo card Anki, nessun brain dump)
    arr_start = cleaned.find("[")
    arr_end = cleaned.rfind("]")
    if arr_start == -1 or arr_end == -1:
        raise ValueError("Nessun JSON valido trovato nella risposta LLM")

    cards = json.loads(cleaned[arr_start:arr_end + 1])
    if not isinstance(cards, list):
        raise ValueError("La risposta LLM non è un JSON array")

    return {"anki": cards, "brain_dumps": []}


def format_brain_dumps_md(brain_dumps: list[dict]) -> str:
    """Formatta i brain dump come sezione Markdown per Obsidian."""
    lines = ["## Brain Dump\n"]
    for bd in brain_dumps:
        title = bd.get("title", "Topic")
        btype = bd.get("type", "")
        context = bd.get("context", "")
        checklist = bd.get("checklist", [])

        lines.append(f"### {title}")
        meta = []
        if btype:
            meta.append(f"tipo: *{btype}*")
        if context:
            meta.append(f"contesto: *{context}*")
        if meta:
            lines.append(" · ".join(meta))
        lines.append("")
        for item in checklist:
            lines.append(item)
        lines.append("")

    return "\n".join(lines)


def append_brain_dumps_to_studio(studio_path: Path, brain_dumps: list[dict]) -> None:
    """Appende/sostituisce la sezione Brain Dump in fondo alla sbobina studio."""
    if not brain_dumps:
        return

    content = studio_path.read_text(encoding="utf-8")

    # Rimuovi sezione Brain Dump preesistente
    content = re.sub(r"\n*---\n+## Brain Dump\b.*", "", content, flags=re.DOTALL).rstrip()

    brain_dump_md = format_brain_dumps_md(brain_dumps)
    studio_path.write_text(f"{content}\n\n---\n\n{brain_dump_md}", encoding="utf-8")
    print(f"[flashcards_llm] Brain dump appeso a {studio_path.name} ({len(brain_dumps)} topic)")


def save_trial_output(output_dir: Path, subject: str, lesson: str,
                      cards: list[dict], brain_dumps: list[dict]) -> Path:
    """Salva l'output della trial run in formato JSON + Markdown leggibile.

    Returns:
        Path al file Markdown generato.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    today = date.today().isoformat()
    stem = f"{subject}_{lesson}_{today}"

    # JSON grezzo
    json_path = output_dir / f"{stem}.json"
    json_path.write_text(
        json.dumps({"anki": cards, "brain_dumps": brain_dumps}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    # Markdown leggibile
    lines = [
        f"# Trial: {subject.capitalize()} — {lesson.replace('_', ' ').title()}",
        f"*Generato il {today}*",
        f"*{len(cards)} card Anki · {len(brain_dumps)} brain dump*",
        "",
        "---",
        "",
        f"## Card Anki ({len(cards)})",
        "",
    ]
    for i, card in enumerate(cards, 1):
        ctype = card.get("type", "")
        tags = ", ".join(card.get("tags", []))
        lines += [
            f"### {i}. [{ctype}]",
            f"**Fronte:** {card['front']}",
            f"**Retro:** {card['back']}",
            f"**Tag:** {tags}",
            "",
            "---",
            "",
        ]

    lines += [f"## Brain Dump ({len(brain_dumps)})", ""]
    for bd in brain_dumps:
        title = bd.get("title", "Topic")
        btype = bd.get("type", "")
        context = bd.get("context", "")
        checklist = bd.get("checklist", [])
        lines.append(f"### {title}")
        meta = []
        if btype:
            meta.append(f"tipo: *{btype}*")
        if context:
            meta.append(f"contesto: *{context}*")
        if meta:
            lines.append(" · ".join(meta))
        lines.append("")
        lines += checklist
        lines += ["", "---", ""]

    md_path = output_dir / f"{stem}.md"
    md_path.write_text("\n".join(lines), encoding="utf-8")

    print(f"[trial] Salvato: {md_path}")
    print(f"[trial] Salvato: {json_path}")
    return md_path


def generate_flashcards(sbobina_path: Path, subject: str, lesson: str,
                        trial_tag: str = None, dry_run: bool = False,
                        output_dir: Path = None, skip_anki: bool = False) -> int:
    """Genera flashcard Basic dalla sbobina studio, una sezione alla volta via DeepSeek Reasoner.

    Args:
        sbobina_path: Path alla sbobina archivio (il path studio viene derivato).
        subject: Materia (es. "anatomia").
        lesson: Nome lezione (es. "lezione_01").
        trial_tag: Tag per discriminare la run di prova (default: "trial::YYYY-MM-DD" con data odierna).
        dry_run: Se True, non invia ad Anki né modifica la sbobina studio.
                 Salva l'output in output_dir.
        output_dir: Directory dove salvare l'output in dry_run (default: PROJECT_ROOT/trial_output).

    Returns:
        Numero di card aggiunte ad Anki (0 in dry_run).
    """
    if trial_tag is None:
        trial_tag = f"trial::{date.today().isoformat()}"

    # Deriva path sbobina studio
    studio_path = sbobina_path.parent / (sbobina_path.stem + "_studio.md")
    if not studio_path.exists():
        raise FileNotFoundError(f"Sbobina studio non trovata: {studio_path}")

    studio_text = studio_path.read_text(encoding="utf-8")
    sections = split_sections(studio_text)

    if not sections:
        print("[flashcards_llm] Nessuna sezione trovata nella sbobina studio, skip")
        return 0

    n = len(sections)
    print(f"[flashcards_llm] {n} sezioni trovate in {studio_path.name}")

    prompt_template = load_prompt(subject)
    deck_name = f"{DECK_PREFIX}::{subject.capitalize()}"

    def _process_section(idx: int, title: str, section_text: str) -> tuple[list[dict], list[dict]]:
        """Processa una sezione: chiamata LLM + parse JSON. Thread-safe.

        Returns:
            (anki_cards, brain_dumps)
        """
        cleaned = strip_summaries(section_text, subject)
        print(f"[flashcards_llm] Invio sezione {idx}/{n}: \"{title}\"...")

        full_prompt = prompt_template + "\n\n" + cleaned
        messages = [{"role": "user", "content": full_prompt}]
        response = chat(messages, provider="deepseek-reasoner", max_tokens=16384)

        try:
            parsed = parse_json_response(response)
        except (json.JSONDecodeError, ValueError) as e:
            print(f"[flashcards_llm]   Sezione {idx} errore JSON: {e}, retry...")
            messages.append({"role": "assistant", "content": response})
            messages.append({"role": "user", "content": "La risposta precedente non è un JSON valido. Rispondi SOLO con l'oggetto JSON {\"anki\": [...], \"brain_dumps\": [...]}, senza testo aggiuntivo."})
            response = chat(messages, provider="deepseek-reasoner", max_tokens=16384)
            try:
                parsed = parse_json_response(response)
            except (json.JSONDecodeError, ValueError) as e2:
                print(f"[flashcards_llm]   Sezione {idx} retry fallito: {e2}, skip")
                return [], []

        valid_cards = []
        for card in parsed["anki"]:
            if not isinstance(card, dict) or "front" not in card or "back" not in card:
                continue
            tags = card.get("tags", [])
            if isinstance(tags, str):
                tags = [tags]
            tags.append(f"{subject}::{lesson}")
            tags.append(trial_tag)
            valid_cards.append({"front": card["front"], "back": card["back"], "tags": tags})

        brain_dumps = [bd for bd in parsed["brain_dumps"] if isinstance(bd, dict)]

        print(f"[flashcards_llm]   Sezione {idx}/{n}: \"{title}\" → {len(valid_cards)} card, {len(brain_dumps)} brain dump")
        return valid_cards, brain_dumps

    # Lancio parallelo: 6 sezioni alla volta
    all_results: list[tuple[int, list[dict], list[dict]]] = []
    with ThreadPoolExecutor(max_workers=6) as pool:
        futures = {
            pool.submit(_process_section, i, title, text): i
            for i, (title, text) in enumerate(sections, 1)
        }
        for future in as_completed(futures):
            idx = futures[future]
            try:
                cards, dumps = future.result()
                all_results.append((idx, cards, dumps))
            except Exception as exc:
                print(f"[flashcards_llm]   Sezione {idx} eccezione: {exc}")

    # Appiattisci in ordine
    all_results.sort(key=lambda x: x[0])
    flat = [card for _, cards, _ in all_results for card in cards]
    all_brain_dumps = [bd for _, _, dumps in all_results for bd in dumps]

    # Deduplica card e invia ad Anki
    before = len(flat)
    flat = deduplicate_cards(flat)
    removed = before - len(flat)
    if removed:
        print(f"[flashcards_llm] Deduplicazione: {removed} card rimosse ({before} → {len(flat)})")

    if dry_run:
        out_dir = output_dir or PROJECT_ROOT / "trial_output"
        save_trial_output(out_dir, subject, lesson, flat, all_brain_dumps)
        print(f"[flashcards_llm] dry_run: {len(flat)} card salvate, nessuna inviata ad Anki")
        return 0

    if skip_anki:
        print(f"[flashcards_llm] skip_anki=True: {len(flat)} card generate ma non inviate ad Anki")
        total_added = 0
    else:
        total_added = send_basic_to_anki(flat, deck_name) if flat else 0
        print(f"[flashcards_llm] Totale: {total_added} card aggiunte ad Anki")

    # Appendi brain dump alla sbobina studio
    if all_brain_dumps:
        append_brain_dumps_to_studio(studio_path, all_brain_dumps)

    return total_added


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Uso: python flashcards_llm.py <sbobina.md> <materia> <lezione>")
        print("  Esempio: python flashcards_llm.py sbobine/anatomia/lezione_01.md anatomia lezione_01")
        sys.exit(1)

    sbobina_p = Path(sys.argv[1])
    subj = sys.argv[2]
    les = sys.argv[3]
    generate_flashcards(sbobina_p, subj, les)
