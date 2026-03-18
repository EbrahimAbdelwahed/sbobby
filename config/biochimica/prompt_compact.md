# Prompt — Documento di Studio Compatto (Biochimica)

Ricevi una sbobina rielaborata di una lezione di biochimica. Produci un **documento di studio compatto** a partire dal suo contenuto.

## Cosa questo documento è

Il documento compatto è una versione ripulita della sbobina d'archivio: stessa struttura, stesso livello di dettaglio nei descrittivi, senza le ridondanze interne. **Non è un riassunto.** Non comprime i concetti: elimina solo ciò che è duplicato o irrilevante allo studio.

## Cosa eliminare

Elimina esclusivamente:

1. **Ridondanza interna esplicita.** Se lo stesso concetto compare in due punti diversi della sbobina (es. in un blocco descrittivo e in un riepilogo rapido finale), mantienilo solo una volta, nella sede più ricca. I "Riepilogo rapido" in coda ai blocchi devono essere mantenuti, ma se sono pura replica del descrittivo, accorcia o semplifica il descrittivo anziché eliminare il riepilogo.
2. **Logistica e organizzazione.** Blocchi che contengono esclusivamente informazioni su orari, aule, contatti docenti, suddivisione del monte ore, frequenze obbligatorie e simili. Se un blocco mescola logistica e contenuto biochimico, elimina solo la parte logistica.
3. **Filler verbale.** Formulazioni ridondanti che esprimono lo stesso concetto con parole diverse, senza aggiungere informazione.

## Cosa non eliminare

- Qualsiasi concetto biochimico, clinico o fisiopatologico menzionato nella sbobina, anche se sintetico.
- Le correlazioni cliniche: vanno mantenute integralmente.
- Il contenuto marcato `> [!warning] Enfasi docente`: è obbligatoriamente incluso, senza eccezioni, nel formato callout originale.
- I marcatori `[VERIFICARE]`, `[INCOMPLETO]`, `[AUDIO INAUDIBILE]`, `[AUDIO NON TRASCRIVIBILE]`, `[→ ARGOMENTO FUTURO: ...]`.
- I "Riepilogo rapido" in coda ai blocchi: sono utili per ricerca rapida e per la generazione di flashcard. Mantienili. Se risultano troppo ridondanti rispetto al descrittivo, aggiusta il descrittivo, non il riepilogo.
- **Color coding.** Mantieni i tag `<span style="color:...">` esattamente come nel documento sorgente. Non rimuovere né modificare i colori.
- **Immagini e strutture chimiche.** Tutti gli embed `![[file.svg]]`, `![[file.png]]` e le relative didascalie in corsivo (`*nome*`) devono essere mantenuti nella posizione originale. I marker `[CHEM:]` e `[REACTION:]` non ancora renderizzati vanno preservati. **Non eliminare mai immagini o strutture chimiche durante la compattazione.**

## Come accorpare i blocchi

La sbobina d'archivio è organizzata in blocchi numerati (`## BLOCCO N — Titolo`). Il documento compatto **non usa blocchi numerati**: usa titoli tematici liberi (`## Titolo`).

Puoi accorpare due blocchi dell'archivio solo se trattano lo stesso sottoargomento con sovrapposizione diretta di contenuto (es. due blocchi separati che ripetono la stessa definizione). Non accorpare blocchi in sequenza progressiva (es. concetto → meccanismo → clinica → esempio biologico): quella progressione ha valore didattico e va mantenuta come struttura interna di un unico blocco.

Non frammentare un blocco esistente in più sezioni.

## Struttura interna di ogni sezione

Ogni sezione tematica del documento compatto contiene, nell'ordine:

1. **Concetto chiave.** 1–2 frasi che catturano l'essenza del blocco. Obbligatorio.

2. **Meccanismo / logica sottostante.** Il ragionamento o processo biochimico, compatto ma completo. È la sede principale dello studio per la comprensione. Non svuotarlo per riempire gli altri elementi: deve essere autosufficiente. Se il meccanismo nella sbobina d'archivio è già conciso, riportalo pressoché integralmente. Includi qui le immagini e le strutture chimiche nella posizione originale.

3. **Esempi biologici / correlazioni cliniche** (se presenti nella sbobina). Solo quelli esplicitamente presenti: non aggiungerne. Se assenti, ometti questa voce.

4. **Riepilogo rapido.** Sintesi per punti in coda al blocco. Mantienilo dalla sbobina d'archivio. Può essere abbreviato se risulta eccessivamente ridondante rispetto al meccanismo, ma non eliminato.

Se un blocco è puramente introduttivo o concettuale e non si presta alla struttura sopra, mantieni il filo logico della sbobina eliminando solo le ripetizioni. Il documento deve essere leggibile autonomamente, non solo come promemoria.

## Appendice tabellare

Produci un'unica appendice tabellare in coda al documento, aggregando tutte le tabelle riepilogative della lezione. Se la sbobina contiene tabelle sia inline nei blocchi che in appendice, unificale eliminando i duplicati. Le tabelle devono contenere solo dati presenti nella sbobina, senza aggiunte.

## Lunghezza e compressione

La lunghezza del documento compatto è una conseguenza dell'eliminazione delle ridondanze, non un obiettivo numerico. Non applicare un target percentuale. Se la sbobina d'archivio è già poco ridondante, il documento compatto sarà simile in lunghezza. L'obiettivo è la pulizia, non la brevità.

## Formato output

- Formato **Obsidian-native**: callout `> [!warning]`, embed `![[file]]`, `<span style="color:">` per colori
- Intestazione:
  ```
  # Biochimica — Lezione [N]: [Titolo] (Studio)
  
  > **Argomento:** [argomento principale e sottoargomenti]
  > **Blocchi consolidati:** [elenco blocchi della sbobina d'archivio che compongono questo documento]
  ```
- Sezioni tematiche con `## [Titolo]` (senza numerazione)
- Chiusura con argomenti correlati: `*Argomenti correlati: → ...*`

## Nessuna informazione aggiunta

Usa esclusivamente informazioni presenti nella sbobina sorgente. Non aggiungere spiegazioni, contesto enciclopedico o dettagli biochimici non presenti nell'originale.

---

## Documento sorgente

Elabora il seguente documento: