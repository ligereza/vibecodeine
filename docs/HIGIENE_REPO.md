# Higiene del repositorio

La regla de higiene principal es evitar que outputs, cachés y documentación histórica vuelvan a competir con las fuentes reales.

## Orientación

- Agentes: `AGENTS.md` → `REAL_INFO.md`.
- Historia: `HISTORICO.md`.
- No crear nuevos handoffs globales, “current state”, “master context” o “next action” permanentes.
- No commitear credenciales, caches, bases regenerables ni medios pesados salvo que exista una decisión explícita de producto/archivo.

## Antes de cerrar un cambio

```bash
git status --short
```

Después ejecuta sólo los checks que correspondan al área tocada; para el baseline integrado consulta `branch_profile.json`.

La versión antigua de este documento contenía rutas, comandos Windows y un `LAST_HANDOFF` que ya no representan la jerarquía documental. El detalle permanece en Git.
