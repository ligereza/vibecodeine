# Phase 407 — RD mutation entrypoint static audit

Date: 2026-08-15 (America/Santiago)

## Validation

`/home/mak/flujo/src/flujo/web/hub.py` parsed with exit 0. AST inspection of
`HubRequestHandler.do_POST` found 16 literal routes:

```text
/api/auto-pending-flyers
/api/comando
/api/cotizacion/render
/api/create-job-draft
/api/datadrop-analyze
/api/datadrop-prepare-package
/api/datadrop-scan-incoming
/api/datadrop-upload
/api/list-datadrops
/api/parse-pedido
/api/parse-real-pedido
/api/plano-simbolos
/api/plano-simbolos/trazar
/api/plano/render
/api/rd-db/logo
/api/run-safe-command
```

The Phase250 matrix remains complete. Its 15 table rows intentionally combine
`/api/parse-pedido` and `/api/parse-real-pedido` because they share one
handler branch; no route disappeared.

## Write-set classification

| Class | Routes | Durable effect |
|---|---|---|
| transient/read | `cotizacion/render`, `parse-pedido`, `parse-real-pedido`, `plano-simbolos/trazar`, `list-datadrops` | response or read-only listing |
| local output | `plano/render`, `plano-simbolos` | render/output or symbol catalog paths |
| job/automation | `create-job-draft`, `auto-pending-flyers`, `comando`, `run-safe-command` | jobs, declared commands or automation outputs |
| asset/datadrop | `rd-db/logo`, `datadrop-upload`, `datadrop-analyze`, `datadrop-prepare-package`, `datadrop-scan-incoming` | logos, media, manifests, review package or intake paths |

No route was called. The source contains file-write and subprocess boundaries,
so AST success does not prove live mutation safety. Existing temporary fixture
evidence remains the allowed validation layer until a named live target,
expected output and rollback are supplied.

Disposition: `RD_MUTATION_ROUTES_STATIC_CURRENT; LIVE_POSTS_UNEXECUTED`.
