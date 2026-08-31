Identity: LUNA principal

# Phase 34 — optional MAK status panel no-network gate

## Decision

The `/api/mak` route is integrated for its local, unconfigured fallback. With
`FLUJO_MAK_URL` absent, it returns a truthful `disponible=false` and
`configurado=false` response while still exposing the local read-only `tandas`
surface. A direct call proved that no external `urlopen` occurs in this state;
the temporary local GET also passed with HTTP 200 and zero writes.

The configured branch remains deferred external runtime. It would call
`<FLUJO_MAK_URL>/api/organismo` in another process, which is outside this
migration boundary. No URL was contacted, no SSH was used and no MAK service
was started.

## Contract

```text
GET /api/mak
  FLUJO_MAK_URL unset -> local fallback + local tandas ledger reads
  FLUJO_MAK_URL set   -> external /api/organismo (deferred, not called)
```

The static vocabulary covered `MAK`, `mak`, `status`, `estado`, `organismo`,
`tandas`, `ledger`, `health`, `salud`, `configured`, `configurado`,
`disponible`, `external`, `externo`, `local` and `network`.

## Static and fallback gate

Foreground command: AST parse of `src/flujo/web/hub.py`; environment check with
`FLUJO_MAK_URL` removed for the process; direct fallback invocation with
`urllib.request.urlopen` monkeypatched to fail if called; then a temporary
local HTTP server and one GET request.

Observed exit code: `0`.

- Hub AST parse: PASS.
- Environment: `FLUJO_MAK_URL` unset.
- Direct fallback: `disponible=false`, `configurado=false`, error identifies
  the missing variable, local `tandas` object present, external urlopen calls
  `0`, PASS.
- `GET /api/mak` on temporary localhost server: HTTP 200 with the same
  unconfigured fallback, PASS.
- Protected hub and local ledger sizes/mtimes: `writes_detected=0`.
- Temporary server shutdown: PASS.

Final status: `INTEGRATED_LOCAL_FALLBACK`; configured external branch is
`DEFERRED_EXTERNAL_RUNTIME`.

## Mutation boundary and rollback

The local fallback reads only the optional ledger paths and environment state.
The configured branch is intentionally not invoked because it crosses a
process/network boundary. Rollback is temporary-server shutdown and removal of
the test-only environment override; no source, ledger or service state was
changed.

## Risks and next action

- A configured `FLUJO_MAK_URL` may point to a live MAK box or another runtime;
  no availability or schema claim is made here.
- The local ledger paths can be overridden by environment variables, so their
  physical availability is optional and read-only in this route.
- Continue with a local read-only hub consumer. Keep external MAK status,
  SSH, workers and mutating automation deferred until a separate authorized
  boundary exists.
