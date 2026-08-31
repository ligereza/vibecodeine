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
7 */4 * * * cd ~/plataforma && python3 latido.py >> logs/latido_cron.log 2>&1 # MAK-LATIDO restaurado 2026-07-22
*/10 * * * * /home/mak/curatoria/curatoria_guardia.sh rd # MAK-CURATORIA
15 * * * * /usr/bin/python3 /home/mak/plataforma/material.py >> /home/mak/plataforma/logs/material.log 2>&1 # MAK-MATERIAL
35 * * * * /usr/bin/python3 /home/mak/research/corpus_a_micelio.py >> /home/mak/plataforma/logs/corpus.log 2>&1 # MAK-CORPUS
45 * * * * /home/mak/vigia/vigia_guardia.sh >> /home/mak/plataforma/logs/vigia.log 2>&1 # MAK-VIGIA
*/20 * * * * /home/mak/research/micelio_guardia.sh >> /home/mak/plataforma/logs/micelio.log 2>&1 # MAK-MICELIO
*/10 * * * * FLUJO_GPU_BACKEND=CUDA /usr/bin/python3 /home/mak/plataforma/puente_issues.py >> /home/mak/plataforma/logs/puente_issues.log 2>&1 # MAK-PUENTE-ISSUES
# PAUSED-FARO */10 * * * * git -C /home/mak/flujo fetch -q origin +refs/heads/main:refs/remotes/origin/main && git -C /home/mak/flujo checkout -q -B main origin/main && git -C /home/mak/flujo reset -q --hard origin/main && cp -r /home/mak/flujo/cultura/mak_plataforma/. /home/mak/plataforma/ && cp -r /home/mak/flujo/cultura/mak_research/. /home/mak/research/ && cp -r /home/mak/flujo/cultura/mak_codex/. /home/mak/codex/ && cp -r /home/mak/flujo/cultura/mak_curatoria/. /home/mak/curatoria/  && cp -r /home/mak/flujo/cultura/mak_xio_puente/. /home/mak/xio_puente/ && mkdir -p /home/mak/vigia && cp -r /home/mak/flujo/cultura/mak_vigia/. /home/mak/vigia/ # MAK-REPO-SYNC
10 5 * * * /usr/bin/python3 /home/mak/research/retencion.py --dir /home/mak/research/informes --keep 50 --apply >> /home/mak/plataforma/logs/retencion.log 2>&1 # MAK-RETENCION
20 5 * * * /usr/bin/python3 /home/mak/research/retencion.py --dir /home/mak/research/paneles --keep 50 --apply >> /home/mak/plataforma/logs/retencion.log 2>&1 # MAK-RETENCION
# PAUSED-NEW-HEARTBEAT-20260830 */15 * * * * /usr/bin/python3 /home/mak/flujo/tools/mak_heartbeat.py >> /home/mak/plataforma/logs/mak_heartbeat.log 2>&1 # MAK-HEARTBEAT
