// ═══════════════════════════════════════════════════════════════════
// TEMPLATE SBOBINA MEDICA
// Import: #import "sbobina.typ": quick-recap, float-right, float-left
// ═══════════════════════════════════════════════════════════════════

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

// Float-right: image on the right, text on the left (grid workaround)
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

// Float-left: image on the left, text on the right
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
