# Plan de acción de control distribuido

## Resultado buscado

Cerrar los dos gaps que el piloto ARICA/Fondart ya seleccionó y repetir el mismo tramo desde fit hasta autonomía. No se agrega otro piso arquitectónico. El éxito es más evidencia explícita, menos gaps justificables y la misma prohibición de publicación, submission, training, dispatch y mutación de fuentes.

Baselines observados que deben conservarse como comparación, no como metas a maquillar:

- oportunidad local: 22 constraints, 8 hard gates y 8 documentos requeridos;
- fit: `abstain` con 16 constraints requeridos sin apoyo;
- dossier: 1 programa provisional, 99 assets privados/internos, 0 assets públicos, 0 narrative atoms inventados y 9 gaps;
- aplicación: 22 requirements mapeados y estado bloqueado;
- autonomía: 1 acción `research`, acotada y no despachada;
- fuentes ARICA: los 14 hashes declarados permanecieron iguales;
- gate de regresión: 173 pruebas focalizadas más compilación y whitespace en el checkpoint aceptado.

## Secuencia

### 0. Congelar el sobre de control

**Objetivo.** Reutilizar los contratos y snapshots aceptados, sin reconstruir arquitectura ni reobservar el archivo.

**Dependencias.** Project IR y practice snapshot del piloto bajo `/tmp`; oportunidad, fit, possibility, frontier, product plan, dossier, application y autonomy outputs del mismo run; hashes fuente previos.

**Gate de entrada.** Todos los JSON deben parsear, declarar el schema esperado y pertenecer a la misma identidad de oportunidad/archive snapshot. Si falta una ruta o no puede vincularse por ID/hash, detener el slice y registrar `missing_pilot_input`; no regenerar desde filenames.

**Métrica observable.** Conteo de contratos resueltos, mismatches de identidad y hashes de inputs.

**Fail closed.** Cero escritura en archive roots, production DBs o runtime roots. Toda salida temporal queda en un directorio nuevo bajo `/tmp`.

### 1. Primer slice ejecutable: vigencia oficial de Fondart

**Objetivo.** Resolver solo `source-validity:<opportunity_id>` con el job ya planificado por la autonomía real.

**Quién hace qué.** Research captura; el adaptador normaliza; el triangulador refuta o apoya; evidence return propone; el compilador de fit decide el nuevo gate. Ninguno de estos roles publica o despacha por sí mismo.

**Dependencias.** El frontier real del piloto, la URL o referencia oficial que ese job declare, el requirement ID técnico, el opportunity ID y un directorio temporal vacío. No usar la consulta legacy hard-coded de plantas ni inventar una URL desde el nombre del fondo.

**Ejecución acotada.** Primero resolver las rutas reales desde el manifiesto del piloto. Luego:

```text
./.venv/bin/python tools/triangulate_research_evidence.py \
  --frontier <frontier.json> \
  --results <official-source-result-batch.json> [<independent-result-batch.json>] \
  --output <tmp>/fondart-validity-triangulation.json

./.venv/bin/python tools/build_evidence_return.py \
  <opportunity.json> <practice.json> <fit.json> <frontier.json> \
  <tmp>/fondart-validity-triangulation.json \
  --output <tmp>/fondart-validity-evidence-return.json
```

La captura previa debe usar el general bounded capture path declarado por el job. Este plan no inventa su comando: si el job no resuelve a un consumer real, el slice falla con `missing_capture_consumer`.

**Gates.** Captura exit `0`; URL oficial y timestamp observados; hash de contenido presente; licencia/uso registrados; membership job/requirement válido; cada fuente y claim referenciable; independencia de grupos observada, no inferida por tener dos URLs. Solo `current_verified` más confirmación explícita puede abrir el source gate.

**Métricas.** `capture_status`, fuentes válidas, grupos independientes, claims apoyados/contradichos/no resueltos, errores de triangulación, propuestas aditivas, truth promotions y source mutation count.

**Fail closed.** Ante timeout, fuente no oficial, hash ausente, contradicción, vigencia ambigua o independencia insuficiente: resultado `unresolved`/`abstain`; cero propuestas de práctica; cero promoción; cero reintento automático después de `max_attempts=1`.

### 2. Proyectar witnesses C04-C06 a evidencia de práctica

**Objetivo.** Representar los receipts técnicos ya existentes en el vocabulario aceptado de práctica sin convertirlos en evidencia web, autoría, intención o claim curatorial automático.

**Dependencias.** Receipts C04-C06, hashes y referencias físicas existentes; schema `mak-practice-evidence-state-v1`; Project IR del mismo snapshot ARICA.

**Gate de entrada.** Cada witness debe resolver a un `artifact_ref` existente y a su hash/transform chain. Un receipt que solo nombre un archivo queda `unknown`.

**Transición permitida.** Añadir evidencia técnica como exportación, actividad u output observado dentro del scope `practice`; conservar límites de afirmación. C05 puede apoyar el evento de exportación medido; C06 puede apoyar `EXPORTS_TO`; el MP4 sin proyecto Unreal nativo mantiene `source_binding=unknown`.

**Métricas.** Witnesses considerados, artifact refs resueltos, hashes coincidentes, proposals aceptables, unknowns preservados, claims curatoriales nuevos y truth promotions.

**Fail closed.** `claims_curatoriales_nuevos=0` salvo que exista un contrato separado con evidencia explícita; `truth_promotions=0`; `public_assets_added=0`; fuente ARICA sin cambios.

### 3. Ingesta aditiva y replay desde fit

**Objetivo.** Ingerir solo propuestas que pasen sus gates y repetir fit -> possibility -> frontier -> evidence return -> product plan -> dossier/application -> episode/learning -> autonomy.

**Dependencias.** Outputs de los slices 1 y 2, snapshots originales y los mismos compiladores aceptados.

**Comandos de compilación relevantes.** Las firmas observadas son:

```text
./.venv/bin/python tools/compile_product_plan.py \
  <opportunity> <practice> <fit> <program_candidates> <possibility> \
  <frontier> <evidence_return> --output <tmp>/product-plan.json

./.venv/bin/python tools/compile_autonomy_plan.py \
  <product-plan> <dossier> <application> <evidence-return> \
  --learning <learning-evaluation> --output <tmp>/autonomy-plan.json
```

Los compiladores intermedios deben seleccionarse desde los schemas reales del piloto; no se reemplazan con fixtures.

**Gates.** Todos los inputs validan; IDs y hashes encadenan; rejected permanece rejected; evidence return fue ingerido aditivamente antes de recomputar; dossier y aplicación derivan del mismo product plan; controles finales siguen `promotion=none`, `training=false`, `publication=false`, `submission=false`, `dispatch=false`.

**Métricas comparativas.** Cambio de hash por contrato, source gate, supported/unsupported requirements, accepted/abstained/rejected programs, dossier gaps, narrative atoms apoyados, assets privados/públicos, application status, research jobs pendientes y acción prioritaria de autonomía.

**Criterio de mejora.** Menos gaps solo cuando una referencia nueva los cierra. Una abstención igual o más específica es válida. Un `pass` sin bindings nuevos es regresión.

**Fail closed.** Cualquier mismatch de schema/ID/hash produce `abstain` y detiene el replay aguas abajo. No se reanuda desde un artifact parcial como si fuese aceptado.

### 4. Validación independiente y no mutación

**Objetivo.** Demostrar que el replay preserva fuentes y límites de control.

**Dependencias.** Manifest de comandos y outputs del replay, hashes pre/post y suite focalizada de los quince contratos.

**Gates.** JSON parse; validadores de cada contrato; smoke real desde fit; comparación de hashes de las 14 fuentes ARICA; diff check limitado al write set del slice; ningún proceso permanente nuevo.

**Métricas.** Exit codes, tests passed/failed, validation errors, source hashes changed, runtime processes started, external side effects y outputs fuera del directorio temporal.

**Fail closed.** Un solo hash de fuente cambiado invalida el slice. Una prueba verde sobre fixture no sustituye el smoke con outputs reales. Restaurar no es una opción automática: preservar evidencia y detenerse en el boundary exacto.

### 5. Aprendizaje shadow entre archivos, no sobre verdad

**Objetivo.** Acumular outcomes externos verificados de múltiples identity groups para mejorar atención, ranking y routing sin entrenar verdad.

**Dependencias.** Episodios ledger-compatible, receipts externos, tenant/archive identity group estable y holdout independiente.

**Gates.** Outcome cerrado y verificado; identidad separada de snapshot; al menos más de un identity group para evaluar policy candidate; split independiente; `training_permitted=false` hasta un contrato posterior explícito.

**Métricas.** Identity groups, outcomes abiertos/cerrados, ejemplos elegibles, holdout count, señales de atención/ranking, policy candidates y promotion attempts.

**Fail closed.** Open, abstained, failed o needs-evidence no son negativos. Los borradores propios no prueban identidad, autoría ni calidad artística. Sin holdout independiente, estado `abstain`.

### 6. Gate futuro para autonomía ejecutora

**Objetivo.** Solo después de portabilidad real y aprendizaje shadow suficiente, especificar un adaptador explícito entre `mak-autonomy-plan-v1` y Conductor.

**Dependencias.** No están satisfechas hoy: consumer real, autorización por clase de acción, presupuesto, idempotencia, rollback, observabilidad y pruebas adversariales.

**Gate mínimo.** Allowlist de `observe/research/recompute/compile`; prohibición estructural de publish/submit/promotion/training/source mutation; job claim e idempotency; validación independiente; receipt; límites de intento/costo; kill switch. Las acciones externas conservan gate explícito.

**Métrica.** Cero dispatch implícito, cero acción fuera de allowlist, cero completion sin `validated=true`, cero consecuencia externa sin receipt.

**Fail closed.** Hasta que todos los requisitos tengan evidencia, `link.autonomy_conductor_blocked` permanece bloqueado y el plan sigue siendo documentación ejecutable, no actuador.

## Orden de decisión

1. Resolver inputs reales del piloto y congelar hashes.
2. Ejecutar una sola captura oficial de vigencia.
3. Triangular y retornar evidencia aditiva sin promoción.
4. Proyectar C04-C06 por una ruta practice-scoped separada.
5. Ingerir y recomputar desde fit.
6. Validar contratos, no mutación y side effects cero.
7. Comparar métricas contra el baseline y aceptar también una abstención mejor fundamentada.
8. Mantener autonomía en plan-only hasta que un futuro slice demuestre un adaptador seguro.

## Condición de cierre

El plan termina cuando los dos gaps tienen una disposición respaldada —cerrado o explícitamente no resoluble con el intento acotado—, el replay conserva todos los invariantes de [hashmap.json](hashmap.json), los cuatro documentos de aprendizaje siguen internamente consistentes y ninguna frontera externa fue cruzada.
