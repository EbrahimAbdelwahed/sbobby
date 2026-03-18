# Pipeline Study System — Implementation Plan

> Handover document per implementare le modifiche alla pipeline di studio.
> Contesto: pipeline audio → Whisper → LLM → sbobina già funzionante per Anatomia, Istologia e Biochimica.

---

## Stato attuale

La pipeline produce sbobine in markdown con HTML inline (div flex per layout immagini, span per colori, SVG inline per strutture molecolari). Il formato attuale funziona come archivio della lezione ma è troppo lungo e verboso per lo studio attivo. Le flashcard Anki e l'integrazione immagini non sono ancora implementate.

L'utente lavora su Mac (16GB) per processing serale e iPad in aula. Editor scelto: **Obsidian** (iPad + Mac).

---

## Modifica 1: Adattare l'output della pipeline a Obsidian

### Problema
L'HTML inline attuale (`<div style="display:flex">`, `<span style="color:...">`, `<img src="...">`) non viene renderizzato in modo affidabile nella live preview di Obsidian su iPad.

### Cosa fare
Modificare il prompt LLM della pipeline (il passaggio che genera la sbobina dal transcript Whisper) per produrre output in formato Obsidian-native.

### Sostituzioni specifiche

**Immagini:** da HTML a sintassi Obsidian
```
<!-- PRIMA -->
<div style="display:flex; align-items:flex-start; gap:1.5em;">
<div style="flex:1;">testo descrittivo</div>
<img src="structures/abc123.svg" alt="glicina" width="250" />
</div>

<!-- DOPO -->
testo descrittivo
![[structures/abc123.svg]]
```

Per layout affiancato testo-immagine, valutare il plugin **Obsidian Columns** o un CSS snippet custom. In alternativa, le immagini possono stare su riga separata subito dopo il paragrafo — meno elegante ma funziona ovunque senza plugin.

**Colori/highlighting:** da `<span style="color:...">` a una delle seguenti opzioni:
- Obsidian callout blocks per enfasi (`> [!info]`, `> [!warning]`)
- Plugin Highlightr per colori inline
- Markup `==highlighted==` nativo per singolo colore
- Decidere con l'utente quale approccio preferisce — il colore inline era usato per: nomi aminoacidi (arancione), molecole chiave (rosso), vie metaboliche (blu)

**Enfasi docente:** da `> ⚠️ **Enfasi docente:**` a Obsidian callout:
```markdown
> [!warning] Enfasi docente
> Contenuto dell'enfasi
```

**Tabelle:** il markdown table standard funziona in Obsidian senza modifiche. Nessun cambiamento necessario.

### Note implementative
- Le sbobine già generate rimangono come sono (archivio). Le modifiche si applicano solo al prompt per le sbobine future.
- Testare il rendering su Obsidian iPad dopo le modifiche al prompt, prima di processare lezioni in batch.
- Le immagini SVG delle strutture molecolari devono trovarsi nella vault Obsidian, nella cartella `structures/` relativa alla sbobina (o in una cartella assets centralizzata — da decidere con l'utente).

---

## Modifica 2: Secondo passaggio LLM — Documento di studio compatto

### Problema
Le sbobine attuali funzionano come archivio ma sono troppo lunghe per la revisione attiva. Servono due artefatti: l'archivio (già prodotto) e un documento di studio compatto.

### Cosa fare
Aggiungere un secondo passaggio LLM che prende la sbobina completa come input e produce un documento di studio condensato.

### Principi del prompt di estrazione

1. **Non è un riassunto — è una riorganizzazione.** Ogni concetto, fatto, correlazione clinica e termine tecnico deve sopravvivere. Si elimina solo: ridondanza (concetti ripetuti in blocchi diversi), filler organizzativo (info su turnazione, email, logistica), e verbosità (riformulazioni prolisse).

2. **Terminologia del docente preservata.** Il prompt deve specificare: "preserva i termini tecnici esatti usati nel documento sorgente, non parafrasare la terminologia specialistica."

3. **Contenuto marcato `Enfasi docente` è obbligatoriamente incluso**, senza eccezioni.

4. **Nessuna informazione aggiunta.** Il prompt deve specificare: "usa esclusivamente informazioni presenti nel documento sorgente. Non aggiungere spiegazioni, contesto o dettagli non presenti nell'originale."

5. **Formato output differenziato per materia:**

**Anatomia / Istologia:** struttura descrittivo parallelo + bullet riepilogo (il formato definito nel sample della spalla). Per ogni blocco tematico:
   - Descrittivo: prosa compatta con le informazioni chiave, spazio per integrazioni future dal manuale
   - Bullet riepilogo: dati fattuali compressi (origine/inserzione/innervazione per muscoli, tipo/superfici/movimenti per articolazioni)
   - Tabelle aggregate a fine documento

**Biochimica:** struttura più concept-driven. Per ogni blocco tematico:
   - Concetto chiave in 1-2 frasi
   - Meccanismo o logica sottostante
   - Esempi biologici / correlazioni cliniche
   - Tabelle aggregate a fine documento (aminoacidi, interazioni, vie metaboliche)

6. **Il documento compatto deve essere in formato Obsidian** (stesse convenzioni della Modifica 1).

### Input/Output
- **Input:** sbobina completa (archivio) in markdown
- **Output:** documento di studio compatto in markdown Obsidian-native
- **API:** stessa usata per il primo passaggio (DeepSeek V3 o equivalente)
- **Costo stimato:** trascurabile — una seconda chiamata API per lezione

### Validazione
L'utente prende note a mano durante le lezioni (concetti chiave, cose nuove/controintuitive). Queste note servono come checklist di validazione: ogni punto annotato deve essere coperto nel documento compatto. Se manca qualcosa, si torna all'archivio.

---

## Modifica 3: Generazione flashcard Anki via AnkiConnect

### Problema
Le flashcard non sono ancora generate automaticamente. Il flusso era stato definito concettualmente ma non implementato.

### Architettura

```
Sbobina (archivio)
    └─> Appendice tabellare
            └─> Passaggio LLM: genera JSON flashcard
                    └─> Script Python: invia a AnkiConnect
```

### Fonte delle card
Le flashcard si generano dalle **tabelle** nelle sbobine (appendice tabellare), NON dal testo descrittivo. Le tabelle sono strutturate, fattuali e complete — il formato ideale per card.

Per anatomia: tabelle muscoli (origine/inserzione/azione/innervazione), tabelle articolazioni, tabelle legamenti.
Per biochimica: tabella aminoacidi, tabelle interazioni, tabelle vie metaboliche.
Per istologia: tabelle tessuti, tabelle strutture.

### Formato JSON intermedio
L'LLM riceve la tabella e produce un JSON array di card:

```json
[
  {
    "front": "Qual è l'origine del muscolo sovraspinato?",
    "back": "Fossa sovraspinata della scapola",
    "tags": ["anatomia", "locomotore", "spalla", "muscoli", "cuffia-rotatori"],
    "image": "netter_234_cuffia_rotatori.jpg"
  }
]
```

Il campo `image` è opzionale e presente solo quando disponibile (vedi Modifica 4).

### Tipi di card da generare
- **Card fattuali dirette:** "Qual è l'innervazione del deltoide?" → "Nervo ascellare (C5-C6)"
- **Card di confronto:** "Qual è la differenza tra LGOI fascio anteriore e posteriore?" (quando la tabella contiene strutture confrontabili)
- **Card di ragionamento (solo biochimica):** "Perché l'istidina è utile nei sistemi tampone?" → "Il suo pKa (~6.0) è vicino al pH fisiologico (7.4), rendendola sensibile a piccole fluttuazioni di pH"

Il prompt per la generazione delle card deve specificare il tipo di card appropriate per materia.

### Script AnkiConnect
Script Python che:
1. Legge il JSON generato dall'LLM
2. Per ogni card, chiama AnkiConnect API (`addNote`) con:
   - `deckName`: organizzato per materia/argomento (es. "Medicina::Anatomia::Locomotore::Spalla")
   - `modelName`: "Basic" per card standard, da valutare "Image Occlusion" per card con immagini anatomiche
   - `fields`: front, back
   - `tags`: dal JSON
   - Se presente `image`: copia il file nella media folder di Anki e include `<img src="...">` nel campo back
3. AnkiConnect deve essere in esecuzione (Anki aperto con plugin AnkiConnect installato)

### Organizzazione deck
Gerarchia suggerita:
```
Medicina
├── Anatomia
│   ├── Locomotore
│   │   ├── Spalla
│   │   ├── Gomito
│   │   └── ...
│   ├── Splancnologia
│   └── ...
├── Biochimica
│   ├── Aminoacidi
│   ├── Proteine
│   ├── Vie Metaboliche
│   └── ...
└── Istologia
    └── ...
```

I tag nel JSON servono per cross-referencing (es. filtrare tutte le card sulla "cuffia dei rotatori" indipendentemente dal deck).

---

## Modifica 4: Gestione immagini da testi di riferimento

### Problema
Le immagini nelle flashcard e nelle sbobine dovrebbero provenire dai testi di riferimento (Netter Atlas per anatomia, Lehninger per biochimica). Non è stato ancora implementato nessun workflow.

### Workflow proposto

**Step 1 — Creazione libreria immagini (una tantum per testo)**
- Fotografare/scansionare le tavole rilevanti dal Netter e altri testi
- Naming convention sistematico: `{fonte}_{pagina}_{argomento}.jpg`
  - Es: `netter_234_cuffia_rotatori.jpg`, `lehninger_75_struttura_aminoacidi.png`
- Salvare in una cartella centralizzata accessibile sia dalla pipeline che da Obsidian e Anki

**Step 2 — File di mapping argomento→immagine**
Creare un file JSON/CSV di corrispondenza:
```json
{
  "cuffia dei rotatori": ["netter_234_cuffia_rotatori.jpg"],
  "plesso brachiale": ["netter_418_plesso_brachiale.jpg", "netter_419_plesso_brachiale_rami.jpg"],
  "glicina struttura": ["lehninger_75_aminoacidi.png"]
}
```

Questo file viene passato all'LLM durante la generazione delle flashcard. Quando l'LLM genera una card su un argomento presente nel mapping, include il riferimento all'immagine.

**Step 3 — Integrazione con Anki**
Lo script AnkiConnect, quando incontra un campo `image` nel JSON delle card, copia il file dalla libreria alla media folder di Anki (`~/.local/share/Anki2/User/collection.media/` su Mac) e formatta il campo back con `<img src="filename.jpg">`.

**Step 4 — Integrazione con Obsidian**
La libreria immagini può vivere come cartella nella vault Obsidian. Le sbobine in formato Obsidian possono referenziare le immagini con `![[netter_234_cuffia_rotatori.jpg]]`.

### Note
- Questo è il componente con più lavoro manuale (la scansione/fotografia). Il costo è concentrato nella fase iniziale di setup.
- Le strutture molecolari SVG che la pipeline già genera per biochimica sono un caso separato: vengono prodotte automaticamente e non richiedono scansione manuale.
- Per le Image Occlusion card (anatomia), servono immagini di qualità sufficiente. Valutare la qualità delle foto da telefono vs scanner.

---

## Priorità di implementazione suggerite

1. **Modifica 1 (Obsidian format)** — sblocca tutto il resto, è prerequisito per poter consumare le sbobine
2. **Modifica 2 (Documento compatto)** — impatto diretto sulla qualità dello studio
3. **Modifica 3 (Anki/AnkiConnect)** — flashcard dalla pipeline
4. **Modifica 4 (Immagini)** — enhancement, può procedere in parallelo come setup incrementale


---

## Riferimenti

- Sbobina sample anatomia (spalla) con formato descrittivo parallelo + bullet: generata in conversazione precedente
- Sbobina reale anatomia lezione 1 e biochimica lezione 1: fornite dall'utente come esempio del formato attuale
- AnkiConnect API: https://foosoft.net/projects/anki-connect/
- Obsidian: https://obsidian.md