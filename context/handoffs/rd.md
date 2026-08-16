# RD department handoff

Status: contract and read-only runtime surface validated.
Current consumer: MAK Hub `8900`, RD packs/plano/rider and database reads.
Source of truth: RD JSON/YAML sources; `data/rd.db` is a generated projection.
Empty boundary: `data/rd_datos.db` is preserved and not merged into `rd.db`.

Validated surfaces: `/api/rd/summary`, `/api/rd/crosswalk`,
`/api/rd/cultura-relations` and the static plano editor route. The relation
graph keeps ambiguous venue names as review candidates.

Next action: after explicit authorization, test one approved EVENT workflow;
do not mutate either RD database during that test.
