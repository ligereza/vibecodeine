# Phase 273 — language consumer and projection gate

Date: 2026-08-15 America/Santiago  
Owner: LUNA principal  
Subagents: none

## Scope

Started at `/home/mak/*`, then audited `/home/mak/lenguaje` against
`/home/mak/flujo/cultura/mak_lenguaje` and active department manifests. The
question was whether the root language directory could be fused or removed.

## Physical and consumer evidence

`/home/mak/lenguaje` contains:

- runtime Python tools: `corregir.py`, `hook_barrido.py`, `lenguaje_lib.py`,
  `medir.py`;
- dictionary assets under `diccionarios/`;
- mutable lexicon outputs under `lexico/`;
- shell entrypoints `cron_lexicon.sh` and `instalar_diccionarios.sh`;
- Python cache/log artifacts.

The active crosswalk found direct references from the canonical platform
manifest and roles to `/home/mak/lenguaje/cron_lexicon.sh` and
`/home/mak/lenguaje/hook_barrido.py`. The canonical language package itself
also deliberately sets `BASE = "/home/mak/lenguaje"`. Therefore the root
directory is a load-bearing runtime projection/data owner, not unconsumed
duplicate material.

## Exact projection comparison

```text
corregir.py              cmp rc=0
hook_barrido.py          cmp rc=0
lenguaje_lib.py          cmp rc=0
medir.py                 cmp rc=0
cron_lexicon.sh          cmp rc=0
instalar_diccionarios.sh cmp rc=0
```

The six files exist in both locations and are byte-identical. Similarity is
therefore established, but removal is not authorized: active callers use the
root paths and the root path owns dictionaries/lexicon state. The safe current
model is one semantic implementation plus a retained runtime projection,
until a separate path-injection migration is designed and validated.

## Static/runtime gate

```text
root Python AST parse: 3/3, all rc=0
root shell syntax: 2/2, all rc=0
relevant user units: inactive (5/5)
installed crontab: all entries paused; active non-comment count 0
focused tests: 47 passed, PYTEST_RC=0
```

The focused tests were:

```text
tests/test_idioma_ratchet.py
tests/test_mak_mirror_fixes.py
tests/test_mak_organos_visibles.py
tests/test_operational_entrypoints.py
```

The first run exposed two contract issues caused by the Phase 270 quarantine
and a newly declared local variable in `src/flujo/cli.py`. The language
ratchet now excludes `context/quarantine/` as reversible evidence, while the
CLI-only locals `valor` were renamed to English `amount`/`key`; behavior and
the user-facing data key `valor_dia_clp` are unchanged. The rerun passed.

No hook, cron entry, dictionary installer, provider, database, service or
external system was executed or changed. WIN was untouched.

## Disposition

`/home/mak/lenguaje` stays in place as an active runtime/data projection.
`/home/mak/flujo/cultura/mak_lenguaje` remains the semantic owner for the
language module. Do not delete or merge dictionaries, lexicon outputs, logs or
the six exact projections by hash alone.

## Rollback

No filesystem move occurred. The code-only ratchet/CLI edits are reversible by
the normal file-level patch review; no database or runtime state requires
rollback. The root language paths remain unchanged.

## Next concrete action

Proceed to the next review surface, `/home/mak/trazos`, with the same order:
physical inventory, Spanish/English-aware consumer mapping, exact/semantic
crosswalk, then fixture/static validation. Do not merge creative source or
generated SVG/PDF material by filename or hash alone.
