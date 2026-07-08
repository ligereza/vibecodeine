# proyectos/ - ideas comprimidas por REDU

Cada subcarpeta es una idea que REDU (el asistente de voz) capturo y comprimio a un
**formato ahorrativo**, lista para arrancar en Claude Code con la skill `go <nombre>`.

## Estructura por idea

```
proyectos/
+-- <nombre-idea>/
    +-- idea.md      # bloque comprimido (task:/input:/output:/...) + idea original
    +-- idea.json    # (opcional) misma idea en JSON
```

## Flujo

1. En `tools/vibo_voz` corre el asistente de voz (`py vibo.py`).
2. Explicale una idea; REDU la comprime y la guarda aqui (`guardar_proyecto`).
3. En Claude Code: `go <nombre>` -> lee esta carpeta y arranca el proyecto desde el
   formato comprimido.

Las carpetas se crean solas al guardar; este README solo documenta la convencion.
