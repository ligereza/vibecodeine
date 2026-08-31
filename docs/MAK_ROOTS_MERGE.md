# MAK: raíces canónicas y política de merge

Medición estructural: 2026-08-31. Este documento evita que una copia histórica,
de runner o de caché sea confundida con el árbol de autoría.

## Fuente canónica

`/home/mak/flujo` es la única raíz de autoría y de verificación local. Su rama
actual es `main`, con base `ab9afa13`; el checkpoint de este estado debe quedar
en Git antes de que otro agente continúe.

## Copias no canónicas y archivo de fusión

- `/home/mak/WIN/flujo`: copia histórica de Windows; rama
  `codex/three-plane-consolidation`, base `f588ecf8`. Es evidencia, no fuente de
  merge ni destino de borrado.
- `/home/mak/actions-runner/_work/vibecodeine/vibecodeine`: checkout efímero del
  runner, base `23d6152`. No es un árbol de trabajo del operador.
- `/home/mak/state/**`, `/home/mak/_archive/**`, papelera y
  `/home/mak/.cache/rclone/**`: snapshots, retiros o cachés. Se incorporan al
  expediente de fusión por hash y procedencia, nunca como código activo.
- `projects/flujo`, `proyectos/flujo` y `src/flujo` dentro de copias son
  subárboles o artefactos de esas copias, no nuevas raíces canónicas.

## Regla

Todo cambio nuevo entra en `/home/mak/flujo`. La corrida física
`mak-merge-20260831` dejó las copias no activas en
`/home/mak/_archive/merge-20260831/sources/` y las divergencias en
`/home/mak/_archive/merge-20260831/variants/`; cada operación tiene hash y verificación en
`context/mak-merge-20260831/actions.jsonl`. No se borró ninguna fuente.

La raíz histórica `/home/mak/WIN/flujo` ya fue retirada de su ubicación original
con un symlink transparente hacia
`/home/mak/_archive/merge-20260831/checkouts/win-flujo-full`; el checkout del runner no se
mueve mientras `Runner.Listener` esté activo. Los cachés rclone, la papelera y
los snapshots bajo `state/` conservan su ubicación administrada y quedan
registrados, no reinterpretados como autoría.

La selección no usa sólo el nombre: `mak_triangulate_roots.py` cruza nacimiento
del inode, mtime, hash, primer/último commit del archivo y metadatos del checkout.
Su salida durable es `context/mak-merge-20260831/triangulation.{json,md}`.

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
