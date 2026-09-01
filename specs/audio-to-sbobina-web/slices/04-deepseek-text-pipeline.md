# S04 — DeepSeek-only segmentation, elaboration, and study compaction

## Contract unlocked

Expose the three model-backed text services required by the product behind one server
application service and one pinned DeepSeek adapter. A canonical transcript
becomes structurally valid full and study documents through resumable bounded
operations, without another model or a semantic quality gate.

## Scope

- Add generic, versioned prompts for segmentation, elaboration, and compact
  study transformation.
- Add one DeepSeek adapter through the AI SDK and Vercel AI Gateway.
- Add thin invite-protected routes for every named service.
- Segment by references to transcript unit IDs, elaborate per section, compact
  each full section, and assemble full/study documents deterministically.
- Validate schemas, reference integrity, exact segmentation coverage, request/
  response bounds, and deterministic final assembly.
- Add provider-disabled fixture workbenches for every valid/failure shape.

Out of scope: Luna/Kimi/another model, fallback, semantic grading, WER, medical
fact checking, subject prompts, custom glossaries, user editing, chat, or model
comparison.

## API seam and ownership

Routes:

```text
POST /api/v1/text/segment
POST /api/v1/text/elaborate
POST /api/v1/text/compact
```

Each route authenticates, validates a discriminated request, calls
`TextPipelineService`, and maps one typed response/error. The service is the
only owner of stage semantics; `DeepSeekTextAdapter` is the only provider owner;
`PromptCatalog` is the only prompt owner.

```ts
interface DeepSeekTextAdapter {
  generate<TInput, TOutput>(operation: TextOperation<TInput, TOutput>):
    Promise<ProviderResult<TOutput>>;
}

type TextOperationKind =
  | "segment"
  | "elaborate"
  | "compact";
```

Provider contract:

- `model = deepseek/deepseek-v4-flash-0731`;
- AI Gateway restricted to DeepSeek, no fallback models;
- no content cache and content logging disabled;
- per-user/stage redacted tags and budget limits;
- one same-model repair on structurally invalid output;
- fixed maximum input/output and server duration;
- resolved model ID, prompt version, hashes, usage, and latency returned in a
  redacted local receipt.

Every route reserves bounded maximum input/output tokens and one concurrency
lease through the S01 `RateLimitPolicy` before the model call, then atomically
settles against provider-reported usage. Retries/repairs share an idempotent
operation identity but consume their actual usage. Missing quota state or the
provider kill switch fails closed.

Document output is typed blocks (`paragraph`, `bullets`, `callout`, `table` only
if the PDF/viewer contract supports it). HTML, scripts, remote assets, arbitrary
URLs, and unreferenced transcript unit IDs are rejected.

Provider operations have no tools, browsing, URL fetch, file access, or dynamic
provider selection. Transcript instructions are untrusted content. Adversarial
fixtures verify only that output stays inside inert typed schemas and cannot
cause effects; they do not claim the model semantically ignored an injection.

## Structural validators

- Segmentation covers every canonical transcript unit exactly once, in order,
  with no gap or overlap.
- Every section range exists and `firstUnitId <= lastUnitId`.
- Elaboration output remains bound to its requested section ID and source range.
- Pure `DocumentAssembler` preserves section order and IDs and rejects gaps,
  duplicates, or a second title/owner without invoking a model.
- Study sections derive from the corresponding full section and preserve source
  ranges; they do not feed back into the full document.
- Final assembly fails on missing/duplicate sections or size truncation.

These validators do not judge truth, terminology, completeness of ideas,
hallucinations, or medical quality.

## Playable artifact

`/dev/workbench/documents` accepts a fixed transcript fixture and shows the
segmentation plan, per-section full blocks, study blocks, provenance receipts,
and structural failures. With live credentials, one short fixture can run all
services. The workbench explicitly labels the result “schema validated, content
quality not evaluated.”

## Acceptance gates

- All three model services are independently callable and compose with the pure
  document assembler in the expected order.
- Long input is split at canonical unit/section boundaries before context or
  Vercel payload limits, never by silent character truncation.
- A malformed provider output gets exactly one repair request with the same
  model; the second failure returns `INVALID_PROVIDER_OUTPUT` and keeps prior
  artifacts.
- Network/429/5xx retry does not change input, prompt, model, or stage identity.
- Routes set `no-store`; tests prove prompt/text/response bodies are absent from
  logs, errors, caches, and client bundles.
- The root repository Luna policy is unchanged; the scoped app instruction
  records this user-authorized exception.
- No test introduces a golden semantic answer or alternative model.

## Verification

```bash
pnpm test:unit -- text-pipeline prompt-catalog structural-validators
pnpm test:contract -- text-routes deepseek-output
pnpm test:security -- text-redaction gateway-config
pnpm test:e2e -- document-workbench
pnpm typecheck
pnpm build
```

Run one live Vercel preview smoke using a short non-sensitive text fixture. It
verifies current model availability, structured response, usage receipt, no
fallback, and error mapping only.

This slice produces visual shots. Run unprimed `screenshot-critique` last on the
segmentation, full, study, provenance, invalid-output, rate-limit, and context
limit workbench states. Use `compare-screenshots` against the approved document
workbench baseline once one exists. Open the curated shots with `preview-shots`,
allow about five minutes, then record/close/proceed if the user is silent.

## What must stay green

- S01 contracts/import/auth, S02 repository, and S03 transcript semantics.
- No provider call in components or client modules.
- No server content store or Vercel Workflow; only the S01 metadata-only quota
  policy may write operational counters.

## Human feedback that changes this slice

Feedback may change generic prompt wording, block presentation, or service
diagnostics. Any change that adds a quality benchmark, fallback, subject prompt,
or editorial approval requires a product decision and spec update.

## Stop or reslice

Stop if the verified Gateway list no longer exposes the pinned model, if a
required stage cannot fit bounded operations, or if exact segmentation coverage
cannot be enforced. Do not route to another model.

## Definition of Done

One canonical transcript fixture reliably produces structurally complete full
and study documents through the three named DeepSeek-only services, every output
has local provenance, and the UI/tests make no unearned quality claim.
