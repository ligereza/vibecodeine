# Expediente de fusión física MAK — 2026-08-31

La raíz física única es `/home/mak`; `/home/mak/flujo` es un adaptador de
compatibilidad no recursivo. Esta corrida fusionó por hash las tres raíces
encontradas y preservó cada divergencia con su `source_id`. Las capas
redundantes de proyección y las copias exactas se purgaron después; los
orígenes con contenido divergente siguen intactos.

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
  `win-flujo` y `runner-vibecodeine` (5.426 rutas iguales; 813 divergentes;
  2.366 variantes conservadas).
- `fused/root-materialization.json`: registro de cómo esas rutas quedaron
  materializadas una sola vez bajo `/home/mak`; una colisión preexistente se
  dejó intacta y quedó anotada, no sobrescrita. Para que exista un único árbol
  ejecutable, las rutas divergentes usan el baseline que ya estaba activo y
  sus bytes alternativos quedan íntegros en `fused/origins/` y en el manifiesto;
  no se afirma que esas 813 diferencias sean una fusión semántica automática.
  Dos entradas históricas que no pueden ser entrypoints activos se trasladaron
  a `resolved-conflicts/` y quedaron registradas como tales.
  En las 813 rutas divergentes, 805 conservan el baseline activo y sólo 8
  requieren el fallback operativo de `win-flujo`; ninguna variante se descartó.

El material preservado está en `/home/mak/_archive/merge-20260831/fused/`:
`origins/` contiene los tres checkouts completos, `projection3/MANIFEST.json`
es el manifiesto lossless y `resolved-conflicts/` los archivos que no deben
ser entrypoints activos. La subcarpeta de variantes era una segunda copia de
`origins/` y fue eliminada tras verificar sus hashes. `/home/mak/WIN/flujo` y el checkout del runner son symlinks a sus
orígenes fusionados; se movieron cuando no había `Runner.Worker` activo y el
listener siguió sin reiniciarse.

La suite local previa a la re-raíz pasó `4208 passed, 5 skipped`; después de la
re-raíz se corrigieron los escáneres para no recorrer el home completo y los
checks de higiene/auditoría del árbol único pasan.
