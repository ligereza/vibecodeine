#!/usr/bin/env python3
"""tests/test_mak_mirror_fixes.py -- mirror de reparaciones vivas del MAK
(box 192.168.50.2): "win" agregado a las whitelists de proveedores +
CODER_CHAIN configurable por env var; y 3 defectos encontrados en testing
en vivo:
  5. cadena.py: un proveedor caido (groq 429) mataba el job entero -- ahora
     reintenta el paso con el resto de la cadena antes de rendirse.
  6. interfaz.py /run: modos front-end-only (adversarial, single, ...)
     caian callados al default "research" -- ahora se traducen o 400.
  7. research_lib.py marco(): la negacion de sustancias se colaba en TODO
     tema y confundia a modelos chicos en temas benignos -- ahora es
     condicional al contenido del tema.

Sin red, sin ollama. interfaz.py importa worker.py -> fcntl (Linux-only):
esa clase se gatea igual que en test_mak_reanudar.py.
"""
import sys
from pathlib import Path

import pytest

TEST_DIR = Path(__file__).parent
PROYECTO_DIR = TEST_DIR.parent
MAK_RESEARCH = PROYECTO_DIR / "cultura" / "mak_research"
MAK_CODEX = PROYECTO_DIR / "cultura" / "mak_codex"

sys.path.insert(0, str(MAK_RESEARCH))

import cadena  # noqa: E402
import grafo  # noqa: E402
import research_lib  # noqa: E402


# ── mirror: "win" agregado a las whitelists de proveedores ──

class TestWinEnWhitelists:
    def test_grafo_proveedores_incluye_win(self):
        assert "win" in grafo.PROVEEDORES

    def test_cadena_arg_filter_acepta_win(self):
        orden = [p.strip() for p in "groq,win,ollama".split(",")
                if p.strip() in ("groq", "cerebras", "azure", "win", "ollama")]
        assert orden == ["groq", "win", "ollama"]

    def test_research_lib_llm_order_incluye_win(self):
        llm = research_lib.LLM(order="groq,win,ollama")
        assert llm.order == ["groq", "win", "ollama"]


# ── fix 5: fallback intra-paso de cadena.py ──

class FakeLLM:
    """Simula LLM.call: los proveedores en `fallan` levantan RuntimeError,
    el resto responde 'ok desde <proveedor>'. Registra cada `order` con el
    que se lo llamo, para verificar que el reintento usa el resto correcto
    de la cadena (no re-prueba el proveedor que ya fallo)."""

    def __init__(self, fallan):
        self.fallan = set(fallan)
        self.llamadas = []
        self.stats = {}
        self.errors = []

    def call(self, system, user, max_tok, order=None):
        orden = list(order or [])
        self.llamadas.append(orden)
        for p in orden:
            if p not in self.fallan:
                self.stats[p] = self.stats.get(p, 0) + 1
                return "ok desde " + p, p
            self.errors.append(p + ": simulado")
        raise RuntimeError("Todos los proveedores LLM fallaron. Ultimo: %s"
                           % (orden[-1] if orden else "?"))


class TestCadenaFallbackIntraPaso:
    def test_primer_proveedor_falla_segundo_responde(self):
        llm = FakeLLM(fallan={"groq"})
        orden = ["groq", "cerebras", "azure"]
        out, real = cadena._paso_con_fallback(llm, orden, "groq", "rol", "prompt", 500)
        assert real == "cerebras"
        assert out == "ok desde cerebras"
        assert llm.llamadas[0] == ["groq"]
        assert llm.llamadas[1] == ["cerebras", "azure"]

    def test_primer_proveedor_exitoso_sin_retry(self):
        """Camino feliz identico al comportamiento viejo: una sola llamada."""
        llm = FakeLLM(fallan=set())
        orden = ["groq", "cerebras"]
        out, real = cadena._paso_con_fallback(llm, orden, "groq", "rol", "prompt", 500)
        assert real == "groq"
        assert len(llm.llamadas) == 1

    def test_todos_fallan_propaga_error(self):
        llm = FakeLLM(fallan={"groq", "cerebras", "azure"})
        orden = ["groq", "cerebras", "azure"]
        with pytest.raises(RuntimeError):
            cadena._paso_con_fallback(llm, orden, "groq", "rol", "prompt", 500)

    def test_proveedor_fallido_ultimo_de_la_cadena_no_reintenta(self):
        llm = FakeLLM(fallan={"azure"})
        orden = ["groq", "cerebras", "azure"]
        with pytest.raises(RuntimeError):
            cadena._paso_con_fallback(llm, orden, "azure", "rol", "prompt", 500)
        assert len(llm.llamadas) == 1  # no hay proveedores despues de azure

    def test_encadenar_job_no_muere_si_un_solo_paso_recupera(self, monkeypatch):
        """Espejo del job f69f: groq 429 en el paso 1 ya no mata el job
        entero si cerebras responde."""
        llm = FakeLLM(fallan={"groq"})
        monkeypatch.setattr(cadena, "LLM", lambda: llm)
        monkeypatch.setattr(cadena, "correlacionar", lambda *a, **k: ("sintesis", None))
        result = cadena.encadenar("tema de prueba", ["groq", "cerebras"], densidad="corto")
        assert result["pasos"][0]["proveedor_real"] == "cerebras"
        assert result["correlacion"] == "sintesis"

    def test_encadenar_job_muere_si_ningun_proveedor_responde(self, monkeypatch):
        llm = FakeLLM(fallan={"groq", "cerebras"})
        monkeypatch.setattr(cadena, "LLM", lambda: llm)
        monkeypatch.setattr(cadena, "correlacionar", lambda *a, **k: ("sintesis", None))
        with pytest.raises(RuntimeError):
            cadena.encadenar("tema de prueba", ["groq", "cerebras"], densidad="corto")


# ── mirror: CODER_CHAIN configurable por env var ──

def _import_codex_lib():
    """Import limpio de codex_lib con research_lib/resource stubbeados
    (mismo patron que tests/test_mak_fallback.py). Se reimporta desde cero
    en cada llamada para que CODER_CHAIN se recalcule con el os.environ
    vigente en ese momento."""
    import types
    import importlib

    if "research_lib" not in sys.modules:
        fake = types.ModuleType("research_lib")
        fake.LLM = object
        fake.MODELO_CAPAZ = "fake-model"
        fake._http_json = lambda *a, **k: {}
        fake.escala_tok = lambda *a, **k: 1000
        fake.load_env = lambda: None
        fake.red_ok = lambda: True
        fake.slug = lambda s: s
        fake.stamp = lambda: "stamp"
        sys.modules["research_lib"] = fake
    try:
        import resource  # noqa: F401  -- existe en Linux
    except ImportError:
        sys.modules["resource"] = types.ModuleType("resource")
    if str(MAK_CODEX) not in sys.path:
        sys.path.insert(0, str(MAK_CODEX))
    sys.modules.pop("codex_lib", None)
    return importlib.import_module("codex_lib")


class TestCoderChainEnvOverride:
    def test_csv_valido_reordena_y_filtra(self, monkeypatch):
        monkeypatch.setenv("CODER_CHAIN", "win,ollama")
        codex_lib = _import_codex_lib()
        assert codex_lib.CODER_CHAIN == [
            codex_lib._CODER_CHAIN_MAP["win"],
            codex_lib._CODER_CHAIN_MAP["ollama"],
        ]

    def test_csv_con_claves_invalidas_se_descartan(self, monkeypatch):
        monkeypatch.setenv("CODER_CHAIN", "win,basura,nim-pro")
        codex_lib = _import_codex_lib()
        assert codex_lib.CODER_CHAIN == [
            codex_lib._CODER_CHAIN_MAP["win"],
            codex_lib._CODER_CHAIN_MAP["nim-pro"],
        ]

    def test_csv_todo_basura_cae_a_default(self, monkeypatch):
        monkeypatch.setenv("CODER_CHAIN", "basura,otra-basura")
        codex_lib = _import_codex_lib()
        assert codex_lib.CODER_CHAIN == [
            codex_lib._CODER_CHAIN_MAP[k] for k in codex_lib._CODER_CHAIN_DEFAULT
        ]

    def test_env_var_ausente_cae_a_default(self, monkeypatch):
        monkeypatch.delenv("CODER_CHAIN", raising=False)
        codex_lib = _import_codex_lib()
        assert codex_lib.CODER_CHAIN == [
            codex_lib._CODER_CHAIN_MAP[k] for k in codex_lib._CODER_CHAIN_DEFAULT
        ]

    def test_env_var_vacia_cae_a_default(self, monkeypatch):
        monkeypatch.setenv("CODER_CHAIN", "")
        codex_lib = _import_codex_lib()
        assert codex_lib.CODER_CHAIN == [
            codex_lib._CODER_CHAIN_MAP[k] for k in codex_lib._CODER_CHAIN_DEFAULT
        ]

    def test_default_preserva_las_4_entradas_originales(self, monkeypatch):
        monkeypatch.delenv("CODER_CHAIN", raising=False)
        codex_lib = _import_codex_lib()
        assert codex_lib.CODER_CHAIN == [
            ("nim", "deepseek-ai/deepseek-v4-pro"),
            ("nim", "deepseek-ai/deepseek-v4-flash"),
            ("win", codex_lib.WIN_CODE_MODEL),
            ("ollama", "deepseek-coder:6.7b"),
        ]


# ── fix 7: marco() condicional (research_lib.py, usado por research.py) ──

class TestMarcoCondicional:
    def test_tema_neutro_sin_negaciones_de_sustancia(self):
        texto = research_lib.marco("automatizar deploys de un servidor web con Docker")
        assert "sintesis quimica" not in texto
        assert "cultivo" not in texto
        assert "no perfilar personas reales" in texto
        assert texto.endswith("automatizar deploys de un servidor web con Docker")

    def test_tema_sustancia_preserva_marco_completo(self):
        texto = research_lib.marco("historia del cultivo de cannabis en Chile")
        assert "sintesis quimica ni cultivo" in texto
        assert "no perfilar personas reales" in texto

    def test_marco_desactivado_no_agrega_nada(self):
        assert research_lib.marco("cualquier tema", activo=False) == "cualquier tema"

    def test_deteccion_case_insensitive_por_substring(self):
        assert research_lib._es_tema_sustancia("Historia de la COCAÍNA en el siglo XX")
        assert not research_lib._es_tema_sustancia("Historia del jazz en Nueva Orleans")


# ── fix 6: /run exige modo estricto (interfaz.py) ──
# interfaz.py importa worker.py -> fcntl (Linux-only); se gatea por clase
# igual que tests/test_mak_reanudar.py, para no saltear todo el archivo.

try:
    import fcntl  # noqa: F401
    import interfaz  # noqa: E402
    HAY_FCNTL = True
except ImportError:
    HAY_FCNTL = False

requiere_fcntl = pytest.mark.skipif(
    not HAY_FCNTL, reason="interfaz.py importa worker->fcntl (Linux-only)")


@requiere_fcntl
class TestResolverModo:
    def test_clave_real_pasa_directa(self):
        modo, err = interfaz._resolver_modo("cadena")
        assert modo == "cadena" and err is None

    def test_alias_adversarial_mapea_a_refutar(self):
        # bug probado en vivo: modo=adversarial corria como research (single)
        modo, err = interfaz._resolver_modo("adversarial")
        assert modo == "refutar" and err is None

    def test_alias_single_mapea_a_research(self):
        modo, err = interfaz._resolver_modo("single")
        assert modo == "research" and err is None

    def test_alias_pipeline_y_discussion(self):
        assert interfaz._resolver_modo("pipeline")[0] == "cadena"
        assert interfaz._resolver_modo("discussion")[0] == "panel"

    def test_alias_grafo_es_identidad(self):
        assert interfaz._resolver_modo("grafo") == ("grafo", None)

    def test_modo_desconocido_devuelve_error_con_validas_listadas(self):
        modo, err = interfaz._resolver_modo("bailar")
        assert modo is None
        assert err is not None
        assert err["ok"] is False
        assert "bailar" in err["error"]
        assert "cadena" in err["error"]
        assert "adversarial" in err["error"]
