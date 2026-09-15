"""Adapt an explicitly observed folder to the MAK Portafolio inbox.

The filesystem observer belongs to FLUJO and remains the authority for
physical provenance. This adapter only translates its file artifacts into the
small record shape consumed by IRIS; it does not call an embedder, assign
authorship, or decide which file is an artwork.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Mapping

from flujo.knowledge.archive_observer import observe_archive


SCHEMA = "faro-portfolio-folder-adapter-v1"
INBOX_SCHEMA = "faro-portfolio-inbox-v1"
_MEDIA_FAMILIES = {"image", "video", "audio"}


def default_corpus_id(root: str | Path) -> str:
    """Derive a stable source id without deriving an artist identity."""
    path = str(Path(root).expanduser().resolve())
    return "portfolio-folder:%s" % hashlib.sha256(path.encode("utf-8")).hexdigest()[:16]


def _source_context(
    *, corpus_id: str, artist_id: str | None,
) -> dict[str, Any]:
    return {
        "schema": "faro-portfolio-corpus-context-v1",
        "corpus_id": corpus_id,
        "artist_id": artist_id,
        "artist_context": "declared" if artist_id else "not_supplied",
        "source": "explicit_folder_observation",
        "membership": {
            "relation": "belongs_to_declared_corpus",
            "basis": "explicit_input_context",
            "authorship_claim": False,
        },
        "preserved_provenance": ["relative_path", "folder", "subfolders", "metadata", "sha256"],
        "signals": {
            "metadata": "ordering_and_declared_evidence",
            "semantic": "candidate_relations_only",
            "visual": "candidate_relations_only",
        },
        "workflow": {
            "format": "artist_specific",
            "precision_target": "workflow_fit",
            "universal_accuracy_required": False,
            "human_gate": True,
        },
    }


def _item_type(family: str) -> str:
    return {
        "image": "image",
        "video": "video",
        "audio": "audio",
        "document": "document",
        "code": "code",
        "data": "metadata",
        "archive": "archive",
    }.get(family, "record")


def _item(artifact: Mapping[str, Any], root: str, corpus_id: str) -> dict[str, Any]:
    relative = str(artifact["relative_path"])
    parts = relative.split("/")
    family = str(artifact.get("family") or "unknown")
    return {
        "id": str(artifact["artifact_ref"]),
        "tipo_contenido": _item_type(family),
        "fecha": None,
        "publicacion_id": "",
        "publicacion_archivo": "",
        "medio_indice": 0,
        "medio_total": 1,
        "descripcion_original": "",
        "uri_export": relative,
        "asset_path": "/portfolio-media/%s" % relative,
        "asset_available": family in _MEDIA_FAMILIES,
        "source_path": relative,
        "relative_path": relative,
        "folder": "/".join(parts[:-1]),
        "subfolders": parts[:-1],
        "status": "inbox",
        "source": {
            "kind": "archive_observer_artifact",
            "archive_id": corpus_id,
            "artifact_ref": str(artifact["artifact_ref"]),
            "physical_id": str(artifact["physical_id"]),
            "content_id": artifact.get("content_id"),
            "sha256": artifact.get("sha256"),
            "root": root,
        },
    }


def inbox_from_observation(
    batch: Mapping[str, Any],
    *,
    root: str | Path,
    corpus_id: str,
    artist_id: str | None = None,
) -> dict[str, Any]:
    """Translate file artifacts while preserving the observer snapshot."""
    if batch.get("schema") != "mak-archive-observation-batch-v1":
        raise ValueError("archive_observation_schema_invalid")
    root = str(Path(root).expanduser().resolve())
    items = [
        _item(artifact, root, corpus_id)
        for artifact in batch.get("artifacts", [])
        if isinstance(artifact, Mapping) and artifact.get("kind") == "file"
    ]
    items.sort(key=lambda item: item["relative_path"])
    return {
        "schema": INBOX_SCHEMA,
        "status": "inbox",
        "total": len(items),
        "available_assets": sum(1 for item in items if item["asset_available"]),
        "items": items,
        "asset_root": root,
        "asset_sync": "explicit_folder_observation",
        "context": _source_context(corpus_id=corpus_id, artist_id=artist_id),
        "observation": {
            "schema": batch["schema"],
            "archive_id": batch["archive_id"],
            "snapshot_id": batch["snapshot_id"],
            "artifact_count": len(batch.get("artifacts", [])),
            "observation_count": len(batch.get("observations", [])),
        },
    }


def observe_portfolio_folder(
    root: str | Path,
    *,
    corpus_id: str | None = None,
    artist_id: str | None = None,
    max_files: int | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Observe one explicit folder and return ``(batch, inbox)``."""
    root = str(Path(root).expanduser().resolve())
    corpus_id = str(corpus_id or default_corpus_id(root)).strip()
    if not corpus_id:
        raise ValueError("corpus_id_empty")
    batch = observe_archive(root, corpus_id, max_files=max_files, follow_symlinks=False)
    inbox = inbox_from_observation(
        batch, root=root, corpus_id=corpus_id,
        artist_id=str(artist_id).strip() if artist_id else None,
    )
    return batch, inbox


__all__ = [
    "INBOX_SCHEMA",
    "SCHEMA",
    "default_corpus_id",
    "inbox_from_observation",
    "observe_portfolio_folder",
]
