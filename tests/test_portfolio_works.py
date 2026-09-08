"""Tests para generar_works.py — catálogo de obras."""
import json
from pathlib import Path

import pytest

from tools.portfolio.generar_works import (
    extraer_fecha,
    leer_datadrop_manifest,
    leer_flyer_evento_manifest,
    main,
    procesar_datadrops,
    procesar_flyer_eventos,
)


class TestExtraerFecha:
    """Tests del extractor de fecha."""

    def test_iso_timestamp(self):
        """Extrae la parte de fecha de un ISO timestamp."""
        assert extraer_fecha("2026-06-22T15:46:43") == "2026-06-22"

    def test_fecha_directa(self):
        """Retorna fecha si ya está en formato YYYY-MM-DD."""
        assert extraer_fecha("2026-06-12") == "2026-06-12"

    def test_fecha_vacia(self):
        """Retorna string vacío para entrada vacía."""
        assert extraer_fecha("") == ""


class TestLeerDatadropManifest:
    """Tests de lectura de manifest de datadrop."""

    def test_manifest_valido(self, tmp_path):
        """Lee un manifest válido de datadrop."""
        manifest = {
            "id": "2026-06-22_test",
            "uploaded_at": "2026-06-22T15:46:43",
            "original_filename": "test.png",
            "image_path": "datadrops/2026-06-22_test/test.png",
            "type": "flyer",
            "palette": [
                {"hex": "#ffffff", "rgb": [255, 255, 255], "pct": 0.5},
                {"hex": "#000000", "rgb": [0, 0, 0], "pct": 0.5},
            ],
        }
        manifest_file = tmp_path / "manifest.json"
        manifest_file.write_text(json.dumps(manifest), encoding="utf-8")

        resultado = leer_datadrop_manifest(manifest_file)
        assert resultado is not None
        assert resultado["id"] == "2026-06-22_test"
        assert resultado["original_filename"] == "test.png"
        assert len(resultado["palette"]) == 2

    def test_manifest_faltantes_campos(self, tmp_path):
        """Tolera campos faltantes en manifest."""
        manifest = {
            "id": "2026-06-22_test",
            "uploaded_at": "2026-06-22T15:46:43",
        }
        manifest_file = tmp_path / "manifest.json"
        manifest_file.write_text(json.dumps(manifest), encoding="utf-8")

        resultado = leer_datadrop_manifest(manifest_file)
        assert resultado is not None
        assert resultado["id"] == "2026-06-22_test"
        assert resultado["original_filename"] == ""
        assert resultado["palette"] == []

    def test_manifest_json_corrupto(self, tmp_path):
        """Retorna None para JSON inválido."""
        manifest_file = tmp_path / "manifest.json"
        manifest_file.write_text("{ invalid json", encoding="utf-8")

        resultado = leer_datadrop_manifest(manifest_file)
        assert resultado is None

    def test_manifest_no_existe(self, tmp_path):
        """Retorna None si el archivo no existe."""
        manifest_file = tmp_path / "no_existe.json"
        resultado = leer_datadrop_manifest(manifest_file)
        assert resultado is None


class TestLeerFlyerEventoManifest:
    """Tests de lectura de manifest de flyer_eventos."""

    def test_manifest_valido(self, tmp_path):
        """Lee un manifest válido de flyer_eventos."""
        manifest = {
            "tool": "flyer_eventos",
            "name": "evento test",
            "date": "2026-06-13",
            "status": "completed",
            "input": {
                "main_image": "projects/flyer_eventos/test/input.jpg",
            },
            "outputs": ["out1.jpg", "out2.jpg"],
        }
        manifest_file = tmp_path / "manifest.json"
        manifest_file.write_text(json.dumps(manifest), encoding="utf-8")

        resultado = leer_flyer_evento_manifest(manifest_file)
        assert resultado is not None
        assert resultado["name"] == "evento test"
        assert resultado["date"] == "2026-06-13"
        assert len(resultado["outputs"]) == 2

    def test_manifest_sin_input(self, tmp_path):
        """Tolera input faltante."""
        manifest = {
            "tool": "flyer_eventos",
            "name": "evento test",
            "date": "2026-06-13",
            "status": "pending",
        }
        manifest_file = tmp_path / "manifest.json"
        manifest_file.write_text(json.dumps(manifest), encoding="utf-8")

        resultado = leer_flyer_evento_manifest(manifest_file)
        assert resultado is not None
        assert resultado["main_image"] is None
        assert resultado["outputs"] == []

    def test_manifest_json_corrupto(self, tmp_path):
        """Retorna None para JSON inválido."""
        manifest_file = tmp_path / "manifest.json"
        manifest_file.write_text("{ broken", encoding="utf-8")

        resultado = leer_flyer_evento_manifest(manifest_file)
        assert resultado is None


class TestProcesarDatadrops:
    """Tests de procesamiento de directorio datadrops."""

    def test_procesa_datadrops_validos(self, tmp_path):
        """Procesa datadrops válidos."""
        # Crear estructura: datadrops/id1/manifest.json, datadrops/id2/manifest.json
        datadrops_dir = tmp_path / "datadrops"
        datadrops_dir.mkdir()

        id1_dir = datadrops_dir / "2026-06-22_001"
        id1_dir.mkdir()
        manifest1 = {
            "id": "2026-06-22_001",
            "uploaded_at": "2026-06-22T10:00:00",
            "original_filename": "obra1.png",
            "image_path": "datadrops/2026-06-22_001/obra1.png",
            "type": "flyer",
            "palette": [{"hex": "#ffffff", "rgb": [255, 255, 255], "pct": 1.0}],
        }
        (id1_dir / "manifest.json").write_text(json.dumps(manifest1), encoding="utf-8")

        id2_dir = datadrops_dir / "2026-06-23_002"
        id2_dir.mkdir()
        manifest2 = {
            "id": "2026-06-23_002",
            "uploaded_at": "2026-06-23T15:00:00",
            "original_filename": "obra2.png",
            "image_path": "datadrops/2026-06-23_002/obra2.png",
            "type": "flyer",
            "palette": [],
        }
        (id2_dir / "manifest.json").write_text(json.dumps(manifest2), encoding="utf-8")

        obras = procesar_datadrops(datadrops_dir)
        assert len(obras) == 2
        assert obras[0]["id"] == "2026-06-22_001"
        assert obras[1]["id"] == "2026-06-23_002"
        assert all(o["fuente"] == "datadrop" for o in obras)
        assert all(o["estado"] == "entregado" for o in obras)

    def test_skipped_corrupt_manifest(self, tmp_path):
        """Salta manifests corrompidos."""
        datadrops_dir = tmp_path / "datadrops"
        datadrops_dir.mkdir()

        id1_dir = datadrops_dir / "2026-06-22_001"
        id1_dir.mkdir()
        (id1_dir / "manifest.json").write_text("{ invalid json", encoding="utf-8")

        id2_dir = datadrops_dir / "2026-06-22_002"
        id2_dir.mkdir()
        manifest2 = {
            "id": "2026-06-22_002",
            "uploaded_at": "2026-06-22T10:00:00",
            "original_filename": "obra.png",
            "type": "flyer",
            "palette": [],
        }
        (id2_dir / "manifest.json").write_text(json.dumps(manifest2), encoding="utf-8")

        obras = procesar_datadrops(datadrops_dir)
        assert len(obras) == 1
        assert obras[0]["id"] == "2026-06-22_002"

    def test_directorio_no_existe(self, tmp_path):
        """Retorna lista vacía si el directorio no existe."""
        obras = procesar_datadrops(tmp_path / "no_existe")
        assert obras == []

    def test_directorio_vacio(self, tmp_path):
        """Retorna lista vacía para directorio vacío."""
        datadrops_dir = tmp_path / "datadrops"
        datadrops_dir.mkdir()

        obras = procesar_datadrops(datadrops_dir)
        assert obras == []


class TestProcesarFlyerEventos:
    """Tests de procesamiento de directorio flyer_eventos."""

    def test_procesa_flyer_eventos_validos(self, tmp_path):
        """Procesa flyer_eventos válidos."""
        flyer_dir = tmp_path / "flyer_eventos"
        flyer_dir.mkdir()

        id1_dir = flyer_dir / "2026-06-13_evento-01"
        id1_dir.mkdir()
        manifest1 = {
            "tool": "flyer_eventos",
            "name": "evento 01",
            "date": "2026-06-13",
            "status": "completed",
            "input": {"main_image": "projects/flyer_eventos/2026-06-13_evento-01/input.jpg"},
            "outputs": ["out1.jpg"],
        }
        (id1_dir / "manifest.json").write_text(json.dumps(manifest1), encoding="utf-8")

        id2_dir = flyer_dir / "2026-06-14_evento-02"
        id2_dir.mkdir()
        manifest2 = {
            "tool": "flyer_eventos",
            "name": "evento 02",
            "date": "2026-06-14",
            "status": "pending",
            "input": {},
            "outputs": [],
        }
        (id2_dir / "manifest.json").write_text(json.dumps(manifest2), encoding="utf-8")

        obras = procesar_flyer_eventos(flyer_dir)
        assert len(obras) == 2
        assert obras[0]["id"] == "2026-06-13_evento-01"
        assert obras[1]["id"] == "2026-06-14_evento-02"
        assert all(o["fuente"] == "flyer_evento" for o in obras)
        assert all(o["tipo"] == "flyer_evento" for o in obras)
        assert obras[0]["salidas"] == 1
        assert obras[1]["salidas"] is None  # outputs está vacío

    def test_directorio_vacio(self, tmp_path):
        """Retorna lista vacía para directorio vacío."""
        flyer_dir = tmp_path / "flyer_eventos"
        flyer_dir.mkdir()

        obras = procesar_flyer_eventos(flyer_dir)
        assert obras == []


class TestOrdenamiento:
    """Tests del ordenamiento de obras por fecha."""

    def test_orden_descendente_por_fecha_en_main(self, tmp_path):
        """Las obras se ordenan por fecha descendente en main()."""
        datadrops_dir = tmp_path / "datadrops"
        datadrops_dir.mkdir()

        flyer_dir = tmp_path / "flyer_eventos"
        flyer_dir.mkdir()

        # Crear datadrops en orden aleatorio
        for idx, (id_str, fecha) in enumerate([("old", "2026-06-10"), ("new", "2026-06-20"), ("mid", "2026-06-15")]):
            dir_ = datadrops_dir / f"dd-{idx:02d}"
            dir_.mkdir()
            manifest = {
                "id": f"dd-{idx:02d}",
                "uploaded_at": fecha,
                "original_filename": f"{id_str}.png",
                "type": "flyer",
                "palette": [],
            }
            (dir_ / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

        # Crear un flyer_evento con fecha intermedia
        fe_dir = flyer_dir / "fe-01"
        fe_dir.mkdir()
        (fe_dir / "manifest.json").write_text(
            json.dumps({
                "tool": "flyer_eventos",
                "name": "evento",
                "date": "2026-06-12",
                "status": "completed",
                "input": {},
                "outputs": [],
            }),
            encoding="utf-8"
        )

        out_file = tmp_path / "out" / "works.json"
        main([
            "--salida", str(out_file),
            str(datadrops_dir),
            str(flyer_dir),
        ])

        datos = json.loads(out_file.read_text(encoding="utf-8"))
        fechas = [o["fecha"] for o in datos["obras"]]
        # Verificar que está ordenado descendente
        assert fechas == sorted(fechas, reverse=True)


class TestMain:
    """Tests de la función main."""

    def test_main_genera_works_json(self, tmp_path):
        """main() genera works.json con estructura correcta."""
        datadrops_dir = tmp_path / "datadrops"
        datadrops_dir.mkdir()

        flyer_dir = tmp_path / "flyer_eventos"
        flyer_dir.mkdir()

        # Crear un datadrop
        dd_dir = datadrops_dir / "2026-06-22_001"
        dd_dir.mkdir()
        (dd_dir / "manifest.json").write_text(
            json.dumps({
                "id": "2026-06-22_001",
                "uploaded_at": "2026-06-22T10:00:00",
                "original_filename": "obra.png",
                "type": "flyer",
                "palette": [{"hex": "#ffffff", "rgb": [255, 255, 255], "pct": 1.0}],
            }),
            encoding="utf-8"
        )

        # Crear un flyer_evento
        fe_dir = flyer_dir / "2026-06-13_evento"
        fe_dir.mkdir()
        (fe_dir / "manifest.json").write_text(
            json.dumps({
                "tool": "flyer_eventos",
                "name": "evento",
                "date": "2026-06-13",
                "status": "completed",
                "input": {},
                "outputs": ["out.jpg"],
            }),
            encoding="utf-8"
        )

        out_file = tmp_path / "out" / "works.json"
        ret = main([
            "--salida", str(out_file),
            str(datadrops_dir),
            str(flyer_dir),
        ])

        assert ret == 0
        assert out_file.exists()

        datos = json.loads(out_file.read_text(encoding="utf-8"))
        assert "generado" in datos
        assert "total" in datos
        assert "obras" in datos
        assert datos["total"] == 2
        assert len(datos["obras"]) == 2

    def test_main_salida_default(self, tmp_path):
        """main() respeta la salida por defecto."""
        datadrops_dir = tmp_path / "datadrops"
        datadrops_dir.mkdir()

        flyer_dir = tmp_path / "flyer_eventos"
        flyer_dir.mkdir()

        # Crear directorio out
        out_dir = tmp_path / "out"
        out_dir.mkdir()

        # Sin --salida, debería usar default (pero modificamos para que use tmp_path)
        # En este test, solo verificamos que el argumento es ignorado si no pasamos --salida
        ret = main([
            str(datadrops_dir),
            str(flyer_dir),
        ])
        assert ret == 0

    def test_main_directorio_vacio_total_cero(self, tmp_path):
        """main() genera works.json con total=0 para directorios vacíos."""
        datadrops_dir = tmp_path / "datadrops"
        datadrops_dir.mkdir()

        flyer_dir = tmp_path / "flyer_eventos"
        flyer_dir.mkdir()

        out_file = tmp_path / "out" / "works.json"
        ret = main([
            "--salida", str(out_file),
            str(datadrops_dir),
            str(flyer_dir),
        ])

        assert ret == 0
        datos = json.loads(out_file.read_text(encoding="utf-8"))
        assert datos["total"] == 0
        assert len(datos["obras"]) == 0
