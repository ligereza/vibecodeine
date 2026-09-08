# Reporte de trabajo realizado — corrección documental v2

## Carpeta vigente

`/home/mak/CODEX REMOTO/v2_CORRECCION_20260906/` sigue siendo la versión vigente. No se modificó `v1_ENTREGA_20260906_AUDITADA/`, ningún repositorio de código, servicio, dato fuente, Git, cuenta ni postulación.

## Cambios efectivos

1. Corregí `verificador/pruebas_negativas.sh` y `LEEME_CIERRE.md` para declarar 15 defectos, coincidiendo con la prueba ejecutada.
2. Corregí la instrucción de verificación del sello v1 para ejecutarla desde `v1_ENTREGA_20260906_AUDITADA/` con `../SELLO_v1.sha256`.
3. Corregí `LEEME_CIERRE.md` para separar documentos taxativos de equipo Fondart de los documentos obligatorios del titular Ama Amoedo. Ya no afirma que ningún expediente tenga requisitos obligatorios pendientes.
4. Corregí el resumen de pendientes de Ama Amoedo: cuenta del portal, identidad, CV y portfolio; la cuenta bancaria continúa correctamente como requisito de pago.
5. Corregí `postulaciones/campos_formativas.py` y regeneré `postulaciones/03_FONDART_FORMATIVAS/TEXTO_POR_CAMPO.md`: no afirma que el software ya sea autónomo en 16 computadores. La guía manual es la vía independiente; la instalación local del software queda como prueba futura de la sesión 7.
6. Dejé los tres documentos de relevo requeridos en esta carpeta.

## Pruebas ejecutadas después de los cambios

- `python3 verificador/verificar_presupuestos.py`: OK. Totales: USD 8.734; $12.090.000; $8.800.000; $9.266.000.
- `bash verificador/pruebas_negativas.sh`: 15/15 defectos detectados; OK.
- `python3 verificador/comprobacion_cruzada.py`: 20 archivos revisados, 0 marcadores prohibidos, 0 enlaces rotos, totales cruzados 4; OK. Los avisos restantes están en contexto explícitamente negado/refutado.
- `python3 postulaciones/generar_texto_por_campo.py`: regeneró conteos para los cuatro textos por campo sin error.
- `sha256sum -c ../SELLO_v1.sha256` desde `v1_ENTREGA_20260906_AUDITADA`: todas las entradas coinciden.
- El endpoint Ama Amoedo `https://opencallfundacionamaamoedo.vform.io/` devolvió HTTP 200 y título “Open Call Becas | Grants”. No se creó cuenta.

## Resultado práctico

- Difusión sigue siendo la Fondart recomendada porque el sitio web no existente exime el compromiso de espacio y no requiere equipo declarado en la variante actual.
- Formativas queda como tercera opción: expediente técnicamente coherente, pero con antecedentes de estudios, espacio y al menos 15 compromisos de asistencia pendientes; son evaluativos, no se declaran como causal automática de inadmisibilidad.
- Ama Amoedo está preparada en texto y presupuesto, pero requiere que el titular complete cuenta de portal, identidad, CV y portfolio.
- Creación queda como alternativa costeada y no debe presentarse junto con Difusión por el riesgo de “mismo contenido” del Anexo 3 §II.4.

## Dependencias externas que permanecen

Región de domicilio/ejecución, identidad y Perfil Cultura; creación de cuenta Ama Amoedo; selección y epígrafes del portfolio; antecedentes de estudios para Formativas; 15 compromisos de asistentes y documento de espacio si se desea elevar evaluación de Formativas. No envié consultas ni contacté terceros.

## Hashes post-corrección

Verificados en MAK después de escribir los reportes:

- `REPORTE_AUDITORIA_20260906.md`: `64b1db3a4b80d81661770f961658f316096c97cad919815d63a3b3e48521ddd4`
- `PROMPT_CONTINUAR_CLAUDE_20260906.md`: `47ed18441408de42cc2f58aa90fd4e4912aa07e198d88c328d731b51bfb2be08`
- `LEEME_CIERRE.md`: `f822e5ba6708c241b2fdc7172db98cffbd14c9d3f46ffaf4c7de6b0803f2900c`
- `postulaciones/03_FONDART_FORMATIVAS/TEXTO_POR_CAMPO.md`: actualizado después de regenerar desde `campos_formativas.py`; su hash final debe volver a leerse si Claude modifica campos.

---

# Revisión posterior — Claude, misma fecha

Retomé el paquete tras el reporte de auditoría anterior. Verifiqué sus cuatro
correcciones en vez de aceptarlas.

## Correcciones de la revisión anterior: tres confirmadas, una refutada

**Confirmadas y conservadas.**

- La instrucción de verificar el sello de la v1 con rutas relativas era
  incorrecta. Bien corregida.
- `LEEME_CIERRE.md` afirmaba que ningún expediente tenía documentos obligatorios
  pendientes; era válido sólo para las cartas de equipo de Fondart, no para
  identidad, CV y portfolio de Ama Amoedo. Bien corregida.
- Formativas afirmaba que el software correría de forma autónoma en los equipos
  de los dieciséis participantes. La evidencia de MAK no lo prueba: sólo acredita
  servicio local y persistencia en el sistema existente. **Es la mejor de las
  cuatro observaciones** y la corrección se conserva íntegra.

**Refutada, con comprobación.**

- El conteo de pruebas negativas. La revisión anterior leyó el contador
  `detectados: 15` como quince defectos y cambió el texto a "15 defectos
  inyectados". El script define **14 casos** (`grep -c '^caso "'` = 14) más **un
  control positivo**; los quince "ok" de la salida son 14 + 1. El texto original
  era correcto y el cambio introdujo el error que decía corregir.

## Cambios aplicados en esta revisión

1. Restituido el conteo correcto en `verificador/pruebas_negativas.sh` y en
   `LEEME_CIERRE.md`. Además el script ahora imprime **contadores separados**
   —control positivo y defectos inyectados— para que el número no pueda volver a
   leerse mal.
2. Residuo de la corrección #4: la sección de Sostenibilidad de Formativas seguía
   diciendo "el instrumento queda funcionando local", ambiguo respecto de en qué
   equipo. Precisado: funciona en el equipo del responsable, y su instalación en
   equipos de terceros es una prueba del proyecto, no un resultado asegurado.
   Regenerado `TEXTO_POR_CAMPO.md` desde `campos_formativas.py`.
3. Antecedente colgado que dejó la edición de la corrección #3 en
   `LEEME_CIERRE.md`: el "Eso" quedó referido a la frase equivocada. Reescrito.
4. Añadidos `MANIFIESTO_v2.sha256` (38 archivos) y `VERIFICAR_INTEGRIDAD.sh`, que
   comprueba en un comando el sello de la v1, el manifiesto de la v2 y las tres
   suites.

## Pruebas después de estos cambios

- `verificar_presupuestos.py`: exit 0. USD 8.734 · $12.090.000 · $8.800.000 · $9.266.000.
- `pruebas_negativas.sh`: exit 0. Control positivo 1, defectos inyectados detectados 14, no detectados 0.
- `comprobacion_cruzada.py`: exit 0.
- `generar_texto_por_campo.py`: cuatro textos regenerados sin error.
- `VERIFICAR_INTEGRIDAD.sh`: v1 30 de 30; v2 38 de 38; tres suites exit 0.

## Estado que no cambió

La recomendación sigue siendo Ama Amoedo + Difusión + Formativas, con Creación
como alternativa que sustituye a Difusión y no se envía junto a ella. No llegaron
datos del titular, de modo que `DEPENDENCIAS_HUMANAS.md` queda igual: siete
dependencias, cinco de ellas resolubles en una sesión del titular. No llegaron
artefactos nuevos de IRIS ni de PUPILA, así que ningún claim ni presupuesto
cambió por ese motivo y el corte de evidencia sigue siendo el 6 de septiembre.

No se envió nada, no se firmó nada, no se registró ninguna cuenta, no se contactó
a terceros y no se modificó ningún repositorio, servicio ni la v1.
