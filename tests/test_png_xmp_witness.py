from __future__ import annotations

import struct
import zlib
from pathlib import Path

from tools.png_xmp_witness import PNG_MAGIC, PNG_XMP_KEYWORD, run


def chunk(kind: bytes, data: bytes) -> bytes:
    return (struct.pack(">I", len(data)) + kind + data
            + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF))


def write_png(path: Path, *, outside: bytes = b"", corrupt_crc: bool = False,
              text_kind: bytes = b"iTXt") -> Path:
    packet = b"<?xpacket begin='x'?>" + b"<x:xmpmeta><xmpMM:DocumentID>doc</xmpMM:DocumentID></x:xmpmeta>"
    itxt = PNG_XMP_KEYWORD + b"\x00\x00\x00\x00\x00" + packet
    body = chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0))
    body += chunk(text_kind, itxt if text_kind == b"iTXt"
                  else PNG_XMP_KEYWORD + b"\x00" + packet)
    body += chunk(b"IDAT", b"\x78\x9c\x63\x00\x00\x00\x02\x00\x01")
    end = chunk(b"IEND", b"")
    if corrupt_crc:
        end = end[:-1] + bytes([end[-1] ^ 1])
    path.write_bytes(PNG_MAGIC + body + end + outside)
    return path


def test_witness_ignores_packet_inside_declared_xmp_container(tmp_path):
    write_png(tmp_path / "inside.png")
    report = run(tmp_path, argv=["test"])
    assert report["candidate_count"] == 1
    assert report["files_checked"] == 1
    assert report["xmp_container_count"] == 1
    assert report["outside_marker_file_count"] == 0
    assert report["eligible_for_witness"]


def test_witness_also_accepts_legacy_text_xmp_container(tmp_path):
    write_png(tmp_path / "legacy.png", text_kind=b"tEXt")
    report = run(tmp_path, argv=["test"])
    assert report["xmp_container_count"] == 1
    assert report["outside_marker_file_count"] == 0
    assert report["eligible_for_witness"]


def test_witness_rejects_raw_packet_marker_outside_xmp_container(tmp_path):
    write_png(tmp_path / "outside.png", outside=b"<?xpacket begin='outside'?>")
    report = run(tmp_path, argv=["test"])
    assert report["outside_marker_file_count"] == 1
    assert report["outside_marker_hits"][0]["markers"] == ["<?xpacket"]
    assert not report["eligible_for_witness"]


def test_witness_rejects_bad_crc(tmp_path):
    write_png(tmp_path / "bad.png", corrupt_crc=True)
    report = run(tmp_path, argv=["test"])
    assert report["error_count"] == 1
    assert "crc_mismatch" in report["errors"][0]["error"]
    assert not report["eligible_for_witness"]
