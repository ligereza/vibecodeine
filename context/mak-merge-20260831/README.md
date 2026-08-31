# Expediente de fusión física MAK — 2026-08-31

La raíz física única es `/home/mak`; `/home/mak/flujo` es sólo un symlink de
compatibilidad. Esta corrida fusionó por hash las tres raíces encontradas y
preservó cada divergencia con su `source_id`. No se eliminó contenido.

- `plan.json`: plan inicial de las 23 raíces detectadas.
- `plan-post-redirect.json`: plan posterior a la redirección de `WIN`.
- `plan-final.json`: plan idempotente; reconoce 29 archivos ya archivados y no
  los vuelve a copiar.
- `actions.jsonl`: una línea por copia, verificación, variante, traslado o
  redirección; incluye la reubicación del expediente pesado fuera del checkout.
- `triangulation.json` / `triangulation.md`: nacimiento de inode, mtime, hash y
  primera/última aparición en Git; incluye los `.py` temporales sin ejecutar ni
  interpretar.
- `fused/projection3/MANIFEST.json`: manifiesto de la fusión de `active-flujo`,
  `win-flujo` y `runner-vibecodeine` (5.426 rutas iguales; 813 divergentes).
- `fused/root-materialization.json`: registro de cómo esas rutas quedaron
  materializadas una sola vez bajo `/home/mak`; una colisión preexistente se
  dejó intacta y quedó anotada, no sobrescrita.

El material preservado está en `/home/mak/_archive/merge-20260831/`:
`sources/` contiene archivos únicos y `variants/` contiene divergencias. El
checkout histórico completo de Windows vive en `checkouts/win-flujo-full/` y
`/home/mak/WIN/flujo` apunta a él. El checkout del runner queda en su ruta
original como symlink hacia `checkouts/runner-vibecodeine-full/`; se movió cuando
no había `Runner.Worker` activo y el listener siguió sin reiniciarse.

La suite local previa a la re-raíz pasó `4208 passed, 5 skipped`; después de la
re-raíz se corrigieron los escáneres para no recorrer el home completo y los
checks de higiene/auditoría del árbol único pasan.
