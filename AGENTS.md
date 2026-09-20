# AGENTS.md — entrada única para cualquier agente

Este archivo es el único punto de arranque para Codex, Claude u otro agente que trabaje en este repositorio.

## Regla principal

**No reconstruyas el proyecto leyendo Markdown al azar.** El repositorio acumuló cientos de documentos históricos, snapshots y handoffs que contienen palabras como `CURRENT`, `vigente`, `canonical`, `next action` o `master` aunque ya no describan el presente.

Orden obligatorio:

1. Lee **sólo** este archivo.
2. Lee `REAL_INFO.md`.
3. Identifica el encargo actual desde el mensaje del usuario, issue, PR o rama en la que estás trabajando.
4. Abre únicamente el código, datos o documentación de dominio necesarios para ese encargo.
5. Si necesitas saber por qué algo terminó así, consulta `HISTORICO.md`. No uses la historia como backlog.

## De dónde sale la verdad

- **Intención y prioridad actual:** del usuario o del encargo explícito. Nunca de un viejo `next action`.
- **Estructura actual del repo:** árbol Git y `branch_profile.json`.
- **Estado del runtime MAK:** medirlo con `.venv/bin/python tools/mak_status.py --json` cuando estés en la máquina MAK. Si no puedes ejecutar esa medición, dilo; no sustituyas la medición por prosa histórica.
- **CLI FLUJO:** `python -m flujo --help` y el código actual.
- **Decisiones y vocabulario vigentes:** resumen en `REAL_INFO.md`.
- **Historia:** únicamente `HISTORICO.md` como índice humano; para detalle forense usa Git por commit/fecha.

## Prohibiciones de arranque

No leas como contexto inicial:

- `context-history/**`
- `docs/handoffs/archive/**`
- `docs/recovered/**`
- documentos `PHASE*.md`
- cierres de sesión fechados
- `CAPACIDADES_*.md` completas
- archivos que se autodenominan `CURRENT`, `CANONICAL`, `MASTER` o `LAST_HANDOFF`

Sólo ábrelos si el encargo actual exige específicamente evidencia histórica o de ese dominio.

## Cómo decidir qué hacer

La pregunta correcta al empezar no es “¿qué decía el agente anterior?”, sino:

1. ¿Qué pidió el usuario ahora?
2. ¿Qué parte del árbol implementa eso hoy?
3. ¿Qué evidencia actual necesito antes de editar?
4. ¿Cuál es el cambio mínimo que deja un resultado verificable?

No continúes automáticamente una tarea antigua encontrada en un Markdown. No inventes una misión por proximidad de archivos.

## Límites semánticos que no debes re-derivar

- `vibecodeine` es el repositorio integrado.
- `main` es la base Git integrada MAK + FLUJO, no un tercer runtime.
- MAK y FLUJO conservan superficies y responsabilidades distintas dentro de la base integrada.
- IRIS es el sistema interno de orden/relación del archivo. No es sinónimo de portafolio público.
- RD, Cultura/iskvw, FLUJO, MAK y XIO pueden compartir evidencia o contratos; co-localización en el repo no los vuelve la misma autoridad.
- Un archivo o directorio llamado “current”, “actual”, “canonical” o “master” no obtiene autoridad por su nombre.

## Antes de entregar un cambio

Verifica el ámbito real que tocaste. Para cambios generales del repo, usa los gates definidos por el árbol actual; como mínimo revisa `branch_profile.json`, `pyproject.toml` y las pruebas relevantes. No declares “todo verde” si sólo corriste una selección.

## Al terminar

No crees otro handoff permanente. Si cambió un hecho durable, actualiza `REAL_INFO.md` de forma breve. Si sólo ocurrió algo histórico que merece conservarse, agrega una entrada resumida a `HISTORICO.md`. El detalle técnico ya queda en Git, tests y commits.

El objetivo de este contrato es que un agente nuevo pueda empezar sin memoria previa y sin tener que leer el archivo documental completo.
