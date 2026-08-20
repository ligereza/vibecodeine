# Operational Handoff

## Current objective

Mantener el repo web y el runtime local en un estado coherente y verificable.
El cierre de limpieza/publicación de esta tanda ya fue ejecutado; la siguiente
acción independiente es el simulate acotado del Research job 4.

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
- La interfaz temporal del Research local ya estaba activa antes de esta
  tanda; no fue iniciada, detenida ni modificada aquí.

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
  total fijo de tests ni se recicla el conteo antiguo del learner.
- Se declaró en `web/package.json`, `web/package-lock.json` y
  `web/README.md` el requisito real `Node >=20.19.0`; con el Node 24.19.0
  disponible en MAK los builds reproducibles pasan.
- Los cambios de código y contratos fueron publicados en `main`; la paridad
  del último commit se verifica por comando, no por un hash copiado en esta
  memoria.

## Open integration items

| Item | Path | Status | Proof required |
| --- | --- | --- | --- |
| Python learning layer | `src/flujo/knowledge/learning_policy.py` | verified, published | full pytest exit 0; py_compile exit 0; diff check exit 0 |
| Web source | `web/` | verified, published | Node 24.19.0: `npm ci`, audit 0 vulnerabilities, typecheck and all three builds exit 0 |
| Documentation contract | `CAPACIDADES.md`, `docs/MAK_CURRENT_STATE.md`, this file | verified, published | docs hygiene included in full pytest exit 0 |
| Research learning | `/home/mak/research/jobs/4/` | captured/interpreted; simulation pending | only simulate against a declared local consumer; no candidate install |
| Publication | `main` -> `origin/main` | verified | `git rev-parse HEAD` equals `git ls-remote origin refs/heads/main` |

## Tool and dependency verification matrix

| Surface | Command | Current result |
| --- | --- | --- |
| Python suite | `./.venv/bin/python -m pytest -q` | exit 0; warnings only from existing Pillow deprecation |
| Learning policy | `./.venv/bin/python tools/project_learning.py --db data/mak_knowledge.db` | exit 0; abstain; 5 eligible; no independent holdout |
| Python syntax | `./.venv/bin/python -m py_compile ...` | exit 0 |
| Diff hygiene | `git diff --check` | exit 0 before commit |
| Python dependencies | `./.venv/bin/python -m pip check` | exit 0; no broken requirements |
| Web typecheck/build | commands in Open integration items | exit 0 with Node 24.19.0 |
| Hub smoke | `./.venv/bin/python scripts/hub_smoke.py --port 0 --timeout 20` | exit 0; temporary port 48545; no persistent hub |
| Remote parity | `git rev-parse HEAD` vs `git ls-remote origin refs/heads/main` | equal when the commands return the same value |

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

For Research job 4, locate a declared MAK consumer for a bounded L-system
simulation. If none exists, record `simulate` as unavailable without cloning
or installing candidate repositories. Do not promote the five same-project
episodes to a learned policy.

## Last verified

2026-08-19 America/Santiago — cleanup/publication verified; local and remote
HEAD equal according to the commands in the matrix.
