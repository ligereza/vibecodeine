# Historical worktree review

Reviewed against `main`/`origin/main` on 2026-08-16. The worktree is
intentionally dirty; this document distinguishes publishable improvements
from preserved evidence. No bulk staging or deletion was performed.

## Tracked changes

| Path | Disposition | Reason |
|---|---|---|
| `.env.example` | publish | Corrects the obsolete local `GITHUB_TOKEN` expectation; GitHub CLI and the external Gmail bridge own their credentials separately. |
| `CAPACIDADES.md` | publish after correction | API/credential inventory is useful; corrected stale claim that 8890/8891 were active. Current count is 14 active/cabled surfaces, 15 including optional Crawl4AI. |
| `context/flujo_hub.html` | publish | Offline generated hub removes obsolete portal command wording. |
| `context/plano_demo.html` | publish | Same generated offline build correction; no source data deletion. |
| `context/svg_visualizer.html` | publish | Same generated offline build correction; no source data deletion. |

These five tracked files are the only current non-integrated tracked changes.
The HTML files share the same generated build fingerprint and are treated as a
single offline-build update, not three independent tools.

## Untracked historical evidence

- `context/PHASE*.md/.csv/.json` (748 files): historical phase evidence;
  preserve, do not publish as a new feature batch and do not delete during
  this review. The active/evidence boundary is recorded in
  `context/PHASE_REPORTS_INDEX.md`.
- `context/quarantine/` and `context/fixtures/`: protected rollback fixtures
  and test evidence; preserve until a separate retention decision.
- `data/rd.db.pre-*`: SQLite rollback snapshots; preserve while the active
  `data/rd.db` remains the canonical projection.
- `tools/probe_flujo_windows*.ps1`: useful read-only Windows migration probes;
  keep as historical tooling, not Linux runtime requirements.
- `tools/render_archaeology_deliverables.py`: bounded offline archaeology
  utility; keep unmerged until a concrete consumer is requested.

## Decision

Publish only the five tracked improvements above. Do not stage the historical
phase corpus, rollback databases, quarantine, fixtures or probe utilities in
the same commit. No deletion is justified by this review.
