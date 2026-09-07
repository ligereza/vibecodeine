# Auditoría sustantiva de postulaciones MAK

## 1. Corte, material y método

Auditoría independiente realizada el 6 de septiembre de 2026. Se leyó el traspaso, el informe final, los tres expedientes, anexos, CSV, evidencia técnica, registro de citas, bases PDF y resoluciones conservadas en MAK. Se consultaron las páginas oficiales vigentes de Fondos Cultura el mismo día. No se modificó ningún archivo remoto.

Material central auditado:

- `/home/mak/CODEX REMOTO/INFORME_FINAL.md`, `/home/mak/CODEX REMOTO/LEEME_ENTREGA.md`, `AVANCES_Y_TRASPASO.md`, `PROMPT_CONTINUIDAD_MAK.md`.
- `postulaciones/01_AMA_AMOEDO_ARTISTAS/EXPEDIENTE.md`, `02_FONDART_CREACION_IRIS/EXPEDIENTE.md`, `03_FONDART_FORMATIVAS_LABORATORIO/EXPEDIENTE.md`.
- `presupuestos/*.csv`, `VERIFICACION_TOPES.md`, `ESCENARIOS_DE_ADJUDICACION.md`.
- `evidencia/CIRCUITO_IRIS_COMPROBADO.md`, `MAPA_DE_FUNCIONES.md`, `fuentes/REGISTRO_DE_CITAS.md`.
- Base Ama Amoedo recuperada en `/home/mak/BASES/postulaciones/03-becas-fundacion-ama-amoedo-2026/01_BASE_ORIGINAL_AMA_AMOEDO_2026.pdf`.

Los hashes y el registro de estado completo están en `work/agent-ledger/2026-09-06/research.md`.

## 2. Veredicto por convocatoria

### 2.1 Ama Amoedo 2026 — Artistas / “Dimensiones del Orden”

**Veredicto: no verificable para envío; corregible.** El PDF 2026 conservado indica cuatro becas de USD 10.000 para artistas visuales, archivo/preservación del propio trabajo como ejemplo admisible, un titular único, mayoría de edad, conexión latinoamericana, cuenta bancaria a nombre del titular si se adjudica, CV, portfolio y presupuesto; cierre 9/9/2026 a las 23:59 hora de Uruguay. El PDF tiene hash `f170821...f501` y fue recuperado desde el enlace público registrado por Claude. La página oficial consultada no expuso el formulario vivo, por lo que el portal y sus límites de campos siguen no verificados.

**Lo que sí encaja:** archivo propio, creación/investigación artística, trabajo de curaduría y publicación no comercial. El presupuesto queda bajo el máximo y la propuesta reconoce que la salida de portafolio aún no existe.

**Bloqueos:** identidad, edad, CV, portfolio artístico real, cuenta bancaria, declaraciones de incompatibilidad y URL/formulario. La ficha Markdown de corpus no equivale todavía al portfolio PDF exigido. También debe aclararse que “219 obras” es incorrecto: la evidencia separa 219 piezas procesadas de 134 tipificadas como obra.

**Corrección necesaria:** mantener el proyecto, corregir el claim numérico, adjuntar un portfolio artístico independiente y no enviar hasta verificar formulario y documentos del titular.

### 2.2 Fondart Regional 2027 — Creación Artística / Diseño / “IRIS: Mesa de Montaje”

**Veredicto: corregible; actualmente fuera de convocatoria por anexos faltantes.** La página oficial vigente confirma estado abierto, cierre RM 11/9/2026 a las 15:00, monto máximo $18.000.000 y que Diseño financia obras, piezas, dispositivos, sistemas, juegos o experiencias originales con participación de públicos. La base PDF, §I.3 y §I.7, confirma exhibición de la obra final, ítems Operación/Personal/Inversión/Imprevistos, asignación del responsable hasta 40% y gastos imprevistos hasta 2%. La base, Anexo 3, exige carta firmada por cada integrante esencial del equipo; Anexo 2 exige compromiso/cotización del espacio existente cuando corresponde.

**Encaje:** Diseño es más sólido que Artes de la Visualidad para una mesa/dispositivo de participación. El espacio y la exhibición no son accesorios: el expediente los promete y por eso necesita compromiso del espacio. La evidencia técnica acredita base funcional, no obra exhibible terminada.

**Problemas:** tres roles esenciales figuran “por nombrar” y sin cartas; el espacio también está pendiente. El resumen abre describiendo decisiones del visitante y documento de salida como si el flujo ya operara, aunque la prueba dice que el bucle tiene cero decisiones y sólo descarga JSON. Debe formularse como resultado a construir dentro del proyecto. “219 piezas” debe reemplazar “219 obras” cuando se use esa cifra.

**Presupuesto auditado:** $18.000.000 exactos; Personal $11.450.000, Operación $3.100.000, Inversión $3.130.000, Imprevistos $320.000. Responsable $7.000.000 = 38,89%; imprevistos = 1,78%. Las cifras son aritméticamente correctas, pero computador, pantalla/proyector, espacio y parte de servicios son estimaciones. La pertinencia del 100% de inversión se evaluará según adquisición y destino posterior.

**Corrección necesaria:** obtener cartas o eliminar roles y rehacer presupuesto; obtener carta/cotización del espacio; reescribir presente/futuro; separar el hosting y registro documental de otros expedientes mediante servicios y resultados inequívocamente distintos.

### 2.3 Fondart Regional 2027 — Actividades Formativas / “Laboratorio Dimensiones del Orden”

**Veredicto: corregible; actualmente fuera de convocatoria por cartas faltantes.** La página oficial confirma que la línea financia proyectos colectivos, talleres/laboratorios/tutorías gratuitos orientados a transferencia efectiva, con máximo $15.000.000 y cierre RM 11/9 a las 15:00. La base permite postular a personas naturales mayores de 18 y no contiene ítem Inversión; sí contempla Operación, Personal e Imprevistos.

**Encaje:** el laboratorio es pertinente si la necesidad formativa se presenta como hipótesis comprobable desde la experiencia propia, con método gratuito y verificadores. El presupuesto no depende de comprar equipamiento. La guía manual puede ser una mitigación razonable si se la presenta como diseño del proyecto, no como transferencia ya validada.

**Problemas:** co-facilitación y coordinación figuran “por nombrar” y sin cartas; el compromiso del espacio sigue pendiente. La guía y el método no tienen evidencia de haber sido probados con participantes. La meta de 16 inscritos/12 finalizan es una meta de proyecto, no un resultado validado.

**Presupuesto auditado:** $14.900.000 exactos; Personal $9.940.000, Operación $4.696.000, Imprevistos $264.000. Responsable $5.400.000 = 36,24%; imprevistos = 1,77%; Inversión $0. Las multiplicaciones y sumas son correctas.

**Corrección necesaria:** conseguir cartas o retirar funciones; asegurar espacio y gratuidad; cambiar “la guía funciona sin software” por “la guía se diseñará para ser ejecutable sin software y se verificará en la primera y última sesión”.

## 3. Claims técnicos y estado de motores

La evidencia remota del 6/9 acredita: 2.034 piezas y 5.812 vínculos en `archivo.json`; 219 piezas con percepción visual; 134 tipificadas como obra en `campo.json`; métrica `vecindad_conservada = 0.4855`; contrato de curaduría reversible; `curaduria.json` vacío; servicio local en `127.0.0.1:8900`; salida comprobada sólo JSON. No acredita usuarios externos, eficacia curatorial, persistencia operativa, portfolio publicable ni accesibilidad validada con personas.

Los demos locales de IRIS y PUPILA tuvieron cambios posteriores al corte de la prueba remota y no forman parte de la evidencia integrada en las postulaciones. No se auditan como motor terminado ni se usan para elevar claims. La postulación debe citar “desarrollo propuesto” hasta que exista una prueba integrada, fechada y reproducible sobre el sistema pertinente.

WACHUMA sí existe en MAK, pero su propio README declara corpus sintético o restringido; no debe sustituir la evidencia de IRIS ni presentarse como colección biocultural pública. FARMAKSIA/PUPILA no fueron auditables en MAK; correctamente no son dependencia de estas tres postulaciones.

## 4. Compatibilidad, doble financiación y carga

La afirmación de Claude “las tres son compatibles y acumulables” debe rebajarse. La FAQ oficial confirma una postulación por línea y que se considera la última enviada; las bases citadas no establecen una autorización positiva para resultar seleccionado en varias líneas distintas ni una regla completa de doble financiamiento. La separación de actividades es una buena salvaguarda, pero no prueba acumulabilidad. Resultado: **no prohibido expresamente en lo localizado, no confirmado**. Consultar SIAC y revisar convenios antes de aceptar más de una.

Además, hosting/dominio y registro aparecen en varios presupuestos. Pueden ser gastos distintos sólo si hay servicios, periodos, dominios y productos separables; de lo contrario, hay riesgo de doble imputación. Si se adjudican las tres, las dedicaciones del mismo responsable se superponen y suman $12.400.000 más USD 8.700 de dedicación. Es un riesgo de ejecución y de veracidad de disponibilidad, no una incompatibilidad automática; debe resolverse antes de firmar convenios.

## 5. Bases oficiales y fechas

Consultadas el 6/9/2026: [Creación Regional 2027](https://www.fondosdecultura.cl/creacion-artistica-innovacion-y-nuevos-formatos-creativos-fondart-regional-2027/) líneas web 20–29 y 36–55; [Formativas Regional 2027](https://www.fondosdecultura.cl/actividades-formativas-fondart-regional-2027/) líneas web 20–49; [Investigación Nacional 2027](https://www.fondosdecultura.cl/investigacion-fondart-nacional-2027/) líneas web 20–49; [FAQ Fondart Regional](https://www.fondosdecultura.cl/fondos/fondart-regional/preguntas-fondart-regional/) preguntas 2, 4, 23 y 24; [Ama Amoedo](https://www.fundacionamaamoedo.org/programas/becas), cuya página no expuso formulario ni detalles al crawler. Las páginas oficiales confirman que Creación y Formativas están abiertas y que Investigación Nacional sigue abierta con cierre 14/9 RM. Esto no convierte JARDINES en postulación entregada: no hay expediente completo de Investigación en CODEX REMOTO.

## 6. Cierre de auditoría

La entrega de Claude supera un resumen complaciente: contiene investigación, trazabilidad, prueba técnica y cálculo. No obstante, el estado correcto es **tres expedientes trabajados pero no enviables**, con dos bloqueos taxativos en Fondart, bloqueos de identidad/formulario en Ama Amoedo, claims numéricos que requieren corrección y acumulabilidad aún no verificada. No hay base para afirmar aprobación probable ni para afirmar que las mejoras de los motores en curso ya sostienen las postulaciones.
