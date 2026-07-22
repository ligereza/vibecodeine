# Director snapshot — Windows → MAK

Generado: `2026-07-21T05:01:16+00:00`  
Modo: **solo lectura**. Este archivo no prueba que una configuracion documentada siga vigente: registra lo que fue observable durante esta corrida.

## Resumen rapido

- SSH MAK: **ok**
- APIs inaccesibles: **ninguna**
- Repo local Windows: rama `main`, HEAD `e88a419e2893`

## APIs LAN

| Servicio | Estado | Evidencia minima |
|---|---|---|
| research :8890 | ok | HTTP 200 |
| codex :8891 | ok | HTTP 200 |
| hub :8900 | ok | HTTP 200; JSON keys: desde, proveedores |

## Checkout Windows

```text
root=C:\IA\flujo
branch=main
head=e88a419e2893aad8033d4f3b585319850a6e938e
status=?? director_snapshot.md
?? director_snapshot.py
?? director_snapshot_2.md
?? mak_sync_repair.md
?? repair_mak_sync.py
```

## Lectura remota MAK por SSH

```text
@@ IDENTITY @@
dell-11m
2026-07-21T01:01:16-04:00
Linux 6.1.0-50-amd64 x86_64 GNU/Linux

@@ RESOURCES @@
 01:01:16 up  1:48,  1 user,  load average: 0,04, 0,09, 0,19
               total       usado       libre  compartido   búf/caché   disponible
Mem:            15Gi       4,8Gi       3,3Gi       721Mi       8,3Gi        10Gi
Inter:         8,7Gi        10Mi       8,7Gi
S.ficheros     Tamaño Usados  Disp Uso% Montado en
/dev/sda2        456G    62G  372G  15% /
NVIDIA GeForce GTX 1650, 4096 MiB, 6 MiB

@@ PORTS @@
LISTEN 0      4096       127.0.0.1:11434      0.0.0.0:*          
LISTEN 0      5            0.0.0.0:8900       0.0.0.0:*          
LISTEN 0      5            0.0.0.0:8891       0.0.0.0:*          
LISTEN 0      5            0.0.0.0:8890       0.0.0.0:*          

@@ CRON @@
*/5 * * * * /home/mak/research/watchdog.sh >> /home/mak/research/watchdog.log 2>&1
*/5 * * * * /home/mak/plataforma/watchdog_mak.sh # MAK-ORGANISMO watchdog
30 4 * * * /home/mak/plataforma/backup.sh >> /home/mak/plataforma/logs/backup.log 2>&1 # MAK-ORGANISMO backup
0 5 * * * /home/mak/lenguaje/cron_lexicon.sh # MAK-ORGANISMO lexicon
*/10 * * * * /usr/bin/python3 /home/mak/lenguaje/hook_barrido.py >> /home/mak/plataforma/logs/hook.log 2>&1 # MAK-ORGANISMO senal
*/5 * * * * /usr/bin/python3 /home/mak/plataforma/vigilar_red.py >> /home/mak/plataforma/logs/vigilar.log 2>&1 # MAK-VIGILAR
*/30 * * * * /usr/bin/python3 /home/mak/plataforma/trabajo.py >/dev/null 2>&1 # MAK-TRABAJO
*/2 * * * * /usr/bin/python3 /home/mak/plataforma/red_watch.py >/dev/null 2>&1 # MAK-REDWATCH
0 */6 * * * /usr/bin/python3 /home/mak/plataforma/entregar.py --limit 1 >> /home/mak/plataforma/logs/entregar.log 2>&1 # MAK-ENTREGAR
17 */12 * * * /usr/bin/python3 /home/mak/plataforma/backlog_codex.py >> /home/mak/plataforma/logs/backlog_codex.log 2>&1 # MAK-BACKLOG-CODEX
35 6 * * * /usr/bin/python3 /home/mak/plataforma/junta.py >> /home/mak/plataforma/logs/junta.log 2>&1 # MAK-JUNTA
15 7 * * * /usr/bin/python3 /home/mak/codex/agente_libre.py >> /home/mak/plataforma/logs/agente_libre.log 2>&1 # MAK-AGENTE-LIBRE
20 */6 * * * cd /home/mak/flujo && /usr/bin/python3 /home/mak/plataforma/revisor.py --enforce >> /home/mak/plataforma/logs/revisor.log 2>&1 # MAK-REVISOR
10,40 * * * * /usr/bin/python3 /home/mak/plataforma/capataz.py >> /home/mak/plataforma/logs/capataz.log 2>&1 # MAK-CAPATAZ
25,55 * * * * cd /home/mak/plataforma && /usr/bin/python3 agente_real.py >> /home/mak/plataforma/logs/agente_real.log 2>&1 # MAK-AGENTE-REAL
*/10 * * * * git -C /home/mak/flujo fetch -q origin +refs/heads/main:refs/remotes/origin/main && git -C /home/mak/flujo checkout -q -B main origin/main && git -C /home/mak/flujo reset -q --hard origin/main && cp -ru /home/mak/flujo/cultura/mak_plataforma/. /home/mak/plataforma/ && cp -ru /home/mak/flujo/cultura/mak_research/. /home/mak/research/ && cp -ru /home/mak/flujo/cultura/mak_codex/. /home/mak/codex/ # MAK-REPO-SYNC

@@ PROCESSES @@
    402    6515 watchdogd       [watchdogd]
    979    6512 python3         /usr/bin/python3 /home/mak/codex/interfaz_codex.py
    980    6512 python3         /usr/bin/python3 /home/mak/plataforma/hub.py
   4184    6374 python3         python3 /home/mak/research/cola.py
   4188    6374 python3         python3 /home/mak/research/interfaz.py
  15854      74 python3         /usr/bin/python3 /home/mak/codex/revisar.py /home/mak/research/research_lib.py --densidad medio --ntfy

@@ LIVE_DIRS @@
/home/mak/flujo=present
/home/mak/plataforma=present
/home/mak/research=present
/home/mak/codex=present

@@ GIT @@
## main...origin/main
HEAD=3d3f7a1693067cadeb7e678cd8070c75801049ab
DATE=2026-07-21 00:10:11 -0400
SUBJECT=feat(mak): utilidad autogenerada -- un-visor-stdlib-que-lea-logs-red-jsonl-y (#120)

@@ CONTROL_FILES @@
/home/mak/plataforma/trabajo.py=present
/home/mak/plataforma/guardia.py=present
/home/mak/plataforma/agente_real.py=present
```

## Contrato de interpretacion

- `ok` significa que esta corrida obtuvo respuesta; no significa que todo el sistema este sano.
- `unreachable` significa que no hubo respuesta mediante este canal; no autoriza cambiar configuracion.
- No hay logs, secretos, .env, datos de RD ni contenido de bases en este snapshot.
- El siguiente paso debe basarse en diferencias entre esta evidencia y la documentacion, no en suposiciones.

## Prompt para analisis local o agente director

Usa exclusivamente este snapshot y las fuentes versionadas del repo. Responde en maximo 500 palabras:

1. Separa hechos observados, documentacion historica y datos desconocidos.
2. Enumera contradicciones relevantes con `context/LAST_HANDOFF.md`, `cultura/mak_plataforma/GENESIS.md`, `tools/mak/delegar.py` y `cultura/mak_plataforma/trabajo.py`.
3. Elige UNA siguiente observacion de solo lectura que reduzca mas incertidumbre.
4. Indica explicitamente si corresponde o no crear un airdrop. Por defecto: NO.
5. No propongas cambios de red, cron, servicios, credenciales, XIO, datos RD, modelos, instalaciones ni merges.
