# Phase 118 - tandas root projection merge

## Scope and ownership evidence

The active FLUJO consumers import
`cultura.mak_plataforma.tandas`: `src/flujo/cli.py`,
`src/flujo/autonomia.py`, `cultura/mak_conductor/handler_registry.py` and
the MAK tandas tests. `/home/mak/plataforma/tandas.py` had the same runtime
contracts but a divergent evidence-path manifest. WIN additionally carried
historical external-dispatch fields (`out_dir`, ledger paths, instruction and
image paths). Those differences are preserved in
`/home/mak/WIN/flujo/cultura/mak_plataforma/tandas.py` and were not edited.

## Change

Replaced only `/home/mak/plataforma/tandas.py` with a compatibility projection
to `/home/mak/flujo/cultura/mak_plataforma/tandas.py`. The projection exports
the canonical module namespace and delegates its direct `__main__` entrypoint
to the canonical `main()`. No database, ledger, evidence, provider or output
was touched.

## Foreground validation

Command:

```text
/home/mak/venvs/flujo/bin/python -m py_compile \
  /home/mak/plataforma/tandas.py \
  /home/mak/flujo/cultura/mak_plataforma/tandas.py
/home/mak/venvs/flujo/bin/python /home/mak/plataforma/tandas.py areas
/home/mak/venvs/flujo/bin/python -m cultura.mak_plataforma.tandas areas
```

Results: compile exit 0; root `areas` exit 0; canonical `areas` exit 0; both
produced identical `mak-batch-v1` area JSON. Isolated imports of root and
canonical both returned `provider_plan(['groq', 'ollama']) ==
['groq', 'ollama']` and `validate_result({'items': []}) == (True, [])`.
No provider or external batch was called.

## Decision and risk

`MERGE_NOW`: yes for the unreferenced MAK root projection; canonical FLUJO is
the sole active owner. `MERGE_NOW`: no for WIN, whose historical dispatch
contract remains evidence. The remaining risk is an undocumented dynamic
consumer of the old root-only evidence manifest; the compatibility bridge
preserves the import and direct command surface but intentionally follows the
active canonical manifest.

## Next action

Run the remaining read-only department/entrypoint gates, then re-audit exact
and semantic duplicates by consumer. Keep production mutators, external
providers, empty field data, generated outputs, WIN and Git application
closed until their evidence gates are individually satisfied.
