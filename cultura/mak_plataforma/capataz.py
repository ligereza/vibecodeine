#!/usr/bin/env python3
"""capataz.py -- el CAPATAZ de MAK: director autonomo con modelo gratis.

Un ciclo por corrida (cron repite el ciclo). Junta metricas deterministicas
(reusa junta.metricas()) -> pide UNA decision al modelo capaz gratis
(cerebras/groq/azure via research_lib.LLM) con un MENU ACOTADO de acciones
-> valida la respuesta contra el menu -> ejecuta el organo real
correspondiente (subprocess o HTTP) -> loguea en bitacora_capataz.jsonl +
eventos.jsonl. Nunca crasha: si el modelo esta caido o alucina una accion
fuera del menu, fallback seguro = "vetear" (revisor.py --enforce, no
inventa nada, solo mergea lo que el gate CI ya aprobo).

Ver CLAUDE.md (flujo): "el director emerge de (modelo capaz + loop
acotado + feedback), no de Claude". Este script es esa afirmacion hecha
codigo, corriendo en MAK (192.168.50.2), sin Claude en el loop.
"""
import datetime
import json
import os
import subprocess
import sys
import urllib.parse
import urllib.request

HOME = os.path.expanduser("~")
sys.path.insert(0, os.path.join(HOME, "research"))
sys.path.insert(0, os.path.join(HOME, "plataforma"))

try:
    from research_lib import LLM, emitir_evento, mint_job_id
except Exception:
    LLM = None
    emitir_evento = None
    mint_job_id = None

try:
    import junta
except Exception:
    junta = None

PLATAFORMA = os.path.join(HOME, "plataforma")
CODEX = os.path.join(HOME, "codex")
RESEARCH = os.path.join(HOME, "research")
BITACORA = os.path.join(PLATAFORMA, "bitacora_capataz.jsonl")
CAPATAZ_PATH = os.path.join(HOME, "flujo", "context", "CAPATAZ.md")
AJUSTES_JUNTA = os.path.join(PLATAFORMA, "ajustes_junta.json")
BACKLOG_CODEX_TXT = os.path.join(PLATAFORMA, "backlog_codex.txt")
REPO_SLUG = "ligereza/vibecodeine"

ACCIONES = ("investigar", "codificar", "entregar", "vetear",
            "mejora_libre", "reflexionar", "vigilar_proveedores", "descansar")

MENU_TXT = (
    "ACCIONES POSIBLES (elegi UNA, exactamente como aparece en \"accion\"):\n"
    "- investigar: args {\"tema\": str} -- dispara research nuevo (research:8890)\n"
    "- codificar: args {\"pedido\": str} -- pide una pieza de codigo nueva (codex:8891)\n"
    "- entregar: args {} -- entrega UNA pieza codex lista al repo (PR draft, entregar.py)\n"
    "- vetear: args {} -- revisa y mergea PRs capataz/ listos (revisor.py --enforce, gateado por CI)\n"
    "- mejora_libre: args {} -- el coder propone y codea su propia mejora (agente_libre.py)\n"
    "- reflexionar: args {} -- corre la junta diaria (metricas + reflexion, junta.py)\n"
    "- vigilar_proveedores: args {} -- detecta proveedores LLM cronicamente malos (expulsion.py)\n"
    "- descansar: args {\"motivo\": str} -- no-op, DESALENTADO, solo si de verdad no hay nada que hacer\n"
)


def _leer_json(ruta, default=None):
    try:
        with open(ruta, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


def _run(cmd, timeout=600):
    """Corre un organo como subprocess. Nunca lanza. Devuelve dict resumen."""
    try:
        r = subprocess.run(cmd, cwd=PLATAFORMA, capture_output=True,
                            text=True, timeout=timeout)
        return {
            "rc": r.returncode,
            "stdout_tail": (r.stdout or "").strip()[-800:],
            "stderr_tail": (r.stderr or "").strip()[-400:],
        }
    except subprocess.TimeoutExpired:
        return {"rc": -1, "error": "timeout tras %ss" % timeout}
    except Exception as e:  # noqa: BLE001 - un organo caido no debe tumbar el ciclo
        return {"rc": -1, "error": str(e)[:300]}


def _http_post_form(url, fields, timeout=10):
    data = urllib.parse.urlencode(fields).encode()
    req = urllib.request.Request(url, data=data, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return {"ok": True, "status": resp.status,
                    "body": resp.read().decode(errors="replace")[:400]}
    except Exception as e:  # noqa: BLE001 - HTTP a un organo local, nunca fatal
        return {"ok": False, "error": str(e)[:300]}


def _prs_capataz_abiertos():
    try:
        r = subprocess.run(["gh", "pr", "list", "--repo", REPO_SLUG,
                            "--state", "open", "--json", "headRefName"],
                           capture_output=True, text=True, timeout=30)
        if r.returncode != 0:
            return {"error": (r.stderr or "").strip()[:200]}
        prs = json.loads(r.stdout or "[]")
        capataz = [p for p in prs if p.get("headRefName", "").startswith("capataz/")]
        return {"total_abiertos": len(prs), "capataz_abiertos": len(capataz)}
    except Exception as e:  # noqa: BLE001
        return {"error": str(e)[:200]}


def gather_state():
    """Estado deterministico (0 LLM). Reusa junta.metricas() -- mismo
    calculo de salud/backlog/exito_24h/producidos_hoy que la junta diaria;
    no reinventamos el conteo."""
    if junta is not None:
        try:
            m = junta.metricas()
        except Exception as e:  # noqa: BLE001
            m = {"error": "junta.metricas() fallo: %s" % e}
    else:
        m = {"error": "junta.py no importable"}
    m["prs_abiertos"] = _prs_capataz_abiertos()
    m["ultima_decision_junta"] = _leer_json(AJUSTES_JUNTA)
    return m


def leer_capataz(max_chars=2500):
    try:
        with open(CAPATAZ_PATH, encoding="utf-8") as f:
            return f.read()[:max_chars]
    except OSError:
        return "(CAPATAZ.md no disponible)"


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


def pedir_decision(estado):
    """UNA llamada al modelo capaz. Devuelve (decision_dict|None, proveedor|None,
    motivo_falla|None). Nunca lanza."""
    if LLM is None:
        return None, None, "research_lib.LLM no importable"
    system = (
        leer_capataz()
        + "\n\n---\nSos el CAPATAZ, director autonomo de MAK. Con el estado "
        "del sistema en JSON que te doy, elegi la PROXIMA accion (SOLO JSON, "
        "sin texto extra, sin markdown, sin fences): "
        '{"accion": <una de la lista>, "args": {...}, "razon": "..."}.\n'
        + MENU_TXT +
        "Nunca elijas descansar si hay backlog pendiente (research o codex) o "
        "PRs capataz/ sin vetear. Si el estado trae error o proveedores caidos, "
        "elegi vetear (es seguro: solo mergea lo que CI ya aprobo) y decilo en razon."
    )
    user = json.dumps(estado, ensure_ascii=False, indent=2)
    try:
        llm = LLM("cerebras,groq,azure")
        texto, prov = llm.call(system, user, 500)
    except Exception as e:  # noqa: BLE001 - cadena entera caida
        return None, None, "cerebro caido: %s" % str(e)[:300]
    decision = _extraer_json(texto)
    if decision is None:
        return {"accion": None, "razon": "respuesta no parseable como JSON",
                "raw": texto[:600]}, prov, None
    return decision, prov, None


def validar(decision):
    if not isinstance(decision, dict):
        return False, "decision no es un dict"
    accion = decision.get("accion")
    if accion not in ACCIONES:
        return False, "accion invalida o ausente: %r" % (accion,)
    return True, None


def ejecutar(accion, args):
    args = args or {}
    if accion == "investigar":
        tema = str(args.get("tema") or "").strip()[:300]
        if not tema:
            return {"ok": False, "error": "tema vacio"}
        return _http_post_form("http://127.0.0.1:8890/run",
                                {"tema": tema, "modo": "research", "densidad": "medio"})
    if accion == "codificar":
        pedido = str(args.get("pedido") or "").strip()[:2000]
        if not pedido:
            return {"ok": False, "error": "pedido vacio"}
        r = _http_post_form("http://127.0.0.1:8891/run",
                             {"pedido": pedido, "modo": "generar", "densidad": "medio"})
        if not r.get("ok"):
            try:
                with open(BACKLOG_CODEX_TXT, "a", encoding="utf-8") as f:
                    f.write(pedido + "\n")
                r["fallback"] = "http caido -- appendido a backlog_codex.txt"
            except OSError as e:
                r["fallback_error"] = str(e)[:200]
        return r
    if accion == "entregar":
        return _run(["python3", os.path.join(PLATAFORMA, "entregar.py"), "--limit", "1"])
    if accion == "vetear":
        return _run(["python3", os.path.join(PLATAFORMA, "revisor.py"), "--enforce"])
    if accion == "mejora_libre":
        return _run(["python3", os.path.join(CODEX, "agente_libre.py")], timeout=900)
    if accion == "reflexionar":
        return _run(["python3", os.path.join(PLATAFORMA, "junta.py")], timeout=300)
    if accion == "vigilar_proveedores":
        return _run(["python3", os.path.join(RESEARCH, "expulsion.py")])
    if accion == "descansar":
        return {"ok": True, "motivo": args.get("motivo") or "(sin motivo)"}
    return {"ok": False, "error": "accion sin ejecutor: %s" % accion}


def _resumen_resultado(resultado):
    if not isinstance(resultado, dict):
        return str(resultado)[:300]
    if "stdout_tail" in resultado or "stderr_tail" in resultado:
        texto = (resultado.get("stdout_tail") or resultado.get("stderr_tail") or "").strip()
        return (texto[-300:] if texto else "rc=%s" % resultado.get("rc"))
    return json.dumps(resultado, ensure_ascii=False)[:300]


def log_bitacora(entry):
    try:
        os.makedirs(PLATAFORMA, exist_ok=True)
        with open(BITACORA, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except OSError:
        pass
    if emitir_evento is not None:
        try:
            jid = mint_job_id() if mint_job_id is not None else entry["ts"].replace(" ", "T")
            emitir_evento("plataforma", jid, "CAPATAZ",
                          accion=entry.get("accion"),
                          proveedor=entry.get("proveedor_decisor"),
                          razon=(entry.get("razon") or "")[:200])
        except Exception:
            pass


def ciclo():
    estado_previo = gather_state()
    decision, proveedor, motivo_falla = pedir_decision(estado_previo)
    fallback_usado = False
    if motivo_falla:
        decision = {"accion": "vetear", "razon": motivo_falla}
        fallback_usado = True
    else:
        ok, err = validar(decision)
        if not ok:
            decision = {"accion": "vetear",
                        "razon": "fallback (%s) -- crudo del modelo: %s" %
                                 (err, json.dumps(decision, ensure_ascii=False)[:250])}
            fallback_usado = True
    accion = decision.get("accion")
    razon = decision.get("razon", "")
    args = decision.get("args", {})
    try:
        resultado = ejecutar(accion, args)
    except Exception as e:  # noqa: BLE001 - un organo roto no tumba el ciclo
        resultado = {"ok": False, "error": "ejecutar() exploto: %s" % str(e)[:300]}
    entry = {
        "ts": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "proveedor_decisor": proveedor or "ninguno",
        "accion": accion,
        "razon": razon,
        "fallback_usado": fallback_usado,
        "resultado_resumen": _resumen_resultado(resultado),
        "estado_previo": {
            "backlog": estado_previo.get("backlog"),
            "prs_abiertos": estado_previo.get("prs_abiertos"),
            "producidos_hoy": estado_previo.get("producidos_hoy"),
        },
    }
    log_bitacora(entry)
    return entry


def main():
    entry = ciclo()
    print(json.dumps(entry, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
