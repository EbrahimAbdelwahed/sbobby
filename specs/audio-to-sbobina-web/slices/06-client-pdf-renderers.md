# S06 — Client-side complete and study PDF renderers

## Contract unlocked

Generate two complete, readable, downloadable PDFs from the canonical typed
documents without sending document content to a PDF server or persisting PDF
blobs in the application.

## Scope

- Add one document layout model shared by preview and both PDF variants.
- Add a client-only `ClientPdfRenderer` using `@react-pdf/renderer`, loaded only
  when needed.
- Bundle approved local fonts and prohibit remote assets.
- Render full and study templates from complete typed documents.
- Render both PDFs automatically in memory after `ready`, expose progress,
  cancel/failure/retry, and require a user gesture for each download with a safe
  deterministic filename.
- Add a PDF workbench with long headings, paragraphs, lists, callouts, tables if
  supported by the contract, page breaks, and Italian characters.

Out of scope: Typst, Python, server-side rendering, persisted PDF blobs, images,
OCR, arbitrary Markdown/HTML, remote fonts, and visual parity with the historical
template.

## API seam and ownership

```ts
interface ClientPdfRenderer {
  render(layout: DocumentLayoutTree,
         signal: AbortSignal): Promise<RenderedPdf>;
}

type RenderedPdf = {
  bytes: Uint8Array;
  sha256: string;
  pageCount: number;
  templateVersion: string;
};
```

`DocumentLayout` is the sole owner of typography, spacing, section numbering,
headers/footers, page-break policy, and block rendering and returns the layout
tree. `ClientPdfRenderer` only serializes that tree. The full and study templates
may vary density but cannot define separate document semantics.
PDF bytes remain in memory until download and are then released; IndexedDB
stores only structured text and an optional render receipt, never the bytes.

Provider output is rendered only through typed blocks. No raw HTML, script,
remote URL, CSS, or unsafe filename reaches the renderer.

## First-principles visual target

- A4 academic document optimized for sustained reading and printing.
- Clear title/section hierarchy, conservative density, adequate margins, stable
  line length, page numbers, and no orphaned heading at a page bottom.
- Full PDF prioritizes fidelity and detail; study PDF prioritizes scanning and
  compact hierarchy without hiding that it is a transformed document.
- Every supported block remains legible in monochrome print and at 200% zoom.

## Playable artifact

`/dev/workbench/pdf` renders the same long fixture as browser preview, full PDF,
and study PDF. Users can download both, inspect page count and hash, cancel a
render, and trigger explicit invalid/oversized/failure fixtures without a live
provider.

## Acceptance gates

- Both files begin with `%PDF`, open in two independent readers, and contain at
  least one page.
- Extracted text contains title plus first and last canonical section text in
  correct order; no section is omitted, duplicated, or truncated.
- The PDF is generated only from a document whose structural completion receipt
  matches its hash/version.
- Page renders show no clipped text, overlapping blocks, missing glyphs, blank
  trailing pages, isolated headings, or unreadable tables/callouts.
- A malicious/invalid block, URL, HTML string, and path-like title are rejected
  or rendered as inert text; filenames cannot traverse paths.
- Parsed output contains no `/JavaScript`, `/OpenAction`, `/Launch`,
  `/EmbeddedFile`, or remote `/URI` action. Filenames reject bidi/control
  characters, traversal, and reserved device names.
- Rendering does not call an application API, remote asset, analytics endpoint,
  or persistent storage.
- Large fixtures respect a declared memory/time budget and cancellation.
- A download is outside the app's 30-day retention; UI copy says so.

## Verification

```bash
pnpm test:unit -- document-layout pdf-renderer filenames
pnpm test:contract -- pdf-ready-document
pnpm test:security -- pdf-untrusted-content
pnpm test:e2e -- pdf-workbench pdf-download
pnpm typecheck
pnpm build
```

Automate PDF text extraction, page count, first/last section assertions, and
render selected pages to PNG at fixed DPI. Include long Italian text, diacritics,
lists, callouts, a multi-page section, and malicious strings.

This slice produces visual shots and must run unprimed `screenshot-critique` as
the last acceptance check on the full PDF pages, study PDF pages, and browser
preview, using tight crops for hierarchy, page breaks, dense sections, glyphs,
and footers. Once the first accepted PDF shot exists, run `compare-screenshots`
for later candidates against the stated first-principles target and report which
is less wrong. Open the reference/candidate set with `preview-shots`; allow about
five minutes, then record the decision and close Preview if the user is silent.

## What must stay green

- S01 typed/inert document blocks, S02 no-PDF storage audit, S04 completeness,
  and S05 ready-state semantics.
- No historical Typst or server rendering path added as compatibility layer.

## Human feedback that changes this slice

Feedback may change typography, density, spacing, page breaks, headers/footers,
and the distinction between full/study layouts. It cannot change canonical
content, silently omit blocks, or add remote assets.

## Stop or reslice

Stop if the selected renderer cannot preserve every canonical block, produces
unbounded memory use, or needs server persistence. If one block type is the
problem, split that renderer variable into a focused sub-slice; do not weaken the
whole-document completeness gate.

## Definition of Done

Both PDFs are client-generated, structurally complete, text-extractable,
visually reviewed, downloadable, and absent from durable app storage.
