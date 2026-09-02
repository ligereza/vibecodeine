# Phase 220 — post-quarantine validation and remaining gates

Date: 2026-08-15 (America/Santiago)

## Validation

- `python -m flujo health`: exit 0.
- `python -m flujo rd-db packs`: exit 0.
- Real-job `python -m flujo job status ...`: exit 0.
- Imports of `flujo.cli`, `flujo.web.hub` and `flujo.rd.datos`: exit 0.
- `/home/mak/curatoria_encolado` is absent from the active root.
- All four relevant user services remain `inactive`.
- OneDrive still reports the known disconnected mount during broad `find`; no
  repair was attempted.

## Remaining objective gates

The physical cleanup candidate was handled reversibly. The remaining
unfinished items are authority-dependent rather than undiscovered files:

1. real RD field-data source/acta and ingest authority;
2. explicit approval for live RD mutating routes and output destinations;
3. final optional runtime/provider/GPU checks where hardware or external
   services are required;
4. historical `panel_directivo.py` remains preserved incomplete evidence, not
   an active consumer.

The Git branch proposal is complete as a proposal but has not been applied.

## Next concrete action

Maintain the handoff at this boundary and do not fabricate field data or
external authority. If no new authority arrives, the next safe work is a
read-only evidence report of these remaining gates; no further broad cleanup
is justified.

