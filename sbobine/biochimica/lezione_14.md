# Biochimica — Lezione: Trasporto attraverso le membrane biologiche

> **Argomento:** Principi, meccanismi e classificazione del trasporto transmembrana, dai gradienti ionici ai canali
> **Blocchi presenti:** Introduzione e importanza · Concentrazioni ioniche chiave · Principi del trasporto passivo · Diffusione semplice · Diffusione facilitata: concetti generali · Trasportatori (Carrier) · Canali ionici · Classificazione carrier vs. canali · Esempi di trasporto passivo: GLUT e antiporto bicarbonato-cloro · Classificazione dei trasportatori · Trasporto attivo: primario e secondario · ATPasi di tipo P (meccanismo generale) · Pompa SERCA · Pompa Na⁺/K⁺ · Trasportatori ABC · Trasportatore sodio-glucosio (SGLT) · Acquaporine · Canali ionici: selettività e modelli di regolazione · Canali ligando-dipendenti · Canale TRICB e correlazione clinica

---

## BLOCCO 1 — Introduzione e importanza del trasporto transmembrana

Il trasporto attraverso le membrane biologiche è un elemento essenziale per la vita cellulare. Le cellule e i loro organelli non sono entità isolate; devono comunicare e scambiare molecole sia internamente (tra organelli e citosol) che con l'ambiente esterno. Questo scambio è fondamentale per:
* Garantire l'ingresso delle macromolecole necessarie per i processi catabolici.
* Rilasciare i prodotti dei processi anabolici.
* Mantenere una corretta omeostasi del tessuto in cui la cellula è inserita.
* Eliminare le sostanze tossiche derivanti dal metabolismo.

> [immagine di: schema generale di una cellula che mostra scambi tra ambiente extracellulare, membrana plasmatica, citosol e organelli]

---

## BLOCCO 2 — Concentrazioni ioniche chiave: ambiente interno vs. esterno

Esiste una marcata diversità tra l'ambiente intracellulare e quello extracellulare per quanto riguarda la concentrazione di specifici ioni, che hanno un ruolo fondamentale nelle reazioni biochimiche. È importante comprendere l'ordine di grandezza di queste differenze per quattro elementi chiave:

### 1. Sodio (Na⁺)
* **Concentrazione extracellulare:** 140 mM
* **Concentrazione intracellulare:** 10 mM
Il <span style="color:#E57373">sodio</span> è sempre più concentrato all'esterno della cellula. Questa differenza è possibile perché le membrane biologiche non sono assolutamente permeabili, altrimenti si raggiungerebbe rapidamente l'equilibrio.

### 2. Potassio (K⁺)
* **Concentrazione extracellulare:** 4 mM
* **Concentrazione intracellulare:** 140 mM
Il <span style="color:#E57373">potassio</span> presenta una situazione opposta a quella del sodio, essendo molto più concentrato all'interno della cellula. Insieme al sodio, è rilevante nel determinare l'esistenza di un **potenziale di membrana**.

### 3. Calcio (Ca²⁺)
* **Concentrazione extracellulare:** 2.5 mM
* **Concentrazione intracellulare (citosolica):** 0.1 µM
Il <span style="color:#E57373">calcio</span> ha una concentrazione extracellulare molto più alta. Tuttavia, all'interno della cellula, una concentrazione simile a quella extracellulare si trova in un organello specifico che funge da riserva: il **reticolo endoplasmatico**. Il calcio è un importante messaggero intracellulare e un cofattore per diversi enzimi metabolici.

> [!warning] Enfasi docente
> Il rilascio di calcio dal reticolo endoplasmatico è un meccanismo chiave nella trasduzione del segnale. Ad esempio, nell'attivazione della via dell'angiotensina, il calcio rilasciato determina l'attivazione della <span style="color:#2E7D32">proteina chinasi C</span>, che poi agisce su vari target cellulari.

### 4. Glucosio
* **Concentrazione ematica (extracellulare):** ~4.5-5.5 mM
* **Concentrazione intracellulare:** Generalmente più bassa.
La concentrazione intracellulare di <span style="color:#B8860B">glucosio</span> è tipicamente inferiore perché, una volta entrato, viene immediatamente catabolizzato (ad esempio, attraverso la <span style="color:#1565C0">glicolisi</span>) o accumulato sotto forma di <span style="color:#B8860B">glicogeno</span>. Un'eccezione sono gli epatociti, che possono accumulare glucosio in alte concentrazioni per poi rilasciarlo ai tessuti periferici quando necessario. [CHEM:glucosio]

> [!warning] Enfasi docente
> Ricordate che la concentrazione di glucosio intracellulare è generalmente inferiore a quella extracellulare. Questo concetto sarà fondamentale quando parleremo del **trasportatore del glucosio**.

**Riepilogo rapido — Gradienti ionici:**
* **Na⁺:** Alto fuori, basso dentro.
* **K⁺:** Basso fuori, alto dentro.
* **Ca²⁺:** Alto fuori, bassissimo nel citosol (riserva nel RE).
* **Glucosio:** Più alto nel sangue, generalmente più basso nel citosol.

---

## BLOCCO 3 — Principi del trasporto passivo: gradiente di concentrazione ed elettrochimico

### Trasporto di soluti neutri
Se un soluto è presente in concentrazioni diverse in due compartimenti separati da una membrana **permeabile** a quel soluto, si verificherà un movimento spontaneo.
* Il soluto si sposta dalla zona in cui è **più concentrato** a quella in cui è **meno concentrato**.
* Questo movimento è definito **secondo gradiente di concentrazione**.
* Il sistema raggiungerà una condizione di **equilibrio**, dove le concentrazioni nei due compartimenti sono uguali (il passaggio molecolare continua, ma non c'è cambiamento netto).

### Trasporto di soluti carichi (ioni)
Per le molecole dotate di carica elettrica (ioni) la situazione è più complessa. Il loro passaggio attraverso una membrana permeabile è guidato non solo dal gradiente di concentrazione, ma anche dalla differenza di carica tra i due lati della membrana.
* La forza motrice combinata si chiama **gradiente elettrochimico**.
* All'equilibrio, il sistema raggiungerà una condizione in cui sia la concentrazione che la distribuzione delle cariche sono bilanciate.

> [!warning] Enfasi docente
> I due concetti base da tenere sempre presenti sul trasporto spontaneo sono:
> 1. **Gradiente di concentrazione:** guida il passaggio di molecole neutre.
> 2. **Gradiente elettrochimico:** guida il passaggio di molecole cariche (ioni).

**Riepilogo rapido — Forze motrici del trasporto:**
* **Soluto neutro:** Si muove spontaneamente secondo il suo **gradiente di concentrazione** (da [alto] a [basso]).
* **Soluto carico (ione):** Si muove spontaneamente secondo il suo **gradiente elettrochimico** (combinazione di gradiente di concentrazione e gradiente elettrico).

---

## BLOCCO 4 — Diffusione semplice

> [immagine di: schema del doppio strato fosfolipidico con molecole idrofobiche e piccole molecole apolari che lo attraversano]

La **diffusione semplice** è il meccanismo di trasporto più basilare. Una molecola può diffondere semplicemente attraverso la membrana se:
*   È una molecola **non polare (idrofobica)**.
*   Oppure è una molecola **molto piccola**.

**Esempi di molecole che attraversano per diffusione semplice:**
*   Anidride carbonica (CO₂)
*   Ossido di azoto (NO) – importante ligando per la trasduzione del segnale.
*   Ormoni steroidei (molecole più grandi ma idrofobiche).

**Forza motrice:** Il passaggio è guidato esclusivamente dal **gradiente di concentrazione** del soluto. Non richiede supporto energetico aggiuntivo (ATP) né proteine di trasporto.
*   **Esempio applicativo:** Durante il catabolismo, l'<span style="color:#E57373">anidride carbonica</span> prodotta in alta concentrazione all'interno della cellula viene espulsa all'esterno, dove la concentrazione è minore, semplicemente per diffusione semplice attraverso la membrana. [CHEM:anidride carbonica]

---

## BLOCCO 5 — Diffusione facilitata: concetti generali

Per le **molecole polari o cariche** (come piccoli ioni), attraversare la regione idrofobica centrale della membrana è estremamente difficile e lento. Questo passaggio diretto non è compatibile con le necessità fisiologiche della cellula.

La soluzione è l'utilizzo di **proteine integrali di membrana** che facilitano il passaggio. Il loro meccanismo ricorda la cinetica enzimatica:
*   La proteina si lega al soluto tramite **interazioni deboli non covalenti** (legami idrogeno, interazioni ioniche).
*   Questa interazione **abbassa l'energia necessaria** al soluto idrofilico per attraversare la regione idrofobica.
*   Il trasporto avviene sempre **secondo gradiente** (di concentrazione o elettrochimico), senza consumo diretto di ATP.

Le proteine che mediano la diffusione facilitata si dividono in due grandi categorie: **Trasportatori (Carrier)** e **Canali**.

---

## BLOCCO 6 — Trasportatori (Carrier)

> [immagine di: modello schematico di un trasportatore che lega il soluto e cambia conformazione per traslocarlo]

I trasportatori sono proteine integrali di membrana caratterizzate da:

1.  **Alta specificità:** Legano in modo specifico il soluto da trasportare tramite interazioni non covalenti. Esiste una vasta famiglia di trasportatori, ciascuno per molecole specifiche.
2.  **Saturabilità:** La velocità di trasporto ha un massimo (Vmax). Quando tutti i siti di legame dei trasportatori sono occupati, aggiungere più soluto non aumenta il flusso.
    *   La velocità di passaggio dipende quindi non solo dalla concentrazione del soluto, ma anche dal **numero di trasportatori** presenti in membrana.
    *   La cellula può regolare il trasporto modulando il numero di trasportatori sulla membrana (es. tramite traslocazione da vescicole di deposito).
3.  **Meccanismo "a porta alternata":** Il trasportatore cambia conformazione. Immaginandolo come un passaggio con due porte, queste non sono mai aperte contemporaneamente. Il soluto si lega da un lato, la conformazione cambia, e il soluto viene rilasciato dall'altro lato.

> [!warning] Enfasi docente
> Le due caratteristiche fondamentali che definiscono un trasportatore sono la **specificità** e la **saturabilità**.

---

## BLOCCO 7 — Canali ionici

> [immagine di: struttura di un canale ionico che forma un poro idrofilico attraverso la membrana]

I canali sono un'altra classe di proteine per il trasporto facilitato, con caratteristiche distinte:

1.  **Stereospecificità ridotta:** Hanno una specificità per il soluto generalmente meno stringente rispetto ai trasportatori. Alcuni canali possono trasportare tipi diversi di ioni (es. sodio e potassio; sodio e calcio), mentre altri sono altamente specifici (es. solo per il potassio).
2.  **Non saturabilità:** Il flusso di ioni attraverso un canale aperto è molto vicino al flusso libero, come se non ci fosse ostacolo. Non si verifica saturazione perché il meccanismo non prevede un legame specifico e saturabile.
3.  **Meccanismo "a porta singola":** Il canale ha essenzialmente due stati: **aperto** o **chiuso**. Quando è aperto, gli ioni fluiscono liberamente attraverso il poro idrofilico che attraversa la membrana.

> [!warning] Enfasi docente
> La distinzione cruciale tra trasportatore e canale è la **saturabilità**. Il trasportatore è saturabile, il canale no. Questo deriva dal diverso meccanismo: il trasportatore lega il soluto e cambia conformazione (meccanismo più lento e limitato), mentre il canale, una volta aperto, permette un flusso libero.

---

## BLOCCO 8 — Classificazione: Carrier (trasportatori) vs. Canali

La distinzione fondamentale tra un **carrier** (o trasportatore) e un **canale** è la **saturabilità**. Il trasportatore è saturabile, mentre il canale non lo è.

> [immagine di: schema comparativo di un canale (porta singola) e un carrier (porta doppia alternata)]

*   **Modello del canale:** Si può immaginare come una porta singola. Quando è aperta, le molecole passano liberamente; quando è chiusa, non passano. Non c'è interazione specifica che facilita il passaggio, quindi il flusso non si satura.
*   **Modello del carrier (trasportatore):** Si può immaginare come un passaggio con due porte che non sono mai aperte contemporaneamente. Per far passare una molecola, deve avvenire una sequenza: interazione con il soluto, cambiamento conformazionale che chiude la prima porta e apre la seconda, rilascio del soluto. Questo meccanismo sequenziale introduce un limite di velocità, rendendo il sistema **saturabile**.

> [!warning] Enfasi docente
> Il concetto di saturabilità è cruciale per distinguere questi due sistemi di trasporto attraverso la membrana.

---

## BLOCCO 9 — Esempi di trasporto passivo

### Esempio 1: I trasportatori del glucosio (GLUT)

> [immagine di: struttura del trasportatore GLUT con 12 alfa-eliche transmembrana]

I trasportatori del glucosio (<span style="color:#2E7D32">GLUT</span>) sono una **famiglia di proteine** (es. <span style="color:#2E7D32">GLUT1</span>, <span style="color:#2E7D32">GLUT2</span>, <span style="color:#2E7D32">GLUT3</span>, <span style="color:#2E7D32">GLUT4</span>) che operano tutti con un meccanismo di **trasporto passivo**. Hanno strutture simili, derivanti da un precursore comune.

*   **Struttura:** Sono proteine integrali di membrana che attraversano il doppio strato con **12 alfa-eliche**. Le estremità N- e C-terminale si trovano all'interno del citoplasma.
*   **Meccanismo di trasporto:**
    1.  Il <span style="color:#B8860B">glucosio</span>, più concentrato all'esterno, si lega a residui amminoacidici specifici all'interno del passaggio formato dalle alfa-eliche.
    2.  Questo legame (non covalente) induce un **cambiamento conformazionale** nel trasportatore.
    3.  Il cambiamento riduce l'affinità per il glucosio, permettendone il rilascio nel citoplasma, dove la concentrazione è più bassa.
    4.  Il rilascio del glucosio induce un secondo cambiamento conformazionale che riporta il trasportatore alla conformazione originale, pronto per un nuovo ciclo.
*   **Architettura della via di trasporto:** Le alfa-eliche hanno residui idrofobici all'esterno (a contatto con i lipidi di membrana) e residui idrofilici all'interno del passaggio, per interagire con il soluto polare.

[CHEM:glucosio]

### Esempio 2: L'antiporto bicarbonato-cloro

> [immagine di: schema dell'antiporto bicarbonato-cloro nei globuli rossi, con direzioni del flusso nei tessuti periferici e nel polmone]

Questo trasportatore è fondamentale per il trasporto dell'<span style="color:#E57373">anidride carbonica</span> (<span style="color:#E57373">CO₂</span>) dal tessuti periferici ai polmoni. È un esempio di **antiporto**, un trasportatore che muove due molecole in **direzioni opposte**.

**A. Nei tessuti periferici (produzione di CO₂):**
1.  La <span style="color:#E57373">CO₂</span>, prodotto di scarto metabolico, diffonde per **diffusione semplice** dalle cellule nei capillari e negli eritrociti.
2.  Negli eritrociti, la <span style="color:#E57373">CO₂</span> reagisce con acqua (reazione catalizzata dall'<span style="color:#2E7D32">anidrasi carbonica</span>) formando **ione bicarbonato** (<span style="color:#E57373">HCO₃⁻</span>) e un protone.
3.  La concentrazione di <span style="color:#E57373">bicarbonato</span> aumenta all'interno dell'eritrocita.
4.  Il **trasportatore bicarbonato-cloro** (antiporto) fa uscire il <span style="color:#E57373">bicarbonato</span> dall'eritrocita nel plasma e, per mantenere l'equilibrio elettrico, fa entrare uno ione **cloruro** (<span style="color:#E57373">Cl⁻</span>).
5.  Il <span style="color:#E57373">bicarbonato</span> viene così trasportato dal plasma verso i polmoni.

**B. Nei polmoni (eliminazione di CO₂):**
1.  Nel capillare polmonare, la concentrazione di <span style="color:#E57373">bicarbonato</span> è alta nel plasma.
2.  Lo stesso antiporto opera in direzione inversa (trasporto passivo guidato dal gradiente): il <span style="color:#E57373">bicarbonato</span> entra nell'eritrocita e il <span style="color:#E57373">cloruro</span> esce.
3.  All'interno dell'eritrocita, il <span style="color:#E57373">bicarbonato</span> si ricombina con un protone (reazione inversa catalizzata) per formare <span style="color:#E57373">CO₂</span> e acqua.
4.  La <span style="color:#E57373">CO₂</span>, ora più concentrata nell'eritrocita, diffonde per **diffusione semplice** nel plasma alveolare e viene esalata.

> [!warning] Enfasi docente
> Questo esempio è importante per due motivi: 1) la sua rilevanza fisiologica nel garantire il trasporto di CO₂ nel sangue, e 2) perché è un ottimo esempio di antiporto che sottolinea come questi trasportatori funzionino unicamente in base ai gradienti di concentrazione.

[CHEM:anidride carbonica] [CHEM:bicarbonato] [CHEM:cloruro]

---

## BLOCCO 10 — Classificazione dei trasportatori

I trasportatori di membrana vengono classificati in letteratura scientifica in base al numero e alla direzione dei soluti trasportati. Questa classificazione vale sia per i **trasportatori passivi** che per quelli **attivi**.

| TIPO | DESCRIZIONE | ESEMPIO CITATO |
|---|---|---|
| **Uniporto** | Trasporta un solo tipo di molecola. | — |
| **Antiporto** (Cotrasporto) | Trasporta due molecole in **direzioni opposte**. | Antiporto bicarbonato-cloro |
| **Simporto** (Cotrasporto) | Trasporta due molecole nella **stessa direzione**. | Trasportatore del glucosio (GLUT) |

La classificazione generale di un trasportatore avviene in due step:
1.  Si definisce se il trasporto è **attivo** o **passivo**.
2.  Si definisce la **modalità** con cui trasferisce il soluto: un solo soluto, due soluti, e se questi vanno nella stessa direzione (simporto) o in direzioni opposte (antiporto).

---

## BLOCCO 11 — Trasporto attivo: primario e secondario

La differenza principale tra trasporto **attivo** e **passivo** risiede nell'**uso di energia**. Il trasporto passivo sfrutta solo il gradiente di concentrazione. Il trasporto attivo, invece, **richiede energia** per trasferire le molecole **contro** il loro gradiente di concentrazione.

Esistono due tipi di trasporto attivo:

### 1. Trasporto attivo primario
In questo tipo, il trasportatore ottiene l'energia necessaria direttamente dall'**idrolisi dell'<span style="color:#81C784">ATP</span>**. L'energia derivante dalla rottura dei legami fosfo-anidridici (spesso il legame gamma) può essere utilizzata per **fosforilare il trasportatore stesso**, innescando un cambiamento conformazionale che sposta il soluto.

### 2. Trasporto attivo secondario
Questo meccanismo è più complesso e coinvolge **due soluti**:
*   **Soluto S:** viene trasportato **contro** il suo gradiente di concentrazione (es. da zona a bassa concentrazione a zona ad alta concentrazione). È il soluto che "ha bisogno" di energia.
*   **Soluto X (molecola "driver"):** viene trasportato **secondo** il suo gradiente di concentrazione (da zona ad alta concentrazione a zona a bassa concentrazione).

Il trasporto attivo secondario permette il movimento di **S contro gradiente**, sfruttando l'**energia liberata** dal movimento secondo gradiente di **X**.

> [!warning] Enfasi docente
> Perché il trasporto secondario non si blocchi, la concentrazione intracellulare della molecola driver **X** deve rimanere bassa. Questo è garantito dall'accoppiamento con un **trasportatore attivo primario** (es. una pompa ATP-dipendente) che espelle continuamente **X** dalla cellula, mantenendo il suo gradiente. Lo schema mostra quindi due trasportatori: uno secondario (che sfrutta il gradiente) e uno primario (che ricostituisce il gradiente).

**Riepilogo rapido — Trasporto Attivo:**
*   **Primario:** Energia diretta da ATP. Trasporto contro gradiente di un singolo soluto.
*   **Secondario:** Energia indiretta dal gradiente di un secondo soluto (X). Trasporto contro gradiente di S accoppiato al trasporto secondo gradiente di X. Richiede una pompa primaria per mantenere il gradiente di X.

---

## BLOCCO 12 — ATPasi di tipo P: meccanismo generale

> [immagine di: struttura generale di un'ATPasi di tipo P con domini N, P, A, M]

I trasportatori della famiglia delle **ATPasi di tipo P** si chiamano così perché i cambiamenti conformazionali necessari per il trasporto richiedono la **fosforilazione e defosforilazione** di un particolare residuo di aspartato in un dominio specifico. Il fosfato (P) deriva dall'idrolisi dell'<span style="color:#81C784">ATP</span>.

Il meccanismo chiave, comune a tutti i membri di questa famiglia, è il seguente:
1.  **Fosforilazione** (da parte dell'<span style="color:#81C784">ATP</span>) di un residuo di aspartato nel dominio P.
2.  Questo determina il **primo cambio conformazionale**, che riduce l'affinità per il soluto e ne causa il rilascio.
3.  **Defosforilazione** del residuo (attività fosfatasica del dominio A).
4.  Questo determina il **secondo cambio conformazionale**, che riporta il trasportatore alla conformazione originale, pronta per un nuovo ciclo.

> [!warning] Enfasi docente
> Nelle ATPasi di tipo P, l'<span style="color:#81C784">ATP</span> è necessario per **fosforilare** il trasportatore (determinando il primo cambio conformazionale) e poi per essere **rimosso** (determinando il secondo cambio). Questo meccanismo sarà diverso nei trasportatori ABC.

---

## BLOCCO 13 — Pompa SERCA

> [immagine di: struttura dettagliata della pompa SERCA con i siti di legame per Ca²⁺ nel dominio M]

La **pompa SERCA** (Sarcoplasmic/Endoplasmic Reticulum Calcium ATPase) è un esempio di ATPasi di tipo P. È una proteina integrale della membrana del **reticolo endoplasmatico** (non della membrana plasmatica) e ha il compito di riportare il <span style="color:#E57373">calcio</span> (Ca²⁺) all'interno del reticolo, terminando il suo ruolo di secondo messaggero nella trasduzione del segnale. [CHEM:calcio]

**Funzione:** Trasporta attivamente il <span style="color:#E57373">calcio</span> dal **citosol** (bassa concentrazione) al **lume del reticolo endoplasmatico** (alta concentrazione). La stechiometria è di **2 ioni Ca²⁺** per ciclo.

**Struttura e domini:**
*   **Dominio M (Membrana):** Dominio transmembrana con eliche alfa. Contiene i **due siti di legame per il Ca²⁺**, posizionati a metà dello spessore della membrana.
*   **Dominio N (Nucleotide):** Dominio citosolico che lega l'<span style="color:#81C784">ATP</span> e ha attività chinasica.
*   **Dominio P (Fosforilazione):** Dominio citosolico in cui un residuo di **aspartato** viene fosforilato.
*   **Dominio A (Attuatore):** Dominio citosolico con attività **fosfatasica**, che rimuove il fosfato.

**Ciclo di trasporto dettagliato:**
1.  **Stato di riposo:** I siti di legame per il Ca²⁺ nel dominio M sono esposti verso il citosol e liberi.
2.  **Legame del substrato:** Quando la concentrazione citosolica di Ca²⁺ aumenta, **due ioni Ca²⁺** si legano al dominio M. L'<span style="color:#81C784">ATP</span> si lega al dominio N.
3.  **Fosforilazione e primo cambio conformazionale:** Il dominio N fosforila l'aspartato nel dominio P. La fosforilazione induce un cambio conformazionale che modifica la struttura del dominio M, riducendo drasticamente la sua affinità per il Ca²⁺.
4.  **Rilascio del substrato:** Il Ca²⁺ viene così rilasciato nel lume del reticolo endoplasmatico.
5.  **Defosforilazione e secondo cambio conformazionale:** Il dominio A, con la sua attività fosfatasica, rompe il legame fosfo-estere, rimuovendo il fosfato. Questo causa un secondo cambio conformazionale che riporta la pompa alla sua conformazione originale, con i siti di legame esposti nuovamente verso il citosol.

[REACTION:2 Ca²⁺(cit) + ATP -> 2 Ca²⁺(lum) + ADP + Pi]

---

## BLOCCO 14 — Pompa Na⁺/K⁺ ATPasi

> [immagine di: schema del ciclo di trasporto della pompa Na⁺/K⁺ ATPasi che mostra le due conformazioni e i siti di legame per Na⁺ e K⁺]

La **pompa sodio-potassio** (Na⁺/K⁺ ATPase) è un altro esempio di ATPasi di tipo P, **ubiquitario** sulla **membrana plasmatica**. Il suo meccanismo è **assolutamente identico** a quello della pompa SERCA, ma con peculiarità di stechiometria, direzione e funzione fisiologica cruciale.

**Funzione:** Trasporta attivamente il <span style="color:#E57373">sodio</span> (Na⁺) e il <span style="color:#E57373">potassio</span> (K⁺) contro i loro gradienti di concentrazione.
*   **Stechiometria:** **3 Na⁺** in uscita, **2 K⁺** in ingresso per ciclo.
*   **Direzione:** Espelle **3 Na⁺** dall'interno (dove è meno concentrato) all'esterno (dove è più concentrato). Importa **2 K⁺** dall'esterno (dove è meno concentrato) all'interno (dove è più concentrato). [CHEM:sodio] [CHEM:potassio]

**Ciclo di trasporto (sovrapponibile a SERCA):**
1.  **Legame del Na⁺:** In condizioni di riposo, il dominio M è aperto verso l'interno della cellula e ha alta affinità per il Na⁺. **Tre ioni Na⁺** si legano.
2.  **Fosforilazione e rilascio del Na⁺:** L'<span style="color:#81C784">ATP</span> fosforila un aspartato nel dominio P. Il cambio conformazionale risultante riduce l'affinità per il Na⁺, che viene rilasciato all'esterno, e **aumenta l'affinità per il K⁺**.
3.  **Legame del K⁺:** **Due ioni K⁺** si legano dal lato esterno.
4.  **Defosforilazione e rilascio del K⁺:** Il dominio A defosforila il residuo di aspartato. Il secondo cambio conformazionale riporta la pompa alla conformazione originale, riduce l'affinità per il K⁺, che viene rilasciato all'interno, e ripristina l'alta affinità per il Na⁺.

**Conseguenza fisiologica fondamentale:** Questo trasporto **netto di una carica positiva verso l'esterno** (3 Na⁺ out, 2 K⁺ in) è il principale responsabile della generazione e del mantenimento del **potenziale di membrana a riposo** (negativo all'interno della cellula).

[REACTION:3 Na⁺(in) + 2 K⁺(out) + ATP -> 3 Na⁺(out) + 2 K⁺(in) + ADP + Pi]

---

## BLOCCO 15 — Trasportatori della famiglia ABC (ATP-Binding Cassette)

> [immagine di: struttura schematica di un trasportatore ABC con i due domini transmembrana e i due domini citosolici leganti ATP]

I trasportatori della famiglia **ABC** (ATP-Binding Cassette) sono un altro esempio di trasporto attivo primario, ma con un meccanismo diverso. Sono di grande rilevanza clinica, in particolare in oncologia.

**Caratteristiche generali:**
*   **Struttura:** Possiedono due domini transmembrana collegati a livello citosolico da due domini che legano <span style="color:#81C784">ATP</span>.
*   **Direzione del trasporto:** Hanno la peculiarità di trasportare molecole **sempre dall'interno della cellula verso l'esterno**.
*   **Rilevanza clinica:** Sono noti come **multidrug resistant proteins (MRP)**. Trasportano attivamente molti farmaci chemioterapici fuori dalla cellula tumorale, conferendo resistenza ai trattamenti. Se un farmaco viene espulso, non può esercitare la sua azione.

**Meccanismo d'azione:**
1.  **Condizione di riposo:** Il sito di legame del trasportatore è rivolto verso il lume (interno) della cellula.
2.  **Legame del substrato:** Il legame di un soluto favorisce l'interazione con le due molecole di ATP.
3.  **Cambio conformazionale e espulsione:** Il legame dell'ATP determina un cambio conformazionale che espelle il soluto dalla cellula.
4.  **Idrolisi e reset:** Segue l'idrolisi dell'ATP in <span style="color:#81C784">ADP</span> e fosfato inorganico, con rilascio di questi prodotti e ritorno alla conformazione originale.

**Differenza chiave:** In questi trasportatori, l'ATP **non viene utilizzato per una reazione di fosforilazione** (a differenza delle pompe P-type). Il cambio conformazionale è determinato dal **legame e dalla successiva idrolisi** dell'ATP stesso. [REACTION:ATP -> ADP + Pi]

> [!warning] Enfasi docente
> Quando si descrive un trasportatore attivo primario, è fondamentale specificare il meccanismo. Dire che un trasportatore P-type "utilizza l'energia dell'idrolisi dell'ATP" è impreciso; il cambio conformazionale è in realtà determinato dalla **fosforilazione**. Per i trasportatori ABC, invece, è proprio il legame e l'idrolisi dell'ATP a guidare il cambio conformazionale.

---

## BLOCCO 16 — Trasporto attivo secondario: il cotrasportatore Sodio-Glucosio (SGLT)

> [immagine di: cellula intestinale polarizzata che mostra il trasportatore SGLT nei microvilli apicali e la pompa Na⁺/K⁺ ATPasi nella membrana basolaterale]

Il trasportatore sodio-glucosio (SGLT) è un esempio di **trasporto attivo secondario**. Permette l'ingresso del <span style="color:#B8860B">glucosio</span> nella cellula sfruttando il **gradiente di concentrazione del sodio**.

*   Il sodio (Na⁺) è più concentrato all'esterno della cellula rispetto all'interno.
*   Questo gradiente fornisce l'energia per il cotrasporto del glucosio *contro* il suo gradiente di concentrazione (dall'esterno verso l'interno).

**Contesto cellulare:** Le cellule intestinali (enterociti) sono **polarizzate**. La membrana apicale, rivolta verso il lume intestinale, presenta microvilli per aumentare la superficie di assorbimento. Il trasportatore SGLT si trova proprio in questi microvilli.

**Meccanismo del SGLT:**
*   È un sistema di **cotrasporto** (simporto).
*   Permette l'ingresso di una molecola di <span style="color:#B8860B">glucosio</span> **contro** il suo gradiente di concentrazione, accoppiandolo al flusso **secondo gradiente** di **due ioni sodio (Na⁺)**.
*   Il Na⁺ è più concentrato all'esterno (nel lume intestinale) che all'interno della cellula, quindi tende ad entrare. Questo flusso "trainante" fornisce l'energia per l'ingresso del glucosio.

**Mantenimento del gradiente di Na⁺:** L'efficacia del SGLT dipende dal mantenimento di una bassa concentrazione intracellulare di Na⁺. Questo è garantito dalla **<span style="color:#2E7D32">pompa Na⁺/K⁺ ATPasi</span>**, un trasportatore attivo primario ubicato nella membrana **basolaterale** della stessa cellula. La pompa espelle attivamente il Na⁺ che è entrato tramite il SGLT, mantenendo il gradiente necessario.

**Conclusione:** Il trasportatore SGLT è attivo secondario perché sfrutta primariamente il gradiente di Na⁺. Tale gradiente è però creato e mantenuto secondariamente dall'<span style="color:#81C784">ATP</span> consumato dalla pompa Na⁺/K⁺.

> [!warning] Enfasi docente
> La distinzione chiave è:
> *   **Trasporto attivo primario:** guidato direttamente dall'idrolisi dell'<span style="color:#81C784">ATP</span> (es. pompa Na⁺/K⁺).
> *   **Trasporto attivo secondario:** guidato in prima battuta dall'energia del gradiente ionico (es. di Na⁺), gradiente che viene a sua volta mantenuto da un trasportatore primario che consuma ATP.

[CHEM:glucosio]

---

## BLOCCO 17 — Le acquaporine: canali per l'acqua

> [immagine di: struttura tetramerica di un'acquaporina con dettaglio del poro selettivo in un monomero]

Le **acquaporine** sono proteine integrali di membrana che fungono da canali per il passaggio dell'<span style="color:#E57373">acqua</span>. Sono presentate come un esempio di patologie genetiche legate a difetti del trasporto di membrana.

*   **Funzione:** Permettono il passaggio **passivo** dell'acqua secondo il gradiente di pressione osmotica.
*   **Struttura:** Sono **tetrameri**. Ciascun monomero forma un canale indipendente attraverso la membrana.
*   **Selettività:** La parte centrale di ciascun canale presenta due corte **α-eliche selettive** che rendono il passaggio così stretto da permettere il transito **solo** alle molecole d'acqua.
*   **Importanza fisiologica e patologica:** Sono cruciali in tessuti con elevato scambio d'acqua (es. ghiandole, rene). Mutazioni che compromettono la loro funzione sono associate a patologie.

[CHEM:acqua]

---

## BLOCCO 18 — Canali ionici: il canale del potassio

> [immagine di: struttura del canale del potassio voltaggio-dipendente, con evidenza della regione del poro selettivo e del filtro di selettività]

I canali ionici si dividono in due grandi categorie in base al loro meccanismo di apertura/chiusura (gating):
1.  **Canali voltaggio-dipendenti:** Si aprono in risposta a una variazione (depolarizzazione) del potenziale di membrana.
2.  **Canali ligando-dipendenti:** Si aprono o chiudono in seguito al legame con una specifica molecola segnale (ligando).

Il **canale del potassio** voltaggio-dipendente è preso come esempio storico e paradigmatico.

### Selettività del canale del potassio
Il canale del <span style="color:#E57373">potassio</span> è altamente selettivo. Per passare attraverso il filtro, uno ione deve possedere **due caratteristiche**:
1.  **Diametro compatibile** con le dimensioni del passaggio.
2.  **Capacità di formare interazioni ioniche** (legami non covalenti) con i residui amminoacidici delle eliche selettive.

*   **Ioni troppo grandi** (es. cesio, Cs⁺) non passano perché non entrano fisicamente.
*   **Ioni troppo piccoli** (es. sodio, Na⁺, o litio, Li⁺) non passano perché, pur entrando, **non riescono a formare le interazioni ioniche** necessarie con le pareti del canale.
*   Solo lo ione **potassio** possiede la giusta combinazione di dimensione e proprietà chimiche per soddisfare entrambi i requisiti.

**Dinamica del flusso ionico:** Nella regione più stretta del canale possono trovare posto contemporaneamente solo **due ioni potassio**, separati da una **molecola d'acqua**. Questa disposizione alternata (K⁺ - H₂O - K⁺) è necessaria per evitare la repulsione elettrostatica tra cariche positive dello stesso segno, che bloccherebbe il flusso.

> [!warning] Enfasi docente
> Anche nei canali, il flusso ionico **non è una diffusione completamente libera**. Sebbene i canali non siano saturabili come i trasportatori, il passaggio richiede sempre specifiche **interazioni ioniche** tra lo ione e il canale, il che ne modula la velocità.

[CHEM:potassio]

---

## BLOCCO 19 — Modelli di apertura/chiusura voltaggio-dipendente

Per i canali voltaggio-dipendenti, come quello del potassio, sono state proposte due ipotesi per spiegare il meccanismo di apertura e chiusura.

### Ipotesi 1: Modello conformazionale diretto
Questo è il modello più intuitivo. I canali voltaggio-dipendenti possiedono una o due **eliche transmembrana** in cui prevalgono amminoacidi caricati positivamente.
*   **Meccanismo:** Quando la membrana si depolarizza (riducendo la carica negativa interna), le eliche con carica positiva subiscono un cambio conformazionale a causa della repulsione tra cariche simili. Questo cambiamento apre il canale.
*   **Problema:** Questo modello non spiega la **fase di refrattarietà** osservata fisiologicamente, durante la quale il canale è aperto ma lo ione non passa. Un sistema basato su una semplice transizione "aperto/chiuso" non può giustificare questo stato.

### Ipotesi 2: Modello "palla-catena" (più accreditato)
Questo modello spiega meglio il comportamento dei canali che presentano una fase di refrattarietà.
*   **Componenti:** Oltre al canale vero e proprio, esiste un **dominio proteico globulare** legato ad esso da una catena di amminoacidi, libero di muoversi sul lato citosolico.
*   **Meccanismo:**
    1.  **Canale chiuso:** Il dominio globulare non ha affinità per il canale chiuso e fluttua liberamente.
    2.  **Depolarizzazione:** Il cambio di voltaggio causa l'apertura del canale. Contemporaneamente, **l'affinità del dominio globulare per il canale aperto aumenta**.
    3.  **Blocco (refrattarietà):** Il dominio globulare si lega al canale aperto, fungendo da "tappo" e bloccando fisicamente il passaggio degli ioni. Il canale è strutturalmente aperto, ma impermeabile.
    4.  **Ripolarizzazione:** Il ritorno al potenziale di riposo ripristina la conformazione originale, il dominio globulare perde affinità e si stacca, permettendo al canale di chiudersi e poi riaprirsi.

> [!warning] Enfasi docente
> Il modello "palla-catena" risponde meglio alle evidenze sperimentali e alle misure fisiologiche per i canali che mostrano refrattarietà.

---

## BLOCCO 20 — Canali ligando-dipendenti: il recettore colinergico

Un esempio fondamentale di canale ligando-dipendente è il **recettore per l'acetilcolina**, un neurotrasmettitore cruciale.

> [immagine di: schema della sinapsi con cellula presinaptica, vescicole di neurotrasmettitore, fessura sinaptica e recettore colinergico sulla membrana postsinaptica]

### Localizzazione e Funzione
Il recettore si trova sulla **membrana postsinaptica**. Il suo ruolo è trasdurre un segnale chimico in un segnale elettrico.

### Meccanismo di Attivazione
1.  **Rilascio del neurotrasmettitore:** Un impulso nervoso causa la depolarizzazione della membrana presinaptica, inducendo la fusione delle vescicole contenenti <span style="color:#E57373">acetilcolina</span> con la membrana e il suo rilascio nella fessura sinaptica.
2.  **Legame e apertura:** L'<span style="color:#E57373">acetilcolina</span> si lega al recettore. Questo legame induce un **cambio conformazionale** nel recettore-canale, aprendolo.
3.  **Flusso ionico e trasmissione del segnale:** Il canale aperto permette il passaggio di ioni. È un **canale non selettivo** che consente il flusso di **ioni sodio (Na⁺) e potassio (K⁺)**. L'ingresso netto di cariche positive (soprattutto Na⁺) nella cellula postsinaptica ne depolarizza la membrana, innescando il trasferimento dell'impulso nervoso.

> [!warning] Enfasi docente
> È importante ricordare la **modalità di apertura (ligando-dipendente)** e la **struttura** di questo canale, in quanto rappresentativo della classe dei canali ligando-dipendenti.

[CHEM:acetilcolina]

---

## BLOCCO 21 — Canale TRICB: un esempio di complessità e correlazione clinica

> [immagine di: localizzazione del canale TRICB sulla membrana del reticolo endoplasmatico e suo ruolo nel flusso del calcio]

Il canale **TRICB** è un canale per il potassio (<span style="color:#E57373">K⁺</span>) localizzato sulla **membrana del reticolo endoplasmatico**.

### Ruolo fisiologico
Il canale TRICB funziona come un **cotrasportatore**. Il suo ruolo è permettere l'uscita di potassio dal reticolo endoplasmatico, fungendo da **controione** necessario per il corretto funzionamento dei **canali per il calcio (<span style="color:#E57373">Ca²⁺</span>) insositolo trifosfato-dipendenti** (IP3-dipendenti). In sostanza, il flusso di potassio fuori dal reticolo bilancia elettricamente il flusso di calcio in uscita, facilitandolo.

### Correlazione clinica: una malattia rara dello scheletro
Studi di analisi genomica su pazienti affetti da una rara malattia ossea hanno identificato mutazioni nel gene che codifica per il canale TRICB. La ricerca, supportata da modelli animali, ha chiarito il meccanismo patologico:

1.  **Mutazione in TRICB** → Canale non funzionante.
2.  **Assenza del flusso di potassio** dal reticolo endoplasmatico.
3.  **Alterazione del flusso di calcio** dai canali IP3-dipendenti.
4.  **Squilibrio della concentrazione di calcio** nel citosol e nel reticolo endoplasmatico.
5.  **Disfunzione degli enzimi** citosolici calcio-dipendenti necessari per la sintesi del **collagene di tipo I**.
6.  **Produzione di collagene con struttura alterata** e **scarsa mineralizzazione** ossea da parte degli osteoblasti.
7.  **Risultato clinico:** <span style="color:#7B1F3A">fragilità ossea</span> nel paziente.

> [!warning] Enfasi docente
> Questo esempio dimostra come lo studio di canali e trasportatori apparentemente "banali" sia fondamentale per comprendere la fisiopatologia di malattie che potrebbero sembrare non correlate. Una mutazione in un canale per il potassio del reticolo endoplasmatico può causare una grave malattia scheletrica attraverso l'alterazione dell'omeostasi del calcio e della sintesi del collagene.

---

## APPENDICE TABELLARE

*Riepilogo aggregato della lezione per ripasso rapido e generazione flashcard.*

### Concentrazioni Ioniche Chiave

| IONE/MOLECOLA | CONCENTRAZIONE EXTRACELLULARE | CONCENTRAZIONE INTRACELLULARE (CITOSOL) | NOTE | IMMAGINE |
|---|---|---|---|---|
| <span style="color:#E57373">Sodio (Na⁺)</span> | 140 mM | 10 mM | Più concentrato all'esterno. Determinante per il potenziale di membrana. | |
| <span style="color:#E57373">Potassio (K⁺)</span> | 4 mM | 140 mM | Più concentrato all'interno. Determinante per il potenziale di membrana. | |
| <span style="color:#E57373">Calcio (Ca²⁺)</span> | 2.5 mM | 0.1 µM | Importante messaggero e cofattore. Riserva ad alta concentrazione nel **Reticolo Endoplasmatico**. | |
| <span style="color:#B8860B">Glucosio</span> | ~5 mM | Generalmente inferiore | Viene rapidamente metabolizzato (glicolisi) o accumulato (glicogeno). Epatociti possono fare eccezione. | |

### Principi del Trasporto Passivo

| TIPO DI SOLUTO | FORZA MOTRICE PRIMARIA | DEFINIZIONE | CONDIZIONE ALL'EQUILIBRIO | IMMAGINE |
|---|---|---|---|---|
| **Neutro (senza carica)** | Gradiente di Concentrazione | Movimento spontaneo dalla zona a concentrazione maggiore a quella a concentrazione minore. | Concentrazione uguale in entrambi i compartimenti. | |
| **Carico (ione)** | Gradiente Elettrochimico | Movimento spontaneo guidato dalla combinazione del gradiente di concentrazione e del gradiente elettrico. | Bilancio sia della concentrazione che della distribuzione delle cariche. | |

### Meccanismi di Trasporto di Membrana

| MECCANISMO | FORZA MOTRICE | CARATTERISTICHE CHIAVE | ESEMPI DI MOLECOLE TRASPORTATE | SATURABILITÀ | IMMAGINE |
|---|---|---|---|---|---|
| **Diffusione Semplice** | Gradiente di concentrazione | Passaggio diretto attraverso il doppio strato. Per molecole idrofobiche o molto piccole. | <span style="color:#E57373">Anidride carbonica</span>, ossido di azoto, ormoni steroidei | No | |
| **Diffusione Facilitata (Trasportatori)** | Gradiente di concentrazione o elettrochimico | Alta specificità. Meccanismo a cambiamento conformazionale ("porta alternata"). | Molecole polari, zuccheri, aminoacidi | **Sì** (raggiunge Vmax) | |
| **Diffusione Facilitata (Canali)** | Gradiente elettrochimico (principalmente) | Stereospecificità ridotta. Stati: Aperto/Chiuso. Flusso libero quando aperto. | Ioni (Na⁺, K⁺, Ca²⁺, Cl⁻) | **No** | |

### Confronto Trasportatori vs. Canali

| CARATTERISTICA | TRASPORTATORI (Carrier) | CANALI |
|---|---|---|
| **Specificità** | Alta (legame specifico) | Da bassa a moderata (alcuni sono specifici) |
| **Meccanismo** | Cambiamento conformazionale sequenziale | Poro idrofilico con gate (porta) |
| **Saturabilità** | **Sì** (dipende dal numero di proteine) | **No** (flusso libero quando aperto) |
| **Velocità di trasporto** | Più lenta (limitata dal cambio conformazionale) | Molto veloce (vicina alla diffusione libera) |
| **Regolazione** | Numero di trasportatori in membrana; modulazione allosterica | Apertura/chiusura del gate (ligando, voltaggio, ecc.) |
| **IMMAGINE** | | |

### Classificazione dei Trasportatori

| TIPO | TRASPORTO | NUMERO SOLUTI | DIREZIONE | FONTE ENERGETICA | ESEMPIO | IMMAGINE |
|---|---|---|---|---|---|---|
| **Uniporto** | Passivo | 1 | Secondo gradiente | Gradiente di concentrazione | — | |
| **Antiporto** | Passivo | 2 | Opposte | Gradiente di concentrazione | Bicarbonato-Cloro | |
| **Simporto** | Passivo | 2 | Stessa | Gradiente di concentrazione | GLUT (glucosio) | |
| **Attivo Primario** | Attivo | 1 (o più) | Contro gradiente | Idrolisi diretta di <span style="color:#81C784">ATP</span> | Pompe ioniche ATP-dipendenti | |
| **Attivo Secondario** | Attivo | 2 | S: contro gradiente; X: secondo gradiente | Gradiente di concentrazione di X (creato da una pompa primaria) | Trasportatori accoppiati (es. Na+/glucosio) | |

### Esempi di Trasporto Passivo

| TRASPORTATORE | TIPO | SOLUTI TRASPORTATI | DIREZIONE | MECCANISMO GUIDA | CONTESTO FISIOLOGICO | IMMAGINE |
|---|---|---|---|---|---|---|
| **Famiglia <span style="color:#2E7D32">GLUT</span>** | Uniporto (presunto) | <span style="color:#B8860B">Glucosio</span> | Secondo gradiente | Gradiente di concentrazione del glucosio | Ingresso di glucosio nelle cellule | |
| **Antiporto Bicarbonato-Cloro** | Antiporto | <span style="color:#E57373">HCO₃⁻</span> (bicarbonato) e <span style="color:#E57373">Cl⁻</span> (cloruro) | Opposte (scambio 1:1) | Gradiente di concentrazione dei due ioni | Trasporto della <span style="color:#E57373">CO₂</span> dai tessuti ai polmoni | |

### Trasportatori Attivi Primari (ATPasi di tipo P)

| TRASPORTATORE | LOCALIZZAZIONE | SOLUTO TRASPORTATO | DIREZIONE (da → a) | STECHIOMETRIA (per ATP) | FUNZIONE PRINCIPALE | IMMAGINE |
|---|---|---|---|---|---|---|
| **Pompa SERCA** | Membrana del Reticolo Endoplasmatico | <span style="color:#E57373">Ioni Calcio (Ca²⁺)</span> | Citosol → Lume del RE | 2 Ca²⁺ | Rimuove Ca²⁺ dal citosol, termina la segnalazione cellulare | |
| **Pompa Na⁺/K⁺ ATPasi** | Membrana Plasmatica | <span style="color:#E57373">Ioni Sodio (Na⁺)</span> e <span style="color:#E57373">Potassio (K⁺)</span> | Na⁺: Interno → Esterno<br>K⁺: Esterno → Interno | 3 Na⁺ out, 2 K⁺ in | Genera e mantiene il potenziale di membrana a riposo | |

### Meccanismo Comune delle ATPasi di tipo P

| FASE | EVENTO CHIMICO | CAMBIO CONFORMAZIONALE | RISULTATO |
|---|---|---|---|
| **1. Legame Substrato** | Il soluto si lega al dominio M. | — | Il trasportatore è carico. |
| **2. Fosforilazione** | Il dominio N utilizza <span style="color:#81C784">ATP</span> per fosforilare un Aspartato nel dominio P. | **Primo cambio** (dopo la fosforilazione) | Riduce l'affinità per il soluto legato, che viene rilasciato. |
| **3. Defosforilazione** | Il dominio A rimuove il fosfato (attività fosfatasica). | **Secondo cambio** (dopo la defosforilazione) | Ripristina la conformazione originale e l'affinità per il soluto. |

### Trasportatori Attivi

| TRASPORTATORE | TIPO | ENERGIA | MECCANISMO CHIAVE | DIREZIONE TRASPORTO | FUNZIONE / NOTE | IMMAGINE |
|---|---|---|---|---|---|---|
| **Trasportatori ABC** (es. MRP) | Primario (ABC-type) | <span style="color:#81C784">ATP</span> | Legame e idrolisi dell'ATP (NON fosforilazione) | Sostanze dall'interno all'esterno | Conferiscono resistenza multifarmaco (MDR) nelle cellule tumorali. | |
| <span style="color:#2E7D32">Trasportatore SGLT</span> | Secondario (Simporto) | Gradiente di Na⁺ | Cotrasporto con 2 Na⁺ | Glucosio e Na⁺ dentro la cellula | Assorbimento intestinale di glucosio; localizzato nei microvilli apicali. | |

### Proteine di trasporto di membrana

| TIPO | ESEMPIO | MECCANISMO | FONTE ENERGETICA | SELE- TTIVITÀ | SATURA- BILE | NOTE | IMMAGINE |
|---|---|---|---|---|---|---|---|
| **Canale** | Acquaporina | Diffusione facilitata | Gradiente di pressione osmotica | **Stretta** (solo H₂O) | **No** | Tetramero; poro selettivo formato da α-eliche. Mutazioni causano patologie. | |

### Canali Ionici

| CANALE / RECETTORE | TIPO | IONE TRASPORTATO | MECCANISMO DI APERTURA | CARATTERISTICHE PRINCIPALI | IMMAGINE |
|---|---|---|---|---|---|
| Canale del <span style="color:#E57373">Potassio</span> | Voltaggio-dipendente | <span style="color:#E57373">K⁺</span> | Cambio di potenziale di membrana (depolarizzazione) | Alta selettività; flusso ad alternanza ione-acqua; mostra refrattarietà. | |
| Recettore Colinergico (per <span style="color:#E57373">Acetilcolina</span>) | Ligando-dipendente | <span style="color:#E57373">Na⁺</span> e <span style="color:#E57373">K⁺</span> | Legame del neurotrasmettitore (<span style="color:#E57373">acetilcolina</span>) | Canale non selettivo; localizzato sulla membrana postsinaptica; trasduce segnale chimico in elettrico. | |
| Canale TRICB | Canale per <span style="color:#E57373">K⁺</span> | <span style="color:#E57373">K⁺</span> | [VERIFICARE] | Membrana del Reticolo Endoplasmatico | Funge da controione per i canali del <span style="color:#E57373">Ca²⁺</span> IP3-dipendenti. Mutazioni causano una malattia rara da fragilità ossea. | |

### Modelli di Regolazione dei Canali

| MODELLO | APPLICABILE A | MECCANISMO | VANTAGGI / NOTE | IMMAGINE |
|---|---|---|---|---|
| Modello Conformazionale Diretto | Canali voltaggio-dipendenti | Depolarizzazione → repulsione di carica in eliche positive → cambio conformazionale → apertura. | Intuitivo, ma non spiega la fase di refrattarietà. | |
| Modello "Palla-Catena" | Canali voltaggio-dipendenti con refrattarietà | 1) Apertura per depolarizzazione.<br>2) Dominio globulare legato aumenta affinità per canale aperto e lo blocca.<br>3) Ripolarizzazione ripristina stato iniziale. | Spiega la refrattarietà (canale aperto ma bloccato). Considerato il modello più accreditato per molti canali. | |

### Correlazione Clinica

| MALATTIA | CAUSA GENETICA | MECCANISMO FISIOPATOLOGICO | EFFETTO SULL'ORGANO | IMMAGINE |
|---|---|---|---|---|
| <span style="color:#7B1F3A">Rara malattia ossea / Fragilità ossea</span> | Mutazione nel canale **TRICB** | Alterato flusso di <span style="color:#E57373">K⁺</span> → Alterato rilascio di <span style="color:#E57373">Ca²⁺</span> dal RE → Disfunzione enzimi sintesi collagene | Produzione di collagene di tipo I alterato e scarsa mineralizzazione ossea. | |

---

*Fine sbobina — Lezione: Trasporto attraverso le membrane biologiche*
*Argomenti correlati: → Trasportatori di membrana · → Trasportatore del glucosio · → Pompa sodio-potassio · → Potenziale di membrana · → Trasporto attivo · → Pompe ioniche · → Vie metaboliche del glucosio · → Diffusione facilitata · → Trasportatori accoppiati · → Trasportatori ABC · → Assorbimento intestinale · → Resistenza ai farmaci · → Potenziale di membrana a riposo · → Trasporto vescicolare · → Trasmissione sinaptica · → Elettrofisiologia · → Omeostasi del calcio · → Sintesi del collagene*