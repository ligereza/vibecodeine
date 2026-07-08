#!/usr/bin/env python3
"""Exporta una propuesta RD en PDF por tier de evento (under/base/mainstream).

Cada PDF junta: brief institucional (texto exacto de la propuesta) + datos del
evento + plano SVG del stand + rider (necesidades logicas) + cotizacion, con
tablas alineadas. Vectorial via Edge headless (mismo motor que tools/svg/svg_to_pdf.py).

Uso:
    py scripts/export_propuesta_pdf.py                 # los 3 tiers -> _entregas/
    py scripts/export_propuesta_pdf.py under base       # subconjunto
    py scripts/export_propuesta_pdf.py --out C:/ruta    # carpeta de salida
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from html import escape
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from flujo.eventos.presets import apply_event_preset  # noqa: E402
from flujo.plano.costs import calcular_costos  # noqa: E402
from flujo.plano.engine import reglas_rider, render_svg, validate_evento  # noqa: E402

_REPO = Path(__file__).resolve().parents[1]
_BRIEF_TXT = _REPO / "datadrops" / "Propuesta_Reduciendo_Dano.txt"
_EDGE_CANDS = [
    r"C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
    r"C:/Program Files/Microsoft/Edge/Application/msedge.exe",
]

TIERS = ["under", "base", "mainstream"]


def _edge() -> str:
    for e in _EDGE_CANDS:
        if os.path.exists(e):
            return e
    raise SystemExit("Edge no encontrado (ajusta _EDGE_CANDS)")


def _brief_secciones() -> dict[str, str]:
    """Extrae 'Quienes Somos' y 'Objetivo del Servicio' del txt canonico (cp1252)."""
    txt = _BRIEF_TXT.read_text(encoding="cp1252")
    lineas = [l.strip() for l in txt.splitlines()]
    def bloque(desde: str, hasta: str) -> str:
        try:
            i = lineas.index(desde)
            j = lineas.index(hasta)
        except ValueError:
            return ""
        return " ".join(l for l in lineas[i + 1:j] if l)
    return {
        "quienes": bloque("Quiénes Somos", "Objetivo del Servicio"),
        "objetivo": bloque("Objetivo del Servicio", "Modalidades de Intervención"),
    }


def _clp(n: float) -> str:
    return "$" + format(int(n), ",d").replace(",", ".")


def _fila(k: str, v: str) -> str:
    return f'<tr><th>{escape(k)}</th><td>{escape(v)}</td></tr>'


def _html_tier(tier: str, brief: dict[str, str]) -> str:
    ev = apply_event_preset({"preset": tier})
    ev.setdefault("layout_mode", "grid_2x")
    nombre = str(ev.get("preset_label", tier.upper()))
    dur = float(ev.get("duracion_horas", 0) or 0)
    vol = int(ev.get("voluntarios", 0) or 0)
    asis = int(ev.get("asistentes_estimados", 0) or 0)
    testeo = bool(ev.get("incluye_testeo", False))

    svg = render_svg(ev)
    costos = calcular_costos(ev)
    reqs = reglas_rider(ev)
    val = validate_evento(ev)

    datos = "".join([
        _fila("Preset", nombre),
        _fila("Duracion", f"{dur:g} h"),
        _fila("Voluntarios", str(vol)),
        _fila("Asistentes estimados", f"~{asis}"),
        _fila("Incluye testeo", "Si" if testeo else "No"),
        _fila("Layout", str(ev.get("layout_mode"))),
    ])
    rider_rows = "".join(f"<li>{escape(r)}</li>" for r in reqs)
    costos_rows = "".join([
        _fila("Personal", _clp(costos["personal"])),
        _fila("Alimentacion / colacion", _clp(costos["alimentacion"])),
        _fila(f"Mobiliario ({costos['detalle']['mesas']} mesas)", _clp(costos["mobiliario"])),
        _fila(f"Infraestructura ({costos['detalle']['stands']} stands)", _clp(costos["infraestructura"])),
        _fila("Extras (testeo / contencion)", _clp(costos["extras"])),
    ])
    val_html = ""
    if val["warnings"]:
        val_html = "<p class='warn'>Advertencias: " + "; ".join(escape(w) for w in val["warnings"]) + "</p>"

    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
@page {{ size:A4; margin:14mm 12mm; }}
* {{ box-sizing:border-box; }}
body {{ font-family:Inter,Arial,sans-serif; color:#1f2a24; font-size:11px; margin:0; }}
h1 {{ font-size:20px; margin:0 0 2px; }}
h2 {{ font-size:13px; margin:14px 0 6px; border-bottom:2px solid #1f6f4e; padding-bottom:2px; color:#1f6f4e; }}
.sub {{ color:#6b7a72; font-size:10px; margin:0 0 8px; }}
p {{ line-height:1.4; margin:0 0 6px; text-align:justify; }}
table {{ border-collapse:collapse; width:100%; margin:4px 0 8px; }}
th, td {{ border:1px solid #d5ddd8; padding:4px 8px; text-align:left; vertical-align:top; }}
th {{ background:#f1f6f3; width:42%; font-weight:600; }}
td.num {{ text-align:right; font-variant-numeric:tabular-nums; }}
ul {{ margin:4px 0 8px 0; padding-left:18px; }}
li {{ line-height:1.4; margin-bottom:2px; }}
.total {{ font-size:14px; font-weight:800; color:#1f6f4e; margin-top:4px; }}
.warn {{ color:#a86500; font-size:10px; }}
.map {{ border:1px solid #d5ddd8; padding:6px; text-align:center; }}
.map svg {{ max-width:100%; height:auto; }}
.foot {{ margin-top:10px; color:#8b968f; font-size:9px; border-top:1px solid #e3e9e5; padding-top:4px; }}
</style></head><body>
<h1>Propuesta de Intervencion en Terreno &mdash; {escape(nombre)}</h1>
<p class="sub">Reduciendo Dano Chile &middot; entregable operativo por tier de evento</p>

<h2>1. Quienes Somos</h2>
<p>{escape(brief['quienes'])}</p>
<h2>2. Objetivo del Servicio</h2>
<p>{escape(brief['objetivo'])}</p>

<h2>3. Datos del Evento</h2>
<table>{datos}</table>
{val_html}

<h2>4. Plano del Stand</h2>
<div class="map">{svg}</div>

<h2>5. Rider &mdash; Necesidades Operativas</h2>
<ul>{rider_rows}</ul>

<h2>6. Cotizacion Referencial</h2>
<table>{costos_rows}</table>
<p class="total">TOTAL REFERENCIAL: {_clp(costos['total'])}</p>
<p class="warn">Valores referenciales; ajustables por evento (ev["precios"]).</p>

<p class="foot">Generado por flujo.plano (motor unico). Fines preventivos, educativos y de reduccion de riesgos.</p>
</body></html>"""


def _render_pdf(html: str, out_pdf: Path) -> bool:
    tmp = Path(tempfile.gettempdir()) / f"_propuesta_{out_pdf.stem}.html"
    tmp.write_text(html, encoding="utf-8")
    udd = Path(tempfile.gettempdir()) / "_propuesta_edge"
    subprocess.run(
        [_edge(), "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
         "--print-to-pdf-no-header", f"--user-data-dir={udd}",
         f"--print-to-pdf={os.path.abspath(out_pdf)}", tmp.as_uri()],
        check=False,
    )
    return out_pdf.exists()


def main() -> None:
    args = [a for a in sys.argv[1:]]
    out_dir = _REPO / "_entregas"
    if "--out" in args:
        i = args.index("--out")
        out_dir = Path(args[i + 1])
        del args[i:i + 2]
    tiers = [a for a in args if a in TIERS] or TIERS
    out_dir.mkdir(parents=True, exist_ok=True)

    brief = _brief_secciones()
    if not brief["quienes"] or not brief["objetivo"]:
        raise SystemExit(f"No pude extraer el brief de {_BRIEF_TXT}")

    ok = []
    for tier in tiers:
        out_pdf = out_dir / f"propuesta_{tier}.pdf"
        if _render_pdf(_html_tier(tier, brief), out_pdf):
            print(f"OK  {out_pdf}")
            ok.append(tier)
        else:
            print(f"FALLO  {out_pdf}")
    print(f"\n{len(ok)}/{len(tiers)} PDFs en {out_dir}")


if __name__ == "__main__":
    main()
