# C03 — reporte del puente ciego

## Alcance

Este experimento está aislado en `experiments/cycles/C03/blind_bridge/` y usa
únicamente observaciones sintéticas normalizadas. La raíz declarada es
`archive-arica-001`; no se infiere autoría, no se consulta producción, no se
lee una base de datos y no se modifica ningún archivo nativo.

La función pública de recuperación es `recover(observations)`. Tanto ella como
`recover_direct(observations)` y `recover_mediated(observations)` reciben un
solo bundle de observaciones públicas y locales/nativas. El módulo de
recuperación no importa `evaluator.py` ni abre `truth.json`. `runner.py` ejecuta
ambas recuperaciones primero y sólo después carga el archivo de evaluación.

## Archivos del experimento

- `bridge.py` — normalización, validación, baseline directo y puente mediado.
- `evaluator.py` — carga separada de la verdad y cálculo de métricas.
- `runner.py` — ejecución reproducible y salida JSON por stdout.
- `fixtures/observations.json` — observaciones públicas y locales/nativas; no
  contiene etiquetas de evaluación.
- `fixtures/truth.json` — verdad separada para puntuar los seis queries.
- `fixtures/observations_catalog_absent.json` y
  `fixtures/truth_catalog_absent.json` — caso separado de catálogo ausente.
- `tests/test_blind_bridge.py` — 9 pruebas `unittest` de stdlib.

## Casos adversariales

| Query | Forma | Baseline directo | Puente mediado | Verificación |
|---|---|---|---|---|
| `pub-exact` | hash exacto único | `confirmed` → `local-exact` | `confirmed` → `local-exact` | TP |
| `pub-reencode` | bytes distintos, misma clase técnica y duración | `candidate` → `local-reencode` | `confirmed` → `local-reencode` | TP; requiere clave de observación nativa compatible |
| `pub-decoy` | decoy y objetivo con mismas dimensiones | `candidate` → `local-decoy-a` | `confirmed` → `local-decoy-z` | baseline FP; puente TP por evidencia explícita |
| `pub-no-local` | publicación sin local | `unknown` | `unknown` | abstención |
| `pub-ambiguous` | dos locales con el mismo hash exacto | `ambiguous` | `ambiguous` | abstención |
| `pub-conflict` | hash exacto con conflicto nativo explícito | `confirmed` | `contradicted` | baseline FP; puente conserva conflicto |
| `local-only` | local sin publicación | queda en `orphan_local_ids` | queda en `orphan_local_ids` | no se inventa publicación |

El baseline directo usa igualdad SHA-256 cuando es única; si no hay hash
exacto, compara clase de media, ancho, alto y duración cuando ambas partes la
declaran. Ante varios candidatos técnicos el baseline escoge el primero por
ID, precisamente para hacer visible el falso enlace del decoy. El puente
mediado no escoge entre varios candidatos: sólo confirma una coincidencia
técnica única con una observación nativa explícita y compatible; ante conflicto
explícito emite `contradicted`.

Los resultados pueden emitir exactamente los estados del contrato:
`candidate`, `confirmed`, `contradicted`, `ambiguous` y `unknown`.
Dimensiones, MIME y coincidencia técnica no son prueba de procedencia. No se
usan embeddings, modelos, red ni GPU.

## Métricas observadas

La cobertura principal es `TP / casos_linkables`; también se reporta
`decision_coverage = (TP + FP) / total_cases`. `abstentions` incluye
`unknown`, `ambiguous` y `contradicted`; `contradicted` se desglosa aparte.

| Estrategia | TP | FP | Abstenciones | Contradicted | Cobertura linkable | Decision coverage |
|---|---:|---:|---:|---:|---:|---:|
| Directa | 2 | 2 | 2 | 0 | 0.6667 | 0.6667 |
| Mediada conservadora | 3 | 0 | 3 | 1 | 1.0000 | 0.5000 |

La mejora relevante del puente es eliminar los dos falsos enlaces del
baseline: el primer candidato del decoy y la confirmación por hash en el caso
con conflicto. La menor `decision_coverage` mediada es intencional: el puente
se abstiene cuando la evidencia no basta.

## Catálogo ausente

`observations_catalog_absent.json` declara `catalog_status=unavailable` y no
declara publicaciones recuperables. Ambos resolvers devuelven el query
`catalog-request-arica-001` con `status=unknown`, razón
`public_catalog_unavailable` y cero candidatos locales. La evaluación produce
cobertura `0.0`; la ausencia no se transforma en un resultado vacío presentado
como reconciliación.

## Comandos y códigos de salida

Ejecutados desde `experiments/cycles/C03/blind_bridge/`:

```text
python3 -m py_compile bridge.py evaluator.py runner.py tests/test_blind_bridge.py
exit 0

python3 -m unittest discover -s tests -v
exit 0 — 9 tests OK

python3 runner.py
exit 0 — catálogo disponible; salida JSON con métricas y estados anteriores

python3 runner.py --catalog-absent
exit 0 — ambos caminos devuelven unknown por catálogo ausente
```

La comprobación de aislamiento de la suite también confirmó que las tres
entradas de recuperación tienen una sola firma `observations`, que un campo de
evaluación insertado en las observaciones es rechazado, y que la salida del
runner no contiene relaciones fuera del contrato del ciclo.

## Limitaciones y siguiente paso

El `bridge_observation_key` es una observación sintética compartida entre el
registro público y la evidencia nativa; demuestra el contrato de mediación,
pero no demuestra que un export real contenga esa clave ni que una actividad
local haya causado una publicación. El benchmark tampoco prueba OCR, lectura
de un catálogo social real, orden temporal, intención, autoría o equivalencia
visual.

El siguiente paso acotado es sustituir sólo `observations.json` por un export
real normalizado, manteniendo `truth` fuera del resolver y dejando cualquier
campo no observado como `unknown` o abstención.
