# Phase 425 - HTML vertical owner consolidation

Date: 2026-08-15
Agent: LUNA principal
Scope: consolidate the static HTML owner map for Hub, RD, Plano, Venue and
Portfolio while the Vite build environment remains gated.

## Actions completed

1. Confirmed the hub family: `web/src` is the source, `web/dist/index.html`
   is the generated build candidate, `copy-context.mjs` produces the three
   pathname-selected context aliases, and `src/flujo/web/hub.py` serves them.
2. Confirmed RD and Plano are intentionally separate standalone bundles:
   `mainRd.tsx` owns `dist-rd/rd.html`; `mainPlano.tsx` owns
   `dist-plano/plano.html`; each has its own Vite config and copy script.
3. Confirmed the standalone entries exclude unrelated hub panels by source
   imports. They must not be merged into the hub bundle by filename similarity.
4. Recorded Venue and Portfolio as separate consumers: Venue is a catalogue /
   cross-domain projection; Portfolio is the public skin/editor and has its
   own publication gate.
5. Added the HTML owner map to `context/MD_CONTEXT_MASTER.md`.

## Verification

- `node --check` on `copy-context.mjs`, `copy-rd-share.mjs` and
  `copy-plano-share.mjs`: exit 0.
- `npm run typecheck` already passed in Phase 424: exit 0.
- Static inspection of four HTML entry/source pairs and their Vite configs:
  exit 0.
- No HTML, source, database, service, external provider or Git state changed.

## Consolidation decision

Consolidate logically by source/consumer/projection, not by deleting duplicate
HTML. The hub aliases remain one generated family; RD and Plano remain two
purpose-built bundles; Venue and Portfolio remain separate domains. Historical,
deployment and WIN copies remain evidence until a proven projection owner is
retired.

## Next concrete action

Keep the HTML write gate closed. The remaining executable work is read-only
parity mapping for Venue/Portfolio data and generated copies, or a separately
authorized Node/Vite environment repair. Do not install packages, change
permissions, overwrite context aliases, delete evidence or start services.
