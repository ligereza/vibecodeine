"""Tests para mantenimiento.py -- F1b: mantenimiento dry-run-first de MAK.

Cubre las 4 tareas (limpiar, archivar, relanzar, ratchet) + el dispatch
mantener() + la integracion con capataz.ejecutar("mantener", ...).
"""
from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from cultura.mak_plataforma import capataz, mantenimiento


# ---------------------------------------------------------------------
# limpiar_temporales
# ---------------------------------------------------------------------

def _preparar_temporales(base: Path) -> None:
    (base / "a.tmp").write_text("x", encoding="utf-8")
    (base / "b.log.old").write_text("x", encoding="utf-8")
    (base / "conservar.py").write_text("x", encoding="utf-8")
    pycache = base / "sub" / "__pycache__"
    pycache.mkdir(parents=True)
    (pycache / "modulo.pyc").write_text("x", encoding="utf-8")
    pytest_cache = base / ".pytest_cache"
    pytest_cache.mkdir()
    (pytest_cache / "v" / "cache").mkdir(parents=True)


def test_limpiar_temporales_dry_no_borra_nada(tmp_path: Path):
    _preparar_temporales(tmp_path)
    reporte = mantenimiento.limpiar_temporales(base=str(tmp_path), execute=False)

    assert reporte["execute"] is False
    assert reporte["eliminados"] == []
    assert reporte["errores"] == []
    # candidatos incluyen los 2 archivos y los 2 directorios frozen
    assert any(c.endswith("a.tmp") for c in reporte["candidatos"])
    assert any(c.endswith("b.log.old") for c in reporte["candidatos"])
    assert any("__pycache__" in c for c in reporte["candidatos"])
    assert any(".pytest_cache" in c for c in reporte["candidatos"])
    # nada tocado en disco
    assert (tmp_path / "a.tmp").exists()
    assert (tmp_path / "b.log.old").exists()
    assert (tmp_path / "sub" / "__pycache__").exists()
    assert (tmp_path / ".pytest_cache").exists()
    assert (tmp_path / "conservar.py").exists()


def test_limpiar_temporales_execute_borra_solo_los_candidatos(tmp_path: Path):
    _preparar_temporales(tmp_path)
    reporte = mantenimiento.limpiar_temporales(base=str(tmp_path), execute=True)

    assert reporte["execute"] is True
    assert set(reporte["eliminados"]) == set(reporte["candidatos"])
    assert not (tmp_path / "a.tmp").exists()
    assert not (tmp_path / "b.log.old").exists()
    assert not (tmp_path / "sub" / "__pycache__").exists()
    assert not (tmp_path / ".pytest_cache").exists()
    # lo que no matchea el patron frozen sigue vivo
    assert (tmp_path / "conservar.py").exists()


# ---------------------------------------------------------------------
# archivar_reportes
# ---------------------------------------------------------------------

def _crear_md(dir_: Path, nombre: str, hace_segundos: float) -> Path:
    p = dir_ / nombre
    p.write_text("contenido " + nombre, encoding="utf-8")
    ts = time.time() - hace_segundos
    import os
    os.utime(p, (ts, ts))
    return p


def test_archivar_reportes_dry_plan_respeta_keep(tmp_path: Path):
    # 5 reportes, keep=3 -> 2 mas viejos van a archivar
    for i in range(5):
        _crear_md(tmp_path, "r%d.md" % i, hace_segundos=i * 100)

    reporte = mantenimiento.archivar_reportes(str(tmp_path), keep=3, execute=False)

    assert reporte["execute"] is False
    assert reporte["total"] == 5
    assert reporte["quedan"] == 3
    assert len(reporte["a_archivar"]) == 2
    assert reporte["archivados"] == []
    # los mas viejos (r3, r4) son los que se archivarian
    assert set(reporte["a_archivar"]) == {"r3.md", "r4.md"}
    # nada se movio
    assert not (tmp_path / "archive").exists()


def test_archivar_reportes_execute_mueve_y_conserva_keep(tmp_path: Path):
    for i in range(5):
        _crear_md(tmp_path, "r%d.md" % i, hace_segundos=i * 100)

    reporte = mantenimiento.archivar_reportes(str(tmp_path), keep=3, execute=True)

    assert reporte["execute"] is True
    assert set(reporte["archivados"]) == {"r3.md", "r4.md"}
    archive_dir = tmp_path / "archive"
    assert (archive_dir / "r3.md").exists()
    assert (archive_dir / "r4.md").exists()
    # los movidos ya no estan en el dir original
    assert not (tmp_path / "r3.md").exists()
    assert not (tmp_path / "r4.md").exists()
    # los conservados (keep=3, los mas nuevos) siguen en su lugar
    assert (tmp_path / "r0.md").exists()
    assert (tmp_path / "r1.md").exists()
    assert (tmp_path / "r2.md").exists()


def test_archivar_reportes_dir_no_existe_reporta_nota(tmp_path: Path):
    inexistente = tmp_path / "no_existe"
    reporte = mantenimiento.archivar_reportes(str(inexistente), keep=20, execute=False)

    assert reporte["a_archivar"] == []
    assert reporte.get("nota") == "dir no existe"


# ---------------------------------------------------------------------
# relanzar_organos
# ---------------------------------------------------------------------

def _mock_pgrep_uno_muerto(cmd, **kwargs):
    # cmd = ["pgrep", "-f", patron]; el segundo organo (codex) esta muerto
    patron = cmd[2]
    if patron == "codex/interfaz_codex.py":
        return MagicMock(returncode=1, stdout="", stderr="")
    return MagicMock(returncode=0, stdout="12345\n", stderr="")


def _mock_pgrep_todos_vivos(cmd, **kwargs):
    return MagicMock(returncode=0, stdout="999\n", stderr="")


def test_relanzar_organos_dry_reporta_vivo_pid_y_no_dispara_nada():
    with patch("subprocess.run", side_effect=_mock_pgrep_uno_muerto) as mock_run:
        reporte = mantenimiento.relanzar_organos(execute=False)

    assert reporte["execute"] is False
    assert reporte["accion"] == "ninguna"
    organos_por_nombre = {o["nombre"]: o for o in reporte["organos"]}
    assert organos_por_nombre["hub"]["vivo"] is True
    assert organos_por_nombre["hub"]["pid"] == "12345"
    assert organos_por_nombre["codex_interfaz"]["vivo"] is False
    assert organos_por_nombre["codex_interfaz"]["pid"] is None
    # nunca se invoco el watchdog en modo dry
    for llamada in mock_run.call_args_list:
        args = llamada[0][0]
        assert "watchdog_mak.sh" not in " ".join(str(a) for a in args)


def test_relanzar_organos_execute_con_muerto_dispara_watchdog_una_vez():
    llamadas = []

    def _fake_run(cmd, **kwargs):
        llamadas.append(cmd)
        if cmd[0] == "pgrep":
            return _mock_pgrep_uno_muerto(cmd, **kwargs)
        return MagicMock(returncode=0, stdout="revivido", stderr="")

    with patch("subprocess.run", side_effect=_fake_run):
        reporte = mantenimiento.relanzar_organos(execute=True)

    assert reporte["accion"] == "watchdog_disparado"
    assert reporte["rc"] == 0
    disparos = [c for c in llamadas if "watchdog_mak.sh" in " ".join(str(a) for a in c)]
    assert len(disparos) == 1


def test_relanzar_organos_execute_todos_vivos_no_dispara_watchdog():
    with patch("subprocess.run", side_effect=_mock_pgrep_todos_vivos) as mock_run:
        reporte = mantenimiento.relanzar_organos(execute=True)

    assert reporte["accion"] == "ninguna"
    for llamada in mock_run.call_args_list:
        args = llamada[0][0]
        assert "watchdog_mak.sh" not in " ".join(str(a) for a in args)


def test_relanzar_organos_pgrep_no_disponible_marca_vivo_none():
    with patch("subprocess.run", side_effect=FileNotFoundError("no pgrep")):
        reporte = mantenimiento.relanzar_organos(execute=False)

    assert all(o["vivo"] is None for o in reporte["organos"])
    assert reporte["accion"] == "ninguna"


# ---------------------------------------------------------------------
# regla viva: nunca pkill / kill / terminar procesos
# ---------------------------------------------------------------------

def test_mantenimiento_source_nunca_contiene_pkill():
    ruta = Path(__file__).resolve().parents[1] / "cultura" / "mak_plataforma" / "mantenimiento.py"
    fuente = ruta.read_text(encoding="utf-8")
    assert "pkill" not in fuente


# ---------------------------------------------------------------------
# correr_ratchet
# ---------------------------------------------------------------------

def test_correr_ratchet_dry_reporta_existencia():
    reporte = mantenimiento.correr_ratchet(execute=False)
    assert reporte["execute"] is False
    rutas = {r["ruta"]: r["existe"] for r in reporte["ratchets"]}
    assert "tests/test_utilidades_mak_sanidad.py" in rutas
    assert "tests/test_mak_salud_proveedores.py" in rutas
    # en este repo ambos existen de verdad
    assert rutas["tests/test_utilidades_mak_sanidad.py"] is True
    assert rutas["tests/test_mak_salud_proveedores.py"] is True


def test_correr_ratchet_execute_compone_comando_pytest():
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stdout="1 passed", stderr="")
        reporte = mantenimiento.correr_ratchet(execute=True)

    assert reporte["rc"] == 0
    assert "1 passed" in reporte["stdout_tail"]
    args = mock_run.call_args[0][0]
    assert args[1:3] == ["-m", "pytest"]
    assert "tests/test_utilidades_mak_sanidad.py" in args
    assert "tests/test_mak_salud_proveedores.py" in args
    kwargs = mock_run.call_args[1]
    assert kwargs["cwd"] == mantenimiento.RAIZ_REPO


# ---------------------------------------------------------------------
# mantener() dispatch
# ---------------------------------------------------------------------

def test_mantener_tarea_desconocida_ok_false():
    reporte = mantenimiento.mantener("nada")
    assert reporte["ok"] is False
    assert "tarea desconocida" in reporte["error"]


def test_mantener_todo_devuelve_las_4_tareas():
    reporte = mantenimiento.mantener("todo", execute=False)
    assert set(reporte.keys()) == {"limpiar", "archivar", "relanzar", "ratchet"}
    for sub in reporte.values():
        assert sub["execute"] is False


def test_mantener_archivar_usa_dir_reportes_kwarg(tmp_path: Path):
    _crear_md(tmp_path, "solo.md", hace_segundos=0)
    reporte = mantenimiento.mantener("archivar", execute=False,
                                     dir_reportes=str(tmp_path), keep=20)
    assert reporte["total"] == 1
    assert reporte["a_archivar"] == []


# ---------------------------------------------------------------------
# integracion con capataz
# ---------------------------------------------------------------------

def test_mantener_en_acciones_de_capataz():
    assert "mantener" in capataz.ACCIONES


def test_capataz_validar_acepta_mantener():
    ok, err = capataz.validar({"accion": "mantener", "args": {"tarea": "todo"}})
    assert ok is True
    assert err is None


def test_capataz_ejecutar_mantener_siempre_dry_run(monkeypatch):
    recibido = {}

    def _stub_mantener(tarea, execute=False, **kwargs):
        recibido["tarea"] = tarea
        recibido["execute"] = execute
        return {"total": 3}

    monkeypatch.setattr(mantenimiento, "mantener", _stub_mantener)

    resultado = capataz.ejecutar("mantener", {"tarea": "ratchet"})

    assert resultado["ok"] is True
    assert resultado["tarea"] == "ratchet"
    assert json.loads(resultado["reporte"]) == {"total": 3}
    assert recibido["tarea"] == "ratchet"
    assert recibido["execute"] is False
