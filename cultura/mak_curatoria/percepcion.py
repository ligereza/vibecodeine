#!/usr/bin/env python3
"""percepcion.py -- departamento CURATORIA de MAK: percepcion unificada.

Recorre 2 corpus (archivo RD + media IG), les hace OCR + vision (ollama
gemma3:4b) y escribe una ficha de schema UNICO por archivo, resumible
(checkpoint) y con auto-pausa si se acumulan errores seguidos (avalancha).

Ambiente objetivo: tesseract 5.x + spa, ffmpeg/ffprobe, poppler
(pdftotext/pdftoppm), ollama gemma3:4b en localhost. Todo opcional: si una
herramienta no esta instalada, la ficha queda con el campo vacio y
"error" seteado, pero el loop NUNCA se cae por un archivo puntual.

stdlib puro + PIL (ya presente en el entorno). PIL se usa para 2 cosas:
- vision: toda imagen se reescala a lado mayor MAX_LADO_VISION (1280px) y
  se re-encodea JPEG calidad 85 antes de mandarla en base64 a ollama.
- OCR: si el archivo original pesa mas de UMBRAL_BYTES_OCR_RESCALE (8MB),
  tesseract corre sobre una copia reescalada a lado mayor MAX_LADO_OCR
  (2000px) en vez del original (evita que un flyer de produccion de
  ~50MB se cuelgue). Si pesa menos, corre sobre el original tal cual.
NUNCA se descarta un archivo por tamano: el walker no filtra por bytes,
y si el reescalado con PIL falla se cae al archivo original (tesseract
puede fallar despues, eso ya queda tolerado como "error" en la ficha).
Si PIL no esta disponible, todo esto cae a leer/usar los bytes crudos.

    python3 percepcion.py correr --raiz-rd RUTA --raiz-ig RUTA --out DIR
        [--max-errores-seguidos 20] [--timeout-archivo 120]
        [--solo-fuente rd|ig]
    python3 percepcion.py estado --out DIR
"""
import base64
import hashlib
import io
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    Image = None

EXT_IMAGEN = {".jpg", ".jpeg", ".png", ".webp"}
EXT_VIDEO = {".mp4", ".mov"}
EXT_PDF = {".pdf"}

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
OLLAMA_MODEL = "gemma3:4b"

DEFAULT_MAX_ERRORES_SEGUIDOS = 20
DEFAULT_TIMEOUT_ARCHIVO = 120

VIDEO_LARGO_SEG = 120
TILE_FRAMES = 9  # tile 3x3
GUARDADO_CADA_N = 10
MAX_ULTIMOS_ERRORES = 5

MAX_LADO_VISION = 1280
MAX_LADO_OCR = 2000
UMBRAL_BYTES_OCR_RESCALE = 8 * 1024 * 1024  # 8MB

CATEGORIAS_VALIDAS = (
    "flyer_evento", "material_rd", "logo", "ficha_sustancia",
    "foto_evento", "obra", "otro",
)

PROMPT_VISION = (
    "Analiza esta imagen de una obra/pieza cultural o flyer de evento y "
    "responde SOLO con un objeto JSON, sin texto adicional antes ni "
    "despues. Formato exacto de las claves: "
    '{"descripcion": "", "estilo": "", "colores": [], "tipo_obra": "", '
    '"categoria": "", "productora": "", "venue": "", "fecha": "", '
    '"handles": []}. El campo categoria debe ser EXACTAMENTE uno de '
    "estos valores (enum): flyer_evento, material_rd, logo, "
    "ficha_sustancia, foto_evento, obra, otro. Si "
    "parece un flyer de evento completa productora/venue/fecha/handles; "
    "si no, dejalos vacios. No inventes datos que no veas."
)


# ---------------------------------------------------------------------------
# Paso 1: recorrido de los 2 corpus (orden estable)
# ---------------------------------------------------------------------------

def clasificar_ext(path: Path) -> str:
    """Clasificacion barata por extension: imagen | video | pdf | otro."""
    ext = path.suffix.lower()
    if ext in EXT_IMAGEN:
        return "imagen"
    if ext in EXT_VIDEO:
        return "video"
    if ext in EXT_PDF:
        return "pdf"
    return "otro"


def recorrer(raiz, fuente: str) -> list[dict]:
    """Recorre `raiz` y devuelve la lista de archivos en orden estable.

    Cada item: {"fuente", "ruta_rel" (posix, relativo a raiz), "ruta_abs",
    "tipo", "bytes", "mtime"}. Directorios y archivos se ordenan con
    sorted() en cada nivel y el resultado final se re-ordena por
    ruta_rel, asi el orden no depende del filesystem/SO.
    """
    raiz_path = Path(raiz)
    resultado: list[dict] = []
    if not raiz_path.exists():
        return resultado

    for dirpath, dirnames, filenames in os.walk(raiz_path):
        dirnames.sort()
        for nombre in sorted(filenames):
            p = Path(dirpath) / nombre
            try:
                st = p.stat()
            except OSError:
                continue
            ruta_rel = p.relative_to(raiz_path).as_posix()
            resultado.append({
                "fuente": fuente,
                "ruta_rel": ruta_rel,
                "ruta_abs": str(p),
                "tipo": clasificar_ext(p),
                "bytes": st.st_size,
                "mtime": st.st_mtime,
            })

    resultado.sort(key=lambda e: e["ruta_rel"])
    return resultado


def construir_trabajo(raiz_rd, raiz_ig, solo_fuente: str | None = None) -> list[dict]:
    """Junta el trabajo de ambas raices (o solo una si `solo_fuente`)."""
    trabajo: list[dict] = []
    if solo_fuente in (None, "rd") and raiz_rd:
        trabajo.extend(recorrer(raiz_rd, "rd"))
    if solo_fuente in (None, "ig") and raiz_ig:
        trabajo.extend(recorrer(raiz_ig, "ig"))
    return trabajo


# ---------------------------------------------------------------------------
# Paso 2: checkpoint (procesados.txt)
# ---------------------------------------------------------------------------

def clave_checkpoint(fuente: str, ruta_rel: str) -> str:
    """Clave unica de checkpoint: fuente+ruta_rel (2 corpus pueden repetir
    la misma ruta relativa)."""
    return "%s:%s" % (fuente, ruta_rel)


def cargar_procesados(dir_out: Path) -> set:
    p = Path(dir_out) / "procesados.txt"
    if not p.exists():
        return set()
    try:
        with p.open("r", encoding="utf-8") as f:
            return {linea.strip() for linea in f if linea.strip()}
    except OSError:
        return set()


def marcar_procesado(dir_out: Path, clave: str) -> None:
    p = Path(dir_out) / "procesados.txt"
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as f:
        f.write(clave + "\n")


def id_ficha(fuente: str, ruta_rel: str) -> str:
    """Hash corto (12 hex) de fuente+ruta_rel, usado como id de la ficha."""
    return hashlib.sha1(clave_checkpoint(fuente, ruta_rel).encode("utf-8")).hexdigest()[:12]


# ---------------------------------------------------------------------------
# Paso 3: OCR (tesseract / pdftotext), tolerante a ausencia
# ---------------------------------------------------------------------------

def ocr_tesseract(path: str, timeout: int = 60) -> str:
    """OCR spa via tesseract. Tolerante: sin tesseract instalado -> ''."""
    try:
        proc = subprocess.run(
            ["tesseract", str(path), "stdout", "-l", "spa"],
            capture_output=True, text=True, timeout=timeout,
        )
        return (proc.stdout or "").strip()
    except (OSError, subprocess.SubprocessError):
        return ""


def preparar_imagen_para_ocr(path: str, dir_tmp,
                             umbral_bytes: int = UMBRAL_BYTES_OCR_RESCALE,
                             max_lado: int = MAX_LADO_OCR) -> str:
    """Devuelve la ruta que debe usar `ocr_tesseract`.

    Si el archivo original pesa <= `umbral_bytes`, corre sobre el
    original tal cual. Si pesa mas (flyers de produccion de 40-50MB
    existen en ~/RD), genera una copia PNG reescalada a lado mayor
    `max_lado` en `dir_tmp` para que tesseract no tenga que digerir el
    archivo completo. NUNCA descarta el archivo: si PIL no esta
    disponible o el reescalado falla por la razon que sea, cae al path
    original (tesseract puede fallar despues; eso ya queda tolerado
    aparte como "error" en la ficha).
    """
    try:
        tamano = Path(path).stat().st_size
    except OSError:
        return path

    if tamano <= umbral_bytes or Image is None:
        return path

    try:
        with Image.open(path) as im:
            im = im.convert("RGB")
            w, h = im.size
            if max(w, h) > max_lado:
                escala = max_lado / max(w, h)
                nuevo = (max(1, int(w * escala)), max(1, int(h * escala)))
                im = im.resize(nuevo, Image.LANCZOS)
            dir_tmp_p = Path(dir_tmp)
            dir_tmp_p.mkdir(parents=True, exist_ok=True)
            nombre = "ocr_%s.png" % hashlib.sha1(str(path).encode("utf-8")).hexdigest()[:10]
            destino = dir_tmp_p / nombre
            im.save(destino, format="PNG")
            return str(destino)
    except Exception:
        return path


def ocr_pdftotext_primera_pagina(path: str, timeout: int = 60) -> str:
    """Texto de la primera pagina de un PDF via pdftotext -layout."""
    try:
        proc = subprocess.run(
            ["pdftotext", "-f", "1", "-l", "1", "-layout", str(path), "-"],
            capture_output=True, text=True, timeout=timeout,
        )
        return (proc.stdout or "").strip()
    except (OSError, subprocess.SubprocessError):
        return ""


def pdf_primera_pagina_a_imagen(path: str, dir_tmp: Path, timeout: int = 60) -> str | None:
    """Convierte la primera pagina del PDF a JPEG via pdftoppm.

    Devuelve la ruta de la imagen generada, o None si pdftoppm no esta
    disponible o no produjo salida (PDF vectorial raro, herramienta
    ausente, etc.) -- en ese caso el llamador se queda solo con el texto.
    """
    dir_tmp = Path(dir_tmp)
    dir_tmp.mkdir(parents=True, exist_ok=True)
    base_nombre = "pdfpag_%s" % hashlib.sha1(str(path).encode("utf-8")).hexdigest()[:10]
    salida_base = dir_tmp / base_nombre
    try:
        subprocess.run(
            ["pdftoppm", "-jpeg", "-f", "1", "-l", "1", "-r", "100",
             str(path), str(salida_base)],
            capture_output=True, timeout=timeout, check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None

    candidatos = sorted(dir_tmp.glob(base_nombre + "*.jpg"))
    return str(candidatos[0]) if candidatos else None


# ---------------------------------------------------------------------------
# Paso 4: contact sheet de video (ffmpeg/ffprobe)
# ---------------------------------------------------------------------------

def ffprobe_duracion(path: str, timeout: int = 30) -> float | None:
    """Duracion en segundos via ffprobe. None si ffprobe falla/ausente."""
    try:
        proc = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
            capture_output=True, text=True, timeout=timeout,
        )
        salida = (proc.stdout or "").strip()
        return float(salida) if salida else None
    except (OSError, subprocess.SubprocessError, ValueError):
        return None


def construir_comando_contact_sheet(path_video: str, path_salida: str,
                                     duracion: float | None = None) -> list[str]:
    """Arma el comando ffmpeg de un contact sheet 3x3 (9 tomas, 1 imagen).

    fps por defecto 1/3 (cubre ~27s con las 9 tomas). Si el video dura
    mas de VIDEO_LARGO_SEG, usa fps proporcional (TILE_FRAMES/duracion)
    para que las 9 tomas cubran todo el video en vez de solo el arranque.
    """
    if duracion and duracion > VIDEO_LARGO_SEG:
        fps = TILE_FRAMES / duracion
    else:
        fps = 1.0 / 3.0
    vf = "fps=%s,scale=480:-1,tile=3x3" % fps
    return [
        "ffmpeg", "-y", "-i", str(path_video),
        "-vf", vf,
        "-frames:v", "1",
        str(path_salida),
    ]


def generar_contact_sheet(path_video: str, path_salida: str, timeout: int = 60) -> bool:
    """Genera el contact sheet en `path_salida`. True si el archivo quedo."""
    duracion = ffprobe_duracion(path_video, timeout=min(timeout, 30))
    comando = construir_comando_contact_sheet(path_video, path_salida, duracion)
    try:
        subprocess.run(comando, capture_output=True, timeout=timeout, check=False)
    except (OSError, subprocess.SubprocessError):
        return False
    return Path(path_salida).exists()


# ---------------------------------------------------------------------------
# Paso 5: vision (ollama gemma3:4b)
# ---------------------------------------------------------------------------

def _imagen_a_b64(path: str, max_lado: int = MAX_LADO_VISION) -> str | None:
    """Prepara una imagen para vision como base64.

    Si PIL esta disponible: abre, convierte a RGB, la achica si supera
    `max_lado` y la re-encodea como JPEG (asi webp/png raros llegan en un
    formato mas parejo al modelo y el payload no explota con fotos
    gigantes). Si PIL falla o no esta instalado, cae a leer los bytes
    crudos del archivo.
    """
    if Image is not None:
        try:
            with Image.open(path) as im:
                im = im.convert("RGB")
                w, h = im.size
                if max(w, h) > max_lado:
                    escala = max_lado / max(w, h)
                    nuevo = (max(1, int(w * escala)), max(1, int(h * escala)))
                    im = im.resize(nuevo, Image.LANCZOS)
                buf = io.BytesIO()
                im.save(buf, format="JPEG", quality=85)
                return base64.b64encode(buf.getvalue()).decode("ascii")
        except Exception:
            pass

    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode("ascii")
    except OSError:
        return None


def _parsear_json_vision(texto: str) -> dict:
    """Busca el primer '{' y el ultimo '}' y parsea eso como JSON.

    Ante cualquier fallo devuelve {"error": ...} en vez de reventar. Ante
    exito, garantiza que todas las claves del schema de vision esten
    presentes (default vacio) para que el llamador nunca tenga que
    chequear ausencia de clave.
    """
    inicio = texto.find("{")
    fin = texto.rfind("}")
    if inicio == -1 or fin == -1 or fin < inicio:
        return {"error": "sin_json_en_respuesta"}

    fragmento = texto[inicio:fin + 1]
    try:
        datos = json.loads(fragmento)
    except json.JSONDecodeError as exc:
        return {"error": "json_invalido: %s" % exc}

    if not isinstance(datos, dict):
        return {"error": "json_no_es_objeto"}

    for clave, default in (
        ("descripcion", ""), ("estilo", ""), ("colores", []), ("tipo_obra", ""),
        ("categoria", ""), ("productora", ""), ("venue", ""), ("fecha", ""),
        ("handles", []),
    ):
        datos.setdefault(clave, default)
    if datos.get("categoria") not in CATEGORIAS_VALIDAS:
        datos["categoria"] = ""
    return datos


def vision_imagen(path: str, timeout: int = 120) -> dict:
    """Manda `path` (imagen ya lista, o contact sheet de video) a ollama
    y devuelve el JSON de vision parseado de forma tolerante. Cualquier
    fallo de lectura/red/parseo devuelve {"error": ...} sin lanzar
    excepcion, para que un archivo puntual nunca tumbe el loop."""
    imagen_b64 = _imagen_a_b64(path)
    if imagen_b64 is None:
        return {"error": "no_se_pudo_leer_imagen"}

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
        return {"error": "ollama_no_disponible: %s" % exc}

    try:
        sobre = json.loads(cuerpo)
    except json.JSONDecodeError:
        return {"error": "respuesta_no_json"}

    texto_modelo = sobre.get("response", "") if isinstance(sobre, dict) else ""
    return _parsear_json_vision(texto_modelo)


# ---------------------------------------------------------------------------
# Paso 6: ficha (schema UNICO)
# ---------------------------------------------------------------------------

def calcular_calidad_senal(ocr_texto: str, vision: dict) -> str:
    """alta: vision parseo limpio y (ocr>50 chars o descripcion>100).
    baja: vision con error (fallo parcial) o sin ninguna senal.
    media: vision parseo limpio pero senal debil (ni ocr ni descripcion
    largos)."""
    vision = vision or {}
    if vision.get("error"):
        return "baja"
    descripcion = vision.get("descripcion") or ""
    if len(ocr_texto or "") > 50 or len(descripcion) > 100:
        return "alta"
    if vision or ocr_texto:
        return "media"
    return "baja"


def _mtime_a_fecha(mtime) -> str:
    try:
        return datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")
    except (OSError, OverflowError, ValueError, TypeError):
        return ""


def construir_ficha(entry: dict, dir_tmp: Path, timeout_archivo: int) -> dict:
    """Construye la ficha de schema UNICO para un item de trabajo.

    Nunca lanza: cualquier excepcion durante el analisis queda como
    "error" en la ficha y el resto de los campos con sus defaults, para
    que el loop de `correr()` pueda seguir con el resto de los archivos.
    """
    fuente = entry["fuente"]
    ruta_rel = entry["ruta_rel"]
    ruta_abs = entry["ruta_abs"]
    tipo = entry["tipo"]

    t0 = time.time()
    ocr_texto = ""
    vision: dict = {}
    error = None

    try:
        if tipo == "imagen":
            ruta_ocr = preparar_imagen_para_ocr(ruta_abs, dir_tmp)
            ocr_texto = ocr_tesseract(ruta_ocr, timeout=timeout_archivo)
            if ruta_ocr != ruta_abs:
                try:
                    Path(ruta_ocr).unlink(missing_ok=True)
                except OSError:
                    pass
            vision = vision_imagen(ruta_abs, timeout=timeout_archivo)

        elif tipo == "video":
            sheet_path = Path(dir_tmp) / ("sheet_%s.jpg" % id_ficha(fuente, ruta_rel))
            ok = generar_contact_sheet(ruta_abs, str(sheet_path), timeout=timeout_archivo)
            if ok:
                vision = vision_imagen(str(sheet_path), timeout=timeout_archivo)
                try:
                    sheet_path.unlink(missing_ok=True)
                except OSError:
                    pass
            else:
                vision = {"error": "contact_sheet_fallo"}

        elif tipo == "pdf":
            ocr_texto = ocr_pdftotext_primera_pagina(ruta_abs, timeout=timeout_archivo)
            imagen_pdf = pdf_primera_pagina_a_imagen(ruta_abs, dir_tmp, timeout=timeout_archivo)
            if imagen_pdf:
                vision = vision_imagen(imagen_pdf, timeout=timeout_archivo)
                try:
                    Path(imagen_pdf).unlink(missing_ok=True)
                except OSError:
                    pass
        # tipo "otro": clasificacion barata, sin analisis.

    except Exception as exc:  # nunca tumbar el loop por un archivo puntual
        error = "excepcion_no_controlada: %s" % exc

    if not isinstance(vision, dict):
        vision = {}
    if vision.get("error") and error is None:
        error = vision["error"]

    vision_final = {
        "descripcion": vision.get("descripcion", "") or "",
        "estilo": vision.get("estilo", "") or "",
        "colores": vision.get("colores") or [],
        "tipo_obra": vision.get("tipo_obra", "") or "",
    }
    datos_evento = {
        "productora": vision.get("productora", "") or "",
        "venue": vision.get("venue", "") or "",
        "fecha": vision.get("fecha", "") or "",
        "handles": vision.get("handles") or [],
    }
    categoria = vision.get("categoria", "") or ""

    return {
        "id": id_ficha(fuente, ruta_rel),
        "fuente": fuente,
        "ruta_rel": ruta_rel,
        "tipo": tipo,
        "categoria": categoria,
        "bytes": entry.get("bytes", 0),
        "mtime": _mtime_a_fecha(entry.get("mtime")),
        "ocr_texto": (ocr_texto or "")[:1500],
        "vision": vision_final,
        "datos_evento": datos_evento,
        "calidad_senal": calcular_calidad_senal(ocr_texto, vision),
        "error": error,
        "seg_proceso": round(time.time() - t0, 3),
        "ts": datetime.now(timezone.utc).isoformat(),
    }


def escribir_ficha(dir_fichas: Path, ficha: dict) -> None:
    """Append de una ficha a fichas.jsonl, una linea JSON por archivo."""
    dir_fichas = Path(dir_fichas)
    dir_fichas.mkdir(parents=True, exist_ok=True)
    ruta = dir_fichas / "fichas.jsonl"
    linea = json.dumps(ficha, ensure_ascii=True)
    with ruta.open("a", encoding="utf-8") as f:
        f.write(linea + "\n")
        f.flush()


# ---------------------------------------------------------------------------
# Paso 7: estado.json
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


def guardar_estado(dir_out, estado: dict) -> None:
    dir_out = Path(dir_out)
    dir_out.mkdir(parents=True, exist_ok=True)
    p = dir_out / "estado.json"
    tmp = dir_out / "estado.json.tmp"
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(estado, f, ensure_ascii=True, indent=2)
    os.replace(tmp, p)


# ---------------------------------------------------------------------------
# Paso 8: loop principal (correr)
# ---------------------------------------------------------------------------

def correr(raiz_rd, raiz_ig, dir_out,
           max_errores_seguidos: int = DEFAULT_MAX_ERRORES_SEGUIDOS,
           timeout_archivo: int = DEFAULT_TIMEOUT_ARCHIVO,
           solo_fuente: str | None = None) -> int:
    """Corre la percepcion sobre ambos corpus. Retorna el codigo de salida:

    0 = termino todo el trabajo pendiente.
    3 = auto-pausa por errores_seguidos >= max_errores_seguidos.
    """
    dir_out = Path(dir_out)
    dir_fichas = dir_out / "fichas"
    dir_tmp = dir_out / "_tmp"
    dir_out.mkdir(parents=True, exist_ok=True)

    trabajo = construir_trabajo(raiz_rd, raiz_ig, solo_fuente=solo_fuente)
    total_trabajo = len(trabajo)

    procesados_set = cargar_procesados(dir_out)

    estado_previo = cargar_estado(dir_out)
    inicio_ts = estado_previo.get("inicio") or datetime.now(timezone.utc).isoformat()
    por_fuente = dict(estado_previo.get("por_fuente") or {"rd": 0, "ig": 0})
    por_fuente.setdefault("rd", 0)
    por_fuente.setdefault("ig", 0)
    errores_totales = estado_previo.get("errores_totales", 0)
    ultimos_errores = list(estado_previo.get("ultimos_errores") or [])

    errores_seguidos = 0
    procesados_count = len(procesados_set)
    tiempos: list[float] = []
    contador_desde_guardado = 0

    def _snapshot(pausado_por):
        seg_prom = (sum(tiempos) / len(tiempos)) if tiempos else 0.0
        return {
            "inicio": inicio_ts,
            "ultimo": datetime.now(timezone.utc).isoformat(),
            "total_trabajo": total_trabajo,
            "procesados": procesados_count,
            "por_fuente": por_fuente,
            "errores_totales": errores_totales,
            "errores_seguidos": errores_seguidos,
            "seg_por_archivo_prom": round(seg_prom, 3),
            "pausado_por": pausado_por,
            "ultimos_errores": ultimos_errores[-MAX_ULTIMOS_ERRORES:],
        }

    for entry in trabajo:
        clave = clave_checkpoint(entry["fuente"], entry["ruta_rel"])
        if clave in procesados_set:
            continue

        ficha = construir_ficha(entry, dir_tmp, timeout_archivo)
        tiempos.append(ficha.get("seg_proceso") or 0.0)
        if len(tiempos) > 200:
            del tiempos[:-200]

        escribir_ficha(dir_fichas, ficha)

        procesados_set.add(clave)
        marcar_procesado(dir_out, clave)
        procesados_count += 1
        por_fuente[entry["fuente"]] = por_fuente.get(entry["fuente"], 0) + 1

        if ficha.get("error"):
            errores_totales += 1
            errores_seguidos += 1
            ultimos_errores.append({
                "ruta_rel": entry["ruta_rel"],
                "error": ficha["error"],
            })
            ultimos_errores = ultimos_errores[-MAX_ULTIMOS_ERRORES:]
        else:
            errores_seguidos = 0

        contador_desde_guardado += 1
        if contador_desde_guardado >= GUARDADO_CADA_N:
            guardar_estado(dir_out, _snapshot(None))
            contador_desde_guardado = 0

        if errores_seguidos >= max_errores_seguidos:
            guardar_estado(dir_out, _snapshot("errores_seguidos"))
            return 3

    guardar_estado(dir_out, _snapshot("fin"))
    return 0


# ---------------------------------------------------------------------------
# CLI (sys.argv manual)
# ---------------------------------------------------------------------------

def _obtener_flag(argv: list, nombre: str, default=None):
    if nombre in argv:
        idx = argv.index(nombre)
        if idx + 1 < len(argv):
            return argv[idx + 1]
    return default


def main() -> int:
    """CLI: correr --raiz-rd .. --raiz-ig .. --out DIR [...] | estado --out DIR"""
    argv = sys.argv[1:]
    if not argv:
        print("uso: percepcion.py [correr|estado] ...", file=sys.stderr)
        return 2

    cmd = argv[0]
    resto = argv[1:]

    if cmd == "correr":
        raiz_rd = _obtener_flag(resto, "--raiz-rd")
        raiz_ig = _obtener_flag(resto, "--raiz-ig")
        out = _obtener_flag(resto, "--out")
        if not out:
            print("ERROR: --out es obligatorio", file=sys.stderr)
            return 2

        solo_fuente = _obtener_flag(resto, "--solo-fuente")
        if solo_fuente not in (None, "rd", "ig"):
            print("ERROR: --solo-fuente debe ser rd o ig", file=sys.stderr)
            return 2

        try:
            max_errores = int(_obtener_flag(
                resto, "--max-errores-seguidos", DEFAULT_MAX_ERRORES_SEGUIDOS))
            timeout_archivo = int(_obtener_flag(
                resto, "--timeout-archivo", DEFAULT_TIMEOUT_ARCHIVO))
        except ValueError:
            print("ERROR: --max-errores-seguidos/--timeout-archivo deben ser enteros",
                  file=sys.stderr)
            return 2

        try:
            return correr(
                raiz_rd, raiz_ig, out,
                max_errores_seguidos=max_errores,
                timeout_archivo=timeout_archivo,
                solo_fuente=solo_fuente,
            )
        except Exception as exc:
            print("ERROR correr: %s" % exc, file=sys.stderr)
            return 1

    elif cmd == "estado":
        out = _obtener_flag(resto, "--out")
        if not out:
            print("ERROR: --out es obligatorio", file=sys.stderr)
            return 2
        estado = cargar_estado(out)
        print(json.dumps(estado, ensure_ascii=False, indent=2))
        return 0

    else:
        print("uso: percepcion.py [correr|estado] ...", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
