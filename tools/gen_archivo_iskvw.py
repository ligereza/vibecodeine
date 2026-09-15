#!/usr/bin/env python3
"""Las dos fuentes de iskvw, en la forma que lee cualquier piel.

Antes de esto, las obras del artista y el micelio de MAK no se podian mirar
juntos: cada fuente tenia su forma y cada piel escribia su propio lector. Esta
capa las entrega como piezas y vinculos sin que la piel tenga que conocer el
origen.

Aca las dos salen en la misma forma -- piezas y vinculos -- descrita en
`iskvw/ESQUEMA_ARCHIVO.md`. Una piel pide eso y no necesita saber que hay
detras.

Uso:
    py tools/gen_archivo_iskvw.py --fuente obras
    py tools/gen_archivo_iskvw.py --fuente micelio --url http://<caja>:8900/research
    py tools/gen_archivo_iskvw.py --fuente micelio_snapshot
    py tools/gen_archivo_iskvw.py --fuente ensayos
    py tools/gen_archivo_iskvw.py --fuente todo
    py tools/gen_archivo_iskvw.py --fuente todo --incluir-ensayos

`--fuente todo` intenta el micelio EN VIVO y, si no responde (por ejemplo, CI
no alcanza la LAN privada de la caja), cae al snapshot versionado en
`iskvw/datos/micelio.json`. La promoción de ese snapshot se revisa en `main`;
las puntas `source/*` son preservación histórica, no runtime.

Essays are explicit opt-in. Their iconographic annex is not junk: it is a
research guarantee lane. If MAK claims to understand a topic, the concepts and
SVG annex test whether the reading can become a representative visual system
(post proposal, laser/plotter seed, animated SVG, README-like ASCII digestion).
The 2026-08-05 correction is only the publication boundary: `--fuente todo`
previously mixed `informe` and `concepto` pieces into iskvw.cl by default, so
curation material appeared with report shape and reports appeared as archive
pieces. The default also excludes historical `informe`, `concepto` and
`pieza_grafica` nodes from the micelio snapshot; the source files remain intact.
Use `--fuente ensayos` or `--incluir-ensayos` when that research view is
deliberately requested.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import urllib.request
from datetime import datetime
from itertools import combinations
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "cultura" / "mak_plataforma"))
import contrato_archivo  # noqa: E402

OBRAS = RAIZ / "iskvw" / "datos" / "obras.json"
CAMPO = RAIZ / "iskvw" / "datos" / "campo.json"
SALIDA = RAIZ / "iskvw" / "datos" / "archivo.json"
ENSAYOS = RAIZ / "docs" / "cultura" / "ensayos"
ANIMADAS = RAIZ / "iskvw" / "datos" / "animadas.json"
LASER = RAIZ / "iskvw" / "datos" / "laser.json"
CURADURIA = RAIZ / "iskvw" / "datos" / "curaduria.json"
# Snapshot committed from the MAK box: the Pages runner cannot assume access to
# the private LAN, so the checked-in snapshot is the deterministic fallback.
# It uses the same reproducible-snapshot principle as campo.json positions and
# carries the micelio's measured links without opening a service.
MICELIO_SNAPSHOT = RAIZ / "iskvw" / "datos" / "micelio.json"
PORTAFOLIO = RAIZ / "iskvw" / "datos" / "portafolio.json"

# Por defecto el micelio se pide a la variable de entorno, no a una IP escrita
# en el repo: este repositorio es publico.
MICELIO_URL = os.environ.get(
    "FLUJO_MAK_RESEARCH_URL", "http://127.0.0.1:8900/research"
)

# Dos obras con etiquetas en comun quedan unidas. Debajo de esto el vinculo es
# ruido: una sola etiqueta generica compartida no dice que dos obras se
# parezcan.
MIN_ETIQUETAS = 1
UMBRAL_MICELIO = 0.55


# La formacion de ids y la conversion micelio -> contrato viven en UN solo
# lugar, compartido con el hub de la caja (2026-07-29): duplicarlas aqui es
# como las claves dejaron de empalmar una vez (1004 piezas, 0 con posicion).
_id = contrato_archivo._id
_id_pieza = contrato_archivo._id_pieza


def _fecha(obra: dict) -> str | None:
    """AAAA si hay año. Ausente si no: no se inventa, y no vale cero."""
    anio = obra.get("year")
    if isinstance(anio, int) and 1900 < anio < 2200:
        return str(anio)
    creado = str(obra.get("createdAt") or "")
    return creado[:10] if re.match(r"^\d{4}-\d{2}-\d{2}", creado) else None


def desde_obras(ruta: Path = OBRAS) -> dict:
    crudo = json.loads(ruta.read_text(encoding="utf-8"))
    obras = crudo if isinstance(crudo, list) else crudo.get("obras", [])

    piezas, por_etiqueta = [], {}
    for o in obras:
        pid = _id(o.get("id") or o.get("title"))
        etiquetas = [str(t) for t in (o.get("tags") or []) if t]
        medio = {"tipo": "ninguno"}
        if o.get("video"):
            medio = {"tipo": "video", "src": o["video"], "poster": o.get("poster")}
        elif o.get("image") or o.get("src"):
            medio = {"tipo": "imagen", "src": o.get("image") or o.get("src")}

        piezas.append({
            "id": pid,
            "titulo": str(o.get("title") or pid),
            "clase": "obra",
            "fecha": _fecha(o),
            "resumen": (o.get("description") or "").strip() or None,
            "etiquetas": etiquetas,
            # Una obra con galeria tiene mas materia que una suelta.
            "peso": 1 + len(o.get("gallery") or []),
            "medio": medio,
            # `placeholder` significa anunciada y sin archivo detras. Mostrarla
            # como terminada es la mentira que el contrato prohibe.
            "estado": "anunciada" if o.get("placeholder") else "publicada",
            "extra": {k: v for k, v in (
                ("categoria", o.get("category")),
                ("tecnica", o.get("technique")),
                ("descripcion_larga", o.get("descriptionLong")),
            ) if v},
        })
        for t in etiquetas:
            por_etiqueta.setdefault(t.lower(), []).append(pid)

    # Vinculo por etiqueta compartida. Se declara `clase: etiqueta` y NO
    # `semantico`: nadie midio que se parezcan, comparten una palabra.
    compartidas: dict[tuple[str, str], int] = {}
    for ids in por_etiqueta.values():
        for a, b in combinations(sorted(set(ids)), 2):
            compartidas[(a, b)] = compartidas.get((a, b), 0) + 1

    total_max = max(compartidas.values(), default=1)
    vinculos = [
        {"de": a, "a": b, "peso": round(n / total_max, 3), "clase": "etiqueta"}
        for (a, b), n in sorted(compartidas.items()) if n >= MIN_ETIQUETAS
    ]
    return {"piezas": piezas, "vinculos": vinculos}


def desde_micelio(url: str = MICELIO_URL, umbral: float = UMBRAL_MICELIO) -> dict:
    pedido = f"{url.rstrip('/')}/api/memoria/grafo?umbral={umbral}"
    with urllib.request.urlopen(pedido, timeout=90) as r:
        g = json.loads(r.read().decode("utf-8", "replace"))

    # La conversion (titulo vacio para obras, percibido en extra, vinculos
    # semanticos filtrados a ids conocidos) vive en contrato_archivo.convertir,
    # compartida con GET /api/archivo del hub de la caja.
    return contrato_archivo.convertir(g)


def desde_micelio_snapshot(ruta: Path = MICELIO_SNAPSHOT) -> dict:
    """The micelio's measured graph, already converted and committed by the
    box (cultura/mak_plataforma/entregar_micelio.py) -- because CI cannot
    reach the box directly, only the box can put this data here.

    A snapshot, not live: it only advances when the box opens a new PR, the
    same pattern campo.json already uses for obra positions. Same rule as
    every other optional fuente here: an absent file is an absent source,
    never an invented empty result.
    """
    if not ruta.is_file():
        return {"piezas": [], "vinculos": []}
    d = json.loads(ruta.read_text(encoding="utf-8"))
    return {"piezas": d.get("piezas") or [], "vinculos": d.get("vinculos") or []}


def desde_ensayos(raiz: Path = ENSAYOS) -> dict:
    """Los ensayos curados del repo, con su anexo iconografico.

    Es el tramo que faltaba para que lo que MAK produce le sirva al portafolio:
    hasta ahora un ensayo terminaba en una carpeta que ninguna piel miraba. La
    conversion vive en `contrato_archivo.desde_ensayo` porque un ensayo existe
    en los DOS lados (aca los curados, en la caja los que escribe
    `research.py --formato ensayo`).

    Nada se inventa: el titulo sale del H1 del documento y los conceptos del
    manifiesto. Un icono declarado que no esta en disco NO entra -- una pieza
    que afirma un archivo ausente es justo la mentira que el esquema prohibe.
    """
    if not raiz.is_dir():
        return {"piezas": [], "vinculos": []}
    partes = []
    for carpeta in sorted(p for p in raiz.iterdir() if p.is_dir()):
        doc = carpeta / "ensayo.md"
        manifiesto = carpeta / "iconos.json"
        if not doc.is_file():
            continue
        texto = doc.read_text(encoding="utf-8", errors="replace")
        h1 = re.search(r"^#\s+(.+)$", texto, re.MULTILINE)
        conceptos = []
        if manifiesto.is_file():
            try:
                conceptos = json.loads(manifiesto.read_text(encoding="utf-8"))
            except ValueError:
                conceptos = []
        for c in conceptos:
            svg = carpeta / "iconos" / str(c.get("archivo") or "")
            if c.get("archivo") and svg.is_file():
                c["archivo_src"] = "%s/%s" % (
                    carpeta.relative_to(RAIZ).as_posix(), "iconos/" + c["archivo"])
                # Se LEE del archivo, no se afirma: tiene keyframes o no los
                # tiene. Que se mueva de forma perceptible se mide contando
                # cuadros distintos, que es otra pregunta y otro comando.
                c["declara_animacion"] = "@keyframes" in svg.read_text(
                    encoding="utf-8", errors="replace")
        partes.append(contrato_archivo.desde_ensayo({
            "slug": carpeta.name,
            "titulo": (h1.group(1).strip() if h1 else carpeta.name),
            "ruta": doc.relative_to(RAIZ).as_posix(),
            "conceptos": conceptos,
        }))
    if not partes:
        return {"piezas": [], "vinculos": []}
    return unir(*partes)


def del_campo(ruta: Path = CAMPO) -> tuple[dict, float | None]:
    """Lo que el campo sabe de cada obra, por id, para pegarlo al contrato.

    Antes de esto el archivo salia partido en dos y la costura era justamente
    esto: `archivo.json` traia las relaciones sin posicion y `campo.json` la
    posicion sin las relaciones, asi que una piel que queria las dos cosas
    tenia que conocer DOS archivos y unirlos ella. Eso es exactamente lo que el
    contrato existe para evitar.

    No se fusionan los generadores: proyectar necesita los 768 vectores del
    micelio y el contrato no los tiene ni los quiere. Lo que viaja es el
    resultado, que son dos numeros por obra.

    La metrica viaja aparte, en `meta`, porque describe la PROYECCION entera y
    no una pieza. Si no esta el archivo, no se inventa nada: el contrato sale
    sin posiciones y una piel que no las encuentra dibuja como sabe.
    """
    try:
        d = json.loads(ruta.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}, None
    reg = {}
    for p in d.get("piezas") or []:
        pid = _id(p.get("id"))
        if pid:
            reg[pid] = p
    return reg, (d.get("meta") or {}).get("vecindad_conservada")


def desde_animadas(manifiesto: Path = ANIMADAS) -> dict:
    """Las piezas animadas que el motor semantico derivo de las obras curadas.

    Una por obra, determinista desde el id (tools/gen_animadas_obras.py). La
    conversion vive en `contrato_archivo.desde_animadas` por la regla de
    siempre: la pieza existe en los dos lados y dos conversiones divergen.
    Sin manifiesto se sigue sin el: las animadas enriquecen, no condicionan.
    """
    if not manifiesto.is_file():
        return {"piezas": [], "vinculos": []}
    datos = json.loads(manifiesto.read_text(encoding="utf-8"))
    return contrato_archivo.desde_animadas(datos)


def desde_campo_curado(ruta: Path = CAMPO) -> dict:
    """Las obras curadas del campo medido como piezas del contrato.

    La correccion de fondo del 2026-07-30: sin micelio alcanzable (CI), el
    archivo salia SIN las obras del artista -- solo tools, ensayos e iconos.
    El campo ya carga lo percibido bajo el filtro del usuario; ahora ademas
    de posiciones aporta las piezas. La conversion vive en el contrato.
    """
    if not ruta.is_file():
        return {"piezas": [], "vinculos": []}
    datos = json.loads(ruta.read_text(encoding="utf-8"))
    return contrato_archivo.desde_campo(datos)


def desde_laser_manifiesto(campo_ruta: Path = CAMPO,
                           ruta: Path = LASER) -> dict:
    """Las piezas laser/plotter del manifiesto, unidas al campo por media id.

    Genera `flujo laser lote`; la conversion vive en el contrato
    (`desde_laser`). Sin manifiesto se sigue sin el.
    """
    if not ruta.is_file():
        return {"piezas": [], "vinculos": []}
    manif = json.loads(ruta.read_text(encoding="utf-8"))
    campo = (json.loads(campo_ruta.read_text(encoding="utf-8"))
             if campo_ruta.is_file() else {})
    return contrato_archivo.desde_laser(manif, campo)


def unir(*partes: dict) -> dict:
    """Junta fuentes sin duplicar por id y por media ID explícito.

    Una obra percibida por MAK y la misma obra cargada a mano son UNA pieza:
    conserva la observación de campo y anexa la evidencia semántica, sin
    tratarla como autoría ni como una segunda obra.
    """
    piezas: dict[str, dict] = {}
    vinculos: dict[tuple[str, str], dict] = {}
    for parte in partes:
        for p in parte["piezas"]:
            previa = piezas.get(p["id"])
            if previa is None or _riqueza(p) > _riqueza(previa):
                piezas[p["id"]] = p if previa is None else {**previa, **{
                    k: v for k, v in p.items() if v not in (None, "", [], {})}}
        for v in parte["vinculos"]:
            clave = tuple(sorted((v["de"], v["a"])))
            # Un vinculo medido gana sobre uno derivado de etiquetas.
            if clave not in vinculos or (v["clase"] == "semantico"
                                         and vinculos[clave]["clase"] != "semantico"):
                vinculos[clave] = v
    return contrato_archivo.deduplicate_media_sources({
        "piezas": list(piezas.values()),
        "vinculos": list(vinculos.values()),
    })


def _riqueza(p: dict) -> int:
    return sum(1 for k in ("fecha", "resumen", "medio", "extra")
               if p.get(k) not in (None, "", [], {}, {"tipo": "ninguno"}))


def _orden_portafolio(piezas: list[dict]) -> list[dict]:
    """Give every source piece one deterministic place in the portfolio.

    Measured positions lead when they exist. The rest are not held back for a
    decision and are not discarded: their stable id gives them a reproducible
    place until a measurement arrives. This is the visual portfolio order, not
    a claim about authorship or semantic similarity.
    """
    def clave(p: dict) -> tuple:
        pos = p.get("posicion") or {}
        x, y = pos.get("x"), pos.get("y")
        if isinstance(x, (int, float)) and not isinstance(x, bool) \
                and isinstance(y, (int, float)) and not isinstance(y, bool):
            return (0, y, x, str(p.get("id") or ""))
        return (1, str(p.get("id") or ""))

    return sorted(piezas, key=clave)


def construir_portafolio(archive_data: dict, *, source_path: str,
                         source_bytes: bytes) -> dict:
    """Build the single visual-portafolio manifest consumed by every skin.

    The archive remains the content source. This manifest only fixes its
    complete selection, order, and available views, so missing metadata or
    missing human decisions never turns into an omitted work.
    """
    piezas = list(archive_data.get("piezas") or [])
    ordenadas = _orden_portafolio(piezas)
    ids = [str(p["id"]) for p in ordenadas if p.get("id")]
    posicionadas = sum(1 for p in ordenadas if isinstance(p.get("posicion"), dict)
                       and isinstance(p["posicion"].get("x"), (int, float))
                       and isinstance(p["posicion"].get("y"), (int, float)))
    return {
        "schema": "iskvw-portfolio-manifest-v1",
        "version": 1,
        "source": {
            "path": source_path,
            "sha256": hashlib.sha256(source_bytes).hexdigest(),
            "piece_count": len(piezas),
            "link_count": len(archive_data.get("vinculos") or []),
        },
        # The artist is the corpus context for this MAK portfolio. It is not
        # an inferred authorship assertion; the archive's own `clase` and
        # fields remain the authority for what each piece says.
        "artist": {"id": "mak", "basis": "operator_context",
                    "authorship_claimed": False},
        "default_skin": "campo",
        "skins": [
            {"id": "campo", "path": "piel/campo/", "label": "campo",
             "scope": "portfolio"},
            {"id": "terminal", "path": "piel/terminal/", "label": "terminal",
             "scope": "portfolio"},
        ],
        "sections": [{"id": "portfolio", "title": "Portafolio",
                       "item_ids": ids}],
        "order": ids,
        "ordering": {
            "algorithm": "measured_position_yx_then_stable_id",
            "positioned_count": posicionadas,
            "unpositioned_count": len(piezas) - posicionadas,
        },
        "selection": {"mode": "all_source_pieces", "omitted_count": 0},
        "control": {
            "publication": False,
            "submission": False,
            "training": False,
            "source_mutation": False,
            "authorship_claimed": False,
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--fuente",
                    choices=("obras", "campo", "micelio", "micelio_snapshot",
                             "ensayos", "animadas", "laser", "todo"),
                    default="obras")
    ap.add_argument("--url", default=MICELIO_URL)
    ap.add_argument("--umbral", type=float, default=UMBRAL_MICELIO)
    ap.add_argument("--salida", type=Path, default=SALIDA)
    ap.add_argument("--posiciones", type=Path, default=CAMPO,
                    help="campo.json con las posiciones medidas; si no esta, "
                         "el contrato sale sin posiciones")
    ap.add_argument("--incluir-ensayos", action="store_true",
                    help="include docs/cultura/ensayos in --fuente todo; "
                         "off by default so the public iskvw archive does not "
                         "mix research reports with artwork")
    args = ap.parse_args()

    partes = []
    if args.fuente in ("obras", "todo"):
        partes.append(desde_obras())
    if args.fuente in ("campo", "todo"):
        partes.append(desde_campo_curado(args.posiciones))
    if args.fuente in ("micelio", "todo"):
        try:
            partes.append(desde_micelio(args.url, args.umbral))
        except Exception as e:  # noqa: BLE001
            # Sin micelio se escribe lo que SI hay y se dice. Abortar dejaria a
            # quien genera sin archivo por una maquina apagada.
            print(f"aviso: no se pudo leer el micelio ({e}). Sigo sin el.",
                  file=sys.stderr)
            if args.fuente == "micelio":
                return 1
            # CI no puede asumir acceso a la caja (LAN privada, workflow en
            # ubuntu-latest); no es una falla del snapshot, es el motivo por
            # el que existe. Con él, "todo" lleva lo último promovido desde
            # MAK en vez de degradar silenciosamente a una sola fuente.
            snap = desde_micelio_snapshot()
            if snap["piezas"] or snap["vinculos"]:
                print(f"aviso: uso el snapshot versionado en su lugar "
                      f"({len(snap['piezas'])} piezas, "
                      f"{len(snap['vinculos'])} vinculos, "
                      f"{MICELIO_SNAPSHOT.relative_to(RAIZ)}).",
                      file=sys.stderr)
                partes.append(snap)
    if args.fuente == "micelio_snapshot":
        partes.append(desde_micelio_snapshot())
    if args.fuente == "ensayos" or (args.fuente == "todo"
                                    and args.incluir_ensayos):
        partes.append(desde_ensayos())
    if args.fuente in ("animadas", "todo"):
        partes.append(desde_animadas())
    if args.fuente in ("laser", "todo"):
        partes.append(desde_laser_manifiesto(args.posiciones))

    datos = unir(*partes)
    if args.fuente == "todo" and not args.incluir_ensayos:
        datos = _sustrato_publico(datos)

    # La posicion entra como campo OPCIONAL: la pieza que la tiene la lleva y la
    # que no, no la lleva vacia. Un campo que no conoces es un campo que
    # ignoras, y un cero fingido seria una posicion afirmada sin medir.
    campo, vecindad = del_campo(args.posiciones)
    con_pos = con_medio = 0
    for p in datos["piezas"]:
        c = campo.get(p["id"])
        if not c:
            continue
        if c.get("x") is not None and c.get("y") is not None:
            p["posicion"] = {"x": c["x"], "y": c["y"]}
            con_pos += 1
        # Lo descriptivo que el micelio no tiene y una piel necesita para
        # dibujar: color, tipo y estilo. Va a `extra` porque no es parte del
        # contrato minimo -- una piel que no lo conoce lo ignora.
        for origen, destino in (("colores", "colores"), ("tipo", "tipo"),
                                ("estilo", "estilo")):
            if c.get(origen):
                p["extra"][destino] = c[origen]
        # Y el defecto de fondo: el micelio indexa TEXTO, asi que marcaba toda
        # obra del artista como `medio: texto`. Una obra es una imagen, y el
        # campo trae su ruta. Un contrato que declara mal el medio hace que una
        # piel decida mal como mostrarla.
        if c.get("archivo") and p.get("medio", {}).get("tipo") == "texto":
            p["medio"] = {"tipo": "imagen", "src": c["archivo"]}
            con_medio += 1

    # La mano del artista, al final y sobre todo: titulo firmado, mostrar,
    # abstraccion, svg firmado y regimen (contrato_archivo.aplicar_curaduria).
    regimen = None
    if CURADURIA.is_file():
        cur = json.loads(CURADURIA.read_text(encoding="utf-8"))
        datos = contrato_archivo.aplicar_curaduria(datos, cur)
        regimen = cur.get("regimen")

    salida = {
        "version": 1,
        "fuente": args.fuente,
        "generado": datetime.now().isoformat(timespec="seconds"),
        "piezas": datos["piezas"],
        "vinculos": datos["vinculos"],
        "meta": {
            "regimen": regimen,
            "piezas": len(datos["piezas"]),
            "vinculos": len(datos["vinculos"]),
            "por_clase": _contar(datos["piezas"], "clase"),
            "vinculos_por_clase": _contar(datos["vinculos"], "clase"),
            "con_posicion": con_pos,
            "medio_corregido_a_imagen": con_medio,
            "por_medio": _contar([p.get("medio") or {} for p in datos["piezas"]],
                                 "tipo"),
            # Describe la PROYECCION entera, no una pieza, asi que va aca. Es la
            # fraccion de vecinos reales que siguen siendo vecinos en el plano:
            # si baja, lo que el campo afirma se debilita y hay que decirlo.
            "vecindad_conservada": vecindad,
        },
    }
    args.salida.parent.mkdir(parents=True, exist_ok=True)
    archive_bytes = json.dumps(salida, ensure_ascii=False, indent=1).encode("utf-8")
    args.salida.write_bytes(archive_bytes)
    portfolio_path = args.salida.with_name(PORTAFOLIO.name)
    try:
        source_manifest = args.salida.relative_to(RAIZ).as_posix()
    except ValueError:
        source_manifest = args.salida.name
    portfolio_path.write_text(
        json.dumps(construir_portafolio(
            salida, source_path=source_manifest, source_bytes=archive_bytes),
                   ensure_ascii=False, indent=1),
        encoding="utf-8",
    )
    # `relative_to` levanta ValueError con una salida fuera del repo, asi que
    # --salida a cualquier ruta absoluta de afuera reventaba DESPUES de haber
    # escrito bien el archivo. El nombre corto es una comodidad, no un requisito.
    try:
        donde = args.salida.relative_to(RAIZ)
    except ValueError:
        donde = args.salida
    print(f"{donde}: {len(datos['piezas'])} piezas, "
          f"{len(datos['vinculos'])} vinculos "
          f"({args.salida.stat().st_size / 1024:.1f} KB)")
    print(f"  manifiesto: {portfolio_path.name} ({len(salida['piezas'])} ids)")
    print("  por clase:", salida["meta"]["por_clase"])
    return 0


def _sustrato_publico(datos: dict) -> dict:
    """Keep the generator aligned with the shared public contract."""
    return contrato_archivo.sustrato_publico(datos)


def _contar(filas: list[dict], campo: str) -> dict:
    out: dict[str, int] = {}
    for f in filas:
        out[str(f.get(campo) or "?")] = out.get(str(f.get(campo) or "?"), 0) + 1
    return dict(sorted(out.items()))


if __name__ == "__main__":
    raise SystemExit(main())
