@echo off
chcp 65001 >nul
echo === MAK curatoria: enviando carpeta ===
py "%~dp0enviar_a_mak.py" %1
echo.
echo (codigo de salida: %ERRORLEVEL%)
pause
