#!/usr/bin/env python3
"""tests/test_mak_codex_nodos.py -- canvas de nodos del codex (interfaz_codex.py):
el formulario lineal se convirtio en un canvas con la topologia FIJA del
pipeline real (Pedido -> Plan -> Coder [cadena de fallback reordenable] ->
Mood/Revision -> Output), mas un tab "clasico" con el formulario viejo intacto.

Sin red, sin ollama. interfaz_codex.py importa worker_codex.py -> fcntl
(Linux-only): se gatea igual que tests/test_mak_mirror_fixes.py, para no
saltear todo el archivo en Windows/CI sin fcntl.
"""
import sys
import types
from pathlib import Path

import pytest

TEST_DIR = Path(__file__).parent
PROYECTO_DIR = TEST_DIR.parent
MAK_CODEX = PROYECTO_DIR / "cultura" / "mak_codex"
MAK_RESEARCH = PROYECTO_DIR / "cultura" / "mak_research"


def _import_interfaz_codex():
    """Import limpio de interfaz_codex con research_lib stubbeado (mismo
    patron que tests/test_mak_fallback.py / test_mak_mirror_fixes.py)."""
    import importlib

    if "research_lib" not in sys.modules:
        fake = types.ModuleType("research_lib")
        fake.mint_job_id = lambda: "fake-job-id"
        sys.modules["research_lib"] = fake
    if str(MAK_RESEARCH) not in sys.path:
        sys.path.insert(0, str(MAK_RESEARCH))
    if str(MAK_CODEX) not in sys.path:
        sys.path.insert(0, str(MAK_CODEX))
    sys.modules.pop("interfaz_codex", None)
    return importlib.import_module("interfaz_codex")


try:
    import fcntl  # noqa: F401
    interfaz_codex = _import_interfaz_codex()
    HAY_FCNTL = True
except ImportError:
    HAY_FCNTL = False

requiere_fcntl = pytest.mark.skipif(
    not HAY_FCNTL, reason="interfaz_codex.py importa worker_codex->fcntl (Linux-only)")


@requiere_fcntl
class TestValidarCadena:
    """_validar_cadena: CSV de claves de coder -> CSV validado (filtrado a
    proveedores conocidos, invalido -> default, vacio -> default)."""

    def test_csv_valido_se_preserva_en_orden(self):
        assert interfaz_codex._validar_cadena("win,ollama") == "win,ollama"

    def test_csv_con_claves_invalidas_se_filtran(self):
        assert interfaz_codex._validar_cadena(
            "win,basura,nim-pro") == "win,nim-pro"

    def test_csv_todo_invalido_cae_a_default(self):
        assert interfaz_codex._validar_cadena(
            "basura,otra-basura") == interfaz_codex.CADENA_DEFAULT

    def test_csv_vacio_cae_a_default(self):
        assert interfaz_codex._validar_cadena("") == interfaz_codex.CADENA_DEFAULT

    def test_csv_ausente_cae_a_default(self):
        assert interfaz_codex._validar_cadena(None) == interfaz_codex.CADENA_DEFAULT

    def test_claves_duplicadas_se_deduplican_preservando_primera_aparicion(self):
        assert interfaz_codex._validar_cadena(
            "win,win,ollama,win") == "win,ollama"

    def test_default_incluye_los_4_proveedores(self):
        assert set(interfaz_codex.CADENA_DEFAULT.split(",")) == set(
            interfaz_codex.CADENA_CLAVES)


@requiere_fcntl
class TestPaginaCanvasDeNodos:
    """Asserts baratos de template (patron TestPaginaMarcoUnico): evitan
    una regresion que reintroduzca el formulario lineal como unica vista."""

    def test_contiene_los_nodos_del_pipeline_real(self):
        for nid in ("nodo-pedido", "nodo-plan", "nodo-coder",
                    "nodo-mood", "nodo-output"):
            assert 'id="%s"' % nid in interfaz_codex.PAGINA

    def test_contiene_la_cadena_de_fallback_win_y_nim(self):
        assert "nim-pro" in interfaz_codex.PAGINA
        assert "'win'" in interfaz_codex.PAGINA
        assert "'ollama'" in interfaz_codex.PAGINA

    def test_conserva_el_formulario_clasico_en_su_propio_tab(self):
        assert 'id="tab-clasico"' in interfaz_codex.PAGINA
        assert 'id="pedido-clasico"' in interfaz_codex.PAGINA
