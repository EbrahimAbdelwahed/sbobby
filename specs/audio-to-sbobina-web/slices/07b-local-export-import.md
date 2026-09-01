# S07b — Local export, import, and downloads

## Contract unlocked

Make project movement and backup explicit without cloud content storage. A
student can download both PDFs, export a plaintext structured project, and
import it in another invited browser without trusting archive claims.

## Scope

- Integrate S06 full/study PDF render status, retry, and user-gesture downloads.
- Add versioned `.sbobina.json` export/import with strict pre-parse and schema
  limits, known migrations, archive hash, and a new local identity.
- Add export disclosure, import review, corrupt/hostile archive, migration,
  oversized input, download failure, and completed-transfer workbenches.

Out of scope: cloud backup, share links, automatic course publishing, server
project routes, signed authenticity claims, collaboration, audio export, PDF
blob persistence, and automatic provider calls after import.

## API seam and ownership

```ts
interface ProjectArchiveService {
  export(ownerId: string, projectId: string): Promise<ExportArchive>;
  import(ownerId: string, bytes: Uint8Array): Promise<ProjectRecord>;
}
```

The archive contains canonical structured text, schema/prompt/model versions,
and source descriptor fields needed for display. It never contains audio,
credentials, raw prompts/provider requests, PDF bytes, original filename,
source fingerprint, or `lastModified` unless a later reviewed contract proves a
need. Exported files are plaintext and outside the app's 30-day retention.

Import applies a byte cap before decoding/parsing, then depth, node, string,
list, key, and total-text bounds. Duplicate keys and `__proto__`, `prototype`,
or `constructor` keys fail closed. The active owner is injected; archived owner,
project ID, stage status, readiness, hashes, and provider receipts are never
trusted. The service recomputes canonical hashes and structural completeness,
assigns a new project ID/expiry, and writes a fresh
`{ origin: "imported", trust: "unverified" }` receipt. Historical provenance may
be retained only as bounded untrusted display metadata.

## Playable artifact

An invited student downloads both PDFs, exports a ready project, reviews the
plaintext/outside-retention warning, deletes the local project, imports the
archive, and opens the newly identified unverified import. A second invited
browser can receive the file through any user-chosen channel and import it; the
project never appears automatically.

## Acceptance gates

- PDF download uses only the already rendered in-memory bytes and an explicit
  user gesture; failure does not change canonical ready state.
- Export/import round trip preserves all permitted transcript/full/study text
  and required versions; inspection finds no audio, secret, raw prompt, PDF,
  original filename, or source fingerprint.
- Import never accepts owner, ID, ready state, receipt, hash, or provider claim
  as authoritative; every trusted field is rebound or recomputed.
- Corrupt, truncated, oversized, deeply nested, duplicate-key, unknown-future,
  prototype-polluting, path-like, bidi/control-name, and hostile archives fail
  closed with redacted errors before durable writes.
- Known migration plus import commits atomically; a failure leaves no partial
  project and cannot overwrite an existing record.
- Import never triggers Groq, DeepSeek, PDF generation, or another network call.
- UI distinguishes local deletion from exported/downloaded files, browser/OS
  backups, other devices, and third-party processing.

## Verification

```bash
pnpm test:unit -- archive-service download-controller
pnpm test:contract -- export-import
pnpm test:security -- archive-input download-filenames
pnpm test:e2e -- export-import pdf-downloads
pnpm typecheck
pnpm build
```

Include round trips, every parse bound, duplicate/dangerous keys, forged
receipts/owners/hashes, known and unknown versions, atomic failure, plaintext
inspection, provider-network silence, and owner changes.

This slice produces visual shots. Run unprimed `screenshot-critique` last on
download readiness/failure, export disclosure, import review, unverified-import,
migration, and corrupt/oversized archive states. Use `compare-screenshots`
against accepted S06/S07a surfaces. Open the smallest useful set with
`preview-shots`, wait about five minutes, then record/close/proceed if silent.

## What must stay green

- S02 repository/retention, S06 renderer integrity, and S07a reading/search.
- Zero project/export/import route and zero project content on the server.
- No archive authenticity claim, hidden sync, audio field, or PDF persistence.

## Human feedback that changes this slice

Feedback may change warning copy, import review density, download placement, or
the optional untrusted provenance shown. It cannot make sharing automatic or
turn unsigned archives into trusted provider evidence.

## Stop or reslice

Stop if archive parsing/migration cannot be bounded before durable writes or if
PDF download requires persistence/server rendering. Split the failing variable;
do not weaken import trust or local-only ownership.

## Definition of Done

Both PDFs download from memory, and export/import is the only explicit
cross-browser project path. Imported content is structurally revalidated,
clearly unverified, locally rebound, and never treated as authenticated
provenance.
