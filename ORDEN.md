# ORDEN

state: READY
cycle: supervisor-001
executor: Codex local
branch: SUPERVISOR

## Objetivo único

Restaurar la **recolección de pytest** sin resucitar
`tools/consolidate_static_duplicates.py`, que fue retirado deliberadamente.

## Contexto mínimo

- `tests/test_scan_roots_skip_cloud_mounts.py` todavía importa
  `PROTECTED_TOPS` desde la herramienta retirada.
- `data/tool_registry.json` todavía contiene la entrada fantasma
  `consolidate_static_duplicates.py`.
- No restaures esa herramienta sólo para satisfacer el import o un test viejo.
- No leas `SYSTEM.md`, `SUPERVISOR.md` ni historia Git salvo que esta tarea
  resulte imposible sin una contradicción concreta.

## Trabajo

1. Inspecciona `tests/test_scan_roots_skip_cloud_mounts.py` y localiza el
   owner **actual** de la regla que protege roots/mounts.
2. Haz que el test valide la superficie actual:
   - reutiliza un owner vigente si ya existe;
   - si el contrato murió junto con la herramienta, retira/reformula únicamente
     el test obsoleto en vez de recrear el módulo.
3. Elimina de `data/tool_registry.json` la entrada fantasma
   `consolidate_static_duplicates.py`.
4. No intentes todavía reconciliar todas las herramientas faltantes del
   registry; eso será otra orden.
5. Ejecuta como mínimo:
   - `python -m pytest -q tests/test_scan_roots_skip_cloud_mounts.py`
   - `python -m pytest -q --collect-only`
6. Si aparece el siguiente fallo de colección, **no abras un frente nuevo**:
   regístralo como bloqueo para el supervisor.

## Criterio de éxito

- ya no existe un import activo hacia
  `tools.consolidate_static_duplicates`;
- el registry ya no declara ese archivo eliminado;
- el test afectado pasa o fue retirado con justificación de contrato obsoleto;
- la colección completa avanza más allá de este `ModuleNotFoundError`.

## Entrega

No crees `ERRORES.md`, `RESULTADOS.md` ni otro handoff.

Al terminar, **reemplaza completamente este mismo `ORDEN.md`** por:

```text
# ORDEN
state: DONE | BLOCKED
cycle: supervisor-001

summary: <máximo 5 líneas>
changed:
  - <archivos tocados>
tests:
  - <comando>: <resultado breve>
next_blocker: <uno, si existe; de lo contrario none>
```

No pegues logs largos ni historia.
