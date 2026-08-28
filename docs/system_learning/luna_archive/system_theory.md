# Teoría de sistemas de LUNA-ARCHIVE

## Tesis

MAK puede hacerse portable a cualquier archivo artístico si conserva cuatro cantidades a través de cada transformación: identidad, procedencia, incertidumbre y significado. La portabilidad no consiste en generalizar nombres de carpetas ni en trasladar reglas de ARICA, MYRA, RAYU o ISKVW. Consiste en mantener invariantes comprobables mientras cada archivo aporta su propia evidencia.

El sistema no “descubre la verdad del artista”. Construye una memoria de evidencia que permite formular, falsar y revisar hipótesis sin borrar el estado desconocido. Curatoria, Portfolio, Postulación y Research son consumidores diferentes de un estado común; ninguno adquiere autoridad sobre la fuente física por compilar un producto convincente.

La topología indexada de esta teoría está en `hashmap.json`; el inventario de contratos y huecos está en `inventory.json`; la secuencia de ejecución está en `action_plan.md`.

## 1. El sistema y sus autoridades

Sea un archivo artístico observado en un instante:

\[
A_t = (T, R, S_t, F_t)
\]

donde `T` es el tenant o ámbito estable, `R` es la identidad del archivo, `S_t` es la identidad del snapshot y `F_t` es el conjunto de referencias físicas observadas. `T` y `R` agrupan continuidad; `S_t` distingue estados temporales. Un cambio de snapshot no debe inventar un nuevo artista, y una igualdad de contenido no debe fusionar dos entidades físicas.

MAK opera con autoridades separadas:

- El archivo físico autoriza afirmaciones sobre bytes, estructura y observaciones realizadas.
- El baseline de `/home/mak/flujo` autoriza contratos de transformación y validación, no hechos artísticos.
- Un documento de oportunidad autoriza requisitos, plazos y elegibilidad dentro de la vigencia de su fuente.
- Un recibo externo verificado autoriza un resultado acotado —por ejemplo, recepción o rechazo—, no una explicación causal ni una verdad estética.
- `/home/mak/WIN` conserva historia; su existencia no prueba integración operativa.

Estas autoridades pueden relacionarse, pero no sustituirse.

## 2. Conservación de identidad

La unidad mínima es una referencia física contextualizada:

\[
I_f = (T, R, S_t, artifact\_ref)
\]

Un SHA-256 agrega una propiedad de contenido, no reemplaza `I_f`. Si dos referencias tienen el mismo hash, el sistema puede afirmar equivalencia de bytes dentro del alcance observado. No puede afirmar que son la misma obra, el mismo proyecto, la misma versión significativa, el mismo rol o la misma manifestación.

La reconstrucción conserva una partición total:

\[
F_t = Assigned \;\dot\cup\; Ambiguous \;\dot\cup\; Unassigned
\]

Cada `artifact_ref` aparece exactamente una vez en esa frontera. Los `dependency_refs` permanecen separados de los miembros de la unidad. Esta separación impide dos errores sistémicos: absorber una biblioteca compartida como identidad del proyecto y convertir un límite de búsqueda en una negación de pertenencia artística.

La identidad de proyecto es provisional mientras su Project IR sea `candidate` o `unknown`. Renombres, movimientos y snapshots futuros requieren relaciones explícitas y evidencia; no se resuelven por semejanza textual.

## 3. Conservación de procedencia

Una afirmación utilizable se modela como:

\[
E = (subject, predicate, value, evidence\_refs, method, scope, status)
\]

Toda transformación `f` debe conservar referencias resolubles:

\[
provenance(f(E)) \supseteq provenance(E)
\]

Si la transformación no puede conservarlas, su salida debe ser `unknown` o un hueco explícito. La procedencia incluye la fuente física, el snapshot, el método de observación, la versión de herramienta cuando existe y la relación entre el claim y sus pruebas.

La memoria de archivo es temporal y append-only: permite replay determinista de lo observado, no reconstruye observaciones ausentes. Por eso “no apareció en el scan” significa únicamente “no observado dentro del root, snapshot y límites declarados”.

En el cruce con oportunidades hay dos namespaces de evidencia:

- Evidencia de práctica: artefactos y receipts vinculados al archivo.
- Evidencia de oportunidad: documentos oficiales o fuentes ambientales que describen requisitos y vigencia.

El join válido requiere `requirement_id` explícito en la evidencia interna. Un párrafo del fondo no puede reutilizarse como prueba de que el artista cumple ese párrafo.

## 4. Conservación de incertidumbre

La incertidumbre no es ruido residual; es estado operativo. MAK conserva al menos:

- `supported`: existe evidencia explícita suficiente dentro del contrato.
- `candidate`: existe una hipótesis trazable que necesita falsación o evidencia adicional.
- `unknown`: el contrato no permite afirmar esa dimensión.
- `contradicted` o `rejected`: evidencia o evaluación invalida una posibilidad concreta.
- `abstain`: el control impide decidir, aunque el pipeline siga siendo funcional.

No existe una promoción automática basada solo en score:

\[
score(x) \not\Rightarrow supported(x)
\]

Los scores pueden ordenar sondas o acotar candidatos. No aportan semántica, autoría ni intención. Tampoco existe la equivalencia `unknown = false`. Un resultado abierto no se convierte en fracaso y una abstención no es una etiqueta negativa.

La evolución válida es aditiva: nueva evidencia puede provocar recomputación, contradicción o una propuesta de promoción. La promoción exige un gate independiente y queda fuera del research return, del dossier y del plan autónomo.

## 5. Conservación de significado

El significado permitido de una salida no puede exceder la unión de significados apoyados por sus entradas y por el contrato de transformación:

\[
Meaning(f(X)) \subseteq SupportedMeaning(X) \cup DeclaredSemantics(f)
\]

Esta ley bloquea inferencias frecuentes:

- Un `.blend`, `.aep`, `.uproject` o carpeta no prueba autoría ni intención.
- Un export técnico no prueba entrega final, publicación ni manifestación pública.
- Una secuencia de frames no prueba por sí sola su proyecto fuente.
- Un nombre común o ancestro compartido no crea una obra o serie.
- Una narrativa fluida generada por un dossier no añade claims a la práctica.
- Un outcome exitoso puede enseñar prioridad o ranking, no verdad artística.

Cuando un rol cambia —fuente, componente, export, manifestación, publicación— debe existir una relación tipada y evidencia específica. La ausencia de esa relación mantiene roles coexistentes y desconocidos en vez de colapsarlos.

## 6. Circulación por capas

La cadena aceptada puede expresarse así:

\[
A_t \rightarrow O_t \rightarrow M_t \rightarrow R_t \rightarrow U_t \rightarrow P_t \rightarrow S_t
\]

- `O_t`: observaciones mecánicas y receipts.
- `M_t`: memoria inmutable y replay.
- `R_t`: relaciones candidatas.
- `U_t`: unidades provisionales con partición total.
- `P_t`: Project IR compartido.
- `S_t`: estado de práctica basado solo en evidencia.

En paralelo, una oportunidad sigue su propia autoridad:

\[
D_t \rightarrow Q_t
\]

donde `D_t` es el corpus documental y `Q_t` sus constraints con vigencia. El fit no es una fusión de bases, sino una relación explícita:

\[
Fit_t = Join_{requirement\_id}(S_t, Q_t)
\]

Desde allí, MAK puede construir posibilidades provisionales, falsarlas, ordenar huecos y producir jobs no despachados. Los resultados triangulados regresan como propuestas aditivas. El bucle es:

\[
gap \rightarrow planned\_job \rightarrow receipt \rightarrow triangulation \rightarrow evidence\_proposal \rightarrow recompute
\]

No existe la transición implícita `receipt -> truth`.

## 7. Productos como vistas coordinadas

Portfolio, Postulación y Research no deben mantener verdades independientes. Derivan de un `product_plan` común que conserva vínculos entre claims, programas, assets, requirements, privacidad, licencias y gaps.

Un dossier interno puede ser `draftable` con assets privados y huecos explícitos. Eso es valioso: ofrece una superficie curatorial inspeccionable sin declarar contenido público. Una postulación puede permanecer bloqueada mientras el dossier interno existe. Un research brief puede ser draftable con jobs `planned_not_dispatched`.

Los verbos de control son distintos:

- `compile`: transformación local y determinista.
- `draft`: producto revisable.
- `publish` o `submit`: acción externa, nunca implicada por draftability.
- `dispatch`: ejecución de investigación, deshabilitada por defecto.
- `promote`: cambio epistemológico, siempre explícito e independiente.

## 8. Aprendizaje y autonomía finita

El aprendizaje aceptable usa episodios con resultados externos verificados y grupos de identidad estables. Sus targets permitidos son atención, ranking y selección de próxima sonda. Sus targets prohibidos son autoría, identidad artística, intención y verdad factual.

Con un resultado abierto:

\[
label = abstain(outcome\_open\_not\_negative)
\]

Con insuficientes grupos independientes o sin holdout, el sistema no promueve política. El plan autónomo puede usar una evaluación shadow para prioridad, pero mantiene controles explícitos: intentos finitos, detención sin cambio de hash, detención al agotar presupuesto, sin loops, sin publicación, submission, dispatch, promotion ni training.

La autonomía útil no es libertad para actuar; es capacidad de elegir la próxima reducción de incertidumbre con un criterio observable y un límite de ejecución.

## 9. Portabilidad

MAK será portable cuando una implementación nueva necesite declarar parámetros del archivo —roots, adapters, herramientas disponibles, políticas de privacidad y namespaces— sin modificar las invariantes. Un caso no puede introducir una excepción semántica oculta.

La portabilidad debe probarse en tres escalas:

1. Conformidad de contrato: entradas adversariales producen errores o abstenciones deterministas.
2. Transferencia entre archivos: dos o más archivos independientes conservan identidad, partición, procedencia y gaps sin reglas por nombre.
3. Transferencia temporal: snapshots sucesivos distinguen continuidad, cambio y ausencia observacional.

Una suite verde sobre fixtures prueba el contrato, no readiness universal. Un piloto real prueba una trayectoria acotada, no generalización. La generalización exige archivos holdout, métricas por invariante y revisión de los falsos verdes.

## 10. Lectura del piloto actual

El piloto ARICA/Fondart valida precisamente el valor de abstener: observó 417 artefactos y produjo un Project IR y practice state válidos, pero encontró cero claims supported/candidate, cero assets públicos y una fuente de oportunidad local no confirmada. El dossier interno fue útil; la aplicación quedó bloqueada; Research recibió una acción acotada. El sistema conservó nueve gaps en vez de redactar una identidad autoral.

Eso no demuestra que MAK esté listo para cualquier archivo. Demuestra una propiedad más importante: ante datos reales insuficientes, las capas permanecen coordinadas sin fabricar completitud.

## 11. Principio rector

El objetivo de MAK no es maximizar respuestas. Es maximizar circulación útil de evidencia bajo conservación semántica:

\[
Utility = information\_gain - false\_promotion - irreversible\_action
\]

El mejor próximo paso es el que reduce un gap explícito, produce una señal verificable y deja intactas las fuentes. Si no cambia la evidencia o amenaza una autoridad, el sistema se detiene o cambia de ruta.
