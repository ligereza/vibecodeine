# Expediente de fusión física MAK — 2026-08-31

La raíz activa sigue siendo `/home/mak/flujo`. Esta corrida fusionó por hash los
archivos compatibles de los checkouts encontrados y preservó cada divergencia
con su `source_id`. No se eliminó contenido.

- `plan.json`: plan inicial de las 23 raíces detectadas.
- `plan-post-redirect.json`: plan posterior a la redirección de `WIN`.
- `actions.jsonl`: una línea por copia, verificación, variante, traslado o
  redirección; incluye la reubicación del expediente pesado fuera del checkout.
- `triangulation.json` / `triangulation.md`: nacimiento de inode, mtime, hash y
  primera/última aparición en Git; incluye los `.py` temporales sin ejecutar ni
  interpretar.

El material preservado está en `/home/mak/_archive/merge-20260831/`:
`sources/` contiene archivos únicos y `variants/` contiene divergencias. El
checkout histórico completo de Windows vive en `checkouts/win-flujo-full/` y
`/home/mak/WIN/flujo` apunta a él. El checkout del runner queda en su ruta
original mientras `Runner.Listener` esté activo.

La suite local posterior a la limpieza del árbol activo: `4208 passed, 5
skipped`.
