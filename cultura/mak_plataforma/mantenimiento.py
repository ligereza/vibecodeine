#!/usr/bin/env python3
"""mantenimiento.py -- mantenimiento de rutina de la plataforma MAK, dry-run primero.

Agrupa 4 tareas de limpieza/salud que antes vivian como pasos manuales
sueltos: purgar temporales acotados (nunca fuera de la plataforma),
archivar reportes viejos de research (nunca borrar, solo mover a
archive/), revisar si los organos vivos siguen vivos y re-disparar el
watchdog si hace falta, y correr los ratchets de sanidad del repo. TODAS
las tareas son dry-run por defecto (execute=False): sin --execute solo
devuelven un reporte de lo que HARIAN, nada se toca en disco ni se lanza
un proceso real. Regla viva post-incidente del 2026-07-22 (relanzar =
revivir, nunca matar): este modulo no contiene ni un solo llamado que
termine un proceso -- relanzar_organos() solo re-dispara watchdog_mak.sh,
jamas manda una senal de terminacion. Sin llamadas de red. Import seguro
en Windows (pgrep/bash solo se invocan detras de execute=True o quedan
mockeados en tests; el resto es os/shutil/subprocess.run estandar).

    python3 mantenimiento.py limpiar [--execute]              # temporales de la plataforma
    python3 mantenimiento.py archivar [--dir RUTA] [--keep N] [--execute]
    python3 mantenimiento.py relanzar [--execute]              # liveness + watchdog si hace falta
    python3 mantenimiento.py ratchet [--execute]               # tests de sanidad del repo
    python3 mantenimiento.py todo [--execute]                  # las 4 tareas juntas
"""
import fnmatch
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

PLATAFORMA = os.path.dirname(os.path.abspath(__file__))


def _detectar_raiz_repo():
    """Sube desde este archivo hasta encontrar pyproject.toml.

    Returns:
        Directorio raiz del repo. Si no se encuentra (layout atipico),
        cae a 2 niveles arriba de este archivo como aproximacion.
    """
    actual = PLATAFORMA
    visto = set()
    while actual not in visto:
        visto.add(actual)
        if os.path.isfile(os.path.join(actual, "pyproject.toml")):
            return actual
        padre = os.path.dirname(actual)
        if padre == actual:
            break
        actual = padre
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


RAIZ_REPO = _detectar_raiz_repo()

# Patrones frozen -- cambiar requiere revisar F1b de nuevo, no ampliar sueltos.
TEMPORALES = ("*.tmp", "*.log.old", "__pycache__", ".pytest_cache")
_TEMPORALES_DIRS = {"__pycache__", ".pytest_cache"}
_TEMPORALES_GLOBS = ("*.tmp", "*.log.old")

ORGANOS = (
    ("hub", "plataforma/hub.py"),
    ("codex_interfaz", "codex/interfaz_codex.py"),
    ("xio_monitor", "xio_puente/monitor.py"),
)

RATCHETS = (
    "tests/test_utilidades_mak_sanidad.py",
    "tests/test_mak_salud_proveedores.py",
)


def limpiar_temporales(base=PLATAFORMA, execute=False):
    """Purga temporales acotados (nunca fuera de `base`).

    Camina `base` (nunca sale de ahi) buscando los patrones frozen de
    TEMPORALES: archivos *.tmp / *.log.old, y directorios __pycache__ /
    .pytest_cache completos. Nunca desciende dentro de un directorio ya
    marcado como candidato (evita recorrer basura que de todos modos se
    va a borrar entera).

    Args:
        base: directorio raiz del recorrido (default: esta plataforma).
        execute: si True, borra los candidatos. Si False (default),
            solo lista que borraria.

    Returns:
        dict: {"execute", "candidatos": [rutas relativas a base],
        "eliminados": [rutas efectivamente borradas], "errores": [...]}.
        Nunca lanza -- errores por item quedan en "errores".
    """
    candidatos = []
    errores = []

    for raiz, dirnames, filenames in os.walk(base):
        marcados = [d for d in dirnames if d in _TEMPORALES_DIRS]
        for d in marcados:
            ruta = os.path.join(raiz, d)
            candidatos.append(os.path.relpath(ruta, base))
        # no bajar a directorios que ya vamos a borrar enteros
        dirnames[:] = [d for d in dirnames if d not in _TEMPORALES_DIRS]

        for nombre in filenames:
            if any(fnmatch.fnmatch(nombre, patron) for patron in _TEMPORALES_GLOBS):
                ruta = os.path.join(raiz, nombre)
                candidatos.append(os.path.relpath(ruta, base))

    eliminados = []
    if execute:
        for rel in candidatos:
            ruta = os.path.join(base, rel)
            try:
                if os.path.isdir(ruta):
                    shutil.rmtree(ruta)
                else:
                    os.remove(ruta)
                eliminados.append(rel)
            except OSError as e:
                errores.append({"ruta": rel, "error": str(e)[:200]})

    return {
        "execute": bool(execute),
        "candidatos": candidatos,
        "eliminados": eliminados,
        "errores": errores,
    }


def archivar_reportes(dir_reportes, keep=20, execute=False):
    """Archiva reportes *.md viejos de `dir_reportes` (nunca borra).

    Mismo criterio que cultura/mak_research/retencion.py (implementado
    localmente aca, sin importar entre paquetes): ordena *.md por mtime
    (mas nuevo primero), conserva los `keep` mas nuevos, y MUEVE el resto
    a `<dir_reportes>/archive/`. Los que ya viven en archive/ no se
    recuentan.

    Args:
        dir_reportes: directorio a escanear. Si no existe, reporta
            "a_archivar": [] con "nota": "dir no existe" (no es error).
        keep: cuantos reportes recientes conservar (minimo 1).
        execute: si True, mueve los que sobran a archive/.

    Returns:
        dict: {"execute", "total", "quedan", "a_archivar": [nombres],
        "archivados": [nombres movidos], "errores": [...]}.
    """
    dir_path = Path(dir_reportes)
    if not dir_path.is_dir():
        return {
            "execute": bool(execute),
            "total": 0,
            "quedan": 0,
            "a_archivar": [],
            "archivados": [],
            "errores": [],
            "nota": "dir no existe",
        }

    archivos = [
        p for p in dir_path.glob("*.md")
        if p.is_file() and p.parent.name != "archive"
    ]
    archivos_ordenados = sorted(archivos, key=lambda p: p.stat().st_mtime, reverse=True)

    keep = max(1, keep)
    quedan = archivos_ordenados[:keep]
    a_archivar = archivos_ordenados[keep:]

    archivados = []
    errores = []
    if execute and a_archivar:
        archive_dir = dir_path / "archive"
        archive_dir.mkdir(exist_ok=True)
        for p in a_archivar:
            try:
                p.rename(archive_dir / p.name)
                archivados.append(p.name)
            except OSError as e:
                errores.append({"ruta": p.name, "error": str(e)[:200]})

    return {
        "execute": bool(execute),
        "total": len(archivos_ordenados),
        "quedan": len(quedan),
        "a_archivar": [p.name for p in a_archivar],
        "archivados": archivados,
        "errores": errores,
    }


def _vivo_organo(patron):
    """Liveness de un organo via pgrep -f. Nunca termina el proceso.

    Returns:
        (vivo, pid): vivo=True/False si pgrep respondio (rc 0/no-0),
        vivo=None si pgrep no esta disponible (por ejemplo Windows) --
        OSError/FileNotFoundError se tragan, esto no es un error fatal.
        pid = primera linea de stdout si vivo, sino None.
    """
    try:
        r = subprocess.run(["pgrep", "-f", patron], capture_output=True,
                           text=True, timeout=5)
        if r.returncode == 0:
            lineas = (r.stdout or "").strip().splitlines()
            return True, (lineas[0] if lineas else None)
        return False, None
    except (OSError, FileNotFoundError):
        return None, None


def relanzar_organos(execute=False):
    """Revisa liveness de los organos frozen y re-dispara el watchdog si hace falta.

    NUNCA mata nada -- es revive-only por diseno (regla viva desde el
    incidente del 2026-07-22: relanzar = revivir un organo caido, jamas
    terminar uno vivo). Solapamiento conocido: mak-hub.service y
    mak-xio.service (systemd con Restart=always) son un mecanismo
    PARALELO que ya revive hub y xio_monitor por su cuenta; esta funcion
    no administra systemd para nada, solo re-dispara watchdog_mak.sh (la
    capa extra descripta en watchdog_mak.sh:1-3) cuando detecta al menos
    un organo caido.

    Args:
        execute: si False (default), solo reporta liveness, no dispara
            nada. Si True y algun organo esta caido, corre
            watchdog_mak.sh UNA vez.

    Returns:
        dict: {"execute", "organos": [{"nombre","patron","vivo","pid"}],
        "accion": "ninguna" | "watchdog_disparado", y si se disparo
        tambien "rc" (codigo de salida del watchdog).
    """
    organos = []
    hay_caido = False
    for nombre, patron in ORGANOS:
        vivo, pid = _vivo_organo(patron)
        if vivo is False:
            hay_caido = True
        organos.append({"nombre": nombre, "patron": patron, "vivo": vivo, "pid": pid})

    if not execute:
        return {"execute": False, "organos": organos, "accion": "ninguna"}

    if not hay_caido:
        return {"execute": True, "organos": organos, "accion": "ninguna"}

    script = os.path.join(PLATAFORMA, "watchdog_mak.sh")
    try:
        r = subprocess.run(["bash", script], capture_output=True, text=True, timeout=60)
        return {"execute": True, "organos": organos,
                "accion": "watchdog_disparado", "rc": r.returncode}
    except (OSError, subprocess.TimeoutExpired) as e:
        return {"execute": True, "organos": organos,
                "accion": "watchdog_disparado", "rc": -1, "error": str(e)[:200]}


def correr_ratchet(execute=False):
    """Reporta o corre los ratchets de sanidad frozen del repo.

    Args:
        execute: si False (default), solo reporta si cada ruta existe.
            Si True, corre pytest sobre los que existen.

    Returns:
        Dry: {"execute": False, "ratchets": [{"ruta","existe"}]}.
        Execute: agrega "rc" y "stdout_tail" (ultimos 300 chars).
    """
    rutas = []
    existentes = []
    for rel in RATCHETS:
        ruta = os.path.join(RAIZ_REPO, rel)
        existe = os.path.isfile(ruta)
        rutas.append({"ruta": rel, "existe": existe})
        if existe:
            existentes.append(rel)

    if not execute:
        return {"execute": False, "ratchets": rutas}

    try:
        r = subprocess.run(
            [sys.executable, "-m", "pytest", "-q", *existentes],
            cwd=RAIZ_REPO, capture_output=True, text=True, timeout=600,
        )
        return {
            "execute": True,
            "ratchets": rutas,
            "rc": r.returncode,
            "stdout_tail": (r.stdout or "").strip()[-300:],
        }
    except (OSError, subprocess.TimeoutExpired) as e:
        return {"execute": True, "ratchets": rutas, "rc": -1, "error": str(e)[:200]}


def mantener(tarea, execute=False, **kwargs):
    """Dispatch de mantenimiento: limpiar | archivar | relanzar | ratchet | todo.

    Args:
        tarea: una de las 5 tareas frozen.
        execute: propagado a la tarea elegida (default False = dry-run).
        **kwargs: para "archivar", acepta dir_reportes (default
            ~/research/informes) y keep (default 20).

    Returns:
        dict de la tarea elegida. "todo" corre las 4 con el mismo
        execute y devuelve {"limpiar", "archivar", "relanzar", "ratchet"}.
        Tarea desconocida: {"ok": False, "error": "tarea desconocida: ..."}.
    """
    tarea = str(tarea)

    if tarea == "limpiar":
        base = kwargs.get("base", PLATAFORMA)
        return limpiar_temporales(base=base, execute=execute)

    if tarea == "archivar":
        dir_reportes = kwargs.get("dir_reportes") or os.path.expanduser("~/research/informes")
        keep = kwargs.get("keep", 20)
        return archivar_reportes(dir_reportes, keep=keep, execute=execute)

    if tarea == "relanzar":
        return relanzar_organos(execute=execute)

    if tarea == "ratchet":
        return correr_ratchet(execute=execute)

    if tarea == "todo":
        return {
            "limpiar": limpiar_temporales(execute=execute),
            "archivar": mantener("archivar", execute=execute, **kwargs),
            "relanzar": relanzar_organos(execute=execute),
            "ratchet": correr_ratchet(execute=execute),
        }

    return {"ok": False, "error": "tarea desconocida: %s" % tarea}


def _uso():
    print("uso: mantenimiento.py limpiar|archivar|relanzar|ratchet|todo "
          "[--execute] [--dir RUTA] [--keep N]")


def main():
    """CLI: limpiar|archivar|relanzar|ratchet|todo [--execute] [--dir RUTA] [--keep N]"""
    if len(sys.argv) < 2:
        _uso()
        return 2

    tarea = sys.argv[1]
    if tarea not in ("limpiar", "archivar", "relanzar", "ratchet", "todo"):
        _uso()
        return 2

    resto = sys.argv[2:]
    execute = "--execute" in resto
    kwargs = {}

    if "--dir" in resto:
        i = resto.index("--dir")
        if i + 1 < len(resto):
            kwargs["dir_reportes"] = resto[i + 1]

    if "--keep" in resto:
        i = resto.index("--keep")
        if i + 1 < len(resto):
            try:
                kwargs["keep"] = int(resto[i + 1])
            except ValueError:
                print("ERROR: keep debe ser entero", file=sys.stderr)
                return 1

    try:
        reporte = mantener(tarea, execute=execute, **kwargs)
        print(json.dumps(reporte, ensure_ascii=True, indent=1))
        return 0
    except Exception as e:
        print("ERROR %s: %s" % (tarea, e), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
