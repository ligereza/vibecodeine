import json, glob, re, os
from collections import defaultdict

BASE = r"C:\Users\issvk\.claude\projects\C--IA-flujo"
files = glob.glob(os.path.join(BASE, "*.jsonl"))

EXCLUDE_MARKERS = [
    "<system-reminder>", "[SYSTEM NOTIFICATION", "caveMan", "caveman",
    "Autonomous loop tick", "Base directory for this skill",
    "<command-message>", "<command-name>", "<local-command",
    "hook", "tool_result", "<system_warning",
]

def get_text_blocks(content):
    texts = []
    if isinstance(content, str):
        texts.append(content)
    elif isinstance(content, list):
        for block in content:
            if not isinstance(block, dict):
                continue
            if block.get("type") == "tool_result":
                continue
            if block.get("type") == "text":
                t = block.get("text", "")
                if t:
                    texts.append(t)
    return texts

n_files = 0
n_user_msgs = 0
n_kept = 0
raw_msgs = []

for fp in files:
    n_files += 1
    try:
        with open(fp, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except Exception:
                    continue
                if obj.get("type") != "user":
                    continue
                msg = obj.get("message", {})
                if msg.get("role") != "user":
                    continue
                content = msg.get("content")
                texts = get_text_blocks(content)
                for t in texts:
                    n_user_msgs += 1
                    stripped = t.strip()
                    if not stripped:
                        continue
                    # exclude noise
                    if any(m in stripped for m in EXCLUDE_MARKERS):
                        continue
                    # exclude very long pasted docs (>1200 chars likely paste/skill body)
                    if len(stripped) > 1200:
                        continue
                    # exclude things that look like file dumps (many newlines with code-like markers)
                    if stripped.count("\n") > 25:
                        continue
                    # exclude pure tool/system junk patterns
                    if stripped.startswith("{") or stripped.startswith("["):
                        continue
                    raw_msgs.append((fp, stripped))
                    n_kept += 1
    except Exception:
        continue

print(f"FILES_SCANNED={n_files}")
print(f"USER_MSGS_SEEN={n_user_msgs}")
print(f"KEPT_AFTER_FILTER={n_kept}")

# dedup near-identical: normalize whitespace/case for key
seen = {}
for fp, t in raw_msgs:
    key = re.sub(r"\s+", " ", t.lower()).strip()
    key = key[:200]
    if key not in seen:
        seen[key] = t

deduped = list(seen.values())
print(f"DEDUPED={len(deduped)}")

# Score for demand/critique/pressure/correction/philosophy
KEYWORDS = [
    "no esperes", "avanza", "ejecuta", "no asumas", "asumas", "lee ", "delega",
    "no confies", "no repitas", "no me hagas", "dale", "hace", "haz", "corre",
    "verifica", "no inventes", "no adivines", "cuidado", "mal", "error",
    "no sirve", "basura", "falso", "mentira", "no es cierto", "revisa",
    "no gastes", "cuota", "barato", "caro", "no toques", "prohibido",
    "nunca", "jamas", "obligatorio", "no se puede", "si se puede",
    "confirma", "no confirmes", "chequea", "no me digas", "termina",
    "no pares", "segui", "sigue", "segui dale", "no preguntes", "resolve",
    "arregla", "por que", "porque no", "no entiendo por que", "de una",
    "ya", "urgente", "no jodas", "carajo", "mierda", "pelotudo", "hueon",
    "no puede ser", "otra vez", "de nuevo", "cansado", "harto",
]

def score(t):
    tl = t.lower()
    s = 0
    for k in KEYWORDS:
        if k in tl:
            s += 1
    # prefer short-medium, imperative-y
    length = len(t)
    if 10 <= length <= 400:
        s += 1
    if t.strip().endswith("?"):
        s -= 0.2
    return s

scored = sorted(deduped, key=score, reverse=True)

# Filter out very short trivial ones like "ok", "si", "dale" alone unless demanding tone; keep as-is per instructions (verbatim)
top = []
for t in scored:
    if len(t) < 3:
        continue
    top.append(t)
    if len(top) >= 150:
        break

out_path = os.path.join(os.path.dirname(__file__), "corpus_candidates.txt")
with open(out_path, "w", encoding="utf-8") as f:
    for t in top:
        f.write(t.replace("\n", " \\n ") + "\n---\n")

print(f"WROTE_CANDIDATES={out_path}")
print(f"TOP_COUNT={len(top)}")
