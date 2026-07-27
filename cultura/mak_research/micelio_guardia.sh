#!/bin/bash
# micelio_guardia.sh -- reindexa el micelio, pero NUNCA junto a una percepcion.
#
# Por que existe: el 2026-07-26 el corpus del artista (697 obras) desaparecio del
# indice y el reindexado lanzado para recuperarlo estuvo 7 minutos al 0.2% de CPU
# sin escribir una linea. La causa no era el codigo: memoria.py tenia 'corpus' en
# FUENTES y el gate correctamente scopeado. La causa era la GPU. percepcion.py
# tenia gemma3:4b residente ocupando 2846 de 4096 MiB y nomic-embed-text no
# entraba. Con la GPU libre el mismo reindexado tardo menos de un minuto.
#
# Es el mismo modo de falla que mato la corrida de julio, y la misma leccion que
# ya estaba escrita en curatoria_guardia.sh: un solo consumidor de GPU a la vez.
# Por eso este script toma EXACTAMENTE EL MISMO lock que la curatoria, y no uno
# propio: dos locks distintos no se ven entre si y no habrian evitado nada.
#
# Quien gana: la percepcion. flock -n sale en el acto si el lock esta tomado, asi
# que mientras haya percepcion corriendo el reindexado simplemente se saltea y lo
# reintenta al tick siguiente. Recupera el atraso solo, sin cola ni espera.
#
# Cron sugerido (cada 20 min):
#   */20 * * * * /home/mak/research/micelio_guardia.sh >> \
#     /home/mak/plataforma/logs/micelio.log 2>&1 # MAK-MICELIO
#
# Retiro: si el organismo pasa a una GPU donde percepcion y embebedor entran
# juntos, esta serializacion deja de hacer falta.
set -u

CUR="$HOME/curatoria"
RES="$HOME/research"

mkdir -p "$CUR"
exec 9>"$CUR/.guardia.lock" || exit 0
flock -n 9 || exit 0

# Doble red: el lock cubre lo que se lanza por la guardia, esto cubre una
# percepcion lanzada a mano (que es como se lanzaba antes de que hubiera cron).
if pgrep -f "percepcion.py correr" > /dev/null; then
    exit 0
fi

cd "$RES" || exit 0
echo "== $(date '+%F %T') reindexando micelio =="
python3 -c 'import sys; sys.path.insert(0, "."); import memoria; print(memoria.indexar())'
