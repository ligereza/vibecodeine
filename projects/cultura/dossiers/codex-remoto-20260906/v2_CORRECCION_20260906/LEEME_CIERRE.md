# Cierre de corrección — versión vigente

**6 de septiembre de 2026.** Esta carpeta, `v2_CORRECCION_20260906/`, es la
**versión vigente**.

## Entregables de relevo

- `REPORTE_AUDITORIA_20260906.md`: corte del trabajo nuevo de Claude antes de la intervención de Luna.
- `REPORTE_TRABAJO_REALIZADO_20260906.md`: cambios efectivamente aplicados y pruebas posteriores.
- `PROMPT_CONTINUAR_CLAUDE_20260906.md`: encargo autónomo para el siguiente relevo.
- `FICHA_DATOS_TITULAR_20260906.md`: ficha única para completar los bloqueos humanos.
- `CONTINUACION_CLAUDE_CIERRE_20260906.md`: orden para cerrar teoría y preparar anexos demostrables en paralelo.
- `PROMPT_CLAUDE_TRABAJO_AUTONOMO_20260906.md`: encargo autónomo para decidir y cerrar todo lo no personal.
- `FORMULARIO_UNICO_DATOS_PERSONALES_20260906.md`: único formulario que debe completar el titular.
- `evidencia/MAPA_SISTEMAS_AUTORALES_MAK_20260906.md`: mapa de sistemas, prototipos, procesos y evidencia autoral.
- `postulaciones/ANEXOS/PORTFOLIO_SISTEMAS_MAK_AMA_20260906.md`: dossier de portfolio basado en sistemas reales de MAK.
- `MATRIZ_CIERRE_EVIDENCIA_POSTULACIONES_20260906.md`: campo por campo, fuente, anexo y estado de cada expediente.
- `postulaciones/ANEXOS/INDICE_EVIDENCIA_SISTEMAS_MAK_20260906.md`: clasificación operativa de IRIS, Grados, Jardines y Tapiz, con fuente y uso permitido.
- `PROMPT_CLAUDE_CONTINUACION_SISTEMAS_MAK_20260906.md`: orden de continuación para convertir la evidencia de MAK en textos y anexos postulables.


La versión auditada quedó congelada e intacta en
`../v1_ENTREGA_20260906_AUDITADA/`, con sello de integridad en
`../SELLO_v1.sha256`. Verifiqué los hashes de la auditoría contra la v1
antes de tocar nada: **coinciden**.

---

## 1. Lo que cambió el dictamen

Cinco hallazgos de esta corrección modifican conclusiones de la v1 o de la
auditoría. Los cinco tienen fuente citable.

| # | Hallazgo | Efecto |
|---|---|---|
| 1 | **La curaduría humana sí está persistida y ejercida.** 87 decisiones en 14 sesiones entre el 7 de agosto y el 2 de septiembre de 2026, con 9 reversiones reales y 65 descartes con motivo "no es obra" | Cae la afirmación central de la v1: "cero decisiones, bucle sin ejercer". `curaduria.json` vacío sólo describía ese archivo |
| 2 | **El formulario de Ama Amoedo estaba en el propio PDF de bases**, como anotación de enlace: `opencallfundacionamaamoedo.vform.io` | Deja de ser un pendiente indefinido. La barrera real es crear una cuenta |
| 3 | **Existe una cláusula que gobierna las postulaciones múltiples:** Anexo 3, §II.4 de las tres bases, sobre identidad de contenido | La acumulabilidad deja de ser una incógnita para consultar. Cambia el diseño del paquete |
| 4 | **Formativas exige quince compromisos de asistencia** y antecedentes de estudios de quien imparte. Ni la v1 ni la auditoría lo detectaron | Baja Formativas al tercer lugar |
| 5 | **"Cotización" aparece una vez en Creación, una en Difusión y ninguna en Formativas**, siempre como alternativa a la carta del espacio | Las cotizaciones dejan de ser un bloqueo. No son obligatorias |

Detalle punto por punto en **`RESPUESTA_AUDITORIA.md`**, que responde A1-A4,
F1-F4, N1-N4 y las siete precisiones de Faro con aceptado, refutado o parcial,
evidencia, cambio aplicado y comprobación.

---

## 2. La recomendación, y por qué cambió

La v1 recomendaba Ama Amoedo + Creación + Formativas. La v2 recomienda:

| | Convocatoria | Proyecto | Solicitado | Firmas de terceros |
|---|---|---|---|---|
| **1** | Becas Ama Amoedo 2026 — Artistas | Ordenar el propio archivo | **US$8.734** de 10.000 | **ninguna** |
| **2** | Fondart Regional 2027 — **Difusión** | Superficie pública de obras | **$8.800.000** de 18.000.000 | **ninguna** |
| **3** | Fondart Regional 2027 — Actividades Formativas | Laboratorio del método, **modalidad mixta** | **$8.608.000** de 15.000.000 | 15 compromisos de asistencia |

**Alternativa costeada:** `postulaciones/ALTERNATIVA_CREACION/`, que **sustituye**
a Difusión si el titular prefiere producir una obra exhibible. **No se postulan
las dos.**

### Los tres motivos del cambio

**Primero, normativo.** El Anexo 3 §II.4 declara fuera de convocatoria las
postulaciones de *"mismo contenido"* aunque cambien de Fondo, Línea o Modalidad,
conservando sólo la última enviada. Presentar el mismo instrumento en Creación y
en Difusión es exactamente ese caso. Se postula una.

**Segundo, de dependencias.** Difusión es la única línea cuyas bases **eximen** el
compromiso del espacio cuando el soporte es *"un medio de difusión no existente
(ejemplo: un sitio web) y que será desarrollado por el proyecto en concurso"*.
Sin equipo declarado y sin espacio que pedir, **no depende de la firma de nadie**.

**Tercero, de dirección.** La instrucción fue simplificar alrededor de una
herramienta durable y no convertir el proyecto en una instalación vistosa que
sustituya al motor. Difusión financia exactamente la brecha verificada —que el
archivo decidido llegue a ser público— sin mesa, sin montaje y sin equipamiento.
Creación financia una instalación. Por eso una es la recomendada y la otra la
alternativa.

---

## 3. Qué hay en cada carpeta

### Para decidir
- **`LEEME_CIERRE.md`** — este archivo
- **`RESPUESTA_AUDITORIA.md`** — A1-A4, F1-F4, N1-N4 y las precisiones de Faro
- **`MATRIZ_REQUISITOS.md`** — fuente exacta, momento de exigencia, evidencia y estado
- **`DEPENDENCIAS_HUMANAS.md`** — las siete cosas que no puedo resolver

### Para completar y enviar
- **`FICHA_DATOS_TITULAR_20260906.md`** — la ficha que el titular rellena
- **`PAQUETE_DE_ACCION_TITULAR_20260906.md`** — ficha copiable en 4 bloques
- **`DRY_RUN_ENVIO_20260906.md`** — dry-run campo por campo de los cuatro expedientes
- **`MATRIZ_CAMPOS_FINAL_20260906.md`** — 39 campos con fuente, estado, dato pendiente y prueba
- **`INDICE_ANEXOS_20260906.md`** — 41 anexos con estado LISTO / BORRADOR / FALTANTE / POSTERIOR
- **`MATRIZ_COHERENCIA_20260906.md`** — título → idea → concepto → área → metodología → resultados → presupuesto → anexos, de los cuatro
- **`postulaciones/ANEXOS/SELECCION_PORTFOLIO_AMA.md`** — 16 piezas propuestas por nivel de procedencia, con epígrafes y alertas de dato
- **`PARA_COPIAR/`** — 35 textos limpios, sin formato, listos para pegar o imprimir

### Postulaciones
- `postulaciones/01_AMA_AMOEDO_ARTISTAS/TEXTO_POR_CAMPO.md`
- `postulaciones/02_FONDART_DIFUSION/TEXTO_POR_CAMPO.md`
- `postulaciones/03_FONDART_FORMATIVAS/TEXTO_POR_CAMPO.md`
- `postulaciones/ALTERNATIVA_CREACION/TEXTO_POR_CAMPO.md`
- `postulaciones/generar_texto_por_campo.py` — recalcula los conteos
- `postulaciones/BORRADORES_SIN_FIRMA/` — **todo lo de esa carpeta es borrador**

### Presupuestos y verificación
- `presupuestos/0{1..4}_*.csv` — con `id_coste`, actividad, periodo, producto y proyecto que paga
- `presupuestos/TRAZABILIDAD_COSTES.md` — por qué ningún gasto se paga dos veces
- `verificador/verificar_presupuestos.py` — lee los CSV, aritmética decimal, **sale con 1 ante cualquier inconsistencia**
- `verificador/pruebas_negativas.sh` — control positivo mas 14 defectos inyectados, los 14 detectados
- `verificador/comprobacion_cruzada.py` — contradicciones, marcadores, adjuntos, totales y afirmaciones sin fuente
- `verificador/revision_ids_y_gastos.py` — IDs únicos, gastos comunes duplicados y exclusión de las dos líneas
- `verificador/leer_ficha_titular.py` — qué campos completó el titular y qué desbloquean
- `verificador/generar_indice_anexos.py` — regenera el índice de anexos con datos reales de archivo
- `VERIFICAR_INTEGRIDAD.sh` — un comando: sellos, manifiesto, cinco suites y estado de la ficha

### Evidencia y tiempos
- `evidencia/ESTADO_TECNICO_VERIFICADO.md` — observado / no probado / inexistente demostrado
- `evidencia/prueba_estado.sh` y su salida — solo lectura, reproducible
- `cronogramas/CARGA_Y_ESCENARIOS.md` — carga del responsable en ocho escenarios
- `cronogramas/PREPARACION_HASTA_EL_ENVIO.md` y `EJECUCION_2027.md`

---

## 4. Estado de cada convocatoria, sin eufemismos

La auditoría escribió "actualmente fuera de convocatoria". No corresponde: nadie
ha dictado ninguna exclusión y no hay ninguna postulación enviada. Los cuatro
estados separados están en `MATRIZ_REQUISITOS.md` §1. Aplicados:

| | Convocatoria | Elegibilidad | Expediente | Inadmisibilidad |
|---|---|---|---|---|
| **Ama Amoedo** | **abierta**, cierra 9 sep 23:59 | elegible salvo datos del titular | completo salvo identidad, CV y portfolio | **ninguna** |
| **Difusión** | **abierta**, cierra 11 o 16 sep 15:00 | elegible salvo datos del titular | **completo**: ningún documento pendiente de tercero | **ninguna** |
| **Formativas** | **abierta**, mismo cierre | elegible salvo datos del titular | completo salvo 15 compromisos, antecedentes de estudios y espacio, **todos de evaluación, ninguno taxativo** | **ninguna** |

En las variantes Fondart recomendadas no falta hoy un documento taxativo por equipo,
porque no se declara equipo de trabajo y las cartas son exigibles sólo "si corresponde".
Ama Amoedo sí mantiene documentos obligatorios del titular pendientes: identidad,
CV y portfolio.

Prescindir del equipo en las variantes Fondart no se hizo cambiando etiquetas: se
rehizo el alcance, se eliminaron funciones y se recalcularon presupuestos y metas.
El razonamiento y su límite están en `MATRIZ_REQUISITOS.md` §9.

---

## 5. ¿Es enviable el paquete?

La dirección pidió demostrarlo o identificar exactamente qué lo impide.

**Difusión es enviable en cuanto el titular complete el FUP.** No requiere firma,
cotización ni documento de ningún tercero. Lo que falta es su identidad, su
Perfil Cultura y confirmar su región.

**Ama Amoedo queda preparada salvo lo que sólo tiene el titular:** completar la
cuenta del portal, aportar identidad, CV y portfolio. Y aquí hay un dato que conviene saber hoy y no el martes: las
decisiones ya registradas dejan **cuatro candidatas netas**, y las bases admiten
hasta veinte imágenes. **Cuatro no alcanza.** Tendrá que seleccionar el resto con
su propio criterio; son unas horas de trabajo suyo.

**Formativas es enviable con menor puntaje** mientras no se reúnan los quince
compromisos de asistencia. No es un impedimento: es una pérdida de puntos en el
criterio que menos pondera.

**Lo que impide enviar hoy, exactamente:** datos y decisiones del titular
—región, identidad y Perfil Cultura, cuenta en el portal de Ama Amoedo, selección
del portfolio, CV y antecedentes de estudios si va Formativas— más identidad como
adjunto de Ama Amoedo y, sólo para el tercer expediente, quince firmas. Nada más. Están agrupados en
`DEPENDENCIAS_HUMANAS.md` para una sola sesión de unos cuarenta minutos, salvo el
portfolio y las firmas.

---

## 6. Cómo comprobar este paquete sin creerme

Un solo comando comprueba integridad de ambas versiones y las tres suites:

```bash
bash "/home/mak/CODEX REMOTO/v2_CORRECCION_20260906/VERIFICAR_INTEGRIDAD.sh"
```

Comprueba que la v1 congelada sigue coincidiendo con `../SELLO_v1.sha256`, que la
v2 coincide con `MANIFIESTO_v2.sha256`, y que las tres suites salen con 0.

Por separado:

```bash
cd "/home/mak/CODEX REMOTO/v2_CORRECCION_20260906"
bash evidencia/prueba_estado.sh                   # estado tecnico, solo lectura
python3 verificador/verificar_presupuestos.py     # sale 1 si algo no cuadra
bash verificador/pruebas_negativas.sh             # control positivo + 14 defectos inyectados
python3 verificador/comprobacion_cruzada.py       # contradicciones y coherencia del paquete
python3 cronogramas/carga.py                      # carga del responsable por escenario
python3 postulaciones/generar_texto_por_campo.py  # recalcula los conteos
```

El sello de la v1 se comprueba **desde dentro de su carpeta**, porque sus rutas
son relativas:

```bash
cd "/home/mak/CODEX REMOTO/v1_ENTREGA_20260906_AUDITADA" && sha256sum -c ../SELLO_v1.sha256
```

Si se edita cualquier archivo de la v2, el manifiesto queda desfasado a propósito.
Regenerarlo sólo cuando el cambio sea intencional:

```bash
cd "/home/mak/CODEX REMOTO/v2_CORRECCION_20260906"
find . -type f ! -name MANIFIESTO_v2.sha256 ! -path "*/__pycache__/*" | sort | xargs sha256sum > MANIFIESTO_v2.sha256
```

---

## 7. Alcance respetado

No se envió ninguna postulación, no se contactó a nadie, no se registró ninguna
cuenta, no se publicó nada. No se tocaron los repositorios de vibecodeine, flujo,
WACHUMA ni FARMAXIA; se leyeron de forma focalizada sólo donde sostenían una
afirmación. No se hizo ninguna operación de Git, no se reinició ningún servicio y
no se modificó ningún dato de IRIS: la prueba técnica sólo lee, y su único POST
es un control que debe fallar. El historial de la v1 se conserva íntegro.
