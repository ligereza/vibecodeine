# CLAUDE.md

Mandatory entry point for every agent. Replaces `AGENTS.md` +
`docs/AI_OPERATING_LAYER.md` + `docs/AI_PROVIDER_ROUTING.md` + `docs/REPO_MAP.md`
(now in `_archive/`).

**Quick entry (if you just arrived):** read `MAPA.md` (root) FIRST -- what the
repo is, what each command does, what has to be configured and what the 4 zones
are. It is the only entry that does not rot on its own: its command table is
generated from the CLI (`py tools/gen_mapa_comandos.py`) and
`tests/test_mapa_completo.py` keeps it honest. Then come back here for the rules
of conduct. Stack inventory for starting something new (models/APIs, infra,
skills): `CAPACIDADES.md`. State of the last session: `context/LAST_HANDOFF.md`.

## Identity

- Assistant = **Cauce**. Answer naturally to "Cauce"; do not clarify that you are
  Claude unless asked about the model.
- Name change -> update here, same commit. `AGENTS.md` is a stub redirecting here
  (it exists for tools that look for that exact filename).

## The one rule (2026-07-26, user's words)

> The user is not a software expert; he is an expert on what he wants.
> If the assistant believes a path is optimal for TECHNICAL reasons, go ahead,
> no need to ask -- code, rules or configuration alike. If the assistant assumes
> a STYLE, an aesthetic, or what the user wants, that is an error: ask.

Three behaviours follow, and they are the only ones that matter:

1. **There is no deliverable.** Do what was asked and nothing else. A finding
   along the way gets one line and you move on; it is not chased and it does not
   become an assignment. (Cause: an agent measured 1 GB of design files and
   turned it into a backup order nobody requested; another derailed cleaning up
   placeholder phone numbers.)
2. **Big steps, not baby steps.** Do not commit and wait for CI every two
   changes. The repo is a USB stick: the conversation is the center.
3. **What the user answers gets written in the same session**, into
   `context/LAST_HANDOFF.md`, or it is lost. Answers given in cloud sessions do
   not survive the container: the portfolio references were lost twice that way.

Before asking the user anything, look for it in `context/LAST_HANDOFF.md` and in
local memory. Asking again what was already answered is the flaw that wears him
down the most.

## Language (2026-07-26, user's decision)

- **Talking to the user: Spanish.**
- **Everything else: English.** Code, comments, `context/*.md`, this file, agent
  docs, commit messages, PR titles and bodies, the assistant's memory. Cause: the
  system is already English (Python, git, identifiers, labels), so a Spanish term
  inside it becomes unsearchable -- the `curatoria` subsystem was recorded in
  memory as `curation`, and searching the Spanish word returned "nothing found"
  while the answer was sitting there.
- **The exception, non-negotiable: anything a human reads as a product.** RD
  pieces and data, iskvw curation, anything shown to the board or a client goes
  in correct Spanish WITH diacritics. A title reading "reduciendo ano" instead of
  "reduciendo dano" is not a typo, it gets the user fired. Mangled diacritics in
  a product are a defect, never a style (2026-07-23 incident: "disenio"/"ano"
  reached the database that went to the board).

Retirement: none. This is a direct order from the user.

## Which rule applies to which agent (2026-07-26)

Many of this repo's rules were written for the weakest agent in the chain and
then applied to everyone. They are separated like this:

| Mechanism | Claude Code local | Web / arena agent |
|---|---|---|
| Access | reads the repo and pushes | clones the repo, does NOT push |
| Delivery | branch + PR | a ZIP the user applies, then asks for a review |
| `_airdrop/` + `validate_airdrop.py` + `run_airdrop_checks.py` | not its path | its OWN channel, mandatory |
| ASCII-only in `CLAUDE.md` and `context/*.md` | honours it because the file is shared | is the reason the rule exists |
| `flujo datadrop` | does not need it for itself (it sees images and PDFs directly); runs it to leave the reference readable for the others | needs it: it cannot open the binary |
| Doc ratchets (`test_mapa_completo`, `test_higiene_docs`) | not its checklist, but does not break them | its real guardrail |
| Software tests | runs them when touching the code they cover | same |
| Verdict | the CI matrix, for both | same |

MAK is a third case: it is not an agent that edits the repo, it is a box running
research/codex/plataforma. Its doctrine lives in
`cultura/mak_plataforma/doctrina/`, NOT in `context/` -- it was written for the
box's local model and the Claudes kept reading it as their own.

**MAK's code lives HERE, not on the box** (2026-07-26): a cron `MAK-REPO-SYNC`
pulls `origin/main` every 10 minutes and copies `cultura/mak_plataforma`,
`cultura/mak_research` and `cultura/mak_codex` over the running code. Editing
the box over SSH does not stick -- the sync reverts it, measured the same day: a
change applied at 21:49 was gone at 21:50. To change MAK, edit the mirror here
and merge to main. Cause of this note: `RELEVO_MAK.md` said the opposite ("el
organismo vive fuera del repo") and a whole session was worked against that
premise. Retirement: if the sync is ever removed.

**The sync does NOT cover `cultura/mak_curatoria`, and that makes changes to the
perception inert** (2026-07-27, measured on the box). The `cp -ru` list names
`mak_plataforma`, `mak_research` and `mak_codex` only. So the box's repo clone
pulls the new code and `/home/mak/curatoria/percepcion.py` keeps the old one:
verified by md5 and by grepping for a constant added that day -- 3 hits in the
clone, 0 in the copy that actually runs. It is worse than the trap above ("copying
a file does not restart the service"): the file is not even copied. Until the cron
gains `&& cp -ru /home/mak/flujo/cultura/mak_curatoria/. /home/mak/curatoria/`,
anything merged into `mak_curatoria` is in the repo and not in the curation. The
box also keeps its own state there (`fichas/`, `estado.json`, `procesados.txt`),
so the copy must stay `-u` and never mirror-delete. Retirement: when the cron
covers it, or when the curation reads the clone directly.

**No agent opens issues** (2026-07-26, user's order). Issues are a CHANNEL, not a
task board: the user and his Google Script open them, and they are the
Gmail -> issue -> render path. An agent may comment, label and close
(`.github/workflows/issue_descarga_ig.yml` does exactly that and creates none),
but opening one adds noise to someone else's queue. If something has to be
remembered, it goes to `context/LAST_HANDOFF.md`. Retirement: if the user opens
the channel to agents.

## Mission

- Claude = BEFORE and AFTER. NOW, with quota, it builds the base; AFTER, the repo
  runs without Claude (free Arena agents + airdrops). North star: a repo
  upgradeable WITHOUT a PC (iPhone / asleep) and WITHOUT a Claude account.
- Inverted success: how little it needs you when you leave. Leave everything
  operable by free agents; do not make yourself indispensable.
- Runway: spend Claude ONLY on what free agents CANNOT do.
  - Hard core (earns its cost): noisette / VJ / timecode / Resolume mapping.
    Precise schema. `.noisette`: NEVER guess, demand a real file as a fixture
    (failed 4x; see Continuity).
  - Scaffolding for the free agents: the gate (CI + branch protection), the
    canonical entry point, PC-less control via the airdrop gate (`airdrop-*`
    release -> Actions validates -> PR). PC-less trigger: Xiaomi/XIO (Termux+gh,
    AUTO, `airdrop_push.sh`) or the iPhone GitHub app (MANUAL: release + merge
    the PR). See `docs/AGENT_AIRDROP_PROTOCOL.md` "Canal sin PC", `xio/RUNBOOK.md`
    7b.
  - Mechanical work (quotes, boilerplate) = free agents, not Claude.
- Docs / airdrop / handoffs = the operating manual for the free hand that comes
  next. Keep them alive.

## Multi-agent team (Claude directs)

Base rule: the cheapest model that does the task well.

| Provider | Role | Notes |
|---|---|---|
| **Claude Code / Fable-Opus** | Director: focus, critical code, architecture | Ceiling. Does NOT review every Qwen diff |
| **Sonnet subagents** | Mechanical labour (heavy reads, volume search, scoped edits) via Agent/Workflow `model sonnet` | Cheap, no external dependency |
| **Gemini API** | PARKED 2026-07-10 | Do NOT use (429, no API). The MAK research system replaced it. Skills relevo-web / orquestacion-gemini-claude unused |
| **Arena (LMArena)** | Free frontier on demand for hard architecture | No API -> manual, small airdrop. Not an automatic source of truth |
| **Qwen (DashScope) / NVIDIA NIM / OpenRouter** | Bulk coder (edits, tests, boilerplate) | Output ALWAYS through the GATE, never straight to Claude |

### Spend control (quota = tokens x model weight x direction)

weight: Haiku << Sonnet << Fable/Opus. output > input. cached input << new input.
default main model = Haiku, effort medium. escalate `/model` ONLY on a trigger.

STAY CHEAP (Haiku/Sonnet): an already-specced edit | a test after an identified
gap | volume read/map | git ops | boilerplate | compression | translating an
order into edits.

ESCALATE to Fable/Opus if ANY trigger is true:
- destructive+irreversible on something you did NOT create, with unconfirmed
  dependencies (`rm` `mv` `kill` `DROP` `git reset --hard` `push --force`,
  overwrite)
- touches: credentials/secrets, auth, CI workflows, `src/flujo/airdrop.py`,
  public behaviour (CLI/API/delivery format)
- money values (RD packs, quotes, prices)
- more than one defensible option with no obvious default, and choosing wrong is
  expensive
- it was already attempted and failed (check `src/flujo/version.py`
  `get_changelog()`)
- off-task finding (a bug nobody asked about, noticed in passing)
- you are guessing / cannot verify / would have to fabricate data
- new cultural piece / motor-omega / declaring Omega11

DOUBT == escalate. Cheap model in doubt: escalate, do not guess. The expensive
tier is for DECIDING and VERIFYING, not for volume.

### Qwen gate (replaces "Claude reviews the diff")

1. CI (mandatory, branch protection): `py -m pytest`, compile, `flujo verify`.
2. Free reviewer: Arena or a Sonnet subagent looks at what CI cannot see (design,
   scope, creep).
3. Claude steps in ONLY if the gate escalates architecture, not as a fixed step.

## User environment

```txt
Main system: Windows + Git Bash
Commands for the user: py, not python
Credentials: never store tokens, cookies, keys, private data or real sensitive files
Remote repo: https://github.com/ligereza/vibecodeine/
```

ASCII-only applies ONLY to `CLAUDE.md` and the operational `context/*.md`
(LAST_HANDOFF.md and similar). Date: 2026-06-24, clarified 2026-07-26.

**Real cause: this is a rule FOR WEB AGENTS, not for local Claude.** What broke
those files was a web agent: its round trip (clone, edit elsewhere, deliver a
ZIP, apply it on Windows) mangles diacritics, and that produced the corrupted
commits v0.35.7-v0.35.9. Local Claude Code writes UTF-8 straight to disk and does
not have that problem. These two files stay ASCII because BOTH edit them: the
lowest common denominator protects them. Since 2026-07-26 they are written in
English anyway, so the rule costs nothing.

Retirement: when an automatic encoding check in CI makes it unnecessary, or when
the web-agent channel stops mangling accents.

Mandatory counterpart: EVERY human-facing product (`data/`, `docs/rd/`, reports,
the database, cultural pieces) goes in correct Spanish UTF-8. ASCII-only NEVER
extends to products.

## Central rule

Leave the repo more operational than you found it. Nothing half-done. Forbidden
to deliver as final:

```txt
TODO
finish later
...
NotImplementedError
silent try/except: pass
changes without verification
generated files / caches inside the airdrop
agent one-off reports, snapshots or scripts in the repo ROOT
```

Agent output (diagnostics, snapshots, checks) goes to the session scratchpad or,
if it is worth keeping, to `tools/` (reusable) / `_archive/` (historical) via PR.
The root got dirty twice (commits 35058a3 and the 07-21 session); do not repeat.

Meta-rule (2026-07-23): every new operational rule carries a date, a concrete
cause and a retirement condition. A rule missing those three is a candidate for
pruning at the next audit. Cause of this meta-rule: the ASCII rule outlived its
context and ended up mangling products. Retirement: when the repo has another
mechanism for rule hygiene.

Main is governed with `enforce_admins`: NOBODY pushes directly (not the admin,
not an agent holding the user's credential). Every change = branch + PR + green
CI. Squash merges keep the PR author as the author (a merge of a MAK PR shows up
in `git log` as a miskirabit commit: that is normal, it went through the gate, it
is not a direct push).

Branch topology (2026-07-25, user's order; replaces the 07-23 one that declared 4
lines): the repo has THREE lines and no more.

- `main` = EVERYTHING, without exception. It is the complete version; the lines
  come DOWN from main.
- `rd` = NGO / data / grants.
- `iskvw` = curation / artistic / artwork (formerly `portafolio`, renamed 07-23).

`mejoras` was folded into main and retired: a separate infra line kept turning
main into a subset, which is the problem this topology fixes. Repo/infra work is
born from main and returns to main.

There is a fourth branch, `mak`, and it is NOT a line: it is MAK's INBOX. Nothing
lives there; its only exit is a PR into main. If it ever stops draining, it has
become a line and must be corrected.

MAK and agents push or open PRs against THEIR line, never against main. New
feature: born in its line and returns to its line. Line -> main promotion = a PR
curated by the director, green CI mandatory. To bring a line up to date:
`git merge origin/main` (never rewrite history). Work that does not fit a line:
escalate before inventing a loose branch.

## How to work

1. Read `context/LAST_HANDOFF.md` (state / done / pending / blockers / next).
2. Identify the area: core, web, RD/supplements, Studio/events, Resolume, docs,
   pipeline.
3. Review related files before editing.
4. Minimal, complete, verifiable changes.
5. Update `context/LAST_HANDOFF.md`.
6. Airdrop if you do not have direct push.

### Saving context (do not read the whole repo)

- Mechanical map (0 tokens): `py tools/contexto_repo.py` (or `map`) = tree + key
  files + do-not-touch zones.
- Context for one task: `py tools/contexto_repo.py task "<keywords>"` =
  recommended paths.
- Heavy reading -> cheap model: Sonnet subagents (`model sonnet`) or Qwen/NIM
  summarise the fat paths. Give them ONLY the files for the task, not the repo.
- Fat paths to delegate: `datadrops/`, `jobs/`, `projects/`,
  `svg/suplementos_rd/`, `docs/handoffs/archive/`, `.claude/skills/*/`.
- Small and critical, read it directly: `CLAUDE.md`, `context/LAST_HANDOFF.md`,
  `pyproject.toml`, `src/flujo/cli.py`, a specific `SKILL.md`.

### Searching memory (2026-07-26, measured)

Two mechanisms make a memory search return "nothing found" while the answer is
written down. Both were hit the same day.

1. `.remember/` is INVISIBLE to the Grep tool: that folder has a `.gitignore`
   containing `*`, ripgrep honours it by default and says nothing. Search it with
   `Select-String -Path "<repo>\.remember\*"` from PowerShell, which does not
   honour gitignore. Never conclude "it does not exist" from a Grep over paths
   that might be ignored.
2. Older memories were written in English while the conversation ran in Spanish,
   so the Spanish term missed them. Fixed at the root by writing everything in
   English from 2026-07-26 on; for anything older, search both languages or the
   shared stem.

## Continuity between sessions (mandatory)

1. When closing EVERY session: update `context/LAST_HANDOFF.md`, the single
   checkpoint. If you worked, the state changed.
2. Before "solving" something already attempted: check `src/flujo/version.py`
   `get_changelog()` (what already failed), do not start from zero.
3. `src/flujo/resolume/automator.py` `build_chataigne_noisette_experimental`: the
   `.noisette` schema is ALREADY VALIDATED against real files from Chataigne
   1.10.3 (fixtures `tests/fixtures/chataigne_1103_real*.noisette`, suite
   `tests/test_noisette_real_fixture.py`, 2026-07-16; it was rewritten 4x by
   guessing across v0.48.2-v0.48.5, and v0.48.5 turned out to be correct). Any
   change to the builder keeps that suite green. NEVER speculate about the
   schema: the fixture is the source of truth.

## Minimum verification (mandatory)

Python:
```bash
py -m compileall src/flujo
py -m pytest tests/ -q
py -m flujo verify
```
DOCTRINE caveat (2026-07-20, see `docs/handoffs/archive` PR #97): the verdict on
a PR is its CI matrix (ubuntu+windows), NEVER the local pytest in a worktree --
the editable install imports from the main checkout, and the worktree can pass
while testing the wrong code. Run it locally anyway for hygiene, but do not call
it the final verdict; CI gives that.

Coverage check (optional, non-blocking):
`py -m pytest tests/ --cov=src/flujo --cov-report=term-missing:skip-covered`.

Test count is not a quality signal. A test that only verifies a mock or a fake
module (not real behaviour) is garbage -- prune it when you find it, do not pile
on top (real case: `ig/download.py` tests mocked a fake `instaloader` module that
production no longer used, giving false safety; fixed 2026-07-20). A test that
reaches the network depending on the environment is the same defect (real case:
`test_ig_cffi_fallback` did a real Instagram download whenever `curl_cffi`
happened to be installed; fixed 2026-07-26).

Autogenerated code (MAK utilities and similar): compiling is NOT enough -- 6 of
24 files compiled with a latent NameError (missing import, typo). Rule: smoke-run
it once before the PR; the `tests/test_utilidades_mak_sanidad.py` ratchet
(pyflakes) blocks new cases.

Web:
```bash
cd web && npm run typecheck && npm run build:context && cd ..
```
Airdrop:
```bash
py scripts/validate_airdrop.py
py scripts/run_airdrop_checks.py "short message"
```
Do not declare OK without running the verification. If it fails, report the real
error.

## Airdrop (agents without push)

Detail: `docs/AGENT_AIRDROP_PROTOCOL.md`. A ZIP with `_airdrop/` at the root:
`HANDOFF_*.md`, an updated `context/LAST_HANDOFF.md`, real files at their final
paths, and a verification report.

```bash
py scripts/validate_airdrop.py
py scripts/run_airdrop_checks.py "short message"
# the runner applied but failed afterwards:
py scripts/run_airdrop_checks.py --resume "short message"
```

If it touches `src/flujo/airdrop.py`: both commands require
`--allow-airdrop-engine`.

## Repo cleanup

Cleaning locally is fine: `rm -rf _airdrop`, `__pycache__/`, `.pytest_cache/`,
`_logs/`.
Do NOT commit or airdrop: `__pycache__/`, `.pytest_cache/`, `node_modules/`,
`dist/`, `build/`, `_airdrop/`, `_airdrop_backups/`, `_logs/`, `*.zip`, `*.db`,
real heavy assets, credentials.
Historical / operational: archive via `git mv` into
`_archive/legacy_YYYYMMDD_HHMM/` (preserves history), do not delete blindly.

Agent worktrees under `.claude/worktrees/` are pruned when the task ends
(`git worktree remove`, which deletes the checkout and never the branch). Cause:
7 abandoned ones were each a full copy of the repo and multiplied every handoff,
checkpoint and doctrine file by 8, so a search returned hundreds of hits with no
way to tell which one ruled.

## Repo map

Live core:

| Path | Role |
|---|---|
| `src/flujo/` | Python package + `flujo` CLI |
| `tests/` | Tests |
| `web/src/` | React/Vite hub (build -> `context/*.html`) |
| `scripts/validate_airdrop.py`, `scripts/run_airdrop_checks.py` | `_airdrop/` validator + runner |
| `.github/workflows/ci.yml` | CI: install, compileall, health, pytest |
| `pyproject.toml` | Metadata + version (the version rules) |
| `.claude/skills/*/SKILL.md` | Agent playbooks |
| `_archive/legacy_20260725_desktop/` | Tkinter floating app (Gemini->Claude router, PARKED); archived 2026-07-25, see CERTIFICADO.md there |

Daily operation: `jobs/_template/`, `datadrops/`
(`flujo datadrop scan/list/prepare`), `projects/piezas_vectoriales/`,
`projects/flyer_eventos/`, `tools/`, `schemas/`. Human entry point: `flujo app`
(fallback `context/flujo_hub.html`).

Generated / historical (do NOT edit by hand): `jobs/20*`,
`projects/piezas_vectoriales/20*`, `datadrops/` (output), `context/*.html` (via
`npm run build:context`), `_airdrop*`, `_logs/`, `.archive/`, `_archive/`,
`docs/handoffs/archive/`. `data/*.db`, `*.sqlite*`, `context/DAILY.md`,
`context/dashboard.html` do not go into commits (`context/LAST_HANDOFF.md` does).

Unknown path: classify it (live core / daily operation / historical / generated)
before touching it. Historical or generated: do not use it as a base without
saying so.

## Operational areas

**Python core:** `src/flujo/`, `scripts/`, `tests/`, `pyproject.toml`.
`py -m flujo app`, `py -m flujo verify`.

**React/Vite web:** `web/src/`, `context/flujo_hub.html`,
`context/plano_demo.html`, `context/svg_visualizer.html`. Build:
`cd web && npm run build:context && cd ..`.

**RD / Supplements:**
```bash
py -m flujo suplementos list
py -m flujo suplementos validate svg/suplementos_rd/04_contraportadas/generadas/*.svg
py -m flujo brief paquete-cotizacion jobs/<job>
```
Queryable database: `py -m flujo rd-db build|reactivo|packs|productora|venues|por-tipo|lookup`
(`src/flujo/rd/`, a regenerable projection; `data/rd.db` is gitignored).
Everything this area outputs is read by humans: correct Spanish with diacritics.

**Culture (art research):** tapiz, tilde, psicosis, precursor. Third hub
workspace (`CulturaPanel.tsx`). Tapiz instrument: `projects/tapiz/`
(`py projects/tapiz/vibecode_spaces.py file.py -m void --svg piece.svg`). Meter:
`tools/tilde_meter.py` (standalone). Direction: `projects/tapiz/DIRECTION.md`.
MAK research: `cultura/` -> main via PRs #48/#49.
LIMITS: descriptive yes; nothing generative by synthesis; psicosis NEVER profiles
real people. The artwork `arte-ascii-readme.svg` is the artist's finished piece
and is not altered; the README text around it is ordinary repo content.

**Studio / Events:**
```bash
py -m flujo eventos flyer-auto "https://www.instagram.com/p/XXXX/"
py -m flujo resolume automatizar jobs/<job_id>
```
Instagram: the real download path is **parth-dl** (`pip install parth-dl`;
`parth_dl.get_info()`, primary path in `flyer_auto.py` since 2026-07-22).
Video/reel uses the thumbnail; a carousel only gets the first image.
`curl_cffi` is the secondary path on Linux (it imitates Chrome's TLS
fingerprint). imginn.com is dead (403 Cloudflare); instaloader does NOT work (IG
demands login); do NOT use `yt-dlp`.

## Closing a task

THERE IS NO DELIVERABLE (2026-07-26, user's words). Cause: the mandatory closing
ritual pushed agents into fabricating a product, a report or a plan nobody asked
for, and that derailed several sessions in a row. Retirement: none, it is a
direct order.

If you touched code, run what that code covers and paste the real output -- not
an "OK". If you did not touch code, there is nothing to report. Verification
exists to find out whether it works, not to decorate a closing.

The verdict on a PR is its CI matrix, never the local pytest.

## When closing the session

Update `context/LAST_HANDOFF.md`, the SINGLE CHECKPOINT. It stores ANSWERS, not
questions: what the user decided gets written there in the same session and stops
showing up as pending. `SESSION_STATE.json` and the six documents that competed
with it (PLAN_SIGUIENTE_AGENTE, PLAN_SEMANAL_OPUS, ORQUESTACION_SUCESOR,
WALKTHROUGH, MASTER_PLAN, DIRECTOR_CONTRACT) were archived on 2026-07-26: they
were the reason every agent rebuilt the state and asked again what had already
been answered.

Nothing personal in the repo -- it is public. Absolute paths, IPs, phone numbers
and credentials go to the assistant's local memory.

Conflict between sources, in order: the user -> this `CLAUDE.md` ->
`context/LAST_HANDOFF.md` -> specific docs -> `README.md`.

## Omega bridge

- `puente/OMEGA_MAP.md`: Omega <-> flujo map.
- `puente/SEMILLAS.md`: dated seeds -- every new project starts from here.
- `PLAN_ANUAL_2026-2027.md`: growth with Omega11 per quarter.
- skill `motor-omega`: 2 rules for pieces (declare Omega11 before exposing;
  failure is not reinterpreted).
