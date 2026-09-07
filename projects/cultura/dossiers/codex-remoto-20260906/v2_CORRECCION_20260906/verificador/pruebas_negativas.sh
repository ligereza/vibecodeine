#!/usr/bin/env bash
# Pruebas negativas del verificador. Copia los CSV a un directorio temporal,
# inyecta una inconsistencia por caso y comprueba que el verificador FALLA.
# Un verificador que solo imprime sumas no sirve: esto demuestra que detecta.
# No toca los CSV entregados.
set -u
AQUI="$(cd "$(dirname "$0")" && pwd)"
SRC="$AQUI/../presupuestos"
V="$AQUI/verificar_presupuestos.py"
ok=0; fallidas=0; inyectados=0

caso() { # nombre  comando-de-mutacion
  local nombre="$1"; shift
  local T; T="$(mktemp -d)"
  cp "$SRC"/*.csv "$T"/
  ( cd "$T" && eval "$@" )
  if python3 "$V" --dir "$T" >/dev/null 2>&1; then
    printf "  FALLA  %-52s el verificador NO detecto el defecto\n" "$nombre"; fallidas=$((fallidas+1))
  else
    printf "  ok     %-52s detectado\n" "$nombre"; ok=$((ok+1)); inyectados=$((inyectados+1))
  fi
  rm -rf "$T"
}

echo "# Pruebas negativas del verificador de presupuestos"
echo

echo "## Control positivo (los CSV entregados deben pasar)"
if python3 "$V" --dir "$SRC" >/dev/null 2>&1; then
  echo "  ok     CSV entregados pasan la verificacion"; ok=$((ok+1))
else
  echo "  FALLA  los CSV entregados NO pasan"; fallidas=$((fallidas+1))
fi
echo
echo "## Defectos inyectados (cada uno debe hacer fallar al verificador)"

caso "subtotal que no cuadra con cantidad x precio" \
  "sed -i '2s/,8734,/,9999,/' 01_ama_amoedo.csv 2>/dev/null; python3 - <<'P'
import csv
r=list(csv.reader(open('01_ama_amoedo.csv')));r[1][8]=str(int(r[1][8])+1)
csv.writer(open('01_ama_amoedo.csv','w',newline='')).writerows(r)
P"

caso "total por sobre el tope de la convocatoria" \
  "python3 - <<'P'
import csv
r=list(csv.reader(open('03_fondart_difusion.csv')));r[1][7]=str(30000000);r[1][8]=str(30000000)
csv.writer(open('03_fondart_difusion.csv','w',newline='')).writerows(r)
P"

caso "asignacion del responsable sobre el 40%" \
  "python3 - <<'P'
import csv
r=list(csv.reader(open('04_fondart_formativas.csv')));r[1][7]=str(8000000);r[1][8]=str(8000000)
csv.writer(open('04_fondart_formativas.csv','w',newline='')).writerows(r)
P"

caso "imprevistos sobre el 2%" \
  "python3 - <<'P'
import csv
r=list(csv.reader(open('02_fondart_creacion.csv')))
for f in r[1:]:
    if f[1]=='Imprevistos': f[7]='900000'; f[8]='900000'
csv.writer(open('02_fondart_creacion.csv','w',newline='')).writerows(r)
P"

caso "item Inversion en una linea que no lo contempla" \
  "python3 - <<'P'
import csv
r=list(csv.reader(open('04_fondart_formativas.csv')));r[2][1]='Inversion'
csv.writer(open('04_fondart_formativas.csv','w',newline='')).writerows(r)
P"

caso "categoria inexistente" \
  "python3 - <<'P'
import csv
r=list(csv.reader(open('03_fondart_difusion.csv')));r[2][1]='Marketing'
csv.writer(open('03_fondart_difusion.csv','w',newline='')).writerows(r)
P"

caso "id_coste duplicado dentro del mismo archivo" \
  "python3 - <<'P'
import csv
r=list(csv.reader(open('02_fondart_creacion.csv')));r[3][0]=r[2][0]
csv.writer(open('02_fondart_creacion.csv','w',newline='')).writerows(r)
P"

caso "mismo id_coste pagado por dos proyectos" \
  "python3 - <<'P'
import csv
r=list(csv.reader(open('03_fondart_difusion.csv')));r[2][0]='O-FOR-01'
csv.writer(open('03_fondart_difusion.csv','w',newline='')).writerows(r)
P"

caso "cantidad cero" \
  "python3 - <<'P'
import csv
r=list(csv.reader(open('01_ama_amoedo.csv')));r[1][5]='0';r[1][8]='0'
csv.writer(open('01_ama_amoedo.csv','w',newline='')).writerows(r)
P"

caso "cantidad no numerica" \
  "python3 - <<'P'
import csv
r=list(csv.reader(open('01_ama_amoedo.csv')));r[1][5]='seis'
csv.writer(open('01_ama_amoedo.csv','w',newline='')).writerows(r)
P"

caso "unidad vacia" \
  "python3 - <<'P'
import csv
r=list(csv.reader(open('02_fondart_creacion.csv')));r[1][6]=''
csv.writer(open('02_fondart_creacion.csv','w',newline='')).writerows(r)
P"

caso "origen_del_valor invalido" \
  "python3 - <<'P'
import csv
r=list(csv.reader(open('03_fondart_difusion.csv')));r[1][12]='me parece'
csv.writer(open('03_fondart_difusion.csv','w',newline='')).writerows(r)
P"

caso "columna faltante" \
  "python3 - <<'P'
import csv
r=[f[:-1] for f in csv.reader(open('04_fondart_formativas.csv'))]
csv.writer(open('04_fondart_formativas.csv','w',newline='')).writerows(r)
P"

caso "archivo de presupuesto ausente" "rm -f 01_ama_amoedo.csv"

echo
echo "control positivo: 1"
echo "defectos inyectados detectados: $inyectados    no detectados: $fallidas"
if [ "$fallidas" -ne 0 ]; then echo "RESULTADO: el verificador tiene huecos"; exit 1; fi
echo "RESULTADO: OK, control positivo mas $inyectados defectos inyectados"
