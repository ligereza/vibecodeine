#!/usr/bin/env python3
"""generar.py -- CODEX: plan (gpt-5-mini) -> codigo (DeepSeek) -> sandbox ->
reparacion -> pieza.

    python3 generar.py "un parser de csv a json" [--densidad corto|medio|largo]
                        [--sin-ejecutar] [--ntfy]
"""
import argparse
import os
import sys
import time
import tempfile

from codex_lib import (PROMPT_CODER, coder_llm, coder_tok, escanear,
                       extraer_codigo, guardar_pieza, guardia_espera,
                       planner_llm, sandbox_run, tiempo_ms)

sys.path.insert(0, "/home/mak/research")
from research_lib import escala_tok, ntfy_publish  # noqa: E402


def generar(pedido, densidad="medio", ejecutar=True):
    t0 = time.time()
    planner = planner_llm()
    coder = coder_llm()

    print("STATUS: Planificando (gpt-5-mini)...", flush=True)
    plan, real_plan = planner.call(
        "Eres el arquitecto del departamento Codex. Respondes en espanol, "
        "conciso y tecnico.",
        'PEDIDO: "%s"\n\nEscribe una spec corta: 1. QUE construir (un solo '
        "archivo Python stdlib), 2. INTERFAZ (funciones/CLI), 3. TRES casos "
        "de prueba concretos (entrada -> salida esperada) que el propio "
        "script debe autoverificar con assert al correr." % pedido,
        escala_tok(600, densidad))
    _primer = next((ln.strip() for ln in plan.splitlines() if ln.strip()), "")
    print("HALLAZGO: plan -- " + _primer[:120], flush=True)

    print("STATUS: Escribiendo codigo (DeepSeek)...", flush=True)
    bruto, real_coder = coder.call(
        PROMPT_CODER,
        "SPEC:\n%s\n\nEscribe el archivo completo. Debe incluir un bloque "
        'if __name__ == "__main__": que corra los casos de prueba con assert '
        'y termine imprimiendo "PRUEBAS OK".' % plan,
        coder_tok(densidad))
    codigo = extraer_codigo(bruto)

    resultado = {"ok": None, "rc": None, "stdout": "", "stderr": "",
                 "bloqueado": False}
    reparado = False
    if ejecutar:
        motivos = escanear(codigo)
        if motivos:
            resultado = {"ok": False, "bloqueado": True, "motivos": motivos,
                         "stdout": "", "stderr": "", "rc": -1}
            print("STATUS: Ejecucion bloqueada (%s) -- pieza guardada para "
                  "revision humana." % ", ".join(motivos), flush=True)
        else:
            print("STATUS: Sandbox...", flush=True)
            with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False,
                                             encoding="utf-8") as f:
                f.write(codigo)
                tmp_path = f.name
            try:
                resultado = sandbox_run(tmp_path)
                if not resultado["ok"] and not resultado.get("bloqueado"):
                    print("STATUS: Fallo, una ronda de reparacion (DeepSeek)...",
                          flush=True)
                    bruto2, _ = coder.call(
                        PROMPT_CODER,
                        "Este codigo fallo en el sandbox.\n\nCODIGO:\n```python\n"
                        "%s\n```\n\nSTDERR:\n%s\n\nDevuelve el archivo COMPLETO "
                        "corregido." % (codigo, resultado["stderr"]),
                        coder_tok(densidad))
                    codigo2 = extraer_codigo(bruto2)
                    if codigo2 and not escanear(codigo2):
                        with open(tmp_path, "w", encoding="utf-8") as f:
                            f.write(codigo2)
                        resultado2 = sandbox_run(tmp_path)
                        if resultado2["ok"]:
                            codigo, resultado, reparado = codigo2, resultado2, True
            finally:
                os.unlink(tmp_path)
    else:
        print("STATUS: --sin-ejecutar: pieza guardada sin correr.", flush=True)

    # F2b/#139: smoke_ok gatea la entrega en entregar.py. True SOLO si el
    # sandbox de verdad corrio y termino con rc==0 (que en la practica
    # significa que imprimio "PRUEBAS OK", ver PROMPT_CODER); bloqueado
    # (patron peligroso, nunca corrio) o --sin-ejecutar cuentan como
    # smoke_ok=False, no como "desconocido" -- entregar.py NO debe tratar
    # una pieza nunca ejecutada como si fuera compatible-vieja.
    if resultado.get("bloqueado"):
        _razon_smoke = "bloqueado (patron peligroso): " + ", ".join(
            resultado.get("motivos", []))
    elif not ejecutar:
        _razon_smoke = "no ejecutado (--sin-ejecutar)"
    elif not resultado.get("ok"):
        _razon_smoke = resultado.get("stderr") or "sandbox fallo sin stderr"
    else:
        _razon_smoke = ""
    smoke_ok = (ejecutar and bool(resultado.get("ok"))
               and not resultado.get("bloqueado", False))

    meta = {"pedido": pedido, "plan_por": real_plan, "codigo_por": real_coder,
            "reparado": reparado, "smoke_ok": smoke_ok,
            "llmCalls": {"planner": planner.stats, "coder": coder.stats},
            "errors": (planner.errors + coder.errors)[:10], "ms": tiempo_ms(t0)}
    if not smoke_ok:
        meta["smoke_stderr_tail"] = _razon_smoke[-300:]
    _estado = ("bloqueado" if resultado.get("bloqueado")
              else ("OK" if resultado.get("ok") else "fallo sandbox"))
    print("HALLAZGO: resultado -- %s (%s, reparado=%s)"
          % (_estado, real_coder, reparado), flush=True)
    path_py, path_md = guardar_pieza(pedido, codigo, resultado, meta)
    return path_md, resultado, meta


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pedido")
    ap.add_argument("--densidad", choices=("corto", "medio", "largo"),
                    default="medio")
    ap.add_argument("--sin-ejecutar", action="store_true")
    ap.add_argument("--ntfy", action="store_true")
    a = ap.parse_args()

    if not guardia_espera():
        print("INFORME: (ninguno)")
        return 1
    path_md, resultado, meta = generar(a.pedido, a.densidad,
                                       ejecutar=not a.sin_ejecutar)
    estado = ("bloqueado-revision" if resultado.get("bloqueado")
              else ("ok" if resultado.get("ok") else "fallo-sandbox"))
    print("codex generar: %s, codigo por %s, %d ms"
          % (estado, meta["codigo_por"], meta["ms"]))
    if a.ntfy:
        ntfy_publish(os.environ.get("NTFY_TOPIC_OUT", ""),
                     "pieza codex (%s): %s" % (estado, path_md),
                     title="codex: " + a.pedido[:70])
    print("INFORME: " + path_md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
