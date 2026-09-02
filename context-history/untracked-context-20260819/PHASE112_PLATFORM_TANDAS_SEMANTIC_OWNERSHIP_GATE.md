# Phase 112 — platform tandas semantic ownership gate

## Scope and evidence

`tandas.py` exists in canonical MAK, root MAK and WIN. All three expose the
same main signatures and pass the basic provider/result contract fixtures, but
they are not interchangeable:

- canonical vs root differ in `AREAS[*].evidence_paths`, including whether
  `context/LAST_HANDOFF.md` or operational source paths are evidence;
- WIN additionally carries `out_dir`, ledger paths, `instruction` and image
  paths in the external dispatch payload;
- canonical is the active FLUJO/CLI consumer, while root is the direct
  platform surface and WIN is historical evidence.

## Foreground validation

Loaded all three files by isolated module path without starting providers.
For each variant:

- `provider_plan(["groq", "ollama"])` returned `['groq', 'ollama']`;
- `build_brief("rd_evidence", "fixture-1", providers=[])` returned an
  `in_progress` brief without writing a ledger or output;
- `validate_result({"items": []})` returned `(True, [])`;
- `validate_product_contract({"items": []}, "rd_evidence")` returned
  `(True, [])`;
- `run_external_batch` signature remained equal across variants.

All checks exited 0. No provider, queue, Ollama, ledger, brief, batch or
external action ran.

## Decision

`JUNK_CONFIRMED`: no. `MERGE_NOW`: no. This is a semantic ownership fork,
not an exact duplicate. Preserve all three until the evidence manifest and
external-batch payload contract are explicitly reconciled.

## Rollback and risk

No files were edited, so rollback is not applicable. The principal risk is
silently losing provenance paths or external dispatch metadata by replacing
one variant with another.

## Next action

Move to the next platform read-only consumer or define a dedicated contract
reconciliation slice for `tandas.py`; do not run external batches.
