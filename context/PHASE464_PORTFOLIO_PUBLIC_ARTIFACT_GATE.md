# Phase 464 — public portfolio artifact gate

## Scope

The public ISKVW artifact was checked without starting a service, installing a
package or modifying generated repository data.

## Evidence

- `node tools/iskvw_piel_smoke.mjs campo` exited 0.
- `node tools/iskvw_piel_smoke.mjs terminal` exited 0.
- `node tools/iskvw_piel_smoke.mjs venue` exited 0.
- The public inputs `iskvw/piel/campo/index.html`,
  `iskvw/datos/campo.json`, `iskvw/datos/obras.json` and
  `iskvw/piel/trazos/_indice.json` exist and are non-empty.
- `git diff --check` exited 0 for the isolated write set.
- The already-present `@babel/parser` parsed `web/src/data/portfolio.ts` and
  `web/src/components/PortafolioPanel.tsx` with TypeScript/JSX plugins; both
  exited 0 at syntax level.
- Python compilation and the Phase 462 contract gate still exit 0.

The workspace dependency runtime was inspected. It contains Node but no
TypeScript compiler, and the isolated worktree has neither `tsc` nor a local
`node_modules/.bin/tsc`. `npm run typecheck` therefore remains an environment
boundary with exit 127; no installation was attempted.

## Disposition

`PUBLIC_ISKVW_SKINS_GREEN; STATIC_INPUTS_PRESENT; DIFF_WHITESPACE_GREEN;
TSC_UNAVAILABLE_WITHOUT_INSTALL`

## Next action

Keep the portfolio write set isolated and prepare its focused review/commit
boundary. Before integration, obtain TypeScript verification through an
authorized existing environment or leave the exact exit-127 limitation in the
review evidence. Do not merge the worktree into `main` while its write set is
unreviewed.
