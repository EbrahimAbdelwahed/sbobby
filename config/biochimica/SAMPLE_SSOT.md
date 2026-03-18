# Biochimica — Lezione 3: La Glicolisi

> **Argomento:** Via glicolitica
> **Blocchi presenti:** Informazioni sul corso · Visione d'insieme · Fase di investimento energetico · Fase di recupero energetico · Regolazione · Destini del piruvato · Appendice tabellare

---

## Informazioni sul corso

L'esame di Biochimica prevede una prova scritta con domande aperte sulle vie metaboliche e una prova orale facoltativa per migliorare il voto. Il docente ha specificato che per le vie metaboliche è necessario conoscere: substrati e prodotti di ogni tappa, enzimi chiave, cofattori coinvolti e i punti di regolazione. Non è richiesto il meccanismo catalitico dettagliato degli enzimi. Testo consigliato: Lehninger, Principi di Biochimica.

---

## BLOCCO 1 — Visione d'insieme

La <mark style="background: #1565C0; color: #fff">**glicolisi**</mark> è la via metabolica che converte una molecola di <mark style="background: #B8860B; color: #fff">glucosio</mark> (6 atomi di carbonio) in due molecole di <mark style="background: #E57373">piruvato</mark> (3 atomi di carbonio ciascuna). Avviene nel **citoplasma** di tutte le cellule — è una via ubiquitaria e filogeneticamente antica.

Il bilancio netto è: consumo di 2 <mark style="background: #81C784">ATP</mark> nella fase iniziale, produzione di 4 <mark style="background: #81C784">ATP</mark> e 2 <mark style="background: #00ACC1; color: #fff">NADH</mark> nella fase di recupero, per una resa netta di **2 ATP + 2 NADH** per molecola di glucosio. [CHEM:glucosio]

> [!warning] Enfasi docente
> Il docente ha insistito sul fatto che la glicolisi non richiede ossigeno — è una via anaerobica. La presenza o assenza di O₂ determina il destino del piruvato, non la glicolisi stessa.

---

## BLOCCO 2 — Fase di investimento energetico (reazioni 1–5)

> [immagine di: schema delle prime 5 reazioni della glicolisi con strutture dei substrati]

### Reazione 1 — Fosforilazione del glucosio

La <mark style="background: #2E7D32; color: #fff">esochinasi</mark> (o <mark style="background: #2E7D32; color: #fff">glucochinasi</mark> nel fegato) catalizza la fosforilazione del <mark style="background: #B8860B; color: #fff">glucosio</mark> a <mark style="background: #E57373">glucosio-6-fosfato</mark>, utilizzando una molecola di <mark style="background: #81C784">ATP</mark>. Questa reazione è **irreversibile** (ΔG molto negativo) e rappresenta il primo punto di regolazione. Il glucosio-6-fosfato non può uscire dalla cellula perché la membrana è impermeabile ai composti fosforilati — la fosforilazione "intrappola" il glucosio nella cellula.

[REACTION:glucosio + ATP -> glucosio-6-fosfato + ADP]

Il docente ha distinto le due isoforme: la <mark style="background: #2E7D32; color: #fff">esochinasi</mark> è presente in tutti i tessuti, ha bassa Km (alta affinità) ed è inibita dal prodotto (glucosio-6-fosfato). La <mark style="background: #2E7D32; color: #fff">glucochinasi</mark> è presente nel fegato e nelle cellule β del pancreas, ha alta Km (bassa affinità, funziona solo ad alte concentrazioni di glucosio) e **non** è inibita dal prodotto — questo permette al fegato di assorbire glucosio dopo i pasti quando la glicemia è alta.

> [!warning] Enfasi docente
> La differenza tra esochinasi e glucochinasi è domanda d'esame frequente. Il concetto chiave è la Km: l'esochinasi lavora sempre, la glucochinasi solo a glicemia alta.

### Reazione 2 — Isomerizzazione

La <mark style="background: #2E7D32; color: #fff">fosfoglucosio isomerasi</mark> converte il glucosio-6-fosfato in <mark style="background: #E57373">fruttosio-6-fosfato</mark>. Reazione reversibile, trasforma un aldoso in un chetoso. [CHEM:fruttosio-6-fosfato]

### Reazione 3 — Fosforilazione del fruttosio-6-fosfato

La <mark style="background: #2E7D32; color: #fff">fosfofruttochinasi-1</mark> (PFK-1) catalizza la seconda fosforilazione: fruttosio-6-fosfato + ATP → <mark style="background: #E57373">fruttosio-1,6-bisfosfato</mark> + ADP. Questa è la **tappa limitante** della glicolisi e il principale punto di regolazione.

[REACTION:fruttosio-6-fosfato + ATP -> fruttosio-1,6-bisfosfato + ADP]

La PFK-1 è un enzima allosterico regolato da molteplici effettori:
- **Attivatori:** AMP, fruttosio-2,6-bisfosfato (il più potente), ADP
- **Inibitori:** ATP (ad alte concentrazioni), citrato, H⁺ (acidosi)

L'<mark style="background: #C2185B; color: #fff">insulina</mark> stimola indirettamente la PFK-1 aumentando i livelli di fruttosio-2,6-bisfosfato.

> [!warning] Enfasi docente
> PFK-1 e i suoi regolatori sono da sapere a memoria. Il docente ha chiesto esplicitamente di saper spiegare perché l'ATP è sia substrato che inibitore — a basse concentrazioni funge da substrato, ad alte concentrazioni si lega al sito allosterico inibitorio.

### Reazioni 4–5 — Scissione

La <mark style="background: #2E7D32; color: #fff">aldolasi</mark> scinde il fruttosio-1,6-bisfosfato in due triosi: <mark style="background: #E57373">gliceraldeide-3-fosfato</mark> (G3P) e <mark style="background: #E57373">diidrossiacetone fosfato</mark> (DHAP). La <mark style="background: #2E7D32; color: #fff">trioso fosfato isomerasi</mark> interconverte DHAP in G3P — da qui in avanti ogni tappa avviene **due volte** per molecola di glucosio iniziale.

---

**Riepilogo rapido — Fase di investimento:**
- 2 ATP consumati (reazioni 1 e 3)
- Glucosio (C6) → 2× gliceraldeide-3-fosfato (C3)
- 2 reazioni irreversibili (esochinasi, PFK-1) = punti di regolazione
- PFK-1 è la tappa limitante

---

## BLOCCO 3 — Fase di recupero energetico (reazioni 6–10)

### Reazione 6 — Ossidazione e fosforilazione

La <mark style="background: #2E7D32; color: #fff">gliceraldeide-3-fosfato deidrogenasi</mark> (GAPDH) ossida la G3P a <mark style="background: #E57373">1,3-bisfosfoglicerato</mark>, riducendo <mark style="background: #00ACC1; color: #fff">NAD+</mark> a <mark style="background: #00ACC1; color: #fff">NADH</mark>. Questa è l'unica reazione di ossidoriduzione della glicolisi. Il fosfato in posizione 1 è un legame ad alta energia ("acil-fosfato").

### Reazione 7 — Prima fosforilazione a livello del substrato

La <mark style="background: #2E7D32; color: #fff">fosfoglicerato chinasi</mark> trasferisce il gruppo fosfato ad alta energia dal 1,3-bisfosfoglicerato all'ADP, producendo <mark style="background: #81C784">ATP</mark> e <mark style="background: #E57373">3-fosfoglicerato</mark>. Questa è una **fosforilazione a livello del substrato** — non richiede la catena di trasporto degli elettroni.

### Reazioni 8–9 — Riarrangiamento

Il 3-fosfoglicerato viene convertito in <mark style="background: #E57373">2-fosfoglicerato</mark> dalla <mark style="background: #2E7D32; color: #fff">fosfoglicerato mutasi</mark>, poi in <mark style="background: #E57373">fosfoenolpiruvato</mark> (PEP) dalla <mark style="background: #2E7D32; color: #fff">enolasi</mark>. L'enolasi richiede Mg²⁺ come cofattore ed è inibita dal fluoruro — questo è il motivo per cui le provette per la glicemia contengono fluoruro di sodio. [CHEM:fosfoenolpiruvato]

### Reazione 10 — Seconda fosforilazione a livello del substrato

La <mark style="background: #2E7D32; color: #fff">piruvato chinasi</mark> trasferisce il gruppo fosfato dal PEP all'ADP, producendo ATP e <mark style="background: #E57373">piruvato</mark>. Reazione **irreversibile** — terzo punto di regolazione. La piruvato chinasi è attivata dal fruttosio-1,6-bisfosfato (regolazione feed-forward) e inibita da ATP e <mark style="background: #E65100; color: #fff">alanina</mark>.

[REACTION:fosfoenolpiruvato + ADP -> piruvato + ATP]

> [!warning] Enfasi docente
> Le tre reazioni irreversibili (esochinasi, PFK-1, piruvato chinasi) sono i punti di regolazione — nella gluconeogenesi vengono aggirate da enzimi diversi. Questo concetto sarà ripreso nella lezione sulla gluconeogenesi.

---

**Riepilogo rapido — Fase di recupero:**
- 4 ATP prodotti (×2 reazioni 7 e 10) — resa netta 2 ATP
- 2 NADH prodotti (×2 reazione 6)
- 2 fosforilazioni a livello del substrato
- Piruvato chinasi = terzo punto di regolazione

---

## BLOCCO 4 — Regolazione della glicolisi

La regolazione avviene sui tre enzimi che catalizzano le reazioni irreversibili:

| ENZIMA | ATTIVATORI | INIBITORI | REGOLAZIONE ORMONALE |
|---|---|---|---|
| <mark style="background: #2E7D32; color: #fff">Esochinasi</mark> | — | Glucosio-6-fosfato (prodotto) | — |
| <mark style="background: #2E7D32; color: #fff">Glucochinasi</mark> | Glucosio (alta [conc.]) | Proteina regolatrice (GKRP) | <mark style="background: #C2185B; color: #fff">Insulina</mark> ↑ espressione |
| <mark style="background: #2E7D32; color: #fff">PFK-1</mark> | AMP, F-2,6-BP, ADP | ATP, citrato, H⁺ | <mark style="background: #C2185B; color: #fff">Insulina</mark> ↑ F-2,6-BP; <mark style="background: #C2185B; color: #fff">glucagone</mark> ↓ F-2,6-BP |
| <mark style="background: #2E7D32; color: #fff">Piruvato chinasi</mark> | F-1,6-BP (feed-forward) | ATP, alanina | <mark style="background: #C2185B; color: #fff">Glucagone</mark> → fosforilazione → inibizione (fegato) |

La logica complessiva: quando la carica energetica è alta (molto ATP, poco AMP) la glicolisi rallenta. Quando la cellula ha bisogno di energia (poco ATP, molto AMP) la glicolisi accelera.

---

## BLOCCO 5 — Destini del piruvato

Il <mark style="background: #E57373">piruvato</mark> è un bivio metabolico — il suo destino dipende dalla disponibilità di ossigeno e dal tipo cellulare. [CHEM:piruvato]

### In condizioni aerobiche
Il piruvato entra nel mitocondrio e viene decarbossilato ossidativamente a <mark style="background: #E57373">acetil-CoA</mark> dal complesso della <mark style="background: #2E7D32; color: #fff">piruvato deidrogenasi</mark>, con produzione di CO₂ e <mark style="background: #00ACC1; color: #fff">NADH</mark>. L'acetil-CoA entra nel <mark style="background: #1565C0; color: #fff">**ciclo di Krebs**</mark>. [→ ARGOMENTO FUTURO: ciclo di Krebs]

### In condizioni anaerobiche
Il piruvato viene ridotto a <mark style="background: #E57373">lattato</mark> dalla <mark style="background: #2E7D32; color: #fff">lattato deidrogenasi</mark> (LDH), ossidando NADH a NAD+. Questo passaggio è essenziale per **rigenerare il NAD+** citosolico necessario alla reazione 6 (GAPDH) — senza di esso la glicolisi si fermerebbe. È quello che avviene nel muscolo durante esercizio intenso e negli eritrociti (che mancano di mitocondri).

La <mark style="background: #7B1F3A; color: #fff">acidosi lattica</mark> si verifica quando la produzione di lattato supera la capacità di smaltimento — ad esempio nello shock, nell'ipossia tissutale o in alcune intossicazioni.

### Nel lievito (fermentazione alcolica)
Il piruvato viene decarbossilato ad <mark style="background: #E57373">acetaldeide</mark> e poi ridotto a etanolo. [INCOMPLETO]

---

## APPENDICE TABELLARE

*Riepilogo aggregato della lezione per ripasso rapido e generazione flashcard.*

### Enzimi della glicolisi

| ENZIMA | REAZIONE CATALIZZATA | SUBSTRATO | PRODOTTO | COFATTORE | REGOLAZIONE | VIA METABOLICA | IMMAGINE |
|---|---|---|---|---|---|---|---|
| <mark style="background: #2E7D32; color: #fff">Esochinasi</mark> | Fosforilazione | <mark style="background: #B8860B; color: #fff">Glucosio</mark> | G-6-P | <mark style="background: #81C784">ATP</mark> → ADP | Inibita da G-6-P | <mark style="background: #1565C0; color: #fff">Glicolisi</mark> | |
| <mark style="background: #2E7D32; color: #fff">Glucochinasi</mark> | Fosforilazione | <mark style="background: #B8860B; color: #fff">Glucosio</mark> | G-6-P | <mark style="background: #81C784">ATP</mark> → ADP | Alta Km; <mark style="background: #C2185B; color: #fff">insulina</mark> ↑ | <mark style="background: #1565C0; color: #fff">Glicolisi</mark> (fegato) | |
| <mark style="background: #2E7D32; color: #fff">PFK-1</mark> | Fosforilazione | F-6-P | F-1,6-BP | <mark style="background: #81C784">ATP</mark> → ADP | AMP ↑, F-2,6-BP ↑; ATP ↓, citrato ↓ | <mark style="background: #1565C0; color: #fff">Glicolisi</mark> | |
| <mark style="background: #2E7D32; color: #fff">Aldolasi</mark> | Scissione | F-1,6-BP | G3P + DHAP | — | — | <mark style="background: #1565C0; color: #fff">Glicolisi</mark> | |
| <mark style="background: #2E7D32; color: #fff">GAPDH</mark> | Ossidazione + fosforilazione | G3P | 1,3-BPG | <mark style="background: #00ACC1; color: #fff">NAD+</mark> → NADH | — | <mark style="background: #1565C0; color: #fff">Glicolisi</mark> | |
| <mark style="background: #2E7D32; color: #fff">Fosfoglicerato chinasi</mark> | Fosforilazione substrato | 1,3-BPG | 3-PG | ADP → <mark style="background: #81C784">ATP</mark> | — | <mark style="background: #1565C0; color: #fff">Glicolisi</mark> | |
| <mark style="background: #2E7D32; color: #fff">Enolasi</mark> | Deidratazione | 2-PG | PEP | Mg²⁺ | Inibita da fluoruro | <mark style="background: #1565C0; color: #fff">Glicolisi</mark> | |
| <mark style="background: #2E7D32; color: #fff">Piruvato chinasi</mark> | Fosforilazione substrato | PEP | <mark style="background: #E57373">Piruvato</mark> | ADP → <mark style="background: #81C784">ATP</mark> | F-1,6-BP ↑; ATP ↓, <mark style="background: #E65100; color: #fff">Ala</mark> ↓ | <mark style="background: #1565C0; color: #fff">Glicolisi</mark> | |

### Via metabolica

| VIA | SEDE CELLULARE | SUBSTRATO INIZIALE | PRODOTTO FINALE | RESA ENERGETICA | REGOLAZIONE CHIAVE | IMMAGINE |
|---|---|---|---|---|---|---|
| <mark style="background: #1565C0; color: #fff">Glicolisi</mark> | Citoplasma | <mark style="background: #B8860B; color: #fff">Glucosio</mark> | 2× <mark style="background: #E57373">Piruvato</mark> | 2 ATP + 2 NADH (netti) | PFK-1 (tappa limitante) | |

---

*Fine sbobina — Lezione 3*
*Argomenti correlati: → Gluconeogenesi · → Ciclo di Krebs · → Fermentazione · → Via del pentoso fosfato*
