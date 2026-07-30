# -*- coding: utf-8 -*-
"""Ratchet de higiene del repo (2026-07-25).

Dos reglas que evitan repetir el problema medido en la sesion de
orquestacion: el handoff crecio a 1554 lineas sin tope, y tools/ acumula
scripts sin registro de si estan vivos o muertos. Ninguna de las dos
reglas se relaja "arreglando" el archivo que la dispara con contenido
falso: se comprime/archiva (handoff) o se declara en el registro
(tools/), nunca se edita el test.
"""
from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
LAST_HANDOFF = REPO_ROOT / "context" / "LAST_HANDOFF.md"
CAPACIDADES = REPO_ROOT / "CAPACIDADES.md"
TOOLS_DIR = REPO_ROOT / "tools"

MAX_HANDOFF_LINES = 350


def test_handoff_dentro_del_tope():
    contenido = LAST_HANDOFF.read_text(encoding="utf-8")
    lineas = contenido.splitlines()
    assert len(lineas) <= MAX_HANDOFF_LINES, (
        "LAST_HANDOFF.md excede 350 lineas: comprimir y archivar a "
        "docs/handoffs/archive/ (regla 2026-07-25, causa: llego a 1554 "
        "lineas; retiro: cuando el handoff viva en un sistema con "
        "rotacion automatica)"
    )


def test_tools_en_registro():
    capacidades = CAPACIDADES.read_text(encoding="utf-8")
    archivos = sorted(p for p in TOOLS_DIR.glob("*.py") if p.is_file())
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
    if salida.returncode != 0:  # sin git disponible no hay nada que medir
        return
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
