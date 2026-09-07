# Recomendación final: qué tres postular, y qué cuesta realmente adaptarse

Fecha: 2026-09-06. Fuentes: `fuentes/REGISTRO_DE_CITAS.md` y `fuentes/MATRIZ_COMPARATIVA.csv`.
Evidencia técnica: `evidencia/CIRCUITO_IRIS_COMPROBADO.md`.

## 0. Primero: los tres concursos originales sí existen y están identificados

El traspaso decía que la carpeta "bases" no se había localizado y que los tres
concursos originales eran desconocidos. **Ambas cosas ya no son ciertas.**

La carpeta es **`/home/mak/BASES/postulaciones/`**. Su `README.md` no deja lugar
a interpretación: *"Este directorio concentra los tres concursos que la dirección
está siguiendo"*, y los lista con orden de prioridad propio:

| Prioridad declarada | Concurso | Proyecto | Estado declarado |
|---|---|---|---|
| 1 | Becas Fundación Ama Amoedo 2026 — Artistas | postulación independiente | base verificada, expediente no listo |
| 2 | Fondart Regional — Creación Artística 2027 | *IRIS: Mesa de Montaje* | avanzada, faltan cartas y espacio |
| 3 | Fondart Nacional — Investigación 2027 | *Jardines interpretativos* | borrador |

Hay además un paquete de trabajo paralelo en `/home/mak/borradores/` con las
mismas tres carpetas, anexos, un FUP redactado y snapshots de código.

**Conclusión de Bloque 1, punto uno: la terna original era Ama Amoedo + Creación
Regional + Investigación Nacional. La terna Creación/Difusión/Formativas fue una
propuesta del asistente anterior y no corresponde a lo que el usuario tenía en
mente.** Verifiqué el PDF de bases de Creación descargado hoy contra el
conservado en esa carpeta: son **el mismo archivo** (MD5 idéntico). El trabajo
previo estaba bien fundado; lo que faltaba era leerlo.

## 1. Recomendación

Recomiendo **mantener dos de los tres originales y sustituir el tercero**:

| # | Concurso | Proyecto | Cierre | Monto | Por qué |
|---|---|---|---|---|---|
| **1** | **Becas Fundación Ama Amoedo 2026 — Artistas** | *Dimensiones del Orden: ordenar el propio archivo* | **mié 9 sep, 23:59** | US$10.000 | Encaje literal y costo de adaptación casi nulo |
| **2** | **Fondart Regional — Creación Artística, disciplina Diseño** | *IRIS: Mesa de Montaje* | vie 11 sep, 15:00 | hasta $18.000.000 | Expediente más avanzado, disciplina correcta, admite inversión |
| **3** | **Fondart Regional — Actividades Formativas** | *Laboratorio Dimensiones del Orden* | vie 11 sep, 15:00 | hasta $15.000.000 | Su primer criterio de selección premia exactamente este proyecto |

**El tercero sustituye a Fondart Nacional Investigación / JARDINES.** La razón no
es que JARDINES sea débil, sino de costo real, y está en §3.

### Por qué estas tres son compatibles entre sí

- **No hay regla que lo impida.** Las tres bases prohíben únicamente más de una
  postulación *"a la presente línea"* (§I.4 en las tres) y la FAQ oficial 23 lo
  confirma. Ninguna cláusula de doble financiamiento aparece en los textos
  descargados. Ama Amoedo es otra institución y su única restricción relevante
  es no haber recibido apoyo de la propia Fundación en 12 meses.
- **Y aun así, este paquete se autolimita.** El Anexo 1 letra q de las bases
  define proyecto como *"todas las actividades que en él hubiesen sido
  comprometidas, sea que éstas se financien con recursos propios, de terceros o
  con los que son entregados por el Ministerio"*. Bajo esa definición, comprometer
  la misma actividad en dos expedientes sería comprometerla dos veces. Por eso
  **ninguna actividad y ningún ítem de gasto aparece en dos de los tres
  expedientes**, y cada uno es ejecutable solo. El reparto está en
  `presupuestos/ESCENARIOS_DE_ADJUDICACION.md`.

## 2. Costo real de adaptación, uno por uno

### 1. Ama Amoedo — Artistas · costo de adaptación: **bajo**

Las bases dicen, textualmente, que la categoría Artistas acepta *"propuestas
específicas de investigación o creación artística, tales como: producción de obra
para exhibiciones que no estén asociados a espacios comerciales, desarrollo de un
proyecto, **archivo y preservación de su propio trabajo**, entre otros ejemplos"*.

No hay que adaptar nada: el proyecto ya es literalmente eso. 2.034 piezas
propias, un instrumento para ordenarlas y ninguna salida todavía. Lo que se pide
es un formulario, CV, portfolio y un presupuesto en Excel o PDF. Sin cartas
firmadas, sin espacio anfitrión, sin garantía notarial, sin equipo.

*Lo que sí cuesta:* cierra **en tres días** y exige datos que sólo el artista
tiene (identidad, cuenta bancaria, CV). Y el portfolio adjunto tiene que existir
como PDF — que es, irónicamente, la salida que IRIS todavía no genera.

### 2. Fondart Regional Creación Artística · costo de adaptación: **medio**

**Corrección de disciplina, y es decisiva.** Las bases §I.3 fijan orientaciones
por disciplina, y para **Artes de la Visualidad** exigen *"intervenciones
artísticas en espacios públicos o de uso comunitario, mediante la creación de
esculturas, murales u otros, que contribuyan a la recuperación y revitalización
de barrios"*. Una obra digital de mesa no cabe ahí. Para **Diseño**, en cambio,
piden *"obras, piezas, dispositivos, sistemas, juegos o experiencias de diseño
originales que propongan nuevas formas de acceso a la disciplina desde la
ciudadanía, participación de los públicos"*. IRIS es exactamente un dispositivo
y una experiencia de diseño con participación de públicos.

El FUP ya redactado en `~/BASES/.../FUP_IRIS_GENERADO.md` **ya toma esa
decisión** y la fundamenta. Coincide con mi lectura independiente de las bases.

*Lo que cuesta:* la exhibición es obligatoria (§I.3: *"El proyecto deberá
contemplar la exhibición de la o las obras finales resultantes"*), y con ella el
espacio anfitrión y su carta. Las cartas de compromiso del equipo son
**taxativas**: si falta una, el proyecto queda fuera de convocatoria.

*Riesgo que hay que decir en voz alta:* el criterio de selección prioriza *"los
dos proyectos con más alto puntaje para la realización de su **primera obra
artística**"*, y en la Región Metropolitana, dos por cada disciplina. Un artista
con trayectoria no compite por esos cupos; compite por el resto, con umbral de
elegibilidad de 85 puntos. Es admisible y sensato postular, pero presentar esta
línea como la de mayor probabilidad sería inventar.

### 3. Fondart Regional Actividades Formativas · costo de adaptación: **medio-bajo**

Este es el hallazgo que cambia el orden respecto de los briefs recibidos. El
**primer criterio de selección** de la línea es, textualmente: *"De mayor a menor
puntaje obtenido en la evaluación, seleccionándose en primer lugar el proyecto
con más alto puntaje que considere alguna de las siguientes temáticas:
interregionalización, internacionalización, el desarrollo de públicos y la
**incorporación de nuevas tecnologías y formatos para la innovación**."*

Un laboratorio gratuito donde artistas ordenan sus propios archivos con una
herramienta nueva no *encaja* en ese criterio: lo *ocupa*. El brief anterior
puso esta línea en tercer lugar; la lectura de las bases la sube.

*Lo que cuesta:* la gratuidad es obligatoria, la actividad no puede conducir a
grado académico, y hay tres anexos de evaluación que no existen todavía
(Programa de la Formación, Diagnóstico de Necesidad Formativa, Estrategias de
Transferencia). Están redactados en este paquete.

*Corrección al traspaso:* que la línea financie "proyectos colectivos" **no**
obliga a constituir una persona jurídica. Las bases §II.1 admiten persona
natural. El traspaso ya sospechaba esto; queda confirmado.

## 3. Por qué se desplaza Fondart Nacional — Investigación (JARDINES)

No por debilidad del proyecto. Por tres costos concretos:

1. **Es otro proyecto, no otra cara del mismo motor.** JARDINES tiene su propia
   base de datos verificada (22 tablas pobladas, 44 fuentes, 26 claims). Es
   investigación sobre interpretación de fuentes, no producción con el archivo
   del artista. Postularlo obliga a sostener dos narrativas en paralelo en la
   misma semana.
2. **Es el expediente menos avanzado.** El README de `borradores/` lo dice:
   *"Faltan identidad, CV, muestra, fuentes, anexos y maquetación FUP."*
3. **Una línea de Investigación se evalúa por método, no por prototipo.** El
   activo más fuerte de MAK —un sistema que funciona— pesa menos ahí que en
   Creación o Formativas.

**Queda como cuarta opción viva y con la ventaja de cerrar tres días después
(14 de septiembre, 15:00).** Si el artista prefiere conservar los tres
originales, la sustitución razonable es la inversa: postular JARDINES a
Investigación Nacional el 14 y dejar Formativas fuera. El material de JARDINES
no se toca ni se degrada en esta entrega.

## 4. Alternativa documentada: Difusión en vez de Creación

**Fondart Regional Difusión** es la línea con mejor encaje *literal* de las
cinco: nombra entre sus soportes *"sitios web para la exhibición de obras en
línea"* y *"aplicaciones móviles"*, tiene el mismo tope de $18.000.000, pondera
Impacto Potencial al 50% (el más alto), y su anexo de compromiso de exhibición
**exime expresamente** al proyecto cuando *"el soporte lo constituya un medio de
difusión no existente (ejemplo: un sitio web) y que será desarrollado por el
proyecto en concurso"*. Eso elimina la dependencia de un espacio anfitrión.

**No la recomiendo como una de las tres por dos razones concretas:**

1. Exige difundir **obras ya creadas**. El corpus lo permite —134 piezas tipadas
   como `obra` en `campo.json`— pero el proyecto se convertiría en *publicar el
   portafolio*, no en *construir el instrumento*. Es una postulación distinta.
2. **Colisiona con Creación.** Ambas financiarían el mismo desarrollo. Bajo la
   regla de no duplicar actividades, hay que elegir una.

*Cuándo cambiar de opinión:* si el espacio anfitrión no se cierra a tiempo,
Difusión es el reemplazo directo de Creación, porque es la única de las tres
regionales que no necesita carta de espacio. Ese es el plan B y está anotado en
`RESOLUCIONES_EXTERNAS.md`, ítem R-3.

## 5. Fondos consultados y descartados, con la razón

- **Becas Chile Crea 2027** — cerró el 7 de septiembre de 2026. Además financia
  formación individual, no este proyecto.
- **Fondo Audiovisual** — Investigación y Obras Experimentales cerraron el 8 de
  septiembre. Fuera de plazo.
- **Libro y Lectura** — cerró entre el 4 y el 9 de septiembre y su objeto es el
  ecosistema del libro.
- **Artes Escénicas** — cerró el 7 de septiembre.
- **Fondart Regional Culturas Regionales y Culturas Tradicionales** — siguen
  abiertas al 11 de septiembre, pero su objeto es territorial y patrimonial.
  Forzar IRIS ahí sería un encaje inventado.
- **Fondart Nacional Barrios Creativos e Infraestructura** — abiertas al 14, sin
  relación con el objeto.

**Sobre la suficiencia de la evidencia:** hay tres opciones admisibles y
defendibles, más una cuarta viva. No fue necesario forzar ningún encaje.
