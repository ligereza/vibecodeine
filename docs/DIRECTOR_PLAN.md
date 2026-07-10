# DIRECTOR PLAN - unified backlog, architecture, security, roadmap
Date: 2026-07-10 | v0.49.0 | Author: Claude (director) | Phase 0 inventory: 3 parallel sub-agents (src/flujo, tools/projects, security audit). Nothing below is speculation; all states verified against the tree.

## 1. Unified backlog (inventory-first; nothing rebuilt)

| Item | Column | Status | What exists | Next move |
|---|---|---|---|---|
| Tapiz | creative-pipeline | STARTED | `projects/tapiz/vibecode/` (render/life/power, colorama-style API, entry `example_agent.py`) + standalone `vibecode_void.py`/`vibecode_spaces.py` + `feedback.md` (pivot: color only the voids) + `docs/TAPIZ.md`. Hub already serves `projects/tapiz/` (`web/hub.py:279,422`) | Reconcile the 2 implementations per `feedback.md`; fix its listed bugs; do NOT rewrite |
| tilde | creative-pipeline | TO-START | Zero footprint (repo-wide search: 0 hits) | Greenfield; reuse `src/flujo/render/` + SVG toolchain (`tools/svg/`) as output layer |
| psicosis | creative-pipeline | TO-START | Zero footprint. Nearest code (`src/flujo/privacy/`) is unrelated | Greenfield; text-analysis lens, gated as art/introspection only (no profiling real people) |
| Precursor | creative-pipeline | TO-START | Zero footprint (hits are supplement copy "precursor del glutation", unrelated) | Greenfield; DESCRIPTIVE layer only (see section 4) |
| Idea intake (voice/text messenger) | intake | STARTED | Mature: `src/flujo/intake/` (email/JSON parsers, tested), `tools/vibo_voz/` (voice, working), `desktop/` (floating Gemini->Claude router, working), `/go` skill reads `tools/vibo_voz/proyectos/<name>/idea.md` (folder currently empty) | Extend, do not build new. Gap: captured ideas -> `proyectos/` folder pipeline unused |
| Git automation (commit msgs, PR desc, diff review) | automation | TO-START (code) / STARTED (prompts) | NO `commit_ai.py` exists anywhere. Only prompt skills (`.claude/skills/caveman-commit`, `caveman-review`) + fixed-string `airdrop.py:218 run_auto_checkpoint()` | Small script wrapping git diff (~6000 char cap) -> cheap model; reuse `pedir_codigo.py` provider/scrub pattern, hook into `airdrop.py` checkpoint |
| Blender/3D render agent | creative-pipeline | STARTED (thin) | `src/flujo/eventos/blender_render.py` (headless bpy, wired `flujo eventos flyer-auto --render-blender`), `templates/blender_setup.py` (copy-paste stub), no .blend committed, end-to-end untested on render machine | Blocked on real-machine test (pending in handoff). Verify-with-numbers harness (bounds, mean brightness) is new work |
| Realism dossier (grounding library) | creative-pipeline | TO-START | `src/flujo/knowledge/` store exists (productoras/venues/logos) - right home for it | New `knowledge/` category: descriptive dossiers feeding tilde/Precursor/Tapiz |
| Cost routing (cost-guardian) | governance | STARTED | Encoded in `CLAUDE.md` (team table, runway rule), `pedir_a_gemini.py` (cheap read), `pedir_codigo.py` (cheap write, multi-provider), desktop router (EJECUTAR_DIRECTO/ENRUTAR_CLAUDE), API-vs-quota split via `claude.yml` Actions | Policy exists; enforcement is manual. Do not build an agent for it yet (see roadmap) |
| Security auditing | governance | STARTED (this doc) | Full audit done 2026-07-10, section 3. 3 fixes already applied on this branch | Re-audit only when integrations change |
| Docs/skills (docs-agent) | governance | STARTED | 15+ skills in `.claude/skills/`, handoff system (`context/LAST_HANDOFF.md` + `SESSION_STATE.json`), `contexto_repo.py` 0-token map | Working; over-building here is the repo's known failure mode (see handoff `critique_acida`) |
| Resolume/.noisette | creative-pipeline | STARTED-BLOCKED | `src/flujo/resolume/automator.py`; XML/CSV stable, .noisette experimental, rewritten 4x guessing | HARD STOP: needs real .noisette fixture from user's Chataigne 1.10.3, or delete the experimental fn |

### Duplication / dependency findings
- Tapiz has TWO parallel implementations (package `vibecode/` vs standalone scripts) - internal duplication to reconcile, not extend separately.
- Intake exists THREE times (flujo intake/, vibo_voz voice, desktop app). They are complementary layers (email/voice/overlay) but all should land ideas in ONE place: `tools/vibo_voz/proyectos/<name>/` (the `/go` skill contract). Today none of the three writes there.
- Git automation must reuse `pedir_codigo.py` scrub+provider pattern; do not create a second secret-scrubbing implementation (regex drift already happened once - fixed on this branch).
- realism-dossier feeds tilde + Precursor + Tapiz - build it before or alongside the first consumer, inside `src/flujo/knowledge/`.
- 7 tools/ SPECs are IDEA-ONLY (asistente_pedido, canva_data, privacidad_datos, resolume_chataigne_automator, slowmo_blender_ae, agente1/2 prompts). Not backlog items until scoped; per handoff, ask user before coding.

## 2. Current architecture (sub-agents and active flows)

```
USER (voice/text, Spanish, iPhone or desktop)
  |-- desktop/ overlay (Tkinter): Idea|Explicar|Chat -> Gemini router
  |       EJECUTAR_DIRECTO (Gemini solves) / ENRUTAR_CLAUDE (compressed prompt)
  |-- tools/vibo_voz/vibo.py (voice, Gemini Live) -> claude_bridge.py (headless claude -p, opt-in, capped)
  |-- GitHub issue "@claude ..." -> .github/workflows/claude.yml (Actions = API, not weekly quota)
        |
        v
CLAUDE (director): architecture, critical code, this doc
  |-- cheap READ:  tools/vibo_voz/pedir_a_gemini.py (scrubbed, capped)
  |-- cheap WRITE: tools/vibo_voz/pedir_codigo.py (Gemini/NIM/GitHub Models, scope-locked, .bak)
  |-- bulk code:   Qwen web / LMArena (manual) -> PR -> GATE
        |
        v
GATE: ci.yml (compileall+pytest+verify+web build) + free reviewer (Gemini/Arena) ; Claude only on escalation
        |
        v
PRODUCT: src/flujo CLI (intake, jobs, plano, eventos, resolume, render, knowledge, web hub)
```

Sub-agent mapping (requested id -> existing asset; NONE need to be built from scratch):
- intake-agent -> desktop/ + vibo_voz + src/flujo/intake (gap: write-through to proyectos/)
- automation-agent -> TO BUILD small (`tools/vibo_voz/commit_ai.py`-style, reusing pedir_codigo.py internals)
- render-agent -> blender_render.py (gap: numeric verification harness)
- realism-dossier -> TO BUILD inside src/flujo/knowledge/
- cost-guardian -> CLAUDE.md policy + desktop router (adequate; no new agent)
- security-auditor -> periodic audit task (first run done, below)
- docs-agent -> .claude/skills + handoff system (adequate)

## 3. Security posture (audit 2026-07-10)

Critical: NONE. No real credentials in tracked files (entropy-regex sweep clean; all hits are placeholders/scrubber sources/prose).

Fixed on this branch:
- M2: `desktop/gui.py` config.json path was CWD-relative; if launched from repo root the plaintext API key file escaped `desktop/.gitignore`. Now anchored to script dir.
- M3: `ci.yml`, `validar-piezas.yml`, `render_piezas_vectoriales.yml` had no `permissions:` block while running PR-supplied code. Now `contents: read`.
- L4: `pedir_a_gemini.py` scrub regex lacked `nvapi-`/`sk-or-v1-` patterns that `pedir_codigo.py` had. Aligned.

Open gaps (accepted/deferred):
- M1: `claude.yml` grants contents/PR/issues write on comment events. Mitigated (author_association gate, no bot, no ${{ }} body interpolation, prompt hardening). Residual: compromised collaborator. Accept.
- L1: `anthropics/claude-code-action@v1` tag-pinned, not SHA-pinned. Low; consider SHA pin.
- L2: claude_bridge Windows `cmd /c` metacharacter nuance; opt-in off by default, input is the owner. Accept.
- L3: `desktop/local_tools.py` denylist misses `credentials.json`/`token.json`/`.aider.conf.yml` (readable by Gemini if present locally). Small fix, next touch of desktop/.
- Branch protection on main: NOT confirmable from repo; user must verify in GitHub UI (already in handoff next-steps).

Done right (keep): content-based secret scrubbing before any external send; whole-repo upload refusal + size caps; keys only in env/gitignored files, masked in logs; local_tools PROJECT_ROOT confinement verified; scope-locked LLM writes with .bak; claude.yml avoids pull_request_target and body interpolation.

## 4. Hard limits (director enforces; binding for all sub-agents)

Boundary is DESCRIPTIVE vs GENERATIVE. Allowed as art grounding: real molecular structure/geometry, mechanism of action and pharmacology, species morphology, history/law/culture/iconography, informational harm-reduction. Prohibited regardless of framing ("for art", "simulation", "no steps"): synthesis routes/reactions, precursor-to-product mapping, yield/purity optimization, novel analog design, methods to modify/cultivate organisms to produce controlled substances. On a prohibited ask: refuse, offer the descriptive equivalent, never delegate it. psicosis: introspective/literary lens only, never profiling or surveilling real people.

## 5. Roadmap - next 3 steps

1. **Prove the pipe with Tapiz reconciliation** (effort: 1 session, ~1 PR; target 2026-07-13)
   Why: handoff's own rule - "no more infra until ONE thing has gone through the new tube"; Tapiz is the only STARTED creative idea and the cheapest real deliverable.
   Do: open issue "@claude reconcile projects/tapiz per feedback.md" -> Actions -> PR -> CI -> merge.
   Accept: one `vibecode` implementation (package form), `feedback.md` bugs closed (`__name__` mangling, `import re` placement), `python projects/tapiz/example_agent.py` runs clean, standalone scripts either deleted or thin wrappers; issue->PR->merge happened via Actions, not chat quota.

2. **automation-agent: minimal commit/PR/review script** (effort: half session; target 2026-07-16)
   Why: highest-frequency mechanical task; nothing exists as code; unblocks cheap-model routing for every future PR.
   Do: `tools/vibo_voz/commit_ai.py` - git diff capped ~6000 chars -> cheap model (reuse `pedir_codigo.py` `_scrub`/provider fallback) -> commit msg + PR description + 5-line review. Wire as opt-in into `airdrop.py run_auto_checkpoint()`.
   Accept: on a real diff produces Conventional-Commits msg; never sends secrets (scrub test in tests/); runs on Gemini free tier; `py -m pytest tests/ -q` green.

3. **realism-dossier v0 inside knowledge/ + first consumer (tilde spec)** (effort: 1 session; target 2026-07-20)
   Why: unblocks all three TO-START creative tracks with one shared, hard-limits-compliant substrate; knowledge/ store already exists.
   Do: add `dossier` category to `src/flujo/knowledge/store` (schema: subject, real-structure/mechanism/morphology facts, sources, iconography notes); seed 2 dossiers (one linguistic for tilde: n/diacritics/inverted punctuation semantics+history; one botanical/molecular DESCRIPTIVE for Precursor); write `projects/tilde/SPEC.md` consuming the linguistic dossier.
   Accept: `flujo knowledge list` shows dossiers; schema validated in tests; zero prohibited content (checklist from section 4 in the PR description); tilde SPEC names its first render target (SVG via existing toolchain).

NOT doing (explicit): no new orchestration framework, no 7 new agent definition files, no airdrop extensions - handoff's critique_acida stands: scaffolding already outweighs product. Every step above ships product or hardens the gate.

USER DECISION 2026-07-10 (overrides restructure_optima step 1 "matar el airdrop"): the airdrop workflow STAYS AS IS. It is the delivery channel for web agents with no GitHub access (Qwen web, LMArena). Do not remove, do not extend.
