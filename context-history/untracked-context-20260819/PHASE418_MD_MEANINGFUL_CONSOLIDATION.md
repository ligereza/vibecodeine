# Phase 418 - meaningful Markdown consolidation

Date: 2026-08-15
Agent: LUNA principal
Scope: continue Markdown consolidation before any HTML work. Preserve every
source file and create navigation summaries only for coherent families with a
real owner, consumer or durable idea.

## Actions completed

1. Re-read the current handoff and the agent contract before acting.
2. Confirmed the canonical Markdown inventory is still larger than the useful
   context masters; HTML is deferred. The last physical scan found 427
   context Markdown files, 33 culture Markdown files and 24 RD/plano Markdown
   files under the canonical tree. It also found 59 canonical HTML files and
   814 HTML files across reachable MAK surfaces.
3. Read and classified the meaningful families:
   - direction memory and service hypotheses;
   - MAPA/CAPACIDADES/PLAN architecture and backlog;
   - RD editorial contract;
   - RD data, venue, plano and visual guardrails;
   - Fondart/opportunity research and proposal templates;
   - raw recovered session evidence.
4. Extended `context/MD_CONTEXT_MASTER.md` with the operational family table.
5. Extended `projects/cultura/MD_IDEAS_MASTER.md` with Curatoria/archive/
   postulaciones, RD/VJ/venue/proposal and editorial-memory sections.

## Consolidation decisions

- `MEMORIA_DIRECCION.md` is a source of human direction, not a runtime plan.
- Fondart extracts and calendars are research evidence. Promotion requires a
  current primary source, exact deadline, eligibility and next action.
- `postulacion_base.md` is a reusable template with placeholders, not proof of
  a complete application.
- RD editorial material is human-facing Spanish UTF-8 and remains separate
  from machine-facing runtime configuration.
- Venue, RD catalog, VJ geometry and portfolio share crosswalk/provenance but
  are not collapsed into one database.
- Raw transcripts, recovered documents, WIN and vendor/plugin Markdown remain
  evidence or inventory; originals were not moved, overwritten or deleted.

## Verification

- Read-only canonical Markdown scan: exit 0.
- Read-only headings and family inspection: exit 0.
- No database, source code, service, external provider or Git state changed.
- No permanent process was started.

## Files modified

- `context/MD_CONTEXT_MASTER.md`
- `projects/cultura/MD_IDEAS_MASTER.md`
- `context/PHASE418_MD_MEANINGFUL_CONSOLIDATION.md`
- `context/LAST_HANDOFF.md`

## Risks

- Recovered Fondart material may be stale or incomplete and must not be used
  as legal or submission authority.
- Similar Markdown remains intentionally separate when provenance or wording
  differs; exact duplicate families are represented by pointers, not deletion.
- HTML is not yet the next safe target while meaningful Markdown families
  remain unindexed.

## Next concrete action

Continue the Markdown ranking with the remaining bridge/line-editorial and
Curatoria families. After useful Markdown is indexed, inventory HTML by owner,
consumer and exact duplicate hash, starting at `/home/mak/*` and preserving
historical and generated copies.
