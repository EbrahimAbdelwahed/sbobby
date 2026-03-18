# Prompt — Generazione Flashcard Anki

Questo file contiene tre prompt separati, uno per materia. Ogni prompt riceve come input l'appendice tabellare e il testo della sbobina, e produce un JSON array di flashcard pronte per AnkiConnect.

---

## Formato output (comune a tutte le materie)

```json
[
  {
    "type": "fattuale|meccanismo|predittiva|confronto|clinica",
    "front": "Testo della domanda",
    "back": "Testo della risposta con contesto sufficiente",
    "tags": ["materia", "macro-argomento", "argomento-specifico"],
    "image": "filename.jpg (opzionale, solo se presente nel mapping immagini)"
  }
]
```

### Regole generali per tutte le materie

1. **Fonte esclusiva.** Genera card solo da informazioni presenti nel documento sorgente. Non aggiungere conoscenze esterne.
2. **Retro mai telegrafici.** Il retro di ogni card deve includere contesto sufficiente per fissare il concetto, mai una singola parola isolata. Esempio: "Nervo ascellare (C5-C6), ramo terminale del fascicolo posteriore del plesso brachiale" è meglio di solo "Nervo ascellare."
3. **Una nozione per card.** Ogni card testa un singolo concetto o collegamento. Se una tabella ha 5 colonne per un muscolo, genera 3-4 card separate (una per innervazione, una per azione, una predittiva), non una card con tutto.
4. **Domande esplicite.** Il fronte deve essere una domanda chiara e specifica, mai un prompt vago tipo "Parlami di X."
5. **Tags gerarchici.** Usa tags che seguano la struttura: `materia::macro-argomento::argomento-specifico`. Es: `anatomia::locomotore::spalla::muscoli`.
6. **Marcatori preservati.** Se il contenuto sorgente ha marcatori `[VERIFICARE]` o simili, includi il marcatore nella card come avviso.
7. **Card reversibili dove sensato.** Per card fattuali con associazioni bidirezionali (es. nome muscolo ↔ innervazione), genera entrambe le direzioni.

---

## Prompt 1 — Anatomia

### Distribuzione target
- ~50% Card fattuali dirette
- ~20% Card predittive
- ~15% Card cliniche/applicative
- ~15% Card di confronto

### Istruzioni

Ricevi una sbobina di anatomia (testo e appendice tabellare). Genera flashcard in formato JSON seguendo le regole generali e queste istruzioni specifiche.

**Card fattuali dirette (~50%)**
Genera card di recall puro dalle tabelle e dal testo fattuale:
- Per muscoli: card separate per origine, inserzione, azione, innervazione
- Per articolazioni: tipo, superfici articolari, gradi di libertà, movimenti consentiti
- Per legamenti: inserzioni, funzione meccanica, posizione di massima tensione
- Per vasi/nervi: origine, decorso, territorio di distribuzione
- Per le card su strutture con nome, genera anche la card reversa (es. "Quale nervo innerva il deltoide?" E "Quali muscoli sono innervati dal nervo ascellare?")

Esempio:
```json
{
  "type": "fattuale",
  "front": "Qual è l'innervazione del muscolo deltoide?",
  "back": "Nervo ascellare (C5-C6), ramo terminale del fascicolo posteriore del plesso brachiale.",
  "tags": ["anatomia::locomotore::spalla::muscoli"]
}
```

**Card predittive (~20%)**
Genera card "Se X, allora cosa succede a Y?" basandoti su relazioni funzionali presenti nella sbobina:
- Lesioni nervose → deficit motori/sensitivi
- Posizioni articolari → legamenti in tensione
- Varianti anatomiche → conseguenze funzionali

Esempio:
```json
{
  "type": "predittiva",
  "front": "Se il nervo ascellare viene lesionato (es. lussazione della spalla), quale movimento è compromesso?",
  "back": "Abduzione del braccio oltre i primi 15° è gravemente compromessa, perché il deltoide (principale abduttore) è paralizzato. Residua solo l'abduzione iniziale da parte del sovraspinato.",
  "tags": ["anatomia::locomotore::spalla::muscoli", "anatomia::clinica"]
}
```

**Card cliniche/applicative (~15%)**
Genera card che collegano concetti anatomici a patologie o applicazioni cliniche, solo quando queste correlazioni sono presenti nella sbobina (enfasi docente, note cliniche, peculiarità):
- Sindromi da compressione
- Lussazioni e instabilità
- Punti di repere per procedure cliniche

Esempio:
```json
{
  "type": "clinica",
  "front": "Perché la gleno-omerale è l'articolazione che si lussa più frequentemente?",
  "back": "Massima mobilità a scapito della stabilità intrinseca: il raggio di curvatura della testa omerale è molto maggiore della cavità glenoidea. La stabilità dipende quasi interamente da strutture capsulo-legamentose e dalla cuffia dei rotatori.",
  "tags": ["anatomia::locomotore::spalla::articolazione", "anatomia::clinica"]
}
```

**Card di confronto (~15%)**
Genera card che forzano la discriminazione tra strutture simili o facilmente confondibili, quando la sbobina presenta strutture confrontabili nella stessa regione:
- Muscoli con azioni simili ma innervazione diversa
- Fasci dello stesso legamento con funzioni diverse
- Strutture topograficamente vicine

Esempio:
```json
{
  "type": "confronto",
  "front": "Qual è la differenza funzionale tra il fascio anteriore e il fascio posteriore del legamento gleno-omerale inferiore (LGOI)?",
  "back": "Fascio anteriore: si tende a 90° di abduzione + rotazione esterna, resiste alla traslazione antero-inferiore (lesione di Bankart). Fascio posteriore: si tende in flessione + rotazione interna, resiste alla traslazione postero-inferiore.",
  "tags": ["anatomia::locomotore::spalla::legamenti"]
}
```

### Documento sorgente
Elabora il seguente documento:

---

## Prompt 2 — Biochimica

### Distribuzione target
- ~25% Card fattuali dirette
- ~30% Card meccanismo/perché
- ~25% Card predittive
- ~10% Card di confronto
- ~10% Card cliniche/applicative

### Istruzioni

Ricevi una sbobina di biochimica (testo e appendice tabellare). Genera flashcard in formato JSON seguendo le regole generali e queste istruzioni specifiche.

**Card fattuali dirette (~25%)**
Genera card di recall per i dati fondamentali:
- Aminoacidi: gruppo funzionale, polarità, proprietà speciali
- Enzimi: substrato, prodotto, cofattori
- Vie metaboliche: substrati iniziali, prodotti finali, localizzazione cellulare
- Valori numerici esplicitamente menzionati dal docente (pKa, pH, energie di legame)

Esempio:
```json
{
  "type": "fattuale",
  "front": "Qual è il gruppo funzionale della catena laterale della cisteina?",
  "back": "Gruppo tiolico (-SH), anche detto sulfidrilico. È l'unico aminoacido (insieme alla metionina) che contiene zolfo nella catena laterale.",
  "tags": ["biochimica::aminoacidi::polari-non-carichi"]
}
```

**Card meccanismo/perché (~30%)**
Queste sono le card più importanti per biochimica. Genera card che testano la comprensione della logica causale dei processi:
- Perché un processo avviene in un determinato modo
- Qual è il meccanismo molecolare alla base di un fenomeno
- Qual è la logica termodinamica o chimica di un evento

Il retro deve spiegare il meccanismo in modo conciso ma completo, non solo nominarlo.

Esempio:
```json
{
  "type": "meccanismo",
  "front": "Perché le molecole idrofobiche tendono ad aggregarsi in ambiente acquoso?",
  "back": "Le molecole d'acqua si riorganizzano in modo più ordinato attorno alla superficie apolare (non potendo formare legami H con essa), riducendo l'entropia del sistema. Questa situazione è termodinamicamente sfavorevole. L'aggregazione minimizza la superficie esposta al solvente, mitigando la perdita entropica. Questo è l'effetto idrofobico.",
  "tags": ["biochimica::interazioni-deboli::effetto-idrofobico"]
}
```

**Card predittive (~25%)**
Genera card "Se cambia X, cosa succede a Y?" basandoti su relazioni logiche presenti nella sbobina:
- Variazioni di pH → effetto sulla carica degli aminoacidi
- Cambiamenti ambientali → effetto sulla struttura proteica
- Mutazioni/sostituzioni aminoacidiche → conseguenze funzionali
- Alterazione di una via metabolica → effetti a cascata

Esempio:
```json
{
  "type": "predittiva",
  "front": "Se il pH di una soluzione contenente istidina scende da 7.4 a 5.0, cosa succede alla carica netta dell'istidina?",
  "back": "Il pKa dell'anello imidazolico dell'istidina è ~6.0. A pH 5.0 (sotto il pKa), l'imidazolo è protonato e l'istidina ha carica netta positiva. A pH 7.4 era sostanzialmente neutra. Questa sensibilità alle piccole variazioni di pH è ciò che la rende cruciale nei sistemi tampone e nei siti attivi enzimatici.",
  "tags": ["biochimica::aminoacidi::basici", "biochimica::punto-isoelettrico"]
}
```

**Card di confronto (~10%)**
Genera card che forzano la discriminazione tra molecole o concetti facilmente confondibili:
- Aminoacidi della stessa classe con proprietà diverse
- Vie anaboliche vs cataboliche
- Legami deboli diversi tra loro

Esempio:
```json
{
  "type": "confronto",
  "front": "Qual è la differenza tra asparagina e aspartato?",
  "back": "Asparagina ha un gruppo ammidico (-CONH₂) nella catena laterale: è polare ma non carica a pH fisiologico. Aspartato ha un gruppo carbossilico (-COO⁻): è carico negativamente a pH fisiologico. L'aspartato è anche un intermedio del ciclo di Krebs.",
  "tags": ["biochimica::aminoacidi::confronto"]
}
```

**Card cliniche/applicative (~10%)**
Genera card che collegano concetti biochimici a patologie o applicazioni, solo quando presenti nella sbobina:
- Malattie da misfolding proteico
- Deficit enzimatici
- Basi molecolari di condizioni cliniche

Esempio:
```json
{
  "type": "clinica",
  "front": "Quale meccanismo molecolare è alla base delle malattie da aggregazione proteica?",
  "back": "Il misfolding espone i residui idrofobici normalmente segregati nel core della proteina. Questi residui, a contatto con l'ambiente acquoso, si associano tra loro (effetto idrofobico) causando aggregazione patologica non controllata.",
  "tags": ["biochimica::proteine::folding", "biochimica::clinica"]
}
```

### Documento sorgente
Elabora il seguente documento:

---

## Prompt 3 — Istologia

### Distribuzione target
- ~35% Card fattuali dirette
- ~25% Card meccanismo/perché
- ~15% Card predittive
- ~25% Card di confronto

### Nota sulle card di riconoscimento visivo
Le card di identificazione tissutale da immagine (es. "Che tessuto è questo?" con foto del preparato) NON vengono generate da questo prompt. Queste card richiedono immagini da lezione/laboratorio e vanno create manualmente usando il plugin Image Occlusion di Anki. Questo prompt genera solo card testuali.

### Istruzioni

Ricevi una sbobina di istologia (testo e appendice tabellare). Genera flashcard in formato JSON seguendo le regole generali e queste istruzioni specifiche.

**Card fattuali dirette (~35%)**
Genera card di recall per l'identificazione e le caratteristiche dei tessuti:
- Classificazione dei tessuti: tipo, sottotipo, varianti
- Caratteristiche morfologiche: forma delle cellule, numero di strati, specializzazioni di superficie
- Localizzazione: dove si trova ciascun tessuto nell'organismo
- Componenti specifiche: fibre, cellule residenti, matrice extracellulare

Esempio:
```json
{
  "type": "fattuale",
  "front": "Dove si trova l'epitelio pavimentoso semplice nell'organismo?",
  "back": "Riveste le superfici dove avvengono scambi per diffusione o filtrazione: endotelio dei vasi sanguigni e linfatici, mesotelio delle sierose (pleura, peritoneo, pericardio), capsula di Bowman nel rene, alveoli polmonari.",
  "tags": ["istologia::epiteliale::pavimentoso-semplice"]
}
```

**Card meccanismo/perché (~25%)**
Genera card struttura→funzione che testano la comprensione del perché un tessuto è fatto in un certo modo:
- Perché un certo tipo di epitelio si trova in una certa sede
- Come la struttura della matrice extracellulare determina le proprietà meccaniche
- Perché certe cellule hanno determinate specializzazioni

Esempio:
```json
{
  "type": "meccanismo",
  "front": "Perché l'epitelio delle vie respiratorie è pseudostratificato ciliato con cellule caliciformi?",
  "back": "Le ciglia creano un movimento coordinato (battito ciliare) che spinge il muco verso la faringe. Le cellule caliciformi secernono il muco che intrappola particelle e patogeni inalati. Insieme formano l'apparato mucociliare, meccanismo di difesa primario delle vie aeree.",
  "tags": ["istologia::epiteliale::pseudostratificato", "istologia::meccanismo"]
}
```

**Card predittive (~15%)**
Genera card su conseguenze funzionali di alterazioni tissutali, quando presenti nella sbobina:
- Cosa succede se un tessuto perde una caratteristica
- Conseguenze di metaplasie o alterazioni
- Effetti della perdita di componenti specifiche

Esempio:
```json
{
  "type": "predittiva",
  "front": "Cosa succede alla funzione respiratoria se l'epitelio ciliato viene danneggiato (es. dal fumo cronico)?",
  "back": "Si perde la clearance mucociliare: il muco e le particelle intrappolate non vengono più trasportate verso la faringe. Questo porta a ristagno di secrezioni, maggiore suscettibilità alle infezioni, e tosse cronica come meccanismo compensatorio di pulizia.",
  "tags": ["istologia::epiteliale::pseudostratificato", "istologia::clinica"]
}
```

**Card di confronto (~25%)**
Particolarmente importanti in istologia, dove la discriminazione tra tessuti simili è una competenza fondamentale:
- Epitelio semplice vs stratificato
- Connettivo lasso vs denso
- Tessuti con morfologia simile ma localizzazione/funzione diversa
- Componenti della matrice con ruoli distinti

Esempio:
```json
{
  "type": "confronto",
  "front": "Qual è la differenza tra epitelio stratificato cheratinizzato e non cheratinizzato?",
  "back": "Entrambi sono pluristratificati pavimentosi con funzione protettiva. Il cheratinizzato (epidermide) ha strati superficiali di cellule morte piene di cheratina, resiste all'abrasione meccanica e alla disidratazione. Il non cheratinizzato (esofago, vagina, cornea) mantiene le cellule superficiali nucleate e umide, protegge da attrito in ambienti interni umidi.",
  "tags": ["istologia::epiteliale::stratificato::confronto"]
}
```

### Documento sorgente
Elabora il seguente documento: