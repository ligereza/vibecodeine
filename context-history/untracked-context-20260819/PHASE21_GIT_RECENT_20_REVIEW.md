Identity: LUNA-23

# Phase 21 — revisión histórica de los últimos 20 commits

## Alcance y autorización

El usuario autorizó expresamente revisar los últimos 20 commits de las ramas
locales `mak` y `main` del repositorio `/home/mak/flujo`. Esta revisión es
histórica y no reemplaza la autoridad física de `/home/mak` y `/home/mak/WIN`.
No se usó Git para inventariar archivos, decidir duplicados ni promover
código; no se modificó ningún ref, rama, índice o working tree.

## Estado de las puntas

| Ref | Punta | Fecha | Sujeto |
|---|---|---|---|
| `main` | `032822b61f3d7cb84c7b52ae1ac6330b2a1f7fcb` | 2026-08-14 | `chore: remove obsolete agent routes` |
| `mak` | `814b74c1f5335170bf5ed1ee8c054565d6e3fc3e` | 2026-08-13 | `feat: reconcile local structure and mak research` |

`git rev-list --left-right --count main...mak` devolvió `18 1`: 18 commits
son alcanzables solo desde `main` y 1 solo desde `mak`. El merge-base es
`4b8453cbf17b25431e091a4a6fe3f09a819a0ffb`. La rama `mak` aparece detrás de
`main` en el grafo local, pero conserva una punta propia de reconciliación.

## Últimos 20 de `mak`

| Fecha | Commit | Sujeto |
|---|---|---|
| 2026-08-13 | `814b74c` | `feat: reconcile local structure and mak research` |
| 2026-08-12 | `4b8453c` | `docs: record MAK live mirror sync` |
| 2026-08-12 | `5bd5de1` | `docs: record recovered integration refs` |
| 2026-08-12 | `cd5ab70` | `feat: integrate recovered MAK and RD work` |
| 2026-08-12 | `eaa5b22` | `feat: add durable MAK conductor shadow circuit` |
| 2026-08-12 | `a878ee0` | `docs: record MAK runtime recovery` |
| 2026-08-11 | `306f320` | `record canonical branch synchronization` |
| 2026-08-11 | `9e9abb6` | `retire obsolete Gemini paths and slow fixture tests` |
| 2026-08-11 | `32688c8` | `make autonomy status resilient to gh timeout` |
| 2026-08-11 | `8ae5aa0` | `record Atlas release and MAK verification` |
| 2026-08-11 | `f7e268a` | `fix Linux resume concurrency test double` |
| 2026-08-11 | `ebc8b6a` | `consolidate Atlas decision gate and MAK supervision` |
| 2026-08-11 | `b4f5b2a` | `docs: refresh final branch state` |
| 2026-08-11 | `bd3810e` | `docs: record canonical branch promotion` |
| 2026-08-11 | `5f7e2e0` | `docs: record final branch validation` |
| 2026-08-11 | `d1977e0` | `test: remove personal path from privacy fixture` |
| 2026-08-11 | `5adaddc` | `docs: record canonical branch cleanup` |
| 2026-08-11 | `7172616` | `consolidate mak hub boundary and state guards` |
| 2026-08-11 | `160b94d` | `Synchronize mak CI and portable path test` |
| 2026-08-10 | `abe27c2` | `restore canonical ASCII vessel` |

## Últimos 20 de `main`

| Fecha | Commit | Sujeto |
|---|---|---|
| 2026-08-14 | `032822b` | `chore: remove obsolete agent routes` |
| 2026-08-14 | `a04093c` | `chore: remove legacy instruction docs` |
| 2026-08-14 | `857ede5` | `docs: remove handoff records` |
| 2026-08-14 | `8de3781` | `docs(hand): record main merge verification` |
| 2026-08-14 | `900f535` | `Reconcile MAK runtime on current main (#532)` |
| 2026-08-12 | `4861797` | `Merge branch 'mak'` |
| 2026-08-12 | `4b8453c` | `docs: record MAK live mirror sync` |
| 2026-08-12 | `5bd5de1` | `docs: record recovered integration refs` |
| 2026-08-12 | `bba8ba8` | `Merge branch 'mak'` |
| 2026-08-12 | `cd5ab70` | `feat: integrate recovered MAK and RD work` |
| 2026-08-12 | `eaa5b22` | `feat: add durable MAK conductor shadow circuit` |
| 2026-08-12 | `a878ee0` | `docs: record MAK runtime recovery` |
| 2026-08-11 | `f745755` | `merge canonical branch sync handoff into main` |
| 2026-08-11 | `306f320` | `record canonical branch synchronization` |
| 2026-08-11 | `93743ac` | `merge mak cleanup into main` |
| 2026-08-11 | `9e9abb6` | `retire obsolete Gemini paths and slow fixture tests` |
| 2026-08-11 | `04577d7` | `Merge pull request #525 from ligereza/mak` |
| 2026-08-11 | `32688c8` | `make autonomy status resilient to gh timeout` |
| 2026-08-11 | `a857e87` | `merge MAK release verification into main` |
| 2026-08-11 | `8ae5aa0` | `record Atlas release and MAK verification` |

## Qué cuenta este historial sobre la casa

1. **`mak` fue una rama de recuperación e integración.** Sus commits más
   voluminosos agregan o reconcilian MAK, RD, investigación, conocimiento
   unificado, `mak_conductor` y rutas de sincronización. El commit `814b74c`
   toca 58 archivos, agrega contratos de tres planos, migración/reconciliación
   de conocimiento, importación recuperada y `sync_mak_safe`.

2. **El conductor apareció como circuito de sombra, no como servicio probado.**
   `eaa5b22` agrega cola, idempotencia, workers, probes y unidades
   `mak-conductor-shadow`; esto explica por qué el inventario físico puede
   mostrar rutas válidas pero la auditoría semántica las dejó bloqueadas o
   diferidas por efectos, locks, servicios y rollback.

3. **`main` es una rama de promoción, merges y poda.** Después de incorporar
   MAK, `main` reconcilia el runtime (`900f535`) y luego elimina registros de
   handoff (`857ede5`), documentación de instrucciones heredadas (`a04093c`)
   y rutas obsoletas (`032822b`). Un commit de eliminación es evidencia de una
   decisión histórica, no prueba suficiente de que toda copia física haya sido
   eliminada o que una ruta restante sea basura.

4. **La actividad se concentra en las mismas zonas que ya resultaron de alto
   riesgo físico:** `cultura/mak_plataforma`, `cultura/mak_research`,
   `cultura/mak_conductor`, `tools/mak_ops`, `tests` y `context`. En los 20
   commits de `mak` hubo 118 toques bajo `cultura`, 99 bajo `docs` y 76 bajo
   `tests`; en `main`, 101 bajo `cultura`, 132 bajo `docs` y 50 bajo `tests`.
   La ruta más repetida fue `context/LAST_HANDOFF.md` (17 veces en `mak`, 12
   veces en `main`), por lo que los handoffs son memoria de proceso, no una
   señal de que exista una sola implementación funcional.

5. **El nombre de rama no identifica la máquina ni un departamento vigente.**
   La historia del documento `historia git.odt` ya advertía que la rama `mak`
   no equivale al equipo MAK. Esta revisión confirma además que `main` y `mak`
   tienen funciones históricas distintas y no son dos copias físicas que deban
   fusionarse automáticamente.

## Consecuencia para la continuación

- No hacer merge, rebase, reset, checkout, commit ni poda Git como resultado
  de esta revisión.
- Terminar primero la prueba contractual acotada de `discernment.py`, el único
  par que Phase 20 dejó como `ADOPTABLE_CANDIDATE`; no promover por el mero
  hecho de que `mak` o `main` lo tocaron.
- Mantener diferidos `trabajo`, `mineria_rd`, `revisor`, `capataz`, `junta`,
  `latido`, `material` y `backlog_codex` hasta disponer de fixtures,
  dependencias, límites de servicio/LLM/cola y rollback verificable.
- Mantener fuera de integración `repair_mak_sync.py`, `panel_directivo.py`,
  SSH, servicios, cron, workers, SVG/artwork y los 167 renglones no adoptables
  de la matriz semántica.
- El futuro sistema de ramas debe proponerse después de cerrar la casa física
  y debe representar ciclo de vida/responsabilidad verificados, no replicar
  los nombres históricos `mak`, `main`, `rd`, `iskvw` o `mak-svg`.

## Estado del working tree

La lectura fue solo de Git. El working tree ya tenía cambios del usuario y
artefactos locales del proceso (incluyendo `context/LAST_HANDOFF.md` y los
reportes de fases) sin commit. Se preservaron todos; no se limpiaron ni se
compararon como evidencia de integración.

## Comandos y códigos

- `git branch --list 'mak' 'main' --verbose --no-abbrev`: exit 0.
- `git log -20 ... mak` y `git log -20 ... main`: exit 0.
- `git rev-list --left-right --count main...mak`: exit 0; salida `18 1`.
- `git merge-base main mak`: exit 0; salida `4b8453c...`.
- `git log --graph --decorate --oneline --all --max-count=35`: exit 0.
- `git status --short --branch`: exit 0; cambios previos preservados.
- No se ejecutó red, SSH, servicio, worker, cron ni operación mutante de Git.

