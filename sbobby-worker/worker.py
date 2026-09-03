"""Runpod Flash queue worker for the audio-to-sbobina beta."""

from __future__ import annotations

from typing import Any

from runpod_flash import Endpoint

from pipeline import PipelineError, run_pipeline


@Endpoint(
    name="audio-to-sbobina",
    cpu="cpu5c-4-8",
    workers=(0, 1),
    system_dependencies=["ffmpeg"],
    execution_timeout_ms=30 * 60 * 1000,
)
async def process_job(
    audio_url: str | dict[str, Any] = "",
    title: str = "",
    **extra: Any,
) -> dict[str, Any]:
    """Process ``{audio_url, title}`` and return structured lesson artifacts.

    Flash's generated queue handler expands JSON object keys as keyword
    arguments.  Accepting a mapping too keeps direct local invocation handy.
    """
    if isinstance(audio_url, dict):
        input_data = audio_url
    else:
        input_data = {"audio_url": audio_url, "title": title, **extra}
    if not isinstance(input_data, dict):
        return {"status": "failed", "error": {"code": "INVALID_INPUT", "message": "input must be an object"}}
    try:
        result = run_pipeline(
            input_data.get("audio_url", ""),
            input_data.get("title", ""),
        )
        return {"status": "completed", **result}
    except PipelineError as exc:
        return {
            "status": "failed",
            "error": {"code": exc.code, "message": str(exc)},
            "stages": exc.stages,
        }


if __name__ == "__main__":
    import asyncio
    import json
    import sys

    payload = json.loads(sys.stdin.read()) if not sys.stdin.isatty() else {"audio_url": "", "title": "Demo"}
    print(json.dumps(asyncio.run(process_job(payload)), ensure_ascii=False))
