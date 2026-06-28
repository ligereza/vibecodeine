@echo off
REM ============================================================
REM  FLUJO - instalador / verificador del airdrop (Windows)
REM  Copia src\flujo\... y context\... a tu repo y verifica.
REM  Uso: doble clic, o  instalar.bat C:\ruta\al\repo
REM  Si no pasas ruta, asume que ya estas dentro del repo.
REM ============================================================
setlocal
cd /d "%~dp0"
set "DEST=%~1"
if "%DEST%"=="" set "DEST=%cd%"

echo Instalando FLUJO airdrop en: %DEST%
echo.

REM copiar paquetes (respeta estructura)
xcopy /E /I /Y "src\flujo" "%DEST%\src\flujo" >nul
xcopy /E /I /Y "context" "%DEST%\context" >nul
if exist "docs" xcopy /E /I /Y "docs" "%DEST%\docs" >nul

echo Verificando entorno...
cd /d "%DEST%\src"
py -m flujo doctor
echo.
echo ============================================================
echo  Listo. Comandos:
echo    py -m flujo serve --open     (hub en el navegador)
echo    py -m flujo doctor           (chequeo)
echo    py -m flujo index agent-brief "..."   (indexar C:\rd)
echo    py -m flujo route where --area eventos --pieza flyer
echo ============================================================
pause
