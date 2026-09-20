# ERRORES — revisión de `SUPERVISOR`

Estado: **BLOQUEA LA INTEGRACIÓN**.

Este documento registra los conflictos comprobados al revisar la rama remota
`SUPERVISOR` contra `main`. Su propósito es entregar contexto al supervisor
para la siguiente instrucción. No autoriza a restaurar archivos históricos en
bloque: cada restauración debe demostrar owner, consumer y capacidad actual.

## Base revisada

- Repositorio: `ligereza/vibecodeine`
- Rama: `SUPERVISOR`
- HEAD revisado: `02cf51bb`
- Base comparada: `main` en `974bfccd`
- Diferencia: 93 commits adelante; 993 archivos afectados, 950 eliminados,
  40 modificados y 3 agregados.

## Fallos bloqueantes reproducibles

### 1. La suite no puede recolectarse

`SUPERVISOR` elimina `tools/consolidate_static_duplicates.py`, pero conserva
este import activo:

```python
# tests/test_scan_roots_skip_cloud_mounts.py
from tools.consolidate_static_duplicates import PROTECTED_TOPS
```

Reproducción:

```bash
python -m pytest -q
```

Resultado:

```text
ModuleNotFoundError: No module named 'tools.consolidate_static_duplicates'
```

Esto impide que pytest recolecte la suite completa. Resolver demostrando si la
capacidad fue retirada: restaurar el módulo sólo si existe consumer vigente, o
retirar/reemplazar el test si el contrato que protege ya no existe.

### 2. Auditoría de herramientas inconsistente

```bash
python tools/repo_audit.py --format text
```

Falla con:

```text
RuntimeError: stale no-reference classifications: mak_status
```

La clasificación de `tools/mak_status.py` ya no coincide con la medición real
de consumidores. No marcar la auditoría como verde mediante una excepción
manual: reconciliar la clasificación con evidencia.

### 3. Registry de herramientas roto en ambas direcciones

`tests/test_higiene_repo.py` detecta que el registry conserva una herramienta
fantasma:

```text
consolidate_static_duplicates.py
```

Y que `data/tool_registry.json` no contiene estas herramientas que sí existen:

```text
adapt_practice_receipts.py
archive_observer.py
arica01_portfolio.py
azure_ml_learning_dataset.py
azure_ml_mlflow_compat.py
build_evidence_return.py
build_possibility_field.py
certified_query.py
classification_review.py
compile_application_research_package.py
compile_autonomy_plan.py
compile_cross_archive_relations.py
compile_cross_archive_research_frontier.py
compile_portfolio.py
compile_practice_evidence_state.py
compile_product_episode.py
compile_ssd_order_foundation.py
context_pack.py
contexto_repo.py
deep_learning_gate.py
evaluate_artistic_program_hypotheses.py
evaluate_opportunity_fit.py
evaluate_product_learning.py
gen_rd_standalone.py
import_project_reconstruction.py
materialize_pilot_run.py
math_kernel.py
project_reconstruction.py
project_review.py
render_archaeology_deliverables.py
render_output_edges.py
research_simulation.py
run_archive_toolchain.py
run_vision_feedback.py
show_asset_usage.py
source_learning_bridge.py
tennis_mcp_ingest.py
tennis_shot_events.py
token_budget.py
venue.py
venue_screen_setup.py
verify_all.py
```

El registry debe representar el árbol actual antes de declarar cerrada la
limpieza.

### 4. Mapa de lanes de tests desactualizado

`tools/test_lane_map.py`, `context/test_lane_map.json` y fixtures siguen
enumerando tests eliminados, entre ellos:

```text
tests/test_airdrop.py
tests/test_airdrop_checkpoint.py
tests/test_airdrop_signing.py
tests/test_reception.py
tests/test_run_airdrop_checks.py
tests/test_validate_airdrop.py
```

Además, `tests/test_test_taxonomy.py` mide 24 tests sin lane, por encima del
techo declarado de 19. El listado medido es:

```text
tests/test_branch_contract.py
tests/test_capataz_extraer_json.py
tests/test_cuotas_aplanar_llmcalls.py
tests/test_diagnostico_dirs_generadas.py
tests/test_forense.py
tests/test_forense_estructura.py
tests/test_gen_archivo_iskvw_riqueza.py
tests/test_hub_gtm_map_projection.py
tests/test_mak_azure_search.py
tests/test_motor_semantico_distancia.py
tests/test_operation_receipt.py
tests/test_portfolio_review_context.py
tests/test_rd_event_links.py
tests/test_research_compact_search_query.py
tests/test_review_queue_surface.py
tests/test_triangular_ficha_contenido.py
tests/test_verify_portfolio_surface_parity.py
tests/test_vigia_titulo_util.py
tests/test_vj_event_context.py
tests/test_xio_event_ingest.py
tests/test_xio_event_vertical.py
tests/test_xio_sample_read.py
tests/test_xio_signal_ingest.py
tests/test_zone_overlay.py
```

Regenerar el contrato desde el árbol actual y revisar los tests nuevos antes de
reducir el techo.

### 5. Herramientas declaradas activas que lanzan traceback

El guard de higiene ejecuta `--help` de las herramientas declaradas `VIVO` y
encuentra:

```text
compile_vigia_capture_plans.py: ModuleNotFoundError: No module named 'tools.source_pipeline'
reportar_calibracion_deepseek.py: sqlite3.OperationalError: no such table: learning_evaluations
```

Cada herramienta debe manejar la ausencia de dependencia/estado y explicar el
resultado, o cambiar su clasificación si ya no es operativa.

## Hallazgos no bloqueantes, pero pendientes

### 6. Superficies declaradas sin fuente local

`tools/capabilities.py --no-live --check-branch --format json` informa:

```text
searxng: source_missing
mak_research_queue: source_missing
```

Pueden ser superficies opcionales, pero su estado debe quedar explícito y no
producir una falsa lectura de salud.

### 7. Referencias a autoridades retiradas

El propio `SUPERVISOR.md` identifica trabajo pendiente en:

- `src/flujo/knowledge/system_status.py`, que aún modela `AGENTS.md`;
- `src/flujo/diagnostics.py`, que conserva fallbacks a `AGENTS.md` y
  `context/LAST_HANDOFF.md`;
- skills activas que todavía exigen `context/LAST_HANDOFF.md`;
- índices y fixtures que conservan rutas de tests eliminados.

Clasificar cada referencia como consumer activo, documentación histórica o
referencia colgante. No borrar por coincidencia textual sin distinguir esas
categorías.

### 8. Perfil heredado de `main`

`branch_profile.json` conserva `"branch": "main"`. El contrato de ramas lo
interpreta como metadata heredada para una rama auxiliar, por lo que no es por
sí solo una regresión. Debe mantenerse sólo si esa herencia es intencional y
queda explicada en el protocolo de la rama.

## Qué sí fue verificado

- `python -m compileall -q src scripts tests`: pasa.
- `PYTHONPATH=src python -m flujo --help`: pasa.
- `PYTHONPATH=src python -m flujo verify --no-pytest --no-hub-smoke`: pasa.
- `flujo health` y `flujo version`: pasan.

Esto demuestra que el arranque básico de FLUJO sigue funcionando, pero no
compensa la suite no recolectable ni los contratos de higiene fallidos.

## Instrucción para la siguiente revisión del supervisor

1. Resolver primero los cinco fallos bloqueantes de arriba.
2. No restaurar historia, handoffs, XIO ni Airdrop en bloque.
3. Para cada eliminación discutida, demostrar owner, consumer y capacidad rota.
4. Ejecutar `python -m pytest -q` completo.
5. Ejecutar `python tools/repo_audit.py --format text`.
6. Ejecutar `python tools/capabilities.py --no-live --check-branch`.
7. Ejecutar `PYTHONPATH=src python -m flujo verify` con pytest y hub smoke.
8. Actualizar este archivo con estados `[RESUELTO]`, `[DESCARTADO]` o
   `[PENDIENTE]`, incluyendo el commit que justifica cada decisión.
9. Sólo declarar lista la rama cuando la suite pueda recolectarse y los gates
   pasen sin excepciones ad hoc.

