# Plan: Audio-to-Sbobina web specification

Date: 2026-09-01 00:08 CEST
Area: sbobby-web

## Goal

Create a complete, implementation-ready specification for a new browser-only
Audio-to-Sbobina application deployed on Vercel. The product must accept M4A and
MP3 lessons, transcribe through Groq, segment and rework text through DeepSeek
V4 Flash, generate full and study PDFs, and provide literal local search.

## Scope

- In scope: product contract, Vercel/browser architecture, local data ownership,
  transient audio handling, auth, pipeline state, service seams, UI routes,
  security, observability, slice graph, playable checkpoints, verification, and
  handoff state under `specs/audio-to-sbobina-web/`.
- Out of scope: implementation, modification of existing pipeline source,
  semantic search, audio playback, mobile/desktop apps, provider fallbacks,
  subject-specific prompts, and model-output quality evaluation.

## Approach

1. Consolidate the user decisions with repository and official platform facts.
2. Produce three independent spec drafts with fewest-slices, risk-first, and
   seam-quality biases. Attempt the required Claude/Fable draft, then use a
   third independent Codex draft if the local CLI is unavailable.
3. Synthesize the canonical multi-slice spec and explicitly resolve the
   browser-local/Vercel upload constraints.
4. Run architecture, security, and refactor-clean audits; apply accepted
   findings without changing the agreed product scope.
5. Verify the materialized spec, references, TODO graph, and next-agent handoff.

## Risks

- Vercel Functions enforce a 4.5 MB request/response payload limit, so strict
  no-storage audio ingestion requires a browser chunking feasibility gate.
- Browser-local persistence conflicts with cross-device and automatic
  cross-user sharing; the beta must use explicit export/import instead.
- Direct-to-PDF processing without server persistence must remain resumable
  from IndexedDB and cannot silently depend on a durable server copy.
- The user explicitly accepts DeepSeek-only generation with no quality
  benchmark; structural validation remains required, but semantic quality is an
  accepted product risk.

## Verification

- `find specs/audio-to-sbobina-web -type f -maxdepth 3 | sort`
- `rg` checks for required decisions, slice links, contracts, screenshot gates,
  and Next Agent Prompt state.
- `git diff --check -- specs/audio-to-sbobina-web dev/plans dev/logs`
