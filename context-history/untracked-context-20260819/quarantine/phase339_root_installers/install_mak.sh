#!/bin/bash
# install_mak.sh -- instala el organismo MAK (corre EN MAK como usuario mak).
# Idempotente. Los pasos sudo van APARTE (los corre el operador).
set -eu
cd "$HOME"
echo "== permisos =="
chmod +x plataforma/*.sh plataforma/*.py codex/*.py lenguaje/*.py \
         lenguaje/*.sh xio_puente/monitor.py 2>/dev/null || true

echo "== token codex =="
if [ ! -f codex/.token ]; then
  python3 -c "import secrets; print('CODEX_TOKEN=' + secrets.token_urlsafe(18))" > codex/.token
  chmod 600 codex/.token
  echo "token generado en ~/codex/.token"
else
  echo "token ya existia"
fi

echo "== micelio: symlink codex =="
ln -sfn "$HOME/codex/piezas" "$HOME/research/codex"

echo "== patch memoria.py (fuente codex) e interfaz.py (color) =="
python3 - <<'PY'
import re
p = "/home/mak/research/memoria.py"
src = open(p, encoding="utf-8").read()
if '"codex"' not in src:
    src = src.replace('"correlaciones", "grafos")',
                      '"correlaciones", "grafos", "codex")', 1)
    open(p, "w", encoding="utf-8").write(src)
    print("memoria.py: fuente codex agregada")
else:
    print("memoria.py ya tenia codex")
p2 = "/home/mak/research/interfaz.py"
src2 = open(p2, encoding="utf-8").read()
cambiado = False
if '"codex":' not in src2:
    src2 = src2.replace('"memoria": "#e0c58f"}',
                        '"memoria": "#e0c58f", "codex": "#c9a86a"}', 1)
    cambiado = True
if "codex:'#c9a86a'" not in src2:
    src2 = src2.replace("memoria:'#e0c58f'};",
                        "memoria:'#e0c58f',codex:'#c9a86a'};", 1)
    cambiado = True
if cambiado:
    open(p2, "w", encoding="utf-8").write(src2)
    print("interfaz.py: color codex agregado (py+js)")
else:
    print("interfaz.py ya tenia color codex")
import py_compile
py_compile.compile(p, doraise=True)
py_compile.compile(p2, doraise=True)
print("compilan OK tras el patch")
PY

echo "== compilar todo =="
python3 -m py_compile plataforma/salud.py plataforma/guardia.py \
  plataforma/descargar.py plataforma/hub.py codex/codex_lib.py \
  codex/generar.py codex/revisar.py codex/testear.py codex/worker_codex.py \
  codex/interfaz_codex.py lenguaje/lenguaje_lib.py lenguaje/medir.py \
  lenguaje/corregir.py lenguaje/hook_barrido.py xio_puente/monitor.py
echo "py_compile OK"

echo "== systemd user units =="
mkdir -p .config/systemd/user
cat > .config/systemd/user/mak-hub.service <<EOF
[Unit]
Description=MAK hub (plataforma :8900)
[Service]
ExecStart=/usr/bin/python3 %h/plataforma/hub.py
Restart=always
RestartSec=5
[Install]
WantedBy=default.target
EOF
cat > .config/systemd/user/mak-codex.service <<EOF
[Unit]
Description=MAK codex (:8891, token en ~/codex/.token)
[Service]
EnvironmentFile=%h/codex/.token
ExecStart=/usr/bin/python3 %h/codex/interfaz_codex.py
Restart=always
RestartSec=5
[Install]
WantedBy=default.target
EOF
cat > .config/systemd/user/mak-xio.service <<EOF
[Unit]
Description=MAK xio puente (monitor GET-only)
[Service]
ExecStart=/usr/bin/python3 %h/xio_puente/monitor.py
Restart=always
RestartSec=10
[Install]
WantedBy=default.target
EOF

echo "== cron (merge idempotente) =="
( crontab -l 2>/dev/null | grep -v "MAK-ORGANISMO" ) > /tmp/cron_nuevo || true
cat >> /tmp/cron_nuevo <<EOF
*/5 * * * * $HOME/plataforma/watchdog_mak.sh # MAK-ORGANISMO watchdog
30 4 * * * $HOME/plataforma/backup.sh >> $HOME/plataforma/logs/backup.log 2>&1 # MAK-ORGANISMO backup
0 5 * * * $HOME/lenguaje/cron_lexicon.sh # MAK-ORGANISMO lexicon
*/10 * * * * /usr/bin/python3 $HOME/lenguaje/hook_barrido.py >> $HOME/plataforma/logs/hook.log 2>&1 # MAK-ORGANISMO senal
EOF
crontab /tmp/cron_nuevo
rm /tmp/cron_nuevo
echo "cron instalado: $(crontab -l | grep -c MAK-ORGANISMO) lineas"

echo "== diccionarios de espanol =="
if [ ! -f lenguaje/diccionarios/es.txt ]; then
  bash lenguaje/instalar_diccionarios.sh || echo "AVISO: diccionario fallo (URL o red); correr a mano despues"
else
  echo "diccionario ya presente"
fi

echo "== lexicon inicial + primer barrido de senal =="
bash lenguaje/cron_lexicon.sh || true
python3 lenguaje/hook_barrido.py || true

echo "== INSTALACION BASE LISTA =="
