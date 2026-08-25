"""Small, evidence-gated practice-art graph prototype for C07.

Only local filesystem probes are used. Missing or conflicting evidence remains
an actionable candidate; it is never promoted to a terminal ``unknown`` state.
"""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import unicodedata
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Mapping

try:
    from PIL import Image
except ImportError:  # pragma: no cover - the stdlib fallback keeps the probe usable.
    Image = None


SCHEMA = "mak-cycle-c07-practice-art-graph-v1"
RELATIONS = (
    "component_of",
    "version_of",
    "manifestation_of",
    "same_series_candidate",
    "published_as",
)
PENDING = "pending_relation"
UNRESOLVED = "unresolved_candidate"
PROJECT_EXTENSIONS = {"blend", "aep", "psd", "kra", "ora", "xcf", "c4d", "hip", "ma", "mb"}
IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "tif", "tiff", "webp", "bmp", "svg"}
VIDEO_EXTENSIONS = {"mp4", "mov", "mkv", "webm", "avi", "m4v"}
XML_EXTENSIONS = {"xml", "xmp", "svg"}
GENERIC_TOKENS = {
    "a", "an", "and", "art", "copy", "export", "file", "final", "frame", "frames",
    "image", "img", "master", "output", "preview", "project", "published", "render",
    "source", "test", "the", "v", "version",
}


def _json(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value)
    return value


def _tokens(value: str) -> list[str]:
    value = unicodedata.normalize("NFKC", value).replace("\\", "/")
    value = re.sub(r"([a-z])([A-Z])", r"\1 \2", value).lower()
    return re.findall(r"[a-z0-9]+", value)


def _path_tokens(path: Path) -> list[str]:
    return _tokens("/".join(path.parts[:-1]))


def _sequence(stem: str) -> tuple[str | None, int | None]:
    match = re.search(r"^(.*?)(?:[_-](?:frame|frames|f))?[_-](\d{2,6})$", stem, re.I)
    if not match:
        return None, None
    family = "_".join(_tokens(match.group(1))) or "sequence"
    return family, int(match.group(2))


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _ratio(width: int | None, height: int | None) -> float | None:
    if not width or not height:
        return None
    return round(width / height, 6)


def _xml_probe(path: Path, extension: str) -> dict[str, Any]:
    if extension not in XML_EXTENSIONS:
        return {"readable": False, "format": None, "fields": {}, "reason": "not_xml_like"}
    try:
        text = path.read_text(encoding="utf-8", errors="replace")[:1024 * 1024]
        root = ET.fromstring(text)
    except (OSError, ET.ParseError) as exc:
        return {"readable": False, "format": "xml", "fields": {}, "reason": type(exc).__name__}

    fields: dict[str, str] = {}
    for element in root.iter():
        local = element.tag.rsplit("}", 1)[-1]
        if element.text and element.text.strip():
            fields[local] = element.text.strip()[:500]
        for key, value in element.attrib.items():
            fields[f"{local}@{key.rsplit('}', 1)[-1]}"] = str(value)[:500]
    is_xmp = any("xmp" in key.lower() or "rdf" in key.lower() for key in fields) or "xmpmeta" in root.tag.lower()
    return {"readable": True, "format": "xmp" if is_xmp else "xml", "fields": fields, "reason": "parsed"}


def _fraction(value: str | None) -> float | None:
    if not value or value in {"0/0", "N/A"}:
        return None
    try:
        if "/" in value:
            numerator, denominator = value.split("/", 1)
            return round(float(numerator) / float(denominator), 6) if float(denominator) else None
        return round(float(value), 6)
    except (ValueError, ZeroDivisionError):
        return None


def _ffprobe(path: Path, binary: str = "ffprobe") -> dict[str, Any]:
    if shutil.which(binary) is None:
        return {"available": False, "reason": "ffprobe_not_found", "duration": None, "fps": None, "codec": None}
    command = [binary, "-v", "error", "-print_format", "json", "-show_streams", "-show_format", str(path)]
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=False, timeout=15)
        payload = json.loads(result.stdout or "{}") if result.returncode == 0 else {}
    except (OSError, subprocess.SubprocessError, json.JSONDecodeError):
        return {"available": False, "reason": "ffprobe_failed", "duration": None, "fps": None, "codec": None}
    streams = payload.get("streams") or []
    video = next((item for item in streams if item.get("codec_type") == "video"), streams[0] if streams else {})
    duration = _fraction((payload.get("format") or {}).get("duration"))
    if duration is None:
        duration = _fraction(video.get("duration"))
    return {
        "available": True,
        "reason": "parsed",
        "duration": duration,
        "fps": _fraction(video.get("avg_frame_rate") or video.get("r_frame_rate")),
        "codec": video.get("codec_name"),
        "width": video.get("width"),
        "height": video.get("height"),
    }


@dataclass
class Artifact:
    id: str
    path: str
    kind: str
    extension: str
    sha256: str
    bytes: int
    dimensions: dict[str, int] | None = None
    aspect_ratio: float | None = None
    alpha: bool | None = None
    video_duration: float | None = None
    video_fps: float | None = None
    video_codec: str | None = None
    sequence_family: str | None = None
    sequence_index: int | None = None
    name_tokens: list[str] = field(default_factory=list)
    path_tokens: list[str] = field(default_factory=list)
    xml_xmp: dict[str, Any] = field(default_factory=dict)
    evidence_refs: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {key: _json(value) for key, value in self.__dict__.items()}


@dataclass
class RelationCandidate:
    id: str
    source_id: str
    target_id: str | None
    relation: str
    status: str
    score: float
    score_breakdown: dict[str, Any]
    evidence_refs: list[str]
    alternatives: list[dict[str, Any]]
    missing_evidence: list[str]
    next_probe: str

    def as_dict(self) -> dict[str, Any]:
        return {key: _json(value) for key, value in self.__dict__.items()}


def inspect_artifact(path: str | Path, root: str | Path | None = None, ffprobe: str = "ffprobe") -> Artifact:
    file_path = Path(path)
    stat = file_path.stat()
    absolute = file_path.resolve()
    if root is None:
        logical = absolute.as_posix()
    else:
        logical = absolute.relative_to(Path(root).resolve()).as_posix()
    extension = file_path.suffix.lower().lstrip(".")
    name_tokens = _tokens(file_path.stem)
    path_tokens = _path_tokens(file_path)
    sequence_family, sequence_index = _sequence(file_path.stem)
    dimensions = None
    alpha = None
    if extension in IMAGE_EXTENSIONS and Image is not None:
        try:
            with Image.open(file_path) as image:
                dimensions = {"width": image.width, "height": image.height}
                alpha = "A" in image.getbands() or (image.mode == "P" and "transparency" in image.info)
        except (OSError, ValueError):
            pass
    xml_xmp = _xml_probe(file_path, extension)
    if dimensions is None and xml_xmp.get("readable") and extension == "svg":
        width = xml_xmp.get("fields", {}).get("svg@width")
        height = xml_xmp.get("fields", {}).get("svg@height")
        if width and height and str(width).isdigit() and str(height).isdigit():
            dimensions = {"width": int(width), "height": int(height)}
    video = _ffprobe(file_path, ffprobe) if extension in VIDEO_EXTENSIONS else {}
    if dimensions is None and video.get("width") and video.get("height"):
        dimensions = {"width": int(video["width"]), "height": int(video["height"])}
    kind = "project" if extension in PROJECT_EXTENSIONS else "video" if extension in VIDEO_EXTENSIONS else "image" if extension in IMAGE_EXTENSIONS else "document"
    artifact_id = f"artifact:{logical}"
    evidence = [f"{artifact_id}#{field}" for field in ("path", "extension", "sha256", "bytes", "name_tokens", "path_tokens")]
    if dimensions:
        evidence.append(f"{artifact_id}#dimensions")
    if video.get("available"):
        evidence.extend(f"{artifact_id}#video_{field}" for field in ("duration", "fps", "codec"))
    if xml_xmp.get("readable"):
        evidence.append(f"{artifact_id}#xml_xmp")
    return Artifact(
        id=artifact_id,
        path=logical,
        kind=kind,
        extension=extension,
        sha256=_sha256(file_path),
        bytes=stat.st_size,
        dimensions=dimensions,
        aspect_ratio=_ratio((dimensions or {}).get("width"), (dimensions or {}).get("height")),
        alpha=alpha,
        video_duration=video.get("duration"),
        video_fps=video.get("fps"),
        video_codec=video.get("codec"),
        sequence_family=sequence_family,
        sequence_index=sequence_index,
        name_tokens=name_tokens,
        path_tokens=path_tokens,
        xml_xmp=xml_xmp,
        evidence_refs=evidence,
    )


def _meaningful(tokens: Iterable[str]) -> set[str]:
    return {token for token in tokens if token not in GENERIC_TOKENS and len(token) > 1}


def _overlap(left: Artifact, right: Artifact) -> set[str]:
    return _meaningful(left.name_tokens) & _meaningful(right.name_tokens)


def _exportish(artifact: Artifact) -> bool:
    """Return true only for media that can be an export target.

    A numbered frame is an input/component candidate, not an export target;
    XML/XMP sidecars must never become media edges merely because their name
    contains ``export``.
    """
    tokens = set(artifact.name_tokens + artifact.path_tokens)
    return (
        artifact.kind in {"image", "video"}
        and artifact.sequence_index is None
        and not _published(artifact)
        and (artifact.kind == "video" or bool(tokens & {"export", "render", "final", "output", "delivery"}))
    )


def _published(artifact: Artifact) -> bool:
    return bool({"published", "gallery", "public"} & set(artifact.name_tokens + artifact.path_tokens))


def _refs(artifact: Artifact, *fields: str) -> list[str]:
    return [f"{artifact.id}#{field}" for field in fields]


def _raw_candidate(source: Artifact, target: Artifact | None, relation: str, signals: list[dict[str, Any]], refs: list[str], missing: list[str], next_probe: str) -> dict[str, Any]:
    score = round(min(0.99, 0.12 + sum(float(item["contribution"]) for item in signals)), 3)
    status = "supported" if score >= 0.9 and not missing else PENDING if score >= 0.45 else UNRESOLVED
    if relation in {"component_of", "version_of", "published_as"} and not missing and score >= 0.78:
        status = PENDING
    target_id = target.id if target else None
    candidate_id = f"candidate:{relation}:{source.id}->{target_id or 'missing'}"
    return {
        "id": candidate_id,
        "source_id": source.id,
        "target_id": target_id,
        "relation": relation,
        "status": status,
        "score": score,
        "score_breakdown": {"base": 0.12, "signals": signals, "explanation": " + ".join(item["explanation"] for item in signals) or "no positive signal"},
        "evidence_refs": sorted(set(refs)),
        "alternatives": [],
        "missing_evidence": sorted(set(missing)),
        "next_probe": next_probe,
    }


def _pair_candidates(left: Artifact, right: Artifact) -> list[dict[str, Any]]:
    shared = _overlap(left, right)
    same_basename = Path(left.path).stem.lower() == Path(right.path).stem.lower()
    signals_common: list[dict[str, Any]] = []
    refs_common = _refs(left, "name_tokens", "path_tokens") + _refs(right, "name_tokens", "path_tokens")
    if shared:
        signals_common.append({"name": "shared_name_tokens", "value": sorted(shared), "contribution": min(0.36, 0.16 + 0.06 * len(shared)), "explanation": f"shared tokens={sorted(shared)}"})
    if same_basename:
        signals_common.append({"name": "same_basename", "value": True, "contribution": 0.2, "explanation": "same basename"})
    candidates: list[dict[str, Any]] = []
    if left.sequence_family and left.sequence_family == right.sequence_family:
        candidates.append(_raw_candidate(left, right, "same_series_candidate", [{"name": "sequence_family", "value": left.sequence_family, "contribution": 0.6, "explanation": f"same sequence family={left.sequence_family}"}], _refs(left, "sequence_family", "sequence_index") + _refs(right, "sequence_family", "sequence_index"), ["series_manifest_or_curatorial_id"], "inspect sequence manifest or curator declaration"))
    if left.sequence_index is not None and _exportish(right) and shared:
        candidates.append(_raw_candidate(left, right, "component_of", signals_common + [{"name": "frame_to_export_shape", "value": True, "contribution": 0.28, "explanation": "numbered frame paired with export-like artifact"}], refs_common + _refs(left, "sequence_index", "sha256"), ["explicit_composition_or_export_manifest"], "inspect export manifest or project timeline"))
    if right.sequence_index is not None and _exportish(left) and shared:
        candidates.append(_raw_candidate(right, left, "component_of", signals_common + [{"name": "frame_to_export_shape", "value": True, "contribution": 0.28, "explanation": "numbered frame paired with export-like artifact"}], refs_common + _refs(right, "sequence_index", "sha256"), ["explicit_composition_or_export_manifest"], "inspect export manifest or project timeline"))
    if left.kind == "project" and _exportish(right) and shared:
        candidates.append(_raw_candidate(right, left, "version_of", signals_common + [{"name": "project_to_media", "value": True, "contribution": 0.38, "explanation": "media artifact paired with project artifact"}], refs_common + _refs(left, "extension"), ["declared_export_event"], "inspect project export log or embedded project identifier"))
    if right.kind == "project" and _exportish(left) and shared:
        candidates.append(_raw_candidate(left, right, "version_of", signals_common + [{"name": "project_to_media", "value": True, "contribution": 0.38, "explanation": "media artifact paired with project artifact"}], refs_common + _refs(right, "extension"), ["declared_export_event"], "inspect project export log or embedded project identifier"))
    if left.kind in {"image", "video"} and right.kind in {"image", "video"} and _published(left) != _published(right) and shared:
        source, target = (right, left) if _published(left) else (left, right)
        if _exportish(source):
            candidates.append(_raw_candidate(source, target, "published_as", signals_common + [{"name": "publication_token", "value": True, "contribution": 0.3, "explanation": "one path/name is publication-like"}], refs_common, ["publication_record_or_url"], "inspect publication record or platform URL"))
    if (left.kind == right.kind and left.kind in {"image", "video"}) and (shared or same_basename or left.sha256 == right.sha256):
        extra = list(signals_common)
        missing = ["declared_work_id", "curatorial_lineage"]
        refs = refs_common
        if left.sha256 == right.sha256:
            extra.append({"name": "same_sha256", "value": True, "contribution": 0.6, "explanation": "byte-identical artifacts"})
            refs += _refs(left, "sha256") + _refs(right, "sha256")
            missing = []
        if left.aspect_ratio and right.aspect_ratio and left.aspect_ratio != right.aspect_ratio:
            extra.append({"name": "different_aspect_ratio", "value": [left.aspect_ratio, right.aspect_ratio], "contribution": 0.12, "explanation": "same-name family with different proportions"})
            refs += _refs(left, "aspect_ratio") + _refs(right, "aspect_ratio")
        candidates.append(_raw_candidate(left, right, "manifestation_of", extra, refs, missing, "inspect declared work ID, source record, or curatorial note"))
    return candidates


def propose_relations(artifacts: list[Artifact]) -> list[RelationCandidate]:
    raw: list[dict[str, Any]] = []
    for index, left in enumerate(artifacts):
        for right in artifacts[index + 1:]:
            raw.extend(_pair_candidates(left, right))
    projects = [item for item in artifacts if item.kind == "project"]
    media = [item for item in artifacts if _exportish(item)]
    if not projects:
        for item in media:
            raw.append(_raw_candidate(item, None, "version_of", [], _refs(item, "kind", "path"), ["project_artifact"], "locate the authoring project or export witness"))
    if not media:
        for item in projects:
            raw.append(_raw_candidate(item, None, "published_as", [], _refs(item, "kind", "path"), ["export_or_publication_artifact"], "locate an export, publication, or delivery record"))
    by_pair: dict[tuple[str, str | None], list[dict[str, Any]]] = {}
    for item in raw:
        by_pair.setdefault((item["source_id"], item["target_id"]), []).append(item)
    output: list[RelationCandidate] = []
    for item in raw:
        alternatives = []
        for alternative in by_pair[(item["source_id"], item["target_id"])]:
            if alternative["id"] != item["id"]:
                alternatives.append({"relation": alternative["relation"], "score": alternative["score"], "status": alternative["status"], "reason": alternative["score_breakdown"]["explanation"]})
        item["alternatives"] = sorted(alternatives, key=lambda value: (-value["score"], value["relation"]))
        output.append(RelationCandidate(**item))
    return output


def build_graph(paths: Iterable[str | Path], root: str | Path | None = None) -> dict[str, Any]:
    artifacts = [inspect_artifact(path, root=root) for path in paths]
    candidates = propose_relations(artifacts)
    return {
        "schema": SCHEMA,
        "policy": {"filesystem_scope": "explicit_paths_only", "terminal_statuses": ["supported"], "pending_statuses": [PENDING, UNRESOLVED], "blender_or_adobe_execution": False},
        "artifacts": [item.as_dict() for item in artifacts],
        "relation_candidates": [item.as_dict() for item in candidates],
        "edges": [item.as_dict() for item in candidates if item.status == "supported"],
        "summary": {"artifact_count": len(artifacts), "candidate_count": len(candidates), "supported_count": sum(item.status == "supported" for item in candidates), "pending_relation_count": sum(item.status == PENDING for item in candidates), "unresolved_candidate_count": sum(item.status == UNRESOLVED for item in candidates)},
    }
