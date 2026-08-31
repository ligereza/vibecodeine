# Phase 160 — backup projection gate

Date: 2026-08-15
Owner: LUNA-PRINCIPAL

## Selection

`backup.sh` is an exact source/runtime projection referenced by the
`MAK-ORGANISMO backup` schedule. The installed cron entry is paused. Running
it would create a tarball under `/home/mak/backups` and delete archives older
than seven days, so live execution is not permitted in this gate.

## Action and validation

Preserve the exact runtime copy in quarantine and replace only the runtime
projection with a wrapper to the canonical source. Validate both shell files
with `bash -n` and verify the wrapper's canonical path. Do not create a backup,
run retention, enable cron or touch user data.

## Result

`bash -n` passed for source and wrapper. In separate temporary HOME fixtures,
the canonical script and executable wrapper each produced one non-empty
`mak-YYYYMMDD.tar.gz` with the same fixture size (`324` bytes). The wrapper
was intentionally made executable (`0755`) because the declared cron command
invokes the target path directly; the canonical source remains unchanged at
`0644`. Temporary fixtures were removed and the process gate found no backup
script running. The former exact target hash
`6db6de7b9fffc757f68294c196d03a8017f3f7fdf1e1548232e4c64c3eecf292` remains
in quarantine.
