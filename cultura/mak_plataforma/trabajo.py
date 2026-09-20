#!/usr/bin/env python3
"""trabajo.py -- el orquestador del trabajo autonomo del organismo MAK.

El cron lo dispara cada CADA_MIN. En cada tick hace UNA unidad de trabajo,
ciclando los verbos de roles.py por round-robin, con topes de carga/cupo/gap.
La cola real manda primero; si no hay trabajo productivo, los verbos idle
revisan, discuten, refutan o exponen en vez de fabricar mas ensayos. El ritmo
se adapta a la red: offline (local serial y lento) se espacia mas. El fallback
nube<->local lo maneja red_ok() dentro de las libs de cada departamento; aca
 solo se decide QUE y CUANDO, y se despacha por HTTP a los servicios internos
Research/Codex en loopback. La superficie humana y la delegacion remota pasan
por el Hub.

Apagar: quitar la linea MAK-TRABAJO del crontab.
Ajustar ritmo/verbos/modulos/semillas: editar roles.py.
"""
import json
import os
import sys
import tempfile
import threading
import time
import urllib.parse
import urllib.request
from contextlib import contextmanager

try:
    import fcntl
except ImportError:  # pragma: no cover - Windows director has no fcntl
    fcntl = None

HOME = os.path.expanduser("~")
sys.path.insert(0, os.path.join(HOME, "plataforma"))
sys.path.insert(0, os.path.join(HOME, "research"))
_DIR = os.path.dirname(os.path.abspath(__file__))
for _cand in (os.path.join(_DIR, "..", "mak_research"),
              os.path.join(_DIR, "..", "research")):
    if os.path.isdir(_cand) and _cand not in sys.path:
        sys.path.insert(0, _cand)
try:
    from cultura.mak_conductor.runtime import (active_enabled, dispatch_sync,
                                                enqueue_shadow,
                                                observe_shadow)
except ImportError:
    sys.path.insert(0, os.environ.get("MAK_CONDUCTOR_PATH",
                                     "/home/mak/cultura"))
    try:
        from mak_conductor.runtime import (active_enabled, dispatch_sync,
                                           enqueue_shadow,
                                           observe_shadow)
    except ImportError:
        enqueue_shadow = dispatch_sync = None
        def active_enabled():
            return False
        observe_shadow = None
import roles  # noqa: E402
try:
    import research_router  # noqa: E402
except Exception:  # noqa: BLE001 - legacy deployment without the new router
    research_router = None
try:
    from research_lib import red_ok  # comparte la deteccion de red
except Exception:  # noqa: BLE001 - si falla, asumimos online
    def red_ok():
        return True
    def _es_pregunta_factual(_topic):
        return False
else:
    try:
        from research_lib import _es_pregunta_factual  # noqa: E402
    except Exception:  # noqa: BLE001 - format routing degrades to verb routing
        def _es_pregunta_factual(_topic):
            return False
try:
    import backlog  # noqa: E402
    try:
        import material  # noqa: E402
    except Exception:
        material = None
except Exception:
    backlog = None

STATE = os.path.join(HOME, "plataforma/.trabajo_state.json")
LOG = os.path.join(HOME, "plataforma/logs/trabajo.log")
IDLE_AUDIT = os.path.join(HOME, "plataforma/idle_decisions.jsonl")
IDLE_LEDGER_REVIEWS = os.path.join(HOME, "plataforma/idle_ledger_reviews.jsonl")
IDLE_BENCHMARK_REVIEWS = os.path.join(HOME, "plataforma/idle_benchmark_reviews.jsonl")
IDLE_MEMORY_AUDITS = os.path.join(HOME, "plataforma/idle_memory_audits.jsonl")
IDLE_CURATORIA_REVIEWS = os.path.join(HOME, "plataforma/idle_curatoria_reviews.jsonl")
BENCHMARK = os.path.join(HOME, "plataforma/corpus_benchmark.json")
CORPUS_REVIEW_LOG = os.path.join(HOME, "plataforma/corpus_reviews.jsonl")
COMMON_LEDGER = os.path.join(HOME, "plataforma/common_ledger.jsonl")
BACKLOG = os.path.join(HOME, "plataforma/backlog_codex.txt")
SEMILLAS_F = os.path.join(HOME, "plataforma/semillas_latido.txt")
RESEARCH = "http://127.0.0.1:8890/run"
CODEX = "http://127.0.0.1:8891/run"
BACKLOG_GEN = os.path.join(HOME, "plataforma/backlog.jsonl")
INFORMES_DIRS = [os.path.join(HOME, "research", d) for d in ("informes", "cadenas", "paneles", "refutaciones", "grafos", "memoria")]
CORPUS_REVIEW_EVERY = max(1, int(os.environ.get("MAK_CORPUS_REVIEW_EVERY", 4)))
CURATORIA_BATCH_SIZE = max(1, int(os.environ.get("MAK_CURATORIA_BATCH_SIZE", 3)))
# nota: dirs que no existen son saltados por cosechar
_RUN_LOCK = threading.RLock()


@contextmanager
def _exclusive_run_lock():
    """Prevent two work ticks from dispatching the same unit."""
    with _RUN_LOCK:
        lock_path = os.path.abspath(STATE) + ".lock"
        os.makedirs(os.path.dirname(lock_path), exist_ok=True)
        fd = os.open(lock_path, os.O_CREAT | os.O_RDWR, 0o600)
        try:
            if fcntl is not None:
                fcntl.flock(fd, fcntl.LOCK_EX)
            yield
        finally:
            if fcntl is not None:
                fcntl.flock(fd, fcntl.LOCK_UN)
            os.close(fd)


def log(m):
    try:
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(m + "\n")
    except OSError:
        pass


def _append_jsonl(path, row):
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    except OSError:
        pass


def _read_jsonl(path, limit=500):
    rows = []
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                try:
                    row = json.loads(line)
                except ValueError:
                    continue
                if isinstance(row, dict):
                    rows.append(row)
    except OSError:
        return []
    return rows[-max(0, int(limit)):]


def _read_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            value = json.load(f)
        return value
    except (OSError, ValueError):
        return None


def load1():
    try:
        return os.getloadavg()[0]
    except (OSError, AttributeError):
        return 0.0


def _state():
    try:
        with open(STATE) as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def _save(s):
    temp_path = None
    try:
        os.makedirs(os.path.dirname(STATE), exist_ok=True)
        with tempfile.NamedTemporaryFile(
                "w", encoding="utf-8", dir=os.path.dirname(STATE),
                prefix=".trabajo-state-", suffix=".tmp", delete=False) as f:
            temp_path = f.name
            json.dump(s, f)
            f.flush()
            os.fsync(f.fileno())
        os.replace(temp_path, STATE)
        temp_path = None
    except OSError:
        pass
    finally:
        if temp_path:
            try:
                os.unlink(temp_path)
            except OSError:
                pass


def _lineas(path, fallback):
    try:
        with open(path, encoding="utf-8") as f:
            xs = [x.strip() for x in f if x.strip() and not x.startswith("#")]
        return xs or fallback
    except OSError:
        return fallback


def _has_pending_material():
    if material is None:
        return False
    try:
        return any(r.get("estado") == "pendiente" for r in material.cargar())
    except Exception:  # noqa: BLE001 - idle review must degrade safely
        return False


def _has_pending_research_backlog():
    if backlog is None:
        return False
    try:
        return any(e.get("estado") == "pendiente"
                   for e in backlog.cargar(BACKLOG_GEN))
    except Exception:  # noqa: BLE001 - idle review must degrade safely
        return False


def _has_pending_codex_backlog():
    return bool(_lineas(BACKLOG, []))


def _pending_snapshot():
    return {
        "material": _has_pending_material(),
        "research_backlog": _has_pending_research_backlog(),
        "codex_backlog": _has_pending_codex_backlog(),
    }


def _memory_audit_data():
    if backlog is None or not hasattr(backlog, "auditar_memoria"):
        return {}
    try:
        return backlog.auditar_memoria(INFORMES_DIRS, BACKLOG_GEN)
    except Exception:  # noqa: BLE001 - memory audit cannot stop MAK
        return {}


def _memory_requires_review():
    data = _memory_audit_data()
    return bool(data.get("bloquea_produccion", False))


def _iskvw_campo_path():
    """Return the deployed archive projection only when MAK can see it.

    The Windows checkout is not MAK's source of truth. Requiring the explicit
    box path (or the real Linux deployment path) prevents the local director
    from silently curating a stale copy and keeps this idle lane inert in
    repository-only tests.
    """
    roots = []
    configured = os.environ.get("MAK_REPO_ROOT", "").strip()
    if configured:
        roots.append(configured)
    if os.path.isdir("/home/mak/flujo"):
        roots.append("/home/mak/flujo")
    for root in roots:
        path = os.path.join(root, "iskvw", "datos", "campo.json")
        if os.path.isfile(path):
            return path
    return ""


def _iskvw_curation_payload(st):
    """Queue a small critical reading from MAK's real artwork corpus.

    This is deliberately a research payload, not a publication step. The
    selected records carry machine perception and media paths; the research
    service must produce reading, selection, relationships and public_status.
    A batch is marked seen only after the remote work succeeds, so a failed
    model cannot erase a work from the queue.
    """
    path = _iskvw_campo_path()
    if not path:
        return None
    datos = _read_json(path)
    piezas = [p for p in (datos or {}).get("piezas", [])
              if p.get("tipo") == "obra" and p.get("id") and p.get("archivo")]
    if not piezas:
        return None
    seen = set(st.get("curatoria_seen", [])[-500:])
    inflight = st.get("curatoria_inflight", [])
    seleccion = [p for p in piezas
                 if p["id"] not in seen and p["id"] not in inflight]
    if not seleccion:
        return None
    seleccion = seleccion[:CURATORIA_BATCH_SIZE]
    ids = [p["id"] for p in seleccion]
    st["curatoria_inflight"] = ids
    tema = ("curatoria critica local de obras propias: separar descripcion "
            "percibida, interpretacion, debilidades y decision de archivo "
            "sin publicar automaticamente")
    return {
        "modo": "curation_review",
        "formato": "curatoria",
        "densidad": "medio",
        "tema": tema,
        "source_path": path,
        "selection": seleccion,
        "review_ids": ids,
        "output_contract": contract_for_task("multiplicar", tema),
        "work_contract": work_contract("multiplicar", tema),
    }


def _finish_curatoria_review(st, payload, accepted):
    ids = list(payload.get("review_ids") or [])
    if accepted and ids:
        seen = list(st.get("curatoria_seen", []))
        st["curatoria_seen"] = (seen + ids)[-500:]
    if st.get("curatoria_inflight") == ids:
        st.pop("curatoria_inflight", None)


def _corpus_files():
    """Return reviewable reports without duplicating the research pipeline."""
    files = []
    for directory in INFORMES_DIRS:
        try:
            names = os.listdir(directory)
        except OSError:
            continue
        for name in names:
            if not name.lower().endswith((".md", ".txt")):
                continue
            path = os.path.join(directory, name)
            if os.path.isfile(path):
                files.append(path)
    return sorted(files, key=lambda path: (os.path.getmtime(path), path))


def _corpus_review_id(path):
    try:
        stat = os.stat(path)
        return "%s:%d:%d" % (path, stat.st_mtime_ns, stat.st_size)
    except OSError:
        return path


def _corpus_review_payload(st, verbo="multiplicar"):
    """Select one old report for review, retaining retryability on failure."""
    seen = set(st.get("corpus_review_seen", [])[-500:])
    inflight = st.get("corpus_review_inflight", "")
    for path in _corpus_files():
        review_id = _corpus_review_id(path)
        if review_id in seen or review_id == inflight:
            continue
        st["corpus_review_inflight"] = review_id
        topic = "revisar informe MAK antes de producir mas: %s" % os.path.basename(path)
        return {
            "modo": "research",
            "formato": "revision",
            "densidad": "corto",
            "tema": topic,
            "source_path": path,
            "review_id": review_id,
            "output_contract": contract_for_task(verbo, topic),
            "work_contract": work_contract(verbo, topic),
        }
    return None


def _finish_corpus_review(st, payload, accepted):
    review_id = payload.get("review_id", "")
    if not review_id:
        return
    if accepted:
        seen = list(st.get("corpus_review_seen", []))
        st["corpus_review_seen"] = (seen + [review_id])[-500:]
    if st.get("corpus_review_inflight") == review_id:
        st.pop("corpus_review_inflight", None)


def _should_review_corpus(st):
    if st.get("count", 0) <= 0 or st.get("count", 0) % CORPUS_REVIEW_EVERY:
        return False
    return bool(_corpus_files())


def _idle_review_topic(st):
    return _idle_node_payload("repasar", st)["tema"]


def _idle_review_allowed():
    pending = _pending_snapshot()
    return not any(pending.values()) or _memory_requires_review()


def _is_idle_verbo(verbo):
    return verbo in IDLE_NODES


def _seed_fallback_enabled():
    return os.environ.get("MAK_SEED_FALLBACK", "0").lower() in (
        "1", "true", "yes", "on")


IDLE_NODES = {
    "repasar": {
        "modo": "research",
        "formato": "revision",
        "densidad": "corto",
        "temas": [
            "revision operativa de los ultimos informes MAK: detectar formato equivocado, fuentes debiles y acciones ejecutivas",
            "revision de cola y autonomia MAK: distinguir research, curatoria, codex, discusion y exposicion",
            "revision de calidad MAK: que trabajos deben archivarse, refutarse o exponerse antes de producir mas",
        ],
    },
    "discutir": {
        "modo": "panel",
        "densidad": "corto",
        "n": "1",
        "temas": [
            "discusion ejecutiva: cuando MAK debe investigar, revisar, exponer o archivar en vez de producir mas",
            "discusion critica: limites entre iskvw public archive, research lane y RD primary-source work",
        ],
    },
    "refutar": {
        "modo": "refutar",
        "densidad": "corto",
        "temas": [
            "refutar la tesis: los ultimos informes MAK son confiables como corpus de verdad",
            "refutar la tesis: mas autonomia MAK significa producir mas documentos",
        ],
    },
    "exponer": {
        "modo": "research",
        "formato": "exposicion",
        "densidad": "corto",
        "temas": [
            "exponer para lectura humana que aprendio MAK de sus ultimos hallazgos sin convertirlo en informe ni ensayo",
            "exponer una curatoria breve de cabos sueltos MAK separando evidencia, interpretacion y usos posibles",
        ],
    },
}


def _idle_node_payload(verbo, st):
    node = IDLE_NODES.get(verbo)
    if not node:
        return None
    if verbo == "repasar":
        benchmark_payload = _benchmark_review_payload(st)
        if benchmark_payload:
            return benchmark_payload
        ledger_payload = _idle_ledger_review_payload(st)
        if ledger_payload:
            return ledger_payload
        memory_payload = _memory_review_payload(st)
        if memory_payload:
            return memory_payload
        curatoria_payload = _iskvw_curation_payload(st)
        if curatoria_payload:
            return curatoria_payload
    topics = node["temas"]
    key = "idle_%s_idx" % verbo
    i = st.get(key, 0) % len(topics)
    st[key] = i + 1
    payload = {"modo": node["modo"], "tema": topics[i],
               "densidad": node.get("densidad", "corto")}
    if node.get("formato"):
        payload["formato"] = node["formato"]
    if node.get("n"):
        payload["n"] = node["n"]
    return payload


def _benchmark_review_payload(st):
    """Pick one benchmark defect for no-cost local queue review."""
    data = _read_json(BENCHMARK)
    if not isinstance(data, dict):
        return None
    seen = set(st.get("benchmark_seen", [])[-500:])
    priority = {"route_format_mismatch": 0,
                "essay_structural_gaps": 1,
                "missing_or_unknown_format": 2}
    queue = sorted(data.get("queue") or data.get("issues") or [],
                   key=lambda item: priority.get(item.get("kind"), 9))
    for issue in queue:
        key = "%s:%s" % (issue.get("kind", ""), issue.get("path", ""))
        if not issue.get("path") or key in seen:
            continue
        st["benchmark_seen"] = (list(seen) + [key])[-500:]
        return {
            "modo": "benchmark_review",
            "formato": "benchmark",
            "densidad": "corto",
            "tema": "benchmark: %s" % issue.get("path"),
            "benchmark_key": key,
            "benchmark_kind": issue.get("kind", ""),
            "benchmark_action": issue.get("next_action", "manual_review"),
            "benchmark_path": issue.get("path", ""),
            "benchmark_declared": issue.get("declared", ""),
            "benchmark_expected": issue.get("expected", ""),
            "benchmark_topic": issue.get("topic", ""),
        }
    return None


def _memory_review_payload(st):
    """Queue one deterministic memory audit before more generated research."""
    data = _memory_audit_data()
    if data.get("accion") != "revisar_memoria":
        return None
    signature = "%s:%s:%s:%s:%s" % (
        data.get("entradas", 0), len(data.get("slugs_duplicados", [])),
        len(data.get("slugs_colision_prefijo", [])),
        len(data.get("origenes_faltantes", [])),
        len(data.get("entidades_bloqueadas", [])),
    )
    if signature in set(st.get("memory_audit_seen", [])[-100:]):
        return None
    st["memory_audit_seen"] = (list(st.get("memory_audit_seen", [])) +
                               [signature])[-100:]
    return {
        "modo": "memory_audit",
        "formato": "ledger",
        "densidad": "corto",
        "tema": "auditoria determinista de memoria MAK",
        "memory_signature": signature,
        "memory_audit": data,
    }


def _idle_ledger_review_payload(st):
    """Pick one pending ledger item for no-cost idle introspection."""
    seen = set(st.get("idle_ledger_seen", [])[-200:])
    opportunities = []
    candidates = []
    for row in _read_jsonl(COMMON_LEDGER):
        if row.get("metadata", {}).get("queue_status") == "pending_human":
            row_id = row.get("id") or ""
            if row_id and row_id not in seen:
                opportunities.append(row)
        if row.get("type") == "reject" or row.get("confidence") == "low":
            row_id = row.get("id") or ""
            if row_id and row_id not in seen:
                candidates.append(row)
    if opportunities:
        def priority(row):
            value = row.get("metadata", {}).get("priority_score", 0)
            try:
                value = int(value)
            except (TypeError, ValueError):
                value = 0
            return value
        row = sorted(enumerate(opportunities),
                     key=lambda pair: (priority(pair[1]), pair[0]),
                     reverse=True)[0][1]
    elif candidates:
        row = candidates[-1]
    else:
        return None
    row_id = row.get("id") or ""
    st["idle_ledger_seen"] = (list(seen) + [row_id])[-200:]
    return {
        "modo": "ledger_review",
        "formato": "ledger",
        "densidad": "corto",
        "tema": "ledger pending: %s" % str(row.get("claim") or "")[:180],
        "ledger_id": row_id,
        "domain": row.get("domain", ""),
        "lane": row.get("lane", "sistema"),
        "decision": row.get("decision", "revisar"),
        "purpose": row.get("purpose", ""),
        "owner": row.get("owner", "MAK"),
        "action": row.get("action", ""),
        "reason": (row.get("reject_reason", "") or
                   row.get("metadata", {}).get("next_action", "")),
        "source": row.get("source", ""),
    }


def _run_local_idle(payload):
    """Execute a local idle unit without calling research/codex or spending LLM."""
    if payload.get("modo") == "memory_audit":
        data = payload.get("memory_audit", {})
        row = {
            "ts": time.strftime("%F %T"),
            "schema": "mak-idle-memory-audit-v1",
            "signature": payload.get("memory_signature", ""),
            "action": data.get("accion", ""),
            "entries": data.get("entradas", 0),
            "states": data.get("estados", {}),
            "duplicate_slugs": data.get("slugs_duplicados", []),
            "prefix_slug_collisions": data.get(
                "slugs_colision_prefijo", []),
            "missing_origins": data.get("origenes_faltantes", []),
            "historical_missing_origins": data.get(
                "origenes_historicos_ausentes", []),
            "blocked_entities": data.get("entidades_bloqueadas", []),
            "blocks_production": data.get("bloquea_produccion", False),
            "next_action": (
                "repair historical references without blocking production"
                if not data.get("bloquea_produccion") else
                "classify critical gaps before producing more research"
            ),
        }
        _append_jsonl(IDLE_MEMORY_AUDITS, row)
        return json.dumps({"ok": True, "local": True,
                           "mode": "memory_audit",
                           "signature": row["signature"]})
    if payload.get("modo") == "benchmark_review":
        row = {
            "ts": time.strftime("%F %T"),
            "schema": "mak-idle-benchmark-review-v1",
            "benchmark_key": payload.get("benchmark_key", ""),
            "kind": payload.get("benchmark_kind", ""),
            "path": payload.get("benchmark_path", ""),
            "declared": payload.get("benchmark_declared", ""),
            "expected": payload.get("benchmark_expected", ""),
            "topic": payload.get("benchmark_topic", ""),
            "next_action": payload.get("benchmark_action", "manual_review"),
            "status": "queued_for_repair",
        }
        _append_jsonl(IDLE_BENCHMARK_REVIEWS, row)
        return json.dumps({"ok": True, "local": True,
                           "mode": "benchmark_review",
                           "benchmark_key": row["benchmark_key"]})
    if payload.get("modo") != "ledger_review":
        return json.dumps({"ok": False, "error": "unknown local idle mode"})
    row = {
        "ts": time.strftime("%F %T"),
        "schema": "mak-idle-ledger-review-v1",
        "ledger_id": payload.get("ledger_id", ""),
        "domain": payload.get("domain", ""),
        "action": payload.get("action", ""),
        "source": payload.get("source", ""),
        "reason": payload.get("reason", ""),
        "next_action": "review or rerun the source batch with stronger evidence",
    }
    _append_jsonl(IDLE_LEDGER_REVIEWS, row)
    return json.dumps({"ok": True, "local": True, "mode": "ledger_review",
                       "ledger_id": row["ledger_id"]})


def _audit_idle_decision(ts, online, verbo, depto, payload, status,
                         response="", error=""):
    if not _is_idle_verbo(verbo):
        return
    row = {
        "ts": ts,
        "online": bool(online),
        "verbo": verbo,
        "depto": depto,
        "modo": payload.get("modo"),
        "formato": payload.get("formato", ""),
        "densidad": payload.get("densidad", ""),
        "tema": payload.get("tema", ""),
        "status": status,
        "pending": _pending_snapshot(),
    }
    if response:
        row["response_preview"] = str(response)[:300]
    if error:
        row["error"] = str(error)[:200]
    _append_jsonl(IDLE_AUDIT, row)


def _post(url, data):
    fields = dict(data)
    if isinstance(fields.get("work_contract"), dict):
        fields["work_contract"] = json.dumps(
            fields["work_contract"], ensure_ascii=True, sort_keys=True)
    body = urllib.parse.urlencode(fields).encode()
    req = urllib.request.Request(
        url, data=body, method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded"})
    with urllib.request.urlopen(req, timeout=8) as r:
        return r.read(2000).decode("utf-8", "replace")


def _resp_ok(resp):
    """Parsea el body JSON de /run; (True, "") si ok o no-JSON (legacy), (False, error) si ok==false."""
    try:
        d = json.loads(resp)
    except ValueError:
        return (True, "")
    if not isinstance(d, dict):
        return (True, "")
    if not d.get("ok", True):
        return (False, str(d.get("error", ""))[:200])
    return (True, "")


def _shadow_dispatch(depto, verbo, payload):
    if enqueue_shadow is None:
        return None
    stage = "cron_dispatch"
    body = {"department": depto, "verb": verbo,
            "mode": payload.get("modo", ""),
            "topic": payload.get("tema", ""),
            "density": payload.get("densidad", "medio")}
    return enqueue_shadow(
        stage, body, producer="platform.trabajo",
        estimated_vram_mb=3000 if depto in ("research", "codex") else 0,
        template_version="cron-dispatch-v1",
    )


# Un tema que es el TEXTO DE UN FALLO no es un tema. Medido el 2026-08-01: el
# organismo estaba investigando "**Detalles del Evento:** No se encontraron
# detalles especificos", con los asteriscos de Markdown adentro. Eso no salio
# de una pregunta: salio de un campo vacio de una ficha, entro al backlog que
# se autorellena, y produjo un informe cada 30 minutos por cron. El formato del
# informe se puede arreglar -- se arreglo el mismo dia -- y no sirve de nada:
# un informe impecable sobre "no se encontraron detalles" sigue siendo basura,
# solo que mejor escrita.
#
# SOLO marcas de render, y esa lista corta es el resultado de haberse
# equivocado midiendo. La primera version rechazaba tambien por frases de
# ausencia ("no se encontro", "falta de", "no hay informacion"), y al correrla
# contra el backlog real -- 167 preguntas -- rechazaba 82. Mirando las 82, la
# mitad eran preguntas de investigacion LEGITIMAS: "la falta de investigacion
# sobre la relacion entre la estetica y la construccion de identidades
# culturales" es un tema, no un fallo. El filtro habria borrado la mitad del
# trabajo del organismo.
#
# Y la hipotesis de que la cola era una pregunta repetida tampoco se sostuvo:
# agrupadas por vocabulario, las 167 dan 150 grupos distintos. Solo 32 se
# repiten, y varias de esas son eventos DISTINTOS con la misma forma de
# pregunta, que no es repetirse.
#
# Lo unico que quedo probado como defecto fue el MARCADO: un tema no es un
# fragmento de documento. Esta es la red de ultimo momento; el arreglo de
# verdad esta en `backlog.preguntas_del_informe`, que lee el dato en vez de
# parsear la prosa.
_MARCAS_DE_RENDER = ("**", "##", "```", "|---")

# Se reusa el limpiador de `backlog` en vez de escribir un segundo: dos
# limpiadores del mismo marcado se separan, y entonces la cola y el que la
# consume dejan de coincidir sobre que es un tema.
try:
    from backlog import _limpiar_render
except ImportError:
    _limpiar_render = None


def tema_limpio(texto):
    """(tema, motivo). El tema listo para usar, o "" con el motivo del descarte.

    REPARA antes de rechazar, y esa es la diferencia que costo medirlo: en el
    backlog real hay 66 preguntas de 167 que traen marcado (`**Titulo:** cuerpo`)
    y NO son basura -- son preguntas envueltas en el formato del informe del que
    salieron. Tirarlas seria tirar el 40% del trabajo acumulado del organismo
    por un problema de presentacion.

    Solo se descarta lo que despues de desenvuelto no queda siendo nada: una
    fila de tabla, un separador, un titulo vacio.

    Devuelve el MOTIVO para que quien llame pueda contar por que descarto: un
    rechazo silencioso deja la cola vaciandose sin que nadie sepa de que."""
    t = (texto or "").strip()
    if _limpiar_render is not None:
        t = _limpiar_render(t)
    else:
        # Sin backlog importable se limpia lo minimo, en vez de dejar pasar el
        # marcado entero. Degradar no es lo mismo que no hacer nada.
        for m in _MARCAS_DE_RENDER:
            t = t.replace(m, " ")
        t = t.strip()
    if len(t) < 12:
        return "", "queda en %d caracteres despues de limpiar el marcado" % len(t)
    if len(t) > 400:
        return "", "demasiado largo (%d caracteres)" % len(t)
    if not any(c.isalpha() for c in t):
        return "", "no tiene una sola letra"
    return t, ""


# Que formato pide cada verbo, y por que no es el mismo para todos.
#
# Medido el 2026-08-01 sobre los ultimos 40 informes: `informe` en 40 de 40 y
# `densidad: corto` en todas. El formato `ensayo` existe desde el 2026-07-30
# con siete exigencias -- tesis que se puede negar, tabla donde compiten dos
# lecturas, cronologia, cierre que argumenta, anexo iconografico -- y no se
# invoco NUNCA, porque este archivo nunca mandaba el parametro y research.py
# caia a su default. El motor de calidad estaba apagado.
#
# El corte no es de gusto:
#   - `atender` trabaja la cola de material (triangulacion RD: quien organizo
#     tal evento). Eso es un DATO y se responde con un informe corto y
#     verificable. Un ensayo sobre "quien organizo la fiesta" seria ridiculo.
#   - `multiplicar` y `definir` trabajan temas culturales del backlog. Eso es
#     lo que se merece el nombre research, y el ensayo es el formato que lo
#     exige. Con densidad `medio` porque `corto` le da 64 segundos y 6 fuentes:
#     no alcanza para sostener una tesis.
FORMATO_POR_VERBO = {
    "atender":     ("informe", "corto"),
    "multiplicar": ("ensayo",  "medio"),
    "definir":     ("ensayo",  "medio"),
}


def format_for_task(verbo, tema):
    """The product shape wins over the verb.

    Measured 2026-08-05 on MAK: a harvested backlog question named "Quien
    organizo el evento del 2023-10-28" ran as verb `multiplicar`, so the
    dispatcher requested an essay and produced PARTE I / ANEXO ICONOGRAFICO
    around a factual triangulation. The factual detector already existed in
    research_lib for the prompt frame; the missing seam was using that same
    detector for the output format."""
    if research_router is not None:
        route = research_router.route_research_task(
            verbo, tema, factual_detector=_es_pregunta_factual)
        return (route.formato, route.densidad)
    if _es_pregunta_factual(tema):
        return ("informe", "corto")
    return FORMATO_POR_VERBO.get(verbo, ("informe", "corto"))


def contract_for_task(verbo, tema):
    """Return the output contract alongside the selected product shape."""
    if research_router is not None:
        route = research_router.route_research_task(
            verbo, tema, factual_detector=_es_pregunta_factual)
        return list(route.required_fields)
    return ["claim", "sources", "uncertainty", "next_action"]


def identity_contract(route, verbo):
    """Return the portable identity envelope for a dispatched task."""
    kind_by_domain = {
        "rd": "report",
        "iskvw": "work",
        "mak": "report",
        "opportunities": "opportunity",
        "research": "work",
    }
    return {
        "schema": "mak-identity-v1",
        "kind": kind_by_domain.get(route.domain, "task"),
        "source_id": "dispatch:%s:%s" % (route.domain, route.intent),
        "parent_id": "verb:%s" % verbo,
        "entities": {
            "artist": [], "username": [], "client": [], "collab": [],
            "event": [], "festival": [], "venue": [], "location": [],
            "source": [],
        },
        "event_date": "",
        "published_at": "",
    }


def work_contract(verbo, tema):
    """Build the typed receipt that travels with every research dispatch."""
    if research_router is not None:
        route = research_router.route_research_task(
            verbo, tema, factual_detector=_es_pregunta_factual)
        return {
            "schema": "mak-work-contract-v1",
            "domain": route.domain,
            "intent": route.intent,
            "format": route.formato,
            "density": route.densidad,
            "required_fields": list(route.required_fields),
            "reason": route.reason,
            "profile": research_router.profile_for_route(route),
            "identity": identity_contract(route, verbo),
        }
    formato, densidad = format_for_task(verbo, tema)
    return {
        "schema": "mak-work-contract-v1",
        "domain": "research",
        "intent": "answer",
        "format": formato,
        "density": densidad,
        "required_fields": contract_for_task(verbo, tema),
        "reason": "conservative local fallback",
        "identity": {
            "schema": "mak-identity-v1", "kind": "task",
            "source_id": "dispatch:research:answer", "parent_id": "verb:%s" % verbo,
            "entities": {}, "event_date": "", "published_at": "",
        },
    }


def validate_work_contract(verbo, payload):
    """Reject route drift before a research request reaches MAK services."""
    if payload.get("modo") != "research":
        return []
    tema = payload.get("tema", "")
    actual = payload.get("work_contract") or {}
    expected = work_contract(verbo, tema)
    errors = []
    for field in ("domain", "intent", "format", "density"):
        if actual.get(field) != expected[field]:
            errors.append("work_contract_%s_mismatch" % field)
    if actual.get("required_fields") != expected["required_fields"]:
        errors.append("work_contract_required_fields_mismatch")
    if actual.get("identity") != expected.get("identity"):
        errors.append("work_contract_identity_mismatch")
    if payload.get("formato") != expected["format"]:
        errors.append("payload_format_mismatch")
    if payload.get("densidad") != expected["density"]:
        errors.append("payload_density_mismatch")
    if payload.get("output_contract") != expected["required_fields"]:
        errors.append("output_contract_mismatch")
    return errors


def _tarea(verbo, st):
    """Arma (depto, payload_dict) para un verbo, o None si no hay trabajo."""
    v = next((x for x in roles.VERBOS if x["verbo"] == verbo), None)
    if not v:
        return None
    fuente = v["fuente"]
    sems = _lineas(SEMILLAS_F, roles.SEMILLAS)
    if fuente == "material":
        # La cola que sale de lo percibido (triangulacion RD + lineas de las
        # obras). Si esta vacia devolvemos None y la rotacion sigue: el modo
        # autonomo es el fallback, no el default.
        if material is None:
            return None
        tarea = material.pop_pendiente()
        if not tarea:
            return None
        if tarea.get("depto") == "codex":
            return ("codex", {"modo": tarea.get("modo", "generar"),
                              "pedido": tarea["texto"], "densidad": "medio"})
        tema, motivo = tema_limpio(tarea["texto"])
        if not tema:
            print("tema descartado (%s): %.70s" % (motivo, tarea["texto"]),
                  flush=True)
            return None
        fmt, dens = format_for_task(verbo, tema)
        return ("research", {"modo": tarea.get("modo", "research"),
                             "tema": tema, "densidad": dens, "formato": fmt,
                             "output_contract": contract_for_task(verbo, tema),
                             "work_contract": work_contract(verbo, tema)})
    if fuente == "concepto":
        if _memory_requires_review():
            return None
        if verbo == "multiplicar" and _should_review_corpus(st):
            payload = _corpus_review_payload(st, verbo)
            if payload:
                return ("research", payload)
        if backlog is not None:
            entrada = backlog.pop_pendiente(BACKLOG_GEN)
            if entrada:
                tema, motivo = tema_limpio(entrada["pregunta"])
                if not tema:
                    # Se DICE. Una tarea que desaparece sin dejar rastro es
                    # como esta cola se lleno de vinnetas sin que nadie lo
                    # notara durante dias.
                    print("tema descartado (%s): %.70s"
                          % (motivo, entrada["pregunta"]), flush=True)
                    return None
                fmt, dens = format_for_task(verbo, tema)
                return ("research", {"modo": v["modo"], "tema": tema,
                                     "densidad": dens, "formato": fmt,
                                     "output_contract": contract_for_task(verbo, tema),
                                     "work_contract": work_contract(verbo, tema)})
        if not _seed_fallback_enabled():
            return None
        i = st.get("sem_idx", 0) % len(sems)
        st["sem_idx"] = i + 1
        fmt, dens = format_for_task(verbo, sems[i])
        return ("research", {"modo": v["modo"], "tema": sems[i],
                             "densidad": dens, "formato": fmt,
                             "output_contract": contract_for_task(verbo, sems[i]),
                             "work_contract": work_contract(verbo, sems[i])})
    if fuente == "definir":
        if not _seed_fallback_enabled():
            return None
        i = st.get("def_idx", 0) % len(sems)
        st["def_idx"] = i + 1
        tema = "definicion cultural precisa y genealogia de: " + sems[i]
        fmt, dens = format_for_task(verbo, tema)
        return ("research", {"modo": v["modo"], "tema": tema,
                             "densidad": dens, "formato": fmt,
                             "output_contract": contract_for_task(verbo, tema),
                             "work_contract": work_contract(verbo, tema)})
    if fuente == "modulo":
        mods = roles.MODULOS
        i = st.get("mod_idx", 0) % len(mods)
        st["mod_idx"] = i + 1
        return ("codex", {"modo": v["modo"], "pedido": mods[i], "densidad": "medio"})
    if fuente == "backlog":
        bl = _lineas(BACKLOG, [])
        if not bl:
            return None  # sin backlog: desarrollar no tiene trabajo este tick
        i = st.get("bl_idx", 0) % len(bl)
        st["bl_idx"] = i + 1
        return ("codex", {"modo": v["modo"], "pedido": bl[i], "densidad": "medio"})
    if fuente == "idle":
        if not _idle_review_allowed():
            return None
        payload = _idle_node_payload(verbo, st)
        if not payload:
            return None
        if payload.get("modo") in ("ledger_review", "benchmark_review",
                                     "memory_audit"):
            return ("local", payload)
        return (v["depto"], payload)
    return None


def _main_unlocked():
    ts = time.strftime("%F %T")
    now = time.time()
    # dia anclado a las 19:00 locales (de 19:00 a 19:00), no fecha calendario
    # 2026-07-23; causa: reset a medianoche regala las horas de trabajo del
    # usuario; retiro: tope dinamico por medicion de consumo
    hoy = time.strftime("%Y-%m-%d", time.localtime(now - 19 * 3600))
    st = _state()
    if st.get("date") != hoy:
        st = {"date": hoy, "count": 0, "last": 0, "verbo_idx": 0}
    if backlog is not None:
        try:
            n = backlog.cosechar(INFORMES_DIRS, BACKLOG_GEN)
            if n:
                log("%s cosecha: +%d preguntas al backlog generativo" % (ts, n))
        except Exception:
            pass
    if load1() > roles.LOAD_MAX:
        log("%s skip: load %.2f > %s" % (ts, load1(), roles.LOAD_MAX))
        return
    online = red_ok()
    gap = (roles.GAP_MIN if online else roles.GAP_MIN_OFFLINE) * 60
    if now - st.get("last", 0) < gap:
        return  # aun en el gap; el proximo tick del cron reintenta
    if st.get("count", 0) >= roles.MAX_DIA:
        log("%s skip: tope diario (%d)" % (ts, roles.MAX_DIA))
        return

    # PRIORIDAD: mientras haya material del usuario en cola, se atiende eso.
    # Sin esto el round-robin le daba 1 de cada 5 turnos y la cola crecia mas
    # rapido de lo que drenaba -- o sea, el modo autonomo seguia ganando.
    # Cuando la cola se vacia, el verbo atender no produce tarea y la rotacion normal
    # sigue su curso: el modo autonomo es el fallback, como fue disenado.
    n = len(roles.VERBOS)
    idx = st.get("verbo_idx", 0) % n
    if any(v["verbo"] == "atender" for v in roles.VERBOS):
        idx = next(i for i, v in enumerate(roles.VERBOS) if v["verbo"] == "atender")
    tarea = None
    verbo = None
    for k in range(n):
        verbo = roles.VERBOS[(idx + k) % n]["verbo"]
        tarea = _tarea(verbo, st)
        if tarea:
            st["verbo_idx"] = (idx + k + 1) % n
            break
    if not tarea:
        log("%s skip: ningun verbo con trabajo" % ts)
        _save(st)
        return

    depto, payload = tarea
    # The autonomous scheduler is the source of this trigger. It travels with
    # the request so activity inventory can distinguish cron work from a human
    # API call all the way down to the model/resource boundary.
    payload = dict(payload)
    payload.setdefault("trigger", "cron:MAK-TRABAJO")
    url = RESEARCH
    if depto == "codex":
        url = CODEX
    if depto == "local":
        resp = _run_local_idle(payload)
        ok, err = _resp_ok(resp)
        if ok:
            st["count"] = st.get("count", 0) + 1
            st["last"] = now
            _save(st)
            log("%s OK local %.80s" % (ts, payload.get("modo", "")))
            _audit_idle_decision(ts, online, verbo, depto, payload,
                                 "accepted", resp)
        else:
            log("%s RECHAZO local: %s" % (ts, err))
            _audit_idle_decision(ts, online, verbo, depto, payload,
                                 "rejected", resp, err)
        return
    contract_errors = validate_work_contract(verbo, payload)
    if contract_errors:
        error = ",".join(contract_errors)
        log("%s RECHAZO local de contrato: %s" % (ts, error))
        _finish_corpus_review(st, payload, False)
        _finish_curatoria_review(st, payload, False)
        _audit_idle_decision(ts, online, verbo, depto, payload,
                             "rejected", error=error)
        _save(st)
        return
    try:
        shadow_job = _shadow_dispatch(depto, verbo, payload)
        resp = _post(url, payload)
        ok, err = _resp_ok(resp)
        if observe_shadow is not None:
            observe_shadow(
                shadow_job, producer="platform.trabajo",
                result_status="ACCEPTED" if ok else "REJECTED",
                payload={"department": depto, "verb": verbo,
                         "error": err} if err else
                        {"department": depto, "verb": verbo},
            )
        if not ok:
            log("%s [%s] %s RECHAZADO: %s"
                % (ts, "on" if online else "OFF", verbo, err))
            _audit_idle_decision(ts, online, verbo, depto, payload,
                                 "rejected", resp, err)
            _finish_corpus_review(st, payload, False)
            _finish_curatoria_review(st, payload, False)
            _save(st)
            return
        st["count"] = st.get("count", 0) + 1
        st["last"] = now
        _finish_corpus_review(st, payload, True)
        _finish_curatoria_review(st, payload, True)
        _save(st)
        if backlog is not None and st["count"] % 8 == 0:
            try:
                backlog.curar(BACKLOG_GEN)
            except Exception:
                pass
        etiqueta = payload.get("tema") or payload.get("pedido") or ""
        log("%s [%s] %s #%d/%d (%s) -> %s"
            % (ts, "on" if online else "OFF", verbo, st["count"], roles.MAX_DIA,
               etiqueta[:60], resp[:50]))
        _audit_idle_decision(ts, online, verbo, depto, payload,
                             "accepted", resp)
    except Exception as e:  # noqa: BLE001 - el orquestador no debe morir
        if observe_shadow is not None:
            observe_shadow(
                shadow_job, producer="platform.trabajo",
                result_status="FAILED", payload={
                    "department": depto, "verb": verbo,
                    "error": str(e)[:2000]},
            )
        _save(st)
        _finish_curatoria_review(st, payload, False)
        log("%s [%s] %s FALLO: %s" % (ts, "on" if online else "OFF", verbo, str(e)[:120]))
        _audit_idle_decision(ts, online, verbo, depto, payload,
                             "failed", error=str(e))


def main():
    if active_enabled():
        payload = {"tick_bucket": int(time.time() // 60)}

        def handle(_job):
            result = _main_unlocked()
            return {"validated": True, "result": result}

        queued = dispatch_sync(
            "cron_tick", payload, producer="platform.trabajo.main",
            handler=handle, template_version="cron-tick-v2")
        return queued
    shadow_job = (enqueue_shadow(
        "cron_tick", {"tick_bucket": int(time.time() // 60)},
        producer="platform.trabajo.main", template_version="cron-tick-v1")
        if enqueue_shadow is not None else None)
    started = time.time()
    with _exclusive_run_lock():
        try:
            result = _main_unlocked()
        except Exception as exc:
            if observe_shadow is not None:
                observe_shadow(
                    shadow_job, producer="platform.trabajo.main",
                    result_status="FAILED", payload={
                        "error": str(exc)[:2000],
                        },
                    started_at=started, owner_pid=os.getpid())
            raise
    if observe_shadow is not None:
        observe_shadow(
            shadow_job, producer="platform.trabajo.main",
            result_status="READY", validated=True,
            payload={"tick_bucket": int(started // 60)},
            started_at=started, owner_pid=os.getpid())
    return result


if __name__ == "__main__":
    main()
