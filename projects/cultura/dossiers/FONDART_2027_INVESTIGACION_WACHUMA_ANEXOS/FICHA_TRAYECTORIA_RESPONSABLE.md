# Ficha de trayectoria del responsable

Estructura para el criterio Currículo (20%) de la línea Investigación. Completa
sólo lo marcado `[FALTA]`; el resto ya está verificado contra el repositorio o
contra datos que entregaste.

## Identidad

- Nombre legal: `[FALTA]`
- RUT: `[FALTA]`
- Nombre artístico, si corresponde para presentarse: MAKSI / ISKVW
- Domicilio y región: `[FALTA]` — condiciona además la fecha de cierre aplicable (ver nota en `README.md` de `BASES/postulaciones/`).
- Perfil Cultura: trámite iniciado; `[FALTA]` completar los documentos pendientes de enviar en la plataforma antes del FUP.

## Trayectoria técnica ya verificable (no requiere tu confirmación adicional)

Evidencia comprobada en este repositorio, con lo que cada ítem demuestra para el criterio de competencias y experiencia pertinente a la metodología de esta investigación:

- **Autoría y mantenimiento de `github.com/ligereza/WACHUMA`** (83 commits al 5 de septiembre de 2026): monorepo con web (Next.js), API (Fastify), worker y base PostgreSQL/PostGIS, con esquemas de contenido vinculantes e importadores versionados. Demuestra capacidad de diseño de datos y de arquitectura de un sistema de investigación, no sólo de uso de una herramienta ajena.
- **Diseño del modelo de procedencia**: separación por esquema entre `sourceType`/`assertionType` y el rótulo `procedural-interpretation` (presente en cuatro esquemas: `garden-scene`, `material-fixture`, `plant-descriptor`, `scroll-experience`). Es evidencia directa de trabajo metodológico sobre la misma distinción evidencia/interpretación que la investigación pone a prueba con público.
- **Batería de verificación propia** (`pnpm verify:release`): tipos, pruebas, build, contenido, licencias, SBOM, migraciones, formato, siembra idempotente, generación procedural con verificación de hash, integración contra PostgreSQL y humo de superficies públicas. Demuestra disciplina de comprobación aplicable al protocolo de campo del proyecto.
- **Documentación de decisiones y límites propios** (`CAPACIDADES.md`, `NOMENCLATURA.md`, ADRs de arquitectura): evidencia de trabajo previo separando lo que un sistema hace de lo que declara no hacer, la misma separación que la investigación mide en un público externo.

## Lo que sólo tú puedes acreditar `[FALTA]`

- Formación (títulos, cursos, talleres relevantes para artes visuales, nuevos medios o investigación cultural).
- Trayectoria artística o de investigación previa a MAK: exposiciones, publicaciones, participación en convocatorias, docencia, si existen y están documentadas. Esta ficha no atribuye ninguna que no puedas acreditar.
- Enlaces públicos vigentes (portafolio, redes profesionales, publicaciones) que el FUP pida para currículo.
- CV firmado en el formato que exija la plataforma de postulación.

## Nota de uso

Esta ficha no reemplaza el CV que pide el FUP: es la fuente de la que se redacta, para que el CV final no contenga ninguna afirmación que este expediente no pueda sostener con evidencia. Una vez completados los ítems `[FALTA]`, actualizar `sections.trayectoria_responsable` en `FONDART_2027_INVESTIGACION_WACHUMA.json` y la sección equivalente del `.md`.
