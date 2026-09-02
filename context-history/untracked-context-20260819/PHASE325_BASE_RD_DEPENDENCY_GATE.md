# Phase 325 — base FLUJO/RD dependency gate

Date: 2026-08-15 (America/Santiago)
Scope: one active dependency slice: CLI + RD/privacy + hub imports.

## Consumer and environment

Consumer modules:

- `flujo.cli`
- `flujo.rd.database`
- `flujo.rd.datos`
- `flujo.rd.informe`
- `flujo.privacy`
- `flujo.web.hub`

Interpreter: `/home/mak/venvs/flujo/bin/python` with
`PYTHONPATH=/home/mak/flujo/src:/home/mak/flujo` and bytecode disabled. No
package installation or service startup was performed.

## Results

All six imports returned `IMPORT_PASS` and exit code 0. The same environment's
`python -m pip check` returned exit code 0: `No broken requirements found.`

Installed versions observed for the base `pyproject.toml` requirements:

```text
matplotlib 3.11.1
PyYAML 6.0.3
Pillow 12.3.0
pydantic 2.13.4
typer 0.27.1
rich 15.0.0
jsonschema 4.26.0
requests 2.34.2
boto3 1.43.66
```

All satisfy the declared lower bounds. This is a slice result for the
existing Linux environment; it does not certify optional provider, render,
desktop or Windows-global environments.

## Disposition

`VERIFIED_BASE_SLICE_NO_DEPENDENCY_EDIT`.

The base CLI/RD/privacy/hub consumer is importable and dependency-consistent.
The Windows `pip check` conflicts received earlier must remain evidence about
that Windows global environment, not be copied into Linux requirements.

## Changes and risks

- Files, databases, packages, services, providers, Git and WIN: unchanged.
- Risk: optional extras and external runtimes remain separate dependency
  slices; no broad upgrade is justified by this gate.
- Rollback: no rollback needed because no mutation occurred.

