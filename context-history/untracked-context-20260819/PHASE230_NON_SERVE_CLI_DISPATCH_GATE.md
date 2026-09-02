# Phase 230 — Non-serve CLI dispatch gate

## Scope

The complete top-level non-`serve` command dispatch surface was exercised with
`--help` in the base FLUJO venv. Help dispatch parses command registration and
option wiring without creating jobs, ingesting data, rendering outputs,
contacting providers or changing databases.

## Result

All 17 dispatch checks returned exit 0:

`--help`, `autonomia --help`, `micelio --help`, `rd-db --help`,
`rd-datos --help`, `airdrop --help`, `datadrop --help`, `job --help`,
`privacy --help`, `eventos --help`, `render --help`, `knowledge --help`,
`health --help`, `doctor --help`, `verify --help`, `version --help` and
`daily --help`.

This closes the dispatch/registration portion of objective 5. It does not
claim that mutating commands have been executed; those remain separate gates
requiring a bounded input/output contract.

## Validation

- Interpreter: `/home/mak/venvs/flujo/bin/python`.
- Source compile: `/home/mak/flujo/src/flujo/cli.py`, exit 0.
- Existing read-only command gate: Phase 227, all named read surfaces passed.
- No files, jobs, databases, assets, providers, services or WIN paths changed.

## Next concrete action

Keep mutating CLI commands classified by write set and proceed with the RD
database relation gate. Do not call mutators merely to turn dispatch help into
a false claim of integration.
