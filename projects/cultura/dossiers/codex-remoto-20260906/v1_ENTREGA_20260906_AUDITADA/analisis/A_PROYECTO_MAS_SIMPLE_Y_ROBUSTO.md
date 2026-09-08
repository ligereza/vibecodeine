# Análisis A — El proyecto más simple, robusto y compatible con lo verificado

Fecha: 2026-09-06. Las valoraciones son **juicio fundado**, no probabilidades.
No aparece aquí ninguna cifra de adjudicación: nadie las conoce.

## 1. Los tres alcances comparados

- **IRIS mínimo** — Terminar el eslabón que falta: que el archivo propio, ya
  ordenado por criterio visual, produzca una salida (portafolio publicable) tras
  una decisión humana registrada. Alcance acotado al archivo del artista.
- **JARDINES/WACHUMA mínimo** — Convertir la base de interpretación en una
  publicación o experiencia sobre fuentes, correspondencias e incertidumbre.
- **Alcance mixto** — IRIS como instrumento y WACHUMA como corpus demostrativo.

## 2. Criterios explícitos

### Evidencia disponible hoy

**IRIS: alta y citable.** Servicio corriendo (verificado 2026-09-06), 2.034
piezas, 5.812 vínculos, 219 obras con percepción de máquina, métrica publicada
de pérdida al ordenar (`vecindad_conservada = 0.4855`), contrato de curaduría
reversible. Prueba reproducible incluida.

**JARDINES: media y de otra naturaleza.** `jardines_interpretativos.sqlite` tiene
22 tablas pobladas: 44 fuentes, 26 claims, 13 entidades, 12 semánticas de
proceso, 11 eventos de auditoría. Es evidencia de método, no de obra.

**WACHUMA: alta como software, baja como contenido.** Monorepo completo en
`~/WACHUMA`. Su propio README: *"los ejemplares, la escena 3D, el linaje y la
relación cultural del jardín siguen siendo sintéticos o restringidos"*. Un
proyecto cultural no puede exhibir contenido sintético como si fuera archivo.

**Mixto: hereda lo peor.** La evidencia técnica de WACHUMA no cubre la brecha de
contenido, y sumar dos dominios duplica lo que hay que explicar en el formulario.

### Encaje con lo que efectivamente está abierto

**IRIS: encaja en tres convocatorias abiertas simultáneamente** —Ama Amoedo
Artistas (archivo del propio trabajo), Creación en Diseño (dispositivo y
experiencia), Formativas (nuevas tecnologías para la innovación). Es raro que un
mismo objeto encaje en tres puertas sin deformarse. Encaja porque el objeto es
un instrumento y las tres puertas preguntan cosas distintas sobre él.

**JARDINES: encaja en una** (Investigación Nacional, cierre 14 de septiembre).

**WACHUMA: en ninguna sin resolver antes consentimiento biocultural.**

**Mixto: encaja peor que IRIS solo**, porque obliga a justificar el corpus ajeno.

### Trabajo nuevo requerido

**IRIS: acotado y nombrable.** Tres cosas, ninguna especulativa: exportación a
formato de portafolio, publicación fuera de `127.0.0.1`, y ejercicio real del
bucle de curaduría con normalización del vocabulario visual (`azul`/`Azul`).
Están identificadas por lectura de código, no estimadas.

**JARDINES: trabajo de investigación, no de producto** — diseño metodológico,
corpus de fuentes, muestra, validación.

**WACHUMA: trabajo de gobernanza antes que de código** — permisos, revisión
comunitaria, registros reales. No tiene plazo previsible.

**Mixto: la suma, sin ahorro.**

### Dependencias humanas

**IRIS mínimo: mínimas.** El archivo es del artista, las obras son suyas, no hay
datos de terceros en el corpus de trabajo. Ama Amoedo no exige ninguna firma
externa. Creación exige carta de espacio y cartas de equipo. Formativas exige
equipo, no espacio necesariamente.

**JARDINES: fuentes de terceros con licencias que revisar.**

**WACHUMA: consentimiento de comunidades. Es la dependencia más pesada posible.**

### Dificultad de los anexos

**IRIS: baja a media.** El anexo más difícil de Creación —el compromiso de
exhibición— tiene una vía de escape textual en las bases para soportes virtuales
que el propio proyecto desarrollará, y esa vía existe en Creación y en Difusión.
El portfolio PDF de Ama Amoedo es trabajo de una tarde con material existente.

**JARDINES: alta.** Muestra, fuentes citables, maquetación de FUP, y un CV que
acredite trayectoria investigadora.

### Presupuesto

**IRIS: cómodo en las tres.** Es un proyecto de personas y tiempo, no de
materiales caros. Creación admite **Inversión** (equipo de exhibición con destino
posterior declarado); Difusión y Formativas **no tienen ítem de inversión**, lo
que empuja hacia honorarios y operación — que es justamente la forma natural de
este proyecto.

**JARDINES: también cómodo**, pero con menos que mostrar por peso.

### Capacidad de entrega en la ventana real

**IRIS: la única con capacidad demostrada.** Hay un FUP redactado, anexos
modelados, código snapshotteado y datos verificables. Faltan firmas, no textos.

**JARDINES: no en tres días**, sí quizá en ocho (cierra el 14).

**WACHUMA y mixto: no.**

### Utilidad posterior

**IRIS: la más alta de las tres, y es la razón de fondo.** Lo que queda
funcionando después del financiamiento es un instrumento que el artista usa en su
propia práctica todas las semanas. No es un entregable que se archiva: es una
herramienta que se sigue usando porque resuelve un problema que su autor tiene.
Esa es la condición que distingue una herramienta que sobrevive de una que muere
con el informe final.

**JARDINES: alta como conocimiento, baja como instrumento cotidiano.**

**WACHUMA: alta a largo plazo, nula en el horizonte de esta entrega.**

## 3. Conclusión

**Se elige IRIS mínimo.** No por entusiasmo con el nombre, sino porque es el
único alcance donde las nueve dimensiones apuntan en la misma dirección, y
porque su brecha —la salida— es el eslabón más pequeño, más visible y más
verificable de todo el sistema. Es también el único donde el fracaso sería
honesto: si la exportación no se logra, se sabrá, porque hoy se puede comprobar
que no existe.

**Se descarta el alcance mixto** por una razón concreta y no por prudencia
genérica: añadir WACHUMA no aporta ninguna capacidad que IRIS no tenga, y añade
la única dependencia del sistema que nadie puede resolver por trabajo propio.

**Se conserva JARDINES intacto** como cuarta opción con cierre posterior. Su
material no se degrada ni se canibaliza en esta entrega.

## 4. Alcance ejecutable resultante

El mismo núcleo, tres salidas que no se pisan:

| Convocatoria | Qué financia exactamente | Qué queda funcionando |
|---|---|---|
| Ama Amoedo | Ordenar y preservar el archivo propio y producir su primera salida publicable | Un archivo del artista ordenado, con decisiones registradas, y un portafolio |
| Creación (Diseño) | Convertir el instrumento en obra situada, exhibible y mediada | Una obra exhibible y un protocolo de mediación reutilizable |
| Formativas | Enseñar el método a otros artistas con sus propios archivos | Personas capacitadas, una guía transferible y un instrumento probado fuera de su autor |

Ninguna de las tres promete que la máquina encuentre el orden correcto. Las tres
prometen lo que hoy ya se puede comprobar que el sistema hace: **proponer un
orden, mostrar cuánto pierde al proponerlo, y dejar que una persona decida.**
