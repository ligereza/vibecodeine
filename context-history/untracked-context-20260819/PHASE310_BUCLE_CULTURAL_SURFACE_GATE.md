# Phase 310 — bucle cultural surface gate

Date: 2026-08-15 America/Santiago  
Owner: LUNA principal  
Status: `INDEPENDENT_CULTURAL_SOURCE_PROTECTED`

## Scope

The search started at `/home/mak/*` and narrowed to the non-Git working
surface `/home/mak/bucle`. The embedded `.git` directory was excluded from
the physical asset inventory and was not used as an inventory or migration
source. Active FLUJO/cultura/departments were scanned for exact path
consumers in Spanish and English.

## Physical findings

The non-Git surface contains exactly 10 files: one README, one LICENSE, two
SVGs (`ALLTO.svg`, `tottl.svg`) and six PNGs (`BOCAS.png`, `DIENTE.png`,
`DIENTES.png`, `JUNTOS.png`, `LIP.png`, `boca y dientes.png`). All non-Git
files share the same narrow mtime window on 2026-07-18, and no exact duplicate
group exists within the surface.

The README says only `No mas bucles`; no runtime contract, manifest, job ID or
FLUJO launcher is present. The folder is a cultural/source project with
visual assets, not a Python department or installable tool.

## Consumer and provenance decision

An exact path scan of active source/departments found zero references to
`/home/mak/bucle`. Generic words such as `tapiz` and `vibecodeine` appear in
unrelated FLUJO documentation and repository metadata, but they do not prove
that these visual files are consumed.

`bucle` is therefore `INDEPENDENT_CULTURAL_SOURCE_PROTECTED`. Do not copy it
into `flujo/projects`, `RD`, `trazos` or `assets` by visual similarity. A
future adoption requires a named project consumer and a deliverable manifest.

## Foreground validation

```text
file on README, LICENSE, 2 SVG and 6 PNG files: valid identified formats
ElementTree parse of ALLTO.svg and tottl.svg: 2/2 SVG_OK
exact active path scan: 0 consumers
exact-hash inventory of the 10 non-Git files: 0 duplicate groups
```

No file changed, moved, deleted or rendered. WIN, FLUJO, databases, assets,
providers, services and Git state were untouched.

## Risk and rollback

The risk is provenance loss: filenames and artwork may be meaningful to the
author even without machine metadata. The rollback is the unchanged
`/home/mak/bucle` surface. No quarantine is warranted without a separate
creative/archive decision.

## Next action

Continue with `/home/mak/vibecodeine` using the same physical-first static
crosswalk. Treat it as a potentially separate source project/dependency; do
not inspect or mutate its Git history, install dependencies, call providers or
merge it into FLUJO by repository name alone.
