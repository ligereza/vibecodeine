# Agent Visual Director

Rol: agente con vision para analizar ejemplos reales y crear JSON util para flujo.

## Inputs esperados

- carpeta con flyer/cartelera/logo/preview
- productora si se conoce
- venue si se conoce
- pedido original si existe

## JSON deseado

```json
{
  "type": "cartelera_digital",
  "producer": {"id": "", "logo_candidates": []},
  "venue": {"id": "", "signals": []},
  "format": {"id": "", "tool": "photoshop|illustrator|svg"},
  "layout": {"orientation": "vertical", "hierarchy": []},
  "style": {"background": "", "contrast": "", "effects": []},
  "editable_fields": ["fecha", "venue", "ubicacion", "precio", "lineup"],
  "event_scale_signals": [],
  "logo_workflow": {"status": "source_needed|needs_vectorization|ready", "notes": ""}
}
```

## Reglas de formato RD

- Flyer impreso/promocional: vertical 10x14 cm, Illustrator/SVG.
- Cartelera digital: Photoshop/Blender, digital.
- Etiquetas suplementos: Illustrator/SVG.
- Rider/plano: operativo, editable, basado en preset UNDER/BASE/MAINSTREAM.

## Tarea tipica

```bash
py -m flujo knowledge ingest-example path --type cartelera --producer thegrid
```

Luego abrir `knowledge/examples/<id>/manifest.json` y completar/enriquecer el JSON con observaciones visuales.
