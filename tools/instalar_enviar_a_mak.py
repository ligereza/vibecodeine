# -*- coding: utf-8 -*-
"""Instala la integracion "Enviar a" -> "MAK curatoria" en Windows.

Crea:
  1. C:\\IA\\flujo\\tools\\enviar_a_mak.bat
     - llama `py tools\\enviar_a_mak.py "%1"`, ventana visible, pausa al final.
  2. Un acceso directo "MAK curatoria.lnk" en
     %APPDATA%\\Microsoft\\Windows\\SendTo\\

Despues de correr esto: click derecho en cualquier carpeta -> Enviar a ->
"MAK curatoria".

Uso:
    py tools/instalar_enviar_a_mak.py
"""
from __future__ import annotations

import os
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
BAT_PATH = REPO_ROOT / "tools" / "enviar_a_mak.bat"

BAT_CONTENT = (
    "@echo off\r\n"
    "chcp 65001 >nul\r\n"
    "echo === MAK curatoria: enviando carpeta ===\r\n"
    'py "%~dp0enviar_a_mak.py" %1\r\n'
    "echo.\r\n"
    "echo (codigo de salida: %ERRORLEVEL%)\r\n"
    "pause\r\n"
)


def crear_bat() -> Path:
    BAT_PATH.write_bytes(BAT_CONTENT.encode("utf-8"))
    return BAT_PATH


def crear_acceso_sendto(bat_path: Path) -> Path:
    sendto = Path(os.environ["APPDATA"]) / "Microsoft" / "Windows" / "SendTo"
    sendto.mkdir(parents=True, exist_ok=True)
    lnk = sendto / "MAK curatoria.lnk"

    ps_script = f"""
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("{lnk}")
$Shortcut.TargetPath = "{bat_path}"
$Shortcut.WorkingDirectory = "{bat_path.parent}"
$Shortcut.Description = "Enviar carpeta a MAK curatoria (staging)"
$Shortcut.Save()
"""
    subprocess.run(
        ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", ps_script],
        check=True,
    )
    return lnk


def main() -> int:
    bat_path = crear_bat()
    print(f"Creado: {bat_path}")

    if os.name != "nt" or "APPDATA" not in os.environ:
        print("No es Windows (o falta %APPDATA%): solo se creo el .bat. "
              "Copia el acceso a SendTo manualmente en Windows.")
        return 0

    lnk_path = crear_acceso_sendto(bat_path)
    print(f"Creado: {lnk_path}")
    print('Listo: click derecho en una carpeta -> Enviar a -> "MAK curatoria".')
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
