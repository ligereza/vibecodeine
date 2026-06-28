# Integrar los subcomandos al dispatcher de flujo

Este airdrop trae un `src/flujo/__main__.py` que enruta:
`serve · index · route · doctor · version`.

## Caso A — tu repo NO tiene __main__ propio
No haces nada: el `__main__.py` del airdrop ya te da `py -m flujo <cmd>`.

## Caso B — tu repo YA tiene dispatcher (app/health/portal...)
NO sobreescribas tu `__main__.py`. En su lugar, registra los nuevos subcomandos
delegando a cada modulo. Patron generico:

```python
# dentro de tu dispatcher, donde resuelves el subcomando:
def _route(cmd, rest):
    if cmd == "serve":
        from flujo.serve import server;   return server.main(rest)
    if cmd == "index":
        from flujo.index import indexer;   return indexer.main(rest)
    if cmd == "route":
        from flujo.route import resolver;  return resolver.main(rest)
    if cmd == "doctor":
        from flujo.__main__ import _doctor; return _doctor()
    # ... tus comandos existentes (app, health, portal) ...
```

Si usas argparse con subparsers, agrega uno por comando con
`add_argument("rest", nargs=argparse.REMAINDER)` y delega `module.main(args.rest)`.

## Verificacion
```
py -m flujo doctor
py -m flujo serve --open
```

## Reglas del repo
- Windows + py (no python).
- ASCII-only en handoffs.
- No tokens, no datos sensibles.
- Aplicar via airdrop:
    py scripts/validate_airdrop.py
    py scripts/run_airdrop_checks.py "feat: flujo serve + hub + index + route"
