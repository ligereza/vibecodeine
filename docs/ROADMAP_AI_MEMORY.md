# Roadmap AI Memory - flujo

## Vision

Convertir el repo en memoria operacional, no solo en scripts:

- productoras
- venues
- logos
- eventos
- ejemplos reales
- formatos oficiales
- decisiones historicas

## Knowledge base propuesta

```txt
knowledge/
  productoras/
  venues/
  events/
  logos/
  examples/
```

Cada entidad debe guardar facts, signals, confidence, sources y overrides humanos.

## Productoras

Datos importantes:

- nombre y aliases
- instagram/url
- escala default: under/base/mainstream
- afinidad RD: full test / informativo / mixto
- venues recurrentes
- logos asociados
- ejemplos reales

## Venues

Datos importantes:

- capacidad bucket
- escala default
- electricidad/luz default
- restricciones
- presets recomendados

## Logos

Integrar con logo clean lab:

- source image
- source quality
- status: needs_vectorization / in_progress / final_svg_ready
- final svg
- manifest de limpieza

## Examples ingestion

Objetivo:

```bash
py -m flujo examples ingest carpeta --type flyer_evento
```

Salida deseada:

```json
{
  "layout": {},
  "style": {},
  "producer": {},
  "editable_fields": [],
  "signals": []
}
```

## Internet enrichment

No debe ser rigido ni automatico ciego. Debe guardar:

- source url
- dato extraido
- confianza
- fecha
- quien/que lo agrego

## Principio

Cada pedido debe mejorar la memoria del sistema.
