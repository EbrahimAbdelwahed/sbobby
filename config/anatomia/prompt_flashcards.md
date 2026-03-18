# Prompt Anatomia — Generazione Flashcard Anki (v5)

---

## Formato output

Restituisci un oggetto JSON con due campi:

```json
{
  "anki": [
    {
      "front": "Testo della domanda",
      "back": "Testo della risposta con contesto sufficiente",
      "tags": ["anatomia::macro-argomento::argomento-specifico"]
    }
  ],
  "brain_dumps": [
    {
      "title": "Titolo del topic",
      "type": "architettura|topografia",
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
- **→ Brain dump**: il topic richiede di ricostruire una rete → genera UN brain dump con checklist, e al massimo 1-2 card Anki sullo stesso topic (solo per fatti completamente isolati dal resto, es. un nome specifico o un valore numerico che non dipende dalla rete)

**Il brain dump non è un'aggiunta alle card. È un'alternativa che le sostituisce.**

### Esempio SBAGLIATO (additivo — da evitare):
- Card: "Quale neurotrasmettitore rilascia la placca neuromotrice?" → ACh
- Card: "Cosa succede dopo che l'ACh si lega al recettore?" (step della cascata)
- Card: "Come avviene il rilascio di Ca²⁺ dal reticolo sarcoplasmatico?"
- Brain dump: "Meccanismo integrato della neurotrasmissione" (contiene gli stessi step)

→ SBAGLIATO: le card replicano il contenuto del brain dump. Se esiste il brain dump, quelle card non ci sono.

### Esempio CORRETTO (sostitutivo):
- Card: "Quale neurotrasmettitore viene rilasciato alla placca neuromotrice?" → ACh *(fatto autonomo)*
- Card: "Quale enzima degrada l'ACh e qual è la conseguenza clinica della sua inibizione?" *(fatto autonomo con contesto)*
- Brain dump: "Meccanismo di trasmissione neuromuscolare: sequenza completa" *(la rete — nessuna card sulla cascata di eventi)*

→ CORRETTO: i fatti isolati vanno in Anki, la rete va nel brain dump. La sovrapposizione è legittima quando le funzioni cognitive sono diverse (recall isolato in Anki, nodo in una rete nel brain dump) — illegittima quando la checklist ripete esattamente la domanda della card senza aggiungere contesto relazionale.

### Discriminante card Anki vs brain dump per topic con rete

Quando un topic ha un brain dump (architettura o topografia), le card Anki ammesse sullo stesso topic sono quelle che testano **fatti puntuali non derivabili dalla logica dell'architettura** (nome di un legamento specifico, tipo di tessuto, numero di vertebre, presenza di una caratteristica specifica come le faccette costali). Non sono ammesse card che testano **i rapporti topografici** ("qual è il rapporto tra X e Y?"), **la sequenza di eventi** ("cosa succede dopo che...?"), o **la logica struttura-funzione di sistema** — queste appartengono al brain dump.

Un fatto puntuale può apparire sia in Anki sia nella checklist del brain dump se le funzioni cognitive sono diverse: la card testa il recupero isolato del dato, la checklist lo usa come nodo in una rete più ampia. Questa ridondanza è legittima. È illegittima solo quando la voce del brain dump ripete la domanda della card senza aggiungere contesto relazionale.

---

## Filtro conoscenza generale (CRITICO)

Prima di generare qualsiasi card, filtra il materiale con questa domanda: **uno studente di medicina al primo anno saprebbe già questa informazione senza averla studiata in modo specifico?**

Se sì, la card non si genera. Esempi di materiale da non generare:
- "Il cuore pompa il sangue"
- "I muscoli scheletrici consentono il movimento volontario"
- "I legamenti connettono osso a osso"
- "I tendini trasmettono la forza muscolare all'osso"

Queste sono nozioni di cultura scientifica generale. **Non sono materiale da spaced repetition**. Se la sbobina le usa come contesto introduttivo o come classificazione di base, ignorale o condensale in un brain dump — mai in card individuali.

**Informazioni amministrative** (formato esame, struttura del programma, crediti, calendario) non generano né card né brain dump. Sono informazioni logistiche, non contenuto esaminabile.

---

## Principio di parsimonia estrema

Genera il **minor numero possibile** di card per coprire i fatti puntuali della sezione. Prima di aggiungere una card, chiediti: *questa informazione è davvero autonoma e non recuperabile ragionando dalla rete concettuale?* Se il dato è derivabile da un'altra card o dal brain dump, non generarlo.

Una sezione con un solo fatto puntuale produce una sola card. Una sezione interamente relazionale produce zero card e un brain dump.

---

## Criterio discriminante: Anki vs brain dump

**Una card va in `anki` se il fatto sta in piedi da solo**, indipendentemente dalla rete concettuale in cui è inserito. Va nel **brain dump** se vive dentro una rete — richiede di ricostruire relazioni, gerarchie, topografie, o strutture complesse.

### Va in Anki:
- Dati non derivabili: origine, inserzione, innervazione, azione di un muscolo
- Nomi di rami nervosi, forami, legamenti specifici
- Tipo di articolazione, superfici articolari, gradi di libertà
- Territorio di distribuzione di un vaso o nervo specifico
- Card predittive puntuali (es. "quale nervo passa nel solco del nervo radiale?")
- Card cliniche puntuali (es. "dove si palpa il tendine d'Achille?")
- Card di confronto puntuali (es. "epifisi vs diafisi: tipo di tessuto osseo")

### Va nel brain dump:
- **Architettura interna** di strutture: composizione e organizzazione di un osso, un'articolazione, un disco, un organo
- **Topografia regionale**: rapporti tra strutture, decorsi, logica dei piani anatomici
- **Patogenesi clinica**: sequenze "condizione X → effetto Y → sintomo Z" appartengono sempre al brain dump, anche quando brevi. Esempio: "infiammazione → liquido viscoso → aderenze → limitazione del movimento" è una catena, non un fatto puntuale.
- Card predittive relazionali (es. "se il nervo radiale è lesionato, cosa succede?" — la risposta richiede di ricostruire l'intero territorio)
- Card di confronto sistemici tra strutture di regioni diverse

### Tipi di brain dump:
- `architettura` — composizione e organizzazione interna di una struttura
- `topografia` — rapporti spaziali, decorsi, logica dei piani

---

## Regole generali (blocco Anki)

1. **Fonte esclusiva — senza elaborazione.** Usa solo informazioni presenti nel documento sorgente. Non aggiungere dettagli, specificazioni o aggettivi non presenti nel testo (es. se la sbobina dice "sinapsi specializzata", non scrivere "sinapsi chimica specializzata"). Parafrasa, ma non completare.

2. **Retro mai telegrafici.** Il retro deve includere contesto sufficiente per fissare il concetto, mai una singola parola isolata. Esempio: "Nervo ascellare (C5-C6), ramo terminale del fascicolo posteriore del plesso brachiale" è meglio di solo "Nervo ascellare."

3. **Una domanda, una risposta.** Ogni card testa un singolo concetto o collegamento. Il fronte deve porre **una sola domanda** — mai "qual è X e perché Y" nello stesso fronte. Il retro deve rispondere solo a quella domanda — mai aggiungere il meccanismo quando il fronte chiedeva un nome, o il contesto clinico quando il fronte chiedeva una struttura. Se ci sono due fatti distinti, sono due card separate.

   **Esempio di violazione**: fronte "da quale struttura viene rilasciato il Ca²⁺?" → retro che aggiunge la propagazione della depolarizzazione attraverso i tubuli T e il potenziale di placca. Il retro corretto è solo: "Reticolo sarcoplasmatico — rilascia ioni Ca²⁺ nel citosol quando la fibra muscolare si depolarizza." Tutto il resto è sequenza di eventi e appartiene al brain dump.

4. **Domande esplicite a cue funzionale.** Il fronte deve essere una domanda chiara, specifica, e formulata come cue funzionale (es. "cosa succede se…", "quale struttura è responsabile di…", "perché…") — mai un prompt vago tipo "parlami di X."

5. **Tags gerarchici.** Usa la struttura `anatomia::macro-argomento::argomento-specifico`. Es: `anatomia::locomotore::spalla::muscoli`.

6. **Marcatori preservati.** Se il contenuto sorgente ha marcatori `[VERIFICARE]` o simili, includi il marcatore nella card come avviso.

7. **Enfasi docente.** I blocchi `> [!warning] Enfasi docente` segnalano concetti su cui il docente ha insistito. Assicurati che ogni enfasi sia coperta da almeno una card o un brain dump — **ma solo se il contenuto enfatizzato è esaminabile come fatto discreto**. Se l'enfasi riguarda un commento meta (es. "questo concetto è difficile", "il corpo umano non funziona come vi aspettate") senza produrre un fatto testabile, non generare alcuna card. Il concetto sottostante sarà coperto dal brain dump del topic.

8. **Formattazione**: Usa formattazione compatibile con Anki e SEMPRE in lowercase, tranne per nomi propri di persona. Puoi mettere le parole in grassetto se ritieni che possa essere utile per catturare l'attenzione dello studente.

9. **Deduplicazione del sorgente.** Il testo di una sezione può contenere lo stesso concetto ripetuto in forme diverse (riassunto iniziale, spiegazione dettagliata, riepilogo finale). Tratta queste come un'unica fonte: genera card solo dalla versione più completa e dettagliata, ignora le riformulazioni.

---

## Regole anti-ridondanza (CRITICHE)

### Principio di parsimonia
Genera il **minor numero di card possibile** per coprire ogni concetto. Concetti complessi con più nessi causali o angolazioni cliniche giustificano card multiple che testano **aspetti indipendenti**. Il criterio è: **ogni card deve testare un collegamento diverso, non lo stesso collegamento con parole diverse.**

### Divieto di riformulazione
**Mai due card con lo stesso back.** Se due front portano alla stessa risposta, tieni solo il cue più specifico. Questo include i **versi inversi**: "Quante vertebre cervicali esistono? → 7" e "Quale regione ha 7 vertebre? → cervicale" hanno back equivalenti — tieni solo la domanda più specifica, elimina l'altra.

**Divieto di sottoinsieme**: se la risposta della card A è contenuta nella risposta della card B (es. card A: "quale curva è convessa anteriormente in cervicale?" → "lordosi cervicale"; card B: "quali curve sono convesse anteriormente?" → "lordosi cervicale e lombare"), elimina card A e tieni solo card B, che testa la conoscenza completa.

### Verso inverso ristretto
Genera la card inversa (es. nome→innervazione E innervazione→muscoli) **solo** quando si verifica almeno una di queste condizioni:
- Il termine ha **sinonimi confondibili** (es. ginglimo angolare vs. ginglimo assiale)
- Fa parte di una **serie simile** dove la discriminazione è utile (es. 6 tipi di articolazione per forma)
- L'associazione **non è ovvia** nella direzione inversa (es. dato un nervo, ricordare tutti i muscoli che innerva)

**NON** generare il verso inverso per:
- Termini unici e non confondibili (es. rotula, sarcomero, miotubo)
- Associazioni ovvie in entrambe le direzioni
- Strutture che non fanno parte di un set confrontabile

---

## Distribuzione target (blocco Anki)

| Tipo | % | Quando |
|------|---|--------|
| Fattuale diretta | ~50% | Recall puro da tabelle e testo fattuale |
| Predittiva | ~20% | "Se X, cosa succede a Y?" — relazioni puntuali |
| Clinica/applicativa | ~15% | Solo se la correlazione clinica è nel testo |
| Confronto | ~15% | Discriminazione tra strutture simili — solo confronti puntuali |

---

## Istruzioni per tipo (blocco Anki)

### Card fattuali dirette (~50%)

Card di recall puro dalle tabelle e dal testo fattuale:
- Per muscoli: card separate per origine, inserzione, azione, innervazione
- Per articolazioni: tipo, superfici articolari, gradi di libertà, movimenti consentiti
- Per legamenti: inserzioni, funzione meccanica, posizione di massima tensione
- Per vasi/nervi: origine, decorso, territorio di distribuzione

Applica il **verso inverso ristretto**: genera il verso inverso solo secondo le condizioni sopra.

Esempio:
```json
{
  "type": "fattuale",
  "front": "Qual è l'innervazione del muscolo deltoide?",
  "back": "Nervo ascellare (C5-C6), ramo terminale del fascicolo posteriore del plesso brachiale.",
  "tags": ["anatomia::locomotore::spalla::muscoli"]
}
```

### Card predittive (~20%)

Card "Se X, allora cosa succede a Y?" **puntuali** — basate su relazioni funzionali dirette:
- Lesioni nervose specifiche → deficit motori/sensitivi locali
- Posizioni articolari → legamenti in tensione
- Varianti anatomiche → conseguenze funzionali

**Non includere** predittive che richiedono di ricostruire un intero territorio nervoso o vascolare — quelle vanno nel brain dump.

Esempio:
```json
{
  "type": "predittiva",
  "front": "Se il nervo ascellare viene lesionato (es. lussazione della spalla), quale movimento è compromesso?",
  "back": "Abduzione del braccio oltre i primi 15° è gravemente compromessa, perché il deltoide (principale abduttore) è paralizzato. Residua solo l'abduzione iniziale da parte del sovraspinato.",
  "tags": ["anatomia::locomotore::spalla::muscoli", "anatomia::clinica"]
}
```

### Card cliniche/applicative (~15%)

Card che collegano anatomia a patologie o applicazioni cliniche — **solo quando la correlazione è presente nella sbobina**:
- Sindromi da compressione
- Lussazioni e instabilità
- Punti di repere per procedure cliniche
- Meccanismi degenerativi

Esempio:
```json
{
  "type": "clinica",
  "front": "Perché la gleno-omerale è l'articolazione che si lussa più frequentemente?",
  "back": "Massima mobilità a scapito della stabilità intrinseca: il raggio di curvatura della testa omerale è molto maggiore della cavità glenoidea. La stabilità dipende quasi interamente da strutture capsulo-legamentose e dalla cuffia dei rotatori.",
  "tags": ["anatomia::locomotore::spalla::articolazione", "anatomia::clinica"]
}
```

### Card di confronto (~15%)

Card che forzano la discriminazione tra strutture simili — **solo confronti puntuali** (stessa sezione, proprietà specifiche):
- Muscoli con azioni simili ma innervazione diversa
- Fasci dello stesso legamento con funzioni diverse
- Strutture topograficamente vicine con proprietà distinte
- Articolazioni con forma simile ma funzione diversa

**Nota:** Le card di confronto cross-sezione (tra concetti di sezioni diverse) sono fatte manualmente dopo l'import. Qui genera solo confronti all'interno della stessa sezione.

Esempio:
```json
{
  "type": "confronto",
  "front": "Qual è la differenza funzionale tra il fascio anteriore e il fascio posteriore del legamento gleno-omerale inferiore (LGOI)?",
  "back": "Fascio anteriore: si tende a 90° di abduzione + rotazione esterna, resiste alla traslazione antero-inferiore (lesione di Bankart). Fascio posteriore: si tende in flessione + rotazione interna, resiste alla traslazione postero-inferiore.",
  "tags": ["anatomia::locomotore::spalla::legamenti"]
}
```

---

## Regole brain dump

- Crea un brain dump per ogni struttura/argomento della sezione che richiede di ricostruire una rete concettuale (architettura o topografia).
- Il campo `context` deve indicare brevemente da quale parte della lezione viene l'argomento (es. "sezione sull'articolazione gleno-omerale").
- La checklist deve contenere i punti chiave che uno studente dovrebbe saper ricostruire senza guardare appunti. Formulali come obiettivi di recall: "Nominare le componenti di…", "Descrivere il decorso di…", "Spiegare il rapporto tra…".
- Usa il formato `- [ ] punto chiave` per ogni voce.
- **Ridondanza tra Anki e brain dump: quando è legittima.** La presenza dello stesso fatto in una card Anki e in una checklist è legittima quando le due funzioni cognitive sono diverse: la card testa il recupero isolato del dato ("quante vertebre cervicali?"), la checklist lo usa come nodo in una rete più ampia ("nel contesto della colonna, spiega la progressione dimensionale e il suo significato funzionale"). È illegittima quando la voce della checklist ripete esattamente la domanda della card senza aggiungere contesto relazionale — in quel caso elimina la voce dalla checklist (il brain dump assume i fatti puntuali già coperti in Anki come dati noti).
- **Densità minima**: un brain dump su un topic complesso deve avere abbastanza item da testare realmente la comprensione — almeno 4-5 checkpoint. Un brain dump con 2 item non è un test della rete concettuale, è una lista.

Esempio:
```json
{
  "title": "Architettura della spalla: strutture ossee e legamentose",
  "type": "architettura",
  "context": "Sezione sull'articolazione gleno-omerale",
  "checklist": [
    "- [ ] Nominare le ossa che compongono il complesso della spalla",
    "- [ ] Descrivere i tre legamenti gleno-omerali e le loro inserzioni",
    "- [ ] Spiegare il ruolo del labbro glenoideo nella stabilizzazione",
    "- [ ] Identificare i punti di massima vulnerabilità della capsula"
  ]
}
```

---

## Documento sorgente

Elabora il seguente documento:
