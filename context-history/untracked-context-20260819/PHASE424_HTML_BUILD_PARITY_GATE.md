# Phase 424 - HTML generated parity build gate

Date: 2026-08-15
Agent: LUNA principal
Scope: validate the canonical React/Vite HTML build without overwriting
`context/*.html` or `web/dist/index.html`.

## Checks

1. `npm run typecheck` in `/home/mak/flujo/web`: exit 0 (`tsc --noEmit`).
2. A temporary `npm run build -- --outDir <tmp>` attempt: exit 127. The local
   `web/node_modules/.bin/vite` and `vite/bin/vite.js` are mode `644`, so the
   npm shell wrapper cannot execute. No install or permission change was made.
3. Direct `node node_modules/vite/bin/vite.js build --outDir <tmp>` attempt:
   exit 1. The environment reports Node.js `18.20.4`, while the installed
   Vite requires Node `20.19+` or `22.12+`, and Rollup cannot load the optional
   module `@rollup/rollup-linux-x64-gnu`.
4. Both build attempts targeted temporary `/tmp/mak-flujo-html-*` paths. No
   canonical HTML or source file changed.

## Disposition

The source type contract is green, but generated parity cannot be claimed from
this environment. The context aliases remain the currently served, previously
validated artifacts; `web/dist/index.html` remains a newer but unverified
build output. The safe recovery is an explicit Node/runtime dependency repair,
followed by a temporary build and then a reviewed copy step. That repair is
not performed here because it would alter the local dependency environment and
requires its own bounded authorization.

## Risks

- Copying `web/dist/index.html` into `context/*.html` now could change the hub,
  plano and SVG behavior without a successful build/runtime validation.
- Installing or replacing Rollup/Node dependencies could alter the workspace
  beyond the HTML owner gate.
- Existing context aliases are identical and route-selected, so they should
  remain one generated family rather than be independently edited.

## Next concrete action

Keep the HTML write gate closed. Resolve the local Node/Vite dependency
environment in a separately bounded step, or continue read-only owner mapping
for RD/plano/venue/portfolio artifacts while preserving the current aliases.
