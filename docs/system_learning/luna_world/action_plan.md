# Plan de acción LUNA-WORLD para el acoplamiento MAK–mundo

## Resultado buscado

Convertir el ciclo ya aceptado de oportunidad, research, triangulación y retorno en una capacidad repetible sobre fuentes oficiales cambiantes, sin aumentar falsos positivos ni crear un crawler, base o departamento paralelo. El objetivo observable es que MAK detecte un cambio relevante, lo capture con procedencia, determine qué requisitos afecta, investigue solo la incertidumbre de alto valor, retorne evidencia como propuesta y recompute productos sin publicación, submission ni promoción automática.

Este plan se apoya en el [inventario](inventory.json), el [mapa de sistema](hashmap.json) y la [teoría](system_theory.md).

## Principios de ejecución

1. Un corte debe tener fuente física, contrato de entrada, consumidor, salida y gate foreground.
2. El default de red es plan-only; cada captura real es una URL, un objetivo y un intento.
3. Una URL igual con hash distinto es una nueva versión; una URL distinta con bytes iguales es evidencia de duplicación, no independencia.
4. `current_verified` exige confirmación explícita; unknown, observed_local y stale abstienen.
5. La evidencia de oportunidad y la evidencia de práctica conservan namespaces separados.
6. Triangulación requiere grupos y dominios independientes, no cantidad bruta de páginas.
7. Evidence return propone; ingestión y recomputación son acciones separadas.
8. Sin cambio de hash, sin ganancia de información o con presupuesto agotado, el ciclo se detiene.

## Secuencia práctica

### Corte 1 — cerrar la validez oficial del piloto real

**Objetivo.** Resolver el gap `source-validity:<opportunity_id>` del corpus local Fondart usado por el piloto ARICA, mediante la ruta general de captura, sin hardcodear la institución ni reutilizar una consulta legacy.

**Dependencias.** Frontier real persistido en `/tmp` o reproducible desde los inputs ya verificados; URL oficial exacta; revisión de licencia; `tools/research_source_capture.py`; contratos `mak-research-result-batch-v1`, `mak-research-triangulation-v1` y `mak-evidence-return-v1`.

**Acciones.**

1. Reproducir el job de validez y comprobar que mantiene `planned_not_dispatched`, requirement explícito y policy de fuente.
2. Ejecutar primero el modo plan del gate de captura. Verificar URL canónica, backend propuesto, `network_called=false` y acción siguiente.
3. Tras revisar licencia y autoridad de la URL, ejecutar una sola captura `--record` con timeout acotado; guardar receipt, raw/text SHA-256, fecha, backend, código/estado y licencia en un directorio temporal.
4. Construir un result batch que conserve exactamente el `job_id + requirement_id` del frontier.
5. Conseguir un segundo grupo verdaderamente independiente solo si el claim requiere corroboración; un mirror o dos páginas del mismo dominio no cuentan.
6. Triangular, construir evidence return y verificar que cualquier propuesta siga `candidate_pending_ingestion`, `promotion=none` y `training_permitted=false`.
7. No ingerir ni recomputar si la captura es ambigua, contradictoria, sin hash, sin licencia o fuera de período.

**Gate.** Éxito no significa oportunidad vigente. Significa: captura reproducible, hashes válidos, pair reconciliation completa, independencia correctamente contada, contradicciones preservadas y una decisión explícita entre proposal, unresolved o contradiction. Cualquier error de provenance, licencia, ID o fecha falla cerrado.

**Métricas observables.** Capturas reales `<=2`; llamadas por URL `=1`; pares inesperados `=0`; sources sin raw/text hash `=0`; falsos `current_verified=0`; promoción, submission, publication y training `=0`.

### Corte 2 — retornar witnesses técnicos de ARICA a práctica

**Objetivo.** Proyectar los receipts C04-C06 ya existentes en el vocabulario aceptado de práctica, sin tratarlos como evidencia web, autoría, publicación o claim curatorial automático.

**Dependencias.** Artefactos aceptados del Project IR/practice snapshot; hashes de los witnesses; contrato de propuesta `scope=practice`; artifact refs no colgantes.

**Acciones.** Mapear cada witness a un artifact existente, conservar relación y límites del claim, generar candidate evidence con namespace de práctica, rechazar refs colgantes y recomputar fit desde el mismo snapshot.

**Gate.** Los hashes fuente permanecen iguales; cada propuesta de práctica nombra artifacts aceptados; cero claims de autoría/publicación; cero activos públicos promovidos; disminución de gaps solo cuando un requirement queda explícitamente enlazado.

**Métricas.** Artifact refs colgantes `=0`; namespaces cruzados `=0`; claims inventados `=0`; diferencia del hash de practice explicada por proposals ingeridas.

### Corte 3 — adaptador Vigía -> paquete de captura

**Objetivo.** Cerrar el hueco entre candidato detectado y fuente versionada sin convertir el watcher en scraper ni compilador semántico.

**Dependencias.** Filas Vigía deduplicadas; source registry declarativo; gate de captura existente; oportunidad genérica sin campos Fondart.

**Acciones.** Diseñar un adaptador puro que acepte una fila de Vigía y emita un capture plan con ID determinista, URL canónica, source-group candidata, licencia `pending_review` y razón de prioridad. Debe rechazar URLs inválidas, duplicados semánticos y candidatos sin procedencia del watcher.

**Gate.** Fixtures adversariales: mismo contenido en URLs distintas no crea independencia; misma URL con hash distinto crea nueva versión; rediseño masivo de URLs activa avalanche; candidato sin URL queda en review y no llega al compilador.

**Métricas.** Duplicados reenviados `=0`; candidatos sin provenance compilados `=0`; orden determinista `100%`; network calls del adaptador `=0`.

### Corte 4 — radar de validez diferencial

**Objetivo.** Priorizar refresh por cambio semántico y valor de información, no por intervalo fijo o volumen de páginas.

**Dependencias.** Al menos dos snapshots inmutables por una oportunidad; diff por requirement; deadline confirmado o explícitamente unknown; costo estimado de captura.

**Acciones.** Clasificar cambios en `identity`, `validity`, `deadline`, `eligibility`, `budget`, `required_document`, `criterion_weight`, `transfer` y `nonsemantic`; calcular qué hard gates/productos podrían cambiar; emitir como máximo un refresh action por source/revision; parar si no cambia el hash semántico.

**Gate.** Un cambio de estilo HTML no altera constraints; un PDF distinto bajo la misma URL dispara reconciliación; pesos incompletos bloquean scoring; fechas no confirmadas nunca pasan a current_verified.

**Métricas.** Latencia de detección; cambios semánticos por captura; recomputaciones sin cambio; hard gates cerrados por costo; tasa de alertas no semánticas; contradicciones preservadas.

### Corte 5 — portfolio de oportunidades multi-caso

**Objetivo.** Probar reusabilidad con al menos tres familias de oportunidades y dos archivos/artistas, sin entrenar política.

**Dependencias.** Cortes 1-4 verdes; fuentes con licencias compatibles; identidad de tenant/archive estable y separada de snapshot.

**Acciones.** Ejecutar los mismos contratos sobre una convocatoria pública nacional, una residencia y una comisión/beca; incluir al menos un caso expirado, uno contradictorio y uno vigente; comparar abstenciones, jobs, costos y productos internos.

**Gate.** Cero campos específicos de institución en el núcleo; outcomes separados por identity group; holdout independiente antes de cualquier policy candidate; publicación y submission siguen deshabilitadas.

**Métricas.** Cobertura de requisitos con locator; falsos pass de hard gate; contradicciones detectadas; costo por requirement cerrado; grupos independientes; outcome receipts externos; identity groups disponibles para shadow learning.

### Corte 6 — aprendizaje de atención, no de verdad

**Objetivo.** Usar outcomes externos verificados para ajustar prioridad de observación e investigación, conservando contratos y gates invariantes.

**Dependencias.** Diversidad de identity groups, outcomes verificables, holdout independiente, estabilidad de hashes y features de routing.

**Acciones.** Evaluar solo señales de atención, ranking, costo y cierre; prohibir labels derivados de drafts propios; comparar una policy candidate contra baseline en shadow; promover únicamente mediante un gate separado y evidencia independiente.

**Gate.** `training_permitted=false` hasta que el holdout y la diversidad sean suficientes; ningún cambio de policy puede alterar source validity, requirement binding, independencia o no-promotion.

**Métricas.** Regret de selección de research, tiempo/costo por gap cerrado, generalización por identity group, degradación de falsos positivos, número de decisiones abstained convertidas correctamente en preguntas útiles.

## Primer corte ejecutable

El primer corte ejecutable es **Corte 1, pasos 1 y 2 solamente**: reproducir el job oficial de validez del piloto y ejecutar el gate de captura en modo plan. Es reversible, no hace red, no escribe bases, no modifica fuentes y permite verificar que el vínculo `opportunity_id -> job_id -> requirement_id -> URL oficial candidata` está completo antes de autorizar una captura.

La primera orden foreground propuesta es:

```text
./.venv/bin/python tools/research_source_capture.py '<official-url-from-frontier>' --root '<temporary-source-corpus>'
```

Debe observarse `schema=mak-source-capture-gate-v1`, `decision=plan`, URL canónica, `network_called=false` y `next_action=review_url_license_then_rerun_with_record`. La URL no se inventa ni se copia desde este documento: se toma del frontier/paquete real y se coteja con la fuente oficial.

## Matriz de parada y fallo cerrado

| Señal | Acción segura | Reanudación permitida |
|---|---|---|
| URL inválida o no oficial | `abstain`; conservar candidato | nueva URL con procedencia |
| hash ausente o inválido | rechazar batch | receipt completo |
| misma URL, hash distinto | nueva versión; reconciliar | después del diff semántico |
| dos fuentes del mismo grupo/dominio | independencia insuficiente | fuente realmente independiente |
| fecha no confirmada | mantener `observed_local`/unknown | confirmación oficial |
| reglas contradictorias | emitir contradiction notice | evidencia que explique versión/alcance |
| pesos incompletos | no calcular fit ponderado | pesos reconciliados con locator |
| artifact ref colgante | rechazar proposal de práctica | Project IR/practice aceptado |
| resultado fuera del frontier | fallar pair reconciliation | job y requirement reconciliados |
| recomputación sin cambio de hash | detener ciclo | nueva evidencia externa |
| presupuesto o intento agotado | detener y reportar gap | nueva autoridad o presupuesto explícito |

## Definición de progreso

El progreso no se mide por número de páginas, oportunidades ni dossiers. Se mide por:

- reducción de unknowns relevantes sin pérdida de provenance;
- requisitos con evidencia localizada y versionada;
- contradicciones detectadas antes de producto;
- latencia y costo de cerrar un hard gate;
- cero promociones indebidas;
- productos recomputados solo cuando cambia su evidencia;
- y capacidad de transferir el mismo ciclo a otro caso sin modificar el núcleo.

Hasta completar los gates reales, MAK posee contratos aceptados y un piloto informativo; no posee una vigilancia-to-submission autónoma ni un backend externo declarado ready por esta tarea.
