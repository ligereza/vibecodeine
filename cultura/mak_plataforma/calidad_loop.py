#!/usr/bin/env python3
"""calidad_loop.py -- metricas del loop codex autonomo (generar -> entregar ->
vetear -> merge), F2a. Baseline medible de la calidad del vibecoding local
ANTES de intentar mejorarlo.

Fuentes reales (ver cultura/mak_codex/interfaz_codex.py, generar.py,
cultura/mak_plataforma/entregar.py):

- jobs.jsonl: un job codex por linea, escrito por interfaz_codex._lanzar()
  cuando el job TERMINA. Campos ciertos: job_id, pedido, modo, estado, path,
  error, t, ms. modo en {"generar", "revisar", "testear", "debug"} -- SOLO
  "generar" pasa por el sandbox de generar.py y produce piezas cosechables
  por entregar.py; revisar/testear/debug operan sobre archivos existentes y
  pueden terminar "listo"/"FALLO" sin ser jamas elegibles para el pipeline
  de entrega (metricas de generacion/entrega se filtran a modo=="generar").
  estado en {"en cola", "corriendo", "listo", "FALLO", "BLOQUEADO"}
  ("BLOQUEADO" = guardia de entrada de interfaz_codex rechazo el pedido
  antes de generar codigo; esa guardia SOLO corre para modo=="generar", ver
  interfaz_codex._lanzar). smoke_ok / smoke_stderr_tail son OPCIONALES: los
  agrega generar.py al meta de la pieza .md (F2b/#139); solo aparecen
  directo en jobs.jsonl si algo los copio ahi (ver
  tests/test_entregar_smoke_gate.py). jobs.jsonl viejos, o jobs de modos sin
  sandbox (revisar/testear/debug/mejora-libre), NUNCA traen smoke_ok.

- codex_delivered.json (opcional, escrito por entregar.py.guardar_estado):
  {"entregados": [job_id, ...], "slugs": [slug, ...]}. Un job_id en
  "entregados" significa que entregar.py abrio un PR DRAFT para esa pieza
  (compilo OK, paso el gate de smoke). NO significa que el PR fue MERGEADO:
  ese ultimo paso (revisor humano + CI + branch protection) no deja rastro
  en ningun archivo local -- requeriria la API de GitHub, fuera del alcance
  stdlib-puro de este modulo. La "tasa merge" que exponemos es en realidad
  tasa de ENTREGA (PR abierto), la mejor aproximacion local disponible.

- backlog_codex.txt (cultura/mak_plataforma/, tambien ~/plataforma/ en el
  organismo real): una tarea por linea; comentarios ('#' al inicio) se
  ignoran. Las lineas agregadas por backlog_codex.py llevan el marcador
  '# auto YYYYMMDD' al final -- unica fuente de fecha confiable. Lineas
  curadas a mano (sin marcador) no tienen fecha: se cuentan pero se excluyen
  del calculo de edad (no se puede fabricar una fecha que no existe).

Regla de datos faltantes (igual que metricas_capataz.py con
decisor_nivel): un campo/estado ausente se EXCLUYE del denominador de esa
metrica puntual, nunca se cuenta como si fuera False/0.

Salida: render_md() -> texto para CALIDAD_LOOP.md.
"""
from __future__ import annotations

import argparse
import datetime
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ESTADOS_TERMINALES = {"listo", "FALLO", "BLOQUEADO"}

_VEREDICTO_RE = re.compile(r"guardia de codigo:\s*([A-Z_]+)")
_EXC_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*(?:Error|Exception))\b")
_MARCADOR_EDAD_RE = re.compile(r"#\s*auto\s+(\d{8})\s*$")


# ---------------------------------------------------------------------------
# carga (IO separado de calculo)
# ---------------------------------------------------------------------------

def cargar_jobs(ruta: str) -> list[dict]:
    """Carga jobs.jsonl. Tolerante: lineas vacias/corruptas o sin job_id se
    saltan (job_id es la unica identidad confiable de un job)."""
    ruta_p = Path(ruta)
    if not ruta_p.exists():
        return []
    jobs: list[dict] = []
    try:
        with ruta_p.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except (json.JSONDecodeError, ValueError):
                    continue
                if isinstance(entry, dict) and entry.get("job_id"):
                    jobs.append(entry)
    except OSError:
        pass
    return jobs


def cargar_entregados(ruta: str) -> set[str] | None:
    """Carga codex_delivered.json -> set de job_id con PR draft abierto.

    Archivo ausente/corrupto -> None (desconocido: NO hay evidencia de
    entregas, distinto de "0 entregados"). Lo distingue tasas_entrega()."""
    ruta_p = Path(ruta)
    try:
        with ruta_p.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError):
        return None
    if not isinstance(data, dict):
        return None
    return set(data.get("entregados") or [])


def cargar_backlog(ruta: str) -> list[str]:
    """Carga backlog_codex.txt: lineas no vacias, sin las puramente
    comentario ('#' al inicio)."""
    ruta_p = Path(ruta)
    if not ruta_p.exists():
        return []
    lineas: list[str] = []
    try:
        with ruta_p.open("r", encoding="utf-8") as f:
            for cruda in f:
                s = cruda.strip()
                if s and not s.startswith("#"):
                    lineas.append(s)
    except OSError:
        pass
    return lineas


# ---------------------------------------------------------------------------
# calculo puro
# ---------------------------------------------------------------------------

def _causa_bloqueo(error: str) -> str:
    """De 'guardia de codigo: VEREDICTO -- razon' extrae VEREDICTO; si no
    matchea (formato distinto/legado) usa el error crudo truncado."""
    m = _VEREDICTO_RE.search(error or "")
    if m:
        return m.group(1)
    limpio = (error or "").strip()
    return limpio[:60] if limpio else "desconocido"


def _causa_smoke(stderr_tail: str) -> str:
    """Nombre de excepcion (ej. AssertionError) de la ULTIMA linea del
    stderr que matchea 'algo Error/Exception'; si no hay ninguna, 'otro';
    si el tail esta vacio, 'desconocido'."""
    stderr_tail = (stderr_tail or "").strip()
    if not stderr_tail:
        return "desconocido"
    for linea in reversed(stderr_tail.splitlines()):
        m = _EXC_RE.search(linea.strip())
        if m:
            return m.group(1)
    return "otro"


def tasas_entrega(jobs: list[dict], entregados: set[str] | None = None) -> dict:
    """Tasa de entrega del loop codex: generados vs entregados vs
    rechazados. entregados=None => la parte de entrega queda None (no hay
    codex_delivered.json disponible, no se asume 0).

    "generados_listo" y "fallo_sandbox" se filtran a modo == "generar":
    interfaz_codex tambien lanza jobs modo revisar/testear/debug que pueden
    terminar "listo"/"FALLO" sin haber pasado por el pipeline de codigo de
    generar.py -- mezclarlos infla/ensucia la tasa de entrega real (esos
    jobs nunca son elegibles para entregar.py). "bloqueado_guardia" NO
    necesita este filtro: la guardia de entrada de interfaz_codex._lanzar
    solo corre para modo == "generar" (ver docstring del modulo)."""
    total = len(jobs)
    terminales = [j for j in jobs if j.get("estado") in ESTADOS_TERMINALES]
    en_progreso = total - len(terminales)

    generar_terminales = [j for j in terminales if j.get("modo", "generar") == "generar"]
    listos = [j for j in generar_terminales if j.get("estado") == "listo"]
    fallos = [j for j in generar_terminales if j.get("estado") == "FALLO"]
    bloqueados = [j for j in terminales if j.get("estado") == "BLOQUEADO"]

    rechazados_smoke = [j for j in listos if j.get("smoke_ok") is False]
    smoke_desconocido = sum(1 for j in listos if "smoke_ok" not in j)

    entregados_n = None
    entrega_pct = None
    if entregados is not None:
        entregados_n = sum(1 for j in listos if j.get("job_id") in entregados)
        entrega_pct = (round(100.0 * entregados_n / len(listos), 1)
                       if listos else 0.0)

    return {
        "total": total,
        "en_progreso": en_progreso,
        "terminales": len(terminales),
        "generados_listo": len(listos),
        "fallo_sandbox": len(fallos),
        "bloqueado_guardia": len(bloqueados),
        "rechazado_smoke": len(rechazados_smoke),
        "smoke_desconocido": smoke_desconocido,
        "entregados": entregados_n,
        "entrega_pct": entrega_pct,
    }


def causas_rechazo(jobs: list[dict]) -> dict:
    """Bugs cazados por el ratchet del loop, agrupados por causa: guardia de
    entrada (bloqueado antes de generar), gate de smoke (F2b, codigo que no
    corre), fallo de sandbox crudo (sin llegar a rc==0 tras reparacion).

    fallo_sandbox y rechazado_smoke se filtran a modo == "generar" (mismo
    criterio que tasas_entrega -- ver esa docstring); bloqueado_guardia no
    necesita filtro porque la guardia de entrada solo corre para
    modo == "generar"."""
    terminales = [j for j in jobs if j.get("estado") in ESTADOS_TERMINALES]
    generar_terminales = [j for j in terminales if j.get("modo", "generar") == "generar"]
    bloqueados = [j for j in terminales if j.get("estado") == "BLOQUEADO"]
    fallos = [j for j in generar_terminales if j.get("estado") == "FALLO"]
    rechazados_smoke = [j for j in generar_terminales
                        if j.get("estado") == "listo" and j.get("smoke_ok") is False]

    por_guardia = Counter(_causa_bloqueo(j.get("error", "")) for j in bloqueados)
    por_smoke = Counter(_causa_smoke(j.get("smoke_stderr_tail", ""))
                        for j in rechazados_smoke)

    return {
        "bloqueado_guardia_n": len(bloqueados),
        "bloqueado_guardia_causas": dict(por_guardia),
        "rechazado_smoke_n": len(rechazados_smoke),
        "rechazado_smoke_causas": dict(por_smoke),
        "fallo_sandbox_n": len(fallos),
    }


def edad_backlog(lineas: list[str], hoy: datetime.date | None = None) -> dict:
    """Antiguedad (dias) de los items pendientes del backlog codex.

    Solo cuenta lineas con marcador '# auto YYYYMMDD' (agregadas por
    backlog_codex.py). Lineas curadas a mano sin marcador se cuentan en
    'sin_fecha' pero se EXCLUYEN de min/max/promedio -- no hay fecha real
    que usar, y contarlas como edad 0 mentiria sobre que tan viejo es el
    backlog."""
    hoy = hoy or datetime.date.today()
    edades: list[int] = []
    sin_fecha = 0
    for linea in lineas:
        m = _MARCADOR_EDAD_RE.search(linea)
        if not m:
            sin_fecha += 1
            continue
        try:
            fecha = datetime.datetime.strptime(m.group(1), "%Y%m%d").date()
        except ValueError:
            sin_fecha += 1
            continue
        edades.append((hoy - fecha).days)

    total = len(lineas)
    if not edades:
        return {
            "total_pendientes": total,
            "con_fecha": 0,
            "sin_fecha": sin_fecha,
            "edad_min_dias": None,
            "edad_max_dias": None,
            "edad_prom_dias": None,
        }
    return {
        "total_pendientes": total,
        "con_fecha": len(edades),
        "sin_fecha": sin_fecha,
        "edad_min_dias": min(edades),
        "edad_max_dias": max(edades),
        "edad_prom_dias": round(sum(edades) / len(edades), 1),
    }


# ---------------------------------------------------------------------------
# render
# ---------------------------------------------------------------------------

def _fmt(v: Any, sufijo: str = "") -> str:
    return "—" if v is None else "%s%s" % (v, sufijo)


def render_md(entrega: dict, causas: dict, backlog: dict) -> str:
    """Genera markdown con las tres tablas de calidad del loop codex."""
    lines = [
        "# Calidad del Loop Codex (F2a -- baseline)",
        "",
        "Metricas del loop autonomo generar -> entregar -> vetear -> merge.",
        "Ver docstring de calidad_loop.py para de donde sale cada dato y",
        "que faltante se excluye (nunca se cuenta como 0).",
        "",
        "## Loop generar -> entregar",
        "",
    ]

    lines.extend([
        f"- **Jobs totales**: {entrega.get('total', 0)}",
        f"- **En progreso (en cola/corriendo)**: {entrega.get('en_progreso', 0)}",
        f"- **Terminales**: {entrega.get('terminales', 0)}",
        f"- **Generados (listo)**: {entrega.get('generados_listo', 0)}",
        f"- **Fallo sandbox**: {entrega.get('fallo_sandbox', 0)}",
        f"- **Bloqueado por guardia**: {entrega.get('bloqueado_guardia', 0)}",
        f"- **Rechazado por smoke (F2b)**: {entrega.get('rechazado_smoke', 0)}",
        f"- **Smoke desconocido (jobs sin smoke_ok)**: {entrega.get('smoke_desconocido', 0)}",
        f"- **Entregados (PR draft abierto)**: {_fmt(entrega.get('entregados'))} "
        "(desconocido si no hay codex_delivered.json -- ver nota mas abajo)",
        f"- **Tasa de entrega sobre generados**: {_fmt(entrega.get('entrega_pct'), '%')}",
        "",
        "Nota: \"entregado\" = entregar.py abrio PR draft (compilo + paso smoke).",
        "NO es \"mergeado\": ese paso depende del revisor humano + CI + branch",
        "protection y no queda registrado en ningun archivo local (requeriria",
        "la API de GitHub). Esta metrica es la mejor aproximacion local a",
        "\"tasa merge\", no la tasa de merge real.",
        "",
        "## Bugs cazados por el ratchet (rechazos por causa)",
        "",
        "| gate | rechazos | causas |",
        "|---|---:|---|",
    ])

    def _causas_txt(d: dict) -> str:
        if not d:
            return "—"
        return ", ".join("%s: %d" % (k, v) for k, v in sorted(d.items(),
                          key=lambda kv: (-kv[1], kv[0])))

    lines.append("| guardia de entrada | %d | %s |" % (
        causas.get("bloqueado_guardia_n", 0),
        _causas_txt(causas.get("bloqueado_guardia_causas", {}))))
    lines.append("| smoke (F2b) | %d | %s |" % (
        causas.get("rechazado_smoke_n", 0),
        _causas_txt(causas.get("rechazado_smoke_causas", {}))))
    lines.append("| sandbox (fallo crudo) | %d | — |" % causas.get("fallo_sandbox_n", 0))
    lines.append("")

    lines.extend([
        "## Edad del backlog codex",
        "",
        f"- **Items pendientes**: {backlog.get('total_pendientes', 0)}",
        f"- **Con fecha (marcador auto)**: {backlog.get('con_fecha', 0)}",
        f"- **Sin fecha (curados a mano, excluidos de edad)**: {backlog.get('sin_fecha', 0)}",
        f"- **Edad minima**: {_fmt(backlog.get('edad_min_dias'), ' dias')}",
        f"- **Edad maxima**: {_fmt(backlog.get('edad_max_dias'), ' dias')}",
        f"- **Edad promedio**: {_fmt(backlog.get('edad_prom_dias'), ' dias')}",
        "",
    ])

    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Genera metricas de calidad del loop codex (F2a baseline)."
    )
    parser.add_argument("jobs", nargs="?", default="jobs.jsonl",
                        help="Ruta a jobs.jsonl (default: jobs.jsonl en cwd)")
    parser.add_argument("--entregados", default=None,
                        help="Ruta a codex_delivered.json (opcional)")
    parser.add_argument("--backlog", default="backlog_codex.txt",
                        help="Ruta a backlog_codex.txt "
                             "(default: backlog_codex.txt en cwd)")
    args = parser.parse_args()

    jobs = cargar_jobs(args.jobs)
    entregados = cargar_entregados(args.entregados) if args.entregados else None
    backlog_lineas = cargar_backlog(args.backlog)

    entrega = tasas_entrega(jobs, entregados)
    causas = causas_rechazo(jobs)
    backlog = edad_backlog(backlog_lineas)

    md = render_md(entrega, causas, backlog)

    salida = Path(args.jobs).parent / "CALIDAD_LOOP.md"
    try:
        salida.write_text(md, encoding="utf-8")
        print(f"wrote {salida.name}")
        return 0
    except OSError as e:
        print(f"error escribiendo {salida}: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
