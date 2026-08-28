# MAK file ordering and cleanup -- 2026-08-28

Retirement zone declared by the repo itself: `tests/test_higiene_docs.py` lists
`.archive/` in `ZONA_MUERTA`, so the documentation ratchet already knows to skip
what lives here.

Language: English ASCII, per the Language section of `agents.md` for operational
metadata. The first version of this manifest was Spanish with diacritics.

## Rule applied

Nothing was retired without a prior consumer check. An empty or old directory is
NOT evidence of death. Three obvious candidates survived the check and stayed:

| Candidate | Why it stayed |
|---|---|
| `checkpoints/` (only `.gitkeep`) | consumed by `src/flujo/airdrop.py`, `src/flujo/knowledge/project_ir.py`, `src/flujo/knowledge/director.py` and 3 test suites |
| `inbox/` (2 txt from June) | consumed by `src/flujo/cli.py`, `src/flujo/intake/reception.py` and tests |
| `data/flujo.db` (frozen 2026-06-30) | consumed by `tools/repo_audit.py`, which runs in CI, and `tests/test_portfolio_gen.py` |

## Reverting

Each entry under `retirado/` keeps its original path in this directory's tree.
To revert one: `mv .archive/2026-08-28-orden/retirado/<path> <path>`.

## Baseline measured before touching anything

| Surface | Value |
|---|---|
| test ids | 3799 across 357 suites |
| suite | 3794 pass, 5 skip, 0 fail (3m25s) |
| `flujo.*` modules that import | 196 of 196 |
| endpoints in `cultura/mak_plataforma/hub.py` | 121 |
| endpoints in `src/flujo/web/hub.py` | 50 |
| schema identifiers | 209 |
| CLI commands | 42 |
| physical files | 3356 |

---

## Retired here -- 138 MB total

| Original path | Weight | Last signal | Measured consumer | gitignored |
|---|---|---|---|---|
| `.aider.chat.history.md` | 91 KB | 2026-07-08 | none; one changelog line in `src/flujo/version.py` | no |
| `.aider.input.history` | 10 KB | 2026-07-08 | none | no |
| `.aider.conf.example.yml` | 2 KB | 2026-07-04 | none (was tracked in git) | no |
| `.playwright-mcp/` (21 traces) | -- | 2026-07-31 | none | yes |
| `.remember/` (61 `today-*.done.md`) | -- | 2026-08-01 | only `docs/system_learning/luna_archive/hashmap.json`, an audit record, not code | yes |
| `proyectos/` (1 file) | -- | 2026-07-17 | none; the only "proyectos/" citation in code points at `00_sistema_generico/proyectos/`, a different path (was tracked in git) | no |
| `dist_compartir/` (2 HTML) | 1.1 MB | 2026-08-21 | none; it is a build output, see below | yes |
| `drive/` (9 files) | 127 MB | 2026-07-26 | none in code | yes |
| `_entregas/` (6 proposal PDFs) | 904 KB | 2026-07-08 | none in code | yes |
| `_logs/` (69 files) | 320 KB | 2026-08-21 | none in code | yes |

`dist_compartir/` regenerates: `web/scripts/copy-rd-share.mjs` and
`copy-plano-share.mjs` both call `mkdirSync(dirname(dest), {recursive: true})`,
so `npm run build:rd` and `npm run build:plano` recreate it.

`drive/` held render outputs keyed by issue number
(`render_issue320_DZGp0MtDYk7.png`) plus a video smoke. They are evidence that
the flyer chain worked, which is why they are archived rather than deleted.

Two of these files were tracked in git, so `git status` shows them as deleted:
`.aider.conf.example.yml` and `proyectos/flujo/OptimizerGen/prompt_optimizado.txt`.

## Deduplicated by hardlink -- 187.2 MB, no path lost

76 byte-identical copies now share an inode. **No path disappeared and no byte
changed**: verified with `md5sum` over the 895 files of the affected trees,
before and after, and the diff is empty.

Hardlink instead of retirement because 9 test suites read
`experiments/pilots/` as a fixture: moving a file there breaks tests, linking it
changes nothing observable.

| Tree | Before | After |
|---|---|---|
| `experiments/` | 420 MB | 237 MB |
| `docs/` | 61 MB | 60 MB |
| `jobs/` | 287 MB | 284 MB |

**Residual risk**: if anything rewrites one of the 76 linked files with
`open(path, 'w')`, its twin changes. To diverge on purpose:
`cp --remove-destination <source> <dest>`.

### What was deliberately NOT deduplicated

29.7 MB remain duplicated on purpose. Every group has a stated cause:

| Group | Size | Why it must not share an inode |
|---|---|---|
| `experiments/pilots/*/input/*` vs `runs/*/observation.json` | 14.6 MB | a re-run writing into `runs/` would truncate the shared inode and destroy the pilot input it started from. Runs are reproducible; the input is not |
| `data/rd_fuentes/*.json` vs `docs/recovered/**/raw/*.json` | 5.3 MB | live data vs preserved evidence. `raw/MANIFEST.json` records the evidence sha256; if the live copy is rewritten the hash no longer describes the evidence |
| `jobs/**/cambios.svg` vs `svg/**/_plantilla/*.svg` | 4.8 MB | delivered job output vs live template |
| `context/*.html`, `mapping.html` x5 vs `web/dist*/` | 2.2 MB | documented build projections (`context/MD_CONTEXT_MASTER.md`). `web/scripts/copy-context.mjs` rewrites them with `copyFileSync`, which truncates a shared inode |
| `.claude/skills/**` vs `.agents/skills/**` | small | it is source code |

An earlier version of this manifest reported 59.1 MB remaining. That figure was
inflated: it counted a group of 4 paths as 3 recoverable copies when 3 of them
already shared an inode. The correct method counts distinct inodes, not paths.

## Two findings from the dedup worth more than the megabytes

1. `runs/*/observation.json` in three ARICA runs is **byte-identical to
   `input/archive_observation.json`**: the pilot's "observation" output is a
   copy of its own input.
2. `enriched` and `enriched-technical-surface-20260827` share **24 of 29 files,
   117.4 MB identical**. The "technical surface" run differs in 5 files, not 30.

---

## Documents corrected, none retired

| Document | Claimed | Measured 2026-08-28 |
|---|---|---|
| `context/PHASE_REPORTS_INDEX.md` | 748 PHASE files, "untracked", plus its own list of truth sources omitting `docs/MAK_CURRENT_STATE.md` | 13 files, all tracked; now repeats the bootstrap order |
| `docs/SCRIPTS_INVENTORY.md` | four minors behind; `checkpoint.sh` nonexistent; `scripts/app.py` active; legacy under `_archive/**`; protocol at `docs/AGENT_AIRDROP_PROTOCOL.md` | version matches `pyproject.toml`; `checkpoint.sh` exists and `src/flujo/airdrop.py` invokes it; `app.py` does not exist; `_archive/` did not exist; neither did the protocol. Rewritten with a measured invoker column: 15 with an invoker, 14 with none |
| `CAPACIDADES.md` | 4 databases with "integridad OK" under `research/**` and `labs/**` | neither tree exists |
| `CAPACIDADES.md` | `mak_knowledge.db` 35 tables / 387.089 rows | 48 tables / 387.104 rows by `tools/repo_audit.py` (CI), which excludes SQLite internal tables |
| `CAPACIDADES.md` | runbooks at `xio/RUNBOOK.md` | were absent locally; restored, see below |
| `docs/GLOSSARY.md` | "236 Python files carry Spanish comments against 36 in English" (2026-07-30) | inverted: 405 carrying Spanish against 435 English. Also removed a PowerShell instruction for `.remember/` on a Linux box |
| `README.md` | 113 bytes, an ASCII image and nothing else | real entry point with the read order and a minimal map |
| `context/MD_CONTEXT_MASTER.md` | cited `dist_compartir/` with no note | notes that it is a regenerable build output |

## Restored, not deleted -- 4 documents

Four operational documents were missing from `/home/mak/flujo` while four active
documents cited them: nine dangling references, including the show-day runbook.
They existed only in `/home/mak/WIN/flujo/xio/`, and they were **not stale**:
`xio/FACES.md` is byte-identical in both trees, so WIN never diverged. Copied
with `cp -p`; the legacy tree was not modified.

`xio/RUNBOOK.md` (23 KB), `xio/HOTSPOT_SHOW_RUNBOOK.md`, `xio/CAPACIDADES.md`,
`xio/PLAN_SERVICIOS_SIN_ROOT.md`.

## Authority consolidated

New: `docs/AUTORIDAD.md`. Nine documents declared themselves canonical and the
loader (`tools/agent_bootstrap.py`) reads three. Headers demoted in
`docs/MAK_SYSTEM_DIRECTIVE.md`, `docs/system_learning/master/action_plan.md`,
`docs/INFLECTION_POINT_ARTISTIC_ARCHIVE_2026-08-24.md`,
`docs/PORTAFOLIO_PRODUCCION.md`, `PLAN.md` and `context/MD_CONTEXT_MASTER.md`:
each now states its domain and its date, and that it is not in the read order.

## Language

`agents.md` requires English ASCII for operational metadata. Applied to the
files authored in this session: `docs/AUTORIDAD.md` (0 non-ASCII), `README.md`,
this manifest, and the current packet of `context/LAST_HANDOFF.md`.

`context/*.md` cannot be mass-converted: `tools/agent_bootstrap.py:18` defines
`CURRENT_PACKET_START` with an em-dash and `tests/test_agent_bootstrap.py`
asserts a heading that carries an accent. Those characters are load-bearing.

The language ratchet `tests/test_idioma_ratchet.py` was tightened by hand from
**406 to 405** after `cultura/mak_plataforma/hub.py` left the Spanish-carrying
set. Its docstring says the pin only tightens by hand; it now reflects reality.

An emoji found in `context/VIDEO_WORKFLOW_MAK_20260817.md:86` was left alone: it
is part of a real media filename, so it is data, not decoration.

## Two measurement errors of my own, corrected in session

1. Searching only `<name>.py` reported 24 tools with no consumer, including
   `tools/agent_bootstrap.py`, which does have a test:
   `tests/test_agent_bootstrap.py` does `from tools.agent_bootstrap import SCHEMA`,
   the module form. Searching three forms gives **13**, not 24.
2. The first correction of the database table counted `sqlite_sequence`, giving
   49 tables where `tools/repo_audit.py` -- which runs in CI -- measures 48.
   Corrected to the CI method, which is the authority, and the method is now
   stated in the document.

## Post-cleanup verification

| Surface | Before | After |
|---|---|---|
| test ids | 3799 | identical set, 0 disappeared, 0 new |
| `flujo.*` modules that import | 196 | 196, identical set |
| endpoints `cultura/.../hub.py` | 121 | identical |
| endpoints `src/flujo/web/hub.py` | 50 | identical |
| schema identifiers | 209 | identical |
| product hashes under `out/` | 41 | none changed |
| hashes of the deduplicated trees | 895 | empty diff |

The suite caught two real regressions during the work:

- `test_higiene_docs.py::test_la_version_afirmada_coincide_con_pyproject` went
  red because `docs/AUTORIDAD.md`, while documenting the gate's blind spot,
  wrote the exact pattern the gate matches.
- `test_agent_bootstrap.py::test_current_packet_stops_before_historical_heading`
  went red because the first version of the new handoff packet dropped the four
  standing-contract statements the gate requires. The gate is right: a cleanup
  that loses an accepted boundary is a regression, not tidying.
