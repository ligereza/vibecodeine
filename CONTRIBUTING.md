# Como contribuir a flujo

Repo personal de organizacion creativa con CLI unificada (`flujo`).

## Entrada obligatoria

1. Lee `CLAUDE.md` (raiz): identidad, mision, flujo de trabajo y reglas. Es la
   entrada unica para cualquier agente, humano o IA.
2. Estado actual: `context/LAST_HANDOFF.md`. Pendientes priorizados:
   `context/PLAN_SIGUIENTE_AGENTE.md`.

## Proponer cambios

1. Abre un issue o mensaje describiendo el cambio.
2. Rama + PR contra `main`; el CI debe pasar. Sin push directo a `main`.
3. Agentes sin push usan el protocolo airdrop (`docs/AGENT_AIRDROP_PROTOCOL.md`):
   ```bash
   py scripts/validate_airdrop.py
   py scripts/run_airdrop_checks.py "mensaje corto"
   ```

## Verificacion minima

```bash
py -m compileall src/flujo
py -m pytest tests/ -q
py -m flujo verify
```

## Estilo de codigo

- Python 3.10+; tipado con `from __future__ import annotations`; stdlib primero.
- Sin `print()` en modulos: usar `rich.console` o logging.
- Tests con pytest en `tests/test_<modulo>.py`.
- No subir archivos pesados ni credenciales.
- Windows usa `py` (no `python`/`python3`).
