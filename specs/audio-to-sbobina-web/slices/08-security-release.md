# S08 — Security, privacy, observability, and beta release

## Contract unlocked

Prove the complete private beta under production-like Vercel conditions. Close
upload, auth, provider-secret, content-redaction, browser-storage, accessibility,
performance, and failure risks without adding a content database or silently
changing the product.

## Scope

- Threat-model untrusted M4A/MP3, imported archives, model output, browser-local
  tenancy, auth/revocation, rate abuse, prompt injection, and secret exposure.
- Apply strict CSP/origin/CSRF, route validation, rate/budget limits, redacted
  logging, safe headers, and production-only route exclusions.
- Configure AI Gateway metadata-only observability, content logging/cache off,
  DeepSeek-only routing, and per-user/stage tags/budgets.
- Configure Groq route abuse protection without storing content.
- Remove or production-disable `/dev/workbench/**` and all fixture controls.
- Run complete browser, live-provider, accessibility, privacy, and deployment
  journeys; document accepted limitations.
- Produce release/runbook docs for invitations, secrets, budgets, incident
  response, deletion expectations, model outage, and rollback.

Out of scope: adding fallback providers, server content storage beyond the
explicit metadata-only quota counters, background
processing, billing, legal certification, medical validation, or any deferred
study feature.

## Security ownership

- `authorize` remains the only access decision.
- `RequestValidator` owns media/schema/origin/size/count limits.
- `RedactionPolicy` owns permitted log/error fields.
- `RateLimitPolicy` owns named coarse Vercel WAF rules plus metadata-only
  Upstash counters for per-user/day provider quotas and concurrency leases; no
  route invents its own and no function-memory counter is accepted as global
  enforcement.
- A dedicated AI Gateway key owns the DeepSeek workload budget with auto top-up
  off; exhausted budget maps 402 to a stable public error. WAF and budget
  and Upstash metadata contain only keyed-HMAC identifiers, routes/stages,
  counters, and bounded TTLs—never lesson content.
- `ContentSecurityPolicy` owns script/connect/font/worker sources.
- `PrivacyAudit` is the test oracle for prohibited content surfaces.

Allowed operational telemetry:

```text
request ID, redacted user ID, route/stage, input byte or token count,
output byte or token count, latency, attempt, provider/model ID,
HTTP status, public error code, deployment/environment
```

Forbidden telemetry: email, filename, audio, transcript, prompts, model output,
project title, archive body, provider raw error, cookies, tokens, and secrets.

## Playable artifact

A production-like protected preview runs the complete invited-student journey
with real browser storage and bounded live-provider smokes. The admin can invite
and revoke but cannot inspect projects; the student can complete, search,
download, export, delete, and import while privacy, quota, outage, and recovery
panels expose the exact release evidence and limitations.

## Integrated user journey

1. Admin invites a student; a non-invited user is rejected.
2. Student signs in and, before file selection, sees truthful local-only,
   storage, deletion, and named third-party processor/retention warnings.
3. Student selects a supported M4A, keeps the tab open, and reaches ready.
4. Repeat the input boundary with MP3.
5. Student reads transcript/full/study, searches literally, and downloads both
   complete PDFs.
6. Refresh after every stage; reselect audio only while transcription is
   incomplete; prove completed text stages are not rerun.
7. Trigger 429, timeout, malformed provider output, quota denial, cancellation,
   corrupted archive, expired project, revocation, and multi-tab contention.
8. Export, delete, import, and verify no server route can recover the project.
9. Delete local data and prove the app, admin, and logs expose no
   application-controlled content copy. Provider processing and retention stay
   governed by provider terms; this test does not claim provider-side erasure.

## Acceptance gates

- Independent security review has no unresolved critical/high finding.
- MIME spoof, malformed containers, excessive duration/size/chunk count,
  decompression/memory exhaustion, hostile model blocks, XSS, path-like names,
  forged IDs, CSRF/origin failure, revoked sessions, and rate abuse fail closed.
- A cookie minted before revocation, public signup, forged/client-writable role,
  disabled admin, and Clerk outage fail closed. Revocation copy states that
  existing browser-local records are not remotely erased.
- Parallel abuse across cold starts and regions cannot bypass Upstash user/day
  quotas or concurrency leases. Default beta caps are one 180-minute source per
  user/day, two concurrent provider calls per user, 1,000,000 DeepSeek input
  tokens and 300,000 output tokens per user/day; changing them is a reviewed
  config change.
- Production has a documented provider-call kill switch. The dedicated Gateway
  key has a USD 25 monthly beta budget with auto top-up off and explicit 402
  handling; Groq receives a USD 25 monthly operational ceiling via its account
  controls when available, otherwise alerts at USD 20 and the kill switch is
  mandatory.
- Provider keys exist only in Vercel secrets/OIDC and are absent from source,
  client chunks, sourcemaps, error output, logs, and archives.
- IndexedDB, Cache API, service workers, Vercel Blob/storage, deployment files,
  logs, traces, analytics, and error reporting contain no audio; server
  observability contains no lesson content.
- Every content route uses `no-store`; AI Gateway content logging/caching is off
  and routing cannot fall back from DeepSeek.
- Release evidence captures the actual AI Gateway logging/cache/budget settings
  and the then-current Vercel, Clerk, Groq, Gateway, and DeepSeek processing and
  retention terms; application tests do not claim provider-side erasure.
- Production navigation/build cannot expose dev workbenches or fixture controls.
- Latest required Chromium/WebKit and manual Safari journeys pass within the S00
  envelope; unsupported browsers receive a truthful block before audio work.
- Keyboard, screen-reader announcements, focus recovery, reduced motion, AA
  contrast, 200% zoom, and long-session readability pass.
- Production build, preview deployment, rollback, invite runbook, budget alerts,
  and incident/log redaction runbook are reproducible.
- Release notes disclose no background run, cloud backup, automatic sharing,
  audio player, semantic search, or verified medical-quality guarantee.

## Verification

```bash
pnpm lint
pnpm typecheck
pnpm test:unit
pnpm test:contract
pnpm test:security
pnpm test:e2e
pnpm build
```

Then run:

- Vercel preview live smoke for a short Groq fixture and short DeepSeek fixture;
- full M4A and MP3 journeys with redacted captures;
- browser storage/cache/log/bundle inspection;
- accessibility automation plus keyboard/zoom manual review;
- dependency/license/vulnerability review;
- independent semantic regression review and dedicated security review;
- `git diff --check` and confirmation that unrelated dirty paths are untouched.

This slice produces integrated UI and PDF shots. Run unprimed
`screenshot-critique` last on the exact production-like success and failure
journeys, including crops for progress, storage warning, search, downloads,
errors, and admin access. Run `compare-screenshots` against each approved visual
baseline and decide which shot is less wrong against the specified product
target. Open only the curated final set with `preview-shots`, allow about five
minutes, and if silent record the rationale, close Preview, and proceed.

## What must stay green

- Every prior slice contract and the entire existing repository suite relevant
  to touched paths.
- No implementation change in `biochimica-sites/` or the historical Python
  pipeline.
- No server content store, Workflow, queue, Blob, fallback model, or semantic
  quality test introduced during “hardening.”

## Human feedback that changes this slice

Feedback may change release copy, visual polish, budget thresholds, supported
browser wording, or runbook presentation. A request for cloud sync, background
work, another model, or automatic sharing reopens architecture and cannot enter
as a release fix.

## Stop or reslice

Stop release for any high security finding, persisted/logged content, secret
exposure, auth bypass, incomplete PDF presented as complete, unsupported source
accepted, or failed required-browser journey. Do not downgrade these to known
limitations.

## Definition of Done

The production-like Vercel beta completes the full agreed journey for invited
students, failure and privacy evidence is reproducible, administrators can
manage access but not content, and the release communicates every local-only and
quality limitation without ambiguity.
