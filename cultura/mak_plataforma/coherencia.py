#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Coherencia entre el REPO y lo que la caja de verdad corre.

Por que existe, medido el 2026-07-30: el cron MAK-REPO-SYNC copia con `cp -ru`,
y `-u` significa "solo si el origen es MAS NUEVO". Basta editar un archivo en la
caja para que la version del repo no vuelva a entrar NUNCA: la copia local queda
mas nueva para siempre. Encontrado asi:

    revisor.py    repo 165 lineas (2026-07-20 15:48)
                  caja 216 lineas (2026-07-20 17:39)  <- la que corre

Las 51 lineas de diferencia eran `enforce_pr()`, que mergea PRs sola y corre
cada 6 horas por cron. Vivia en un solo disco, sin revision y sin respaldo. Y la
version del repo, la que cualquiera lee para entender que hace el revisor, ni
siquiera tenia la bandera `--enforce` con la que se invoca.

La deriva es de UNA sola direccion y por eso nadie la ve: repo -> caja esta
forzado cada 10 minutos, caja -> repo no ocurre jamas. Este script mira las dos.

    python3 coherencia.py            # informe
    python3 coherencia.py --estricto # ademas sale 1 si hay deriva

Sale 0 si todo calza. No escribe nada: solo mira.
"""
from __future__ import annotations

import argparse
import hashlib
import subprocess
import sys
from pathlib import Path

CASA = Path.home()
CLON = CASA / "flujo" / "cultura"

# organo -> (carpeta del repo, carpeta donde CORRE)
ORGANOS = {
    "plataforma": (CLON / "mak_plataforma", CASA / "plataforma"),
    "research": (CLON / "mak_research", CASA / "research"),
    "codex": (CLON / "mak_codex", CASA / "codex"),
    "curatoria": (CLON / "mak_curatoria", CASA / "curatoria"),
}

# Lo que la caja produce y NO tiene por que estar en el repo. No es deriva:
# es su estado. Distinguirlo importa -- si todo cuenta como deriva, el informe
# se vuelve ruido y nadie lo lee, que es como se pierden los hallazgos reales.
SUYO_DE_LA_CAJA = ("piezas/", "fichas/", "jobs/", "logs/", "estado",
                   "procesados", "backlog", "__pycache__/", ".git/")


def _md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


def _propio(rel: str) -> bool:
    return any(m in rel.replace("\\", "/") for m in SUYO_DE_LA_CAJA)


def revisar(nombre: str, repo: Path, vivo: Path) -> dict:
    r = {"organo": nombre, "distintos": [], "solo_en_la_caja": [],
         "faltan_en_la_caja": [], "existe": repo.is_dir() and vivo.is_dir()}
    if not r["existe"]:
        return r
    for f in sorted(repo.rglob("*.py")):
        rel = f.relative_to(repo).as_posix()
        if _propio(rel):
            continue
        destino = vivo / rel
        if not destino.exists():
            r["faltan_en_la_caja"].append(rel)
        elif _md5(f) != _md5(destino):
            # cual gana hoy: el que tenga mtime mas nuevo, que es lo que mira -u
            gana = "caja" if destino.stat().st_mtime > f.stat().st_mtime else "repo"
            r["distintos"].append((rel, gana))
    for f in sorted(vivo.rglob("*.py")):
        rel = f.relative_to(vivo).as_posix()
        if _propio(rel):
            continue
        if not (repo / rel).exists():
            r["solo_en_la_caja"].append((rel, len(
                f.read_text(encoding="utf-8", errors="replace").splitlines())))
    return r


def _vive(rel: str, cron: str) -> bool:
    """Si el cron lo invoca. Un archivo huerfano que ADEMAS corre es urgente;
    uno que no corre es una linea en el handoff y nada mas."""
    return Path(rel).name in cron


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--estricto", action="store_true",
                    help="sale 1 si hay deriva (para cron o CI)")
    args = ap.parse_args()

    try:
        cron = subprocess.run(["crontab", "-l"], capture_output=True,
                              text=True, timeout=20).stdout
    except Exception:
        cron = ""

    deriva = 0
    for nombre, (repo, vivo) in ORGANOS.items():
        r = revisar(nombre, repo, vivo)
        if not r["existe"]:
            print("== %-11s no aplica (falta %s)"
                  % (nombre, repo if not repo.is_dir() else vivo))
            continue
        malos = len(r["distintos"]) + len(r["faltan_en_la_caja"])
        huerfanos_vivos = [(f, n) for f, n in r["solo_en_la_caja"]
                           if _vive(f, cron)]
        deriva += malos + len(huerfanos_vivos)
        print("== %-11s %d distinto(s), %d sin copiar, %d solo-en-la-caja "
              "(%d de ellos EN CRON)"
              % (nombre, len(r["distintos"]), len(r["faltan_en_la_caja"]),
                 len(r["solo_en_la_caja"]), len(huerfanos_vivos)))
        for rel, gana in r["distintos"]:
            print("   DISTINTO  %-40s hoy gana: %s" % (rel, gana))
        for rel in r["faltan_en_la_caja"]:
            print("   SIN COPIAR %-39s el repo lo tiene, la caja no" % rel)
        for rel, n in huerfanos_vivos:
            print("   SOLO AQUI %-40s %d lineas y EL CRON LO CORRE" % (rel, n))

    print()
    if deriva:
        print("%d punto(s) de deriva. Lo que 'gana: caja' no volvera a "
              "actualizarse solo: `cp -u` no pisa un archivo mas nuevo." % deriva)
    else:
        print("Sin deriva: la caja corre lo que dice el repo.")
    return 1 if (deriva and args.estricto) else 0


if __name__ == "__main__":
    sys.exit(main())
