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
typed contracts and evidence references, and neither hub *requires* the
other: `cultura/mak_plataforma/hub.py` does import a handful of
`flujo.knowledge.*` modules (`product_view`, `portfolio_claims`, ...), but
every one of those imports is wrapped in `try/except` and degrades to
`None`/"motor_no_disponible" on a standalone MAK checkout without
`src/flujo/`. `src/flujo/web/hub.py` never imports MAK. The lane-specific
documents remain authoritative for runtime details:

- `CAPACIDADES_MAK.md` — MAK box, departments and machine-bound projections.
- `CAPACIDADES_FLUJO.md` — portable workflow engine, CLI and workspace.

## Verification

```text
python -m pytest -m "mak or flujo or integration or repo_hygiene" -q
python tools/test_lane_map.py --format text
```

The second command must print `contract_disagreements=0` and an empty
`not_covered=`. `--check` is not a real flag (the CLI only has `--format`,
`--select-changed` and `--write`); do not run `--write` as a "check" — it
overwrites `context/test_lane_map.json`'s per-test `assignments` schema
(read by `_load_lane_contract()`) with the coarser `lanes` summary schema
that `report()` produces, which the loader does not understand, silently
falling back to the embedded map on the next read.

The integrated profile is a validation baseline. Deployment still occurs from
the explicit `MAK` or `FLUJO` lane after its own gate passes.
