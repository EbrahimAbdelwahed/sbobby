# Audio to Sbobina worker

Fast-path beta backend for the browser app. The browser sends a temporary
audio URL and a lesson title to one queue-style Runpod Flash endpoint:

```json
{"audio_url":"https://.../lesson.m4a","title":"Fisiologia — lezione 1"}
```

The CPU worker downloads the file into a temporary directory, converts it to
small MP3 chunks with system FFmpeg, transcribes each chunk with Groq
`whisper-large-v3` in Italian, then uses only DeepSeek for generic
segmentation, sbobina rewriting, and study compaction. The response contains
structured transcript/full/study data plus base64 `full` and `study` PDFs.
Audio is never returned or persisted by this worker; the temporary directory is
removed at the end of the request. Provider keys are read only from the
environment and request bodies/provider bodies are not logged.

The first iteration is intentionally bounded: `MAX_AUDIO_SECONDS` defaults to
four hours, `MAX_DEEPSEEK_INPUT_CHARS` defaults to 200,000 characters, and each
Groq upload is capped at 25 MB. Increase limits only after measuring worker
memory and response sizes. For very large documents, the frontend should move
to a result-store handoff rather than growing the synchronous response.

## Local

```bash
cd sbobby-worker
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
pip install -e '.[test]'
cp .env.example .env
pytest -q
python -m py_compile pipeline.py worker.py
```

FFmpeg and ffprobe must be available on `PATH` locally. No audio or model is
bundled in this repository.

## Flash

Authenticate once with `RUNPOD_API_KEY`, then run the local queue worker or
build/deploy it:

```bash
flash run
flash build
flash deploy
```

Configure `GROQ_API_KEY`, `DEEPSEEK_API_KEY`, and the optional limits in the
Runpod endpoint environment. The deployment uses a CPU5C 4-vCPU/8-GB worker,
one maximum worker, and installs `ffmpeg` as a system dependency. `flash run`
  can run the endpoint locally without contacting provider APIs when tests inject
  mock clients through `pipeline.run_pipeline`.
