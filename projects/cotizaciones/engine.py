"""Cotizaciones duales integradas con aistetic y planos.

Genera 2 versiones:
- productora: branded, infográfico (usa aistetic + formatos)
- interno (ong/empresa): desglose detallado
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from src.flujo.plano import load_evento, resumen_costos  # reuse existing

def _load_aistetic() -> Dict[str, Any]:
    p = Path("projects/aistetic/aistetic.json")
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return {}

def generar_cotizacion(evento_path: Path, audiencia: str = "productora") -> str:
    """Genera cotización según audiencia (integrado aistetic + formatos)."""
    ev = load_evento(evento_path)
    aistetic = _load_aistetic()
    costos = resumen_costos(ev)
    paleta = aistetic.get("colors", {})

    if audiencia == "productora":
        return f"""COTIZACIÓN — {ev.get('nombre', 'Evento')} (Reduciendo Daño, diseñador)
Estilo aistetic: {paleta}
Infografía: usa catálogo formatos (A4/rider) + aistetic para branded.

{ev.get('notas', '')}

{costos}
"""
    else:
        return f"""COTIZACIÓN INTERNA — {ev.get('nombre')}
Para ONG/trabajador/empresa (desglose real)
{costos}

Ajustar precios. Integrar con infografías de aistetic.
"""

if __name__ == "__main__":
    print(generar_cotizacion(Path("projects/plano/ejemplos/evento_ejemplo.json"), "productora"))