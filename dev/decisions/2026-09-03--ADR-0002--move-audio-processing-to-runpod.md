# ADR-0002: Move audio processing to a Python worker on Runpod

Date: 2026-09-03
Status: Accepted

## Context

The browser-FFmpeg feasibility gate consumed implementation time without
delivering the requested end-to-end beta. The repository already contains a
working Python/FFmpeg pipeline, and the product owner explicitly prioritized a
publishable first iteration over proving a browser-only audio architecture.

## Decision

Use Vercel for the private web UI and small control-plane routes. Upload audio
directly from the browser to temporary Vercel Blob storage, then submit its URL
to a single Runpod Flash CPU worker. The worker downloads the file, runs
FFmpeg, Groq transcription, DeepSeek segmentation/elaboration/compaction, and
returns the structured text result. The browser renders and downloads PDFs.

The temporary source Blob is deleted when the Runpod job completes or fails.
This explicitly supersedes the local-only/no-server-audio constraint and the
S00 stop/go gate in ADR-0001's original implementation plan.

## Consequences

- The first usable iteration can ship without FFmpeg/WASM or long-running work
  in the browser.
- Audio exists temporarily in Vercel Blob and on the worker's ephemeral disk.
- Runpod and Blob credentials become release prerequisites.
- The existing `sbobby-web.vercel.app` remains untouched; deployment still
  targets the separate `audio-to-sbobina` project.
- Authentication starts as a shared closed-beta access code and can be replaced
  with managed per-user invitations after the core journey is validated.

## Alternatives Considered

- Continue browser FFmpeg hardening: rejected for the first iteration because
  it delays the end-to-end product.
- Send whole audio through a Vercel Function: rejected because of the platform
  request-body limit.
