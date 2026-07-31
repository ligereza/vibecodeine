"""Offline tests for cultura/mak_curatoria/ordenes.py -- the remote-order
handler the ordenes-curatoria workflow invokes on the MAK runner.

The file was rescued on 2026-07-30 (it lived on ONE disk while a workflow in
this repo invoked it by absolute path) and had never been verified running.
Its doctrine is in its own docstring: strict whitelist, NEVER free text. These
tests pin the dispatch table, the branch-name gate and the redeploy sequence
without touching pgrep, git or the box: every subprocess seam is faked.
"""
import importlib.util
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
ORDENES_PY = RAIZ / "cultura" / "mak_curatoria" / "ordenes.py"


def _cargar():
    spec = importlib.util.spec_from_file_location("ordenes_bajo_prueba",
                                                  ORDENES_PY)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


ordenes = _cargar()


class FakeRun:
    """Records subprocess.run calls; answers by prefix of the argv list."""

    def __init__(self, responses=None):
        self.responses = responses or {}
        self.calls = []

    def __call__(self, args, **kwargs):
        self.calls.append(list(args))
        for prefix, (rc, out, err) in self.responses.items():
            if tuple(args[: len(prefix)]) == tuple(prefix):
                return subprocess.CompletedProcess(args, rc, out, err)
        return subprocess.CompletedProcess(args, 0, "", "")


# ------------------------------------------------------------ dispatch table

def test_sin_argumentos_imprime_uso_y_devuelve_2(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["ordenes.py"])
    assert ordenes.main() == 2
    assert "Whitelist" in capsys.readouterr().out


def test_orden_desconocida_devuelve_2_sin_ejecutar_nada(monkeypatch, capsys):
    """The whitelist IS the security model: an unknown order must not reach
    any subprocess. `rm -rf /` arriving via an issue label dies here."""
    fake = FakeRun()
    monkeypatch.setattr(ordenes.subprocess, "run", fake)
    monkeypatch.setattr(ordenes.subprocess, "Popen",
                        lambda *a, **k: (_ for _ in ()).throw(
                            AssertionError("Popen reached")))
    monkeypatch.setattr(sys, "argv", ["ordenes.py", "rm -rf /"])
    assert ordenes.main() == 2
    assert fake.calls == [], "an unknown order must never spawn a process"
    out = capsys.readouterr().out
    assert "orden desconocida" in out


def test_orden_desconocida_se_trunca_a_40_caracteres(monkeypatch, capsys):
    """The echoed order is capped: a hostile 10 KB issue body does not get
    replayed into the workflow log."""
    monkeypatch.setattr(sys, "argv", ["ordenes.py", "x" * 500])
    assert ordenes.main() == 2
    out = capsys.readouterr().out
    assert "x" * 40 in out and "x" * 41 not in out


def test_redeploy_sin_rama_es_orden_desconocida(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["ordenes.py", "redeploy"])
    assert ordenes.main() == 2


# --------------------------------------------------------------- branch gate

def test_rama_re_acepta_ramas_git_normales():
    for rama in ("main", "mak/curatoria-v2", "feature/x_1.2-ok", "a"):
        assert ordenes.RAMA_RE.match(rama), rama


def test_rama_re_rechaza_inyeccion_y_flags():
    """The branch lands in a git argv: no leading dash (option injection), no
    spaces or shell metacharacters, no over-long names."""
    for rama in ("--upload-pack=/bin/sh", "-x", "a b", "a;b", "a$(id)",
                 "a`id`", "", "a" * 82, "ñandu"):
        assert not ordenes.RAMA_RE.match(rama), repr(rama)


def test_redeploy_rama_invalida_no_toca_git(monkeypatch, capsys):
    fake = FakeRun()
    monkeypatch.setattr(ordenes.subprocess, "run", fake)
    assert ordenes.redeploy("--evil") == 1
    assert fake.calls == []
    assert "rama invalida" in capsys.readouterr().out


# ------------------------------------------------------------------ redeploy

def test_redeploy_despliega_percepcion_y_reporter(monkeypatch, tmp_path, capsys):
    """Happy path: fetch, then `git show FETCH_HEAD:<repo path>` for exactly
    percepcion.py and reporter.py, written into BASE."""
    base = tmp_path / "curatoria"
    base.mkdir()
    monkeypatch.setattr(ordenes, "BASE", base)
    fake = FakeRun({
        ("git",): (0, "# deployed source\n", ""),
    })
    monkeypatch.setattr(ordenes.subprocess, "run", fake)

    assert ordenes.redeploy("mak/fix-1") == 0

    assert fake.calls[0][:4] == ["git", "-C", fake.calls[0][2], "fetch"]
    shows = [c for c in fake.calls if "show" in c]
    pedidos = [c[-1] for c in shows]
    assert pedidos == ["FETCH_HEAD:cultura/mak_curatoria/percepcion.py",
                       "FETCH_HEAD:cultura/mak_curatoria/reporter.py"]
    assert (base / "percepcion.py").read_text() == "# deployed source\n"
    assert (base / "reporter.py").read_text() == "# deployed source\n"
    assert "redeploy OK" in capsys.readouterr().out


def test_redeploy_fetch_fallido_aborta_sin_escribir(monkeypatch, tmp_path):
    base = tmp_path / "curatoria"
    base.mkdir()
    monkeypatch.setattr(ordenes, "BASE", base)
    fake = FakeRun({("git",): (1, "", "fatal: rama no existe")})
    monkeypatch.setattr(ordenes.subprocess, "run", fake)

    assert ordenes.redeploy("no-existe") == 1
    assert list(base.iterdir()) == [], "a failed fetch must deploy nothing"


def test_redeploy_archivo_ausente_en_rama_corta_el_despliegue(monkeypatch,
                                                              tmp_path):
    """If `git show` fails for the first file, the second is not deployed:
    no half-updated pair on the box."""
    base = tmp_path / "curatoria"
    base.mkdir()

    def run(args, **kwargs):
        if "fetch" in args:
            return subprocess.CompletedProcess(args, 0, "", "")
        return subprocess.CompletedProcess(args, 128, "", "does not exist")

    monkeypatch.setattr(ordenes, "BASE", base)
    monkeypatch.setattr(ordenes.subprocess, "run", run)
    assert ordenes.redeploy("main") == 1
    assert list(base.iterdir()) == []


# ------------------------------------------------------- estado / pausar / reanudar

def test_estado_reporta_pid_estado_y_reporte(monkeypatch, tmp_path, capsys):
    base = tmp_path
    (base / "estado.json").write_text('{"procesados": 7}')
    (base / "reportes").mkdir()
    (base / "reportes" / "REPORTE_CURATORIA.md").write_text(
        "# REPORTE\nlinea2\n")
    monkeypatch.setattr(ordenes, "BASE", base)
    monkeypatch.setattr(ordenes, "_pid", lambda: "4242")

    assert ordenes.estado() == 0
    out = capsys.readouterr().out
    assert "PID: 4242" in out
    assert '"procesados": 7' in out
    assert "# REPORTE" in out


def test_estado_sin_archivos_no_revienta(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(ordenes, "BASE", tmp_path)
    monkeypatch.setattr(ordenes, "_pid", lambda: None)
    assert ordenes.estado() == 0
    assert "no corre" in capsys.readouterr().out


def test_pausar_cuando_no_corre_es_idempotente(monkeypatch, capsys):
    fake = FakeRun()
    monkeypatch.setattr(ordenes.subprocess, "run", fake)
    monkeypatch.setattr(ordenes, "_pid", lambda: None)
    assert ordenes.pausar() == 0
    assert fake.calls == [], "nothing running -> no kill"
    assert "ya estaba detenida" in capsys.readouterr().out


def test_pausar_envia_sigterm_al_pid_correcto(monkeypatch, capsys):
    fake = FakeRun()
    pids = iter(["1234", None])  # alive before kill, gone after
    monkeypatch.setattr(ordenes.subprocess, "run", fake)
    monkeypatch.setattr(ordenes, "_pid", lambda: next(pids))
    monkeypatch.setattr(ordenes.time, "sleep", lambda s: None)
    assert ordenes.pausar() == 0
    assert ["kill", "1234"] in fake.calls
    assert "detenida" in capsys.readouterr().out


def test_reanudar_cuando_ya_corre_no_relanza(monkeypatch, capsys):
    monkeypatch.setattr(ordenes, "_pid", lambda: "99")
    monkeypatch.setattr(ordenes.subprocess, "Popen",
                        lambda *a, **k: (_ for _ in ()).throw(
                            AssertionError("must not relaunch")))
    assert ordenes.reanudar() == 0
    assert "ya corre" in capsys.readouterr().out


def test_reanudar_lanza_percepcion_y_devuelve_1_si_no_arranca(monkeypatch,
                                                              tmp_path):
    lanzados = []
    monkeypatch.setattr(ordenes, "BASE", tmp_path)
    pids = iter([None, None])  # not running before, still absent after launch
    monkeypatch.setattr(ordenes, "_pid", lambda: next(pids))
    monkeypatch.setattr(ordenes.subprocess, "Popen",
                        lambda cmd, **k: lanzados.append(cmd))
    monkeypatch.setattr(ordenes.time, "sleep", lambda s: None)

    assert ordenes.reanudar() == 1, "no PID after launch is a failure"
    assert lanzados == [ordenes.CMD_CORRER]
    assert "percepcion.py" in " ".join(ordenes.CMD_CORRER)
    assert (tmp_path / "percepcion.log").exists(), "output goes to the log"
