# HANDOFF v0.42.2 - Migración Flexible de Branding

## Cambios
- **Migración:** El branding rígido se mueve a `knowledge/logos` y `logo-lab`.
- **Compatibilidad:** El comando `brand` se mantiene como legacy no bloqueante.
- **Seguridad:** Restaurada definición de todas las sub-apps en la CLI.
- **Logo Lab:** Implementado comando `knowledge logo-lab` como bridge operativo.

## Verificación
- py -m flujo verify
- py -m flujo knowledge logo-lab --help
