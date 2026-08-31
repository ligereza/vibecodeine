# Phase 430 - OpenKlub source correction and RD rebuild

Date: 2026-08-15
Agent: LUNA principal
Scope: remove the known OpenKlub producer/venue conflation from the active RD
venue projection while preserving the original evidence and validating the
producer consumer.

## Actions

1. Preserved `knowledge/venues/openklub.yaml` in
   `context/quarantine/phase430_openklub_role_correction/openklub.yaml`.
2. Verified preserved SHA-256:
   `40c8ef77770c6581ca2d772f98408f801e6c41b7e167de8c7627f9af7711ebf9`.
3. Rebuilt the generated RD database with the operational runtime:
   `/home/mak/venvs/flujo/bin/python -m flujo rd-db build`.
4. Validated the RD venue CLI, OpenKlub producer CLI, SQLite role assertions and
   the independent JSON venue validator.

## Results

- RD build: exit 0.
- `rd-db venues`: exit 0; active venues are `espacio_riesco` and
  `paralelo_89`; `openklub` is absent.
- `rd-db productora openklub`: exit 0; OpenKlub remains a producer, with
  `Central Cultural [candidato_sin_confirmar]` and no venue ID.
- SQLite assertions: exit 0; producer present, conflated venue absent,
  unresolved candidate preserved.
- `tools/venue.py validar`: exit 0; 3 public JSON technical venues remain
  valid, including SCD.
- New `data/rd.db` SHA-256:
  `a1b547d2b658f8e27741f84d0e2e89f945d9401e58ea1b58adf636923459073f`.

## Changed files

- Moved one source file to reversible quarantine:
  `knowledge/venues/openklub.yaml` ->
  `context/quarantine/phase430_openklub_role_correction/openklub.yaml`.
- Regenerated `data/rd.db` from active sources.
- Updated `context/MD_CONTEXT_MASTER.md`, this report and `LAST_HANDOFF.md`.

## Rollback

```bash
mv context/quarantine/phase430_openklub_role_correction/openklub.yaml knowledge/venues/openklub.yaml
/home/mak/venvs/flujo/bin/python -m flujo rd-db build
```

The rollback restores the previous source role and generated projection. No
historical evidence was deleted.

## Risks and next action

The real venue for the OpenKlub event remains unknown; `Central Cultural` must
not be promoted by name similarity. Next, refresh any generated RD presentation
or panel fixture that explicitly counted the old three-venue projection, then
continue the venue/portfolio crosswalk without inventing a replacement ID.
