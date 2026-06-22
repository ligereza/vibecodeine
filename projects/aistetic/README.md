# aistetic — Línea editorial central de flujo

**Propósito**: Definir y centralizar la identidad visual, tono, reglas de marca y lenguaje estético que debe guiar **todos** los entregables generados con flujo (piezas vectoriales, flyers de eventos, riders, planos, visualizaciones, etc.).

Este es el proyecto "satélite" que actúa como **fuente de verdad** de la estética. Los otros proyectos (piezas_vectoriales, flyer_eventos, plano, tapiz) deben poder referenciarlo.

## Estructura recomendada

```
projects/aistetic/
├── README.md
├── linea_editorial.md         # Documento principal de la línea editorial
├── aistetic.json              # Versión machine-readable
├── ejemplos/                  # <--- Trabajos ya hechos que cargas tú (imágenes, configs, carpetas reales)
├── json/                      # <--- JSONs descriptivos generados por agentes desde los ejemplos
├── palettes/
├── typography/
├── motifs/
├── references/
└── ...
```

**Importante:** 
- Tú cargas trabajos terminados en `ejemplos/`
- El agente que entre analiza y genera (o usa) los JSON descriptivos en `json/`
- Si ya existen JSONs dentro de esta estructura, la carpeta `json/` ya existirá.
- Ver `ejemplos/README.md` y `json/README.md` para instrucciones detalladas + schema.

## Cómo se usa (visión)

1. Una IA externa recibe el repo completo (o esta carpeta + algunos ejemplos) y genera/actualiza `linea_editorial.md` + `aistetic.json`.
2. Los motores de flujo (`render/`, `plano/`, etc.) leen `aistetic.json` o referencias para aplicar consistencia.
3. Cuando se crea un nuevo proyecto o pieza, se puede pasar `--aistetic aistetic/` o referenciarlo en el `config.json`.

## Estado actual (2026-06)

- Proyecto recién creado como estructura.
- Aún no hay contenido real de línea editorial.
- El objetivo de esta carpeta es servir como **paquete limpio** para alimentar a otra IA y que extraiga/refine la identidad a partir del trabajo existente en el resto del repo (principalmente `piezas_vectoriales/`, `flyer_eventos/` y `plano/`).

## Instrucciones para la IA que recibirá este repo

Si te están mandando el repositorio `flujo` para que generes la línea editorial:

1. Lee primero `projects/README.md` para entender el ecosistema.
2. Lee `docs/FOR_EXTERNAL_AI.md` (guía específica para este caso de uso).
3. Enfócate en `projects/aistetic/` (aquí es donde debe vivir el resultado).
4. Explora patrones estéticos en:
   - `projects/piezas_vectoriales/` (config.json → colores, tipografía, jerarquía, marcos)
   - `projects/flyer_eventos/` (manifiestos + imágenes de referencia)
   - `projects/plano/` (estilo de diagramas, tipografía técnica, uso de color)
   - `projects/tapiz/` (estética visual de "vida del código")
5. Extrae y produce:
   - `linea_editorial.md`
   - `aistetic.json`
   - Contenido en `palettes/`, `typography/`, `references/`

No inventes. Basa todo en lo que realmente aparece en el trabajo existente del repo.

## Próximos pasos

- [ ] Generar primera versión de `linea_editorial.md` + `aistetic.json` (por IA externa)
- [ ] Hacer que el render de flujo pueda leer `aistetic.json`
- [ ] Actualizar plantillas de `piezas_vectoriales/` para que hereden de aistetic
- [ ] Documentar reglas de "cuándo romper la línea editorial"

---

Este proyecto convierte al repo en algo **ocupable** y no solo mejorado internamente. Es el punto de entrada para definir identidad antes de generar más piezas.