"""Degradation-path and logic tests for memoria.py (the research department's
local RAG memory). All network/provider calls (ollama embeddings, ntfy, the
capable LLM) are mocked; every path is redirected under tmp_path so nothing
here reads or writes ~/research/memoria or fires a real notification.

Focus, per the audit brief: NTFY_TOPIC_OUT is unset everywhere on MAK, so
ntfy_publish() always returns False here -- these tests pin that memoria.py
handles that False without pretending a notification went out. They also
document a real ambiguity: buscar()/consultar() return the exact same
"vacio" signal whether the memory index is genuinely empty or whether the
embedding provider (ollama) is simply unreachable right now.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import pytest

pytest.importorskip("fcntl", reason="memoria.py importa fcntl (Linux-only)")

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "cultura" / "mak_research"))

import memoria  # noqa: E402
import research_lib  # noqa: E402


# ---------------------------------------------------------------------------
# _titulo / _meta_documento / cuerpo_util: parsing puro
# ---------------------------------------------------------------------------

def test_titulo_uses_first_markdown_heading():
    texto = "algo antes\n# El titulo real\nresto"
    assert memoria._titulo(texto, "/x/archivo.md") == "El titulo real"


def test_titulo_falls_back_to_basename_without_heading():
    assert memoria._titulo("solo prosa, sin encabezado", "/x/archivo.md") == "archivo.md"


def test_meta_documento_reads_trailing_meta_line():
    texto = "cuerpo\nmas cuerpo\nmeta: {\"tipo\": \"informe\", \"origen\": \"x\"}"
    assert memoria._meta_documento(texto) == {"tipo": "informe", "origen": "x"}


def test_meta_documento_ignores_malformed_json():
    texto = "cuerpo\nmeta: {esto no es json"
    assert memoria._meta_documento(texto) == {}


def test_meta_documento_ignores_non_object_json():
    texto = "cuerpo\nmeta: [1, 2, 3]"
    assert memoria._meta_documento(texto) == {}


def test_cuerpo_util_strips_headers_meta_and_quotes():
    texto = "# Titulo\n---\n> una cita\nmeta: {}\nlinea real 1\n\nlinea real 2"
    assert memoria.cuerpo_util(texto) == "linea real 1\nlinea real 2"


# ---------------------------------------------------------------------------
# calidad_documento / util_para_micelio: la puerta de entrada al micelio
# ---------------------------------------------------------------------------

def test_calidad_documento_detects_declared_failure_as_compost():
    texto = "Todos los proveedores LLM fallaron\nsin contenido util"
    calidad = memoria.calidad_documento(texto, "informes")
    assert calidad["estado"] == "compost"
    assert calidad["sustancia"] == 0.0


def test_calidad_documento_corpus_is_always_cultivo_regardless_of_length():
    calidad = memoria.calidad_documento("una obra breve.", "corpus")
    assert calidad["estado"] == "cultivo"
    assert calidad["sustancia"] == 1.0


def test_calidad_documento_short_report_is_compost():
    calidad = memoria.calidad_documento("muy corto", "informes")
    assert calidad["estado"] == "compost"
    assert calidad["razon"] == "sin sustancia"


def test_util_para_micelio_empty_text_is_excluded():
    entra, motivo = memoria.util_para_micelio("   ", carpeta="informes")
    assert entra is False
    assert motivo == "vacio"


def test_util_para_micelio_declared_failure_is_excluded_regardless_of_length():
    texto = "Informe no generado" + ("x" * 2000)
    entra, motivo = memoria.util_para_micelio(texto, carpeta="informes")
    assert entra is False
    assert "fallo declarado" in motivo


def test_util_para_micelio_corpus_is_exempt_from_minimum_length():
    entra, _motivo = memoria.util_para_micelio("Una obra en un parrafo.", carpeta="corpus")
    assert entra is True


def test_util_para_micelio_informe_below_minimum_is_excluded():
    entra, motivo = memoria.util_para_micelio("informe corto", carpeta="informes")
    assert entra is False
    assert "sin sustancia" in motivo


def test_util_para_micelio_informe_above_minimum_is_included():
    entra, motivo = memoria.util_para_micelio("x" * 500, carpeta="informes")
    assert entra is True
    assert motivo == ""


# ---------------------------------------------------------------------------
# _fragmentar
# ---------------------------------------------------------------------------

def test_fragmentar_groups_short_paragraphs_into_single_chunk():
    texto = "parrafo uno.\n\nparrafo dos.\n\nparrafo tres."
    chunks = memoria._fragmentar(texto)
    assert chunks == ["parrafo uno.\n\nparrafo dos.\n\nparrafo tres."]


def test_fragmentar_splits_oversized_paragraph_with_overlap():
    huge_paragraph = "a" * (memoria.CHUNK * 2 + 10)
    chunks = memoria._fragmentar(huge_paragraph)
    assert len(chunks) > 1
    for c in chunks:
        assert len(c) <= memoria.CHUNK
    step = memoria.CHUNK - memoria.SOLAPE
    assert chunks[1][0] == huge_paragraph[step]


def test_fragmentar_empty_text_yields_no_chunks():
    assert memoria._fragmentar("   \n\n  ") == []


# ---------------------------------------------------------------------------
# _cargar_index / _guardar_index roundtrip
# ---------------------------------------------------------------------------

def test_index_roundtrip_survives_corrupt_lines(tmp_path, monkeypatch):
    index_file = tmp_path / "memoria" / "index.jsonl"
    monkeypatch.setattr(memoria, "MEM_DIR", str(index_file.parent))
    monkeypatch.setattr(memoria, "INDEX_FILE", str(index_file))
    memoria._guardar_index([{"path": "a.md", "vec": [1.0]}])
    # simulate one corrupted line appended by a crashed writer
    with open(index_file, "a", encoding="utf-8") as f:
        f.write("esto no es json\n")
    entradas = memoria._cargar_index()
    assert entradas == [{"path": "a.md", "vec": [1.0]}]


# ---------------------------------------------------------------------------
# _cos
# ---------------------------------------------------------------------------

def test_cos_identical_vectors_is_one():
    assert memoria._cos([1.0, 2.0, 3.0], [1.0, 2.0, 3.0]) == pytest.approx(1.0)


def test_cos_zero_vector_is_minus_one():
    assert memoria._cos([0.0, 0.0], [1.0, 2.0]) == -1.0


def test_cos_empty_or_mismatched_vectors_is_minus_one():
    assert memoria._cos([], [1.0]) == -1.0
    assert memoria._cos([1.0, 2.0], [1.0]) == -1.0


# ---------------------------------------------------------------------------
# _embed: la ausencia del proveedor (ollama) nunca se propaga como excepcion
# ---------------------------------------------------------------------------

def test_embed_returns_vector_on_success(monkeypatch):
    monkeypatch.setattr(memoria, "_http_json",
                        lambda url, payload, timeout=60: {"embedding": [0.1, 0.2]})
    assert memoria._embed("un texto") == [0.1, 0.2]


def test_embed_returns_empty_list_when_ollama_is_unreachable(monkeypatch):
    def boom(*a, **k):
        raise ConnectionRefusedError("ollama no responde")
    monkeypatch.setattr(memoria, "_http_json", boom)
    assert memoria._embed("un texto") == []


# ---------------------------------------------------------------------------
# buscar()/consultar(): el defecto real -- "sin memoria" y "proveedor caido"
# emiten la MISMA senal (lista vacia / meta.vacio=True).
# ---------------------------------------------------------------------------

def test_buscar_empty_index_returns_empty_without_calling_embed(tmp_path, monkeypatch):
    monkeypatch.setattr(memoria, "INDEX_FILE", str(tmp_path / "index.jsonl"))
    embed_calls = []
    monkeypatch.setattr(memoria, "_embed", lambda t: embed_calls.append(t) or [1.0])
    assert memoria.buscar("tema cualquiera") == []
    assert embed_calls == []  # nothing to search, so it never even tries


def test_buscar_reads_identically_whether_memory_is_empty_or_provider_is_down(
        tmp_path, monkeypatch):
    """Regression-shaped: populate a real index (memory is NOT empty), then
    make _embed fail (the provider is down, not absent memory). buscar()
    returns [] in both cases -- a caller cannot tell "nothing learned yet"
    from "cannot reach ollama right now" from this return value alone."""
    index_file = tmp_path / "index.jsonl"
    monkeypatch.setattr(memoria, "INDEX_FILE", str(index_file))
    memoria._guardar_index([{"path": "a.md", "dir": "informes", "titulo": "A",
                             "vec": [1.0, 0.0], "chunk": "contenido de A"}])

    monkeypatch.setattr(memoria, "_embed", lambda t: [])  # simulated outage
    hits_with_populated_index_but_dead_provider = memoria.buscar("tema")

    monkeypatch.setattr(memoria, "INDEX_FILE", str(tmp_path / "no-existe.jsonl"))
    hits_with_genuinely_empty_memory = memoria.buscar("tema")

    assert hits_with_populated_index_but_dead_provider == []
    assert hits_with_genuinely_empty_memory == []


def test_consultar_reports_vacio_when_provider_is_down_despite_populated_index(
        tmp_path, monkeypatch):
    index_file = tmp_path / "index.jsonl"
    monkeypatch.setattr(memoria, "INDEX_FILE", str(index_file))
    memoria._guardar_index([{"path": "a.md", "dir": "informes", "titulo": "A",
                             "vec": [1.0, 0.0], "chunk": "contenido de A"}])
    monkeypatch.setattr(memoria, "_embed", lambda t: [])  # provider down
    monkeypatch.setattr(memoria, "load_env", lambda *a, **k: None)

    result = memoria.consultar("tema")

    # This is the ambiguity itself: a down provider is indistinguishable
    # from "the department never researched this before" to any caller.
    assert result["meta"]["vacio"] is True
    assert result["sintesis"] == ""
    assert result["fuentes"] == []


def test_contexto_empty_when_no_hits(monkeypatch):
    monkeypatch.setattr(memoria, "buscar", lambda tema, k: [])
    assert memoria.contexto("tema") == ""


def test_contexto_formats_hits_and_respects_max_chars(monkeypatch):
    hits = [{"titulo": "Uno", "dir": "informes", "chunk": "x" * 3000},
            {"titulo": "Dos", "dir": "paneles", "chunk": "y" * 3000}]
    monkeypatch.setattr(memoria, "buscar", lambda tema, k: hits)
    bloque = memoria.contexto("tema", max_chars=100)
    assert "MEMORIA DEL DEPARTAMENTO" in bloque
    assert "[Uno | informes]" in bloque
    assert "Dos" not in bloque  # cut off once max_chars is reached


# ---------------------------------------------------------------------------
# consultar(): cuando SI hay memoria, la ausencia del LLM se nombra, no se
# esconde -- confirmacion positiva del comportamiento correcto.
# ---------------------------------------------------------------------------

class _FakeLLM:
    def __init__(self, order):
        self.order = order
        self.stats = {"gemini": 1}
        self.errors = []
        self._raise = False

    def call(self, system, user, max_tok, order=None):
        if self._raise:
            raise RuntimeError("todos los proveedores fallaron")
        return "sintesis ok", "gemini"


def _seed_one_hit_index(tmp_path, monkeypatch):
    index_file = tmp_path / "index.jsonl"
    monkeypatch.setattr(memoria, "INDEX_FILE", str(index_file))
    memoria._guardar_index([{"path": "a.md", "dir": "informes", "titulo": "A",
                             "vec": [1.0, 0.0], "chunk": "contenido de A"}])
    monkeypatch.setattr(memoria, "_embed", lambda t: [1.0, 0.0])
    monkeypatch.setattr(memoria, "load_env", lambda *a, **k: None)


def test_consultar_synthesizes_when_llm_succeeds(tmp_path, monkeypatch):
    _seed_one_hit_index(tmp_path, monkeypatch)
    fake = _FakeLLM(["gemini"])
    monkeypatch.setattr(memoria, "LLM", lambda: fake)

    result = memoria.consultar("tema")

    assert result["sintesis"] == "sintesis ok"
    assert result["meta"]["proveedor"] == "gemini"
    assert result["meta"]["vacio"] is False if "vacio" in result["meta"] else True


def test_consultar_names_total_provider_failure_instead_of_faking_a_synthesis(
        tmp_path, monkeypatch):
    _seed_one_hit_index(tmp_path, monkeypatch)
    fake = _FakeLLM(["gemini"])
    fake._raise = True
    monkeypatch.setattr(memoria, "LLM", lambda: fake)

    result = memoria.consultar("tema")

    assert "sintesis fallo" in result["sintesis"]
    assert result["meta"]["proveedor"] is None  # never fakes a source


# ---------------------------------------------------------------------------
# indexar(): el flujo incremental, con ollama y el resto del organismo mockeados
# ---------------------------------------------------------------------------

@pytest.fixture
def isolated_research(tmp_path, monkeypatch):
    research = tmp_path / "research"
    mem_dir = research / "memoria"
    for carpeta in memoria.FUENTES:
        (research / carpeta).mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(memoria, "RESEARCH", str(research))
    monkeypatch.setattr(memoria, "MEM_DIR", str(mem_dir))
    monkeypatch.setattr(memoria, "INDEX_FILE", str(mem_dir / "index.jsonl"))
    monkeypatch.setattr(memoria, "_embed", lambda t: [1.0, 0.0])
    monkeypatch.setattr(memoria, "active_enabled", lambda: False)
    return research


def test_indexar_ingests_a_valid_report_and_skips_unchanged_on_rerun(
        isolated_research, monkeypatch):
    informe = isolated_research / "informes" / "20260830-a.md"
    informe.write_text("# Un informe\n\n" + ("cuerpo real. " * 60), encoding="utf-8")

    stats1 = memoria.indexar()
    assert stats1["archivos"] == 1
    assert stats1["nuevos"] >= 1

    embed_calls = []
    monkeypatch.setattr(memoria, "_embed",
                        lambda t: embed_calls.append(t) or [1.0, 0.0])
    stats2 = memoria.indexar()
    assert stats2["nuevos"] == 0  # unchanged mtime -> reused, not re-embedded
    assert embed_calls == []


def test_indexar_keeps_declared_failure_as_indexable_compost_when_it_has_prose(
        isolated_research):
    """A pipeline that declares its own failure but still emits prose is not
    silently dropped from the memory -- it is kept as low-quality compost,
    never deleted, per the module's own contract in calidad_documento()."""
    fallo = isolated_research / "informes" / "20260830-b.md"
    fallo.write_text(
        "# Intento fallido\n\nTodos los proveedores LLM fallaron.\n\n"
        "Contexto parcial que si se escribio antes del fallo, "
        "suficiente para superar el minimo de sustancia exigido aqui.",
        encoding="utf-8")

    memoria.indexar()
    entradas = memoria._cargar_index()
    assert entradas  # it was NOT discarded outright
    assert entradas[0]["calidad"]["estado"] == "compost"


def test_indexar_survives_ideas_sync_failure_and_logs_it(isolated_research, monkeypatch):
    class _BoomModule:
        def sincronizar(self):
            raise RuntimeError("ideas.jsonl no disponible")
    monkeypatch.setitem(sys.modules, "ideas_a_micelio", _BoomModule())

    logged = []
    stats = memoria.indexar(log=logged.append)

    assert isinstance(stats, dict)  # indexing itself still completed
    assert any("no se sincronizaron ideas" in line for line in logged)


def test_indexar_dispatches_through_the_shared_conductor_when_active(
        isolated_research, monkeypatch):
    """The active-conductor branch (MAK's shared job queue) is a completely
    different code path from the default local run; it was measured at 0%
    coverage before this test."""
    # Only the outer call takes the queued branch; the handler's own nested
    # indexar() call must fall through to the real local path (as it would
    # inside an actual out-of-process queue worker) or it recurses forever.
    calls = {"n": 0}

    def fake_active_enabled():
        calls["n"] += 1
        return calls["n"] == 1
    monkeypatch.setattr(memoria, "active_enabled", fake_active_enabled)

    def fake_dispatch_sync(kind, payload, producer, handler, **kwargs):
        result = handler({"payload": payload})
        return {"queue_status": "COMPLETED", **result}
    monkeypatch.setattr(memoria, "dispatch_sync", fake_dispatch_sync)

    stats = memoria.indexar(rebuild=True)
    # "validated" and "queue_status" are queue bookkeeping, stripped before
    # reaching the caller: only the plain indexing stats survive.
    assert "validated" not in stats
    assert "archivos" in stats


def test_indexar_reports_queue_failure_without_pretending_success(
        isolated_research, monkeypatch):
    monkeypatch.setattr(memoria, "active_enabled", lambda: True)
    monkeypatch.setattr(
        memoria, "dispatch_sync",
        lambda *a, **k: {"queue_status": "FAILED", "reason": "arbiter offline"})

    stats = memoria.indexar()

    assert stats["error"] == "queued_memory_index_failed"
    assert stats["queue"]["queue_status"] == "FAILED"


# ---------------------------------------------------------------------------
# _vectores_por_producto: promedio de vectores + calidad diferida
# ---------------------------------------------------------------------------

def test_vectores_por_producto_averages_chunk_vectors_per_file(tmp_path, monkeypatch):
    monkeypatch.setattr(memoria, "INDEX_FILE", str(tmp_path / "index.jsonl"))
    memoria._guardar_index([
        {"path": "a.md", "dir": "informes", "titulo": "A", "vec": [1.0, 1.0],
         "chunk": "c1", "calidad": {"estado": "cultivo", "sustancia": 0.5}},
        {"path": "a.md", "dir": "informes", "titulo": "A", "vec": [3.0, 3.0],
         "chunk": "c2", "calidad": {"estado": "cultivo", "sustancia": 0.5}},
    ])
    vecs, meta = memoria._vectores_por_producto()
    assert vecs["a.md"] == [2.0, 2.0]
    assert meta["a.md"][2] == 2  # nchunks


# ---------------------------------------------------------------------------
# grafo semantico: cache, camino numpy vs. camino puro-Python, best-effort
# ---------------------------------------------------------------------------

@pytest.fixture
def isolated_grafo(tmp_path, monkeypatch):
    monkeypatch.setattr(memoria, "INDEX_FILE", str(tmp_path / "index.jsonl"))
    monkeypatch.setattr(memoria, "MEM_DIR", str(tmp_path))
    monkeypatch.setattr(memoria, "GRAFO_CACHE", str(tmp_path / "grafo_cache.json"))
    memoria._guardar_index([
        {"path": "a.md", "dir": "informes", "titulo": "A", "vec": [1.0, 0.0],
         "chunk": "c1", "doc_meta": {}, "calidad": {"estado": "cultivo", "sustancia": 0.5}},
        {"path": "b.md", "dir": "informes", "titulo": "B", "vec": [0.9, 0.1],
         "chunk": "c2", "doc_meta": {}, "calidad": {"estado": "cultivo", "sustancia": 0.5}},
    ])
    return tmp_path


def test_grafo_semantico_numpy_and_pure_python_paths_agree(isolated_grafo, monkeypatch):
    grafo_numpy = memoria.grafo_semantico(umbral=0.5, tope_por_nodo=4)
    memoria.invalidate_grafo_cache()
    monkeypatch.setattr(memoria, "_aristas_numpy", lambda *a, **k: None)
    grafo_puro = memoria.grafo_semantico(umbral=0.5, tope_por_nodo=4)

    edges_numpy = {frozenset((e["a"], e["b"])) for e in grafo_numpy["edges"]}
    edges_puro = {frozenset((e["a"], e["b"])) for e in grafo_puro["edges"]}
    assert edges_numpy == edges_puro
    assert edges_numpy  # the two documents are similar enough to connect


def test_grafo_semantico_reuses_cache_without_recomputing(isolated_grafo, monkeypatch):
    memoria.grafo_semantico()  # first call builds and caches

    def boom():
        raise AssertionError("should not recompute: the cache is still valid")
    monkeypatch.setattr(memoria, "_vectores_por_producto", boom)
    memoria.grafo_semantico()  # must be served entirely from cache


def test_grafo_semantico_survives_fructificacion_failure(isolated_grafo, monkeypatch):
    class _BoomFructificacion:
        def evaluar(self, nodes, edges):
            raise RuntimeError("regla de fructificacion rota")
    monkeypatch.setitem(sys.modules, "fructificacion", _BoomFructificacion())

    grafo = memoria.grafo_semantico()
    assert "nodes" in grafo  # best-effort: a broken rule never breaks the graph


def test_invalidate_grafo_cache_reports_whether_it_removed_anything(isolated_grafo):
    memoria.grafo_semantico()
    assert memoria.invalidate_grafo_cache() is True
    assert memoria.invalidate_grafo_cache() is False


# ---------------------------------------------------------------------------
# main(): CLI degradation -- NTFY_TOPIC_OUT no esta configurado en MAK
# ---------------------------------------------------------------------------

def _mock_cli_deps(monkeypatch, consultar_result):
    monkeypatch.setattr(memoria, "indexar", lambda log=lambda s: None: {
        "archivos": 0, "chunks": 0, "nuevos": 0})
    monkeypatch.setattr(memoria, "load_env", lambda *a, **k: None)
    monkeypatch.setattr(memoria, "marco", lambda tema, activo=True: tema)
    monkeypatch.setattr(memoria, "consultar",
                        lambda tema, k, densidad: consultar_result)


def test_main_buscar_without_topic_returns_error_code(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["memoria.py", "buscar"])
    rc = memoria.main()
    assert rc == 2
    assert "falta el tema" in capsys.readouterr().out


def test_main_index_command_reports_stats(monkeypatch, capsys):
    monkeypatch.setattr(
        memoria, "indexar",
        lambda rebuild=False, log=lambda s: None: {
            "archivos": 3, "chunks": 9, "nuevos": 2})
    monkeypatch.setattr(memoria, "load_env", lambda *a, **k: None)
    monkeypatch.setattr(sys, "argv", ["memoria.py", "index"])
    rc = memoria.main()
    assert rc == 0
    assert "3 archivos, 9 chunks (2 nuevos)" in capsys.readouterr().out


def test_main_reports_empty_memory_plainly_when_vacio(monkeypatch, capsys):
    _mock_cli_deps(monkeypatch, {
        "tema": "x", "sintesis": "", "fuentes": [],
        "meta": {"vacio": True, "ms": 1}})
    monkeypatch.setattr(sys, "argv", ["memoria.py", "un tema nuevo"])
    rc = memoria.main()
    assert rc == 0
    assert "La memoria esta vacia" in capsys.readouterr().out


def test_main_ntfy_false_publish_does_not_crash_or_claim_success(
        monkeypatch, tmp_path, capsys):
    """The core degradation case: NTFY_TOPIC_OUT is unset everywhere on MAK,
    so ntfy_publish() always returns False. --ntfy must still finish cleanly
    and must never print anything claiming the notification was sent."""
    monkeypatch.setattr(memoria, "MEM_DIR", str(tmp_path))
    _mock_cli_deps(monkeypatch, {
        "tema": "x", "sintesis": "hallazgo importante", "fuentes": [],
        "meta": {"n_fuentes": 1, "proveedor": "gemini", "llmCalls": {}, "ms": 5}})
    ntfy_calls = []
    monkeypatch.setattr(
        memoria, "ntfy_publish",
        lambda *a, **k: (ntfy_calls.append(a), False)[1])
    monkeypatch.setattr(sys, "argv", ["memoria.py", "un tema", "--ntfy"])

    rc = memoria.main()

    assert rc == 0
    assert ntfy_calls  # it did try to notify
    out = capsys.readouterr().out.lower()
    assert "enviad" not in out and "notificacion enviada" not in out


def test_main_ntfy_real_absence_is_named_on_stderr_not_hidden(
        monkeypatch, tmp_path, capsys):
    """End-to-end with the real (unmocked) ntfy_publish: an empty
    NTFY_TOPIC_OUT must still name the silence once, on stderr -- not
    pretend the outbound channel is fine."""
    monkeypatch.setattr(memoria, "MEM_DIR", str(tmp_path))
    monkeypatch.delenv("NTFY_TOPIC_OUT", raising=False)
    monkeypatch.setattr(research_lib, "_NTFY_SILENCE_REPORTED", False)
    _mock_cli_deps(monkeypatch, {
        "tema": "x", "sintesis": "hallazgo", "fuentes": [],
        "meta": {"n_fuentes": 1, "proveedor": "gemini", "llmCalls": {}, "ms": 5}})
    monkeypatch.setattr(sys, "argv", ["memoria.py", "un tema", "--ntfy"])

    rc = memoria.main()

    assert rc == 0
    err = capsys.readouterr().err
    assert "NTFY_TOPIC_OUT" in err


# ---------------------------------------------------------------------------
# huecos adicionales
# ---------------------------------------------------------------------------

def test_fragmentar_flushes_buffer_before_starting_a_paragraph_that_fits_alone():
    first = "a" * (memoria.CHUNK - 100)
    second = "b" * 500  # first+second would overflow CHUNK, but second alone fits
    chunks = memoria._fragmentar(first + "\n\n" + second)
    assert chunks == [first, second]


def test_indexar_reraises_and_records_failure_when_local_run_breaks(
        isolated_research, monkeypatch):
    def boom(rebuild=False, log=lambda s: None):
        raise RuntimeError("disco de indice corrupto")
    monkeypatch.setattr(memoria, "_index_unlocked", boom)
    with pytest.raises(RuntimeError, match="disco de indice corrupto"):
        memoria.indexar()


def test_index_unlocked_skips_missing_source_folder(isolated_research, tmp_path):
    import shutil
    shutil.rmtree(Path(memoria.RESEARCH) / "informes")
    stats = memoria._index_unlocked()
    assert stats["archivos"] == 0  # a missing FUENTES folder is skipped, not fatal


def test_index_unlocked_ignores_non_markdown_files(isolated_research):
    (Path(memoria.RESEARCH) / "informes" / "notas.txt").write_text(
        "no es markdown", encoding="utf-8")
    stats = memoria._index_unlocked()
    assert stats["archivos"] == 0


def test_index_unlocked_discards_genuinely_empty_document(isolated_research):
    (Path(memoria.RESEARCH) / "informes" / "vacio.md").write_text(
        "", encoding="utf-8")
    memoria._index_unlocked()
    assert memoria._cargar_index() == []


def test_index_unlocked_drops_a_chunk_whose_embedding_failed_mid_document(
        isolated_research, monkeypatch):
    doc = Path(memoria.RESEARCH) / "informes" / "doc.md"
    doc.write_text("# T\n\n" + ("cuerpo real. " * 60), encoding="utf-8")
    calls = {"n": 0}

    def flaky_embed(texto):
        calls["n"] += 1
        return [] if calls["n"] == 1 else [1.0, 0.0]
    monkeypatch.setattr(memoria, "_embed", flaky_embed)
    monkeypatch.setattr(memoria, "_fragmentar", lambda texto: ["frag uno", "frag dos"])

    memoria._index_unlocked()
    entradas = memoria._cargar_index()
    assert len(entradas) == 1  # the chunk with no vector never made it in
    assert entradas[0]["chunk"] == "frag dos"


def test_vectores_por_producto_skips_entries_with_no_valid_vector(tmp_path, monkeypatch):
    monkeypatch.setattr(memoria, "INDEX_FILE", str(tmp_path / "index.jsonl"))
    memoria._guardar_index([{"path": "a.md", "dir": "informes", "titulo": "A",
                             "vec": None, "chunk": "c1"}])
    vecs, _meta = memoria._vectores_por_producto()
    assert vecs == {}


def test_vectores_por_producto_computes_missing_quality_from_chunks(tmp_path, monkeypatch):
    monkeypatch.setattr(memoria, "INDEX_FILE", str(tmp_path / "index.jsonl"))
    memoria._guardar_index([
        {"path": "a.md", "dir": "corpus", "titulo": "A", "vec": [1.0],
         "chunk": "una obra", "calidad": None},
    ])
    _vecs, meta = memoria._vectores_por_producto()
    assert meta["a.md"][4]["estado"] == "cultivo"  # recomputed via calidad_documento


def test_invalidate_grafo_cache_reports_false_on_permission_error(
        isolated_grafo, monkeypatch):
    memoria.grafo_semantico()

    def boom(_path):
        raise PermissionError("solo lectura")
    monkeypatch.setattr(memoria.os, "unlink", boom)
    assert memoria.invalidate_grafo_cache() is False


def test_aristas_numpy_falls_back_to_none_without_numpy(monkeypatch):
    monkeypatch.setitem(sys.modules, "numpy", None)
    assert memoria._aristas_numpy({"a": [1.0]}, ["a"], {"a": ("d", "t", 1, {}, {})},
                                  0.5, 4) is None


def test_aristas_numpy_returns_no_edges_for_a_single_node():
    vecs = {"a": [1.0, 0.0]}
    meta = {"a": ("informes", "A", 1, {}, {})}
    assert memoria._aristas_numpy(vecs, ["a"], meta, 0.5, 4) == []


def test_firma_index_is_empty_string_when_index_file_is_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(memoria, "INDEX_FILE", str(tmp_path / "no-existe.jsonl"))
    assert memoria._firma_index() == ""


def test_grafo_semantico_draws_explicit_provenance_edge_for_an_idea(
        tmp_path, monkeypatch):
    monkeypatch.setattr(memoria, "INDEX_FILE", str(tmp_path / "index.jsonl"))
    monkeypatch.setattr(memoria, "MEM_DIR", str(tmp_path))
    monkeypatch.setattr(memoria, "GRAFO_CACHE", str(tmp_path / "grafo_cache.json"))
    # Two dissimilar vectors: no affinity edge should form on cosine alone.
    memoria._guardar_index([
        {"path": "origen.md", "dir": "corpus", "titulo": "Obra", "vec": [1.0, 0.0],
         "chunk": "c1", "doc_meta": {}, "calidad": {"estado": "cultivo", "sustancia": 1.0}},
        {"path": "idea.md", "dir": "ideas", "titulo": "Idea", "vec": [0.0, 1.0],
         "chunk": "c2", "doc_meta": {"origen_materia": {"id": "corpus/origen.md"}},
         "calidad": {"estado": "cultivo", "sustancia": 0.5}},
    ])
    grafo = memoria.grafo_semantico(umbral=0.9)
    procedencia = [e for e in grafo["edges"] if e["clase"] == "procedencia"]
    assert procedencia == [{"a": "ideas/idea.md", "b": "corpus/origen.md",
                            "w": 1.0, "clase": "procedencia"}]


def test_grafo_semantico_survives_a_cache_write_failure(isolated_grafo, monkeypatch):
    def boom(*a, **k):
        raise OSError("disco lleno")
    monkeypatch.setattr(memoria.os, "replace", boom)
    grafo = memoria.grafo_semantico()
    assert "nodes" in grafo  # a cache-write failure never breaks the response


def test_limitar_grafo_passthrough_for_invalid_limit_string():
    grafo = {"nodes": [{"id": "a"}], "edges": []}
    assert memoria.limitar_grafo(grafo, "no-es-un-numero") is grafo


def test_limitar_grafo_passthrough_when_under_the_limit():
    grafo = {"nodes": [{"id": "a"}], "edges": []}
    assert memoria.limitar_grafo(grafo, 10) is grafo


def test_escribir_lists_consulted_sources_in_the_markdown(tmp_path, monkeypatch):
    monkeypatch.setattr(memoria, "MEM_DIR", str(tmp_path))
    base = memoria._escribir("mi tema", {
        "sintesis": "hallazgo", "fuentes": [
            {"titulo": "Informe A", "dir": "informes", "score": 0.87, "path": "a.md"}]})
    texto = Path(base + ".md").read_text(encoding="utf-8")
    assert "Informe A (informes, score 0.87) -- a.md" in texto


def test_main_buscar_with_topic_prints_ranked_hits(monkeypatch, capsys):
    monkeypatch.setattr(memoria, "buscar", lambda tema, k: [
        {"score": 0.5, "dir": "informes", "titulo": "T1"}])
    monkeypatch.setattr(sys, "argv", ["memoria.py", "buscar", "mi tema"])
    rc = memoria.main()
    assert rc == 0
    assert "[informes] T1" in capsys.readouterr().out


def test_main_falls_back_to_generic_finding_line_when_synthesis_has_no_prose(
        monkeypatch, capsys):
    _mock_cli_deps(monkeypatch, {
        "tema": "x", "sintesis": "# solo un titulo", "fuentes": [],
        "meta": {"n_fuentes": 3, "proveedor": "gemini", "llmCalls": {}, "ms": 5}})
    monkeypatch.setattr(sys, "argv", ["memoria.py", "un tema"])
    rc = memoria.main()
    assert rc == 0
    assert "HALLAZGO: memoria: 3 fuentes consultadas" in capsys.readouterr().out
