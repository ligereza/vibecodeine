# Manifiesto del paquete candidato -- IRIS: Mesa de Montaje

Generado por un agente Claude el 2026-09-07. Este paquete reune unicamente los
archivos relevantes para revision/envio de la postulacion **IRIS: Mesa de
Montaje** (Fondart Regional -- Creacion Artistica: Innovacion y Nuevos
Formatos Creativos 2027). No se envio nada: esto es material de trabajo para
que el operador complete los campos personales/de permiso y decida que
adjuntar.

Cierre reconfirmado en el portal oficial el 2026-09-07: **16 de septiembre de
2026, 15:00 hrs de Santiago**, para todas las regiones.

## Matriz breve de decision (agregada 2026-09-07, plan del coordinador)

| Campo | Contenido |
|---|---|
| Objeto | Mesa de Montaje: instrumento de lectura curatorial donde el archivo del participante aparece como relaciones/hipotesis que se aceptan, rechazan o dejan abiertas -- no un catalogo, chatbot ni grafo universal |
| Audiencia | Jurado Fondart Regional (Potencial 40%, Calidad 30%); publico general en montaje abierto y grupo de artistas en el taller de archivo propio |
| Evidencia real | 30 pruebas reales pasando (`opportunity_fit` 15, `test_iris_invariants` 10, `test_contracurator` 5); piloto `ARICA-FONDART-2027` re-verificado (12.332 artefactos, 128 observaciones, 512 candidatos, hashes de manifest); corpus real de 2.034 piezas / 5.812 vinculos |
| Trabajo futuro | Montaje fisico de la obra, los cuatro talleres, la exhibicion de 4+ semanas -- todo lo declarado en el Anexo 1 como resultado del financiamiento, no como hecho ya logrado |
| Dependencia externa | Carta firmada del espacio anfitrion; cartas firmadas de los tres integrantes del equipo (formato oficial Fondart); cotizaciones reales |
| Decision del operador | Identidad/RUT/domicilio del responsable; Perfil Cultura; cual de las tres direcciones de titulo usar (seccion 3 de la bitacora); que subconjunto de assets declarar con elegibilidad publica (0 hoy) |

## Que NO esta en este paquete, y por que

- `FONDART_2027_IRIS_REGIONAL_CREACION.md` (bitacora interna de decisiones y
  evidencia, 500+ lineas): es material de trabajo del operador, no un
  documento para adjuntar. Sus cifras y hallazgos ya estan resumidos y
  citados desde `ANEXO_01` y `FUP_IRIS_GENERADO.md`.
- `FONDART_2027_IRIS_POSTULACION.md/.json`: fuente estructurada interna, no
  un anexo de postulacion.
- Ningun backup, cache ni credencial: no existen archivos de ese tipo en la
  carpeta de anexos de IRIS al momento de armar este paquete.
- Ningun dato personal (identidad, RUT, domicilio, cotizaciones): siguen
  siendo `[FALTA]` en los documentos originales y no se completaron aqui.

## Archivos incluidos

| Archivo | Rol | Estado | SHA-256 |
|---|---|---|---|
| `ANEXO_01_DESCRIPCION_PROPUESTA.md` | Descripcion artistica para adjuntar al FUP (texto fuente) | **listo** -- contenido verificado, sin datos personales | `1dab5fc7c6b6867d93213f00f75e7c0f21ab7022f706ab554c904ed03a9f1deb` |
| `ANEXO_01_DESCRIPCION_PROPUESTA.html` | Version maquetada (carta, Arial 12) del anexo anterior | **listo**, generado hoy desde el .md | `5f0755dd3dac9d26800018e0d8c083b5413453657a873c3283ab77dfd12c252a` |
| `ANEXO_01_DESCRIPCION_PROPUESTA.pdf` | Version PDF para adjuntar si la plataforma pide PDF en vez de texto pegado | **listo** -- 4 paginas, tamano carta, verificado con `pdfinfo` y `pdftotext` hoy | `e2d90e6406be45b210cb76d5872cc7aa2323f79204f7dc42e73f2405790bb304` |
| `ANEXO_02_MODELO_COMPROMISO_ESPACIO.md` | Plantilla de carta de compromiso del espacio anfitrion | **requiere operador** -- es una plantilla, no adjuntable sin completar y firmar | `7c70744d2e56044ca0673db3edab2fe4b823f451261370cb9864c24d1c2a790a` |
| `ANEXO_03_CARTAS_COMPROMISO_EQUIPO.md` | Matriz de funciones del equipo + modelo de preparacion | **requiere operador** -- hay que usar el formato oficial de Fondart, completar identidad/honorarios y firmar cada carta | `22dbe98650d3bd0410bc32678ad651d3ab450341b0c4259451b9b1c9998b85b8` |
| `CHECKLIST_ENVIO.md` | Checklist de envio (bloqueos P0, revision de plataforma, que no hacer) | **referencia interna** -- no se adjunta, se usa antes de enviar | `5028a3f11130b18393083ea98bfb4be395296ad859be70a7c6febb2460d91750` |
| `FUP_IRIS_GENERADO.md` | Borrador reproducible del validador de bases, con el desglose de puntaje y campos del FUP | **referencia interna** -- se usa para transcribir al formulario, no se adjunta como archivo | `da8fd5b7257249f3ec4fa2fd9cc892366aae8469ae7c6b6b0ddc667b7ed3ad88` |

## Bloqueos no resueltos, clasificados

- **Datos personales** (impide completar, no impide preparar): identidad y
  RUT del responsable, domicilio y region (que ademas decide si aplica el
  cierre unico del 16 de septiembre), Perfil Cultura vigente, CV firmado.
- **Decision del operador**: cual de las tres direcciones de titulo (seccion
  3 de la bitacora interna) usar; si el proyecto se ejecuta efectivamente en
  Region Metropolitana.
- **Permiso/curatoria**: 0 assets con elegibilidad publica explicita hoy --
  sin esto no hay link vivo que adjuntar; requiere decision de que mostrar y
  bajo que permiso, no codigo.
- **Gestion externa**: carta firmada del espacio anfitrion (Anexo 2),
  cartas firmadas del equipo con el formato oficial (Anexo 3), cotizaciones
  reales para reemplazar las estimaciones del presupuesto.

## Validaciones ejecutadas hoy (2026-09-07)

- `pdfinfo ANEXO_01_DESCRIPCION_PROPUESTA.pdf`: 4 paginas, 612x792 pts (carta), Producer LibreOffice 7.4.
- `pdftotext` sobre el PDF: contenido integro y legible, comparado contra el `.md` fuente.
- Barrido de la fecha de cierre vieja ("11 de septiembre") sobre todos los archivos activos de IRIS: sin coincidencias activas restantes (ver bitacora interna, ciclo 2026-09-07 20:00).
- Aritmetica del presupuesto ya verificada en ciclos anteriores: $18.000.000 solicitados (tope), responsable 37,78% (bajo el tope de 40%), imprevistos 1,67% (bajo el tope de 2%).


## Actualización 2026-09-08

`ANEXO_01_DESCRIPCION_PROPUESTA.{md,html,pdf}` se regeneró: se sumó a
`FONDART_2027_IRIS_REGIONAL_CREACION.md` §5-bis literatura sobre interfaces de
mesa compartida (Jordà et al., reacTable, ICMC 2005), estética relacional
(Bourriaud, 1998) e investigación basada en práctica (Sullivan, 2010),
conectada a decisiones concretas de esta obra -- no bibliografía decorativa --
y se agregó a este anexo un párrafo breve de fundamento de diseño (mesa
compartida, decisiones como medio). Sigue en 4 páginas, sin datos personales
ni metadatos de autor en el PDF (`pdfinfo`: Producer LibreOffice 7.4, sin
campo Author). También se agregó a `FONDART_2027_IRIS_REGIONAL_CREACION.md`
la sección 5-quater (criterios de éxito por eje de evaluación, declarados
antes de ejecutar). Ningún otro archivo de este paquete cambió.
