"""Synthetic fixture writer used by tests; no production data is involved."""

from __future__ import annotations

import json
from pathlib import Path


ARCHIVE_ID = "artist-001"


def write_synthetic_fixture(root: str | Path) -> Path:
    """Create the clean C01 public-side fixture under *root* and return it."""

    root_path = Path(root)
    (root_path / "public").mkdir(parents=True, exist_ok=True)
    (root_path / "deliverables").mkdir(parents=True, exist_ok=True)

    payloads = {
        "exp-post-exact.bin": b"C01|post|exact|payload|v1",
        "exp-reel-reencoded.bin": b"C01|reel|public|codec=h264|frame-data",
        "exp-story-unanchored.bin": b"C01|story|public-only",
        "exp-carousel-a.bin": b"C01|carousel|slide-a|payload",
        "exp-carousel-b.bin": b"C01|carousel|slide-b|payload",
        "del-post-exact.bin": b"C01|post|exact|payload|v1",
        "del-reel-reencoded.bin": b"C01|reel|local|codec=h265|frame-data",
        "del-carousel-a.bin": b"C01|carousel|slide-a|payload",
        "del-carousel-b.bin": b"C01|carousel|slide-b|payload",
        "del-local-only.bin": b"C01|local-only|no-public-item",
    }
    for filename, payload in payloads.items():
        destination = root_path / ("public" if filename.startswith("exp-") else "deliverables") / filename
        destination.write_bytes(payload)

    image_1080 = {"width": 1080, "height": 1080, "mime": "image/png"}
    video_1080 = {"width": 1080, "height": 1920, "duration_ms": 15000, "mime": "video/mp4"}
    image_story = {"width": 1080, "height": 1920, "mime": "image/jpeg"}
    image_1200 = {"width": 1200, "height": 1200, "mime": "image/png"}
    manifest = {
        "schema": "mak-cycle-c01-public-fixture-v1",
        "archive_id": ARCHIVE_ID,
        "publications": [
            {
                "id": "pub-post-exact",
                "type": "post",
                "media_ids": ["media-post-exact"],
                "activity_id": "activity-post-exact",
            },
            {
                "id": "pub-reel-reencoded",
                "type": "reel",
                "media_ids": ["media-reel-reencoded"],
                "activity_id": "activity-reel-reencoded",
            },
            {
                "id": "pub-story-no-source",
                "type": "story",
                "media_ids": ["media-story-unanchored"],
            },
            {
                "id": "pub-carousel",
                "type": "carousel",
                "media_ids": ["media-carousel-a", "media-carousel-b"],
                "activity_id": "activity-carousel",
            },
        ],
        "exported_media": [
            {
                "id": "media-post-exact",
                "publication_id": "pub-post-exact",
                "archive_id": ARCHIVE_ID,
                "file": "public/exp-post-exact.bin",
                "media_kind": "image",
                "technical": image_1080,
                "embedding": [1.0, 0.0, 0.0],
            },
            {
                "id": "media-reel-reencoded",
                "publication_id": "pub-reel-reencoded",
                "archive_id": ARCHIVE_ID,
                "file": "public/exp-reel-reencoded.bin",
                "media_kind": "video",
                "technical": video_1080,
                "embedding": [0.0, 1.0, 0.0],
            },
            {
                "id": "media-story-unanchored",
                "publication_id": "pub-story-no-source",
                "archive_id": ARCHIVE_ID,
                "file": "public/exp-story-unanchored.bin",
                "media_kind": "image",
                "technical": image_story,
                "embedding": [0.0, 0.0, 1.0],
            },
            {
                "id": "media-carousel-a",
                "publication_id": "pub-carousel",
                "archive_id": ARCHIVE_ID,
                "file": "public/exp-carousel-a.bin",
                "media_kind": "image",
                "technical": image_1200,
                "embedding": [0.7, 0.7, 0.0],
            },
            {
                "id": "media-carousel-b",
                "publication_id": "pub-carousel",
                "archive_id": ARCHIVE_ID,
                "file": "public/exp-carousel-b.bin",
                "media_kind": "image",
                "technical": image_1200,
                "embedding": [0.7, 0.6, 0.0],
            },
        ],
        "deliverables": [
            {
                "id": "del-post-exact",
                "archive_id": ARCHIVE_ID,
                "file": "deliverables/del-post-exact.bin",
                "media_kind": "image",
                "technical": image_1080,
                "activity_id": "activity-post-exact",
                "embedding": [1.0, 0.0, 0.0],
            },
            {
                "id": "del-reel-reencoded",
                "archive_id": ARCHIVE_ID,
                "file": "deliverables/del-reel-reencoded.bin",
                "media_kind": "video",
                "technical": {**video_1080, "mime": "video/webm"},
                "activity_id": "activity-reel-reencoded",
                "embedding": [0.0, 0.98, 0.1],
            },
            {
                "id": "del-carousel-a",
                "archive_id": ARCHIVE_ID,
                "file": "deliverables/del-carousel-a.bin",
                "media_kind": "image",
                "technical": image_1200,
                "activity_id": "activity-carousel",
                "embedding": [0.7, 0.7, 0.0],
            },
            {
                "id": "del-carousel-b",
                "archive_id": ARCHIVE_ID,
                "file": "deliverables/del-carousel-b.bin",
                "media_kind": "image",
                "technical": image_1200,
                "activity_id": "activity-carousel",
                "embedding": [0.7, 0.6, 0.0],
            },
            {
                "id": "del-local-only",
                "archive_id": ARCHIVE_ID,
                "file": "deliverables/del-local-only.bin",
                "media_kind": "image",
                "technical": {"width": 800, "height": 800, "mime": "image/png"},
                "embedding": [0.2, 0.2, 0.9],
            },
        ],
        "activities": [
            {
                "id": "activity-post-exact",
                "publication_id": "pub-post-exact",
                "deliverable_ids": ["del-post-exact"],
            },
            {
                "id": "activity-reel-reencoded",
                "publication_id": "pub-reel-reencoded",
                "deliverable_ids": ["del-reel-reencoded"],
            },
            {
                "id": "activity-carousel",
                "publication_id": "pub-carousel",
                "deliverable_ids": ["del-carousel-a", "del-carousel-b"],
            },
        ],
    }
    (root_path / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return root_path
