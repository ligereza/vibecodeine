"""Tests para empaquetar_assets.py — empaquetado de imágenes de works.json."""
import json
from pathlib import Path

from tools.portfolio.empaquetar_assets import empaquetar, main


def _escribir_works(tmp_path: Path, obras: list[dict]) -> Path:
    works_path = tmp_path / "out" / "works.json"
    works_path.parent.mkdir(parents=True, exist_ok=True)
    datos = {"generado": "2026-07-18", "total": len(obras), "obras": obras}
    works_path.write_text(json.dumps(datos, ensure_ascii=False, indent=2), encoding="utf-8")
    return works_path


def _crear_imagen(ruta: Path, contenido: bytes = b"fake-png-bytes") -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_bytes(contenido)


class TestEmpaquetarHappyPath:
    """Copia + reescritura cuando la imagen existe."""

    def test_copia_y_reescribe_imagen(self, tmp_path):
        img_real = tmp_path / "datadrops" / "obra1" / "foto.png"
        _crear_imagen(img_real, b"contenido-real-1")

        works_path = _escribir_works(tmp_path, [
            {
                "id": "obra1",
                "fuente": "datadrop",
                "titulo": "Obra 1",
                "fecha": "2026-06-22",
                "tipo": "flyer",
                "estado": "entregado",
                "imagen": str(img_real),
                "paleta": [],
                "salidas": None,
            }
        ])
        assets_dir = tmp_path / "out" / "assets" / "flujo-works"

        datos = empaquetar(works_path, assets_dir, repo_root=tmp_path)

        obra = datos["obras"][0]
        assert obra["imagen"] == "assets/flujo-works/obra1.png"
        assert (assets_dir / "obra1.png").is_file()
        assert (assets_dir / "obra1.png").read_bytes() == b"contenido-real-1"

        # También se escribió de vuelta en works_path
        releido = json.loads(works_path.read_text(encoding="utf-8"))
        assert releido["obras"][0]["imagen"] == "assets/flujo-works/obra1.png"

    def test_preserva_extension_original(self, tmp_path):
        img_real = tmp_path / "datadrops" / "obra2" / "grafico.jpg"
        _crear_imagen(img_real)

        works_path = _escribir_works(tmp_path, [
            {"id": "obra2", "fuente": "datadrop", "titulo": "t", "fecha": "2026-06-20",
             "tipo": "flyer", "estado": "entregado", "imagen": str(img_real),
             "paleta": [], "salidas": None}
        ])
        assets_dir = tmp_path / "out" / "assets" / "flujo-works"

        datos = empaquetar(works_path, assets_dir, repo_root=tmp_path)
        assert datos["obras"][0]["imagen"] == "assets/flujo-works/obra2.jpg"
        assert (assets_dir / "obra2.jpg").is_file()


class TestEmpaquetarImagenFaltante:
    """Cuando imagen apunta a un archivo que no existe."""

    def test_imagen_inexistente_pasa_a_null(self, tmp_path):
        works_path = _escribir_works(tmp_path, [
            {"id": "obra3", "fuente": "flyer_evento", "titulo": "t", "fecha": "2026-06-12",
             "tipo": "flyer_evento", "estado": "pending",
             "imagen": "projects/flyer_eventos/2026-06-12_evento-prueba/input/input_ig.jpg",
             "paleta": [], "salidas": None}
        ])
        assets_dir = tmp_path / "out" / "assets" / "flujo-works"

        datos = empaquetar(works_path, assets_dir, repo_root=tmp_path)

        assert datos["obras"][0]["imagen"] is None
        assert list(assets_dir.glob("obra3*")) == []

    def test_no_crashea_sin_archivo(self, tmp_path):
        works_path = _escribir_works(tmp_path, [
            {"id": "obraX", "fuente": "datadrop", "titulo": "t", "fecha": "2026-01-01",
             "tipo": "flyer", "estado": "entregado", "imagen": "no/existe/nunca.png",
             "paleta": [], "salidas": None}
        ])
        assets_dir = tmp_path / "out" / "assets" / "flujo-works"

        ret = main(["--works", str(works_path), "--assets", str(assets_dir)])
        assert ret == 0
        releido = json.loads(works_path.read_text(encoding="utf-8"))
        assert releido["obras"][0]["imagen"] is None


class TestEmpaquetarSinImagen:
    """Obra sin imagen (null) queda intacta."""

    def test_obra_sin_imagen_no_se_toca(self, tmp_path):
        works_path = _escribir_works(tmp_path, [
            {"id": "obra4", "fuente": "datadrop", "titulo": "t", "fecha": "2026-05-01",
             "tipo": "flyer", "estado": "entregado", "imagen": None,
             "paleta": [], "salidas": None}
        ])
        assets_dir = tmp_path / "out" / "assets" / "flujo-works"

        datos = empaquetar(works_path, assets_dir, repo_root=tmp_path)
        assert datos["obras"][0]["imagen"] is None
        assert list(assets_dir.iterdir()) == []


class TestDeterminismo:
    """Correr dos veces sobre el mismo works.json original produce resultado idéntico."""

    def test_dos_corridas_identicas(self, tmp_path):
        img_a = tmp_path / "datadrops" / "obraA" / "a.png"
        img_b = tmp_path / "datadrops" / "obraB" / "b.jpg"
        _crear_imagen(img_a, b"AAAA")
        _crear_imagen(img_b, b"BBBB")

        obras_originales = [
            {"id": "obraA", "fuente": "datadrop", "titulo": "a", "fecha": "2026-06-22",
             "tipo": "flyer", "estado": "entregado", "imagen": str(img_a),
             "paleta": [], "salidas": None},
            {"id": "obraB", "fuente": "datadrop", "titulo": "b", "fecha": "2026-06-21",
             "tipo": "flyer", "estado": "entregado", "imagen": str(img_b),
             "paleta": [], "salidas": None},
            {"id": "obraC", "fuente": "datadrop", "titulo": "c", "fecha": "2026-06-20",
             "tipo": "flyer", "estado": "entregado", "imagen": "no/existe.png",
             "paleta": [], "salidas": None},
        ]

        # Corrida 1
        works_1 = _escribir_works(tmp_path / "run1", obras_originales)
        assets_1 = tmp_path / "run1" / "out" / "assets" / "flujo-works"
        datos_1 = empaquetar(works_1, assets_1, repo_root=tmp_path)

        # Corrida 2 (desde una copia fresca del works.json original)
        works_2 = _escribir_works(tmp_path / "run2", obras_originales)
        assets_2 = tmp_path / "run2" / "out" / "assets" / "flujo-works"
        datos_2 = empaquetar(works_2, assets_2, repo_root=tmp_path)

        assert datos_1 == datos_2

        archivos_1 = sorted(p.name for p in assets_1.iterdir())
        archivos_2 = sorted(p.name for p in assets_2.iterdir())
        assert archivos_1 == archivos_2 == ["obraA.png", "obraB.jpg"]


class TestMainCLI:
    """Tests del entrypoint CLI."""

    def test_main_ok(self, tmp_path):
        img_real = tmp_path / "datadrops" / "obra9" / "foto.png"
        _crear_imagen(img_real)

        works_path = _escribir_works(tmp_path, [
            {"id": "obra9", "fuente": "datadrop", "titulo": "t", "fecha": "2026-06-22",
             "tipo": "flyer", "estado": "entregado", "imagen": str(img_real),
             "paleta": [], "salidas": None}
        ])
        assets_dir = tmp_path / "out" / "assets" / "flujo-works"

        ret = main(["--works", str(works_path), "--assets", str(assets_dir)])
        assert ret == 0
        assert (assets_dir / "obra9.png").is_file()

    def test_main_works_no_existe(self, tmp_path):
        works_path = tmp_path / "out" / "no_existe.json"
        assets_dir = tmp_path / "out" / "assets" / "flujo-works"

        ret = main(["--works", str(works_path), "--assets", str(assets_dir)])
        assert ret == 1
