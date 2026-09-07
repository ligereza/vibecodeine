# Registro de auditoría — 2026-09-06

## Marco y cobertura

Decisión: determinar si cada postulación efectivamente entregada es elegible en principio, coherente, ejecutable, numéricamente correcta y honesta respecto del estado técnico. Corte 2026-09-06 America/Santiago. Lectura remota exclusivamente por SSH en modo no interactivo; sin escritura, Git, despliegues ni contactos externos.

## Fuentes y hashes

Material remoto auditado (SHA-256):

- `INFORME_FINAL.md` `1cd6ef4792208dd31bc6a335d9a3ac43e4e273b64547cb37c3550319ba51a74d`
- `LEEME_ENTREGA.md` `28b39f75c54bf1875fdd8f35b1598d850014853b70b7c24363dbff2c60d6fbb3`
- `postulaciones/01.../EXPEDIENTE.md` `668e6d6306b8ec1adcfabba48d91abc6eb3f6bf7cb77de8f60c6ecf1263dd027`
- `postulaciones/02.../EXPEDIENTE.md` `7b8ee7a61336cc58a4ed688e9ff7d96e9e00fc6fe00eaf26b0753269e9c887d3`
- `postulaciones/03.../EXPEDIENTE.md` `73e4a48d17b9520cb01a3ffde076228f3aec23ffe9d91e3e1b7446852092e4b3`
- `presupuestos/01_ama_amoedo.csv` `dcc0f4aafb4228d88da4ff342fe3019fb5efe9143f116ac68a0a1b88198e3711`
- `presupuestos/02_fondart_creacion.csv` `1411e519ba30ca002d7e3d00e8ed5c4024fb8b2b427894022c62dad39ac2cb2d`
- `presupuestos/03_fondart_formativas.csv` `876438e72582718ae5feacba5042f45fb0968357cbc28181505ca1eb71cf70ca`
- `evidencia/CIRCUITO_IRIS_COMPROBADO.md` `f4bdfeb3fc5deab65c7e87b4da71089be60b20fec84bd1b30d32d9f76b075245`
- Base Ama Amoedo 2026 `f170821183f299bace4b502d83d12efe113f81034701325de11a925de166f501`

Los hashes de PDFs Fondart están en el `fuentes/HASHES.txt` remoto; se conservaron sin editar. La fecha de los expedientes y fuentes declarada por MAK es 2026-09-06.

## Registro de búsqueda y decisiones

1. **MAPA_CONCEPTOS:** tres expedientes reales: Ama/IRIS, Fondart Creación/IRIS, Fondart Formativas/Laboratorio; JARDINES sólo aparece como alternativa, no como expediente entregado. IRIS, WACHUMA y límites de PUPILA separados por evidencia.
2. **FUENTES:** páginas oficiales Fondos Cultura abiertas; bases y resoluciones locales leídas por extracción de texto; PDF Ama 2026 contrastado con el texto y registro web transferidos.
3. **CLAIMS:** corpus y métrica apoyados por evidencia IRIS; “219 obras” rechazado por inconsistencia con `campo.json` (134 obras/219 piezas); exportación, decisiones y publicación clasificados como desarrollo futuro.
4. **MODELO CUANTITATIVO:** todos los subtotales recalculan cantidad × precio unitario. Totales: USD 9.994; CLP 18.000.000; CLP 14.900.000. Topes y porcentajes responsables/imprevistos dentro de los límites declarados.
5. **DECISIÓN:** ningún expediente es enviable al corte: Ama por formulario/identidad/portfolio; ambos Fondart por cartas firmadas y, en Creación, espacio. Acumulabilidad no confirmada; no se trató como prohibición ni autorización.

## Fuentes web primarias consultadas

- https://www.fondosdecultura.cl/creacion-artistica-innovacion-y-nuevos-formatos-creativos-fondart-regional-2027/ — estado abierto, cierre, Diseño, máximo y anexos.
- https://www.fondosdecultura.cl/actividades-formativas-fondart-regional-2027/ — objetivo, gratuidad, máximo, cierre y anexos.
- https://www.fondosdecultura.cl/investigacion-fondart-nacional-2027/ — alternativa viva, cierre y monto.
- https://www.fondosdecultura.cl/fondos/fondart-regional/preguntas-fondart-regional/ — una postulación por línea, inicio, restricción 2026.
- https://www.fundacionamaamoedo.org/programas/becas — página canónica; crawler no expuso formulario.

## Incertidumbres aceptadas y siguiente disparador

No se verificaron identidad, región, cartas, cotizaciones, formulario vivo de Ama Amoedo, usuarios externos ni integración de los cambios locales de IRIS/PUPILA. Son dependencias humanas o evidencia posterior que puede cambiar el dictamen de envío. No se buscó aprobación ni se hizo inferencia jurídica sobre acumulabilidad.

## Coste registrado

Coste financiero externo: 0; no se enviaron mensajes, no se contrataron servicios y no se modificó MAK. La sesión no expone un medidor fiable de horas o tokens facturables, por lo que no se inventa una cifra. Trabajo realizado: lectura focalizada remota, consulta de fuentes oficiales, recálculo independiente y creación de cuatro entregables locales.
