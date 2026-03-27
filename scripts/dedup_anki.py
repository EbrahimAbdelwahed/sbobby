"""
Dedup card Anki per le lezioni di run_overnight.py.

1. Scarica tutte le note taggate con le lezioni target
2. Normalizza il testo (strip HTML, cloze markers, punteggiatura)
3. Confronto pairwise con difflib ratio
4. Cluster Union-Find → mantiene la nota con più reviews
5. Mostra report, chiede conferma, cancella

Uso:
    conda activate sbobine
    python scripts/dedup_anki.py               # dry-run, tutte le lezioni overnight
    python scripts/dedup_anki.py --execute      # cancella davvero
    python scripts/dedup_anki.py --threshold 0.90
    python scripts/dedup_anki.py --subject anatomia   # solo anatomia
"""

import argparse
import json
import re
import urllib.request
from collections import defaultdict
from difflib import SequenceMatcher
from itertools import combinations
from pathlib import Path

ANKI_URL = "http://localhost:8765"
REPORT_PATH = Path(__file__).resolve().parent.parent / "dedup_report.md"
DEFAULT_THRESHOLD = 0.90  # conservativo: cattura solo near-exact (stessa frase, phrasing lievemente diverso)

OVERNIGHT_LESSONS = [
    ("anatomia",   "lezione_08"),
    ("anatomia",   "lezione_09"),
    ("anatomia",   "lezione_canzi_02"),
    ("biochimica", "lezione_10"),
    ("biochimica", "lezione_11"),
    ("biochimica", "lezione_12"),
    ("biochimica", "lezione_13"),
    ("biochimica", "lezione_14"),
    ("biochimica", "lezione_15"),
    ("istologia",  "lezione_04"),
]


# ── AnkiConnect ───────────────────────────────────────────────────────────────

def anki(action, **params):
    payload = json.dumps({"action": action, "version": 6, "params": params}).encode()
    with urllib.request.urlopen(urllib.request.Request(ANKI_URL, data=payload), timeout=30) as r:
        res = json.loads(r.read())
    if res.get("error"):
        raise RuntimeError(f"AnkiConnect {action}: {res['error']}")
    return res["result"]


# ── Testo e similarità ────────────────────────────────────────────────────────

def primary_text(note: dict) -> str:
    fields = note.get("fields", {})
    for f in ("Testo", "Fronte", "Front", "Text"):
        if f in fields:
            return fields[f].get("value", "")
    return next(iter(fields.values()), {}).get("value", "") if fields else ""


def secondary_text(note: dict) -> str:
    """Retro per Basic, vuoto per Cloze (Testo contiene tutto)."""
    fields = note.get("fields", {})
    for f in ("Retro", "Back"):
        if f in fields:
            return fields[f].get("value", "")
    return ""


def normalize(text: str) -> str:
    text = re.sub(r"\{\{c\d+::(.*?)\}\}", r"\1", text)   # cloze → testo
    text = re.sub(r"<[^>]+>", " ", text)                   # strip HTML
    text = re.sub(r"[^\w\s]", " ", text, flags=re.UNICODE) # punteggiatura
    return " ".join(text.lower().split())


def sim(a: str, b: str) -> float:
    na, nb = normalize(a), normalize(b)
    if not na or not nb:
        return 0.0
    return SequenceMatcher(None, na, nb).ratio()


def note_sim(n1: dict, n2: dict) -> float:
    """Similarità tra due note: media pesata primario (70%) + secondario (30%).

    Per Basic: confronta Fronte+Retro → evita falsi positivi su card con
    stesso Fronte ma Retro diverso (stessa domanda, risposta diversa).
    Per Cloze: campo Testo contiene tutto, secondario è vuoto → ratio normale.
    """
    s_primary = sim(primary_text(n1), primary_text(n2))
    sec1, sec2 = secondary_text(n1), secondary_text(n2)
    if sec1 and sec2:
        s_secondary = sim(sec1, sec2)
        return 0.70 * s_primary + 0.30 * s_secondary
    return s_primary


# ── Stats card ────────────────────────────────────────────────────────────────

def best_stats(note: dict, cmap: dict) -> tuple[int, int]:
    reps = [cmap.get(c, {}).get("reps", 0) for c in note.get("cards", [])]
    ivl  = [cmap.get(c, {}).get("interval", 0) for c in note.get("cards", [])]
    return (max(reps, default=0), max(ivl, default=0))


# ── Union-Find ────────────────────────────────────────────────────────────────

class UF:
    def __init__(self): self.p = {}
    def find(self, x):
        self.p.setdefault(x, x)
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]; x = self.p[x]
        return x
    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb: self.p[rb] = ra
    def clusters(self):
        g = defaultdict(list)
        for x in self.p: g[self.find(x)].append(x)
        return [v for v in g.values() if len(v) > 1]


# ── Core ──────────────────────────────────────────────────────────────────────

def fetch_notes(subjects: list[str]) -> list[dict]:
    ids: set[int] = set()
    for subject, lesson in OVERNIGHT_LESSONS:
        if subjects and subject not in subjects:
            continue
        tag = f"{subject}::{lesson}"
        found = anki("findNotes", query=f"tag:{tag}") or []
        ids.update(found)
        print(f"  tag:{tag} → {len(found)}")
    if not ids:
        return []
    return anki("notesInfo", notes=list(ids))


def fetch_card_map(notes: list[dict]) -> dict:
    cids = [c for n in notes for c in n.get("cards", [])]
    if not cids:
        return {}
    infos = anki("cardsInfo", cards=cids)
    return {c["cardId"]: c for c in infos}


def find_clusters(notes: list[dict], cmap: dict, threshold: float) -> list[list[dict]]:
    uf = UF()
    by_id = {n["noteId"]: n for n in notes}
    ids = [n["noteId"] for n in notes]
    total = len(ids) * (len(ids) - 1) // 2
    print(f"  Confronto {len(ids)} note ({total} coppie)...")

    for id_a, id_b in combinations(ids, 2):
        if note_sim(by_id[id_a], by_id[id_b]) >= threshold:
            uf.union(id_a, id_b)

    result = []
    for members in uf.clusters():
        group = [by_id[m] for m in members if m in by_id]
        group.sort(key=lambda n: best_stats(n, cmap), reverse=True)
        result.append(group)
    return result


def build_report(clusters: list[list[dict]], cmap: dict, threshold: float) -> str:
    lines = [f"# Dedup Anki — soglia {threshold}\n"]
    to_del = sum(len(c) - 1 for c in clusters)
    lines.append(f"**{len(clusters)} cluster, {to_del} note da cancellare**\n")

    for i, cluster in enumerate(clusters, 1):
        champ = cluster[0]
        cs = best_stats(champ, cmap)
        lines.append(f"## Cluster {i} ({len(cluster)} note)")
        lines.append(f"✓ TENERE `#{champ['noteId']}` [{champ.get('modelName','?')}] reviews={cs[0]} ivl={cs[1]}")
        lines.append(f"> {primary_text(champ)[:180]}\n")
        for dup in cluster[1:]:
            ds = best_stats(dup, cmap)
            ratio = note_sim(champ, dup)
            lines.append(f"✗ CANCELLARE `#{dup['noteId']}` [{dup.get('modelName','?')}] reviews={ds[0]} ivl={ds[1]} sim={ratio:.0%}")
            lines.append(f"> {primary_text(dup)[:180]}\n")
    return "\n".join(lines)


def parse_report_ids(report_text: str) -> list[int]:
    """Estrae gli ID delle note marcate '✗ CANCELLARE' nel report.

    L'utente può rimuovere o modificare le righe '✗ CANCELLARE' per escluderle.
    Qualsiasi riga che non inizia esattamente con '✗ CANCELLARE `#' viene ignorata.
    """
    ids = []
    for line in report_text.splitlines():
        m = re.match(r"✗ CANCELLARE `#(\d+)`", line)
        if m:
            ids.append(int(m.group(1)))
    return ids


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--execute", action="store_true",
                    help="Legge dedup_report.md ed esegue la cancellazione")
    ap.add_argument("--threshold", type=float, default=DEFAULT_THRESHOLD)
    ap.add_argument("--subject", nargs="+", default=[], help="Filtra per materia (es. anatomia)")
    ap.add_argument("--fresh", action="store_true",
                    help="Forza ricalcolo anche se il report esiste già")
    args = ap.parse_args()

    # ── EXECUTE: legge il report (eventualmente già modificato dall'utente) ──
    if args.execute:
        if not REPORT_PATH.exists():
            print(f"Report non trovato: {REPORT_PATH}")
            print("Esegui prima senza --execute per generarlo.")
            return

        report_text = REPORT_PATH.read_text(encoding="utf-8")
        ids = parse_report_ids(report_text)

        if not ids:
            print("Nessuna riga '✗ CANCELLARE' nel report. Nulla da fare.")
            return

        print(f"\n=== Dedup Anki [EXECUTE] ===")
        print(f"Note da cancellare (dal report): {len(ids)}")
        print("IDs:", ids)

        confirm = input(f"\nConfermi cancellazione di {len(ids)} note? [s/N] ").strip().lower()
        if confirm != "s":
            print("Annullato.")
            return

        anki("deleteNotes", notes=ids)
        print(f"Cancellate {len(ids)} note. Stats delle note mantenute intatte.")
        return

    # ── ANALISI: genera/aggiorna il report ───────────────────────────────────
    if REPORT_PATH.exists() and not args.fresh:
        print(f"Report già presente: {REPORT_PATH}")
        print("Modificalo e riesegui con --execute, oppure usa --fresh per ricalcolare.")
        return

    print(f"\n=== Dedup Anki [ANALISI] | soglia={args.threshold} ===\n")

    print("Fetch note...")
    notes = fetch_notes(args.subject)
    if not notes:
        print("Nessuna nota trovata.")
        return

    print(f"{len(notes)} note totali. Fetch card info...")
    cmap = fetch_card_map(notes)

    clusters = find_clusters(notes, cmap, args.threshold)
    to_del = sum(len(c) - 1 for c in clusters)

    report = build_report(clusters, cmap, args.threshold)
    REPORT_PATH.write_text(report, encoding="utf-8")
    print(f"\nReport → {REPORT_PATH}")
    print(f"Cluster trovati: {len(clusters)} | Note da cancellare: {to_del}")

    if to_del == 0:
        print("Nessun duplicato. Fine.")
    else:
        print("\nRevisionare il report, rimuovere le righe '✗ CANCELLARE' indesiderate,")
        print("poi eseguire:  python scripts/dedup_anki.py --execute")


if __name__ == "__main__":
    main()
