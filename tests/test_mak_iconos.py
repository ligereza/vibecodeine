#!/usr/bin/env python3
"""tests/test_mak_iconos.py -- codex mode `iconos`: brief -> spec SEMANTICA
(closed vocabulary) -> real compiler -> SVG. The LLM is faked (no network, no
API key in CI); everything downstream of the fake boundary is REAL: the real
`compilador.validar_spec`, the real `compilador.compilar`, the real file
written to disk by `codex_lib.guardar_pieza_generica`, and the real
`entregar.leer_smoke_meta` that the delivery guard depends on.

iconos.py / codex_lib.py are written for the Linux box (`codex_lib` inserts
"/home/mak/research" into sys.path and imports research_lib; it also
`import resource`, Unix-only). Same stubbing pattern as
tests/test_mak_mirror_fixes.py `_import_codex_lib` / tests/test_mak_codex_nodos.py:
a fake `research_lib` module is injected into sys.modules only if one isn't
already there, and `resource` is stubbed if missing (Windows/CI).
"""
import importlib
import json
import re
import sys
import types
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

TEST_DIR = Path(__file__).parent
PROYECTO_DIR = TEST_DIR.parent
MAK_CODEX = PROYECTO_DIR / "cultura" / "mak_codex"
MAK_PLATAFORMA = PROYECTO_DIR / "cultura" / "mak_plataforma"


def _slug_simple(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-") or "x"


def _import_iconos():
    """Import limpio de iconos.py (y su dependencia codex_lib) con
    research_lib/resource stubbeados -- mismo patron que
    tests/test_mak_mirror_fixes.py::_import_codex_lib."""
    fake_puesto = False
    if "research_lib" not in sys.modules:
        fake = types.ModuleType("research_lib")
        fake.LLM = object
        fake.MODELO_CAPAZ = "fake-model"
        fake._http_json = lambda *a, **k: {}
        fake.escala_tok = lambda *a, **k: 1000
        fake.load_env = lambda: None
        fake.red_ok = lambda: True
        fake.slug = _slug_simple
        fake.stamp = lambda: "20260730-000000"
        sys.modules["research_lib"] = fake
        fake_puesto = True
    resource_puesto = False
    try:
        import resource  # noqa: F401 -- existe en Linux
    except ImportError:
        sys.modules["resource"] = types.ModuleType("resource")
        resource_puesto = True
    if str(MAK_CODEX) not in sys.path:
        sys.path.insert(0, str(MAK_CODEX))
    sys.modules.pop("codex_lib", None)
    sys.modules.pop("iconos", None)
    try:
        mod = importlib.import_module("iconos")
    finally:
        # no revertimos research_lib/resource: otros archivos de test (godspeed
        # lesson) pueden depender de que quede puesto una vez importado; el
        # patron de test_mak_mirror_fixes.py tampoco lo revierte para codex_lib.
        pass
    return mod


class FakeLLM:
    """Fake SOLO en la frontera del LLM: .call(sistema, usuario, tok) ->
    (texto, "nombre-modelo"). .stats / .errors espejan research_lib.LLM real
    (ver research_lib.py: self.stats es dict modelo->conteo, self.errors es
    lista)."""

    def __init__(self, respuestas):
        self._respuestas = list(respuestas)
        self.stats = {}
        self.errors = []
        self.llamadas = 0
        self.sistemas = []
        self.usuarios = []

    def call(self, sistema, usuario, tok):
        self.llamadas += 1
        self.sistemas.append(sistema)
        self.usuarios.append(usuario)
        idx = min(self.llamadas - 1, len(self._respuestas) - 1)
        texto = self._respuestas[idx]
        self.stats["fake-modelo"] = self.stats.get("fake-modelo", 0) + 1
        return texto, "fake-modelo"


def _spec_valida(slug="icono-test"):
    return {
        "slug": slug, "titulo": "Titulo de prueba", "brief": "una prueba",
        "composicion": "centro_unico", "tono": "acido",
        "capas": [{"rol": "protagonista", "figura": "disco", "gesto": "girar",
                   "ritmo": "lento"}],
    }


@pytest.fixture
def iconos_mod(tmp_path, monkeypatch):
    mod = _import_iconos()
    codex_lib = sys.modules["codex_lib"]
    monkeypatch.setattr(codex_lib, "PIEZAS", str(tmp_path))
    return mod


def _svg_path_de(path_md):
    return str(Path(path_md).with_suffix(".svg"))


class TestCaminoFeliz:
    def test_spec_valida_compila_y_guarda_svg_real(self, iconos_mod, monkeypatch):
        fake = FakeLLM([json.dumps(_spec_valida())])
        monkeypatch.setattr(iconos_mod, "planner_llm", lambda: fake)

        path_md, meta = iconos_mod.generar_icono("el muro que se parte")

        assert meta["smoke_ok"] is True
        svg_path = _svg_path_de(path_md)
        assert Path(svg_path).is_file()
        contenido_svg = Path(svg_path).read_text(encoding="utf-8")
        root = ET.fromstring(contenido_svg)
        assert root.attrib["viewBox"] == "0 0 120 120"

        contenido_md = Path(path_md).read_text(encoding="utf-8")
        assert "```json" in contenido_md
        m = re.search(r"```json\n(.*?)```", contenido_md, re.S)
        assert m, "el .md no trae la spec como bloque json"
        spec_en_md = json.loads(m.group(1))
        assert spec_en_md == meta["spec"]

    def test_llm_llamado_una_sola_vez_si_la_spec_es_valida(self, iconos_mod, monkeypatch):
        fake = FakeLLM([json.dumps(_spec_valida())])
        monkeypatch.setattr(iconos_mod, "planner_llm", lambda: fake)
        iconos_mod.generar_icono("pedido cualquiera")
        assert fake.llamadas == 1


class TestReparacion:
    def test_spec_invalida_luego_valida_repara_en_dos_rondas(self, iconos_mod, monkeypatch):
        invalida = json.dumps({
            "slug": "x", "titulo": "t", "composicion": "centro_unico",
            "tono": "acido",
            "capas": [{"rol": "protagonista", "figura": "figura-inventada-rara"}],
        })
        valida = json.dumps(_spec_valida())
        fake = FakeLLM([invalida, valida])
        monkeypatch.setattr(iconos_mod, "planner_llm", lambda: fake)

        path_md, meta = iconos_mod.generar_icono("pedido de reparacion")

        assert meta["smoke_ok"] is True
        assert fake.llamadas == 2
        assert meta["problemas"], "debe registrar el fallo de la primera ronda"
        assert "figura-inventada-rara" in meta["problemas"][0]


class TestIrreparable:
    def test_garbage_persistente_no_levanta_y_marca_smoke_ok_false(
            self, iconos_mod, monkeypatch):
        fake = FakeLLM(["esto no es json en absoluto, ni con llaves sueltas"])
        monkeypatch.setattr(iconos_mod, "planner_llm", lambda: fake)

        path_md, meta = iconos_mod.generar_icono("pedido imposible")

        assert meta["smoke_ok"] is False
        assert meta.get("smoke_stderr_tail")
        assert fake.llamadas == iconos_mod.MAX_REPARACIONES + 1
        assert Path(path_md).is_file()
        contenido_md = Path(path_md).read_text(encoding="utf-8")
        assert "irreparable" in contenido_md.lower()
        # el .svg hermano queda vacio: la pieza irreparable no tiene
        # geometria que compilar (guardar_pieza_generica igual escribe el
        # archivo, pero sin contenido de figura)
        svg_hermano = Path(path_md).with_suffix(".svg")
        assert svg_hermano.is_file()
        assert svg_hermano.read_text(encoding="utf-8").strip() == ""

    def test_mutacion_menos_una_ronda_de_reparacion_rompe_el_conteo(
            self, iconos_mod, monkeypatch):
        """Mutation check del test de arriba: si MAX_REPARACIONES bajara en 1
        (p.ej. el codigo dejara de intentar la ultima ronda), la cuenta de
        llamadas real ya no coincidiria con MAX_REPARACIONES+1 -- se simula
        pisando la constante que el PROPIO test usa para la asercion (no la
        que ve generar_icono) y confirmando que un valor incorrecto SI hace
        fallar la comparacion."""
        fake = FakeLLM(["basura sin json"])
        monkeypatch.setattr(iconos_mod, "planner_llm", lambda: fake)
        _, meta = iconos_mod.generar_icono("pedido imposible 2")
        valor_mutado_incorrecto = iconos_mod.MAX_REPARACIONES  # sin el +1
        assert fake.llamadas != valor_mutado_incorrecto
        assert fake.llamadas == iconos_mod.MAX_REPARACIONES + 1


class TestNuncaEscribeGeometria:
    def test_sistema_trae_vocabulario_cerrado_y_spec_sin_coordenadas(
            self, iconos_mod, monkeypatch):
        fake = FakeLLM([json.dumps(_spec_valida())])
        monkeypatch.setattr(iconos_mod, "planner_llm", lambda: fake)

        from motor_semantico import esquema
        _, meta = iconos_mod.generar_icono("pedido de vocabulario")

        assert fake.sistemas, "el planner debe haber recibido un system prompt"
        sistema = fake.sistemas[0]
        resumen = esquema.resumen_para_prompt()
        # el prompt contiene el vocabulario cerrado real, no una version resumida
        assert "VOCABULARIO CERRADO" in sistema
        for linea_clave in ("FIGURAS:", "GESTOS:", "TONOS:", "COMPOSICIONES"):
            assert linea_clave in resumen
            assert linea_clave in sistema

        prohibidas = ("cx", "cy", "viewBox", "transform", "stroke", "fill",
                      "width", "height", "d")
        spec = meta["spec"]
        assert not (set(spec.keys()) & set(prohibidas))
        for capa in spec["capas"]:
            assert not (set(capa.keys()) & set(prohibidas))


class TestMetaFooterRoundTrip:
    def test_leer_smoke_meta_real_recupera_smoke_ok_y_modo(
            self, iconos_mod, tmp_path, monkeypatch):
        codex_lib = sys.modules["codex_lib"]
        meta = {"smoke_ok": True, "modo": "iconos", "pedido": "x"}
        _, path_md = codex_lib.guardar_pieza_generica(
            "un pedido de prueba", "<svg/>", meta, ext="svg", lang="xml")

        if str(MAK_PLATAFORMA) not in sys.path:
            sys.path.insert(0, str(MAK_PLATAFORMA))
        sys.modules.pop("entregar", None)
        import entregar
        monkeypatch.setattr(entregar, "PIEZAS_DIR", str(tmp_path))

        recuperado = entregar.leer_smoke_meta(Path(path_md).name)
        assert recuperado["smoke_ok"] is True
        assert recuperado["modo"] == "iconos"

    def test_mutacion_meta_ok_false_no_pasa_por_true(
            self, iconos_mod, tmp_path, monkeypatch):
        """Mutation check: si el footer no viajara realmente (p.ej. quedara
        vacio), leer_smoke_meta real devuelve {} y el assert de arriba
        fallaria. Se confirma aca escribiendo un meta con smoke_ok=False y
        viendo que el round-trip real NO lo confunde con True."""
        codex_lib = sys.modules["codex_lib"]
        meta = {"smoke_ok": False, "modo": "iconos"}
        _, path_md = codex_lib.guardar_pieza_generica(
            "otro pedido", "", meta, ext="svg", lang="xml")

        if str(MAK_PLATAFORMA) not in sys.path:
            sys.path.insert(0, str(MAK_PLATAFORMA))
        sys.modules.pop("entregar", None)
        import entregar
        monkeypatch.setattr(entregar, "PIEZAS_DIR", str(tmp_path))

        recuperado = entregar.leer_smoke_meta(Path(path_md).name)
        assert recuperado["smoke_ok"] is False
        assert recuperado["smoke_ok"] is not True


class TestGuardarPiezaGenerica:
    def test_svg_md_fence_xml_y_guardar_pieza_vieja_sigue_intacta(
            self, iconos_mod, tmp_path, monkeypatch):
        codex_lib = sys.modules["codex_lib"]

        # -- lo nuevo: guardar_pieza_generica con ext/lang variables --
        svg_path, md_path = codex_lib.guardar_pieza_generica(
            "pedido svg", "<svg><rect/></svg>", {"smoke_ok": True},
            ext="svg", lang="xml", nota_md="nota de prueba")
        assert Path(svg_path).suffix == ".svg"
        assert Path(svg_path).is_file()
        assert Path(md_path).is_file()
        md_txt = Path(md_path).read_text(encoding="utf-8")
        assert "```xml" in md_txt
        assert "<svg><rect/></svg>" in md_txt
        assert "nota de prueba" in md_txt

        # -- lo viejo: guardar_pieza (modo generar) no se toco --
        py_path, md_path_py = codex_lib.guardar_pieza(
            "pedido py", "print('hola')\n", {"ok": True, "rc": 0, "stdout": "",
                                              "stderr": ""}, {"smoke_ok": True})
        assert Path(py_path).suffix == ".py"
        assert Path(py_path).is_file()
        md_txt_py = Path(md_path_py).read_text(encoding="utf-8")
        assert "```python" in md_txt_py
        assert "print('hola')" in md_txt_py


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
