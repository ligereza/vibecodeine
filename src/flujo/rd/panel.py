"""Los datos de RD que ve un panel, con su allowlist de privacidad.

Vivia dentro del handler del hub. Se saco a un modulo porque ahora lo necesitan
DOS lugares: el hub, que lo sirve en vivo, y el empaquetado del HTML suelto,
que lo hornea adentro para que funcione sin servidor. Duplicar esta funcion
seria duplicar la allowlist, y esa es la peor duplicacion posible: un campo de
contacto agregado manana entraria por la copia que nadie recuerda.
"""
from __future__ import annotations

import json
from pathlib import Path


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

    # Estado de la triangulacion: cuantos eventos se pueden cruzar de verdad
    # (necesitan fecha ISO Y lineup). Es el numero que dice si esa tarea
    # puede avanzar o si primero hay que completar datos.
    todos_ev = [e for p in prods for e in p["eventos"]]
    triangulables = [e for e in todos_ev if e.get("fecha_iso") and e.get("lineup")]
    sin_fuente_primaria = [e for e in todos_ev if e.get("sin_fuente_primaria")]

    return {
        "productoras": prods,
        "venues": venues_cat,
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
