"""Every script MAK's cron invokes must exist in the repo tree.

Cause (2026-07-30): PR #406 deleted cultura/mak_plataforma/agente_real.py
without a word in its message, while the box's crontab kept running it every
30 minutes from the local copy -- which the sync can never reconcile because
cp -ru does not delete. Code invoked by cron but absent from the repo is
live code governed by nothing: the recurring reason "MAK never quite works".

cultura/mak_plataforma/crontab.mak is the box's crontab, versioned. It does
NOT deploy automatically (applying it stays a deliberate act on the box);
what this test guards is the REFERENCES: deleting a repo file that the cron
still names turns CI red in the same PR that deletes it.

Retirement: when the sync applies the crontab itself, or MAK stops using cron.
"""
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
CRONTAB = RAIZ / "cultura" / "mak_plataforma" / "crontab.mak"

# /home/mak/<runtime dir> -> where that code lives in the repo
ESPEJO = {
    "plataforma": "cultura/mak_plataforma",
    "research": "cultura/mak_research",
    "codex": "cultura/mak_codex",
    "curatoria": "cultura/mak_curatoria",
    "lenguaje": "cultura/mak_lenguaje",
    "vigia": "cultura/mak_vigia",
}

# Box-local by design: state, logs, or infrastructure the repo does not carry.
# Every entry needs a reason; an unexplained entry here defeats the test.
SOLO_CAJA = {
    "/home/mak/flujo",           # the clone itself (git handles it)
    "/home/mak/curatoria_inbox", # inbox de material, no codigo
}


def _scripts_invocados():
    lineas = CRONTAB.read_text(encoding="utf-8").splitlines()
    rutas = []
    for ln in lineas:
        ln = ln.strip()
        if not ln or ln.startswith("#"):
            continue
        for m in re.finditer(r"/home/mak/[\w./-]+\.(?:py|sh)", ln):
            rutas.append(m.group(0))
    return rutas


def test_todo_script_del_cron_existe_en_el_repo():
    assert CRONTAB.exists(), "crontab.mak missing: re-capture with ssh crontab -l"
    faltantes = []
    for ruta in _scripts_invocados():
        if any(ruta.startswith(p) for p in SOLO_CAJA):
            continue
        m = re.match(r"/home/mak/(\w+)/(.+)$", ruta)
        if not m:
            continue
        carpeta, resto = m.groups()
        espejo = ESPEJO.get(carpeta)
        if espejo is None:
            faltantes.append(f"{ruta} (runtime dir '{carpeta}' has no repo mirror mapping)")
            continue
        if not (RAIZ / espejo / resto).exists():
            faltantes.append(f"{ruta} -> {espejo}/{resto} DOES NOT EXIST in the repo")
    assert not faltantes, (
        "MAK's cron invokes code the repo does not have. Either restore the "
        "file, or retire the cron line in crontab.mak IN THE SAME CHANGE:\n  "
        + "\n  ".join(faltantes)
    )
