# Contributing to vibecodeine

## Entrada obligatoria para agentes

1. Lee `AGENTS.md`.
2. Lee `REAL_INFO.md`.
3. Toma la tarea del encargo actual, no de un handoff o plan histórico.
4. Abre sólo el dominio que necesitas.

Historia y decisiones anteriores: `HISTORICO.md`. El estado de la máquina MAK se mide con `.venv/bin/python tools/mak_status.py --json` cuando esa máquina está disponible.

## Cambios

- Trabaja en una rama y propone PR contra `main`; evita pushes directos a `main`.
- No conviertas issues, cierres de sesión, PHASE reports o archivos recuperados en backlog salvo que el usuario lo pida.
- Conserva las fronteras MAK/FLUJO/RD/iskvw/XIO descritas en `REAL_INFO.md`.

## Verificación

Usa `branch_profile.json`, `pyproject.toml` y las pruebas relevantes al cambio. El selector integrado declarado por el perfil actual es:

```bash
python -m pytest -m "mak or flujo or integration or repo_hygiene" -q
```

No declares “todo verde” si ejecutaste sólo una selección.

## Estilo

- Python >= 3.10.
- Código e identificadores nuevos: inglés salvo razones de compatibilidad.
- Productos humanos RD/iskvw: español correcto con diacríticos.
- No commitear credenciales ni artefactos pesados/regenerables.
