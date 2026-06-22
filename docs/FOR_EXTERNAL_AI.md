# Guía para IAs externas que reciben este repositorio

Si te mandaron el repo completo de **flujo** para que analices información y generes algo (por ejemplo, una **línea editorial** llamada "aistetic"), sigue estas instrucciones para no perderte y producir algo útil.

## Orden de lectura recomendado (ahorra tokens)

1. `projects/README.md` — Entiende qué es cada proyecto satélite.
2. `projects/aistetic/` (especialmente `README.md` y `linea_editorial.md`) — Aquí es donde debe vivir el resultado.
3. `docs/REPO_MAP.md` — Qué está vivo vs histórico.
4. `PARA_IA_CONTEXT.md` + `context/LAST_HANDOFF.md` (si existe) — Estado actual del desarrollo.
5. Ejemplos concretos de estética:
   - `projects/piezas_vectoriales/*/config.json`
   - `projects/flyer_eventos/` (manifests + archivos de referencia)
   - `projects/plano/` (output SVG + reglas)

**No leas todo el código fuente ni todos los handoffs antiguos** al principio. Solo si te piden algo técnico específico.

## Qué extraer típicamente

Cuando te pidan una "línea editorial" o "aistetic":

- **Paleta de colores** (nombres internos usados + usos)
- **Tipografía y jerarquía**
- **Principios de composición** (márgenes, ritmos, densidad)
- **Motivos visuales** recurrentes
- **Tono de voz** y lenguaje
- **Reglas por formato** (qué cambia entre flyer impreso, IG, rider, plano)

## Dónde vive la identidad real hoy

La estética actual **no** está centralizada. Está dispersa en:

- Configuraciones de piezas vectoriales (`config.json`)
- Manifiestos y archivos de entrada de eventos reales
- Reglas del generador de planos
- Estilo visual de las herramientas experimentales (tapiz)

Tu trabajo es **sintetizarla** en `projects/aistetic/`.

## Estructura que se espera que produzcas

Idealmente genera/actualiza:

- `projects/aistetic/linea_editorial.md` (documento humano)
- `projects/aistetic/aistetic.json` (versión estructurada para código futuro)
- Carpetas `palettes/`, `typography/`, `references/` con contenido real extraído

## Reglas importantes del repo

- No automatizar Photoshop/Illustrator/Blender (solo preparar archivos).
- Solo usar instaloader para Instagram.
- Todo cambio se entrega como airdrop (pero como IA externa probablemente solo generas el contenido de aistetic).
- Mantén los archivos generados **útiles y accionables**.

## Mecanismo de ejemplos + JSON descriptivos (para línea editorial)

Si tu tarea es generar/refinar la línea editorial de **aistetic**:

1. Ve a `projects/aistetic/ejemplos/`
2. Analiza los trabajos reales que el dueño haya cargado allí (carpetas con archivos terminados).
3. Genera JSONs descriptivos en `projects/aistetic/json/`.
4. Usa el schema `schemas/example_description.schema.json` como guía de estructura.
5. Con la información de los JSONs + lo que veas en piezas y planos, actualiza:
   - `projects/aistetic/linea_editorial.md`
   - `projects/aistetic/aistetic.json`

Este es el flujo principal para "ocupar" el repo con información real de estética.

## Si te piden algo más (no solo línea editorial)

- Para entender el pipeline completo → `README.md` (sección de pipeline).
- Para agregar un nuevo proyecto satélite → sigue el patrón de `plano/` o `tapiz/`.
- Para trabajar con el sistema → usa `flujo --help` después de instalar.

---

Este archivo existe precisamente para que cuando manden el repo a otra IA, sepa cómo navegarlo sin ahogarse en detalles irrelevantes.