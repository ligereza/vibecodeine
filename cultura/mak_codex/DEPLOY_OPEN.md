# Desplegar codex ABIERTO (auth opcional) en el Linux MAK

Contexto: `interfaz_codex.py` y `watchdog_mak.sh` (este repo, cultura/) ya
traen auth OPCIONAL -- sin `CODEX_TOKEN` en el entorno, codex corre abierto.
Es seguro en xio Face A (LAN privada casa: Linux MAK + Windows; el Linux nunca
sale a los shows -> ver `xio/FACES.md`). Falta reflejarlo en el box vivo.

El agente Claude NO puede hacer esto (el guardrail bloquea SSH que toque la
auth de un servicio remoto). Corre TU una de estas, con el prefijo `!` en la
consola de Claude Code o en cualquier terminal.

## Opcion A -- el box tiene este repo clonado

    ! ssh mak@192.168.50.2 "cd ~/<repo>/cultura && \
      cp mak_codex/interfaz_codex.py ~/codex/interfaz_codex.py && \
      cp mak_plataforma/watchdog_mak.sh ~/plataforma/watchdog_mak.sh && \
      mv ~/codex/.token ~/codex/.token.disabled 2>/dev/null; \
      pkill -f codex/interfaz_codex.py; sleep 1; \
      unset CODEX_TOKEN; setsid python3 ~/codex/interfaz_codex.py \
        >>~/plataforma/logs/codex.log 2>&1 </dev/null & sleep 1; \
      echo 'codex reiniciado ABIERTO'"

## Opcion B -- copiar desde el Windows (no hace falta repo en el box)

    ! W=C:/IA/flujo/.claude/worktrees/god-haiku-fixes; \
      scp "$W/cultura/mak_codex/interfaz_codex.py" mak@192.168.50.2:~/codex/interfaz_codex.py && \
      scp "$W/cultura/mak_plataforma/watchdog_mak.sh" mak@192.168.50.2:~/plataforma/watchdog_mak.sh && \
      ssh mak@192.168.50.2 "mv ~/codex/.token ~/codex/.token.disabled 2>/dev/null; \
        pkill -f codex/interfaz_codex.py; sleep 1; unset CODEX_TOKEN; \
        setsid python3 ~/codex/interfaz_codex.py >>~/plataforma/logs/codex.log 2>&1 </dev/null & \
        sleep 1; echo 'codex reiniciado ABIERTO'"

## Verificar (deberia dar 200 sin token)

    ! curl -s -o /dev/null -w "%{http_code}\n" http://192.168.50.2:8891/api/jobs

## Re-bloquear (si algun dia queres la llave de vuelta)

    ! ssh mak@192.168.50.2 "mv ~/codex/.token.disabled ~/codex/.token; \
      pkill -f codex/interfaz_codex.py"
    # el watchdog (cron */5) lo revive BLOQUEADO al ver el .token

## Despues: correr un job real de codex desde el Windows

    py tools/mak/delegar.py codex --pedido "<lo que sea>" --modo generar
    # abierto -> ya no hace falta --token-file
