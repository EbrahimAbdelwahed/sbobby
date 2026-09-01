# Self-hosted FFmpeg assets

S00 serves the pinned FFmpeg WebAssembly runtime from this directory. The
browser worker never fetches a CDN asset and does not write audio to a server.

Versions:

- `@ffmpeg/ffmpeg` 0.12.15
- `@ffmpeg/core` 0.12.10
- `@ffmpeg/util` 0.12.2

SHA-256 (the build script copies these exact package files):

| File | SHA-256 |
| --- | --- |
| `const.js` | `d6a4edf4efd20db2945457741365fd645919c7ff4573929cf1af76f4f3e0ade7` |
| `errors.js` | `619310d7ef5fe5fefa0a31927db862b7c291713cfef4d71753fa8aafd18f4db6` |
| `ffmpeg-core.esm.js` | `e1e7c9208c2fd28f5a93f180a9e57053db66eaf644df6d69498d5f9f1e008879` |
| `ffmpeg-core.esm.wasm` | `9f57947a5bd530d8f00c5b3f2cb2a3492faa7e5d823315342d6a8656d0a6b7b7` |
| `ffmpeg-worker.js` | `feff0ac937ea225e997e1fae997a74f8b8d572423a526da59eb56624b1f3cde7` |

Run `node scripts/copy-ffmpeg-assets.mjs` after dependency installation to
refresh the checked-in assets. The ESM core is intentional: the worker loads
it with `importScripts`/dynamic import under the browser's module worker
contract.
