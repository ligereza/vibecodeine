#!/usr/bin/env python3
"""revisor.py -- vetea (observacional) las utilidades autogeneradas que el
entregador subio como PR draft (branch capataz/*). Gates ESTATICOS, mechanical-
first (mas confiable que el juicio de un modelo chico sobre codigo de otro modelo
chico): compila + stdlib-only + el pedido se refleja en el codigo.

NO ejecuta el codigo revisado.

DOS MODOS, y la diferencia importa:
  - sin `--enforce`: observacional. Escribe el veredicto a
    reflexiones/revisor_shadow.json + log y no toca el PR.
  - con `--enforce`: ACTUA. `enforce_pr` marca ready, comenta y MERGEA. Corre
    asi por cron cada 6 horas.

Esta cabecera decia "NO toca el PR (no ready/comment/close/merge)" mientras
`enforce_pr` ya mergeaba, y el cron ya lo invocaba con --enforce. Quien leia
el archivo para saber que hacia la maquina leia lo contrario de lo que hacia.

Solo actua sobre PRs con rama HEAD `capataz/*` Y rama BASE `RAMA_BUZON`. El
segundo filtro se agrego el 2026-08-01: el primero mira de donde viene el PR
y no a donde va, asi que una rama `capataz/*` apuntando a main se mergeaba
sola. Nunca ocurrio -- `entregar.py` siempre usa `mak` -- pero eso es una
costumbre de otro archivo, no una garantia de este.
"""
import argparse
import ast
import json
import os
import subprocess
import sys
import time

try:
    from cultura.mak_conductor.runtime import active_enabled, dispatch_sync
except ImportError:  # pragma: no cover - direct MAK deployment
    sys.path.insert(0, os.environ.get("MAK_CONDUCTOR_PATH", "/home/mak/cultura"))
    try:
        from mak_conductor.runtime import active_enabled, dispatch_sync
    except ImportError:
        active_enabled = lambda: False
        dispatch_sync = None

REPO_SLUG = "ligereza/vibecodeine"
# El buzon de MAK. `enforce_pr` solo actua sobre PRs con ESTA base:
# lo que mergea declara contra que mergea.
RAMA_BUZON = "mak"
RUTA_UTILIDADES = "cultura/mak_plataforma/utilidades/"

HOME = os.path.expanduser("~")
REPO = HOME  # the MAK checkout is this department's repo root
JOBS = os.path.join(HOME, "codex", "jobs.jsonl")
OUT = os.path.join(HOME, "plataforma", "reflexiones", "revisor_shadow.json")
LOG = os.path.join(HOME, "plataforma", "logs", "revisor.log")
STDLIB = set(getattr(sys, "stdlib_module_names", set())) | {"__future__"}


def log(m):
    print(m)
    try:
        os.makedirs(os.path.dirname(LOG), exist_ok=True)
        with open(LOG, "a", encoding="utf-8") as f:
            f.write("%s %s\n" % (time.strftime("%Y-%m-%d %H:%M:%S"), m))
    except OSError:
        pass


def sh(args):
    r = subprocess.run(args, capture_output=True, text=True, cwd=REPO)
    return r.returncode, r.stdout, r.stderr


def pedido_de(job_hex):
    """Busca el pedido cuyo job_id termina en job_hex (sufijo de la rama)."""
    try:
        with open(JOBS, encoding="utf-8") as f:
            for line in f:
                try:
                    j = json.loads(line)
                except ValueError:
                    continue
                if (j.get("job_id") or "").endswith(job_hex):
                    return j.get("pedido") or j.get("tema") or ""
    except OSError:
        pass
    return ""


def gate_encoding(src):
    """El fuente tiene que ser UTF-8 de verdad, no UTF-8 con agujeros.

    `sh()` lee con `text=True`, asi que los bytes que no son UTF-8 valido
    entran como SURROGATES en vez de reventar ahi.

    Y lo que pasa despues es peor que aprobarlos: `compile()` levanta
    `UnicodeEncodeError`, que NO es `SyntaxError`, asi que `gate_compila` no lo
    captura y la excepcion se propaga hasta arriba. Un solo archivo con el
    encoding roto tumba la corrida COMPLETA del revisor, y todos los PR que
    venian detras se quedan sin revisar sin que nadie lo pida.

    Medido el 2026-08-01: de las 33 utilidades del buzon `mak`, 3 tienen esa
    forma. Este gate corre PRIMERO justamente por eso -- las atrapa como
    NO-APROBADO, con su motivo, antes de que lleguen a `compile()`.

    Se prueba re-codificando: si el texto no vuelve a bytes, no era texto.
    """
    try:
        (src or "").encode("utf-8")
    except UnicodeEncodeError as e:
        malo = (src or "")[e.start:e.start + 1]
        return False, ("encoding roto en la posicion %d (%r): el archivo no es "
                       "UTF-8 y no se puede leer fuera de la caja"
                       % (e.start, malo))
    return True, ""


def gate_compila(src):
    try:
        compile(src, "<pr>", "exec")
        return True, ""
    except SyntaxError as e:
        return False, "no compila: %s L%s" % (e.msg, e.lineno)


def gate_stdlib(src):
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return False, "no parsea"
    externos = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                top = a.name.split(".")[0]
                if top not in STDLIB:
                    externos.append(top)
        elif isinstance(node, ast.ImportFrom):
            if node.level == 0 and node.module:
                top = node.module.split(".")[0]
                if top not in STDLIB:
                    externos.append(top)
    if externos:
        return False, "imports no-stdlib: " + ",".join(sorted(set(externos)))
    return True, ""


def gate_pedido(src, pedido):
    palabras = [w.strip(".,:()\"'").lower() for w in pedido.split()]
    clave = [w for w in palabras if len(w) > 4]
    low = src.lower()
    hits = [w for w in clave if w in low]
    if not clave:
        return True, "pedido sin palabras clave (skip)"
    if hits:
        return True, "match: " + ",".join(hits[:4])
    return False, "el codigo no refleja el pedido (0 palabras clave)"


def rutas_fuera_de_zona(files):
    """Paths a capataz PR is not allowed to touch.

    MAK's autonomous delivery channel is intentionally narrow: one generated
    Python utility under cultura/mak_plataforma/utilidades/. If the branch
    drags Dependabot, workflow or web changes, the reviewer must veto the PR
    instead of silently reviewing the first .py file and merging the rest.
    """
    out = []
    for f in files or []:
        path = f.get("path") if isinstance(f, dict) else str(f)
        path = (path or "").replace("\\", "/")
        if not path.startswith(RUTA_UTILIDADES):
            out.append(path)
    return out


def revisar_pr(n, branch, path, veredictos):
    job_hex = branch.rsplit("-", 1)[-1]
    pedido = pedido_de(job_hex)
    # traer el archivo desde la rama remota (fetch primero)
    sh(["git", "fetch", "origin", branch, "--quiet"])
    rc, src, err = sh(["git", "show", "FETCH_HEAD:%s" % path])
    if rc != 0 or not src.strip():
        rc, src, err = sh(["git", "show", "origin/%s:%s" % (branch, path)])
    if rc != 0 or not src.strip():
        v = {"pr": n, "veredicto": "ERROR", "razon": "no pude leer el archivo", "gates": {}}
        veredictos.append(v)
        log("PR #%d ERROR: no pude leer %s" % (n, path))
        return
    gates = {}
    # El encoding va PRIMERO: un archivo que no se puede leer no tiene sentido
    # compilar, y `compile()` sobre surrogates lanza UnicodeEncodeError, que
    # `gate_compila` no captura -- eso tumbaba la corrida entera.
    ok0, m0 = gate_encoding(src); gates["encoding"] = ok0
    ok1, m1 = gate_compila(src); gates["compila"] = ok1
    ok2, m2 = gate_stdlib(src); gates["stdlib_only"] = ok2
    ok3, m3 = gate_pedido(src, pedido); gates["pedido_match"] = ok3
    passed = ok0 and ok1 and ok2 and ok3
    v = {"pr": n, "branch": branch, "archivo": path,
         "pedido": pedido[:120],
         "veredicto": "PASS" if passed else "NO-APROBADO",
         "gates": gates,
         "detalle": {"encoding": m0, "compila": m1, "stdlib": m2,
                     "pedido": m3},
         "bytes": len(src)}
    veredictos.append(v)
    log("PR #%d %s | encoding=%s compila=%s stdlib=%s pedido=%s | %s"
        % (n, v["veredicto"], ok0, ok1, ok2, ok3,
           (m0 or m2 or m3 or m1 or "todo OK")))


def ci_verde(n):
    """True si TODOS los checks del PR pasaron (ninguno pending/fail)."""
    rc, out, err = sh(["gh", "pr", "checks", str(n), "--repo", REPO_SLUG])
    if rc != 0 and not out.strip():
        return False
    estados = [ln.split("\t")[1].lower() for ln in out.splitlines()
               if "\t" in ln and len(ln.split("\t")) > 1]
    if not estados:
        return False
    return all("pass" in e for e in estados)


def enforce_pr(v):
    """Aplica el veredicto sobre el PR (el box actua sobre si mismo). PASS + CI
    verde -> ready + merge (miskirabit, requiere checks verdes por branch
    protection). NO-APROBADO -> comenta, deja en draft (no cierra, no pierde
    trabajo). Nunca lanza."""
    n = v["pr"]
    if v["veredicto"] == "PASS":
        if not ci_verde(n):
            log("PR #%d PASS pero CI no verde aun -- espero proximo ciclo" % n)
            return "espera-ci"
        sh(["gh", "pr", "ready", str(n), "--repo", REPO_SLUG])
        sh(["gh", "pr", "comment", str(n), "--repo", REPO_SLUG, "-b",
            "revisor MAK: OK (mecanico) + CI verde. Merge autonomo."])
        rc, out, err = sh(["gh", "pr", "merge", str(n), "--repo", REPO_SLUG,
                           "--squash", "--delete-branch"])
        if rc == 0:
            log("PR #%d MERGEADO autonomo por el box" % n)
            return "merged"
        log("PR #%d merge fallo: %s" % (n, (err or out).strip()[:160]))
        return "merge-fallo"
    else:
        sh(["gh", "pr", "comment", str(n), "--repo", REPO_SLUG, "-b",
            "revisor MAK: NO APROBADO -- queda en draft para revision."])
        log("PR #%d NO-APROBADO (comentado, sin cerrar)" % n)
        return "no-aprobado"


def main():
    if (active_enabled() and dispatch_sync is not None and
            "--enforce" in sys.argv[1:]):
        payload = {"argv": sys.argv[1:], "bucket": int(time.time() // 21600),
                   "requires_human": True}

        def queued_merge(_job):
            result_code = _main_unlocked()
            return {
                "validated": result_code == 0,
                "result_code": result_code,
                "artifacts": [{
                    "kind": "pr_merge_manifest",
                    "content": json.dumps(
                        dict(payload, result_code=result_code), sort_keys=True),
                    "staging_path": OUT,
                }],
            }

        result = dispatch_sync(
            "pr_merge", payload, producer="platform.revisor.enforce_pr",
            handler=queued_merge, template_version="pr-merge-v1",
        )
        return int((result or {}).get("result_code", 2))
    return _main_unlocked()


def _main_unlocked():
    ap = argparse.ArgumentParser()
    ap.add_argument("--enforce", action="store_true",
                    help="aplica el veredicto (ready/merge/comment); sin esto solo observa")
    args = ap.parse_args()
    rc, out, err = sh(["gh", "pr", "list", "--repo", REPO_SLUG,
                       "--state", "open", "--json",
                       "number,headRefName,baseRefName,isDraft,files"])
    if rc != 0:
        log("ERROR gh pr list: %s" % err.strip()[:160])
        return 1
    try:
        prs = json.loads(out)
    except ValueError:
        log("ERROR json gh pr list")
        return 1
    veredictos = []
    for pr in prs:
        branch = pr.get("headRefName", "")
        if not branch.startswith("capataz/"):
            continue
        # El filtro de arriba mira la rama HEAD; este mira la BASE, y son
        # cosas distintas. `enforce_pr` mergea, y sin esta linea alcanzaba con
        # que un PR llevara una rama `capataz/*` apuntando a main para que un
        # cron lo cerrara solo cada 6 horas. Hoy `entregar.py` siempre usa
        # `mak` como base, pero eso es una costumbre de otro archivo, no una
        # garantia de este. Lo que mergea declara contra que mergea.
        # AUSENTE no es lo mismo que DISTINTA, y esa diferencia importa aca:
        # un PR que declara otra base se rechaza, pero uno que no trae el campo
        # (un `gh` viejo, una respuesta recortada) no se puede juzgar por el.
        # Tratar la ausencia como rechazo apagaria el revisor entero en
        # silencio -- el modo de fallo que este archivo ya tuvo con su propia
        # cabecera. Se procesa y se DICE, para que se vea en el log.
        base = pr.get("baseRefName")
        if base is None or base == "":
            log("PR #%d sin baseRefName declarado: se revisa igual" % pr["number"])
        elif base != RAMA_BUZON:
            log("PR #%d ignorado: base '%s', no '%s'"
                % (pr["number"], base, RAMA_BUZON))
            continue
        files = pr.get("files") or []
        fuera = rutas_fuera_de_zona(files)
        if fuera:
            veredictos.append({
                "pr": pr["number"],
                "branch": branch,
                "veredicto": "NO-APROBADO",
                "razon": "capataz toca rutas fuera de utilidades",
                "rutas_fuera_de_zona": fuera,
                "gates": {"zona_utilidades": False},
            })
            log("PR #%d NO-APROBADO: rutas fuera de %s: %s"
                % (pr["number"], RUTA_UTILIDADES, ", ".join(fuera[:5])))
            continue
        pys = [f["path"] for f in files if f["path"].endswith(".py")]
        if not pys:
            continue
        revisar_pr(pr["number"], branch, pys[0], veredictos)
    if args.enforce:
        for v in veredictos:
            if v["veredicto"] in ("PASS", "NO-APROBADO"):
                v["accion"] = enforce_pr(v)
    rep = {"ts": time.time(),
           "modo": "enforce" if args.enforce else "shadow (observacional)",
           "veredictos": veredictos}
    try:
        os.makedirs(os.path.dirname(OUT), exist_ok=True)
        with open(OUT, "w", encoding="utf-8") as f:
            json.dump(rep, f, ensure_ascii=False, indent=1)
    except OSError as e:
        log("WARN no guarde reporte: %s" % e)
    log("revisor: %d PR capataz revisados (%d PASS)"
        % (len(veredictos), sum(1 for v in veredictos if v["veredicto"] == "PASS")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
