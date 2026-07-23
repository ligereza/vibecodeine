# -*- coding: utf-8 -*-
"""Puente WIN -> MAK: envia una carpeta local a ~/curatoria_inbox/ en MAK
via tar|ssh, con verificacion de conteo/bytes en ambos lados.

IMPORTANTE (staging, no curatoria automatica): esto SOLO deja la carpeta
en ~/curatoria_inbox/<nombre>/ en MAK. Ningun cron/pipeline mira ese
directorio -- se verifico crontab -l y percepcion.py en MAK (ambos requieren
--raiz-rd/--raiz-ig explicitos, no barren directorios por su cuenta).
Para que la curatoria real la procese hay que encolarla a mano en MAK:

    ssh mak@192.168.50.2 curatoria_encolar.sh <nombre>

Pipeline completo (3 etapas separadas, cada una manual):
    1. WIN  -> MAK inbox   : este script (enviar_a_mak.py)
    2. MAK inbox -> curatoria : ~/curatoria/curatoria_encolar.sh (en MAK)
    3. MAK -> OneDrive archivo : ~/curatoria/onedrive_archivar.sh (en MAK, post-curatoria)

Uso:
    py tools/enviar_a_mak.py "C:\\ruta\\a\\carpeta"
    py tools/enviar_a_mak.py            # abre dialogo tkinter askdirectory
    py tools/enviar_a_mak.py "C:\\ruta" --overwrite   # borra destino y reenvia
    py tools/enviar_a_mak.py "C:\\ruta" --merge       # tar sobre lo existente (no borra)

Requiere: ssh en PATH, llave autorizada sin password contra mak@192.168.50.2
(ver context/ para detalles de la llave). Fuerza UTF-8 en todo el proceso
para no romper nombres con tildes/enies (gotcha cp1252 de Windows).
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

MAK_HOST = "mak@192.168.50.2"
MAK_INBOX = "curatoria_inbox"


def _forzar_utf8() -> None:
    """Evita que Git Bash / consola Windows en cp1252 rompa nombres con tildes."""
    if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
            sys.stderr.reconfigure(encoding="utf-8")
        except Exception:
            pass
    os.environ.setdefault("PYTHONUTF8", "1")
    os.environ.setdefault("LANG", "C.UTF-8")
    os.environ.setdefault("LC_ALL", "C.UTF-8")


def elegir_carpeta() -> str:
    try:
        import tkinter as tk
        from tkinter import filedialog
    except Exception as exc:  # pragma: no cover - entorno sin tkinter
        print(f"ERROR: no se paso carpeta y tkinter no esta disponible ({exc})",
              file=sys.stderr)
        sys.exit(2)
    root = tk.Tk()
    root.withdraw()
    ruta = filedialog.askdirectory(title="Elegi la carpeta a enviar a MAK")
    root.destroy()
    if not ruta:
        print("ERROR: no se eligio ninguna carpeta.", file=sys.stderr)
        sys.exit(2)
    return ruta


def contar_local(carpeta: Path) -> tuple[int, int]:
    """(num_archivos, bytes_totales) recorriendo la carpeta local."""
    n = 0
    total = 0
    for p in carpeta.rglob("*"):
        if p.is_file():
            n += 1
            try:
                total += p.stat().st_size
            except OSError:
                pass
    return n, total


def ssh_run(cmd: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["ssh", MAK_HOST, cmd],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        check=False,
    )


def destino_existe(nombre_remoto: str) -> bool:
    r = ssh_run(f'test -d ~/{MAK_INBOX}/{nombre_remoto} && echo SI || echo NO')
    return r.stdout.strip().endswith("SI")


def contar_remoto(nombre_remoto: str) -> tuple[int, int]:
    r = ssh_run(
        f"find ~/{MAK_INBOX}/{nombre_remoto} -type f -printf '%s\\n' > /tmp/.eam_sizes; "
        f"wc -l < /tmp/.eam_sizes; "
        f"awk '{{s+=$1}} END{{print s+0}}' /tmp/.eam_sizes; "
        f"rm -f /tmp/.eam_sizes"
    )
    lineas = [l for l in r.stdout.strip().splitlines() if l.strip()]
    if len(lineas) < 2:
        return 0, 0
    try:
        return int(lineas[0]), int(lineas[1])
    except ValueError:
        return 0, 0


def enviar(carpeta: Path, overwrite: bool, merge: bool) -> int:
    nombre = carpeta.name
    parent = str(carpeta.parent)

    print(f"Origen : {carpeta}")
    print(f"Destino: {MAK_HOST}:~/{MAK_INBOX}/{nombre}/  (STAGING -- no auto-consumido)")

    n_local, b_local = contar_local(carpeta)
    print(f"Local  : {n_local} archivos, {b_local:,} bytes")

    if destino_existe(nombre):
        if overwrite:
            print("Destino ya existe -> --overwrite: borrando destino remoto...")
            ssh_run(f'rm -rf ~/{MAK_INBOX}/{nombre}')
        elif merge:
            print("Destino ya existe -> --merge: se sobreescribira archivo por archivo.")
        else:
            resp = input(
                f"'{nombre}' ya existe en ~/{MAK_INBOX}/ en MAK. "
                f"[o]verwrite / [m]erge / [c]ancelar? "
            ).strip().lower()
            if resp.startswith("o"):
                ssh_run(f'rm -rf ~/{MAK_INBOX}/{nombre}')
            elif resp.startswith("m"):
                pass
            else:
                print("Cancelado por el usuario.")
                return 1

    ssh_run(f'mkdir -p ~/{MAK_INBOX}')

    print("Transfiriendo (tar | ssh)...")
    tar_cmd = ["tar", "-C", parent, "-cf", "-", nombre]
    ssh_cmd = ["ssh", MAK_HOST, f"tar -xf - -C ~/{MAK_INBOX}/"]

    tar_proc = subprocess.Popen(tar_cmd, stdout=subprocess.PIPE)
    ssh_proc = subprocess.Popen(ssh_cmd, stdin=tar_proc.stdout)
    tar_proc.stdout.close()
    ssh_proc.communicate()
    tar_rc = tar_proc.wait()
    ssh_rc = ssh_proc.returncode

    if tar_rc != 0 or ssh_rc != 0:
        print(f"FALLO: tar rc={tar_rc} ssh rc={ssh_rc}", file=sys.stderr)
        return 1

    print("Verificando en destino...")
    n_remoto, b_remoto = contar_remoto(nombre)
    print(f"Remoto : {n_remoto} archivos, {b_remoto:,} bytes")

    if n_remoto == n_local and b_remoto == b_local:
        print(f"OK: {n_local} archivos / {b_local:,} bytes coinciden en ambos lados.")
        print("Siguiente paso (en MAK, manual): "
              f"ssh {MAK_HOST} curatoria_encolar.sh {nombre}")
        return 0

    print(
        f"FALLO: no coincide. local={n_local}/{b_local:,} "
        f"remoto={n_remoto}/{b_remoto:,}",
        file=sys.stderr,
    )
    return 1


def main() -> int:
    _forzar_utf8()
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("carpeta", nargs="?", help="ruta local a enviar")
    ap.add_argument("--overwrite", action="store_true",
                     help="borra el destino remoto si ya existe")
    ap.add_argument("--merge", action="store_true",
                     help="tar sobre lo existente sin borrar primero")
    args = ap.parse_args()

    ruta = args.carpeta or elegir_carpeta()
    carpeta = Path(ruta).resolve()

    if not carpeta.exists() or not carpeta.is_dir():
        print(f"ERROR: '{carpeta}' no existe o no es una carpeta.", file=sys.stderr)
        return 2

    return enviar(carpeta, args.overwrite, args.merge)


if __name__ == "__main__":
    raise SystemExit(main())
