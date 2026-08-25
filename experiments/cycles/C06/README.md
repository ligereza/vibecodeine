# C06 — puente de witness de exportación al grafo

C06 convierte el resultado de C05 en una arista aislada `EXPORTS_TO`. Solo
materializa la arista si el witness tiene schema correcto, evento `export`,
refs, referencias de fuente/destino y los siete checks en `pass`.

Un witness faltante, `unknown` o contradictorio produce `claim=unknown` y
cero aristas. El puente no inspecciona filesystem, no abre Blender, no ejecuta
scripts y no crea relaciones de autoría, entrega final o publicación.

```text
PYTHONPATH=. .venv/bin/python experiments/cycles/C06/verify_cycle.py
```
