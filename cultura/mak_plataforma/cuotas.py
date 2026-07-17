#!/usr/bin/env python3
"""cuotas.py -- limites de cuota por modelo de los 2 departamentos (MAK).

Muestra el limite DOCUMENTADO (free tier) de cada modelo + el USO REAL de
HOY, contado desde el meta de los productos del archivo (sin gastar ni una
llamada extra a las APIs). El estado sale de si hubo 429/limite reciente.

Lib + CLI:  python3 cuotas.py        (tabla)
            python3 cuotas.py --json (crudo, lo lee el hub :8900)
"""
import json
import os
import re
import time

HOME = os.path.expanduser("~")

# Registro de modelos: limites DOCUMENTADOS del free tier (aproximados,
# verificar en la doc del proveedor -- cambian). tipo local = sin cuota.
MODELOS = [
    # --- research ---
    {"depto": "research", "proveedor": "Groq", "modelo": "llama-3.3-70b-versatile",
     "claves": ["groq", "llama-3.3-70b-versatile"], "tipo": "api",
     "limite": "30 req/min · ~1.000 req/dia · 12k tok/min", "req_dia": 1000},
    {"depto": "research", "proveedor": "Cerebras", "modelo": "gpt-oss-120b",
     "claves": ["cerebras", "gpt-oss-120b"], "tipo": "api",
     "limite": "30 req/min · free tier (catalogo rota)", "req_dia": 14400},
    {"depto": "research", "proveedor": "Azure Foundry", "modelo": "gpt-5-mini",
     "claves": ["azure", "gpt-5-mini"], "tipo": "api",
     "limite": "segun deployment (RPM/TPM propios)", "req_dia": None},
    {"depto": "research", "proveedor": "Tavily", "modelo": "search",
     "claves": ["tavily"], "tipo": "api",
     "limite": "1.000 creditos/mes (basic=1, advanced=2)", "req_dia": None},
    {"depto": "research", "proveedor": "Ollama (local)", "modelo": "gemma3:4b",
     "claves": ["gemma3:4b", "ollama"], "tipo": "local",
     "limite": "local · sin cuota (limita la GPU 4GB)", "req_dia": None},
    {"depto": "research", "proveedor": "Ollama (local)", "modelo": "nomic-embed-text",
     "claves": ["nomic-embed-text"], "tipo": "local",
     "limite": "local · sin cuota (micelio)", "req_dia": None},
    # --- codex ---
    {"depto": "codex", "proveedor": "NVIDIA NIM", "modelo": "deepseek-v4-pro",
     "claves": ["deepseek-ai/deepseek-v4-pro", "deepseek-v4-pro"], "tipo": "api",
     "limite": "~40 req/min (free hosted, creditos personales)", "req_dia": None},
    {"depto": "codex", "proveedor": "NVIDIA NIM", "modelo": "deepseek-v4-flash",
     "claves": ["deepseek-ai/deepseek-v4-flash", "deepseek-v4-flash"], "tipo": "api",
     "limite": "~40 req/min (free hosted, mas rapido)", "req_dia": None},
    {"depto": "codex", "proveedor": "Ollama (local)", "modelo": "deepseek-coder:6.7b",
     "claves": ["deepseek-coder:6.7b", "deepseek-coder"], "tipo": "local",
     "limite": "local · sin cuota (fallback offline)", "req_dia": None},
]

# carpetas de productos por departamento (.json llevan el meta con llmCalls)
DIRS_RESEARCH = ["informes", "paneles", "cadenas", "refutaciones",
                 "correlaciones", "grafos", "memoria"]
DIRS_CODEX = ["piezas", "revisiones"]
_429 = re.compile(r"429|rate.?limit|too many|quota|exceeded", re.I)


def _aplanar_llmcalls(obj, acc):
    """Suma recursiva de {modelo: n} desde meta.llmCalls (que puede anidar
    {planner:{...}, coder:{...}})."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, (int, float)):
                acc[k] = acc.get(k, 0) + int(v)
            else:
                _aplanar_llmcalls(v, acc)
    elif isinstance(obj, list):
        for x in obj:
            _aplanar_llmcalls(x, acc)


_META_MD = re.compile(r"^meta:\s*(\{.*\})\s*$", re.M)


def _meta_de(path):
    """Extrae el meta de un producto: .json (research, clave 'meta') o de la
    linea 'meta: {...}' del .md (codex). Devuelve dict o None."""
    try:
        with open(path, encoding="utf-8") as f:
            texto = f.read()
    except OSError:
        return None
    if path.endswith(".json"):
        try:
            d = json.loads(texto)
        except ValueError:
            return None
        return d.get("meta", d) if isinstance(d, dict) else None
    m = _META_MD.search(texto)
    if m:
        try:
            return json.loads(m.group(1))
        except ValueError:
            return None
    return None


def uso_hoy():
    """Cuenta llamadas por modelo HOY y detecta 429, leyendo el meta de los
    productos. Agrupa por producto (base) prefiriendo .json, si no el .md,
    para no contar dos veces. Devuelve {llamadas, errores429}."""
    hoy = time.strftime("%Y%m%d")
    llamadas, err429 = {}, set()
    fuentes = [os.path.join(HOME, "research", d) for d in DIRS_RESEARCH]
    fuentes += [os.path.join(HOME, "codex", d) for d in DIRS_CODEX]
    for carpeta in fuentes:
        try:
            nombres = [n for n in os.listdir(carpeta) if n.startswith(hoy)]
        except OSError:
            continue
        bases = {}   # base -> mejor path (.json gana al .md)
        for n in nombres:
            if n.endswith(".json"):
                bases[n[:-5]] = os.path.join(carpeta, n)
            elif n.endswith(".md") and n[:-3] not in bases:
                bases[n[:-3]] = os.path.join(carpeta, n)
        for path in bases.values():
            meta = _meta_de(path)
            if not isinstance(meta, dict):
                continue
            if "llmCalls" in meta:
                _aplanar_llmcalls(meta["llmCalls"], llamadas)
            for e in meta.get("errors") or []:
                if isinstance(e, str) and _429.search(e):
                    low = e.lower()
                    for m in MODELOS:
                        if any(c.lower() in low for c in m["claves"]):
                            err429.add(m["modelo"])
    return {"llamadas": llamadas, "errores429": err429}


def _uso_de(m, llamadas):
    """Suma las llamadas de hoy que matcheen alguna clave del modelo."""
    total = 0
    for clave, n in llamadas.items():
        cl = clave.lower()
        if any(c.lower() == cl or c.lower() in cl for c in m["claves"]):
            total += n
    return total


def snapshot():
    u = uso_hoy()
    filas = []
    for m in MODELOS:
        usado = _uso_de(m, u["llamadas"])
        tuvo_429 = m["modelo"] in u["errores429"]
        if tuvo_429:
            estado = "rojo"
        elif m["tipo"] == "local":
            estado = "local"
        elif m["req_dia"] and usado >= m["req_dia"] * 0.8:
            estado = "ambar"
        else:
            estado = "verde"
        filas.append({
            "depto": m["depto"], "proveedor": m["proveedor"],
            "modelo": m["modelo"], "tipo": m["tipo"],
            "limite": m["limite"], "usado_hoy": usado,
            "req_dia": m["req_dia"], "estado": estado,
        })
    return {"ts": time.strftime("%Y-%m-%d %H:%M:%S"), "modelos": filas,
            "nota": "limites documentados del free tier (aprox., verificar en "
                    "la doc del proveedor); uso = llamadas de HOY contadas del "
                    "archivo, sin gastar API."}


def main():
    import sys
    snap = snapshot()
    if "--json" in sys.argv:
        print(json.dumps(snap, ensure_ascii=False, indent=1))
        return 0
    print("CUOTAS por modelo  (%s)\n" % snap["ts"])
    dep = None
    for f in snap["modelos"]:
        if f["depto"] != dep:
            dep = f["depto"]
            print("== %s ==" % dep.upper())
        print("  [%-5s] %-22s uso_hoy=%-3d  %s"
              % (f["estado"], f["modelo"], f["usado_hoy"], f["limite"]))
    print("\n%s" % snap["nota"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
