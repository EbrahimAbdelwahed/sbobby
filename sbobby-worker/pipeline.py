"""Synchronous audio-to-sbobina pipeline used by the Flash worker.

The module deliberately has no Runpod dependency.  It can therefore be run and
tested locally with provider doubles while the thin ``worker.py`` module owns
the Flash endpoint decorator.
"""

from __future__ import annotations

import base64
import ipaddress
import json
import os
import re
import shutil
import socket
import subprocess
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Protocol


GROQ_URL = "https://api.groq.com/openai/v1/audio/transcriptions"
DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"
DEFAULT_GROQ_MODEL = "whisper-large-v3"
DEFAULT_DEEPSEEK_MODEL = "deepseek-v4-flash"
DEFAULT_CHUNK_SECONDS = 600
DEFAULT_MAX_DOWNLOAD_BYTES = 200 * 1024 * 1024
DEFAULT_MAX_AUDIO_SECONDS = 4 * 60 * 60
DEFAULT_MAX_TEXT_CHARS = 200_000
DEFAULT_GROQ_MAX_BYTES = 25 * 1024 * 1024


class PipelineError(RuntimeError):
    """A user-safe pipeline failure with no provider body or audio content."""

    def __init__(self, code: str, message: str, stages: list[dict[str, Any]] | None = None):
        super().__init__(message)
        self.code = code
        self.stages = stages or []


class ProviderError(PipelineError):
    pass


@dataclass(frozen=True)
class Span:
    start: float
    end: float
    text: str


@dataclass(frozen=True)
class ChunkTranscript:
    index: int
    start: float
    end: float
    text: str
    spans: tuple[Span, ...]


class Transcriber(Protocol):
    def transcribe(self, audio_path: Path) -> Mapping[str, Any]: ...


class TextGenerator(Protocol):
    def generate(self, operation: str, prompt: str) -> str: ...


@dataclass
class StageTracker:
    stages: list[dict[str, Any]] = field(default_factory=list)

    def start(self, name: str) -> None:
        self.stages.append({"name": name, "status": "running"})

    def complete(self, name: str) -> None:
        for stage in reversed(self.stages):
            if stage["name"] == name and stage["status"] == "running":
                stage["status"] = "completed"
                return

    def fail(self, name: str) -> None:
        for stage in reversed(self.stages):
            if stage["name"] == name and stage["status"] == "running":
                stage["status"] = "failed"
                return


def _env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if not value:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def _require_key(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ProviderError("MISSING_PROVIDER_KEY", f"{name} is not configured")
    return value


def _assert_public_url(url: str) -> urllib.parse.ParseResult:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in {"https", "http"} or not parsed.hostname:
        raise PipelineError("INVALID_AUDIO_URL", "audio_url must be an http(s) URL")
    host = parsed.hostname.lower().rstrip(".")
    if host in {"localhost", "localhost.localdomain"}:
        raise PipelineError("INVALID_AUDIO_URL", "audio_url host is not allowed")
    try:
        addresses = socket.getaddrinfo(host, parsed.port or (443 if parsed.scheme == "https" else 80))
    except OSError:
        # Keep the request useful for signed public hosts whose DNS is only
        # available from the worker network; urllib still validates the scheme.
        addresses = []
    for address in addresses:
        ip = ipaddress.ip_address(address[4][0])
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast:
            raise PipelineError("INVALID_AUDIO_URL", "audio_url host is not allowed")
    return parsed


def _download_audio(url: str, target: Path, max_bytes: int) -> None:
    _assert_public_url(url)
    request = urllib.request.Request(url, headers={"User-Agent": "audio-to-sbobina/0.1"})
    try:
        with urllib.request.urlopen(request, timeout=60) as response, target.open("wb") as output:
            content_length = response.headers.get("Content-Length")
            if content_length and int(content_length) > max_bytes:
                raise PipelineError("AUDIO_TOO_LARGE", "audio file exceeds the configured size limit")
            written = 0
            while True:
                block = response.read(1024 * 1024)
                if not block:
                    break
                written += len(block)
                if written > max_bytes:
                    raise PipelineError("AUDIO_TOO_LARGE", "audio file exceeds the configured size limit")
                output.write(block)
    except PipelineError:
        raise
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise PipelineError("AUDIO_DOWNLOAD_FAILED", "audio download failed") from exc


def _run_ffmpeg(command: list[str]) -> None:
    try:
        subprocess.run(command, check=True, capture_output=True, timeout=900)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError) as exc:
        # stderr can contain paths, URLs, or user-controlled media metadata.
        raise PipelineError("FFMPEG_FAILED", "audio conversion failed") from exc


def _probe_duration(path: Path) -> float:
    command = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        str(path),
    ]
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True, timeout=60)
        duration = float(result.stdout.strip())
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError, ValueError) as exc:
        raise PipelineError("AUDIO_INVALID", "audio duration could not be read") from exc
    if duration <= 0:
        raise PipelineError("AUDIO_INVALID", "audio duration is empty")
    return duration


def _split_audio(source: Path, directory: Path, duration: float, chunk_seconds: int) -> list[tuple[int, float, float, Path]]:
    chunks: list[tuple[int, float, float, Path]] = []
    index = 0
    start = 0.0
    while start < duration:
        end = min(duration, start + chunk_seconds)
        path = directory / f"chunk-{index:04d}.mp3"
        _run_ffmpeg(
            [
                "ffmpeg",
                "-nostdin",
                "-v",
                "error",
                "-y",
                "-ss",
                f"{start:.3f}",
                "-i",
                str(source),
                "-t",
                f"{end - start:.3f}",
                "-map",
                "0:a:0",
                "-ac",
                "1",
                "-ar",
                "16000",
                "-c:a",
                "libmp3lame",
                "-b:a",
                "48k",
                "-f",
                "mp3",
                str(path),
            ]
        )
        if path.stat().st_size > DEFAULT_GROQ_MAX_BYTES:
            raise PipelineError("AUDIO_CHUNK_TOO_LARGE", "audio chunk exceeds the provider upload limit")
        chunks.append((index, start, end, path))
        index += 1
        start = end
    return chunks


def _clean_text(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    return re.sub(r"\s+", " ", value).strip()


def normalize_groq_response(payload: Mapping[str, Any], *, chunk_start: float, chunk_end: float) -> tuple[str, tuple[Span, ...]]:
    """Normalize Groq verbose JSON to stable absolute spans."""
    text = _clean_text(payload.get("text"))
    spans: list[Span] = []
    raw_segments = payload.get("segments")
    if isinstance(raw_segments, list):
        for item in raw_segments:
            if not isinstance(item, Mapping):
                continue
            segment_text = _clean_text(item.get("text"))
            if not segment_text:
                continue
            try:
                start = float(item.get("start", 0.0)) + chunk_start
                end = float(item.get("end", 0.0)) + chunk_start
            except (TypeError, ValueError):
                continue
            start = max(chunk_start, min(start, chunk_end))
            end = max(start, min(end, chunk_end))
            if end == start:
                end = min(chunk_end, start + 0.001)
            spans.append(Span(start=start, end=end, text=segment_text))
    spans.sort(key=lambda span: (span.start, span.end, span.text))
    if not text:
        text = " ".join(span.text for span in spans)
    return text, tuple(spans)


def _json_from_text(value: str) -> Any:
    candidate = value.strip()
    if candidate.startswith("```"):
        candidate = candidate.split("\n", 1)[-1]
        candidate = candidate.rsplit("```", 1)[0].strip()
    try:
        return json.loads(candidate)
    except json.JSONDecodeError as exc:
        raise ProviderError("INVALID_PROVIDER_OUTPUT", "text service returned invalid JSON") from exc


def _safe_title(title: str) -> str:
    value = re.sub(r"[\x00-\x1f\x7f]", "", title or "").strip()
    value = re.sub(r"[/\\:*?\"<>|]", "-", value)
    value = re.sub(r"\s+", " ", value).strip(" .")
    return value[:120] or "lezione"


def _text_for_prompt(value: str, label: str) -> str:
    if len(value) > _env_int("MAX_DEEPSEEK_INPUT_CHARS", DEFAULT_MAX_TEXT_CHARS):
        raise PipelineError("TEXT_TOO_LARGE", f"{label} exceeds the configured text limit")
    return value


def _multipart(fields: Mapping[str, str], file_field: str, filename: str, content: bytes, content_type: str) -> tuple[bytes, str]:
    boundary = "----audio-to-sbobina-boundary"
    body = bytearray()
    for name, value in fields.items():
        body.extend(f"--{boundary}\r\nContent-Disposition: form-data; name=\"{name}\"\r\n\r\n{value}\r\n".encode())
    body.extend(
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"{file_field}\"; filename=\"{filename}\"\r\nContent-Type: {content_type}\r\n\r\n".encode()
    )
    body.extend(content)
    body.extend(f"\r\n--{boundary}--\r\n".encode())
    return bytes(body), f"multipart/form-data; boundary={boundary}"


class GroqWhisperClient:
    def __init__(self, api_key: str | None = None, model: str | None = None, opener: Callable[..., Any] | None = None):
        self.api_key = api_key or _require_key("GROQ_API_KEY")
        self.model = model or os.getenv("GROQ_MODEL", DEFAULT_GROQ_MODEL)
        self.opener = opener or urllib.request.urlopen

    def transcribe(self, audio_path: Path) -> Mapping[str, Any]:
        try:
            body, content_type = _multipart(
                {
                    "model": self.model,
                    "language": "it",
                    "response_format": "verbose_json",
                    "temperature": "0",
                    "timestamp_granularities[]": "segment",
                },
                "file",
                audio_path.name,
                audio_path.read_bytes(),
                "audio/mpeg",
            )
            request = urllib.request.Request(
                GROQ_URL,
                data=body,
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": content_type},
                method="POST",
            )
            with self.opener(request, timeout=180) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            raise ProviderError("GROQ_REQUEST_FAILED", f"Groq request failed ({exc.code})") from exc
        except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
            raise ProviderError("GROQ_REQUEST_FAILED", "Groq request failed") from exc


class DeepSeekClient:
    def __init__(self, api_key: str | None = None, model: str | None = None, opener: Callable[..., Any] | None = None):
        self.api_key = api_key or _require_key("DEEPSEEK_API_KEY")
        self.model = model or os.getenv("DEEPSEEK_MODEL", DEFAULT_DEEPSEEK_MODEL)
        self.opener = opener or urllib.request.urlopen

    def generate(self, operation: str, prompt: str) -> str:
        request_body = json.dumps(
            {
                "model": self.model,
                "temperature": 0.2,
                "max_tokens": _env_int("DEEPSEEK_MAX_TOKENS", 8192),
                "messages": [
                    {"role": "system", "content": _system_prompt(operation)},
                    {"role": "user", "content": prompt},
                ],
            }
        ).encode("utf-8")
        request = urllib.request.Request(
            DEEPSEEK_URL,
            data=request_body,
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            method="POST",
        )
        try:
            with self.opener(request, timeout=300) as response:
                payload = json.loads(response.read().decode("utf-8"))
            return str(payload["choices"][0]["message"]["content"])
        except urllib.error.HTTPError as exc:
            raise ProviderError("DEEPSEEK_REQUEST_FAILED", f"DeepSeek request failed ({exc.code})") from exc
        except (urllib.error.URLError, TimeoutError, OSError, KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
            raise ProviderError("DEEPSEEK_REQUEST_FAILED", "DeepSeek request failed") from exc


def _system_prompt(operation: str) -> str:
    return {
        "segment": "Sei un assistente di segmentazione per trascrizioni universitarie in italiano. Restituisci esclusivamente JSON valido.",
        "elaborate": "Sei un redattore di sbobine universitarie in italiano. Riorganizza il testo in modo chiaro, senza aggiungere fatti non presenti. Restituisci solo testo Markdown semplice.",
        "compact": "Sei un assistente di studio universitario in italiano. Comprimi il testo mantenendo i concetti presenti, senza inventare informazioni. Restituisci solo testo Markdown semplice.",
    }[operation]


def _segment_prompt(transcript: str) -> str:
    return (
        "Dividi la trascrizione in sezioni tematiche. Ogni sezione deve riferirsi a un intervallo contiguo di chunk, "
        "coprire tutti i chunk esattamente una volta e mantenere l'ordine. Restituisci {\"sections\":[{\"title\":string,\"start_chunk\":int,\"end_chunk\":int}]} "
        "con indici zero-based.\n\nTRASCRIZIONE:\n" + transcript
    )


def _elaborate_prompt(title: str, text: str) -> str:
    return f"Titolo sezione: {title}\n\nRielabora fedelmente il seguente testo in una sezione di sbobina leggibile:\n{text}"


def _compact_prompt(title: str, text: str) -> str:
    return f"Titolo sezione: {title}\n\nCrea una versione compatta per il ripasso, mantenendo definizioni, relazioni e passaggi presenti:\n{text}"


def _fallback_section_plan(chunks: list[ChunkTranscript]) -> list[dict[str, Any]]:
    return [{"title": "Lezione", "start_chunk": 0, "end_chunk": len(chunks) - 1}]


def _validate_sections(value: Any, chunk_count: int) -> list[dict[str, Any]]:
    if not isinstance(value, Mapping) or not isinstance(value.get("sections"), list) or not value["sections"]:
        raise ProviderError("INVALID_PROVIDER_OUTPUT", "segmentation output has an invalid shape")
    sections: list[dict[str, Any]] = []
    expected = 0
    for raw in value["sections"]:
        if not isinstance(raw, Mapping):
            raise ProviderError("INVALID_PROVIDER_OUTPUT", "segmentation output has an invalid section")
        try:
            start = int(raw["start_chunk"])
            end = int(raw["end_chunk"])
        except (KeyError, TypeError, ValueError) as exc:
            raise ProviderError("INVALID_PROVIDER_OUTPUT", "segmentation output has invalid ranges") from exc
        title = _clean_text(raw.get("title")) or "Sezione"
        if start != expected or end < start or end >= chunk_count:
            raise ProviderError("INVALID_PROVIDER_OUTPUT", "segmentation output does not cover the transcript")
        sections.append({"title": title, "start_chunk": start, "end_chunk": end})
        expected = end + 1
    if expected != chunk_count:
        raise ProviderError("INVALID_PROVIDER_OUTPUT", "segmentation output does not cover the transcript")
    return sections


def _join_chunk_text(chunks: Iterable[ChunkTranscript]) -> str:
    return "\n\n".join(chunk.text for chunk in chunks if chunk.text).strip()


def run_pipeline(
    audio_url: str,
    title: str,
    *,
    transcriber: Transcriber | None = None,
    text_generator: TextGenerator | None = None,
    chunk_seconds: int | None = None,
    downloader: Callable[[str, Path, int], None] = _download_audio,
) -> dict[str, Any]:
    """Download, transcribe, transform, and render one lesson.

    Audio is held under a temporary directory and is deleted automatically when
    this function returns.  Only structured text and bounded PDF bytes are
    returned to the caller.
    """
    if not isinstance(audio_url, str) or not audio_url.strip():
        raise PipelineError("INVALID_AUDIO_URL", "audio_url is required")
    if not isinstance(title, str) or not title.strip():
        raise PipelineError("INVALID_TITLE", "title is required")
    title = _safe_title(title)
    tracker = StageTracker()
    max_download = _env_int("MAX_DOWNLOAD_BYTES", DEFAULT_MAX_DOWNLOAD_BYTES)
    max_duration = _env_int("MAX_AUDIO_SECONDS", DEFAULT_MAX_AUDIO_SECONDS)
    chunk_size = chunk_seconds or _env_int("CHUNK_SECONDS", DEFAULT_CHUNK_SECONDS)
    if chunk_size <= 0:
        raise PipelineError("INVALID_CONFIG", "CHUNK_SECONDS must be positive")

    with tempfile.TemporaryDirectory(prefix="audio-to-sbobina-") as temp_dir:
        root = Path(temp_dir)
        source = root / "source.audio"
        chunks_dir = root / "chunks"
        chunks_dir.mkdir()
        current_stage = "download"
        try:
            tracker.start(current_stage)
            downloader(audio_url, source, max_download)
            tracker.complete(current_stage)

            current_stage = "prepare_audio"
            tracker.start(current_stage)
            duration = _probe_duration(source)
            if duration > max_duration:
                raise PipelineError("AUDIO_TOO_LONG", "audio duration exceeds the configured limit")
            chunks = _split_audio(source, chunks_dir, duration, chunk_size)
            tracker.complete(current_stage)

            current_stage = "transcribe"
            tracker.start(current_stage)
            whisper = transcriber or GroqWhisperClient()
            transcripts: list[ChunkTranscript] = []
            for index, start, end, path in chunks:
                payload = whisper.transcribe(path)
                text, spans = normalize_groq_response(payload, chunk_start=start, chunk_end=end)
                transcripts.append(ChunkTranscript(index=index, start=start, end=end, text=text, spans=spans))
            tracker.complete(current_stage)

            current_stage = "segment"
            tracker.start(current_stage)
            generator = text_generator or DeepSeekClient()
            transcript_text = _join_chunk_text(transcripts)
            segment_raw = generator.generate("segment", _segment_prompt(_text_for_prompt(transcript_text, "transcript")))
            sections = _validate_sections(_json_from_text(segment_raw), len(transcripts))
            tracker.complete(current_stage)

            current_stage = "elaborate"
            tracker.start(current_stage)
            full_sections: list[dict[str, Any]] = []
            for section in sections:
                section_chunks = transcripts[section["start_chunk"] : section["end_chunk"] + 1]
                source_text = _text_for_prompt(_join_chunk_text(section_chunks), "section")
                generated = generator.generate("elaborate", _elaborate_prompt(section["title"], source_text)).strip()
                full_sections.append({**section, "text": generated})
            tracker.complete(current_stage)

            current_stage = "compact"
            tracker.start(current_stage)
            study_sections: list[dict[str, Any]] = []
            for section in full_sections:
                generated = generator.generate(
                    "compact",
                    _compact_prompt(section["title"], _text_for_prompt(section["text"], "full section")),
                ).strip()
                study_sections.append({**section, "text": generated})
            tracker.complete(current_stage)

            current_stage = "render_pdfs"
            tracker.start(current_stage)
            full_pdf = render_pdf(title, full_sections, variant="full")
            study_pdf = render_pdf(title, study_sections, variant="study")
            tracker.complete(current_stage)
        except PipelineError as exc:
            tracker.fail(current_stage)
            raise PipelineError(exc.code, str(exc), tracker.stages) from exc
        except Exception as exc:
            tracker.fail(current_stage)
            raise PipelineError("PIPELINE_FAILED", "pipeline failed", tracker.stages) from exc

    return {
        "version": "0.1",
        "title": title,
        "duration_seconds": round(duration, 3),
        "stages": tracker.stages,
        "transcript": {
            "text": transcript_text,
            "chunks": [
                {
                    "index": chunk.index,
                    "start": round(chunk.start, 3),
                    "end": round(chunk.end, 3),
                    "text": chunk.text,
                    "spans": [
                        {"start": round(span.start, 3), "end": round(span.end, 3), "text": span.text}
                        for span in chunk.spans
                    ],
                }
                for chunk in transcripts
            ],
        },
        "full": {"title": title, "sections": full_sections},
        "study": {"title": title, "sections": study_sections},
        "pdfs": {"full": full_pdf, "study": study_pdf},
    }


def _wrap_text(text: str, width: int) -> list[str]:
    words = re.split(r"\s+", text.strip()) if text.strip() else [""]
    lines: list[str] = []
    line = ""
    for word in words:
        if len(line) + len(word) + (1 if line else 0) <= width:
            line = f"{line} {word}".strip()
        else:
            if line:
                lines.append(line)
            line = word[:width]
    if line or not lines:
        lines.append(line)
    return lines


def _pdf_escape(value: str) -> bytes:
    # WinAnsi covers the Italian alphabet and keeps the renderer dependency-free.
    encoded = value.encode("cp1252", errors="replace")
    return b"(" + encoded.replace(b"\\", b"\\\\").replace(b"(", b"\\(").replace(b")", b"\\)") + b")"


def _pdf_object(body: bytes) -> bytes:
    return body + b"\n"


def _make_pdf(lines_by_page: list[list[tuple[str, int]]]) -> bytes:
    objects: list[bytes] = []
    page_ids: list[int] = []
    # Reserve catalog/pages objects; page and stream objects are appended below.
    objects.extend([b"", b""])
    font_id = 0
    for lines in lines_by_page:
        content = bytearray()
        for index, (line, size) in enumerate(lines):
            y = 800 - index * 14
            content.extend(b"BT\n/F1 " + str(size).encode() + b" Tf\n50 " + str(y).encode() + b" Td\n")
            content.extend(_pdf_escape(line) + b" Tj\nET\n")
        stream_id = len(objects) + 1
        objects.append(b"<< /Length " + str(len(content)).encode() + b" >>\nstream\n" + bytes(content) + b"endstream")
        page_id = len(objects) + 1
        objects.append(
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 "
            + str(0).encode()
            + b" 0 R >> >> /Contents "
            + str(stream_id).encode()
            + b" 0 R >>"
        )
        page_ids.append(page_id)
    font_id = len(objects) + 1
    objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>")
    # Patch references now that all object numbers are known.
    objects[0] = b"<< /Type /Catalog /Pages 2 0 R >>"
    objects[1] = b"<< /Type /Pages /Kids [" + b" ".join(f"{page_id} 0 R".encode() for page_id in page_ids) + b"] /Count " + str(len(page_ids)).encode() + b" >>"
    for index, body in enumerate(objects):
        if b"/Type /Page" in body:
            objects[index] = body.replace(b"/F1 0 0 R", b"/F1 " + str(font_id).encode() + b" 0 R")
    output = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0]
    for object_id, body in enumerate(objects, start=1):
        offsets.append(len(output))
        output.extend(f"{object_id} 0 obj\n".encode() + _pdf_object(body) + b"endobj\n")
    xref = len(output)
    output.extend(f"xref\n0 {len(objects) + 1}\n".encode())
    output.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        output.extend(f"{offset:010d} 00000 n \n".encode())
    output.extend(f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode())
    return bytes(output)


def render_pdf(title: str, sections: list[Mapping[str, Any]], *, variant: str) -> dict[str, Any]:
    lines: list[tuple[str, int]] = [(title, 18), ("Documento di studio" if variant == "study" else "Sbobina completa", 10), ("", 10)]
    for index, section in enumerate(sections, start=1):
        lines.append((f"{index}. {_clean_text(section.get('title')) or 'Sezione'}", 14))
        for paragraph in str(section.get("text", "")).splitlines():
            lines.extend((wrapped, 10) for wrapped in _wrap_text(paragraph, 94))
        lines.append(("", 10))
    if not lines:
        lines = [(title, 18)]
    pages = [lines[index : index + 52] for index in range(0, len(lines), 52)]
    payload = _make_pdf(pages)
    filename = f"{_safe_title(title)}-{'studio' if variant == 'study' else 'sbobina'}.pdf"
    return {
        "filename": filename,
        "mime_type": "application/pdf",
        "bytes": len(payload),
        "base64": base64.b64encode(payload).decode("ascii"),
        "page_count": len(pages),
    }
