"""Cálculo de costos operativos derivado de las reglas del evento.

El objetivo es dar un desglose rápido que aumente con cada cambio de reglas,
para usarlo como base de cotización.
"""
from __future__ import annotations

from typing import Any, Dict, List

from .engine import es_masivo, mesas_requeridas

# Precios unitarios referenciales (CLP). Se pueden pisar por evento con
# ev["precios"] = {"hora_persona": ..., "mesa": ...} sin tocar codigo.
PRECIOS_REF = {
    "hora_persona": 8_000,
    "alimentacion": 6_000,
    "colacion": 3_500,
    "stand": 35_000,
    "mesa": 4_000,
    "testeo": 45_000,
    "contencion": 25_000,
}


def calcular_costos(ev: Dict[str, Any]) -> Dict[str, Any]:
    """Devuelve un desglose de costos a partir de los parámetros del evento.

    Valores son referenciales; el dueño puede ajustarlos via ev["precios"].
    """
    horas = float(ev.get("duracion_horas", 0))
    voluntarios = int(ev.get("voluntarios", 0))
    testeo = bool(ev.get("incluye_testeo", False))
    masivo = es_masivo(ev)

    precios = {**PRECIOS_REF, **(ev.get("precios") or {})}

    personal = voluntarios * horas * precios["hora_persona"]
    alimentacion = 0.0
    if horas > 5:
        alimentacion = voluntarios * precios["alimentacion"]
    elif horas > 4:
        alimentacion = voluntarios * precios["colacion"]

    mesas = mesas_requeridas(voluntarios, incluye_testeo=testeo)
    mobiliario = mesas * precios["mesa"]

    stands = 1
    if testeo:
        stands += 1
    if masivo:
        stands += 1
    infraestructura = stands * precios["stand"]

    extras = 0.0
    if testeo:
        extras += precios["testeo"]
    if masivo:
        extras += precios["contencion"]

    total = personal + alimentacion + mobiliario + infraestructura + extras

    return {
        "personal": personal,
        "alimentacion": alimentacion,
        "mobiliario": mobiliario,
        "infraestructura": infraestructura,
        "extras": extras,
        "total": total,
        "detalle": {
            "voluntarios": voluntarios,
            "horas": horas,
            "mesas": mesas,
            "stands": stands,
            "testeo": testeo,
            "masivo": masivo,
        },
    }


def resumen_costos(ev: Dict[str, Any]) -> str:
    """Genera un texto legible del desglose de costos."""
    c = calcular_costos(ev)
    d = c["detalle"]
    lines = [f"COTIZACIÓN REFERENCIAL — {ev.get('nombre','Evento')}", "=" * 40, ""]
    lines.append(f"Personal ({d['voluntarios']} voluntarios × {d['horas']} h):       ${c['personal']:,.0f}")
    lines.append(f"Alimentación / colación:                       ${c['alimentacion']:,.0f}")
    lines.append(f"Mobiliario ({d['mesas']} mesas):                         ${c['mobiliario']:,.0f}")
    lines.append(f"Infraestructura ({d['stands']} stands):                    ${c['infraestructura']:,.0f}")
    lines.append(f"Extras (testeo + contención):                  ${c['extras']:,.0f}")
    lines.append("")
    lines.append(f"TOTAL REFERENCIAL:                             ${c['total']:,.0f}")
    lines.append("")
    lines.append("Nota: valores referenciales. Ajustar precios unitarios con el dueño.")
    return "\n".join(lines)
