"""Offline tests for cultura/mak_curatoria/watchdog.py and panel.py, two of
the curatoria files rescued on 2026-07-30 (they lived on the box only).

watchdog: the decision ladder (finished / paused / stalled / healthy), the
one-issue antispam flag and its re-arming. panel: the process table and the
GPU line degrade instead of crashing. `gh`, `pgrep` and `nvidia-smi` never
run: subprocess is faked; state lives in tmp_path.
"""
import importlib.util
import json
import os
import subprocess
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
CURATORIA = RAIZ / "cultura" / "mak_curatoria"


def _cargar(nombre):
    spec = importlib.util.spec_from_file_location(
        nombre + "_bajo_prueba", CURATORIA / (nombre + ".py"))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


watchdog = _cargar("watchdog")
panel = _cargar("panel")


class FakeRun:
    def __init__(self, respuesta=""):
        self.calls = []
        self.respuesta = respuesta

    def __call__(self, args, **kwargs):
        self.calls.append(list(args))
        return subprocess.CompletedProcess(args, 0, self.respuesta, "")


def _base(monkeypatch, tmp_path, estado=None, mtime=None):
    fake = FakeRun()
    monkeypatch.setattr(watchdog.subprocess, "run", fake)
    monkeypatch.setattr(watchdog, "BASE", tmp_path)
    monkeypatch.setattr(watchdog, "ESTADO", tmp_path / "estado.json")
    monkeypatch.setattr(watchdog, "FLAG", tmp_path / ".watchdog_alerted")
    if estado is not None:
        (tmp_path / "estado.json").write_text(json.dumps(estado))
        if mtime is not None:
            os.utime(tmp_path / "estado.json", (mtime, mtime))
    return fake


def _titulos(fake):
    titulos = []
    for c in fake.calls:
        assert c[:3] == ["gh", "issue", "create"], "watchdog only files issues"
        titulos.append(c[c.index("--title") + 1])
    return titulos


# ----------------------------------------------------------------- watchdog

def test_sin_estado_no_hace_nada(monkeypatch, tmp_path):
    fake = _base(monkeypatch, tmp_path)
    watchdog.main()
    assert fake.calls == []


def test_fin_crea_issue_terminada(monkeypatch, tmp_path):
    fake = _base(monkeypatch, tmp_path,
                 {"procesados": 3132, "total_trabajo": 3132,
                  "pausado_por": "fin"})
    watchdog.main()
    assert _titulos(fake) == ["[CURATORIA] percepcion TERMINADA"]
    cuerpo = fake.calls[0][fake.calls[0].index("--body") + 1]
    assert "3132/3132" in cuerpo
    assert (tmp_path / ".watchdog_alerted").exists(), "flag arms the antispam"


def test_pausa_crea_issue_pausada_con_el_motivo(monkeypatch, tmp_path):
    fake = _base(monkeypatch, tmp_path,
                 {"procesados": 10, "total_trabajo": 100,
                  "pausado_por": "errores_seguidos",
                  "ultimos_errores": ["timeout ollama"]})
    watchdog.main()
    assert _titulos(fake) == ["[CURATORIA] percepcion PAUSADA"]
    cuerpo = fake.calls[0][fake.calls[0].index("--body") + 1]
    assert "errores_seguidos" in cuerpo and "10/100" in cuerpo


def test_estancada_solo_pasados_25_minutos(monkeypatch, tmp_path):
    viejo = time.time() - 30 * 60
    fake = _base(monkeypatch, tmp_path,
                 {"procesados": 5, "total_trabajo": 100}, mtime=viejo)
    watchdog.main()
    assert _titulos(fake) == ["[CURATORIA] percepcion ESTANCADA"]


def test_corrida_sana_ni_alerta_ni_flag(monkeypatch, tmp_path):
    fake = _base(monkeypatch, tmp_path,
                 {"procesados": 5, "total_trabajo": 100},
                 mtime=time.time() - 60)
    watchdog.main()
    assert fake.calls == [], "fresh estado.json and no pause: silence"


def test_flag_evita_el_segundo_issue_y_se_rearma_al_avanzar(monkeypatch,
                                                            tmp_path):
    """Anti-spam: while the flag exists no second issue goes out; one healthy
    pass removes the flag so the NEXT incident notifies again."""
    fake = _base(monkeypatch, tmp_path,
                 {"procesados": 10, "total_trabajo": 100,
                  "pausado_por": "gpu"})
    watchdog.main()
    watchdog.main()
    assert len(fake.calls) == 1, "one incident, one issue"

    # The run resumes and advances: healthy state removes the flag...
    (tmp_path / "estado.json").write_text(
        json.dumps({"procesados": 50, "total_trabajo": 100}))
    watchdog.main()
    assert not (tmp_path / ".watchdog_alerted").exists()

    # ...so a NEW pause files a new issue.
    (tmp_path / "estado.json").write_text(
        json.dumps({"procesados": 60, "total_trabajo": 100,
                    "pausado_por": "fin"}))
    watchdog.main()
    assert len(fake.calls) == 2


def test_estado_corrupto_no_revienta(monkeypatch, tmp_path):
    fake = _base(monkeypatch, tmp_path)
    (tmp_path / "estado.json").write_text("{esto no es json")
    watchdog.main()
    assert fake.calls == []


# -------------------------------------------------------------------- panel

def test_panel_procesos_marca_activo_e_inactivo(monkeypatch):
    def run(args, **kwargs):
        # Only percepcion is alive.
        vivo = "percepcion.py correr" in args
        return subprocess.CompletedProcess(args, 0 if vivo else 1,
                                           "4321\n" if vivo else "", "")
    monkeypatch.setattr(panel.subprocess, "run", run)
    filas = dict(panel.procesos())
    assert filas["percepcion (curatoria)"] == "ACTIVO pid 4321"
    inactivos = [v for k, v in filas.items() if k != "percepcion (curatoria)"]
    assert inactivos and all(v == "inactivo" for v in inactivos)
    assert len(filas) == 5, "the five watched processes, no more no less"


def test_panel_gpu_degrada_a_nd_sin_nvidia_smi(monkeypatch):
    def run(args, **kwargs):
        raise FileNotFoundError("nvidia-smi")
    monkeypatch.setattr(panel.subprocess, "run", run)
    assert panel.gpu() == "n/d"


def test_panel_es_solo_lectura():
    """Its docstring says 'Solo lectura, LAN': the handler answers GET and
    nothing else, and the module never spawns anything but pgrep/nvidia-smi."""
    assert hasattr(panel.H, "do_GET")
    for verbo in ("do_POST", "do_PUT", "do_DELETE"):
        assert not hasattr(panel.H, verbo), verbo
    fuente = (CURATORIA / "panel.py").read_text(encoding="utf-8")
    for marca in ("Popen", "os.system", "shell=True", "kill"):
        assert marca not in fuente, marca
