#!/usr/bin/env python3
"""revisor.py -- vetea (observacional) las utilidades autogeneradas que el
entregador subio como PR draft (branch capataz/*). Gates ESTATICOS, mechanical-
first (mas confiable que el juicio de un modelo chico sobre codigo de otro modelo
chico): compila + stdlib-only + el pedido se refleja en el codigo.

NO ejecuta el codigo revisado. NO toca el PR (no ready/comment/close/merge).
Solo escribe un veredicto a reflexiones/revisor_shadow.json + log. El merge lo
decide un humano/jefe leyendo este veredicto. Enforcement (marcar ready / cerrar)
es un paso deliberado posterior, cuando el shadow valide los veredictos.
"""
import ast
import json
import os
import subprocess
import sys
import time

HOME = os.path.expanduser("~")
REPO = os.path.join(HOME, "flujo")
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
    ok1, m1 = gate_compila(src); gates["compila"] = ok1
    ok2, m2 = gate_stdlib(src); gates["stdlib_only"] = ok2
    ok3, m3 = gate_pedido(src, pedido); gates["pedido_match"] = ok3
    passed = ok1 and ok2 and ok3
    v = {"pr": n, "branch": branch, "archivo": path,
         "pedido": pedido[:120],
         "veredicto": "PASS" if passed else "NO-APROBADO",
         "gates": gates,
         "detalle": {"compila": m1, "stdlib": m2, "pedido": m3},
         "bytes": len(src)}
    veredictos.append(v)
    log("PR #%d %s | compila=%s stdlib=%s pedido=%s | %s"
        % (n, v["veredicto"], ok1, ok2, ok3, (m2 or m3 or m1 or "todo OK")))


def main():
    rc, out, err = sh(["gh", "pr", "list", "--repo", "ligereza/vibecodeine",
                       "--state", "open", "--json",
                       "number,headRefName,isDraft,files"])
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
        pys = [f["path"] for f in (pr.get("files") or [])
               if f["path"].endswith(".py")]
        if not pys:
            continue
        revisar_pr(pr["number"], branch, pys[0], veredictos)
    rep = {"ts": time.time(), "modo": "shadow (observacional, no toca PRs)",
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
