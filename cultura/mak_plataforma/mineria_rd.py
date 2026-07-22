#!/usr/bin/env python3
"""
mineria_rd.py -- pipeline de mineria sobre la carpeta ~/RD de MAK.

Recorre flyers/PDFs/archivos .ai de RD (57GB, ~1731 archivos), les hace OCR
(pdftotext / tesseract) y, para imagenes con pinta de flyer, los pasa por
vision (ollama gemma3:4b) para extraer productora/evento/venue/fecha/handles
de instagram. Consolida los candidatos y escribe BORRADORES en el schema
real de data/productoras/*.json y knowledge/venues/*.yaml.

Este script NUNCA escribe en data/ ni en knowledge/. Los borradores salen a
propuestas_mineria/ y entran al repo via PR revisado por un humano.

Ambiente objetivo: Linux MAK (tesseract 5.3.0+spa, pdftotext/poppler, ollama
gemma3:4b en localhost:11434). stdlib puro, sin dependencias externas.
Codigo fuente ASCII-only (evita sorpresas de locale/encoding en MAK); los
DATOS que se leen/escriben (nombres reales con acentos, etc.) se manejan
como utf-8 sin problema.
"""

import argparse
import base64
import json
import os
import re
import subprocess
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

# cultura/mak_plataforma/mineria_rd.py -> parents[2] = raiz del repo
REPO_ROOT = Path(__file__).resolve().parents[2]

EXT_IMAGEN = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tif", ".tiff", ".webp"}
EXT_PDF = {".pdf"}
EXT_AI = {".ai"}

LIMITE_TAMANO_BYTES = 30 * 1024 * 1024  # 30MB, archivos mas grandes se saltan
DIR_EXCLUIDO = "_archive"

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "gemma3:4b"

PROMPT_VISION = (
    "Analiza este flyer de evento y responde SOLO con un objeto JSON, sin "
    "texto adicional antes ni despues. Formato exacto de las claves: "
    '{"productora": "", "evento": "", "venue": "", "fecha": "", '
    '"instagram_handles": []}. Si un dato no aparece en la imagen, deja el '
    "valor como cadena vacia o lista vacia. No inventes datos que no veas."
)

PALABRAS_EVENTO = (
    "evento",
    "fiesta",
    "festival",
    "club",
    "dj",
    "line up",
    "lineup",
    "entradas",
    "preventa",
    "puerta",
    "warm up",
    "afterparty",
    "after party",
)
RE_FECHA = re.compile(r"\b\d{1,2}[/\-.]\d{1,2}(?:[/\-.]\d{2,4})?\b")
RE_HORA = re.compile(r"\b\d{1,2}[:.]\d{2}\s*(?:hrs?|am|pm)?\b", re.IGNORECASE)
RE_ARROBA = re.compile(r"@[a-zA-Z0-9_.]{2,}")


# ---------------------------------------------------------------------------
# Paso 1: barrido del arbol de archivos
# ---------------------------------------------------------------------------

def _clasificar_ext(path: Path) -> str:
    ext = path.suffix.lower()
    if ext in EXT_IMAGEN:
        return "imagen"
    if ext in EXT_PDF:
        return "pdf"
    if ext in EXT_AI:
        return "ai"
    return "otro"


def barrer(raiz: str = "~/RD") -> list[dict]:
    """
    Recorre `raiz` y devuelve un listado de archivos clasificados.

    Cada entrada: {"path": str, "tipo": "imagen"|"pdf"|"ai"|"otro", "tamano": int}.
    Se saltan archivos mayores a LIMITE_TAMANO_BYTES y cualquier directorio
    cuyo nombre contenga DIR_EXCLUIDO (case-insensitive).
    """
    raiz_path = Path(raiz).expanduser()
    resultado: list[dict] = []
    if not raiz_path.exists():
        return resultado

    for dirpath, dirnames, filenames in os.walk(raiz_path):
        dirnames[:] = [d for d in dirnames if DIR_EXCLUIDO not in d.lower()]
        for nombre in filenames:
            p = Path(dirpath) / nombre
            try:
                tamano = p.stat().st_size
            except OSError:
                continue
            if tamano > LIMITE_TAMANO_BYTES:
                continue
            resultado.append({
                "path": str(p),
                "tipo": _clasificar_ext(p),
                "tamano": tamano,
            })
    return resultado


# ---------------------------------------------------------------------------
# Paso 2: OCR
# ---------------------------------------------------------------------------

def ocr_pdf(path: str) -> str:
    """
    Extrae texto de un PDF con `pdftotext -layout`. Si el resultado viene
    vacio (PDF escaneado sin capa de texto), intenta tesseract directamente
    sobre el archivo como fallback best-effort.

    Limitacion conocida: tesseract no rasteriza PDFs vectoriales por si
    solo (no hay pdftoppm confirmado en el ambiente MAK objetivo); este
    fallback solo rinde en builds de tesseract con soporte PDF/leptonica
    habilitado. Si falla, se devuelve cadena vacia en vez de fabricar texto.
    """
    try:
        proc = subprocess.run(
            ["pdftotext", "-layout", str(path), "-"],
            capture_output=True, text=True, timeout=60,
        )
        texto = (proc.stdout or "").strip()
    except (OSError, subprocess.SubprocessError):
        texto = ""

    if texto:
        return texto

    try:
        proc2 = subprocess.run(
            ["tesseract", str(path), "stdout", "-l", "spa"],
            capture_output=True, text=True, timeout=120,
        )
        return (proc2.stdout or "").strip()
    except (OSError, subprocess.SubprocessError):
        return ""


def ocr_imagen(path: str) -> str:
    """Extrae texto de una imagen con tesseract -l spa."""
    try:
        proc = subprocess.run(
            ["tesseract", str(path), "stdout", "-l", "spa"],
            capture_output=True, text=True, timeout=120,
        )
        return (proc.stdout or "").strip()
    except (OSError, subprocess.SubprocessError):
        return ""


def parece_flyer(texto_ocr: str) -> bool:
    """Heuristica barata: hay fecha, hora, @handle o palabra de evento."""
    if not texto_ocr:
        return False
    if RE_ARROBA.search(texto_ocr):
        return True
    if RE_FECHA.search(texto_ocr) or RE_HORA.search(texto_ocr):
        return True
    texto_bajo = texto_ocr.lower()
    return any(palabra in texto_bajo for palabra in PALABRAS_EVENTO)


# ---------------------------------------------------------------------------
# Paso 3: vision (ollama gemma3:4b)
# ---------------------------------------------------------------------------

def _parsear_json_tolerante(texto: str) -> dict:
    """Busca el primer '{' y el ultimo '}' y parsea eso como JSON."""
    inicio = texto.find("{")
    fin = texto.rfind("}")
    if inicio == -1 or fin == -1 or fin < inicio:
        return {"error": "sin_json_en_respuesta", "raw": texto[:500]}

    fragmento = texto[inicio:fin + 1]
    try:
        datos = json.loads(fragmento)
    except json.JSONDecodeError as exc:
        return {"error": "json_invalido: %s" % exc, "raw": fragmento[:500]}

    if not isinstance(datos, dict):
        return {"error": "json_no_es_objeto", "raw": fragmento[:500]}

    datos.setdefault("productora", "")
    datos.setdefault("evento", "")
    datos.setdefault("venue", "")
    datos.setdefault("fecha", "")
    datos.setdefault("instagram_handles", [])
    return datos


def vision_flyer(path: str, timeout: int = 300) -> dict:
    """
    Manda la imagen a ollama (gemma3:4b, /api/generate) y devuelve el JSON
    extraido de forma tolerante. En error de lectura/red/parseo devuelve un
    dict con clave "error" en vez de lanzar excepcion (el llamador decide
    que hacer con un fallo puntual sin frenar el resto de la mineria).
    """
    try:
        with open(path, "rb") as f:
            datos_binarios = f.read()
    except OSError as exc:
        return {"error": "no_se_pudo_leer_archivo: %s" % exc, "raw": ""}

    imagen_b64 = base64.b64encode(datos_binarios).decode("ascii")
    payload = json.dumps({
        "model": OLLAMA_MODEL,
        "prompt": PROMPT_VISION,
        "images": [imagen_b64],
        "stream": False,
    }).encode("utf-8")

    req = urllib.request.Request(
        OLLAMA_URL, data=payload,
        headers={"Content-Type": "application/json"}, method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            cuerpo = resp.read().decode("utf-8")
    except (urllib.error.URLError, OSError, TimeoutError) as exc:
        return {"error": "ollama_no_disponible: %s" % exc, "raw": ""}

    try:
        sobre = json.loads(cuerpo)
    except json.JSONDecodeError:
        return {"error": "respuesta_no_json", "raw": cuerpo[:500]}

    texto_modelo = sobre.get("response", "") if isinstance(sobre, dict) else ""
    return _parsear_json_tolerante(texto_modelo)


# ---------------------------------------------------------------------------
# Paso 4: minado resumible
# ---------------------------------------------------------------------------

SOLO_TIPO_MAP = {"imagenes": "imagen", "pdfs": "pdf"}


def _cargar_estado(estado_path: str) -> dict:
    p = Path(estado_path)
    if not p.exists():
        return {"procesados": []}
    try:
        with open(p, "r", encoding="utf-8") as f:
            datos = json.load(f)
    except (OSError, json.JSONDecodeError):
        return {"procesados": []}
    if not isinstance(datos, dict) or "procesados" not in datos:
        return {"procesados": []}
    return datos


def _guardar_estado(estado_path: str, estado: dict) -> None:
    tmp = str(estado_path) + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(estado, f, ensure_ascii=True, indent=2)
    os.replace(tmp, estado_path)


def minar(
    raiz: str,
    limite: int | None = None,
    solo_tipo: str | None = None,
    estado_path: str = "mineria_estado.json",
    jsonl_path: str = "mineria_candidatos.jsonl",
) -> None:
    """
    Recorre `raiz`, hace OCR (siempre) y vision (solo imagenes con pinta de
    flyer) sobre los archivos aun no procesados, y va guardando progreso en
    `estado_path` + resultados en `jsonl_path` (append) para que una corrida
    interrumpida se pueda retomar sin repetir trabajo.

    Archivos tipo "ai" y "otro" quedan registrados en el barrido pero sin
    OCR: el schema solo definio ocr_pdf/ocr_imagen, no hay lector confiable
    de .ai como texto sin abrir Illustrator.
    """
    archivos = barrer(raiz)

    tipo_filtro = SOLO_TIPO_MAP.get(solo_tipo) if solo_tipo else None
    if tipo_filtro:
        archivos = [a for a in archivos if a["tipo"] == tipo_filtro]

    estado = _cargar_estado(estado_path)
    ya_procesados = set(estado.get("procesados", []))

    pendientes = [a for a in archivos if a["path"] not in ya_procesados]
    if limite is not None:
        pendientes = pendientes[:limite]

    for item in pendientes:
        path = item["path"]
        tipo = item["tipo"]
        texto_ocr = ""
        vision = None

        if tipo == "pdf":
            texto_ocr = ocr_pdf(path)
        elif tipo == "imagen":
            texto_ocr = ocr_imagen(path)

        if tipo == "imagen" and parece_flyer(texto_ocr):
            vision = vision_flyer(path)

        registro = {
            "path": path,
            "tipo": tipo,
            "ocr_texto": texto_ocr,
            "vision": vision,
            "procesado_en": datetime.now(timezone.utc).isoformat(),
        }

        with open(jsonl_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(registro, ensure_ascii=True) + "\n")

        ya_procesados.add(path)
        estado["procesados"] = sorted(ya_procesados)
        _guardar_estado(estado_path, estado)


# ---------------------------------------------------------------------------
# Paso 5: consolidacion
# ---------------------------------------------------------------------------

def _normalizar(nombre: str) -> str:
    return re.sub(r"\s+", " ", nombre.strip().lower())


def _slug(nombre: str) -> str:
    s = _normalizar(nombre)
    s = re.sub(r"[^a-z0-9]+", "_", s).strip("_")
    return s or "sin_nombre"


def _cargar_productoras_conocidas(repo_root: Path) -> set:
    conocidas = set()
    dir_productoras = repo_root / "data" / "productoras"
    if not dir_productoras.is_dir():
        return conocidas
    for p in dir_productoras.glob("*.json"):
        try:
            with open(p, "r", encoding="utf-8") as f:
                datos = json.load(f)
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(datos, dict):
            continue
        nombres = [datos.get("name", "")] + list(datos.get("aliases", []) or [])
        for n in nombres:
            if n:
                conocidas.add(_normalizar(n))
    return conocidas


def _leer_yaml_campos_simples(path: Path) -> dict:
    """
    Parser minimo de YAML: solo lee pares "clave: valor" de primer nivel
    (sin indentacion), ignora listas/dicts anidados. Suficiente para leer
    id/name de knowledge/venues/*.yaml, no pretende ser un parser general.
    """
    campos = {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            for linea in f:
                if not linea.strip() or linea.lstrip().startswith("#"):
                    continue
                if linea[0].isspace():
                    continue
                if ":" not in linea:
                    continue
                clave, _, valor = linea.partition(":")
                campos[clave.strip()] = valor.strip().strip('"').strip("'")
    except OSError:
        pass
    return campos


def _cargar_venues_conocidos(repo_root: Path) -> set:
    conocidos = set()
    dir_venues = repo_root / "knowledge" / "venues"
    if not dir_venues.is_dir():
        return conocidos
    for p in dir_venues.glob("*.yaml"):
        campos = _leer_yaml_campos_simples(p)
        for clave in ("id", "name"):
            if campos.get(clave):
                conocidos.add(_normalizar(campos[clave]))
    return conocidos


def consolidar(jsonl_path: str, repo_root: Path | None = None) -> dict:
    """
    Agrupa los candidatos del jsonl de `minar()` en productoras y venues
    NUEVOS (que no matchean, por nombre normalizado o alias, contra
    data/productoras/*.json ni knowledge/venues/*.yaml).

    Devuelve {"productoras_nuevas": {slug: {...}}, "venues_nuevos": {slug: {...}}}
    con conteo de evidencia (archivos distintos) y lista de archivos fuente.
    """
    root = repo_root if repo_root is not None else REPO_ROOT
    productoras_conocidas = _cargar_productoras_conocidas(root)
    venues_conocidos = _cargar_venues_conocidos(root)

    productoras: dict = {}
    venues: dict = {}

    p = Path(jsonl_path)
    if not p.exists():
        return {"productoras_nuevas": {}, "venues_nuevos": {}}

    with open(p, "r", encoding="utf-8") as f:
        for linea in f:
            linea = linea.strip()
            if not linea:
                continue
            try:
                registro = json.loads(linea)
            except json.JSONDecodeError:
                continue

            vision = registro.get("vision")
            if not isinstance(vision, dict) or "error" in vision:
                continue

            path = registro.get("path", "")

            nombre_prod = (vision.get("productora") or "").strip()
            if nombre_prod:
                slug = _slug(nombre_prod)
                entrada = productoras.setdefault(slug, {
                    "nombre": nombre_prod,
                    "archivos_fuente": set(),
                    "instagram_handles": set(),
                    "eventos": set(),
                })
                entrada["archivos_fuente"].add(path)
                for h in vision.get("instagram_handles") or []:
                    if h:
                        entrada["instagram_handles"].add(h)
                if vision.get("evento"):
                    entrada["eventos"].add(vision["evento"])

            nombre_venue = (vision.get("venue") or "").strip()
            if nombre_venue:
                slug_v = _slug(nombre_venue)
                entrada_v = venues.setdefault(slug_v, {
                    "nombre": nombre_venue,
                    "archivos_fuente": set(),
                })
                entrada_v["archivos_fuente"].add(path)

    productoras_nuevas = {}
    for slug, datos in productoras.items():
        if _normalizar(datos["nombre"]) in productoras_conocidas:
            continue
        productoras_nuevas[slug] = {
            "nombre": datos["nombre"],
            "evidencia": len(datos["archivos_fuente"]),
            "archivos_fuente": sorted(datos["archivos_fuente"]),
            "instagram_handles": sorted(datos["instagram_handles"]),
            "eventos": sorted(datos["eventos"]),
        }

    venues_nuevos = {}
    for slug, datos in venues.items():
        if _normalizar(datos["nombre"]) in venues_conocidos:
            continue
        venues_nuevos[slug] = {
            "nombre": datos["nombre"],
            "evidencia": len(datos["archivos_fuente"]),
            "archivos_fuente": sorted(datos["archivos_fuente"]),
        }

    return {"productoras_nuevas": productoras_nuevas, "venues_nuevos": venues_nuevos}


# ---------------------------------------------------------------------------
# Paso 6: propuestas (borradores para PR humano)
# ---------------------------------------------------------------------------

def _ruta_segura(base: Path, *partes: str) -> Path:
    """Resuelve base/partes y garantiza que el resultado quede DENTRO de base."""
    base_resuelta = base.resolve()
    candidato = base_resuelta.joinpath(*partes).resolve()
    try:
        candidato.relative_to(base_resuelta)
    except ValueError:
        raise ValueError("ruta propuesta fuera de outdir: %s" % candidato)
    return candidato


def _borrador_productora(datos: dict) -> dict:
    instagram = ""
    if datos.get("instagram_handles"):
        instagram = datos["instagram_handles"][0]
    fuente = ", ".join(datos["archivos_fuente"][:5])
    return {
        "name": datos["nombre"],
        "aliases": [datos["nombre"]],
        "instagram": instagram,
        "tipos_fecha": [],
        "logos": [],
        "venues": [],
        "confirmed": "",
        "fuente_datos": (
            "mineria_rd.py sobre ~/RD, evidencia en %d archivo(s); "
            "sin confirmar por humano" % datos["evidencia"]
        ),
        "notes": "Candidato detectado por vision (gemma3:4b). Archivos: %s" % fuente,
    }


def _borrador_venue_yaml(slug: str, datos: dict) -> str:
    fuente = ", ".join(datos["archivos_fuente"][:5])
    fuente_txt = (
        "mineria_rd.py sobre ~/RD, evidencia en %d archivo(s) (%s)"
        % (datos["evidencia"], fuente)
    )
    lineas = [
        "id: %s" % json.dumps(slug, ensure_ascii=True),
        "name: %s" % json.dumps(datos["nombre"], ensure_ascii=True),
        "type: unknown",
        "scale_default: base",
        "capacity_bucket: unknown",
        "recommended_preset: base",
        "status: specs_needed",
        "source: %s" % json.dumps(fuente_txt, ensure_ascii=True),
        "notes:",
        "  - Candidato detectado por vision (gemma3:4b); sin confirmar por humano.",
        "  - FALTAN specs reales: aforo, m2, requisitos, preset confirmado.",
        "requirements_defaults: {}",
        "",
    ]
    return "\n".join(lineas)


def proponer(consolidado: dict, outdir: str = "propuestas_mineria") -> None:
    """
    Escribe borradores de productoras/venues nuevos DENTRO de `outdir`,
    calcando el schema real de data/productoras/*.json y
    knowledge/venues/*.yaml. Nunca escribe fuera de `outdir` (ver
    _ruta_segura); nunca toca data/ ni knowledge/ directamente.
    """
    base = Path(outdir)
    (base / "productoras").mkdir(parents=True, exist_ok=True)
    (base / "venues").mkdir(parents=True, exist_ok=True)

    productoras_nuevas = consolidado.get("productoras_nuevas", {})
    venues_nuevos = consolidado.get("venues_nuevos", {})

    lineas_resumen = [
        "# Propuestas de mineria RD",
        "",
        "Borradores generados por cultura/mak_plataforma/mineria_rd.py. "
        "Revisar y confirmar antes de mergear a data/ / knowledge/.",
        "",
        "## Productoras nuevas (%d)" % len(productoras_nuevas),
    ]

    for slug, datos in sorted(productoras_nuevas.items()):
        slug_seguro = _slug(slug)
        ruta = _ruta_segura(base, "productoras", slug_seguro + ".json")
        borrador = _borrador_productora(datos)
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(borrador, f, ensure_ascii=False, indent=2)
            f.write("\n")
        lineas_resumen.append(
            "- %s (evidencia: %d archivo(s))" % (datos["nombre"], datos["evidencia"])
        )

    lineas_resumen.append("")
    lineas_resumen.append("## Venues nuevos (%d)" % len(venues_nuevos))

    for slug, datos in sorted(venues_nuevos.items()):
        slug_seguro = _slug(slug)
        ruta = _ruta_segura(base, "venues", slug_seguro + ".yaml")
        contenido = _borrador_venue_yaml(slug_seguro, datos)
        with open(ruta, "w", encoding="utf-8") as f:
            f.write(contenido)
        lineas_resumen.append(
            "- %s (evidencia: %d archivo(s))" % (datos["nombre"], datos["evidencia"])
        )

    ruta_resumen = _ruta_segura(base, "RESUMEN.md")
    with open(ruta_resumen, "w", encoding="utf-8") as f:
        f.write("\n".join(lineas_resumen) + "\n")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Mineria RD: OCR + vision sobre ~/RD, candidatos via PR (F3d)."
    )
    sub = parser.add_subparsers(dest="comando", required=True)

    p_minar = sub.add_parser(
        "minar", help="Recorre ~/RD, hace OCR/vision y acumula candidatos (resumible)."
    )
    p_minar.add_argument("--raiz", default="~/RD")
    p_minar.add_argument("--limite", type=int, default=None)
    p_minar.add_argument("--solo", choices=["imagenes", "pdfs"], default=None)
    p_minar.add_argument("--estado", default="mineria_estado.json")
    p_minar.add_argument("--jsonl", default="mineria_candidatos.jsonl")

    p_consolidar = sub.add_parser(
        "consolidar", help="Agrupa candidatos del jsonl en productoras/venues nuevos."
    )
    p_consolidar.add_argument("--jsonl", default="mineria_candidatos.jsonl")
    p_consolidar.add_argument(
        "--out", default=None, help="Si se da, escribe el consolidado JSON en este archivo."
    )

    p_proponer = sub.add_parser(
        "proponer", help="Escribe borradores de productoras/venues nuevos en outdir."
    )
    p_proponer.add_argument("--jsonl", default="mineria_candidatos.jsonl")
    p_proponer.add_argument("--outdir", default="propuestas_mineria")

    args = parser.parse_args()

    if args.comando == "minar":
        minar(
            args.raiz, limite=args.limite, solo_tipo=args.solo,
            estado_path=args.estado, jsonl_path=args.jsonl,
        )
        print("mineria: ok (estado=%s, jsonl=%s)" % (args.estado, args.jsonl))
    elif args.comando == "consolidar":
        resultado = consolidar(args.jsonl)
        texto = json.dumps(resultado, ensure_ascii=False, indent=2)
        if args.out:
            with open(args.out, "w", encoding="utf-8") as f:
                f.write(texto + "\n")
            print("consolidado escrito en %s" % args.out)
        else:
            print(texto)
    elif args.comando == "proponer":
        resultado = consolidar(args.jsonl)
        proponer(resultado, outdir=args.outdir)
        print("propuestas escritas en %s" % args.outdir)


if __name__ == "__main__":
    main()
