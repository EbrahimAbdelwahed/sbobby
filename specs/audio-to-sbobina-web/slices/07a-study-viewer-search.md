# S07a — Study experience and literal search

## Contract unlocked

Turn completed artifacts into a useful long-study-session experience: students
can read transcript/full/study views, find literal phrases locally, navigate to
the exact block, and sustain long browser reading sessions without a server
search or second source of truth.

## Scope

- Build the project detail experience with `Sbobina`, `Studio`, and
  `Trascrizione` tabs plus compact provenance/diagnostics.
- Add one derived `LiteralSearchIndex` for all three local text surfaces.
- Add search results, snippets, block navigation, no-results, and index rebuild.
- Add long-form, literal-search, stale-index, no-results, and empty workbenches.

Out of scope: embeddings, fuzzy/semantic search, server search, automatic course
publishing, share links, collaboration, export/import, download integration,
audio/timestamp playback, editing, flashcards, quiz, or study scheduling.

## API seam and ownership

```ts
interface LiteralSearchIndex {
  build(project: SearchableProject): Promise<SearchProjection>;
  query(projection: SearchProjection, query: string): SearchResult[];
}

type SearchResult = {
  surface: "transcript" | "full" | "study";
  sectionId?: string;
  blockId: string;
  heading: string;
  snippet: string;
  matchRanges: Array<{ start: number; end: number }>;
  startMs?: number;
};
```

Matching is Unicode-normalized, case-insensitive literal substring search with
documented accent folding. It does not stem, embed, paraphrase, rerank through a
provider, or search other projects. Ranking is deterministic: exact heading
matches, heading substring, then body occurrences in document order.

The index is derived and disposable; canonical text remains in the repository.

## Playable artifact

An invited student opens a ready project, reads each surface, searches casing
and accent variants, jumps to highlighted blocks, and returns to the prior
reading position without network search traffic.

## Acceptance gates

- Search never sends a request; network inspection stays silent while typing.
- Results are deterministic, escaped, bounded, keyboard navigable, and scroll/
  focus the correct block without changing document text.
- Empty, whitespace, very long, regex-like, HTML-like, and no-result queries are
  safe and responsive.
- Projection rebuild follows canonical hash/version changes and never becomes a
  second source of truth.
- The interface repeatedly states “stored only in this browser”; it does not
  imply that another browser, device, or user can see the project.
- Long-form text remains readable and usable at 200% zoom and on narrow desktop
  windows without a mobile-support promise.

## Verification

```bash
pnpm test:unit -- literal-search
pnpm test:security -- search-rendering
pnpm test:e2e -- study-view search
pnpm typecheck
pnpm build
```

Include casing, accents, substring boundaries, HTML/regex-like inputs, large
documents, stale projections, and owner changes.

This slice produces visual shots. Run unprimed `screenshot-critique` last on the
three reading tabs, long-form density, search results/no-results/highlights,
and stored-only-here copy. Use `compare-screenshots` against approved
shell/document shots and judge reading
hierarchy, scanability, focus, and density. Open the curated set with
`preview-shots`, wait about five minutes, then record/close/proceed if silent.

## What must stay green

- S02 repository/retention and S04/S06 typed complete artifacts.
- Zero project CRUD/search route on the server.
- No search package, embeddings, provider call, or hidden sync.

## Human feedback that changes this slice

Feedback may change typography, tab layout, result density/ranking weights, or
highlight style. It cannot make sharing automatic or introduce semantic search
without a new spec.

## Stop or reslice

Stop if search needs a second canonical representation. Split performance work
from search semantics rather than adding an opaque library.

## Definition of Done

The local project is genuinely useful for reading and exact phrase retrieval,
and the search projection remains local, disposable, and derived from canonical
text.
