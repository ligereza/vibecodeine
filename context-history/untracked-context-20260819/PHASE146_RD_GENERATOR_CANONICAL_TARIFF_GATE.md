# Phase 146 — RD generator canonical tariff gate

Date: 2026-08-15
Scope: active RD generator and its job/delivery artifacts.

## Finding

`/home/mak/flujo/jobs/2026-07-04_eventos-brief/flows/gen_packs.py` contained a
second hardcoded copy of the RD pack names, prices, inclusions and complete-pack
breakdown. This was a real consumer duplication, not disposable history. The
active canonical source is `/home/mak/flujo/data/rd_packs.json`, already shared
by the Python rider, quote flow and web tariff.

## Change

The generator now reads `data/rd_packs.json` and adapts its canonical pack IDs
to the delivery card numbering (`1`, `2`, `3`). It derives:

- pack names, prices, volunteers, dimensions and inclusions;
- the complete-pack breakdown from canonical percentages;
- add-on deltas from canonical pack prices.

The generator's visual/layout logic and output destinations are unchanged. It
still writes only when explicitly run, and supports isolated `--out-job`,
`--out-svg` and `--scratch` destinations.

## Validation

- `python3 -m py_compile .../flows/gen_packs.py`: exit 0.
- isolated generator run under `/tmp/phase146-rd-canonical.6bXgfg`: exit 0;
  generated two SVG variants, two editable SVG variants, one JSON and four
  HTML scratch wrappers.
- generated pack names: `Informativo`, `Testeo y Informativo (ambos)`,
  `Servicio Completo (masivo)`.
- generated prices: `250000`, `300000`, `500000` CLP.
- generated complete breakdown: `300000 + 70000 + 50000 + 45000 + 35000 =
  500000`, percentages `60/14/10/9/7`.
- generated add-ons: `50000` and `200000`.

The previous live job JSON/SVG/PDF files were not overwritten. Their old names
and wording are retained as delivery snapshots until the next output promotion
gate. The RD dark plan/rider PDF and the job plan/rider PDF are byte-identical;
the combined brief PDFs and pack JSON/SVG files are not byte-identical to the
canonical RD delivery variants, so they remain classified as source/output or
delivery variants rather than exact junk.

## Risk and next action

Promoting regenerated outputs without a human delivery review could replace a
previously sent document. No promotion, deletion, PDF replacement or WIN
change occurred in this phase. Next: review the isolated generated output,
then promote only the explicitly identified active delivery files and run
foreground verification. Keep historical RD/WIN copies protected.

## Commands and codes

- bounded RD job/delivery inventory: exit 0.
- PDF metadata and SHA-256 comparison: exit 0.
- first JSON-shape probe assumed a list and exited 1; no files changed; the
  corrected shape probe exited 0.
- canonical generator patch applied with `apply_patch`; one CRLF-to-LF
  formatting normalization preceded it.
- compile and isolated generation: exit 0.

