# S03 — Groq transcription and canonical transcript assembly

## Contract unlocked

Provide the bounded audio preparation, one-chunk transport, normalization, and
pure assembly operations needed to turn prepared chunks into one complete,
deterministic, timestamped canonical transcript. S05 alone owns their lifecycle.

## Scope

- Productize the S00 `AudioPreparer` and transcription route; do not fork them.
- Add `TranscriptionClient` for one prepared chunk with abort support and stable
  typed errors; it does not retry or schedule batches.
- Normalize Groq verbose JSON into `TranscriptChunk`.
- Assemble ordered chunks, offset timestamps, and remove overlap duplication
  deterministically.
- Add an ephemeral workbench that processes one chunk at a time and displays the
  final in-memory transcript; it owns no reusable scheduler or recovery state.

Out of scope: DeepSeek, semantic correction, editorial changes, audio playback,
waveforms, WER/medical-quality evaluation, and server job state.

## API seam and ownership

`POST /api/v1/transcriptions/chunks` remains the only audio route. It accepts the
S00 frozen internal media type, a body below 4 MB, and validated metadata:

```ts
type TranscriptionChunkRequestMeta = {
  requestId: string;
  projectId: string;
  sourceFingerprint: string;
  chunkIndex: number;
  startMs: number;
  endMs: number;
  sha256: string;
};

type TranscriptChunk = {
  chunkIndex: number;
  sourceSha256: string;
  text: string;
  spans: Array<{ startMs: number; endMs: number; text: string }>;
  modelId: "whisper-large-v3";
};
```

The server adapter fixes Groq options: Italian language, temperature zero,
verbose JSON, segment and word timestamps when supported. It never logs the
filename, audio, prompt, response body, or raw provider error.

After authorization/origin/schema checks and before Groq, the route uses the
S01 `RateLimitPolicy` to reserve declared audio seconds and a concurrency lease
with a retry-idempotency key. Denial or unavailable control state fails closed;
the route always settles/releases in `finally` without storing audio.

`TranscriptAssembler` is the sole owner of ordering and overlap de-duplication:

```ts
assemble(manifest: AudioManifest, chunks: TranscriptChunk[]):
  CanonicalTranscript;
```

It uses indexes, source offsets, normalized longest suffix/prefix matching, and
stable tie breaking. It never invokes an LLM. The final transcript is an ordered
list of immutable timestamped units with deterministic IDs.

## Playable artifact

In `/dev/workbench/transcription`, an invited student selects M4A or MP3,
prepares it, explicitly submits each chunk, and assembles the normalized result
in memory. The workbench proves the service seam without promising persistence,
retry, concurrency, reselection, or product progress behavior before S05.

## Acceptance gates

- The workbench permits only one explicit in-flight chunk; the production
  client contains no hidden retry, persistence, or fan-out.
- Chunk order, timestamp offset, de-duplication, whitespace normalization, and
  unit IDs are deterministic across repeated assembly.
- Manifest ranges cover the complete source duration; assembly detects missing,
  duplicate, conflicting, or out-of-range chunks and refuses completion.
- Provider timestamps that are unsorted, negative, or outside a chunk are
  normalized or rejected by documented rules.
- Aborting one request stops its worker/fetch where possible and never marks a
  transcript chunk complete.
- No test grades words or medical accuracy; tests cover only transport,
  structure, timing, completeness, and failure behavior.
- Parallel requests, retries, cold starts, and quota-store outage cannot bypass
  the configured audio-seconds/day or concurrency caps.

## Verification

```bash
pnpm test:unit -- transcript-assembler transcription-client
pnpm test:contract -- groq-transcription
pnpm test:security -- transcription-route redaction
pnpm test:e2e -- transcription-workbench
pnpm typecheck
pnpm build
```

Fixtures must include missing chunks, duplicate chunks, conflicting hashes,
unsorted timestamps, overlap with punctuation/case drift, silence, 429, timeout,
and single-request cancellation. Run a preview live smoke with a short
synthetic file; it checks availability/schema only.

This slice produces visual shots. Run unprimed `screenshot-critique` last on
preparing, one-chunk pending, rate-limited, cancel, and complete transcript
views. Use `compare-screenshots` against approved S01/S02
shell shots. Open a curated set with `preview-shots`; after about five minutes
without feedback, record the evidence-based decision and close Preview.

## What must stay green

- S00 size/no-storage evidence, S01 auth/import firewall, and S02 atomic writes.
- No DeepSeek or correction logic in transcript assembly.
- No server content persistence, queue, background job, or audio cache; only the
  S01 metadata-only quota policy may write operational counters.

## Human feedback that changes this slice

Feedback may change transcript typography or diagnostics visibility. Product
progress, retry, and recovery feedback belongs to S05.

## Stop or reslice

Stop if deterministic assembly cannot prove complete source-time coverage or if
a live route requires audio storage. Update S00 rather than adding a second
chunker.

## Definition of Done

Prepared chunks from supported M4A/MP3 inputs produce exactly one structurally
complete canonical transcript in memory. The service has no second scheduler,
retry policy, quality claim, or audio persistence; S05 owns product recovery.
