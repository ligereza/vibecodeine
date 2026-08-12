# GRADOS DE DESACUERDO
## Borrador de postulación — Fondart Nacional 2027

> **Aviso de trabajo:** las bases definitivas se publican con la apertura (5–6 de agosto). Este borrador está estructurado según los campos estándar de Fondart y hay que reordenarlo cuando salgan. Todo lo que sigue es texto adaptable, no definitivo. Los montos son indicativos.

---

## FICHA

**Nombre del proyecto:** Grados de desacuerdo
**Línea sugerida:** Artes de la Visualidad / Nuevos Medios — modalidad Creación
**Duración estimada:** 12 meses
**Región de ejecución:** Metropolitana, con circulación digital sin límite territorial

---

## RESUMEN

*Grados de desacuerdo* es un instrumento en dos partes que mide la calibración óptica en los dos extremos de la obra de arte: el ojo que la produce y el ojo que la recibe.

**AX** es una herramienta de análisis que extrae, del corpus de un artista digital, su *firma angular* — la distribución de orientaciones que privilegia sin saberlo — y separa por primera vez su componente motor (mano) de su componente perceptual (ojo y corteza).

**Sin referencia** es una pieza web que mide el eje óptico del espectador mediante un test en pantalla, lo somete a una recalibración imperceptible, y le devuelve su propio número.

Ambos producen la misma unidad: un eje en grados. Al restarse, aparece la cifra que da nombre al proyecto: los **grados de desacuerdo** entre quien hizo una obra y quien la mira.

El proyecto parte de un caso concreto —el del autor, con astigmatismo alto asimétrico corregido tardíamente— y se propone convertir una condición individual clasificada como defecto en un instrumento de conocimiento sobre cómo se produce y se recibe cualquier imagen.

---

## FUNDAMENTACIÓN

### El problema

Existe una asimetría invisible en el centro de toda experiencia visual: alguien decidió cuál calibración óptica es la referencia, y todas las demás se llaman error.

No es una metáfora. La agudeza 20/20 es un umbral estadístico fijado en el siglo XIX. La corrección refractiva se distribuye según una norma que nunca se sometió a discusión pública. Y un ojo que enfoca perfectamente a cuarenta centímetros —la distancia a la que la mayoría de la población pasa hoy sus horas de trabajo y de ocio— se clasifica como defectuoso porque falla en el infinito, que casi nadie mira.

Cerca de la mitad de la humanidad tendrá error refractivo en las próximas décadas. Es probablemente la variación humana más extendida del planeta, y es la única que nunca ha sido pensada como diversidad: solo como inventario de dioptrías a corregir.

### El antecedente científico

La investigación reciente en neurociencia de la visión ha demostrado que el cerebro **compensa activamente la óptica del propio ojo**. En astigmatismo crónico, la corteza visual aplica una modulación de ganancia que cancela la distorsión — un proceso que tarda años en consolidarse y que se propaga desde regiones posteriores hacia anteriores. La exposición breve produce el patrón inverso y no funciona: la adaptación durable exige experiencia extendida.

De ahí una consecuencia poco discutida y central para este proyecto: **corregir ópticamente a un astígmata crónico introduce una distorsión nueva**, porque el cerebro estaba calibrado sobre la óptica del propio ojo. Existe literatura específica sobre la adaptación perceptual *a la corrección* del astigmatismo natural.

Se sabe además que el astigmatismo alto no corregido durante el período crítico —que se cierra en gran parte entre los siete y los ocho años— produce **ambliopía meridional**: un déficit permanente de sensibilidad para orientaciones específicas, de origen cortical y no óptico. Ningún lente lo corrige, porque el lente arregla la imagen que llega y el déficit está en quien la lee. Y se sabe, por trabajo publicado reciente, que ese déficit **responde a entrenamiento perceptual orientado al eje individual, en adultos**.

No existe ningún trabajo que aplique esto a la práctica de un artista en ejercicio. No existe ninguna serie temporal del sesgo angular de un artista. No existe ninguna medición sistemática de la relación entre eje refractivo y firma angular de obra.

### El caso 001

A los diez años una profesora me vio achicando los ojos en clase. Antes de eso nadie había considerado llevarme a un oftalmólogo: la miopía produce un síntoma legible —el niño no ve el pizarrón— pero el astigmatismo produce distorsión, y un niño no tiene con qué compararla. No tenía referencia de un mundo sin cizalla. Para mí, eso era el mundo.

Mi corrección actual es de −3.25 y −3.50 dioptrías cilíndricas, con esfera prácticamente nula y **los ejes desalineados dieciséis grados respecto de su posición especular**: cada uno de mis ojos deforma el mundo en una diagonal distinta, y mi corteza fusiona las dos. Me corrigieron a los diez, después del cierre del período crítico.

Trabajo como artista digital. Hace años que observo que **si espejeo una obra terminada, es otra obra**. Lo atribuí a lo que todo artista atribuye: sesgo de mano, hábito compositivo. Este proyecto nace de la sospecha de que hay algo más, de que ese algo es medible, y de que si es medible entonces deja de ser un defecto y pasa a ser un parámetro.

### Por qué importa más allá del caso

Porque lo que le pasa a un astígmata le pasa a todos, solo que con menos amplitud. **Toda obra de arte de la historia ha pasado por dos instrumentos sin calibrar** —el ojo de quien la hizo, el ojo de quien la mira— y el campo entero ha procedido como si ambos fueran ventanas transparentes.

El proyecto no argumenta que no existe una versión de una obra que sea correcta para todos los espectadores. **La calcula.**

---

## OBJETIVO GENERAL

Desarrollar un instrumento en dos partes —herramienta de análisis y obra web— que mida la calibración óptica en la producción y en la recepción de la imagen, y que constituya la variación refractiva como campo de conocimiento estético en lugar de como déficit clínico.

## OBJETIVOS ESPECÍFICOS

1. **Medir** la firma angular de un conjunto de artistas digitales chilenos y establecer el primer corpus de datos sobre sesgo orientacional en práctica artística.
2. **Separar** metodológicamente la componente motora de la componente perceptual de ese sesgo, mediante análisis multi-escala y descuento de lateralidad.
3. **Desarrollar** AX como herramienta de código abierto, de ejecución local, que devuelva al artista su propio eje como parámetro de trabajo y no como diagnóstico.
4. **Producir** *Sin referencia*, pieza web que mide el eje del espectador y le hace experimentar la plasticidad de su propia calibración.
5. **Documentar** el caso 001 como investigación de primera persona, con protocolo de medición replicable.
6. **Circular** el proyecto en exhibición presencial, publicación abierta del dataset y del código, y postulación a circuito internacional de arte y tecnología.

---

## METODOLOGÍA

### Línea 1 — Análisis de imagen (AX)

Extracción de orientaciones mediante **tensor de estructura**: gradientes por operador de Scharr, construcción del tensor con suavizado gaussiano, obtención de orientación y coherencia por píxel, y acumulación en histograma polar ponderado. Se complementa con análisis de anisotropía angular del espectro de Fourier, más robusto frente a la variación de contenido.

El eje dominante se calcula en representación de ángulo duplicado, apropiada para magnitudes orientacionales módulo 180°, y la anisotropía se expresa como longitud del vector resultante.

**Separación motor/perceptual — núcleo metodológico:**

1. *Multi-escala.* El sesgo motor reside en el trazo (frecuencia espacial alta, mecánica de muñeca y codo); el perceptual reside en la colocación y la cizalla global (frecuencia baja). Se analizan bandas separadas: una divergencia direccional entre escalas separa las fuentes.
2. *Descuento de lateralidad.* Se modela la componente diagonal predicha por la lateralidad declarada y se sustrae. **El residuo es la señal.**
3. *Contraste refractivo.* Para los participantes que aporten receta, se contrasta el residuo contra su eje de cilindro. Hipótesis falsable.

**Validación:** el pipeline se valida contra imágenes sintéticas con cizalla de magnitud y ángulo conocidos antes de aplicarse a obra real.

### Línea 2 — Producción de la obra (Sin referencia)

Cuatro movimientos: calibración física de pantalla mediante objeto de dimensión estándar; medición del eje del espectador mediante abanico astigmático (test clínico de uso establecido); recalibración por cizalla de crecimiento subumbral con retorno abrupto a cero; y exposición del fenómeno entóptico de campo azul.

El desarrollo del tercer movimiento requiere calibración empírica de la curva: la tasa de crecimiento debe permanecer bajo el umbral de detección y alcanzar magnitud suficiente para que el retorno sea percibido como distorsión. Esta calibración se realiza mediante pruebas con usuarios.

### Línea 3 — Investigación de primera persona

Protocolo de auto-medición documentado y replicable (topografía, refracción, agudeza orientacional, estenopeico, test de espejo con control de obra ajena, dibujo monocular), ejecutado sobre el caso 001 y publicado como parte del proyecto.

### Ética y datos

AX se ejecuta **enteramente en el dispositivo del usuario**. Ninguna obra abandona la máquina de quien la hizo. El dataset publicado contiene únicamente métricas agregadas y anonimizadas, con consentimiento informado explícito.

El proyecto **no diagnostica**. Cuando un residuo sugiere un componente óptico no evaluado, la herramienta deriva a evaluación profesional. Esta distinción se declara en la interfaz y en toda comunicación pública.

---

## CRONOGRAMA

| Mes | Actividad |
|---|---|
| 1 | Fase 0: protocolo de auto-medición completo, caso 001. Formalización de contraparte científica. |
| 2–3 | AX: pipeline de tensor de estructura, validación contra imágenes sintéticas, módulos FIRMA y ESPEJO. |
| 4 | Convocatoria y consentimiento de artistas participantes. |
| 5–6 | Levantamiento de corpus. Módulos RESIDUO y DERIVA. Primeros resultados. |
| 7–8 | *Sin referencia*: desarrollo de movimientos I y III. |
| 9 | *Sin referencia*: movimiento II y calibración empírica de la curva con pruebas de usuario. |
| 10 | Integración: cálculo del delta obra/espectador. Documentación. |
| 11 | Montaje de exhibición. Publicación de código y dataset. |
| 12 | Exhibición, mediación, postulación a circuito internacional. |

---

## PRESUPUESTO INDICATIVO

| Ítem | Monto (CLP) |
|---|---|
| Honorarios de creación e investigación (12 meses) | 6.000.000 |
| Asesoría científica (ciencias de la visión) | 1.200.000 |
| Desarrollo y testeo de usuario | 1.500.000 |
| Exámenes y mediciones clínicas del caso 001 | 350.000 |
| Equipamiento: monitor calibrado y colorímetro | 900.000 |
| Producción de exhibición (montaje, impresión, mediación) | 1.400.000 |
| Registro audiovisual y fotográfico | 600.000 |
| Difusión, sitio y traducción al inglés | 500.000 |
| Gastos administrativos | 400.000 |
| **Total** | **12.850.000** |

*Ajustar a los topes y a la estructura de ítems de las bases 2027.*

---

## EQUIPO

- **Dirección, creación y desarrollo:** [autor]
- **Asesoría en ciencias de la visión:** a formalizar con centro de neurociencia o escuela de optometría. Carta de interés en gestión.
- **Asesoría curatorial / mediación:** a definir.
- **Testeo de usuario:** artistas participantes del corpus.

---

## ACCESIBILIDAD E INCLUSIÓN

Este proyecto no incorpora la accesibilidad como requisito administrativo: **la accesibilidad es su objeto.**

*Sin referencia* es probablemente la primera obra que se adapta a la óptica individual de cada espectador en lugar de exigir que el espectador se adapte a ella. No presupone visión corregida, no presupone visión normativa, y **carece deliberadamente de una versión "correcta"** frente a la cual las demás sean deficientes.

La pieza opera además como instrumento de detección: para muchos espectadores será la primera vez que un objeto les informe algo sobre su propio sistema visual, y la primera derivación a examen que reciban en su vida. En un país donde el acceso a evaluación oftalmológica es desigual, una obra que mide y deriva sin costo tiene alcance que excede lo artístico.

El proyecto se publica con código abierto y funciona en cualquier navegador, sin hardware especializado.

---

## DIFUSIÓN Y CIRCULACIÓN

- Exhibición presencial en espacio de arte contemporáneo o de arte y ciencia, con estaciones individuales.
- Publicación permanente de *Sin referencia* en web, accesible desde cualquier dispositivo, sin restricción territorial.
- Liberación de AX como herramienta de uso libre para artistas.
- Publicación abierta del dataset agregado y de la metodología.
- Postulación a S+T+ARTS Prize (Ars Electronica), Lumen Prize y festivales de arte y tecnología de la región.
- Presentación del protocolo y los resultados en instancia académica de ciencias de la visión, si la contraparte lo permite.

---

## APORTE AL CAMPO

**Al arte:** una obra sin versión canónica, que computa su propia recepción. El precedente pictórico más cercano —la pintura que representa el mundo tal como lo ve un ojo con error refractivo— *representa* la borrosidad. Esta pieza la **induce** en el cuerpo del espectador. La distancia entre representar e inducir es la contribución.

**A la investigación:** datos que no existen. Firmas angulares de artistas, su deriva temporal, y la primera separación metodológica entre sesgo motor y sesgo perceptual en producción visual.

**Al debate público:** la crítica al modelo médico de la discapacidad aplicada al territorio donde nunca se aplicó. La refracción no es una enfermedad de la que la mitad de la humanidad esté por enfermar. Es una diversidad que decidimos llamar defecto, y este proyecto propone medirla en vez de corregirla.

---

## STATEMENT

> Un niño con astigmatismo no se queja: no tiene con qué comparar. Calibra sobre la distorsión, y eso, para él, es el mundo.
>
> Ver bien no es recibir más — es suprimir más, y suprimir según un consenso que nadie te consultó.
>
> Esta pieza no te corrige. Te devuelve tu número.

---

## ANEXOS A PREPARAR

- [ ] Portafolio de obra (20–30 piezas, fechadas)
- [ ] Currículum artístico
- [ ] Carta de interés de contraparte científica
- [ ] Carta de compromiso de espacio de exhibición
- [ ] Prototipos funcionales de AX y *Sin referencia* — **ya disponibles**
- [ ] Resultados preliminares de Fase 0
- [ ] Cotizaciones de equipamiento
