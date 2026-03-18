"""
Orchestratore della pipeline: audio → sbobina SSOT.

Uso:
    # Pipeline completa
    python pipeline.py run anatomia lezione_01 audio/anatomia/lezione_01.m4a

    # Step singoli
    python pipeline.py transcribe anatomia lezione_01 audio/anatomia/lezione_01.m4a
    python pipeline.py correct anatomia lezione_01
    python pipeline.py segment anatomia lezione_01
    python pipeline.py elaborate anatomia lezione_01
    python pipeline.py merge anatomia lezione_01
    python pipeline.py render_chem biochimica lezione_01
    python pipeline.py insert_images anatomia lezione_01
    python pipeline.py compact anatomia lezione_01
    python pipeline.py sync_vault anatomia lezione_01
    python pipeline.py flashcards anatomia lezione_01
"""

import shutil
import sys
from pathlib import Path

# Aggiungi src al path per gli import
sys.path.insert(0, str(Path(__file__).parent))

from transcribe import transcribe, extract_text_from_vtt
from correct import correct_file
from segment import segment_file
from elaborate import elaborate_segments
from merge import merge_to_file
from chem_renderer import process_file as render_chem
from insert_images import process_sbobina as insert_slide_images
from compact import compact_to_file
from anki import is_anki_available, sync_anki
from flashcards_llm import generate_flashcards
from sr_engine import (
    load_state, save_state, detect_new_items,
    generate_review_section, items_overdue, items_due, items_tomorrow,
    score_item, next_interval,
)
from sr_engine import _format_date_it, _due_date

PROJECT_ROOT = Path(__file__).parent.parent


def get_paths(subject: str, lesson: str) -> dict:
    """Restituisce tutti i path rilevanti per una lezione."""
    ws = PROJECT_ROOT / "workspace" / subject / lesson
    return {
        "workspace": ws,
        "segments_dir": ws / "segmenti",
        "elaborated_dir": ws / "elaborati",
        "vtt": ws / f"{lesson}.vtt",
        "txt": ws / f"{lesson}.txt",
        "corrected": ws / f"{lesson}_corretta.txt",
        "corrections_file": PROJECT_ROOT / "config" / subject / "correzioni.txt",
        "sbobina": PROJECT_ROOT / "sbobine" / subject / f"{lesson}.md",
        "compact": PROJECT_ROOT / "sbobine" / subject / f"{lesson}_studio.md",
        "initial_prompts_dir": PROJECT_ROOT / "config" / subject / "initial_prompts",
    }


def step_transcribe(subject: str, lesson: str, audio_path: str, backend: str = "groq") -> None:
    paths = get_paths(subject, lesson)
    audio_p = Path(audio_path)
    if not audio_p.is_absolute():
        audio_p = PROJECT_ROOT / audio_p

    # Cerca initial prompt per argomento (opzionale)
    initial_prompt = None
    prompt_file = paths["initial_prompts_dir"] / f"{lesson}.txt"
    if prompt_file.exists():
        initial_prompt = prompt_file.read_text(encoding="utf-8").strip()
        print(f"[pipeline] Initial prompt caricato da {prompt_file.name}")

    transcribe(audio_p, paths["workspace"], initial_prompt=initial_prompt, backend=backend)

    # Rinomina output se il nome del file audio non corrisponde al lesson name
    # (es. "lezione 1.m4a" → file "lezione 1.txt", ma serve "lezione_01.txt")
    for ext in (".vtt", ".txt"):
        actual = paths["workspace"] / (audio_p.stem + ext)
        expected = paths["workspace"] / (lesson + ext)
        if actual.exists() and actual != expected:
            actual.rename(expected)
            print(f"[pipeline] Rinominato {actual.name} → {expected.name}")


def step_correct(subject: str, lesson: str) -> None:
    paths = get_paths(subject, lesson)

    # Usa il TXT se esiste, altrimenti estrai dal VTT
    txt_path = paths["txt"]
    if not txt_path.exists():
        vtt_path = paths["vtt"]
        if not vtt_path.exists():
            raise FileNotFoundError(f"Nessuna trascrizione trovata in {paths['workspace']}")
        text = extract_text_from_vtt(vtt_path)
        txt_path.write_text(text, encoding="utf-8")

    correct_file(txt_path, paths["corrections_file"], paths["corrected"])


def step_segment(subject: str, lesson: str) -> None:
    paths = get_paths(subject, lesson)
    corrected = paths["corrected"]
    if not corrected.exists():
        raise FileNotFoundError(f"File corretto non trovato: {corrected}")

    segment_file(corrected, paths["segments_dir"])


def step_elaborate(subject: str, lesson: str) -> None:
    paths = get_paths(subject, lesson)
    seg_dir = paths["segments_dir"]
    if not seg_dir.exists():
        raise FileNotFoundError(f"Directory segmenti non trovata: {seg_dir}")

    seg_paths = sorted(seg_dir.glob("segmento_*.txt"))
    if not seg_paths:
        raise FileNotFoundError(f"Nessun segmento trovato in {seg_dir}")

    elaborate_segments(seg_paths, subject, paths["elaborated_dir"])


def step_merge(subject: str, lesson: str) -> None:
    paths = get_paths(subject, lesson)
    elab_dir = paths["elaborated_dir"]
    if not elab_dir.exists():
        raise FileNotFoundError(f"Directory elaborati non trovata: {elab_dir}")

    elab_paths = sorted(elab_dir.glob("elaborato_*.md"))
    if not elab_paths:
        raise FileNotFoundError(f"Nessun elaborato trovato in {elab_dir}")

    merge_to_file(elab_paths, paths["sbobina"])


def step_render_chem(subject: str, lesson: str) -> None:
    paths = get_paths(subject, lesson)
    sbobina = paths["sbobina"]
    if not sbobina.exists():
        raise FileNotFoundError(f"Sbobina non trovata: {sbobina}")

    text = sbobina.read_text(encoding="utf-8")
    if "[CHEM:" not in text and "[REACTION:" not in text:
        print("[pipeline] Nessun marker chimico trovato, skip render_chem")
        return

    structures_dir = paths["workspace"] / "structures"
    render_chem(sbobina, sbobina, structures_dir)


def step_insert_images(subject: str, lesson: str) -> None:
    paths = get_paths(subject, lesson)
    sbobina = paths["sbobina"]
    if not sbobina.exists():
        raise FileNotFoundError(f"Sbobina non trovata: {sbobina}")

    insert_slide_images(subject, lesson)


VAULT_PATH = Path.home() / "Library/Mobile Documents/iCloud~md~obsidian/Documents/Cerebrum extra"


def step_sync_vault(subject: str, lesson: str) -> None:
    """Copia sbobina, compatto e strutture nel vault Obsidian (iCloud)."""
    vault_sbobine = VAULT_PATH / "Sbobine"
    if not VAULT_PATH.exists():
        print("[pipeline] Vault Obsidian non trovato, skip sync")
        return

    cap = subject.capitalize()
    paths = get_paths(subject, lesson)
    copied = 0

    # Copia sbobina archivio
    if paths["sbobina"].exists():
        dest = vault_sbobine / cap / "Archivio"
        dest.mkdir(parents=True, exist_ok=True)
        shutil.copy2(paths["sbobina"], dest / paths["sbobina"].name)
        copied += 1

    # Copia documento studio
    if paths["compact"].exists():
        dest = vault_sbobine / cap / "Studio"
        dest.mkdir(parents=True, exist_ok=True)
        shutil.copy2(paths["compact"], dest / paths["compact"].name)
        copied += 1

    # Copia strutture chimiche
    structures_dir = paths["workspace"] / "structures"
    if structures_dir.exists():
        dest = vault_sbobine / "Strutture"
        dest.mkdir(parents=True, exist_ok=True)
        for img in structures_dir.iterdir():
            if img.suffix in (".svg", ".png"):
                shutil.copy2(img, dest / img.name)
                copied += 1

    # Copia immagini diapositive (nuovo formato: assets/lezione_XX/)
    assets_base = PROJECT_ROOT / "sbobine" / subject / "assets"
    if assets_base.exists():
        for lesson_assets in assets_base.iterdir():
            if lesson_assets.is_dir():
                dest = vault_sbobine / cap / "Archivio" / "assets" / lesson_assets.name
                dest.mkdir(parents=True, exist_ok=True)
                for img in lesson_assets.iterdir():
                    if img.suffix in (".png", ".jpg", ".jpeg", ".gif", ".webp"):
                        shutil.copy2(img, dest / img.name)
                        copied += 1

    # Copia file aggregato brain dump (se esiste)
    brain_dump_file = PROJECT_ROOT / "sbobine" / subject / f"brain_dump_{subject}.md"
    if brain_dump_file.exists():
        dest_bd = vault_sbobine / cap
        dest_bd.mkdir(parents=True, exist_ok=True)
        shutil.copy2(brain_dump_file, dest_bd / brain_dump_file.name)
        copied += 1

    print(f"[pipeline] Vault sync: {copied} file copiati in Sbobine/{cap}/")


def step_compact(subject: str, lesson: str) -> None:
    paths = get_paths(subject, lesson)
    sbobina = paths["sbobina"]
    if not sbobina.exists():
        raise FileNotFoundError(f"Sbobina non trovata: {sbobina}")

    compact_to_file(sbobina, paths["compact"], subject)


def aggregate_brain_dumps_file(subject: str) -> None:
    """Raccoglie tutti i brain dump dalle sbobine studio e crea un file aggregato per materia.

    Raggruppa per docente: lezione_01.md → sezione canonica, lezione_01_canzi.md → sezione Canzi.
    Qualsiasi suffisso _parola (solo lettere) dopo il numero di lezione viene trattato come docente.
    """
    import re as _re
    sbobine_dir = PROJECT_ROOT / "sbobine" / subject
    if not sbobine_dir.exists():
        print(f"[pipeline] Directory sbobine non trovata: {sbobine_dir}, skip aggregazione")
        return

    studio_files = sorted(sbobine_dir.glob("*_studio.md"))
    if not studio_files:
        print(f"[pipeline] Nessun file studio trovato per {subject}")
        return

    def _parse_lecturer(lesson: str):
        """Restituisce (base_lesson, lecturer|None).
        Es: 'lezione_canzi_01' → ('lezione_01', 'canzi'), 'lezione_01' → ('lezione_01', None)."""
        m = _re.match(r'^lezione_([a-zA-Z]+)_(\d+)$', lesson)
        if m:
            return f"lezione_{m.group(2)}", m.group(1)
        return lesson, None

    # Raccogli: {lecturer | None: [(lesson_title, body), ...]}
    groups: dict = {}
    for studio_path in studio_files:
        lesson = studio_path.stem.replace("_studio", "")
        _, lecturer = _parse_lecturer(lesson)

        content = studio_path.read_text(encoding="utf-8")
        match = _re.search(r"\n*---\n+## Brain Dump\b\n*(.*)", content, _re.DOTALL)
        if not match:
            continue
        body = match.group(1).strip()
        if not body:
            continue

        lesson_title = lesson.replace("_", " ").title()
        if lecturer not in groups:
            groups[lecturer] = []
        groups[lecturer].append((lesson_title, body))

    if not groups:
        print(f"[pipeline] Nessun brain dump trovato per {subject}, file aggregato non creato")
        return

    cap = subject.capitalize()
    lines = [
        f"# Brain Dump — {cap}",
        "",
        "*File aggregato — aggiornato automaticamente*",
        "",
    ]

    # Inserisci sezione ripasso SR (se esiste state)
    review_section = generate_review_section(subject)
    if review_section:
        lines += [review_section, ""]

    # Canonical (None) prima, poi docenti in ordine alfabetico
    ordered = ([None] if None in groups else []) + sorted(k for k in groups if k is not None)

    found = 0
    for lecturer in ordered:
        entries = groups[lecturer]
        section_title = cap if lecturer is None else lecturer.capitalize()
        lines += ["---", "", f"## {section_title}", ""]
        for lesson_title, body in entries:
            lines += [f"### {lesson_title}", "", body, ""]
            found += 1

    out_path = sbobine_dir / f"brain_dump_{subject}.md"
    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"[pipeline] Brain dump aggregato: {out_path} ({found} lezioni, {len(groups)} sezioni)")


def step_aggregate_brain_dumps(subject: str) -> None:
    aggregate_brain_dumps_file(subject)


def step_flashcards(subject: str, lesson: str) -> None:
    """Genera flashcard Anki Basic via LLM (sezione per sezione dalla sbobina studio)."""
    paths = get_paths(subject, lesson)
    sbobina = paths["sbobina"]
    if not sbobina.exists():
        raise FileNotFoundError(f"Sbobina non trovata: {sbobina}")

    anki_ok = is_anki_available()
    if not anki_ok:
        print("[pipeline] AnkiConnect non raggiungibile — genera solo brain dump, skip card Anki")

    print("[pipeline] Generazione card basic via LLM (sezione per sezione)...")
    generate_flashcards(sbobina, subject, lesson, skip_anki=not anki_ok)

    if anki_ok:
        sync_anki()

    # Rigenera file aggregato brain dump per la materia
    aggregate_brain_dumps_file(subject)


def _sync_brain_dump_to_vault(subject: str) -> None:
    """Copia solo il brain_dump file nel vault Obsidian."""
    if not VAULT_PATH.exists():
        print("[pipeline] Vault Obsidian non trovato, skip sync brain dump")
        return
    cap = subject.capitalize()
    brain_dump_file = PROJECT_ROOT / "sbobine" / subject / f"brain_dump_{subject}.md"
    if brain_dump_file.exists():
        dest = VAULT_PATH / "Sbobine" / cap
        dest.mkdir(parents=True, exist_ok=True)
        shutil.copy2(brain_dump_file, dest / brain_dump_file.name)
        print(f"[pipeline] Brain dump sincronizzato nel vault: Sbobine/{cap}/{brain_dump_file.name}")


def step_sr_detect(subject: str) -> None:
    """Rileva nuovi item spuntati nel brain dump del vault e aggiorna SR state."""
    from datetime import date as _date

    cap = subject.capitalize()
    vault_bd = VAULT_PATH / "Sbobine" / cap / f"brain_dump_{subject}.md"

    if not vault_bd.exists():
        # Fallback: leggi dal progetto locale
        vault_bd = PROJECT_ROOT / "sbobine" / subject / f"brain_dump_{subject}.md"
        if not vault_bd.exists():
            print(f"[sr] Brain dump non trovato per {subject}")
            return

    state = load_state(subject)
    state = detect_new_items(state, vault_bd)
    save_state(state, subject)

    # Rigenera brain dump con review section aggiornata
    aggregate_brain_dumps_file(subject)
    _sync_brain_dump_to_vault(subject)


def step_sr_review(subject: str) -> None:
    """Loop interattivo di ripasso: mostra item dovuti, chiede score 0/1/2."""
    from datetime import date as _date

    state = load_state(subject)
    today = _date.today()

    overdue = items_overdue(state, today)
    due = items_due(state, today)
    review_items = overdue + due

    if not review_items:
        tomorrow_items = items_tomorrow(state, today)
        print(f"\n=== Ripasso — {subject.capitalize()} ({_format_date_it(today)}) ===")
        print("Nessun item in scadenza oggi!")
        if tomorrow_items:
            print(f"  Domani: {len(tomorrow_items)} item")
        return

    print(f"\n{'='*50}")
    print(f"  Ripasso — {subject.capitalize()} ({_format_date_it(today)})")
    print(f"  {len(review_items)} item ({len(overdue)} arretrati + {len(due)} oggi)")
    print(f"{'='*50}\n")

    stats = {"advanced": 0, "repeated": 0, "reset": 0}

    try:
        for i, (item_id, item) in enumerate(review_items, 1):
            print(f"[{i}/{len(review_items)}] {item['text']}")
            ctx_parts = []
            if item.get("section"):
                ctx_parts.append(item["section"])
            if item.get("lesson"):
                ctx_parts.append(item["lesson"])
            ctx_parts.append(f"Intervallo: {item['interval_days']}g")
            ctx_parts.append(f"Ripetizioni: {item.get('review_count', 0)}")
            print(f"       {' · '.join(ctx_parts)}")

            while True:
                try:
                    raw = input("       Punteggio (0/1/2): ")
                except EOFError:
                    print("\n[sr] Input terminato, esco senza salvare.")
                    return
                raw = raw.strip()
                if raw in ("0", "1", "2"):
                    s = int(raw)
                    break
                print("       Inserisci 0, 1 o 2")

            new_iv = next_interval(item["interval_days"], s)
            next_date = today + __import__("datetime").timedelta(days=new_iv)
            state = score_item(state, item_id, s, today)

            label = {0: "Reset → 1g", 1: "Ripeti", 2: "Avanza"}[s]
            if s == 2:
                stats["advanced"] += 1
            elif s == 1:
                stats["repeated"] += 1
            else:
                stats["reset"] += 1

            print(f"       > {label} → {new_iv}g · Prossima: {_format_date_it(next_date)}\n")

    except KeyboardInterrupt:
        print("\n\n[sr] Interrotto — stato NON salvato.")
        return

    # Salva e rigenera
    state["last_review"] = __import__("datetime").datetime.now().isoformat(timespec="seconds")
    save_state(state, subject)

    print(f"{'='*50}")
    print(f"  Riepilogo")
    print(f"  Avanzati: {stats['advanced']} · Ripetuti: {stats['repeated']} · Reset: {stats['reset']}")
    tomorrow_items = items_tomorrow(state, today)
    if tomorrow_items:
        print(f"  Prossimo ripasso: domani ({len(tomorrow_items)} item)")
    print(f"{'='*50}\n")

    # Rigenera brain dump e sync
    aggregate_brain_dumps_file(subject)
    _sync_brain_dump_to_vault(subject)


def run_full(subject: str, lesson: str, audio_path: str, backend: str = "groq", no_flashcards: bool = False) -> None:
    """Esegue la pipeline completa."""
    print(f"\n{'='*60}")
    print(f"  Pipeline: {subject} / {lesson}")
    print(f"{'='*60}\n")

    # Pulisci workspace per ripartire da zero
    paths = get_paths(subject, lesson)
    ws = paths["workspace"]
    if ws.exists():
        print(f"[pipeline] Pulizia workspace {ws}...")
        shutil.rmtree(ws)
    ws.mkdir(parents=True, exist_ok=True)

    print("--- STEP 1: Trascrizione ---")
    step_transcribe(subject, lesson, audio_path, backend=backend)

    print("\n--- STEP 2: Correzione ---")
    step_correct(subject, lesson)

    print("\n--- STEP 3: Segmentazione ---")
    step_segment(subject, lesson)

    print("\n--- STEP 4: Elaborazione SSOT ---")
    step_elaborate(subject, lesson)

    print("\n--- STEP 5: Fusione ---")
    step_merge(subject, lesson)

    print("\n--- STEP 6: Strutture chimiche ---")
    step_render_chem(subject, lesson)

    print("\n--- STEP 7: Inserimento immagini diapositive ---")
    step_insert_images(subject, lesson)

    print("\n--- STEP 8: Documento di studio compatto ---")
    step_compact(subject, lesson)

    print("\n--- STEP 9: Sync vault Obsidian ---")
    step_sync_vault(subject, lesson)

    if not no_flashcards:
        print("\n--- STEP 10: Flashcard Anki + Brain Dump ---")
        step_flashcards(subject, lesson)

    paths = get_paths(subject, lesson)
    print(f"\n{'='*60}")
    print(f"  Sbobina archivio: {paths['sbobina']}")
    print(f"  Documento studio: {paths['compact']}")
    print(f"{'='*60}\n")


def _parse_flags(args: list[str]) -> tuple[list[str], str, bool]:
    """Estrae --local/--groq e --no-flashcards dagli args. Default backend: groq."""
    backend = "local" if "--local" in args else "groq"
    no_flashcards = "--no-flashcards" in args
    args = [a for a in args if a not in ("--groq", "--local", "--no-flashcards")]
    return args, backend, no_flashcards


STEPS = {
    "transcribe": lambda args, b, nf: step_transcribe(args[0], args[1], args[2], backend=b),
    "correct": lambda args, b, nf: step_correct(args[0], args[1]),
    "segment": lambda args, b, nf: step_segment(args[0], args[1]),
    "elaborate": lambda args, b, nf: step_elaborate(args[0], args[1]),
    "merge": lambda args, b, nf: step_merge(args[0], args[1]),
    "render_chem": lambda args, b, nf: step_render_chem(args[0], args[1]),
    "insert_images": lambda args, b, nf: step_insert_images(args[0], args[1]),
    "compact": lambda args, b, nf: step_compact(args[0], args[1]),
    "sync_vault": lambda args, b, nf: step_sync_vault(args[0], args[1]),
    "flashcards": lambda args, b, nf: step_flashcards(args[0], args[1]),
    "aggregate_brain_dumps": lambda args, b, nf: step_aggregate_brain_dumps(args[0]),
    "sr_detect": lambda args, b, nf: step_sr_detect(args[0]),
    "sr_review": lambda args, b, nf: step_sr_review(args[0]),
    "run": lambda args, b, nf: run_full(args[0], args[1], args[2], backend=b, no_flashcards=nf),
}

# Comandi che richiedono solo subject (non subject + lesson)
_SUBJECT_ONLY_CMDS = {"aggregate_brain_dumps", "sr_detect", "sr_review"}


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1]
    args = sys.argv[2:]
    args, backend, no_flashcards = _parse_flags(args)

    if command not in STEPS:
        print(f"Comando sconosciuto: {command}")
        print(f"Comandi disponibili: {', '.join(STEPS.keys())}")
        sys.exit(1)

    # Comandi subject-only richiedono almeno 1 arg, gli altri almeno 2
    min_args = 1 if command in _SUBJECT_ONLY_CMDS else 2
    if len(args) < min_args:
        print(f"Uso: python pipeline.py {command} <subject>" +
              ("" if command in _SUBJECT_ONLY_CMDS else " <lesson> [audio_path]"))
        sys.exit(1)

    STEPS[command](args, backend, no_flashcards)


if __name__ == "__main__":
    main()
