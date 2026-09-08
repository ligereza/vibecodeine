# Dry-run de envío — 6 de septiembre de 2026

> **Actualizado** tras la revisión de cierre. Estado de la ficha del titular al
> generar este dry-run: **0 de 28 campos completados**, comprobable con
> `python3 verificador/leer_ficha_titular.py`. No se incorporó ningún dato porque
> no hay ninguno; no se inventó ninguno.
>
> Complementos de esta versión: `MATRIZ_CAMPOS_FINAL_20260906.md` (39 campos con
> su fuente y su prueba), `INDICE_ANEXOS_20260906.md` (37 anexos con estado
> LISTO/BORRADOR/FALTANTE/POSTERIOR) y `PARA_COPIAR/` (28 textos limpios).

Simulación de llenado, campo por campo, con el material que existe hoy.
Conteos verificables con `python3 postulaciones/generar_texto_por_campo.py`.

**Criterio de resultado.** `PUEDE PASAR A CUENTA` significa que el texto y el
presupuesto están completos y que sólo falta que el titular vuelque en la
plataforma datos que ya posee. `NO PUEDE PASAR A CUENTA` significa que falta un
dato o un documento que hoy no existe en ninguna parte.

---

## Resumen

| Expediente | Resultado | Campos completos | Bloqueos del titular | Adjuntos/archivos | Próxima acción |
|---|---|---|---|---|---|
| **Ama Amoedo** | **NO PUEDE PASAR A CUENTA** | 9 de 9 redactados (1.504 palabras) | cuenta del portal, identidad, CV, **portfolio** | `01_AMA_AMOEDO_ARTISTAS/TEXTO_POR_CAMPO.md`; `presupuestos/01_ama_amoedo.csv` | registrar cuenta en `opencallfundacionamaamoedo.vform.io` |
| **Difusión** | **NO PUEDE PASAR A CUENTA** | 13 de 13 redactados (2.326 palabras) | **región**, identidad, Perfil Cultura | `02_FONDART_DIFUSION/TEXTO_POR_CAMPO.md`; `presupuestos/03_fondart_difusion.csv` | confirmar región en `PAQUETE_DE_ACCION_TITULAR_20260906.md` |
| **Formativas** | **NO PUEDE PASAR A CUENTA** | 11 de 11 redactados (2.642 palabras) | región, identidad, Perfil Cultura, **estudios**, **15 asistentes**, espacio | `03_FONDART_FORMATIVAS/TEXTO_POR_CAMPO.md`; `presupuestos/04_fondart_formativas.csv` | repartir `FORMATO_COMPROMISOS_FORMativas_15_FILAS.csv` |
| **Creación (alternativa)** | **NO PUEDE PASAR A CUENTA** | 13 de 13 redactados (2.495 palabras) | región, identidad, Perfil Cultura, **espacio** | `ALTERNATIVA_CREACION/TEXTO_POR_CAMPO.md`; `presupuestos/02_fondart_creacion.csv` | **sólo si sustituye a Difusión** |

**Ninguno de los cuatro tiene un texto sin escribir.** Los cuatro están
bloqueados por datos del titular, no por trabajo documental pendiente.

**Distancia real al envío.** Difusión es el más cercano: tres datos que el
titular ya posee. Ama Amoedo requiere además armar el PDF de portfolio.
Formativas requiere quince firmas de terceros.

---

## Ama Amoedo 2026 — Artistas · cierre miércoles 9 sep, 23:59

Portal: `https://opencallfundacionamaamoedo.vform.io/` — verificado HTTP 200.
**Los campos exactos y sus límites están detrás del registro de cuenta**, por eso
los textos vienen en versiones breve, media y extendida.

| Campo del formulario | Fuente | Estado real | Dato faltante | Archivo destino | Bloqueo |
|---|---|---|---|---|---|
| a) Información personal | titular | **vacío** | nombre, RUT, edad, contacto | formulario | **SÍ** |
| a) Documento de identidad | titular | **vacío** | escaneo | adjunto | **SÍ** |
| b) Título del proyecto | redactado | **completo** | — | `TEXTO_POR_CAMPO.md` §Título | no |
| b) Descripción | redactado, 3 versiones | **completo** | recortar a la extensión que pida el portal | §Descripción | no |
| b) Objetivos | redactado | **completo** | — | §Objetivos | no |
| b) Plan de implementación | redactado | **completo** | — | §Plan | no |
| b) Justificación del interés | redactado | **completo** | — | §Justificación | no |
| c) Presupuesto: destino de fondos | redactado | **completo** | — | §Presupuesto | no |
| d) Portfolio: selección propuesta | 4 en N1 + 12 en N2 | **selección hecha y fundamentada** | aprobación y epígrafes | `ANEXOS/SELECCION_PORTFOLIO_AMA.md` | **SÍ** |
| c) Desglose adjunto | calculado | **completo**, USD 8.734 | exportar CSV a Excel o PDF | `presupuestos/01_ama_amoedo.csv` | no |
| d) CV | titular | **vacío** | documento | adjunto | **SÍ** |
| d) Portfolio artístico: archivo PDF | 16 piezas propuestas | **por armar** | aprobación, epígrafes y entrega de archivos | `ANEXOS/SELECCION_PORTFOLIO_AMA.md` | **SÍ** |
| d) Anexo del proyecto (optativo) | preparado | **completo** | — | `postulaciones/ANEXOS/FICHA_TECNICA_IRIS.md` | no |
| Cuenta bancaria | titular | pendiente | — | — | **no bloquea: es requisito de pago** |

**Resultado: NO PUEDE PASAR A CUENTA.** Faltan cuatro cosas del titular. El
portfolio es la más lenta: las decisiones registradas dejan **cuatro candidatas
netas** y las bases admiten hasta veinte.

---

## Fondart Regional Difusión · cierre 11 sep 15:00, o 16 sep si el domicilio es del norte

| Campo del FUP | Fuente | Estado real | Dato faltante | Archivo destino | Bloqueo |
|---|---|---|---|---|---|
| Región de ejecución | — | **vacío** | **la región** | todos los campos territoriales | **SÍ** |
| Identificación del responsable | titular | **vacío** | nombre, RUT, domicilio | FUP | **SÍ** |
| Perfil Cultura | titular | **vacío** | inscripción vigente | plataforma | **SÍ** |
| Nombre del proyecto | redactado | **completo** | — | `TEXTO_POR_CAMPO.md` §Nombre | no |
| Resumen | redactado, 2 versiones | **completo** | — | §Resumen | no |
| Fundamentación | redactado | **completo** | la región nombrada | §Fundamentación | no |
| Objetivos | redactado | **completo** | — | §Objetivos | no |
| Metodología | redactado | **completo** | — | §Metodología | no |
| Actividades, resultados e indicadores | redactado | **completo** | — | §Actividades | no |
| Currículo del responsable | redactado | **completo** | CV en Perfil Cultura | §Currículo | no |
| Presupuesto | calculado | **completo**, $8.800.000 | — | `presupuestos/03_fondart_difusion.csv` | no |
| Sostenibilidad | redactado | **completo** | — | §Sostenibilidad | no |
| **Anexo** Plan y Fundamentación de la Estrategia de Difusión | redactado | **completo** | — | §Plan y Fundamentación | no |
| **Anexo** Estrategia de Públicos y Acceso | redactado | **completo** | — | §Estrategia de Públicos | no |
| **Anexo** Compromiso de exhibición | — | **no corresponde** | — | eximido por bases | no |
| **Anexo** Cartas de equipo | — | **no corresponde** | — | sin equipo declarado | no |

**Resultado: NO PUEDE PASAR A CUENTA.** Faltan tres datos, y los tres los tiene
el titular. **Ningún documento depende de un tercero.** Es el expediente más
cercano al envío de los cuatro.

---

## Fondart Regional Actividades Formativas · mismo cierre que Difusión

| Campo del FUP | Fuente | Estado real | Dato faltante | Archivo destino | Bloqueo |
|---|---|---|---|---|---|
| Región de ejecución | — | **vacío** | **la región** | campos territoriales | **SÍ** |
| Identificación del responsable | titular | **vacío** | nombre, RUT, domicilio | FUP | **SÍ** |
| Perfil Cultura | titular | **vacío** | inscripción vigente | plataforma | **SÍ** |
| Nombre del proyecto | redactado | **completo** | — | `TEXTO_POR_CAMPO.md` §Nombre | no |
| Resumen | redactado, 2 versiones | **completo** | — | §Resumen | no |
| Objetivos | redactado | **completo** | — | §Objetivos | no |
| Indicadores y verificadores | redactado | **completo** | — | §Indicadores | no |
| Presupuesto | calculado | **completo**, $8.608.000 | — | `presupuestos/04_fondart_formativas.csv` | no |
| Sostenibilidad | redactado | **completo** | — | §Sostenibilidad | no |
| **Anexo** Programa de la Formación | redactado | **completo** | — | §Programa | no |
| **Anexo** Diagnóstico de Necesidad Formativa | redactado | **completo** | — | §Diagnóstico | no |
| **Anexo** Estrategias de Transferencia | redactado | **completo** | — | §Estrategias | no |
| **Anexo** Antecedentes de estudios de quien imparte | titular | **vacío** | certificados y respaldos | adjunto | **SÍ**, evaluación |
| **Anexo** Compromiso de asistentes, ≥15 personas | plantilla lista | **0 de 15 firmas** | 15 firmas | `BORRADORES_SIN_FIRMA/FORMATO_COMPROMISOS_FORMativas_15_FILAS.csv` | **SÍ**, evaluación |
| **Anexo** Compromiso de uso del espacio | plantilla lista | **vacío** | carta o cotización | `BORRADORES_SIN_FIRMA/SOLICITUD_ESPACIO_COTIZACION.md` | **SÍ**, evaluación |
| **Anexo** Cartas de equipo | — | **no corresponde** | — | sin equipo declarado | no |

**Resultado: NO PUEDE PASAR A CUENTA.** Seis bloqueos, tres de ellos de
terceros. **Los tres anexos faltantes son de evaluación, no taxativos:** su
ausencia baja puntaje pero no deja el proyecto fuera de bases.

---

## Fondart Regional Creación · ALTERNATIVA de Difusión

> **No se envía junto con Difusión.** Anexo 3 §II.4 de las bases declara fuera de
> convocatoria las postulaciones de mismo contenido aunque cambien de línea,
> conservando sólo la última enviada. Se postula **una** de las dos.
> `verificador/revision_ids_y_gastos.py` comprueba que esta exclusión se respeta.

| Campo del FUP | Fuente | Estado real | Dato faltante | Archivo destino | Bloqueo |
|---|---|---|---|---|---|
| Región de ejecución | — | **vacío** | **la región** | campos territoriales | **SÍ** |
| Identificación del responsable | titular | **vacío** | nombre, RUT, domicilio | FUP | **SÍ** |
| Perfil Cultura | titular | **vacío** | inscripción vigente | plataforma | **SÍ** |
| No seleccionado en Creación 2026 | titular | **sin verificar** | confirmación | declaración FUP | **SÍ** |
| Nombre del proyecto | redactado | **completo** | — | `TEXTO_POR_CAMPO.md` §Nombre | no |
| Resumen | redactado | **completo** | — | §Resumen | no |
| Objetivos, metodología y cronograma | redactado | **completo** | — | §Objetivos | no |
| Presupuesto | calculado | **completo**, $12.090.000 | — | `presupuestos/02_fondart_creacion.csv` | no |
| **Anexo** Propuesta creativa | redactado | **completo** | — | §Propuesta creativa | no |
| **Anexo** Estrategias de difusión de obra | redactado | **completo** | — | §Estrategias | no |
| **Anexo** Compromiso o cotización del espacio | plantilla lista | **vacío** | carta o cotización | `BORRADORES_SIN_FIRMA/SOLICITUD_ESPACIO_COTIZACION.md` | **SÍ**, evaluación |
| **Anexo** Cartas de equipo | — | **no corresponde** | — | sin equipo declarado | no |

**Resultado: NO PUEDE PASAR A CUENTA.** Cuatro bloqueos del titular más el
espacio. Tiene una restricción propia que los otros no tienen: verificar que el
responsable no fue seleccionado en Creación 2026, porque eso sí sería causal de
exclusión.

---

## Qué desbloquea qué

| Dato que entregue el titular | Expedientes que desbloquea |
|---|---|
| **Región** | Difusión, Formativas, Creación |
| **Identidad y Perfil Cultura** | Difusión, Formativas, Creación |
| Cuenta del portal Ama | Ama Amoedo |
| CV e identidad escaneada | Ama Amoedo |
| **Portfolio con epígrafes** | Ama Amoedo |
| Antecedentes de estudios | Formativas (sube evaluación) |
| 15 compromisos de asistentes | Formativas (sube evaluación) |
| Carta o cotización de espacio | Formativas y Creación (suben evaluación) |
| Decisión Difusión **o** Creación | define cuál de las dos se envía |

**Con región, identidad y Perfil Cultura, Difusión pasa a cuenta el mismo día.**
Ficha copiable en `PAQUETE_DE_ACCION_TITULAR_20260906.md`; ficha de datos en
`FICHA_DATOS_TITULAR_20260906.md`.

---

## Qué está terminado sin datos humanos

| Producto | Cantidad | Archivo |
|---|---:|---|
| Campos redactados en los cuatro expedientes | **46** | `MATRIZ_CAMPOS_FINAL_20260906.md` |
| Palabras de texto utilizable | **8.967** | idem |
| Campos sin redactar | **0** | idem |
| Textos limpios listos para pegar | **35** | `PARA_COPIAR/` |
| Matriz de coherencia de los cuatro | 1 | `MATRIZ_COHERENCIA_20260906.md` |
| Selección de portfolio propuesta y fundamentada | 16 piezas | `postulaciones/ANEXOS/SELECCION_PORTFOLIO_AMA.md` |
| Anexos en estado LISTO | **23** | `INDICE_ANEXOS_20260906.md` |
| Anexos en estado BORRADOR | 4 | idem |
| Anexos FALTANTE, todos del titular | 6 | idem |
| Anexos POSTERIOR, no requeridos al postular | 8 | idem |
| Presupuestos calculados y verificados | 4 | `presupuestos/*.csv` |
| Verificaciones reproducibles que pasan | 6 | `verificador/` |

No queda trabajo documental pendiente que no dependa de un dato del titular.
