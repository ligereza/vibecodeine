# -*- coding: utf-8 -*-
"""Ratchet de higiene del repo (2026-07-25).

Dos reglas que evitan repetir el problema medido en la sesion de
orquestacion: tools/ acumula scripts sin registro de si estan vivos o muertos.
La regla se comprueba contra el registro y el arbol actual; no contra
documentos de continuidad que ya no existen.
"""
from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
CAPACIDADES = REPO_ROOT / "CAPACIDADES.md"
TOOLS_DIR = REPO_ROOT / "tools"

# El tope de 350 lineas se RETIRO el 2026-07-30, y esta es su acta.
#
# Su premisa era que un archivo largo es un archivo malo. Su efecto medido, el
# dia que se retiro: obligo a comprimir CINCO veces mediciones tomadas esa misma
# tarde -- lo unico del archivo que todavia nadie habia leido -- para no tocar
# parrafos de julio que nadie volvio a mirar. Un tope no tiene nocion de valor,
# asi que siempre cobra lo mas nuevo y protege lo mas viejo por antiguedad.
#
# Lo que si vale es podar por OBSOLESCENCIA, no por tamano: una seccion que
# lleva semanas sin tocarse se archiva. Eso pide fechas por seccion, que hoy el
# archivo no tiene; cuando las tenga, el reemplazo va aca.
UTILIDADES = REPO_ROOT / "cultura" / "mak_plataforma" / "utilidades"

# Cuantos archivos de utilidades/ no los invoca NADIE fuera del directorio.
# Medido el 2026-07-30: 28 de 32 (4.275 lineas). El numero solo puede BAJAR.
#
# El ratchet viejo del directorio media `py_compile` + pyflakes, que es
# ortografia: los 32 archivos compilan y 28 no los ejecuta nadie. Que algo se
# use es semantica, y ningun chequeo preguntaba "esto sirve?". La causa esta
# trazada y NO es el codigo: capataz.py enruta pedidos con forma de OPERACIONES
# a un canal cuyo contrato es un archivo stdlib autocontenido que nunca se
# ejecuta. Este numero es el termometro de ese defecto.
MAX_UTILIDADES_INERTES = 28


def test_utilidades_inertes_no_aumentan():
    if not UTILIDADES.is_dir():
        return
    archivos = sorted(p for p in UTILIDADES.glob("*.py") if p.is_file())
    otros = [p for p in REPO_ROOT.rglob("*.py")
             if UTILIDADES not in p.parents and ".git" not in p.parts]
    cuerpo = "\n".join(
        p.read_text(encoding="utf-8", errors="replace") for p in otros)
    inertes = [p.name for p in archivos if p.stem not in cuerpo]
    assert len(inertes) <= MAX_UTILIDADES_INERTES, (
        "utilidades/ tiene %d archivos que no invoca nadie (el tope medido es "
        "%d). No se resuelve borrando: se resuelve en el ENRUTAMIENTO, que es "
        "donde nace -- un pedido de operaciones no puede satisfacerse con un "
        "archivo que nadie ejecuta. Nuevos inertes: %s"
        % (len(inertes), MAX_UTILIDADES_INERTES, ", ".join(inertes[:5]))
    )


def test_tools_en_registro():
    capacidades = CAPACIDADES.read_text(encoding="utf-8")
    archivos = sorted(p for p in TOOLS_DIR.glob("*.py") if p.is_file())
    # El cero silencioso (memoria de direccion 2.3): si tools/ se mueve o se
    # vacia, la lista queda vacia y el ratchet informa "nada falta" para
    # siempre. Cero medido es un ERROR, no un silencio.
    assert archivos, (
        "no se encontro ninguna herramienta en %s: el ratchet no midio nada, "
        "que no es lo mismo que estar limpio" % TOOLS_DIR)
    faltantes = [
        p.name for p in archivos if p.name not in capacidades
    ]
    assert not faltantes, (
        "tools/<x>.py sin entrada en registro VIVO/MUERTO de "
        "CAPACIDADES.md: toda herramienta declara consumidor o no entra "
        "(regla 2026-07-25). Faltan: " + ", ".join(faltantes)
    )


def test_registro_sin_herramientas_fantasma():
    """La direccion inversa, que faltaba (2026-07-27).

    El ratchet solo miraba archivo -> registro, asi que una fila de una
    herramienta BORRADA se quedaba ahi para siempre y nadie se enteraba. Caso
    medido: `gen_piel_iskvw.py` figuraba como REVISAR en el registro y el
    archivo no existia en ninguna rama, asi que el inventario mandaba a un
    agente a buscar una herramienta inexistente. Un registro que miente en una
    direccion miente igual.

    Retiro: cuando el registro se genere desde el arbol de archivos.
    """
    import re

    capacidades = CAPACIDADES.read_text(encoding="utf-8")
    # Solo las filas de la tabla del registro: `nombre.py` en la primera celda.
    declaradas = set(re.findall(r"^\|\s*`([a-z0-9_]+\.py)`\s*\|", capacidades,
                                re.MULTILINE))
    existentes = {p.name for p in TOOLS_DIR.glob("*.py") if p.is_file()}
    assert declaradas, (
        "el registro de CAPACIDADES.md no declaro ninguna fila `x.py`: si la "
        "tabla cambia de formato el regex deja de matchear y este ratchet pasa "
        "sin medir nada")
    assert existentes, "no hay herramientas en tools/: nada que contrastar"
    fantasmas = sorted(declaradas - existentes)
    assert not fantasmas, (
        "el registro de CAPACIDADES.md declara herramientas que no existen en "
        "tools/: se borro el archivo y quedo la fila. Retirar la fila o "
        "restaurar la herramienta. Fantasmas: " + ", ".join(fantasmas)
    )


# Configuracion que el usuario edita a mano y que el codigo declara "fuente
# unica". Si un archivo asi no viaja en el repo, el codigo cae a su respaldo
# interno y NADIE se entera salvo por una linea en stderr.
CONFIG_DEL_USUARIO = (
    "data/rd_packs.json",
    "data/plano_simbolos.json",
    "data/cotizacion_servicios.json",
    "data/svg_estados.json",
    "data/iskvw_campo_filtro.json",
    "data/iskvw_librerias.json",
    "data/iskvw_capas.json",
)


def test_config_del_usuario_versionada():
    """Regresion medida: `data/rd_packs.json` se declaro fuente unica de la
    tarifa RD el 2026-07-26 y quedo fuera del repo, porque .gitignore ignora
    `data/*.json`. En cualquier otro checkout el rider cotizaba con la copia de
    respaldo del codigo. Un archivo de configuracion que no viaja no es una
    fuente de verdad."""
    import subprocess

    salida = subprocess.run(
        ["git", "ls-files", "--", *CONFIG_DEL_USUARIO],
        cwd=REPO_ROOT, capture_output=True, encoding="utf-8", errors="replace",
    )
    if salida.returncode != 0:
        # Sin git no hay nada que medir, y "no medi" no es "esta bien": se
        # salta explicitamente en vez de devolver verde.
        pytest.skip("no es un checkout git usable: el ratchet no puede medir")
    versionados = set(salida.stdout.split())
    faltantes = [p for p in CONFIG_DEL_USUARIO if p not in versionados]
    assert not faltantes, (
        "config editable por el usuario fuera del repo (revisa .gitignore, "
        "necesita una linea `!<ruta>`): " + ", ".join(faltantes)
    )


# Los modulos que un OPERADOR corre desde la consola de Windows. Ahi la salida
# se codifica en cp1252, y un glifo que no existe en esa tabla no es un detalle
# estetico: `print` levanta UnicodeEncodeError y el comando muere a mitad.
# Medido el 2026-07-30: el motor semantico llego con ✓ ✗ ⚠ · ─ ═ → ≥ y reventaba
# al imprimir su primer mensaje de error. Se limpio a mano, y esta regla existe
# porque limpiar a mano no impide que el proximo archivo lo traiga de vuelta.
#
# Las TILDES no entran aca y no son el problema: cp1252 tiene á é í ó ú ñ ¿ ¡.
# Lo que se prohibe son los glifos decorativos fuera de esa tabla. El espanol
# correcto de un valor que lee un humano se conserva siempre.
#
# Retiro: cuando el repo fije PYTHONIOENCODING=utf-8 para todo comando que el
# operador corre, y eso este verificado en Windows.
# Alcance: TODO lo que un operador corre desde la consola. Con excepciones
# DECLARADAS por archivo, porque al medir tools/ entero aparecieron glifos que
# son CONTENIDO y no decoracion, y forzarles ASCII seria repetir el error que
# una vez mutilo los productos del repo. Una excepcion sin razon escrita no
# vale: si no se puede decir por que ese glifo significa algo, es decoracion y
# se saca.
ZONA_CONSOLA = ("tools", "cultura/mak_codex/motor_semantico")

GLIFOS_QUE_SIGNIFICAN = {
    "tools/compete_engine.py":
        "dibuja marcos y sombreados como PIEZA (bloques y lineas de caja): el "
        "glifo es la obra, no un adorno del log",
    "tools/tilde_meter.py":
        "Omega y el subindice son la notacion de Motor Omega, y el circulo "
        "cruzado es su operador; renombrarlos en ASCII cambia lo que dicen",
    "tools/system_map.py":
        "las flechas dibujan el diagrama de arquitectura que el comando imprime",
    "tools/gen_mapa_comandos.py":
        "reproduce el arbol de comandos con las mismas lineas que muestra MAPA.md",
}


def _fuera_de_cp1252(texto: str) -> set[str]:
    return {c for c in texto
            if ord(c) > 127 and c.encode("cp1252", "ignore") == b""}


def test_lo_que_corre_en_la_consola_del_operador_es_imprimible():
    ofensas = []
    for rel in ZONA_CONSOLA:
        carpeta = REPO_ROOT / rel
        if not carpeta.is_dir():
            continue
        for py in sorted(carpeta.glob("*.py")):
            nombre = py.relative_to(REPO_ROOT).as_posix()
            if nombre in GLIFOS_QUE_SIGNIFICAN:
                continue
            malos = _fuera_de_cp1252(py.read_text(encoding="utf-8"))
            if malos:
                ofensas.append("%s: %s" % (
                    nombre, " ".join(sorted(hex(ord(c)) for c in malos))))
    assert not ofensas, (
        "Glifos que la consola cp1252 de Windows no puede imprimir. No es "
        "estetica: `print` levanta UnicodeEncodeError y el comando muere a "
        "mitad. Reemplazalos por ASCII (OK, x, !, -, ->, >=). Las tildes NO "
        "son el problema y se conservan.\n  " + "\n  ".join(ofensas))


def test_toda_excepcion_de_glifo_apunta_a_un_archivo_real_y_con_razon():
    """Una lista de excepciones que nadie poda deja de ser una lista. Si el
    archivo ya no existe, o dejo de tener glifos, la fila sale."""
    for nombre, razon in GLIFOS_QUE_SIGNIFICAN.items():
        ruta = REPO_ROOT / nombre
        assert ruta.is_file(), "excepcion fantasma: %s ya no existe" % nombre
        assert len(razon) > 40, "%s: la razon tiene que decir por que" % nombre
        assert _fuera_de_cp1252(ruta.read_text(encoding="utf-8")), (
            "%s ya no tiene glifos no imprimibles: saca la excepcion" % nombre)
