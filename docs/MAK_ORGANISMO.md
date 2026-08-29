# MAK the machine, measured

Measured 2026-08-28. Language: English ASCII, per the Language section of
`agents.md` for operational metadata.

**MAK is `/home/mak`, not `/home/mak/flujo`.** The repo is the authoring
baseline inside the organism. This file exists because every document in the
repo measures the repo and calls the result MAK, and that mistake has a cost
this session paid twice.

## The finding that outranks everything else in this document

**The MAK organism is stopped, and no document says so.**

```
crontab -l | grep -v '^#' | grep -c .     ->  0
crontab -l | grep -c '^# PAUSED'          ->  23
```

Twenty-three scheduled jobs, none active. The markers give the date:

| Marker | Lines |
|---|---:|
| `PAUSED-DOCTOR-RENOVATION-20260814-1903` | 16 |
| `PAUSED-DOCTOR-20260814-1903` | 6 |
| `PAUSED-FARO` | 1 |

Paused **2026-08-14 at 19:03**, fourteen days before this measurement. What
stopped, by its own cron comment: `MAK-ORGANISMO watchdog`, `MAK-ORGANISMO
backup`, `MAK-ORGANISMO lexicon`, `MAK-ORGANISMO senal`, `MAK-VIGILAR`,
`MAK-TRABAJO`, `MAK-REDWATCH`, `MAK-ENTREGAR`, `MAK-BACKLOG-CODEX`,
`MAK-JUNTA`, `MAK-AGENTE-LIBRE`, `MAK-REVISOR`, `MAK-CAPATAZ`, `MAK-LATIDO`,
`MAK-CURATORIA`, `MAK-MATERIAL`, `MAK-CORPUS`, `MAK-VIGIA`, `MAK-MICELIO`.

The logs agree. Every process log under `/home/mak/plataforma/logs/` stops on
2026-08-14, most between 11:55 and 18:56:

```
watchdog.log  ago 14 11:55     capataz.log   ago 14 14:40
backup.log    ago 14 04:30     micelio.log   ago 14 15:00
latido.log    ago 14 12:07     vigia.log     ago 14 14:45
material.log  ago 14 14:15     hook.log      ago 14 15:10
corpus.log    ago 14 14:35     trabajo.log   ago 14 18:56
```

No file in `CAPACIDADES.md`, `context/LAST_HANDOFF.md`,
`docs/MAK_CURRENT_STATE.md` or anywhere else in the repo mentions the pause.
For fourteen days the documentation has described a running system.

This is the answer to "why does only the flyer chain feel alive": that chain
runs on GitHub Actions, on GitHub's infrastructure. Everything that runs on
this box has been off since August 14.

## Services

| Unit | Active | Enabled |
|---|---|---|
| `mak-research-queue.service` | inactive | static |
| `mak-xio.service` | inactive | disabled |
| `mak-clipboard-type.service` | inactive | disabled |
| `rclone-gdrive.service` | **active** | enabled |
| `onedrive-rclone.service` | **active** | enabled |

Zero timers. Three more services were disabled by renaming on 2026-07-18 and
still sit in `/home/mak/.config/systemd/user/`:
`mak-hub.service.bak`, `mak-codex.service.bak`, `mak-xio.service.bak`.

The two active units are cloud sync, not MAK.

## The one live process

```
/home/mak/plataforma/.venv/bin/python /home/mak/flujo/cultura/mak_plataforma/hub.py
```

Uptime 7h34m at measurement. It is the whole of MAK's running surface.

## The logs were being contaminated by the test suite

Proven by measurement, and fixed the same day:

```
/home/mak/plataforma/logs/entregar_micelio.log     72080 bytes
python -m pytest tests/test_entregar_micelio.py    6 passed
/home/mak/plataforma/logs/entregar_micelio.log     72441 bytes
```

361 bytes of test output appended to a production log. The lines it wrote say
`simulated: box unreachable`, which reads exactly like a real outage.

The repo already knows this is wrong. `tests/test_entregar_smoke_gate.py:89`
carries the comment *"LOG bajo tmp_path para no ensuciar ~/plataforma/logs en
la maquina real"*, and `tests/test_revisor_gates.py:245` monkeypatches `LOG`.
One suite did not: `tests/test_entregar_micelio.py`. **Fixed 2026-08-28**
with an autouse fixture following the same convention; verified by measuring
the production log before and after a run (72802 bytes both times).

`tests/test_coherence_boundaries.py` was a false positive of the first grep,
which matched the string `"logs/"` inside a constant in
`cultura/mak_plataforma/coherence.py`. Measured: it does not write.

Consequence for anything read before 2026-08-28: a claim of the form "process X
last ran on date Y", taken from these logs, is unsound unless the entry is
checked against the pause date. Entries after the fix are trustworthy again.

## Surfaces, measured 2026-08-28

Excluding `curatoria_inbox/` (181 GB, the in-progress Windows-to-Linux
migration staging area; out of scope until MAK runs again) and the standard
desktop directories.

| Surface | Size | What it is |
|---|---|---|
| `RD/` | 58 GB | Reduciendo Dano production material: PSD, flyers, After Effects autosaves. Not machinery |
| `venvs/` | 12 GB | five Python environments; see below |
| `WIN/` | 7.9 GB | legacy Windows tree. `agents.md`: historical evidence, do not change |
| `flujo/` | 7.0 GB | the repo. Authoring baseline |
| `portfolio_media/` | 5.5 GB | media |
| `blender/` | 1.2 GB | vendored Blender |
| `actions-runner/` | 1.2 GB | self-hosted GitHub runner |
| `research/` | 862 MB | live: `jardines_interpretativos.sqlite`, `corpus/`, `intake/`. Modified today |
| `labs/` | 439 MB | 7 lab directories, 6 `archivo_index.sqlite` snapshots |
| `state/` | 301 MB | two snapshots dated 20260813 |
| `rollback/` | 240 MB | atlas-* rollback points, all 20260811 |
| `models/` | 207 MB | model weights |
| `quarantine/` | 185 MB | flujo-* quarantines, all 20260806-09 |
| `backups/` | 166 MB | `mak-20260809`..`mak-20260814.tar.gz` |
| `indexes/` | 113 MB | mak-* runtime maps, 20260813 |
| `plataforma/` | 95 MB | **the organism**: cron targets, logs, `director_runs/`, its own `.venv` |
| `curatoria/`, `codex/`, `trazos/`, `xio_puente/`, `bucle/`, `lenguaje/`, `vigia/` | < 10 MB each | live subsystems |

`rollback/`, `quarantine/`, `state/` and `indexes/` together are 839 MB, all
frozen at 2026-08-06..13, i.e. before the pause.

## Seven Python environments, ~17 GB

All CPython 3.11.2.

| Environment | Size | Status |
|---|---|---|
| `flujo/.venv` | 5.6 GB | runs the test suite |
| `venvs/visual-index-pilot` | 5.6 GB | last modified 2026-08-10 |
| `venvs/mak-gpu` | 4.8 GB | last modified 2026-08-23 |
| `venvs/oi` | 707 MB | last modified 2026-07-15 |
| `venvs/flujo` | 203 MB | last modified 2026-08-06 |
| `plataforma/.venv` | 60 MB | **runs the only live process** |
| `venvs/knowledge-migration` | 46 MB | last modified 2026-08-13 |

The smallest environment runs the only thing that runs. Nothing was found that
references `venvs/visual-index-pilot`, `venvs/mak-gpu`, `venvs/oi` or
`venvs/knowledge-migration` by path, but a venv is also reachable through
`PATH`, an alias or an interactive shell, so absence of a textual reference is
not proof of disuse. **Not retired.** Deciding this needs the operator.

## The addressing error, twice

Documents that live in `flujo/` cite sibling surfaces in relative form. Read
from `flujo/`, they resolve to nothing.

`CAPACIDADES.md` listed four databases under `research/**` and `labs/**`. An
earlier pass this session declared them nonexistent and removed the rows. That
was wrong: they exist under `/home/mak/`, and the original figures were exact.

| Path | Claimed | Re-measured 2026-08-28 |
|---|---|---|
| `/home/mak/research/jardines_interpretativos/jardines_interpretativos.sqlite` | 23 tables, 276 rows, integrity OK | **exact** |
| `/home/mak/labs/**/archivo_index.sqlite` | 6 snapshots | **exact** |
| `/home/mak/research/intake/**/intake.sqlite` | 2 snapshots | **exact** |
| `/home/mak/research/corpus/**/sources.sqlite` | 14 snapshots | 12 (the only real drift) |

The same error hit `docs/GLOSSARY.md`, whose `lenguaje/corregir.py` and
`lenguaje/medir.py` entries read as broken from inside the repo and resolve
fine at `/home/mak/lenguaje/`.

`agents.md` warns about precisely this: *"The absence of a file in
`/home/mak/flujo` does not prove that it is absent from MAK."* The warning
existed and the mistake was made anyway, which is why the rule now has a
measured example attached.

**Rule.** A reference to a surface outside the repo carries its absolute path
from `/home/mak`. A repo-internal reference carries its path from the repo
root. No relative form crosses that boundary.

## Why the organism was paused: the specification nobody executed

`context/GIT_HISTORY_STRATEGIC_REVIEW.md` was written on **2026-08-14 at 19:16**
-- thirteen minutes after the cron pause at 19:03 -- by an agent identifying as
LUNA. It reads a source document, `/home/mak/Descargas/historia git.odt`, whose
sha256 was recorded and **verifies exactly today**:
`510ca28cb0bc1222a659b0077704344a77c8fa3438298a35f18b1e6f562e6a56`.

That ODT is a `git-history-mega-summary-v1`: 44781 paragraphs that reconstruct
as valid JSON of 1382307 characters, exactly the count LUNA declared. It holds
403 decision events, 39 activity days, 450 key path journeys, 6 local refs, 12
remote refs and 5 duplicate-tip groups. The 1347 omitted journeys point at
`git_history_context.full.json`, which does not exist in any tree.

The review closes with **Direction for the house-ordering work**:

1. Complete semantic triage of physical departments first.
2. Assign each path a current owner, consumer, dependency contract, platform
   role and verification result.
3. Classify historical material as live/adoptable, superseded, Windows-legacy,
   obsolete, undeveloped, blocked or evidence-only.
4. Use Git history only to explain how a candidate came to exist.
5. Do not merge, delete, revive or rename anything because a branch or
   historical commit appears authoritative.

**MAK is not broken. It was stopped on purpose to do this work, and the work was
never done.** Fourteen days.

Step 2 is now executed for the repo's 26 top-level paths in
`context/MAK_TRIAGE_20260828.md`, crossing the history's journeys with inode
birth time and this session's measurements. Zero paths remain unmeasured.

## Where things actually were

Every "it does not exist" in this session that got checked against three places
turned out to be "it exists and I looked in one place".

| Looked for | Concluded | Actually |
|---|---|---|
| `research/`, `labs/` | do not exist | exist at `/home/mak/`, figures exact |
| `lenguaje/corregir.py` | broken reference | exists at `/home/mak/lenguaje/` |
| 735 missing `PHASE*` files | "whatever removed them" | **749 of them sit in the Trash**, recoverable |
| `PHASE1_INVENTORY.csv` | never seen | in the Trash; recovered to `context/recuperado_20260818/` |
| the hash map | had to be built | `docs/*_learning/*/hashmap.json` carried `source_hashes` all along; 15 of 19 sources unchanged since 2026-08-25 |
| the reality index | had to be built | `indexes/mak-reality-20260813/archivo_index.sqlite`: 1904 assets with sha256, 431 projects, 1877 families |

**Three surfaces to check before concluding absence**: the Trash
(`/home/mak/.local/share/Trash/files/`, 628 MB, 14065 files), the sibling
directories under `/home/mak`, and the Codex session summaries under
`/home/mak/.codex/memories/rollout_summaries/`.

## Resume readiness, measured 2026-08-28

Each paused cron line was resolved to its executable and checked: `.sh` for the
execute bit, `.py` by importing it with **the same interpreter the cron line
declares** (`/usr/bin/python3`, not a venv). No job was run.

First pass: **19 of 23 would start, 4 would fail.** All four failed for the same
reason. They are symlinks from `/home/mak/` into the repo, and the repo files
were mode `100644` while their sibling `cultura/mak_vigia/vigia_guardia.sh` was
`100755`:

- `cultura/mak_research/watchdog.sh`
- `cultura/mak_lenguaje/cron_lexicon.sh`
- `cultura/mak_curatoria/curatoria_guardia.sh`
- `cultura/mak_research/micelio_guardia.sh`

Cron invokes them directly, not through `bash`, so the execute bit is required.
Fixed with `chmod +x` plus `git update-index --chmod=+x`, which makes the fix
travel. Re-verified: **23 of 23 would start, 0 would fail.**

The other machinery was already intact. All 46 shims under `/home/mak/plataforma`
resolve to a canonical module in the repo, and the ten critical ones import
cleanly under `/usr/bin/python3`. Resuming MAK is a crontab edit, not a repair.

One duplicate: `MAK-RETENCION` appears twice, pointing at
`/home/mak/research/retencion.py` with different `--dir` arguments
(`research/informes` and `research/paneles`). Both are valid; noted so a future
reader does not treat it as an accident.

## What ordering MAK actually requires

Files are the small part and are handled: see
`.archive/2026-08-28-orden/MANIFEST.md`. What remains is not disorder, it is
that the machine is off.

1. **Decide the pause.** Resume the 23 cron lines, or retire the ones that
   should not come back and record why. Either way the decision gets written
   down; right now the state is undocumented and fourteen days old.
2. **Isolate the two test suites** that write into `/home/mak/plataforma/logs/`,
   so the logs become evidence again.
3. **Resolve the seven environments** to the ones actually needed.
4. **Re-enable or delete** the three `.service.bak` files from 2026-07-18.
5. **Decide `rollback/`, `quarantine/`, `state/`, `indexes/`** (839 MB frozen
   before the pause): keep as rollback surface, or retire with a manifest.

Items 1, 2 and 4 are processes and services. They are declared here and not
executed.

## Out of scope, deliberately

- `curatoria_inbox/` (181 GB): active Windows-to-Linux migration staging. The
  operator's instruction is that MAK must be ordered and working before that
  migration completes.
- `RD/` (58 GB): client production material, not machinery.
- `WIN/` (7.9 GB): legacy evidence, `agents.md` forbids changing it.
