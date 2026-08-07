"""Read-only visual review surface for MAK video candidates."""
from __future__ import annotations

import json
import os
import re
import time
from pathlib import Path


ROOT = Path(os.environ.get(
    "MAK_REEL_REVIEW_ROOT",
    os.path.expanduser("~/plataforma/director_runs/reel-vision-batch-20260807"),
)).resolve()
SHEETS = Path(os.environ.get(
    "MAK_REEL_SHEETS_ROOT",
    os.path.expanduser("~/plataforma/director_runs/video-contact-sheets-20260807"),
)).resolve()
REVIEWS = ROOT / "human_reviews.jsonl"
SAFE_NAME = re.compile(r"^[0-9]+_mp4$")
DECISIONS = {"accept", "revise", "reject"}


def _safe_video(video: str) -> str | None:
    value = str(video or "")
    return value if SAFE_NAME.fullmatch(value) else None


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
        video = _safe_video(row.get("video"))
        if video:
            result[video] = row
    return result


def rows() -> list[dict]:
    review_map = _review_map()
    output = []
    for directory in sorted(ROOT.iterdir()) if ROOT.is_dir() else []:
        if not directory.is_dir():
            continue
        video = directory.name
        if not SAFE_NAME.fullmatch(video):
            continue
        result = _read_json(directory / "v2-result.json")
        if not result:
            result = _read_json(directory / "result.json")
        review = result.get("review") or {}
        output.append({
            "video": video,
            "sheet": "/revision/media/%s.jpg" % video[:-4],
            "provider_status": result.get("status", "pending"),
            "ollama_verdict": review.get("verdict", "pending"),
            "reason": review.get("reason", ""),
            "human": review_map.get(video),
        })
    return output


def api() -> dict:
    data = rows()
    return {
        "schema": "mak-reel-review-v1",
        "total": len(data),
        "pending_human": sum(1 for row in data if not row["human"]),
        "rows": data,
    }


def media_path(name: str) -> Path | None:
    value = str(name or "")
    if not value.startswith("/") or not value.endswith(".jpg"):
        return None
    video = value.rsplit("/", 1)[-1][:-4] + "_mp4"
    if not SAFE_NAME.fullmatch(video):
        return None
    candidate = (SHEETS / (video[:-4] + ".jpg")).resolve()
    try:
        candidate.relative_to(SHEETS)
    except ValueError:
        return None
    return candidate if candidate.is_file() else None


def record(video: str, decision: str, note: str = "") -> dict:
    video = _safe_video(video)
    decision = str(decision or "")
    if not video or decision not in DECISIONS:
        return {"ok": False, "error": "video_or_decision_invalid"}
    previous = _review_map().get(video)
    if previous and previous.get("decision") == decision and not note:
        return {"ok": True, "row": previous, "duplicate": True}
    ROOT.mkdir(parents=True, exist_ok=True)
    row = {"video": video, "decision": decision,
           "note": str(note or "")[:1000],
           "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z")}
    with REVIEWS.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(row, ensure_ascii=False) + "\n")
    return {"ok": True, "row": row}


PAGE = r'''<!doctype html><meta charset="utf-8"><title>MAK - revision visual</title>
<style>
body{background:#090807;color:#d0c9ba;font:14px system-ui;margin:0;padding:24px}
h1{color:#9db67c}#meta{color:#9d927f;margin-bottom:18px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(310px,1fr));gap:16px}
article{background:#12100d;border:1px solid #30291f;border-radius:10px;padding:12px}img{width:100%;display:block;border-radius:6px;background:#050504}
small{color:#9d927f}.status{margin:8px 0;color:#d4a259}.buttons{display:flex;gap:7px}.buttons button{background:#201c15;color:#d0c9ba;border:1px solid #514631;border-radius:5px;padding:7px 10px;cursor:pointer}.buttons button:hover{border-color:#9db67c}
textarea{width:100%;box-sizing:border-box;background:#0b0a08;color:#d0c9ba;border:1px solid #30291f;margin:8px 0;padding:6px}
</style><h1>MAK / revision visual</h1><div id="meta">cargando...</div><button onclick="showReviewed=!showReviewed;load()">mostrar/ocultar revisados</button><main class="grid" id="grid"></main>
<script>
let showReviewed=false;
const esc=s=>String(s||'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
async function load(){const d=await fetch('/api/revision').then(r=>r.json());const rows=showReviewed?d.rows:d.rows.filter(r=>!r.human);document.querySelector('#meta').textContent=`${d.total} videos | ${d.pending_human} pendientes humanos | mostrando ${rows.length}`;document.querySelector('#grid').innerHTML=rows.map((r,i)=>`<article><img src="${r.sheet}" loading="lazy"><small>${esc(r.video)}</small><div class="status">modelo: ${esc(r.ollama_verdict)} | ${esc(r.provider_status)}</div><div>${esc(r.reason)}</div><textarea id="n${i}" placeholder="nota opcional"></textarea><div class="buttons"><button onclick="decide('${r.video}', 'accept', ${i})">aceptar</button><button onclick="decide('${r.video}', 'revise', ${i})">revisar</button><button onclick="decide('${r.video}', 'reject', ${i})">rechazar</button></div></article>`).join('')}
async function decide(video,decision,i){await fetch('/api/revision',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({video,decision,note:document.querySelector('#n'+i).value})});load()}
load();
</script>'''
