# Prompt Istologia — Generazione Flashcard Anki (v3)

Ricevi il testo di una sbobina di istologia. Genera flashcard e brain dump in formato JSON.

## Nota sulle card di riconoscimento visivo
Le card di identificazione tissutale da immagine NON vengono generate da questo prompt. Vanno create manualmente con Image Occlusion. Questo prompt genera solo card testuali.

---

## Formato output

Restituisci un oggetto JSON con due campi:

```json
{
  "anki": [
    {
      "front": "Testo della domanda",
      "back": "Testo della risposta con contesto sufficiente",
      "tags": ["istologia::macro-argomento::argomento-specifico"]
    }
  ],
  "brain_dumps": [
    {
      "title": "Titolo del topic",
      "type": "confronto_tissutale|architettura_organo",
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
- **→ Brain dump**: il topic richiede di ricostruire un confronto sistematico o un'architettura → genera UN brain dump con checklist, e al massimo 1-2 card Anki sullo stesso topic (solo per fatti completamente isolati)

**Il brain dump non è un'aggiunta alle card. È un'alternativa che le sostituisce.**

### Discriminante card Anki vs brain dump per topic con rete

Quando un topic ha un brain dump (confronto tissutale o architettura organo), le card Anki ammesse sullo stesso topic sono quelle che testano **fatti puntuali non derivabili dal confronto** (nome di un marcatore specifico, colorazione tipica, presenza di una struttura specifica). Non sono ammesse card che testano **la logica del confronto** ("quali sono le differenze tra X e Y?"), **l'architettura complessiva**, o **il perché** di una caratteristica tissutale con risposta a catena — queste appartengono al brain dump.

Un fatto puntuale può apparire sia in Anki sia nella checklist del brain dump se le funzioni cognitive sono diverse: Anki testa il recupero isolato del dato, il brain dump lo usa come nodo in un ragionamento. Questa ridondanza è legittima. È illegittima solo quando la voce del brain dump ripete la domanda della card senza aggiungere contesto relazionale.

---

## Filtro conoscenza generale (CRITICO)

Prima di generare qualsiasi card, filtra il materiale con questa domanda: **uno studente di medicina al primo anno saprebbe già questa informazione senza averla studiata in modo specifico?**

Se sì, la card non si genera. Esempi di materiale da non generare:
- "Le cellule epiteliali rivestono le superfici del corpo"
- "Il tessuto connettivo ha funzione di sostegno"
- "I globuli rossi trasportano ossigeno"
- "Il fegato svolge funzioni metaboliche"

Queste sono nozioni di cultura scientifica generale. **Non sono materiale da spaced repetition**. Se la sbobina le usa come introduzione o classificazione di primo livello, ignorale o condensale in un brain dump — mai in card individuali.

**Informazioni amministrative** (formato esame, struttura del programma, crediti, calendario) non generano né card né brain dump. Sono informazioni logistiche, non contenuto esaminabile.

---

## Principio di parsimonia estrema

Genera il **minor numero possibile** di card per coprire i fatti puntuali della sezione. Prima di aggiungere una card, chiediti: *questa informazione è davvero autonoma e non recuperabile ragionando dalla rete concettuale?* Se il dato è derivabile da un'altra card o dal brain dump, non generarlo.

Una sezione con un solo fatto puntuale produce una sola card. Una sezione interamente relazionale produce zero card e un brain dump.

---

## Criterio discriminante: Anki vs brain dump

**Una card va in `anki` se il fatto sta in piedi da solo**, indipendentemente dalla rete concettuale in cui è inserito. Va nel **brain dump** se richiede di ricostruire un confronto sistematico tra tessuti o l'architettura complessa di un organo.

### Va in Anki:
- Proprietà puntuali di tessuti e cellule: colorazioni, marcatori funzionali, localizzazioni specifiche
- Card meccanismo puntuali (es. "perché l'epitelio delle vie respiratorie è pseudostratificato?" — risposta diretta)
- Card predittive puntuali (es. "cosa succede alla clearance mucociliare se le ciglia sono danneggiate?")
- Card di confronto puntuali tra due tessuti su una proprietà specifica (es. "epifisi vs diafisi: tipo di tessuto osseo")

### Va nel brain dump:
- **Confronti sistemici tra tessuti simili**: quando la discriminazione richiede di tener presente più proprietà contemporaneamente (morfologia, funzione, localizzazione, colorazione, marcatori)
- **Architettura degli organi**: organizzazione degli strati, tipi cellulari per compartimento, logica struttura-funzione
- **Sequenze procedurali**: fasi di un protocollo (es. preparazione campione istologico) dove ogni step dipende dal precedente
- **Confronto sistematico tra tecniche/strumenti**: quando una sezione presenta 3 o più tecniche microscopiche o strumenti analitici da confrontare (principio, risoluzione, tipo di immagine, applicazioni), il confronto sistematico appartiene al brain dump (`confronto_metodologico`). Le card Anki sono ammesse solo per fatti puntuali non derivabili dal confronto (valore numerico di risoluzione specifico, Premio Nobel, applicazione clinica specifica citata esplicitamente).
- **"Perché" sull'aspetto microscopico**: la domanda "perché X appare come appare in H&E?" richiede quasi sempre di ricostruire la logica acidofilia/basofilia + composizione molecolare + funzione cellulare — catena a più passaggi, appartiene al brain dump. Va in Anki solo il dato osservativo puro ("X appare rosa/viola/chiaro in H&E") o un fatto meccanismo con risposta diretta in una singola freccia causale ("X è acidofilo perché ricco di actina" — un solo nesso).

### Filtro specifico istologia: il ragionamento "vedo X → deduco Y"
La logica dell'istologia è ricostruire: *osservazione microscopica → composizione molecolare → funzione cellulare*. Questa catena triadica appartiene al brain dump. Va in Anki solo uno dei tre nodi isolato (il dato visivo puro, il marcatore specifico, o la funzione puntuale), non la catena.

### Tipi di brain dump:
- `confronto_tissutale` — confronto sistematico tra tessuti simili
- `confronto_metodologico` — confronto sistematico tra tecniche microscopiche o strumenti analitici
- `architettura_organo` — organizzazione strutturale di un organo
- `sequenza_procedurale` — sequenza di passaggi tecnici con logica interna (es. preparazione campione)

---

## Regole generali (blocco Anki)

1. **Fonte esclusiva — senza elaborazione.** Usa solo informazioni presenti nel documento sorgente. Non aggiungere dettagli o specificazioni non presenti nel testo. Parafrasa, ma non completare.
2. **Retro mai telegrafici.** Il retro di ogni card deve includere contesto sufficiente per fissare il concetto, mai una singola parola isolata.
3. **Una domanda, una risposta.** Ogni card testa un singolo concetto o collegamento. Il fronte deve porre **una sola domanda** — mai "qual è X e perché Y" nello stesso fronte. Il retro deve rispondere solo a quella domanda — mai aggiungere il meccanismo quando il fronte chiedeva un nome, o la correlazione clinica quando il fronte chiedeva una caratteristica tissutale. Se ci sono due fatti distinti, sono due card separate.

   **Esempio di violazione**: fronte "qual è la definizione di tessuto?" → retro che aggiunge la nota sull'origine embrionale. Il retro corretto è solo la definizione. La nota sull'origine embrionale è un fatto separato e, se rilevante, va in una card distinta.
4. **Domande esplicite.** Il fronte deve essere una domanda chiara e specifica, mai un prompt vago tipo "Parlami di X."
5. **Tags gerarchici.** Usa tags che seguano la struttura: `istologia::macro-argomento::argomento-specifico`.
6. **Marcatori preservati.** Se il contenuto sorgente ha marcatori `[VERIFICARE]` o simili, includi il marcatore nella card come avviso.
7. **Enfasi docente.** I blocchi `> [!warning] Enfasi docente` segnalano concetti su cui il docente ha insistito. Assicurati che ogni enfasi sia coperta da almeno una card o un brain dump — **ma solo se il contenuto enfatizzato è esaminabile come fatto discreto**. Se l'enfasi riguarda un giudizio meta senza produrre un fatto testabile, non generare una card apposita.

---

## Regole anti-ridondanza

### Divieto di riformulazione
**Mai due card con lo stesso back.** Se due front portano alla stessa risposta, tieni solo il cue più specifico.

**Divieto di sottoinsieme**: se la risposta della card A è interamente contenuta nella risposta della card B, elimina card A e tieni solo card B, che testa la conoscenza completa.

---

## Distribuzione target (blocco Anki)

| Tipo | % | Quando |
|------|---|--------|
| Fattuale diretta | ~30% | Proprietà puntuali: colorazione, marcatori, localizzazione, caratteristica morfologica specifica |
| Meccanismo/perché | ~30% | Logica struttura→funzione puntuale |
| Predittiva | ~20% | Conseguenze funzionali puntuali di alterazioni tissutali |
| Confronto | ~20% | Discriminazione puntuale tra due tessuti su una proprietà specifica |

---

## Istruzioni per tipo (blocco Anki)

### Card meccanismo/perché (~40%)

Card struttura→funzione che testano la comprensione del perché un tessuto è organizzato in un certo modo:
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

### Card predittive (~30%)

Card su conseguenze funzionali puntuali di alterazioni tissutali, quando presenti nella sbobina:
- Cosa succede se un tessuto perde una caratteristica specifica
- Conseguenze di metaplasie o alterazioni circoscritte
- Effetti della perdita di un componente specifico

Esempio:
```json
{
  "type": "predittiva",
  "front": "Cosa succede alla funzione respiratoria se l'epitelio ciliato viene danneggiato (es. dal fumo cronico)?",
  "back": "Si perde la clearance mucociliare: il muco e le particelle intrappolate non vengono più trasportate verso la faringe. Questo porta a ristagno di secrezioni, maggiore suscettibilità alle infezioni, e tosse cronica come meccanismo compensatorio di pulizia.",
  "tags": ["istologia::epiteliale::pseudostratificato", "istologia::clinica"]
}
```

### Card di confronto (~30%)

Card che forzano la discriminazione puntuale tra due tessuti su una singola proprietà — **non confronti sistemici** (quelli vanno nel brain dump):
- Due tessuti che differiscono su una caratteristica specifica (cheratinizzazione, tipo di collagene, ecc.)
- Ghiandole con meccanismi di secrezione diversi

Esempio:
```json
{
  "type": "confronto",
  "front": "Qual è la differenza tra epitelio stratificato cheratinizzato e non cheratinizzato?",
  "back": "Entrambi sono pluristratificati pavimentosi con funzione protettiva. Il cheratinizzato (epidermide) ha strati superficiali di cellule morte piene di cheratina, resiste all'abrasione meccanica e alla disidratazione. Il non cheratinizzato (esofago, vagina, cornea) mantiene le cellule superficiali nucleate e umide, protegge da attrito in ambienti interni umidi.",
  "tags": ["istologia::epiteliale::stratificato::confronto"]
}
```

---

## Regole brain dump

- Crea un brain dump per ogni confronto sistematico tra tessuti simili o per ogni organo la cui architettura è descritta nella sezione.
- Il campo `context` deve indicare brevemente da quale parte della lezione viene l'argomento.
- La checklist deve contenere i punti chiave che uno studente dovrebbe saper ricostruire senza guardare appunti: proprietà da confrontare, strati da nominare, tipi cellulari da identificare. Formulali come obiettivi di recall.
- Usa il formato `- [ ] punto chiave` per ogni voce.
- **Ridondanza tra Anki e brain dump: quando è legittima.** La presenza dello stesso fatto in una card Anki e in una checklist è legittima quando le due funzioni cognitive sono diverse: la card testa il recupero isolato del dato ("di che colore appare la struttura X in H&E?"), la checklist lo usa come nodo in un ragionamento ("nell'architettura del tessuto Y, spiega perché ogni componente appare come appare in H&E"). È illegittima quando la voce della checklist ripete esattamente la domanda della card senza aggiungere contesto relazionale — in quel caso elimina la voce dalla checklist (il brain dump assume i fatti puntuali già coperti in Anki come dati noti).
- **Densità minima**: un brain dump su un topic complesso deve avere abbastanza item da testare realmente la comprensione — almeno 4-5 checkpoint. Un brain dump con 2 item non è un test della rete concettuale, è una lista.

Esempio:
```json
{
  "title": "Epitelii di rivestimento: confronto sistematico",
  "type": "confronto_tissutale",
  "context": "Sezione sugli epiteli di rivestimento",
  "checklist": [
    "- [ ] Classificare gli epiteli per numero di strati (semplice, pseudostratificato, stratificato)",
    "- [ ] Per ogni tipo, indicare la forma delle cellule superficiali e la sede principale",
    "- [ ] Distinguere cheratinizzato da non cheratinizzato: sede, funzione, aspetto",
    "- [ ] Descrivere l'urotelio: caratteristica morfologica in distensione vs contrazione"
  ]
}
```

---

## Documento sorgente
Elabora il seguente documento:
