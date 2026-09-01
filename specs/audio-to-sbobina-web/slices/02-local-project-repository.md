# S02 — Browser-local project repository and 30-day retention

## Contract unlocked

Make the browser the single durable owner of project text and run state. Projects
survive refresh on the same origin/account, expire predictably after 30 days,
handle quota/eviction honestly, and never persist audio or PDF blobs.

## Scope

- Implement one typed IndexedDB adapter through `idb`.
- Add schema versioning and explicit forward migrations.
- Store projects, transcript chunks, text artifacts, stage receipts, and settings.
- Namespace reads and writes by the authenticated `ownerId`.
- Implement atomic artifact-plus-receipt commits and downstream invalidation.
- Implement persistence request, quota estimates, expiry, manual delete, and
  delete-all.
- Render the local library and truthful storage/expiry warnings from fixtures and
  real local records.

Out of scope: audio storage, PDF Blob storage, provider calls, background sync,
service workers, automatic sharing, encryption claims, and final export UI.

## API seam and ownership

```ts
interface LocalProjectRepository {
  list(ownerId: string): Promise<ProjectSummary[]>;
  get(ownerId: string, projectId: string): Promise<ProjectRecord | null>;
  create(ownerId: string, source: AudioSourceDescriptor): Promise<ProjectRecord>;
  commitStage(input: CommitStageInput): Promise<ProjectRecord>;
  interruptRunning(ownerId: string): Promise<void>;
  delete(ownerId: string, projectId: string): Promise<void>;
  deleteAllForOwner(ownerId: string): Promise<void>;
  purgeExpired(now: string): Promise<PurgeReceipt>;
}
```

`commitStage` is the only write path for pipeline artifacts. One transaction
validates `inputHash`, writes the typed text output, records the receipt, updates
`updatedAt`, sets `expiresAt = updatedAt + 30 days`, and invalidates downstream
outputs when the upstream hash changes.

IndexedDB stores:

```text
projects
transcript_chunks
stage_artifacts
stage_receipts
settings
```

It must reject `File`, audio `Blob`, `ArrayBuffer` tagged as audio, PCM, encoded
chunks, object URLs, secrets, provider bodies, raw prompts, and PDF blobs.

## Playable artifact

An invited student creates fixture projects, refreshes, filters by owner,
inspects expiry/storage status, deletes one or all, simulates 29/30/31 days, and
sees clear handling when persistent storage is denied or quota is exhausted.

## Acceptance gates

- Project and successful stage commit are atomic; a killed transaction exposes
  neither a receipt without output nor output without receipt.
- A changed transcript atomically invalidates all persisted downstream
  artifacts and receipts. Disposable search/PDF projections rebuild in memory
  when their canonical input hash changes.
- Startup converts the active owner's persisted `running` stages to
  `interrupted` and purges expired records across every local owner namespace.
  Expiry cannot run while the origin is never opened, which the UI states.
- Expiry is 30 days after the last successful write; viewing does not extend it.
- Logout/cross-account reads do not return another `ownerId` namespace. “Delete
  all” is labeled “delete all my project data in this browser”; it does not
  imply origin-wide or remote erasure.
- The UI states that a shared browser profile is not cryptographic isolation.
- `navigator.storage.persist()` and `storage.estimate()` results are shown
  truthfully; `QuotaExceededError` preserves prior committed data.
- A database/cache inspection finds no prohibited audio/PDF material.
- Schema downgrade or unknown future version fails closed and offers export or
  deletion, never destructive silent migration.

## Verification

```bash
pnpm test:unit -- repository retention invalidation
pnpm test:contract -- project migrations
pnpm test:security -- local-storage
pnpm test:e2e -- local-library retention quota
pnpm typecheck
pnpm build
```

Use a fake clock for 29/30/31-day cases and fault injection around each
transaction boundary. Inspect IndexedDB and Cache API from Playwright after a
fixture run.

This slice produces visual shots. Run unprimed `screenshot-critique` last on the
library, persistence denied, quota full, expiring, expired, and destructive
confirmation states. Use `compare-screenshots` against the S01 shell baseline.
Open the minimal set with `preview-shots`, wait about five minutes, and record a
decision and close Preview if the user does not respond.

## What must stay green

- S00 no-audio evidence and S01 import/auth/contract tests.
- No server route for project CRUD.
- No service worker or cache layer introduced by the app shell.

## Human feedback that changes this slice

Feedback may change library density, warning placement, expiry copy, or delete
confirmation. It cannot turn local storage into a backup promise or move content
to the server.

## Stop or reslice

Stop if a browser cannot meet the required atomic/quota behavior or if the app
needs audio persistence to resume. A failure may narrow supported browsers, but
only after updating S00 and the README.

## Definition of Done

IndexedDB is the only project owner, retention and invalidation are deterministic,
the library survives refresh and fails honestly, and audits prove no audio or PDF
blob is durable.
