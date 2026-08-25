# C07 — grafo mínimo de práctica artística

Prototipo local, ejecutable con Python stdlib, Pillow cuando está disponible y
`ffprobe` cuando el archivo es vídeo. No instala paquetes y no abre ni ejecuta
Blender/Adobe.

## Contrato

`practice_graph.py` extrae cada `artifact` con extensión, SHA-256, bytes,
dimensiones, aspect ratio, alpha, duración/fps/codec de vídeo, familia e índice
de secuencia, tokens de nombre/ruta y XML/XMP legible.

`RelationCandidate` implementa `component_of`, `version_of`,
`manifestation_of`, `same_series_candidate` y `published_as`. Cada candidato
incluye score, desglose explicable, `evidence_refs`, `alternatives`,
`missing_evidence` y `next_probe`. Los estados son `supported`,
`pending_relation` o `unresolved_candidate`; la falta de contraparte conserva
un candidato accionable con `target_id: null`.

## Ejecución

Desde C07:

```bash
python3 runner.py
```

El runner ejecuta los tests, `py_compile` y escribe `graph.json`. Las fixtures
se materializan en un directorio temporal: frames + export, export sin
proyecto, proyecto sin export, mismo nombre/diferente obra y misma obra en
proporciones distintas. El archivo `fixtures/manifest.json` documenta los
casos.
