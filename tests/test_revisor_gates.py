"""Offline tests for cultura/mak_plataforma/revisor.py -- the mechanical
reviewer of capataz/* draft PRs.

The enforce_pr() half of this file is the one that lived on ONE disk for ten
days merging PRs by itself (measured 2026-07-30: repo 165 lines, box 216) and
was rescued into the repo in PR #405. These tests pin what that code DOES:
the three static gates, the CI-check parser, and above all the enforcement
contract -- shadow by default, merge ONLY behind --enforce AND a fully green
CI, never close, comment-and-wait on NO-APROBADO. `gh` and `git` never run:
`sh` is faked and records every argv.
"""
import importlib.util
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
REVISOR_PY = RAIZ / "cultura" / "mak_plataforma" / "revisor.py"


def _cargar():
    spec = importlib.util.spec_from_file_location("revisor_bajo_prueba",
                                                  REVISOR_PY)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


revisor = _cargar()


class FakeSh:
    """Replaces revisor.sh: answers by predicate, records every argv."""

    def __init__(self, respuestas=()):
        self.respuestas = list(respuestas)  # [(predicate, (rc, out, err))]
        self.calls = []

    def __call__(self, args):
        self.calls.append(list(args))
        for pred, r in self.respuestas:
            if pred(args):
                return r
        return 0, "", ""

    def hubo(self, *palabras):
        return [c for c in self.calls if all(w in c for w in palabras)]


# -------------------------------------------------------------------- gates

def test_gate_compila_acepta_y_localiza_el_error():
    ok, _ = revisor.gate_compila("x = 1\n")
    assert ok
    ok, msg = revisor.gate_compila("def f(:\n    pass\n")
    assert not ok and "L1" in msg


def test_gate_stdlib_deja_pasar_stdlib_y_frena_terceros():
    ok, _ = revisor.gate_stdlib(
        "import json\nfrom pathlib import Path\nimport os.path\n")
    assert ok
    ok, msg = revisor.gate_stdlib("import requests\nfrom numpy import array\n")
    assert not ok
    assert "numpy" in msg and "requests" in msg


def test_gate_stdlib_ignora_imports_relativos():
    """`from . import x` (level > 0) is first-party by definition."""
    ok, _ = revisor.gate_stdlib("from . import hermano\n")
    assert ok


def test_gate_pedido_exige_que_el_codigo_refleje_el_pedido():
    src = "def contar_lineas(archivo):\n    return len(open(archivo).readlines())\n"
    ok, msg = revisor.gate_pedido(src, "script que cuente contar_lineas de un log")
    assert ok and "contar_lineas" in msg
    ok, msg = revisor.gate_pedido(src, "grafique histograma temperaturas")
    assert not ok and "0 palabras" in msg


def test_gate_pedido_sin_palabras_clave_es_skip_no_veto():
    """A request made only of short words cannot gate anything: pass with a
    'skip' note instead of a false NO-APROBADO."""
    ok, msg = revisor.gate_pedido("print(1)\n", "haz algo ya")
    assert ok and "skip" in msg


# ---------------------------------------------------------------- pedido_de

def test_pedido_de_encuentra_por_sufijo_y_tolera_lineas_rotas(monkeypatch,
                                                              tmp_path):
    jobs = tmp_path / "jobs.jsonl"
    jobs.write_text(
        "esto no es json\n"
        + json.dumps({"job_id": "job-0000aaaa", "pedido": "viejo"}) + "\n"
        + json.dumps({"job_id": "job-1234beef", "pedido": "contar lineas"}) + "\n",
        encoding="utf-8")
    monkeypatch.setattr(revisor, "JOBS", str(jobs))
    assert revisor.pedido_de("beef") == "contar lineas"
    assert revisor.pedido_de("nohay") == ""


# ----------------------------------------------------------------- ci_verde

def test_ci_verde_exige_todos_los_checks_en_pass(monkeypatch):
    tabla_verde = "build\tpass\t1m\nlint\tpass\t10s\n"
    tabla_mixta = "build\tpass\t1m\ntests\tpending\t-\n"
    for tabla, esperado in ((tabla_verde, True), (tabla_mixta, False),
                            ("", False)):
        fake = FakeSh([(lambda a: "checks" in a, (0, tabla, ""))])
        monkeypatch.setattr(revisor, "sh", fake)
        assert revisor.ci_verde(7) is esperado, tabla


# --------------------------------------------------------------- revisar_pr

def _pr_verdicto(monkeypatch, src, pedido="contar lineas en un log"):
    fake = FakeSh([
        (lambda a: a[:2] == ["git", "fetch"], (0, "", "")),
        (lambda a: a[:2] == ["git", "show"], (0, src, "")),
    ])
    monkeypatch.setattr(revisor, "sh", fake)
    monkeypatch.setattr(revisor, "pedido_de", lambda h: pedido)
    veredictos = []
    revisor.revisar_pr(7, "capataz/util-1234beef", "utilidades/x.py",
                       veredictos)
    return veredictos[0]


def test_revisar_pr_pass_cuando_los_tres_gates_pasan(monkeypatch):
    v = _pr_verdicto(monkeypatch,
                     "import json\ndef contar(archivo):\n"
                     "    return len(open(archivo).readlines())  # lineas\n")
    assert v["veredicto"] == "PASS"
    assert v["gates"] == {"compila": True, "stdlib_only": True,
                          "pedido_match": True}


def test_revisar_pr_un_gate_caido_es_no_aprobado(monkeypatch):
    v = _pr_verdicto(monkeypatch, "import requests\n# contar lineas\n")
    assert v["veredicto"] == "NO-APROBADO"
    assert v["gates"]["stdlib_only"] is False


def test_revisar_pr_archivo_ilegible_es_error_no_pass(monkeypatch):
    fake = FakeSh([(lambda a: True, (1, "", "boom"))])
    monkeypatch.setattr(revisor, "sh", fake)
    monkeypatch.setattr(revisor, "pedido_de", lambda h: "")
    veredictos = []
    revisor.revisar_pr(9, "capataz/x-aa", "utilidades/x.py", veredictos)
    assert veredictos[0]["veredicto"] == "ERROR"


# --------------------------------------------------------------- enforce_pr

def test_enforce_pass_con_ci_verde_hace_ready_comenta_y_mergea(monkeypatch):
    fake = FakeSh()
    monkeypatch.setattr(revisor, "sh", fake)
    monkeypatch.setattr(revisor, "ci_verde", lambda n: True)
    assert revisor.enforce_pr({"pr": 7, "veredicto": "PASS"}) == "merged"
    assert fake.hubo("gh", "ready")
    assert fake.hubo("gh", "comment")
    merges = fake.hubo("gh", "merge")
    assert merges and "--squash" in merges[0]
    assert not fake.hubo("gh", "close"), "the reviewer never closes a PR"


def test_enforce_pass_sin_ci_verde_espera_sin_tocar_el_pr(monkeypatch):
    """The half of the lesson that matters: PASS alone is NOT enough. Without
    a green CI the box waits for the next cycle and issues zero gh calls."""
    fake = FakeSh()
    monkeypatch.setattr(revisor, "sh", fake)
    monkeypatch.setattr(revisor, "ci_verde", lambda n: False)
    assert revisor.enforce_pr({"pr": 7, "veredicto": "PASS"}) == "espera-ci"
    assert fake.calls == []


def test_enforce_no_aprobado_comenta_y_no_mergea_ni_cierra(monkeypatch):
    fake = FakeSh()
    monkeypatch.setattr(revisor, "sh", fake)
    monkeypatch.setattr(revisor, "ci_verde",
                        lambda n: (_ for _ in ()).throw(
                            AssertionError("CI is irrelevant to a veto")))
    assert revisor.enforce_pr({"pr": 8, "veredicto": "NO-APROBADO"}) \
        == "no-aprobado"
    assert fake.hubo("gh", "comment")
    assert not fake.hubo("merge") and not fake.hubo("close")


def test_enforce_merge_fallido_se_reporta_no_se_reintenta(monkeypatch):
    fake = FakeSh([(lambda a: "merge" in a, (1, "", "protected branch"))])
    monkeypatch.setattr(revisor, "sh", fake)
    monkeypatch.setattr(revisor, "ci_verde", lambda n: True)
    assert revisor.enforce_pr({"pr": 7, "veredicto": "PASS"}) == "merge-fallo"
    assert len(fake.hubo("gh", "merge")) == 1


# --------------------------------------------------- main: shadow by default

def _main_con(monkeypatch, tmp_path, argv):
    listado = json.dumps([{
        "number": 7, "headRefName": "capataz/util-1234beef", "isDraft": True,
        "files": [{"path": "utilidades/x.py"}, {"path": "README.md"}],
    }, {
        "number": 8, "headRefName": "feature/no-capataz", "isDraft": False,
        "files": [{"path": "src/otro.py"}],
    }])
    fake = FakeSh([
        (lambda a: a[:3] == ["gh", "pr", "list"], (0, listado, "")),
        (lambda a: a[:2] == ["git", "show"],
         (0, "import json\n# contar lineas de un log\n", "")),
        (lambda a: "checks" in a, (0, "build\tpass\t1m\n", "")),
    ])
    monkeypatch.setattr(revisor, "sh", fake)
    monkeypatch.setattr(revisor, "pedido_de", lambda h: "contar lineas")
    monkeypatch.setattr(revisor, "OUT", str(tmp_path / "shadow.json"))
    monkeypatch.setattr(revisor, "LOG", str(tmp_path / "revisor.log"))
    monkeypatch.setattr(sys, "argv", ["revisor.py"] + argv)
    assert revisor.main() == 0
    return fake, json.loads((tmp_path / "shadow.json").read_text())


def test_main_sin_flags_es_shadow_y_no_toca_ningun_pr(monkeypatch, tmp_path):
    """Default mode is observational: it reviews only capataz/* PRs, writes
    the verdict file, and issues NO mutating gh call whatsoever."""
    fake, rep = _main_con(monkeypatch, tmp_path, [])
    assert rep["modo"] == "shadow (observacional)"
    assert [v["pr"] for v in rep["veredictos"]] == [7], "capataz/* only"
    assert rep["veredictos"][0]["veredicto"] == "PASS"
    assert "accion" not in rep["veredictos"][0]
    for mutante in ("merge", "ready", "comment", "close"):
        assert not fake.hubo(mutante), mutante


def test_main_con_enforce_registra_la_accion(monkeypatch, tmp_path):
    fake, rep = _main_con(monkeypatch, tmp_path, ["--enforce"])
    assert rep["modo"] == "enforce"
    assert rep["veredictos"][0]["accion"] == "merged"
    assert fake.hubo("gh", "merge")

def test_solo_mergea_contra_el_buzon(tmp_path, monkeypatch):
    """`enforce_pr` merges, so the reviewer must declare WHICH branch it acts
    against.

    The only filter looked at the HEAD branch (`capataz/*`), which says where
    the PR comes from and not where it goes: a `capataz/*` branch pointing at
    main would be closed by a cron every 6 hours with nobody deciding it. It
    never happened because `entregar.py` always uses `mak` as base, but that
    is another file's habit, not this file's guarantee.

    And an ABSENT field is not a wrong base: treating absence as rejection
    would silence the whole reviewer, which is the failure mode this file
    already had with its own header.
    """
    vistos = []
    monkeypatch.setattr(revisor, "revisar_pr",
                        lambda n, b, p_, v: vistos.append(n))
    prs = [
        {"number": 1, "headRefName": "capataz/x-aaa", "baseRefName": "mak",
         "files": [{"path": "a.py"}]},
        {"number": 2, "headRefName": "capataz/y-bbb", "baseRefName": "main",
         "files": [{"path": "b.py"}]},
        {"number": 3, "headRefName": "capataz/z-ccc",
         "files": [{"path": "c.py"}]},
        {"number": 4, "headRefName": "feature/otra", "baseRefName": "mak",
         "files": [{"path": "d.py"}]},
    ]
    monkeypatch.setattr(revisor, "sh",
                        lambda args: (0, json.dumps(prs), ""))
    monkeypatch.setattr(revisor, "OUT", str(tmp_path / "out.json"))
    monkeypatch.setattr(revisor, "LOG", str(tmp_path / "r.log"))
    monkeypatch.setattr(sys, "argv", ["revisor.py"])

    revisor.main()

    assert 1 in vistos, "a capataz/* PR against the inbox is reviewed"
    assert 2 not in vistos, "a capataz/* PR against MAIN is left alone"
    assert 3 in vistos, "no baseRefName still reviewed: absent != different"
    assert 4 not in vistos, "a branch that is not capataz/* is none of its business"
