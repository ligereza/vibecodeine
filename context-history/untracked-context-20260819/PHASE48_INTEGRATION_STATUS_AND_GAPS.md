# Phase 48 — MAK FLUJO integration status and gap ledger

Identity: LUNA principal
Status: CONSOLIDATED_EVIDENCE

## Integrated local runtime

The real MAK `flujo serve` process has a verified safe GET surface of 12
endpoints: ping, status, RD packs, RD database projection, SVG listing aliases,
portfolio, show-kit, jobs, dashboard summary, event presets and hub roles.
Each returned HTTP 200 in one temporary process, which then shut down with no
remaining process and `writes_detected=false`.

The entrypoint contract is resolved: `flujo serve --help` and module help exit
0, `serve/server.py` and the `serve`/`app_alias` AST contracts match WIN, and
the real process responds at version `0.56.1`.

## Explicitly deferred boundaries

- `/api/rd-datos-summary`: active `rd_datos.db` is empty; synthetic demo CSVs
  and controlled evidence are not live field data. Normal connector writes
  schema, so only guarded fallback was tested.
- `/api/automatizaciones`: external GitHub/provider path via `gh`; real
  provider and mutating runner were not called.
- `/api/mak`: local fallback is integrated; configured external
  `FLUJO_MAK_URL/api/organismo` remains uncontacted.
- POST/job lifecycle, uploads, renderers, hardware/OSC and workers remain
  outside read-only migration gates.
- `/home/mak/RD` is a 1,743-file creative asset surface pending a named
  consumer and visual validation; no whole-tree merge is justified.
- Full `cli.py` differences remain historical/non-serve evidence after the
  serve AST contract was proven equal.

## Operating conclusion

The former WIN FLUJO APP hub is materially integrated into MAK for its local
read-only RD/ISKVW/CULTURA-supported surface. Remaining work is not a mass
file union: each deferred item needs its own owner, input authority, rollback
and runtime gate. No deletion, Git mutation, SSH, permanent service or
unapproved dependency installation occurred.

