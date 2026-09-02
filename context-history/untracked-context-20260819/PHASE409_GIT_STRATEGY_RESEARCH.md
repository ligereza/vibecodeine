# Phase 409 — Git branching strategy research and recommendation

Date: 2026-08-15 (America/Santiago)

## Sources reviewed

- GitHub Flow: <https://docs.github.com/en/get-started/using-github/github-flow>
- GitLab branching strategies:
  <https://docs.gitlab.com/user/project/repository/branches/strategies/>
- Trunk-Based Development:
  <https://trunkbaseddevelopment.com/>

These are primary documentation sources for the compared workflows. The
recommendation below applies them to MAK's monorepo, one Linux runtime,
protected WIN evidence, independent integration slices and a small
agent/user team.

## Top three models

| Model | Shape | Strength | Cost/risk for MAK |
|---|---|---|---|
| GitHub Flow | `main` plus short feature branches and review/merge | Simple, easy rollback and clear review boundary | Needs discipline to keep branches small |
| GitLab Flow | feature branches plus optional environment/release branches | Useful for multiple deployments, versions or compliance gates | More branches and process than one MAK runtime currently needs |
| Trunk-Based Development | one trunk plus very short-lived task branches, or direct commits for tiny teams | Minimizes merge drift and long-lived branch divergence | Requires strong foreground checks before integration |

GitHub documents a short descriptive branch per unrelated change and a review
before merge. GitLab explicitly says to merge feature branches directly to
`main` for the simple case and not to add complexity beyond the product's
needs. Trunk-Based Development rejects long-lived development branches and
allows short-lived review branches or just-in-time release branches.

## Recommendation for MAK

Use **Trunk-Based Development with a GitHub-Flow pull-request boundary**:

```text
main (protected, always releasable)
  ├── codex/<area>/<small-slice>  -> review/checks -> main -> delete
  └── release/vX.Y (optional, temporary hardening only) -> tag -> delete
```

This is a recommendation/inference from the sources and the current repo
shape, not a claim that GitHub or GitLab requires this exact naming.

## MAK branch policy

1. `main` is the only permanent development branch.
2. Create a topic branch only when its bounded write set starts; do not create
   all planned branches in advance.
3. Each branch covers one consumer-backed slice and one reversible change.
4. Each branch merges directly to `main`, never into another topic branch.
5. Delete the topic branch after merge; keep the commit/tag as history.
6. Use a temporary `release/vX.Y` only for a real release hardening window;
   do not create `develop`, `staging`, or permanent environment branches.
7. Keep databases, credentials, WIN and bulk `portfolio_media` outside the
   normal source branch write set; version code, schemas, manifests and
   evidence references instead.

## Suggested topic names

These are names to use when work actually starts, not permanent branches:

```text
codex/rd/field-review
codex/rd/runtime
codex/flujo/event-bridge
codex/rd/assets
codex/portfolio/web
codex/mak/ownership
codex/tools/consolidation
codex/cleanup/confirmed-junk
```

The former sequential merge order is superseded. Independent slices should
each target `main` after their own checks. Only dependencies impose order; for
example, an ownership/path contract must land before a consumer that relies on
that new path. `codex/release/full-audit` is replaced by the optional temporary
`release/vX.Y` plus a final audit tag unless a real release requires a branch.

No Git branch, commit, merge, checkout, reset or push was performed.

Disposition: `TRUNK_BASED_PR_RECOMMENDED; LONG_LIVED_BRANCHES_REJECTED; GIT_UNTOUCHED`.
