# Log: Fast server-worker iteration

Date: 2026-09-03 13:02
Area: audio-to-sbobina

## Summary

Replaced the browser-only delivery path with a first usable server-worker
iteration. The new private web app uploads MP3/M4A directly to temporary Vercel
Blob storage, starts and polls a Runpod job, renders the returned transcript and
study documents, supports literal search, generates PDFs, and keeps completed
text locally in the browser for 30 days. A Python/FFmpeg worker implements the
full Groq transcription and DeepSeek text pipeline.

The web app and worker were published. The real audio journey remains blocked
only by Blob provisioning and authorization to transfer the existing provider
secrets.

## Files Changed

- `sbobby-worker/`: Runpod Flash worker and provider pipeline.
- `sbobby-web/app/app/`: upload, progress, reader, search, PDF, and local library.
- `sbobby-web/app/api/`: direct Blob upload token and Runpod control routes.
- `sbobby-web/app/sign-in/` and `sbobby-web/proxy.ts`: closed-beta shared access.
- `dev/decisions/2026-09-03--ADR-0002--move-audio-processing-to-runpod.md`: active architecture decision.
- `specs/audio-to-sbobina-web/README.md`: fast-path implementation status.

## Verification

- `python -m py_compile pipeline.py worker.py`: passed.
- `pytest -q`: 4 passed.
- `flash build --no-deps`: passed.
- `node_modules/.bin/eslint app/app/workspace.tsx app/api/jobs/start/route.ts 'app/api/jobs/[jobId]/route.ts'`: passed.
- `node_modules/.bin/tsc --noEmit`: passed.
- `node_modules/.bin/next build`: passed.
- Local production login and `/app` browser smoke: passed.
- `flash deploy --no-deps`: deployed endpoint `vu0rlld758qrrg` to production.
- Initial `vercel deploy --yes`: build reported success but the project had no
  framework preset, produced zero deployment outputs, and all aliases returned
  `404 NOT_FOUND`.
- Set the separate project's framework preset to `nextjs`, then ran
  `vercel deploy --prod --yes --force`: deployment contains 33 outputs.
- `curl -L https://audio-to-sbobina.vercel.app`: HTTP 200 at the private-beta
  sign-in page; the original 404 no longer reproduces.
- Configured sensitive production-only `APP_ACCESS_CODE` and
  `APP_SESSION_TOKEN` values in Vercel, redeployed, and completed a headless
  browser login smoke through to `/app`.

## Notes

- The separate Vercel project is `audio-to-sbobina`; the existing Sbobby production deployment was not changed.
- Required release variables: `APP_ACCESS_CODE`, `APP_SESSION_TOKEN`, `BLOB_READ_WRITE_TOKEN`, `RUNPOD_API_KEY`, and `RUNPOD_ENDPOINT_ID` on Vercel; `GROQ_API_KEY` and `DEEPSEEK_API_KEY` on Runpod.
- The earlier S00 browser workbench remains a later hardening/prototype artifact and is not a release gate.
- Runpod's generated `.runpod/` local state can contain credentials; it was removed and the directory is now ignored.
