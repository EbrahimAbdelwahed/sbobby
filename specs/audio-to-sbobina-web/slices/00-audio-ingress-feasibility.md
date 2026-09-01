# S00 — No-storage audio ingress feasibility

## Contract unlocked

Prove or reject the only architecture that satisfies all current constraints:
the browser turns realistic M4A and MP3 lectures into independently decodable
audio chunks, each complete Vercel request stays below 4 MB, the
preview-protected probe forwards the chunk to Groq without persistence, and the
browser receives timestamped text.

This is a stop/go slice. It does not claim transcript quality and must not grow
into the product pipeline.

## Scope

- A fixture-driven `/dev/workbench/audio-ingress` route.
- Deterministic synthetic 90-minute M4A and MP3 fixture generation.
- An `AudioPreparer` Web Worker experiment with cancellation and telemetry.
- Self-hosted, version/hash-pinned worker, FFmpeg core, and WASM assets running
  under the intended production CSP with no worker network or persistent FS.
- Candidate internal encodings evaluated only for decodability, size, runtime,
  memory, and Groq acceptance; no WER or semantic comparison.
- A Vercel Deployment Protection-gated preview probe that accepts one
  independent chunk, calls Groq `whisper-large-v3`, and returns normalized
  timestamped JSON. Product authentication is deliberately deferred to S01.
- Exact preview Host/Origin agreement, a required custom probe header, no CORS,
  and rejection of missing/`null`/cross-site origins before the first paid call.
- A preview-only provider-call kill switch, one in-flight request per protected
  operator, and teardown of live access immediately after evidence capture.
- Storage/log/cache inspection proving the audio is absent after each run.

Out of scope: IndexedDB projects, DeepSeek, final UI, PDF, search, Blob, queues,
background work, and promotion of multiple audio implementations.

## API seam and ownership

```ts
interface AudioPreparer {
  inspect(file: File): Promise<AudioSourceDescriptor>;
  prepare(file: File, budget: AudioChunkBudget, signal: AbortSignal):
    AsyncIterable<PreparedAudioChunk>;
}

type AudioChunkBudget = {
  maxAudioBytes: 3_500_000;
  maxRequestBodyBytes: 3_500_000;
  maxResponseBytes: 1_000_000;
  overlapMs: number;       // fixed by this slice
  internalMediaType: string; // fixed by this slice
};
```

`AudioPreparer` is the only owner of audio conversion. `AudioChunkBudget` is the
only owner of request/response sizing. Browser-to-Vercel transport is the raw
prepared-audio body with bounded validated metadata headers; it does not use
browser `FormData`, whose multipart overhead is variable. The probe route builds
the Groq multipart body server-side and delegates provider logic to
`GroqTranscriptionAdapter`. No `File`, `Blob`, PCM, encoded chunk, or object URL
crosses into a durable contract.

Likely owned files:

```text
sbobby-web/app/dev/workbench/audio-ingress/**
sbobby-web/app/api/internal/spikes/transcription-chunk/route.ts
sbobby-web/src/client/audio/{preparer,prepare.worker,chunk-budget}.ts
sbobby-web/src/server/providers/groq-transcription.ts
sbobby-web/tests/fixtures/audio/**
sbobby-web/tests/{unit,integration,security}/audio-*.test.ts
specs/audio-to-sbobina-web/assets/audio-fixtures-manifest.json
```

The minimal Next.js/Vercel scaffold created here is the permanent build
foundation; S01 extends it rather than re-bootstrapping or replacing it. The
preview-only probe route is not a public product contract and S01 must remove
it before establishing `/api/v1/**`. Spike-only candidate adapters must be
deleted before this slice closes; exactly one adapter may be promoted behind
`AudioPreparer`.

## Playable artifact

An operator with access to the protected preview opens the workbench, chooses
either fixture or a local file, sees source metadata, conversion progress,
chunk byte sizes, worker memory, request totals, Groq latency, and normalized
transcript spans. A storage audit panel shows zero audio records and zero
cached requests.

## Acceptance gates

- Both deterministic 90-minute fixtures work on the latest desktop Chromium and
  WebKit used by Playwright; manual Safari verification is recorded.
- Every produced chunk is independently decodable and accepted by Groq.
- Every browser request body is measured before fetch and is at most 3,500,000
  bytes; normalized responses are bounded to 1,000,000 bytes. Preview tests cover
  just below, at, and above both application caps.
- No gap exists in the declared time ranges; overlap is explicit and bounded.
- Peak worker memory is below 1 GiB on the recorded reference machine.
- Source byte and container bounds are checked before worker allocation. Decoded
  samples, output bytes, chunk count, heap, and wall time are capped; a breach
  terminates the worker and clears its in-memory WASM filesystem.
- Preparation of the 90-minute fixture completes within 10 minutes, begins
  producing useful chunks without waiting for the whole pipeline, and aborts.
- Reload requires source reselection; no audio is recovered from storage.
- No audio bytes, filename, provider body, or secret appear in IndexedDB, Cache
  API, Blob storage, filesystem, analytics, tracing, logs, or public errors.
- Vercel Deployment Protection rejects access to the preview without the
  configured team/automation credential; within the platform limit the probe
  maps 413, 415, 429,
  timeout, and redacted 5xx behavior without leaking provider bodies.
- A body above Vercel's own 4.5 MB ceiling may receive Vercel's platform 413;
  the spec does not promise an application error shape when the handler cannot
  run.
- Cross-site form, missing/`null`/spoofed Origin, forged custom header from a
  disallowed origin, and permissive preflight attempts never reach Groq.

The target production envelope is 180 minutes/250 MiB, but it is not promised
until measured. Supporting less than 90 minutes is a failed gate.

## Verification

```bash
pnpm test:unit -- audio
pnpm test:contract -- transcription
pnpm test:security -- audio-ingress
pnpm test:e2e -- audio-ingress
pnpm typecheck
pnpm build
```

Run a live Vercel preview smoke with a short generated fixture and Groq
credentials. Record the deployment, browser versions, reference hardware,
fixture hashes, encoding choice, overlap, request sizes, runtime, peak memory,
and storage/log audit in this slice.

Fixtures include truncated/malformed containers, MIME and duration lies, huge
metadata, expansion bombs, cap boundaries, cancellation, and repeated worker
crashes. The preview smoke runs under the production-intended CSP.

This slice produces visual shots. As the final visual check, run an unprimed
`screenshot-critique` on the full workbench plus tight crops of progress,
limits, cancellation, and failure states. Open the smallest useful set with
`preview-shots` for a non-blocking review of about five minutes. If the user is
silent, decide from the evidence, record the rationale here, close Preview, and
continue. Use `compare-screenshots` only after a prior accepted shot exists.

## What must stay green

- No changes to `biochimica-sites/`, the Python pipeline, or existing outputs.
- No persistent storage dependency or server content schema.
- No provider key in any client bundle.
- Final CSP permits only the exact self-hosted worker/WASM mechanism and no
  broad `'unsafe-eval'`, remote core asset, OPFS, or service-worker fallback.

## Human feedback that changes this slice

Feedback may change the diagnostic layout or evidence presentation. It cannot
weaken byte/resource caps, required browsers, no-application-storage evidence,
or the stop/go nature of the gate.

## Stop conditions

Stop the feature, do not implement S01+, and request a new product decision if:

- either input format cannot meet the gate in a required browser;
- a realistic fixture requires persistent intermediary storage;
- a request cannot stay below the budget;
- worker memory/runtime makes the beta unusable;
- required FFmpeg behavior needs remote assets, persistent browser filesystems,
  worker networking, or broad `'unsafe-eval'`;
- any audit finds persisted or logged audio.

The only valid next choices after failure are a lower user-approved duration,
temporary object storage, or non-Vercel processing. None is pre-authorized.

## Definition of Done

The report ends with one verdict, one production `AudioPreparer`, fixed internal
encoding and overlap values, reproducible fixtures, exact evidence, and no
remaining candidate path. The README Next Agent Prompt is updated before S01.
The probe route is explicitly marked for removal by S01 and is never promoted
as an unauthenticated product API.
