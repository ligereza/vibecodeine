#!/usr/bin/env python3
"""agente_libre.py -- P1-1: harness de MEJORA LIBRE para MAK.

A diferencia de generar.py (que ejecuta el pedido del backlog en un
sandbox), agente_libre PROPONE su propio objetivo (semilla libre, no
backlog fijo), lo planifica y codea, y lo entrega SIN EJECUTARLO --
solo estatico (py_compile + AST stdlib-only). Nunca corre el codigo
generado (a diferencia de generar.py que sandboxea).

CONFINAMIENTO DURO (P1-1, ver CLAUDE.md seguridad):
  - Este script NUNCA toca el repo ~/flujo directamente. Solo escribe
    en ~/codex/piezas/ (igual que guardar_pieza de codex_lib) y
    apendea a ~/codex/jobs.jsonl en el MISMO formato que usa
    interfaz_codex.py -- as[i] el entregador YA EXISTENTE
    (~/plataforma/entregar.py) es el UNICO que toca el repo, y solo
    escribe bajo cultura/mak_plataforma/utilidades/ (su DEST_REL fijo).
    agente_libre no reinventa ese camino, lo REUSA.
  - _assert_confinado() rechaza cualquier intento de escribir fuera de
    ~/codex/piezas (defensa en profundidad; por construccion el script
    ni siquiera importa nada que toque ~/flujo).
  - NUNCA ejecuta el codigo generado (ni sandbox_run). Solo:
      1. py_compile (sintaxis real, motor CPython)
      2. AST stdlib-only (rechaza cualquier import fuera de la stdlib)
    Si falla, UN reintento pasando el error al coder. Si vuelve a
    fallar: ABORTA, no escribe nada, no apendea jobs.jsonl.

Uso:
  python3 agente_libre.py               # elige un objetivo de la lista semilla
  python3 agente_libre.py --objetivo "..."   # objetivo especifico (aun asi
                                              # queda confinado a stdlib/piezas)
"""
import argparse
import ast
import os
import py_compile
import random
import sys
import tempfile
import time

sys.path.insert(0, "/home/mak/codex")
from codex_lib import (PROMPT_CODER, coder_llm, coder_tok, escanear,
                       extraer_codigo, guardia_espera, planner_llm,
                       tiempo_ms)

sys.path.insert(0, "/home/mak/research")
from research_lib import slug, stamp  # noqa: E402

BASE = "/home/mak/codex"
PIEZAS = os.path.join(BASE, "piezas")
JOBS_FILE = os.path.join(BASE, "jobs.jsonl")

# Semillas libres: utilidades stdlib, autocontenidas, genericas -- se
# convierten en cultura/mak_plataforma/utilidades/<slug>.py via el
# entregador existente. Nada de red/proceso/archivos fuera de su propio
# argumento (el escaneo de codex_lib.escanear() ya filtra eso).
OBJETIVOS_SEMILLA = [
    "una utilidad stdlib que valide que un archivo .json es parseable y "
    "reporte linea/columna del primer error si no lo es",
    "una utilidad stdlib que cuente lineas de codigo vs comentarios vs "
    "blancas en un archivo .py dado por ruta",
    "una utilidad stdlib que detecte archivos duplicados por hash sha256 "
    "dentro de una carpeta dada",
    "una utilidad stdlib que convierta un CSV simple a una tabla markdown",
    "una utilidad stdlib que calcule estadisticas basicas (min/max/media/"
    "mediana) de una columna numerica de un CSV",
    "una utilidad stdlib que liste las funciones publicas de un modulo .py "
    "(nombre + firma) sin ejecutarlo, usando ast",
]


def elegir_objetivo(forzado=None):
    if forzado and forzado.strip():
        return forzado.strip()
    return random.choice(OBJETIVOS_SEMILLA)


def _assert_confinado(path_abs):
    """Defensa en profundidad: agente_libre SOLO puede escribir bajo
    ~/codex/piezas. Nunca ~/flujo, nunca otra cosa. Aborta (excepcion)
    si algun cambio futuro intenta desviarse."""
    real = os.path.realpath(path_abs)
    raiz = os.path.realpath(PIEZAS)
    if not (real == raiz or real.startswith(raiz + os.sep)):
        raise RuntimeError(
            "CONFINAMIENTO VIOLADO: intento de escribir fuera de %s -> %s"
            % (raiz, real))


# -- checks estaticos (NUNCA se ejecuta el codigo) --------------------

def _stdlib_modules():
    mods = set(getattr(sys, "stdlib_module_names", ()))
    if mods:
        return mods
    # fallback python <3.10: set chico de lo mas comun (no deberia
    # dispararse en esta caja, py 3.11 confirmado)
    return set(sys.builtin_module_names)


_STDLIB = _stdlib_modules()


def check_ast_stdlib(codigo):
    """Devuelve (ok, motivo). Rechaza cualquier import que no sea stdlib
    o el propio __future__. No ejecuta nada, solo parsea el AST."""
    try:
        arbol = ast.parse(codigo)
    except SyntaxError as e:
        return False, "SyntaxError (ast): %s (linea %s)" % (e.msg, e.lineno)
    externos = []
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.Import):
            for alias in nodo.names:
                raiz = alias.name.split(".")[0]
                if raiz not in _STDLIB and raiz != "__future__":
                    externos.append(raiz)
        elif isinstance(nodo, ast.ImportFrom):
            if nodo.level and nodo.level > 0:
                continue  # import relativo (no aplica en pieza suelta)
            raiz = (nodo.module or "").split(".")[0]
            if raiz and raiz not in _STDLIB and raiz != "__future__":
                externos.append(raiz)
    if externos:
        return False, "imports no-stdlib: %s" % ", ".join(sorted(set(externos)))
    return True, ""


def check_py_compile(codigo):
    """py_compile real (motor CPython) sobre un archivo temporal. Solo
    COMPILA (bytecode), NUNCA lo importa ni lo corre."""
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False,
                                     encoding="utf-8") as f:
        f.write(codigo)
        tmp_path = f.name
    cfile_path = tmp_path + "c"
    try:
        py_compile.compile(tmp_path, doraise=True, cfile=cfile_path)
        return True, ""
    except py_compile.PyCompileError as e:
        return False, "py_compile: %s" % str(e.exc_value or e)[:300]
    finally:
        for p in (tmp_path, cfile_path):
            try:
                os.unlink(p)
            except OSError:
                pass


def check_codigo(codigo):
    """Chequeo estatico completo: py_compile + ast stdlib-only + el
    escaneo de peligro de codex_lib (defensa extra, aunque nunca se
    ejecute). Devuelve (ok, motivo)."""
    ok, motivo = check_py_compile(codigo)
    if not ok:
        return False, motivo
    ok, motivo = check_ast_stdlib(codigo)
    if not ok:
        return False, motivo
    peligros = escanear(codigo)
    if peligros:
        return False, "patrones peligrosos: %s" % ", ".join(peligros)
    return True, ""


# -- pipeline plan -> codigo -> check -> handoff -----------------------

def planificar(objetivo, planner, densidad="medio"):
    print("STATUS: Planificando (modelo capaz)...", flush=True)
    plan, real_plan = planner.call(
        "Eres el arquitecto del departamento Codex de MAK, area de mejora "
        "libre. Respondes en espanol, conciso y tecnico.",
        'OBJETIVO LIBRE: "%s"\n\nEscribe una spec corta: 1. QUE construir '
        "(un solo archivo Python stdlib, SIN dependencias externas), "
        "2. INTERFAZ (nombre de funcion principal + CLI si aplica), "
        "3. TRES casos de prueba concretos (entrada -> salida esperada) "
        "que el propio script debe autoverificar con assert bajo "
        'if __name__ == "__main__". El archivo NUNCA debe tocar red, '
        "procesos, ni rutas fuera de sus propios argumentos." % objetivo,
        600)
    return plan, real_plan


def codear(spec, coder, densidad="medio", error_previo=None):
    user = ("SPEC:\n%s\n\nEscribe el archivo completo, stdlib-only, "
            'con un bloque if __name__ == "__main__": que corra los '
            'casos de prueba con assert y termine imprimiendo "PRUEBAS '
            'OK".' % spec)
    if error_previo:
        user = ("Tu intento anterior NO paso el chequeo estatico.\n\n"
                "ERROR: %s\n\n%s\n\nDevuelve el archivo COMPLETO "
                "corregido (sigue siendo stdlib-only)." % (error_previo, user))
    bruto, real_coder = coder.call(PROMPT_CODER, user, coder_tok(densidad))
    return extraer_codigo(bruto), real_coder


def guardar_pieza_libre(objetivo, codigo, meta):
    """Escribe la pieza .py + .md hermano bajo ~/codex/piezas, mismo
    layout que codex_lib.guardar_pieza pero SIN sandbox_run (nunca se
    ejecuta el codigo de mejora libre)."""
    os.makedirs(PIEZAS, exist_ok=True)
    base = os.path.join(PIEZAS, "%s-%s" % (stamp(), slug(objetivo)))
    py_path = base + ".py"
    md_path = base + ".md"
    _assert_confinado(py_path)
    _assert_confinado(md_path)
    with open(py_path, "w", encoding="utf-8") as f:
        f.write(codigo if codigo.endswith("\n") else codigo + "\n")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("# Codex (mejora-libre): %s\n\n" % objetivo)
        f.write("Chequeo estatico: **OK** (py_compile + ast stdlib-only). "
                "NUNCA ejecutado.\n\n")
        f.write("```python\n%s\n```\n\n" % codigo.strip())
        f.write("---\nmeta: %s\n" % meta)
    return py_path, md_path


def apendear_job(job_id, objetivo, md_path, ok, error=""):
    """Apendea a ~/codex/jobs.jsonl EXACTAMENTE en el formato que
    interfaz_codex.py._lanzar() escribe, para que
    ~/plataforma/entregar.py lo cosecheque sin cambios."""
    import json
    entrada = {
        "pedido": objetivo,
        "modo": "mejora-libre",
        "estado": "listo" if ok else "FALLO",
        "path": os.path.basename(md_path) if md_path else "",
        "error": error[:1500],
        "t": time.strftime("%H:%M:%S"),
        "job_id": job_id,
    }
    linea = json.dumps(entrada, ensure_ascii=False)
    with open(JOBS_FILE, "a", encoding="utf-8") as f:
        f.write(linea + "\n")
    return linea


def mint_job_id_libre():
    return "%s-%s" % (stamp(), os.urandom(2).hex())


def correr(objetivo_forzado=None, densidad="medio"):
    t0 = time.time()
    objetivo = elegir_objetivo(objetivo_forzado)
    job_id = mint_job_id_libre()
    print("HALLAZGO: objetivo -- %s" % objetivo, flush=True)

    if not guardia_espera():
        print("INFORME: (ninguno) -- guardia de recursos, no corrio")
        return 1

    planner = planner_llm()
    coder = coder_llm()

    plan, real_plan = planificar(objetivo, planner, densidad)
    print("HALLAZGO: plan por %s" % real_plan, flush=True)

    codigo, real_coder = codear(plan, coder, densidad)
    ok, motivo = check_codigo(codigo) if codigo else (False, "coder devolvio vacio")
    reintentado = False

    if not ok:
        print("STATUS: chequeo estatico fallo (%s) -- un reintento" % motivo,
              flush=True)
        reintentado = True
        codigo2, real_coder2 = codear(plan, coder, densidad, error_previo=motivo)
        ok2, motivo2 = check_codigo(codigo2) if codigo2 else (False, "coder devolvio vacio")
        if ok2:
            codigo, real_coder, ok, motivo = codigo2, real_coder2, True, ""
        else:
            ok, motivo = False, motivo2

    if not ok:
        print("HALLAZGO: ABORTADO -- no compila / no stdlib-only tras "
              "reintento: %s" % motivo, flush=True)
        apendear_job(job_id, objetivo, "", ok=False, error=motivo)
        print("INFORME: (ninguno)")
        return 1

    meta = ("plan_por=%s codigo_por=%s reintentado=%s ms=%d"
            % (real_plan, real_coder, reintentado, tiempo_ms(t0)))
    py_path, md_path = guardar_pieza_libre(objetivo, codigo, meta)
    apendear_job(job_id, objetivo, md_path, ok=True)

    print("HALLAZGO: pieza OK -- %s" % py_path, flush=True)
    print("agente_libre: ok, plan por %s, codigo por %s, %d ms"
          % (real_plan, real_coder, tiempo_ms(t0)))
    print("INFORME: " + md_path)
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--objetivo", default="",
                    help="objetivo libre especifico (default: elige de la "
                         "lista semilla)")
    ap.add_argument("--densidad", choices=("corto", "medio", "largo"),
                    default="medio")
    a = ap.parse_args()
    return correr(a.objetivo, a.densidad)


if __name__ == "__main__":
    sys.exit(main())
