# Biochimica — Lezione: Classificazione e struttura delle proteine di membrana

> **Argomento:** Proteine di membrana
> **Blocchi presenti:** Classificazione funzionale · Strutture di attraversamento · Predizione bioinformatica · Proteine ancorate ai lipidi · Mobilità

---

## BLOCCO 1 — Classificazione funzionale delle proteine di membrana

La composizione proteica delle membrane biologiche è dinamica e varia tra cellule, tessuti e stadi di sviluppo. Le proteine di membrana si classificano in base alla modalità di interazione con il doppio strato lipidico.

### Proteine integrali di membrana
La definizione corretta non si basa sul fatto che la proteina attraversi completamente il doppio strato. Una **proteina integrale di membrana** è tale se, per essere rimossa dalla membrana, richiede la **distruzione della membrana stessa** mediante solventi o detergenti denaturanti. Questo include proteine che attraversano uno o entrambi i foglietti.

### Proteine periferiche di membrana
Queste proteine interagiscono con le teste idrofiliche dei lipidi (lato esterno o interno) o con altre proteine di membrana, tramite legami ionici o idrogeno. Possono essere separate dalla membrana semplicemente **cambiando la forza ionica** del mezzo (ad esempio variando il pH), senza distruggere il doppio strato.

### Proteine ancorate (antitropiche)
Queste proteine si legano alla membrana solo in **condizioni specifiche** (es. dopo fosforilazione o defosforilazione) tramite legami non covalenti. Dinamicamente, possono trovarsi legate alla membrana o libere nel citosol. [→ ARGOMENTO FUTURO: traduzione del segnale]

> [!warning] Enfasi docente
> Non è corretto definire una proteina "integrale" solo se attraversa il doppio strato. La definizione operativa è legata al metodo necessario per staccarla: se serve distruggere la membrana, è integrale.

---

## BLOCCO 2 — Strutture secondarie per l'attraversamento della membrana

Le proteine utilizzano principalmente due strutture secondarie per attraversare il doppio strato lipidico: **l'alfa elica** e il **foglietto beta**.

### Struttura ad alfa elica
È la forma **più comune**. Può essere una singola elica o un fascio multiplo (2, 10, 12 eliche). Lo spessore della membrana plasmatica è di circa **20 nanometri**. Considerando che ogni residuo amminoacidico in un'alfa elica contribuisce per ~1.5 nm, sono necessarie circa **20 amminoacidi** idrofobici in sequenza per coprire l'intero spessore.

### Struttura a foglietto beta (barile beta)
Questa struttura è tipica di complessi proteici che formano **pori** (es. pori mitocondriali). I foglietti beta si dispongono in modo da creare un canale che attraversa la membrana. La disposizione alternata di amminoacidi idrofobici e idrofilici rende difficile la predizione bioinformatica della localizzazione di membrana per queste proteine, che richiede **verifica sperimentale**. [→ ARGOMENTO FUTURO: metabolismo]

---

## BLOCCO 3 — Predizione bioinformatica delle proteine transmembrana

La presenza di sequenze di amminoacidi idrofobici nella struttura primaria è un forte indicatore di un dominio transmembrana ad alfa elica.

### L'indice idropatico
È una misura dell'energia necessaria per trasferire un amminoacido da un ambiente idrofobico a uno idrofilico. Più un amminoacido è **idrofobico**, più il suo indice idropatico è **elevato** (valori > 0).

### Utilizzo pratico
Inserendo la sequenza amminoacidica di una proteina in appositi software, si ottiene un grafico con il numero dei residui sull'asse X e l'indice idropatico sull'asse Y.
*   Se si osserva un **picco positivo** (indice > 0) per una sequenza di circa 20 residui, è alta la probabilità che quella regione sia un'**alfa elica transmembrana**.
*   **Esempi:**
    *   **Glicoforina:** Un solo picco → una singola alfa elica transmembrana.
    *   **Rodopsina:** Sette picchi → sette alfa eliche transmembrana.

> [!warning] Enfasi docente
> La predizione è possibile solo per le proteine che attraversano la membrana con alfa eliche, non per quelle a foglietto beta. Inoltre, non tutte le proteine integrali attraversano completamente la membrana.

---

## BLOCCO 4 — Proteine ancorate covalentemente ai lipidi

Un gruppo importante di proteine legate alla membrana è rappresentato dalle **proteine ancorate mediante lipidi**. Queste proteine formano un **legame covalente** con uno o più acidi grassi (es. acido palmitico C16, acido miristico C14), che si inseriscono nella porzione idrofobica del doppio strato.

### Vantaggio funzionale
Queste proteine possono muoversi **lateralmente** nel foglietto con grande rapidità. Questo permette interazioni veloci e mirate con altre proteine bersaglio nella membrana, potenziando la **rapidità della trasduzione del segnale**.

### Localizzazione
*   **Lato interno (citosolico):** Coinvolte nella trasduzione del segnale (es. proteine Ras, subunità alfa delle proteine G).
*   **Lato esterno:** Spesso legate a componenti zuccherine (glicosilate), sono rilevanti per l'ancoraggio e l'interazione cellula-cellula o cellula-matrice extracellulare.

---

## BLOCCO 5 — Mobilità delle proteine di membrana

Le proteine di membrana **possono muoversi** all'interno del doppio strato lipidico. Questo movimento laterale è fondamentale per processi come l'assemblaggio di complessi proteici e la trasduzione del segnale.

---

## APPENDICE TABELLARE

*Riepilogo aggregato della lezione per ripasso rapido e generazione flashcard.*

### Classificazione delle Proteine di Membrana

| TIPO | DEFINIZIONE OPERATIVA | TIPO DI INTERAZIONE | METODO DI RIMOZIONE | ESEMPI CITATI | IMMAGINE |
|---|---|---|---|---|---|
| **Integrali** | Richiedono la distruzione della membrana per essere rimosse. | Fortemente associate alla porzione idrofobica. | Solventi/detergenti denaturanti. | Prostaglandina H2 sintasi 1 | |
| **Periferiche** | Interagiscono con teste lipidiche o altre proteine. | Legami ionici / idrogeno. | Cambio di forza ionica (pH). | — | |
| **Ancorate (Antitropiche)** | Si legano dinamicamente in condizioni specifiche. | Legami non covalenti condizionati (es. da fosforilazione). | Cambiamenti conformazionali. | — | |
| **Ancorate ai Lipidi** | Legate covalentemente ad acidi grassi. | Legame covalente con acido grasso inserito nel doppio strato. | Idrolisi del legame covalente. | Proteine Ras, Subunità alfa delle proteine G | |

### Strutture di Attraversamento

| STRUTTURA | CARATTERISTICA | LUNGHEZZA TIPICA (residui) | PREDICIBILITÀ | ESEMPI | IMMAGINE |
|---|---|---|---|---|---|
| **Alfa Elica** | Più comune. Singola o multipla. | ~20 (per coprire 20 nm) | Alta (tramite indice idropatico). | Glicoforina (1 elica), Rodopsina (7 eliche) | |
| **Foglietto Beta (Barile)** | Forma pori/canali. | Variabile. | Bassa (richiede verifica sperimentale). | Pori mitocondriali | |

---

*Fine sbobina — Lezione: Classificazione e struttura delle proteine di membrana*
*Argomenti correlati: → Trasduzione del segnale · → Metabolismo · → Glicosilazione*