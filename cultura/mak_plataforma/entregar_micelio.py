#!/usr/bin/env python3
"""entregar_micelio.py -- push the micelio's measured graph into the repo.

Why this exists (2026-08-01). The site's publish workflow
(.github/workflows/publicar_iskvw.yml) runs on `ubuntu-latest`, a
GitHub-hosted cloud runner. It was never going to reach this box's
private-LAN address -- that is not an outage, the workflow's own comment
already says so ("la caja no es visible desde CI... eso es lo esperado").
Measured the same day by fetching the live iskvw.cl/datos/archivo.json:
269 published `vinculos`, 0 of them `clase: "semantico"` -- every link the
site shows is either tag-derived or manifest-declared, never a distance
the micelio actually measured. The 227 `obra` pieces it does publish come
from two files this repo already commits and regenerates by hand
(iskvw/datos/campo.json + obras.json, 219 + 8 = 227) -- proof the
"committed snapshot" shape already works for this exact problem; this
script does the same thing for the micelio's links.

The self-hosted runner labelled 'mak' is ALSO offline right now (confirmed
via `gh api repos/.../actions/runners`, and its own runner.log dying
mid-retry at 2026-07-24 14:03:59Z) -- but that is a separate, unrelated
fact. `publicar_iskvw.yml` targets `ubuntu-latest` regardless of that
runner's health, so reviving it would not close this gap by itself.

The fix pulls from the half of the pipe that already works
(the MAK-REPO-SYNC cron mirrors this very file to the box every
10 minutes) and pushes the other way, following the exact git/gh pattern
`entregar.py` already proves in production (git checkout -B / commit /
push / gh pr create --draft), including its base branch: 'mak' is MAK's
inbox, PRs never target main directly (branch topology).

Hard rule, non-negotiable: an absence never becomes a plausible-looking
zero. If the micelio does not answer, or answers with zero links, this
script says so on stderr and exits 1 -- it writes nothing and opens
nothing. A committed file claiming 0 links would read as a measurement
instead of the failure it actually is.

Usage:
  python3 entregar_micelio.py --dry-run     # fetch + convert + print counts, no git/gh
  python3 entregar_micelio.py               # fetch, write iskvw/datos/micelio.json, open PR
"""
import argparse
import json
import os
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import contrato_archivo  # noqa: E402 -- same conversion tools/gen_archivo_iskvw.py uses

# Same inbox topology entregar.py uses: MAK never opens a PR
# against main directly, only against its own branch 'mak'.
RAMA_BASE = "mak"

HOME = os.path.expanduser("~")
REPO = os.path.join(HOME, "flujo")
DEST_REL = os.path.join("iskvw", "datos", "micelio.json")
LOG = os.path.join(HOME, "plataforma", "logs", "entregar_micelio.log")

# Env override, not a LAN IP hardcoded in a public repo (same rule
# tools/gen_archivo_iskvw.py follows). Default is correct only when this
# script runs ON the box: 127.0.0.1 is the box's own research service.
MICELIO_URL = os.environ.get("FLUJO_MAK_RESEARCH_URL", "http://127.0.0.1:8890")
UMBRAL = float(os.environ.get("FLUJO_MICELIO_UMBRAL", "0.55"))


def log(msg):
    line = msg.rstrip()
    print(line)
    try:
        os.makedirs(os.path.dirname(LOG), exist_ok=True)
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except OSError:
        pass


def leer_grafo(url, umbral, timeout=90):
    """The same endpoint tools/gen_archivo_iskvw.py:desde_micelio() calls
    from the repo side -- only reachable here because this runs ON the box."""
    pedido = "%s/api/memoria/grafo?umbral=%s" % (url.rstrip("/"), umbral)
    with urllib.request.urlopen(pedido, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


def git(*args, check=True):
    r = subprocess.run(["git", "-C", REPO] + list(args),
                       capture_output=True, text=True)
    if check and r.returncode != 0:
        raise RuntimeError("git %s -> %s" % (" ".join(args), r.stderr.strip()))
    return r


def contenido_en(rama, ruta_rel):
    """What's already committed at ruta_rel on `rama`, or None if it is not
    there yet. Used to skip opening a PR that would change nothing."""
    r = subprocess.run(["git", "-C", REPO, "show", "%s:%s" % (rama, ruta_rel)],
                       capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def _sin_generado(d):
    return {k: v for k, v in d.items() if k != "generado"}


def construir_salida(grafo, umbral):
    """Pure: graph payload + threshold -> the file this script writes.
    Returns (salida_dict, n_piezas, n_vinculos); raises nothing -- callers
    decide what a 0-vinculos result means for their own exit code."""
    datos = contrato_archivo.convertir(grafo)
    salida = {
        "version": 1,
        "fuente": "micelio_snapshot",
        "umbral": umbral,
        "generado": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "piezas": datos["piezas"],
        "vinculos": datos["vinculos"],
    }
    return salida, len(datos["piezas"]), len(datos["vinculos"])


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true",
                    help="fetch + convert + print counts; no git, no gh")
    ap.add_argument("--url", default=MICELIO_URL)
    ap.add_argument("--umbral", type=float, default=UMBRAL)
    args = ap.parse_args()

    try:
        grafo = leer_grafo(args.url, args.umbral)
    except Exception as e:  # noqa: BLE001 -- any network/HTTP/JSON failure
        log("ERROR: el micelio no respondio en %s (%s). No se escribe nada, "
            "no se abre PR." % (args.url, e))
        return 1

    salida, n_piezas, n_vinculos = construir_salida(grafo, args.umbral)

    if n_vinculos == 0:
        log("ERROR: el micelio devolvio %d piezas y 0 vinculos contra "
            "umbral %s -- eso es un fallo, no un archivo para commitear."
            % (n_piezas, args.umbral))
        return 1

    log("leido: %d piezas, %d vinculos, umbral %s" % (n_piezas, n_vinculos, args.umbral))
    texto = json.dumps(salida, ensure_ascii=False, indent=1) + "\n"

    if args.dry_run:
        log("DRY-RUN: escribiria %s (%d bytes) y abriria PR contra %s"
            % (DEST_REL, len(texto), RAMA_BASE))
        return 0

    git("fetch", "origin", "--quiet")
    previo = contenido_en("origin/%s" % RAMA_BASE, DEST_REL)
    if previo is not None:
        try:
            igual = _sin_generado(json.loads(previo)) == _sin_generado(salida)
        except ValueError:
            igual = False
        if igual:
            log("sin cambios frente a origin/%s:%s -- no se abre PR"
                % (RAMA_BASE, DEST_REL))
            return 0

    branch = "mak-micelio/%s" % datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    git("checkout", "-B", branch, "origin/%s" % RAMA_BASE, "--quiet")
    dest_abs = os.path.join(REPO, os.path.dirname(DEST_REL))
    os.makedirs(dest_abs, exist_ok=True)
    with open(os.path.join(REPO, DEST_REL), "w", encoding="utf-8") as f:
        f.write(texto)
    git("add", DEST_REL)
    msg = ("feat(iskvw): micelio snapshot -- %d piezas, %d vinculos "
           "(umbral %s)\n\n"
           "Pushed from the box because CI cannot reach it: "
           "publicar_iskvw.yml runs on ubuntu-latest, which was never "
           "going to reach a private-LAN address. Read via GET "
           "/api/memoria/grafo, converted with contrato_archivo.convertir "
           "(the same function tools/gen_archivo_iskvw.py and the hub's "
           "own GET /api/archivo already use).\n\n"
           "Co-Authored-By: MAK entregador <mak@organismo>"
           % (n_piezas, n_vinculos, args.umbral))
    git("commit", "-q", "-m", msg)
    git("push", "-u", "origin", branch, "--quiet")
    pr = subprocess.run(
        ["gh", "pr", "create", "--draft", "--base", RAMA_BASE, "--head", branch,
         "--title", "feat(iskvw): micelio snapshot -- %d piezas, %d vinculos"
                    % (n_piezas, n_vinculos),
         "--body", ("Snapshot of the micelio's measured graph "
                    "(GET /api/memoria/grafo?umbral=%s) so the published "
                    "site carries at least one real semantic link, even "
                    "though CI cannot reach this box.\n\n"
                    "%d piezas, %d vinculos.\n\n"
                    "Draft: human review before merge. CI decides."
                    % (args.umbral, n_piezas, n_vinculos))],
        cwd=REPO, capture_output=True, text=True)
    salida_pr = (pr.stdout or pr.stderr).strip().splitlines()[-1] if (pr.stdout or pr.stderr) else "?"
    if pr.returncode != 0:
        log("WARN PR fallo: %s" % pr.stderr.strip()[:300])
        return 1
    log("ENTREGADO -> %s" % salida_pr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
