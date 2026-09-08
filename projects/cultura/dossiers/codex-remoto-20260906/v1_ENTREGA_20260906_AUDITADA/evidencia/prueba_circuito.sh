#!/usr/bin/env bash
# Prueba reproducible del circuito IRIS servido por el Hub de MAK (puerto 8900).
# No escribe nada en el archivo de produccion: solo GET y un POST de control.
# Uso: bash evidencia/prueba_circuito.sh
B="${IRIS_BASE:-http://127.0.0.1:8900}"
echo "# Prueba circuito IRIS  ---  $(date -Is)"
echo "# base: $B"
echo
printf "%-38s %-5s %-10s %s\n" RUTA HTTP BYTES TIPO
for r in /portafolio/ /portafolio/editor.html /portafolio/mesa_montaje.js \
         /portafolio/datos/archivo.json /portafolio/datos/campo.json \
         /portafolio/datos/obras.json /portafolio/datos/curaduria.json \
         /portafolio/datos/tablero.json /portafolio/CONTRATO.md; do
  code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 10 "$B$r")
  size=$(curl -s --max-time 10 "$B$r" | wc -c)
  ctyp=$(curl -s -o /dev/null -w '%{content_type}' --max-time 10 "$B$r")
  printf "%-38s %-5s %-10s %s\n" "$r" "$code" "$size" "$ctyp"
done
echo
echo "# Control de escritura (se espera 404: la superficie es de solo lectura)"
printf "POST /portafolio/datos/curaduria.json -> %s\n" \
  "$(curl -s -o /dev/null -w '%{http_code}' --max-time 10 -X POST -d '{}' "$B/portafolio/datos/curaduria.json")"
echo
echo "# Corpus (lectura local, sin modificar)"
python3 - <<'PY'
import json, collections, os
H = os.path.expanduser("~/iskvw/datos")
a = json.load(open(f"{H}/archivo.json"))
c = json.load(open(f"{H}/campo.json"))
u = json.load(open(f"{H}/curaduria.json"))
print(f"archivo.json   generado={a['generado']}  piezas={len(a['piezas'])}  vinculos={len(a['vinculos'])}")
print(f"               por_clase={a['meta']['por_clase']}  por_medio={a['meta']['por_medio']}")
print(f"campo.json     piezas={len(c['piezas'])}  con_percepcion={c['meta']['con_percepcion']}"
      f"  filtradas={c['meta']['filtradas']}  vecindad_conservada={c['meta']['vecindad_conservada']}")
print("               tipos=", collections.Counter(x.get('tipo') for x in c['piezas']).most_common())
print(f"curaduria.json decisiones humanas registradas = {len(u['piezas'])}")
PY
