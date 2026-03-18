# Prompt Biochimica — Generazione Flashcard Anki (v4)

---

## Formato output

Restituisci un oggetto JSON con due campi:

```json
{
  "anki": [
    {
      "front": "Testo della domanda",
      "back": "Testo della risposta con contesto sufficiente",
      "tags": ["biochimica::macro-argomento::argomento-specifico"]
    }
  ],
  "brain_dumps": [
    {
      "title": "Titolo del topic",
      "type": "via_metabolica|regolazione|logica_causale",
      "context": "Da quale parte della lezione viene questo topic",
      "checklist": ["- [ ] punto chiave 1", "- [ ] punto chiave 2"]
    }
  ]
}
```

---

## REGOLA FONDAMENTALE: Anki e brain dump sono canali sostitutivi, non additivi

Per ogni topic della sezione, **scegli uno solo**:

- **→ Anki**: il topic produce solo fatti puntuali e autonomi → genera card, nessun brain dump su quel topic
- **→ Brain dump**: il topic richiede di ricostruire una rete → genera UN brain dump con checklist, e al massimo 1-2 card Anki sullo stesso topic (solo per fatti completamente isolati, es. un cofattore specifico o un valore di Km che non dipende dalla rete)

**Il brain dump non è un'aggiunta alle card. È un'alternativa che le sostituisce.**

### Esempio SBAGLIATO (additivo — da evitare):
- Card: "Quali enzimi regolano la PFK-1?" → citrato, ATP (inibitori), AMP, fruttosio-2,6-P (attivatori)
- Card: "Come l'AMP attiva la PFK-1?" (step della regolazione)
- Card: "Cosa succede alla glicolisi se il citrato aumenta?" (conseguenza)
- Brain dump: "Regolazione allosterica della PFK-1" (contiene gli stessi step)

→ SBAGLIATO: le card replicano il brain dump. Se esiste il brain dump, quelle card non ci sono.

**Esempio additivo per via metabolica (errore frequente):**
- Card: "Quali sono gli step della sintesi del collagene nel RER?" → sequenza di 5 modifiche
- Card: "Perché la Pro4 viene idrossilata nel collagene?" → per formare legami H intramolecolari stabilizzanti
- Card: "Cosa succede se la vitamina C manca nella sintesi del collagene?" → scorbuto
- Brain dump: "Sintesi collagene: sequenza di modifiche post-traduzionali" (copre l'intera rete causale)

→ SBAGLIATO: le card testano la sequenza e la logica causale — già coperti dal brain dump.

### Esempio CORRETTO (sostitutivo):
- Card: "Qual è il Km della PFK-1 per il fruttosio-6-fosfato?" *(valore numerico isolato — Anki)*
- Card: "Quale tipo di inibizione esercita il citrato sulla PFK-1?" *(fatto puntuale — Anki)*
- Brain dump: "Regolazione allosterica della PFK-1: integratori energetici e logica" *(la rete — nessuna card sulla logica della regolazione)*

→ CORRETTO: dati isolati in Anki, logica di regolazione nel brain dump.

**Esempio corretto per via metabolica:**
- Card: "Quanti tipi di collagene esistono?" *(numero isolato — Anki)*
- Card: "Quale enzima catalizza l'idrossilazione Pro4 nel procollagene?" *(nome specifico — Anki)*
- Card: "Quale ione metallico è cofattore della prolil-4-idrossilasi?" *(dato isolato — Anki)*
- Brain dump: "Sintesi collagene: sequenza di modifiche post-traduzionali" *(copre la logica d'insieme — nessuna card sulla sequenza o sul perché delle modifiche)*

→ CORRETTO: i nomi e i dati specifici stanno in Anki; la logica sequenziale e il perché stanno nel brain dump. La sovrapposizione è legittima quando le funzioni cognitive sono diverse (recall isolato del dato in Anki, uso del dato come nodo in una sequenza nel brain dump) — illegittima quando la checklist ripete esattamente la domanda della card senza aggiungere contesto relazionale.

### Discriminante card Anki vs brain dump per step di una via

Quando una via metabolica ha un brain dump, le card Anki ammesse sullo stesso topic sono quelle che testano **dati specifici non derivabili dalla logica** (nome di un enzima specifico, numero di subunità, cofattore specifico, valore numerico). Non sono ammesse card che testano **la sequenza** ("quale step viene prima/dopo?"), **la logica causale** ("perché avviene X?"), o **le conseguenze** ("cosa succede se X manca?") — queste appartengono al brain dump.

Un fatto puntuale (es. il cofattore Fe²⁺ di un enzima) può apparire sia in Anki sia nella checklist del brain dump se le funzioni cognitive sono diverse: Anki testa il recupero isolato, il brain dump lo usa come elemento in una sequenza. Questa ridondanza è legittima. È illegittima solo quando la voce del brain dump ripete esattamente la domanda della card senza inserirla in una rete più ampia.

---

## Filtro conoscenza generale (CRITICO)

Prima di generare qualsiasi card, filtra il materiale con questa domanda: **uno studente di medicina al primo anno saprebbe già questa informazione senza averla studiata in modo specifico?**

Se sì, la card non si genera. Esempi di materiale da non generare:
- "L'emoglobina trasporta ossigeno"
- "L'insulina regola la glicemia"
- "Gli anticorpi difendono l'organismo"
- "Gli enzimi sono catalizzatori biologici"
- "I lipidi sono idrofobici"

Queste sono nozioni di cultura scientifica generale (liceo scientifico o anno propedeutico). **Non sono materiale da spaced repetition**. Se la sbobina le usa come contesto introduttivo o classificazione tassonomica, genera al massimo un singolo brain dump di riepilogo — non card individuali per ogni classe o esempio.

**Informazioni amministrative** (formato esame, struttura del programma, crediti, calendario) non generano né card né brain dump. Sono informazioni logistiche, non contenuto esaminabile.

---

## Principio di parsimonia estrema

Genera il **minor numero possibile** di card per coprire i fatti puntuali della sezione. Prima di aggiungere una card, chiediti: *questa informazione è davvero autonoma e non recuperabile ragionando dalla rete concettuale?* Se il dato è derivabile da un'altra card o dal brain dump, non generarlo.

Una sezione con un solo fatto puntuale produce una sola card. Una sezione interamente processuale produce zero card e un brain dump.

---

## Criterio discriminante: Anki vs brain dump

**Una card va in `anki` se il fatto sta in piedi da solo**, indipendentemente dalla rete concettuale in cui è inserito. Va nel **brain dump** se vive dentro una rete — richiede di ricostruire relazioni, meccanismi a più step, vie metaboliche, o logiche causali sistemiche.

### Va in Anki:
- Proprietà puntuali di molecole: gruppo funzionale, polarità, pKa, localizzazione cellulare
- Dati enzimi: substrato, prodotto, cofattore, tipo di inibizione, numero di subunità, Km, classe enzimatica
- Card meccanismo puntuali (es. "quale tipo di inibizione esercita il fluoruro sull'enolasi?" — risposta diretta)
- Card predittive con una sola variabile e risposta diretta (es. "cosa succede alla carica di X se il pH scende sotto il suo pKa?")
- Card di confronto puntuali tra molecole o enzimi con proprietà parzialmente sovrapponibili

### Va nel brain dump:
- **Vie metaboliche complete**: tutti gli step, intermedi, regolazione integrata, bilancio energetico
- **Meccanismi di regolazione**: regolazione allosterica integrata di più enzimi, signaling a cascata
- **Logiche causa-effetto sistemiche**: catene causali con più di 2 passaggi (es. "come il digiuno induce la gluconeogenesi?")

### Tipi di brain dump:
- `via_metabolica` — via completa con step, intermedi, regolazione, bilancio energetico
- `regolazione` — meccanismo di regolazione integrato di una via o processo
- `logica_causale` — catena causa-effetto sistemica

---

## Regole generali (blocco Anki)

1. **Fonte esclusiva — senza elaborazione.** Usa solo informazioni presenti nel documento sorgente. Non aggiungere dettagli, specificazioni o aggettivi non presenti nel testo. Parafrasa, ma non completare.

2. **Retro mai telegrafici.** Il retro deve includere contesto sufficiente per fissare il concetto. Mai una singola parola o un nome isolato. Il retro di una card meccanismo deve contenere: trigger → evento molecolare → conseguenza.

3. **Una domanda, una risposta.** Ogni card testa un singolo concetto o un singolo collegamento causale. Il fronte deve porre **una sola domanda** — mai "cosa X e perché Y" nello stesso fronte. Il retro deve rispondere solo a quella domanda — mai aggiungere il meccanismo quando il fronte chiedeva un nome, o la conseguenza clinica quando il fronte chiedeva un cofattore. Se ci sono due fatti distinti, sono due card separate.

   **Esempio di violazione**: fronte "quale enzima catalizza l'idrossilazione Pro4?" → retro che elenca enzima + cofattori (Fe²⁺, 2-ossoglutarato, O₂) + prodotti + ruolo funzionale. Il retro corretto è: "Prolil-4-idrossilasi, che catalizza l'idrossilazione della prolina in posizione 4." I cofattori, i prodotti e il ruolo funzionale sono fatti separati e appartengono a card distinte o al brain dump.

4. **Domande esplicite a cue funzionale.** Il fronte deve essere una domanda chiara e specifica, formulata come cue funzionale: "Perché…", "Cosa succede se…", "Quale vantaggio conferisce…", "Come fa X a produrre Y?" — mai un prompt vago tipo "Parlami di X."

5. **Tags gerarchici.** Usa la struttura `biochimica::macro-argomento::argomento-specifico`. Es: `biochimica::aminoacidi::polari-non-carichi`.

6. **Marcatori preservati.** Se il contenuto sorgente ha marcatori `[VERIFICARE]` o simili, includi il marcatore nella card.

7. **Enfasi docente.** I blocchi `> [!warning] Enfasi docente` segnalano concetti su cui il docente ha insistito. Assicurati che ogni enfasi sia coperta da almeno una card o un brain dump — **ma solo se il contenuto enfatizzato è esaminabile come fatto discreto**. Se l'enfasi riguarda un giudizio meta (es. "questa proteina è la più importante", "questo è il concetto fondamentale") senza produrre un fatto discreto testabile, non generare una card apposita. Il concetto è già coperto dal brain dump o dalle card del topic.

8. **Card fattuali: contesto, non elenco.** Quando generi card fattuali (substrati, cofattori, valori numerici, localizzazioni), il back deve sempre includere un aggancio funzionale o contestuale che aiuti la memorizzazione. Esempio: "Gruppo tiolico (-SH), anche detto sulfidrilico. È reattivo e può formare ponti disolfuro (legami S-S) con un'altra cisteina" è meglio di solo "-SH".

9. **Deduplicazione del sorgente.** Il testo di una sezione può contenere lo stesso concetto ripetuto in forme diverse. Tratta queste come un'unica fonte: genera card solo dalla versione più completa e dettagliata, ignora le riformulazioni.

---

## Regole anti-ridondanza (CRITICHE)

### Principio di parsimonia
Genera il **minor numero di card possibile** per coprire ogni concetto. Concetti complessi con catene causali a più passaggi giustificano card multiple che testano **anelli causali indipendenti**. Il criterio è: ogni card deve testare un collegamento diverso, non lo stesso collegamento con parole diverse.

### Divieto di riformulazione
**Mai due card con lo stesso back.** Se due front portano alla stessa risposta, tieni solo il cue più specifico. Questo include i **versi inversi**: se la risposta è equivalente nella direzione A→B e B→A, tieni solo la domanda più specifica, elimina l'altra.

**Divieto di sottoinsieme**: se la risposta della card A è interamente contenuta nella risposta della card B, elimina card A e tieni solo card B, che testa la conoscenza completa.

### Verso inverso ristretto
Genera la card nella direzione inversa **solo** quando:
- L'associazione non è ovvia nella direzione inversa
- Fa parte di una serie confondibile (es. aminoacidi della stessa classe)
- Le due direzioni testano skill cognitive genuinamente diverse (struttura→funzione vs funzione→struttura)

**NON** generare il verso inverso per concetti unici e non confondibili.

---

## Regola di segmentazione delle catene causali (CRITICA)

Le card meccanismo puntuali testano un singolo passaggio causale. Se una catena ha più di 2 step complessivi e la logica sistemica è il vero obiettivo di apprendimento, il contenuto appartiene al brain dump, non ad Anki.

Per le card meccanismo che restano in Anki: **una freccia per card.** Il back spiega un solo nesso causale (trigger → evento → conseguenza immediata).

---

## Distribuzione target (blocco Anki)

| Tipo | % | Quando |
|------|---|--------|
| Fattuale diretta | ~25% | Recall di dati fondamentali con aggancio funzionale |
| Meccanismo/perché | ~30% | Logica causale puntuale di processi molecolari |
| Predittiva | ~25% | "Se cambia X, cosa succede a Y?" — una variabile, risposta diretta |
| Clinica/applicativa | ~10% | Solo se la correlazione clinica è nel testo |
| Confronto | ~10% | Discriminazione tra molecole/concetti confondibili — solo puntuali |

---

## Istruzioni per tipo (blocco Anki)

### Card fattuali dirette (~25%)

Card di recall per dati fondamentali:
- Aminoacidi: gruppo funzionale della catena laterale, polarità, proprietà speciali
- Enzimi: substrato, prodotto, cofattori, classe, tipo di inibizione, Km, localizzazione
- Valori numerici esplicitamente menzionati dal docente (pKa, pH, ΔG)

**Il back deve sempre includere un aggancio funzionale**, non solo il dato nudo.

Esempio:
```json
{
  "type": "fattuale",
  "front": "Qual è il gruppo funzionale della catena laterale della cisteina?",
  "back": "Gruppo tiolico (-SH), anche detto sulfidrilico. È reattivo e può formare ponti disolfuro (legami S-S) con un'altra cisteina, stabilizzando la struttura terziaria delle proteine.",
  "tags": ["biochimica::aminoacidi::polari-non-carichi"]
}
```

### Card meccanismo/perché (~30%)

Card che testano la comprensione di un singolo nesso causale puntuale. Il back spiega: trigger → evento molecolare → conseguenza immediata.

Esempio:
```json
{
  "type": "meccanismo",
  "front": "Perché le molecole d'acqua attorno a una superficie apolare formano strutture ordinate (clatrati)?",
  "back": "L'acqua non può formare legami H con la superficie apolare. Per massimizzare i propri legami H, le molecole d'acqua si dispongono in gabbie ordinate attorno alla molecola apolare, mantenendo la rete di legami H tra di loro ma a costo di una riduzione dell'entropia del sistema.",
  "tags": ["biochimica::interazioni-deboli::effetto-idrofobico"]
}
```

### Card predittive (~25%)

Card "Se cambia X, cosa succede a Y?" — **una variabile alla volta**, con contesto quantitativo dove disponibile:
- Variazioni di pH → effetto sulla carica/struttura
- Mutazioni/sostituzioni aminoacidiche → conseguenze funzionali dirette
- Alterazione di un singolo enzima → effetto immediato

Esempio:
```json
{
  "type": "predittiva",
  "front": "Se il pH di una soluzione contenente istidina scende da 7.4 a 5.0, cosa succede alla carica netta dell'istidina?",
  "back": "Il pKa dell'anello imidazolico è ~6.0. A pH 5.0 (sotto il pKa), l'imidazolo è protonato: l'istidina passa da sostanzialmente neutra (a pH 7.4) a carica netta positiva.",
  "tags": ["biochimica::aminoacidi::basici"]
}
```

### Card cliniche/applicative (~10%)

Card che collegano biochimica a patologie — **solo quando presenti nella sbobina**:
- Malattie da misfolding proteico
- Deficit enzimatici
- Basi molecolari di condizioni cliniche

Esempio:
```json
{
  "type": "clinica",
  "front": "Quale meccanismo molecolare è alla base dell'anemia falciforme?",
  "back": "Una mutazione puntiforme (Glu→Val in posizione 6 della catena β) introduce un residuo idrofobico sulla superficie dell'emoglobina. Nella forma deossigenata, questo residuo si inserisce in una tasca idrofobica di un'altra molecola di Hb, causando polimerizzazione in fibre rigide che deformano l'eritrocita a falce.",
  "tags": ["biochimica::proteine::emoglobina", "biochimica::clinica"]
}
```

### Card di confronto (~10%)

Card che forzano la discriminazione tra molecole o concetti facilmente confondibili — **solo confronti puntuali**:
- Aminoacidi della stessa classe con proprietà diverse
- Isoforme enzimatiche con regolazione diversa
- Legami deboli con caratteristiche diverse

**Nota:** Le card di confronto cross-sezione sono fatte manualmente. Qui genera solo confronti all'interno della stessa sezione.

Esempio:
```json
{
  "type": "confronto",
  "front": "Qual è la differenza tra legame a idrogeno e interazione di van der Waals in termini di forza e specificità?",
  "back": "Legame H: più forte (~10-40 kJ/mol), richiede donatore e accettore specifici (direzionale), distanza ottimale ~2.8 Å. Van der Waals: più debole (~2-4 kJ/mol), non specifico (dipende solo dalla vicinanza), ma il contributo cumulativo è significativo per la stabilità proteica.",
  "tags": ["biochimica::interazioni-deboli::confronto"]
}
```

---

## Regole brain dump

- Crea un brain dump per ogni via metabolica, meccanismo di regolazione, o logica causa-effetto sistemica presente nella sezione.
- Il campo `context` deve indicare brevemente da quale parte della lezione viene l'argomento.
- La checklist deve contenere i punti chiave che uno studente dovrebbe saper ricostruire senza guardare appunti: step della via, regolatori allosterici, bilancio energetico, conseguenze fisiologiche. Formulali come obiettivi di recall.
- Usa il formato `- [ ] punto chiave` per ogni voce.
- **Ridondanza tra Anki e brain dump: quando è legittima.** La presenza dello stesso fatto in una card Anki e in una checklist è legittima quando le due funzioni cognitive sono diverse: la card testa il recupero isolato del dato ("qual è il cofattore di X?"), la checklist lo usa come nodo in una catena di ragionamento ("nel contesto della via Y, descrivi il ruolo del cofattore di X"). È illegittima quando la voce della checklist ripete esattamente la domanda della card senza aggiungere contesto relazionale — in quel caso elimina la voce dalla checklist (il brain dump assume i fatti puntuali già coperti in Anki come dati noti).
- **Densità minima**: un brain dump su un topic complesso deve avere abbastanza item da testare realmente la comprensione — almeno 4-5 checkpoint. Un brain dump con 2 item non è un test della rete concettuale, è una lista.

Esempio:
```json
{
  "title": "Glicolisi: step, regolazione e bilancio",
  "type": "via_metabolica",
  "context": "Sezione sul metabolismo del glucosio",
  "checklist": [
    "- [ ] Elencare i 10 step della glicolisi con gli enzimi principali",
    "- [ ] Identificare i 3 step irreversibili e i relativi enzimi regolatori",
    "- [ ] Descrivere la regolazione allosterica della PFK-1 (attivatori e inibitori)",
    "- [ ] Calcolare il bilancio netto di ATP, NADH e piruvato per molecola di glucosio"
  ]
}
```

---

## Documento sorgente

Elabora il seguente documento:
