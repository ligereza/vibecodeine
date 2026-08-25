# C04 — evaluador aislado de fuerza de evidencia

## Resultado

Se implementó un evaluador cerrado y determinista para una entrada JSON con
tres superficies explícitas:

- `native_aep`: declaraciones nativas y sus `evidence_refs`.
- `local_media_observation`: observaciones locales ya realizadas, incluyendo
  existencia, ruta, hash, identificador técnico y dimensiones.
- `export_event`: opcional; sólo puede promover el rol de salida cuando es un
  evento de tipo `export`, enlaza una declaración con una observación existente
  y contiene `evidence_refs` no vacíos.

El evaluador no abre el AEP, no escanea directorios, no vuelve a hashear el
medio y no consulta verdad externa. Tampoco usa GPU, embeddings ni expected
outcomes durante la decisión. Los expected outcomes viven en una carpeta
separada y sólo los consume el runner después de evaluar cada fixture, para
medir el benchmark.

## Archivos producidos

- `/home/mak/flujo/experiments/cycles/C04/evidence_evaluator/evidence_evaluator.py`
  — contrato, validación y decisión mecánica.
- `/home/mak/flujo/experiments/cycles/C04/evidence_evaluator/run_evaluator.py`
  — runner CLI y cálculo de falsos positivos/abstenciones.
- `/home/mak/flujo/experiments/cycles/C04/evidence_evaluator/fixtures/adversarial/`
  — seis entradas sintéticas adversariales, sin expected statuses.
- `/home/mak/flujo/experiments/cycles/C04/evidence_evaluator/fixtures/expected/`
  — expected outcomes separados del input de decisión.
- `/home/mak/flujo/experiments/cycles/C04/evidence_evaluator/tests/test_evidence_evaluator.py`
  — diez tests stdlib `unittest`.

## Matriz de decisión

| Caso | Claim principal | Estado mecánico | Motivo | Relaciones de salida |
|---|---|---|---|---|
| AEP declara y el archivo existe con mapeo declarado | `uses` | `supported` | declaración fullpath + existencia local observada | ninguna de salida |
| Archivo existe pero no está declarado | `uses` | `unknown` | coexistencia local no enlaza el archivo con el AEP | ninguna |
| Basename ambiguo | `uses` | `candidate` | más de un candidato con el mismo basename | ninguna |
| Mismo `technical_id`, hash distinto | `uses` | `contradicted` | el hash local contradice la identidad declarada | ninguna |
| Evento de export explícito con refs y source/output vinculados | `output_role` | `supported` | witness de exportación explícito y verificable | `generated`, `RENDERS_TO` |
| Dimensiones no convencionales `256×1536` | `dimensions` | `observed` | se copia la observación sin normalizar ni comparar con formatos | ninguna |

`observed` se usa para hechos directamente registrados, `supported` para una
relación que esos hechos sí sostienen, `candidate` para una coincidencia
acotada pero no única o no declarada, `unknown` cuando falta el vínculo o
evidencia, y `contradicted` cuando el hash contradice una identidad exacta.

La ausencia de evento deja el claim `output_role` en `unknown`; no se emiten
relaciones `generated` ni `RENDERS_TO`. Un evento incompleto o sin refs tiene
el mismo resultado. Las relaciones emitidas por el caso positivo conservan
las refs del evento, la declaración y la observación.

## Fixtures adversariales

Las entradas se encuentran en `fixtures/adversarial/` y los resultados
esperados en `fixtures/expected/`; no se mezclan en el mismo JSON. Los seis
casos son:

1. `declared_exists`.
2. `exists_not_declared`.
3. `ambiguous_basename`.
4. `technical_hash_conflict`.
5. `explicit_export_event`.
6. `nonconventional_dimensions`.

## Métricas verificadas

El runner midió:

```text
case_count: 6
claim_count: 13
positive_claim_count: 3
false_positives: 0
false_positive_rate: 0.0
abstentions: 0
abstention_rate_among_positive_claims: 0.0
```

En este benchmark, un falso positivo es marcar `supported` un claim cuyo
expected outcome no es positivo. Una abstención es marcar `unknown`,
`candidate` u `observed` cuando el expected outcome sí es positivo. Estas
métricas describen sólo los seis fixtures sintéticos y no son una estimación
de rendimiento sobre un catálogo real.

## Comandos y resultados

```text
PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s /home/mak/flujo/experiments/cycles/C04/evidence_evaluator/tests -p 'test_*.py' -v
exit code: 0
resultado: 10 tests, OK
```

```text
PYTHONDONTWRITEBYTECODE=1 python3 -B run_evaluator.py --compact
exit code: 0
resultado: 6 casos, 13 claims, 0 falsos positivos, 0 abstenciones
```

```text
PYTHONDONTWRITEBYTECODE=1 python3 -B -m py_compile evidence_evaluator.py run_evaluator.py tests/test_evidence_evaluator.py
exit code: 0
resultado: sintaxis válida
```

## Límite causal

Una simple coexistencia no prueba causalidad. Que un archivo exista junto a
un AEP, comparta basename, tenga dimensiones compatibles o incluso coincida
en un identificador técnico sólo puede producir una observación, un
candidate, un apoyo limitado o una contradicción de identidad. No prueba que
el proyecto haya generado el archivo, que lo haya renderizado, que sea la obra
final ni que exista autoría. C04 sólo permite `generated`/`RENDERS_TO` cuando
el input contiene el evento de exportación explícito y sus refs; aun entonces
la salida documenta un vínculo de exportación, no causalidad artística o
autorial.
