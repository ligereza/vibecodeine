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
        [--solo-fuente rd|ig] [--limite N] [--meta-ig ig_meta.json]
    python3 percepcion.py estado --out DIR
"""
import base64
import hashlib
import io
import json
import os
import re
import subprocess
import sys
import time
import unicodedata
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

# Lo mismo para el archivo del artista. Es un vocabulario CERRADO, y existe por
# una medicion del 2026-07-27 sobre las 937 fichas ig del corpus real: el prompt
# viejo dejaba el tipo en texto libre y salieron 20 valores distintos donde
# tenia que haber un conjunto fijo. Dos pares eran el MISMO tipo escrito de dos
# formas -- tatuaje(42)/tattoo(16), 58 obras partidas en dos, y obra(503)/
# obras(3) -- y la cola era tecnica disfrazada de tipo (dibujo, pintura,
# ilustracion, tela), que ya tiene su propio campo.
#
# Ninguno de estos nombres se invento: son los que MAK ya escribio, colapsados.
# Y hace falta que el tipo VUELVA: el prompt nuevo lo habia dejado de pedir, asi
# que las fichas ig salian sin ninguna clasificacion -- `categoria` solo se llena
# desde el prompt RD. Eso es lo que llevo al tramo anterior a pedirle al usuario
# que clasificara 697 obras a mano.
TIPOS_OBRA_VALIDOS = (
    "obra", "tatuaje", "foto_evento", "logo", "flyer_evento",
    "material_rd", "ficha_sustancia", "otro",
)

# Lo que el modelo escribe distinto para decir lo mismo. Se normaliza aca, en el
# ORIGEN, para que no haya que arreglarlo aguas abajo en cada consumidor.
SINONIMOS_TIPO_OBRA = {
    "tattoo": "tatuaje", "tatuajes": "tatuaje",
    "obras": "obra", "obra de arte": "obra", "obras de arte": "obra",
    "foto": "foto_evento", "fotografia": "foto_evento",
}

PROMPT_RD = (
    "Esta imagen es material de Reduciendo Dano, una ONG de reduccion de danos "
    "que trabaja en eventos de musica electronica: flyers de fiesta, material "
    "informativo, fichas de sustancias o logos. NO es una obra de arte. Tu "
    "trabajo es EXTRAER DATOS, no interpretarla. "
    "Responde SOLO con un objeto JSON, sin texto antes ni despues. Claves "
    "exactas: "
    '{"categoria": "", "productora": "", "venue": "", "fecha": "", '
    '"headliners": [], "handles": [], "texto_visible": "", "colores": []}. '
    "categoria debe ser EXACTAMENTE uno de: flyer_evento, material_rd, logo, "
    "ficha_sustancia, foto_evento, otro. "
    "headliners son los nombres de artistas del cartel, en orden de tamano "
    "tipografico: el mas grande primero. Es el dato MAS importante junto con la "
    "fecha, porque con artista y fecha se puede identificar despues quien "
    "produjo la fiesta. Si ves nombres de artistas, listalos SIEMPRE, aunque no "
    "reconozcas la productora. "
    "handles son cuentas de instagram visibles (@algo). "
    "texto_visible es todo el texto que puedas leer, tal cual, sin resumir. "
    "fecha en el formato que aparezca; no la conviertas ni la inventes. "
    "Si un campo no esta en la imagen, dejalo vacio. No inventes NADA."
)


PROMPT_ISKVW = (
    "Esta imagen es una obra del archivo personal del artista (iskvw). NO es "
    "un flyer ni material de una ONG: no busques productora, venue ni fecha de "
    "evento. Tu trabajo es entenderla para poder RELACIONARLA con las demas "
    "obras del archivo. "
    "Responde SOLO con un objeto JSON, sin texto antes ni despues. Claves "
    "exactas: "
    '{"tipo_obra": "", "descripcion": "", "conceptos": [], "tecnica": "", '
    '"materiales": [], '
    '"colores": [], "texto_visible": "", "datos_extraibles": "", '
    '"linea_investigacion": "", "oportunidad_codigo": ""}. '
    "tipo_obra debe ser EXACTAMENTE uno de: " + ", ".join(TIPOS_OBRA_VALIDOS) +
    ". Es lo que la imagen ES, no como esta hecha: si es una obra del artista "
    "poné obra, si es un tatuaje poné tatuaje, si es la foto de una fiesta poné "
    "foto_evento. Si no podes decidir, poné otro y no inventes una categoria "
    "nueva. "
    "conceptos son 3 a 6 ideas o temas que la obra toca, en palabras sueltas o "
    "frases cortas: son las que van a unir esta obra con otras, asi que usa "
    "terminos que se repitan entre obras parecidas y no descripciones unicas. "
    "tecnica es como parece estar hecha (fotografia, render 3D, collage, ASCII, "
    "grabado, IA generativa, etc). "
    "datos_extraibles: si la obra contiene informacion estructurada que se "
    "podria leer y tabular (una tabla, una serie, coordenadas, una notacion, un "
    "codigo), describila; si no hay, deja vacio. "
    "linea_investigacion: si la obra abre una pregunta que valga la pena "
    "investigar, formulala en una frase; si no, deja vacio. "
    "oportunidad_codigo: si la obra sugiere un procedimiento que podria "
    "automatizarse o generarse por codigo (por ejemplo si trata de matematica, "
    "de patrones, de repeticion o de sistemas), describi en una frase que "
    "programa la generaria; si no aplica, deja vacio. "
    "No inventes: si algo no esta, dejalo vacio."
)


# Que claves se conservan de la respuesta del modelo, por corpus. Antes esto
# estaba cableado a un solo esquema y descartaba en silencio todo lo que pedia
# el prompt nuevo (headliners, conceptos, oportunidad_codigo...).
ESQUEMA_POR_FUENTE = {
    "rd": (
        ("categoria", ""), ("productora", ""), ("venue", ""), ("fecha", ""),
        ("headliners", []), ("handles", []), ("texto_visible", ""),
        ("colores", []),
    ),
    "ig": (
        ("tipo_obra", ""),
        ("descripcion", ""), ("conceptos", []), ("tecnica", ""),
        ("materiales", []), ("colores", []), ("texto_visible", ""),
        ("datos_extraibles", ""), ("linea_investigacion", ""),
        ("oportunidad_codigo", ""),
    ),
}

# Lo que va al bloque `vision` de la ficha (lo descriptivo) y lo que va a
# `datos_evento` (lo extraido, solo RD).
CLAVES_VISION = {
    "rd": ("texto_visible", "colores"),
    "ig": ("tipo_obra", "descripcion", "conceptos", "tecnica", "materiales",
           "colores",
           "texto_visible", "datos_extraibles", "linea_investigacion",
           "oportunidad_codigo"),
}
CLAVES_EVENTO = ("productora", "venue", "fecha", "headliners", "handles")

# Campos de `datos_evento` cuyo valor SE PUEDE contrastar contra el texto que
# se leyo de la imagen. `fecha` queda fuera a proposito: el modelo normaliza
# ("VIERNES 01 MAYO" -> "2026-05-01") y comparar palabras diria "sin respaldo"
# sobre una lectura correcta. Medir con el instrumento equivocado y reportar el
# resultado es peor que no medir. `handles` tampoco: una arroba se deduce
# legitimamente de un correo.
CONTRASTABLES = ("productora", "venue", "headliners")


def _plegar_texto(t: str) -> str:
    d = unicodedata.normalize("NFKD", t or "")
    return "".join(c for c in d if not unicodedata.combining(c)).lower()


def _palabras_de(t: str, minimo: int = 3) -> set:
    return {p for p in re.findall(r"[a-z0-9]+", _plegar_texto(t))
            if len(p) >= minimo}


def respaldo_evento(datos_evento: dict, ocr_texto: str,
                    texto_visible: str) -> dict:
    """Que campos extraidos APARECEN en el texto que se leyo de la imagen.

    Medido el 2026-08-01 sobre 300 archivos reales de RD: `venue` tenia
    respaldo en el 99% de los casos y `headliners` en el 97%, pero
    `productora` solo en el 33% -- de 173 productoras extraidas, 116 no
    figuraban en el texto. Casi todas decian "Reduciendo Dano": el modelo
    dedujo la productora del CONTEXTO (es material de RD) en vez de leerla del
    cartel. No es mentira, pero tampoco es lectura, y la base RD se alimenta de
    aca: una productora equivocada es un cliente equivocado.

    Marca, NO borra. Un dato deducido puede ser el correcto y el que decide es
    quien lo cura, no este archivo. Lo que no puede pasar es que llegue a la
    base sin distinguirse de uno leido.
    """
    base = _palabras_de((ocr_texto or "") + " " + (texto_visible or ""))
    sin_respaldo, con_respaldo = [], []
    for campo in CONTRASTABLES:
        valor = datos_evento.get(campo)
        if not valor:
            continue
        texto = " ".join(valor) if isinstance(valor, list) else str(valor)
        (con_respaldo if _palabras_de(texto) & base
         else sin_respaldo).append(campo)
    out = {}
    if con_respaldo:
        out["con_respaldo"] = con_respaldo
    if sin_respaldo:
        out["sin_respaldo"] = sin_respaldo
    return out


def canonizar_tecnicas(valores):
    """Un mapa valor -> grafia canonica, decidido MIRANDO EL CORPUS.

    Una ficha sola no alcanza para saber si `fotografia` es un error o una
    palabra sin tilde: hace falta ver que en el mismo corpus hay 163
    `fotografía` y 35 `fotografia`. Por eso esto recibe TODOS los valores y no
    uno.

    Gana la variante ACENTUADA cuando existe, aunque sea minoria: en castellano
    la tilde no es una opcion de estilo, y el valor que sale de aca lo lee un
    humano. Entre variantes igual de acentuadas gana la mas frecuente. Si
    ninguna lleva tilde, tambien la mas frecuente -- ahi no hay nada que
    corregir.

    No hay lista escrita a mano: el mapa sale de los datos, asi que el dia que
    aparezca una tecnica nueva no hay que acordarse de nada.
    """
    grupos = {}
    for valor in valores:
        if not valor:
            continue
        texto = " ".join(str(valor).lower().split())
        clave = _plegar_texto(texto)
        grupos.setdefault(clave, {})
        grupos[clave][texto] = grupos[clave].get(texto, 0) + 1
    mapa = {}
    for variantes in grupos.values():
        if len(variantes) < 2:
            continue
        def _rango(par):
            texto, veces = par
            return (any(unicodedata.combining(c)
                        for c in unicodedata.normalize("NFKD", texto)), veces)
        canonica = max(variantes.items(), key=_rango)[0]
        for texto in variantes:
            if texto != canonica:
                mapa[texto] = canonica
    return mapa


def prompt_de(fuente: str, texto_autor: str = "", fecha: str = "") -> str:
    """El prompt que corresponde al corpus. Son dos trabajos distintos.

    'rd' extrae datos de material de la ONG. 'ig' (el archivo del artista)
    arma el mapa conceptual. Usar uno solo para ambos fue el defecto que hizo
    inservible la corrida del 2026-07-23.
    """
    base = PROMPT_RD if fuente == "rd" else PROMPT_ISKVW
    if not (texto_autor or fecha):
        return base
    # Lo que el ARTISTA escribio sobre su propia obra, y cuando la publico.
    # Un modelo mirando un render dice "composicion 3D abstracta"; el artista
    # escribio "Animacion 3D para @sweettoothskully, meses de ensayo y error",
    # que nombra la tecnica, el encargo, la duracion y la intencion. Eso NO
    # esta en los pixeles y ningun modelo lo recupera de ahi. Medido sobre el
    # export real: 1.013 de 1.401 fichas ig tienen texto propio y 1.124 tienen
    # fecha exacta.
    #
    # Va como CONTEXTO, no como respuesta: el modelo sigue teniendo que mirar
    # la imagen. Si copia el texto en vez de leer la obra, el campo deja de
    # medir lo que dice medir.
    extra = [chr(10) + chr(10) +
             "CONTEXTO QUE APORTA EL ARTISTA (no es la respuesta, es lo "
             "que el escribio al publicarla):"]
    if fecha:
        extra.append("Publicada el %s." % fecha)
    if texto_autor:
        extra.append('Sus palabras: "%s"' % texto_autor[:1200].replace('"', "'"))
    extra.append("Usalo para acertar la TECNICA y la idea principal, que es "
                 "donde una imagen sola engana. NO lo copies como descripcion "
                 "ni inventes lo que ahi no dice: describi lo que VES, y que "
                 "el contexto te ayude a nombrarlo bien.")
    return base + chr(10).join(extra)


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


def reconciliar_checkpoint_fallido(dir_out: Path, procesados: set) -> set:
    """Undo the legacy bug that checkpointed failed fichas as successes.

    The latest JSONL row wins, so an old failure followed by a successful retry
    stays processed. Rewriting is atomic and happens only when reconciliation
    actually changes the checkpoint.
    """
    fichas = Path(dir_out) / "fichas" / "fichas.jsonl"
    if not fichas.exists() or not procesados:
        return procesados
    ultimas: dict[str, dict] = {}
    filas = 0
    try:
        with fichas.open("r", encoding="utf-8") as fh:
            for line in fh:
                try:
                    ficha = json.loads(line)
                    clave = clave_checkpoint(ficha["fuente"], ficha["ruta_rel"])
                    ultimas[clave] = ficha
                    filas += 1
                except (KeyError, TypeError, json.JSONDecodeError):
                    continue
    except OSError:
        return procesados
    # The file used to append retries, while consumers treated every row as a
    # distinct work. Compact it atomically so every consumer sees latest-wins.
    if filas != len(ultimas):
        tmp_fichas = fichas.with_suffix(".jsonl.tmp")
        tmp_fichas.write_text(
            "".join(json.dumps(ficha, ensure_ascii=True) + "\n"
                    for ficha in ultimas.values()), encoding="utf-8")
        os.replace(tmp_fichas, fichas)
    corregidos = {
        clave for clave in procesados
        if not bool((ultimas.get(clave) or {}).get("error"))
    }
    if corregidos == procesados:
        return procesados
    p = Path(dir_out) / "procesados.txt"
    tmp = p.with_suffix(".txt.tmp")
    tmp.write_text("".join(clave + "\n" for clave in sorted(corregidos)), encoding="utf-8")
    os.replace(tmp, p)
    return corregidos


MAX_INTENTOS_FALLIDOS = 3


def _firma_entry(entry: dict) -> str:
    """Detect replacement even when copy tools preserve size and mtime."""
    digest = ""
    path = entry.get("ruta_abs")
    if path:
        try:
            with open(path, "rb") as fh:
                head = fh.read(65536)
                fh.seek(max(0, int(entry.get("bytes", 0)) - 65536))
                tail = fh.read(65536)
            digest = hashlib.sha256(head + tail).hexdigest()[:16]
        except OSError:
            pass
    return "%s:%s:%s" % (entry.get("bytes", 0), entry.get("mtime", 0), digest)


def cargar_fallos(dir_out: Path) -> dict:
    p = Path(dir_out) / "fallos.json"
    if not p.exists():
        return {}
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def guardar_fallos(dir_out: Path, fallos: dict) -> None:
    p = Path(dir_out) / "fallos.json"
    tmp = p.with_suffix(".json.tmp")
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp.write_text(json.dumps(fallos, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, p)


def registrar_fallo(fallos: dict, clave: str, entry: dict, error: str) -> dict:
    firma = _firma_entry(entry)
    previo = fallos.get(clave) if isinstance(fallos.get(clave), dict) else {}
    intentos = int(previo.get("intentos", 0)) + 1 if previo.get("firma") == firma else 1
    ahora = datetime.now(timezone.utc).isoformat()
    registro = {
        "firma": firma,
        "intentos": intentos,
        "error": str(error),
        "ultimo_intento": ahora,
        "cuarentena": intentos >= MAX_INTENTOS_FALLIDOS,
    }
    if previo.get("firma") == firma and previo.get("primer_intento"):
        registro["primer_intento"] = previo["primer_intento"]
    else:
        registro["primer_intento"] = ahora
    fallos[clave] = registro
    return registro


def esta_en_cuarentena(fallos: dict, clave: str, entry: dict) -> bool:
    registro = fallos.get(clave)
    return bool(isinstance(registro, dict)
                and registro.get("cuarentena")
                and registro.get("firma") == _firma_entry(entry))


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


def generar_contact_sheet(path_video: str, path_salida: str, timeout: int = 60):
    """Genera el contact sheet. Devuelve (ok, motivo).

    Antes devolvia solo True/False y capturaba el stderr de ffmpeg SIN LEERLO,
    asi que todo fallo terminaba escrito como `contact_sheet_fallo` a secas.
    Medido el 2026-07-31: ese fue el UNICO modo de fallo de una corrida de 127
    fichas -- 10 de 10 -- y el mensaje no decia por que ninguna vez. Un modo de
    fallo que se repite diez veces sin motivo no es un error, es un dato que
    nadie recogio."""
    duracion = ffprobe_duracion(path_video, timeout=min(timeout, 30))
    comando = construir_comando_contact_sheet(path_video, path_salida, duracion)
    try:
        r = subprocess.run(comando, capture_output=True, timeout=timeout,
                           check=False)
    except subprocess.TimeoutExpired:
        return False, "ffmpeg paso los %ds" % timeout
    except OSError as e:
        return False, "no pude ejecutar ffmpeg: %s" % e
    if Path(path_salida).exists():
        return True, ""
    err = (r.stderr or b"").decode("utf-8", "replace").strip().splitlines()
    return False, "rc=%d %s" % (r.returncode, (err[-1] if err else "sin stderr")[:160])


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


def _parsear_json_vision(texto: str, fuente: str = "rd") -> dict:
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

    # El esquema depende de la fuente, igual que el prompt: pedirle
    # 'productora' a una obra del archivo no tiene sentido, y pedirle
    # 'conceptos' a un flyer tampoco.
    for clave, default in ESQUEMA_POR_FUENTE.get(fuente, ESQUEMA_POR_FUENTE["rd"]):
        datos.setdefault(clave, default)
    if datos.get("categoria") not in CATEGORIAS_VALIDAS:
        datos["categoria"] = ""
    # El tipo del archivo del artista pasa por el mismo aro que la categoria de
    # RD: se normaliza el sinonimo y lo que no este en el vocabulario cerrado se
    # vacia, en vez de quedar como un valor nuevo que despues hay que descubrir
    # contando. Un modelo que contesta "dibujo digital" esta contestando la
    # tecnica, y la tecnica ya tiene su campo.
    # La TECNICA es texto libre y por eso deriva. Medido el 2026-08-01 sobre las
    # 1.401 fichas ig: 54 valores crudos distintos que son 48 conceptos, con 5
    # grupos escritos de mas de una forma y ~330 fichas involucradas --
    # `fotografia`(35) vs `fotografía`(163), `Ilustración digital`(5) vs
    # `ilustración digital`(103) vs `ilustracion digital`(9).
    #
    # Aca se arregla SOLO lo que se puede decidir mirando un valor solo:
    # mayusculas y espacios. La tilde NO: para saber si `fotografia` es un
    # error de `fotografía` hay que ver el corpus entero, y decidirlo desde una
    # ficha suelta seria inventar. Eso lo hace `canonizar_tecnicas()`, que ve
    # todas. Y la tilde NUNCA se borra: es un valor que lee un humano.
    if datos.get("tecnica"):
        datos["tecnica"] = " ".join(str(datos["tecnica"]).lower().split())

    if "tipo_obra" in datos:
        t = str(datos.get("tipo_obra") or "").strip().lower()
        t = SINONIMOS_TIPO_OBRA.get(t, t)
        datos["tipo_obra"] = t if t in TIPOS_OBRA_VALIDOS else ""
        # Una sola pregunta, un solo campo. Medido el 2026-07-27: `categoria`
        # decia 354 obras y `vision.tipo_obra` decia 503 sobre el mismo corpus,
        # porque los dos contestaban lo mismo y derivaban. Para el archivo del
        # artista manda el tipo, que es el que el prompt pide.
        if datos["tipo_obra"] and not datos.get("categoria"):
            datos["categoria"] = (datos["tipo_obra"]
                                  if datos["tipo_obra"] in CATEGORIAS_VALIDAS
                                  else "obra")
    return datos


def vision_imagen(path: str, timeout: int = 120, fuente: str = "rd",
                  texto_autor: str = "", fecha: str = "") -> dict:
    """Manda `path` (imagen ya lista, o contact sheet de video) a ollama
    y devuelve el JSON de vision parseado de forma tolerante. Cualquier
    fallo de lectura/red/parseo devuelve {"error": ...} sin lanzar
    excepcion, para que un archivo puntual nunca tumbe el loop."""
    imagen_b64 = _imagen_a_b64(path)
    if imagen_b64 is None:
        return {"error": "no_se_pudo_leer_imagen"}

    # Which engine reads the image. `ollama` by default: without the variable
    # the behaviour is byte for byte today's, so a corpus run cannot be changed
    # by accident. `watsonx` is the paid one that actually sees -- probed
    # 2026-07-31 before this line existed (tools/watsonx_vision_smoke.py).
    #
    # The resize, the prompt and the tolerant parse are REUSED, not rewritten:
    # only the transport changes. If watsonx fails for any reason it falls back
    # to ollama, and the ficha's `medicion.vision` says who answered -- a
    # corpus run must not die because the cloud did.
    if os.environ.get("PERCEPCION_VISION", "ollama").lower() == "watsonx":
        try:
            # Se busca por el sys.path normal PRIMERO. La version anterior
            # insertaba `~/research` en la posicion 0, o sea una ruta absoluta
            # del home ganandole a todo: imposible correr una copia parchada
            # para probar, e imposible fuera de la caja. El home queda como
            # ULTIMO recurso, que es lo que de verdad es.
            try:
                from research_lib import watsonx_vision
            except ImportError:
                sys.path.append(os.path.expanduser("~/research"))
                from research_lib import watsonx_vision
            texto = watsonx_vision(prompt_de(fuente, texto_autor, fecha),
                                   imagen_b64,
                                   timeout=timeout)
            d = _parsear_json_vision(texto, fuente)
            if not d.get("error"):
                d["_motor"] = "watsonx"
                return d
        except Exception as exc:                 # noqa: BLE001 - cae a ollama
            print("aviso: watsonx no pudo, caigo a ollama (%s)" % str(exc)[:120],
                  flush=True)

    payload = json.dumps({
        "model": OLLAMA_MODEL,
        "prompt": prompt_de(fuente, texto_autor, fecha),
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
    d = _parsear_json_vision(texto_modelo, fuente)
    # Ollama tambien se firma. Si solo firmara watsonx, la AUSENCIA de firma
    # significaria dos cosas a la vez -- "respondio ollama" y "nadie atribuyo"
    # -- y el campo dejaria de servir para lo unico que existe.
    d["_motor"] = "ollama"
    return d


# ---------------------------------------------------------------------------
# Paso 6: ficha (schema UNICO)
# ---------------------------------------------------------------------------

ESTADOS_MEDICION = ("medido", "vacio", "no_intentado", "fallo")

# Que mediciones aplican a cada tipo de archivo. Es la tabla que convierte un
# `""` en una respuesta: si el tipo no esta aca, la medicion NO se intento.
APLICA = {
    "imagen": ("ocr", "vision"),
    "video": ("vision",),
    "pdf": ("ocr", "vision"),
    "otro": (),
}


def estado_medicion(aplica: bool, valor, error=None) -> dict:
    """Say WHAT was measured and what was not, instead of leaving a bare `""`.

    Measured 2026-07-31 over the 3.138 real fichas: `ocr_texto` empty in 76%,
    `datos_evento` empty in 69%. That emptiness meant three different things at
    once -- the OCR was never run for this file type, it ran and the image
    carried no text, or it blew up -- and nothing downstream could tell them
    apart. A skin cannot decide what to do with a datum whose absence has no
    reason, and neither can a weak model. So the reason travels with the datum:

        no_intentado  esta medicion no aplica a este tipo de archivo
        fallo         se intento y reventó (el motivo va en `detalle`)
        vacio         se midio de verdad y no habia nada
        medido        se midio y hay dato

    Pure on purpose: it takes no path and runs no model, so it is testable off
    the box and a change in it cannot break a perception run.
    """
    if not aplica:
        return {"estado": "no_intentado", "detalle": "no aplica a este tipo"}
    if error:
        return {"estado": "fallo", "detalle": str(error)[:200]}
    vacio = valor in (None, "", [], {}) or (
        isinstance(valor, str) and not valor.strip())
    if vacio:
        return {"estado": "vacio", "detalle": "se midio y no habia dato"}
    tam = len(valor) if hasattr(valor, "__len__") else 1
    return {"estado": "medido", "detalle": "%d" % tam}


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


def construir_ficha(entry: dict, dir_tmp: Path, timeout_archivo: int,
                    meta_ig: dict | None = None) -> dict:
    """Construye la ficha de schema UNICO para un item de trabajo.

    Nunca lanza: cualquier excepcion durante el analisis queda como
    "error" en la ficha y el resto de los campos con sus defaults, para
    que el loop de `correr()` pueda seguir con el resto de los archivos.
    """
    fuente = entry["fuente"]
    ruta_rel = entry["ruta_rel"]
    # Lo que el artista escribio y cuando lo publico, si el export lo trae.
    # Sale de `tools/ig_metadatos.py`; la clave es el nombre del archivo.
    _meta = (meta_ig or {}).get(os.path.basename(ruta_rel)) or {}
    texto_autor = _meta.get("texto") or ""
    fecha_publicacion = _meta.get("fecha") or ""
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
            vision = vision_imagen(ruta_abs, timeout=timeout_archivo, fuente=fuente,
                                   texto_autor=texto_autor, fecha=fecha_publicacion)

        elif tipo == "video":
            sheet_path = Path(dir_tmp) / ("sheet_%s.jpg" % id_ficha(fuente, ruta_rel))
            ok, motivo_sheet = generar_contact_sheet(
                ruta_abs, str(sheet_path), timeout=timeout_archivo)
            if ok:
                vision = vision_imagen(str(sheet_path), timeout=timeout_archivo,
                                       fuente=fuente, texto_autor=texto_autor,
                                       fecha=fecha_publicacion)
                try:
                    sheet_path.unlink(missing_ok=True)
                except OSError:
                    pass
            else:
                # El motivo VIAJA. Diez fallos identicos sin causa fueron el
                # unico modo de fallo de la corrida del 2026-07-31.
                vision = {"error": "contact_sheet_fallo: " + motivo_sheet}

        elif tipo == "pdf":
            ocr_texto = ocr_pdftotext_primera_pagina(ruta_abs, timeout=timeout_archivo)
            imagen_pdf = pdf_primera_pagina_a_imagen(ruta_abs, dir_tmp, timeout=timeout_archivo)
            if imagen_pdf:
                vision = vision_imagen(imagen_pdf, timeout=timeout_archivo, fuente=fuente)
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

    claves_vision = CLAVES_VISION.get(fuente, CLAVES_VISION["rd"])
    vision_final = {k: vision.get(k) for k in claves_vision if vision.get(k)}
    # Este filtro tiene DOS canales silenciosos y los dos costaron una hora el
    # 2026-07-31. `CLAVES_VISION` es una lista blanca escrita a mano: una clave
    # que el modelo devuelve y no esta declarada se cae sin decir nada -- asi
    # se perdio `_motor` y el conteo culpo al transporte, que funcionaba. Y
    # `if vision.get(k)` bota tambien los valores VACIOS, asi que una medicion
    # legitimamente vacia y una clave que nunca llego quedan identicas.
    # No se cambia que se guarda: se cambia que ahora se SABE cual es cual.
    # `_ignoradas` son las claves que NO van al bloque `vision` pero SI se
    # usan: `datos_evento` se arma con CLAVES_EVENTO y `categoria` sale un
    # poco mas abajo, las dos leyendo este mismo dict. Sin restarlas, el aviso
    # anunciaba que se descartaban seis claves que en realidad se guardan --
    # medido en la sonda RD del 2026-08-01, 7 de 10 archivos avisando de un
    # descarte que no ocurre. Una falsa alarma es el defecto espejo del
    # descarte callado: manda al operador a perseguir un fantasma, y la
    # proxima alarma verdadera ya no se cree.
    _ignoradas = {"error", "_motor", "categoria"} | set(CLAVES_EVENTO)
    desconocidas = sorted(set(vision) - set(claves_vision) - _ignoradas)
    vacias = sorted(k for k in claves_vision
                    if k in vision and not vision.get(k))
    ausentes = sorted(k for k in claves_vision if k not in vision)
    if desconocidas:
        print("aviso: %s devolvio claves no declaradas y se descartan: %s"
              % (id_ficha(fuente, ruta_rel), ", ".join(desconocidas)),
              flush=True)
    # Compatibilidad: las fichas viejas y el corpus esperan 'descripcion'.
    if "descripcion" not in vision_final and vision.get("descripcion"):
        vision_final["descripcion"] = vision["descripcion"]
    datos_evento = (
        {k: (vision.get(k) or ([] if k in ("headliners", "handles") else ""))
         for k in CLAVES_EVENTO}
        if fuente == "rd" else {}
    )
    categoria = vision.get("categoria", "") or ""

    # Cada medicion declara su estado. Los campos de siempre NO se tocan: el
    # corpus, el micelio y el contrato del archivo los leen tal cual, y romper
    # eso para agregar honestidad seria cambiar un defecto por otro.
    aplica = APLICA.get(tipo, ())
    # QUIEN respondio la vision. Va en `medicion` y no dentro de `vision`
    # porque `vision_final` se filtra a CLAVES_VISION y cualquier clave extra
    # se cae en silencio -- medido el 2026-07-31: una corrida entera con
    # watsonx reporto `_motor: 0` en las 119 fichas y parecia que la ruta nueva
    # nunca se habia tomado. El transporte estaba bien; el instrumento miraba
    # un campo que el propio constructor descartaba.
    # SIN default. `or "ollama"` rellenaba la ausencia con un valor plausible,
    # que es el mismo defecto que este campo existe para matar: el proximo que
    # cuente motores contaria fantasmas. Si nadie atribuyo, lo dice.
    motor = (vision or {}).get("_motor") or "sin_atribucion"
    medicion = {
        "ocr": estado_medicion("ocr" in aplica, ocr_texto, error),
        "vision": estado_medicion("vision" in aplica, vision_final, error),
        "datos_evento": estado_medicion(
            fuente == "rd" and "vision" in aplica,
            [v for v in datos_evento.values() if v] if datos_evento else [],
            error),
    }
    medicion["vision"]["motor"] = motor
    if _meta:
        # El contexto CAMBIA la respuesta del modelo, asi que tiene que quedar
        # registrado: dos fichas con el mismo motor y distinto contexto no son
        # comparables, y quien mida cobertura despues tiene que poder separarlas.
        medicion["metadatos"] = {
            "fuente": "export_ig",
            "con_texto_autor": bool(texto_autor),
            "con_fecha": bool(fecha_publicacion),
            "en_el_prompt": bool(texto_autor or fecha_publicacion),
        }
        if _meta.get("encoding_sospechoso"):
            medicion["metadatos"]["encoding_sospechoso"] = True
    else:
        medicion["metadatos"] = {"fuente": "sin_metadatos",
                                 "con_texto_autor": False, "con_fecha": False,
                                 "en_el_prompt": False}
    if fuente == "rd" and datos_evento:
        medicion["datos_evento"].update(
            respaldo_evento(datos_evento, ocr_texto,
                            (vision_final or {}).get("texto_visible")))
    if desconocidas:
        medicion["vision"]["claves_desconocidas"] = desconocidas
    if vacias:
        medicion["vision"]["claves_vacias"] = vacias
    if ausentes:
        medicion["vision"]["claves_ausentes"] = ausentes

    return {
        "id": id_ficha(fuente, ruta_rel),
        "fuente": fuente,
        "ruta_rel": ruta_rel,
        "tipo": tipo,
        "categoria": categoria,
        "bytes": entry.get("bytes", 0),
        "mtime": _mtime_a_fecha(entry.get("mtime")),
        # Lo que el artista escribio y cuando lo publico. NO sale de ningun
        # modelo: sale del export, y por eso vale mas que cualquier
        # descripcion generada. Vacio cuando el export no lo trae, sin
        # rellenar: 277 de las 1.401 fichas ig no casan con ninguna entrada.
        "fecha_publicacion": fecha_publicacion,
        "texto_autor": texto_autor[:2000],
        "ocr_texto": (ocr_texto or "")[:1500],
        "vision": vision_final,
        "datos_evento": datos_evento,
        "medicion": medicion,
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
           solo_fuente: str | None = None,
           limite: int | None = None,
           meta_ig: str | None = None) -> int:
    """Corre la percepcion sobre ambos corpus. Retorna el codigo de salida:

    0 = termino todo el trabajo pendiente.
    3 = auto-pausa por errores_seguidos >= max_errores_seguidos.
    """
    dir_out = Path(dir_out)
    dir_fichas = dir_out / "fichas"
    dir_tmp = dir_out / "_tmp"
    dir_out.mkdir(parents=True, exist_ok=True)
    # `_tmp` se crea UNA vez, aca, y no en cada rama que escribe adentro.
    # Lo creaban `preparar_imagen_para_ocr` y `pdf_primera_pagina_a_imagen`;
    # la rama de VIDEO no, y ffmpeg contra un directorio inexistente responde
    # `Conversion failed!` -- generico, sin decir que falta el directorio.
    # Medido el 2026-07-31: ese fue el UNICO modo de fallo de la corrida sobre
    # el corpus del artista, 10 de 10 y despues 8 de 8, todos videos de
    # `archived_posts/`, que es donde el recorrido empieza. Cuando el primer
    # archivo de un corpus es un video, el contact sheet no puede escribir
    # nunca. Tres funciones hacian lo mismo y una se olvido: la respuesta no es
    # agregar el cuarto mkdir, es que ninguna tenga que acordarse.
    dir_tmp.mkdir(parents=True, exist_ok=True)

    mapa_meta = {}
    if meta_ig:
        # Si se pidio y no se puede leer, se ABORTA. Seguir sin el mapa daria
        # una corrida completa, plausible y sin el dato que la justificaba, y
        # nadie lo notaria hasta contar fichas horas despues.
        try:
            mapa_meta = json.loads(Path(meta_ig).read_text(encoding="utf-8"))
            mapa_meta = mapa_meta.get("medios") or mapa_meta
        except (OSError, ValueError) as exc:
            print("ERROR: no pude leer --meta-ig %s (%s)" % (meta_ig, exc),
                  file=sys.stderr)
            return 2
        con_texto = sum(1 for v in mapa_meta.values() if v.get("texto"))
        print("META: %d archivos con metadatos del export, %d con texto del "
              "artista" % (len(mapa_meta), con_texto), flush=True)

    trabajo = construir_trabajo(raiz_rd, raiz_ig, solo_fuente=solo_fuente)
    # `--limite` existe para SONDEAR un corpus sin correrlo entero: el usuario
    # pidio 10 flyers de RD, no los miles que hay. El recorte se dice en la
    # salida -- un total mas chico sin explicacion se lee como "eso era todo el
    # corpus", y el que compare cobertura despues estaria dividiendo por el
    # numero equivocado.
    if limite is not None and limite > 0 and len(trabajo) > limite:
        print("LIMITE: sonda de %d de %d archivos (el resto NO se toca)"
              % (limite, len(trabajo)), flush=True)
        trabajo = trabajo[:limite]
    total_trabajo = len(trabajo)

    procesados_set = reconciliar_checkpoint_fallido(
        dir_out, cargar_procesados(dir_out))
    fallos = cargar_fallos(dir_out)

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
            "fallos_reintentables": sum(
                1 for value in fallos.values()
                if isinstance(value, dict) and not value.get("cuarentena")),
            "cuarentena": sum(
                1 for value in fallos.values()
                if isinstance(value, dict) and value.get("cuarentena")),
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
        if esta_en_cuarentena(fallos, clave, entry):
            continue

        ficha = construir_ficha(entry, dir_tmp, timeout_archivo,
                                meta_ig=mapa_meta)
        tiempos.append(ficha.get("seg_proceso") or 0.0)
        if len(tiempos) > 200:
            del tiempos[:-200]

        escribir_ficha(dir_fichas, ficha)

        if ficha.get("error"):
            errores_totales += 1
            errores_seguidos += 1
            registrar_fallo(fallos, clave, entry, ficha["error"])
            guardar_fallos(dir_out, fallos)
            ultimos_errores.append({
                "ruta_rel": entry["ruta_rel"],
                "error": ficha["error"],
            })
            ultimos_errores = ultimos_errores[-MAX_ULTIMOS_ERRORES:]
        else:
            errores_seguidos = 0
            fallos.pop(clave, None)
            guardar_fallos(dir_out, fallos)
            procesados_set.add(clave)
            marcar_procesado(dir_out, clave)
            procesados_count += 1
            por_fuente[entry["fuente"]] = por_fuente.get(entry["fuente"], 0) + 1

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

    if cmd == "reconciliar":
        out = _obtener_flag(resto, "--out")
        if not out:
            print("falta --out", file=sys.stderr)
            return 2
        antes = cargar_procesados(Path(out))
        despues = reconciliar_checkpoint_fallido(Path(out), antes)
        print(json.dumps({"antes": len(antes), "despues": len(despues)}, ensure_ascii=True))
        return 0

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

        meta_ig = _obtener_flag(resto, "--meta-ig")
        limite_txt = _obtener_flag(resto, "--limite")
        try:
            limite = int(limite_txt) if limite_txt else None
        except ValueError:
            print("ERROR: --limite debe ser un entero", file=sys.stderr)
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
                limite=limite,
                meta_ig=meta_ig,
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
