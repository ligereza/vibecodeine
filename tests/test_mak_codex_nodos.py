#!/usr/bin/env python3
"""tests/test_mak_codex_nodos.py -- canvas de nodos del codex (interfaz_codex.py):
el formulario lineal se convirtio en un canvas con la topologia FIJA del
pipeline real (Pedido -> Plan -> Coder [cadena de fallback reordenable] ->
Mood/Revision -> Output), mas un tab "clasico" con el formulario viejo intacto.

Sin red, sin ollama. interfaz_codex.py importa worker_codex.py -> fcntl
(Linux-only): se gatea igual que tests/test_mak_mirror_fixes.py, para no
saltear todo el archivo en Windows/CI sin fcntl.
"""
import json
import re
import sys
import threading
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

    # snapshot + restore: el stub NO puede quedar en sys.modules o envenena
    # los imports de research_lib de OTROS archivos de test (leccion godspeed:
    # mutaciones de sys.modules se filtran entre archivos; fallo real CI ubuntu)
    fake_puesto = False
    if "research_lib" not in sys.modules:
        fake = types.ModuleType("research_lib")
        fake.mint_job_id = lambda: "fake-job-id"
        sys.modules["research_lib"] = fake
        fake_puesto = True
    if str(MAK_RESEARCH) not in sys.path:
        sys.path.insert(0, str(MAK_RESEARCH))
    if str(MAK_CODEX) not in sys.path:
        sys.path.insert(0, str(MAK_CODEX))
    sys.modules.pop("interfaz_codex", None)
    try:
        return importlib.import_module("interfaz_codex")
    finally:
        if fake_puesto:
            sys.modules.pop("research_lib", None)


try:
    import fcntl  # noqa: F401
    interfaz_codex = _import_interfaz_codex()
    HAY_FCNTL = True
except ImportError:
    HAY_FCNTL = False

requiere_fcntl = pytest.mark.skipif(
    not HAY_FCNTL, reason="interfaz_codex.py importa worker_codex->fcntl (Linux-only)")


@requiere_fcntl
def test_codex_jobs_append_is_serialized(tmp_path, monkeypatch):
    path = str(tmp_path / "jobs.jsonl")
    monkeypatch.setattr(interfaz_codex, "JOBS_FILE", path)
    barrier = threading.Barrier(10)

    def write_record(index):
        barrier.wait(timeout=3)
        interfaz_codex._append_job_record({"job_id": "codex-%d" % index,
                                           "estado": "listo"})

    threads = [threading.Thread(target=write_record, args=(i,)) for i in range(10)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=3)

    records = [json.loads(line) for line in
               Path(path).read_text(encoding="utf-8").splitlines()]
    assert len(records) == 10
    assert {record["job_id"] for record in records} == {
        "codex-%d" % index for index in range(10)}


def test_producers_and_delivery_share_codex_ledger_lock():
    codex = (MAK_CODEX / "interfaz_codex.py").read_text(encoding="utf-8")
    libre = (MAK_CODEX / "agente_libre.py").read_text(encoding="utf-8")
    delivery = (PROYECTO_DIR / "cultura" / "mak_plataforma" /
                "entregar.py").read_text(encoding="utf-8")
    assert "def _exclusive_jobs_file_lock" in codex
    assert "_append_job_record(job)" in codex
    assert "def _exclusive_jobs_file_lock" in libre
    assert "def _exclusive_codex_jobs_lock" in delivery
    assert "with _exclusive_codex_jobs_lock()" in delivery


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


@requiere_fcntl
class TestModoIconosReachableEndToEnd:
    """El modo `iconos` (spec semantica -> SVG) tiene que ser alcanzable de
    punta a punta desde la interfaz web, o la pieza existe en disco y es
    invisible: no aparece en el <select>, el server la rechaza antes de
    lanzarla, o /f la sirve 404 porque NOMBRE_OK/FECHA_RE no reconocen su
    nombre de archivo (.svg)."""

    def test_value_iconos_aparece_en_los_dos_selects(self):
        """PAGINA es la UNICA plantilla (no hay una segunda constante): trae
        el select del canvas (id="modo-canvas") y el del tab clasico
        (id="modo"), y los dos deben ofrecer iconos."""
        pagina = interfaz_codex.PAGINA
        assert pagina.count('value="iconos"') >= 2, (
            "value=\"iconos\" deberia aparecer en el select del canvas Y en "
            "el del tab clasico")
        # cada select declarado explicitamente trae la opcion
        for anchor in ('id="modo-canvas"', 'id="modo"'):
            i = pagina.index(anchor)
            cierre = pagina.index("</select>", i)
            assert 'value="iconos"' in pagina[i:cierre], anchor

    def test_whitelist_server_side_incluye_iconos(self):
        """do_POST descarta a 'generar' cualquier modo que no reconozca; si
        'iconos' no esta en esa tupla, un pedido de iconos legitimo se
        silencia como si fuera 'generar'."""
        src = Path(interfaz_codex.__file__).read_text(encoding="utf-8")
        m = re.search(r'if modo not in \(([^)]*)\):', src)
        assert m, "no encuentro la whitelist de modos en do_POST"
        assert '"iconos"' in m.group(1)

    def test_nombre_ok_acepta_svg_y_sigue_aceptando_md_py(self):
        assert interfaz_codex.NOMBRE_OK.match("20260730-000000-icono-test.svg")
        assert interfaz_codex.NOMBRE_OK.match("pieza.md")
        assert interfaz_codex.NOMBRE_OK.match("pieza.py")
        assert not interfaz_codex.NOMBRE_OK.match("pieza.exe")

    def test_fecha_re_parsea_un_svg_estampado(self):
        m = interfaz_codex.FECHA_RE.match(
            "20260730-153045-el-muro-que-se-parte.svg")
        assert m
        assert m.group(8) == "svg"
        assert m.group(7) == "el-muro-que-se-parte"

    def test_scripts_de_worker_codex_mapea_iconos_a_su_script(self):
        worker_codex = sys.modules["worker_codex"]
        assert worker_codex.SCRIPTS["iconos"] == "iconos.py"

    def test_iconos_no_es_un_modo_de_ruta(self):
        """iconos recibe un BRIEF de texto, no una ruta a un .py existente
        (a diferencia de revisar/testear/debug): si 'iconos' terminara en
        MODOS_RUTA, run_pedido le exigiria un archivo real bajo /home/mak y
        un brief de texto normal fallaria siempre con 'ruta invalida'."""
        worker_codex = sys.modules["worker_codex"]
        assert "iconos" not in worker_codex.MODOS_RUTA

    def test_mutacion_scripts_sin_iconos_se_detecta(self):
        """Mutation check: si SCRIPTS perdiera la entrada 'iconos' (o
        apuntara al script equivocado), la comparacion de arriba debe
        fallar. Se simula con un dict de prueba, no editando worker_codex.py
        en disco."""
        worker_codex = sys.modules["worker_codex"]
        scripts_mutados = dict(worker_codex.SCRIPTS)
        scripts_mutados.pop("iconos", None)
        with pytest.raises(KeyError):
            assert scripts_mutados["iconos"] == "iconos.py"
