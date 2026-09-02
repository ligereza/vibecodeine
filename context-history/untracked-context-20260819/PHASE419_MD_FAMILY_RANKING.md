# Phase 419 - Markdown family ranking and bridge classification

Date: 2026-08-15
Agent: LUNA principal
Scope: continue meaningful Markdown consolidation. HTML remains deferred until
the remaining useful Markdown families have an owner and disposition.

## Actions completed

1. Ranked the remaining canonical Markdown surface by byte size after
   excluding the handoff, phase reports, masters, vendor/plugin trees and
   generated dependency trees.
2. Compared the editorial revisions. `linea_editorial/v3.md`, `v4.md` and
   `v4.1.md` have different SHA-256 values, so they remain a version lineage;
   `v4.1.md` is the current RD-facing contract.
3. Classified the `puente/` family as theory/manifesto material with no
   runtime consumer.
4. Classified the recovered Firecrawl/Crawl4AI and quantified-self reports as
   Curatoria research evidence, not provider authorization or runtime
   dependency.
5. Added both dispositions to the context and idea masters.

## Verification

- Read-only Markdown ranking and SHA-256 comparison: exit 0.
- Editorial `diff -q` comparisons: exit 1 for each pair, confirming the files
  are non-identical revisions rather than exact duplicates; this is an
  expected comparison result, not a failed integration test.
- No original Markdown, database, source code, service, provider or Git state
  changed.

## Files modified

- `context/MD_CONTEXT_MASTER.md`
- `projects/cultura/MD_IDEAS_MASTER.md`
- `context/PHASE419_MD_FAMILY_RANKING.md`
- `context/LAST_HANDOFF.md`

## Risks and boundaries

- Theory documents must not be mistaken for executable architecture.
- Scraped research may be stale or incomplete; primary sources and user
  authorization are required before external execution.
- The three editorial versions must not be silently merged because their
  differences may encode intentional RD design decisions.
- HTML remains unprocessed; its generated, historical and active owners still
  need classification after Markdown consolidation.

## Next concrete action

Continue the remaining meaningful Markdown ranking, especially recovered
Curatoria research and RD reports. Once that pass yields no new coherent
family, start the HTML inventory from `/home/mak/*` by exact hash, owner,
consumer and generated/history status.
