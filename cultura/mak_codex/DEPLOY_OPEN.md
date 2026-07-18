# Codex ABIERTO en MAK -- YA DESPLEGADO (2026-07-18)

ESTADO: **HECHO Y VERIFICADO.** No hay que correr nada de nuevo salvo que se
vuelva a caer o se toque la topologia.

## Que se hizo (2026-07-18)
- Se borro TODO el token/auth del codigo (codex + research). Detalle en PR #71.
- Se desplegaron al box vivo `192.168.50.2` SOLO los 2 archivos que cambiaron:
  - `~/codex/interfaz_codex.py`  (sin `_auth`, sin `TOKEN`)
  - `~/plataforma/watchdog_mak.sh`  (arranca codex sin token)
  - `codex_lib.py` NO se toco -> NO se copio (copiarlo regresaria el vivo).
- Se removio `~/codex/.token` del box.
- Se reinicio codex. Verificado: `curl http://192.168.50.2:8891/api/jobs` -> **200**
  sin token; log dice `(abierto, sin token)`; un job real (`resumir_jobs.py`)
  corrio y quedo `listo`.

Antes del deploy confirme que el `interfaz_codex.py` y el `watchdog_mak.sh`
vivos eran byte-identicos al mirror del repo salvo el borrado de token -> deploy
sin perdida (0 divergencia).

## Re-desplegar (solo si hace falta otra vez)
Desde Git Bash de Windows. NO copiar codex_lib.py. Sin placeholder `<repo>`:

    scp /c/IA/flujo/.claude/worktrees/god-haiku-fixes/cultura/mak_codex/interfaz_codex.py mak@192.168.50.2:~/codex/interfaz_codex.py
    scp /c/IA/flujo/.claude/worktrees/god-haiku-fixes/cultura/mak_plataforma/watchdog_mak.sh mak@192.168.50.2:~/plataforma/watchdog_mak.sh
    ssh mak@192.168.50.2 "rm -f ~/codex/.token; pkill -f codex/interfaz_codex.py; sleep 1; setsid python3 ~/codex/interfaz_codex.py >>~/plataforma/logs/codex.log 2>&1 </dev/null & sleep 1; echo OK-abierto"

Verificar (200): `curl -s -o /dev/null -w "%{http_code}\n" http://192.168.50.2:8891/api/jobs`

El agente Claude NO puede correr esto (el guardrail bloquea SSH que toca auth
remota). Lo corre el operador con `!` o en cualquier terminal.

## Usar
    py tools/mak/delegar.py codex --pedido "<lo que sea>" --modo generar
    # abierto: sin token

## Revertir (si Face A deja de ser privada)
`git checkout <commit-con-token> -- cultura/mak_codex/interfaz_codex.py` y
re-desplegar, o implementar auth minima (IP whitelist / bind a localhost).
research (:8890) ya era auth-opcional (solo si `INTERFAZ_TOKEN`), esta abierto igual.
