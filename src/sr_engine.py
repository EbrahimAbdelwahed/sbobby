"""
Spaced Repetition engine per Brain Dump.

Ogni checkbox nel brain dump è un'unità SR indipendente.
Quando l'utente spunta un checkbox in Obsidian, l'item entra nel ciclo di ripetizione.

Intervalli: 1 → 3 → 7 → 14 → 28 → 60 giorni
Score 2 → avanza, Score 1 → ripeti stesso intervallo, Score 0 → reset a 1g
"""

import hashlib
import json
import re
from datetime import date, datetime, timedelta
from difflib import SequenceMatcher
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent

INTERVALS = [1, 3, 7, 14, 28, 60]


# ── State I/O ──────────────────────────────────────────────────────────────

def _state_path(subject: str) -> Path:
    return PROJECT_ROOT / "config" / subject / "sr_state.json"


def load_state(subject: str) -> dict:
    p = _state_path(subject)
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return {
        "version": 1,
        "subject": subject,
        "last_detect": None,
        "last_review": None,
        "items": {},
        "known_unchecked": [],
    }


def save_state(state: dict, subject: str) -> None:
    p = _state_path(subject)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")


# ── Parsing ────────────────────────────────────────────────────────────────

def parse_brain_dump(text: str) -> list[dict]:
    """Estrae ogni checkbox con contesto (section, lesson, topic, text, checked)."""
    items = []
    current_section = None   # ## heading
    current_lesson = None    # ### Lezione NN
    current_topic = None     # ### other heading (non-lesson)

    for line in text.splitlines():
        line_stripped = line.strip()

        # ## Section
        if line_stripped.startswith("## ") and not line_stripped.startswith("## Ripasso del giorno"):
            current_section = line_stripped[3:].strip()
            current_lesson = None
            current_topic = None
            continue

        # ### heading — lesson marker or topic
        if line_stripped.startswith("### "):
            heading = line_stripped[4:].strip()
            if re.match(r"^Lezione\s+\d+", heading, re.IGNORECASE):
                current_lesson = heading
                current_topic = None
            else:
                current_topic = heading
            continue

        # Checkbox
        m = re.match(r"^- \[([ xX])\] (.+)$", line_stripped)
        if m:
            checked = m.group(1).lower() == "x"
            text_val = m.group(2).strip()
            items.append({
                "section": current_section,
                "lesson": current_lesson,
                "topic": current_topic,
                "text": text_val,
                "checked": checked,
            })

    return items


# ── Identity ───────────────────────────────────────────────────────────────

def _normalize(text: str) -> str:
    """Normalizza testo per hashing: lowercase, collapse whitespace."""
    return re.sub(r"\s+", " ", text.lower().strip())


def compute_item_id(section: str | None, topic: str | None, text: str) -> str:
    raw = f"{section or ''}|{topic or ''}|{_normalize(text)}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


# ── Detection ──────────────────────────────────────────────────────────────

def _fuzzy_match(text_a: str, text_b: str, threshold: float = 0.85) -> bool:
    return SequenceMatcher(None, _normalize(text_a), _normalize(text_b)).ratio() >= threshold


def detect_new_items(state: dict, vault_brain_dump_path: Path) -> dict:
    """Legge brain dump dal vault, confronta con state.

    - Item checked non in state → entra nel ciclo (interval=1)
    - Item unchecked → tracked in known_unchecked
    - Item spariti → retired
    - Fuzzy match per testo cambiato tra rigenerazioni
    """
    if not vault_brain_dump_path.exists():
        print(f"[sr] Brain dump non trovato: {vault_brain_dump_path}")
        return state

    text = vault_brain_dump_path.read_text(encoding="utf-8")
    parsed = parse_brain_dump(text)

    today = date.today().isoformat()
    now = datetime.now().isoformat(timespec="seconds")

    # Compute IDs for all parsed items
    parsed_ids = set()
    parsed_map = {}  # id → item
    for item in parsed:
        item_id = compute_item_id(item["section"], item["topic"], item["text"])
        parsed_ids.add(item_id)
        parsed_map[item_id] = item

    existing_ids = set(state["items"].keys())
    known_unchecked = set(state.get("known_unchecked", []))
    new_count = 0
    migrated_count = 0

    # Check for fuzzy matches: items in state not found in parsed_ids
    missing_from_parse = existing_ids - parsed_ids
    unmatched_parsed = {iid: it for iid, it in parsed_map.items() if iid not in existing_ids}

    # Try to migrate SR data for fuzzy-matched items
    for old_id in list(missing_from_parse):
        old_item = state["items"][old_id]
        best_match_id = None
        best_ratio = 0.0
        for new_id, new_item in list(unmatched_parsed.items()):
            ratio = SequenceMatcher(
                None, _normalize(old_item["text"]), _normalize(new_item["text"])
            ).ratio()
            if ratio >= 0.85 and ratio > best_ratio:
                best_ratio = ratio
                best_match_id = new_id
        if best_match_id:
            # Migrate: copy SR data to new ID, retire old
            new_entry = dict(state["items"][old_id])
            new_entry["item_id"] = best_match_id
            new_entry["text"] = parsed_map[best_match_id]["text"]
            new_entry["section"] = parsed_map[best_match_id]["section"]
            new_entry["topic"] = parsed_map[best_match_id]["topic"]
            new_entry["lesson"] = parsed_map[best_match_id].get("lesson", new_entry.get("lesson"))
            state["items"][best_match_id] = new_entry
            state["items"][old_id]["retired"] = True
            del unmatched_parsed[best_match_id]
            missing_from_parse.discard(old_id)
            migrated_count += 1

    # Retire items that truly disappeared
    for old_id in missing_from_parse:
        if not state["items"][old_id].get("retired"):
            state["items"][old_id]["retired"] = True

    # Process parsed items
    new_known_unchecked = []
    for item_id, item in parsed_map.items():
        if item["checked"]:
            if item_id not in state["items"]:
                # New checked item → enters SR cycle
                state["items"][item_id] = {
                    "item_id": item_id,
                    "text": item["text"],
                    "section": item["section"],
                    "topic": item["topic"],
                    "lesson": item["lesson"],
                    "entered": today,
                    "last_review_date": today,
                    "interval_days": 1,
                    "performance_score": 2,
                    "review_count": 1,
                    "retired": False,
                }
                new_count += 1
            else:
                # Already tracked, ensure not retired
                state["items"][item_id]["retired"] = False
        else:
            new_known_unchecked.append(item_id)

    state["known_unchecked"] = new_known_unchecked
    state["last_detect"] = now

    print(f"[sr] Detect: {new_count} nuovi, {migrated_count} migrati, "
          f"{len(new_known_unchecked)} unchecked, "
          f"{sum(1 for i in state['items'].values() if i.get('retired'))} ritirati")
    return state


# ── Algorithm ──────────────────────────────────────────────────────────────

def next_interval(current: int, score: int) -> int:
    """Calcola prossimo intervallo dato score (0/1/2)."""
    if score == 0:
        return 1
    if score == 1:
        return current
    # score == 2: avanza al prossimo intervallo
    try:
        idx = INTERVALS.index(current)
        return INTERVALS[min(idx + 1, len(INTERVALS) - 1)]
    except ValueError:
        # Intervallo custom, trova il primo >= current e avanza
        for i, iv in enumerate(INTERVALS):
            if iv >= current:
                return INTERVALS[min(i + 1, len(INTERVALS) - 1)]
        return INTERVALS[-1]


def _due_date(item: dict) -> date:
    return date.fromisoformat(item["last_review_date"]) + timedelta(days=item["interval_days"])


def _active_items(state: dict) -> list[tuple[str, dict]]:
    return [(iid, it) for iid, it in state["items"].items() if not it.get("retired")]


def items_due(state: dict, today: date | None = None) -> list[tuple[str, dict]]:
    """Item con scadenza == oggi."""
    today = today or date.today()
    return [(iid, it) for iid, it in _active_items(state) if _due_date(it) == today]


def items_overdue(state: dict, today: date | None = None) -> list[tuple[str, dict]]:
    """Item con scadenza < oggi."""
    today = today or date.today()
    return [(iid, it) for iid, it in _active_items(state) if _due_date(it) < today]


def items_tomorrow(state: dict, today: date | None = None) -> list[tuple[str, dict]]:
    """Item con scadenza == domani."""
    today = today or date.today()
    tomorrow = today + timedelta(days=1)
    return [(iid, it) for iid, it in _active_items(state) if _due_date(it) == tomorrow]


# ── Scoring ────────────────────────────────────────────────────────────────

def score_item(state: dict, item_id: str, score: int, today: date | None = None) -> dict:
    """Aggiorna interval/date/count per un item dopo scoring."""
    today = today or date.today()
    item = state["items"][item_id]
    new_iv = next_interval(item["interval_days"], score)
    item["interval_days"] = new_iv
    item["last_review_date"] = today.isoformat()
    item["performance_score"] = score
    item["review_count"] = item.get("review_count", 0) + 1
    return state


# ── Review section generator ──────────────────────────────────────────────

def _format_date_it(d: date) -> str:
    mesi = ["gen", "feb", "mar", "apr", "mag", "giu",
            "lug", "ago", "set", "ott", "nov", "dic"]
    return f"{d.day} {mesi[d.month - 1]} {d.year}"


def generate_review_section(subject: str) -> str:
    """Produce markdown con sezione 'Ripasso del giorno'."""
    state = load_state(subject)
    today = date.today()

    overdue = items_overdue(state, today)
    due = items_due(state, today)
    tomorrow = items_tomorrow(state, today)

    total_due = len(overdue) + len(due)

    lines = [
        f"## Ripasso del giorno ({_format_date_it(today)})",
        "",
        f"> {total_due} item in scadenza · {len(overdue)} arretrati · {len(tomorrow)} domani",
        "",
    ]

    if overdue:
        lines.append("### Arretrati")
        for _, item in sorted(overdue, key=lambda x: _due_date(x[1])):
            due_d = _format_date_it(_due_date(item))
            lines.append(f"- [ ] {item['text']} *(scad. {due_d} · intervallo {item['interval_days']}g)*")
        lines.append("")

    if due:
        lines.append("### Oggi")
        for _, item in due:
            lines.append(f"- [ ] {item['text']} *(intervallo {item['interval_days']}g)*")
        lines.append("")

    if tomorrow:
        lines.append("### Domani (anteprima)")
        for _, item in tomorrow:
            lines.append(f"- [ ] {item['text']} *(intervallo {item['interval_days']}g)*")
        lines.append("")

    if total_due == 0 and not tomorrow:
        lines.append("*Nessun item in scadenza oggi. Ottimo lavoro!*")
        lines.append("")

    lines.append(f"> Esegui: `python pipeline.py sr_review {subject}`")
    lines.append("")

    return "\n".join(lines)
