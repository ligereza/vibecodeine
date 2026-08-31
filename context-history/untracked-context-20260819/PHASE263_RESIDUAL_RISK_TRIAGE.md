# Phase 263 — residual risk-test triage

Date: 2026-08-15 America/Santiago  
Owner: LUNA principal  
Subagents: none

## Scope

Refine the Phase 252 keyword-based exclusion using AST imports and executable
call names. Promoted fixture groups from Phases 253–261 were removed from this
residual set before classification.

## Validation sequence

1. First analyzer attempt: exit `1`, internal `Counter.update` invocation
   error. It read source only and changed no file or runtime state.
2. Corrected analyzer: exit `0`; all remaining files parsed.

## Result

| Measure | Result |
|---|---:|
| Fixture groups already promoted | 39 files |
| Residual excluded files | 138 |
| Residual executable-risk files | 76 |
| Residual keyword/fixture candidates | 62 |
| AST parse failures | 0 |

The executable-risk marker is intentionally conservative: it detects imports
or calls such as `subprocess`, `urllib`, `requests`, `socket`, `run`, `get`,
`post`, `urlopen` or `request`. It is not proof that a test reaches the
external system; each candidate needs source inspection and an explicit
fixture/rollback boundary.

The 62 keyword/fixture candidates are the next economical review pool. The 76
executable-risk files remain gated, especially Airdrop, provider/network,
desktop/GPU, GitHub/Instagram/ADB/XIO, worker and service surfaces.

## Risk and rollback

No test from the residual set was executed. No source, database, service,
provider, network route or Git state changed. No rollback is needed.

## Next concrete action

Inspect the 62 keyword/fixture candidates in small groups, starting with
source-only or `tmp_path` tests. Do not execute the 76 executable-risk files as
a batch and do not promote XIO, n8n, worker, provider or live mutation tests.
