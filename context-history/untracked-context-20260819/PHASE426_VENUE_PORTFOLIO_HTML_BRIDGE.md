# Phase 426 - Venue/Portfolio HTML bridge consolidation

Date: 2026-08-15
Agent: LUNA principal
Scope: map the static Venue and Portfolio HTML consumers to their real data
owners and cross-domain bridge.

## Findings

1. `web/venues/index.html` contains two embedded example records. Its own
   labels state that values are `aportado`/not verified. It does not fetch
   `data/venues/*.json`; classify it as an open-base demo, not the canonical
   venue database.
2. `iskvw/piel/venue/index.html` is the actual SCD venue viewer. Its default
   path is `data/venues/scd-plaza-egana.json`, and `?venue=<id>` resolves a
   registry entry. It renders confidence-aware geometry and a declared edge
   budget.
3. `iskvw/piel/campo/index.html` reads `iskvw/datos/archivo.json` with a
   fallback to `campo.json`, reads `tablero.json`, and exposes the venue link
   only when `mejoras.venue3d` is true. Current `tablero.json` has that flag
   set to true.
4. `tools/portfolio/proyectos.json` contains 10 curated public projects and
   identifies `plano-rider-rd` and the cultural lines as public catalogue
   entries. The GitHub Pages workflow publishes the `iskvw/` projection,
   while Hub portfolio APIs/editing remain a separate local consumer.

## Verification

- Read-only JSON loading for venue schema, SCD venue, portfolio catalogue,
  `tablero.json`, `archivo.json` and `curaduria.json`: exit 0.
- Static HTML/data marker scan: exit 0.
- No HTML, JSON, database, source, service, provider or Git state changed.

## Consolidation decision

The bridge is logical and explicit:

```text
data/venues/*.json
        -> iskvw/piel/venue/index.html
        -> campo link when tablero.mejoras.venue3d=true
        -> public portfolio projection

web/venues/index.html -> open example catalogue only
tools/portfolio/proyectos.json -> curated public project catalogue
```

Do not merge the example catalogue into the RD/venue database by name, and do
not publish a venue as measured when its confidence is only `aportado`.

## Next concrete action

Keep HTML and data write gates closed. The next safe slice is a read-only
crosswalk between `data/venues/*.json`, `data/rd.db` venue IDs and the
portfolio venue projection; the Node/Vite build repair remains a separate
environment task.
