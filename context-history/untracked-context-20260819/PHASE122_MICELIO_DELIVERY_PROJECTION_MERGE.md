# Phase 122 - micelio delivery projection merge

## Scope and safety boundary

`/home/mak/flujo/cultura/mak_plataforma/entregar_micelio.py` is the active
delivery-gate implementation. The root variant at
`/home/mak/plataforma/entregar_micelio.py` had the same function surface and
only documentation drift. Both variants are external writers: `main()` can
reach the micelio over HTTP, write logs/data and invoke Git/PR commands.

## Change

Replaced only the MAK root file with a compatibility projection to the
canonical implementation. WIN, the repository, micelio endpoint, logs,
`iskvw` data and all Git state were untouched. No `main()` or `--dry-run` was
run against a service.

## Foreground validation

- Pre-merge AST gate: both variants exposed the same functions
  (`log`, `leer_grafo`, `git`, `contenido_en`, `_sin_generado`,
  `construir_salida`, `main`). The only diff was documentation.
- Post-merge `py_compile` for root and canonical: exit 0.
- Root `--help`: exit 0.
- Isolated root/canonical imports: exit 0; both exposed the same public
  helpers and `_sin_generado({'piezas': [], 'vinculos': []})` returned the same
  empty snapshot.
- No HTTP, log write, filesystem output, Git or PR action ran.

## Decision and risk

`MERGE_NOW`: yes for the root projection. The external-action boundary remains
unchanged and is now owned in one canonical file. A real micelio delivery is
still a separately authorized foreground operation; this phase does not claim
that it works against a live service.

## Next action

Re-run the mirror ownership inventory to confirm no non-projection semantic
Python candidates remain, then update the folder/duplicate cleanup matrix.
Preserve all data, evidence, generated outputs, logs, WIN and Git state.
