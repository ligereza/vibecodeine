# BRANCH AGENT CONTRACT

Copy this file into the active topic branch as:
`contracts/branches/<branch-id>/agents.md`.

## Identity

- Branch: `<branch-name>`
- Base commit: `<commit>`
- Agent: `<LUNA-N or human owner>`
- Domain: `rd | iskvw | cultura | tools`
- Consumer: `<real consumer>`

## Objective

State one bounded improvement or bug fix. Do not turn this branch into a
department-wide rewrite.

## Allowed write set

- `<path or path family>`

## Read-only context

- `<path or path family>`

## Forbidden changes

- Do not modify the current root README or its SVG artwork.
- Do not modify unrelated domains, databases, credentials or generated
  projections.
- Do not add permanent branches, services, cron jobs or external providers.

## Dependency contract

- Python version: `<version>`
- Project source: `pyproject.toml`
- Extras/groups: `<base/dev/rd/iskvw/cultura/web>`
- Dependency changes in this branch: `<none or exact packages and reason>`
- Lock/requirements update: `<path and command>`

## Validation gate

```text
<install command>
<compile/import command>
<focused test command>
<entrypoint or export check>
```

## Rollback

State the exact files/commit to revert and the data that must not be touched.

## Merge condition

The branch is mergeable only when the consumer works, the focused tests pass,
the dependency contract is reproducible and the exclusive handoff is complete.
