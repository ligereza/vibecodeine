# Quantified Self — primera pasada con Firecrawl

Fecha de captura: 2026-08-11

## Fuente procesada

- URL: https://github.com/topics/quantified-self
- Herramienta: Firecrawl API v2, operación `scrape`
- Estado HTTP: 200
- Título: `quantified-self · GitHub Topics · GitHub`

## Resultado de la página

GitHub declara **481 repositorios públicos** asociados al tema `quantified-self`.
La distribución visible por lenguaje incluye Python (172), TypeScript (72), JavaScript (46), HTML (25), Jupyter Notebook (25), Swift (18), Go (14), Ruby (10), Dart (9) y Rust (6).

La página es un inventario ordenado por estrellas, no una taxonomía neutral. GitHub decide el orden y cada autor decide sus etiquetas. Sirve para descubrir proyectos, pero no basta para afirmar que cada repositorio pertenece realmente a una categoría.

## Repositorios relevantes detectados

- [ActivityWatch](https://github.com/ActivityWatch/activitywatch): registro automático de actividad y tiempo, multiplataforma, extensible y orientado a privacidad. Referencia para medir actividad, no para vigilar trabajadores.
- [awesome-quantified-self](https://github.com/woop/awesome-quantified-self): lista curada de recursos, dispositivos, aplicaciones y plataformas de autoseguimiento.
- [open-wearables](https://github.com/the-momentum/open-wearables): plataforma autoalojada para unificar datos de dispositivos portátiles mediante una API.
- [obsidian-tracker](https://github.com/pyrochlore/obsidian-tracker): registra ocurrencias y números dentro de notas; referencia para convertir notas en señales observables.
- [flow-dashboard](https://github.com/onejgordon/flow-dashboard): panel de objetivos, tareas y hábitos; aparece marcado como no mantenido, por lo que interesa como referencia histórica.
- [HPI](https://github.com/karlicoss/HPI): módulos para consultar de forma unificada redes, lecturas, anotaciones, notas, salud, ubicación, fotos, historial y mensajería.
- [Memacs](https://github.com/novoid/Memacs): convierte rastros digitales en una representación temporal para consultarlos y visualizarlos en Org-mode.
- [qs_ledger](https://github.com/markwk/qs_ledger): agregador de datos personales y análisis desde varias fuentes.
- [chronicle-etl](https://github.com/chronicle-app/chronicle-etl): herramientas para extraer y trabajar con historia digital, ETL, archivos, CSV, JSON y memex.
- [hermes-life-os](https://github.com/Lethe044/hermes-life-os): sistema personal con memoria, hábitos, agentes y almacenamiento local; referencia contemporánea, no prueba de madurez o seguridad.

## Lectura para el proyecto de organizaciones

La transferencia más fértil no es construir un “Quantified Self para ONG” que vigile personas. Es hacer una **radiografía del archivo institucional**:

- antigüedad de documentos;
- duplicación de archivos;
- versiones contradictorias;
- tiempo aproximado para encontrar información;
- documentos sin responsable;
- procesos que dependen de una sola persona;
- términos usados de manera inconsistente;
- carpetas que funcionan como depósitos, pero no como sistemas.

El objeto de medición sería el sistema documental, no el rendimiento individual. La salida podría ser un mapa de fricción, una línea de tiempo de proyectos y una lectura de los puntos donde se pierde la memoria institucional.

## Qué puede obtenerse ofreciendo un piloto gratuito

El activo legítimo no sería conservar la basura documental ni apropiarse de ideas. Sería obtener, con autorización:

- patrones abstractos de desorden;
- métricas anónimas de fricción;
- vocabulario operativo del sector;
- casos de estudio;
- validación de la metodología;
- referencias y legitimidad institucional.

Una condición razonable para un piloto sería una entrevista breve, una devolución sobre el diagnóstico y autorización para publicar resultados anónimos. Los documentos originales, datos personales y contenidos confidenciales permanecen en la organización.

## Relación con Solid

Solid propone que los datos permanezcan en un Pod controlado por la persona u organización y que las aplicaciones accedan con autorización. Aunque no se implemente Solid todavía, puede usarse como principio:

> La organización conserva el territorio; el servicio realiza una intervención temporal y devuelve un mapa.

Fuentes oficiales:

- https://solidproject.org/about
- https://solidproject.org/apps
- https://solidproject.org/TR/sai
- https://solidproject.org/get_a_pod
- https://solidproject.org/faq
- https://solidproject.org/TR/
- https://solidproject.org/for_developers/tools
- https://solidproject.org/for_developers/getting_started

## Límites de esta captura

Firecrawl obtuvo la primera página visible del tema y detectó enlaces a repositorios, pero la página indica “Load more”. Esta pasada **no constituye un inventario completo de los 481 repositorios**.

El siguiente paso debería ser seleccionar un grupo pequeño por relevancia —HPI, Memacs, chronicle-etl, ActivityWatch, Obsidian Tracker y algún proyecto local-first— y procesar sus README individuales.

La lista de GitHub es evidencia de descubrimiento, no validación técnica. Antes de recomendar un proyecto hay que revisar actividad reciente, licencia, dependencias, modelo de almacenamiento y riesgos de privacidad.

## Auditoría de calidad del lote completo

El inventario paginado de GitHub devolvió 470 URLs únicas asociadas al tema. Se enviaron las 470 a Firecrawl mediante `batch/scrape`, usando el `.env` de esta carpeta. La tanda quedó identificada como `019ff181-0e38-746f-9a2e-8f72fd247cb5`.

En una comprobación temprana de cinco resultados, todos devolvieron HTTP 200 y el título correspondía al repositorio solicitado:

- `0xPD33/attn`: ledger local de atención para Niri y Quickshell.
- `3kyou1/EchoProfile`: convierte conversaciones con IA en un perfil personal.
- `5agado/conversation-analyzer`: análisis y estadísticas de conversaciones de texto.
- `8tp/Vitals-Command-Center`: panel de salud autoalojado y local-first.
- `davidmosiah/wellness-air`: MCP local-first para datos de calidad del aire.

La extracción es correcta como captura de página y README, pero no todavía como informe semántico final. Algunos resultados incluyen navegación, mensajes de inicio de sesión o tablas de archivos de GitHub junto al README. Por tanto, la siguiente fase debe limpiar y clasificar los textos antes de enviarlos a Watsonx.

En una auditoría posterior de los 43 resultados disponibles:

- 43 devolvieron HTTP 200.
- 36 contenían señales de README, descripción u overview.
- 22 superaron un filtro conservador: README detectable, más de 1.000 caracteres y sin ruido visible de navegación.
- 21 quedaron marcados para limpieza o revisión manual.

Los 22 resultados utilizables en esta primera auditoría son:

- https://github.com/5agado/conversation-analyzer
- https://github.com/davidmosiah/wellness-air
- https://github.com/davidmosiah/wellness-cgm-mcp
- https://github.com/kay-enigma/jarvis
- https://github.com/kmteras/timenaut
- https://github.com/knowhy/py-sleep-influxdb
- https://github.com/kiliankanofsky/HealthOS
- https://github.com/owen282000/life-dashboard-companion-app
- https://github.com/PabloJSV/Sleep-Diet-Predictor
- https://github.com/Paco5687/GlucoPilot
- https://github.com/trishab/endo-protocols
- https://github.com/bluzir/hermes-health
- https://github.com/bridgemouse/Bacta
- https://github.com/bryantee/quantified-self-project
- https://github.com/burakdirin/apple-health-export-mcp
- https://github.com/btrkeks/lifestats
- https://github.com/hlyboki-sensy/oura-health-dashboard
- https://github.com/ikheet7734/longevity-os
- https://github.com/ialchemist-dev/glancely
- https://github.com/nighttimecf/awesome-sleep-tracking
- https://github.com/ninyawee/healthkit-from-backup-to-sqlite
- https://github.com/nitobuendia/travel-track

“Utilizable” aquí significa que la captura es legible y atribuible a su URL; no significa que el proyecto haya sido probado, que sus afirmaciones sean verdaderas o que su código sea seguro.

## Revisión puntual: NGOWorld

Fuente: https://github.com/ngoworldcommunity/NGOWorld

Firecrawl devolvió HTTP 200 y detectó una licencia MIT. El README describe una plataforma para conectar ONG, organizaciones benéficas y personas interesadas en colaborar. Las funciones explícitas detectadas son registro de organizaciones, conexión y colaboración.

La captura no aporta evidencia suficiente sobre almacenamiento, arquitectura, seguridad, privacidad, permisos documentales o gestión de archivos. Por eso la conclusión automática de que tiene “alta relevancia” para ordenar documentos es demasiado amplia.

Evaluación corregida:

- **Sirve como referencia:** red de colaboración, onboarding de organizaciones y contribuciones estructuradas.
- **No sirve todavía como referencia directa:** archivo institucional, curaduría documental, trazabilidad, control de versiones o protección de datos.
- **Valor para tu idea:** puede inspirar una capa comunitaria o directorio de ONG, pero no reemplaza el servicio de radiografía y orden documental.
- **Confianza:** alta para describir el propósito general; baja para inferir arquitectura, seguridad o utilidad documental.

## Revisión puntual: Houdini

Fuente: https://github.com/houdiniproject/houdini

Houdini se presenta como infraestructura libre y gratuita de recaudación de fondos para organizaciones sin fines de lucro y ONG. La extracción identificó campañas de crowdfunding, widgets de donación, eventos, perfiles de organizaciones, historial y pagos, donaciones recurrentes, métricas, CRM de supporters y cuentas de usuarios.

También detectó PostgreSQL y un backend Ruby on Rails con frontend separado. Los datos explícitos incluyen transacciones, cuentas de usuario y donaciones. La licencia, las medidas de seguridad y la privacidad no quedaron suficientemente documentadas en la captura.

Evaluación:

- **Relevancia operativa para ONG:** alta. Permite observar procesos de donación, pagos, CRM, usuarios y reportes.
- **Relevancia para ordenar documentos:** baja o indirecta. No es un sistema de archivo documental; es una plataforma de fundraising y relaciones.
- **Valor para tu servicio:** alto como mapa de los datos y procesos que una ONG debe gobernar antes de preparar su declaración de privacidad.
- **Riesgo:** maneja transacciones, cuentas y posibles datos financieros; no sería un buen primer piloto para recibir datos reales sin una revisión jurídica y de seguridad.
- **Confianza:** alta para el propósito y las funciones visibles; media para arquitectura; baja para seguridad y licencia.

## Revisión puntual: guía oficial de implementación de la nueva ley

Fuente: https://wikiguias.digital.gob.cl/datos-personales/guia-practica-implementacion-nueva-ley-datos-personales

La página corresponde a la **Guía Práctica para facilitar la implementación de la nueva Ley de Protección de Datos Personales en la Administración**, publicada el 13 de diciembre de 2024 por la Secretaría de Gobierno Digital con apoyo de otras instituciones. Indica como fecha de entrada en vigencia el 1 de diciembre de 2026.

La guía propone fases de implementación:

1. designar un encargado;
2. levantar información;
3. elaborar un informe;
4. constituir un comité ejecutivo;
5. elaborar instrumentos.

Entre los productos que menciona aparecen un catálogo de datos personales, una política de tratamiento y un informe de hallazgos. También menciona capacitación, comunicación interna, proveedores de nube y derechos de acceso, rectificación, supresión, oposición y portabilidad.

### Evaluación para el servicio

- Es una fuente oficial y una excelente referencia para estructurar un diagnóstico.
- Su público explícito son órganos de la Administración del Estado y funcionarios públicos.
- No debe presentarse como una obligación específica para toda ONG privada sin contrastarla con la Ley 21.719 y asesoría jurídica.
- Su mejor traducción comercial sería una “revisión de preparación documental inspirada en la guía oficial”, no una certificación de cumplimiento.
- El catálogo de datos, el informe de hallazgos y la política son entregables concretos que pueden convertirse en una primera fase de servicio.

La guía no debe confundirse con el texto completo de la ley: orienta la implementación y contiene recomendaciones prácticas. Las obligaciones vinculantes deben verificarse directamente en la Ley 21.719 y, cuando corresponda, en reglamentos o instrucciones posteriores.

Esta tanda revisa las páginas públicas de los repositorios y sus README visibles; no equivale a leer cada archivo del código fuente ni a auditar seguridad, licencia o funcionamiento. Las afirmaciones de cada proyecto deberán conservar su URL y quedar marcadas como descripción del repositorio, no como verificación independiente.
