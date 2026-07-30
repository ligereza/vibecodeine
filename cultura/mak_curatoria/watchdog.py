#!/usr/bin/env python3
"""Watchdog curatoria MAK: si la percepcion se pausa, se estanca o termina,
crea UN issue en GitHub (notificacion al telefono del usuario). Cron */20.
Anti-spam via flag; se rearma solo si la corrida vuelve a avanzar."""
import json
import subprocess
import time
from pathlib import Path

BASE = Path.home() / "curatoria"
ESTADO = BASE / "estado.json"
FLAG = BASE / ".watchdog_alerted"
REPO = "ligereza/vibecodeine"


def alerta(titulo: str, cuerpo: str) -> None:
    if FLAG.exists():
        return
    try:
        subprocess.run(
            ["gh", "issue", "create", "--repo", REPO,
             "--title", f"[CURATORIA] {titulo}",
             "--body", cuerpo + "\n\nDetalle: ~/curatoria/reportes/REPORTE_CURATORIA.md (en MAK).",
             "--label", "bloqueado"],
            timeout=60, check=False)
        FLAG.touch()
    except Exception:
        pass


def main() -> None:
    if not ESTADO.exists():
        return
    try:
        e = json.loads(ESTADO.read_text())
    except Exception:
        return
    proc = e.get("procesados", 0)
    tot = e.get("total_trabajo", "?")
    pausa = e.get("pausado_por")
    if pausa == "fin":
        alerta("percepcion TERMINADA",
               f"Corrida completa: {proc}/{tot} fichas. Lista para pasada relacional.")
        return
    if pausa:
        alerta("percepcion PAUSADA",
               f"pausado_por={pausa}; procesados={proc}/{tot}; "
               f"ultimos_errores={e.get('ultimos_errores')}")
        return
    edad_min = (time.time() - ESTADO.stat().st_mtime) / 60
    if edad_min > 25:
        alerta("percepcion ESTANCADA",
               f"estado.json sin cambios hace {int(edad_min)} min; "
               f"procesados={proc}/{tot}. Revisar proceso/GPU en MAK.")
        return
    if FLAG.exists():
        FLAG.unlink()


if __name__ == "__main__":
    main()
