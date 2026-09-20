# ORDEN

state: READY
cycle: supervisor-001
executor: Codex local
branch: SUPERVISOR

## Objetivo único

Eliminar la dependencia activa del test hacia la herramienta retirada
`tools/consolidate_static_duplicates.py` y quitar su entrada fantasma del
registry, sin resucitar esa herramienta.

## Preflight ya resuelto por el supervisor

No necesitas volver a investigar estas premisas:

- `tests/test_scan_roots_skip_cloud_mounts.py` existe y todavía importa
  `PROTECTED_TOPS` desde `tools.consolidate_static_duplicates`.
- La herramienta `tools/consolidate_static_duplicates.py` fue retirada.
- El owner vigente de la política de exclusión es
  `tools/build_mak_knowledge_db.py::ACTIVE_SKIP`.
- `ACTIVE_SKIP` ya contiene los cuatro roots que el test intenta proteger:
  `WIN`, `curatoria_inbox`, `GoogleDrive` y `OneDrive`.
- `data/tool_registry.json` todavía declara
  `consolidate_static_duplicates.py`.

No leas `SYSTEM.md`, `SUPERVISOR.md` ni historia Git salvo contradicción
concreta con estas premisas.

## Write-set esperado

- `tests/test_scan_roots_skip_cloud_mounts.py`
- `data/tool_registry.json`

Amplía el write-set sólo si una dependencia directa de estos dos archivos hace
imposible cumplir el objetivo; si ocurre, devuelve `BLOCKED` antes de abrir un
frente amplio.

## Trabajo

1. Cambia el test para que su contrato dependa del owner vigente
   `ACTIVE_SKIP`, no de `PROTECTED_TOPS`.
2. Conserva explícitamente la protección de:
   `WIN`, `curatoria_inbox`, `GoogleDrive`, `OneDrive`.
3. Elimina del registry la entrada
   `consolidate_static_duplicates.py`.
4. No reconcilies todavía el resto del registry.
5. Ejecuta:
   - `python -m pytest -q tests/test_scan_roots_skip_cloud_mounts.py`
   - `python -m pytest -q --collect-only`

## Si aparecen muchos errores

No intentes arreglarlos todos.

- Si un fallo fue causado por estos cambios y cabe en el write-set, corrígelo y
  vuelve a probar.
- Si es externo/preexistente, no amplíes el alcance.
- Si aparecen decenas o miles, agrúpalos por causa raíz/firma.
- Reporta conteo total y como máximo cinco grupos representativos.
- Un fallo externo no convierte esta tarea en `BLOCKED` si el objetivo quedó
  cumplido.
- Usa `BLOCKED` sólo si no puedes completar **este objetivo** dentro del
  alcance permitido.

## Criterio de éxito

- no queda import activo hacia
  `tools.consolidate_static_duplicates` en el test;
- el contrato de roots protegidos usa `ACTIVE_SKIP`;
- el registry ya no declara la herramienta retirada;
- el test específico pasa;
- la colección completa avanza más allá del antiguo
  `ModuleNotFoundError`.

## Entrega

No crees `ERRORES.md`, `RESULTADOS.md` ni otro handoff.

Reemplaza completamente este mismo archivo por:

```text
# ORDEN
state: DONE | BLOCKED
cycle: supervisor-001
objective_met: true | false

summary: <máximo 5 líneas>
changed:
  - <archivos realmente tocados>
tests:
  - <comando>: <resultado breve>
failure_groups:
  - signature: <causa raíz/firma>
    count: <n>
    relation: task_local | external | unknown
    example: <máximo una línea>
next_blocker: <sólo si objective_met=false; de lo contrario none>
```

Omite `failure_groups` si no hay fallos. Máximo cinco grupos. No pegues logs
largos ni historia.
