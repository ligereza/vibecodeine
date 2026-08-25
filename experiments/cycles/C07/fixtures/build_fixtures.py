"""Create tiny deterministic fixture trees in a caller-owned temporary root."""

from __future__ import annotations

import struct
import zlib
from pathlib import Path
from typing import Iterable

try:
    from PIL import Image
except ImportError:  # pragma: no cover
    Image = None


def _png_stdlib(path: Path, width: int, height: int, rgba: tuple[int, int, int, int]) -> None:
    raw = b"".join(b"\x00" + bytes(rgba) * width for _ in range(height))
    def chunk(name: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + name + data + struct.pack(">I", zlib.crc32(name + data) & 0xFFFFFFFF)
    path.write_bytes(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b""))


def _png(path: Path, size: tuple[int, int], color: tuple[int, int, int, int]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if Image is not None:
        mode = "RGB" if path.suffix.lower() in {".jpg", ".jpeg"} else "RGBA"
        pixel = color[:3] if mode == "RGB" else color
        Image.new(mode, size, pixel).save(path)
    else:
        _png_stdlib(path, size[0], size[1], color)


def create_case(case_id: str, root: str | Path) -> list[Path]:
    root = Path(root)
    files: list[Path] = []
    if case_id == "frames_plus_export":
        for number in (1, 2):
            path = root / "aurora" / f"aurora_frame_{number:04d}.png"
            _png(path, (80, 40), (20 * number, 100, 180, 255))
            files.append(path)
        export = root / "aurora" / "aurora_export.png"
        _png(export, (160, 80), (40, 120, 180, 255))
        files.append(export)
        project = root / "aurora" / "aurora_project.blend"
        project.write_bytes(b"BLENDER C07 fixture; no Blender execution")
        files.append(project)
        xmp = root / "aurora" / "aurora_export.xmp"
        xmp.write_text("<x:xmpmeta xmlns:x='adobe:ns:meta/'><rdf:RDF xmlns:rdf='rdf'><rdf:Description dc:identifier='aurora-01' xmlns:dc='dc'/></rdf:RDF></x:xmpmeta>", encoding="utf-8")
        files.append(xmp)
        post = root / "published" / "aurora_public_post.jpg"
        _png(post, (160, 80), (40, 120, 180, 255))
        files.append(post)
    elif case_id == "export_without_project":
        path = root / "orphan" / "export_only.png"
        _png(path, (100, 100), (200, 80, 40, 255))
        files.append(path)
    elif case_id == "project_without_export":
        path = root / "unexported" / "installation_project.blend"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"BLENDER C07 project-only fixture")
        files.append(path)
    elif case_id == "same_name_different_work":
        for name, color in (("red", (220, 20, 40, 255)), ("blue", (20, 40, 220, 255))):
            path = root / name / "final.png"
            _png(path, (90, 90), color)
            files.append(path)
    elif case_id == "same_work_different_proportions":
        for suffix, size in (("4x5", (80, 100)), ("16x9", (160, 90))):
            path = root / "study" / f"study_{suffix}.png"
            _png(path, size, (80, 140, 100, 255))
            files.append(path)
    else:
        raise ValueError(f"unknown fixture case: {case_id}")
    return files


def create_all(root: str | Path) -> list[Path]:
    cases = ("frames_plus_export", "export_without_project", "project_without_export", "same_name_different_work", "same_work_different_proportions")
    files: list[Path] = []
    for case in cases:
        files.extend(create_case(case, Path(root) / case))
    return files
