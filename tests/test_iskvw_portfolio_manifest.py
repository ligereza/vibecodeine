"""The visual portfolio has one complete, deterministic input for every skin."""

import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import gen_archivo_iskvw as G

ROOT = Path(__file__).resolve().parents[1]


def _piece(pid, **extra):
    return {"id": pid, "titulo": "", "clase": "obra", **extra}


def test_manifest_orders_measured_pieces_and_keeps_unmeasured_ones():
    archive_data = {
        "piezas": [
            _piece("sin-z"),
            _piece("medida-b", posicion={"x": 2, "y": 5}),
            _piece("medida-a", posicion={"x": 9, "y": 1}),
            _piece("sin-a"),
        ],
        "vinculos": [],
    }
    raw = b"archivo estable para la prueba"

    manifest = G.construir_portafolio(
        archive_data, source_path="iskvw/datos/archivo.json", source_bytes=raw
    )

    assert manifest["schema"] == "iskvw-portfolio-manifest-v1"
    assert manifest["order"] == ["medida-a", "medida-b", "sin-a", "sin-z"]
    assert manifest["selection"] == {"mode": "all_source_pieces", "omitted_count": 0}
    assert manifest["ordering"] == {
        "algorithm": "measured_position_yx_then_stable_id",
        "positioned_count": 2,
        "unpositioned_count": 2,
    }
    assert manifest["source"]["sha256"] == hashlib.sha256(raw).hexdigest()
    assert {skin["id"]: skin["scope"] for skin in manifest["skins"]} == {
        "campo": "portfolio", "terminal": "portfolio"
    }


def test_main_writes_archive_and_its_companion_manifest(tmp_path, monkeypatch):
    output_file = tmp_path / "archivo.json"
    position_file = tmp_path / "campo-no-existe.json"
    monkeypatch.setattr(G, "desde_obras", lambda: {
        "piezas": [_piece("obra-b"), _piece("obra-a")], "vinculos": []
    })
    monkeypatch.setattr(G, "del_campo", lambda _ruta: ({}, None))
    monkeypatch.setattr(sys, "argv", [
        "gen", "--fuente", "obras", "--salida", str(output_file),
        "--posiciones", str(position_file),
    ])

    assert G.main() == 0

    manifest_path = tmp_path / "portafolio.json"
    assert manifest_path.is_file()
    archive_bytes = output_file.read_bytes()
    archive_data = json.loads(archive_bytes)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["source"]["piece_count"] == len(archive_data["piezas"])
    assert manifest["source"]["sha256"] == hashlib.sha256(archive_bytes).hexdigest()
    assert manifest["order"] == ["obra-a", "obra-b"]
    assert manifest["selection"]["omitted_count"] == 0


def test_all_visual_views_use_the_shared_skin_runtime():
    runtime = ROOT / "iskvw" / "piel" / "lib" / "skin_runtime.js"
    assert runtime.is_file()
    source = runtime.read_text(encoding="utf-8")
    for skin in ("campo", "terminal"):
        html = (ROOT / "iskvw" / "piel" / skin / "index.html").read_text(
            encoding="utf-8"
        )
        assert f'<body data-skin="{skin}">' in html
        assert '<script src="../lib/skin_runtime.js"></script>' in html
    assert 'schema === "iskvw-portfolio-manifest-v1"' in source
    for symbol in ("loadPortfolio", "rutaDePiel", "installSkinSwitcher",
                   "registryFromManifest(manifest.skins)",
                   "loc.hash", "loc.search"):
        assert symbol in source
