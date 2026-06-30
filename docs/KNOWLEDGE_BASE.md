# Knowledge base

La carpeta `knowledge/` es la memoria operacional versionable de flujo.

## Entidades actuales

```txt
knowledge/productoras/*.yaml
knowledge/venues/*.yaml
knowledge/logos/*.yaml
knowledge/events/*.yaml
knowledge/examples/*/manifest.json
```

## Comandos

```bash
py -m flujo knowledge list productoras
py -m flujo knowledge show productora creamfields
py -m flujo knowledge classify "Creamfields Espacio Riesco rider cartelera"
py -m flujo knowledge ingest-example carpeta --type flyer_evento --producer creamfields
py -m flujo knowledge logo-source creamfields path/logo.jpg
```

## Principio

No guardar solo archivos: guardar contexto accionable.

Cada dato debe poder tener fuente, confianza, notas y posibilidad de override humano.

## Example templates

Templates for IA vision analysis live in:

```txt
knowledge/templates/*.for_ai.json
```

Current templates:

- `cartelera_digital`
- `flyer_evento_10x14`
- `suplemento_flyer`
- `logo_source`
- `generic`

When you ingest examples, flujo writes:

```txt
manifest.json
for_ai.json
README.md
```

Give `for_ai.json` plus the copied files to a vision IA and ask it to return `analysis.json`.
