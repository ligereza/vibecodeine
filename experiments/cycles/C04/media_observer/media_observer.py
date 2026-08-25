"""Read-only technical observer for the real C04 media artifact.

The observer hashes one explicitly supplied file before and after a bounded
``ffprobe`` metadata query.  It never opens a media player, renders,
transcodes, or writes a media file.  The emitted document is deliberately
closed: it contains technical observations only, not provenance relations.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any, Mapping, Sequence


SCHEMA = "c04.media_observer.v1"
EXPECTED_SHA256 = "b7253320e7a23917439dd6ad2fa084a68510469517b76b6428c54f9856ca0776"
DEFAULT_MEDIA_PATH = Path("/home/mak/curatoria_inbox/ARICA/tottem_ojo.mp4")
HASH_CHUNK_BYTES = 1 << 20
DEFAULT_TIMEOUT_SECONDS = 120

FFPROBE_QUERY = (
    "format=format_name,format_long_name,duration,size,bit_rate,nb_streams:"
    "stream=index,codec_type,codec_name,codec_long_name,profile,width,height,"
    "avg_frame_rate,r_frame_rate,duration,nb_frames,nb_read_frames,channels,"
    "sample_rate,channel_layout"
)


def build_ffprobe_command(
    media_path: str | Path, ffprobe_bin: str = "ffprobe"
) -> list[str]:
    """Build a metadata-only command; the final argument is the sole input."""

    return [
        ffprobe_bin,
        "-v",
        "error",
        "-count_frames",
        "-print_format",
        "json",
        "-show_format",
        "-show_streams",
        "-show_entries",
        FFPROBE_QUERY,
        str(media_path),
    ]


def _fingerprint(path: Path) -> dict[str, Any]:
    digest = hashlib.sha256()
    byte_count = 0
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(HASH_CHUNK_BYTES), b""):
            digest.update(block)
            byte_count += len(block)
    return {"sha256": digest.hexdigest(), "bytes": byte_count}


def _safe_text(value: Any, source_path: Path) -> str:
    text = str(value or "")
    return text.replace(str(source_path), "<artifact>")


def _int_or_none(value: Any) -> int | None:
    if value in (None, ""):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _float_or_none(value: Any) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _stream_observation(stream: Mapping[str, Any]) -> dict[str, Any]:
    """Keep query fields only; metadata tags and disposition are not copied."""

    result: dict[str, Any] = {
        "index": _int_or_none(stream.get("index")),
        "type": stream.get("codec_type"),
        "codec": stream.get("codec_name"),
        "codec_long_name": stream.get("codec_long_name"),
        "profile": stream.get("profile"),
        "duration_seconds": _float_or_none(stream.get("duration")),
        "declared_frames": _int_or_none(stream.get("nb_frames")),
        "observed_frames": _int_or_none(stream.get("nb_read_frames")),
        "frame_rate": stream.get("avg_frame_rate"),
    }
    if stream.get("width") is not None or stream.get("height") is not None:
        result["dimensions"] = {
            "width": _int_or_none(stream.get("width")),
            "height": _int_or_none(stream.get("height")),
        }
    if stream.get("channels") is not None:
        result["channels"] = _int_or_none(stream.get("channels"))
    if stream.get("sample_rate") is not None:
        result["sample_rate_hz"] = _int_or_none(stream.get("sample_rate"))
    if stream.get("channel_layout") is not None:
        result["channel_layout"] = stream.get("channel_layout")
    return result


def sanitize_ffprobe_payload(raw: Mapping[str, Any]) -> dict[str, Any]:
    """Convert ffprobe JSON into a stable, metadata-only observation."""

    raw_streams = raw.get("streams", [])
    streams = [
        _stream_observation(stream)
        for stream in raw_streams
        if isinstance(stream, Mapping)
    ]
    raw_format = raw.get("format", {})
    if not isinstance(raw_format, Mapping):
        raw_format = {}

    video_stream = next((item for item in streams if item["type"] == "video"), None)
    dimensions = video_stream.get("dimensions") if video_stream else None
    frame_counts = [
        {
            "stream_index": item["index"],
            "type": item["type"],
            "declared": item["declared_frames"],
            "observed": item["observed_frames"],
        }
        for item in streams
    ]
    return {
        "container": {
            "format": raw_format.get("format_name"),
            "format_long_name": raw_format.get("format_long_name"),
            "stream_count": _int_or_none(raw_format.get("nb_streams")),
        },
        "duration_seconds": _float_or_none(raw_format.get("duration")),
        "dimensions": dimensions,
        "frames": {
            "video": video_stream.get("observed_frames") if video_stream else None,
            "by_stream": frame_counts,
        },
        "streams": streams,
    }


def _blocked(
    *,
    source: Path,
    command: Sequence[str],
    exit_code: int | None,
    reason: str,
    before: dict[str, Any] | None,
    after: dict[str, Any] | None,
    detail: str = "",
) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "status": "blocked",
        "artifact": {"name": source.name},
        "integrity": {
            "expected_sha256": EXPECTED_SHA256,
            "before": before,
            "after": after,
            "before_matches": bool(before and before["sha256"] == EXPECTED_SHA256),
            "after_matches": bool(after and after["sha256"] == EXPECTED_SHA256),
        },
        "probe": {
            "program": command[0],
            "command": [*command[:-1], "<artifact>"],
            "exit_code": exit_code,
            "detail": _safe_text(detail, source),
        },
        "limits": {
            "read_only": True,
            "writes_performed": False,
            "render_requested": False,
            "transcode_requested": False,
            "scope": "one explicitly supplied file and one metadata query",
        },
        "block_reason": reason,
    }


def observe_media(
    media_path: str | Path = DEFAULT_MEDIA_PATH,
    *,
    ffprobe_bin: str = "ffprobe",
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
) -> dict[str, Any]:
    """Observe one file and return ``status=blocked`` for every failed gate."""

    source = Path(media_path)
    command = build_ffprobe_command(source, ffprobe_bin)
    before: dict[str, Any] | None = None
    after: dict[str, Any] | None = None
    try:
        before = _fingerprint(source)
    except (OSError, ValueError) as exc:
        return _blocked(
            source=source,
            command=command,
            exit_code=None,
            reason="pre_probe_hash_failed",
            before=None,
            after=None,
            detail=str(exc),
        )

    if before["sha256"] != EXPECTED_SHA256:
        try:
            after = _fingerprint(source)
        except (OSError, ValueError):
            after = None
        return _blocked(
            source=source,
            command=command,
            exit_code=None,
            reason="pre_probe_sha256_mismatch",
            before=before,
            after=after,
            detail="expected C04 artifact digest did not match before probing",
        )

    try:
        completed = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )
        probe_exit_code: int | None = completed.returncode
        probe_stderr = _safe_text(completed.stderr, source)
    except FileNotFoundError as exc:
        probe_exit_code = None
        probe_stderr = str(exc)
        completed = None
    except subprocess.TimeoutExpired as exc:
        probe_exit_code = None
        probe_stderr = _safe_text(exc, source)
        completed = None
    except OSError as exc:
        probe_exit_code = None
        probe_stderr = str(exc)
        completed = None

    try:
        after = _fingerprint(source)
    except (OSError, ValueError) as exc:
        return _blocked(
            source=source,
            command=command,
            exit_code=probe_exit_code,
            reason="post_probe_hash_failed",
            before=before,
            after=None,
            detail=str(exc),
        )

    if after["sha256"] != EXPECTED_SHA256:
        return _blocked(
            source=source,
            command=command,
            exit_code=probe_exit_code,
            reason="post_probe_sha256_mismatch",
            before=before,
            after=after,
            detail="artifact digest changed or no longer matches after probing",
        )

    if completed is None:
        return _blocked(
            source=source,
            command=command,
            exit_code=probe_exit_code,
            reason="ffprobe_unavailable_or_timed_out",
            before=before,
            after=after,
            detail=probe_stderr,
        )
    if completed.returncode != 0:
        return _blocked(
            source=source,
            command=command,
            exit_code=completed.returncode,
            reason="ffprobe_failed",
            before=before,
            after=after,
            detail=probe_stderr,
        )

    try:
        raw = json.loads(completed.stdout)
        if not isinstance(raw, Mapping):
            raise ValueError("ffprobe JSON root is not an object")
        media = sanitize_ffprobe_payload(raw)
    except (json.JSONDecodeError, TypeError, ValueError) as exc:
        return _blocked(
            source=source,
            command=command,
            exit_code=completed.returncode,
            reason="ffprobe_json_invalid",
            before=before,
            after=after,
            detail=str(exc),
        )

    return {
        "schema": SCHEMA,
        "status": "ok",
        "artifact": {
            "name": source.name,
            "sha256": after["sha256"],
            "bytes": after["bytes"],
        },
        "integrity": {
            "expected_sha256": EXPECTED_SHA256,
            "before": before,
            "after": after,
            "before_matches": before["sha256"] == EXPECTED_SHA256,
            "after_matches": after["sha256"] == EXPECTED_SHA256,
            "unchanged_during_probe": before == after,
        },
        "probe": {
            "program": command[0],
            "command": [*command[:-1], "<artifact>"],
            "exit_code": completed.returncode,
            "stderr": _safe_text(completed.stderr, source),
        },
        "media": media,
        "limits": {
            "read_only": True,
            "writes_performed": False,
            "render_requested": False,
            "transcode_requested": False,
            "provenance_inferred": False,
            "scope": "one explicitly supplied file and one metadata query",
            "not_established": "technical metadata does not establish export history",
        },
    }


def json_document(observation: Mapping[str, Any]) -> str:
    """Serialize one compact, deterministic JSON document for stdout."""

    return json.dumps(observation, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
