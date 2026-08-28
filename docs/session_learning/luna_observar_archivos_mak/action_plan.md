# Plan de accion: de archivo grande a memoria, curaduria, productos y aprendizaje

## Principio de ejecucion

Continuar desde los contratos aceptados. El archivo ya tiene observer,
memoria, reconstruccion, Project IR, practice evidence, opportunity, Research,
productos y shadow learning. El siguiente avance no es otro piso ni otro
registro de departamentos: es cerrar evidencia real y repetir el mismo camino.

La prioridad es maximizar evidencia portable por unidad de riesgo. Toda accion
que lea un archivo debe ser bounded y read-only. Toda accion que escriba debe
estar limitada al artefacto de salida declarado. Ningun resultado local debe
transformarse en `current_verified`, `active`, `verified`, `published` o
`training_permitted=true` sin su gate independiente.

## Objetivos

### O1. Hacer observable cualquier archivo grande sin destruir identidad

Usar `mak-archive-observation-batch-v1` como frontera universal para roots
explicitos. Medir entradas, bytes cuando sean legibles, metadata, errores,
symlinks, sidecars y secuencias. Retener artifacts fisicos y content IDs
separados. Ejecutar por tandas con include/exclude/max_files cuando el volumen
lo exija.

### O2. Convertir observacion en memoria reproducible

Ingresar solo batches validados en las tablas append-only de
`archive_memory_v2_*` o un SQLite temporal para pruebas. Replay debe devolver
el mismo estado semantico, permitir incremental add/change/remove y no mutar
fuentes ni snapshots previos.

### O3. Reconstruir unidades y relaciones sin convertir estructura en verdad

Aplicar Stage 2A-2D y sus evaluadores independientes. Mantener candidates,
alternatives, evidence_for/evidence_against, missing_evidence,
ambiguous/unassigned y dependencies. Prohibir el uso de `content_id` como
endpoint y el colapso de duplicados exactos.

### O4. Proyectar practica y oportunidad con dos autoridades separadas

Consumir Project IR aceptado para producir `mak-practice-evidence-state-v1`.
Consumir documentos externos para producir `mak-opportunity-constraints-v1`.
Unir ambos solo por `requirement_ids` o `supports` declarados explicitamente.
Una copia local de convocatoria sigue `observed_local/unconfirmed` hasta
actualizacion oficial triangulada.

### O5. Generar productos internos portables

Usar un plan comun para portfolio, application y research. La curaduria puede
ordenar provisionalmente programas y atoms, pero no cambia claim status.
Assets privados, raw, sin licencia o con provenance no resoluble quedan fuera
del public manifest. Un dossier `draft_only` puede ser valioso sin ser
publicable.

### O6. Aprender solo de outcomes externos verificables

Compilar episodios y comparar baseline/candidate solo con receipt, binding,
hashes y validacion externa. Usar grupos estables para holdout. Permitir
features exportables de ranking, attention, VOI y query selection, pero
mantener shadow-only y prohibir truth, authorship, identity, claim_status y
artistic_worth.

## Dependencias existentes

| Dependencia | Uso | Condicion de reuse |
|---|---|---|
| `archive_observer.py` | scan fisico | root y archive_id explicitos; no follow symlinks por defecto |
| `archive_memory.py` + `LearningStore` | snapshots/replay | append-only; SQLite temporal para smoke |
| `project_reconstruction.py` | unidades y reglas inversas | leer indice read-only; no convertir labels SSD en hechos |
| `reconstruction_adapter.py` + `project_ir.py` | Project IR portable | `portable_ssd_index`, `review_required`, unknowns explicitos |
| `practice_evidence_state.py` | lado interno | solo campos evidence-bearing; conservar refs fisicos y gaps |
| `opportunity_constraints.py` | lado externo | source validity separada de fit |
| `research_evidence_triangulation.py` | refresh y claims externos | source groups independientes; sin promotion |
| `portfolio_dossier.py` y plan comun | dossier/productos | no silos de application/portfolio; asset privacy/licence gates |
| `product_learning.py` | shadow learning | outcomes externos, holdout y training false |
| C05/C06 witnesses | primer puente tecnico real | solo eventos tipados, nunca entrega/autoria |

Hub, Copilot, Research runtime, Conductor, DB de produccion y servicios de red
son consumidores opcionales. Una falla heredada se registra como boundary de
capacidad; no justifica reparar maquinaria legacy ni duplicar su router.

## Gates de seguridad y aceptacion

### Gate G1: observacion fisica

- `validate_batch` pasa fail-closed.
- artifacts ordenados por `relative_path`, IDs unicos y JSON sin claves
  duplicadas.
- dos roots absolutas con el mismo contenido relativo producen el mismo
  `snapshot_id`.
- roots con `archive_id` distintos no comparten artifact IDs.
- symlinks, errores y especiales aparecen con `sha256=null` cuando corresponde.
- max-files declara limite y no finge cobertura total.
- hashes y mtimes de la fuente son iguales antes y despues.

### Gate G2: memoria e incrementalidad

- mismo batch puede reingresarse sin conflicto.
- add/change/remove coincide exactamente por path.
- old snapshot y prior batch quedan intactos.
- exact duplicates conservan un artifact state por physical ref.
- `replay_hash` coincide y `change_set` no se interpreta como transformacion.

### Gate G3: reconstruccion

- cada endpoint semantico resuelve `artifact_ref` del archive correcto.
- no hay content endpoint, cross-archive ref ni self-edge no permitido.
- candidates estan ordenados y sus IDs son recomputables.
- relation inverses son correctas.
- units balancean assigned + ambiguous + unassigned = total sin duplicados.
- dependencies no se vuelven members ni proyectos automaticamente.
- truth promotions = 0.

### Gate G4: epistemologia

- Project IR es `candidate`, `unknown` o `review_required` salvo evidencia
  independiente que autorice otra cosa.
- practice claims solo son `supported` con evidence refs explicitos.
- requirement IDs se preservan solo cuando vienen declarados.
- source validity `observed_local`, `unknown` o `stale` produce abstention.
- research sin claims extraidos produce unresolved; no produce practice claim.

### Gate G5: producto

- portfolio/application/research derivan del mismo plan.
- `rank` conserva orden estrategico; no se inventa rank para research-first.
- `documented_fact` exige supported claim; binding sin claim queda candidate.
- candidate/unknown atoms y gaps siguen visibles.
- asset manifest contiene solo physical artifact refs permitidos por licencia y
  privacidad; observation/candidate refs quedan como provenance no publicable.
- publication, export, submission y promotion quedan false/none.

### Gate G6: aprendizaje

- episodios open/abstain/unresolved no son negativos.
- solo outcomes externos con receipt/binding, hashes validos y validation pasan.
- split por `identity_group`, fuera del feature set; holdout independiente.
- si no hay minimo de examples/groups/holdout: `abstain`, `shadow-only`.
- señales prohibidas producen invalidacion del lote.
- no se activa policy ni se escribe LearningStore de produccion.

## Metricas

Las metricas deben medir trazabilidad y abstencion, no cantidad de obras
declaradas.

| Metrica | Definicion | Umbral inicial |
|---|---|---|
| `source_integrity` | hashes fuente antes/despues sin diferencia | 100% en cada smoke |
| `replay_determinism` | igualdad de snapshot/replay hash bajo raiz equivalente | 100% |
| `physical_ref_coverage` | entradas representadas como artifact o error | 100% de la ventana observada |
| `duplicate_preservation` | duplicados exactos que mantienen refs fisicos distintos | 100% |
| `incremental_balance` | paths added + changed + unchanged + missing sin intersecciones | 100% |
| `relation_falsification` | adversarial refs rechazadas y no reparadas silenciosamente | 100% |
| `unit_conservation` | assigned + ambiguous + unassigned = total, loss=0 | 100% |
| `provenance_retention` | claims/units/assets con evidence/provenance que sobreviven cada proyeccion | 100% o gap explicito |
| `false_green_rate` | productos que pasan un gate con fuente/binding invalido | 0 |
| `abstention_recall` | casos con evidencia insuficiente que permanecen abstain/unknown | maximizar; nunca penalizar |
| `public_leakage` | refs privados/raw/no licenciados en salida publica | 0 |
| `learning_leakage` | grupos compartidos entre train y holdout | 0 |
| `verified_learning_examples` | episodios externos con validacion y binding completos | reportar; no forzar minimo |

## Primer corte ejecutable

### Corte 1: cerrar dos gaps reales del piloto

1. Ejecutar el job de refresh `source-validity:<opportunity_id>` para el
   corpus Fondart mediante el camino general bounded de Research. No usar la
   query vegetal legacy ni declarar vigente la copia local por su sola
   existencia.
2. Triangular la captura con grupos independientes, hashes raw/text, licencia
   y estado de captura. Si no hay confirmacion suficiente, conservar
   `unresolved` y source validity no confirmada.
3. Convertir los recibos tecnicos ya existentes C04-C06 a la forma aceptada de
   practice evidence. Mantenerlos como evidencia tecnica de uso/exportacion,
   no como evidencia web, autoria o sentido artistico.
4. Recalcular desde fit usando el mismo snapshot Project IR/practice del piloto.
   Comparar gaps, claims, dossier, application y autonomy plan con el baseline.
5. Guardar salidas solamente en `/tmp` o en un output explicitamente autorizado;
   comparar hashes de las 14 fuentes ARICA declaradas.

### Resultado esperado

El corte es exitoso si agrega evidencia concreta, reduce gaps justificados o
mejora la siguiente probe sin aumentar false-green. Puede terminar en
abstention. No se exige que Fondart pase a `current_verified`, que el dossier
publique, que la aplicacion se habilite o que el aprendizaje produzca policy.

## Horizonte por iteraciones

### Iteracion A: volumen y portabilidad

Probar roots pequenos y medianos de ARICA, MYRA, RAYU y una superficie ISKVW
sin cambiar el observer. Generar fixtures con duplicados exactos, paths que
cambian bytes, symlinks, errores, sidecars, secuencias y manifests. Reportar
distribucion de candidate/unassigned, no convertirla en gold truth.

### Iteracion B: calidad de evidencia

Enlazar witnesses nativos y outputs reales solo cuando exista una cadena
tecnica completa. Para C05/C06 mantener un tipo `exports_to` acotado. Para
public manifestations exigir un witness adicional, no inferirlo desde el
nombre del output.

### Iteracion C: curaduria portable

Usar un gold set ciego y pequeno del artista para evaluar top-k relation
candidates y secuencias. Medir precision/recall como diagnostico, nunca como
permiso para promoción automatica. Penalizar especialmente una relacion
inventada aunque mejore recall.

### Iteracion D: productos y aprendizaje

Solo despues de recibos externos reales comparar ranking/attention/VOI con
baseline determinista. Mantener training false hasta que existan ejemplos y
holdout independientes. Un resultado pequeno es preferible a una policy
entrenada con drafts propios.

## Riesgos pendientes y stop conditions

- Si el source validity oficial no se puede confirmar, detener el intento de
  fit positivo y registrar `observed_local/unconfirmed`.
- Si C04-C06 no tienen bindings suficientes al artifact_ref canonico, mantener
  el gap y no reconstruirlo por filename.
- Si un downstream exige Hub, DB, red o rutas privadas para funcionar, marcarlo
  optional-capability boundary y continuar con la proyeccion pura.
- Si aparece un segundo registry, router o learning bridge, detener y reutilizar
  los contratos existentes.
- Si una prueba verde depende de un fixture que inventa readiness, reemplazarla
  por un caso local observado o marcarla como fixture-only.
- Si se pierde un evidence_ref, un physical_ref o una alternativa al serializar,
  bloquear la integracion aunque el producto se vea mas limpio.

## Criterio de finalizacion

El plan no termina cuando aparecen mas candidatos o un dossier bonito. Termina
cuando el corte ejecutable tiene comandos y hashes reproducibles, fuentes
intactas, contratos validados, consumers opcionales bien delimitados, gaps
explicitos y ninguna promocion no respaldada. El siguiente paso entonces es
cerrar la proxima evidencia concreta, no inventar otra capa arquitectonica.
