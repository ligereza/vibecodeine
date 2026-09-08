# Wachuma leído por su público: procedencia visible en un jardín digital

**Convocatoria:** Fondart Nacional — Línea Investigación — Concurso General 2027
**Cierre:** **lunes 14 de septiembre de 2026, 15:00** hora de Santiago, según Rex 2596, que amplía el plazo de esta línea (Res. Ex. 2166) en su tabla de ámbito nacional. No aplica a responsables de Arica y Parinacota, Tarapacá, Antofagasta ni Atacama. El PDF de bases no trae fecha —verificado sobre sus 38 páginas— pero sí fija la hora: las 15:00 de Santiago del último día hábil.
**Solicitado al fondo:** $12.000.000 CLP
**Duración:** 12 meses

> Borrador generado desde las bases y reescrito el 2026-09-07 sobre su caso real. Las secciones marcadas `[FALTA]` siguen vacías: la herramienta no escribe el texto de la postulación.
>
> Reemplaza al borrador «Jardines interpretativos», que postulaba el método sin caso. Jardines es el método; Wachuma es el caso. Las bases admiten **una sola postulación por línea** (I.4), así que existe este expediente y no los dos.

> **Estado:** el Avance de Investigación y el Plan de Actividad de Transferencia
> están redactados en su versión completa, maquetados en tamaño carta/Arial 12
> y exportados a PDF: `FONDART_2027_INVESTIGACION_WACHUMA_ANEXOS/AVANCE_DE_INVESTIGACION.{md,pdf}`
> y `.../PLAN_ACTIVIDAD_TRANSFERENCIA.{md,pdf}`. La extensión del Avance (15
> páginas tamaño carta) fue verificada con `pdfinfo` el 2026-09-07. Dos
> subsecciones de su sección 4 fueron redactadas por un agente Claude ese día
> a partir de evidencia del repositorio WACHUMA para completar esa extensión, y
> están marcadas dentro del propio documento como borrador pendiente de
> aprobación humana -- revisarlas antes de dar el Avance por cerrado. Lo demás
> pendiente de revisión humana es lo que ningún documento puede resolver por su
> cuenta: identidad del responsable, cotizaciones y la confirmación final de la
> autorización ministerial de difusión (ver «Aporte del operador» al final).

## Dónde está el puntaje

| Criterio | Pondera | Secciones que lo alimentan |
| --- | ---: | --- |
| IMPACTO POTENCIAL DE LA ACTIVIDAD TRANSFERENCIA | 40% | `plan_transferencia`, `publicos`, `presupuesto`, `compromisos_difusion` |
| CALIDAD | 30% | `avance_investigacion`, `estudio_campo`, `metodologia`, `fuentes`, `compromisos_difusion` |
| CURRÍCULO | 20% | `equipo`, `trayectoria_responsable` |
| VIABILIDAD | 10% | `objetivos`, `actividades`, `metodologia`, `cronograma`, `presupuesto` |

## Fundamentación

*Se evalúa en: sin criterio directo — peso total 0%*

<!-- Problema, relevancia y aporte al campo disciplinar. -->

Una representación de conocimiento —una ficha, un mapa de relaciones, una escena tridimensional— puede resultar convincente sin que quien la recorre sepa qué proviene de una fuente verificable, qué es una interpretación editorial y qué es apenas un marcador de trabajo en curso. Esta investigación no busca demostrar una tesis botánica: busca caracterizar cómo un público adulto de artes visuales distingue hecho de interpretación cuando esa distinción puede o no descubrirse, y qué ocurre con esa distinción cuando una representación visual particularmente convincente —una escena tridimensional— compite con el juicio evidencial. El proyecto se inscribe en el Grupo A, en nuevos medios, y en la temática autorizada de caracterización de públicos y consumo cultural.

El estímulo del estudio no se construye desde cero ni como maqueta de laboratorio: es Wachuma, un atlas biológico y jardín digital ya existente sobre *Echinopsis pachanoi*, cuyo modelo de datos separa por esquema —no por intención editorial— qué clase de cosa dijo algo (`sourceType`) de qué clase de afirmación es (`assertionType`), y marca cada representación tridimensional del organismo con el rótulo `procedural-interpretation`, presente en cuatro esquemas distintos del sistema, que impide leer un render generado proceduralmente como una reconstrucción evidencial. Al 7 de septiembre de 2026 el corpus registra 28 fuentes, 67 registros de origen, 69 filas de procedencia y 53 revisiones de esos registros, sobre 7 taxones y 7 ejemplares. Esa arquitectura, y no una promesa, es lo que permite mostrarle a un público una lectura y su origen —o su falta— al mismo tiempo.

Lo que Wachuma todavía no tiene es contenido curado en su totalidad ni una superficie pública completa: hay una ficha de especie real y el resto de sus piezas de contenido (ficha cultural, escena tridimensional, una de las dos guías de cultivo) están marcadas `demo` o `restricted` en su propio esquema. Esa condición mixta —parte real, parte declaradamente demostrativa— no es un obstáculo para el estudio: es su segunda fuente de evidencia, porque permite preguntarle a un público real si distingue lo real de lo demostrativo cuando se le da la oportunidad de descubrirlo, y qué pasa cuando no se le da. El objeto evaluable no es la infraestructura sino el estudio de campo: qué distingue, qué rechaza y qué da por hecho un público cuando la procedencia y el estatuto epistémico de lo que ve están, o no están, a la vista.

## Objetivos

*Se evalúa en: VIABILIDAD 10% — peso total 10%*

<!-- Objetivo general y específicos, con logros observables. -->

Objetivo general:
Caracterizar cómo un público adulto vinculado a las artes visuales distingue hecho documentado de interpretación al recorrer una pieza de conocimiento biocultural digital, y cómo cambia esa distinción cuando la procedencia y el estatuto epistémico de cada afirmación son explorables frente a cuando no lo son.

Objetivos específicos:
1. Delimitar, dentro del corpus real y demostrativo de Wachuma, un conjunto acotado de contenidos (ficha de especie, guía de cultivo, ficha cultural, escena tridimensional) que permita manipular la disponibilidad de procedencia sin alterar el contenido mostrado.
2. Implementar dos condiciones de exploración —procedencia cerrada y procedencia abierta— como una capa de interacción reproducible sobre la interfaz pública existente, sin modificar el modelo de datos ni el estatus real de ningún registro.
3. Diseñar y aplicar un protocolo de campo (cuestionario de entrada, tarea de clasificación con confianza, observación con pensar en voz alta, entrevista breve, ficha de salida comparativa) con consentimiento informado, anonimización y posibilidad de retiro.
4. Analizar las diferencias, dentro de cada participante, en la clasificación de afirmaciones (hecho / interpretación / no sé), en las decisiones de aceptar-rechazar-dejar abierta una relación, y en las verbalizaciones de duda o confianza, entre ambas condiciones y entre las dos rutas de entrada (recorrido espacial/3D frente a ficha convencional).
5. Transferir el protocolo y sus resultados —incluida la posibilidad de un resultado negativo— mediante una actividad de transferencia y un informe que distinga hallazgo de límite.

## Actividades

*Se evalúa en: VIABILIDAD 10% — peso total 10%*

<!-- Actividades de investigación y productos que cumplen los objetivos. -->

Fase 1 — delimitación (abril-mayo de 2027): confirmar el conjunto acotado de contenidos, verificar las fuentes primarias, y producir los instrumentos de campo (consentimiento, cuestionario de entrada, tarea de clasificación, guía de entrevista, ficha de salida).
Fase 2 — implementación de las dos condiciones (mayo-junio): construir la capa de interacción que abre o cierra el acceso a fuente/tipo de aserción/rótulo `procedural-interpretation` sobre la interfaz pública existente, sin tocar el modelo de datos ni el estatus real de ningún registro.
Fase 3 — prototipo y piloto (julio-agosto): piloto técnico de las dos condiciones y de las dos rutas de entrada, y sesiones de campo con participantes adultos (24 a 30 personas).
Fase 4 — análisis y curaduría (septiembre-octubre): codificación cualitativa y conteos descriptivos por condición y por ruta de entrada; conservar resultados inciertos o negativos; ajustar textos y visualización.
Fase 5 — transferencia y cierre (noviembre de 2027-marzo de 2028): realizar la actividad de transferencia, publicar el protocolo sin corpus privado, editar el avance/informe final y ordenar evidencias.

## Estudio de campo

*Se evalúa en: CALIDAD 30% — peso total 30%*

<!-- Diseño del levantamiento de datos, participantes, instrumentos y resguardos. -->

El estudio de campo se centra en la temática autorizada de caracterización de públicos y consumo cultural en artes de la visualidad. Se convoca una muestra intencional de 24 a 30 personas adultas vinculadas a prácticas de arte, diseño, mediación o investigación cultural, por difusión en redes propias del campo y sin compra de audiencia ni de datos personales; el diseño y los instrumentos completos están en `AVANCE_DE_INVESTIGACION.md` §6.

Cada participante recorre el mismo conjunto acotado de contenidos de Wachuma (ficha de especie real, guía de cultivo real, ficha cultural demostrativa, escena tridimensional) en dos condiciones contrabalanceadas —procedencia cerrada y procedencia abierta— y por una de dos rutas de entrada asignadas al azar —recorrido espacial/3D o ficha convencional—, pudiendo aceptar, rechazar o dejar abierta cada relación mostrada. Ninguna ubicación de ejemplar se usa ni se muestra. Se aplican cuestionario de entrada, observación estructurada con pensar en voz alta, una tarea de clasificación de afirmaciones (hecho / interpretación / no sé, con confianza 1-5) y una entrevista breve por condición, más una ficha de salida comparativa. Se registran sólo decisiones, tiempos aproximados, clasificaciones y verbalizaciones necesarias para el análisis; no se copian archivos personales ni se publican datos identificables. La comparación entre la condición abierta y la cerrada es lo que permite observar qué aporta hacer explorable la trazabilidad, y no sólo mostrarla de antemano.

El protocolo incluye consentimiento informado, retiro voluntario, anonimización, resguardo local y una devolución agregada. Por diseño, cada participante no es informado de antemano de qué piezas son reales y cuáles demostrativas —eso es precisamente lo que se le pide reconstruir—, y recibe una devolución completa al cierre de cada sesión; esta reserva de información acotada es una práctica establecida en investigación de interpretación y no compromete el consentimiento, que cubre con precisión qué se observa y qué no se conserva. Las hipótesis se tratan como hipótesis y el comportamiento del modelo como resultado simulado, nunca como evidencia del mundo botánico o de la experiencia de un público completo.

## Avance de Investigación

*Se evalúa en: CALIDAD 30% — peso total 30%*

<!-- Problema, objeto de estudio, preguntas o hipótesis, metodología, marco teórico, estado del arte y referencias; el anexo oficial pide 15 páginas tamaño carta. -->

**El Avance de Investigación completo (15 páginas, Arial 12) ya está redactado y maquetado**: `FONDART_2027_INVESTIGACION_WACHUMA_ANEXOS/AVANCE_DE_INVESTIGACION.md` (editable) y su PDF correspondiente. Este campo resume su contenido para mantener la coherencia del expediente; el documento oficial es el que se adjunta al FUP.

Problema: una pieza digital que representa conocimiento puede resultar convincente sin que quien la recorre sepa qué proviene de una fuente verificable, qué es una interpretación editorial y qué es un marcador de trabajo en curso. Esa opacidad es un problema de conocimiento público, no un defecto menor de diseño.

Objeto de estudio: la relación entre un público de artes visuales y una pieza de conocimiento biocultural cuya procedencia y estatuto epistémico pueden o no ponerse a la vista. El caso —Wachuma, *Echinopsis pachanoi*— está fijado de antemano y no se elige durante la ejecución.

Pregunta: ¿cambia la forma en que un público adulto de artes visuales distingue un hecho documentado de una interpretación cuando puede descubrir activamente la procedencia y el estatuto epistémico de lo que observa, frente a la misma pieza sin ese acceso? ¿Y en qué medida, sin ese acceso, la verosimilitud de una escena tridimensional (`procedural-interpretation`) hace que se lea como un hecho? La pregunta secundaria —qué aporta recorrer un organismo digital frente a leer una ficha convencional— queda como dimensión de observación (ruta de entrada), no como hipótesis central.

Hipótesis de trabajo: H1, hacer explorable la procedencia y el estatuto epistémico aumenta la proporción de clasificaciones correctas y el número de dudas informadas, respecto de la misma pieza sin esa capa. H2, sin acceso a la procedencia, la escena tridimensional tiende a clasificarse como hecho con mayor frecuencia y confianza que cuando el rótulo `procedural-interpretation` es visible. El Avance especifica, en su §2, qué tres resultados obligarían a revisar ambas hipótesis.

Metodología: estudio de campo intra-sujeto (dos condiciones: procedencia cerrada / procedencia abierta, orden contrabalanceado) con una dimensión de observación entre-sujeto (ruta espacial/3D frente a ficha convencional), sobre un corpus real y demostrativo ya existente —no construido para la ocasión—: ficha de especie real, guía de cultivo real, ficha cultural `demo`, escena tridimensional `restricted`. Instrumentos: cuestionario de entrada, observación con pensar en voz alta, tarea de clasificación con confianza, registro de decisiones de lectura, entrevista breve y ficha de salida comparativa. El detalle completo —participantes, procedimiento por sesión, consideración ética sobre la reserva de información, y plan de análisis— está en el Avance, §6.

Marco teórico y estado del arte: el proyecto articula seis líneas —el estándar de procedencia PROV-O (W3C, 2013); la Carta de Londres y su noción de *paradata* para reconstrucciones interpretativas (Denard, 2009); el heurístico de realismo en credibilidad de medios (Sundar, 2008) y el efecto de detalles seductores (Sundararajan & Adesope, 2020) como mecanismo cognitivo de riesgo; el modelo contextual de aprendizaje en museos (Falk & Dierking, 2013); *Data Feminism* (D'Ignazio & Klein, 2020) como argumento normativo; y la Encuesta Nacional de Participación Cultural (2018) como campo de públicos al que este estudio se suma sin duplicarlo—. El aspecto novedoso, desarrollado con su análisis bibliográfico completo en el Avance §5, es poner a prueba con público real, en un sistema de producción y no en una maqueta, si una arquitectura de datos que ya separa evidencia de interpretación cambia la lectura de un público cuando esa separación se hace explorable.

## Fuentes y trazabilidad

*Se evalúa en: CALIDAD 30% — peso total 30%*

<!-- Fuentes primarias/secundarias, procedencia, claims y límites de interpretación. -->

El corpus del caso ya está constituido y es consultable. Medido el 7 de septiembre de 2026 sobre la base PostgreSQL/PostGIS del proyecto:

| Tabla | Filas | Qué guarda |
| --- | ---: | --- |
| `record_provenance` | 69 | de dónde vino cada registro |
| `source_records` | 67 | el registro tal como lo entregó su fuente |
| `source_record_reviews` | 53 | la revisión humana de ese registro |
| `specimen_locations` | 42 | ubicaciones de ejemplares, **no publicables** |
| `sources` | 28 | las fuentes citables |
| `claim_sources` | 23 | qué fuente sostiene qué afirmación |
| `claims` | 21 | las afirmaciones |
| `observations` | 21 | observaciones de campo |
| `external_identifiers` | 14 | identificadores en repositorios externos |
| `growing_guide_claims` | 12 | afirmaciones de guía de cultivo |
| `taxa` / `specimens` | 7 / 7 | taxones y ejemplares |

El repositorio del caso es `github.com/ligereza/WACHUMA`, con 83 commits, esquemas de contenido vinculantes e importadores versionados. El rótulo `procedural-interpretation` —que distingue una representación 3D generada de una reconstrucción evidencial— está declarado a nivel de esquema en cuatro archivos distintos del sistema (`garden-scene`, `material-fixture`, `plant-descriptor`, `scroll-experience`), verificado el 7 de septiembre de 2026.

Lo que **no** puede afirmarse todavía, y el proyecto lo trata como trabajo por hacer y no como logro: de las piezas de contenido público usadas en el estudio, sólo `content/species/echinopsis-pachanoi.json` es material real y revisado; la ficha cultural (`content/cultures/echinopsis-pachanoi-demo.json`) y la escena tridimensional (`content/scenes/echinopsis-pachanoi-demo.json`) están marcadas `demo`/`restricted` en su propio esquema, y la guía de cultivo general (`content/cultivation-guides/echinopsis-pachanoi-general-cacti-v1.json`) es real pero de alcance institucional genérico, no un protocolo de campo propio. Esa condición mixta es corpus del estudio, no una brecha a resolver antes de empezar: el objetivo específico 1 la delimita, no la disuelve.

Cada fuente nueva tendrá URL o ruta, fecha, hash, tipo, cita y estado, según el esquema que el repositorio ya hace vinculante. Las relaciones llevarán base y confianza; una analogía no se presentará como hecho. La bibliografía teórica completa —ocho referencias, cada una con la función que cumple en el argumento— está en `AVANCE_DE_INVESTIGACION.md` §8.

## Metodología

*Se evalúa en: VIABILIDAD 10%, CALIDAD 30% — peso total 40%*

<!-- Cadena de investigación, análisis y validación; separar dato, inferencia y decisión artística. -->

El diseño intra-sujeto compara, para cada participante, la condición de procedencia cerrada con la condición abierta (orden contrabalanceado), y registra además la ruta de entrada asignada (espacial/3D o ficha convencional) como covariable descriptiva. El componente de campo tiene tres capas: (1) recorrido de la pieza bajo cada condición, con observación y pensar en voz alta; (2) tarea de clasificación de afirmaciones (hecho / interpretación / no sé, con confianza) y entrevista breve por condición; (3) ficha de salida comparativa entre ambas condiciones. El análisis combina codificación cualitativa de verbalizaciones y entrevistas con conteos descriptivos de la tarea de clasificación y de las decisiones de lectura, comparados dentro de cada participante; no se aplican pruebas de significancia estadística formal ni se generaliza una muestra intencional acotada a todos los públicos de artes visuales.

La escena tridimensional y sus interpretaciones son modelos interpretativos declarados como tales por el propio sistema (`procedural-interpretation`). El estudio no prueba crecimiento, eficacia, salud, cultivo ni equivalencia entre dominios. El piloto puede producir un resultado negativo —que la procedencia explorable no cambie la clasificación, o que la cambie para peor por sobrecarga informativa—, y esa constatación será parte del informe, no un resultado a evitar. Las decisiones de curaduría quedan separadas de la extracción automática y el corpus privado (incluidas las ubicaciones de ejemplares) permanece fuera de la publicación.

## Cronograma

*Se evalúa en: VIABILIDAD 10% — peso total 10%*

<!-- Ejecución de hasta 12 meses iniciada entre marzo y abril de 2027. -->

Abril 2027: delimitación del caso, selección preliminar de fuentes y protocolo de consentimiento.
Mayo: captura, hash y normalización del corpus; diseño de instrumentos y piloto técnico.
Junio: relaciones, contexto, primera versión del jardín y prueba interna.
Julio: convocatoria, accesibilidad y primeras sesiones de campo.
Agosto: sesiones restantes, entrevistas y consolidación de registros agregados.
Septiembre: análisis de recorridos, comparación de lecturas y revisión de la pieza.
Octubre: validación de límites, curaduría del prototipo y documentación.
Noviembre: actividad de transferencia y devolución agregada.
Diciembre: redacción del avance/informe, referencias y matriz de riesgos.
Enero 2028: edición del protocolo y documentación pública.
Febrero: revisión de evidencias, respaldos y cierre administrativo.
Marzo: entrega de resultados, archivo de auditoría y cierre del proyecto.

El inicio del 1 de abril de 2027 está dentro de la ventana de la convocatoria (1 de marzo–30 de abril) y la ejecución dura doce meses.

## Equipo de trabajo

*Se evalúa en: CURRÍCULO 20% — peso total 20%*

<!-- Responsabilidades, competencias y cartas de compromiso cuando corresponda. -->

La propuesta se presenta como persona natural responsable y, en esta versión, no declara un equipo de trabajo: la dirección, curaduría, implementación, campo, análisis y administración quedan bajo responsabilidad de quien postula. Los servicios o compras que eventualmente requieran una cotización no se convierten automáticamente en integrantes del equipo; si antes del envío se incorpora una persona con funciones de equipo, se actualizarán sus datos, cartas y presupuesto y se marcará la condición correspondiente.

Esta decisión mantiene la postulación comprobable sin inventar colaboradores. La asesoría disciplinar o de accesibilidad que resulte necesaria queda [FALTA] hasta confirmar nombre, función, disponibilidad y carta.

## Trayectoria del responsable

*Se evalúa en: CURRÍCULO 20% — peso total 20%*

<!-- Experiencia pertinente y antecedentes acreditables. -->

La evidencia técnica local muestra implementación y mantenimiento del repositorio del caso, `github.com/ligereza/WACHUMA`, con 83 commits, base PostgreSQL/PostGIS, importadores, esquemas de contenido vinculantes y un modelo de procedencia con revisión humana registrada; además de `tools/interpretive_garden_workflow.py`, el registro SQLite de procedencia y la ruta `/research-garden/` del hub. El/la responsable ha trabajado con diseño de datos, trazabilidad, curaduría de relaciones, documentación y separación entre evidencia e interpretación en MAK.

Responsable: [FALTA] nombre legal y RUT — el titular los completa directamente en el FUP. Faltan por completar: Perfil Cultura vigente (el trámite está iniciado; quedan documentos pendientes de enviar en la plataforma), domicilio y región acreditables, CV firmado y enlaces públicos vigentes que acrediten la experiencia artística y de investigación [FALTA]. Esta sección no atribuye premios, publicaciones ni selecciones que no estén documentadas.

## Presupuesto

*Se evalúa en: VIABILIDAD 10%, IMPACTO POTENCIAL DE LA ACTIVIDAD TRANSFERENCIA 40% — peso total 50%*

<!-- Gastos por actividad y funciones, con transferencia entre 5% y 10%, imprevistos hasta 2% y responsable hasta 40%. -->

Se solicita al Fondo $12.000.000 CLP, dentro del rango del Grupo A. La asignación del/de la responsable es $3.600.000 (30%); la transferencia es $600.000 (5%); los imprevistos son $240.000 (2%). Las partidas están distribuidas entre personal, operación e inversión y suman exactamente el monto solicitado.

El presupuesto es una base de trabajo para hacer comprobable la estructura, no una cotización. Antes del FUP se deben obtener cotizaciones o valores verificables, revisar contratación y obligaciones laborales, y ajustar cada partida a las horas y funciones reales. No se declara cofinanciamiento obligatorio. La compra de equipo local se justifica por el prototipo y las sesiones, y su destino posterior será continuidad del protocolo y futuras instancias de transferencia.

## Plan de Actividad de transferencia

*Se evalúa en: IMPACTO POTENCIAL DE LA ACTIVIDAD TRANSFERENCIA 40% — peso total 40%*

<!-- Contenido, metodología, formato, público, resultados esperados, impacto y alcance; mínimo una actividad presencial o virtual. -->

Se realizará al menos una actividad presencial o virtual de transferencia, en formato taller-charla de dos horas, dirigida a artistas visuales, mediadores, curadores e investigadores que trabajen con archivos o visualización.

Contenido: cómo delimitar un caso, capturar fuentes, separar claim, inferencia y metáfora, registrar relaciones y documentar una decisión curatorial. Metodología: demostración del prototipo, ejercicio guiado con una fuente, discusión de límites y entrega de un protocolo editable. Público: participantes adultos vinculados a artes visuales, nuevos medios, mediación o investigación; el número final y la organización anfitriona quedan [FALTA] hasta confirmar. Resultados esperados: que cada participante pueda identificar procedencia, incertidumbre y punto de quiebre en una interpretación y se lleve una plantilla reutilizable. Impacto: transferir un método auditable y sus límites al campo, sin presentar el modelo como conocimiento botánico ni como diagnóstico.

Se presupuestan $600.000, equivalentes al 5% del monto solicitado, dentro del rango 5–10% declarado en I.7. El plan se convertirá en el documento del Anexo N° 2 antes del envío.

## Públicos beneficiarios

*Se evalúa en: IMPACTO POTENCIAL DE LA ACTIVIDAD TRANSFERENCIA 40% — peso total 40%*

<!-- Perfil, convocatoria, número estimado y relación con el contenido. -->

El estudio se dirige a públicos adultos de artes visuales y nuevos medios: artistas, estudiantes avanzados, mediadores, curadores e investigadores. Se observarán perfiles, recorridos, preguntas, rechazos y comprensión de la procedencia; no se comprará una base de datos ni se guardarán identificadores innecesarios.

La muestra intencional, el número de sesiones y la meta de beneficiarios quedan [FALTA] hasta confirmar la convocatoria; el caso ya no condiciona esa definición, porque está cerrado. Se reportarán sólo resultados descriptivos y agregados, con consentimiento y posibilidad de retiro. La actividad de transferencia tendrá además un público profesional ampliado, que recibirá el protocolo y una explicación de sus límites.

## Compromisos de realización y/o difusión

*Se evalúa en: CALIDAD 30%, IMPACTO POTENCIAL DE LA ACTIVIDAD TRANSFERENCIA 40% — peso total 70%*

<!-- Compromisos firmados de espacios, infraestructuras o medios existentes cuando la formulación los nombre. -->

No se declara en esta versión un espacio físico o medio existente como parte de la estrategia de difusión, por lo que no se activa un compromiso externo en el verificador. El prototipo podrá circular en la ruta local `/research-garden/` y en una actividad virtual o presencial cuya organización queda [FALTA]. Si se nombra un espacio existente o una institución antes del envío, se adjuntará su compromiso firmado y se actualizarán las condiciones y documentos del proyecto.

## Riesgos, ética y límites

*Se evalúa en: sin criterio directo — peso total 0%*

<!-- Consentimiento, privacidad, derechos, seguridad y límites de la interpretación visual. -->

Riesgos y resguardos: consentimiento informado, retiro voluntario, anonimización, almacenamiento local, no publicación de archivos privados y revisión de derechos de cualquier fuente de terceros. La muestra no incluye menores ni actividades en vía pública o territorios indígenas.

Límite de publicación, explícito por ser el riesgo mayor del caso: la base contiene 42 filas en `specimen_locations`. Las ubicaciones de ejemplares **no se publican, no se muestran al público del estudio y no salen en la pieza**, ni exactas ni aproximadas ni derivables de un mapa. *Echinopsis pachanoi* es una especie con presión de recolección y con significado cultural vivo en los Andes; difundir dónde está un ejemplar es un daño concreto, no un problema de forma. La política de publicación distingue tres niveles —público, restringido y no publicable— y las ubicaciones quedan en el tercero de manera permanente.

Límite disciplinar: el jardín es una interpretación visual; no entrega diagnósticos, tratamientos, instrucciones de cultivo ni recomendaciones de uso de sustancias. Las fuentes botánicas, culturales y técnicas se mantendrán diferenciadas. Una fuente no se transforma en verdad por aparecer en una visualización; cada relación indicará si es documentada, inferida, hipotética o curatorial.

Riesgos pendientes [FALTA]: cerrar la bibliografía secundaria, revisar derechos de las fuentes de terceros, confirmar el instrumento con una persona asesora y obtener identidad/Perfil Cultura del responsable. El caso y su corpus primario ya no figuran aquí: están cerrados.

## Documentos que este proyecto debe adjuntar

> Los documentos del Anexo N° 2 son indispensables para la postulación o la evaluación según corresponda; las formalidades exigidas deben verificarse en el FUP y en el anexo oficial vigente.

- [declarado] Avance de Investigación (15 páginas tamaño carta, Arial 12):
  redactado y maquetado en `FONDART_2027_INVESTIGACION_WACHUMA_ANEXOS/AVANCE_DE_INVESTIGACION.{md,pdf}`.
  Pendiente sólo la revisión humana final antes de adjuntar al FUP.
- [declarado] Plan de Actividad de transferencia: redactado y maquetado en
  `FONDART_2027_INVESTIGACION_WACHUMA_ANEXOS/PLAN_ACTIVIDAD_TRANSFERENCIA.{md,pdf}`,
  con actividad, público, metodología y resultados esperados confirmados.
  Pendiente sólo la revisión humana final.

## Aporte del operador antes del envío

- Nombre legal y RUT: [FALTA] — el responsable debe completarlos directamente
  en el FUP; este expediente no los retiene por escrito.
  [FALTA] domicilio/región acreditables y completar el trámite de Perfil Cultura
  (documentos pendientes de enviar en la plataforma).
- Caso único y corpus primario: **cerrados**. El caso es Wachuma
  (*Echinopsis pachanoi*) y su corpus es la base medida en «Fuentes y
  trazabilidad».
- Bibliografía teórica, muestra (24-30 personas), diseño metodológico completo
  y número de sesiones: **cerrados**, en el Avance de Investigación §6-8.
- [FALTA] Cotizaciones o valores verificables y revisión laboral, tributaria y de
  derechos de terceros.
- [FALTA] Confirmación de la autorización ministerial de difusión y verificación
  final de fecha y hora en el portal.

---

Bases leídas el 2026-09-05: https://www.fondosdecultura.cl/wp-content/uploads/2026/08/investigacion-fondart-nacional-2027.pdf
