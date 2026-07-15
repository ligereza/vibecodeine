"""
Self-contained cue-panel HTML for the showcontrol plugin.

Served from GET /api/plugins/showcontrol/panel -- the xiotech M2 "panel de
control HTTP para disparar cues desde navegador/tablet". No frameworks, no CDN,
no external assets: one string, works offline on the hotspot LAN. All actions
go through the plugin's existing validated JSON endpoints.
"""

PANEL_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>xio · show control</title>
<style>
  :root{--bg:#111317;--panel:#191c22;--line:#2a2e37;--ink:#eef0f3;--dim:#8a90a0;
        --accent:#7fd1ae;--warn:#ffd166;--hot:#ff6b6b;}
  *{box-sizing:border-box;-webkit-tap-highlight-color:transparent;}
  body{margin:0;background:var(--bg);color:var(--ink);
       font-family:ui-monospace,Menlo,Consolas,monospace;padding:14px 12px 40px;}
  h1{font-size:14px;font-weight:600;margin:0 0 2px;}
  .sub{color:var(--dim);font-size:11px;margin-bottom:14px;}
  #go{width:100%;padding:26px 0;font-size:28px;font-weight:700;letter-spacing:.12em;
      background:var(--accent);color:#0b0d10;border:none;border-radius:14px;cursor:pointer;}
  #go:active{filter:brightness(1.15);}
  #go:disabled{background:#2a2e37;color:var(--dim);}
  .row{display:flex;gap:8px;margin-top:10px;}
  .row button{flex:1;padding:14px 0;font-size:14px;font-weight:600;border-radius:10px;
      border:1px solid var(--line);background:var(--panel);color:var(--ink);cursor:pointer;}
  #stop:active{border-color:var(--warn);color:var(--warn);}
  #release:active{border-color:var(--hot);color:var(--hot);}
  .state{display:flex;gap:8px;align-items:center;margin:14px 0 8px;font-size:12px;}
  .dot{width:10px;height:10px;border-radius:50%;background:var(--dim);flex:none;}
  .dot.fading{background:var(--warn);}
  .dot.idle{background:var(--accent);}
  .dot.stopped{background:var(--hot);}
  #statetxt{color:var(--dim);}
  #cuelist{margin-top:6px;}
  .cue{display:flex;gap:10px;padding:10px 12px;border:1px solid var(--line);
       border-radius:10px;margin-bottom:6px;font-size:13px;align-items:center;cursor:pointer;}
  .cue .n{color:var(--dim);width:24px;}
  .cue .lbl{flex:1;}
  .cue .meta{color:var(--dim);font-size:11px;}
  .cue.current{border-color:var(--accent);background:#13201b;}
  details{margin-top:16px;}
  summary{color:var(--dim);font-size:12px;cursor:pointer;}
  textarea{width:100%;height:150px;margin-top:8px;background:#0e1015;color:var(--ink);
       border:1px solid var(--line);border-radius:8px;font-family:inherit;font-size:11px;padding:8px;}
  .mini{margin-top:8px;display:flex;gap:8px;}
  .mini input{flex:1;background:#0e1015;color:var(--ink);border:1px solid var(--line);
       border-radius:8px;padding:8px;font-family:inherit;font-size:12px;}
  .mini button{padding:8px 14px;border-radius:8px;border:1px solid var(--line);
       background:var(--panel);color:var(--ink);cursor:pointer;font-size:12px;}
  #err{color:var(--hot);font-size:11px;min-height:14px;margin-top:8px;word-break:break-all;}
</style>
</head>
<body>
<h1>xio &middot; show control</h1>
<div class="sub">cue engine &middot; GO / STOP / RELEASE &middot; corre en el telefono</div>

<button id="go">GO</button>
<div class="row">
  <button id="stop">STOP</button>
  <button id="release">RELEASE 2s</button>
</div>

<div class="state"><div class="dot" id="dot"></div><span id="statetxt">&mdash;</span></div>
<div id="cuelist"></div>

<details>
  <summary>cargar cue list (JSON)</summary>
  <textarea id="json" placeholder='{"output":{"protocol":"artnet","host":"192.168.1.50"},"cues":[{"label":"open","fade":3,"levels":{"0":{"1":255}}}]}'></textarea>
  <div class="mini"><button id="load">cargar</button></div>
</details>

<details>
  <summary>wake-on-lan</summary>
  <div class="mini">
    <input id="mac" placeholder="AA:BB:CC:DD:EE:FF">
    <button id="wol">WOL</button>
  </div>
</details>

<div id="err"></div>

<script>
const B = "/api/plugins/showcontrol";
const $ = id => document.getElementById(id);
let cues = [];

async function api(path, body){
  const r = await fetch(B + path, body === undefined ? {} :
    {method:"POST", headers:{"Content-Type":"application/json"}, body: JSON.stringify(body)});
  const d = await r.json().catch(() => ({}));
  if(!r.ok || d.ok === false) throw new Error(d.error || ("HTTP " + r.status));
  return d;
}
function err(e){ $("err").textContent = e ? String(e.message || e) : ""; }

function renderState(st){
  $("dot").className = "dot " + st.state;
  $("statetxt").textContent =
    st.state + (st.label ? " · " + st.label : "") +
    " · cue " + (st.position + 1) + "/" + st.cue_count +
    (st.active ? " · LIVE" : "");
  document.querySelectorAll(".cue").forEach((el, i) =>
    el.classList.toggle("current", i === st.position));
}
function renderCues(){
  $("cuelist").innerHTML = cues.map((c, i) =>
    '<div class="cue" data-i="' + i + '"><span class="n">' + (i + 1) + '</span>' +
    '<span class="lbl">' + String(c.label).replace(/[<>&]/g, "") + '</span>' +
    '<span class="meta">fade ' + c.fade + 's' +
    (c.follow != null ? ' · follow ' + c.follow + 's' : '') + '</span></div>').join("");
  document.querySelectorAll(".cue").forEach(el =>
    el.onclick = () => api("/cue/go", {index: +el.dataset.i}).catch(err));
}
async function refresh(){
  try{
    const d = await api("/cues");
    cues = d.cues || [];
    renderCues();
    renderState(d.state);
    err("");
  }catch(e){ err(e); }
}
async function poll(){
  try{ renderState((await api("/cue/state")).state); }catch(e){}
}

$("go").onclick = () => api("/cue/go", {}).catch(err);
$("stop").onclick = () => api("/cue/stop", {}).catch(err);
$("release").onclick = () => api("/cue/release", {fade: 2}).catch(err);
$("load").onclick = () => {
  let body;
  try{ body = JSON.parse($("json").value); }catch(e){ return err("JSON invalido: " + e.message); }
  api("/cues", body).then(refresh).catch(err);
};
$("wol").onclick = () => api("/wol", {mac: $("mac").value}).catch(err);

refresh();
setInterval(poll, 1000);
</script>
</body>
</html>
"""
