# ORDEN

state: READY
cycle: supervisor-003
executor: Codex local
code_base_expected: 1e415a574cde36c35ccef199f54811948cfa5a13
mode: BUILD

## Objetivo único

Hacer visible en el panel humano de MAK el lineage sanitizado de Azure ML que
ya produce el sistema, **sin provocar llamadas Azure, MLflow ni Azure CLI en
el polling del panel**.

Cadena a cerrar:

```
local receipt
  -> MAK /api/azure/lineage
  -> FLUJO /api/mak
  -> MakPanel
```

## Por qué esta tarea

El ciclo anterior ya cerró el backend de lineage. La trayectoria reciente del
repo combina Hub + MAK/FLUJO + RD/learning.

Preflight verificado:

- `cultura/mak_plataforma/azure_services.py::machine_learning_lineage()`
  lee sólo el staging local y devuelve una proyección sanitizada.
- `/api/azure/status` usa el snapshot general de Azure; no es apropiado para
  un panel que refresca periódicamente porque el snapshot también resuelve
  inventario de servicios.
- `src/flujo/web/hub.py::_get_mak()` consulta actualmente sólo
  `FLUJO_MAK_URL + /api/organismo`.
- `web/src/components/MakPanel.tsx` hace GET `/api/mak` y refresca cada 30 s.
- Ese panel ya representa salud, servicios, actividad, memoria y tandas del
  box. El lineage pertenece ahí; no hace falta crear otro dashboard.
- El backend FLUJO ya tiene doctrina explícita de forwarding allowlisted:
  no debe retransmitir campos desconocidos del box.

No vuelvas a investigar el registry global ni la taxonomía de tests.

## Implementación

### MAK

1. En `cultura/mak_plataforma/hub.py`, importa de forma opcional
   `machine_learning_lineage` junto a las superficies Azure existentes.
2. Añade GET `/api/azure/lineage`.
3. Esa ruta debe invocar **sólo** `machine_learning_lineage()`.
4. No debe llamar `snapshot()`, `_resource_inventory()`, Azure CLI,
   MLflow, telemetry ni red.
5. Si el adapter no está disponible, degrada con schema/status explícitos sin
   tumbar el Hub.

### FLUJO

6. Extiende `src/flujo/web/hub.py::_get_mak()` para consultar además
   `/api/azure/lineage` en el mismo `FLUJO_MAK_URL`.
7. Un fallo del endpoint de lineage **no convierte al box completo en
   indisponible** si `/api/organismo` respondió.
8. Publica el resultado bajo `azure_ml_lineage`.
9. Proyecta campo por campo; no hagas `**payload` ni forward de claves
   desconocidas. Sólo permite metadata ya declarada:
   `schema`, `available`, `status`, `rows`, `fingerprint_count`,
   `statuses`, `target_kinds`, `dataset_sha256`, `mlflow_run_id`,
   `artifact_upload`, `artifact_builder`.
10. No expongas URLs internas, rutas locales ni mensajes de excepción del box
    como contenido del lineage. Si la consulta falla, usa una razón compacta
    local como `unavailable`.

### UI

11. Extiende el tipo local `Data` de
    `web/src/components/MakPanel.tsx` con `azure_ml_lineage`.
12. Muestra una sección compacta "Azure ML · lineage" dentro del panel MAK:
    estado, filas, fingerprints, run id/upload cuando existan.
13. Cuando esté ausente/invalid/unavailable, debe decirlo sin pintar un falso
    éxito.
14. No agregues botones, acciones ni polling adicional: usa el GET `/api/mak`
    que ya corre cada 30 s.

## Write-set esperado

Sólo:

- `cultura/mak_plataforma/hub.py`
- `src/flujo/web/hub.py`
- `web/src/components/MakPanel.tsx`
- tests directamente relacionados bajo `tests/`
- `ORDEN.md` al entregar

No modifiques `azure_services.py` salvo que un test demuestre un defecto
task_local del contrato recién creado; su proyección ya fue aceptada en el
ciclo anterior.

## Guard de concurrencia

`1e415a574cde36c35ccef199f54811948cfa5a13` es el último HEAD de producto
consumido.

1. Haz `git fetch origin`.
2. Revisa los paths cambiados después de ese code base en la superficie de
   producto.
3. Commits posteriores que sólo cambien `SUPERVISOR.md` y/o `ORDEN.md`
   son control-plane esperado.
4. Si aparece cualquier otro path antes de comenzar, devuelve
   `BLOCKED stale_code_base` con esos paths y no ejecutes la orden vieja.

## Pruebas mínimas

Añade/ajusta pruebas que demuestren:

1. la ruta MAK de lineage puede responder usando un receipt local sin llamar
   inventario Azure;
2. `_get_mak()` conserva `disponible=true` si organismo responde aunque
   lineage falle;
3. cuando lineage responde, FLUJO sólo expone la allowlist;
4. ninguna ruta/source/prompt/campo desconocido cruza a `/api/mak`;
5. `MakPanel.tsx` contiene la superficie de lineage y no añade otro timer.

Ejecuta como mínimo:

- `python -m pytest -q -o addopts='' tests/test_azure_ml_lineage.py`
- los tests de `_get_mak` que extiendas o añadas;
- `python -m pytest -q --collect-only`
- el check TypeScript/build más pequeño ya declarado por el repo que cubra
  `MakPanel.tsx`; si el entorno no tiene dependencias JS, reporta
  `js_dependencies_unavailable` como external en vez de instalar o ampliar
  alcance.

No abras sockets reales ni hagas requests reales a Azure en tests.

## Si aparecen errores

- Corrige sólo `task_local` dentro de esta cadena.
- No abras registry, packaging, Portfolio ni taxonomía por rebote.
- Agrupa múltiples fallos por causa raíz/firma; máximo cinco grupos.
- `DONE` si la cadena queda cerrada aunque exista un fallo external.
- `BLOCKED` sólo si el objetivo no puede completarse dentro del write-set.

## Criterio de éxito

Un operador que abre el panel MAK puede ver el último lineage local de Azure ML
sin que ese acto consulte Azure. La ausencia del receipt o del sub-endpoint es
visible y no degrada falsamente la salud general del box.

## Entrega

No crees archivos auxiliares.

Reemplaza completamente `ORDEN.md` por:

```text
# ORDEN
state: DONE | BLOCKED
cycle: supervisor-003
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

Omite `failure_groups` si no hubo fallos.
