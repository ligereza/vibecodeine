# Phase 444 — portfolio proposal family owner gate

## Scope

This bounded slice is the comparative portfolio proposal family under
`iskvw/propuestas/`. It contains four model-produced candidate skins and an
index that embeds them for visual comparison. It is not the active ISKVW
editor, not the published portfolio skin, and not an RD production tool.

## Owner and classification

- Comparison index: `iskvw/propuestas/index.html`.
- Candidate artifacts:
  `mistral-large-2512/index.html`, `gpt-oss-120b/index.html`,
  `mistral-medium-2505/index.html` and
  `llama-4-maverick-17b-128e-instruct-fp8/index.html`.
- Evaluation context: `iskvw/PROMPT_ESTETICA.md`.
- Deploy projections: matching files under `/home/mak/flujo-deploy` and
  `/home/mak/vibecodeine`.
- Active portfolio owner remains `iskvw/editor.html` and its established skin;
  these proposals are a candidate/evidence family only.

## Foreground validation

```text
HTMLParser over the index and four candidates
exit 0 — 5 HTML files; all four candidate links resolve; no external HTML
navigation dependency

Node new Function syntax check over every inline script
exit 0 — 5 files, 4 scripts

Static assertions
exit 0 — four model candidates, five explicit `datos falsos 0/3` markers,
PROMPT_ESTETICA.md present

cmp against /home/mak/flujo-deploy and /home/mak/vibecodeine
exit 0 for all five files in both projections
```

## Disposition

The four proposals are intentionally distinct candidates, not duplicate
runtime tools. They should remain grouped under `iskvw/propuestas/` and must
not be fused into the active skin based on the displayed self-scores. The
index itself states that those scores are not evidence; the `datos falsos 0/3`
checks are the meaningful recorded gate. No proposal, deploy projection or
historical WIN copy was edited, moved or deleted.

Disposition: `PORTFOLIO_PROPOSAL_FAMILY_VALID; CANDIDATES_GROUPED; ACTIVE_SKIN_SEPARATED; PROJECTIONS_EXACT`.

Next action: return to the next unresolved RD HTML projection, verifying its
source/build owner and current physical state without promoting candidate
portfolio skins or overwriting generated bundles.
