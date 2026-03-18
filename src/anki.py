"""
Generazione flashcard cloze dall'appendice tabellare SSOT e invio ad Anki via AnkiConnect.

Max 3 cloze per card, cloze indipendenti (non oscurati tutti contemporaneamente).
"""

import json
import re
import urllib.request
from pathlib import Path

ANKI_CONNECT_URL = "http://localhost:8765"
DECK_PREFIX = "Medicina"  # Deck: Medicina::Anatomia, Medicina::Biochimica, etc.


def _sanitize_html(text: str) -> str:
    """Converte markdown bold in HTML e rimuove doppi punti."""
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"\.{2,}", ".", text)
    return text


def anki_request(action: str, **params) -> dict:
    """Invia una richiesta ad AnkiConnect."""
    payload = json.dumps({"action": action, "version": 6, "params": params}).encode()
    req = urllib.request.Request(ANKI_CONNECT_URL, data=payload)
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read().decode())
    err = result.get("error")
    if err:
        # addNotes restituisce errori per-nota come stringa repr di lista
        # es. "['cannot create note because it is a duplicate', ...]"
        # Questi non sono errori fatali — li gestiamo nel chiamante
        if "cannot create note because it is a duplicate" in str(err):
            return result["result"]
        raise RuntimeError(f"AnkiConnect error: {err}")
    return result["result"]


def ensure_deck(deck_name: str) -> None:
    """Crea il deck se non esiste."""
    anki_request("createDeck", deck=deck_name)


def ensure_cloze_model() -> None:
    """Verifica che il modello Cloze esista (è built-in in Anki)."""
    models = anki_request("modelNames")
    if "Cloze" not in models:
        raise RuntimeError("Modello 'Cloze' non trovato in Anki. Dovrebbe essere un modello built-in.")


def parse_markdown_tables(text: str) -> list[dict]:
    """Estrae le tabelle markdown dall'appendice tabellare.

    Restituisce una lista di dict con chiavi:
        - 'type': nome della sezione (es. 'Muscoli', 'Legamenti')
        - 'headers': lista delle intestazioni
        - 'rows': lista di liste (righe della tabella)
    """
    # Trova la sezione APPENDICE TABELLARE
    appendix_match = re.search(r"## APPENDICE TABELLARE.*", text, re.DOTALL)
    if not appendix_match:
        print("[anki] Nessuna appendice tabellare trovata")
        return []

    appendix_text = appendix_match.group(0)
    tables = []

    # Trova ogni sottosezione (### Muscoli, ### Legamenti, etc.)
    sections = re.split(r"###\s+", appendix_text)[1:]  # skip prima parte

    for section in sections:
        lines = section.strip().splitlines()
        if not lines:
            continue

        table_type = lines[0].strip()

        # Trova le righe della tabella markdown
        table_lines = [l for l in lines[1:] if l.strip().startswith("|")]
        if len(table_lines) < 3:  # header + separator + almeno una riga
            continue

        # Parse header
        headers = [h.strip() for h in table_lines[0].split("|") if h.strip()]
        # Rimuovi colonna IMMAGINE (la gestiamo separatamente)
        img_idx = None
        for i, h in enumerate(headers):
            if h.upper() == "IMMAGINE":
                img_idx = i
                break

        # Parse righe (salta la riga separatore |---|---|)
        rows = []
        for line in table_lines[2:]:
            cells = [c.strip() for c in line.split("|") if c.strip()]
            if img_idx is not None and len(cells) > img_idx:
                cells.pop(img_idx)
            if cells:
                rows.append(cells)

        if img_idx is not None:
            headers.pop(img_idx)

        tables.append({
            "type": table_type,
            "headers": headers,
            "rows": rows,
        })

    return tables


def _cell_ok(value: str) -> bool:
    """Controlla se una cella ha contenuto utilizzabile per un cloze."""
    v = value.strip()
    if not v or v == "-" or v == "—" or v == "–":
        return False
    return True


def _clean(value: str) -> str:
    """Strip HTML spans (coloring), converti markdown bold, rimuovi punto finale trailing."""
    v = re.sub(r"</?span[^>]*>", "", value).strip()
    v = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", v)
    v = v.rstrip(".")
    return v


def _tag_from_heading(table_type: str, subject: str) -> str:
    """Genera tag gerarchico dal nome della sezione tabellare."""
    # "Muscoli Cuffia dei Rotatori" → "muscoli-cuffia-dei-rotatori"
    slug = re.sub(r"[^\w\s-]", "", table_type.lower())
    slug = re.sub(r"\s+", "-", slug.strip())
    return f"{subject}::{slug}"


def _detect_table_kind(headers: list[str]) -> str:
    """Rileva il tipo di tabella dagli header (case-insensitive)."""
    h_upper = [h.upper() for h in headers]

    # Anatomia — strutture specifiche
    if "MUSCOLO" in h_upper and "INNERVAZIONE" in h_upper:
        return "muscoli"
    if "ARTICOLAZIONE" in h_upper and "TIPO" in h_upper:
        return "articolazioni"
    if "LEGAMENTO" in h_upper and "FUNZIONE" in h_upper:
        return "legamenti"
    if any(h in h_upper for h in ("VASO", "NERVO")) and "TERRITORIO" in h_upper:
        return "vasi_nervi"

    # Biochimica
    if "AMINOACIDO" in h_upper:
        return "aminoacidi"
    if "INTERAZIONE" in h_upper and "RUOLO BIOLOGICO" in h_upper:
        return "interazioni_deboli"
    if any("INTERAZIONE" in h for h in h_upper) and any("RUOLO" in h for h in h_upper):
        return "interazioni_deboli"
    if "ORGANELLO" in h_upper or ("ORGANELLO/CONTESTO" in h_upper):
        return "compartimentalizzazione"
    if any("ORGANELLO" in h for h in h_upper):
        return "compartimentalizzazione"
    if "VIA" in h_upper and any("SUBSTRATO" in h for h in h_upper):
        return "vie_metaboliche"
    if "ENZIMA" in h_upper and any("REAZIONE" in h or "SUBSTRATO" in h for h in h_upper):
        return "vie_metaboliche"
    if "MODIFICAZIONE" in h_upper or any("MODIFICAZIONE" in h for h in h_upper):
        return "modificazioni"

    # Istologia
    if "CELLULA / STRUTTURA" in h_upper or "CELLULA" in h_upper:
        return "cellule"
    if any("TESSUTO" in h for h in h_upper) and any("MORFOLOGIA" in h or "STRATI" in h for h in h_upper):
        return "tessuti"
    if any("TECNICA" in h for h in h_upper) and any("RISOLUZIONE" in h or "LIMITE" in h for h in h_upper):
        return "microscopia"
    if any("COLORAZIONE" in h or "BASOFILIA" in h or "ACIDOFILIA" in h for h in h_upper):
        return "colorazione"
    if any("NUCLEO" in h or "NUCLEARE" in h for h in h_upper) and any("CROMATINA" in h for h in h_upper):
        return "nuclei"
    if any("TECNICA" in h or "PROCESSO" in h for h in h_upper) and any("SCOPO" in h for h in h_upper):
        return "tecniche"

    # Fallback: tabella concettuale
    return "concettuale"


def _get_col(row: list[str], headers: list[str], *col_names: str) -> str | None:
    """Trova il valore di una colonna per nome (case-insensitive, partial match)."""
    h_upper = [h.upper() for h in headers]
    for name in col_names:
        name_up = name.upper()
        for i, h in enumerate(h_upper):
            if name_up in h:
                if i < len(row) and _cell_ok(row[i]):
                    return _clean(row[i])
    return None


def generate_cloze_cards(tables: list[dict], lesson_tag: str, subject: str = "") -> list[dict]:
    """Genera card cloze dalle tabelle con template specifici per tipo.

    Ogni riga può generare 1-3 card separate con frasi contestuali.
    """
    cards = []

    for table in tables:
        headers = table["headers"]
        if len(headers) < 2:
            continue

        kind = _detect_table_kind(headers)
        table_tag = _tag_from_heading(table["type"], subject) if subject else f"tabella::{table['type'].lower()}"
        base_tags = [lesson_tag, table_tag]

        for row in table["rows"]:
            if len(row) < 2:
                continue

            # Skip righe-intestazione (es. "**Alifatici Apolari**" senza dati)
            name = _clean(row[0])
            data_cells = [c for c in row[1:] if _cell_ok(c)]
            if not data_cells:
                continue

            new_cards = _generate_for_kind(kind, row, headers, name, base_tags)
            cards.extend(new_cards)

    return cards


def _generate_for_kind(
    kind: str, row: list[str], headers: list[str], name: str, base_tags: list[str]
) -> list[dict]:
    """Genera card per una riga in base al tipo di tabella rilevato."""
    g = lambda *names: _get_col(row, headers, *names)  # shortcut
    cards = []

    # ─── ANATOMIA ─────────────────────────────────────────────
    if kind == "muscoli":
        origine = g("ORIGINE")
        inserzione = g("INSERZIONE")
        azione = g("AZIONE")
        innervazione = g("INNERVAZIONE")

        if origine and inserzione:
            cards.append(_card(
                f"Il muscolo <b>{name}</b> origina da {{{{c1::{origine}}}}} "
                f"e si inserisce su {{{{c2::{inserzione}}}}}.",
                base_tags
            ))
        if azione:
            cards.append(_card(
                f"Il muscolo <b>{name}</b> ha come azione principale {{{{c1::{azione}}}}}.",
                base_tags
            ))
        if innervazione:
            cards.append(_card(
                f"Il muscolo <b>{name}</b> è innervato dal {{{{c1::{innervazione}}}}}.",
                base_tags
            ))

    elif kind == "articolazioni":
        tipo = g("TIPO")
        gdl = g("GRADI DI LIBERTÀ", "GRADI")
        superfici = g("SUPERFICI")
        movimenti = g("MOVIMENTI")

        if tipo:
            text = f"L'articolazione <b>{name}</b> è classificata come {{{{c1::{tipo}}}}}"
            if gdl:
                text += f" con {{{{c2::{gdl}}}}} gradi di libertà"
            text += "."
            cards.append(_card(text, base_tags))
        if superfici:
            cards.append(_card(
                f"Le superfici articolari dell'articolazione <b>{name}</b> sono {{{{c1::{superfici}}}}}.",
                base_tags
            ))
        if movimenti:
            cards.append(_card(
                f"L'articolazione <b>{name}</b> consente i seguenti movimenti: {{{{c1::{movimenti}}}}}.",
                base_tags
            ))

    elif kind == "legamenti":
        origine = g("ORIGINE")
        inserzione = g("INSERZIONE")
        funzione = g("FUNZIONE")
        tensione = g("POSIZIONE DI TENSIONE", "TENSIONE")

        if origine and inserzione:
            cards.append(_card(
                f"Il legamento <b>{name}</b> si estende da {{{{c1::{origine}}}}} a {{{{c2::{inserzione}}}}}.",
                base_tags
            ))
        if funzione:
            text = f"Il legamento <b>{name}</b> ha come funzione {{{{c1::{funzione}}}}}"
            if tensione:
                text += f" ed è in massima tensione in {{{{c2::{tensione}}}}}"
            text += "."
            cards.append(_card(text, base_tags))

    elif kind == "vasi_nervi":
        origine = g("ORIGINE")
        territorio = g("TERRITORIO")

        if origine:
            cards.append(_card(
                f"<b>{name}</b> origina da {{{{c1::{origine}}}}}.",
                base_tags
            ))
        if territorio:
            cards.append(_card(
                f"<b>{name}</b> irrora/innerva {{{{c1::{territorio}}}}}.",
                base_tags
            ))

    # ─── BIOCHIMICA ───────────────────────────────────────────
    elif kind == "aminoacidi":
        gruppo = g("GRUPPO")
        catena = g("CATENA LATERALE", "CATENA")
        pka = g("PKA")
        note = g("NOTE", "RUOLO")

        if gruppo and catena:
            cards.append(_card(
                f"L'aminoacido <b>{name}</b> appartiene al gruppo {{{{c1::{gruppo}}}}} "
                f"e ha catena laterale {{{{c2::{catena}}}}}.",
                base_tags
            ))
        if pka:
            cards.append(_card(
                f"Il pKa della catena laterale di <b>{name}</b> è {{{{c1::{pka}}}}}.",
                base_tags
            ))
        if note:
            cards.append(_card(
                f"Proprietà speciale di <b>{name}</b>: {{{{c1::{note}}}}}.",
                base_tags
            ))

    elif kind == "interazioni_deboli":
        descrizione = g("DESCRIZIONE", "NATURA")
        forza = g("ENERGIA", "FORZA")
        ruolo = g("RUOLO")

        if descrizione:
            text = f"Le <b>{name}</b> sono {{{{c1::{descrizione}}}}}"
            if forza:
                text += f". La loro forza è {{{{c2::{forza}}}}}"
            text += "."
            cards.append(_card(text, base_tags))
        if ruolo:
            cards.append(_card(
                f"Il ruolo biologico delle <b>{name}</b> è {{{{c1::{ruolo}}}}}.",
                base_tags
            ))

    elif kind == "compartimentalizzazione":
        ambiente = g("AMBIENTE", "CARATTERISTICA")
        funzione = g("FUNZIONE")
        vantaggio = g("VANTAGGIO")

        if ambiente and funzione:
            cards.append(_card(
                f"<b>{name}</b> ha un ambiente {{{{c1::{ambiente}}}}} "
                f"e svolge la funzione di {{{{c2::{funzione}}}}}.",
                base_tags
            ))
        if vantaggio and vantaggio != funzione:
            cards.append(_card(
                f"Il vantaggio della compartimentalizzazione in <b>{name}</b> è {{{{c1::{vantaggio}}}}}.",
                base_tags
            ))

    elif kind == "vie_metaboliche":
        substrato = g("SUBSTRATO INIZIALE", "SUBSTRATO")
        prodotto = g("PRODOTTO FINALE", "PRODOTTO")
        sede = g("SEDE", "LOCALIZZAZIONE")
        regolazione = g("REGOLAZIONE")

        if substrato and prodotto:
            cards.append(_card(
                f"La via <b>{name}</b> converte {{{{c1::{substrato}}}}} in {{{{c2::{prodotto}}}}}.",
                base_tags
            ))
        if sede:
            cards.append(_card(
                f"La via <b>{name}</b> avviene nel/nella {{{{c1::{sede}}}}}.",
                base_tags
            ))
        if regolazione:
            cards.append(_card(
                f"La regolazione principale della via <b>{name}</b> è {{{{c1::{regolazione}}}}}.",
                base_tags
            ))

    elif kind == "modificazioni":
        aa = g("AMINOACIDI COINVOLTI", "AMINOACIDI")
        legame = g("TIPO DI LEGAME", "LEGAME")
        funzione = g("FUNZIONE", "ESEMPIO")

        if aa and legame:
            text = f"<b>{name}</b> coinvolge {{{{c1::{aa}}}}} tramite {{{{c2::{legame}}}}}"
            if funzione:
                text += f". Funzione: {funzione}"
            text += "."
            cards.append(_card(text, base_tags))

    # ─── ISTOLOGIA ────────────────────────────────────────────
    elif kind == "tessuti":
        morfologia = g("MORFOLOGIA")
        strati = g("STRATI")
        localizzazione = g("LOCALIZZAZIONE")
        funzione = g("FUNZIONE")

        if morfologia and strati:
            cards.append(_card(
                f"<b>{name}</b> ha cellule di forma {{{{c1::{morfologia}}}}} "
                f"organizzate in {{{{c2::{strati}}}}}.",
                base_tags
            ))
        if localizzazione:
            cards.append(_card(
                f"<b>{name}</b> si trova in {{{{c1::{localizzazione}}}}}.",
                base_tags
            ))
        if funzione:
            cards.append(_card(
                f"La funzione principale di <b>{name}</b> è {{{{c1::{funzione}}}}}.",
                base_tags
            ))

    elif kind == "cellule":
        localizzazione = g("LOCALIZZAZIONE")
        morfologia = g("MORFOLOGIA", "ASPETTO")
        funzione = g("FUNZIONE")

        if morfologia:
            cards.append(_card(
                f"<b>{name}</b>: morfologia/aspetto → {{{{c1::{morfologia}}}}}.",
                base_tags
            ))
        if localizzazione:
            cards.append(_card(
                f"<b>{name}</b> si trova in {{{{c1::{localizzazione}}}}}.",
                base_tags
            ))
        if funzione:
            cards.append(_card(
                f"La funzione di <b>{name}</b> è {{{{c1::{funzione}}}}}.",
                base_tags
            ))

    elif kind == "nuclei":
        aspetto = g("ASPETTO")
        cromatina = g("CROMATINA")
        stato = g("STATO FUNZIONALE", "STATO")

        if cromatina and stato:
            cards.append(_card(
                f"Un <b>{name}</b> contiene {{{{c1::{cromatina}}}}} "
                f"ed è in uno stato di {{{{c2::{stato}}}}}.",
                base_tags
            ))

    elif kind == "colorazione":
        definizione = g("DEFINIZIONE", "AFFINITÀ")
        colorante = g("COLORANTE")
        colore = g("COLORE")
        esempio = g("ESEMPIO")

        if definizione:
            text = f"<b>{name}</b>: {{{{c1::{definizione}}}}}"
            if colore:
                text += f". Colore risultante: {{{{c2::{colore}}}}}"
            text += "."
            cards.append(_card(text, base_tags))

    elif kind == "microscopia":
        fonte = g("FONTE", "PRINCIPIO")
        risoluzione = g("RISOLUZIONE", "LIMITE")
        vantaggi = g("VANTAGGI", "CARATTERISTICHE")

        if risoluzione:
            text = f"Il limite di risoluzione di <b>{name}</b> è {{{{c1::{risoluzione}}}}}"
            if fonte:
                text += f" (principio: {fonte})"
            text += "."
            cards.append(_card(text, base_tags))
        if vantaggi and vantaggi != "—":
            cards.append(_card(
                f"Vantaggi/caratteristiche di <b>{name}</b>: {{{{c1::{vantaggi}}}}}.",
                base_tags
            ))

    elif kind == "tecniche":
        scopo = g("SCOPO")
        materiale = g("MATERIALE", "METODO")

        if scopo:
            text = f"Lo scopo della tecnica <b>{name}</b> è {{{{c1::{scopo}}}}}"
            if materiale:
                text += f". Metodo: {{{{c2::{materiale}}}}}"
            text += "."
            cards.append(_card(text, base_tags))

    # ─── FALLBACK: CONCETTUALE ────────────────────────────────
    else:
        # Tabella concettuale generica: nome + definizione
        definizione = g("DEFINIZIONE", "DESCRIZIONE", "CARATTERISTICA", "FUNZIONE")
        esempio = g("ESEMPIO", "APPLICAZIONE")

        if definizione:
            text = f"<b>{name}</b>: {{{{c1::{definizione}}}}}"
            if esempio:
                text += f" (es. {esempio})"
            text += "."
            cards.append(_card(text, base_tags))
        elif len(row) >= 2:
            # Ultimo fallback: secondo campo come cloze
            val = _clean(row[1])
            if _cell_ok(val):
                cards.append(_card(
                    f"<b>{name}</b>: {{{{c1::{val}}}}}.",
                    base_tags
                ))

    return cards


def _card(text: str, tags: list[str]) -> dict:
    """Crea un dict card cloze."""
    return {"text": text, "tags": list(tags)}


def send_to_anki(cards: list[dict], deck_name: str) -> int:
    """Invia le card cloze ad Anki via AnkiConnect. Restituisce il numero di card aggiunte."""
    ensure_deck(deck_name)
    ensure_cloze_model()

    notes = []
    for card in cards:
        notes.append({
            "deckName": deck_name,
            "modelName": "Cloze",
            "fields": {
                "Testo": _sanitize_html(card["text"]),
            },
            "tags": card["tags"],
            "options": {
                "allowDuplicate": False,
                "duplicateScope": "deck",
            },
        })

    if not notes:
        print("[anki] Nessuna card da inviare")
        return 0

    results = anki_request("addNotes", notes=notes)
    if results is None:
        # Tutti duplicati — AnkiConnect restituisce null
        print(f"[anki] Tutte {len(notes)} card cloze sono duplicate, skip")
        return 0
    added = sum(1 for r in results if r is not None)
    skipped = len(results) - added
    print(f"[anki] Aggiunte {added} card cloze, {skipped} duplicate saltate")
    return added


def send_basic_to_anki(cards: list[dict], deck_name: str) -> int:
    """Invia card Basic (front/back) ad Anki via AnkiConnect. Restituisce il numero di card aggiunte."""
    ensure_deck(deck_name)

    # Verifica che il modello Basilare esista (Anki in italiano)
    models = anki_request("modelNames")
    if "Basilare" not in models:
        raise RuntimeError("Modello 'Basilare' non trovato in Anki. Dovrebbe essere un modello built-in.")

    notes = []
    for card in cards:
        notes.append({
            "deckName": deck_name,
            "modelName": "Basilare",
            "fields": {
                "Fronte": _sanitize_html(card["front"]),
                "Retro": _sanitize_html(card["back"]),
            },
            "tags": card.get("tags", []),
            "options": {
                "allowDuplicate": False,
                "duplicateScope": "deck",
            },
        })

    if not notes:
        print("[anki] Nessuna card basic da inviare")
        return 0

    results = anki_request("addNotes", notes=notes)
    if results is None:
        print(f"[anki] Tutte {len(notes)} card basic sono duplicate, skip")
        return 0
    added = sum(1 for r in results if r is not None)
    skipped = len(results) - added
    print(f"[anki] Aggiunte {added} card basic, {skipped} duplicate saltate")
    return added


def is_anki_available() -> bool:
    """Verifica se AnkiConnect è raggiungibile."""
    try:
        anki_request("version")
        return True
    except Exception:
        return False


def sync_anki() -> None:
    """Avvia la sincronizzazione Anki → AnkiWeb (non fatale se fallisce)."""
    try:
        anki_request("sync")
        print("[anki] Sincronizzazione AnkiWeb avviata")
    except Exception as e:
        print(f"[anki] Sync AnkiWeb non riuscito (non fatale): {e}")


def process_ssot(ssot_path: Path, subject: str, lesson: str) -> int:
    """Estrae tabelle da un file SSOT e invia le card ad Anki."""
    text = ssot_path.read_text(encoding="utf-8")
    tables = parse_markdown_tables(text)

    if not tables:
        print("[anki] Nessuna tabella trovata nel file SSOT")
        return 0

    total_rows = sum(len(t["rows"]) for t in tables)
    print(f"[anki] Trovate {len(tables)} tabelle, {total_rows} righe totali")

    lesson_tag = f"{subject}::{lesson}"
    cards = generate_cloze_cards(tables, lesson_tag, subject)
    print(f"[anki] Generate {len(cards)} card cloze")

    deck_name = f"{DECK_PREFIX}::{subject.capitalize()}"
    return send_to_anki(cards, deck_name)


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 4:
        print("Uso: python anki.py <sbobina.md> <materia> <lezione>")
        print("  Esempio: python anki.py sbobine/anatomia/lezione_01.md anatomia lezione_01")
        sys.exit(1)

    ssot_p = Path(sys.argv[1])
    subj = sys.argv[2]
    les = sys.argv[3]
    process_ssot(ssot_p, subj, les)
