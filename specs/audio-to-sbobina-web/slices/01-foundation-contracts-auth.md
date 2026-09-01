# S01 — Application foundation, contracts, and invite-only auth

## Contract unlocked

Create the clean application boundary future slices consume: a Vercel-deployable
Next.js App Router shell, versioned shared contracts, enforced client/server
imports, and invite-only `student`/`admin` authorization on pages and APIs.

## Scope

- Extend the S00 Next.js/Vercel scaffold with strict TypeScript, complete package
  scripts, error/loading boundaries, accessible shell, and preview configuration.
- Add a scoped `sbobby-web/AGENTS.md` recording DeepSeek-only NLP for this app.
- Add runtime-validated contracts for projects, pipeline stages, transcripts,
  documents, APIs, exports, errors, hashes, and timestamps.
- Integrate Clerk through the current Next.js-compatible pattern.
- Protect `/app/**` and `/api/v1/**`; restrict `/app/admin/**` to `admin`.
- Remove the S00 preview-only probe endpoint before adding product API routes;
  `authorize` becomes the sole application authorization boundary.
- Add fixture-driven workbenches for shell, progress states, and public errors.
- Add import firewall and bundle-secret tests.
- Make an exact Host/Origin allowlist, required custom CSRF header, no-CORS
  policy, and SameSite cookies part of the mutation-route foundation.
- Define the sole `RateLimitPolicy`, provider-call kill switch, Vercel WAF
  baseline, and metadata-only Upstash adapter before product provider routes.

Out of scope: real IndexedDB writes, audio/provider calls, pipeline logic, PDF,
search, custom password storage, cloud project records, and course libraries.

## API seam and ownership

`src/contracts/**` is the only owner of cross-boundary data. Each contract has:

- a TypeScript type derived from or paired with one runtime schema;
- a `schemaVersion` where it persists or exports;
- explicit byte/string/list bounds;
- JSON round-trip fixtures and rejection fixtures.

`src/server/auth/authorize.ts` is the only application authorization API:

```ts
type SessionView = { userId: string; role: "student" | "admin" };

authorize(request, requirement: "student" | "admin"):
  Promise<SessionView>;
```

One configured Clerk Organization owns identity, invitations, and the
`org:student`/`org:admin` roles. Public signup is disabled and client-writable
user metadata is never authoritative. `authorize` verifies an active user and
session plus current server-side membership in the configured organization;
provider/admin mutations fail closed if current membership cannot be checked.
The application stores no password, session, lesson, or invitation database.
Admins can invite members, remove membership, and revoke that user's active
sessions, but cannot inspect projects or remotely erase browser-local content.

The import firewall is a product invariant:

- `src/client/**` and components cannot import `src/server/**`;
- `src/server/**` cannot import `src/client/**` or UI;
- both may import `src/contracts/**`;
- route handlers stay thin;
- provider environment variables are absent from client chunks.

`RateLimitPolicy` is the only paid-route admission API. It atomically reserves
and settles per-user/day audio seconds or text tokens and short concurrency
leases in Upstash. Keys contain only keyed-HMAC user/source/request IDs,
route/stage, counters, and TTLs of at most 35 days. It is idempotent for retry
identities, fails closed when unavailable, and honors `PROVIDER_CALLS_ENABLED`.
WAF remains the coarse IP/route shield; neither routes nor function memory own
counters.

## Playable artifact

- Invited student signs in and sees an empty local project library shell.
- Admin sees the member-management route.
- Non-invited, revoked, student-on-admin, and unauthenticated cases render
  distinct accessible states.
- `/dev/workbench/pipeline-states` renders every state from fixtures with no
  provider or storage dependency.

## Acceptance gates

- All protected pages and every `/api/v1/**` route enforce authorization on the
  server.
- A pre-revocation cookie fails after membership removal/session revocation;
  public signup, forged roles, disabled admins, and Clerk lookup failure fail
  closed.
- `GET /api/v1/session` returns only `SessionView` and `Cache-Control: no-store`.
- Contract fixtures reject unknown discriminants, oversized strings/lists,
  invalid hashes/timestamps, partial documents, and audio bytes in durable data.
- `PipelineError` maps internal causes to stable redacted public codes.
- ESLint/architecture tests reject every forbidden import direction.
- Production bundles contain no Groq, DeepSeek, Gateway, or Clerk secret.
- Multi-instance tests prove quota reservations and concurrency leases are
  atomic/idempotent and contain no lesson text, raw identity, prompt, or output.
- Missing/`null`/cross-site Origin, Host mismatch, cross-site forms, permissive
  preflight, and missing CSRF headers fail before any provider/admin effect.
- Error/loading/empty/forbidden states remain keyboard and screen-reader usable.
- The scoped app policy does not alter the root policy for other projects.

## Verification

```bash
pnpm lint
pnpm typecheck
pnpm test:unit -- contracts auth rate-limit-policy
pnpm test:contract
pnpm test:security -- imports secrets auth csrf quota-metadata
pnpm test:e2e -- auth shell
pnpm build
```

This slice produces visual shots. Run an unprimed `screenshot-critique` last on
sign-in, empty library, admin, forbidden, loading, and public-error shots with
tight crops for focus, alerts, and status labels. Open the curated set through
`preview-shots`; allow about five minutes, then record and proceed if silent.
Use `compare-screenshots` against any approved prior shell shot and judge against
the stated accessibility/hierarchy target, not pixel parity.

## What must stay green

- S00 request budgets, no-storage evidence, production `AudioPreparer` seam,
  and the retained provider adapter; the temporary probe route does not remain.
- Existing repository behavior outside `sbobby-web/`.
- Vercel preview deployment with no content database or Blob binding.

## Human feedback that changes this slice

Feedback may change information hierarchy, copy, managed auth provider, or the
admin surface. It must not weaken server authorization, add cloud project state,
or merge client/server ownership.

## Stop or reslice

Stop if the chosen auth integration cannot implement true invite-only access,
server route protection, and revocation without custom credential storage. Stop
if current Next.js/Vercel versions invalidate the planned proxy/route pattern;
update the spec from official docs before changing architecture.

## Definition of Done

A fresh implementation agent can use the contracts without guessing, an invited
student and admin see correct fixture surfaces, forbidden users fail closed, and
automated imports/bundle checks prove the server boundary.
