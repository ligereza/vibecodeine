import re

with open("interfaz.py", "r") as f:
    code = f.read()

# 1. Add JOBS_FILE and _load_jobs()
code = code.replace(
    "JOBS = []  # historial en memoria: {tema, modo, estado, path, t}",
    """JOBS_FILE = os.path.expanduser("~/research/jobs.jsonl")
JOBS = []  # historial en memoria: {tema, modo, estado, path, t}

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

_load_jobs()"""
)

# 2. Modify _lanzar to measure time and persist job
old_correr = """    def correr():
        job["estado"] = "corriendo"
        r = run_tema(modo, tema, n=n, ntfy=True)
        job["estado"] = "listo" if r["ok"] else "FALLO"
        job["path"] = os.path.basename(r["path"]) if r["path"] else ""

    threading.Thread(target=correr, daemon=True).start()"""

new_correr = """    def correr():
        t0 = time.time()
        job["estado"] = "corriendo"
        r = run_tema(modo, tema, n=n, ntfy=True)
        job["estado"] = "listo" if r["ok"] else "FALLO"
        job["path"] = os.path.basename(r["path"]) if r["path"] else ""
        job["ms"] = int((time.time() - t0) * 1000)
        
        # Persistir el job atomico y append
        try:
            with open(JOBS_FILE, "a", encoding="utf-8") as f:
                f.write(json.dumps(job) + "\\n")
        except OSError:
            pass

    threading.Thread(target=correr, daemon=True).start()"""
code = code.replace(old_correr, new_correr)

# 3. Add auth check in H class
old_class_h = """class H(BaseHTTPRequestHandler):
    def _html(self, body, code=200):"""

new_class_h = """TOKEN = os.environ.get("INTERFAZ_TOKEN")

class H(BaseHTTPRequestHandler):
    def _check_auth(self):
        if not TOKEN:
            return True
        q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        t = (q.get("t") or [""])[0]
        if t == TOKEN or self.headers.get("X-Token") == TOKEN:
            return True
        self._html("No autorizado", 401)
        return False

    def _html(self, body, code=200):"""
code = code.replace(old_class_h, new_class_h)

# 4. Auth checks in do_GET and do_POST
code = code.replace("    def do_GET(self):", "    def do_GET(self):\n        if not self._check_auth(): return")
code = code.replace("    def do_POST(self):", "    def do_POST(self):\n        if not self._check_auth(): return")

# 5. Fix Javascript and HTML to include ?t=token
code = code.replace("let url = '/status';", "let url = '/status';") # wait it doesn't have url var

old_js = """        let r = await fetch('/status');"""
new_js = """        let t = new URLSearchParams(window.location.search).get('t');
        let r = await fetch(t ? '/status?t=' + encodeURIComponent(t) : '/status');"""
code = code.replace(old_js, new_js)

old_form = """<form method="post" action="/run">"""
new_form = """<form method="post" action="/run" id="runform">
<script>
let t = new URLSearchParams(window.location.search).get('t');
if (t) document.getElementById('runform').action = '/run?t=' + encodeURIComponent(t);
</script>"""
code = code.replace(old_form, new_form)

old_a_paneles = """<a href="/f?d=%s&n=%s">ver</a>"""
new_a_paneles = """<a href="/f?d=%s&n=%s" class="lnk-ver">ver</a>"""
code = code.replace(old_a_paneles, new_a_paneles)

old_a_listas = """<li><a href="/f?d=%s&n=%s">%s</a></li>"""
new_a_listas = """<li><a href="/f?d=%s&n=%s" class="lnk-ver">%s</a></li>"""
code = code.replace(old_a_listas, new_a_listas)

# Also need to append ?t=... to links in the page if token is present
# I can just use a bit of JS at the end of the page to append it
append_js = """
<script>
if (t) {
    document.querySelectorAll('a.lnk-ver').forEach(a => {
        a.href = a.href + '&t=' + encodeURIComponent(t);
    });
}
</script>
"""
code = code.replace("<h3>paneles</h3><ul>{paneles}</ul>", '<h3>paneles</h3><ul>{paneles}</ul>' + append_js)


with open("interfaz.py", "w") as f:
    f.write(code)
