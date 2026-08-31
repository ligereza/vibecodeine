# MAK: raíces canónicas y política de merge

Medición estructural: 2026-08-31. Este documento evita que una copia histórica,
de runner o de caché sea confundida con el árbol de autoría.

## Fuente canónica

`/home/mak` es ahora la única raíz física de autoría y verificación local. El
antiguo `/home/mak/flujo` se conserva sólo como symlink de compatibilidad hacia
`.`; no hay un segundo checkout activo. El Git de la raíz sigue en `main` y el
checkpoint anterior era `ab9afa13`.

## Copias no canónicas y archivo de fusión

- `/home/mak/WIN/flujo`: symlink a
  `/home/mak/_archive/merge-20260831/fused/origins/win-flujo`, rama histórica
  `codex/three-plane-consolidation`, base `f588ecf8`.
- `/home/mak/actions-runner/_work/vibecodeine/vibecodeine`: symlink a
  `/home/mak/_archive/merge-20260831/fused/origins/runner-vibecodeine`, checkout
  efímero con base `23d6152`.
- El checkout activo que estaba en `/home/mak/flujo` fue trasladado completo a
  `/home/mak/_archive/merge-20260831/fused/origins/active-flujo`; no se borró.
- `/home/mak/state/**`, `/home/mak/_archive/**`, papelera y
  `/home/mak/.cache/rclone/**`: snapshots, retiros o cachés. Se incorporan al
  expediente de fusión por hash y procedencia, nunca como código activo.
- `projects/flujo`, `proyectos/flujo` y `src/flujo` dentro de copias son
  subárboles o artefactos de esas copias, no nuevas raíces canónicas.

## Regla

Todo cambio nuevo entra en `/home/mak` (el alias `/home/mak/flujo` resuelve ahí).
La fusión lossless de las tres raíces está materializada en el propio árbol:
`/home/mak/_archive/merge-20260831/fused/projection3/MANIFEST.json` registra
5.426 rutas iguales, 813 rutas divergentes y 2.366 variantes. El expediente
completo conserva los tres orígenes bajo `fused/origins/`; la proyección pone
una sola ruta activa por entrada, sin sobrescribir archivos preexistentes, y el
informe de materialización está en `fused/root-materialization.json`.
Cada operación tiene hash y verificación en
`context/mak-merge-20260831/actions.jsonl`. No se borró ninguna fuente.

La raíz histórica `/home/mak/WIN/flujo` y el checkout del runner fueron
reubicados como orígenes de la fusión mientras el runner estaba idle (sólo
`Runner.Listener` activo) y conservan sus symlinks originales. Los cachés rclone,
la papelera y
los snapshots bajo `state/` conservan su ubicación administrada y quedan
registrados, no reinterpretados como autoría.

La selección no usa sólo el nombre: `mak_triangulate_roots.py` cruza nacimiento
del inode, mtime, hash, primer/último commit del archivo y metadatos del checkout.
Su salida durable es `context/mak-merge-20260831/triangulation.{json,md}`.

"Una sola raíz" no significa que se haya declarado ganador una variante. Las
rutas con bytes divergentes requieren un baseline operativo para que `/home/mak`
sea ejecutable; los bytes de las demás fuentes siguen intactos en
`fused/origins/` y cada relación está en `projection3/MANIFEST.json`. Esa
decisión de ejecución es reversible y está registrada; no es una afirmación de
que se haya resuelto semánticamente cada divergencia.

El caso `airdrop` queda etiquetado como antecesor histórico, no como descarte:
`WIN/flujo/src/flujo/airdrop.py` aparece añadido el 2026-06-28 y usado hasta el
2026-07-31; el commit `a6fe4662` lo retiró explícitamente el 2026-08-28. Sus
variantes y tests se conservan en el archivo de fusión para una eventual
reintegración deliberada. Los 48 `.py` de temporales de Claude se registran sólo
por metadatos/hash y no entran al importador activo.

## Instrumentos relevantes

La cronología de tests se mide con `tools/medir_tests.py`; el solape estructural
con `tools/medir_test_overlap.py`; la política bilingüe de comentarios y
docstrings con `tools/idioma.py` y `tests/test_idioma_ratchet.py`. Los scripts
efímeros de jobs de Claude (`clasificar_tests.py`, `solape.py`, etc.) son
evidencia de trabajo, no código canónico hasta ser revisados y portados.

`WIN` y `curatoria_inbox` no forman parte de la colección de tests local.
