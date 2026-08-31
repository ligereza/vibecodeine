#!/bin/bash
# vigia_guardia.sh -- runs the watch once an hour and never twice at once.
#
# ITS OWN LOCK, on purpose. curatoria_guardia.sh and micelio_guardia.sh share
# ~/curatoria/.guardia.lock because they fight over one 4 GB GPU and only one
# may run. The vigia has the opposite problem: it uses no GPU and no model at
# all, it is six HTTP GETs and a sha256. Taking the shared lock would make it
# wait behind a perception run for hours -- and worse, it would make the watch
# invisible to itself the day the perception hangs. Different resource,
# different lock.
#
# What the lock DOES protect: two overlapping runs would both read vistos.jsonl
# before either wrote it, and every new item would be notified twice.
#
# Cron (hourly, at :45 to stay clear of the other MAK jobs):
#   45 * * * * /home/mak/vigia/vigia_guardia.sh >> \
#     /home/mak/plataforma/logs/vigia.log 2>&1 # MAK-VIGIA
#
# Topics come from the environment, and cron has almost none: they are read
# from the same env file the rest of the organism uses.
#
# Retirement: if the watch ever stops being a pure diff and needs a queue.
set -u

VIG="$HOME/vigia"
ENV_FILE="${VIGIA_ENV:-$HOME/n8n-local/research.env}"

mkdir -p "$VIG/estado"

exec 9>"$VIG/.vigia.lock" || exit 0
flock -n 9 || exit 0

# shellcheck disable=SC1090
[ -f "$ENV_FILE" ] && . "$ENV_FILE"
export VIGIA_NTFY_TOPIC="${VIGIA_NTFY_TOPIC:-${NTFY_TOPIC_OUT:-}}"
export VIGIA_NTFY_TOPIC_ENFERMERIA="${VIGIA_NTFY_TOPIC_ENFERMERIA:-}"

echo "== $(date '+%F %T') vigia =="
python3 "$VIG/vigia.py" --estado "$VIG/estado" --fuentes "$VIG/fuentes.json" \
  --ledger-oportunidades "$HOME/plataforma/common_ledger.jsonl" \
  --max-oportunidades-fuente 8
# Exit code 1 means at least one source is broken or stale. It is already a
# high-priority ntfy; keep it in the log too so the box's own health checks
# can see it without parsing the notification.
estado=$?
[ "$estado" -ne 0 ] && echo "$(date -Is) vigia: alguna fuente rota o estancada"
exit 0
