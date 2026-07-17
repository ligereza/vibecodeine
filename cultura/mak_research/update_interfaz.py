import re

with open("interfaz.py", "r") as f:
    code = f.read()

# Order 3 & 4 changes

code = code.replace("JOBS = []  # historial en memoria: {tema, modo, estado, path, t}", """
JOBS_FILE = os.path.expanduser("~/research/jobs.jsonl")
JOBS = []

def _load_jobs():
    global JOBS
    try:
        with open(JOBS_FILE, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    JOBS.append(json.loads(line.strip()))
                except Exception:
                    pass
        JOBS = JOBS[-15:]
    except OSError:
        pass

_load_jobs()
""")

code = code.replace('job["estado"] = "listo" if r["ok"] else "FALLO"', """
        job["estado"] = "listo" if r["ok"] else "FALLO"
        job["path"] = os.path.basename(r["path"]) if r["path"] else ""
        job["ms"] = r.get("ms", 0)  # worker returns tail and ok, wait we need to extract ms? research.py prints it in meta...
        # Wait, run_tema returns {"ok": p.returncode == 0 and bool(path), "path": path, "tail": out[-800:]}
        # It doesn't return ms. But we can just measure it here!
""")
