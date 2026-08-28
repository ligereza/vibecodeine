# Plan de activación de capacidades MAK

## Objetivo

Activar el potencial ya existente en un vertical slice archivo -> memoria ->
curatoria -> research/application interno, sin crear otro framework, otro
registro ni otra base de datos.

El primer corte debe producir más evidencia explícita y menos gaps
justificados. No debe forzar un fit positivo ni crear un portfolio público o
una postulación.

## Corte 1: cerrar ARICA/Fondart sin cambiar arquitectura

### Dependencias

- Project IR y practice state aceptados del archivo ARICA.
- Testigos locales C04, C05 y C06 con hashes y límites intactos.
- Paquete local Fondart convertido a opportunity constraints.
- Un job de verificación de fuente oficial con source policy explícita.
- Frontier, triangulation y evidence return existentes.

### Acciones

1. Proyectar C04-C06 como evidencia de práctica técnica, sin afirmar autoría,
   entrega, publicación ni intención artística.
2. Ejecutar una única investigación bounded sobre la validez oficial de la
   convocatoria Fondart.
3. Triangular el receipt con grupos independientes; si no hay dos grupos,
   conservar `unresolved`.
4. Aplicar `evidence_return` como propuesta aditiva con `promotion=none`.
5. Recomputar desde fit usando el mismo snapshot Project IR/practice.
6. Comparar gaps, hard gates, source gate y application status antes/después.

### Gates de seguridad

- `archive_id`, `snapshot_id` e input hashes no cambian.
- C04-C06 permanecen en namespace de práctica y no se mezclan con refs del
  PDF de oportunidad.
- sólo bindings explícitos `requirement_ids/supports` cierran fit.
- `observed_local`, `stale` o `unknown` mantienen source abstain.
- contradicciones de hard gate fallan cerrado.
- research `dispatch=false`; evidence return `candidate_pending_ingestion`.
- `publication=false`, `submission=false`, `promotion=none`,
  `training_permitted=false`.
- si falta evidencia, el resultado esperado es una pregunta nueva, no un claim.

### Métricas

- cantidad de claims practice explícitos añadidos;
- cantidad de requisitos Fondart que pasan de unknown/missing a supported o
  permanecen justificadamente unresolved;
- cantidad y tipo de contradicciones;
- número de grupos independientes por resultado;
- application blocked/draftable;
- cero cambios en hashes de fuentes;
- cero dispatches, publicaciones, submissions o promociones.

## Corte 2: crosswalk de consumidores, no nuevo registro

Construir una tabla mantenida junto a esta documentación que relacione cada
capacidad con productor, contrato, consumidor, owner, test y estado runtime.
Debe reconciliar la topología de departamentos, órganos visibles y owner/
consumer map sin reemplazar ninguno.

Prioridad: Hub 8900, Research, Curatoria, Portfolio/ISKVW y RD. Copilot/Codex
recibe el crosswalk como contexto operativo, pero no adquiere autoridad sobre
claims.

Gate: ninguna fila `VIVO` sin consumidor medido; ninguna fila `REVISAR` se
reactiva sin un corte vertical completo.

## Corte 3: aprendizaje shadow con holdout real

Separar episodios por identidad de proyecto/archivo, no por filas. Usar sólo
resultados verificados y outcomes externos. Medir ranking de jobs,
priorización y selección de próxima consulta. Mantener en shadow cualquier
policy candidate mientras `deep_learning_gate` no valide holdout independiente.

No usar como labels: drafts, similarity, embeddings, abstentions,
contradictions no resueltas, claims externos no triangulados o resultados
generados por el mismo pipeline que se evalúa.

## Disposición de REVISAR/muertas

- `context_pack.py`, `token_budget.py` y `verify_all.py`: sólo recuperar si se
  les asigna consumidor real, contrato de salida y test de integración.
- `render_archaeology_deliverables.py`: mantener histórico hasta que un
  consumidor de snapshot SQLite esté delimitado y no duplique Project IR.
- `tapiz_live_loop.py` y `tapiz_telemetry.py`: no activar como daemon; primero
  demostrar una necesidad bounded y una política de parada.
- `render_video_rd.py` y rutas legacy de flyer: conservar manual-only donde la
  documentación ya lo declara; no presentarlas como producción activa.

## Definición de éxito

El plan termina cada corte con una salida reproducible, un consumidor real,
un gate medido, hashes comparables y una lista explícita de unknowns. El éxito
no es que el sistema diga “sí”; es que pueda explicar por qué dice sí, no,
abstain o research, y que esa explicación sobreviva al replay.

## Primer comando ejecutable

El primer trabajo operativo es el replay read-only de ARICA/Fondart desde los
outputs existentes en `/tmp`, después de proyectar C04-C06 y triangular la
validez oficial. Si cualquiera de esas entradas no tiene contrato aceptado,
el runner debe detenerse con `abstain` y registrar el campo faltante. No se
debe parchear el contrato en caliente ni ampliar el write-set.
