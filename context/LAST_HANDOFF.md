# Operational Handoff

## Current objective

Dejar el repo web y el runtime local en un estado coherente, verificable y
publicable: corregir contradicciones documentales o de código, ejecutar los
gates Python y web, y hacer commit/push solo del estado que pase.

## Physical authority and migration status

- La autoridad física es `/home/mak/*`; `/home/mak/flujo` es el baseline de
  autoría y `/home/mak/WIN` es evidencia histórica de Windows.
- No se copia ni se borra el árbol histórico. Los datos locales ignorados y los
  productos generados se preservan fuera del commit salvo que una regla del
  repo los declare artefactos versionables.
- Git tiene una sola rama local (`main`) y una sola rama remota operativa
  (`origin/main`). El README y su SVG protegido no se modifican.
- En la inspección actual se observaron `cron`, el runner local de GitHub
  Actions y Open WebUI ya instalados; esta tarea no inició ninguno ni dejó un
  proceso de render o hub corriendo.

## Completed work with command and result

- Se agregó `src/flujo/knowledge/learning_policy.py`: learner categórico
  auditable, split por `project_id`, abstención ante evidencia insuficiente y
  registro de política solo como candidata.
- Se agregó `tools/project_learning.py` y
  `tests/test_learning_policy.py`. El adaptador
  `mak-verified-result-v1` exige proyecto existente, evidencia, validador y
  checks pasados; es idempotente y falla cerrado.
- `src/flujo/knowledge/project_api.py` expone `learning.policy` en modo
  read-only. `CAPACIDADES.md` y `docs/MAK_CURRENT_STATE.md` declaran el
  contrato.
- Research job 4 sobre `JARDINES_INTERPRETATIVOS.md` capturó cuatro fuentes,
  extrajo claims, relaciones, contexto e interpretación y dejó el siguiente
  paso en `simulate`; no se instalaron repos candidatos.
- La base local ignorada `data/mak_knowledge.db` contiene cinco episodios
  verificables del mismo proyecto. La política medida es `abstain` con razón
  `no_independent_holdout`, `eligible_examples=5`, `train_count=5` y
  `holdout_count=0`. No se promovió ninguna regla.
- La contradicción detectada en el handoff fue eliminada: ya no se escribe un
  total fijo de tests ni se afirma `eligible_examples=0`.

## Open integration items

| Item | Path | Status | Proof required |
| --- | --- | --- | --- |
| Python learning layer | `src/flujo/knowledge/learning_policy.py` | changed, focused tests pending rerun | pytest, compile, diff check |
| Web source | `web/` | unchanged in this pass | `npm ci`, `npm run typecheck`, `npm run build:context`, `npm run build:plano`, `npm run build:rd` |
| Documentation contract | `CAPACIDADES.md`, `docs/MAK_CURRENT_STATE.md`, this file | changed | docs hygiene and full pytest |
| Research learning | `/home/mak/research/jobs/4/` | captured/interpreted; simulation pending | only simulate against a declared local consumer; no candidate install |
| Publication | `main` -> `origin/main` | not executed yet | commit after all gates, then push and verify remote |

## Tool and dependency verification matrix

| Surface | Command | Current result |
| --- | --- | --- |
| Python suite | `./.venv/bin/python -m pytest -q` | last run exposed one stale handoff count; rerun after this correction |
| Learning policy | `./.venv/bin/python tools/project_learning.py --db data/mak_knowledge.db` | exit 0; abstain; 5 eligible; no independent holdout |
| Python syntax | `./.venv/bin/python -m py_compile ...` | passed for the new module, wrapper and test before this correction |
| Diff hygiene | `git diff --check` | passed before this correction |
| Python dependencies | `./.venv/bin/python -m pip check` | must be rerun before publish |
| Web typecheck/build | commands in Open integration items | must be rerun before publish |
| Processes | `pgrep` guarded check | no Blender, render, Vite, hub or Flujo process from this task |

## Conflicts and risks

- `abstain` is intentional. Five episodes from one project are not an
  independent learning evaluation; promoting them would be data leakage.
- `data/mak_knowledge.db` and generated research SQLite/report files are local
  operational state and are not Git inventory. Their current state is noted,
  not copied into the web repo.
- Historical phase documents and recovered sessions remain evidence. They are
  not the current handoff and must not override this file.
- A green local check does not prove external GitHub Actions or provider
  credentials. The push must be followed by remote status inspection.

## Next concrete action

Run the full Python and web gates in the foreground. If all pass, stage only
the intended source/docs/test files, commit the coherent change, push `main`,
and verify `HEAD` equals `origin/main`. If a gate fails, fix that failure
before publishing and record the exact command and result here.

## Last verified

2026-08-19 America/Santiago — handoff compacted after stale-count failure;
full gates and publication still pending.
