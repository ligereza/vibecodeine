#!/usr/bin/env python3
"""puente.py -- relay de conversacion entre Antigravity y VSCode/Copilot.

Protocolo: cada agente escribe SU buzon; el puente detecta el cambio y
avisa al otro por su canal nativo. El contenido viaja en el archivo,
el aviso es corto.

  Antigravity escribe -> buzon_para_vscode.md      -> aviso via `code chat`
  VSCode escribe      -> buzon_para_antigravity.md -> append a ordenes_director.md

Freno anti-loop: maximo MAX_HORA relays por hora y por direccion; todo
queda en conversacion.log. Correr: nohup python3 puente.py >> puente.log 2>&1 &
"""
import hashlib
import os
import subprocess
import time

BASE = os.path.expanduser("~/research")
B_VSCODE = os.path.join(BASE, "buzon_para_vscode.md")
B_ANTI = os.path.join(BASE, "buzon_para_antigravity.md")
ORDENES = os.path.join(BASE, "ordenes_director.md")
LOG = os.path.join(BASE, "conversacion.log")
CODE = os.path.expanduser("~/.local/bin/code")
MAX_HORA = 8  # relays maximos por hora por direccion (freno de cuota)
ENV_GUI = {**os.environ, "DISPLAY": ":1",
           "XAUTHORITY": "/run/user/1000/gdm/Xauthority"}


def h(path):
    try:
        return hashlib.sha1(open(path, "rb").read()).hexdigest()
    except OSError:
        return ""


def log(msg):
    with open(LOG, "a", encoding="utf-8") as f:
        f.write("%s %s\n" % (time.strftime("%H:%M:%S"), msg))


def main():
    ultimo = {B_VSCODE: h(B_VSCODE), B_ANTI: h(B_ANTI)}
    relays = {B_VSCODE: [], B_ANTI: []}  # timestamps ultima hora
    log("puente arriba")
    while True:
        for buzon in (B_VSCODE, B_ANTI):
            actual = h(buzon)
            if not actual or actual == ultimo[buzon]:
                continue
            ultimo[buzon] = actual
            ahora = time.time()
            relays[buzon] = [t for t in relays[buzon] if ahora - t < 3600]
            if len(relays[buzon]) >= MAX_HORA:
                log("FRENO: %s supero %d/hora, no se relaya"
                    % (os.path.basename(buzon), MAX_HORA))
                continue
            relays[buzon].append(ahora)
            if buzon == B_VSCODE:
                subprocess.run(
                    [CODE, "chat", "Antigravity te dejo un mensaje nuevo en "
                     "buzon_para_vscode.md. Leelo y respondele escribiendo/"
                     "actualizando buzon_para_antigravity.md."],
                    env=ENV_GUI, capture_output=True, timeout=30)
                log("relay -> vscode (code chat)")
            else:
                with open(ORDENES, "a", encoding="utf-8") as f:
                    f.write("\n# MENSAJE DEL AGENTE VSCODE (%s)\n\n"
                            "VSCode te escribio: lee buzon_para_antigravity.md "
                            "y respondele escribiendo/actualizando "
                            "buzon_para_vscode.md.\n"
                            % time.strftime("%H:%M"))
                log("relay -> antigravity (ordenes_director.md)")
        time.sleep(60)


if __name__ == "__main__":
    main()
