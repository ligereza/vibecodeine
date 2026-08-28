# LUNA-WORLD: teoría de sistemas del acoplamiento MAK–mundo

## Tesis

MAK debe entenderse como un sistema abierto adaptativo de producción cultural con memoria epistémica. Su función no es “encontrar convocatorias” ni “ordenar un archivo” como tareas aisladas. Su función es transformar perturbaciones del mundo —convocatorias, cambios de bases, fechas, políticas, publicaciones, respuestas y resultados— en diferencias verificables dentro de una memoria de evidencia; convertir esas diferencias en posibilidades condicionadas por la práctica real; producir investigación y artefactos útiles; y aprender de resultados externos sin convertir sus propias inferencias en verdad.

La unidad mínima del sistema no es un documento ni una oportunidad. Es un ciclo trazable:

`perturbación externa -> observación -> captura versionada -> restricción -> pregunta -> investigación -> triangulación -> propuesta de evidencia -> recomputación -> producto/abstención -> resultado externo`

El [inventario operacional](inventory.json) registra los componentes y sus límites. El [hashmap de relaciones](hashmap.json) materializa nodos, enlaces, invariantes y modos de fallo. El [plan de acción](action_plan.md) convierte esta teoría en cortes ejecutables.

## 1. MAK como sistema abierto

El entorno relevante de MAK es no estacionario: las convocatorias aparecen, cambian de URL, corrigen anexos, sustituyen PDFs, alteran fechas, agregan preguntas frecuentes y expiran. También cambian las manifestaciones públicas de una obra y los resultados de una postulación. Por eso una URL estable no identifica contenido estable, un resultado de búsqueda no es una fuente y un snapshot local no prueba vigencia.

La frontera MAK–mundo tiene tres operaciones distintas:

1. **Descubrimiento:** Vigía observa cambios y propone candidatos. Su señal es útil para atención, no para verdad.
2. **Captura:** un gate acotado registra una URL, el backend usado, hashes y recibo. La captura conserva un estado del mundo; no interpreta por sí sola su significado.
3. **Investigación:** preguntas explícitas buscan cerrar requisitos o contradicciones mediante grupos de fuentes independientes. La independencia exige diversidad de origen, no multiplicidad de páginas.

Esta separación protege contra dos errores simétricos: tratar cada novedad como hecho o esperar certeza total antes de actuar. MAK responde con una tercera vía: `abstain` mantiene la incertidumbre estructurada y la convierte en una acción de información acotada.

## 2. Dos autoridades y una unión tipada

MAK opera sobre dos dominios de autoridad que no pueden fusionarse por proximidad textual:

- **Autoridad externa:** bases, anexos, FAQs, calendarios, presupuestos, criterios, restricciones y resultados publicados por una institución.
- **Autoridad de práctica:** archivos físicos, documentos nativos, versiones, componentes, export witnesses, relaciones y decisiones del artista.

Una base puede demostrar que “se exige difusión”, pero no que una obra concreta satisface ese requisito. Un archivo puede demostrar que existe un video, pero no que la convocatoria esté abierta. El único acoplamiento válido es un binding explícito entre `requirement_id` y evidencia interna con referencias de artefacto. Esta unión tipada es el punto donde MAK mide compatibilidad sin fabricar elegibilidad, autoría o identidad artística.

En términos de teoría de sistemas, la separación mantiene observables distintos. Colapsarlos destruiría identificabilidad: una salida positiva ya no permitiría saber si provino de la regla externa, de la evidencia interna o de una inferencia circular.

## 3. Estado, memoria y tiempo

El estado útil de una oportunidad no es binario. Como mínimo incluye identidad, versión documental, hash de contenido, localizador, período efectivo, confirmación, contradicciones, unknowns y relaciones con requisitos. La variable de control temporal admite estados como:

- `observed_local`: hay evidencia local versionada, pero no confirmación oficial actual;
- `current_verified`: la fuente oficial vigente fue confirmada explícitamente;
- `stale` o `unknown`: la edad, versión o período no permiten afirmar vigencia;
- `expired` o `ineligible`: la puerta falla;
- `contradicted`: dos evidencias relevantes no son reconciliables todavía.

La validez temporal no es metadata decorativa: es un gate que condiciona el fit. Una fecha no confirmada debe reducir la acción disponible, no rellenarse con una estimación. Una misma URL con hash distinto representa una nueva observación y exige reconciliación. El tiempo se modela como secuencia de snapshots inmutables, no como sobrescritura del “último dato”.

Esto convierte la memoria en un acumulador de diferencias. MAK puede responder no solo “qué dice la fuente”, sino “qué cambió, desde qué versión, con qué evidencia y qué productos deben recomputarse”.

## 4. Transformaciones y conservación semántica

Cada transformación debe ser determinista, reversible al nivel de procedencia y conservadora de incertidumbre:

- el compilador de oportunidad conserva fuente, hash, versión, localizadores, restricciones, pesos, contradicciones y unknowns;
- el fit conserva cada requirement y las celdas de evidencia que lo apoyan o dejan abierto;
- el frontier conserva la pregunta, el requirement propietario, la política de fuentes, el valor de información y `dispatch=false`;
- la triangulación conserva fuentes, hashes, licencia, apoyo, contraevidencia y pares no reconciliados;
- el retorno conserva proposals, contradicciones y unresolved sin mutar la autoridad de origen;
- el controlador conserva precondiciones, observaciones de éxito/fallo, intentos máximos y condiciones de parada.

La conservación semántica importa más que maximizar la cantidad de datos. Un scraper que descarga mil páginas pero pierde versión, licencia o vínculo con la pregunta reduce la inteligencia del sistema. Un compilador que resume bellamente pero elimina contradicciones también la reduce.

## 5. Regulación, variedad y abstención

El mundo presenta más variedad que cualquier conjunto fijo de reglas: rediseños de sitios, paywalls, PDFs sustituidos, calendarios implícitos, convocatorias multilingües, criterios con pesos parciales y fuentes que se citan entre sí. Según el principio de variedad requerida, MAK no necesita una respuesta automática para cada caso; necesita un repertorio suficiente de estados y acciones seguras.

Sus acciones de control son deliberadamente pequeñas: `observe`, `research`, `recompute`, `compile`, `wait` y `abstain`. La variedad reside también en los estados intermedios: unknown, stale, contradicted, unresolved, candidate pending ingestion. Si esos estados se reducen a éxito/fallo, el sistema pierde capacidad de regulación y comienza a inventar cierre.

`Abstain` es homeostasis epistémica: conserva la integridad del sistema cuando la evidencia no alcanza. No equivale a inacción. Debe emitir la pregunta mínima, el requisito afectado, el valor esperado de información, el costo/límite, la fuente competente y la observación que cerraría el ciclo.

## 6. Triangulación como filtro de causalidad informacional

La triangulación no cuenta URLs; estima independencia operacional. Dos páginas del mismo dominio o dos copias de un comunicado no son dos observaciones independientes. El contrato existente exige grupos de fuente explícitos y dominios distintos, además de hashes, estado de captura, licencia y referencias de evidencia.

El resultado correcto no es siempre `supported_candidate`. Puede ser `contradicted_candidate`, `mixed_conflict` o `unresolved`. La contraevidencia debe aumentar la capacidad de control, no ser promediada hasta desaparecer. Un par `job_id + requirement_id` inesperado falla reconciliación porque rompería la trazabilidad entre pregunta y respuesta.

La triangulación produce evidencia ambiental. Solo puede alimentar la memoria externa. Para entrar a práctica debe existir un contrato de alcance `practice`, artefactos ya aceptados y referencias explícitas. Esta compuerta evita que una narrativa web se convierta en historia artística por repetición.

## 7. Retroalimentación sin auto-confirmación

El bucle de retorno tiene dos tiempos:

- **bucle rápido:** nueva evidencia -> propuesta pendiente -> ingestión explícita -> recomputación de fit/producto;
- **bucle lento:** resultado externo verificado -> evaluación de atención/ranking -> política shadow entre grupos de identidad independientes.

El bucle rápido no promociona. El bucle lento no aprende verdad, autoría ni identidad. Ningún dossier generado puede ser su propio label de éxito. Una recepción externa puede indicar que cierta ruta de investigación fue útil o que una secuencia de acciones mereció atención; no demuestra que los claims del dossier sean verdaderos.

Las condiciones de parada son parte del conocimiento: un intento máximo, parada si el hash de estado no cambia, parada al agotar presupuesto y parada al cerrar el requisito. Sin ellas, el acoplamiento se transforma en scraping recurrente sin ganancia informacional.

## 8. Productos como actuadores reversibles

Portfolio, aplicación y research no deben ser silos. Son actuadores derivados de un plan común que comparte claims, activos, requisitos, privacidad, licencia e incertidumbre. Un dossier interno puede ser útil aunque la aplicación esté bloqueada. `Draftable` significa que el sistema puede compilar un borrador trazable; nunca significa publicado, enviado, elegible o premiado.

La mejor salida de MAK puede ser un producto parcial acompañado de una abstención precisa. En el piloto real ARICA/Fondart, el dossier interno fue útil mientras la aplicación permaneció bloqueada y el plan autónomo eligió investigación. Esa combinación es señal de regulación correcta, no de fracaso.

## 9. ARICA como caso; MAK como arquitectura

ARICA, MYRA y RAYU aportan evidencia de supervisión: muestran archivos reales, ambigüedad, outputs sin fuente enlazada y witnesses técnicos que no implican publicación ni autoría. Fondart aporta un caso real de oportunidad documental con hard gates, documentos y criterios. Juntos tensionan el sistema, pero no lo definen.

La arquitectura reusable usa identificadores genéricos (`opportunity_id`, `requirement_id`, `artifact_ref`, `source_group`, `job_id`) y contratos independientes del fondo o artista. Una fixture Fondart puede falsificar el contrato; no autoriza campos Fondart hardcodeados. Un witness ARICA puede cerrar un gap de práctica; no autoriza inferir que todos los archivos artísticos tienen la misma topología.

El aprendizaje reusable es la política de límites: cómo distinguir autoridades, cuándo refrescar, cómo preguntar, qué cuenta como independencia, cómo retornar evidencia y cuándo detenerse.

## 10. Hipótesis operacional propia: radar de validez diferencial

La extensión más valiosa y realizable para MAK no es aumentar el volumen de scraping, sino construir un **radar de validez diferencial** sobre los contratos existentes. Para cada oportunidad, el radar mantendría una secuencia de snapshots de fuentes oficiales, calcularía diferencias semánticas ligadas a `requirement_id`, mediría el tiempo hasta deadline y priorizaría solo capturas cuyo valor de información pueda cambiar un hard gate, una contradicción o un producto.

El radar no sería un crawler permanente ni una nueva base paralela. Sería un adaptador y una política:

1. Vigía propone una URL candidata.
2. El adaptador crea un plan de captura con `opportunity_id`, fuente oficial candidata y licencia por revisar.
3. Una captura autorizada produce receipt y hashes.
4. El compilador compara la nueva versión con la anterior por requisito.
5. El frontier prioriza cambios con impacto observable: vigencia, deadline, elegibilidad, presupuesto, documentos o pesos.
6. La triangulación busca confirmación independiente solo cuando la fuente oficial es ambigua o contradicha.
7. El retorno solicita recomputación de los productos afectados y se detiene si el hash de estado no cambia.

La métrica central sería **reducción de incertidumbre relevante por captura**, no páginas descargadas. Sus métricas auxiliares: latencia entre cambio oficial y detección, proporción de requirements con localizador, tasa de contradicciones preservadas, falsos `current_verified`, costo por hard gate cerrado y número de recomputaciones sin cambio. Esta propuesta aumenta el acoplamiento con el mundo sin debilitar los límites epistémicos de MAK.

## 11. Criterio de salud sistémica

MAK está sano cuando puede explicar, para cada acción externa propuesta:

- qué perturbación la originó;
- qué evidencia versionada la respalda;
- qué autoridad puede resolverla;
- qué requisito o contradicción afecta;
- qué cambio observable constituiría éxito o fallo;
- qué producto deberá recomputarse;
- y por qué el ciclo se detendrá.

La readiness no se deduce de la existencia de código. Se demuestra con recorridos reales acotados, hashes antes/después, reconciliación completa, salidas deterministas, consumidores reales y ausencia de promoción indebida. En esta tarea solo se preserva teoría y evidencia consultada: no se ejecutó red, no se escribió una base y no se declaró operativo ningún backend externo.
