# Audio fixtures

The 90-minute fixtures are intentionally not committed. Generate them with:

```bash
node scripts/generate-audio-fixtures.mjs
```

The generator uses the system FFmpeg binary and writes the reproducible files
under `tests/fixtures/audio/generated/`. The committed manifest records the
command, format, duration, and SHA-256 values from the reference run. Hostile
inputs are described there and are synthesized in tests so no audio is stored
in the repository.
