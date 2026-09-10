# Integrated main capabilities

`main` is the reviewed Git baseline that carries MAK and FLUJO together. It is
not a third runtime and it does not replace either operational lane.

## Included surfaces

- MAK source and Hub: `cultura/mak_*/` and `cultura/mak_plataforma/hub.py` on
  port `8900`.
- FLUJO source and App: `src/flujo/` and `src/flujo/web/hub.py` on port
  `8765`.
- Integration contracts and tests: `requirements-integration.txt`,
  `tests/` and the `integration` marker.

## Ownership boundary

The MAK and FLUJO hubs remain separate implementations. They may exchange
typed contracts and evidence references, but neither hub imports the other.
The lane-specific documents remain authoritative for runtime details:

- `CAPACIDADES_MAK.md` — MAK box, departments and machine-bound projections.
- `CAPACIDADES_FLUJO.md` — portable workflow engine, CLI and workspace.

## Verification

```text
python -m pytest -m "mak or flujo or integration or repo_hygiene" -q
python tools/test_lane_map.py --check
```

The integrated profile is a validation baseline. Deployment still occurs from
the explicit `MAK` or `FLUJO` lane after its own gate passes.
