# Artefactos locales fuera de Git — 2026-09-10

Este registro evita confundir un árbol Git limpio con la desaparición de
material local. Los grupos siguientes se conservan físicamente y se excluyen
del índice de `/home/mak` por su naturaleza, tamaño o frontera de repositorio.

| Ruta | Medición | Tratamiento | Motivo |
|---|---:|---|---|
| `/home/mak/.azure/` | ~328 KiB | conservar localmente | sesión, caché, logs y credenciales Azure; nunca versionar |
| `/home/mak/nomadicIT_research/` | ~684 MiB, 13.603 archivos | conservar localmente | corpus de investigación y salidas generadas; no tiene consumidor MAK ni repo propio |
| `/home/mak/data/matrix_surface_workflow_v1/` | ~28 KiB | conservar localmente | experimento autónomo de PyTorch/CUDA sin referencias desde el runtime MAK |
| `/home/mak/XIO-import-review/` | ~43 MiB | revisar como repo separado | checkout Git independiente, rama `codex/xio-import-review`, limpio y alineado con `origin` |
| `/home/mak/.claude/worktrees/revision-branches-huerfanas/_revision_vibecodeine_20260908/` | ~1,8 MiB, 123 archivos | conservar localmente | exportación de revisión generada dentro de un worktree; no es fuente del repositorio |

La exclusión vive en `.git/info/exclude`, no en `.gitignore`, porque es una
decisión de esta máquina y no una regla que deba propagarse a otros clones.
El script `cultura/mak_curatoria/curatoria_guardia_rd.sh`, en cambio, sí forma
parte del cambio funcional de MAK y no se excluye.
