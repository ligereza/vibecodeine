"""Motor de planos de stands para eventos.

Genera planos SVG y riders de texto a partir de constantes de realidad
(medidas de mesas, toldos, sillas, pasillos) y reglas operativas sobre los
parámetros del evento.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Tuple

def _load_flujo_styles() -> Dict[str, Any]:
    """Carga estilos desde flujo si existe (integración con línea editorial)."""
    from ..paths import asset_root
    flujo_path = asset_root() / "projects" / "flujo" / "flujo.json"
    if flujo_path.exists():
        # estilos opcionales: si el JSON esta roto se sigue con defaults,
        # pero solo se toleran fallas de lectura/parseo, no cualquier cosa
        try:
            data = json.loads(flujo_path.read_text(encoding="utf-8"))
            return data.get("colors", {})
        except (json.JSONDecodeError, OSError, UnicodeDecodeError):
            return {}
    return {}


# ============================================================
# 1. CONSTANTES DE REALIDAD (metros)
# ============================================================
# Umbral unico para clasificar un evento como masivo (fuente de verdad; antes
# el literal 2000 estaba repetido en 5 lugares entre engine.py y costs.py)
UMBRAL_MASIVO = 2000


def es_masivo(ev: Dict[str, Any]) -> bool:
    """True si el evento es masivo (bandera explicita o asistentes >= umbral)."""
    return bool(ev.get("masivo", False)) or int(ev.get("asistentes_estimados", 0) or 0) >= UMBRAL_MASIVO


CONSTANTES = {
    "mesa":        {"w": 2.0, "h": 0.7},     # mesa rectangular estándar
    "silla":       {"w": 0.5, "h": 0.5},     # asiento
    "toldo_3x3":   {"w": 3.0, "h": 3.0},     # stand base
    "toldo_3x45":  {"w": 4.5, "h": 3.0},
    "toldo_6x3":   {"w": 6.0, "h": 3.0},
    "pasillo_min": 1.2,                       # ancho mínimo de circulación
    "asiento_area": 0.5,                      # lado de un asiento
}


# ============================================================
# 2. REGLAS (constantes operativas) -> requerimientos del rider
# ============================================================
def mesas_requeridas(voluntarios: int, incluye_testeo: bool = False) -> int:
    """Regla unica de mesas: 1 base + 1 por cada 5 voluntarios (+1 si hay testeo).

    Fuente unica para rider (sin testeo, lo lista aparte) y costos (con testeo).
    """
    mesas = 1 + max(0, (voluntarios - 1)) // 5
    if incluye_testeo:
        mesas += 1
    return mesas


def reglas_rider(ev: Dict[str, Any]) -> List[str]:
    """Deriva requerimientos del rider según los parámetros del evento."""
    req: List[str] = []
    horas = float(ev.get("duracion_horas", 0))
    voluntarios = int(ev.get("voluntarios", 0))
    asistentes = int(ev.get("asistentes_estimados", 0))
    testeo = bool(ev.get("incluye_testeo", False))
    masivo = es_masivo(ev)

    if horas > 5:
        req.append("Jornada > 5 h: ALIMENTACIÓN obligatoria para el equipo (producción o costo extra).")
    elif horas > 4:
        req.append("Jornada > 4 h: agregar colación / viático para el equipo.")

    mesas = mesas_requeridas(voluntarios)
    req.append(f"{voluntarios} voluntarios -> {mesas} mesa(s) (1 base + 1 por cada 5).")

    if testeo:
        req.append("Incluye testeo: +1 stand contiguo + 1 mesa extra para reactivos (ventilación obligatoria).")
    if masivo:
        req.append("Evento masivo: agregar ZONA DE CONTENCIÓN/DESCANSO de baja estimulación sensorial.")
    if asistentes:
        req.append(f"{asistentes} asistentes estimados: dimensionar personal y material acorde.")
    req.append("Coordinación previa con producción, seguridad y equipo médico. Acceso para carga/descarga.")
    return req


def modulos_desde_evento(ev: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Decide qué módulos (stands/zonas) incluir según el evento."""
    voluntarios = int(ev.get("voluntarios", 0))
    testeo = bool(ev.get("incluye_testeo", False))
    masivo = es_masivo(ev)

    mods = [{"tipo": "stand", "nombre": "Stand Informativo", "toldo": "toldo_3x3",
             "mesas": 1, "sillas": min(voluntarios, 4)}]
    if testeo:
        mods.append({"tipo": "stand", "nombre": "Stand Testeo", "toldo": "toldo_3x3",
                     "mesas": 2, "sillas": min(max(voluntarios - 4, 1), 4)})
    if masivo:
        mods.append({"tipo": "zona", "nombre": "Contención / Descanso", "toldo": "toldo_3x3",
                     "mesas": 0, "sillas": 0})
    return mods


# ============================================================
# 3. LAYOUT — coloca módulos en fila con pasillo (coordenadas en metros)
# ============================================================
@dataclass
class Caja:
    nombre: str
    x: float
    y: float
    w: float
    h: float
    hijos: List["Caja"] = field(default_factory=list)
    rol: str = "stand"


def solve_layout(ev: Dict[str, Any]) -> Tuple[List[Caja], float, float]:
    """Coloca los módulos según layout_mode.

    Soporta:
    - "row" (default, fila horizontal con pasillos) — legacy
    - "grid_2x" — colocación aproximada en grilla 2 columnas (más compacta)

    El evento puede declarar "layout_mode": "grid_2x".
    Ver también schemas/layout_primitives.schema.json para evolución declarativa futura.
    """
    mods = modulos_desde_evento(ev)
    layout_mode = ev.get("layout_mode", "row")
    pasillo = CONSTANTES["pasillo_min"]

    if layout_mode == "grid_2x":
        return _solve_grid_2x(mods, pasillo)

    # default: fila (row)
    return _solve_row(mods, pasillo)


def _solve_row(mods: List[Dict], pasillo: float) -> Tuple[List[Caja], float, float]:
    """Implementación original en fila."""
    x = 0.0
    cajas: List[Caja] = []
    max_h = 0.0
    for m in mods:
        toldo = CONSTANTES[m["toldo"]]
        caja = Caja(m["nombre"], x, 0.0, toldo["w"], toldo["h"], rol=m["tipo"])
        mw, mh = CONSTANTES["mesa"]["w"], CONSTANTES["mesa"]["h"]
        for i in range(m.get("mesas", 0)):
            my = 0.2 + i * (mh + 0.15)
            if my + mh > toldo["h"]:
                break
            caja.hijos.append(Caja("mesa", 0.2, my, min(mw, toldo["w"] - 0.4), mh, rol="mesa"))
        sa = CONSTANTES["asiento_area"]
        for i in range(m.get("sillas", 0)):
            sx = 0.2 + i * (sa + 0.1)
            if sx + sa > toldo["w"]:
                break
            caja.hijos.append(Caja("silla", sx, toldo["h"] - sa - 0.2, sa, sa, rol="silla"))
        cajas.append(caja)
        max_h = max(max_h, toldo["h"])
        x += toldo["w"] + pasillo
    ancho_total = max(0.0, x - pasillo)
    return cajas, ancho_total, max_h


def _solve_grid_2x(mods: List[Dict], pasillo: float) -> Tuple[List[Caja], float, float]:
    """Layout simple en grilla de 2 columnas (demo de estructura más declarativa)."""
    col_w = max((CONSTANTES[m["toldo"]]["w"] for m in mods), default=3.0)
    row_h = max((CONSTANTES[m["toldo"]]["h"] for m in mods), default=3.0)
    cajas: List[Caja] = []
    for idx, m in enumerate(mods):
        col = idx % 2
        row = idx // 2
        toldo = CONSTANTES[m["toldo"]]
        x = col * (col_w + pasillo)
        y = row * (row_h + pasillo * 0.6)
        caja = Caja(m["nombre"], x, y, toldo["w"], toldo["h"], rol=m["tipo"])
        # colocar las cantidades REALES del modulo; el unico limite es que
        # quepan dentro del toldo (misma regla que _solve_row)
        mw, mh = CONSTANTES["mesa"]["w"], CONSTANTES["mesa"]["h"]
        for i in range(m.get("mesas", 0)):
            my = 0.2 + i * (mh + 0.1)
            if my + mh > toldo["h"]:
                break
            caja.hijos.append(Caja("mesa", 0.2, my, min(mw, toldo["w"] - 0.4), mh, rol="mesa"))
        sa = CONSTANTES["asiento_area"]
        for i in range(m.get("sillas", 0)):
            sx = 0.2 + i * (sa + 0.08)
            if sx + sa > toldo["w"]:
                break
            caja.hijos.append(Caja("silla", sx, toldo["h"] - sa - 0.15, sa, sa, rol="silla"))
        cajas.append(caja)
    cols = 2 if len(mods) > 1 else 1
    rows = (len(mods) + 1) // 2
    ancho = cols * col_w + (cols - 1) * pasillo
    alto = rows * row_h + (rows - 1) * pasillo * 0.6
    return cajas, ancho, alto


def _esc(s: str) -> str:
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ============================================================
# 4. RENDER SVG (escala metros -> px)
# ============================================================
# Zonas del layout logico de produccion: cada icono operativo cae en su grupo
_ZONAS_ICONOS = [
    ("SERVICIOS", ["tent", "table", "testeo"]),
    ("INFRAESTRUCTURA", ["power", "light", "water", "food", "heating"]),
    ("SEGURIDAD", ["extinguisher", "medical", "security"]),
    ("COORDINACION", ["contact", "contencion", "sensory", "trash"]),
]

# Paleta dark RD (coincide con el canvas del editor web, PlanoTool.tsx)
_BG = "#09090b"
_PANEL = "rgba(255,255,255,0.035)"
_LIGHT = "#e8eef0"
_MUTED = "#8b968f"
_STAND = "#10b981"
_ZONA = "#a78bfa"


def render_svg(ev: Dict[str, Any], px_por_metro: float = 90.0) -> str:
    """Plano SVG en estilo dark RD: modulos + iconos operativos por zona logica.

    Los iconos (luces, extintor, agua, medico, testeo, contencion...) se derivan
    del evento via iconos.simbolos_de_evento y se agrupan como en un montaje real.
    Las sillas no se dibujan (confunden el plano; su conteo va en el rider).
    """
    from . import iconos

    cajas, W_m, H_m = solve_layout(ev)
    s = px_por_metro
    activos = set(iconos.simbolos_de_evento(ev))
    grupos = [(t, [k for k in ks if k in activos]) for t, ks in _ZONAS_ICONOS]
    grupos = [(t, ks) for t, ks in grupos if ks]

    margin = 0.8
    paso_icono = 1.7          # separacion horizontal entre iconos (m)
    alto_grupo = 2.1          # titulo + fila de iconos (m)
    max_iconos = max((len(ks) for _, ks in grupos), default=1)
    ancho_iconos = max_iconos * paso_icono
    W_m_total = max(W_m, ancho_iconos)
    H_iconos = len(grupos) * alto_grupo

    W = (W_m_total + 2 * margin) * s
    H = (H_m + 1.4 + H_iconos + 2 * margin) * s
    ox, oy = margin * s, (margin + 0.9) * s

    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W:.0f}" height="{H:.0f}" viewBox="0 0 {W:.0f} {H:.0f}">']
    out.append(f'<rect width="{W:.0f}" height="{H:.0f}" fill="{_BG}"/>')
    out.append(f'<text x="{ox:.0f}" y="{0.55*s:.0f}" font-family="Inter,Arial" font-size="{0.34*s:.0f}" '
               f'font-weight="800" fill="{_LIGHT}">PLANO — {_esc(ev.get("nombre","Evento"))}</text>')
    out.append(f'<text x="{ox:.0f}" y="{0.9*s:.0f}" font-family="Inter,Arial" font-size="{0.16*s:.0f}" '
               f'fill="{_MUTED}">Escala 1m = {px_por_metro:.0f}px · {len(cajas)} modulo(s) · reduccion de danos</text>')

    # --- modulos (stands / zonas) ---
    for c in cajas:
        cx, cy = ox + c.x * s, oy + c.y * s
        col = _STAND if c.rol == "stand" else _ZONA
        out.append(f'<rect x="{cx:.0f}" y="{cy:.0f}" width="{c.w*s:.0f}" height="{c.h*s:.0f}" '
                   f'fill="{_PANEL}" stroke="{col}" stroke-width="3" rx="8"/>')
        for h in c.hijos:
            if h.rol != "mesa":
                continue  # sillas fuera a proposito
            hx, hy = cx + h.x * s, cy + h.y * s
            out.append(f'<rect x="{hx:.0f}" y="{hy:.0f}" width="{h.w*s:.0f}" height="{h.h*s:.0f}" '
                       f'fill="rgba(212,183,143,0.18)" stroke="#c9a96a" stroke-width="1.5" rx="2"/>')
        out.append(f'<text x="{cx+8:.0f}" y="{cy+0.32*s:.0f}" font-family="Inter,Arial" font-size="{0.17*s:.0f}" '
                   f'font-weight="700" fill="{col}" style="paint-order:stroke" stroke="{_BG}" '
                   f'stroke-width="{0.05*s:.0f}">{_esc(c.nombre)}</text>')
        out.append(f'<text x="{cx+8:.0f}" y="{cy+c.h*s-8:.0f}" font-family="Inter,Arial" '
                   f'font-size="{0.12*s:.0f}" fill="{_MUTED}">{c.w:g}×{c.h:g} m</text>')

    # --- iconos operativos por zona logica ---
    y_base = oy + (H_m + 0.8) * s
    for titulo, keys in grupos:
        out.append(f'<line x1="{ox:.0f}" y1="{y_base:.0f}" x2="{ox + W_m_total*s:.0f}" y2="{y_base:.0f}" '
                   f'stroke="rgba(255,255,255,0.08)" stroke-width="1"/>')
        out.append(f'<text x="{ox:.0f}" y="{y_base+0.32*s:.0f}" font-family="Inter,Arial" '
                   f'font-size="{0.15*s:.0f}" font-weight="700" fill="{_MUTED}" letter-spacing="1">{titulo}</text>')
        cy_icon = y_base + 1.15 * s
        for i, key in enumerate(keys):
            cx_icon = ox + (i + 0.5) * paso_icono * s
            col = iconos.COLORES.get(key, _LIGHT)
            escala = s / 150.0
            out.append(iconos.icono(key, cx_icon, cy_icon, escala, col))
            out.append(f'<text x="{cx_icon:.0f}" y="{cy_icon+0.72*s:.0f}" text-anchor="middle" '
                       f'font-family="Inter,Arial" font-size="{0.12*s:.0f}" fill="{_LIGHT}">'
                       f'{_esc(iconos.ETIQUETAS.get(key, key))}</text>')
        y_base += alto_grupo * s

    out.append('</svg>')
    return "\n".join(out)


# ============================================================
# 5. RIDER de texto
# ============================================================
def render_rider(ev: Dict[str, Any]) -> str:
    lines = [f"RIDER TÉCNICO — {ev.get('nombre','Evento')}", "=" * 40, ""]
    lines.append(f"Duración: {ev.get('duracion_horas','?')} h · Voluntarios: {ev.get('voluntarios','?')} "
                 f"· Asistentes est.: {ev.get('asistentes_estimados','?')}")
    lines.append("")
    lines.append("Requerimientos (derivados por reglas):")
    for r in reglas_rider(ev):
        lines.append(f"  • {r}")
    return "\n".join(lines)


# ============================================================
# 6. QA operativo (rider/plano)
# ============================================================
def validate_evento(ev: Dict[str, Any]) -> Dict[str, Any]:
    """Valida un evento antes de imprimir/exportar rider y plano.

    Devuelve un reporte simple y serializable:
    {
      "ok": bool,
      "errors": [str],
      "warnings": [str],
      "summary": {...},
    }

    La validacion es deliberadamente conservadora: no bloquea decisiones humanas,
    pero detecta datos faltantes o inconsistencias que suelen romper la operacion.
    """
    errors: List[str] = []
    warnings: List[str] = []

    nombre = str(ev.get("nombre", "")).strip()
    if not nombre:
        errors.append("Falta nombre del evento.")

    duracion = _as_float(ev.get("duracion_horas"), "duracion_horas", errors)
    voluntarios = _as_int(ev.get("voluntarios"), "voluntarios", errors)
    asistentes = _as_int(ev.get("asistentes_estimados", 0), "asistentes_estimados", errors)

    if duracion is not None:
        if duracion <= 0:
            errors.append("duracion_horas debe ser mayor que 0.")
        elif duracion > 12:
            warnings.append("Jornada muy larga: revisar turnos, alimentacion y relevo de voluntarios.")

    if voluntarios is not None:
        if voluntarios <= 0:
            errors.append("voluntarios debe ser mayor que 0.")
        elif voluntarios < 2:
            warnings.append("Dotacion minima: revisar si 1 voluntario es suficiente para operar el stand.")

    if asistentes is not None:
        if asistentes < 0:
            errors.append("asistentes_estimados no puede ser negativo.")
        elif asistentes >= UMBRAL_MASIVO and not ev.get("masivo", False):
            warnings.append(f"asistentes_estimados >= {UMBRAL_MASIVO}: se tratara como evento masivo aunque masivo=false.")

    layout_mode = ev.get("layout_mode", "row")
    if layout_mode not in {"row", "grid_2x"}:
        errors.append("layout_mode debe ser 'row' o 'grid_2x'.")

    if bool(ev.get("incluye_testeo", False)) and (voluntarios or 0) < 3:
        warnings.append("Incluye testeo con menos de 3 voluntarios: revisar dotacion para reactivos y contencion.")

    try:
        cajas, ancho_m, alto_m = solve_layout(ev)
    except Exception as exc:  # pragma: no cover - defensive path
        errors.append(f"No se pudo resolver el layout: {exc}")
        cajas, ancho_m, alto_m = [], 0.0, 0.0

    mesas = sum(1 for caja in cajas for hijo in caja.hijos if hijo.rol == "mesa")
    sillas = sum(1 for caja in cajas for hijo in caja.hijos if hijo.rol == "silla")
    stands = sum(1 for caja in cajas if caja.rol == "stand")
    zonas = sum(1 for caja in cajas if caja.rol == "zona")

    if cajas and ancho_m <= 0:
        errors.append("El layout calculado tiene ancho invalido.")
    if cajas and alto_m <= 0:
        errors.append("El layout calculado tiene alto invalido.")
    if bool(ev.get("incluye_testeo", False)) and stands < 2:
        errors.append("incluye_testeo requiere stand informativo + stand testeo.")
    if (asistentes or 0) >= UMBRAL_MASIVO and zonas < 1:
        errors.append("Evento masivo requiere zona de contencion/descanso.")
    if (voluntarios or 0) > 0 and mesas < 1:
        errors.append("El layout debe incluir al menos una mesa operativa.")

    return {
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "summary": {
            "nombre": nombre or "Evento",
            "layout_mode": layout_mode,
            "modulos": len(cajas),
            "stands": stands,
            "zonas": zonas,
            "mesas": mesas,
            "sillas": sillas,
            "ancho_m": round(ancho_m, 2),
            "alto_m": round(alto_m, 2),
            "requerimientos": len(reglas_rider(ev)),
        },
    }


def render_validation_report(ev: Dict[str, Any]) -> str:
    """Renderiza validate_evento como texto legible para CLI/airdrop."""
    report = validate_evento(ev)
    summary = report["summary"]
    lines = [
        f"VALIDACION RIDER/PLANO - {summary['nombre']}",
        "=" * 46,
        f"Estado: {'OK' if report['ok'] else 'ERROR'}",
        f"Layout: {summary['layout_mode']} | modulos: {summary['modulos']} | tamano: {summary['ancho_m']} x {summary['alto_m']} m",
        f"Stands: {summary['stands']} | zonas: {summary['zonas']} | mesas: {summary['mesas']} | sillas: {summary['sillas']}",
        "",
    ]
    if report["errors"]:
        lines.append("Errores:")
        lines.extend(f"  - {item}" for item in report["errors"])
        lines.append("")
    if report["warnings"]:
        lines.append("Advertencias:")
        lines.extend(f"  - {item}" for item in report["warnings"])
        lines.append("")
    if not report["errors"] and not report["warnings"]:
        lines.append("Sin hallazgos. Listo para rider/plano.")
    return "\n".join(lines).rstrip()


def _as_int(value: Any, field: str, errors: List[str]) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        errors.append(f"{field} debe ser un numero entero.")
        return None


def _as_float(value: Any, field: str, errors: List[str]) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        errors.append(f"{field} debe ser numerico.")
        return None


# ============================================================
# 7. Carga de evento
# ============================================================
def load_evento(path: Path) -> Dict[str, Any]:
    """Carga un evento desde un archivo JSON."""
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("El evento debe ser un objeto JSON")
    return data
