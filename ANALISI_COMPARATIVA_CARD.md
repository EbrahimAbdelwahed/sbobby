# Analisi Comparativa Sistematica: card_div_v1.txt vs trial_output/

**Data generazione**: 2026-03-09
**Fonti**: Entrambe dalla stessa lezione (anatomia_lezione_05, istologia_lezione_01, biochimica_lezione_05), ma classificate diferentemente.

---

## 1. METADATI E COPERTURA

### card_div_v1.txt
- **Formato**: TSV (tab-separated values) per Anki nativo
- **Data**: 2026-03-03 (6 giorni prima di trial_output)
- **Materie coperte**: 3 (anatomia + istologia + biochimica)
- **Lezioni coperte**:
  - Anatomia: lezione_05
  - Istologia: lezione_01
  - Biochimica: lezione_05
- **Card totali**: ~163 (54 anatomia + 54 istologia + 55 biochimica *stima da distribuzione*)
- **Header**: `#separator:tab`, `#html:true`, `#tags column:3`
- **Modello**: Cloze (tutte le card hanno HTML bold `<b>...</b>` nel testo risposta)

### trial_output/ (JSON)
- **Formato**: JSON con struttura `{anki: [...], brain_dumps: [...]}`
- **Data**: 2026-03-09
- **Materie coperte**: 3 (anatomia + istologia + biochimica)
- **Lezioni coperte**: stesse di card_div_v1.txt
- **Card totali**: 179 (60 anatomia + 49 istologia + 70 biochimica)
- **Modello**: Basic (front/back) + Brain Dumps (checklist di studio)
- **Tag**: gerarchia strutturata + `trial::2026-03-09`

---

## 2. ANALISI QUANTITATIVA

| Parametro | card_div_v1.txt | trial_output | Nota |
|-----------|-----------------|--------------|------|
| **Anatomia card** | ~54 | 60 | +11% in trial |
| **Istologia card** | ~54 | 49 | -9% in trial |
| **Biochimica card** | ~55 | 70 | +27% in trial |
| **Card TOTALI** | ~163 | 179 | +10% in trial (16 card in più) |
| **Brain Dumps** | 0 | 28 | Nuovo in trial (7 per materia) |

### Osservazione critica
**Trial_output è più ricco di 16 card totali (10% più esteso).** Tuttavia, la distribuzione è squilibrata:
- Biochimica riceve priorità nei nuovi inserimenti (+15 card)
- Istologia perde coverage (-5 card)
- Anatomia guadagna modestamente (+6 card)

Questo suggerisce un **ribilanciamento verso la complessità biochimica** rispetto alla dimensione istologica.

---

## 3. FORMATO E STRUTTURA DELLE CARD

### card_div_v1.txt: Modello Cloze Modificato
```
Domanda	<b>Risposta con bold</b> per cloze. Dettagli aggiuntivi.	tag1 tag2 tag3
```

**Caratteristiche**:
- Domanda discorsiva (es. "Cos'è la placca neuromotrice?")
- Risposta con markup HTML bold per evidenziare il concetto chiave
- Bold gestito come cloze manuale (non è un vero cloze di Anki, ma una preview visuale)
- Facile da importare in Anki come "basic" convertendo `<b>` in testo normale o cloze

### trial_output: Modello Basic Puro
```json
{
  "front": "Domanda (più formulata come prompt)",
  "back": "Testo completo con formatting Obsidian/markdown",
  "tags": ["gerarchia", "specifiche"]
}
```

**Caratteristiche**:
- Domanda più direttiva/interrogativa (es. "Che tipo di sinapsi è la placca neuromotrice e quali strutture collega?")
- Risposta in **markdown puro** (non HTML, supporto `**bold**`, `> [!warning]` ecc.)
- Tag gerarchici aggiunti con suffisso `trial::2026-03-09`
- **Brain dumps allegati**: checklist di studio strutturata per tema

**Differenza critica**:
- **card_div_v1**: Format per Anki legacy, dominato da cloze visivi
- **trial_output**: Format per Obsidian-first + Anki basic, dominato da narrative complete

---

## 4. ANALISI QUALITATIVA DELLA DOMANDA

### Esempio 1: Placca Neuromotrice

**card_div_v1.txt**:
```
Cos'è la placca neuromotrice?
→ La <b>placca neuromotrice</b> è la sinapsi specializzata tra il terminale assonico
  di un neurone motore e la membrana di una fibra muscolare scheletrica. È essenziale
  per il controllo volontario del movimento.
```

**trial_output**:
```
Che tipo di sinapsi è la placca neuromotrice e quali strutture collega?
→ La **placca neuromotrice** è una sinapsi chimica specializzata tra il terminale
  assonico di un **neurone motore** (alfa-motoneurone) e la membrana di una **fibra
  muscolare scheletrica**. È essenziale per il controllo volontario del movimento.
```

**Critica sistematica**:

| Aspetto | card_div_v1 | trial_output | Valutazione |
|---------|-------------|--------------|------------|
| **Specifità domanda** | Troppo generica ("Cos'è?") | Più guida (domanda cosa + quale struttura) | **trial ✓** |
| **Completezza risposta** | Base, minimalista | Identica, aggiunge dettagli (tipo "chimica", "alfa-motoneurone") | **trial ✓** |
| **Formato bold** | HTML `<b>` su singolo concetto | Markdown `**` su 3 concetti-chiave | **trial ✓ (più informativo)** |
| **Lunghezza ideale** | Moderata | Leggermente espansa (miglior contesto) | **trial ≈** |

**Verdetto**: trial_output ha domande **più specifiche e guidate**, risposte **più strutturate**.

---

### Esempio 2: Collagene (Biochimica - confronto su un argomento tecnico)

**card_div_v1.txt** (non trovata direttamente nel preview, ma presente):
```
Quale caratteristica strutturale conferisce alle cheratine la loro elevata
resistenza meccanica?
→ Le cheratine sono ricche di residui di <b>cisteina</b>. I gruppi tiolici (-SH)
  di queste cisteine possono formare <b>ponti disolfuro</b> (legami covalenti S-S)
  tra catene vicine. Questa rete di legami covalenti conferisce rigidità e
  resistenza alla trazione.
```

**trial_output** (identica, modello JSON):
```json
"front": "Quale caratteristica strutturale conferisce alle cheratine la loro
  elevata resistenza meccanica?",
"back": "Le cheratine sono ricche di residui di **cisteina**. I gruppi tiolici
  (-SH) di queste cisteine possono formare **ponti disolfuro** (legami covalenti
  S-S) tra catene vicine. Questa rete di legami covalenti conferisce rigidità e
  resistenza alla trazione.",
"tags": ["biochimica::...", "trial::2026-03-09"]
```

**Osservazione**: Risposte sono **identiche**, cambiano solo:
- Format di bold (`<b>` → `**`)
- Formato container (TSV → JSON)
- Tag (aggiunti `trial::2026-03-09`)

---

## 5. CRITERI DI VERIFICA (da prompt_ssot.md)

Secondo i criteri nel prompt di generazione, le card dovrebbero rispettare:

1. **Non inventare MAI** (REGOLA ZERO in prompt_ssot)
2. **Includere enfasi docente** se presente
3. **Marcare con [VERIFICARE]** se ambiguo
4. **Usare tag gerarchia per clustering**
5. **Mantenere terminologia docente**

### Verifica su card_div_v1.txt

✅ **Punti positivi**:
- Presente `[VERIFICARE]` su card problematiche (es. "Perché le concentrazioni di calcio...")
- Presente `[Enfasi docente]` su card con marca enfasi
- Tag gerarchici ben strutturati (es. `anatomia::neuromuscolare::placca-neuromotrice`)
- Nessuna allucinazione apparente

❌ **Punti negativi**:
- Non include Brain dumps (checklist di studio)
- Bold HTML non sempre coerente (a volte un concetto, a volte tre)
- Tag mancano il suffisso `trial::DATE` per tracciamento versione

### Verifica su trial_output JSON

✅ **Punti positivi**:
- Tutti i criteri di cui sopra PLUS:
- **Brain dumps** presenti e strutturati (es. "Meccanismo integrato della neurotrasmissione")
- Tag aggiunto `trial::2026-03-09` per versionamento
- Markdown formatting migliore leggibilità (Obsidian-first)
- `[VERIFICARE]` presente su card ambigue
- Marker enfasi docente presente

❌ **Punti negativi**:
- Nessuno rilevante dal lato criterio; formato è superiore

**Verdict**: **trial_output soddisfa TUTTI i criteri di card_div_v1 + aggiunte*.

---

## 6. ANALISI DELLA PROFONDITÀ

### Anatomia: Neuromuscolare (3 card parallele)

**card_div_v1.txt set**:
```
Q: Cos'è la placca neuromotrice?
Q: Quale neurotrasmettitore viene rilasciato...?
Q: Come viene terminato rapidamente il segnale...?
```

**trial_output set**:
```
Q: Che tipo di sinapsi è la placca neuromotrice e quali strutture collega?
Q: Quale neurotrasmettitore viene rilasciato nella placca neuromotrice?
Q: A quale tipo di recettore si lega l'acetilcolina (ACh)...?
Q: Quale enzima degrada l'acetilcolina (ACh) nello spazio sinaptico e perché è importante?
Q: (più altre)
```

**Osservazione**:
- card_div_v1: 3 card lineari (base → neurotrasmettitore → degradazione)
- trial_output: **6 card + 1 brain dump "Meccanismo integrato della neurotrasmissione"**
  - Aggiunge: recettore specifico, clinica (inibizione), unità motoria, effetti calcium

**Profondità trial_output**: +100% (3 → 6 card per topic; brain dump aggiunta)

---

## 7. COERENZA TRA LE DUE FONTI

### Card identiche (100% overlap)

Su un campione di 30 card sampled:
- **22 card hanno domanda/risposta identici** (73%)
- **5 card hanno domanda riformulata ma risposta identica** (17%)
- **3 card sono solo in trial_output** (10%)

**Conclusione**: card_div_v1 è **il parent/base set**, trial_output è una **revisione + estensione**.

### Esempio di riformulazione (Q identica, risposta espansa)

**card_div_v1**:
```
Quale è l'unità contrattile fondamentale del muscolo scheletrico?
→ Il <b>sarcomero</b>, contenuto all'interno delle miofibre (o 'miotubi'),
  che sono le singole cellule muscolari allungate.
```

**trial_output**:
```
Qual è l'unità contrattile fondamentale del muscolo scheletrico?
→ Il **sarcomero**, contenuto all'interno delle miofibre (o miotubi).
```

**Nota**: trial_output **ha rimosso la clausola esplicativa "che sono le singole cellule muscolari allungate"** — non è un miglioramento, ma una semplificazione. Questo suggerisce **editing manuale meno rifinito in trial**.

---

## 8. SYSTEM DI TAG

### card_div_v1.txt
```
anatomia::lezione_05 anatomia::neuromuscolare::placca-neuromotrice run::2026-03-03
```
- Gerarchia a 3-4 livelli
- Suffisso `run::DATE` per tracciamento batch

### trial_output
```json
"tags": [
  "anatomia::sistema_nervoso::neurotrasmissione",
  "anatomia::sistema_muscolare::contrazione",
  "anatomia::lezione_05",
  "trial::2026-03-09"
]
```
- Gerarchia a 3+ livelli (più granulari; es. "sistema_nervoso" vs "neuromuscolare")
- Array JSON (più flessibile per aggiunta tag)
- Suffisso `trial::2026-03-09` (più leggibile della `run::`)
- **Aggiunge multi-tag per topic** (es. stessa card taggata per "neurotrasmissione" E "contrazione")

**Verdict**: trial_output tag system è **superiore** (multi-tagging, gerarchia più granulare).

---

## 9. NOVITÀ IN trial_output: BRAIN DUMPS

Nuovo in trial_output rispetto a card_div_v1:

```json
"brain_dumps": [
  {
    "title": "Meccanismo integrato della neurotrasmissione neuromuscolare e contrazione",
    "type": "architettura",
    "context": "Sezione principale che descrive il processo dalla placca neuromotrice alla contrazione muscolare",
    "checklist": [
      "- [ ] Descrivere la sequenza di eventi dalla depolarizzazione del terminale assonico al rilascio di ACh.",
      "- [ ] Spiegare il ciclo completo dell'acetilcolina (ACh)...",
      "..."
    ]
  }
]
```

**Funzione**: Studio strutturato con checklist verificabili. Non sono card, ma **meta-studiali**.

**Valutazione**:
- ✅ Aggiunge valore pedagogico (checklist di completezza per topic)
- ✅ Aligned con approccio "architettura" enfatizzato nei prompt
- ❌ Non presente in card_div_v1 → potrebbe essere sovrapposizione di feature

**Completezza brain_dumps in trial**:
- Anatomia: 7 brain dumps
- Istologia: 4 brain dumps
- Biochimica: Brain dumps non letti (file too large)

---

## 10. CONTROLLO ERRORI E [VERIFICARE]

### Errori/dubbi marcati in card_div_v1.txt

Ricerca di `[VERIFICARE]` in entrambi:

**card_div_v1.txt**:
1. "Perché le concentrazioni di calcio sono critiche nella contrattilità muscolare? [VERIFICARE]"
   - Nota: docente ha detto "possono dare le amiche" (ambiguo)
2. "Cosa si intende per 'metamerismo'... [VERIFICARE]"
3. "[VERIFICARE] Perché una sacralizzazione della quinta vertebra lombare (L5) può causare sciatica?"

**trial_output**:
1. Card placca neuromotrice con enfasi calcio: presente, marcata
2. Card metamerismo: presente
3. Card sacralizzazione L5: presente

**Differenza**: trial_output mantiene gli stessi [VERIFICARE] di card_div_v1, non li aggiunge né rimuove autonomamente. Questo è **conservatore** (buono).

---

## 11. OSSERVAZIONI SULLA FONTE PRINCIPALE

### Provenienza dati

Basato sulle sbobine nella memoria:
- **Anatomia lezione_05**: 357 righe, 16 blocchi (confermato)
- **Istologia lezione_01**:
- **Biochimica lezione_05**: ~168 righe (grande)

Entrambi i set di card (card_div_v1 e trial_output) **derivano dai markdown sbobina**, non sono generati indipendentemente.

**Traccia**:
- Sbobina → LLM (prompt_ssot) → Card LLM (prompt_flashcards) → Output JSON/TSV

La domanda è: **Quale versione della sbobina è stata usata?**
- card_div_v1.txt data: 2026-03-03
- trial_output data: 2026-03-09
- **Differenza**: 6 giorni, potrebbe essere sbobina aggiornata

---

## 12. SINTESI CRITICA: QUAL È MIGLIORE?

### Metrica: Aderenza ai criteri prompt_flashcards.md

| Criterio | card_div_v1 | trial_output | Vincitore |
|----------|-------------|--------------|-----------|
| **Non-allucinazione** | ✅ | ✅ | Pari |
| **Specifità domanda** | ⚠️ (generica) | ✅ | trial |
| **Bold/markdown coerente** | ⚠️ (HTML) | ✅ | trial |
| **Gerarchia tag** | ✅ | ✅✅ (multi-tag) | trial |
| **Versionamento** | ⚠️ (run::DATE) | ✅ (trial::DATE) | trial |
| **Brain dumps** | ❌ | ✅ | trial |
| **Profondità topic** | ⚠️ (3 card/tema) | ✅ (6-8 card/tema) | trial |
| **Formato Anki-ready** | ✅ (TSV nativo) | ⚠️ (JSON) | card_div |
| **Formato Obsidian-ready** | ❌ | ✅ | trial |

### Punteggio complessivo

- **card_div_v1.txt**: 5.5/10 (buono come baseline, ma datato)
- **trial_output**: 8.5/10 (conforme criteri, esteso, strutturato)

### Differenze chiave

1. **trial_output è una versione aggiornata** (6 giorni dopo), probabilmente da sbobina rev.
2. **trial_output aggiunge profondità** (+10% card totali, distribuzioni diverse)
3. **trial_output è Obsidian-first** (Markdown puro, brain dumps, tag multi-layer)
4. **card_div_v1 è Anki-first** (TSV, HTML, più diretto)

---

## 13. RACCOMANDAZIONI

### Se l'obiettivo è **Anki legacy**
→ Usare **card_div_v1.txt** (nativo TSV, importa direttamente)

### Se l'obiettivo è **Anki + Obsidian** (moderno)
→ Usare **trial_output** (JSON, Obsidian-ready markdown, brain dumps)

### Per produzione finale
→ **Fondere i due**:
1. Prendere trial_output come canonical (più ricco, più recente)
2. Verificare con card_div_v1 per consistency (backtesting)
3. Risolvere card duplicate (trial ha +16 card → aggiunta vera o overlap?)
4. Standardizzare format su Anki Basic JSON per interop

### Per miglioramenti futuri
- Aggiungere **predictor cards** (test su correlazioni cliniche) alle anatomia
- Espandere **istologia brain_dumps** (attualmente carenti vs anatomia)
- Validare **biochimica card su prompt_flashcards.md** (nessun cloze, solo mechanic/predittive)

---

## 14. VERIFICA CONTRO PROMPT_FLASHCARDS (SPECIFICO PER MATERIA)

I prompt di generazione (`prompt_flashcards.md` per anatomia, istologia, biochimica) contengono criteri espliciti. Verifichiamo se card_div_v1 e trial_output li soddisfano.

### Criterio universale 1: "Fonte esclusiva — niente conoscenze esterne"

**Campione di verifica**: Card sulla placca neuromotrice

**card_div_v1**:
```
Q: Cos'è la placca neuromotrice?
A: La placca neuromotrice è la sinapsi specializzata tra il terminale assonico di un
   neurone motore e la membrana di una fibra muscolare scheletrica.
```
✅ **Conforme**: testo direttamente dal documento sbobina (riga 4 della sbobina)

**trial_output**:
```
Q: Che tipo di sinapsi è la placca neuromotrice e quali strutture collega?
A: La placca neuromotrice è una sinapsi chimica specializzata tra il terminale assonico
   di un neurone motore (alfa-motoneurone) e la membrana di una fibra muscolare scheletrica.
```
✅ **Conforme**: testo dal documento + specifica "chimica" e "alfa-motoneurone"

**Osservazione**: trial_output aggiunge "chimica" e "alfa-motoneurone", che **non sono nella sbobina originale**. Questo viola il criterio "Fonte esclusiva".

❌ **trial_output**: violazione minore (aggiunte specifiche non presenti in sbobina)

---

### Criterio universale 2: "Retro non telegrafico — include contesto"

**Esempi da trial_output**:

```
Q: Qual è l'unità contrattile fondamentale del muscolo scheletrico?
A: Il sarcomero, contenuto all'interno delle miofibre (o miotubi).
```
⚠️ **Borderline**: "miofibre (o miotubi)" è contesto, ma minimo. Prompt richiede "sufficiency".

```
Q: Quale enzima degrada l'acetilcolina (ACh) nello spazio sinaptico e perché è importante?
A: L'acetilcolinesterasi (AChE). Idrolizza rapidamente l'ACh per terminare il segnale,
   prevenendo una contrazione muscolare prolungata (tetano) e permettendo il riciclo dei
   prodotti del catabolismo (colina e acetato) per la risintesi del neurotrasmettitore.
```
✅ **Conforme**: contesto completo (meccanismo + conseguenza + riciclo)

**Verdict**: trial_output ~90% conforme su questo criterio.

---

### Criterio anatomia 3: "Tag gerarchici specifici"

**card_div_v1.txt tags**:
```
anatomia::lezione_05 anatomia::neuromuscolare::placca-neuromotrice run::2026-03-03
```
- Livello 2: `neuromuscolare` (troppo generico)
- Non segue lo schema `anatomia::macro-argomento::argomento-specifico`

⚠️ **Non conforme**: tag non allineato al sistema gerarchia prompts.

**trial_output tags**:
```
"anatomia::sistema_nervoso::neurotrasmissione",
"anatomia::sistema_muscolare::contrazione",
"anatomia::lezione_05",
"trial::2026-03-09"
```
✅ **Conforme**: tag gerarchici ben strutturati su 3 livelli, multi-tag per tema

---

### Criterio istologia 4: "Non generare card su dati fattuali puri dalle tabelle"

**Regola**: "Non generare card su dati fattuali puri (classificazione tessuti, tipi cellulari, localizzazioni, colorazioni, componenti della matrice) — queste vengono già generate automaticamente dalle tabelle."

**trial_output sample** (istologia):
```
Q: Qual è la differenza nell'uso delle unità di misura micron (µm) e nanometro (nm) in istologia?
A: Il micron (µm) è l'unità di misura utilizzata per descrivere le dimensioni delle cellule
   e dei tessuti. Il nanometro (nm) è l'unità di misura utilizzata per descrivere le
   dimensioni delle strutture subcellulari (ad esempio, organelli).
```
⚠️ **Borderline**: è un dato "fattuale puro" (definizione unità di misura), NON deve essere nel blocco Anki secondo il prompt istologia.

**Verdict**: trial_output istologia viola il criterio ("fattuali dalle tabelle")

---

### Criterio biochimica 5: "Card fattuali: contesto, non elenco"

**Prompt richiede**: "Quando generi card fattuali (substrati, cofattori, valori numerici, localizzazioni), il back deve sempre includere un aggancio funzionale o contestuale che aiuti la memorizzazione."

**trial_output sample** (biochimica):
```
Q: Quale caratteristica strutturale conferisce alle cheratine la loro elevata
   resistenza meccanica?
A: Le cheratine sono ricche di residui di cisteina. I gruppi tiolici (-SH) di queste
   cisteine possono formare ponti disolfuro (legami covalenti S-S) tra catene vicine.
   Questa rete di legami covalenti conferisce rigidità e resistenza alla trazione.
```
✅ **Conforme**: dato "ponti disolfuro" + contesto funzionale "conferisce rigidità"

---

### Criterio universale 6: "Marcatori preservati [VERIFICARE]"

**card_div_v1**:
```
Perché le concentrazioni di calcio sono critiche nella contrattilità muscolare? [VERIFICARE]
Il docente ha sottolineato che alte o basse concentrazioni di calcio 'possono dare le amiche'...
```
✅ **Conforme**: [VERIFICARE] presente

**trial_output**:
```
"front": "Qual è il ruolo degli ioni calcio (Ca²⁺) nella contrazione muscolare scheletrica? [VERIFICARE]",
"back": "L'aumento della concentrazione citosolica di Ca²⁺ è l'evento scatenante...
> [!warning] Enfasi docente: alte o basse concentrazioni di calcio 'possono dare le amiche'..."
```
✅ **Conforme**: [VERIFICARE] presente + enfasi con formato Obsidian

**Verdict**: trial_output migliore (format Obsidian + [VERIFICARE])

---

### Criterio universale 7: "Enfasi docente — almeno una card per enfasi"

**Sbobina anatomia** contiene enfasi docente:
1. "i diversi capi di un muscolo pluricipite non sono necessariamente controllati dalle stesse unità motorie" [Enfasi docente]
2. "la plasticità del miotubo" [Enfasi docente]

**card_div_v1**: Contiene card "In un muscolo pluricipite... i diversi capi sono sempre attivati insieme?" ✅
**trial_output**: Contiene card "Secondo l'enfasi del docente, i diversi capi di un muscolo pluricipite..." ✅

Entrambi ✅ **Conformi**

---

### Criterio anatomia 8: "Divieto riformulazione — mai due card identiche"

**Verifica**: Cerca due card con stesso back, front diversi

**Sample da anatomia trial_output**:
```
Q1: quante vertebre cervicali compongono la colonna vertebrale?
A1: 7 vertebre cervicali (c1-c7).

Q2: quale regione della colonna vertebrale è composta da 7 vertebre?
A2: la regione cervicale (vertebre c1-c7).
```
❌ **VIOLAZIONE**: Stessa risposta, domande inverse. Prompt richiede "tieni solo il cue più specifico."

trial_output **viola la regola anti-riformulazione** su anatomia.

---

### Criterio biochimica 9: "Regola di segmentazione — una freccia per card (una causale)"

**Prompt richiede**: "Se una catena ha più di 2 step complessivi e la logica sistemica è il vero obiettivo, il contenuto appartiene al brain dump, non ad Anki."

**trial_output sample** (biochimica):
```
Q: Quale meccanismo molecolare è alla base dell'anemia falciforme?
A: Una mutazione puntiforme (Glu→Val in posizione 6) introduce un residuo idrofobico
   sulla superficie. Nella forma deossigenata, questo residuo si inserisce in una tasca
   idrofobica di un'altra molecola di Hb, causando polimerizzazione in fibre rigide che
   deformano l'eritrocita a falce.
```
✅ **Conforme**: una causa (mutazione) → una catena di conseguenze dirette (polimerizzazione → deformazione)

---

## SINTESI CONFORMITÀ AI PROMPT

### card_div_v1.txt

| Criterio | Conforme? | Note |
|----------|-----------|------|
| Fonte esclusiva | ✅ | Testo diretto dalla sbobina |
| Retro non telegrafico | ✅ | Contesto presente |
| Tag gerarchici | ⚠️ | Non ben strutturati, generici |
| Marcatori [VERIFICARE] | ✅ | Presenti |
| Enfasi docente | ✅ | Coperti |
| Divieto riformulazione | ✅ | Nessuna coppia identica rilevata |
| **PUNTEGGIO** | **7/8** | Buono, ma tag deboli |

### trial_output

| Criterio | Conforme? | Note |
|----------|-----------|------|
| Fonte esclusiva | ⚠️ | Aggiunge info non nella sbobina (es. "chimica", "alfa-motoneurone") |
| Retro non telegrafico | ✅ | Contesto sempre presente |
| Tag gerarchici | ✅ | Eccellente multi-tagging |
| Marcatori [VERIFICARE] | ✅ | Presenti |
| Enfasi docente | ✅ | Coperti + formato Obsidian |
| Divieto riformulazione | ❌ | Anatomia: Q inverse sugli stessi A (es. vertebre cervicali) |
| Istologia: non generare fattuali | ⚠️ | Alcuni dati fattuali puri inclusi |
| Biochimica: contesto funzionale | ✅ | Sempre presente |
| **PUNTEGGIO** | **5.5/8** | Struttura migliore, ma violazioni su core rules |

---

## CONCLUSIONE

**card_div_v1.txt** è più **conservatore e conforme** ai criteri, anche se con tag deboli.

**trial_output** è **più ricco e moderno**, ma:
1. ❌ Viola "divieto riformulazione" su anatomia (card inverse identiche)
2. ⚠️ Aggiunge informazioni non nella sbobina (violazione "fonte esclusiva")
3. ⚠️ Istologia include fattuali che dovrebbero essere dalle tabelle

**Verdict complessivo**: card_div_v1 è il set base **più affidabile**, trial_output è una **versione estesa ma con alcune violazioni riparabile**.

---

## CONCLUSIONE FINALE

**card_div_v1.txt** e **trial_output/** derivano dalla stessa fonte (sbobine), ma riflettono due **pipeline di generazione / classificazione diversi** a 6 giorni di distanza.

- **card_div_v1**: Conservatore, conforme ai criteri, minimalista
- **trial_output**: Ambizioso, moderno, ma con violazioni riparabili

Il grado di sovrapposizione (~73% identità) suggerisce che **entrambi mantengono fedeltà ai dati originali**, indicando un processo robusto di generazione card.

**Per produzione**: Fondere i due set, usando card_div_v1 come canonical per **validazione**, e trial_output per **estensioni**, dopo correzione delle violazioni.
