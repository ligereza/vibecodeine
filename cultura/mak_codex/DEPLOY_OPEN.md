# Desplegar codex ABIERTO (sin token) en MAK

Contexto: `interfaz_codex.py`, `codex_lib.py` y `watchdog_mak.sh` (este repo,
cultura/) han sido limpiados completamente de token: NO hay claves en el codigo,
NO hay archivos .token/.token.disabled, NO hay variables CODEX_TOKEN en el
entorno. Codex corre 100% abierto en xio Face A (LAN privada casa: Linux MAK +
Windows; el Linux nunca sale a los shows -> ver `xio/FACES.md`). Desplegar el
codigo limpio al box.

El agente Claude NO puede hacer esto (el guardrail bloquea SSH que toque la
configuracion remota). Corre TU una de estas, con el prefijo `!` en la
consola de Claude Code o en cualquier terminal.

## Opcion A -- el box tiene este repo clonado

    ! ssh mak@192.168.50.2 "cd ~/<repo>/cultura && \
      cp mak_codex/interfaz_codex.py ~/codex/interfaz_codex.py && \
      cp mak_codex/codex_lib.py ~/codex/codex_lib.py && \
      cp mak_plataforma/watchdog_mak.sh ~/plataforma/watchdog_mak.sh && \
      rm -f ~/codex/.token ~/codex/.token.disabled; \
      pkill -f codex/interfaz_codex.py; sleep 1; \
      setsid python3 ~/codex/interfaz_codex.py >>~/plataforma/logs/codex.log 2>&1 </dev/null & \
      sleep 1; echo 'codex reiniciado ABIERTO (sin token)'"

## Opcion B -- copiar desde el Windows (no hace falta repo en el box)

    ! W=C:/IA/flujo/.claude/worktrees/god-haiku-fixes; \
      scp "$W/cultura/mak_codex/interfaz_codex.py" mak@192.168.50.2:~/codex/ && \
      scp "$W/cultura/mak_codex/codex_lib.py" mak@192.168.50.2:~/codex/ && \
      scp "$W/cultura/mak_plataforma/watchdog_mak.sh" mak@192.168.50.2:~/plataforma/watchdog_mak.sh && \
      ssh mak@192.168.50.2 "rm -f ~/codex/.token ~/codex/.token.disabled; \
        pkill -f codex/interfaz_codex.py; sleep 1; \
        setsid python3 ~/codex/interfaz_codex.py >>~/plataforma/logs/codex.log 2>&1 </dev/null & \
        sleep 1; echo 'codex reiniciado ABIERTO (sin token)'"

## Verificar (deberia dar 200 sin token)

    ! curl -s -o /dev/null -w "%{http_code}\n" http://192.168.50.2:8891/api/jobs

## Usar despues del deploy

Codex corre abierto en http://192.168.50.2:8891. Delegar jobs desde Windows:

    py tools/mak/delegar.py codex --pedido "<lo que sea>" --modo generar
    # abierto -> sin token requerido

## Revertir (si la topologia cambia y necesitas seguridad)

Si algun dia la LAN Face A se expande a nodos publicos, recuperar el token gate
desde una version anterior del repo:

    ! ssh mak@192.168.50.2 "cd ~/<repo> && git checkout HEAD~N -- cultura/mak_codex/interfaz_codex.py"
    # (donde HEAD~N es una version anterior con token)

O implementar auth minima en interfaz_codex.py (ej. CORS restrictivo, IP whitelist).

## Regla de seguridad

Codex es abierto por arquitectura: confía en que la LAN privada Face A
no recibe trafico externo. La guardia de contenido (sandbox + static filter)
sigue siendo la unica defensa. Si esa confianza cambia, volver a poner el
token o restringir el endpoint a localhost.
