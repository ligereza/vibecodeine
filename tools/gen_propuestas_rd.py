#!/usr/bin/env python3
"""Wire the perception's digested candidates to mineria_rd's draft writer.

Why this exists (2026-07-29): `cultura/mak_plataforma/mineria_rd.py` was never
executed because its `minar()` step re-OCRs the same files the perception
already processes and fights for the same GPU. But its OUTPUT side --
`proponer()`, which writes productora/venue drafts calcando the real schemas of
`data/productoras/*.json` and `knowledge/venues/*.yaml` into a separate folder
for human-reviewed PR -- is exactly the missing last hop to the RD database.

This tool feeds that draft writer from what already exists IN THE REPO:
`docs/rd/candidatos_curatoria/candidatos_db.jsonl`, the perception's fichas
digested by `extraccion_db.py` (dedup latest-wins, sequence collapse, fuzzy
match 0.82 against both catalogues, own-identity deny-list, garbage filter).
No OCR, no GPU, no box: it runs anywhere the repo is checked out.

The user's constraint, honoured here: the database in the repo is fine, so the
extraction must be clean, must not create duplicates, and must not generate
garbage on top of what is already right. Concretely:

- Rows are re-matched against the CURRENT catalogues at draft time (the jsonl
  may be older than the catalogues), reusing extraccion_db's fuzzy matcher --
  never mineria_rd's exact-only `consolidar()`, whose weak dedup would produce
  "Sundek" vs "Sundeck" twins.
- Only event categories generate candidates (a logo or a ficha_sustancia has
  no productora); own-identity rows (RD itself) never do.
- "dudoso" matches (0.70-0.82) never get a NEW productora/venue draft: a
  dubious name is a triangulation question, not evidence for a new catalog
  entry. They DO get an event draft when they identify a specific event
  (fecha+venue) of what is very likely an existing productora, but that
  draft's own `estado` says `needs_confirmation` -- never `confirmado_auto`
  -- so the uncertainty travels with the data instead of disappearing.
- Drafts require MIN_OBRAS_PROPUESTA distinct works of evidence, the same
  threshold extraccion_db already applies to its own proposals.
- Nothing is written outside --outdir (mineria_rd._ruta_segura enforces it),
  and nothing ever touches data/ or knowledge/ directly: drafts enter the
  repo only through a human-reviewed PR.

Retirement: when the perception writes drafts itself, or the RD database gains
another ingestion path.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "cultura" / "mak_plataforma"))
sys.path.insert(0, str(REPO_ROOT / "cultura" / "mak_curatoria"))

import extraccion_db  # noqa: E402
import mineria_rd  # noqa: E402

CANDIDATOS_DEFAULT = REPO_ROOT / "docs" / "rd" / "candidatos_curatoria" / "candidatos_db.jsonl"
OUTDIR_DEFAULT = REPO_ROOT / "docs" / "rd" / "propuestas_mineria"

# Only these categories can name a productora/venue that exists: a logo or a
# ficha_sustancia carrying a "productora" is vision noise, not evidence.
CATEGORIAS_EVENTO = ("flyer_evento", "foto_evento")

# Vision often answers a city where the flyer names a venue ("Santiago de
# Chile" is not a venue). Measured on the real 970-row jsonl 2026-07-29.
GEOGRAFIA_NO_VENUE = frozenset({
    "santiago", "santiago de chile", "santiago chile", "chile",
    "region metropolitana",
})


def _clave(nombre: str) -> str:
    """Accumulation key for NEW candidates: accents do not split identity.

    mineria_rd._slug alone keys "Nébula Fest" and "Nebula Fest" apart (it
    never strips accents), so a name spelled both ways split its evidence and
    fell under the threshold -- the same twin class this tool exists to avoid.
    Normalize first (extraccion_db strips accents), then slug.
    """
    return mineria_rd._slug(extraccion_db.normalizar_texto(nombre))


# Bug real (2026-09-09, issue #556): un candidato que matchea una productora
# YA CONOCIDA (ratio>=0.82) o dudosa (0.70-0.82) hoy se cuenta y se descarta --
# ni el evento nuevo (fecha, venue, headliners) ni el propio "dudoso" quedan
# en ningun lado consultable. Un flyer repetido de una productora conocida no
# suma nada a la base; la base nunca crece con lo que ya conoce. Esto agrega
# el hop que faltaba: eventos de productoras conocidas/dudosas tambien se
# acumulan y se proponen, con el mismo gate de PR humana que ya usa
# `proponer()` -- no se salta la revision, solo deja de tirar el dato.
RD_LOCAL_RAIZ = Path.home() / "RD"


def _rutas_locales_rd(ruta_rel: str) -> dict:
    """Rutas locales del flyer (fuente + render, si existe), relativas a
    ~/RD -- el mismo arbol que ya usa puente_issues.py / percepcion.py, y
    donde issue_descarga_ig.yml deja cada flyer procesado por un issue
    (RD/desde_issues/issue<N>-<shortcode>.jpg + RD/renders_issues/...png).
    Solo referencia rutas relativas a ~/RD (nunca una ruta absoluta de disco
    en un artefacto que puede terminar en un PR publico)."""
    rutas = {"fuente": "RD/%s" % ruta_rel}
    if ruta_rel.startswith("desde_issues/"):
        nombre = Path(ruta_rel).stem
        render_rel = "renders_issues/%s.png" % nombre
        if (RD_LOCAL_RAIZ / render_rel).is_file():
            rutas["render"] = "RD/%s" % render_rel
    return rutas


def _clave_evento(fecha_cruda: str, venue_crudo: str) -> str:
    """Clave de dedup para 'es el mismo evento': fecha+venue normalizados.
    No pretende entender fechas en prosa (eso es trabajo de
    flujo.rd.eventos.parsear_fecha en otra capa) -- solo evitar proponer el
    mismo evento dos veces cuando dos flyers describen la misma fecha/venue
    con la misma redaccion o casi."""
    return "%s|%s" % (extraccion_db.normalizar_texto(fecha_cruda),
                       extraccion_db.normalizar_texto(venue_crudo))


def cargar_eventos_existentes(canonico: str, repo_root: Path) -> tuple[str, set]:
    """(slug, claves) de los eventos que YA tiene data/productoras/<slug>.json
    -- para no re-proponer un evento que la productora ya registra, sea que
    haya llegado por humano o por una corrida anterior de esta misma
    herramienta.

    El slug se resuelve buscando el archivo cuyo campo "name" sea EXACTO al
    canonico -- nunca re-derivando un slug a partir del nombre. Medido
    2026-09-09: 9 productoras legacy tienen un archivo sin guion bajo
    (piknic.json, panalrecords.json, streetmachine.json...) mientras su
    "name" trae espacios ("Piknic Electronik", "Panal Records"...); adivinar
    el slug desde el nombre ("piknic_electronik") no encuentra esos archivos
    y el borrador de evento sale con slug_productora vacio (nombre de
    archivo sin el prefijo de productora). slug="" si ningun archivo trae
    ese name (productora sin json propio todavia; no deberia pasar para algo
    clasificado "match", pero no se asume)."""
    directorio = repo_root / "data" / "productoras"
    if directorio.is_dir():
        for archivo in sorted(directorio.glob("*.json")):
            try:
                datos = json.loads(archivo.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            if isinstance(datos, dict) and datos.get("name") == canonico:
                claves = set()
                for evento in datos.get("eventos") or []:
                    if isinstance(evento, dict):
                        claves.add(_clave_evento(str(evento.get("fecha") or ""),
                                                 str(evento.get("venue") or "")))
                return archivo.stem, claves
    return "", set()


def cargar_candidatos(path: Path) -> list[dict]:
    """candidatos_db.jsonl rows, latest-wins by obra_id (the file may carry
    re-runs; counting repeated rows would inflate evidence)."""
    por_obra: dict[str, dict] = {}
    with open(path, "r", encoding="utf-8") as f:
        for linea in f:
            linea = linea.strip()
            if not linea:
                continue
            try:
                registro = json.loads(linea)
            except json.JSONDecodeError:
                continue
            # JSON valido que no es objeto (fila corrupta/editada) se salta
            # igual que el JSON roto: una fila mala no aborta la corrida.
            if not isinstance(registro, dict):
                continue
            obra_id = registro.get("obra_id")
            if obra_id:
                por_obra[obra_id] = registro
    return list(por_obra.values())


def _acumular(destino: dict, slug: str, nombre: str, registro: dict) -> dict:
    entrada = destino.setdefault(slug, {
        "nombre": nombre,
        "archivos_fuente": set(),
        "instagram_handles": set(),
        "eventos": set(),
    })
    entrada["archivos_fuente"].add(
        "%s [%s]" % (registro.get("ruta_rel", ""), registro.get("obra_id", ""))
    )
    for h in registro.get("handles") or []:
        if h:
            entrada["instagram_handles"].add(h)
    return entrada


def _cerrar(acumulado: dict, minimo: int) -> tuple[dict, dict]:
    """Split accumulated candidates into (enough evidence, too little)."""
    listos, cortos = {}, {}
    for slug, datos in acumulado.items():
        cerrado = {
            "nombre": datos["nombre"],
            "evidencia": len(datos["archivos_fuente"]),
            "archivos_fuente": sorted(datos["archivos_fuente"]),
        }
        # Venue entries carry only name + sources; productora ones also
        # carry handles and events (mineria_rd's consolidado shape).
        if "instagram_handles" in datos:
            cerrado["instagram_handles"] = sorted(datos["instagram_handles"])
            cerrado["eventos"] = sorted(datos["eventos"])
        if cerrado["evidencia"] >= minimo:
            listos[slug] = cerrado
        else:
            cortos[slug] = cerrado
    return listos, cortos


def consolidar_candidatos(
    candidatos: list[dict],
    catalogo_productoras: list[dict] | None = None,
    catalogo_venues: list[dict] | None = None,
    minimo_evidencia: int = extraccion_db.MIN_OBRAS_PROPUESTA,
    repo_root: Path | None = None,
) -> tuple[dict, dict]:
    """Digested candidates -> the dict `mineria_rd.proponer()` expects, plus a
    report of everything that was NOT drafted and why (no silent drops)."""
    if catalogo_productoras is None:
        catalogo_productoras = extraccion_db.cargar_catalogo_productoras()
    if catalogo_venues is None:
        catalogo_venues = extraccion_db.cargar_catalogo_venues()
    if repo_root is None:
        repo_root = REPO_ROOT

    productoras: dict = {}
    venues: dict = {}
    eventos_conocidos: dict = {}
    _eventos_ya_registrados: dict[str, set] = {}
    informe = {
        "filas": len(candidatos),
        "descartes": {
            "fuente_no_rd": 0,
            "identidad_propia": 0,
            "categoria_no_evento": 0,
            "sin_nombres": 0,
            "venue_geografia": 0,
            "identidad_propia_nombre": 0,
        },
        "productoras": {"conocidas": 0, "dudosas": [], "nuevas": 0, "evidencia_corta": []},
        "venues": {"conocidos": 0, "dudosos": [], "nuevos": 0, "evidencia_corta": []},
        "eventos_conocidos": {"propuestos": 0, "ya_registrados": 0, "sin_fecha": 0},
    }

    for registro in candidatos:
        if registro.get("fuente") != "rd":
            informe["descartes"]["fuente_no_rd"] += 1
            continue
        if registro.get("identidad_propia"):
            informe["descartes"]["identidad_propia"] += 1
            continue
        if registro.get("categoria") not in CATEGORIAS_EVENTO:
            informe["descartes"]["categoria_no_evento"] += 1
            continue

        nombre_prod = extraccion_db.valor_limpio(registro.get("productora_cruda"))
        nombre_venue = extraccion_db.valor_limpio(registro.get("venue_crudo"))
        if not nombre_prod and not nombre_venue:
            informe["descartes"]["sin_nombres"] += 1
            continue

        if nombre_prod and extraccion_db.es_identidad_propia(nombre_prod):
            informe["descartes"]["identidad_propia_nombre"] += 1
            nombre_prod = ""
        if nombre_prod:
            canonico, ratio = extraccion_db.mejor_match(nombre_prod, catalogo_productoras)
            clase = extraccion_db.clasificar_ratio(ratio)
            if clase == "match":
                informe["productoras"]["conocidas"] += 1
            elif clase == "dudoso":
                informe["productoras"]["dudosas"].append(
                    "%s ~ %s (%.3f)" % (nombre_prod, canonico, ratio)
                )
            else:
                _acumular(productoras, _clave(nombre_prod), nombre_prod, registro)

            # match o dudoso -- productora YA IDENTIFICADA, no descartar el
            # evento (fecha/venue) que trae ESTE flyer. Antes de esta fila,
            # esto se contaba y se tiraba: un flyer repetido de una
            # productora conocida no sumaba nada a la base.
            if clase in ("match", "dudoso"):
                fecha_cruda = extraccion_db.valor_limpio(registro.get("fecha_cruda"))
                # Chequeo LOCAL, no toca `nombre_venue` (el bloque de venues
                # de mas abajo lo necesita crudo todavia): "Santiago" no es
                # un venue, es la ciudad -- mismo criterio que
                # GEOGRAFIA_NO_VENUE ya aplica para el candidato de venue.
                venue_evento = (
                    "" if nombre_venue and extraccion_db.normalizar_texto(nombre_venue)
                    in GEOGRAFIA_NO_VENUE else nombre_venue
                )
                if not fecha_cruda:
                    informe["eventos_conocidos"]["sin_fecha"] += 1
                else:
                    if canonico not in _eventos_ya_registrados:
                        slug_prod, ya = cargar_eventos_existentes(canonico, repo_root)
                        _eventos_ya_registrados[canonico] = ya
                    else:
                        slug_prod = mineria_rd._slug(extraccion_db.normalizar_texto(canonico))
                    clave_ev = _clave_evento(fecha_cruda, venue_evento)
                    if clave_ev in _eventos_ya_registrados[canonico]:
                        informe["eventos_conocidos"]["ya_registrados"] += 1
                    else:
                        entrada_ev = eventos_conocidos.setdefault(
                            (slug_prod, clave_ev), {
                                "productora_canonica": canonico,
                                "slug_productora": slug_prod,
                                "clase": clase,
                                "match_ratio": ratio,
                                "nombre_evento": nombre_prod,
                                "fecha": fecha_cruda,
                                "venue": nombre_venue,
                                "handles": set(),
                                "archivos_fuente": [],
                            })
                        # Confianza mas alta gana si el mismo evento aparece
                        # en mas de un flyer con distinta lectura (p.ej. la
                        # fuente y su render, cada uno con su propio OCR).
                        if ratio > entrada_ev["match_ratio"]:
                            entrada_ev["match_ratio"] = ratio
                            entrada_ev["clase"] = clase
                        entrada_ev["handles"].update(registro.get("handles") or [])
                        entrada_ev["archivos_fuente"].append(
                            _rutas_locales_rd(registro.get("ruta_rel", "")))

        if nombre_venue and extraccion_db.normalizar_texto(nombre_venue) in GEOGRAFIA_NO_VENUE:
            informe["descartes"]["venue_geografia"] += 1
            nombre_venue = ""
        if nombre_venue and extraccion_db.es_identidad_propia(nombre_venue):
            informe["descartes"]["identidad_propia_nombre"] += 1
            nombre_venue = ""
        if nombre_venue:
            canonico_v, ratio_v = extraccion_db.mejor_match(nombre_venue, catalogo_venues)
            clase_v = extraccion_db.clasificar_ratio(ratio_v)
            if clase_v == "match":
                informe["venues"]["conocidos"] += 1
            elif clase_v == "dudoso":
                informe["venues"]["dudosos"].append(
                    "%s ~ %s (%.3f)" % (nombre_venue, canonico_v, ratio_v)
                )
            else:
                entrada = venues.setdefault(_clave(nombre_venue), {
                    "nombre": nombre_venue,
                    "archivos_fuente": set(),
                })
                entrada["archivos_fuente"].add(
                    "%s [%s]" % (registro.get("ruta_rel", ""), registro.get("obra_id", ""))
                )

    productoras_listas, prod_cortas = _cerrar(productoras, minimo_evidencia)
    venues_listos, ven_cortos = _cerrar(venues, minimo_evidencia)
    informe["productoras"]["nuevas"] = len(productoras_listas)
    informe["productoras"]["evidencia_corta"] = sorted(
        "%s (%d)" % (d["nombre"], d["evidencia"]) for d in prod_cortas.values()
    )
    informe["venues"]["nuevos"] = len(venues_listos)
    informe["venues"]["evidencia_corta"] = sorted(
        "%s (%d)" % (d["nombre"], d["evidencia"]) for d in ven_cortos.values()
    )
    informe["eventos_conocidos"]["propuestos"] = len(eventos_conocidos)

    consolidado = {
        "productoras_nuevas": productoras_listas,
        "venues_nuevos": venues_listos,
        "eventos_conocidos": list(eventos_conocidos.values()),
    }
    return consolidado, informe


def _imprimir_informe(informe: dict) -> None:
    d = informe["descartes"]
    print("filas: %d | descartes: fuente %d, identidad propia %d, "
          "categoria %d, sin nombres %d, venue=geografia %d, "
          "identidad propia por nombre %d"
          % (informe["filas"], d["fuente_no_rd"], d["identidad_propia"],
             d["categoria_no_evento"], d["sin_nombres"], d["venue_geografia"],
             d["identidad_propia_nombre"]))
    for etiqueta, clave_c, clave_n in (
        ("productoras", "conocidas", "nuevas"),
        ("venues", "conocidos", "nuevos"),
    ):
        seccion = informe[etiqueta]
        dudosos = seccion["dudosas" if etiqueta == "productoras" else "dudosos"]
        print("%s: %d ya en catalogo, %d dudosas (NO se proponen), "
              "%d nuevas con evidencia, %d con evidencia corta"
              % (etiqueta, seccion[clave_c], len(dudosos),
                 seccion[clave_n], len(seccion["evidencia_corta"])))
        for linea in dudosos:
            print("  dudoso: %s" % linea)
        for linea in seccion["evidencia_corta"]:
            print("  evidencia corta: %s" % linea)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--candidatos", default=str(CANDIDATOS_DEFAULT),
                        help="candidatos_db.jsonl (default: el espejo en docs/rd/)")
    parser.add_argument("--outdir", default=str(OUTDIR_DEFAULT),
                        help="carpeta de borradores (nunca data/ ni knowledge/)")
    parser.add_argument("--minimo-evidencia", type=int,
                        default=extraccion_db.MIN_OBRAS_PROPUESTA)
    args = parser.parse_args(argv)

    ruta = Path(args.candidatos)
    if not ruta.exists():
        print("no existe: %s" % ruta, file=sys.stderr)
        return 1

    candidatos = cargar_candidatos(ruta)
    consolidado, informe = consolidar_candidatos(
        candidatos, minimo_evidencia=args.minimo_evidencia)
    _imprimir_informe(informe)

    mineria_rd.proponer(consolidado, args.outdir)
    print("borradores en %s: %d productoras, %d venues, %d eventos de "
          "productoras conocidas/dudosas"
          % (args.outdir,
             len(consolidado["productoras_nuevas"]),
             len(consolidado["venues_nuevos"]),
             len(consolidado["eventos_conocidos"])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
