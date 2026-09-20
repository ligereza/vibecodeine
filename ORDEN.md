# ORDEN

state: READY
queue: vibe-buffer-004
executor: Codex local
base_product_head: fbd2760abd312b5beda2cc3b082ad88fe0110ab4
target_work: 30-60m
execution: sequential

## Protocolo

- Consume items en orden.
- Después de cada item: commit de producto + resultado compacto aquí; luego continúa sin esperar al supervisor.
- CONDITIONAL se promueve sólo si dependencias DONE y condición verdadera.
- Condición falsa => SKIPPED. stale product HEAD o blocker de alcance => top-level BLOCKED y detenerse.
- No crear reportes auxiliares.

## item vcd-004
state: READY
mode: BUILD
depends_on: []
objective: Convertir el preview de una tarea de Portfolio en una solicitud de revisión humana explícita y trazable, todavía sin ejecutar nada.

premises:
- portfolioWorkPacket ya expone 4 tareas.
- portfolioWorkPreview selecciona una tarea sólo para display.
- next_action actual es human_review_selected_work_preview_before_execution.

requirements:
- Crear un contrato pequeño portfolio_work_review_request con project_id, task_id, evidence/source refs, requested_at/request_id y estado pending_human.
- Debe ser validable, no afirmar aprobación y conservar execution_allowed=false.
- Añadir endpoint POST idempotente en FLUJO Hub para preparar/registrar la solicitud.
- Persistencia runtime acotada bajo ruta configurable; no reutilizar selections.jsonl ni classifications.jsonl.
- Añadir al HubDashboard un control solicitar revisión desde el preview y mostrar pending_human.
- No ejecutar normalize, measurement, publication, selection ni promotion.

write_set:
- src/flujo/knowledge/portfolio_work_review_request.py
- src/flujo/web/hub.py
- web/src/api/flujoApi.ts
- web/src/components/HubDashboard.tsx
- tests directly related

tests:
- dedicated contract tests
- affected hub endpoint tests
- python -m pytest -q --collect-only
- smallest existing web typecheck if dependencies exist

success:
- preview -> pending_human review request funciona end-to-end;
- duplicate request_id is idempotent;
- no execution flags become true.

## item vcd-005
state: CONDITIONAL
mode: BUILD
depends_on: [vcd-004]
condition: vcd-004.objective_met == true
objective: Permitir que un actor humano confirme o rechace la solicitud, registrando una decisión idempotente sin ejecutar la tarea.

requirements:
- Extender la autoridad de vcd-004 con human_confirmed o human_rejected.
- Requerir actor no vacío + request_id + identidad exacta de la solicitud.
- Rechazar confirmación de solicitud inexistente o distinta.
- Mantener execution_allowed=false, promotion=none, publication=false.
- Read model y Hub muestran pending/confirmed/rejected.
- UI mínima: actor + confirmar/rechazar; nunca auto-confirmar.

tests:
- idempotent confirm/reject
- wrong request identity fails closed
- no execution after confirmation
- affected endpoint tests + collect-only

success:
- una persona puede dejar una decisión explícita y trazable;
- el sistema todavía no ejecuta ninguna tarea.

## item vcd-006
state: CONDITIONAL
mode: BUILD
depends_on: [vcd-005]
condition: vcd-005.objective_met == true
objective: Producir un receipt de readiness para structural_order confirmado, sin ejecutar nada nuevo ni generalizar a las otras tres tareas.

premises:
- operation_receipt.py ya demuestra una operación estructural local acotada.
- portfolio work packet tiene task_id structural_order.

requirements:
- Combinar confirmed human decision + task_id exacto + operación estructural existente + provenance/hash.
- Si no puede demostrarse mapping seguro, marcar SKIPPED con reason=no_safe_executor_authority; no inventar mapping.
- Readiness sólo puede ser ready_for_manual_execution o not_authorized.
- Exponerlo en Hub junto al preview/decision.
- No tocar archive_orientation, practice_relation ni vizz_calibration.

tests:
- confirmed structural_order with matching authority -> readiness
- unconfirmed/rejected -> not_authorized
- mismatched operation -> fail closed / skipped
- collect-only

success:
- el operador puede saber si la tarea estructural está lista para ejecución manual sin que el Hub la ejecute.

## Resultado por item

Al terminar cada item reemplaza su cuerpo operativo por:
item state: DONE | BLOCKED | SKIPPED
objective_met: true | false
product_commit: <sha-or-none>
summary: <max 4 lines>
changed: [..]
tests: <brief>
failure_groups: <optional max 5>
reason: <only for BLOCKED/SKIPPED>

Al final:
- todos DONE/SKIPPED -> top-level state: DEPLETED
- cualquier BLOCKED -> top-level state: BLOCKED