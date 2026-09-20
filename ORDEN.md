# ORDEN

state: READY
cycle: supervisor-002
executor: Codex local
branch: SUPERVISOR
code_base_expected: 6ebea3efb5ab8f7c87e0cc97ce415ad426875559

## Objetivo único

Hacer que `data/tool_registry.json` represente todos los `tools/*.py`
actuales sin inventar que una herramienta está viva cuando su ciclo de vida aún
no fue demostrado.

## Preflight ya resuelto por el supervisor

Medición sobre HEAD `6ebea3efb5ab8f7c87e0cc97ce415ad426875559`:

- `tools/*.py` relevantes: 143.
- entradas actuales del registry: 101.
- herramientas fantasma: 0.
- faltantes: 42.
- `tests/test_higiene_repo.py::test_tools_en_registro` exige presencia de
  todas las herramientas actuales.
- `test_registro_sin_herramientas_fantasma` exige que no haya entradas de
  archivos eliminados.
- El estado `VIVO` activa además los gates de compilación/`--help`; por eso
  no debe usarse como valor por defecto.
- `tools/repo_audit.py::NO_REFERENCE_CLASSIFICATIONS` ya declara explícitamente
  estas 15 faltantes como `manual_only`:

  - `context_pack.py`
  - `render_archaeology_deliverables.py`
  - `token_budget.py`
  - `verify_all.py`
  - `arica01_portfolio.py`
  - `certified_query.py`
  - `classification_review.py`
  - `compile_portfolio.py`
  - `compile_ssd_order_foundation.py`
  - `gen_rd_standalone.py`
  - `import_project_reconstruction.py`
  - `run_vision_feedback.py`
  - `show_asset_usage.py`
  - `tennis_mcp_ingest.py`
  - `venue_screen_setup.py`

Las 27 faltantes restantes no tienen una clasificación explícita equivalente;
regístralas como `REVISAR`, que expresa incertidumbre sin afirmar vigencia:

  - `adapt_practice_receipts.py`
  - `archive_observer.py`
  - `azure_ml_learning_dataset.py`
  - `azure_ml_mlflow_compat.py`
  - `build_evidence_return.py`
  - `build_possibility_field.py`
  - `compile_application_research_package.py`
  - `compile_autonomy_plan.py`
  - `compile_cross_archive_relations.py`
  - `compile_cross_archive_research_frontier.py`
  - `compile_practice_evidence_state.py`
  - `compile_product_episode.py`
  - `contexto_repo.py`
  - `deep_learning_gate.py`
  - `evaluate_artistic_program_hypotheses.py`
  - `evaluate_opportunity_fit.py`
  - `evaluate_product_learning.py`
  - `materialize_pilot_run.py`
  - `math_kernel.py`
  - `project_reconstruction.py`
  - `project_review.py`
  - `render_output_edges.py`
  - `research_simulation.py`
  - `run_archive_toolchain.py`
  - `source_learning_bridge.py`
  - `tennis_shot_events.py`
  - `venue.py`

## Guard de concurrencia

`6ebea3efb5ab8f7c87e0cc97ce415ad426875559` es el último HEAD de **producto**
consumido por el supervisor. Después de él el supervisor puede haber creado
commits que sólo cambian `SUPERVISOR.md` y/o `ORDEN.md`; esos commits de
control son esperados y no invalidan la orden.

1. Haz `git fetch origin`.
2. Inspecciona los paths cambiados entre
   `6ebea3efb5ab8f7c87e0cc97ce415ad426875559..origin/SUPERVISOR`.
3. Si todos los cambios posteriores están limitados a `SUPERVISOR.md` y
   `ORDEN.md`, continúa.
4. Si aparece cualquier otro path, devuelve `BLOCKED` con firma
   `stale_code_base` y lista sólo esos paths; no apliques esta orden sobre
   producto que cambió fuera del ciclo.

## Write-set

Sólo:

- `data/tool_registry.json`
- `ORDEN.md` para devolver el resultado.

No modifiques `repo_audit.py`, herramientas ni tests en este ciclo.

## Trabajo

1. Añade exactamente las 42 entradas faltantes.
2. Usa `manual-only` como valor para las 15 que el preflight lista como
   `manual_only` en `repo_audit.py` (mantén el estilo de valores existente
   del registry).
3. Usa `REVISAR` para las otras 27.
4. No reclasifiques entradas que ya estaban presentes.
5. Conserva JSON válido y el schema actual.

## Pruebas

Ejecuta:

- `python -m pytest -q tests/test_higiene_repo.py -k "tools_en_registro or registro_sin_herramientas_fantasma"`
- `python -m pytest -q --collect-only`

No ejecutes aún el gate completo de herramientas `VIVO`; ya existen dos
fallos conocidos de `--help` que corresponden a otra tarea.

## Si aparecen errores

- Corrige sólo errores causados por esta edición del registry y que entren en el
  write-set.
- Fallos externos/preexistentes no amplían esta tarea.
- Si aparecen muchos, agrupa por causa raíz/firma, máximo cinco grupos.
- `DONE` si el registry queda estructuralmente alineado aunque exista un fallo
  externo conocido.
- `BLOCKED` sólo si no puedes completar este objetivo dentro del write-set.

## Criterio de éxito

- las 143 herramientas actuales están representadas;
- no hay entradas fantasma;
- ninguna de las 27 inciertas fue promovida a `VIVO`;
- los dos tests estructurales del registry pasan;
- la colección de pytest sigue funcionando.

## Entrega

No crees archivos auxiliares.

Reemplaza completamente este mismo `ORDEN.md` por:

```text
# ORDEN
state: DONE | BLOCKED
cycle: supervisor-002
objective_met: true | false

summary: <máximo 5 líneas>
changed:
  - <archivos tocados>
tests:
  - <comando>: <resultado breve>
failure_groups:
  - signature: <causa raíz/firma>
    count: <n>
    relation: task_local | external | unknown
    example: <máximo una línea>
next_blocker: <sólo si objective_met=false; de lo contrario none>
```

Omite `failure_groups` si no hay fallos. No pegues logs largos ni historia.
