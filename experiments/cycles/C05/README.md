# C05 — witness real de export de Blender

Este ciclo prueba si MAK puede reconocer un evento de exportación de un
proyecto artístico sin abrir Blender, ejecutar el script ni asumir que el
archivo resultante es la obra final.

Entradas explícitas y read-only:

- `ARICA/RAYU.blend` y su snapshot nativo de C02;
- `ARICA/rayu_export.py`;
- `ARICA/rayu_export_done.txt`;
- `ARICA/rayu_resources.glb`.

El observador exige que coincidan el objeto seleccionado por el script, el
marcador de éxito, los nodos/meshes internos del GLB, el hash del `.blend`
contra el snapshot nativo y el orden temporal de los archivos. No recorre el
directorio y no promueve automáticamente autoría, entrega final o calidad
visual.

Gate:

```text
PYTHONPATH=. .venv/bin/python experiments/cycles/C05/verify_cycle.py
```

La salida durable es `real_export_witness.json`. Cualquier contradicción o
ausencia hace que el witness sea `unknown`, no `supported`.
