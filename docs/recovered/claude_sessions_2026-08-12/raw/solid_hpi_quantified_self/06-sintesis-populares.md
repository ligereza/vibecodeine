# Síntesis de repositorios populares de Quantified Self

Fecha: 2026-08-11

## Alcance

Se seleccionaron 40 repositorios de GitHub ordenados por estrellas y se enviaron a Firecrawl. La tanda fue detenida después de obtener 22 resultados completos.

- Tanda: `019ff18d-37e2-7726-b1ad-70ef4e1988d6`
- Estado: cancelada por decisión del usuario
- Resultados completos: 22
- Créditos usados: 110
- Formato: JSON estructurado

La popularidad se usó para descubrir proyectos, no como medida de calidad, seguridad o pertinencia. La siguiente clasificación está ordenada por interés para el proyecto de archivo y diagnóstico institucional.

## Prioridad 1 — memoria, integración y archivo

### HPI

https://github.com/purarue/HPI

Unifica y permite consultar datos personales desde distintas fuentes. Es la referencia más cercana a la idea de que el dato permanezca distribuido y que una capa de lectura lo vuelva consultable.

**Transferencia:** construir índices y relaciones sin obligar a copiar todo a una base central.

### Stratify

https://github.com/jasonrudolph/stratify

Reúne datos digitales en una línea de tiempo consolidada. Es útil para pensar una ONG como historia de proyectos, decisiones y documentos, no solo como carpetas.

**Transferencia:** línea de tiempo de proyectos, hitos, responsables y documentos relacionados.

### chronicle-etl

https://github.com/chronicle-app/chronicle-etl

Herramienta CLI para extraer y trabajar con datos personales. Su valor está en la capa ETL: extraer, transformar y dejar un registro consultable.

**Transferencia:** pipeline por tandas y manifiesto de procedencia, sin convertir el archivo del cliente en propiedad del servicio.

### heedy

https://github.com/heedy/heedy

Agregador de métricas personales y motor de análisis, con orientación autoalojada/local. La captura indica almacenamiento local, pero la arquitectura completa requiere revisión propia.

**Transferencia:** separación entre fuentes, almacenamiento y análisis; no mezclar captura con interpretación.

### qs_ledger

https://github.com/markwk/qs_ledger

Agrega datos personales y los deja localmente después de descargarlos.

**Transferencia:** ledger de observaciones, origen, fecha, transformación y resultado. Para ONG habría que reemplazar “métrica personal” por “evento documental” o “estado de proyecto”.

## Prioridad 2 — medir sin convertirlo en vigilancia

### ActivityWatch

https://github.com/ActivityWatch/activitywatch

Registra actividad y tiempo, con visualización, consultas, historial y exportación. Su utilidad para tu proyecto es metodológica: muestra cómo producir una radiografía de actividad.

**Límite:** no debe trasladarse como vigilancia de trabajadores. En una ONG conviene medir documentos, duplicaciones y fricciones, no productividad individual.

### aw-watcher-web y aw-watcher-window

- https://github.com/ActivityWatch/aw-watcher-web
- https://github.com/ActivityWatch/aw-watcher-window

Son componentes de observación para ActivityWatch. Sirven para entender cómo se capturan eventos, pero tienen poca transferencia directa al archivo institucional y elevan el riesgo de vigilancia.

## Prioridad 3 — soberanía y arquitectura local-first

### Open Wearables

https://github.com/the-momentum/open-wearables

Unifica fuentes de dispositivos mediante una API, con PostgreSQL y Redis, y afirma que los datos pueden permanecer en infraestructura propia.

**Transferencia:** el cliente conserva la infraestructura y las aplicaciones acceden por permisos. El dominio de salud no debe mezclarse con el servicio documental para ONG.

### OpenStrap Edge

https://github.com/OpenStrap/edge

Procesa localmente datos de un dispositivo y evita depender de una suscripción cloud.

**Transferencia:** “local primero” como criterio de diseño. No es una herramienta de archivo.

### personal_dashboard

https://github.com/Andreilys/personal_dashboard

Agrega y visualiza servicios de seguimiento, con PostgreSQL.

**Transferencia:** panel de lectura sobre fuentes existentes. No necesariamente una base central que absorba los datos originales.

### HealthSave Observatory

https://github.com/umutkeltek/healthsave-observatory

Backend autoalojado con TimescaleDB, API, dashboards y resúmenes locales de datos de salud.

**Transferencia:** separación entre almacenamiento propio, API y capas de visualización.

## Prioridad 4 — directorios y listas, no sistemas de archivo

### awesome-quantified-self

https://github.com/woop/awesome-quantified-self

Es una lista curada de recursos. Sirve para descubrir proyectos, pero no almacena ni analiza los datos de manera operativa.

### awesome-biomarkers

https://github.com/markwk/awesome-biomarkers

Lista curada de biomarcadores y análisis. Es una referencia de curaduría, pero entra en datos de salud y no es transferible sin una barrera ética y legal.

## Prioridad 5 — periféricos

- [quantifiedme](https://github.com/ErikBjare/quantifiedme): análisis personal, pero la captura tenía contenido incompleto.
- [wakatime-cli](https://github.com/wakatime/wakatime-cli): medición de actividad de programación; no es archivo institucional.
- [legacy-python-cli](https://github.com/wakatime/legacy-python-cli): aparece como legado/deprecado.
- [friends](https://github.com/JacobEvelyn/friends): relaciones personales en Markdown; puede inspirar legibilidad humana, no organización de ONG.
- [jimmykane/quantified-self](https://github.com/jimmykane/quantified-self): fitness y salud con Firestore; poca transferencia documental.
- [garmin-health-data](https://github.com/diegoscarabelli/garmin-health-data): descarga datos Garmin a archivos locales y SQLite; útil como patrón técnico, no como modelo de ONG.
- [OpenHumans](https://github.com/OpenHumans/open-humans): la captura fue insuficiente para evaluar el proyecto.

## Hallazgos transversales

1. La idea más transferible no es “medir personas”, sino **hacer consultable un archivo distribuido**.
2. El patrón más útil para ONG combina HPI, Stratify, chronicle-etl y Solid: fuentes bajo control del cliente, índice de procedencia, línea de tiempo y lectura por permisos.
3. ActivityWatch aporta la lógica de observación, pero también muestra el límite ético: medir el sistema documental, no a los trabajadores.
4. La popularidad ordena el descubrimiento; no ordena el interés para tu servicio.
5. Firecrawl produjo JSON útil, pero algunos campos quedaron mal atribuidos o demasiado vagos. El caso más evidente es `ActivityWatch`, cuyo nombre no quedó como URL completa, y algunos campos de relevancia institucional quedaron en `unknown`.

## Propuesta derivada

El servicio para ONG podría ser una **radiografía documental local-first**:

- la ONG conserva sus archivos;
- se procesa una tanda delimitada;
- cada documento conserva fuente, fecha, tipo y relación;
- se construye una línea de tiempo de proyectos;
- se detectan duplicados, vacíos y dependencias personales;
- el resultado vuelve al espacio de la ONG;
- el prestador conserva solo patrones abstractos autorizados.

Esto no es un nuevo SaaS ni un sistema de vigilancia. Es una intervención de lectura, trazabilidad y devolución.
