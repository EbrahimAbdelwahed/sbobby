# S05 — Automatic resumable browser pipeline

## Contract unlocked

Compose S03 and S04 into the default one-click journey. The browser state
machine starts from a selected source, runs directly to complete full and study
documents, checkpoints every successful text artifact, and resumes safely after
refresh or a bounded failure.

## Scope

- Implement the sole `BrowserPipelineOrchestrator` and pure transition reducer.
- Implement stage planning, concurrency limits, retry/backoff, cancellation,
  interruption, stale-input detection, repository invalidation requests, and
  source reselection.
- Commit through `LocalProjectRepository` only.
- Add a progress rail, current-action copy, failure recovery, retry-from-stage,
  and optional diagnostics.
- Permit a student to rerun a selected completed downstream phase while the
  normal new-project journey remains automatic.
- Build a fixture-driven `/dev/workbench/pipeline-states` for every transition.

Out of scope: background processing after the page closes, server job history,
exactly-once provider billing, editorial approval, content editing, PDF layout,
and search.

## API seam and ownership

```ts
interface BrowserPipelineOrchestrator {
  start(projectId: string, file: File): Promise<void>;
  resume(projectId: string, file?: File): Promise<void>;
  retry(projectId: string, stage: PipelineStage, unitId?: string): Promise<void>;
  rerunFrom(projectId: string, stage: RerunnableStage): Promise<void>;
  cancel(projectId: string): Promise<void>;
  subscribe(projectId: string, listener: PipelineListener): Unsubscribe;
}
```

The reducer owns the transition table. The orchestrator owns effects and calls
named clients/repository interfaces. React owns presentation only. No stage may
mutate another stage's data except through repository invalidation.

Allowed main path:

```text
new → source_selected → preparing_audio → transcribing[n]
→ assembling_transcript → segmenting → elaborating[n]
→ assembling_full → compacting[n] → assembling_study → ready
```

Lateral states: `waiting_for_source_reselection`, `retryable_failure`,
`terminal_failure`, `interrupted`, and `expired`.

Rules:

- Persist a successful artifact/receipt before dispatching its dependent work.
- At startup, convert stale `running` to `interrupted`.
- Skip a completed stage only when input hash, pipeline version, prompt version,
  and model ID still match.
- Rerunning an upstream stage asks `LocalProjectRepository` to atomically
  invalidate all downstream outputs; the orchestrator never edits stores.
- Maximum two automatic retries for network/429/5xx; one same-model structural
  repair remains owned by S04 and is not counted as a model fallback.
- Cancellation stops future work and aborts current fetch/worker where possible.
- The page states that closing it pauses work; no fake background claim.

## Playable artifact

An invited student selects a supported file once and watches one progress rail
advance automatically through both text documents. Fixture controls can reload
or fail any stage. The student resumes from completed checkpoints, reselects the
source only when audio work remains, retries a failed unit, or reruns from a
chosen service without losing upstream truth.

## Acceptance gates

- A model-based transition table test covers every allowed and forbidden edge.
- Refresh after each stage resumes from the first missing compatible artifact.
- A stale hash/version can never be skipped or mixed into the new run.
- Concurrency is bounded for audio and section generation; work is never fanned
  out without a cap.
- A failed section cannot cause partial full/study documents to appear ready.
- Retry/rerun replaces the same logical unit and records a new attempt receipt.
- Multi-tab contention has a single local leader or fails with an explicit
  “project open elsewhere” state; two tabs cannot mutate one project concurrently.
- Closing during an in-flight provider call may duplicate later cost, but local
  artifacts remain deterministic and no unreceived response is marked complete.
- Progress/error announcements and controls are keyboard/screen-reader usable.

## Verification

```bash
pnpm test:unit -- pipeline-reducer orchestrator invalidation leader-lock
pnpm test:integration -- pipeline-fixtures
pnpm test:security -- pipeline-errors
pnpm test:e2e -- pipeline-resume pipeline-retry multi-tab
pnpm typecheck
pnpm build
```

Use provider mocks with controllable delay/error and reload the real browser at
every stage boundary. Include cancel, two tabs, expired project, changed prompt,
changed source, 429, timeout, invalid output, and quota failure.

This slice produces visual shots. Run unprimed `screenshot-critique` last on all
progress, paused, reselection, retryable, terminal, canceled, multi-tab, and
ready states with tight progress/error crops. Use `compare-screenshots` against
the S01 pipeline workbench target. Open the curated set with `preview-shots`;
after about five minutes of silence, record the decision and close Preview.

## What must stay green

- S02 atomic repository and S03/S04 service contract suites.
- No duplicated state machine in hooks/components.
- No server job, queue, workflow, project record, or content cache.

## Human feedback that changes this slice

Feedback may change progress grouping, retry/rerun placement, diagnostics, or
copy. It cannot add a mandatory editorial pause or imply background execution.

## Stop or reslice

Stop if a stage needs hidden server persistence to resume, if multi-tab writes
cannot be serialized, or if an operation cannot be bounded to a focused unit.
Split the stage contract instead of widening the orchestrator.

## Definition of Done

The complete text journey is one action, every completed phase is durable only
in the browser, refresh/retry/rerun semantics are deterministic, and the UI is
truthful about tab lifetime and failure.
