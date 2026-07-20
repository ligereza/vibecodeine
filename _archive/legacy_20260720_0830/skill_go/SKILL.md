---
name: go
description: Arranca un proyecto a partir de una idea ya comprimida por REDU (el asistente de voz en tools/vibo_voz). Invocar cuando el usuario diga "go <nombre>", "arranca <nombre>", "empieza el proyecto <nombre>", o pida partir de una idea guardada por REDU/Gemini. Busca la carpeta tools/vibo_voz/proyectos/<nombre>/ (idea.md, idea.json) generada por voz y comienza a implementarla desde ese formato ahorrativo, usando ese formato como contexto (sin re-explorar el repo entero).
---

# go - arrancar un proyecto desde una idea de REDU

REDU (el asistente de voz en `tools/vibo_voz`) convierte ideas habladas en un
**formato ahorrativo** (notacion comprimida) y las guarda en
`tools/vibo_voz/proyectos/<nombre>/`. Esta skill toma el nombre de la idea y arranca
el proyecto desde ahi, tratando el formato comprimido como la especificacion.

## Uso

`go <nombre de la idea>`   (ej: `go csv-extractor`)

## Pasos

1. Toma `<nombre>` de los argumentos y normalizalo a slug (minusculas, guiones,
   acentos a ASCII).
2. Busca la carpeta en `tools/vibo_voz/proyectos/`. Si no hay match exacto, LISTA las
   carpetas de `proyectos/` y elige la mas parecida; si hay varias candidatas,
   pregunta cual antes de seguir.
3. Lee `idea.md` (bloque comprimido; puede traer la idea original en voz) y, si existe,
   `idea.json`.
4. Interpreta la notacion como la especificacion del proyecto:
   - Lineas clave: `task:` `input:` `output:` `lang:` `fields/cols:` `steps:` `req:` `context:`
   - Operadores: `->` (produce) `|` (o) `[]` (lista) `{}` (objeto) `+` (y) `~` (aprox)
5. Expande el formato a un plan concreto (objetivo, entradas/salidas, pasos, stack,
   restricciones) y confirmalo en 2-3 lineas.
6. Arranca la implementacion. Si el formato NO dice donde crear los archivos, pregunta
   la carpeta destino antes de escribir nada.

## Notas

- El formato comprimido ES el contexto: no re-explores todo el repo, pide solo lo que
  falte.
- Si la carpeta `proyectos/<nombre>/` no existe, dilo y sugiere generar la idea primero
  con REDU (por voz, en `tools/vibo_voz`).
