# FLUJO branch capabilities

This branch owns the portable workflow engine, CLI and workspace Hub.

## Owned surfaces

- `src/flujo/cli.py`: command-line entrypoint and orchestration.
- `src/flujo/web/hub.py`: workflow/workspace Hub, default port `8765`.
- `src/flujo/knowledge/`: evidence-governed project and system contracts.
- `tools/`: engine-facing operator tools required by the `flujo` lane.

## Validation

```text
python -m pytest -m flujo -q
python -m flujo --help
```

## Transferable consumers

`project_api.py`, `system_status.py`, `departments.py` and the
`data/mak_knowledge.db` schema are shared contracts. Transfer uses typed JSON
payloads and explicit source references; this branch does not import the MAK
Hub implementation.
