"""Audit the known local social-export candidate without extracting it."""

from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from pathlib import Path


KNOWN_ZIP = Path(
    "/media/mak/PortableSSD/descargas hasta RDFLYER 2050/"
    "instagram-iskvw-2025-04-08-jyAjQO7Z.zip"
)
SCHEMA = "mak-cycle-c03-public-input-audit-v1"
MEDIA_SUFFIXES = {".jpg", ".jpeg", ".png", ".gif", ".mp4", ".mov", ".webm"}
PUBLIC_MARKERS = ("post", "reel", "story", "stories", "media")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def audit(path: str | Path = KNOWN_ZIP) -> dict:
    target = Path(path).expanduser().resolve()
    if not target.is_file():
        return {
            "schema": SCHEMA,
            "catalog_status": "unavailable",
            "public_join": "unknown",
            "input": {"path": str(target), "exists": False},
            "reason": "known_candidate_zip_missing",
        }
    with zipfile.ZipFile(target) as archive:
        members = [info.filename for info in archive.infolist() if not info.is_dir()]
    media_members = [
        name for name in members
        if Path(name).suffix.lower() in MEDIA_SUFFIXES
        and Path(name).name.lower() not in {"instagram-logo.png"}
    ]
    public_named_members = [
        name for name in members
        if any(marker in name.lower() for marker in PUBLIC_MARKERS)
        and "followers_and_following" not in name.lower()
    ]
    return {
        "schema": SCHEMA,
        "catalog_status": "available" if public_named_members and media_members else "unavailable",
        "public_join": "unknown",
        "input": {
            "path": str(target),
            "exists": True,
            "sha256": sha256(target),
            "read_method": "zip_directory_listing_only",
            "extracted": False,
        },
        "archive": {
            "member_count": len(members),
            "members": members,
            "media_members_excluding_brand_logo": media_members,
            "public_named_members_outside_connections": public_named_members,
        },
        "reason": (
            "no_posts_reels_stories_or_media_exported"
            if not public_named_members or not media_members
            else "public_named_members_and_media_present"
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=KNOWN_ZIP)
    parser.add_argument("--output", type=Path, default=Path(__file__).parent / "real_input_status.json")
    args = parser.parse_args()
    payload = audit(args.input)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "schema": SCHEMA,
        "catalog_status": payload["catalog_status"],
        "public_join": payload["public_join"],
        "member_count": payload.get("archive", {}).get("member_count"),
        "output": str(args.output),
    }, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
