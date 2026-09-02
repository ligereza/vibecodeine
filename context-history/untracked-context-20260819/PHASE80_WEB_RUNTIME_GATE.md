# Phase 80 — FLUJO web runtime gate

## Scope

Physical search began at `/home/mak/*` and narrowed to the active consumer
`/home/mak/flujo/web`. The package has `typecheck`, normal hub build,
standalone plano build and standalone RD build scripts. Local `node_modules`
and `package-lock.json` exist.

## Validation

- `npm run typecheck --prefix /home/mak/flujo/web` -> exit `0`.
- `node node_modules/vite/bin/vite.js --version` -> exit `0`, Vite 7.3.2.
- Temporary Vite build -> exit `1` before output creation.

## Blocking evidence

1. Node is `18.20.4`; installed Vite requires Node `20.19+` or `22.12+`.
2. Rollup optional native module `@rollup/rollup-linux-x64-gnu` is absent.
3. Local `.bin/vite` is not executable, so `npm exec` also returned
   `vite: Permission denied` (exit `127`); invoking the JS entrypoint confirmed
   the independent Node/native-module failures.

## Decision

TypeScript is verified. The web build remains `BLOCKED_LOCAL_RUNTIME`, not
`INTEGRATED`, because package installation and Node replacement are outside the
current authorized action. No source, lockfile, node_modules, dist output or
MAK runtime changed.

## Recovery

Use a supported Node runtime and restore the lockfile's platform optional
Rollup package, then rerun the three build configurations into bounded output
directories and validate their copy projections. Do not delete node_modules or
lockfiles or install packages automatically.
