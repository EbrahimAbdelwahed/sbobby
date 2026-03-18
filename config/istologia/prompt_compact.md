# Prompt — Documento di Studio Compatto (Istologia)

Ricevi una sbobina rielaborata di una lezione di istologia. Produci un **documento di studio compatto** a partire dal suo contenuto.

## Cosa questo documento è

Il documento compatto è una versione ripulita della sbobina d'archivio: stessa struttura, stesso livello di dettaglio nei descrittivi, senza le ridondanze interne. **Non è un riassunto.** Non comprime i concetti: elimina solo ciò che è duplicato o irrilevante allo studio.

## Cosa eliminare

Elimina esclusivamente:

1. **Ridondanza interna esplicita.** Se lo stesso concetto compare in due punti diversi della sbobina (es. in un blocco descrittivo e in un riepilogo rapido finale), mantienilo solo una volta, nella sede più ricca. I "Riepilogo rapido" in coda ai blocchi devono essere mantenuti, ma se sono pura replica del descrittivo, accorcia o semplifica il descrittivo anziché eliminare il riepilogo.
2. **Logistica e organizzazione.** Blocchi che contengono esclusivamente informazioni su orari, aule, contatti docenti, suddivisione del monte ore, frequenze obbligatorie e simili. Se un blocco mescola logistica e contenuto istologico, elimina solo la parte logistica.
3. **Filler verbale.** Formulazioni ridondanti che esprimono lo stesso concetto con parole diverse, senza aggiungere informazione.

## Cosa non eliminare

- Qualsiasi concetto istologico, clinico o fisiopatologico menzionato nella sbobina, anche se sintetico.
- Le correlazioni cliniche: vanno mantenute integralmente.
- Il contenuto marcato `> [!warning] Enfasi docente`: è obbligatoriamente incluso, senza eccezioni, nel formato callout originale.
- I marcatori `[VERIFICARE]`, `[INCOMPLETO]`, `[AUDIO INAUDIBILE]`, `[AUDIO NON TRASCRIVIBILE]`, `[→ ARGOMENTO FUTURO: ...]`.
- I "Riepilogo rapido" in coda ai blocchi: sono utili per ricerca rapida e per la generazione di flashcard. Mantienili. Se risultano troppo ridondanti rispetto al descrittivo, aggiusta il descrittivo, non il riepilogo.
- **Immagini e placeholder.** Tutti gli embed `![[file]]` e i placeholder `> [immagine di: DESCRIZIONE]` devono essere mantenuti nella posizione originale. Non eliminare mai immagini durante la compattazione.

## Come accorpare i blocchi

La sbobina d'archivio è organizzata in blocchi numerati (`## BLOCCO N — Titolo`). Il documento compatto **non usa blocchi numerati**: usa titoli tematici liberi (`## Titolo`).

Puoi accorpare due blocchi dell'archivio solo se trattano lo stesso sottoargomento con sovrapposizione diretta di contenuto (es. due blocchi separati che ripetono la stessa definizione di un tessuto). Non accorpare blocchi in sequenza progressiva (es. morfologia → funzione → clinica → tecnica di colorazione): quella progressione ha valore didattico e va mantenuta come struttura interna di un unico blocco.

Non frammentare un blocco esistente in più sezioni.

## Struttura interna di ogni sezione

Ogni sezione tematica del documento compatto contiene, nell'ordine:

1. **Descrittivo.** Prosa organizzata che spiega morfologia, funzione e relazioni tra strutture. È la sede principale dello studio per la comprensione. Non svuotarlo per riempire i bullet: deve essere autosufficiente. Se il descrittivo della sbobina d'archivio è già conciso, riportalo pressoché integralmente. Includi qui le immagini nella posizione originale.

2. **Bullet riepilogo** (se il contenuto lo permette). Dati fattuali compressi, immediatamente sotto il descrittivo. Il formato dipende dal tipo di contenuto:
   - Per tessuti: tipo · cellule principali · matrice · localizzazione · funzione
   - Per cellule: morfologia · funzione · colorazione caratteristica
   - Per ghiandole: tipo · struttura · secreto · meccanismo di secrezione
   - Per epiteli: tipo · strati · localizzazione · funzione
   - Per colorazioni/tecniche: principio · strutture evidenziate · colore risultante · applicazione

   Se un blocco è puramente concettuale e non ha dati fattuali da riassumere in questa forma, ometti i bullet.

3. **Riepilogo rapido.** Sintesi per punti in coda al blocco. Mantienilo dalla sbobina d'archivio. Può essere abbreviato se risulta eccessivamente ridondante rispetto al descrittivo, ma non eliminato.

## Appendice tabellare

Produci un'unica appendice tabellare in coda al documento, aggregando tutte le tabelle riepilogative della lezione. Se la sbobina contiene tabelle sia inline nei blocchi che in appendice, unificale eliminando i duplicati. Le tabelle devono contenere solo dati presenti nella sbobina, senza aggiunte.

## Lunghezza e compressione

La lunghezza del documento compatto è una conseguenza dell'eliminazione delle ridondanze, non un obiettivo numerico. Non applicare un target percentuale. Se la sbobina d'archivio è già poco ridondante, il documento compatto sarà simile in lunghezza. L'obiettivo è la pulizia, non la brevità.

## Formato output

- Formato **Obsidian-native**: callout `> [!warning]`, embed immagini `![[file]]`
- Intestazione:
  ```
  # Istologia — Lezione [N]: [Titolo] (Studio)
  
  > **Argomento:** [argomento principale e sottoargomenti]
  > **Blocchi consolidati:** [elenco blocchi della sbobina d'archivio che compongono questo documento]
  ```
- Sezioni tematiche con `## [Titolo]` (senza numerazione)
- Chiusura con argomenti correlati: `*Argomenti correlati: → ...*`

## Nessuna informazione aggiunta

Usa esclusivamente informazioni presenti nella sbobina sorgente. Non aggiungere spiegazioni, contesto enciclopedico o dettagli istologici non presenti nell'originale.

---

## Documento sorgente

Elabora il seguente documento: