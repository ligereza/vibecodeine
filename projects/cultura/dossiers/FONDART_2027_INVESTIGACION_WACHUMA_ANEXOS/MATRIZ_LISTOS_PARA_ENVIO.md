# Matriz de disposición para el envío — FONDART Investigación 2027, caso WACHUMA

Generada por un agente Claude el 2026-09-07 a partir de las bases oficiales
(`BASES/postulaciones/01-fondart-nacional-investigacion-2027/`) y el estado
verificado del dossier y sus anexos en el momento de escribirla. No reemplaza
revisión humana; cada fila indica qué se verificó y cómo, para que esa
revisión no tenga que repetir el trabajo mecánico.

**Este archivo es una herramienta de seguimiento interno, no un anexo de la
postulación: no corresponde adjuntarlo al FUP.**

## Matriz breve de decision (agregada 2026-09-07, plan del coordinador)

Sin reabrir ni reescribir el contenido tecnico ya verificado -- este es solo
el resumen que pide el plan del coordinador, replicado en los tres paquetes
activos hoy.

| Campo | Contenido |
|---|---|
| Objeto | Wachuma leido por su publico: estudio de campo comparativo sobre si hacer explorable la procedencia de un archivo biocultural digital cambia como un publico distingue hecho de interpretacion |
| Audiencia | Jurado Fondart Nacional Investigacion (Calidad 30%, Curriculo 20%); muestra intencional de 24-30 personas vinculadas a artes visuales/mediacion/investigacion |
| Evidencia real | Modelo de procedencia real (schemas `provenance-record`, `species-document`) con revision humana registrada; escritorio de revision `/admin` documentado en `CAPACIDADES.md`; Avance de Investigacion verificado en 15 paginas exactas; presupuesto y topes verificados contra las bases |
| Trabajo futuro | El estudio de campo mismo (Fases 1-5, abril 2027-marzo 2028): instrumentos, sesiones, analisis y actividad de transferencia |
| Dependencia externa | Consentimiento informado de participantes; revision bibliografica secundaria pendiente de cerrar |
| Decision del operador | Identidad/RUT/domicilio y region del responsable (decide si aplica el cierre del 14 o el 16 de septiembre); Perfil Cultura vigente; CV firmado; cotizaciones reales |


| # | Requisito (fuente) | Evidencia | Estado | Verificación realizada | Bloqueo / siguiente acción |
|---|---|---|---|---|---|
| 1 | Persona natural con residencia definitiva en Chile, mayor de 18 (bases, Requisitos duros) | `sections.trayectoria_responsable` | **pendiente (personal)** | — | Domicilio/región acreditables y Perfil Cultura vigente: solo el responsable puede cerrarlo. |
| 2 | Inscripción en Perfil Cultura (bases, Requisitos duros) | `FICHA_TRAYECTORIA_RESPONSABLE.md` | **pendiente (personal)** | — | Trámite iniciado según el propio expediente; faltan documentos por subir a la plataforma. |
| 3 | Proyecto de investigación con estudio de campo (bases, Requisitos duros) | `AVANCE_DE_INVESTIGACION.md` §6 | **cumplido** | Metodología de campo completa (diseño, muestra, instrumentos, procedimiento, análisis, límites) leída en el documento. | Ninguno agente-solvable. |
| 4 | Plan de transferencia con ≥1 actividad presencial/virtual (bases, Requisitos duros) | `PLAN_ACTIVIDAD_TRANSFERENCIA.md` | **cumplido** | Documento declara una actividad concreta (taller-charla 2h) con público, metodología y resultados esperados. | Falta solo confirmar número final de asistentes y organización anfitriona ([FALTA] ya declarado, no bloquea el requisito mínimo). |
| 5 | Avance de Investigación en el formato oficial: 15 páginas tamaño carta (bases, Anexo N°2) | `AVANCE_DE_INVESTIGACION.pdf` | **cumplido, verificado hoy** | `pdfinfo` → Pages: 15, Page size: 612x792 pts (letter). Antes de este ciclo eran 13 páginas; se cerró con dos subsecciones sourced desde el repositorio WACHUMA, marcadas como borrador pendiente de aprobación dentro del propio documento. | Revisión humana de esas dos subsecciones antes de dar el documento por cerrado. |
| 6 | Documentos condicionales del Anexo N°2 (autorización de derechos de autor, cartas de equipo, consentimiento de comunidad indígena, estatutos, certificado de inhabilidades) | `sections.equipo`, `sections.riesgos_etica` | **no aplican, verificado** | El dossier declara explícitamente: sin equipo de trabajo, sin menores, sin actividades en territorio indígena o vía pública, persona natural (no jurídica). Ninguna de las cinco condiciones se activa. | Si cambia el equipo o el alcance antes del envío, reevaluar esta fila. |
| 7 | Ejecución entre el 1 de marzo y el 30 de abril de 2027, máximo 12 meses (bases, Requisitos duros) | `sections.cronograma` | **cumplido** | Inicio declarado: 1 de abril de 2027 (dentro de la ventana); cierre: marzo de 2028 (12 meses exactos). | Ninguno. |
| 8 | Montos y topes: mínimo \$500.000, máximo \$15.000.000; transferencia 5–10%; responsable máx. 40%; imprevistos máx. 2% (bases, Montos y topes) | `sections.presupuesto` | **cumplido, verificado con aritmética** | Solicitado \$12.000.000 (dentro de rango). Responsable \$3.600.000 = 30% (< 40%). Transferencia \$600.000 = 5% (dentro de 5–10%). Imprevistos \$240.000 = 2% (en el límite exacto, no lo excede). | El presupuesto se declara "base de trabajo, no cotización": cotizaciones reales siguen pendientes (fila 9). |
| 9 | Cotizaciones o valores verificables; revisión laboral/tributaria (bases + `sections.presupuesto`) | — | **pendiente (personal/gestión)** | — | Requiere gestión externa (cotizar, revisar obligaciones); no es verificable desde el repositorio. |
| 10 | Una sola postulación por línea (bases, Requisitos duros, I.4) | `NEXT.md`, alerta de dirección #2 en `03_REQUISITOS_CONDICIONES_ALERTAS.md` | **decidido** | El dossier reemplaza explícitamente al borrador "Jardines interpretativos"; Wachuma es la única postulación activa en esta línea. | Ninguno. |
| 11 | Fecha de cierre (bases + portal) | `sections` / región del responsable | **parcialmente verificado** | Portal oficial (consultado hoy): 14 de septiembre de 2026, 15:00, para Coquimbo–Magallanes; 16 de septiembre para Arica y Parinacota, Tarapacá, Antofagasta y Atacama. | La fecha exacta aplicable depende de la región del responsable, que sigue `[FALTA]` (fila 1). Deadline duro en cualquier caso: 14 o 16 de septiembre de 2026, no el 10 que tenía la ficha vieja. |
| 12 | Hash de integridad de las bases conservadas (`03_REQUISITOS_CONDICIONES_ALERTAS.md`) | `01_BASE_ORIGINAL_FONDART_NACIONAL_INVESTIGACION_2027.pdf` | **cumplido, verificado hoy** | `sha256sum` del PDF conservado coincide exactamente con el hash declarado: `9da0ab5f0850fdad354415448829fd88fa1e61beee5fd048c90a4a5b4c418af2`. | Ninguno. |

## Resumen

- **Agente-solvable y cerrado hoy:** filas 3, 4, 5, 6, 7, 8, 10, 12 (8 de 12).
- **Parcialmente cerrado, con un componente personal pendiente:** fila 11.
- **Depende enteramente de datos o gestiones personales, no tocado:** filas 1, 2, 9.
- **Ningún ítem de esta matriz entra en datos personales, declaraciones legales ni montos comprometidos con terceros.**
