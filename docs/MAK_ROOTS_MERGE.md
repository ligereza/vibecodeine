# MAK: raíces canónicas y política de merge

Medición estructural: 2026-08-31. Este documento evita que una copia histórica,
de runner o de caché sea confundida con el árbol de autoría.

## Fuente canónica

`/home/mak/flujo` es la única raíz de autoría y de verificación local. Su rama
actual es `main`, con base `ab9afa13`; el checkpoint de este estado debe quedar
en Git antes de que otro agente continúe.

## Copias no canónicas

- `/home/mak/WIN/flujo`: copia histórica de Windows; rama
  `codex/three-plane-consolidation`, base `f588ecf8`. Es evidencia, no fuente de
  merge ni destino de borrado.
- `/home/mak/actions-runner/_work/vibecodeine/vibecodeine`: checkout efímero del
  runner, base `23d6152`. No es un árbol de trabajo del operador.
- `/home/mak/state/**`, `/home/mak/_archive/**`, papelera y
  `/home/mak/.cache/rclone/**`: snapshots, retiros o cachés. No se fusionan
  automáticamente.
- `projects/flujo`, `proyectos/flujo` y `src/flujo` dentro de copias son
  subárboles o artefactos de esas copias, no nuevas raíces canónicas.

## Regla

Todo cambio nuevo entra en `/home/mak/flujo`. Una contribución de otra raíz sólo
se incorpora después de identificarla como fuente, comparar su hash/commit y
registrar el write-set. Nunca se borra una copia histórica para resolver la
ambigüedad.

## Instrumentos relevantes

La cronología de tests se mide con `tools/medir_tests.py`; el solape estructural
con `tools/medir_test_overlap.py`; la política bilingüe de comentarios y
docstrings con `tools/idioma.py` y `tests/test_idioma_ratchet.py`. Los scripts
efímeros de jobs de Claude (`clasificar_tests.py`, `solape.py`, etc.) son
evidencia de trabajo, no código canónico hasta ser revisados y portados.

`WIN` y `curatoria_inbox` no forman parte de la colección de tests local.
