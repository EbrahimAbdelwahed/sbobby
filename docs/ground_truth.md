# Handover — Pipeline di Studio per Medicina (Anatomia 1 + Biochimica)

## Chi sono

Ebrahim, studente al primo anno di Medicina all'Università di Pavia, trasferito da Roma. Alloggio al Collegio Valla. Ho completato il semestre filtro con 18 CFU e media 25/30. La borsa di studio EDiSU è la mia priorità finanziaria — ogni decisione accademica è subordinata al suo mantenimento. Le lezioni di Anatomia 1 iniziano lunedì. Nello stesso semestre seguo anche Biochimica.

## Obiettivo del progetto

Costruire una pipeline semi-automatizzata che trasforma le registrazioni audio delle lezioni in materiale di studio strutturato e flashcard per Anki. Il principio guida è: **più tempo a studiare, meno tempo a processare gli strumenti di studio**.

Il framework metodologico di riferimento è P.A.C.R.A.R.: Pianificazione – Acquisizione – Comprensione – Rielaborazione – Applicazione/testing – Ricordo. La pipeline copre le fasi di Acquisizione e Rielaborazione. Le fasi di Applicazione e Ricordo sono gestite da Anki e dallo studio attivo (disegno, spiegazione orale, testing reciproco con colleghi).

## Architettura della pipeline

Il flusso è il seguente, dall'input all'output:

1. **Registrazione audio** della lezione in aula.
2. **Trascrizione locale** dell'audio con Whisper (offline, su Mac 16GB RAM).
3. **Correzione automatica** della trascrizione tramite dizionario di errori ricorrenti.
4. **Rilettura veloce** della trascrizione corretta per individuare errori residui, specialmente terminologia latina.
5. **Segmentazione** della trascrizione in blocchi tematici tramite chiamata API a LLM.
6. **Generazione SSOT** per ogni segmento tramite chiamata API a LLM con prompt strutturato.
7. **Assemblaggio** dei segmenti elaborati in un unico documento SSOT per lezione (il documento finale è uno per lezione, non uno per segmento).
8. **Integrazione enfasi docente** da sbobine anni precedenti (chiamata API parallela, opzionale).
9. **Generazione flashcard** testuali (cloze) dall'appendice tabellare del SSOT, inviate ad Anki via AnkiConnect.
10. **Creazione manuale** di flashcard Image Occlusion e card di ragionamento topografico (non automatizzabile — batch settimanale).

## Componenti del sistema

### Whisper — Trascrizione

- Modello: `large-v3` come prima scelta. Se i 16GB di RAM non reggono, fallback su `medium`.
- Implementazione preferita: whisper.cpp o MLX Whisper (ottimizzati per Apple Silicon, non il pacchetto Python originale di OpenAI).
- Parametri obbligatori: `--language it`, output con timestamp (formato vtt o srt).
- **Initial prompt**: parametro `--initial_prompt` popolato con un paragrafo discorsivo denso di terminologia anatomica pertinente alla lezione del giorno. Non una lista di termini, ma prosa che imita l'incipit di un riassunto (~200-300 parole). Questo migliora significativamente il riconoscimento dei termini latini.
- Gli initial prompt per argomento verranno generati automaticamente dal batch processing delle sbobine degli anni precedenti (vedi sezione dedicata).

### Correzione automatica

- File di testo piatto (`correzioni.txt`), una riga per errore, formato: `errore → correzione`.
- Script che legge la trascrizione, applica le sostituzioni, salva il file corretto.
- Il file si popola progressivamente durante l'uso — non serve prepopolarlo.
- Un file di correzioni per materia (anatomia e biochimica hanno terminologia diversa).

### Segmentazione

- Chiamata API a LLM che riceve la trascrizione corretta completa.
- Task: identificare i punti di cambio argomento e restituire i segmenti separati.
- Vincolo: mantenere un overlap di qualche frase tra segmenti consecutivi, perché il docente può anticipare un concetto alla fine di un blocco e svilupparlo all'inizio del successivo.
- Motivazione: le trascrizioni di lezioni da 2 ore (15-20k parole) degradano la qualità dell'output se processate in un unico blocco. Segmentare migliora il risultato e permette di parallelizzare le chiamate.

### Prompt SSOT — Il cuore della pipeline

L'output SSOT è una **sbobina rielaborata con appendice tabellare**, non un documento puramente tabellare. Il corpo principale è prosa organizzata; le tabelle sono un riassunto supplementare in coda.

#### Struttura dell'output SSOT

L'output è un unico documento per lezione (non per segmento). Quando la trascrizione viene segmentata per il processing, i segmenti elaborati vengono riassemblati in un documento finale unico.

**Corpo principale** (prosa):
- Sezione "Informazioni sul corso" per contenuti organizzativi (modalità d'esame, testi consigliati, criteri di valutazione) — presente soprattutto nelle prime lezioni introduttive.
- Blocchi con titoli per ogni macro-argomento trattato nella lezione.
- Paragrafi che seguono il filo logico dell'argomento (non l'ordine cronologico della lezione — il contenuto va riorganizzato logicamente per struttura/regione/argomento).
- Elenchi puntati dove necessario (caratteristiche di una struttura, rami di un nervo, ecc.).
- Correlazioni cliniche integrate nel punto in cui il docente le menziona, non separate.
- Enfasi del docente segnalate contestualmente con un formato inline distinguibile (callout/admonition), nel punto pertinente — non in una sezione separata. Formato: `> ⚠️ **Enfasi docente:** [contenuto]`.
- Marcatore `[VERIFICARE]` sui passaggi ambigui nella trascrizione.
- Placeholder immagini in formato standard: `> [immagine di: DESCRIZIONE]` — utilizzabili in post-processing per il matching con il file di mapping delle tavole.
- Riepilogo rapido in coda a ogni blocco: sintesi compatta per punti del contenuto del blocco, utile per ripasso veloce.
- **Tabelle contestuali**: le tabelle riassuntive di un blocco (es. muscoli della cuffia) appaiono dentro il blocco pertinente, contestualizzate dalla prosa che le precede e le espande.

**Appendice tabellare** (in coda):
- Tabelle riepilogative aggregate di tutti i muscoli, vasi, nervi e legamenti della lezione. Queste sono una raccolta compatta dei dati già presenti nelle tabelle contestuali.
- Servono per il ripasso rapido dell'intera lezione e come fonte per la generazione automatica delle flashcard cloze.
- Tabella muscoli: origine, inserzione, azione, innervazione, immagine.
- Tabella vasi: origine, decorso, rami, territorio, immagine.
- Tabella nervi: radici, decorso, rami, territorio di innervazione, immagine.
- Tabella legamenti: origine, inserzione, funzione, posizione di tensione, immagine.
- Tabella articolazioni: tipo, superfici, gradi di libertà, movimenti, immagine.
- La colonna **immagine** è presente in tutte le tabelle ma viene lasciata vuota dal modello — compilata manualmente in post-processing.

#### Livello di rielaborazione e gestione contenuti

- **Rielaborazione lieve**: la terminologia del docente viene mantenuta fedelmente nell'output — è quella che chiederà all'esame. Quando il docente usa un nome comune o non strettamente corretto, si usa la forma: `[nome usato dal docente] (anche detto: [nome anatomicamente corretto])`.
- **Aneddoti clinici**: riportati per esteso in un formato che preservi le informazioni, come correlazione clinica integrata nel testo.
- **Digressioni personali/battute**: sintetizzate al massimo e incluse solo se correlate all'argomento, altrimenti eliminate.
- **Ripetizioni**: vagliate per verificare l'aggiunta di informazioni marginali da integrare, altrimenti eliminate.
- **Informazioni organizzative**: riportate in sezione dedicata ("Informazioni sul corso") in cima all'output. Incluse solo se correlate all'esame (modalità, criteri, testi, argomenti su cui soffermarsi o esclusi). Escluse le informazioni relative alla logistica delle lezioni. Sezione omessa se non presenti nella trascrizione.

#### Principi del prompt

- Ruolo: anatomista che rielabora trascrizioni in materiale di studio strutturato.
- Non inventare informazioni assenti dalla trascrizione. Marcatori standard:
  - `[VERIFICARE]` — passaggi ambigui nella trascrizione.
  - `[INCOMPLETO]` — argomento troncato dal docente.
  - `[AUDIO INAUDIBILE]` — porzione non trascrivibile.
  - `[→ ARGOMENTO FUTURO: nome]` — riferimento esplicito del docente a un argomento di una lezione futura.
- Riorganizzare logicamente, non riprodurre l'ordine cronologico della lezione.
- Mantenere le spiegazioni e i ragionamenti del docente — non comprimere tutto in dati secchi.
- Il livello di dettaglio dell'output dipende dalla ricchezza della trascrizione — il modello non deve aggiungere conoscenza enciclopedica propria.
- Il prompt deve includere un **esempio completo di output atteso** (il file SAMPLE_SSOT.md allegato). L'esempio definisce formato e struttura, non il livello assoluto di dettaglio o la lunghezza. Senza esempio concreto il modello interpreterà liberamente.
- Il prompt deve gestire naturalmente sia lezioni introduttive (ricche di info organizzative, povere di anatomia) sia lezioni dense di contenuto anatomico, senza necessità di modifiche.

#### Variante Biochimica

Per biochimica il corpo principale è identico nella struttura (prosa riorganizzata logicamente, tabelle contestuali nei blocchi, appendice aggregata in coda). Le differenze:
- Una sezione aggiuntiva **"Logica della via"** che cattura il ragionamento del docente sulla sequenza metabolica (perché ogni reazione prepara la successiva, senso termodinamico della regolazione).
- Tabelle contestuali e appendice con colonne diverse: enzima, substrato, prodotto, cofattori, regolazione (attivatori/inibitori), localizzazione cellulare.
- Per enzimi singoli: classificazione, reazione catalizzata, cinetica rilevante, patologia associata al deficit.

### Estrazione enfasi da sbobine anni precedenti

- Prompt dedicato che riceve una sbobina e restituisce: argomenti enfatizzati, domande d'esame citate, argomenti esplicitamente saltati, pattern valutativi del docente.
- Output strutturato e conciso.
- Aggiunta: il prompt deve anche generare un **elenco di termini anatomici** per ogni argomento. Questi elenchi diventano gli initial prompt per Whisper, pronti all'uso argomento per argomento.
- Il processing è in batch: tutte le sbobine degli anni precedenti vengono processate in blocco prima dell'inizio delle lezioni.
- L'output aggregato per argomento forma il **"dossier esaminatore"**: un documento per argomento con le enfasi di più anni, che rivela pattern ricorrenti.
- **Formato sbobine disponibili:** un unico file SSOT per anno (~100 pagine, tutte le lezioni), prevalentemente muri di testo. Disponibili per gli ultimi 7 anni. Formato DOC o PDF — serve estrazione testo come primo step del batch processing.

### Generazione flashcard e Anki

- Le card **cloze tabellari** vengono generate automaticamente dall'appendice tabellare del SSOT.
- Flusso: script estrae le tabelle → genera card cloze → le invia ad Anki via AnkiConnect API (no CSV, no import manuali).
- Massimo 3 cloze per card. I cloze sono indipendenti (non tutti oscurati contemporaneamente).
- Le card **Image Occlusion** (tavole dell'atlante con etichette oscurate) vengono create manualmente in batch settimanale con l'add-on Image Occlusion Enhanced di Anki. Non automatizzabili.
- Le card di **ragionamento topografico** ("quale struttura è immediatamente posteriore a X?") vengono scritte manualmente durante la fase di rielaborazione. Sono le card a più alto valore cognitivo.
- Per biochimica: le card Image Occlusion si applicano a schemi delle vie metaboliche (stesso principio, su diagrammi di flusso). Le card di ragionamento ("perché X è il punto di regolazione di Y?") hanno peso maggiore rispetto ad anatomia.

### File di mapping argomento → tavole atlante

- File strutturato (CSV o JSON) con colonne: argomento, lezione, tavole corrispondenti.
- Si popola progressivamente lezione per lezione.
- Funzione: aggiungere automaticamente riferimenti visivi alle card testuali; servire come indice personale dell'atlante organizzato per argomento di lezione.

## Scelte architetturali

### Multi-materia per design

Il progetto è un singolo sistema con una **configurazione per materia**, non progetti separati. Una cartella di config per materia contiene: il prompt SSOT specifico, il file di correzioni Whisper specifico, gli initial prompt per argomento, il template delle card Anki. Lo script principale legge la config e gestisce il flusso in modo agnostico rispetto alla materia. L'aggiunta di una nuova materia deve ridursi alla creazione di una nuova cartella di config.

### LLM via API

- Modello default: DeepSeek V3.2. Fallback: Kimi K2.
- Entrambi compatibili con formato OpenAI (`/v1/chat/completions`).
- Tutte le chiamate sono via API, offline non è un requisito.
- Il costo deve restare nell'ordine di pochi euro per l'intero corpus di sbobine e per il processing settimanale delle lezioni.

### Posizioni definite

- **Sbobine altrui**: non le uso come base di studio. Le uso esclusivamente come fonte per l'estrazione automatica delle enfasi del docente e dei pattern d'esame. Possibile utilizzo puntuale come testo di controllo quando la mia trascrizione ha lacune.
- **Color coding**: non lo uso come metodo di annotazione estensivo. L'unico uso del colore è la convenzione standard dell'atlante (arterie rosso, vene blu, nervi giallo), che è già nativa nelle tavole.
- **Appunti in aula**: non prendo appunti tradizionali. L'acquisizione avviene interamente tramite registrazione audio.

## Sequenza di implementazione

### Fase 1 — Fondamenta (pre-lunedì)
1. Setup Whisper (installazione, test su audio campione, script bash riutilizzabile).
2. Script di correzione (file correzioni vuoto + script applicazione).
3. I tre prompt (segmentazione, SSOT principale, estrazione enfasi sbobine). Testare il prompt SSOT su una sbobina degli anni precedenti per avere feedback immediato.
4. Script orchestratore delle chiamate API (trascrizione corretta → segmentazione → SSOT per segmento → assemblaggio).
5. Setup AnkiConnect + script generazione e invio card cloze.
6. Struttura file di mapping (vuoto, con le colonne corrette).

### Fase 2 — Batch processing sbobine (pre-lunedì)
7. Raccolta e organizzazione sbobine anni precedenti per Anatomia 1.
8. Script di batch processing con prompt estrazione enfasi.
9. Generazione dossier esaminatore aggregato per argomento.
10. Estrazione degli elenchi di termini per gli initial prompt di Whisper.

### Fase 3 — Calibrazione (prima settimana di lezioni)
- Testare la pipeline end-to-end sulle prime 2-3 lezioni reali.
- Iterare il prompt SSOT se necessario (massimo 2-3 iterazioni, poi bloccarlo).
- Valutare se large-v3 è sostenibile o se serve fallback su medium.
- Iniziare a popolare il file di mapping e il dizionario di correzioni.

### Cose da NON fare prima della prima settimana di lezioni
- Non comprare libri.
- Non installare app 3D di anatomia.
- Non creare deck Anki con strutture elaborate.
- Non scrivere template per Image Occlusion.
- Non preparare il prompt SSOT per biochimica (prima stabilizzare quello di anatomia).

---

## Allegati

- **SAMPLE_SSOT.md** — Esempio completo di output SSOT per una lezione di anatomia. Definisce formato e struttura (non livello di dettaglio). Da includere nel prompt LLM come esempio di output atteso.