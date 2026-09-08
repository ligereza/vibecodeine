"""Tests para calidad_loop.py -- fixtures jsonl/backlog sinteticas + asserts
de tasas del loop codex (F2a baseline)."""
from __future__ import annotations

import datetime
import json
from pathlib import Path

import pytest

from cultura.mak_plataforma.calidad_loop import (
    cargar_backlog,
    cargar_entregados,
    cargar_jobs,
    causas_rechazo,
    edad_backlog,
    render_md,
    tasas_entrega,
)


def _escribir_jsonl(path: Path, lineas: list) -> Path:
    with path.open("w", encoding="utf-8") as f:
        for l in lineas:
            if isinstance(l, str):
                f.write(l + "\n")
            else:
                f.write(json.dumps(l, ensure_ascii=False) + "\n")
    return path


# ---------------------------------------------------------------------------
# cargar_jobs
# ---------------------------------------------------------------------------

def test_cargar_jobs_archivo_inexistente() -> None:
    assert cargar_jobs("/ruta/inexistente/jobs.jsonl") == []


def test_cargar_jobs_vacio(tmp_path: Path) -> None:
    jf = tmp_path / "jobs.jsonl"
    jf.write_text("", encoding="utf-8")
    assert cargar_jobs(str(jf)) == []


def test_cargar_jobs_tolera_corrupcion_y_exige_job_id(tmp_path: Path) -> None:
    jf = tmp_path / "jobs.jsonl"
    _escribir_jsonl(jf, [
        {"job_id": "j1", "estado": "listo", "path": "j1.md"},
        "esto no es json valido {",
        {"estado": "listo", "path": "sin-id.md"},  # sin job_id -- se descarta
        "",  # linea vacia -- se salta
        {"job_id": "j2", "estado": "FALLO"},
    ])
    jobs = cargar_jobs(str(jf))
    assert [j["job_id"] for j in jobs] == ["j1", "j2"]


# ---------------------------------------------------------------------------
# tasas_entrega -- estados mixtos + campos faltantes
# ---------------------------------------------------------------------------

def _job(job_id, estado="listo", **extra):
    j = {"job_id": job_id, "estado": estado, "path": job_id + ".md",
         "pedido": "algo", "error": "", "t": "10:00:00", "ms": 100}
    j.update(extra)
    return j


def test_tasas_entrega_estados_mixtos() -> None:
    jobs = [
        _job("j-ok1", "listo", smoke_ok=True),
        _job("j-ok2", "listo", smoke_ok=True),
        _job("j-smoke-fail", "listo", smoke_ok=False, smoke_stderr_tail="boom"),
        _job("j-smoke-desconocido", "listo"),  # sin smoke_ok -- ni pasa ni falla
        _job("j-fallo", "FALLO", error="rc=1"),
        _job("j-bloqueado", "BLOQUEADO",
             error="guardia de codigo: RECHAZADO -- pedido dual-use"),
        _job("j-en-cola", "en cola"),
        _job("j-corriendo", "corriendo"),
    ]
    t = tasas_entrega(jobs, entregados=None)

    assert t["total"] == 8
    assert t["en_progreso"] == 2
    assert t["terminales"] == 6
    assert t["generados_listo"] == 4  # los 4 "listo" (incluye smoke desconocido)
    assert t["fallo_sandbox"] == 1
    assert t["bloqueado_guardia"] == 1
    assert t["rechazado_smoke"] == 1
    assert t["smoke_desconocido"] == 1
    # sin codex_delivered.json -> desconocido, NUNCA 0
    assert t["entregados"] is None
    assert t["entrega_pct"] is None


def test_tasas_entrega_con_entregados() -> None:
    jobs = [
        _job("j-ok1", "listo", smoke_ok=True),
        _job("j-ok2", "listo", smoke_ok=True),
        _job("j-ok3", "listo", smoke_ok=True),
    ]
    t = tasas_entrega(jobs, entregados={"j-ok1", "j-ok2", "j-nunca-generado"})

    assert t["generados_listo"] == 3
    assert t["entregados"] == 2  # j-ok3 no esta en entregados
    assert t["entrega_pct"] == pytest.approx(66.7, abs=0.05)


def test_tasas_entrega_excluye_modos_no_generar() -> None:
    """revisar/testear/debug pueden terminar 'listo'/'FALLO' sin haber
    pasado por generar.py; no deben inflar generados_listo/fallo_sandbox ni
    la tasa de entrega (nunca son elegibles para entregar.py)."""
    jobs = [
        _job("j-gen-ok", "listo", modo="generar", smoke_ok=True),
        _job("j-revisar-listo", "listo", modo="revisar"),
        _job("j-testear-fallo", "FALLO", modo="testear", error="assert x"),
        _job("j-debug-listo", "listo", modo="debug"),
    ]
    t = tasas_entrega(jobs, entregados={"j-gen-ok"})

    assert t["generados_listo"] == 1  # solo j-gen-ok
    assert t["fallo_sandbox"] == 0  # j-testear-fallo no cuenta (modo distinto)
    assert t["entregados"] == 1
    assert t["entrega_pct"] == 100.0


def test_causas_rechazo_excluye_modos_no_generar() -> None:
    jobs = [
        _job("j-gen-fallo", "FALLO", modo="generar", error="rc=1"),
        _job("j-testear-fallo", "FALLO", modo="testear", error="assert x"),
        _job("j-gen-smoke-fail", "listo", modo="generar", smoke_ok=False,
             smoke_stderr_tail="AssertionError: x"),
        _job("j-revisar-listo", "listo", modo="revisar", smoke_ok=False,
             smoke_stderr_tail="ValueError: no deberia contar"),
    ]
    c = causas_rechazo(jobs)

    assert c["fallo_sandbox_n"] == 1  # solo el de modo generar
    assert c["rechazado_smoke_n"] == 1  # solo el de modo generar
    assert c["rechazado_smoke_causas"] == {"AssertionError": 1}


def test_tasas_entrega_vacio() -> None:
    t = tasas_entrega([], entregados=None)
    assert t["total"] == 0
    assert t["generados_listo"] == 0
    assert t["entregados"] is None


def test_tasas_entrega_listos_vacio_con_entregados_da_pct_cero() -> None:
    jobs = [_job("j1", "FALLO")]
    t = tasas_entrega(jobs, entregados=set())
    assert t["generados_listo"] == 0
    assert t["entregados"] == 0
    assert t["entrega_pct"] == 0.0


# ---------------------------------------------------------------------------
# cargar_entregados
# ---------------------------------------------------------------------------

def test_cargar_entregados_ausente() -> None:
    assert cargar_entregados("/ruta/inexistente/codex_delivered.json") is None


def test_cargar_entregados_valido(tmp_path: Path) -> None:
    ef = tmp_path / "codex_delivered.json"
    ef.write_text(json.dumps({"entregados": ["j1", "j2"], "slugs": ["a"]}),
                  encoding="utf-8")
    assert cargar_entregados(str(ef)) == {"j1", "j2"}


def test_cargar_entregados_corrupto(tmp_path: Path) -> None:
    ef = tmp_path / "codex_delivered.json"
    ef.write_text("{ no cierra", encoding="utf-8")
    assert cargar_entregados(str(ef)) is None


# ---------------------------------------------------------------------------
# causas_rechazo
# ---------------------------------------------------------------------------

def test_causas_rechazo_agrupa_por_veredicto_y_excepcion() -> None:
    jobs = [
        _job("j1", "BLOQUEADO",
             error="guardia de codigo: RECHAZADO -- pedido dual-use"),
        _job("j2", "BLOQUEADO",
             error="guardia de codigo: RECHAZADO -- otro pedido"),
        _job("j3", "BLOQUEADO", error="algo sin el formato esperado"),
        _job("j4", "listo", smoke_ok=False,
             smoke_stderr_tail="Traceback...\nAssertionError: esperaba 3"),
        _job("j5", "listo", smoke_ok=False,
             smoke_stderr_tail="Traceback...\nAssertionError: otro caso"),
        _job("j6", "listo", smoke_ok=False, smoke_stderr_tail=""),
        _job("j7", "FALLO", error="timeout"),
        _job("j8", "listo", smoke_ok=True),  # no cuenta como rechazo
    ]
    c = causas_rechazo(jobs)

    assert c["bloqueado_guardia_n"] == 3
    assert c["bloqueado_guardia_causas"]["RECHAZADO"] == 2
    assert c["bloqueado_guardia_causas"]["algo sin el formato esperado"] == 1

    assert c["rechazado_smoke_n"] == 3
    assert c["rechazado_smoke_causas"]["AssertionError"] == 2
    assert c["rechazado_smoke_causas"]["desconocido"] == 1

    assert c["fallo_sandbox_n"] == 1


def test_causas_rechazo_vacio() -> None:
    c = causas_rechazo([])
    assert c["bloqueado_guardia_n"] == 0
    assert c["bloqueado_guardia_causas"] == {}
    assert c["rechazado_smoke_n"] == 0
    assert c["fallo_sandbox_n"] == 0


# ---------------------------------------------------------------------------
# backlog: cargar + edad
# ---------------------------------------------------------------------------

def test_cargar_backlog_ignora_comentarios_y_vacias(tmp_path: Path) -> None:
    bf = tmp_path / "backlog_codex.txt"
    bf.write_text(
        "# comentario de cabecera\n"
        "\n"
        "una tarea manual sin fecha\n"
        "otra tarea con marcador # auto 20260701\n",
        encoding="utf-8",
    )
    lineas = cargar_backlog(str(bf))
    assert lineas == [
        "una tarea manual sin fecha",
        "otra tarea con marcador # auto 20260701",
    ]


def test_cargar_backlog_inexistente() -> None:
    assert cargar_backlog("/ruta/inexistente/backlog_codex.txt") == []


def test_edad_backlog_con_fechas_y_sin_fechas() -> None:
    hoy = datetime.date(2026, 7, 22)
    lineas = [
        "tarea manual vieja sin marcador",  # sin_fecha
        "tarea auto reciente # auto 20260720",  # 2 dias
        "tarea auto vieja # auto 20260701",  # 21 dias
        "otra tarea manual sin marcador",  # sin_fecha
    ]
    r = edad_backlog(lineas, hoy=hoy)

    assert r["total_pendientes"] == 4
    assert r["con_fecha"] == 2
    assert r["sin_fecha"] == 2
    assert r["edad_min_dias"] == 2
    assert r["edad_max_dias"] == 21
    assert r["edad_prom_dias"] == pytest.approx(11.5)


def test_edad_backlog_vacio() -> None:
    r = edad_backlog([])
    assert r["total_pendientes"] == 0
    assert r["con_fecha"] == 0
    assert r["sin_fecha"] == 0
    assert r["edad_min_dias"] is None
    assert r["edad_max_dias"] is None
    assert r["edad_prom_dias"] is None


def test_edad_backlog_todas_sin_fecha() -> None:
    r = edad_backlog(["tarea a mano 1", "tarea a mano 2"])
    assert r["total_pendientes"] == 2
    assert r["con_fecha"] == 0
    assert r["sin_fecha"] == 2
    assert r["edad_min_dias"] is None


def test_edad_backlog_fecha_invalida_cuenta_como_sin_fecha() -> None:
    # dia 99 no existe -- strptime debe fallar -> tratado como sin_fecha
    r = edad_backlog(["tarea rota # auto 20269999"])
    assert r["con_fecha"] == 0
    assert r["sin_fecha"] == 1


# ---------------------------------------------------------------------------
# render_md
# ---------------------------------------------------------------------------

def test_render_md_basico() -> None:
    jobs = [
        _job("j1", "listo", smoke_ok=True),
        _job("j2", "listo", smoke_ok=False, smoke_stderr_tail="AssertionError: x"),
        _job("j3", "BLOQUEADO", error="guardia de codigo: RECHAZADO -- x"),
    ]
    entrega = tasas_entrega(jobs, entregados={"j1"})
    causas = causas_rechazo(jobs)
    backlog = edad_backlog(["tarea # auto 20260701"], hoy=datetime.date(2026, 7, 22))

    md = render_md(entrega, causas, backlog)

    assert "# Calidad del Loop Codex (F2a -- baseline)" in md
    assert "## Loop generar -> entregar" in md
    assert "## Bugs cazados por el ratchet (rechazos por causa)" in md
    assert "## Edad del backlog codex" in md
    assert "**Generados (listo)**: 2" in md
    assert "**Entregados (PR draft abierto)**: 1" in md
    assert "RECHAZADO" in md
    assert "AssertionError" in md
    assert "**Edad maxima**: 21 dias" in md


def test_render_md_vacio_no_revienta() -> None:
    entrega = tasas_entrega([], entregados=None)
    causas = causas_rechazo([])
    backlog = edad_backlog([])

    md = render_md(entrega, causas, backlog)

    assert "# Calidad del Loop Codex (F2a -- baseline)" in md
    assert "**Entregados (PR draft abierto)**: —" in md
    assert "**Edad minima**: —" in md
