# Plan de acción portable de LUNA-ARCHIVE

## Resultado buscado

Convertir la cadena aceptada de MAK en un protocolo portable para archivos artísticos heterogéneos, sin añadir otro “piso” arquitectónico. El protocolo debe admitir fuentes incompletas, duplicados físicos, herramientas nativas distintas, outputs sin fuente conocida, proyectos sin publicación y publicaciones sin proyecto, conservando autoridad y abstención.

La unidad de progreso no será “más registros clasificados”, sino una reducción comprobable de incertidumbre sin promociones falsas.

## Métricas transversales

Cada corte debe publicar un reporte local y determinista con estas métricas:

- `source_mutations = 0` y hashes de control antes/después para fuentes seleccionadas.
- `partition_violations = 0`: cada `artifact_ref` asignado, ambiguo o no asignado exactamente una vez.
- `unresolved_refs_preserved = 100%`.
- `claims_without_evidence_promoted = 0`.
- `cross_authority_bindings_without_requirement_id = 0`.
- `research_jobs_dispatched = 0` salvo autorización separada y receipt explícito.
- `publications = 0` y `submissions = 0` durante compilación.
- `deterministic_rerun_equal = true` para iguales entradas normalizadas.
- `case_name_rules = 0` en contratos portables.
- `independent_archive_holdouts >= 2` antes de declarar portabilidad demostrada.

Un incremento de `supported` no es por sí solo una métrica de éxito. Un incremento de `unknown` puede ser correcto si repara un falso verde.

## Secuencia

### Corte 0 — Registro de conformidad y límites

Objetivo: convertir las invariantes de `hashmap.json` en una matriz ejecutable contra los contratos existentes.

Dependencias:

- Schemas aceptados de Stage 2D y Pisos 1–5.
- Fixtures adversariales existentes.
- Hashes y source refs del mapa LUNA-ARCHIVE.

Acciones:

1. Definir una tabla por contrato con input schema, output schema, autoridad, mutabilidad, abstenciones y side effects prohibidos.
2. Ejecutar casos de input alterado, refs faltantes, status no reconocido, duplicados de contenido, orden cambiado y resultados abiertos.
3. Registrar el error o abstención exactos; no suavizar excepciones para lograr cobertura.

Gate:

- Todos los contratos fallan cerrado ante schema o identidad inválidos.
- Cero writes fuera de outputs temporales.
- Cero promociones de candidate/unknown.

Fail-closed:

- Si un contrato no expone suficiente provenance, bloquear su conexión aguas abajo y abrir un gap de contrato.
- Si dos capas usan el mismo ID con significados distintos, detener el join; no renombrar silenciosamente.

### Corte 1 — Perfil portable de archivo

Objetivo: separar configuración física de semántica artística.

Dependencias:

- Corte 0 verde.
- Observer y memoria read-only.

Acciones:

1. Definir un `archive_profile` declarativo: tenant, archive ID, roots acotados, adapters disponibles, límites de scan, privacidad y herramientas observacionales.
2. Prohibir nombres de casos en decisiones de identidad o significado.
3. Ejecutar el mismo contrato sobre dos archivos independientes y un fixture adversarial.
4. Comparar snapshots sucesivos para diferenciar continuidad, movimiento, duplicación y ausencia observacional.

Gate:

- `case_name_rules = 0`.
- `partition_violations = 0` en cada archivo.
- Duplicados de bytes permanecen como referencias físicas distintas.
- Root no disponible produce abstención, no archivo vacío.

Fail-closed:

- Si el root excede el alcance o cambia durante la observación, invalidar el snapshot.
- Si una herramienta nativa no está disponible, conservar el artefacto y abrir `observation_gap`; no inferir su contenido.

### Corte 2 — Adaptadores de receipts técnicos a evidencia de práctica

Objetivo: incorporar witnesses existentes sin convertir actividad técnica en autoría, intención o publicación.

Dependencias:

- Perfil portable.
- Contrato `mak-practice-evidence-state-v1`.
- Namespace explícito para receipts de práctica.

Acciones:

1. Definir un envelope genérico de receipt con `artifact_refs`, `method`, `tool_version`, `checks`, `scope`, `supported_predicates` y `forbidden_inferences`.
2. Adaptar el witness de export C05/C06 y la observación C04 como primeros casos, conservando que `ARICA.aep -> output` sigue unknown y que un export no es publicación.
3. Rechazar receipts sin artifact refs resolubles, checks exitosos o scope compatible.
4. Recompilar practice state y medir qué gaps se cierran realmente.

Gate:

- Cada claim nuevo tiene evidence refs resolubles.
- `authorship_claims_added = 0`.
- `public_manifestations_added = 0` salvo witness público independiente.
- El mismo input produce el mismo hash de estado.

Fail-closed:

- Receipt técnico con predicado más amplio que sus checks se reduce a predicados apoyados o se rechaza.
- Receipt web o de oportunidad no entra al namespace de práctica.

### Corte 3 — Cierre de vigencia de oportunidad

Objetivo: verificar la fuente externa sin contaminar evidencia interna.

Dependencias:

- Frontier job explícito `source-validity:<opportunity_id>`.
- Captura general acotada y política de fuentes independientes.

Acciones:

1. Ejecutar una captura bounded de la fuente oficial de Fondart y guardar receipt, fecha, hash, URL y status.
2. Triangular la vigencia con el número de grupos independientes exigido.
3. Retornar una propuesta de evidencia de oportunidad, nunca de práctica.
4. Recalcular constraints y fit usando la misma practice snapshot.

Gate:

- Resultado ausente o no triangulado queda `unresolved`.
- `practice_evidence_proposals = 0` para esta investigación ambiental.
- Un source gate solo pasa con `current_verified` y confirmación explícita.

Fail-closed:

- HTTP exitoso sin contenido identificable no confirma vigencia.
- Fuente stale, expired o ineligible abstiene o falla según contrato.

### Corte 4 — Replay de producto común

Objetivo: comprobar que evidencia adicional mejora explícitamente el producto sin forzar fit positivo.

Dependencias:

- Cortes 2 y 3 con receipts aditivos.
- Mismo Project IR/practice snapshot del piloto para comparación causal.

Acciones:

1. Recomputar desde fit hacia possibility, research frontier, product plan, dossier y application/research package.
2. Comparar hashes y deltas de claims, gaps, requirements y assets.
3. Explicar cada cambio por un receipt nuevo; cualquier delta sin causa invalida el replay.
4. Mantener publicación, submission, dispatch, promotion y training deshabilitados.

Gate:

- `unexplained_output_deltas = 0`.
- Menos gaps solo cuando existe evidencia nueva.
- Un evaluator rejection nunca revive como abstention.
- Dossier y aplicación conservan la misma base de programas, claims y assets.

Fail-closed:

- Si el replay cambia con orden de entrada, detener y corregir canonicalización.
- Si el dossier genera narrativa sin claim apoyado, eliminar el átomo narrativo y abrir gap.

### Corte 5 — Evaluación independiente de portabilidad

Objetivo: demostrar transferencia, no solo funcionamiento del caso ARICA.

Dependencias:

- Cortes 0–4 verdes.
- Dos archivos holdout con permiso read-only y perfiles independientes.

Acciones:

1. Congelar contratos y seleccionar archivos sin ajustar reglas por sus nombres.
2. Ejecutar observe → memory → reconstruction → Project IR → practice state.
3. Crear un gold set ciego limitado a relaciones observables y particiones, no a interpretaciones estéticas.
4. Medir falsos merges, refs perdidas, promociones falsas, determinismo y carga de gaps.
5. Auditar por separado un output sin fuente conocida y un proyecto sin manifestación pública.

Gate:

- Dos holdouts independientes pasan las invariantes.
- `false_identity_merges = 0`.
- `lost_artifact_refs = 0`.
- `false_supported_claims = 0` en el gold set.
- Cualquier regla específica del caso invalida la declaración de portabilidad.

Fail-closed:

- Si un holdout falla, declarar el adapter o contrato no portable; no diluir el test agregando excepciones nominales.

### Corte 6 — Aprendizaje controlado entre archivos

Objetivo: aprender qué sonda reduce incertidumbre, sin aprender identidad o verdad artística.

Dependencias:

- Resultados externos verificados.
- Múltiples grupos de identidad y holdout independiente.
- Cortes de portabilidad verdes.

Acciones:

1. Compilar episodios por grupo estable tenant/archive, separado de snapshot.
2. Generar features de atención y ranking exclusivamente desde provenance y resultados verificados.
3. Separar train/holdout por identidad de archivo, nunca por filas del mismo snapshot.
4. Evaluar shadow policy y compararla con baseline determinista.
5. Permitir solo una propuesta de política; la promoción sigue siendo un gate separado.

Gate:

- `training_permitted` permanece false hasta satisfacer holdout y grupos mínimos.
- Outcomes abiertos no producen etiquetas negativas.
- Ningún target contiene autoría, intención, significado ni truth status.
- La política supera baseline en información obtenida por costo sin aumentar falsas promociones.

Fail-closed:

- Data leakage entre snapshots del mismo archivo invalida el experimento.
- Falta de recibo externo produce abstención.

## Primer corte ejecutable

Ejecutar ahora una **reconciliación de receipts técnicos a evidence atoms** usando únicamente los receipts existentes C04–C06 y el Project IR/practice snapshot del piloto ARICA en `/tmp`:

1. Inventariar los predicados realmente comprobados por cada receipt.
2. Emitir una propuesta práctica con artifact refs y alcance explícitos.
3. Validarla adversarialmente contra receipt sin refs, check fallido y predicado de publicación inventado.
4. Recompilar `mak-practice-evidence-state-v1` sin reescanear ARICA.
5. Comparar antes/después: claims apoyados, gaps cerrados, gaps nuevos y state hash.

Criterio de éxito: aumentar evidencia técnica trazable y reducir solo los gaps que esa evidencia resuelve. No es éxito obtener un fit positivo, una narrativa más larga ni assets públicos.

Después, y como acción separada, ejecutar el único job oficial de vigencia Fondart. Separar ambos receipts permite atribuir causalmente los cambios: uno pertenece a práctica; el otro, a oportunidad.

## Condición de detención

Detener el plan cuando ocurra cualquiera de estas condiciones:

- No cambia ningún hash de evidencia tras un intento.
- El próximo paso requiere mutar el archivo fuente.
- No puede conservarse la autoridad o provenance de una afirmación.
- El presupuesto o el máximo de un intento se agota.
- La incertidumbre seleccionada ya está cerrada.
- El siguiente paso sería publicar, postular, despachar o promover sin autorización explícita.

En cualquiera de esos casos, registrar `abstain`, `blocked` o `unresolved` con la evidencia disponible y elegir otro gap; no reinterpretar la detención como fracaso del archivo o del artista.
