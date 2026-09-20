# ORDEN

state: READY
cycle: supervisor-002
executor: Codex local
code_base_expected: 6ebea3efb5ab8f7c87e0cc97ce415ad426875559
mode: BUILD

## Objetivo único

Cerrar la integración reciente de Azure ML haciendo que el status Azure del
Hub exponga **lineage read-only del último dataset sanitizado de learning**,
sin hacer llamadas nuevas a Azure y sin filtrar rutas locales, prompts,
documentos ni credenciales.

## Por qué esta tarea

El supervisor revisó la trayectoria reciente antes de elegirla:

- `9b92e4df` añadió export sanitizado de `learning_evaluations` y lineage
  MLflow.
- `3e8be117` resolvió la subida real del artefacto Azure ML.
- `cultura/mak_plataforma/azure_services.py` declara Machine Learning como
  `operational` y nombra `/api/azure/status` como consumer.
- La ruta `/api/azure/status` ya devuelve `azure_services.snapshot()`.
- Ese snapshot hoy muestra inventario de recursos, pero **no el receipt/run
  lineage** que el pipeline acaba de producir.
- `tools/azure_ml_learning_dataset.py` ya escribe un `receipt.json`
  sanitizado con filas, estados, target kinds, fingerprints, hash, run id y
  estado de artifact upload.

No investigues de nuevo si esos hechos son ciertos salvo contradicción concreta
en el checkout.

## Resultado funcional esperado

`/api/azure/status` debe incluir una sección estable y bounded, por ejemplo
`machine_learning_lineage`, que permita al operador saber si existe un último
dataset de learning y qué ocurrió con él.

Puede exponer únicamente metadata segura como:

- disponibilidad;
- schema del receipt;
- cantidad de filas;
- conteo de fingerprints;
- `statuses`;
- `target_kinds`;
- SHA256 del dataset;
- `mlflow_run_id` si existe;
- `artifact_upload`;
- `artifact_builder` si existe.

No devolver:

- `source`;
- `dataset_path`;
- `receipt_path`;
- rutas absolutas;
- prompts/documentos;
- credenciales;
- contenido del dataset.

Si no existe receipt, el endpoint debe seguir funcionando y nombrar la
ausencia; no es error global de Azure.

## Contrato de ubicación

Usa una variable opcional `MAK_AZURE_ML_STAGING_ROOT` para el directorio de
receipts, con el valor actual
`/home/mak/research/azure-ml/staging` como fallback.

Haz que `tools/azure_ml_learning_dataset.py` use el mismo contrato para su
`DEFAULT_OUT`, evitando que productor y consumer tengan dos rutas
independientes.

El consumer debe elegir determinísticamente el receipt más reciente entre los
subdirectorios válidos y degradar limpio ante JSON inválido o estructura
desconocida.

## Write-set esperado

- `cultura/mak_plataforma/azure_services.py`
- `tools/azure_ml_learning_dataset.py`
- un test dedicado nuevo o existente bajo `tests/` para este contrato
- `ORDEN.md` al entregar

No modifiques documentación histórica, registry global ni otras superficies
Azure salvo dependencia directa demostrada.

## Guard de concurrencia

`6ebea3efb5ab8f7c87e0cc97ce415ad426875559` es el último HEAD de producto
consumido.

1. `git fetch origin`.
2. Revisa los paths posteriores a ese code base.
3. Cambios posteriores limitados a archivos de control son esperados.
4. Si existe cualquier cambio de **producto** posterior antes de empezar,
   devuelve `BLOCKED` con `stale_code_base` y sólo esos paths. No apliques
   una orden vieja sobre producto nuevo.

## Implementación

1. Añade una función pura/read-only en `azure_services.py` que resuelva el
   último receipt desde el staging root.
2. Valida que sea el schema esperado y proyecta sólo la allowlist de metadata
   segura.
3. Añade esa proyección a `snapshot()` sin requerir Azure CLI adicional.
4. Haz que el productor `azure_ml_learning_dataset.py` respete
   `MAK_AZURE_ML_STAGING_ROOT`.
5. Añade tests con directorios temporales que cubran al menos:
   - sin receipts;
   - un receipt válido;
   - varios receipts y selección determinística del más reciente;
   - receipt inválido;
   - comprobación de que rutas locales/fields no permitidos no salen en la
     respuesta.
6. No hagas llamadas Azure/MLflow reales en tests.

## Pruebas

Ejecuta como mínimo:

- el test dedicado de Azure services/lineage;
- `python -m pytest -q tests/test_mak_azure_search.py`;
- `python -m pytest -q --collect-only`.

Si existe un test de Hub que pueda comprobar directamente que
`/api/azure/status` entrega el campo sin abrir sockets, añádelo o extiéndelo
sólo si cabe en el write-set lógico.

## Si aparecen errores

- Corrige fallos `task_local` dentro de esta integración.
- No abras frentes de registry, taxonomía, packaging o herramientas ajenas.
- Si aparecen muchos fallos, agrupa por causa raíz/firma; máximo cinco grupos.
- `DONE` si el objetivo funcional queda cumplido aunque haya fallos externos.
- `BLOCKED` sólo si el objetivo no puede completarse sin ampliar el alcance.

## Criterio de éxito

- productor y consumer comparten el mismo staging-root configurable;
- el Hub puede mostrar el último lineage sanitizado sin llamada Azure nueva;
- ninguna ruta local ni campo sensible del receipt se filtra;
- ausencia/corrupción de receipt degrada de forma explícita y no rompe el
  status Azure;
- tests dedicados pasan y pytest sigue recolectando.

## Entrega

No crees archivos auxiliares.

Reemplaza completamente este mismo archivo por:

```text
# ORDEN
state: DONE | BLOCKED
cycle: supervisor-002
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

Omite `failure_groups` si no hay fallos. No pegues logs largos ni historia.
