# Phase 147 — post-generator verification gate

Date: 2026-08-15

## Result

The canonical-tariff generator change passed the repository verification gates:

- `/home/mak/venvs/flujo/bin/flujo verify --no-pytest`: exit 0; compileall,
  health, version and temporary hub smoke passed at `0.56.1`.
- `npm run typecheck` in `/home/mak/flujo/web`: exit 0.
- bounded process check: no persistent hub, serve, generator, Vite or related
  process remained after validation.

The first two verification attempts used the wrong invoker (`flujo` absent from
PATH, exit 127; then the legacy `scripts/flujo.py` dispatcher, exit 2 because
`verify` was retired there). Neither attempt changed files. The official venv
entrypoint was then used and passed.

## Decision

The code consolidation is accepted as a verified consumer change. Generated
live job/RD delivery files remain unchanged until a separate promotion gate
checks the isolated output against the human delivery contract. WIN, databases,
source documents and evidence remain untouched.

## Next action

Perform the bounded promotion review: list the exact active output paths,
compare the isolated canonical JSON/SVG/PDF semantics with the intended
delivery role, and either promote the explicitly approved output set with a
backup or record `NO_PROMOTE` and continue to the next consumer. Then refresh
the objective matrix.

