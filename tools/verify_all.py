#!/usr/bin/env python3
"""Verificacion del repo en un comando, con reporte limpio.

Uso: py tools/verify_all.py [--web]
Corre: compileall flujo/src/flujo, pytest tests/ -m mak, flujo verify.
Con --web agrega: npm run typecheck (en flujo/web/).
Exit != 0 si algo falla.
"""
import subprocess, sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

def run(name, cmd, cwd=None):
    print(f"\n=== {name}: {' '.join(cmd)} ===")
    try:
        r = subprocess.run(cmd, cwd=cwd)
        ok = r.returncode == 0
    except FileNotFoundError as e:
        print(f"  (no ejecutable: {e})"); ok = False
    print(f"--> {'OK' if ok else 'FALLO'} ({name})")
    return ok

def main():
    py = sys.executable
    res = []
    res.append(("compileall", run(
        "compileall", [py, "-m", "compileall", "-q",
                        str(ROOT / "flujo" / "src" / "flujo")], cwd=ROOT)))
    res.append(("pytest", run(
        "pytest", [py, "-m", "pytest", "tests/", "-q", "-m", "mak"], cwd=ROOT)))
    res.append(("flujo verify", run(
        "flujo verify", [py, "-m", "flujo", "verify"], cwd=ROOT / "flujo")))
    if "--web" in sys.argv:
        res.append(("web typecheck", run(
            "web typecheck", ["npm", "run", "typecheck"], cwd=ROOT / "flujo" / "web")))
    print("\n===== RESUMEN =====")
    for n, ok in res:
        print(f"  {'PASS' if ok else 'FAIL'}  {n}")
    sys.exit(0 if all(ok for _, ok in res) else 1)

if __name__ == "__main__":
    main()
