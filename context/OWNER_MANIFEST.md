# MAK owner manifest

This is a current navigation contract, not a historical inventory. It names
the canonical implementation and the intentional projections that consume
it. WIN remains historical evidence and is not an active owner.

| Slice | Canonical owner | Intentional projection / consumer | Decision |
|---|---|---|---|
| MAK hub and area registry | `cultura/mak_plataforma/hub.py` | `/home/mak/plataforma/hub.py` | compatibility projection; do not fork logic |
| RD panel and privacy allowlist | `src/flujo/rd/panel.py` | MAK hub RD routes and offline HTML consumers | shared source; do not duplicate allowlist |
| RD catalog projection | `src/flujo/rd/database.py` + `data/rd.db` | read-only hub summaries | `rd_datos.db` is separate empty field state |
| RD/Cultura entity join | `src/flujo/rd/entity_crosswalk.py` + candidate JSON | `/api/rd/crosswalk`, `/api/rd/cultura-relations` | review-only until explicit provenance |
| Research routing | `cultura/mak_plataforma/research_router.py` | MAK hub research/capability surfaces | canonical router; optional providers stay gated |
| Portfolio project contract | `tools/portfolio/catalog_contract.py` + `tools/portfolio/proyectos.json` | ISKVW editor/publication surfaces | project catalogue is distinct from visual works |
| Portfolio visual works | `iskvw/datos/obras.json` | `iskvw/editor.html`, generated site | visual-work source; not replaced by project catalogue |
| Venue records | `data/venues/*.json` + `tools/venue.py` | SCD geometry and venue web views | JSON is source; renders are regenerable |
| SCD geometry primitive | `projects/plano/referencia_plano_teatro.py` | `tools/venue_geometria_scd.py`, venue skin | derivative is retained, not a second authority |
| Historical FLUJO app | `src/flujo/web/hub.py` | offline/portable FLUJO runtime | separate legacy/offline consumer, not MAK hub duplicate |

Rules:

- A projection may adapt presentation or runtime paths, but must not silently
  become a second source of truth.
- A relation with only a raw venue name remains `review_candidate`.
- Artist, producer, venue, event and project roles stay distinct.
- No file in this manifest authorizes deletion; cleanup requires a separate
  evidence-backed gate.
