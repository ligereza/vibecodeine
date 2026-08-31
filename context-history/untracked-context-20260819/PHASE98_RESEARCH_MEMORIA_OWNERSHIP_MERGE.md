# Phase 98 — research memoria ownership merge

## Scope and evidence

The active root `/home/mak/research/memoria.py`, canonical
`/home/mak/flujo/cultura/mak_research/memoria.py` and WIN historical copy were
byte-identical (SHA-256
`457f7fad5a92af4fc24e6caadcf06dee4fab2fe169557e24a5e2d7e081f09c4e`). Root
research consumers import `memoria` locally from real entrypoints such as
`grafo.py` and `interfaz.py`; therefore deleting the root module would break
those direct paths.

## Action

Replaced only `/home/mak/research/memoria.py` with a compatibility projection
to the canonical implementation. The bridge re-exports the implementation and
retains the direct `python memoria.py ...` behavior by forwarding `main()` when
run as `__main__`. Canonical source, WIN, indexed memory, logs and generated
outputs were not changed.

## Foreground validation

- Root import from `/home/mak/research`: exit 0; canonical function and memory
  directory contract were available.
- Root `python memoria.py --help`: exit 0; the direct entrypoint remained
  callable and did not index or write data.
- Canonical compile plus root bridge compile: exit 0.
- No persistent research, worker, hub, Blender or Ollama process remained.

## Rollback and risk

Rollback is local: restore the pre-edit root file from the WIN historical copy
or the recorded SHA. The bridge intentionally preserves public and private
module names but changes `__file__` to the projection path; callers depending
on module metadata remain an open low-risk check. No data mutation was run.

## Result

The active research memory implementation now has one owner while the root
department entrypoint remains usable. This is a bounded ownership merge, not a
data or whole-tree cleanup.
