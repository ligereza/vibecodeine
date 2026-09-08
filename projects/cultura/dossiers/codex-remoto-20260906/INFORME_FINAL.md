# Informe final — estado real de preparación

Fecha: **domingo 6 de septiembre de 2026**.

## 1. Qué cambió respecto de los briefs recibidos

Ocho correcciones, todas con la evidencia que las sostiene. Ninguna es de estilo.

| # | Lo que decía el material recibido | Lo verificado hoy | Fuente |
|---|---|---|---|
| 1 | *"La carpeta llamada 'bases' no fue localizada definitivamente"* y los tres concursos originales eran desconocidos | **Localizada: `/home/mak/BASES/postulaciones/`.** Su README declara los tres concursos: Ama Amoedo, Creación Regional (IRIS) e Investigación Nacional (JARDINES) | `~/BASES/postulaciones/README.md` |
| 2 | La terna Creación / Difusión / Formativas | **No era la terna original.** Fue propuesta del asistente anterior | Ídem |
| 3 | IRIS es "el Portfolio Editor", una plataforma pública de portafolio | Es la superficie **de operador** para ordenar y curar. *"not the artist's public portfolio"*, **dice el propio código**. Y escucha en `127.0.0.1`: no es pública | `hub.py` l.1-11; prueba HTTP |
| 4 | Se sugería postular IRIS en Artes de la Visualidad | La disciplina correcta es **Diseño**. Artes de la Visualidad exige intervenciones en espacio público con esculturas o murales | Bases Creación §I.3 |
| 5 | Formativas en tercer lugar de prioridad | Su **primer criterio de selección** premia la *"incorporación de nuevas tecnologías y formatos para la innovación"*. Sube de prioridad | Bases Formativas, Procedimiento de Selección |
| 6 | Se sospechaba que "proyecto colectivo" podía exigir persona jurídica | **No la exige.** Persona natural admitida | Bases Formativas §II.1 |
| 7 | Se suponía que WACHUMA existía sólo en Windows | **Está en MAK, monorepo completo.** Pero su README declara contenido *"sintético o restringido"* | `~/WACHUMA/README.md` |
| 8 | Se atribuía a IRIS capacidad de exportación / salida de portafolio | **No existe.** La única salida es la descarga de un JSON. `curaduria.json` tiene **0 decisiones** registradas | `editor.html` l.1092, l.2784-2786; prueba de datos |

**Y una que confirma en vez de corregir:** el traspaso advertía que *"la afirmación
general 'sin datos humanos' no describe automáticamente IRIS"*. Es exacto. El
campo contiene **40 piezas tipificadas `foto_evento`** que pueden mostrar
personas. Están excluidas de la selección de portafolio propuesta.

## 2. Las tres alternativas defendibles

| # | Concurso | Proyecto | Cierre (RM) | Monto |
|---|---|---|---|---|
| 1 | Becas Fundación Ama Amoedo 2026 — Artistas | *Dimensiones del Orden: ordenar el propio archivo* | mié 9 sep, 23:59 | US$10.000 |
| 2 | Fondart Regional — Creación Artística, **Diseño** | *IRIS: Mesa de Montaje* | vie 11 sep, 15:00 | $18.000.000 |
| 3 | Fondart Regional — Actividades Formativas | *Laboratorio Dimensiones del Orden* | vie 11 sep, 15:00 | $14.900.000 |

Dos alternativas vivas y documentadas: **Difusión** como reemplazo de la 2 si el
espacio anfitrión no se cierra, e **Investigación Nacional (JARDINES)** con cierre
el 14 de septiembre.

La evidencia alcanzó para tres opciones admisibles. **No fue necesario forzar
ningún encaje.**

## 3. Dónde está cada postulación

| Expediente | Archivo | Presupuesto | Anexos propios |
|---|---|---|---|
| 1 · Ama Amoedo | `postulaciones/01_AMA_AMOEDO_ARTISTAS/EXPEDIENTE.md` | `presupuestos/01_ama_amoedo.csv` | Ficha de corpus, ficha técnica |
| 2 · Creación | `postulaciones/02_FONDART_CREACION_IRIS/EXPEDIENTE.md` | `presupuestos/02_fondart_creacion.csv` | Propuesta creativa, estrategia de difusión |
| 3 · Formativas | `postulaciones/03_FONDART_FORMATIVAS_LABORATORIO/EXPEDIENTE.md` | `presupuestos/03_fondart_formativas.csv` | Programa, diagnóstico, transferencia |

## 4. Lectura crítica contra la pauta de evaluación de cada fondo

Revisé cada expediente con los criterios de sus propias bases y corregí lo que
encontré **dentro de esta sesión**. Lo que sigue es el resultado, no la promesa.

### Incoherencias que encontré y corregí

| Problema detectado | Dónde estaba | Corrección aplicada |
|---|---|---|
| **El borrador previo de Creación incluía 4 talleres formativos.** Eso duplicaba la actividad central del Expediente 3 y habría financiado dos veces lo mismo | FUP previo en `~/BASES/.../FUP_IRIS_GENERADO.md` | En el Expediente 2 quedan **2 sesiones de prueba de mediación** con hasta 6 personas, descritas explícitamente como ensayos de la obra y **no** como transferencia de conocimiento. Los 8 talleres formativos viven sólo en el Expediente 3 |
| El presupuesto de Creación sumaba **$18.480.000**: excedía el tope | Primera versión de este paquete | Recalculado a **$18.000.000** exactos |
| El presupuesto de Formativas sumaba **$16.466.000**: excedía el tope de $15.000.000 | Ídem | Recalculado a **$14.900.000** |
| El presupuesto de Ama Amoedo sumaba **US$10.294** | Ídem | Recalculado a **US$9.994** |
| Formativas incluía inicialmente equipamiento | Ídem | Eliminado: **la línea no tiene ítem de Inversión**. Sólo Operación, Personal e Imprevistos |
| Ambos Fondart arrancaban el 1 de abril de 2027, concentrando la carga | Cronograma inicial | Formativas se desplaza al **31 de mayo**, dentro de la ventana permitida |
| El diagnóstico de necesidad se leía como afirmación sobre el sector | Borrador del Anexo | Reformulado como hipótesis desde experiencia propia, **con un mecanismo de medición dentro del laboratorio** y compromiso de publicar el resultado en cualquier dirección |

### Verificación por criterio, fondo por fondo

**Creación** — Impacto Potencial 40%: exhibición de 4 semanas con metas y
verificadores; aporte declarado sin prometer transformación del sector. Calidad
30%: propuesta creativa completa, innovación argumentada sobre una propiedad
verificable (la métrica de pérdida). Currículo 20%: **el punto más débil** — la
trayectoria depende de un CV que no tengo (R-2) y el criterio de selección
prioriza primera obra artística, lo que está dicho abiertamente en la
recomendación. Viabilidad 10%: presupuesto coherente y verificado, cronograma
dentro de la ventana.

**Formativas** — Impacto 40%: transferencia con tres mecanismos y evidencias
numeradas; el mecanismo principal (la guía) funciona sin el software del proyecto.
Calidad 30%: programa con carga horaria, secuencia y evaluación del aprendizaje
declarada. Currículo 20%: mismo punto débil que arriba. Viabilidad 10%:
presupuesto sin ítem inválido y metas con deserción realista (12 de 16).

**Ama Amoedo** — Los tres criterios declarados: correlación literal con la
categoría, aporte concreto (un instrumento disponible) y factibilidad acreditada
con un sistema que corre y una prueba fechada.

### Coherencia entre promesa y evidencia

Verifiqué que **ninguno de los tres expedientes presente como capacidad actual**
lo que la evidencia dice que no existe: la exportación, la superficie pública, el
bucle de curaduría ejercido, la validación con artistas externos y el modo
multiusuario. Los cinco aparecen en los tres expedientes como **trabajo a
financiar** o como límite declarado. La ficha técnica los lista explícitamente en
su sección *"Lo que NO existe"*.

**Lo que este paquete promete financiar es exactamente el hueco que la propia
prueba técnica deja a la vista.**

## 5. Lista de verificación antes de enviar

- [ ] Región de domicilio y ejecución confirmada — **cambia la fecha de cierre** (R-2)
- [ ] Perfil Cultura vigente: responsable y **cada** integrante del equipo
- [ ] Una carta de compromiso firmada **por cada** integrante declarado (R-4)
- [ ] Carta o cotización del espacio anfitrión, o plan B activado (R-3)
- [ ] Cotizaciones reemplazando las estimaciones de mayor monto (R-5)
- [ ] Verificado que el responsable no fue seleccionado en Creación 2026
- [ ] Presupuesto del formulario cuadra con el CSV correspondiente
- [ ] Archivos **sin comprimir**, nada de ZIP/RAR/7Z, cada uno bajo 100 MB
- [ ] PDF multipágina en un solo archivo; enlaces vigentes y sin clave
- [ ] Antecedentes en español
- [ ] Una sola postulación por línea (**vale la última enviada**)
- [ ] Enviado **antes de las 12:00** del viernes 11, no a las 14:50
- [ ] Certificado de recepción con folio guardado

## 6. Qué actos externos faltan para poder enviar

Nueve ítems en `RESOLUCIONES_EXTERNAS.md`. **Dos son bloqueantes** (R-1 formulario
de Ama Amoedo, R-2 identidad del responsable), **dos son taxativos o críticos**
(R-4 cartas del equipo, R-3 espacio), **uno afecta evaluación** (R-5
cotizaciones), **dos son decisiones de autor** (R-6 sentido de la capa `tilde`,
R-7 licencia), **uno es posterior** (R-8) y **uno es opcional** (R-9).

## 7. Estado honesto

**Lo que está terminado:** investigación de bases, resolución de fechas y
prórrogas, matriz comparativa, verificación técnica reproducible, dos análisis,
recomendación fundada, tres expedientes redactados con todas sus secciones, tres
presupuestos calculados y verificados contra topes, ocho anexos, dos modelos de
carta, cronogramas de preparación y de ejecución, y escenarios de adjudicación.

**Lo que no está y no podía estar:** los datos personales del artista, las firmas
de terceros, las cotizaciones, el enlace vivo de un formulario que exige un
navegador, y dos decisiones de sentido que son suyas.

**Ninguna postulación está enviada. Ninguna firma se dio por obtenida. Ningún
compromiso externo se dio por conseguido.** Nada de este paquete salió de la
máquina ni se envió a nadie.
