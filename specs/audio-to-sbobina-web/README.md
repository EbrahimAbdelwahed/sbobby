# Audio-to-Sbobina Web — implementation specification

Status: Implementing — fast server-worker iteration
Last updated: 2026-09-03
Target application: `sbobby-web/`
Vercel project: `audio-to-sbobina` (separate from the existing `sbobby-web`)

## Next Agent Prompt

You are implementing the Audio-to-Sbobina private beta using the fast path
accepted in ADR-0002. Vercel owns the UI, shared-code beta access, temporary
Blob upload tokens, and Runpod job control. A Runpod Flash Python/FFmpeg worker
owns transcription and text processing. Optimize for an end-to-end published
iteration before optional hardening.

Deploy only to the separate `audio-to-sbobina` Vercel project. The existing
`sbobby-web` project and `sbobby-web.vercel.app` production alias are explicitly
outside this implementation and must remain unchanged.

Current status: the browser-only S00 architecture is superseded. The web shell,
temporary Blob bridge, Runpod control routes, local 30-day result library,
literal search, and client PDF path are being integrated with the Python worker.

Exact next pickup point: finish the Runpod worker smoke, configure
`RUNPOD_API_KEY`, `RUNPOD_ENDPOINT_ID`, `BLOB_READ_WRITE_TOKEN`, and the two
closed-beta access variables, then deploy a Vercel preview and run one short
audio journey.

Active blockers and warnings:

- Audio is temporarily stored in Vercel Blob and the Runpod worker filesystem;
  both copies are deleted after completion/failure where the platform permits.
- `deepseek-v4-flash` is the only text model. There is no model fallback and no
  semantic quality benchmark. Do not claim that medical accuracy is proven.
- Browser-local storage is not cloud backup. Cross-device sync and automatic
  course sharing are outside this beta.
- Claude/Fable drafting was unavailable because the local CLI was not
  authenticated; the spec was synthesized from three independent Codex drafts.

Fast-iteration TODO (supersedes the original slice ordering below):

- [x] Separate the new Vercel project from the existing Sbobby production app.
- [x] Build the private upload/progress/reader/search/PDF web journey.
- [x] Build, smoke, and deploy the Python/FFmpeg Runpod worker.
- [ ] Configure Runpod, Blob, and beta access credentials.
- [x] Deploy the separate Vercel app.
- [ ] Complete one real audio journey.

Original detailed backlog retained for later hardening:

- [ ] [S00 — prove no-storage audio ingress](slices/00-audio-ingress-feasibility.md)
- [ ] [S01 — establish app, contracts, and invite-only auth](slices/01-foundation-contracts-auth.md)
- [ ] [S02 — implement the 30-day local project repository](slices/02-local-project-repository.md)
- [ ] [S03 — ship Groq transcription and deterministic assembly](slices/03-groq-transcription.md)
- [ ] [S04 — ship the DeepSeek-only text services](slices/04-deepseek-text-pipeline.md)
- [ ] [S05 — integrate the resumable browser pipeline](slices/05-browser-pipeline-orchestrator.md)
- [ ] [S06 — generate complete and study PDFs in the browser](slices/06-client-pdf-renderers.md)
- [ ] [S07a — ship the study viewer and literal search](slices/07a-study-viewer-search.md)
- [ ] [S07b — ship local export, import, and downloads](slices/07b-local-export-import.md)
- [ ] [S08 — harden privacy, security, observability, and release](slices/08-security-release.md)

Before ending every implementation pass, update this section with the last
completed slice, exact verification, open findings, and the next pickup point.

## 1. Outcome

Build a new, invite-only web application for a closed group of medical students.
From one M4A or MP3 lesson, the app automatically produces:

1. a timestamped transcript through Groq;
2. a generic section plan;
3. a complete reworked sbobina;
4. a compact study document;
5. a downloadable complete PDF;
6. a downloadable study PDF;
7. literal local search across transcript, full document, and study document.

The default journey is one guided run from audio selection to both documents.
The completed project also exposes every intermediate artifact and allows a
student to rerun a failed or chosen downstream phase without stopping the
normal automatic pipeline for editorial approval.

## 2. Decisions that matter most now

### D1 — local-only content wins over automatic sharing

The browser is the sole durable owner of project text and pipeline state. The
server owns authentication and provider access, not lessons. Another browser or
device has no access to a project. Sharing in the beta means an explicit local
export/import file; share links and automatic course libraries require a future
cloud-storage decision.

### D2 — no-storage audio ingress is a release gate

A normal lecture cannot pass through one Vercel Function body because the
platform limit is 4.5 MB. The browser must create independently decodable,
overlapping audio chunks and send each as a measured raw body of at most 3.5 MB
with bounded metadata headers; server-side code builds Groq multipart. If
this cannot be demonstrated on realistic M4A and MP3 fixtures, implementation
stops. It must not silently add Vercel Blob, S3, or another worker.

### D3 — the browser, not Vercel Workflow, owns orchestration

Durable server workflows would persist arguments, results, or content state and
would contradict local-only ownership. A client state machine checkpoints text
after every phase in IndexedDB. Vercel route handlers remain stateless and
short-lived. Closing the tab pauses the run; completed text phases survive.

### D4 — DeepSeek-only is explicit accepted risk

All natural-language segmentation, elaboration, and study compaction use the
pinned DeepSeek V4 Flash model. Full and study sections are assembled locally
and deterministically; there is no separate model merge call. There is no Luna
or other model fallback and no
WER, hallucination score, model comparison, or human grading gate. Runtime
schema and coverage validation remain mandatory because they test software
integrity, not medical correctness. “Maximum quality” is an objective supported
by the selected models and loss-minimizing pipeline, not a verified guarantee.

### D5 — the legacy pipeline is reference evidence, not a deployable backend

The historical Python pipeline depends on local FFmpeg, filesystem state,
destructive workspace replacement, and Typst. The new app ports its domain
behavior into browser- and Vercel-native modules. It does not wrap or fork the
old runtime and does not extend `biochimica-sites`.

### D6 — a metadata-only control store is the sole server-state exception

Vercel WAF enforces coarse IP/route limits. Upstash Redis enforces per-user/day
provider quotas and short concurrency leases using only keyed-HMAC user IDs,
route/stage, counters, and TTLs of at most 35 days. A dedicated AI Gateway key
has a workload budget with auto top-up off. Function memory is never treated as
a global counter. No audio, transcript, prompt, model output, title, filename,
or project state may enter this operational store.

Initial beta caps are one 180-minute source per user/day, two concurrent
provider calls per user, 1,000,000 DeepSeek input and 300,000 output tokens per
user/day, and a USD 25 monthly dedicated Gateway-key budget with auto top-up
off. Groq uses a USD 25 account ceiling when supported, otherwise a USD 20
alert plus the mandatory provider-call kill switch. These are reviewed
configuration, not values hidden in route handlers.

## 3. Agreed product contract

| Area | Beta contract |
|---|---|
| Audience | Closed invited group of students; `student` and `admin` roles |
| Surface | Desktop web app only, deployed on Vercel |
| Input | User-selected `.m4a` and `.mp3` only |
| Audio | Ephemeral; never persisted by the application |
| Transcription | Groq `whisper-large-v3`, Italian, verbose timestamps |
| Text model | Only `deepseek/deepseek-v4-flash-0731` through Vercel AI Gateway |
| Prompts | Generic, versioned, no subject-specific configuration |
| Flow | Automatic through both documents and PDFs; no editorial pause |
| Outputs | Transcript, full sbobina, study document, full PDF, study PDF |
| Search | Local, case-insensitive literal substring search; no embeddings |
| Persistence | Text, structured documents, receipts, and run state in IndexedDB |
| Retention | Expires 30 days after the last successful project write |
| Sharing | Explicit `.sbobina.json` export/import and normal file transfer |
| Backup | None; browser data may be evicted or manually cleared |
| Quality testing | Structural checks only; no semantic/model-quality benchmark |

Before file selection, the application names the processors and boundaries:
Clerk receives identity/member data; Vercel handles requests and operational
metadata; Groq receives transient audio chunks; AI Gateway and DeepSeek receive
transient lesson text. Their current retention/deletion terms and configured
logging/cache settings are linked and recorded at release. “No audio storage”
means no application-controlled durable content persistence; deletion cannot
erase provider processing, downloaded/exported files, browser/OS backups, or
copies on another device.

## 4. Scope firewalls

### In scope

- New Next.js App Router application in `sbobby-web/`.
- Invite-only managed authentication and an admin member view.
- Browser Web Worker audio preparation and request budgeting.
- Content-stateless authenticated Vercel route handlers.
- Groq transcription, timestamp normalization, and overlap de-duplication.
- DeepSeek segmentation, per-section elaboration and compact study generation,
  followed by deterministic document assembly.
- Browser-local state machine, retry, interruption, and source reselection.
- Two client-generated PDFs, document viewers, literal search, export/import.
- Privacy-safe logs, rate/budget controls, accessibility, E2E, and Vercel deploy.

### Out of scope

- Persistent audio, Vercel Blob, S3, server document database, or durable Jobs.
- Cross-device synchronization, automatic sharing, collaboration, or comments.
- Audio playback, waveform UI, live recording, URLs, cloud imports, video, WAV,
  or formats other than M4A/MP3.
- Semantic search, embeddings, tutor/chat, flashcards, quiz, Anki, or spaced
  repetition.
- Subject prompts, glossaries, images, OCR, slide extraction, or chemical
  rendering.
- Human review checkpoints, text editing, medical fact verification, model
  fallback, A/B evaluation, billing, native apps, or mobile support.
- Reimplementation inside `biochimica-sites` or direct deployment of the Python
  pipeline.

## 5. Architecture

Open the [architecture and slice map](visualizations/architecture.html) for the
human-reviewable roadmap.

```text
Browser data plane
  File handle in memory
    → AudioPreparer worker
    → TranscriptionClient
    → TranscriptAssembler
    → LocalProjectRepository
    → BrowserPipelineOrchestrator
    → LiteralSearchIndex / DocumentLayout / ClientPdfRenderer / ExportArchive

Vercel control plane (stateless content handling)
  Clerk auth + authorization
  Route validation + redaction + rate limits
  GroqTranscriptionAdapter
  DeepSeekTextAdapter + PromptCatalog

Provider plane
  Groq: transient independent audio chunks
  Vercel AI Gateway → DeepSeek: transient text operations, no fallback
```

### Single-owner invariants

| Concept | Sole owner | Consumers |
|---|---|---|
| Shared schemas | `src/contracts/**` | Client and server boundaries |
| Project truth | `LocalProjectRepository` | Pipeline, library, viewer, export |
| Run transitions | `BrowserPipelineOrchestrator` | Progress and recovery UI |
| Audio bytes | `AudioPreparer` worker for the active session | Transcription client only |
| Chunk sizing | `AudioChunkBudget` | Worker and request validator |
| Transcript ordering | `TranscriptAssembler` | Documents and search |
| Generic prompts | server-only `PromptCatalog` | DeepSeek adapter |
| Provider calls | server-only adapters | Thin route handlers |
| Quota/cost admission | `RateLimitPolicy` | Every paid route |
| Full/study schema | `LessonDocument` contracts | Viewer, search, PDF, export |
| PDF layout | `DocumentLayout` | `ClientPdfRenderer` and preview |
| Literal matching | `LiteralSearchIndex` | Search panel |
| Expiry | `RetentionPolicy` | Repository startup and writes |
| Public errors | `PipelineError` contract | Routes, orchestrator, UI |

No slice may introduce a second project repository, orchestration state
machine, prompt registry, document model, provider client, or search index.
Transitional spike code is not production code; Slice 00 must either promote a
single adapter behind the named interface or delete the spike.

### Import firewall

- `src/server/**` may import `src/contracts/**`, never `src/client/**` or UI.
- `src/client/**` may import `src/contracts/**`, never `src/server/**`.
- React components use application controllers/hooks; they do not call Groq,
  DeepSeek, IndexedDB, or PDF internals directly.
- Route handlers authenticate, parse, call one application service, normalize,
  and return. They do not own prompts or provider-specific logic.
- ESLint `no-restricted-imports` and an architecture test enforce these rules.

## 6. Target application shape

```text
sbobby-web/
  AGENTS.md                         # scoped DeepSeek-only policy
  app/
    (public)/sign-in/[[...sign-in]]/page.tsx
    (protected)/app/page.tsx
    (protected)/app/projects/new/page.tsx
    (protected)/app/projects/[projectId]/page.tsx
    (protected)/app/admin/members/page.tsx
    api/v1/session/route.ts
    api/v1/transcriptions/chunks/route.ts
    api/v1/text/segment/route.ts
    api/v1/text/elaborate/route.ts
    api/v1/text/compact/route.ts
    dev/workbench/*/page.tsx
  src/
    contracts/{project,pipeline,transcript,documents,api,export}.ts
    client/
      audio/{preparer,prepare.worker,chunk-budget,fingerprint}.ts
      persistence/{project-repository,retention,migrations}.ts
      pipeline/{orchestrator,reducer}.ts
      pdf/{layout,renderer}.ts
      search/literal-index.ts
      export/archive.ts
    server/
      auth/authorize.ts
      providers/{groq-transcription,deepseek-text}.ts
      prompts/catalog.ts
      security/{request-validation,redaction,rate-limits}.ts
    components/{source-picker,pipeline,documents,search,failures}/
  tests/{unit,contract,integration,security}/
  e2e/
  public/fonts/
```

The exact route grouping may change if Next.js conventions require it, but the
ownership boundaries and public URLs must remain stable.

## 7. Canonical contracts

All cross-boundary data is plain, versioned, runtime-validated JSON. Audio bytes
are deliberately absent from durable contracts.

```ts
type ProjectRecord = {
  schemaVersion: 1;
  id: string;
  ownerId: string;
  title: string;
  createdAt: string;
  updatedAt: string;
  expiresAt: string;
  source: AudioSourceDescriptor;
  machine: PipelineMachine;
  transcript?: CanonicalTranscript;
  segmentation?: SegmentationPlan;
  fullDocument?: LessonDocument;
  studyDocument?: LessonDocument;
  receipts: StageReceipt[];
};

type AudioSourceDescriptor = {
  name: string;
  mediaType: "audio/mpeg" | "audio/mp4";
  size: number;
  lastModified: number;
  fingerprint: string; // resume aid, not an authorization boundary
  durationMs?: number;
};

type StageReceipt = {
  stage: PipelineStage;
  status: "succeeded" | "failed" | "interrupted";
  attempt: number;
  inputHash: string;
  outputHash?: string;
  promptVersion?: string;
  modelId?: string;
  completedAt?: string;
  error?: PipelineError;
};
```

The detailed schemas belong to S01–S04. Invariants include exact transcript
unit ordering, valid section references, segmentation coverage without gaps or
overlap, downstream invalidation on input-hash change, and no partial document
presented as complete.

## 8. Pipeline and recovery semantics

```text
new
  → source_selected
  → preparing_audio
  → transcribing[n]
  → assembling_transcript
  → segmenting
  → elaborating[n]
  → assembling_full
  → compacting[n]
  → assembling_study
  → ready
```

Lateral states are `waiting_for_source_reselection`,
`retryable_failure(stage, unit?)`, `terminal_failure(stage, code)`, and
`expired`.

- Persist each successful text artifact and receipt before starting the next
  phase.
- A reload converts a local `running` stage to `interrupted`.
- If transcription is incomplete, the user must reselect the same source. The
  client verifies its fingerprint and skips completed chunk receipts.
- Network, 429, and provider 5xx failures receive at most two automatic retries
  with bounded exponential backoff.
- Structurally invalid DeepSeek output receives one repair request using the
  same model. A second failure stops the stage.
- No automatic retry changes model, prompt version, or input.
- The orchestrator detects a changed upstream hash and asks
  `LocalProjectRepository` to atomically invalidate downstream artifacts.
- Closing the tab may waste an in-flight provider call; exactly-once billing is
  not promised.

The direct-to-PDF product flow means no editorial pause. Both PDFs render
automatically in memory after the project becomes `ready`; each filesystem
download still requires an explicit user gesture. Render failure leaves the
canonical documents ready and exposes a focused retry.

## 9. API surface

| Method and route | Input | Output | Owner |
|---|---|---|---|
| `GET /api/v1/session` | Auth cookie | User ID and role only | `authorize` |
| `POST /api/v1/transcriptions/chunks` | Authenticated raw independent audio body `<= 3,500,000` bytes plus bounded metadata headers | Timestamped `TranscriptChunk` `<= 1,000,000` bytes | `GroqTranscriptionAdapter` |
| `POST /api/v1/text/segment` | Canonical transcript units + hashes | `SegmentationPlan` | `TextPipelineService` |
| `POST /api/v1/text/elaborate` | One referenced lesson segment | Full `DocumentSection` | `TextPipelineService` |
| `POST /api/v1/text/compact` | One full section | Study `DocumentSection` | `TextPipelineService` |

Every route is invite-protected, uses the Node.js runtime, sets
`Cache-Control: no-store`, validates content type and schema, applies a request
budget below Vercel's hard limit, and returns a stable public error when its
handler runs. A platform-level 413 may use Vercel's error shape. No route can
list, fetch, save, share, or delete projects.

Public error codes:

```text
AUTH_REQUIRED, FORBIDDEN, UNSUPPORTED_AUDIO, SOURCE_TOO_LARGE,
SOURCE_MISMATCH, AUDIO_PREPARATION_FAILED, PAYLOAD_TOO_LARGE,
RATE_LIMITED, PROVIDER_TIMEOUT, PROVIDER_UNAVAILABLE,
INVALID_PROVIDER_OUTPUT, TEXT_CONTEXT_EXCEEDED, PDF_RENDER_FAILED,
LOCAL_STORAGE_FULL, PROJECT_EXPIRED
```

Provider bodies, raw errors, prompts, filenames, and lesson text never appear in
public errors or logs.

## 10. Provider and prompt policy

### Groq

- Model: `whisper-large-v3`.
- `language=it`, `temperature=0`, `response_format=verbose_json`.
- Request both segment and word timestamps when the API supports them.
- Use independent decodable chunks with a bounded overlap and a generic Italian
  medical-lecture context prompt.
- De-duplicate overlaps deterministically from normalized timestamped text; do
  not ask an LLM to stitch transcripts.

### DeepSeek

- AI SDK through Vercel AI Gateway.
- Pinned model: `deepseek/deepseek-v4-flash-0731`, verified in the Gateway model
  list on 2026-09-01.
- Restrict routing to DeepSeek and configure no fallback models.
- Disable content logging and request caching; tag only redacted user/stage IDs.
- Generic versioned prompts: `segmentation@1`, `elaboration@1`, and
  `compact-study@1`. A pure `DocumentAssembler` orders validated sections and
  rejects gaps or duplicates without another model call.
- Structured outputs are schema-validated. Coverage and reference validation
  protect pipeline integrity but do not assert factual or medical quality.

Implementation must add `sbobby-web/AGENTS.md` to scope this explicit
DeepSeek-only decision to the new app without changing NLP policy for unrelated
repository projects.

## 11. Local persistence, retention, and sharing

Use IndexedDB through one small repository adapter. The stores are:

```text
projects
transcript_chunks
stage_artifacts
stage_receipts
settings
```

Audio `File`, audio `Blob`, encoded chunks, PCM, object URLs, provider request
bodies, and secrets are forbidden. PDFs render automatically in memory after
`ready` and download only on user action; the local canonical form is the
structured text document, not a PDF Blob.

On first project creation, request `navigator.storage.persist()` and show its
truthful result. Before each write, inspect the quota and handle
`QuotaExceededError`. The repository deletes expired records on startup and
periodically while open. `expiresAt` is 30 days after the last successful
project write; merely viewing a document does not extend it.

The UI must always expose:

- expiry date and storage status;
- “Export project”, “Delete now”, and “Delete all my project data in this
  browser”;
- a warning that browser clearing, private browsing, storage pressure, or a new
  device can remove or hide data;
- a warning that a shared OS/browser profile is not a cryptographic tenant
  boundary.
- deletion copy that distinguishes local app records, downloads/exports,
  browser or OS backups, other devices, and third-party provider processing.

The `.sbobina.json` export is plaintext and versioned, contains permitted
structured text and bounded provenance display data, and contains no audio,
credential, raw prompt/provider body, PDF, original filename, or source
fingerprint. Import caps bytes before parsing, rejects dangerous keys and
structural limits, ignores owner/status/receipt claims, recomputes hashes and
completeness, creates a new local project/expiry, and labels provenance
`imported`/`unverified`.

## 12. User experience and routes

| Route | Purpose |
|---|---|
| `/sign-in` | Invite-only authentication |
| `/app` | Local project library, expiry/storage warnings, create/import |
| `/app/projects/new` | M4A/MP3 selection and immediate automatic run |
| `/app/projects/[projectId]` | Progress, recovery, transcript, full/study documents, search, downloads |
| `/app/admin/members` | Invite/revoke members; never inspect projects |
| `/dev/workbench/*` | Fixture-only visual states, absent from production navigation |

The primary project view has one visible progress rail and tabs for `Sbobina`,
`Studio`, and `Trascrizione`. Search is always local to the selected project.
Intermediate service receipts are available in a compact diagnostics panel;
students can retry from a failed phase or rerun a selected downstream phase
without manually orchestrating the normal journey.

Accessibility requirements: full keyboard operation, visible focus, semantic
headings/landmarks, announced progress and errors, reduced-motion support,
minimum WCAG AA contrast, no color-only status, and readable long-form text at
200% zoom.

## 13. Browser and input envelope

The beta targets the latest two desktop releases of Chrome, Edge, and Safari.
Firefox and mobile browsers remain unsupported until they pass S00.

Provisional envelope:

- target maximum: 180 minutes and 250 MiB;
- the released limit must support at least a deterministic 90-minute fixture;
- measured raw prepared-audio request body: at most 3,500,000 bytes;
- normalized transcription response: at most 1,000,000 bytes;
- overlap and internal format are fixed by S00, then frozen in the contracts;
- peak worker memory below 1 GiB on the reference machine;
- local preparation of the 90-minute fixture below 10 minutes and cancellable.

If the gate passes only with a lower limit than 90 minutes or fails M4A/MP3 on
a required browser, the feature is blocked and this spec must be resliced after
a new user decision. Storage or a non-Vercel worker is not an implicit fallback.

## 14. Security and privacy contract

- One Clerk Organization owns invitations and `org:student`/`org:admin` roles;
  public signup is disabled and client-writable metadata is never authoritative.
- `authorize` verifies the active user, session, configured organization, and
  current server-side membership on every provider/admin route, failing closed
  when Clerk cannot be checked. UI hiding is never sufficient.
- Revocation removes organization membership and revokes active sessions. It
  prevents future API use but cannot erase data already stored in that browser.
- Keys only in Vercel environment/OIDC, never in `NEXT_PUBLIC_*` or the bundle.
- Extension, MIME, magic-byte, duration, size, chunk-count, and request-budget
  validation; malformed media fails before provider use where possible.
- Audio preparation uses self-hosted version/hash-pinned worker/core/WASM assets
  with no network or persistent FS. It caps source bytes, decoded samples,
  output, chunk count, heap, time, and abort, then clears in-memory WASM files.
- No analytics or service worker may observe/cache audio or provider bodies.
- CSP explicitly covers Clerk, same-origin FFmpeg worker/WASM, Gateway/Groq
  server paths, bundled fonts, and PDF assets; no broad `'unsafe-eval'`,
  arbitrary remote script, remote PDF asset, or `dangerouslySetInnerHTML`.
- Model text is data rendered from typed blocks; links and HTML are rejected.
- Every mutation rejects missing, `null`, or cross-site `Origin`, requires exact
  Host/Origin agreement plus a custom CSRF header, exposes no permissive CORS,
  and uses SameSite Clerk cookies.
- Vercel WAF owns coarse per-IP/route limits. A metadata-only Upstash Redis
  store owns per-user daily audio-seconds, text-tokens, request counts, and
  concurrency leases using keyed-HMAC identifiers and bounded TTLs; function
  memory is not a limiter. A dedicated AI Gateway key owns the DeepSeek workload
  budget, maps exhausted spend to a public error, and has auto top-up disabled.
- Logs contain request ID, redacted user ID, stage, byte/token counts, duration,
  status, and public error code only.
- AI Gateway content logging and caching remain off.
- Security tests inspect IndexedDB, Cache API, bundles, logs, and error payloads
  for prohibited content.
- The product warns users not to upload patient-identifiable recordings and to
  confirm they are authorized to process the lecture.

## 15. Dependencies and why they exist

| Dependency | Justification |
|---|---|
| Next.js App Router + TypeScript | Vercel-native UI and stateless routes |
| `@clerk/nextjs` | Managed invite-only auth without custom password storage |
| `ai` + schema validator | Current AI Gateway and structured DeepSeek output |
| `idb` | Small typed wrapper around transactional IndexedDB and migrations |
| FFmpeg/WASM adapter, only after S00 | Valid M4A/MP3 chunk creation in a worker |
| `@react-pdf/renderer` | Client-only full/study PDF generation from typed blocks |
| `@vercel/firewall` | Platform-backed limits correct across function instances |
| `@upstash/redis` | Metadata-only global quotas and short concurrency leases |
| Vitest + Playwright | Contract/state tests and real-browser journeys |

Do not add a server content database, object store, queue, vector store, search
library, generic workflow engine, Python runtime, or Typst dependency. The
bounded metadata-only Upstash quota store is the sole server-state exception.
Pin exact versions when S01 creates `package.json`; record every promotion in
the slice log.

## 16. Slice graph and review map

```text
S00 feasibility gate
  → S01 contracts + auth + shell
      → S02 local repository
      → S03 Groq transcription
          → S04 DeepSeek text pipeline
              → S05 browser orchestration
                  → S06 PDFs
                  → S07a viewer/search
                      → S07b export/import/downloads
                          → S08 security + release
```

| Slice | Playable verdict | Human review surface |
|---|---|---|
| S00 | One realistic file becomes preview-protected chunk transcripts without storage | Ingress workbench and performance report |
| S01 | Invited user enters; non-invited user cannot; all fixture states render | Shell, sign-in, state workbench |
| S02 | Project survives refresh, expires, and deletes locally | Library and storage warnings |
| S03 | Prepared M4A/MP3 chunks assemble into one deterministic transcript | Chunk transport and assembly workbench |
| S04 | Fixture transcript becomes valid full/study structured documents | Document workbench, no quality verdict |
| S05 | One click runs and resumes the whole text pipeline | Progress rail and failure recovery |
| S06 | Both PDFs download and remain complete/readable | Rendered PDF page shots |
| S07a | Student reads and searches all local text surfaces | Long-form viewer and search states |
| S07b | Student downloads, exports, deletes, and safely imports locally | Transfer warnings and hostile archives |
| S08 | Vercel preview passes privacy, security, browser, and release journeys | Integrated production-like flow |

Every visual slice must end with an unprimed `screenshot-critique` of the exact
candidate shots. Once a prior accepted shot or reference exists, also run
`compare-screenshots` and judge which candidate is less wrong against the stated
target. Human checkpoints are non-blocking: open the smallest useful shot set
with `preview-shots`, allow about five minutes for feedback, and if the user is
silent decide from evidence, record the rationale in this spec, close Preview,
and proceed.

## 17. Global verification

The implementation must expose these package scripts:

```bash
pnpm lint
pnpm typecheck
pnpm test:unit
pnpm test:contract
pnpm test:security
pnpm test:e2e
pnpm build
```

Final release evidence includes:

- state-transition table coverage and downstream invalidation;
- M4A and MP3 no-storage ingress with every request below budget;
- malformed media, MIME spoof, memory pressure, cancellation, 401/403/413/415,
  429, provider timeout, malformed output, and local quota failure;
- deterministic transcript ordering and overlap de-duplication;
- DeepSeek schema/reference/coverage checks without semantic grading;
- refresh/reselection after every stage and no repeated completed units;
- 29/30/31-day retention with a fake clock;
- PDF header, page count, extracted first/last section text, and page renders;
- literal casing/accent/substring/no-result search and block navigation;
- export/import round trip with no audio or secret fields;
- proof that IndexedDB, Cache API, logs, error reports, and bundles contain no
  audio or provider secret;
- Vercel preview live smoke for one short audio fixture and one text fixture;
- Playwright Chromium and WebKit integrated journeys;
- accessibility scan plus keyboard and 200% zoom manual checks;
- `git diff --check` and an independent semantic/security review.

Live provider tests verify availability, response schema, and error mapping.
They do not grade transcript or medical content quality.

## 18. Known unknowns and stop conditions

Stop the affected branch and update this spec before implementation widens if:

1. M4A or MP3 cannot become independently decodable under-budget chunks in a
   required browser.
2. The 90-minute fixture breaches the memory/time envelope.
3. Any byte of audio appears in persistent browser/server storage, cache,
   analytics, tracing, logs, or error reports.
4. DeepSeek output remains structurally invalid after its one same-model repair.
5. Segmentation does not cover every canonical transcript unit exactly once.
6. A route or generated PDF breaches the bounded payload/document contract.
7. The selected source does not match the interrupted project's fingerprint.
8. Auth or provider-secret isolation cannot be verified.
9. A PDF omits content or presents a partial output as complete.
10. A requested feature requires automatic sharing, server content persistence,
    semantic search, audio playback, another model, or human review.

S00 may discover the internal prepared-audio format and overlap values. That is
the only intentionally open production variable. It owns one question and one
verdict; after the gate, update the contracts and remove all unused alternatives.

## 19. Alternatives rejected

- Whole-file Vercel upload: exceeds the Function payload limit.
- Groq directly from the browser: exposes the secret.
- Temporary Blob/S3: violates the no-persistent-audio decision.
- Vercel Workflow or a queue: creates durable server content state.
- Python/FFmpeg CLI/Typst on Vercel: wrong runtime and ownership shape.
- PDF server-side: unnecessary server content transit and payload pressure.
- Server project CRUD: contradicts browser-local ownership.
- Automatic course sharing: requires cloud document storage.
- Extending `biochimica-sites`: it is a static archive with a different product
  boundary.
- DeepSeek fallback or quality benchmark: explicitly rejected by the user.
- One giant LLM request: poor resumability, response-size risk, and no focused
  structural seam.

## 20. Definition of Done

The beta is done only when an invited student can select a supported M4A or MP3
in a supported desktop browser, keep the audio ephemeral, obtain one complete
timestamped transcript, full and study documents, download both complete PDFs,
search them literally, refresh and resume from completed text checkpoints, and
export/import the project without any server content store.

Admins can invite and revoke members but cannot inspect projects. Every provider
route is protected, bounded, redacted, and content-stateless. Local retention, quota,
expiry, deletion, and data-loss warnings are visible and tested. The release
states plainly that there is no background processing, cloud backup, automatic
sharing, audio playback, semantic search, or verified medical-quality guarantee.

## 21. Primary references

- [Vercel Functions limits](https://vercel.com/docs/functions/limitations) —
  4.5 MB request/response body limit and duration/memory envelope.
- [Vercel guidance for large uploads](https://vercel.com/kb/guide/how-to-bypass-vercel-body-size-limit-serverless-functions) —
  Functions should not act as large-media servers.
- [Groq Speech-to-Text](https://console.groq.com/docs/speech-to-text) — supported
  formats, timestamps, limits, and `whisper-large-v3` accuracy guidance.
- [DeepSeek API models](https://api-docs.deepseek.com/api/list-models/) and
  [V4 change log](https://api-docs.deepseek.com/updates/) — current V4 Flash
  availability and beta status.
- [Vercel AI Gateway](https://vercel.com/docs/ai-gateway) and
  [live model list](https://ai-gateway.vercel.sh/v1/models) — model routing,
  observability, and verified DeepSeek slug.
- [Vercel WAF rate limiting](https://vercel.com/docs/vercel-firewall/vercel-waf/rate-limiting)
  and [AI Gateway key budgets](https://vercel.com/changelog/budgets-for-api-keys-on-ai-gateway) — platform abuse and spend controls.
- [Upstash for Vercel](https://vercel.com/marketplace/upstash) — the explicitly
  bounded metadata-only global quota store.
- [MDN IndexedDB](https://developer.mozilla.org/en-US/docs/Web/API/IndexedDB_API)
  and [storage eviction](https://developer.mozilla.org/en-US/docs/Web/API/Storage_API/Storage_quotas_and_eviction_criteria) — local persistence and eviction.
- [ffmpeg.wasm overview](https://ffmpegwasm.netlify.app/docs/overview/) —
  browser worker execution and performance considerations.
- [Clerk Next.js quickstart](https://clerk.com/docs/quickstarts/nextjs) — managed
  authentication boundary.
