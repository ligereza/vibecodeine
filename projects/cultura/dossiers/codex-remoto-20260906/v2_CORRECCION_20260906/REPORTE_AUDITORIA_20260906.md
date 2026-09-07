# Reporte de auditoría — trabajo nuevo de Claude, corte previo a mis cambios

Fecha: 6 de septiembre de 2026. Alcance: `v2_CORRECCION_20260906/` antes de las correcciones documentales de esta revisión. La v1 quedó preservada en `v1_ENTREGA_20260906_AUDITADA/` y su sello completo pasó con `sha256sum -c` desde ese directorio.

## Dictamen ejecutivo

La v2 corrigió sustantivamente la primera auditoría. El resultado antes de mis cambios era coherente y operativo como paquete documental, aunque no enviable sin datos del titular. No encontré un error que obligara a cambiar la recomendación central: Ama Amoedo + Fondart Difusión + Fondart Formativas; Creación queda como alternativa, no como cuarta postulación simultánea.

## Hallazgos aceptados

- `curaduria.json` vacío sólo describe ese archivo/universo. La v2 rastreó la función `_portfolio_select_unlocked` y demostró persistencia real en `selections.jsonl`, `classifications.jsonl` y `common_ledger.jsonl`: 87 selecciones, 103 clasificaciones y 123 asientos del dominio `iskvw` al corte declarado.
- La brecha técnica correcta no es “construir IRIS”: es conectar inventario + decisiones humanas con un artefacto de portafolio publicable. El editor descarga JSON; el compilador de dossier no lee el inventario ni publica assets.
- Las 219 piezas están desagregadas y la tipificación no se presenta como validación autoral.
- El formulario Ama Amoedo está localizado en la anotación del PDF: `https://opencallfundacionamaamoedo.vform.io/`, verificado HTTP 200. La barrera real es el registro de cuenta del titular.
- La cuenta bancaria de Ama Amoedo es requisito para otorgación/pago, no bloqueo de postulación.
- La cláusula de mismo contenido del Anexo 3 §II.4 exige no duplicar el contenido entre Fondos/Líneas/Modalidades. La separación Difusión/Creación es por tanto una decisión de cumplimiento y diseño, no una mera preferencia.
- Formativas exige como documentos de evaluación antecedentes de estudios de quien imparte y compromiso de asistencia de al menos 15 personas. La v2 lo detectó y redujo su prioridad.
- Las cotizaciones no son obligación general: las bases las mencionan como alternativa a carta/compromiso del espacio cuando corresponde.

## Limitaciones o errores de la v2 detectados antes de corregir

1. El verificador ejecutaba 15 defectos negativos, pero `LEEME_CIERRE.md` y el texto del script decían 14.
2. La instrucción de verificar el sello v1 desde `/home/mak/CODEX REMOTO` usaba rutas relativas incorrectas; debía ejecutarse desde `v1_ENTREGA_20260906_AUDITADA`.
3. `LEEME_CIERRE.md` afirmaba que ningún expediente tenía documentos taxativos pendientes, aunque Ama Amoedo aún requiere identidad, CV y portfolio del titular. La afirmación era válida sólo para cartas de equipo en las variantes Fondart.
4. Formativas afirmaba que el software corría localmente, sin cuenta ni servidor, en los computadores participantes. La evidencia MAK no prueba esa instalación distribuida; sólo prueba servicio local y persistencia en el sistema existente.

## Estado normativo y técnico que se conserva

Las páginas oficiales consultadas el 6/9/2026 mantienen abiertas [Difusión Regional 2027](https://www.fondosdecultura.cl/difusion-fondart-regional-2027/), [Formativas Regional 2027](https://www.fondosdecultura.cl/actividades-formativas-fondart-regional-2027/) y [Creación Regional 2027](https://www.fondosdecultura.cl/creacion-artistica-innovacion-y-nuevos-formatos-creativos-fondart-regional-2027/). Todas muestran cierre 11/9 a las 15:00 para Coquimbo–Magallanes y 16/9 para las cuatro regiones nortinas exceptuadas. La región real del titular aún no consta.

El estado técnico está correctamente separado en OBSERVADO / NO PROBADO / INEXISTENTE DEMOSTRADO. Las mejoras de IRIS y PUPILA en Windows no se usan como evidencia integrada en MAK.

## Verificación de presupuesto antes de mis cambios

El verificador Linux de v2 leyó directamente los CSV y devolvió: Ama USD 8.734; Creación $12.090.000; Difusión $8.800.000; Formativas $9.266.000. Todos los topes, asignaciones del responsable, imprevistos, categorías e IDs de coste pasaron. Las cifras son presupuestos estimados, no cotizaciones obtenidas.

## Fuente y preservación

Antes de intervenir se comprobó el sello íntegro de la v1. Los hashes v2 previos de los cuatro archivos posteriormente corregidos fueron:

- `RESPUESTA_AUDITORIA.md`: `cdf1332fb33a179f4ac31f9b42d6d23b7aa9cb92ece2bc878bee0f57684393e7`
- `LEEME_CIERRE.md`: `f60274d84359ef41b56231cebb0c1411c6c1e7e2b85c48bcdf315e868ff04aeb`
- `verificador/pruebas_negativas.sh`: `4eb93a6783b5667ad00846117637b6e411875765dcaf0ff40de767e587dbb044`
- `postulaciones/03_FONDART_FORMATIVAS/TEXTO_POR_CAMPO.md`: `34afb67035d5b052b5fa149e54594610379d1febbb918942eefabf73d3f97a9f`

Este reporte describe el corte previo; el reporte de trabajo describe el estado posterior.
