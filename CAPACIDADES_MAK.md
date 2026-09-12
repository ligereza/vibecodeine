# MAK branch capabilities

This branch owns the Linux MAK box surface and its department projections.

## Owned surfaces

- `cultura/mak_plataforma/hub.py`: human-facing MAK Hub on port `8900`.
- `plataforma/hub.py`: compatibility entrypoint for the MAK Hub.
- `cultura/mak_*/`: department, research and machine-bound projections.
- `tools/` and `data/`: box-side operators and read-only ledgers required by
  the `mak` lane.

## Validation

```text
python -m pytest -m mak -q
python cultura/mak_plataforma/hub.py --help
```

## Transferable consumers

The MAK Hub and the FLUJO Hub remain separate implementations. They share
`project_api.py`, `system_status.py`, `departments.py` and the
`data/mak_knowledge.db` schema through typed JSON payloads and explicit
`source_ref` values. A future transfer changes an adapter, not the other Hub.
