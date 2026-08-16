# MAK integration objective audit

Audited against the current worktree on 2026-08-16. `Proven` means a local
file and foreground check support the claim. `User gate` means the local
implementation is prepared but an external action was intentionally not run.

| Requirement | Status | Evidence |
|---|---|---|
| One MAK hub on port 8900 | Proven locally | `cultura/mak_plataforma/hub.py`; Phase 529 HTTP checks on `127.0.0.1:8900` |
| RD, Cultura/Research, ISKVW/Portfolio separated | Proven locally | `src/flujo/departments.py`; `/api/departments`; all three ready |
| Per-area requirements, env example, agents and handoff | Proven locally | `contracts/departments/{rd,cultura,iskvw}/`; `context/handoffs/` |
| Interface error exporter | Proven locally | `src/flujo/diagnostics.py`; diagnostics GET/POST redaction tests |
| RD catalog consolidated without merging empty field DB | Proven locally | `data/rd.db` 7,585 rows; `data/rd_datos.db` 0 rows; `/api/rd/summary` |
| RD/Curatoria venue, producer, artist, event and project links | Proven as review graph | `/api/rd/crosswalk`; `/api/rd/cultura-relations`; ambiguous links stay review candidates |
| Research scraping, opportunities and proposals | Offline contract proven | `/api/cultura/capabilities`; `/api/cultura/opportunity-gate`; live providers remain optional |
| Offline/API dependency separation | Proven locally | `context/DEPENDENCY_SURFACE.md`; area contracts inherit root manifest |
| Canonical implementation per functional tool | Proven/documented | `context/OWNER_MANIFEST.md`; intentional projections retained |
| WIN historical boundary | Proven by architecture contract | `agents.md`, owner manifest and read-only policies; no active consumer promotes WIN |
| EVENT workflow published | Proven | `main` commits `e90bd8f`; pushed to `origin/main` |
| Permanent 8900 service enabled | Proven | `mak-hub.service` enabled/active; listener verified on `127.0.0.1:8900` |
| Real EVENT issue end-to-end | Waiting for natural input | User requested waiting for the next Gmail-created issue; no artificial replay |

No requirement is silently marked complete based only on intent. The remaining
observation is a naturally arriving external event, not missing architecture.
