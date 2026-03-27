# Biochimica — Lezione: Inibizione enzimatica irreversibile e regolazione dell'attività enzimatica

> **Argomento:** Inibizione enzimatica irreversibile, reazioni con più substrati, regolazione allosterica, regolazione mediante isoenzimi, modificazioni covalenti (reversibili e irreversibili), attivazione proteolitica.
> **Blocchi presenti:** Tipologie di inibizione irreversibile · Inibitori suicidi (Penicillina) · Inibitori gruppo-specifici (Aspirina) · Reazioni enzimatiche con più substrati · Introduzione alla regolazione enzimatica · Enzimi allosterici: definizione e caratteristiche · Cinetica allosterica (sigmoidea) · Modelli di regolazione allosterica · Modello sequenziale di cooperatività · Esempio di regolazione allosterica: Aspartato transcarbamilasi (ATCase) nella sintesi delle pirimidine · Struttura e stati conformazionali di ATCase · Effetti cinetici dei modulatori su ATCase · Logica biologica della regolazione di ATCase · Isoenzimi: definizione ed esempi (LDH) · Isoenzimi: esempio Esochinasi vs. Glucochinasi · Modificazioni covalenti reversibili e irreversibili · Meccanismo della fosforilazione · Amplificazione del segnale tramite fosforilazione a cascata · Regolazione fine mediante fosforilazione multipla · Regolazione mediante attivazione proteolitica.

---

## BLOCCO 1 — Tipologie di inibizione irreversibile

L'<span style="color:#2E7D32">inibizione enzimatica irreversibile</span> si verifica quando l'inibitore si lega strettamente all'enzima e non viene rimosso, portando a una perdita permanente dell'attività catalitica. Si distinguono tre tipologie principali.

### 1. Analoghi del substrato
Si tratta di molecole strutturalmente analoghe al substrato naturale. Si legano in modo covalente nel <span style="color:#2E7D32">sito attivo</span> al posto del substrato, formando un legame stabile e non idrolizzabile. Poiché non sono substrati, non danno luogo alla formazione di prodotti, inibendo così l'attività enzimatica.

### 2. Inibitori suicidi
Sono molecole che, durante il processo catalitico stesso, generano intermedi reattivi. Questi intermedi modificano covalentemente il <span style="color:#2E7D32">sito attivo</span> dell'enzima, rendendolo incapace di catalizzare la reazione. L'esempio principale è la <span style="color:#E57373">penicillina</span>.

### 3. Inibitori gruppo-specifici
Sono molecole che reagiscono in modo covalente con specifiche catene laterali di <span style="color:#E65100">amminoacidi</span> presenti nel sito attivo dell'enzima. La specificità deriva dalla reazione con particolari gruppi funzionali. L'esempio principale è l'<span style="color:#E57373">aspirina</span> (acido acetilsalicilico).

> [immagine di: schema comparativo delle tre tipologie di inibizione irreversibile con esempi strutturali]

---

## BLOCCO 2 — Inibitori suicidi: il caso della Penicillina

> [immagine di: struttura chimica della penicillina e del suo meccanismo di legame covalente con la serina dell'enzima bersaglio]

La <span style="color:#E57373">penicillina</span> è un antibiotico che agisce come inibitore suicida. Il suo bersaglio sono i batteri Gram-positivi, sui quali esercita la sua azione interferendo con la sintesi della parete cellulare batterica, una struttura essenziale per la loro sopravvivenza.

### Meccanismo d'azione
La penicillina inibisce in modo irreversibile l'enzima <span style="color:#2E7D32">glicopeptide transpeptidasi</span>. Questo enzima è chiave per la sintesi del peptidoglicano della parete batterica, in quanto catalizza la formazione di legami crociati (ponti di vicina) tra le catene polisaccaridiche lineari.

> [immagine di: struttura schematica del peptidoglicano batterico con catene di zuccheri (giallo) e tetra-peptidi (rosso) uniti da ponti trasversali]

Il meccanismo prevede che il <span style="color:#2E7D32">sito attivo</span> dell'enzima, che contiene un residuo di <span style="color:#E65100">serina</span> con un gruppo -OH libero, attacchi l'anello beta-lattamico della penicillina. Si forma così un complesso covalente stabile tra la penicillina e la serina dell'enzima.
[REACTION:penicillina + OH-Serina-enzima -> complesso penicillina-serina (covalente)]

Questo intermedio covalente è inattivo e blocca irreversibilmente l'<span style="color:#2E7D32">enzima</span>. Di conseguenza, la sintesi della parete batterica si arresta.

> [!warning] Enfasi docente
> L'inibizione è irreversibile. L'enzima inattivato non è recuperabile; la cellula batterica, per ripristinare la funzione, deve sintetizzare ex novo nuove molecole enzimatiche.

**Riepilogo rapido — Penicillina:**
- **Tipo:** Inibitore suicida.
- **Bersaglio:** <span style="color:#2E7D32">Glicopeptide transpeptidasi</span> batterica.
- **Meccanismo:** Legame covalente irreversibile tra il gruppo -OH di una serina del sito attivo e l'anello della penicillina.
- **Effetto:** Blocco della sintesi della parete cellulare → azione antibiotica.

---

## BLOCCO 3 — Inibitori gruppo-specifici: il caso dell'Aspirina

> [immagine di: struttura chimica dell'acido acetilsalicilico (aspirina) e meccanismo di acetilazione della serina 530 della COX]

L'<span style="color:#E57373">aspirina</span> (acido acetilsalicilico) è un farmaco noto per le sue proprietà antipiretiche e antinfiammatorie. La sua azione terapeutica deriva proprio da un'inibizione enzimatica irreversibile di tipo gruppo-specifico.

### Bersaglio e Pathway
L'aspirina inibisce in modo irreversibile l'enzima umano <span style="color:#2E7D32">prostaglandina sintetasi</span>, anche noto come <span style="color:#2E7D32">cicloossigenasi (COX)</span>.
Questo enzima è fondamentale nel pathway di biosintesi delle <span style="color:#E57373">prostaglandine</span> a partire dall'<span style="color:#E57373">acido arachidonico</span> (un derivato della via di sintesi del colesterolo). Le prostaglandine sono mediatori chimici responsabili di sintomi come febbre, dolore e infiammazione.
[CHEM:acido arachidonico]

### Meccanismo d'azione
L'<span style="color:#E57373">aspirina</span> agisce come inibitore gruppo-specifico perché trasferisce il suo **gruppo acetilico** al gruppo -OH libero di un residuo specifico di <span style="color:#E65100">serina</span> (la serina 530) presente nel <span style="color:#2E7D32">sito attivo</span> della cicloossigenasi.
[REACTION:aspirina + OH-Ser530-COX -> enzima acetilato + acido salicilico]

Questa acetilazione modifica covalentemente il residuo catalitico essenziale, inattivando l'<span style="color:#2E7D32">enzima</span> in modo irreversibile. Le molecole di COX così modificate vengono poi degradate dalla cellula.

> [!warning] Enfasi docente
> L'OH della serina 530 è essenziale per l'attività catalitica della COX. Il trasferimento del gruppo acetilico dell'aspirina su questo residuo blocca irreversibilmente la funzione dell'enzima.

**Riepilogo rapido — Aspirina:**
- **Tipo:** Inibitore gruppo-specifico.
- **Bersaglio:** <span style="color:#2E7D32">Cicloossigenasi (COX)</span> / Prostaglandina sintetasi umana.
- **Meccanismo:** Trasferimento covalente del gruppo acetilico dell'aspirina al -OH della Ser530 dell'enzima.
- **Effetto:** Blocco della sintesi delle prostaglandine → azione antinfiammatoria, antipiretica, analgesica.

---

## BLOCCO 4 — Reazioni enzimatiche con più substrati

Nella cellula, le reazioni enzimatiche reali sono spesso più complesse del modello a un solo substrato (cinetica di Michaelis-Menten) e coinvolgono **più substrati**. Queste reazioni si dividono in due grandi tipologie:
1.  **Reazioni sequenziali**: tutti i substrati si legano all'enzima prima del rilascio di qualsiasi prodotto.
2.  **Reazioni ping-pong** (o a doppio spostamento): un substrato si lega e viene convertito in prodotto e rilasciato; solo successivamente un secondo substrato diverso si può legare.

### Reazioni sequenziali
Nelle reazioni sequenziali, i substrati si legano in un ordine specifico. Esistono due sottotipi:
*   **Sequenziale ordinato**: i substrati si legano in un ordine fisso e obbligatorio.
*   **Sequenziale casuale**: i substrati possono legarsi in qualsiasi ordine.

**Esempio di sequenziale ordinato:** La <span style="color:#2E7D32">lattato deidrogenasi</span>. Questo enzima catalizza la riduzione del <span style="color:#E57373">piruvato</span> a <span style="color:#E57373">lattato</span>. I due substrati, <span style="color:#00ACC1">NADH</span> e piruvato, si legano uno dopo l'altro in un ordine fisso. Il primo prodotto rilasciato è il lattato, seguito dal <span style="color:#00ACC1">NAD+</span>. [REACTION:piruvato + NADH -> lattato + NAD+]

**Esempio di sequenziale casuale:** La <span style="color:#2E7D32">creatina chinasi</span>, un enzima importante nel metabolismo muscolare. I suoi substrati sono <span style="color:#81C784">ATP</span> e <span style="color:#E57373">creatina</span>. Questi possono legarsi all'enzima in qualsiasi ordine: prima ATP e poi creatina, o viceversa. Di conseguenza, anche i prodotti possono essere rilasciati in ordine variabile.

### Reazioni ping-pong (doppio spostamento)
In questo meccanismo, l'enzima libero si lega prima al substrato A, formando un complesso attivato (E-A). Da questo complesso viene generato e rilasciato il primo prodotto P. Solo successivamente l'enzima, ora modificato, potrà legare un secondo substrato B diverso, che verrà a sua volta convertito.

**Esempio biologico:** Le <span style="color:#2E7D32">transaminasi</span>. Questi enzimi, che hanno rilevanza clinica e diagnostica, seguono un meccanismo di doppio spostamento (ping-pong).

---

## BLOCCO 5 — Introduzione alla regolazione enzimatica

La regolazione dell'attività enzimatica è un processo fisiologico che avviene costantemente all'interno delle cellule, a differenza dei fenomeni di inibizione studiati in precedenza, che erano spesso di natura farmacologica. Oggi ci si focalizza sui meccanismi di controllo endogeno del metabolismo.

> [!warning] Enfasi docente
> La distinzione è cruciale: l'inibizione era un argomento distinto, spesso legato a molecole esterne introdotte a scopo terapeutico. La regolazione è ciò che avviene normalmente nella cellula per controllare i metabolismi.

---

## BLOCCO 6 — Definizione e caratteristiche degli enzimi allosterici

Gli <span style="color:#2E7D32">enzimi allosterici</span> sono **enzimi regolatori** che modificano la propria attività catalitica attraverso il legame reversibile di molecole effettrici. Queste molecole si legano in un sito specifico, diverso dal sito attivo, chiamato **sito allosterico**.

### Caratteristiche chiave:
*   **Sito di legame regolatorio:** Il sito allosterico è distinto dal sito attivo.
*   **Natura degli effettori:** Le molecole che si legano al sito allosterico sono dette **modulatori** e possono essere di due tipi:
    *   **Modulatori positivi (attivatori):** Stimolano l'attività catalitica.
    *   **Modulatori negativi (inibitori):** Riducono l'attività catalitica.
*   **Struttura:** La maggior parte degli enzimi allosterici è composta da più subunità, ma esistono eccezioni (es. <span style="color:#2E7D32">glucochinasi</span>). Ogni subunità può avere una funzione catalitica (C) o regolatoria (R).
*   **Meccanismo d'azione:** Il legame del modulatore alla subunità regolatoria induce una **modificazione conformazionale** che viene trasmessa alla subunità catalitica, alterandone l'attività (es. modificando l'affinità per il substrato).

> [immagine di: schema di un enzima allosterico con subunità catalitica (C) e regolatoria (R) separate, che legano rispettivamente il substrato (S) e il modulatore (M)]

> [!warning] Enfasi docente
> Il substrato **non** è un regolatore allosterico vero e proprio, perché si lega al sito attivo. Tuttavia, può produrre un **effetto allosterico funzionale**, cioè agire in modo paragonabile a un modulatore in alcuni contesti specifici.

---

## BLOCCO 7 — Cinetica degli enzimi allosterici (curva sigmoidea)

La cinetica degli <span style="color:#2E7D32">enzimi allosterici</span> non segue il modello di Michaelis-Menten (che dà una curva iperbolica). La loro attività è descritta da una **funzione sigmoidea** (a forma di "S").

### Confronto con la cinetica iperbolica (Michaelis-Menten):
*   **A basse concentrazioni di substrato:** La velocità di reazione catalizzata da un enzima allosterico è **più lenta** rispetto a un enzima con cinetica iperbolica.
*   **Ad alte concentrazioni di substrato:** La velocità diventa **più veloce**, superando potenzialmente quella dell'enzima iperbolico.

### Effetto dei modulatori sui parametri cinetici:
I modulatori allosterici possono agire su due parametri:
1.  **Sulla velocità massima (Vmax):**
    *   Un modulatore **positivo** la **aumenta**.
    *   Un modulatore **negativo** la **riduce**.
2.  **Sull'affinità per il substrato (descritta da K₀.₅, analogo della Km):**
    *   Un modulatore **positivo** **aumenta** l'affinità (diminuisce K₀.₅).
    *   Un modulatore **negativo** **riduce** l'affinità (aumenta K₀.₅).

> [immagine di: grafico che confronta una curva iperbolica (blu, Michaelis-Menten) con una curva sigmoidea (verde, allosterica), mostrando le differenze a basse e alte concentrazioni di substrato]
> [immagine di: grafico che mostra l'effetto di modulatori positivi (verde) e negativi (rosso) sulla curva sigmoidea di riferimento (nero), sia sullo spostamento della Vmax che della K₀.₅]

---

## BLOCCO 8 — Modelli di regolazione allosterica

### Modello Concertato (OBSOLETO)
Questo modello, inizialmente proposto, presupponeva che l'enzima esistesse in due stati conformazionali globali:
*   **Stato T (teso):** A bassa affinità.
*   **Stato R (rilassato):** Ad alta affinità.
Il modello prevedeva che il legame di un effettore a una subunità causasse un cambiamento conformazionale **immediato e simultaneo** (concertato) di **tutte** le subunità dell'enzima verso lo stato R (se attivatore) o T (se inibitore). Questo modello è stato superato.

### Modello Sequenziale (ATTUALE)
Il modello attualmente accettato per descrivere la regolazione allosterica è il **modello sequenziale**.
*   **Protomeri indipendenti:** In una proteina multimerica, ogni subunità (protomero) può trovarsi nello stato T o R in modo **indipendente** dalle altre nello stato basale.
*   **Cambiamento graduale:** Il legame del primo modulatore a una subunità induce un **cambio conformazionale solo in quella subunità**.
*   **Comunicazione sequenziale:** Questa modificazione conformazionale viene **comunicata in modo sequenziale** alle subunità adiacenti, influenzando la loro propensione a legare il modulatore successivo e cambiare stato.
*   **Stati misti:** Si possono quindi avere situazioni intermedie con un **mix di subunità negli stati T e R**, non solo tutti T o tutti R.

> [immagine di: rappresentazione schematica del modello sequenziale, che mostra una proteina tetramerica con subunità che cambiano stato una alla volta in seguito al legame sequenziale di modulatori]

**Riepilogo rapido — Regolazione Allosterica:**
*   Enzimi regolatori con sito allosterico ≠ sito attivo.
*   Modulatori (attivatori/inibitori) legano il sito allosterico in modo reversibile.
*   Cinetica sigmoidea (non iperbolica).
*   Modulatori agiscono su Vmax e/o affinità (K₀.₅).
*   Meccanismo descritto dal **modello sequenziale** (cambio conformazionale graduale e comunicato tra subunità).

---

## BLOCCO 9 — Modello sequenziale di cooperatività

> [immagine di: schema del modello sequenziale di cooperatività con subunità che passano da stato T a R]

Il modello sequenziale (o "a simpatria infranta") descrive il comportamento degli enzimi allosterici. Inizialmente, le subunità possono trovarsi in modo indipendente nello stato **T** (teso/inattivo) o **R** (rilassato/attivo). Il legame della **prima molecola di modulatore** (o substrato) a una subunità determina un cambiamento conformazionale che viene comunicato alle subunità adiacenti in modo sequenziale. Questa modifica viene "trasmessa" (trasdotta), facilitando il legame del secondo ligando alla subunità vicina, e così via, fino a che tutte le subunità possono trovarsi nello stesso stato (ad esempio, tutto R o tutto T). Esistono anche stati intermedi "misti".

---

## BLOCCO 10 — Esempio di regolazione allosterica: ATCase nella sintesi delle pirimidine

> [immagine di: schema della via di sintesi dei nucleotidi pirimidinici, con evidenziata la prima reazione catalizzata da ATCase]

L'**aspartato transcarbamilasi (ATCase o ATCase)** catalizza la **prima reazione** della sintesi *de novo* dei nucleotidi pirimidinici. La via parte dall'aminoacido <span style="color:#E65100">aspartato</span> e, attraverso una cascata di reazioni, arriva al prodotto finale: la **citidina trifosfato (CTP)**.

La reazione catalizzata da ATCase è la conversione dell'<span style="color:#E65100">aspartato</span> e del carbamil fosfato in **N-carbamil aspartato**. [CHEM:aspartato] [REACTION:aspartato + carbamil fosfato -> N-carbamil aspartato]

> [!warning] Enfasi docente
> È fondamentale ricordare che il **prodotto finale dell'intera via (CTP)** ritorna a inibire il primo enzima della cascata (ATCase). Questo è un classico esempio di **feedback negativo** (inibizione a monte).

L'ATCase è regolata in modo allosterico da due effettori:
*   **CTP**: è il **prodotto finale della via** e agisce come **regolatore allosterico negativo** (inibitore).
*   **ATP**: la adenosina trifosfato, agisce come **regolatore allosterico positivo** (attivatore).

---

## BLOCCO 11 — Struttura e stati conformazionali di ATCase

> [immagine di: struttura quaternaria di ATCase che mostra i due trimeri catalitici e i tre dimeri regolatori]

L'ATCase ha una struttura complessa composta da:
*   **6 subunità catalitiche** (organizzate in due trimeri).
*   **6 subunità regolatorie** (organizzate in tre dimeri).

Questo enzima allosterico esiste in due conformazioni principali:
1.  **Stato T (Teso)**: Conformazione **chiusa/inattiva**. È stabilizzata dal legame del regolatore negativo **CTP** al **sito allosterico** situato sulle subunità regolatorie.
2.  **Stato R (Rilassato)**: Conformazione **aperta/attiva**. Può essere favorita dal legame del **substrato** al sito attivo e, in questo caso specifico, è stabilizzata dal legame del regolatore positivo **ATP**.

> [immagine di: confronto delle conformazioni dello stato T (chiuso) e dello stato R (aperto) di ATCase]

Il legame di questi ligandi induce un **cambio conformazionale** globale della proteina, passando da una struttura più compatta (T) a una più aperta (R).

---

## BLOCCO 12 — Effetti cinetici dei modulatori su ATCase

> [immagine di: grafico sigmoide della velocità di ATCase in funzione della concentrazione di substrato, con curve che si spostano per effetto di CTP e ATP]

La cinetica dell'ATCase in funzione della concentrazione del suo substrato è **sigmoidea**, tipica degli enzimi allosterici.

L'effetto dei due modulatori sulla curva cinetica è opposto:
*   **CTP (inibitore allosterico)**: **Abbassa la curva** e la **sposta verso destra**. Questo significa:
    *   **Aumento della K₀.₅** (concentrazione di substrato per raggiungere metà della Vₘₐₓ), indicando una **minore affinità** dell'enzima per il substrato.
    *   Possibile diminuzione della Vₘₐₓ apparente.
    *   Il CTP si lega e **stabilizza lo stato T inattivo**.

*   **ATP (attivatore allosterico)**: **Sposta la curva verso sinistra**. Questo significa:
    *   **Diminuzione della K₀.₅**, indicando una **maggiore affinità** dell'enzima per il substrato.
    *   L'ATP si lega e **stabilizza lo stato R attivo**.

> [!warning] Enfasi docente
> Il concetto chiave è che **CTP e ATP competono per lo stesso sito allosterico** sulle subunità regolatorie. A seconda delle concentrazioni relative dei due nucleotidi nella cellula, prevarrà l'azione inibitoria o attivatoria.

---

## BLOCCO 13 — Logica biologica della regolazione di ATCase

La ragione per cui il **CTP** agisce da inibitore è intuitiva: è il **prodotto finale della via**. Un'alta concentrazione di CTP segnala che la cellula ha una scorta sufficiente di nucleotidi pirimidinici e attiva un **feedback negativo** per fermare la sintesi a monte, evitando sprechi.

La domanda più interessante è: **perché l'ATP agisce da attivatore?**
L'ATP non è solo la "moneta energetica" della cellula, ma è anche un **nucleotide purinico**. Un'alta concentrazione di ATP segnala due cose:
1.  La cellula ha **energia disponibile** per sostenere processi biosintetici come la sintesi nucleotidica.
2.  La cellula ha un'**abbondanza di nucleotidi purinici**.

Poiché il DNA e l'RNA sono sintetizzati utilizzando **sia purine che pirimidine** in proporzioni bilanciate, ha senso biologico che un eccesso di purine (segnalato dall'ATP) **stimoli la sintesi delle pirimidine** (attivando l'ATCase) per mantenere l'equilibrio necessario per la replicazione e la trascrizione.

---

## BLOCCO 14 — Definizione di isoenzimi

Gli **isoenzimi** sono diverse forme dello stesso enzima. Sono codificati da **geni diversi**, quindi sono proteine diverse, che catalizzano **la stessa reazione**. Essendo enzimi diversi, possono avere **parametri cinetici diversi**, come velocità massima e costante di affinità per il substrato.

> [!warning] Enfasi docente
> Ripeto: gli isoenzimi catalizzano la stessa reazione, ma sono codificati da geni diversi. Geni diversi, proteine diverse, stessa reazione.

---

## BLOCCO 15 — Esempio di isoenzimi: Lattato deidrogenasi (LDH)

> [immagine di: schema del metabolismo energetico che mostra il glucosio, il piruvato e i suoi tre destini, con evidenza della via verso il lattato]

La <span style="color:#2E7D32">lattato deidrogenasi</span> (LDH) è l'enzima che converte il <span style="color:#E57373">piruvato</span> in <span style="color:#E57373">lattato</span> tramite una reazione di riduzione. [CHEM:piruvato] [CHEM:lattato]
Questa reazione rappresenta uno dei tre possibili destini del piruvato, insieme alla fosforilazione ossidativa (ciclo di Krebs) e alla fermentazione alcolica (nei lieviti).

L'attività della LDH è catalizzata da **diversi isoenzimi**. Esistono **5 isoforme** (LDH-1 fino a LDH-5), codificate da geni diversi, ciascuna con una **diversa specificità tessutale**:

*   **LDH-1:** Espressa in tutti i tessuti (cuore, rene, eritrociti, cervello, leucociti), meno nel muscolo e nel fegato.
*   **LDH-2:** Più espressa negli eritrociti e nel cervello, ma presente anche in cuore e rene.
*   **LDH-3:** Più espressa a livello del cervello e negli eritrociti, poco nel cuore.
*   **LDH-4:** Espressa principalmente negli eritrociti, poco in altri tessuti.
*   **LDH-5:** Prevalentemente espressa a livello di muscolo e fegato.

### Utilizzo diagnostico degli isoenzimi LDH
La diversa espressione tessutale degli isoenzimi viene sfruttata a fini diagnostici. Analizzando il profilo elettroforetico delle LDH nel siero di un paziente, si può risalire al tessuto danneggiato:
*   In un paziente con **infarto del miocardio**, il siero mostrerà una **prevalenza delle isoforme LDH-1 e LDH-2**.
*   In un paziente con **epatite acuta**, il siero mostrerà una **maggiore presenza dell'isoforma LDH-5**.

> [!warning] Enfasi docente
> Gli isoenzimi rivestono ruoli fondamentali all'interno della cellula e sono anche sfruttati da un punto di vista diagnostico come marker di diverse condizioni patologiche.

---

## BLOCCO 16 — Esempio di isoenzimi: Esochinasi e Glucochinasi

> [immagine di: grafico che confronta le curve cinetiche dell'esochinasi (blu) e della glucochinasi (rossa) in funzione della concentrazione di glucosio]

<span style="color:#2E7D32">Esochinasi</span> e <span style="color:#2E7D32">glucochinasi</span> sono due isoenzimi che catalizzano entrambi la stessa reazione fondamentale: la trasformazione del <span style="color:#B8860B">glucosio</span> in <span style="color:#E57373">glucosio-6-fosfato</span>. [CHEM:glucosio] [CHEM:glucosio-6-fosfato]

La rilevanza biologica di avere due isoenzimi per la stessa reazione nasce dalle loro **proprietà cinetiche profondamente diverse**:

| ISOENZIMA | Km per il glucosio | ESPRESSIONE | RUOLO FUNZIONALE |
|---|---|---|---|
| <span style="color:#2E7D32">Esochinasi</span> | **0.05 mM** (bassa Km, alta affinità) | **Costitutiva** (sempre espresso, ubiquitario) | Garantisce la <span style="color:#1565C0">glicolisi</span> in **tutte le cellule**, anche a concentrazioni basse di glucosio. Fornisce energia di base fondamentale. |
| <span style="color:#2E7D32">Glucochinasi</span> | **10 mM** (alta Km, bassa affinità) | **Inducibile** (nel fegato, indotta dall'iperglicemia) | Si attiva **solo a concentrazioni molto elevate di glucosio** (es. dopo un pasto). Gestisce l'eccesso di zucchero, indirizzandolo principalmente verso la sintesi di glicogeno per immagazzinamento. |

**Spiegazione cinetica:**
*   La curva dell'<span style="color:#2E7D32">esochinasi</span> (blu) mostra una **velocità elevata già a basse concentrazioni di substrato**. Con poco glucosio, l'enzima lavora comunque.
*   La curva della <span style="color:#2E7D32">glucochinasi</span> (rossa) mostra che l'enzima **è attivo solo ad alte concentrazioni di glucosio**. A basse concentrazioni, la sua attività è trascurabile.

> [!warning] Enfasi docente
> L'esochinasi garantisce la glicolisi sempre, in tutte le cellule, in qualsiasi condizione di glicemia. La glucochinasi, invece, è attiva solo a concentrazioni di glucosio molto elevate e serve per gestire l'eccesso.

---

## BLOCCO 17 — Modificazioni covalenti reversibili e irreversibili

La regolazione mediante **modificazione covalente reversibile** modula le proprietà catalitiche attraverso la formazione o rimozione di legami covalenti.

### Modifiche Covalenti Reversibili
1.  **Fosforilazione:** Il donatore del gruppo fosfato è l'<span style="color:#81C784">ATP</span> (adenosina trifosfato).
2.  **Acetilazione:** Il donatore è l'<span style="color:#E57373">acetil-CoA</span>. Un esempio è la regolazione degli **istoni**, dove l'acetilazione regola l'apertura della cromatina e l'accesso al DNA. [CHEM:acetil-CoA]

### Modifiche Covalenti Irreversibili
Queste modifiche sono permanenti.
*   **Miristolazione:** Aggiunta di un gruppo miristoile. Importante nella regolazione del signaling delle **proteine G**.
*   **ADP-ribosilazione:** Modifica l'attività di molti enzimi.
*   **Farnesilazione:** Aggiunta di un gruppo farnesilico (es. nelle proteine **Ras**). Questa "coda" idrofobica permette l'ancoraggio delle proteine alla membrana plasmatica.
*   **Carbossilazione:** Esempio nella **trombina** per regolare la coagulazione.
*   **Solfatazione:** Vista nei proteoglicani.
*   **Ubiquitinazione:** Aggiunta della piccola proteina **ubiquitina**. Serve per regolare il ciclo cellulare (es. cicline) o per targettare le proteine verso il proteasoma per la degradazione.

> [!warning] Enfasi docente
> La fosforilazione è di gran lunga la modificazione covalente **più comune** nei sistemi biologici per regolare l'attività proteica.

---

## BLOCCO 18 — Il meccanismo della fosforilazione

> [immagine di: schema del ciclo di fosforilazione/deposforilazione di una serina con intervento di chinasi, ATP, fosfatasi e acqua]

La **fosforilazione** è una modificazione covalente reversibile che aggiunge un gruppo fosfato a residui specifici di una proteina.

*   **Residui bersaglio:** Solo alcuni aminoacidi possono essere fosforilati: **serina, treonina, tirosina** e, meno comunemente, **istidina**.
*   **Donatore del fosfato:** <span style="color:#81C784">ATP</span> (adenosina trifosfato).
*   **Enzimi catalizzatori:**
    *   **Chinasi:** Catalizzano il **trasferimento del gruppo fosfato** dall'<span style="color:#81C784">ATP</span> alla proteina bersaglio, rilasciando <span style="color:#81C784">ADP</span>. Attivano l'enzima.
    *   **Fosfatasi:** Catalizzano la **rimozione del gruppo fosfato** (idrolisi) dalla proteina, rilasciando fosfato inorganico (Pi). Disattivano l'enzima. [REACTION:Proteina-OH + ATP -> Proteina-O-P + ADP]

**Perché è un meccanismo efficiente di regolazione?**
1.  **Modifica elettrostatica:** Il gruppo fosfato ha **carica negativa**. La sua aggiunta o rimozione altera drasticamente le interazioni elettrostatiche e la struttura tridimensionale della proteina.
2.  **Velocità:** Fosforilazione e defosforilazione avvengono in **frazioni di secondo**.
3.  **Specificità:** Le chinasi sono **altamente specifiche**. Riconoscono una precisa **sequenza consenso** nella proteina bersaglio prima di fosforilarla.

---

## BLOCCO 19 — Amplificazione del segnale tramite fosforilazione a cascata

> [immagine di: schema di amplificazione a cascata del segnale dell'adrenalina con attivazione sequenziale di chinasi]

La fosforilazione è cruciale per l'**amplificazione del segnale** nella trasduzione.

**Esempio (adrenalina/epinefrina):**
1.  Una molecola di <span style="color:#C2185B">adrenalina</span> si lega al suo recettore.
2.  L'attivazione innesca una cascata che attiva una chinasi (es. PKA).
3.  **Una singola chinasi attivata può fosforilare (e quindi attivare) centinaia di molecole target** (enzimi).
4.  Ogni enzima target attivato può a sua volta processare molti substrati, amplificando ulteriormente il segnale.

Il risultato è un'amplificazione esponenziale: da un segnale iniziale (1 molecola) si può arrivare ad attivare migliaia di effettori finali.

---

## BLOCCO 20 — Regolazione fine mediante fosforilazione multipla

> [immagine di: struttura schematica della glicogeno sintasi con i diversi siti di fosforilazione N-terminale e C-terminale]

Un singolo enzima target può essere regolato in modo **molto preciso e fine** essendo il substrato di **più chinasi diverse**. Un esempio classico è la <span style="color:#2E7D32">glicogeno sintasi</span>, un enzima fondamentale per la sintesi del glicogeno.

*   La <span style="color:#2E7D32">glicogeno sintasi</span> presenta un'estremità N-terminale e una C-terminale, con **molti siti di fosforilazione** distinti sulla sua struttura.
*   **Diverse chinasi specifiche** possono fosforilarla, ognuna su un sito particolare.
*   Lo stato di attivazione/inattivazione finale dell'enzima deriva dalla **sommatoria** (e spesso dalla **sequenza temporale**) di tutte queste fosforilazioni.
*   In alcuni casi, la fosforilazione da parte di una chinasi è un **prerequisito** affinché un'altra chinasi possa agire sullo stesso enzima. Questo è un meccanismo di controllo a cascata.

> [!warning] Enfasi docente
> La regolazione di un dato enzima spesso coinvolge **più chinasi** che devono agire in sequenza. È necessario mantenere una determinata sequenza temporale: un enzima può essere fosforilato da una chinasi, ma quella reazione non procede fino a quando uno specifico residuo di serina non sarà a sua volta fosforilato da un'altra chinatica.

**Riepilogo rapido:**
*   **Fosforilazione**: Regolazione reversibile, spesso multipla e sequenziale, che modula il grado di attività.

---

## BLOCCO 21 — Regolazione mediante attivazione proteolitica

L'altro metodo di controllo dell'attività enzimatica è mediante **attivazione proteolitica**. Questo significa attivazione mediante **taglio proteolitico** della proteina, che la rende attiva. Questa è una modifica **covalente e irreversibile**.

Alcuni enzimi sono sintetizzati come **precursori inattivi**, chiamati **zimogeni** o **proenzimi**. Sono molecole potenzialmente in grado di svolgere la loro attività, ma per essere effettivamente attive devono subire il taglio di specifici legami peptidici, operato da enzimi regolatori specifici.

### Enzimi soggetti a questa regolazione
Le proteine che necessitano di questa regolazione sono prevalentemente gli **enzimi digestivi**, coinvolti nella digestione del cibo. Due esempi principali:
1.  **<span style="color:#2E7D32">Tripsina</span>**: un'idrolasi che taglia le proteine assunte con la dieta in peptidi più piccoli e aminoacidi.
2.  **<span style="color:#2E7D32">Chimotripsina</span>**: un altro enzima proteolitico digestivo, appartenente alla famiglia delle **serine proteasi**. Catalizza la rottura di legami peptidici specifici.

> [!warning] Enfasi docente
> Tripsina e chimotripsina **non sono sintetizzate** a livello cellulare in forma attiva. Devono essere attivate mediante digestione proteolitica da altre proteine (enzimi) per evitare danni ai tessuti che le producono. [INCOMPLETO]

**Riepilogo rapido:**
*   **Attivazione proteolitica**: Regolazione irreversibile mediante taglio di uno zimogeno (precursore inattivo) per generare l'enzima attivo. Tipica degli enzimi digestivi.

---

## APPENDICE TABELLARE

*Riepilogo aggregato della lezione per ripasso rapido e generazione flashcard.*

### Inibitori Enzimatici Irreversibili

| INIBITORE | TIPOLOGIA | ENZIMA BERSAGLIO | MECCANISMO D'AZIONE | EFFETTO BIOLOGICO | IMMAGINE |
|---|---|---|---|---|---|
| <span style="color:#E57373">Penicillina</span> | Inibitore Suicida | <span style="color:#2E7D32">Glicopeptide transpeptidasi</span> (batterica) | Legame covalente irreversibile tra l'anello beta-lattamico e il -OH di una Serina del sito attivo. | Blocco della sintesi della parete cellulare batterica → Azione antibiotica. | |
| <span style="color:#E57373">Aspirina</span> (Acido Acetilsalicilico) | Inibitore Gruppo-Specifico | <span style="color:#2E7D32">Cicloossigenasi (COX)</span> / Prostaglandina sintetasi (umana) | Trasferimento covalente del gruppo acetilico al -OH della Serina 530 nel sito attivo. | Inibizione della sintesi delle prostaglandine → Azione antinfiammatoria, antipiretica, analgesica. | |

### Confronto Tipologie di Inibizione

| TIPOLOGIA | MECCANISMO | LEGAME | ESEMPIO | IMMAGINE |
|---|---|---|---|---|
| Analoghi del Substrato | Molecola strutturalmente simile al substrato si lega al sito attivo. | Covalente, irreversibile. | (Non specificato nella lezione) | |
| Inibitori Suicidi | Durante la catalisi, genera intermedi che modificano covalentemente il sito attivo. | Covalente, irreversibile. | <span style="color:#E57373">Penicillina</span> | |
| Inibitori Gruppo-Specifici | Reagisce con specifiche catene laterali di amminoacidi nel sito attivo. | Covalente, irreversibile. | <span style="color:#E57373">Aspirina</span> | |

### Meccanismi di reazione con più substrati

| TIPO | DESCRIZIONE | ORDINE DI LEGAME | ESEMPIO BIOLOGICO | SUBSTRATI | IMMAGINE |
|---|---|---|---|---|---|
| **Sequenziale Ordinato** | Tutti i substrati si legano prima del rilascio dei prodotti | Ordine fisso e obbligatorio | <span style="color:#2E7D32">Lattato deidrogenasi</span> | <span style="color:#00ACC1">NADH</span>, <span style="color:#E57373">piruvato</span> | |
| **Sequenziale Casuale** | Tutti i substrati si legano prima del rilascio dei prodotti | Ordine casuale | <span style="color:#2E7D32">Creatina chinasi</span> | <span style="color:#81C784">ATP</span>, <span style="color:#E57373">creatina</span> | |
| **Ping-Pong (Doppio spostamento)** | Un substrato si lega, viene convertito e rilasciato; poi si lega il secondo | Sequenziale obbligato ma con rilascio intermedio | <span style="color:#2E7D32">Transaminasi</span> | Substrato A, Substrato B | |

### Confronto Cinetica Enzimatica

| TIPO DI CINETICA | FORMA DELLA CURVA | DESCRIZIONE | ESEMPIO | IMMAGINE |
|---|---|---|---|---|
| **Michaelis-Menten** | Iperbolica | Seguita dalla maggior parte degli enzimi. Velocità aumenta rapidamente poi plateau. | Enzimi non regolatori | |
| **Allosterica** | Sigmoidea (a "S") | Seguita da enzimi regolatori. Lenta a basse [S], poi accelerazione marcata. | <span style="color:#2E7D32">Enzimi allosterici</span> (es. <span style="color:#2E7D32">glucochinasi</span>) | |

### Caratteristiche Enzimi Allosterici

| CARATTERISTICA | DESCRIZIONE | NOTE |
|---|---|---|
| **Definizione** | Enzimi regolatori la cui attività è modulata da legame di effettori in sito diverso dall'attivo. | |
| **Sito di legame** | Sito allosterico (regolatorio). | Distinto dal sito attivo. |
| **Effettori** | Modulatori (positivi/attivatori o negativi/inibitori). | Legame reversibile. |
| **Struttura tipica** | Multimerica (più subunità). | Eccezioni esistono (es. <span style="color:#2E7D32">glucochinasi</span>). |
| **Meccanismo** | Modificazione conformazionale indotta dal legame del modulatore, trasmessa alla subunità catalitica. | Altera affinità per il substrato e/o Vmax. |
| **Modello attuale** | Modello Sequenziale. | Cambiamento conformazionale graduale e comunicato tra subunità. |

### Enzimi Allosterici - Esempio ATCase

| ENZIMA | REAZIONE CATALIZZATA | SUBSTRATI | PRODOTTO | REGOLATORI ALLOSTERICI | CONFORMAZIONI | IMMAGINE |
|---|---|---|---|---|---|---|
| **Aspartato Transcarbamilasi (ATCase)** | Sintesi di N-carbamil aspartato | <span style="color:#E65100">Aspartato</span> + Carbamil fosfato | N-carbamil aspartato | **Negativo:** <span style="color:#81C784">CTP</span> (prodotto finale della via)<br>**Positivo:** <span style="color:#81C784">ATP</span> (nucleotide purinico) | **Stato T (Inattivo):** Stabilizzato da <span style="color:#81C784">CTP</span><br>**Stato R (Attivo):** Stabilizzato da <span style="color:#81C784">ATP</span> e substrato | |

### Effetto dei Modulatori Allosterici sulla Cinetica

| MODULATORE | TIPO | EFFETTO SULLA CURVA | EFFETTO SU K₀.₅ | EFFETTO SULL'AFFINITÀ | STATO STABILIZZATO | IMMAGINE |
|---|---|---|---|---|---|---|
| <span style="color:#81C784">CTP</span> | Inibitore (Negativo) | La abbassa e sposta a DESTRA | Aumenta | Diminuisce | Stato T (Inattivo) | |
| <span style="color:#81C784">ATP</span> | Attivatore (Positivo) | La sposta a SINISTRA | Diminuisce | Aumenta | Stato R (Attivo) | |

### Isoenzimi trattati

| ISOENZIMA | REAZIONE CATALIZZATA | PROPRIETÀ CHIAVE | SIGNIFICATO FUNZIONALE / DIAGNOSTICO | IMMAGINE |
|---|---|---|---|---|
| **LDH-1 a LDH-5** (<span style="color:#2E7D32">Lattato Deidrogenasi</span>) | <span style="color:#E57373">Piruvato</span> → <span style="color:#E57373">Lattato</span> | 5 isoforme con diversa specificità tessutale. | **Diagnostico:** Profilo elettroforetico nel siero indica danno tissutale (es. LDH-1/2 in infarto; LDH-5 in epatite). | |
| <span style="color:#2E7D32">Esochinasi</span> | <span style="color:#B8860B">Glucosio</span> → Glucosio-6-fosfato | Km bassa (0.05 mM). Espressione costitutiva e ubiquitaria. | Garantisce energia di base (<span style="color:#1565C0">glicolisi</span>) in tutte le cellule, indipendentemente dalla glicemia. | |
| <span style="color:#2E7D32">Glucochinasi</span> | <span style="color:#B8860B">Glucosio</span> → Glucosio-6-fosfato | Km alta (10 mM). Espressione inducibile (fegato, da iperglicemia). | Gestisce picchi glicemici post-prandiali, indirizzando il glucosio in eccesso verso deposito (glicogeno). | |

### Modificazioni Covalenti delle Proteine

| MODIFICA | TIPO | DONATORE | ESEMPIO/FUNZIONE | IMMAGINE |
|---|---|---|---|---|
| **Fosforilazione** | Reversibile | <span style="color:#81C784">ATP</span> | Regolazione enzimatica generale (es. chinasi/fosfatasi) | |
| **Acetilazione** | Reversibile | <span style="color:#E57373">Acetil-CoA</span> | Regolazione degli istoni (accesso al DNA) | |
| **Miristolazione** | Irreversibile | - | Regolazione delle **proteine G** (signaling) | |
| **Farnesilazione** | Irreversibile | - | Ancora proteine (es. **Ras**) alla membrana | |
| **Ubiquitinazione** | Irreversibile | Ubiquitina | Targettaggio al proteasoma per degradazione; regolazione ciclo cellulare | |

### Meccanismo della Fosforilazione

| CONCETTO | DESCRIZIONE | ELEMENTI CHIAVE | IMMAGINE |
|---|---|---|---|
| **Residui bersaglio** | Aminoacidi fosforilabili | Serina, Treonina, Tirosina, (Istidina) | |
| **Enzimi** | Catalizzano la reazione | **Chinasi** (aggiungono P da ATP), **Fosfatasi** (rimuovono P per idrolisi) | |
| **Vantaggi** | Perché è un buon meccanismo regolatorio | 1. Modifica carica/proteina<br>2. Veloce (frazioni di secondo)<br>3. Specifico (sequenza consenso)<br>4. **Amplifica il segnale** (cascata) | |

### Meccanismi di Regolazione Enzimatica

| MECCANISMO | NATURA | ESEMPIO | CARATTERISTICHE | IMMAGINE |
|---|---|---|---|---|
| **Fosforilazione multipla** | Covalente, reversibile | <span style="color:#2E7D32">Glicogeno sintasi</span> | Azione di più chinasi su siti specifici; effetto finale è la sommatoria delle fosforilazioni; richiede spesso una sequenza temporale. | |
| **Attivazione proteolitica** | Covalente, irreversibile | <span style="color:#2E7D32">Tripsina</span>, <span style="color:#2E7D32">Chimotripsina</span> | L'enzima è sintetizzato come zimogeno (precursore inattivo); l'attivazione avviene per taglio proteolitico da parte di un altro enzima. Tipico degli enzimi digestivi. | |

---

*Fine sbobina — Lezione su Inibizione Irreversibile e Regolazione Enzimatica*
*Argomenti correlati: → Inibizione enzimatica reversibile · → Regolazione allosterica · → Cinetica enzimatica · → Cinetica di Michaelis-Menten · → Esempi di enzimi allosterici nel metabolismo · → Modelli di cooperatività · → Sintesi dei nucleotidi · → Metabolismo del glucosio · → Glicolisi · → Sintesi del Glicogeno · → Proteine G e Trasduzione del Segnale · → Metabolismo del glicogeno · → Enzimi digestivi · → Cascate di fosforilazione*