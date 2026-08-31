# Phase 234 — Active projection AST gate

## Scope

The current active-code roots were parsed recursively: FLUJO source/culture,
Research, Codex, Curatoria, Plataforma, Vigia, Lenguaje and `/home/mak/bin`.
Generated `codex/piezas`, virtual environments, logs, caches, state, reports
and Git metadata were excluded because they are evidence/data, not active
Python entrypoints.

## Result

`ACTIVE_AST_TOTAL=445|OK=444|FAIL=1`.

The only failure is `/home/mak/plataforma/panel_directivo.py`, line 145:
`SyntaxError: expected 'except' or 'finally' block`. The file ends inside a
truncated helper, has no bounded active launcher/consumer, and is already
classified as preserved incomplete evidence. It was not repaired or deleted;
repairing it would require inventing the missing tail and its orchestration
contract.

The other 444 active Python files parse successfully. This gate does not claim
all external providers, optional hardware or mutating paths are live; those
remain separately classified.

## Validation

- Foreground AST command returned exit 0 after reporting the one classified
  failure.
- The previous non-`serve` CLI and RD route fixtures still pass.
- No source, data, asset, service, provider, WIN or Git path changed.

## Next concrete action

Treat the panel as excluded historical/incomplete evidence and proceed to the
final department/runtime health matrix. Do not reconstruct or promote it as a
working MAK tool without a named implementation request.
