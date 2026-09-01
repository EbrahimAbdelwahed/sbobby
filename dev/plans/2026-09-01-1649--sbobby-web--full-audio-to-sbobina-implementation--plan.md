# Plan: Full Audio-to-Sbobina implementation

Date: 2026-09-01 16:49 CEST
Area: sbobby-web

## Goal

Implement every open slice in `specs/audio-to-sbobina-web/`, verify each
checkpoint, deploy the completed private beta, push focused Git history, and
close the spec without overwriting the existing Sbobby medical-study product.

## Scope

- In scope: S00 through S08, Next.js application scaffold, local/browser data
  plane, Vercel provider routes, auth/quota integration, UI, tests, visual and
  security evidence, preview/production deployment, spec handoff, commits, push,
  and spec closure.
- Out of scope: unrelated root worktree deletions, `biochimica-sites/`, legacy
  Python pipeline behavior, the currently deployed Sbobby study/review product,
  semantic quality testing, cloud project content, and audio persistence.

## Approach

1. Preserve the existing `sbobby-web.vercel.app` production deployment. Keep
   the source in local `sbobby-web/`, but deploy it only through the separate
   Vercel project `audio-to-sbobina` per ADR-0001.
2. S00 stop/go: scaffold the permanent Next.js/test foundation, implement one
   browser audio adapter, fixture generator, protected Groq probe, and prove the
   no-storage byte/runtime/CSP contract on local browsers and Vercel preview.
3. S01: establish canonical schemas, import firewall, Clerk Organization auth,
   CSRF/origin controls, WAF/Upstash quota boundary, accessible app shell, and
   fixture workbenches.
4. Parallel wave after S01: S02 owns IndexedDB/retention; S03 owns bounded Groq
   transport and pure transcript assembly. Integrate and review independently.
5. S04: add the DeepSeek-only server text service and structural validators.
6. S05: compose the sole browser orchestrator and recovery UI over S02–S04.
7. Parallel presentation wave: S06 owns document layout/PDF rendering; S07a
   owns long-form viewer and literal search. Then S07b owns safe transfer and
   download integration.
8. S08: complete threat model, quotas, release evidence, browser/accessibility
   checks, independent semantic/security review, preview and production deploy.
9. After every pass: refactor-clean, focused review, exact staging/commit, spec
   handoff update, and immediate continuation. At the end, run `close-spec`.

## Risks

- The existing Vercel project serves a live Sbobby study dashboard whose source
  is absent locally; replacing that deployment would violate repository rules.
- S00 may honestly fail if browser FFmpeg cannot meet the 90-minute, memory,
  CSP, or under-3.5-MB request contract without persistent audio.
- Provider/auth/resource credentials may be absent; local mocked contracts can
  proceed, but live gates and release cannot be claimed without them.
- The root worktree contains extensive unrelated changes. Every pass must stage
  only named `sbobby-web/`, spec, and new dev-memory paths.
- The spec's DeepSeek-only rule intentionally differs from the root Luna policy;
  the scoped `sbobby-web/AGENTS.md` must own and document the exception.

## Verification

- Slice-specific focused test commands from each spec file.
- `pnpm lint`, `pnpm typecheck`, `pnpm test:unit`, `pnpm test:contract`,
  `pnpm test:security`, `pnpm test:e2e`, `pnpm build`.
- Local Chromium/WebKit flows, screenshot pixel/byte change evidence, unprimed
  screenshot critique, PDF rendering/text extraction, bundle/storage/log audit.
- Vercel preview live smokes, auth/revocation/quota checks, deployment inspect,
  production smoke, `git diff --check`, focused status/diff review, and push.
