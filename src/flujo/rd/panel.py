"""Los datos de RD que ve un panel, con su allowlist de privacidad.

Vivia dentro del handler del hub. Se saco a un modulo porque ahora lo necesitan
DOS lugares: el hub, que lo sirve en vivo, y el empaquetado del HTML suelto,
que lo hornea adentro para que funcione sin servidor. Duplicar esta funcion
seria duplicar la allowlist, y esa es la peor duplicacion posible: un campo de
contacto agregado manana entraria por la copia que nadie recuerda.
"""
from __future__ import annotations

import json
import sqlite3
import re
import unicodedata
from collections import Counter
from pathlib import Path


def _event_key(productora_slug: str, nombre: str, fecha: str = "") -> str:
    """Stable key for an RD event card; never uses a display-name lookup."""
    def token(value: str) -> str:
        plain = unicodedata.normalize("NFD", str(value or "").lower())
        plain = "".join(c for c in plain if unicodedata.category(c) != "Mn")
        return re.sub(r"[^a-z0-9]+", "-", plain).strip("-") or "sin-dato"
    return f"rd:{token(productora_slug)}:{token(nombre)}:{token(fecha)}"


def _wire_event_links(productora_slug: str, event: dict, venues: list[dict]) -> None:
    """Add deterministic links without guessing a venue or rider asset.

    An exact normalized venue match is safe to automate. Rider/layout files
    are only linked when the source event explicitly provides their refs;
    otherwise the UI receives a generated key and a review status.
    """
    event["event_key"] = _event_key(productora_slug, event.get("nombre", ""), event.get("fecha_iso") or event.get("fecha", ""))
    event_venue = str(event.get("venue") or "").strip()
    def norm(value: str) -> str:
        plain = unicodedata.normalize("NFD", value.lower())
        plain = "".join(c for c in plain if unicodedata.category(c) != "Mn")
        return re.sub(r"[^a-z0-9]+", " ", plain).strip()
    venue_map = {norm(v.get("nombre", "")): v for v in venues if v.get("nombre")}
    matched = venue_map.get(norm(event_venue)) if event_venue else None
    venue_link = {"status": "exact" if matched else "pending_review"}
    if matched and matched.get("id"):
        venue_link["id"] = matched["id"]
    if matched:
        venue_link["name"] = matched["nombre"]
    elif event_venue:
        # Conservar el texto de origen sólo cuando existe; no emitir una
        # cadena vacía como si fuera un dato de venue.
        venue_link["name"] = event_venue
    event["venue_link"] = venue_link
    rider_ref = str(event.get("rider_ref") or "").strip()
    layout_ref = str(event.get("layout_ref") or "").strip()
    rider_link = {
        "status": "explicit" if rider_ref else "pending_review",
        "generated_key": event["event_key"] + ":rider",
    }
    if rider_ref:
        rider_link["ref"] = rider_ref
    layout_link = {
        "status": "explicit" if layout_ref else "pending_review",
        "generated_key": event["event_key"] + ":layout",
    }
    if layout_ref:
        layout_link["ref"] = layout_ref
    event["rider_link"] = rider_link
    event["layout_link"] = layout_link


def rd_event_link(root: Path, event_key: str, overrides: dict | None = None) -> dict:
    """Resolve one exact RD event and consume the existing Plano engine.

    This is a read/render projection, not a second database.  A generated key
    is not treated as proof that a rider or layout exists: rendering remains
    ``pending_review`` until the source event has the real pack and operating
    parameters.  Optional overrides are for the operator's current draft and
    never get written back to the catalogue.
    """
    wanted = str(event_key or "").strip()
    if not wanted:
        return {"status": "invalid", "error": "event_key es obligatorio"}
    catalog = datos_panel(Path(root))
    found = None
    for productora in catalog["productoras"]:
        for event in productora.get("eventos", []):
            if event.get("event_key") == wanted:
                found = (productora, event)
                break
        if found:
            break
    if not found:
        return {"status": "not_found", "event_key": wanted,
                "error": "event_key no existe en la ficha RD"}

    productora, event = found
    draft = dict(event)
    supplied = overrides if isinstance(overrides, dict) else {}
    for key in ("pack", "preset", "duracion_horas", "asistentes_estimados",
                "voluntarios", "layout_mode"):
        value = supplied.get(key, event.get(key))
        if value is not None and str(value).strip() != "":
            draft[key] = value

    required = ("pack", "duracion_horas", "asistentes_estimados")
    missing = [key for key in required if draft.get(key) in (None, "")]
    result = {
        "status": "pending_review" if missing else "ready",
        "event_key": wanted,
        "productora_slug": productora["slug"],
        "productora": productora["nombre"],
        "event": event,
        "missing": missing,
        "links": {
            "venue": event.get("venue_link"),
            "rider": event.get("rider_link"),
            "layout": event.get("layout_link"),
        },
    }
    if not missing:
        from ..serve.server import api_plano_render
        result["render"] = api_plano_render(draft)
    return result


def _candidatos_logo(base, slug: str, ref: str = "") -> list:
    """Archivos donde puede estar el logo de `slug`, en orden de preferencia.

    El nombre del archivo NO siempre es el slug: en disco conviven
    `grid_system.svg` (slug `gridsystem`) y `club_freedom.svg` (slug
    `freedom`). El resumen de la base ya resolvia asi, pero este endpoint
    buscaba solo por slug: contaba el logo como existente y despues no podia
    servirlo, o sea que el panel decia "logo vectorial" sobre un recuadro
    vacio.
    """
    norm = slug.replace("_", "").replace("-", "").lower()
    candidatos = [base / "vector" / f"{slug}.svg"]
    if ref:
        candidatos.append(base / "vector" / f"{ref}.svg")
    vector = base / "vector"
    if vector.is_dir():
        candidatos += [p for p in sorted(vector.glob("*.svg"))
                       if p.stem.replace("_", "").replace("-", "").lower() == norm]
    descargas = base / "descargas"
    if descargas.is_dir():
        candidatos += sorted(descargas.glob(f"{slug}.*"))
        if ref:
            candidatos += sorted(descargas.glob(f"{ref}.*"))
        candidatos += [p for p in sorted(descargas.glob("*"))
                       if p.stem.replace("_", "").replace("-", "").lower() == norm]
    return candidatos

# ── Symbols the events manager adds from the app ──────────────────
_SIMBOLO_MAX_BYTES = 512 * 1024


def datos_panel(root) -> dict:
    """Base de datos RD (productoras + venues) para el panel del hub.

    Fuente de verdad: `data/productoras/*.json` + `knowledge/venues/*.yaml`
    (no `data/rd.db`, que es una proyeccion regenerable y gitignored).

    REGLA DE PRIVACIDAD (2026-07-25, pedido del area de eventos RD): este
    endpoint arma cada registro campo por campo con una ALLOWLIST explicita.
    Nunca hace `**dict` del json de origen. Si manana alguien agrega un campo
    de contacto al json, NO se filtra solo: hay que agregarlo aca a proposito.
    Campos deliberadamente excluidos: `instagram` y cualquier dato de
    contacto. Ver tambien PlanoTool.tsx (el rider no lleva bloque de
    contactos).
    """
    prods: list[dict] = []
    pdir = root / "data" / "productoras"
    logos_dir = root / "knowledge" / "logos"
    if pdir.is_dir():
        for f in sorted(pdir.glob("*.json")):
            try:
                d = json.loads(f.read_text(encoding="utf-8"))
            except Exception:
                continue
            slug = f.stem
            # Estado del logo: el json referencia el id; el archivo real vive
            # en knowledge/logos/. Se reporta lo que existe en disco, no lo
            # que el json dice que deberia existir.
            logos = d.get("logos") or []
            estado_logo = "sin_ficha"
            ref_yaml = ""
            if logos and isinstance(logos[0], dict):
                estado_logo = str(logos[0].get("estado") or "sin_estado")
                ref_yaml = str(logos[0].get("knowledge") or "")
            # El nombre del archivo de logo NO siempre es el slug: en disco
            # conviven `grid_system.svg` (slug `gridsystem`) y
            # `club_freedom.svg` (slug `freedom`). Resolver solo por slug
            # reportaba "sin vector" sobre logos que si existian, y por eso
            # el estado de la DB se veia peor de lo que era.
            # Orden: 1) el yaml que referencia el propio json, 2) el slug,
            # 3) comparacion normalizada (sin guiones ni guiones bajos).
            cand: list[str] = []
            if ref_yaml.endswith(".yaml"):
                cand.append(Path(ref_yaml).stem)
            cand.append(slug)
            tiene_vector = any((logos_dir / "vector" / f"{c}.svg").exists() for c in cand)
            if not tiene_vector and (logos_dir / "vector").is_dir():
                norm = slug.replace("_", "").replace("-", "").lower()
                tiene_vector = any(
                    v.stem.replace("_", "").replace("-", "").lower() == norm
                    for v in (logos_dir / "vector").glob("*.svg")
                )
            venues_raw = d.get("venues") or []
            venues = [
                {
                    "nombre": str(v.get("nombre") or ""),
                    "estado": str(v.get("estado") or ""),
                    "preferido": bool(v.get("preferido")),
                }
                for v in venues_raw
                if isinstance(v, dict)
            ]
            # Eventos normalizados: fecha a ISO y lineup como campo propio.
            # Sin esto la triangulacion (fecha + headliner -> productora) no
            # tiene dos campos que cruzar.
            eventos_norm: list[dict] = []
            try:
                from ..rd.database import _event_source_gate
                from ..rd.eventos import normalizar_productora
                norm, _avisos = normalizar_productora(d)
                for ev in (norm.get("eventos") or []):
                    if isinstance(ev, dict):
                        fuentes_primarias, sin_fuente_primaria = _event_source_gate(
                            ev.get("fuente")
                        )
                        eventos_norm.append({
                            "nombre": str(ev.get("nombre") or ""),
                            "fecha": str(ev.get("fecha") or ""),
                            "fecha_iso": ev.get("fecha_iso"),
                            "fecha_confianza": str(ev.get("fecha_confianza") or ""),
                            "venue": str(ev.get("venue") or ""),
                            "estado": str(ev.get("estado") or ""),
                            "fuente": str(ev.get("fuente") or ""),
                            "fuentes_primarias": json.loads(fuentes_primarias),
                            "sin_fuente_primaria": bool(sin_fuente_primaria),
                            "lineup": [str(x) for x in (ev.get("lineup") or [])],
                            "co_organiza": [str(x) for x in (ev.get("co_organiza") or [])],
                        })
                        if ev.get("rider_ref"):
                            eventos_norm[-1]["rider_ref"] = str(ev["rider_ref"])
                        if ev.get("layout_ref"):
                            eventos_norm[-1]["layout_ref"] = str(ev["layout_ref"])
            except Exception:
                eventos_norm = []

            prods.append({
                "slug": slug,
                "nombre": str(d.get("name") or slug),
                "aliases": [str(a) for a in (d.get("aliases") or [])],
                "tipos": [str(t) for t in (d.get("tipos_fecha") or [])],
                "venues": venues,
                # `archivo` dice si hay algo que servir. El panel pedia el
                # logo de las 20 productoras aunque 14 no tienen ninguno, y
                # eso dejaba 18 errores 404 en la consola del navegador:
                # ruido que se lee como si la app estuviera fallando.
                "logo": {
                    "estado": estado_logo,
                    "vector": tiene_vector,
                    "archivo": any(
                        c.is_file() for c in _candidatos_logo(
                            logos_dir, slug,
                            Path(ref_yaml).stem if ref_yaml.endswith(".yaml") else "")
                    ),
                },
                "confirmada": bool(str(d.get("confirmed") or "").strip()),
                "confirmacion": str(d.get("confirmed") or ""),
                "fuente": str(d.get("fuente_datos") or ""),
                "eventos": eventos_norm,
            })

    venues_cat: list[dict] = []
    vdir = root / "knowledge" / "venues"
    if vdir.is_dir():
        for f in sorted(vdir.glob("*.yaml")):
            try:
                raw = f.read_text(encoding="utf-8")
            except Exception:
                continue
            # Parseo minimo de las claves planas que interesan: evita
            # depender de PyYAML en el proceso del servidor.
            info = {"id": f.stem, "nombre": f.stem, "tipo": "", "escala": "", "capacidad": ""}
            for line in raw.splitlines():
                if line.startswith("name:"):
                    info["nombre"] = line.split(":", 1)[1].strip()
                elif line.startswith("type:"):
                    info["tipo"] = line.split(":", 1)[1].strip()
                elif line.startswith("scale_default:"):
                    info["escala"] = line.split(":", 1)[1].strip()
                elif line.startswith("capacity_bucket:"):
                    info["capacidad"] = line.split(":", 1)[1].strip()
            venues_cat.append(info)

    # Vinculos deterministicos para la ficha: el evento se puede automatizar
    # sin convertir una coincidencia de nombre en una afirmacion. Solo el
    # venue normalizado exacto se marca como seguro; rider/layout requieren un
    # ref explicito en la fuente y, mientras tanto, conservan una clave estable
    # para que el operador pueda completar el enlace sin crear otro evento.
    for productora in prods:
        for evento in productora["eventos"]:
            _wire_event_links(productora["slug"], evento, venues_cat)

    # Estado de la triangulacion: cuantos eventos se pueden cruzar de verdad
    # (necesitan fecha ISO Y lineup). Es el numero que dice si esa tarea
    # puede avanzar o si primero hay que completar datos.
    todos_ev = [e for p in prods for e in p["eventos"]]
    triangulables = [e for e in todos_ev if e.get("fecha_iso") and e.get("lineup")]
    sin_fuente_primaria = [e for e in todos_ev if e.get("sin_fuente_primaria")]

    return {
        "productoras": prods,
        "venues": venues_cat,
        "evidencia_2025": _evidencia_2025(root),
        "resumen": {
            "productoras": len(prods),
            "con_vector": sum(1 for p in prods if p["logo"]["vector"]),
            "confirmadas": sum(1 for p in prods if p["confirmada"]),
            "venues": len(venues_cat),
            "eventos": len(todos_ev),
            "eventos_triangulables": len(triangulables),
            "eventos_sin_fuente_primaria": len(sin_fuente_primaria),
            "eventos_sin_fecha_iso": sum(1 for e in todos_ev if not e.get("fecha_iso")),
            "eventos_sin_lineup": sum(1 for e in todos_ev if not e.get("lineup")),
        },
        "excluido_a_proposito": ["instagram", "contactos"],
        "connected": True,
    }


def _evidencia_2025(root) -> list[dict]:
    """Read-only projection of the 2025 testing evidence.

    This is deliberately separate from ``productora_eventos``: the imported
    workbook still has pending event/producer/venue links and the sheet name
    is not enough evidence to invent one.  The web panel may therefore show
    the historical source event and its exact ``event_id`` without attaching
    it to the wrong producer.  Values are source wording only; no colour is
    interpreted as identity, purity, dose or safety.
    """
    db_path = Path(root) / "data" / "rd.db"
    if not db_path.is_file():
        return []
    uri = f"file:{db_path.resolve().as_posix()}?mode=ro"
    try:
        conn = sqlite3.connect(uri, uri=True)
        conn.row_factory = sqlite3.Row
        events = conn.execute(
            "SELECT event_id, source_sheet_index, source_sheet_name, "
            "event_label_candidate, source_period_label, date_iso_candidate, "
            "date_status, duplicate_status, duplicate_group_size, "
            "venue_name_candidate, producer_name_candidate, link_status "
            "FROM testeo_eventos_fuente WHERE source_period_label = '2025' "
            "ORDER BY COALESCE(date_iso_candidate, ''), source_sheet_index"
        ).fetchall()
        out: list[dict] = []
        for event in events:
            rows = conn.execute(
                "SELECT format_raw, result_1_raw, result_2_raw, result_3_raw, "
                "result_4_raw FROM testeo_filas_fuente "
                "WHERE event_id = ? AND row_status = 'data' ORDER BY source_row",
                (event["event_id"],),
            ).fetchall()
            declared = Counter()
            results = Counter()
            for row in rows:
                label = str(row["format_raw"] or "").strip() or "sin registro"
                declared[label] += 1
                for field in ("result_1_raw", "result_2_raw", "result_3_raw", "result_4_raw"):
                    value = str(row[field] or "").strip()
                    if value:
                        results[value] += 1

            def distribution(counter: Counter) -> list[dict]:
                total = sum(counter.values())
                return [
                    {"valor": value, "conteo": count,
                     "porcentaje": round((count / total) * 100, 1) if total else 0}
                    for value, count in counter.most_common()
                ]

            out.append({
                "event_id": event["event_id"],
                "hoja": event["source_sheet_name"],
                "indice_hoja": event["source_sheet_index"],
                "nombre": event["event_label_candidate"] or event["source_sheet_name"],
                "periodo": event["source_period_label"],
                "fecha_iso": event["date_iso_candidate"],
                "estado_fecha": event["date_status"],
                "estado_duplicado": event["duplicate_status"],
                "tamano_grupo_duplicado": event["duplicate_group_size"],
                "venue_fuente": event["venue_name_candidate"],
                "productora_fuente": event["producer_name_candidate"],
                "estado_enlace": event["link_status"],
                "filas": len(rows),
                "muestra_declarada": {
                    "campo": "format_raw",
                    "total": sum(declared.values()),
                    "distribucion": distribution(declared),
                },
                "resultados_colorimetricos": {
                    "campos": ["result_1_raw", "result_2_raw", "result_3_raw", "result_4_raw"],
                    "total": sum(results.values()),
                    "distribucion": distribution(results),
                },
            })
        conn.close()
        return out
    except (OSError, sqlite3.Error):
        return []
