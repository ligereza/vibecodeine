# Proyectos satélite de flujo

Este directorio contiene **proyectos experimentales y productivos** que extienden el sistema flujo más allá del núcleo (jobs → piezas vectoriales).

Cada subdirectorio es un "satélite" con su propia lógica, pero que idealmente debería alinearse con la **línea editorial central** (ver `aistetic/`).

## Lista de proyectos

| Proyecto              | Propósito principal                          | Estado          | Tipo          | Referencia principal |
|-----------------------|----------------------------------------------|-----------------|---------------|----------------------|
| `piezas_vectoriales/` | Generación de flyers, etiquetas, riders vectoriales listos para Illustrator/PS | Activo / producción | Vectorial    | `config.json` + `INDEX_FORMATOS.json` |
| `flyer_eventos/`      | Flujos reales de eventos (ingesta IG/correo → análisis → export) | Operativo (con datos reales) | Operación    | Carpetas fechadas con manifest |
| `plano/`              | Generador paramétrico de planos de stands + riders + costos | Prototipo maduro | Operativo    | `plano_stands.py` + `engine.py` |
| `tapiz/`              | VibeCode: visualización en tiempo real de la generación de código por IA | Experimental     | Herramienta IA | `vibecode/` package + HTML visualizers |
| `aistetic/`           | **Línea editorial / identidad visual central** (paleta, tipografía, motivos, reglas de marca) | Nuevo / por definir | Identidad    | `linea_editorial.md` + `aistetic.json` |

## Reglas de convivencia

- Todos los proyectos deben poder **consumir** definiciones de `aistetic/` (colores, tipografías, estilos de texto, framing, etc.).
- Los proyectos de "producción" (`piezas_vectoriales`, `flyer_eventos`) generan entregables reales.
- Los proyectos "satélite" (`plano`, `tapiz`, `aistetic`) exploran nuevas capacidades o centralizan conocimiento.
- Cuando se alimente este repo a una IA externa (para generar línea editorial, nuevos proyectos, etc.), la IA debe empezar por:
  1. `projects/README.md`
  2. `projects/aistetic/`
  3. Los `README.md` de cada satélite
  4. Ejemplos de `config.json` y `manifest.json` en las piezas activas.

## Cómo agregar un nuevo proyecto satélite

1. Crear `projects/<nombre>/`
2. Incluir al menos:
   - `README.md` (idea + arquitectura + estado)
   - Estructura clara (ejemplos/, src/ o engine/, assets/)
3. Actualizar este `README.md`
4. Actualizar `docs/REPO_MAP.md`
5. (Ideal) Crear referencia en `aistetic/` si afecta identidad visual.

## Para IAs externas que reciban el repo completo

Si te mandaron este repositorio para extraer información (ej. para crear la línea editorial "aistetic"):

- **No leas todo**. Empieza por los archivos de este `projects/README.md` y `projects/aistetic/`.
- Busca patrones visuales en:
  - `projects/piezas_vectoriales/*/config.json` (paletas, tipografía, composición)
  - `projects/flyer_eventos/` (manifests + refs/)
  - `projects/plano/` (reglas operativas + SVG output)
  - `projects/tapiz/vibecode/` (estética de visualización de código)
- El núcleo de flujo (`src/flujo/`) define el pipeline, pero la **estética real** vive en estos proyectos.

---

**Objetivo a largo plazo**: Que "aistetic" se convierta en la fuente de verdad de identidad visual, y que los otros proyectos (incluyendo nuevos) la consuman de forma declarativa.