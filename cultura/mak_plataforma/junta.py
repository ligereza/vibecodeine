#!/usr/bin/env python3
"""junta.py -- junta diaria de MAK (advisory, non-mutating).

Lee salud/backlog/jobs, arma metricas, hace UNA llamada al modelo capaz
(CAPATAZ.md como voz de presion) y escribe una reflexion + ajustes
propuestos. NO edita roles.py, NO toca servicios vivos, NO abre/mergea
PRs, NO ejecuta codigo autogenerado. Stdlib-only + research_lib.
"""
import datetime
import json
import os
import sys

HOME = os.path.expanduser("~")
sys.path.insert(0, os.path.join(HOME, "research"))
sys.path.insert(0, os.path.join(HOME, "plataforma"))

try:
    import salud as salud_mod
except Exception:
    salud_mod = None

try:
    from research_lib import LLM
except Exception:
    LLM = None

CAPATAZ_PATH = os.path.join(HOME, "flujo", "context", "CAPATAZ.md")
SALUD_PROVEEDORES_PATH = os.path.join(HOME, "research", "salud_proveedores.json")
BACKLOG_RESEARCH_PATH = os.path.join(HOME, "plataforma", "backlog.jsonl")
BACKLOG_CODEX_PATH = os.path.join(HOME, "plataforma", "backlog_codex.txt")
CODEX_JOBS_PATH = os.path.join(HOME, "codex", "jobs.jsonl")
RESEARCH_JOBS_PATH = os.path.join(HOME, "research", "jobs.jsonl")
REFLEXIONES_DIR = os.path.join(HOME, "plataforma", "reflexiones")
AJUSTES_PATH = os.path.join(HOME, "plataforma", "ajustes_junta.json")


def _leer_json(ruta, default=None):
    try:
        with open(ruta, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


def _leer_jsonl(ruta):
    filas = []
    try:
        with open(ruta, encoding="utf-8") as f:
            for linea in f:
                linea = linea.strip()
                if not linea:
                    continue
                try:
                    filas.append(json.loads(linea))
                except ValueError:
                    continue
    except OSError:
        pass
    return filas


def _job_dt(job):
    """Fecha/hora real de un job a partir de job_id (YYYYMMDD-HHMMSS-hex)
    + campo 't' (HH:MM:SS). None si falta job_id o no parsea (jobs
    legacy sin job_id quedan fuera del calculo de 24h)."""
    jid = job.get("job_id")
    t = job.get("t")
    if not jid or not t or len(jid) < 8:
        return None
    fecha = jid[:8]
    try:
        return datetime.datetime.strptime(fecha + t, "%Y%m%d%H:%M:%S")
    except ValueError:
        return None


def salud_proveedores():
    """Resumen de salud por proveedor: pct de exito sobre intentos totales
    en la ventana registrada por research_lib (salud_proveedores.json)."""
    data = _leer_json(SALUD_PROVEEDORES_PATH, {}) or {}
    proveedores = data.get("proveedores", {})
    resumen = {}
    for nombre, c in proveedores.items():
        total = sum(c.get(k, 0) for k in ("successes", "timeouts", "api_errors", "errors"))
        exitos = c.get("successes", 0)
        pct = round(100.0 * exitos / total, 1) if total else None
        resumen[nombre] = {"exitos": exitos, "intentos": total, "pct_exito": pct}
    return resumen


def backlog_pendientes():
    filas = _leer_jsonl(BACKLOG_RESEARCH_PATH)
    por_estado = {}
    for f in filas:
        e = f.get("estado", "?")
        por_estado[e] = por_estado.get(e, 0) + 1
    pendientes_research = sum(v for k, v in por_estado.items() if k != "listo" and k != "cerrado")
    try:
        with open(BACKLOG_CODEX_PATH, encoding="utf-8") as f:
            lineas_codex = [l for l in f if l.strip() and not l.strip().startswith("#")]
    except OSError:
        lineas_codex = []
    return {
        "research_por_estado": por_estado,
        "research_pendientes": pendientes_research,
        "codex_pendientes": len(lineas_codex),
    }


def _tasa_exito_24h(jobs):
    ahora = datetime.datetime.now()
    hace_24h = ahora - datetime.timedelta(hours=24)
    por_modo = {}
    for j in jobs:
        dt = _job_dt(j)
        if dt is None or dt < hace_24h:
            continue
        modo = j.get("modo", "?")
        s = por_modo.setdefault(modo, {"total": 0, "listo": 0})
        s["total"] += 1
        if j.get("estado") == "listo":
            s["listo"] += 1
    for modo, s in por_modo.items():
        s["pct_exito"] = round(100.0 * s["listo"] / s["total"], 1) if s["total"] else None
    return por_modo


def _producidos_hoy(jobs):
    hoy = datetime.date.today().strftime("%Y%m%d")
    total = 0
    for j in jobs:
        jid = j.get("job_id") or ""
        if jid[:8] == hoy and j.get("estado") == "listo":
            total += 1
    return total


def metricas():
    codex_jobs = _leer_jsonl(CODEX_JOBS_PATH)
    research_jobs = _leer_jsonl(RESEARCH_JOBS_PATH)
    m = {
        "ts": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "salud_proveedores": salud_proveedores(),
        "backlog": backlog_pendientes(),
        "exito_24h": {
            "codex": _tasa_exito_24h(codex_jobs),
            "research": _tasa_exito_24h(research_jobs),
        },
        "producidos_hoy": {
            "codex": _producidos_hoy(codex_jobs),
            "research": _producidos_hoy(research_jobs),
        },
    }
    if salud_mod is not None:
        try:
            snap = salud_mod.snapshot()
            m["salud_sistema"] = {
                "load": snap.get("load"),
                "mem_disponible_mb": snap.get("mem_disponible_mb"),
                "disco_libre_gb": snap.get("disco_libre_gb"),
                "servicios": snap.get("servicios"),
                "productos": snap.get("productos"),
            }
        except Exception as e:
            m["salud_sistema"] = {"error": "salud.snapshot() fallo: %s" % e}
    else:
        m["salud_sistema"] = {"error": "no se pudo importar salud.py"}
    return m


def leer_capataz(max_chars=2500):
    try:
        with open(CAPATAZ_PATH, encoding="utf-8") as f:
            texto = f.read()
    except OSError:
        texto = "(CAPATAZ.md no disponible)"
    return texto[:max_chars]


def pedir_decision(m):
    """UNA llamada al modelo capaz. Devuelve (decision_dict, proveedor) o
    (None, None) si todos los proveedores fallan. Nunca lanza."""
    if LLM is None:
        return None, None
    system = (
        leer_capataz()
        + "\n\n---\nSos la junta diaria de MAK. NO digas 'todo verde'. Con "
        "estos datos, decidi en JSON (solo el JSON, sin texto extra): "
        '{"estado_general": "...", "riesgo_principal": "...", '
        '"proveedor_a_vigilar": "...", "prioridad_manana": "...", '
        '"accion_concreta": "..."}. accion_concreta DEBE ser algo que MAK ejecute con sus propias herramientas (cron, backlog_codex, cadena de proveedores, ajustes_junta.json); NADA de convocar humanos, reuniones, tickets a terceros ni ETAs inventadas -- solo acciones de maquina reales. Se honesto, sin maquillaje.'
    )
    user = json.dumps(m, ensure_ascii=False, indent=2)
    try:
        llm = LLM("azure,cerebras,groq")
        texto, prov = llm.call(system, user, 900)
    except Exception as e:
        return None, None
    decision = _extraer_json(texto)
    if decision is None:
        decision = {"estado_general": "(respuesta no parseable como JSON)",
                    "raw": texto[:1500]}
    return {"decision": decision, "proveedor": prov, "raw": texto}, prov


def _extraer_json(texto):
    texto = (texto or "").strip()
    inicio = texto.find("{")
    fin = texto.rfind("}")
    if inicio == -1 or fin == -1 or fin < inicio:
        return None
    try:
        return json.loads(texto[inicio:fin + 1])
    except ValueError:
        return None


def escribir_reflexion(m, resultado):
    os.makedirs(REFLEXIONES_DIR, exist_ok=True)
    fecha = datetime.date.today().strftime("%Y%m%d")
    ruta = os.path.join(REFLEXIONES_DIR, "junta_%s.md" % fecha)
    lines = []
    lines.append("# Junta MAK -- %s" % m["ts"])
    lines.append("")
    lines.append("## Metricas")
    lines.append("")
    lines.append("### Salud proveedores LLM")
    for nombre, s in m["salud_proveedores"].items():
        lines.append("- %s: %s/%s exitos (%s%%)" % (
            nombre, s["exitos"], s["intentos"],
            s["pct_exito"] if s["pct_exito"] is not None else "?"))
    if not m["salud_proveedores"]:
        lines.append("- (sin datos de salud_proveedores.json)")
    lines.append("")
    lines.append("### Backlog pendiente")
    b = m["backlog"]
    lines.append("- research: %d pendientes (%s)" % (
        b["research_pendientes"], b["research_por_estado"]))
    lines.append("- codex: %d tareas pendientes" % b["codex_pendientes"])
    lines.append("")
    lines.append("### Tasa de exito 24h")
    for depto, por_modo in m["exito_24h"].items():
        lines.append("- %s:" % depto)
        if not por_modo:
            lines.append("  - (sin jobs en las ultimas 24h)")
        for modo, s in por_modo.items():
            lines.append("  - %s: %d/%d listo (%s%%)" % (
                modo, s["listo"], s["total"],
                s["pct_exito"] if s["pct_exito"] is not None else "?"))
    lines.append("")
    lines.append("### Producidos hoy")
    lines.append("- codex: %d" % m["producidos_hoy"]["codex"])
    lines.append("- research: %d" % m["producidos_hoy"]["research"])
    lines.append("")
    sistema = m.get("salud_sistema", {})
    if "error" not in sistema:
        lines.append("### Sistema")
        lines.append("- load: %s" % sistema.get("load"))
        lines.append("- mem disponible mb: %s" % sistema.get("mem_disponible_mb"))
        lines.append("- disco libre gb: %s" % sistema.get("disco_libre_gb"))
        servicios_caidos = [n for n, s in (sistema.get("servicios") or {}).items()
                            if not s.get("vivo")]
        lines.append("- servicios caidos: %s" % (servicios_caidos or "ninguno"))
        lines.append("")
    lines.append("## Decision de la junta")
    lines.append("")
    if resultado is None:
        lines.append("sin decision del modelo (proveedores caidos)")
    else:
        lines.append("Proveedor que respondio: %s" % resultado["proveedor"])
        lines.append("")
        lines.append("```json")
        lines.append(json.dumps(resultado["decision"], ensure_ascii=False, indent=2))
        lines.append("```")
    contenido = "\n".join(lines) + "\n"
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(contenido)
    return ruta


def escribir_ajustes(m, resultado):
    ajustes = {
        "ts": m["ts"],
        "proveedor": resultado["proveedor"] if resultado else None,
        "decision": resultado["decision"] if resultado else None,
        "nota": ("advisory unicamente -- nada lee esto automaticamente aun"
                 if resultado else "sin decision del modelo (proveedores caidos)"),
    }
    with open(AJUSTES_PATH, "w", encoding="utf-8") as f:
        json.dump(ajustes, f, ensure_ascii=False, indent=2)
    return AJUSTES_PATH


def main():
    m = metricas()
    try:
        resultado, _prov = pedir_decision(m)
    except Exception:
        resultado = None
    ruta_md = escribir_reflexion(m, resultado)
    ruta_json = escribir_ajustes(m, resultado)
    print("reflexion: %s" % ruta_md)
    print("ajustes: %s" % ruta_json)
    if resultado:
        print("proveedor: %s" % resultado["proveedor"])
    else:
        print("proveedor: ninguno (sin decision del modelo)")


if __name__ == "__main__":
    main()
