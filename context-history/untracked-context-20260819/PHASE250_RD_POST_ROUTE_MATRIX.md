# Phase 250 - RD POST route matrix

Date: 2026-08-15 (America/Santiago)
Owner: LUNA principal

## Static surface

AST parsing of `/home/mak/flujo/src/flujo/web/hub.py` and the `do_POST`
handler returned exit 0 and found 16 literal POST paths. The matrix below
separates transient computation, read-like POSTs, local mutators and command/
automation boundaries.

| POST path | Class | Write set / effect | Verification | Gate |
|---|---|---|---|---|
| `/api/comando` | command boundary | manifest-declared command may read or mutate; destructive commands require confirmation | static gate | explicit command/input authority |
| `/api/plano/render` | transient compute | layout/rider/cost payload; module cache reload only | Phase 29 HTTP fixture 200 | no live write needed |
| `/api/cotizacion/render` | transient compute | quote payload in memory | Phase 29 HTTP fixture 200 | no live write needed |
| `/api/parse-pedido`, `/api/parse-real-pedido` | parse/read | parsed request payload | static/CLI gates | no persistent write |
| `/api/run-safe-command` | command boundary | whitelisted manifest command can mutate; origin and size checks | static security gate | explicit command authority |
| `/api/plano-simbolos/trazar` | transient preview | generated SVG response only | static route; internal trace fixture not live | bounded image input if promoted |
| `/api/plano-simbolos` | local mutator | `data/plano_simbolos/<slug>.svg` and `data/plano_simbolos.json` | Phase 233 temp-root fixture exit 0 | live symbol authority |
| `/api/create-job-draft` | job mutator | `jobs/<name>/` brief/intake/result files | static only in current gate | named temporary/live job authority |
| `/api/auto-pending-flyers` | automation mutator | pending flyer/job/output surfaces | static only | explicit automation authority |
| `/api/list-datadrops` | read-like POST | list response; no intended write | static | none |
| `/api/rd-db/logo` | asset mutator | logo file under `knowledge/logos/descargas` and related metadata | Phase 222/233 temp-root fixture exit 0 | live asset authority; no provider download |
| `/api/datadrop-upload` | asset mutator | datadrop image, manifest and analysis under datadrops | Phase 233 temp-root fixture exit 0 | live asset authority |
| `/api/datadrop-analyze` | metadata mutator | updates temporary/datadrop manifest analysis | Phase 233 temp-root fixture exit 0 | live datadrop authority |
| `/api/datadrop-prepare-package` | review-output mutator | `datadrops/_review_package.txt` | Phase 233 temp-root fixture exit 0 | live output authority |
| `/api/datadrop-scan-incoming` | intake mutator | scans/moves incoming datadrop material into workspace | static only | explicit intake authority |

## Result

All 16 routes have a known owner/effect and write-set classification. The
transient quote/plano paths are already validated; symbol/logo/datadrop helper
mutators pass isolated fixtures. The live mutators, job draft, automation,
command boundary and incoming scan remain gated because they can create or
alter user data. No POST was sent to the live hub in this phase.

## Safety and next action

No source, database, asset, job, provider, service, cron or WIN path changed.
The next executable local step is complete route documentation; the remaining
step requires a named target and rollback authority for one live mutator.

