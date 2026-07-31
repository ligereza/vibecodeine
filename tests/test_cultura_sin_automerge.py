"""Guard rails over the rescued one-disk code (the enforce_pr lesson).

Measured 2026-07-30: the box ran `revisor.py --enforce` every 6 hours and its
enforce_pr() -- 51 lines that merge PRs by themselves -- existed on ONE disk,
unreviewed and unbacked. The rescue brought that code INTO the repo (PR #405)
where it is now reviewed and pinned by tests/test_revisor_gates.py. These
guards keep the shape of that lesson:

1. Exactly ONE auto-merge path exists in first-party cultura/ code, and it is
   the reviewed one in revisor.py. A second one appearing anywhere -- or the
   first one moving -- turns this red, so a legitimate future feature has to
   edit THIS file consciously, with the review that edit implies.
2. Enforcement stays a deliberate flag: shadow by default, `--enforce` visible
   in exactly one crontab line.
3. The mechanical modules stay mechanical (no model), in the exact style of
   tests/test_vigia.py::test_no_hay_modelo_en_el_vigia.
4. The xio monitor stays a READ-ONLY eye: GET-only, hard route allowlist.
"""
import ast
import re
import warnings
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
CULTURA = RAIZ / "cultura"

# The invocation shapes that mean "this code can merge a PR on its own".
# Prose and comments about merging do not match; argv lists, shell lines and
# API paths do.
MARCAS_AUTOMERGE = (
    re.compile(r"enforce_pr"),
    re.compile(r"gh['\"\s,\]\[]+pr['\"\s,\]\[]+merge"),
    re.compile(r"pulls/[^\s\"']*/merge"),
    re.compile(r"merge_method"),
    re.compile(r"auto[-_]merge", re.IGNORECASE),
)

# The ONE reviewed auto-merge path. Adding a path here is a conscious,
# reviewed decision -- that is the point of this list.
AUTOMERGE_PERMITIDO = {"cultura/mak_plataforma/revisor.py"}


def _fuentes_cultura():
    for patron in ("*.py", "*.sh"):
        for f in sorted(CULTURA.rglob(patron)):
            yield f


def _solo_codigo(path):
    """The scanned text minus prose: coherence.py's docstring DESCRIBES
    enforce_pr (it measured the drift) and must not trip a guard about code
    that EXECUTES it. Docstrings are blanked via ast; comments are cut at the
    first '#' (a commented-out merge cannot run either way)."""
    texto = path.read_text(encoding="utf-8", errors="replace")
    lineas = texto.splitlines()
    if path.suffix == ".py":
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")  # scanned sources' own escapes
                arbol = ast.parse(texto)
        except SyntaxError:
            arbol = None
        if arbol is not None:
            for nodo in ast.walk(arbol):
                cuerpo = getattr(nodo, "body", None)
                if (isinstance(nodo, (ast.Module, ast.FunctionDef,
                                      ast.AsyncFunctionDef, ast.ClassDef))
                        and cuerpo and isinstance(cuerpo[0], ast.Expr)
                        and isinstance(cuerpo[0].value, ast.Constant)
                        and isinstance(cuerpo[0].value.value, str)):
                    doc = cuerpo[0]
                    for i in range(doc.lineno - 1, doc.end_lineno):
                        lineas[i] = ""
    return "\n".join(ln.split("#", 1)[0] for ln in lineas)


def test_solo_el_revisor_tiene_un_camino_de_automerge():
    con_marca = set()
    for f in _fuentes_cultura():
        texto = _solo_codigo(f)
        if any(m.search(texto) for m in MARCAS_AUTOMERGE):
            con_marca.add(f.relative_to(RAIZ).as_posix())
    assert con_marca == AUTOMERGE_PERMITIDO, (
        "an auto-merge path appeared outside the reviewed allowlist "
        "(or the reviewed one moved). If this is a deliberate, reviewed "
        "feature, edit AUTOMERGE_PERMITIDO in this test in the same PR: %r"
        % sorted(con_marca ^ AUTOMERGE_PERMITIDO))


def test_el_enforcement_del_revisor_es_una_bandera_no_el_default():
    """The behavioral contract lives in test_revisor_gates.py (main() without
    --enforce issues zero mutating gh calls). Here the SOURCE shape is pinned:
    enforce_pr is invoked in exactly one place, guarded by args.enforce."""
    src = (CULTURA / "mak_plataforma" / "revisor.py").read_text(
        encoding="utf-8")
    llamadas = [ln for ln in src.splitlines()
                if "enforce_pr(" in ln and not ln.strip().startswith("def ")]
    assert len(llamadas) == 1, "one call site for enforce_pr, found: %r" % llamadas
    assert "if args.enforce:" in src
    assert src.index("if args.enforce:") < src.index(llamadas[0]), (
        "the only enforce_pr call must sit under the --enforce guard")


def test_el_enforce_del_cron_es_una_sola_linea_visible():
    """The box applies verdicts by cron. That stays legible: exactly one
    crontab line invokes the reviewer, and the --enforce is written on it --
    never hidden inside a wrapper script."""
    cron = (CULTURA / "mak_plataforma" / "crontab.mak").read_text(
        encoding="utf-8")
    lineas = [ln for ln in cron.splitlines()
              if "revisor.py" in ln and not ln.lstrip().startswith("#")]
    assert len(lineas) == 1, lineas
    assert "--enforce" in lineas[0]


def test_no_hay_modelo_en_los_modulos_mecanicos():
    """Style of test_no_hay_modelo_en_el_vigia: these modules' own docstrings
    declare them mechanical (static gates, whitelists, read-only eyes, queue
    builders). If a model ever enters one, it is a decision, not a slide --
    and it edits this list."""
    mecanicos = [
        CULTURA / "mak_plataforma" / "revisor.py",   # "gates ESTATICOS"
        CULTURA / "mak_plataforma" / "latido.py",    # a cron counter + POST
        CULTURA / "mak_curatoria" / "ordenes.py",    # "Whitelist estricta"
        CULTURA / "mak_curatoria" / "watchdog.py",   # a flag and an issue
        # panel.py is NOT here on purpose: its process table names the
        # "ollama (vision)" pid it WATCHES, which is not model use.
        CULTURA / "mak_curatoria" / "triangular.py", # "Esto NO investiga"
        CULTURA / "mak_xio_puente" / "monitor.py",   # "ojo de SOLO LECTURA"
        CULTURA / "mak_xio_puente" / "staged" / "mak_link.py",
        CULTURA / "mak_xio_puente" / "staged" / "wake_mak.py",
    ]
    for archivo in mecanicos:
        fuente = archivo.read_text(encoding="utf-8").lower()
        for palabra in ("import torch", "openai", "ollama", "anthropic",
                        "llm(", "gpt-", "transformers"):
            assert palabra not in fuente, "%s no usa modelos: %s" % (
                archivo.name, palabra)


def test_el_monitor_xio_es_get_only_con_allowlist_dura():
    """monitor.py's doctrine is its first paragraph: 'JAMAS hace POST ni toca
    endpoints de red/hotspot/carga'. Pin the allowlist and the verb."""
    src = (CULTURA / "mak_xio_puente" / "monitor.py").read_text(
        encoding="utf-8")
    assert 'method="GET"' in src
    assert '"POST"' not in src and "'POST'" not in src
    rutas = re.search(r"RUTAS_LECTURA\s*=\s*\(([^)]*)\)", src).group(1)
    assert set(re.findall(r'"([^"]+)"', rutas)) == {
        "/status", "/obs", "/battery/status", "/connectivity/status"}
    for prohibida in ("hotspot", "wifi/", "/charge", "shutdown", "reboot"):
        assert prohibida not in rutas, prohibida


def test_ordenes_jamas_ejecuta_texto_libre():
    """ordenes.py's doctrine: 'JAMAS ejecuta texto libre: solo el enum'. The
    behavioral half is in test_curatoria_ordenes.py (unknown order spawns
    nothing); here the source keeps no door for free text."""
    src = (CULTURA / "mak_curatoria" / "ordenes.py").read_text(
        encoding="utf-8")
    for puerta in ("shell=True", "os.system", "eval(", "exec("):
        assert puerta not in src, puerta
