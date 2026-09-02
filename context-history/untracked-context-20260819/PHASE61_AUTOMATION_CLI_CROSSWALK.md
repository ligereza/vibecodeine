# Phase 61 — automation and non-serve CLI crosswalk

## Automation contract

The user confirmed the operational chain as:

```text
email subject `EVENTO ...`
  -> issue created with the URL inside
  -> local/GitHub issue queue
  -> bridge/render processing
```

This is now an accepted external contract, not a provider-availability
blocker. The hub reader remains truthful: `/api/automatizaciones` reads open
issues through `gh`, while the Gmail-to-issue segment is outside this repo.
No issue, email, render or external provider was contacted in this phase.

## CLI evidence

```text
python -m flujo --help
exit=0; 34 top-level command groups exposed

python -m flujo version
exit=0; v0.56.1

python -m flujo health
exit=0; jobs/inbox/projects/scripts/tools OK; 8 jobs; index present

python -m flujo doctor
exit=0; local Python/repo/workspace/jobs/inbox/datadrops checks OK;
working tree warning only

python -m flujo <job|rd-db|rd-datos|render|datadrop|privacy|brief|intake|eventos|knowledge> --help
exit=0 for all groups

python -m flujo rd-db testeos
exit=0; 42 sheets, 42 events, 1,831 test rows, 5,394 observations,
84 pending links; status candidate_evidence_pending_human_review

python -m flujo rd-db packs
exit=0; three packs listed
```

## Classification

The CLI surface is alive and broad. Read-only commands are verified for
entrypoint/help and selected RD outputs. Mutating families remain explicitly
separate: `rd-db build`, `rd-datos ingest/informe`, `job new/prepare/activate`,
`render run`, `knowledge ingest-example`, `datadrop ingest/scan/prepare`,
`eventos flyer-auto`, `airdrop apply` and `clean`. They need focused fixtures
or owner-approved real inputs; their existence is not evidence of failure.

## Next

Next map the RD asset surface and dependency slices, then design the final MAK
folder architecture and duplicate/tool consolidation policy before any cleanup
or Git branch proposal.
