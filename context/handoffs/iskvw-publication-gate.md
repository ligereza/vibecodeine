# Branch handoff: iskvw/publication-gate

Branch: `iskvw/publication-gate`
Contract: `contracts/branches/iskvw-publication-gate/agents.md`
Owner: `LUNA-505`
Base commit: `e0ff6a1`

## Current objective

Turn the existing publication scope into an executable regression gate without
changing deployment behavior or publishing anything.

## Baseline evidence

- `publicar_iskvw.yml` is `workflow_dispatch` only; no push trigger.
- The workflow copies `iskvw/.` into the Pages staging tree.
- `gen_archivo_iskvw --fuente todo` uses the public substrate filter and keeps
  research essays opt-in.
- Existing Git/web and generator tests pass before this branch.

## Open items

- Promote the durable gate result to the root handoff before branch deletion.

## Next concrete action

Added executable assertions for manual publication, the `cp -r iskvw/.` scope,
and exclusion of RD databases, technical venue records, Cultura, MAK and WIN.

Validation results:

- Git/web and generator suite: exit 0, `17 passed`;
- Python compilation: exit 0;
- `git diff --check`: exit 0;
- no deploy, network call, Cloudflare change or generated public artifact.

## Disposition

`ISKVW_PUBLIC_SCOPE_GREEN; RD_VENUE_EXCLUDED; MANUAL_DEPLOY_PRESERVED`

## Next concrete action

Promote this result to the root handoff, remove the temporary branch contract
and handoff, fast-forward `main`, and delete the short-lived branch.

Last verified: 2026-08-15 America/Santiago.
