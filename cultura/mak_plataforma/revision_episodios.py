"""Human review surface for grouped visual curation episodes."""
from __future__ import annotations

import json
import os
import threading
import time
from pathlib import Path


RUN = Path(os.environ.get(
    "MAK_EPISODE_REVIEW_ROOT",
    os.path.expanduser("~/plataforma/director_runs/curatoria-visual-ronda1-20260807"),
)).resolve()
FICHAS = RUN / "FICHAS_CURATORIA_VISUAL_RONDA1.json"
MAPA = RUN / "MAPA_VISUAL_ARTISTA_PRIMERO.json"
XIO = RUN / "XIO_EVIDENCIA_DREF.json"
REVIEWS = RUN / "episode_reviews.jsonl"
DECISIONS = {"accept", "revise", "reject"}
_REVIEW_LOCK = threading.RLock()


def _read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def _review_map() -> dict:
    result = {}
    try:
        lines = REVIEWS.read_text(encoding="utf-8").splitlines()
    except OSError:
        return result
    for line in lines:
        try:
            row = json.loads(line)
        except ValueError:
            continue
        episode = str(row.get("episodio") or row.get("sujeto") or "")
        if episode:
            result[episode] = row
    return result


def rows() -> list[dict]:
    mapa = _read_json(MAPA)
    if mapa.get("entities"):
        media = {row.get("media"): row for row in mapa.get("media", [])}
        reviews = _review_map()
        output = []
        for entity in mapa["entities"]:
            subject = str(entity.get("id") or "")
            members = [media[name] for name in entity.get("media", []) if name in media]
            output.append({
                "episodio": subject,
                "sujeto": subject,
                "kind": entity.get("kind", "unknown"),
                "medios": entity.get("media", []),
                "publicaciones": sorted({m.get("publicacion_id") for m in members if m.get("publicacion_id")}),
                "descripcion_original": [m.get("descripcion_original", "") for m in members if m.get("descripcion_original")],
                "notas_humanas": [m.get("nota_humana", "") for m in members if m.get("nota_humana")],
                "observaciones_aws": [],
                "estado": "sujeto_agrupado",
                "human": reviews.get(subject),
            })
        return output
    payload = _read_json(FICHAS)
    reviews = _review_map()
    output = []
    for item in payload.get("items", []):
        episode = str(item.get("episodio") or "")
        if not episode:
            continue
        output.append({
            "episodio": episode,
            "medios": item.get("medios", []),
            "publicaciones": item.get("publicaciones", []),
            "descripcion_original": item.get("descripcion_original", []),
            "notas_humanas": item.get("notas_humanas", []),
            "roles_provisionales": item.get("roles_provisionales", {}),
            "observaciones_aws": item.get("observaciones_aws", []),
            "estado": item.get("estado", "revisar"),
            "human": reviews.get(episode),
        })
    return output


def api() -> dict:
    data = rows()
    mapa = _read_json(MAPA)
    return {
        "schema": "mak-episode-review-v1",
        "total": len(data),
        "pending_human": sum(1 for row in data if not row["human"]),
        "event_candidates": mapa.get("event_candidates", []),
        "rows": data,
    }


def evidence() -> dict:
    return _read_json(XIO)


def record(episode: str, decision: str, note: str = "") -> dict:
    with _REVIEW_LOCK:
        return _record_unlocked(episode, decision, note)


def _record_unlocked(episode: str, decision: str, note: str = "") -> dict:
    episode = str(episode or "")
    decision = str(decision or "")
    valid = {row["episodio"] for row in rows()}
    if episode not in valid or decision not in DECISIONS:
        return {"ok": False, "error": "episode_or_decision_invalid"}
    previous = _review_map().get(episode)
    if previous and previous.get("decision") == decision and not note:
        return {"ok": True, "row": previous, "duplicate": True}
    RUN.mkdir(parents=True, exist_ok=True)
    row = {"episodio": episode, "decision": decision,
           "note": str(note or "")[:2000],
           "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z")}
    with REVIEWS.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(row, ensure_ascii=False) + "\n")
    return {"ok": True, "row": row}


PAGE = r'''<!doctype html><meta charset="utf-8"><title>MAK - revision por episodio</title>
<style>body{background:#090807;color:#d0c9ba;font:14px system-ui;margin:0;padding:24px}h1{color:#9db67c}#meta{color:#9d927f;margin-bottom:18px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(360px,1fr));gap:16px}article{background:#12100d;border:1px solid #30291f;border-radius:10px;padding:15px}h2{font-size:1.05rem;color:#d4a259}small{color:#9d927f}.reading{border-left:3px solid #9db67c;padding:8px;margin:10px 0;white-space:pre-wrap}.original{border-left:3px solid #6d6656;padding:8px;margin:10px 0;white-space:pre-wrap;max-height:180px;overflow:auto}.buttons{display:flex;gap:7px}.buttons button{background:#201c15;color:#d0c9ba;border:1px solid #514631;border-radius:5px;padding:7px 10px;cursor:pointer}.buttons button:hover{border-color:#9db67c}textarea{width:100%;box-sizing:border-box;background:#0b0a08;color:#d0c9ba;border:1px solid #30291f;margin:8px 0;padding:6px}</style><h1>MAK / revision por episodio</h1><div id="meta">cargando...</div><main class="grid" id="grid"></main>
<script>
const esc=s=>String(s||'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
async function load(){const d=await fetch('/api/revision/episodios').then(r=>r.json());const x=await fetch('/api/revision/evidencia').then(r=>r.json());const ev=(d.event_candidates||[]).map(x=>x.name||x.id).join(' · ');document.querySelector('#meta').textContent=`${d.total} sujetos | ${d.pending_human} pendientes humanos${ev?' | eventos candidatos: '+ev:''}${x.cues? ' | XIO Dref: '+x.cues.length+' cues':''}`;document.querySelector('#grid').innerHTML=d.rows.map((r,i)=>{const aws=(r.observaciones_aws||[]).map(x=>x.reading).join('\n');const original=(r.descripcion_original||[]).join('\n\n');return `<article><h2>${esc(r.episodio)}</h2><small>tipo: ${esc(r.kind||'sujeto')} | ${r.medios.length} medios | ${esc((r.publicaciones||[]).join(', '))}</small><div class="reading"><b>lectura provisional AWS:</b> ${esc(aws||'sin lectura externa')}</div><div class="original"><b>descripcion original:</b> ${esc(original||'sin descripcion')}</div><div><b>notas humanas:</b> ${esc((r.notas_humanas||[]).join(' | '))}</div><textarea id="n${i}" placeholder="confirmacion o correccion"></textarea><div class="buttons"><button onclick="decide('${esc(r.episodio)}','accept',${i})">aceptar</button><button onclick="decide('${esc(r.episodio)}','revise',${i})">revisar</button><button onclick="decide('${esc(r.episodio)}','reject',${i})">rechazar</button></div></article>`}).join('')}
async function decide(episodio,decision,i){await fetch('/api/revision/episodios',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({episodio,decision,note:document.querySelector('#n'+i).value})});load()}load();
</script>'''
