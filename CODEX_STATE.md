# CODEX_STATE.md — reporte del ejecutor local

> **Propietario: Codex local. ChatGPT supervisor no edita este archivo.**

```yaml
schema: vibecodeine-codex-state-v1
branch: SUPERVISOR
status: IDLE
current_phase: none
last_completed_phase: none
last_seen_order_generation: 1
last_commit: none
updated_at: null
```

## Regla

Este archivo informa; no decide qué hacer. La orden está en `ORDEN.md`.

Antes de una fase cambia `status` a `RUNNING`, indica `current_phase` y
haz commit/push junto con el trabajo cuando corresponda.

Después de una fase registra debajo una entrada compacta. No escribas una
narración de sesión.

## Resultados

_Aún no hay fases ejecutadas._

## Formato por fase

```markdown
### Sxxx — <resultado: PASS | FAIL | BLOCKED | PARTIAL>
- head_before:
- commit:
- changed:
- verification:
  - `comando` -> resultado real
- findings:
- residual_risk:
- next_safe_action:
```

Si una fase falla, no la disfraces de completada. Un `FAIL` bien medido es
información útil para que el supervisor replantee la cola.
