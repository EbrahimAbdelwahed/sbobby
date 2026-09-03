from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from pipeline import (
    PipelineError,
    _make_pdf,
    normalize_groq_response,
    render_pdf,
    run_pipeline,
)


class FakeTranscriber:
    def __init__(self):
        self.paths: list[Path] = []

    def transcribe(self, audio_path: Path):
        self.paths.append(audio_path)
        return {
            "text": "Il cuore pompa il sangue.",
            "segments": [{"start": 0.0, "end": 0.8, "text": "Il cuore pompa il sangue."}],
        }


class FakeTextGenerator:
    def __init__(self):
        self.operations: list[str] = []

    def generate(self, operation: str, prompt: str) -> str:
        self.operations.append(operation)
        if operation == "segment":
            # The synthetic fixture is one chunk; the pipeline validator is
            # tested separately for multi-chunk ranges.
            return json.dumps({"sections": [{"title": "Fisiologia", "start_chunk": 0, "end_chunk": 0}]})
        if operation == "elaborate":
            return "## Fisiologia\nIl cuore pompa il sangue in modo coordinato."
        return "- Cuore: pompa il sangue."


def test_normalize_groq_offsets_and_orders_spans():
    text, spans = normalize_groq_response(
        {
            "text": "Prima seconda",
            "segments": [
                {"start": 1.0, "end": 1.4, "text": " seconda "},
                {"start": -1.0, "end": 0.2, "text": "Prima"},
            ],
        },
        chunk_start=10.0,
        chunk_end=12.0,
    )
    assert text == "Prima seconda"
    assert [round(span.start, 1) for span in spans] == [10.0, 11.0]
    assert all(10.0 <= span.start <= span.end <= 12.0 for span in spans)


def test_pipeline_runs_with_synthetic_audio_and_mocked_providers(tmp_path, monkeypatch):
    audio_path = tmp_path / "fixture.mp3"
    subprocess.run(
        [
            "ffmpeg",
            "-nostdin",
            "-v",
            "error",
            "-y",
            "-f",
            "lavfi",
            "-i",
            "sine=frequency=440:duration=1",
            "-ac",
            "1",
            "-ar",
            "16000",
            str(audio_path),
        ],
        check=True,
    )
    transcriber = FakeTranscriber()
    generator = FakeTextGenerator()
    result = run_pipeline(
        "https://example.test/fixture.mp3",
        "Lezione 1",
        transcriber=transcriber,
        text_generator=generator,
        downloader=lambda _url, target, _limit: target.write_bytes(audio_path.read_bytes()),
    )
    assert result["version"] == "0.1"
    assert result["transcript"]["chunks"][0]["text"] == "Il cuore pompa il sangue."
    assert result["full"]["sections"][0]["text"].startswith("## Fisiologia")
    assert result["study"]["sections"][0]["text"].startswith("-")
    assert result["pdfs"]["full"]["base64"]
    assert result["pdfs"]["study"]["base64"]
    assert result["stages"][-1]["status"] == "completed"
    assert generator.operations == ["segment", "elaborate", "compact"]
    assert len(transcriber.paths) == 1


def test_invalid_segmentation_does_not_silently_truncate(tmp_path):
    audio_path = tmp_path / "fixture.mp3"
    subprocess.run(
        [
            "ffmpeg",
            "-nostdin",
            "-v",
            "error",
            "-y",
            "-f",
            "lavfi",
            "-i",
            "sine=frequency=440:duration=1",
            "-ac",
            "1",
            "-ar",
            "16000",
            str(audio_path),
        ],
        check=True,
    )

    class InvalidGenerator(FakeTextGenerator):
        def generate(self, operation: str, prompt: str) -> str:
            if operation == "segment":
                return '{"sections":[{"title":"Bad","start_chunk":1,"end_chunk":1}]}'
            return super().generate(operation, prompt)

    with pytest.raises(PipelineError) as error:
        run_pipeline(
            "https://example.test/fixture.mp3",
            "Lezione",
            transcriber=FakeTranscriber(),
            text_generator=InvalidGenerator(),
            downloader=lambda _url, target, _limit: target.write_bytes(audio_path.read_bytes()),
        )
    assert error.value.code == "INVALID_PROVIDER_OUTPUT"
    assert error.value.stages[-1] == {"name": "segment", "status": "failed"}


def test_rendered_pdf_is_bounded_and_starts_with_pdf_header():
    result = render_pdf("Lezione à", [{"title": "Titolo", "text": "È una frase con caratteri italiani."}], variant="study")
    import base64

    payload = base64.b64decode(result["base64"])
    assert payload.startswith(b"%PDF-")
    assert result["page_count"] == 1
    assert result["bytes"] == len(payload)
