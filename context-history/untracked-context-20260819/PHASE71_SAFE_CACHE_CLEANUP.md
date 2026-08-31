# Phase 71 — safe cache cleanup

## Target

The only deletion target in this phase is Python bytecode cache under active
MAK source roots:

- `/home/mak/flujo/src/flujo`
- `/home/mak/flujo/cultura/mak_plataforma`
- `/home/mak/flujo/cultura/mak_curatoria`
- `/home/mak/flujo/cultura/mak_research`
- `/home/mak/flujo/cultura/mak_codex`
- `/home/mak/flujo/cultura/mak_lenguaje`
- `/home/mak/flujo/cultura/mak_vigia`
- `/home/mak/flujo/cultura/mak_conductor`
- `/home/mak/post`

Only files named `*.pyc` inside `__pycache__` directories are eligible. These
are regenerated interpreter caches, not source, data, output, evidence or
historical WIN material. Virtual environments, root department state, tests,
RD assets and all other files are excluded.

## Gate

Before deletion: count exact targets and confirm no matching process is active.
After deletion: confirm zero targets in the listed roots, rerun AST/CLI health
checks and verify no runtime source changed. If a check fails, restore is not
needed for bytecode; Python regenerates it on demand, and the source remains
unchanged.

## Result

The exact target list contained 235 files. All 235 were removed from the
listed active roots; zero matching `*.pyc` files remain there. `flujo health`
exited 0, the post-cleanup AST scan covered 218 Python files with zero errors,
and no FLUJO/Blender/vigia/worker process remained. Source, data, evidence,
outputs, logs, documents, root department state and WIN were unchanged.

Final status: `CLEANED_REGENERABLE_CACHE`.
