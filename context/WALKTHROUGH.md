# WALKTHROUGH -- next session quick-start

## You just arrived. Read this first (3 min).

Repo: flujo (vibecodeine), version 0.52.0 | date 2026-07-17T22:30 | assistant Cauce (Claude Code)

**Status:** main stable, v0.52.0 live, suite green (394 tests + 1 skip), all systems passing CI.

### The 4-step entry

1. **Read CLAUDE.md** (5 min) — rules, mission, team structure, when to escalate cost
2. **Read context/LAST_HANDOFF.md** (5 min) — what's done, what's next, blockers
3. **Identify your task** — if unclear, ask the user before diving
4. **Check if this session already touched it** — grep git log, don't re-derive

### Right now

- **Main branch:** 2 commits just merged (156e8b4 cleanup PR#48 stale refs + cultura/ leftovers, be3153e handoff update)
- **Open PRs:** #49 (MAPA_GENERATIVO, DRAFT, user decision pending)
- **Worktree:** mak-research-cultural (PR #48 merged, worktree preserved for ongoing MAK work)
- **CI:** all green, branch protection active on main
- **Blockers:** MAK SSH auth not yet shared by user; portfolio-auto audit complete; offline stale-file scan complete

### Key files (DON'T edit without reading first)

- `CLAUDE.md` — operating layer, cost rules, team routing
- `context/LAST_HANDOFF.md` — state + next + blockers
- `src/flujo/` — core package (Python, CLI)
- `tests/` — 394 green tests
- `cultura/` — now clean (9 leftovers moved out today)
- `docs/` — DIRECTOR_PLAN.md archived (stale v0.49.0)

### Hazard zones (don't touch without escalation)

- `puente/` — theoretical only, see CLAUDE.md; motor-omega protocol for new pieces
- `README.md` — artist's final work, do not add
- `.noisette` files — never guess schema, use real fixtures (tests/fixtures/)
- PRs #48/#49 — waiting user review, don't merge without signal

### Quick tasks ready to go

- MAK Linux audit (once SSH auth provided)
- Portfolio-auto live status check (already audited, outputs green)
- Next ola backlog if MANIFIESTO cultural work unblocks
- Test coverage hunts (no user keys needed, autonomous)

### If you're stuck

1. Check `context/PLAN_SIGUIENTE_AGENTE.md` (prioritized pending with notes)
2. Use `py tools/contexto_repo.py task "<keywords>"` to find relevant files (zero tokens)
3. Ask the user first rather than guessing on cost/scope/blockers decisions
4. Escalate to Opus/Fable if: destructive ops, credentials, >1 option, off-task findings

### Session end (mandatory)

Update these before you leave:
```
context/LAST_HANDOFF.md     (new section, what you did + next)
context/SESSION_STATE.json  (version, date, done[], doing[], next[], blockers[])
py -m compileall src/flujo  (must pass)
py -m pytest tests/ -q      (must pass)
py -m flujo verify          (must pass)
```

Commit + push. Brief and terse. No half-work.

---

**Last updated:** 2026-07-17T22:30 (Cauce, autonomous cleanup session)
