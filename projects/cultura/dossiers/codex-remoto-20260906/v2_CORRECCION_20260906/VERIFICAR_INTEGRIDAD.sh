#!/usr/bin/env bash
# Comprueba que la v1 congelada no se ha tocado y que la v2 coincide con su manifiesto.
# Ejecutar desde cualquier directorio.
set -u
BASE="/home/mak/CODEX REMOTO"
echo "# Verificacion de integridad  --  $(date -Is)"
echo
echo "## v1 congelada (no debe cambiar nunca)"
cd "$BASE/v1_ENTREGA_20260906_AUDITADA" || exit 1
malos=$(sha256sum -c ../SELLO_v1.sha256 2>/dev/null | grep -vc "coincide\|: OK$")
total=$(wc -l < ../SELLO_v1.sha256)
echo "   $((total-malos)) de $total archivos coinciden con SELLO_v1.sha256"
[ "$malos" -ne 0 ] && { echo "   ALERTA: la v1 fue modificada"; exit 1; }
echo
echo "## v2 vigente"
cd "$BASE/v2_CORRECCION_20260906" || exit 1
malos2=$(sha256sum -c MANIFIESTO_v2.sha256 2>/dev/null | grep -vc "coincide\|: OK$")
total2=$(wc -l < MANIFIESTO_v2.sha256)
echo "   $((total2-malos2)) de $total2 archivos coinciden con MANIFIESTO_v2.sha256"
[ "$malos2" -ne 0 ] && echo "   AVISO: $malos2 archivo(s) cambiaron desde el manifiesto; regenerar si el cambio fue intencional"
echo
echo "## Suites"
for c in "python3 verificador/verificar_presupuestos.py" \
         "bash verificador/pruebas_negativas.sh" \
         "python3 verificador/comprobacion_cruzada.py" \
         "python3 verificador/revision_ids_y_gastos.py" \
         "python3 verificador/generar_indice_anexos.py"; do
  $c >/dev/null 2>&1
  printf "   %-44s exit=%s\n" "${c##* }" "$?"
done
echo
echo "## Estado de la ficha del titular"
python3 verificador/leer_ficha_titular.py | grep -E "^campos completados|^filas de portfolio" | sed 's/^/   /'
