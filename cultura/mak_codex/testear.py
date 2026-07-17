#!/usr/bin/env python3
"""testear.py -- CODEX: genera tests unittest para un archivo y los corre
en el sandbox (mismo tempdir que el modulo bajo prueba).

    python3 testear.py /ruta/al/archivo.py [--densidad] [--ntfy]
"""
import argparse
import os
import resource
import subprocess
import sys
import tempfile
import time

from codex_lib import (REVISIONES, coder_llm, coder_tok, escanear,
                       extraer_codigo, guardia_espera, tiempo_ms, _limites)

sys.path.insert(0, "/home/mak/research")
from research_lib import escala_tok, ntfy_publish, slug, stamp  # noqa: E402


def testear(path, densidad="medio"):
    t0 = time.time()
    with open(path, encoding="utf-8", errors="replace") as f:
        codigo = f.read()[:20000]
    modulo = os.path.splitext(os.path.basename(path))[0]
    coder = coder_llm()

    print("STATUS: Generando tests (DeepSeek)...", flush=True)
    bruto, real = coder.call(
        "Eres un ingeniero de tests. Devuelves UN bloque ```python``` con un "
        "archivo unittest stdlib completo, en espanol.",
        "Modulo `%s`:\n```python\n%s\n```\n\nEscribe tests unittest que "
        "importen `%s` (esta en el mismo directorio) cubriendo casos normales "
        "y bordes. Sin mocks de red." % (modulo, codigo, modulo),
        coder_tok(densidad))
    tests = extraer_codigo(bruto)

    bloqueo = escanear(codigo) + escanear(tests)
    resultado = {"ok": False, "rc": -1, "stdout": "", "stderr": ""}
    if bloqueo:
        resultado["stderr"] = ("ejecucion bloqueada, requiere revision humana: "
                               + ", ".join(sorted(set(bloqueo))))
    else:
        print("STATUS: Corriendo tests en sandbox...", flush=True)
        with tempfile.TemporaryDirectory(prefix="codex-test-") as tmp:
            with open(os.path.join(tmp, modulo + ".py"), "w",
                      encoding="utf-8") as f:
                f.write(codigo)
            with open(os.path.join(tmp, "test_pieza.py"), "w",
                      encoding="utf-8") as f:
                f.write(tests)
            try:
                p = subprocess.run(
                    [sys.executable, "-I", "-m", "unittest", "-v",
                     "test_pieza"],
                    cwd=tmp, capture_output=True, text=True, timeout=60,
                    preexec_fn=_limites,
                    env={"PATH": "/usr/bin:/bin", "HOME": tmp,
                         "LANG": "C.UTF-8"})
                resultado = {"ok": p.returncode == 0, "rc": p.returncode,
                             "stdout": p.stdout[-4000:],
                             "stderr": p.stderr[-5000:]}
            except subprocess.TimeoutExpired:
                resultado = {"ok": False, "rc": -9, "stdout": "",
                             "stderr": "timeout 60s"}

    os.makedirs(REVISIONES, exist_ok=True)
    base = os.path.join(REVISIONES, "%s-test-%s" % (stamp(), slug(modulo)))
    with open(base + ".md", "w", encoding="utf-8") as f:
        f.write("# Tests codex: %s\n\nResultado: **%s** (rc=%s, por %s)\n\n"
                % (path, "OK" if resultado["ok"] else "FALLÓ",
                   resultado["rc"], real))
        f.write("```python\n%s\n```\n\n## Salida\n\n```\n%s\n%s\n```\n"
                % (tests.strip(), resultado["stdout"].strip(),
                   resultado["stderr"].strip()))
        f.write("---\nmeta: coder=%s ms=%d\n" % (coder.stats, tiempo_ms(t0)))
    return base + ".md", resultado


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("archivo")
    ap.add_argument("--densidad", choices=("corto", "medio", "largo"),
                    default="medio")
    ap.add_argument("--ntfy", action="store_true")
    a = ap.parse_args()
    real = os.path.realpath(a.archivo)
    if not real.startswith("/home/mak/") or not os.path.isfile(real):
        print("archivo invalido (debe existir bajo /home/mak): %s" % a.archivo)
        print("INFORME: (ninguno)")
        return 2
    if not guardia_espera():
        print("INFORME: (ninguno)")
        return 1
    path_md, resultado = testear(real, a.densidad)
    if a.ntfy:
        ntfy_publish(os.environ.get("NTFY_TOPIC_OUT", ""),
                     "tests codex (%s): %s"
                     % ("OK" if resultado["ok"] else "FALLO", path_md),
                     title="codex testea: " + os.path.basename(real))
    print("INFORME: " + path_md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
