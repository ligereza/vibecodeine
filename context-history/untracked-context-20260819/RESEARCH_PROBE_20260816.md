# Research and proposal probe

Read-only/temporary validation performed 2026-08-16.

## Source capture

- URL: `https://www.fondosdecultura.cl/`
- Requested backend: explicit `urllib` fallback
- Result: HTTP 200, captured
- Extracted text: 6,263 characters
- Extracted links: 53
- Firecrawl/Tavily/Crawl4AI: not called

## Proposal generation

- `tools/gen_propuesta_directiva.py` read the canonical `data/rd.db`.
- Temporary output: 44,112-byte HTML proposal.
- Source counts reported by the generator: 3 packs, 20 producers, 23
  reagents and 8 supplements.
- `tools/gen_propuestas_rd.py` read the existing Curatoria candidate JSONL and
  wrote only to a temporary directory.
- It produced 2 venue drafts; no producer drafts and no writes to `data/`,
  `knowledge/`, `docs/` or the opportunity ledger.

## Findings for future improvement

- The candidate input contains 970 rows; 882 are rejected by category rules,
  which is expected but should remain visible in any future UI summary.
- Nine producer names and ten venue names have only one evidence item. They
  remain short-evidence candidates and must not be promoted automatically.
- Two venue drafts were produced under the configured evidence threshold;
  they require human review before entering canonical venue data.

This probe proves the offline fallback and proposal path work with temporary
outputs. It does not prove current eligibility for a specific live grant or
authorize external publication.
