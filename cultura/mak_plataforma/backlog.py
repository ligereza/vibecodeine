#!/usr/bin/env python3
"""backlog.py -- sistema generativo de backlog para MAK.

Parsea secciones "LAGUNAS DE INFORMACION" de informes y las convierte en
entradas de backlog deduplicadas y ranqueadas. Enforza las reglas de poda:
  1. Max N preguntas por informe
  2. Profundidad de linaje <= 3
  3. Curador: descarta redundantes/triviales
  4. Slug dedup: una pregunta cuyo slug ya existe como informe o en el
     backlog NO se encola de nuevo (2026-07-31; causa medida: 40 de 50
     informes compartian un prefijo -- la misma pregunta respondida 40 veces,
     porque cosechar nunca miraba lo ya respondido)
"""
import json
import collections
import os
import re
import sys
import unicodedata
from datetime import datetime
from hashlib import sha1


PROVENANCE_TYPES = (
    "semilla_sistema", "informe", "intencion_usuario", "tarea_derivada",
    "externo", "desconocido",
)
PROVENANCE_AUTHORITIES = (
    "sistema", "usuario", "fuente_primaria", "modelo", "inferida",
    "desconocida",
)
LEGACY_SYSTEM_SEED_IDS = frozenset({
    "bl-60e3e922", "bl-473d8f25", "bl-ddd9491d", "bl-8e293c3b",
    "bl-ae2937c2", "bl-52670965", "bl-e9f1deb4", "bl-d0e22120",
})

# Report files are named STAMP-slug.md by research.py, with the slug minted by
# research_lib.slug(). Deduplicating against those files REQUIRES the exact
# same function -- a second slug formation is how the 1004-pieces/0-positions
# trap happened (two id formations that never met). Two layouts share this
# file: the repo (cultura/mak_plataforma + cultura/mak_research) and the box
# (~/plataforma + ~/research); do not depend on the caller's sys.path.
_DIR = os.path.dirname(os.path.abspath(__file__))
for _cand in (os.path.join(_DIR, "..", "mak_research"),
              os.path.join(_DIR, "..", "research")):
    if os.path.isdir(_cand) and _cand not in sys.path:
        sys.path.insert(0, _cand)
try:
    from research_lib import slug
except ImportError:  # without research_lib the hash dedup still applies
    slug = None


def _norm(texto):
    """Normaliza para dedup: lowercase, colapsa whitespace, quita accents."""
    # Quitar accents
    nfd = unicodedata.normalize('NFD', texto)
    sin_accents = ''.join(c for c in nfd if unicodedata.category(c) != 'Mn')
    # Lowercase y colapsar whitespace
    normalizado = re.sub(r'\s+', ' ', sin_accents.lower().strip())
    return normalizado


def clasificar_procedencia(entrada):
    """Classify memory origin without treating absence as user intent."""
    if not isinstance(entrada, dict):
        return {"origen_tipo": "desconocido", "autoridad": "desconocida",
                "activacion": "none"}
    tipo = entrada.get("origen_tipo")
    autoridad = entrada.get("autoridad")
    if tipo not in PROVENANCE_TYPES:
        if entrada.get("id") in LEGACY_SYSTEM_SEED_IDS:
            tipo, autoridad = "semilla_sistema", "sistema"
        elif entrada.get("origen_informe"):
            tipo, autoridad = "informe", "modelo"
        elif entrada.get("linaje"):
            tipo, autoridad = "tarea_derivada", "inferida"
        else:
            tipo, autoridad = "desconocido", "desconocida"
    if autoridad not in PROVENANCE_AUTHORITIES:
        autoridad = {
            "semilla_sistema": "sistema",
            "informe": "modelo",
            "tarea_derivada": "inferida",
            "intencion_usuario": "usuario",
            "externo": "fuente_primaria",
        }.get(tipo, "desconocida")
    activacion = entrada.get("activacion") or (
        "manual" if tipo == "intencion_usuario" else
        "backlog" if tipo in ("informe", "tarea_derivada") else "none"
    )
    return {"origen_tipo": tipo, "autoridad": autoridad,
            "activacion": activacion}


def _hash(texto):
    """SHA1 hex del texto normalizado, primeros 12 caracteres."""
    norma = _norm(texto)
    h = sha1(norma.encode('utf-8')).hexdigest()
    return h[:12]


def parsear_lagunas(texto):
    """Extrae preguntas de la seccion 'LAGUNAS DE INFORMACION'.

    Busca encabezado "## LAGUNAS DE INFORMACION" o linea con "LAGUNAS DE INFORMACION".
    Las bullets comienzan con "-", "*" o "N.".
    La seccion termina en el proximo header "#" o EOF.

    Args:
        texto: contenido del informe (str)

    Returns:
        list[str]: preguntas sin bullets, max 300 chars c/u, sin vacias
    """
    lineas = texto.split('\n')

    # Buscar el inicio de la seccion
    inicio_idx = None
    for i, linea in enumerate(lineas):
        if 'LAGUNAS DE INFORMACION' in linea:
            inicio_idx = i + 1  # Comienza en la linea siguiente
            break

    if inicio_idx is None:
        return []

    # Buscar el fin (proximo header o EOF)
    fin_idx = len(lineas)
    for i in range(inicio_idx, len(lineas)):
        if lineas[i].startswith('#'):
            fin_idx = i
            break

    # Extraer bullets
    preguntas = []
    for linea in lineas[inicio_idx:fin_idx]:
        linea = linea.strip()
        if not linea:
            continue

        # Verificar si es bullet: "- ", "* " o "N. "
        match = re.match(r'^[-*]|\d+\.\s', linea)
        if match:
            # Remover el bullet
            pregunta = re.sub(r'^[-*]\s+|\d+\.\s+', '', linea).strip()
            pregunta = _limpiar_render(pregunta)
            if pregunta:
                # Capear a 300 chars
                pregunta = pregunta[:300]
                preguntas.append(pregunta)

    return preguntas


def _limpiar_render(linea):
    """Saca el MARCADO de una vinneta y devuelve la pregunta que traia adentro.

    Medido el 2026-08-01: el organismo estaba investigando un tema llamado
    literalmente `**Detalles del Evento:** No se encontraron detalles
    especificos`, asteriscos incluidos, y produjo un informe de 10 minutos por
    cron con ese titulo. La pregunta util estaba ahi -- llego envuelta en el
    formato con el que se habia renderizado el informe anterior.

    Se midio antes de escribir esto, porque la primera lectura fue equivocada
    dos veces: el backlog real tiene 167 preguntas que agrupan en 150 grupos
    distintos, asi que NO era redundancia (32 repetidas, y varias de esas son
    eventos distintos), y las vinnetas que empiezan por "La falta de..."
    producen preguntas de investigacion legitimas -- filtrarlas por su forma
    habria matado temas buenos. Lo unico defectuoso era el marcado.

    Solo se quita FORMATO. Ni una palabra de la pregunta se descarta: si
    despues de limpiar no queda nada, es que la linea era solo marcado.
    """
    t = (linea or "").strip()
    # `**Titulo:** cuerpo` -> el titulo es la etiqueta de la vinneta y el
    # cuerpo es la pregunta. Si no hay cuerpo, el titulo ES la pregunta.
    m = re.match(r'^\*\*(.+?):?\*\*:?\s*(.*)$', t, re.S)
    if m:
        titulo, cuerpo = m.group(1).strip(), m.group(2).strip()
        t = cuerpo or titulo
    # Enfasis suelto, comillas de codigo y encabezados que se colaron.
    t = re.sub(r'\*\*|__|`|^#+\s*', '', t).strip()
    # Una linea de tabla o un separador no es una pregunta.
    if t.startswith('|') or set(t) <= set('-|: '):
        return ''
    return t.strip()


def preguntas_del_informe(dir_path, filename, contenido):
    """Lo que un informe deja abierto. EL DATO PRIMERO, la prosa despues.

    `research.py` escribe un `.json` al lado de cada `.md`, y ese json es la
    fuente de verdad -- el propio codigo lo dice: "`report` es un RENDER de lo
    de abajo". Desde el 2026-08-01 trae `preguntas_abiertas`, pedidas al modelo
    como array y no incrustadas en el texto.

    Por que dejo de leerse la prosa: `parsear_lagunas` buscaba con una regex la
    seccion "LAGUNAS DE INFORMACION" del Markdown, asi que el loop dependia de
    como se VEIA el informe. Costo dos cosas el mismo dia: un tema entro a la
    cola llamado literalmente "**Detalles del Evento:** No se encontraron
    detalles especificos" -- asteriscos del render incluidos -- y produjo su
    propio informe por cron; y al cambiar el formato esa manana la seccion
    dejo de emitirse, con lo cual el parser habria devuelto vacio y el backlog
    se habria secado SIN QUE NADIE SE ENTERE. Un loop que se apaga en silencio
    es peor que uno que falla.

    El fallback NO se saca: hay cientos de informes viejos con la seccion
    escrita y ese material sigue siendo alimento valido. Tres estados, y son
    distintos entre si:
      - json con `preguntas_abiertas` -> se usa, aunque sea []. Lista vacia
        significa "este informe no dejo nada abierto", que es una respuesta.
      - json sin la clave, o sin json -> informe viejo: se parsea la prosa.
      - json con `preguntas_abiertas_error` -> no se pudo preguntar; tambien
        se parsea la prosa, porque ausencia no es vacio.
    """
    ruta_json = os.path.join(dir_path, filename[:-3] + '.json')
    try:
        with open(ruta_json, 'r', encoding='utf-8') as f:
            doc = json.load(f)
    except (OSError, ValueError):
        return parsear_lagunas(contenido)
    if isinstance(doc, dict) and isinstance(doc.get('preguntas_abiertas'), list):
        return [q for q in doc['preguntas_abiertas'] if isinstance(q, str) and q.strip()]
    return parsear_lagunas(contenido)


_STAMP_RE = re.compile(r'^\d{8}-\d{6}-')

# Una pregunta derivada no puede convertir una entidad nombrada por el modelo
# en un hecho.  El filtro es deliberadamente conservador: solo bloquea cuando
# el propio expediente repite que no hay evidencia y ninguna fuente consultada
# identifica a la entidad.  No intenta resolver personas con regex.
_NOMBRE_COMPUESTO_RE = re.compile(
    r"\b([A-ZÁÉÍÓÚÑ][\wÁÉÍÓÚÑáéíóúñ'-]*\s+[A-ZÁÉÍÓÚÑ][\wÁÉÍÓÚÑáéíóúñ'-]*)\b"
)
_NEGACION_ENTIDAD_RE = re.compile(
    r"(?:no\s+(?:se\s+)?(?:encontr[oó]|menciona|identific[oó]|proporciona)|"
    r"sin\s+(?:informaci[oó]n|evidencia)|informaci[oó]n\s+limitada|"
    r"posible\s+falta\s+de\s+presencia)",
    re.IGNORECASE,
)
_EVIDENCIA_POSITIVA_RE = re.compile(
    r"(?:organiza(?:do|da|dor)|universidad|instituci[oó]n|fundaci[oó]n|"
    r"obra[s]?\s+creada[s]?|artista\s+(?:reconocid|documentad))",
    re.IGNORECASE,
)


def _entidades_compuestas(texto):
    """Extrae candidatos nominales sin afirmar que sean entidades reales."""
    return {m.group(1).strip() for m in _NOMBRE_COMPUESTO_RE.finditer(texto or '')}


def validar_pregunta_derivada(pregunta, documento=None):
    """Decide si una pregunta puede volver a alimentar el backlog.

    Devuelve ``(True, '')`` o ``(False, razon)``.  Si el expediente muestra
    que un nombre compuesto no aparece en títulos/URLs de las fuentes y además
    declara que no encontró información sobre él, se bloquea la propagación.
    La pregunta queda registrada en el estado de cosecha, no se borra.
    """
    if not isinstance(documento, dict):
        return True, ''

    entidades = _entidades_compuestas(pregunta)
    if not entidades:
        return True, ''

    hallazgos = documento.get('hallazgos')
    if not isinstance(hallazgos, list):
        hallazgos = documento.get('findings')
    if not isinstance(hallazgos, list):
        return True, ''

    etiquetas_fuente = []
    cuerpo_evidencia = []
    for hallazgo in hallazgos:
        if not isinstance(hallazgo, dict):
            continue
        for clave in ('titulo', 'title', 'fuente', 'url'):
            valor = hallazgo.get(clave)
            if isinstance(valor, str):
                etiquetas_fuente.append(valor)
        for clave in ('contenido', 'content', 'analysis'):
            valor = hallazgo.get(clave)
            if isinstance(valor, (str, dict, list)):
                cuerpo_evidencia.append(json.dumps(valor, ensure_ascii=False)
                                        if not isinstance(valor, str) else valor)

    etiquetas = _norm(' '.join(etiquetas_fuente))
    cuerpo = ' '.join(cuerpo_evidencia)
    for entidad in entidades:
        # Las siglas de eventos/marcas no son personas desconocidas. El caso
        # `SFERA Experience` debe seguir siendo investigable como evento.
        if any(palabra.isupper() for palabra in entidad.split()):
            continue
        if _norm(entidad) in etiquetas:
            continue
        posiciones = [m.start() for m in re.finditer(
            re.escape(entidad), cuerpo, re.IGNORECASE)]
        ventanas = [cuerpo[max(0, pos - 140):pos + len(entidad) + 180]
                    for pos in posiciones]
        if (posiciones and any(_NEGACION_ENTIDAD_RE.search(ventana)
                               and not _EVIDENCIA_POSITIVA_RE.search(ventana)
                               for ventana in ventanas)):
            return False, 'entidad_no_verificada:%s' % entidad
    return True, ''


def _slug_de_informe(filename):
    """Slug de un archivo de informe: research.py los nombra STAMP-slug.md."""
    base = filename[:-3] if filename.endswith('.md') else filename
    return _STAMP_RE.sub('', base)


def slugs_ocupados(informes_dirs, entradas):
    """Slugs ya 'tomados': uno por informe existente (el sistema YA respondio
    esa pregunta) y uno por entrada del backlog en cualquier estado (ya esta
    encolada, en curso, respondida o descartada). Una pregunta cuyo slug esta
    aca no debe encolarse de nuevo.

    Args:
        informes_dirs: list[str] de directorios con informes *.md
        entradas: list[dict] del backlog actual

    Returns:
        set[str]: slugs ocupados (vacio si research_lib.slug no esta)
    """
    if slug is None:
        return set()
    tomados = set()
    for e in entradas:
        pregunta = e.get('pregunta')
        if pregunta:
            tomados.add(slug(pregunta))
    for dir_path in informes_dirs:
        try:
            nombres = os.listdir(dir_path)
        except OSError:
            continue
        for filename in nombres:
            if filename.endswith('.md'):
                tomados.add(_slug_de_informe(filename))
    return tomados


def cargar(backlog_path):
    """Lee jsonl (un JSON por linea), salta lineas corruptas silenciosamente.

    Args:
        backlog_path: ruta del archivo jsonl

    Returns:
        list[dict]: entradas del backlog
    """
    entradas = []
    try:
        with open(backlog_path, 'r', encoding='utf-8') as f:
            for linea in f:
                linea = linea.strip()
                if not linea:
                    continue
                try:
                    entrada = json.loads(linea)
                    entradas.append(entrada)
                except (ValueError, json.JSONDecodeError):
                    # Salta lineas corruptas silenciosamente
                    pass
    except OSError:
        pass

    return entradas


def auditar_memoria(informes_dirs, backlog_path):
    """Mide salud del backlog sin modificar memoria ni producir prosa.

    El resultado sirve para que MAK decida si debe revisar, reparar o
    investigar. No revive ni descarta entradas.
    """
    if not isinstance(informes_dirs, list):
        informes_dirs = [informes_dirs]
    entradas = cargar(backlog_path)
    estado = collections.Counter(e.get('estado', 'sin_estado') for e in entradas)
    ids = [e.get('id') for e in entradas if e.get('id')]
    hashes = [_hash(e.get('pregunta', '')) for e in entradas if e.get('pregunta')]
    slugs = [slug(e.get('pregunta', '')) for e in entradas
             if e.get('pregunta') and slug is not None]
    nombres = {}
    for directorio in informes_dirs:
        try:
            for nombre in os.listdir(directorio):
                if nombre.endswith('.md'):
                    nombres.setdefault(nombre, directorio)
        except OSError:
            continue

    origenes_faltantes = []
    origenes_historicos_ausentes = []
    procedencia = collections.Counter()
    semillas_sistema = []
    intenciones_usuario = []
    fuentes_desconocidas = []
    entidades_bloqueadas = []
    for entrada in entradas:
        clasificacion = clasificar_procedencia(entrada)
        tipo = clasificacion["origen_tipo"]
        procedencia[tipo] += 1
        if tipo == "semilla_sistema":
            semillas_sistema.append(entrada.get('id'))
        elif tipo == "intencion_usuario":
            intenciones_usuario.append(entrada.get('id'))
        elif tipo == "desconocido":
            fuentes_desconocidas.append(entrada.get('id'))
        origen = entrada.get('origen_informe', '')
        directorio = nombres.get(origen)
        if not directorio:
            if tipo != "semilla_sistema":
                origenes_faltantes.append(entrada.get('id'))
                if entrada.get('origen_informe'):
                    origenes_historicos_ausentes.append(entrada.get('id'))
            continue
        documento = None
        try:
            with open(os.path.join(directorio, origen[:-3] + '.json'),
                      'r', encoding='utf-8') as f:
                documento = json.load(f)
        except (OSError, ValueError, json.JSONDecodeError):
            pass
        valida, razon = validar_pregunta_derivada(
            entrada.get('pregunta', ''), documento)
        if not valida:
            entidades_bloqueadas.append({
                'id': entrada.get('id'),
                'razon': razon,
                'estado': entrada.get('estado'),
            })

    def duplicados(valores):
        conteo = collections.Counter(v for v in valores if v)
        return sorted(k for k, n in conteo.items() if n > 1)

    return {
        'entradas': len(entradas),
        'estados': dict(sorted(estado.items())),
        'ids_duplicados': duplicados(ids),
        'preguntas_duplicadas': duplicados(hashes),
        'slugs_duplicados': duplicados(slugs),
        'origenes_faltantes': origenes_faltantes,
        'origenes_historicos_ausentes': origenes_historicos_ausentes,
        'procedencia': dict(sorted(procedencia.items())),
        'semillas_sistema': semillas_sistema,
        'intenciones_usuario': intenciones_usuario,
        'fuentes_desconocidas': fuentes_desconocidas,
        'entidades_bloqueadas': entidades_bloqueadas,
        'bloquea_produccion': bool(
            fuentes_desconocidas or entidades_bloqueadas or duplicados(slugs)
        ),
        'accion': ('revisar_memoria' if (origenes_faltantes or
                   fuentes_desconocidas or entidades_bloqueadas or
                   duplicados(slugs)) else 'sin_huecos'),
    }


def guardar_append(backlog_path, entradas):
    """Append entradas como jsonl, crea el directorio padre si no existe.

    Args:
        backlog_path: ruta del archivo jsonl
        entradas: list[dict] a agregar
    """
    try:
        # Crear directorio padre si no existe
        parent_dir = os.path.dirname(backlog_path)
        if parent_dir and not os.path.exists(parent_dir):
            os.makedirs(parent_dir, exist_ok=True)

        # Append entradas
        with open(backlog_path, 'a', encoding='utf-8') as f:
            for entrada in entradas:
                f.write(json.dumps(entrada, ensure_ascii=False) + '\n')
    except OSError:
        pass


def cosechar(informes_dirs, backlog_path, max_por_informe=3, profundidad_max=3, estado_path=None):
    """Cosecha lagunas de informes .md y las agrega al backlog.

    Escanea cada dir (no recursivo) por *.md. Rastrea archivos procesados por
    (filename, mtime) en archivo de estado JSON, para saltar informes ya cosechados.
    Dedup por _hash() contra entradas existentes y preguntas ya agregadas en esta
    run, y por slug (research_lib.slug, el mismo que nombra los informes) contra
    los informes ya escritos y el backlog completo: una pregunta ya respondida
    no vuelve a encolarse. Toma max N preguntas por informe.

    Args:
        informes_dirs: list[str] de directorios a escanear
        backlog_path: ruta del backlog jsonl
        max_por_informe: max preguntas por informe (default 3)
        profundidad_max: max profundidad de linaje (default 3, no usado aqui)
        estado_path: ruta del archivo de estado (default backlog_path + ".estado.json")

    Returns:
        int: numero de entradas nuevas agregadas
    """
    if estado_path is None:
        estado_path = backlog_path + '.estado.json'

    # Cargar estado de procesamiento
    estado_proc = {}
    try:
        with open(estado_path, 'r', encoding='utf-8') as f:
            estado_proc = json.load(f)
    except (OSError, ValueError, json.JSONDecodeError):
        pass

    if not isinstance(informes_dirs, list):
        informes_dirs = [informes_dirs]

    # Cargar backlog existente
    existentes = cargar(backlog_path)
    hashes_existentes = {_hash(e['pregunta']) for e in existentes}

    # Slugs ya respondidos (informes en disco) o ya encolados: la cosecha no
    # vuelve a encolar lo que el sistema ya pregunto o ya respondio.
    ocupados = slugs_ocupados(informes_dirs, existentes)

    # Hashes de preguntas ya agregadas en esta run
    hashes_agregadas = set()

    nuevas_entradas = []
    fecha_hoy = datetime.now().strftime('%Y-%m-%d')

    for dir_path in informes_dirs:
        try:
            for filename in os.listdir(dir_path):
                if not filename.endswith('.md'):
                    continue

                filepath = os.path.join(dir_path, filename)
                try:
                    stat = os.stat(filepath)
                    mtime = stat.st_mtime
                except OSError:
                    continue

                # Verificar si ya fue procesado
                clave = f"{filename}:{mtime}"
                if clave in estado_proc:
                    continue

                # Leer informe y parsear lagunas
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        contenido = f.read()
                except OSError:
                    continue

                preguntas = preguntas_del_informe(dir_path, filename, contenido)
                documento = None
                ruta_json = os.path.join(dir_path, filename[:-3] + '.json')
                try:
                    with open(ruta_json, 'r', encoding='utf-8') as f:
                        documento = json.load(f)
                except (OSError, ValueError, json.JSONDecodeError):
                    pass

                # Tomar max_por_informe, dedup
                agregadas_esta_run = 0
                bloqueadas_esta_run = []
                for pregunta in preguntas:
                    if agregadas_esta_run >= max_por_informe:
                        break

                    h = _hash(pregunta)
                    if h in hashes_existentes or h in hashes_agregadas:
                        continue

                    # Dedup por slug: si ya hay un informe (o una entrada) con
                    # este slug, la pregunta ya fue hecha -- no se re-encola.
                    s = slug(pregunta) if slug is not None else None
                    if s is not None and s in ocupados:
                        continue

                    valida, razon = validar_pregunta_derivada(pregunta, documento)
                    if not valida:
                        bloqueadas_esta_run.append({
                            'pregunta': pregunta,
                            'razon': razon,
                        })
                        continue

                    # Nueva entrada
                    entrada = {
                        'id': 'bl-' + h[:8],
                        'pregunta': pregunta,
                        'origen_informe': filename,
                        'linaje': [],
                        'score': 0.0,
                        'estado': 'pendiente',
                        'fecha': fecha_hoy,
                        'origen_tipo': 'informe',
                        'autoridad': 'modelo',
                        'activacion': 'backlog',
                    }
                    nuevas_entradas.append(entrada)
                    hashes_agregadas.add(h)
                    if s is not None:
                        ocupados.add(s)
                    agregadas_esta_run += 1

                # Marcar como procesado
                estado_proc[clave] = {
                    'procesado': True,
                    'bloqueadas': bloqueadas_esta_run,
                }
        except OSError:
            continue

    # Guardar nuevas entradas
    if nuevas_entradas:
        guardar_append(backlog_path, nuevas_entradas)

    # Guardar estado actualizado
    try:
        parent_dir = os.path.dirname(estado_path)
        if parent_dir and not os.path.exists(parent_dir):
            os.makedirs(parent_dir, exist_ok=True)
        with open(estado_path, 'w', encoding='utf-8') as f:
            json.dump(estado_proc, f)
    except OSError:
        pass

    return len(nuevas_entradas)


def derivar(entrada_padre, pregunta):
    """Construye una entrada hijo con linaje = padre["linaje"] + [padre["id"]].

    Retorna None si len(linaje) alcanzaria profundidad_max (3).

    Args:
        entrada_padre: dict del padre
        pregunta: str de la nueva pregunta

    Returns:
        dict|None: entrada hijo o None si excede profundidad
    """
    nuevo_linaje = entrada_padre.get('linaje', []) + [entrada_padre['id']]

    # Profundidad_max = 3, asi que si el linaje tiene 3 elementos, rechaza
    if len(nuevo_linaje) >= 3:
        return None

    h = _hash(pregunta)
    fecha_hoy = datetime.now().strftime('%Y-%m-%d')

    entrada = {
        'id': 'bl-' + h[:8],
        'pregunta': pregunta,
        'origen_informe': '',  # No conocemos el origen aqui
        'linaje': nuevo_linaje,
        'score': 0.0,
        'estado': 'pendiente',
        'fecha': fecha_hoy,
        'origen_tipo': 'tarea_derivada',
        'autoridad': 'inferida',
        'activacion': 'backlog',
    }

    return entrada


def pop_pendiente(backlog_path):
    """Pop la entrada con estado='pendiente', mayor score, desempate: mas vieja.

    Reescribe el archivo atomicamente (write tmp + os.replace), marcando
    la entrada como estado='en_curso'.

    Args:
        backlog_path: ruta del backlog jsonl

    Returns:
        dict|None: entrada (con estado='en_curso') o None si no hay pendientes
    """
    entradas = cargar(backlog_path)

    # Filtrar pendientes
    pendientes = [e for e in entradas if e.get('estado') == 'pendiente']

    if not pendientes:
        return None

    # Ordenar: mayor score, desempate por fecha mas vieja (menor), luego file order
    pendientes_con_idx = [(i, e) for i, e in enumerate(pendientes)]
    pendientes_con_idx.sort(
        key=lambda x: (-x[1].get('score', 0.0), x[1].get('fecha', ''), x[0])
    )

    # Seleccionar el primero
    _, seleccionada = pendientes_con_idx[0]

    # Marcar como en_curso en la lista original
    for entrada in entradas:
        if entrada['id'] == seleccionada['id']:
            entrada['estado'] = 'en_curso'
            break

    # Reescribir atomicamente
    tmp_path = backlog_path + '.tmp'
    try:
        with open(tmp_path, 'w', encoding='utf-8') as f:
            for entrada in entradas:
                f.write(json.dumps(entrada, ensure_ascii=False) + '\n')
        os.replace(tmp_path, backlog_path)
    except OSError:
        try:
            os.remove(tmp_path)
        except OSError:
            pass
        return None

    return seleccionada


def marcar(backlog_path, id_, estado):
    """Marca entrada con id_ con nuevo estado ("listo"/"descartado"/"pendiente").

    Reescribe atomicamente el archivo.

    Args:
        backlog_path: ruta del backlog jsonl
        id_: id de la entrada
        estado: nuevo estado

    Returns:
        bool: True si encontrada, False si no
    """
    entradas = cargar(backlog_path)
    encontrada = False

    for entrada in entradas:
        if entrada['id'] == id_:
            entrada['estado'] = estado
            encontrada = True
            break

    if not encontrada:
        return False

    # Reescribir atomicamente
    tmp_path = backlog_path + '.tmp'
    try:
        with open(tmp_path, 'w', encoding='utf-8') as f:
            for entrada in entradas:
                f.write(json.dumps(entrada, ensure_ascii=False) + '\n')
        os.replace(tmp_path, backlog_path)
    except OSError:
        try:
            os.remove(tmp_path)
        except OSError:
            pass
        return False

    return True


def curar(backlog_path, rankear=None, max_pendientes=40):
    """Pase de poda: si pendientes > max_pendientes, descarta exceso (score mas bajo).

    Si rankear callable se proporciona, aplica los scores retornados a pendientes primero.
    Nunca borra lineas, solo cambia estado a "descartado". Reescribe atomicamente.

    Args:
        backlog_path: ruta del backlog jsonl
        rankear: callable(list[str]) -> list[float] para re-rankear, o None
        max_pendientes: max preguntas en estado pendiente (default 40)

    Returns:
        int: numero de entradas marcadas "descartado"
    """
    entradas = cargar(backlog_path)

    # Filtrar pendientes
    pendientes = [e for e in entradas if e.get('estado') == 'pendiente']

    if len(pendientes) <= max_pendientes:
        return 0

    # Si rankear callable, aplicar scores
    if rankear is not None and callable(rankear):
        preguntas = [e['pregunta'] for e in pendientes]
        try:
            scores = rankear(preguntas)
            for i, e in enumerate(pendientes):
                if i < len(scores):
                    e['score'] = scores[i]
        except Exception:
            # Si rankear falla, continua sin actualizar scores
            pass

    # Ordenar por score (menor primero) para descartar los peores
    pendientes_con_idx = [(i, e) for i, e in enumerate(pendientes)]
    pendientes_con_idx.sort(
        key=lambda x: (x[1].get('score', 0.0), x[1].get('fecha', ''), -x[0])
    )

    # Marcar para descartar: excess = len(pendientes) - max_pendientes
    n_descartar = len(pendientes) - max_pendientes
    a_descartar = {e['id'] for _, e in pendientes_con_idx[:n_descartar]}

    # Aplicar cambios a todas las entradas
    n_descartadas = 0
    for entrada in entradas:
        if entrada['id'] in a_descartar:
            entrada['estado'] = 'descartado'
            n_descartadas += 1

    # Reescribir atomicamente
    tmp_path = backlog_path + '.tmp'
    try:
        with open(tmp_path, 'w', encoding='utf-8') as f:
            for entrada in entradas:
                f.write(json.dumps(entrada, ensure_ascii=False) + '\n')
        os.replace(tmp_path, backlog_path)
    except OSError:
        try:
            os.remove(tmp_path)
        except OSError:
            pass
        return 0

    return n_descartadas
