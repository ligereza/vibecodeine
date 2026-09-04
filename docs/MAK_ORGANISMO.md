# MAK the machine

**MAK is `/home/mak`. The repo is one directory inside it.**

That sentence is the whole reason this file exists. `/home/mak/GENESIS.md`
(2026-07-16) already said it -- *"El repositorio `flujo` vive en otra maquina;
este organismo respira fuera del repo"* -- and a session on 2026-08-28 still
declared `research/` and `labs/` nonexistent after searching only inside the
repo. They exist at `/home/mak/`, and their figures were exact.

## Do not read a number here. Run this.

```bash
python3 tools/medir_organismo.py
```

It answers, in order of consequence: how many cron lines are active, which of
the five organs respond, whether `main` has branch protection, how many lines
would start on resume, and the Python environments. Read-only.

The first version of this document carried those numbers as prose across 496
lines -- in a repo whose diagnosed problem was prose, and against rule 3 of
`docs/AUTORIDAD.md`, which says no measured figure is written without its
measurement date. What follows is only what does not rot.

## Why the organism is paused

`context/GIT_HISTORY_STRATEGIC_REVIEW.md` was written **2026-08-14 at 19:16**,
thirteen minutes after the crontab was paused at 19:03. It closes with
*Direction for the house-ordering work*:

1. Complete semantic triage of physical departments first.
2. Assign each path a current owner, consumer, dependency contract, platform
   role and verification result.
3. Classify historical material as live/adoptable, superseded, Windows-legacy,
   obsolete, undeveloped, blocked or evidence-only.
4. Use Git history only to explain how a candidate came to exist.
5. Do not merge, delete, revive or rename because a branch looks authoritative.

**MAK was stopped on purpose to be ordered, and the ordering did not happen.**
Step 2 was executed for the repo's 26 top-level paths on 2026-08-28
(`context/MAK_TRIAGE_20260828.md`).

## Before resuming

Five of the 23 paused lines write outside this machine. `entregar.py` runs
`gh pr create --draft` every 6 h; **`revisor.py --enforce` runs `gh pr ready`,
`gh pr comment` and `gh pr merge`** every 6 h. Its own docstring records that
this code *"lived on ONE disk for ten days merging PRs by itself"*.

Resume is one command, verified command by command against the live crontab
(23 identical, 0 lost, 1 extra which is `MAK-REPO-SYNC`, already paused there):

```bash
crontab /home/mak/flujo/cultura/mak_plataforma/crontab.mak
```

To resume without merge authority, drop `--enforce` from the `MAK-REVISOR`
line: `revisor.py` without it is observational by design.

`MAK-REPO-SYNC` is the line to keep off. It ran
`git fetch && checkout -B main && reset --hard origin/main` plus `cp -ru` into
three department directories, every ten minutes. It was the deploy mechanism
before the shims replaced it, and it destroys uncommitted local work.

One stray: the `MAK-PUENTE-ISSUES` line carries `FLUJO_GPU_BACKEND=CUDA`, but
`cultura/mak_plataforma/puente_issues.py` never mentions torch, cuda or that
variable. Inert and misleading.

## Where to look before saying something does not exist

Every "it does not exist" in the 2026-08-28 session that was checked against
these three turned out to be "it exists and I looked in one place".

| Surface | What it holds |
|---|---|
| `/home/mak/.local/share/Trash/` | 628 MB, 14065 files, 232 `.trashinfo` records. **Each file carries its original `Path=` and `DeletionDate=` beside it** -- read that before claiming where something came from |
| sibling directories under `/home/mak` | `research/`, `labs/`, `lenguaje/`, `curatoria/`, `vigia/`, `plataforma/` -- all invisible to a repo-relative path |
| `/home/mak/.codex/memories/rollout_summaries/` | 11 dated session summaries that name their own artifacts by full path |

A worked example of getting this wrong twice: the missing `PHASE*` corpus was
first reported as "749 sit in the Trash, recoverable". The `.trashinfo` says
that trashed `flujo` tree is `/home/mak/.codex/worktrees/31af/flujo`, a **Codex
worktree** deleted 2026-08-24, not the repo. And `PHASE1_INVENTORY.csv` was
never deleted from the repo: the session that made it ran with that worktree as
its `cwd`, so it was **written there and never arrived**.

## Triangulation sources

Cross these instead of scanning. Ordered by how fast they pay off.

| Source | What it answers |
|---|---|
| `/home/mak/GENESIS.md` | what MAK **is**: five organs, ports, model chain, rules. 4 KB |
| `/home/mak/Descargas/historia git.odt` | 403 decision events, 39 activity days, 450 key path journeys. sha256 `510ca28c...e6a56` |
| `out/archaeology/claude-codex-mak-20260815.sqlite` | 1028 commits, 9054 file events, 83835 turns, 14224 rule events |
| `indexes/mak-reality-20260813/archivo_index.sqlite` | 1904 assets with sha256, 431 projects, 1877 families |
| `.codex/memories/rollout_summaries/` | what past sessions did, with paths |

`tools/conversacion.py` reads `~/.claude/projects/` transcripts as a corpus.
The `arqueologia.py` and `esfuerzo.py` named beside it in `CAPACIDADES_MAK.md`
do not exist as files; the archaeology function survives as
`tools/inferential_archaeology.py` plus the sqlite above.

The ODT is not plain text. It reconstructs as JSON:

```python
import zipfile, re, json
xml = zipfile.ZipFile("/home/mak/Descargas/historia git.odt").read("content.xml").decode()
txt = re.sub(r"<[^>]+>", "\n", xml)
raw = "".join(l for l in txt.split("\n") if l.strip())
d = json.loads(raw[raw.find("{"):])
```

## The retirement convention, measured from the history

Querying `git_files` joined to `git_commits` in the archaeology sqlite:

- `.archive/` lived in the repo 2026-06-30 to 07-03 (283 events)
- renamed into `_archive/legacy_historico_previo/` on 2026-07-27
- `_archive/` **deleted whole on 2026-07-30**, 458 files in two commits

**This repo has done this cleanup twice and both times the in-repo archive was
later deleted.** Since then retirements live outside the repo:

```
/home/mak/_archive/<what>-<why>-<yyyymmdd>/
```

alongside `faro_sync_20260809`, `watsonx-retired-20260820`,
`provider-retirement-20260820`, `group4-reverted-20260821`,
`shadow-copies-20260821` and `orden-limpieza-20260828`.

**An archive is organised by reason, not by original path.** It gets read with
one question -- *why was this taken out?* -- never *where did it sit?*. The
2026-08-28 retirement holds seven categories (`herramienta-abandonada`,
`dependencia-ausente`, `proveedor-retirado`, `salida-regenerable`,
`evidencia-de-corrida`, `entregado-a-cliente`, `sin-consumidor`), each with a
one-line rule in its own `POR-QUE.txt`, plus `mapa-de-retiro.csv` giving every
item its original path so a single one can be put back.

Its first pass was a flat dump mirroring the original layout -- 30207 files in
one box. Moving a mess into a box is not ordering it.

## Hardlink dedup: what is safe and what was undone

86.1 MB deduplicated across `quarantine/`, `rollback/` and `state/`. Verified
safe: nothing in the repo or in `/home/mak/plataforma` writes to those three,
and `backup.sh` creates a new tarball per day rather than rewriting one, so
`backups/` holds zero links.

**37.6 MB in `research/corpus/` was linked and then undone.** The justification
was the run-directory naming convention (`_v2`, `_v3`) plus mtime -- evidence
about the past, not about what writes. `cultura/mak_research/source_pipeline.py`
lines 425 and 433 use `write_text` and `write_bytes` on
`captures/<capture_id>.txt`, which truncate in place, and its `mkdir(exist_ok=True)`
allows writing into an existing run root. The research organ on :8890 is
running. One re-capture would have silently changed up to twelve copies.

The check that mattered was never mtime. It was: **what code writes here, and
does it truncate or create?**

## The logs are evidence again

`tests/test_entregar_micelio.py` and `tests/test_revisor_gates.py` wrote into
`/home/mak/plataforma/logs/`. The revisor case left the line

```
PR #7 MERGEADO autonomo por el box
```

in the production log while no merge happened. Both fixed 2026-08-28 with an
autouse fixture; a full-suite sweep confirms no test writes there any more.
**Any claim about what ran, read from those logs before 2026-08-28, is unsound
unless checked against the pause date.**

## Out of scope, by operator instruction

- `curatoria_inbox/` (181 GB): the in-progress Windows-to-Linux migration. MAK
  must be ordered and working before it completes.
- `RD/` (58 GB): client production material.
- `WIN/` (7.9 GB): legacy evidence, `agents.md` forbids changing it.
