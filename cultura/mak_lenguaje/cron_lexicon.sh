#!/bin/bash
# cron_lexicon.sh -- reconstruye el lexico vivo (cron diario 05:00)
set -u
python3 - >> "$HOME/lenguaje/lexico/cron.log" 2>&1 <<'PY'
import sys, time
sys.path.insert(0, "/home/mak/lenguaje")
from lenguaje_lib import construir_lexicon
dirs = ["/home/mak/research/" + d for d in
        ("informes", "paneles", "cadenas", "refutaciones",
         "correlaciones", "grafos")] + ["/home/mak/codex/piezas"]
r = construir_lexicon(dirs)
print("%s lexicon: %s" % (time.strftime("%F %T"), r))
PY
