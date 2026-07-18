#!/usr/bin/env python3
"""backlog.py -- sistema generativo de backlog para MAK.

Parsea secciones "LAGUNAS DE INFORMACION" de informes y las convierte en
entradas de backlog deduplicadas y ranqueadas. Enforza las reglas de poda:
  1. Max N preguntas por informe
  2. Profundidad de linaje <= 3
  3. Curador: descarta redundantes/triviales
"""
import json
import os
import re
import unicodedata
from datetime import datetime
from hashlib import sha1


def _norm(texto):
    """Normaliza para dedup: lowercase, colapsa whitespace, quita accents."""
    # Quitar accents
    nfd = unicodedata.normalize('NFD', texto)
    sin_accents = ''.join(c for c in nfd if unicodedata.category(c) != 'Mn')
    # Lowercase y colapsar whitespace
    normalizado = re.sub(r'\s+', ' ', sin_accents.lower().strip())
    return normalizado


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
            if pregunta:
                # Capear a 300 chars
                pregunta = pregunta[:300]
                preguntas.append(pregunta)

    return preguntas


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
    Dedup por _hash() contra entradas existentes y preguntas ya agregadas en esta run.
    Toma max N preguntas por informe.

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

    # Cargar backlog existente
    existentes = cargar(backlog_path)
    hashes_existentes = {_hash(e['pregunta']) for e in existentes}

    # Hashes de preguntas ya agregadas en esta run
    hashes_agregadas = set()

    nuevas_entradas = []
    fecha_hoy = datetime.now().strftime('%Y-%m-%d')

    # Procesar cada directorio
    if not isinstance(informes_dirs, list):
        informes_dirs = [informes_dirs]

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

                preguntas = parsear_lagunas(contenido)

                # Tomar max_por_informe, dedup
                agregadas_esta_run = 0
                for pregunta in preguntas:
                    if agregadas_esta_run >= max_por_informe:
                        break

                    h = _hash(pregunta)
                    if h in hashes_existentes or h in hashes_agregadas:
                        continue

                    # Nueva entrada
                    entrada = {
                        'id': 'bl-' + h[:8],
                        'pregunta': pregunta,
                        'origen_informe': filename,
                        'linaje': [],
                        'score': 0.0,
                        'estado': 'pendiente',
                        'fecha': fecha_hoy
                    }
                    nuevas_entradas.append(entrada)
                    hashes_agregadas.add(h)
                    agregadas_esta_run += 1

                # Marcar como procesado
                estado_proc[clave] = True
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
        'fecha': fecha_hoy
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
