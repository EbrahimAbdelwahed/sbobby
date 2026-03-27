Inizio subito a fare fetch sistematico di tutte le URL indicate. Procedo in parallelo dove posso.Bene, continuo con page, block e heading.Ho tutto quello che serve. Ora scrivo la risposta sistematica punto per punto basandomi esclusivamente su quanto trovato nella documentazione ufficiale.

---

# Typst per pipeline sbobine mediche — Ricerca documentazione ufficiale

---

## 1. Figure placement

### `figure(placement: ...)` — valori accettati

Dalla documentazione ufficiale ([/docs/reference/model/figure/](https://typst.app/docs/reference/model/figure/)):

```typst
figure(
  image("img.jpg", width: 80%),
  caption: [Didascalia qui],
  placement: none,    // ← valore di default
)
```

Valori accettati per `placement`:

| Valore | Comportamento |
|--------|--------------|
| `none` | Inline nel flusso (default) |
| `auto` | Sceglie `top` o `bottom` automaticamente in base alla vicinanza |
| `top`  | Flotta in cima alla pagina |
| `bottom` | Flotta in fondo alla pagina |

**Non esistono valori `left` o `right` per `placement`.** Il floating è solo verticale (top/bottom).

Il gap tra contenuto flottante e testo è controllato da `clearance` su `place`:
```typst
#show figure: set place(clearance: 1em)
```

### Float left/right — risposta diretta

**Typst NON supporta il text wrapping nativo (CSS float left/right).** Non esiste un equivalente del `float: left/right` di CSS. Questa è una limitazione documentata e nota. Il workaround più robusto è la `grid` a due colonne:

```typst
// Immagine a destra, testo a sinistra
#grid(
  columns: (1fr, 35%),
  gutter: 1em,
  [
    Testo che scorre a sinistra. Lorem ipsum dolor sit amet,
    consectetur adipiscing elit. Pellentesque euismod...
  ],
  figure(
    image("muscolo.jpg"),
    caption: [M. bicipite brachiale],
  ),
)
```

Per immagine a sinistra:
```typst
#grid(
  columns: (35%, 1fr),
  gutter: 1em,
  figure(image("muscolo.jpg"), caption: [Figura]),
  [Testo a destra...],
)
```

**Gotcha:** La `grid` non ha wrap automatico se il testo è molto corto — entrambe le celle hanno altezza uguale. Se il testo è meno di 5-6 righe accanto all'immagine, la cella testo si chiude presto e lo spazio vuoto rimane. Non c'è soluzione "fluida" come in CSS senza workaround manuali.

### Comportamento near page break

Quando `placement` è `top` o `bottom`, Typst sposta la figura nella pagina corrente o in quella successiva in base allo spazio disponibile. Le figure flottanti vengono sempre piazzate **nell'ordine del flusso** relativo tra loro. Si può usare `place.flush()` per forzare il piazzamento delle figure pendenti prima di continuare:

```typst
#place.flush()
Questo testo appare dopo tutte le figure pendenti.
```

### Forzare figura nella stessa pagina del testo

Non esiste un parametro diretto per "tieni questa figura vicino al suo riferimento". Con `placement: none` la figura resta inline (nel flusso), ma può essere spezzata da un page break se `breakable: true`. Per tenerla intera:

```typst
#block(breakable: false)[
  #figure(image("img.jpg"), caption: [Non si spezza])
]
```

### Dimensione immagine

La dimensione si controlla sulla funzione `image`, non su `figure`:

```typst
#figure(
  image("img.jpg", width: 60%),  // % relativa alla larghezza della pagina
  caption: [Testo],
)

// Oppure in punti/cm:
image("img.jpg", width: 8cm, height: 5cm)
// fit: "cover" | "contain" | "fill" | "stretch" | "none"  (default: "cover")
image("img.jpg", width: 8cm, fit: "contain")
```

### Caption

```typst
#figure(
  image("img.jpg"),
  caption: [Testo della didascalia],   // posizione default: bottom
)

// Per tabelle, caption sopra:
#show figure.where(kind: table): set figure.caption(position: top)

// Separatore custom tra numero e testo:
#set figure.caption(separator: [ — ])

// Caption completamente custom con show rule:
#show figure.caption: it => [
  #emph(it.body) | Fig. #context it.counter.display(it.numbering)
]
```

### Referencing (cross-reference)

```typst
Come si vede in @muscolo, il...

#figure(
  image("muscolo.jpg"),
  caption: [Muscolo bicipite],
) <muscolo>

// Oppure: vedi @muscolo per dettagli
// Oppure: #ref(<muscolo>) per più controllo
```

---

## 2. Wrap del testo attorno alle immagini

**Risposta diretta: non esiste meccanismo nativo.** Typst non ha un equivalente del CSS float. Confermato dalla documentazione.

### Workaround robusti in ordine di praticità

**Opzione A — Grid a 2 colonne (consigliata):**

```typst
#let img-right(img-path, img-width, body) = grid(
  columns: (1fr, img-width),
  gutter: 1em,
  body,
  figure(image(img-path), caption: none),
)

#img-right("muscolo.jpg", 40%)[
  Il muscolo bicipite brachiale è composto da due teste.
  La testa lunga origina dal tubercolo sovraglenoideo della scapola,
  mentre la testa corta origina dal processo coracoideo.
]
```

**Opzione B — `place()` con offset manuale:**

`place()` permette overlaid positioning con `dx`/`dy`, ma **non sposta il testo** — il testo scorre sotto. Si può usare `pad(left: img-width + gap)` sul testo per creare spazio manuale:

```typst
#block(width: 100%)[
  #place(right, dx: 0pt, dy: 0pt)[
    #image("muscolo.jpg", width: 38%)
  ]
  #pad(right: 40%)[
    Il testo qui andrà a sinistra perché ha padding destra.
    Non è wrapping vero ma funziona se le righe sono abbastanza.
  ]
]
```

**Gotcha critico di place():** `place()` inserisce un elemento block-level invisible nel flusso, che può spezzare il paragrafo. Bisogna wrapparlo in `box()` se si è nel mezzo di un paragrafo.

**Interazione con page break:** La `grid` rimane unita se `breakable: false` sull'eventuale block. Con `place()` e testo corto il layout si rompe facilmente a cavallo di pagina.

---

## 3. Setup pagina e tipografia

### A4 con margini custom

```typst
#set page(
  paper: "a4",   // default è già "a4"
  margin: (top: 2.5cm, bottom: 2.5cm, left: 2.5cm, right: 2cm),
)

// Margini uniformi:
#set page(paper: "a4", margin: 2.5cm)

// Margini con inside/outside per rilegatura:
#set page(paper: "a4", margin: (inside: 3cm, outside: 2cm, top: 2.5cm, bottom: 2.5cm))
```

### Font, size, line spacing

```typst
// Font e dimensione testo principale:
#set text(
  font: "Linux Libertine",  // o "Noto Sans", "DejaVu Serif", etc.
  size: 11pt,
  lang: "it",               // importante per sillabazione e punteggiatura
)

// Line spacing (interlinea):
#set par(
  leading: 0.75em,    // spazio tra righe dello stesso paragrafo
  spacing: 1.2em,     // spazio tra paragrafi
  justify: true,      // giustificazione
  linebreaks: "optimized",  // "simple" | "optimized"
)
```

**Nota:** Non ho trovato nella documentazione un parametro esplicito `line-height` come in CSS. `leading` è lo spazio **aggiuntivo** tra baseline e baseline successiva, non il line-height totale.

### Numerazione pagine

```typst
// Modo semplice: numero in basso al centro (default di number-align)
#set page(numbering: "1")

// Con totale pagine:
#set page(numbering: "1 / 1")

// Allineato a destra in basso:
#set page(numbering: "1", number-align: right + bottom)

// Footer custom con numero pagina:
#set page(
  footer: context [
    #set align(right)
    #counter(page).display("1 di 1", both: true)
  ]
)
```

### Page break prima di ogni H1

```typst
// Show rule: inserisce pagebreak prima di ogni heading livello 1
#show heading.where(level: 1): it => {
  pagebreak(weak: true)
  it
}
```

`weak: true` significa "inserisci il page break solo se non siamo già all'inizio di una nuova pagina". Questo evita una pagina bianca all'inizio del documento.

### Orphans/widows

**Non ho trovato nella documentazione ufficiale parametri espliciti `orphans`/`widows` come in CSS.** Questa feature non è esposta come parametro diretto in Typst. Le opzioni disponibili sono:

- `block(sticky: true)` — tiene un blocco attaccato al successivo (usato di default sugli heading per evitare orphan heading). Può essere impostato su qualsiasi blocco.
- `block(breakable: false)` — impedisce che un blocco si spezzi tra pagine.

Per simulare widow/orphan control si può avvolgere paragrafi critici in `block(breakable: false)`, ma non c'è un parametro globale "minimo N righe in fondo/cima pagina".

---

## 4. Tabelle

### Sintassi base con header, bordi, padding

```typst
#figure(
  table(
    columns: (2fr, 1fr, 1fr, 2fr),
    inset: 8pt,
    align: (left, center, center, left),
    stroke: 0.7pt + black,

    // Header
    table.header(
      [*Muscolo*], [*Origine*], [*Inserzione*], [*Azione*],
    ),

    // Righe dati
    [Bicipite brachiale], [Scapola], [Radio], [Flessione avambraccio],
    [Tricipite brachiale], [Scapola + omero], [Ulna], [Estensione avambraccio],
  ),
  caption: [Muscoli del braccio],
)
```

### Impedire spezzatura tra pagine

Per default le tabelle **sono breakable**. Per impedirlo:

```typst
// Opzione A: blocco non breakable attorno alla tabella
#block(breakable: false)[
  #table(...)
]

// Opzione B: set globale per tutte le tabelle
#show table: set block(breakable: false)

// Opzione C: per tabelle grandi (breakable ma con header ripetuto)
table(
  ...,
  table.header(repeat: true)[...],  // header si ripete ad ogni pagina
)
```

### Larghezza colonne

```typst
// Frazioni (proporzionale):
columns: (1fr, 2fr, 1fr)

// Assoluto + auto:
columns: (3cm, auto, auto)

// Percentuale:
columns: (30%, 40%, 30%)

// N colonne uguali:
columns: 4   // shorthand per 4 colonne auto
```

### Shading alternato righe

```typst
#table(
  fill: (x, y) =>
    if calc.odd(y) { luma(240) } else { white },
  columns: 3,
  ..
)
```

### Celle con colspan/rowspan

```typst
table(
  columns: 3,
  table.cell(colspan: 2)[Intestazione grande], [Singola],
  [A], [B], [C],
  table.cell(rowspan: 2)[Spanna 2 righe], [D], [E],
  [F], [G],
)
```

---

## 5. Box con bordo laterale (riepilogo rapido)

Typst supporta il `stroke` per lato singolo tramite dictionary. Per un box con solo bordo sinistro:

```typst
#block(
  fill: luma(235),           // sfondo grigio chiaro
  inset: (left: 12pt, right: 8pt, top: 8pt, bottom: 8pt),
  stroke: (left: 3pt + rgb("#0066cc")),  // bordo solo a sinistra
  width: 100%,
  [
    *Riepilogo rapido*
    
    - Punto chiave 1
    - Punto chiave 2
    - Punto chiave 3
  ]
)
```

### Impedire spezzatura del box

```typst
#block(
  breakable: false,          // ← impedisce split tra pagine
  fill: luma(235),
  inset: (left: 12pt, top: 8pt, right: 8pt, bottom: 8pt),
  stroke: (left: 3pt + eastern),
  width: 100%,
)[
  Contenuto del riepilogo...
]
```

**Gotcha:** se il contenuto è molto lungo, `breakable: false` può causare il salto a una nuova pagina intera se non c'è spazio sufficiente. Per box lunghi è meglio lasciare `breakable: true` (default).

---

## 6. Integrazione con Python

### CLI base

```bash
typst compile input.typ output.pdf
```

### Parametri CLI utili

```bash
# Font path custom:
typst compile --font-path ./fonts input.typ output.pdf

# Root directory (per path relativi nel .typ):
typst compile --root /path/to/project input.typ output.pdf

# Passare variabili/dati a Typst:
typst compile --input titolo="Sbobine Anatomia" --input data="2024-03-15" input.typ output.pdf
```

### Leggere variabili in Typst da `--input`

```typst
// In input.typ:
#let titolo = sys.inputs.at("titolo", default: "Documento")
#let data = sys.inputs.at("data", default: "")

= #titolo
Data: #data
```

### Da Python con subprocess

```python
import subprocess
import sys

def compile_typst(input_path: str, output_path: str, variables: dict = None):
    cmd = ["typst", "compile"]
    
    if variables:
        for key, value in variables.items():
            cmd.extend(["--input", f"{key}={value}"])
    
    cmd.extend([input_path, output_path])
    
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        raise RuntimeError(f"Typst error:\n{result.stderr}")
    
    return output_path

# Uso:
compile_typst(
    "sbobina.typ",
    "sbobina.pdf",
    variables={
        "titolo": "Anatomia del Braccio",
        "img_base": "/path/to/images"
    }
)
```

### Libreria Python wrapper

Non ho trovato nella documentazione ufficiale di Typst riferimento a una libreria Python ufficiale. Esiste su PyPI un package chiamato `typst` (wrapper non ufficiale attorno alla CLI), ma la via canonica e più stabile è `subprocess`. Per generazione programmatica del `.typ`, si raccomanda di generare il file come stringa Python e poi compilarlo.

---

## 7. Generazione programmatica del file .typ

### Struttura base di un file .typ

```typst
// ── PREAMBOLO (set/show rules globali) ──────────────────────────────

#set page(paper: "a4", margin: 2.5cm, numbering: "1")
#set text(font: "Linux Libertine", size: 11pt, lang: "it")
#set par(leading: 0.75em, justify: true)
#set heading(numbering: none)

// ── IMPORT di moduli/template ────────────────────────────────────────

#import "template.typ": quick-recap, float-right-img

// ── CONTENUTO ────────────────────────────────────────────────────────

= Titolo del Capitolo

Testo del documento...
```

### Includere immagini da path

```typst
// Path relativo al file .typ:
image("images/muscolo.jpg")

// Path assoluto (usare con --root in CLI):
image("/assets/schema_arto.png")

// Con variabile da sys.inputs:
image(sys.inputs.at("img_path") + "/muscolo.jpg")
```

### Escape di caratteri speciali

In Typst il carattere di escape è `\`:

| Carattere | Significato | Escape |
|-----------|-------------|--------|
| `#` | Inizio code expression | `\#` |
| `*` | Bold | `\*` |
| `_` | Italic | `\_` |
| `=` | Heading (a inizio riga) | `\=` |
| `[` `]` | Content block | `\[` `\]` |
| `<` `>` | Label | `\<` `\>` |
| `@` | Reference | `\@` |
| `~` | Non-breaking space | `\~` |

In Python, quando si genera il testo della sbobina:

```python
def escape_typst(text: str) -> str:
    """Escapa caratteri speciali Typst nel testo."""
    # Ordine importante: prima backslash, poi gli altri
    text = text.replace("\\", "\\\\")
    text = text.replace("#", "\\#")
    text = text.replace("*", "\\*")
    text = text.replace("_", "\\_")
    text = text.replace("[", "\\[")
    text = text.replace("]", "\\]")
    text = text.replace("@", "\\@")
    # '=' solo a inizio riga è pericoloso, gestirlo separatamente
    return text
```

### Import di moduli separati

```typst
// In template.typ definisci funzioni:
#let quick-recap(body) = block(
  fill: luma(235),
  inset: (left: 12pt, top: 8pt, right: 8pt, bottom: 8pt),
  stroke: (left: 3pt + eastern),
  width: 100%,
  body
)

// In input.typ:
#import "template.typ": quick-recap

#quick-recap[
  Contenuto del riepilogo
]

// Importare tutto con *:
#import "template.typ": *
```

---

## 8. Template completo funzionante

Questo template implementa tutti i pattern discussi sopra con una sbobina di anatomia fittizia ma realistica.

```typst
// ═══════════════════════════════════════════════════════════════════
// SBOBINA MEDICA — TEMPLATE COMPLETO
// File: sbobina.typ
// Compile: typst compile sbobina.typ output.pdf
// ═══════════════════════════════════════════════════════════════════

// ── SETUP PAGINA ────────────────────────────────────────────────────
#set page(
  paper: "a4",
  margin: (top: 2.5cm, bottom: 2.5cm, left: 2.5cm, right: 2cm),
  numbering: "1",
  number-align: center + bottom,
  header: context [
    #set text(8pt, fill: luma(120))
    #smallcaps[Anatomia — Corso di Laurea in Medicina]
    #h(1fr)
    #datetime.today().display("[day]/[month]/[year]")
  ],
)

// ── TIPOGRAFIA ───────────────────────────────────────────────────────
#set text(
  font: "Linux Libertine",
  size: 11pt,
  lang: "it",
)

#set par(
  leading: 0.75em,
  spacing: 1.2em,
  justify: true,
  linebreaks: "optimized",
)

// ── HEADING: page break prima di H1, stile gerarchia ────────────────
#show heading.where(level: 1): it => {
  pagebreak(weak: true)
  v(0.5em)
  block(
    width: 100%,
    fill: rgb("#003366"),
    inset: (x: 10pt, y: 8pt),
    radius: 3pt,
    text(fill: white, size: 16pt, weight: "bold", it.body)
  )
  v(0.5em)
}

#show heading.where(level: 2): it => {
  v(0.4em)
  text(size: 13pt, weight: "bold", fill: rgb("#003366"), it.body)
  v(0.2em)
}

#show heading.where(level: 3): it => {
  v(0.3em)
  text(size: 11pt, weight: "bold", it.body)
  v(0.1em)
}

// ── FUNZIONI UTILITY ─────────────────────────────────────────────────

// Box riepilogo rapido con bordo laterale sinistro
#let quick-recap(title: "Riepilogo rapido", body) = block(
  breakable: false,
  fill: luma(240),
  inset: (left: 12pt, right: 10pt, top: 10pt, bottom: 10pt),
  stroke: (left: 4pt + rgb("#0066cc")),
  width: 100%,
  [
    #text(weight: "bold", fill: rgb("#0066cc"))[#title]
    #v(0.3em)
    #body
  ]
)

// Layout immagine a destra con testo a sinistra (workaround float-right)
#let float-right(img-path, img-width: 38%, caption-text: none, body) = {
  grid(
    columns: (1fr, img-width),
    gutter: 1.2em,
    align: (top, top),
    body,
    if caption-text != none {
      figure(
        image(img-path),
        caption: caption-text,
      )
    } else {
      image(img-path)
    },
  )
}

// Layout immagine a sinistra con testo a destra
#let float-left(img-path, img-width: 38%, caption-text: none, body) = {
  grid(
    columns: (img-width, 1fr),
    gutter: 1.2em,
    align: (top, top),
    if caption-text != none {
      figure(
        image(img-path),
        caption: caption-text,
      )
    } else {
      image(img-path)
    },
    body,
  )
}

// ═══════════════════════════════════════════════════════════════════
// CONTENUTO
// ═══════════════════════════════════════════════════════════════════

= Anatomia del Braccio

== Generalità

Il braccio (_brachium_) è il segmento prossimale dell'arto superiore,
compreso tra la spalla e il gomito. È costituito da un'unica struttura
ossea, l'*omero*, attorno alla quale si organizzano i muscoli in due
logge principali: anteriore (flessori) e posteriore (estensori).

// ── IMMAGINE FLOAT-RIGHT (workaround grid) ──────────────────────────
#float-right(
  "omero_schema.jpg",        // ← sostituire con path reale
  img-width: 35%,
  caption-text: [Schema dell'omero con inserzioni muscolari],
)[
  L'omero è un osso lungo che si articola prossimalmente con la
  scapola (articolazione gleno-omerale) e distalmente con radio e
  ulna (articolazione del gomito). La testa omerale, emisferica,
  è orientata superiormente, medialmente e posteriormente.

  La diafisi presenta posteriormente il *solco del nervo radiale*,
  un'incisura elicoidale percorsa dal nervo radiale e dall'arteria
  brachiale profonda. Questa è la sede della frattura diafisaria
  più comune, con conseguente paralisi radiale.
]

#v(0.5em)

== Loggia Anteriore

La loggia anteriore del braccio contiene i muscoli flessori
dell'avambraccio: bicipite brachiale, brachiale e coracobrachiale.

=== Bicipite brachiale

Muscolo bipennnato con due teste di origine:

- *Testa lunga*: tubercolo sovraglenoideo della scapola; il tendine
  attraversa la capsula articolare e scorre nel solco bicipitale
- *Testa corta*: apice del processo coracoideo (insieme al
  coracobrachiale)

Le due teste convergono in un ventre muscolare comune che si inserisce
mediante il *tendine del bicipite* sulla tuberosità del radio e,
tramite l'*aponeurosi bicipitale* (lacertus fibrosus), sulla fascia
dell'avambraccio.

// ── IMMAGINE CENTRATA BLOCK-LEVEL ───────────────────────────────────
#figure(
  placement: none,
  image("bicipite_inserzioni.jpg", width: 70%),
  caption: [
    Inserzioni del bicipite brachiale. In rosso l'origine della
    testa lunga, in blu quella della testa corta.
  ],
) <fig-bicipite>

Come visibile in @fig-bicipite, la testa lunga ha un decorso
intrarticolare nel suo tratto prossimale.

**Azione:** flessione dell'avambraccio sul braccio (con avambraccio
in supinazione); supinazione dell'avambraccio; débole flessione
del braccio.

**Innervazione:** nervo muscolocutaneo (C5–C6).

#v(0.5em)

// ── RIEPILOGO RAPIDO ─────────────────────────────────────────────────
#quick-recap(title: "Riepilogo: Bicipite brachiale")[
  - *Origine*: testa lunga → tubercolo sovraglenoideo; testa corta → processo coracoideo
  - *Inserzione*: tuberosità del radio + aponeurosi bicipitale
  - *Azione*: flessione + supinazione avambraccio
  - *Innervazione*: n. muscolocutaneo (C5–C6)
  - *Vascolarizzazione*: a. brachiale
]

#v(0.5em)

== Loggia Posteriore

La loggia posteriore contiene il *tricipite brachiale*, unico muscolo
estensore dell'avambraccio, e il piccolo *anconeo*.

=== Tricipite brachiale

// ── IMMAGINE FLOAT-LEFT ──────────────────────────────────────────────
#float-left(
  "tricipite_schema.jpg",
  img-width: 32%,
  caption-text: [Tricipite brachiale, visione posteriore],
)[
  Il tricipite è un muscolo con tre capi:

  *Capo lungo*: origina dal tubercolo infraglenoideo della scapola;
  è l'unico capo che attraversa l'articolazione della spalla e può
  quindi esercitare un'azione su di essa.

  *Capo mediale* (o brachiale profondo): origina dalla faccia
  posteriore dell'omero, al di sotto del solco del nervo radiale.

  *Capo laterale*: origina dalla faccia posteriore dell'omero, al
  di sopra del solco radiale.
]

I tre capi convergono in un *tendine comune* che si inserisce
sull'*olecrano* dell'ulna.

**Azione principale:** estensione dell'avambraccio (il capo lungo
partecipa anche all'adduzione e retroversione del braccio).

**Innervazione:** nervo radiale (C6–C8).

// ────────────────────────────────────────────────────────────────────
= Muscoli del Braccio — Tabella Riassuntiva

La tabella seguente riassume i muscoli principali del braccio con
le loro caratteristiche anatomiche. La tabella è impostata per non
spezzarsi tra pagine.

// ── TABELLA NON-BREAKABLE ────────────────────────────────────────────
#block(breakable: false)[
  #figure(
    table(
      columns: (1.8fr, 1.5fr, 1.5fr, 1.5fr, 1fr),
      inset: 7pt,
      align: (left, left, left, left, center),
      stroke: 0.6pt + luma(100),

      // Shading alternato righe con fill function
      fill: (x, y) =>
        if y == 0 { rgb("#003366") }
        else if calc.odd(y) { luma(245) }
        else { white },

      table.header(
        text(fill: white, weight: "bold")[Muscolo],
        text(fill: white, weight: "bold")[Origine],
        text(fill: white, weight: "bold")[Inserzione],
        text(fill: white, weight: "bold")[Azione],
        text(fill: white, weight: "bold")[Nervo],
      ),

      // Riga con colspan (loggia anteriore)
      table.cell(colspan: 5, fill: rgb("#e8f0fe"))[
        #text(weight: "bold")[Loggia Anteriore]
      ],

      [Bicipite brachiale],
      [Scapola (2 capi)],
      [Tuberosità radio],
      [Flessione + supinazione avambraccio],
      [Muscolocutaneo C5–C6],

      [Brachiale],
      [Omero (½ inf. ant.)],
      [Processo coronoideo ulna],
      [Flessione avambraccio],
      [Muscolocutaneo C5–C6],

      [Coracobrachiale],
      [Processo coracoideo],
      [Omero (½ mediale),],
      [Flessione + adduzione braccio],
      [Muscolocutaneo C7],

      // Riga divisore loggia posteriore
      table.cell(colspan: 5, fill: rgb("#fff0e8"))[
        #text(weight: "bold")[Loggia Posteriore]
      ],

      [Tricipite brachiale],
      [Scapola + omero (3 capi)],
      [Olecrano ulna],
      [Estensione avambraccio],
      [Radiale C6–C8],

      [Anconeo],
      [Epicondilo laterale],
      [Olecrano (faccia lat.)],
      [Estensione + stabilizzazione],
      [Radiale C7–C8],
    ),
    caption: [Muscoli del braccio: origine, inserzione, azione e innervazione],
  )
]

// ────────────────────────────────────────────────────────────────────
= Vascolarizzazione e Innervazione

== Arterie

Il braccio è vascolarizzato principalmente dall'*arteria brachiale*,
continuazione dell'arteria ascellare dal bordo inferiore del grande
rotondo. Essa decorre medialmente al bicipite, accompagnata dal
nervo mediano.

== Innervazione — Nervi principali

I nervi del braccio originano dal *plesso brachiale* (C5–T1).

// ── APPENDICE IMMAGINI CENTRATE ──────────────────────────────────────
=== Appendice iconografica

Le seguenti immagini mostrano i principali reperti anatomici
discussi in questo capitolo.

#align(center)[
  #grid(
    columns: (1fr, 1fr),
    gutter: 1.5em,
    figure(
      image("plesso_brachiale.jpg", width: 100%),
      caption: [Schema del plesso brachiale],
    ),
    figure(
      image("arteria_brachiale.jpg", width: 100%),
      caption: [Arteria brachiale e rami collaterali],
    ),
  )
]

// Flush: forza il piazzamento delle figure flottanti eventualmente pendenti
#place.flush()
```

---

## Note critiche sull'integrazione Python

Per generare il `.typ` da Python in modo sicuro:

```python
def generate_sbobina_typ(
    titolo: str,
    sezioni: list[dict],
    img_base_path: str,
    output_path: str
):
    """
    sezioni: lista di dict con chiavi 'titolo', 'testo', 'immagini', 'tabelle'
    """
    lines = []
    
    # Preambolo
    lines.append('#import "template.typ": quick-recap, float-right')
    lines.append('#set page(paper: "a4", margin: 2.5cm, numbering: "1")')
    lines.append('#set text(font: "Linux Libertine", size: 11pt, lang: "it")')
    lines.append('')
    
    for sezione in sezioni:
        # H1 — escape del titolo
        titolo_escaped = escape_typst(sezione['titolo'])
        lines.append(f'= {titolo_escaped}')
        lines.append('')
        lines.append(escape_typst(sezione['testo']))
        lines.append('')
        
        # Immagini
        for img in sezione.get('immagini', []):
            img_path = f"{img_base_path}/{img['filename']}"
            caption = escape_typst(img.get('caption', ''))
            placement = img.get('placement', 'center')
            
            if placement == 'float-right':
                lines.append(f'#float-right("{img_path}", img-width: 35%, caption-text: [{caption}])[')
                lines.append(escape_typst(img.get('body_text', '')))
                lines.append(']')
            else:
                lines.append(f'#figure(')
                lines.append(f'  image("{img_path}", width: 70%),')
                lines.append(f'  caption: [{caption}],')
                lines.append(f')')
            lines.append('')
    
    content = '\n'.join(lines)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)


def escape_typst(text: str) -> str:
    text = text.replace("\\", "\\\\")
    for ch in ['#', '*', '_', '[', ']', '@']:
        text = text.replace(ch, f'\\{ch}')
    return text
```

---

## Riepilogo limitazioni importanti

1. **Text wrap (float left/right):** **Non esiste in Typst.** Workaround obbligatorio con `grid`. Non è fluido come CSS.
2. **Orphans/widows:** Nessun parametro diretto. Solo `block(sticky: true/false)` e `block(breakable: false)` come approssimazione.
3. **Place con clearance su figure:** Il parametro `clearance` si imposta con `#show figure: set place(clearance: 1em)`, non direttamente su `figure`.
4. **Figure placement `left`/`right`:** Non esiste — solo `top`, `bottom`, `auto`, `none`.
5. **Libreria Python ufficiale:** Non esiste. Usare `subprocess`.
6. **`sys.inputs`:** Disponibile solo da Typst 0.11+. Verificare la versione installata con `typst --version`.