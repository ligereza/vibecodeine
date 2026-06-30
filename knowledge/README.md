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
```

Los datos pueden ser incompletos. Usar `confidence`, `source` y `notes` antes que inventar certezas.
