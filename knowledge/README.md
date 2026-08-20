# Knowledge base flujo

Memoria operacional versionable para productoras, venues, logos, eventos y ejemplos reales.

Principio: cada pedido debe mejorar la memoria del sistema.

Estructura:

```txt
knowledge/productoras/*.yaml
knowledge/venues/*.yaml
knowledge/logos/*.yaml
knowledge/events/*.yaml
knowledge/examples/*/manifest.json
knowledge/learning_cases/*.json
knowledge/math_targets/*.json
```

Los datos pueden ser incompletos. Usar `confidence`, `source` y `notes` antes que inventar certezas.

`learning_cases/` conecta memoria historica con investigacion posterior sin
copiar los arboles fuente. Cada caso conserva hashes, clase epistemica,
limites de afirmacion y acciones aprendibles. Validar primero en modo
read-only; registrar en el ledger requiere una base explicita:

```bash
PYTHONPATH=src .venv/bin/python tools/source_learning_bridge.py knowledge/learning_cases/<case>.json
PYTHONPATH=src .venv/bin/python tools/source_learning_bridge.py knowledge/learning_cases/<case>.json --db data/mak_knowledge.db --record
```

Un episodio verificado por este puente certifica integridad y trazabilidad de
la ingestion. No certifica la verdad de las hipotesis contenidas en el caso.

`math_targets/` usa la misma primera capa cultural-investigativa para targets
matematicos. El Math Kernel solo agenda requests y conserva `ResultCard`
metadata-only; formulas, pruebas y contraejemplos quedan sellados por hash y
referencia. `MILLENNIUM-PNP-001` es una capsula inicial con fidelidad semantica
`UNTRUSTED`, por lo que ninguna tarjeta puede convertirse en solucion.
