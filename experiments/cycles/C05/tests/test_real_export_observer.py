from __future__ import annotations

import json
import os
import struct
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from real_export_observer import build_observation


def write_glb(path: Path, names: list[str]) -> None:
    document = {
        "asset": {"version": "2.0", "generator": "Khronos glTF Blender I/O v4.5.49"},
        "scene": 0,
        "scenes": [{"name": "Scene", "nodes": list(range(len(names)))}],
        "nodes": [{"name": name, "mesh": index} for index, name in enumerate(names)],
        "meshes": [{"name": name, "primitives": []} for name in names],
    }
    payload = json.dumps(document, separators=(",", ":")).encode("utf-8")
    payload += b" " * ((4 - len(payload) % 4) % 4)
    data = struct.pack("<4sII", b"glTF", 2, 12 + 8 + len(payload))
    data += struct.pack("<II", len(payload), 0x4E4F534A) + payload
    path.write_bytes(data)


def make_case(directory: Path, *, output_names: list[str] | None = None, marker: str | None = None):
    source = directory / "RAYU.blend"
    source.write_bytes(b"source")
    source_hash = __import__("hashlib").sha256(source.read_bytes()).hexdigest()
    snapshot = directory / "snapshot.json"
    snapshot.write_text(json.dumps({
        "integrity": {"sha256_before": source_hash},
        "snapshot": {"native": {"scenes": [{"objects": [{"name": "Recurso 2"}, {"name": "Recurso 3"}]}]}},
    }), encoding="utf-8")
    script = directory / "rayu_export.py"
    script.write_text('names=["Recurso 2","Recurso 3"]\nOUT=r"C:\\ARICA\\rayu_resources.glb"\n', encoding="utf-8")
    marker_path = directory / "rayu_export_done.txt"
    marker_path.write_text(marker or "OK exported=['Recurso 2', 'Recurso 3'] -> C:\\ARICA\\rayu_resources.glb", encoding="utf-8")
    output = directory / "rayu_resources.glb"
    write_glb(output, output_names or ["Recurso 2", "Recurso 3"])
    base = 1_700_000_000
    os.utime(source, (base, base))
    os.utime(snapshot, (base, base))
    os.utime(script, (base + 10, base + 10))
    os.utime(marker_path, (base + 20, base + 20))
    os.utime(output, (base + 20, base + 20))
    return source, snapshot, script, marker_path, output


class RealExportObserverTests(unittest.TestCase):
    def test_real_shape_is_supported_when_all_witness_parts_bind(self):
        with tempfile.TemporaryDirectory() as temporary:
            paths = make_case(Path(temporary))
            result = build_observation(
                source_blend=paths[0], source_snapshot=paths[1], export_script=paths[2], marker=paths[3], output_glb=paths[4]
            )
            self.assertEqual(result["witness"]["status"], "supported")
            self.assertEqual(result["witness"]["event_type"], "export")

    def test_output_name_mismatch_abstains(self):
        with tempfile.TemporaryDirectory() as temporary:
            paths = make_case(Path(temporary), output_names=["Other"])
            result = build_observation(
                source_blend=paths[0], source_snapshot=paths[1], export_script=paths[2], marker=paths[3], output_glb=paths[4]
            )
            self.assertEqual(result["witness"]["status"], "unknown")
            self.assertEqual(result["witness"]["checks"]["output_contains_exported_objects"]["status"], "fail")

    def test_failed_marker_abstains_even_when_glb_is_structurally_valid(self):
        with tempfile.TemporaryDirectory() as temporary:
            paths = make_case(Path(temporary), marker="ERR export failed")
            result = build_observation(
                source_blend=paths[0], source_snapshot=paths[1], export_script=paths[2], marker=paths[3], output_glb=paths[4]
            )
            self.assertEqual(result["witness"]["status"], "unknown")
            self.assertEqual(result["witness"]["checks"]["script_and_marker_agree"]["status"], "fail")


if __name__ == "__main__":
    unittest.main()
