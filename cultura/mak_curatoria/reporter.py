#!/usr/bin/env python3
"""reporter.py -- reporte periodico del departamento CURATORIA de MAK.

Lee DIR_OUT/estado.json + DIR_OUT/fichas/fichas.jsonl (escritos por
percepcion.py) y escribe DIR_OUT/reportes/REPORTE_CURATORIA.md
(sobrescribe). Pensado para cron cada 20 min.

    python3 reporter.py DIR_OUT
"""
import json
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

VENTANA_VELOCIDAD_MIN = 20  # ventana para velocidad archivos/min
UMBRAL_CORRIENDO_MIN = 10  # estado.json con mtime mas nuevo que esto = CORRIENDO
MAX_ULTIMOS_ERRORES_REPORTE = 5


# ---------------------------------------------------------------------------
# Carga de datos
# ---------------------------------------------------------------------------

def cargar_estado(dir_out) -> dict:
    p = Path(dir_out) / "estado.json"
    if not p.exists():
        return {}
    try:
        with p.open("r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return {}


def cargar_fichas(dir_out) -> list[dict]:
    p = Path(dir_out) / "fichas" / "fichas.jsonl"
    fichas: list[dict] = []
    if not p.exists():
        return fichas
    try:
        with p.open("r", encoding="utf-8") as f:
            for linea in f:
                linea = linea.strip()
                if not linea:
                    continue
                try:
                    registro = json.loads(linea)
                except json.JSONDecodeError:
                    continue
                if isinstance(registro, dict):
                    fichas.append(registro)
    except OSError:
        pass
    return fichas


def _parsear_ts(ts_str: str):
    if not ts_str:
        return None
    try:
        return datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
    except ValueError:
        return None


# ---------------------------------------------------------------------------
# Calculos
# ---------------------------------------------------------------------------

def tabla_por_fuente_tipo(fichas: list[dict]) -> list[str]:
    conteo = Counter((f.get("fuente", "?"), f.get("tipo", "?")) for f in fichas)
    lineas = [
        "| fuente | tipo | cantidad |",
        "|---|---|---:|",
    ]
    if conteo:
        for fuente, tipo in sorted(conteo.keys()):
            lineas.append("| %s | %s | %d |" % (fuente, tipo, conteo[(fuente, tipo)]))
    else:
        lineas.append("| - | - | 0 |")
    return lineas


def velocidad_archivos_por_min(fichas: list[dict],
                                ventana_min: int = VENTANA_VELOCIDAD_MIN) -> float:
    """archivos/min en la ultima ventana, usando el ts de cada ficha."""
    tss = sorted(t for t in (_parsear_ts(f.get("ts", "")) for f in fichas) if t is not None)
    if len(tss) < 2:
        return 0.0

    ultimo = tss[-1]
    limite = ultimo - timedelta(minutes=ventana_min)
    en_ventana = [t for t in tss if t >= limite]
    if len(en_ventana) < 2:
        return 0.0

    delta_min = (en_ventana[-1] - en_ventana[0]).total_seconds() / 60.0
    if delta_min <= 0:
        return float(len(en_ventana))
    return round(len(en_ventana) / delta_min, 2)


MUESTRA_SEG_PROCESO = 50


def velocidad_real_archivos_por_min(fichas: list[dict],
                                     muestra: int = MUESTRA_SEG_PROCESO):
    """archivos/min real, a partir del "seg_proceso" de cada ficha (tiempo
    real de analisis por archivo), en vez de gaps entre timestamps.

    Devuelve (archivos_por_min, seg_por_archivo_prom); (0.0, 0.0) si no
    hay fichas con seg_proceso valido.
    """
    valores = [
        f.get("seg_proceso") for f in fichas
        if isinstance(f.get("seg_proceso"), (int, float)) and f.get("seg_proceso") > 0
    ]
    if not valores:
        return 0.0, 0.0

    recientes = valores[-muestra:]
    prom_seg = sum(recientes) / len(recientes)
    if prom_seg <= 0:
        return 0.0, 0.0
    return round(60.0 / prom_seg, 2), round(prom_seg, 2)


def eta_lineal(estado: dict, velocidad: float) -> str:
    total = estado.get("total_trabajo", 0) or 0
    procesados = estado.get("procesados", 0) or 0
    faltan = max(total - procesados, 0)

    if faltan == 0:
        return "completo"
    if velocidad <= 0:
        return "sin datos suficientes (falan %d archivos)" % faltan

    minutos = faltan / velocidad
    horas = minutos / 60.0
    return "%.0f min (~%.1f h) para %d archivos restantes" % (minutos, horas, faltan)


def ficha_compacta(f: dict) -> str:
    vision = f.get("vision") or {}
    descripcion = (vision.get("descripcion") or "")[:80]
    return "%s | tipo=%s | categoria=%s | calidad=%s | %.1fs | %s | ts=%s" % (
        f.get("ruta_rel", "?"),
        f.get("tipo", "?"),
        f.get("categoria", "") or "-",
        f.get("calidad_senal", "?"),
        f.get("seg_proceso") or 0.0,
        descripcion,
        f.get("ts", "?"),
    )


def ultimas_por_fuente(fichas: list[dict]) -> dict:
    ultimas: dict = {}
    for f in fichas:
        fuente = f.get("fuente", "?")
        ts = _parsear_ts(f.get("ts", "")) or datetime.min.replace(tzinfo=timezone.utc)
        actual = ultimas.get(fuente)
        if actual is None or ts >= actual[0]:
            ultimas[fuente] = (ts, f)
    return {fuente: par[1] for fuente, par in ultimas.items()}


def estado_texto(dir_out, estado: dict) -> str:
    """CORRIENDO | PAUSADO(<motivo>) | TERMINADO segun pausado_por +
    frescura de estado.json (si no hay pausa explicita, se asume que se
    sigue corriendo mientras estado.json se haya tocado hace poco)."""
    pausado_por = estado.get("pausado_por")
    if pausado_por == "fin":
        return "TERMINADO"
    if pausado_por:
        return "PAUSADO(%s)" % pausado_por

    p = Path(dir_out) / "estado.json"
    if not p.exists():
        return "PAUSADO(sin_estado)"
    try:
        mtime = datetime.fromtimestamp(p.stat().st_mtime, tz=timezone.utc)
    except OSError:
        return "PAUSADO(sin_estado)"

    delta_min = (datetime.now(timezone.utc) - mtime).total_seconds() / 60.0
    if delta_min < UMBRAL_CORRIENDO_MIN:
        return "CORRIENDO"
    return "PAUSADO(estancado)"


# ---------------------------------------------------------------------------
# Render
# ---------------------------------------------------------------------------

def render_md(dir_out, estado: dict, fichas: list[dict]) -> str:
    total = estado.get("total_trabajo", 0) or 0
    procesados = estado.get("procesados", 0) or 0
    pct = round(100.0 * procesados / total, 1) if total else 0.0

    velocidad = velocidad_archivos_por_min(fichas)
    velocidad_real, seg_prom_real = velocidad_real_archivos_por_min(fichas)
    velocidad_para_eta = velocidad_real if velocidad_real > 0 else velocidad
    eta = eta_lineal(estado, velocidad_para_eta)
    estado_str = estado_texto(dir_out, estado)
    por_fuente = estado.get("por_fuente") or {}

    if velocidad_real > 0:
        linea_velocidad_real = (
            "- Velocidad real (seg_proceso, hasta %d fichas): %.2f "
            "archivos/min (%.1fs/archivo)" % (MUESTRA_SEG_PROCESO, velocidad_real, seg_prom_real)
        )
    else:
        linea_velocidad_real = "- Velocidad real: sin datos (fichas sin seg_proceso)"

    lineas = [
        "# Reporte Curatoria",
        "",
        "Generado: %s" % datetime.now(timezone.utc).isoformat(),
        "",
        "## Resumen",
        "",
        "- Total trabajo: %d" % total,
        "- Procesados: %d (%.1f%%)" % (procesados, pct),
        "- Por fuente: rd=%d, ig=%d" % (por_fuente.get("rd", 0), por_fuente.get("ig", 0)),
        "- Velocidad (ultima ventana %d min, por timestamps): %.2f archivos/min" % (
            VENTANA_VELOCIDAD_MIN, velocidad),
        linea_velocidad_real,
        "- ETA: %s" % eta,
        "",
        "## Procesados por fuente y tipo",
        "",
    ]
    lineas.extend(tabla_por_fuente_tipo(fichas))
    lineas.append("")

    lineas.extend([
        "## Errores",
        "",
        "- Errores totales: %d" % (estado.get("errores_totales", 0) or 0),
        "- Errores seguidos actuales: %d" % (estado.get("errores_seguidos", 0) or 0),
        "",
        "### Ultimos errores",
        "",
    ])
    ultimos_errores = estado.get("ultimos_errores") or []
    if ultimos_errores:
        for e in ultimos_errores[-MAX_ULTIMOS_ERRORES_REPORTE:]:
            lineas.append("- %s: %s" % (e.get("ruta_rel", "?"), e.get("error", "?")))
    else:
        lineas.append("- (sin errores)")
    lineas.append("")

    lineas.extend(["## Muestra de fichas", ""])
    ultimas = ultimas_por_fuente(fichas)
    if ultimas:
        for fuente in sorted(ultimas.keys()):
            lineas.append("- [%s] %s" % (fuente, ficha_compacta(ultimas[fuente])))
    else:
        lineas.append("- (sin fichas todavia)")
    lineas.append("")

    lineas.append("ESTADO: %s" % estado_str)
    lineas.append("")
    return "\n".join(lineas)


def escribir_reporte(dir_out) -> Path:
    dir_out = Path(dir_out)
    estado = cargar_estado(dir_out)
    fichas = cargar_fichas(dir_out)
    md = render_md(dir_out, estado, fichas)

    dir_reportes = dir_out / "reportes"
    dir_reportes.mkdir(parents=True, exist_ok=True)
    ruta = dir_reportes / "REPORTE_CURATORIA.md"
    ruta.write_text(md, encoding="utf-8")
    return ruta


def main() -> int:
    if len(sys.argv) < 2:
        print("uso: reporter.py DIR_OUT", file=sys.stderr)
        return 2

    dir_out = sys.argv[1]
    try:
        ruta = escribir_reporte(dir_out)
    except OSError as exc:
        print("ERROR: %s" % exc, file=sys.stderr)
        return 1

    print("reporte escrito en %s" % ruta)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
