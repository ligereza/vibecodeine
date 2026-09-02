Identity: LUNA-19

## Assigned scope

Trace the flujo maintainer candidates `/home/mak/flujo/pyproject.toml`,
`src/flujo/cli.py`, `src/flujo/__main__.py`, `src/flujo/autonomia.py` and
`tests/test_cli_smoke.py` against `/home/mak/Descargas/historia git.odt`.
No source, runtime, WIN or Git state was modified. Every assigned candidate
was traced.

## History reading method

Read the required handoff, semantic matrix and PHASE10-14 triage CSVs first.
Inspected the ODT ZIP `content.xml` strategically and parsed its embedded JSON
schema/top-level summary, `what_is_alive_in_git`, `branch_paths`,
`key_path_journeys`, `decision_timeline`, `duplicate_tip_groups` and
`unresolved_by_design`. Queried only matching path-lineage and commit records
from `/home/mak/WIN/git_history_context.full.json`; the full evidence body was
not loaded into conversation. Historical refs and subjects are orientation
signals only. Physical `/home/mak/flujo`, `/home/mak` and `/home/mak/WIN`
remain authoritative.

## Bilingual matrix used

Search vocabulary covered exact ASCII identifiers and aliases, casefolded and
accented/unaccented forms: plataforma/platform/mak_plataforma; trabajo/work/
job/task; guardia/watchdog/guardian/vigia; bitácora/bitacora/log/ledger/journal;
estado/state/status/salud/health; carpeta/directory/dir/ruta/route/path;
servicio/service/unit/systemd; cron/timer/crontab/scheduled; cola/queue/backlog/
pending; investigación/investigacion/research; curatoria/curation/curate;
conductor/dispatcher/runner/handler/worker; entrega/delivery/deliver/output;
respaldo/backup/archive/restore; legado/legacy; obsoleto/obsolete;
reemplazado/superseded; improvisado/improvised; parche/patch. Searches were
also interpreted by owner and consumer, not literal path alone.

## Candidate counts

- Assigned: 5.
- Physically present and PHASE13 LIVE/ADOPTABLE: 5.
- Historical exact path journeys: 5/5.
- Historical path refs include the shared ref family (six local and twelve
  remote refs in the evidence); this does not identify a current branch.
- Current Debian venv contract: verified for CLI/module help; pytest runner
  unavailable.

## Evidence table

| Physical path | Layer / current classification | History refs and journey | First / last touched; changes | Historical domain and likely purpose | Owner / consumer / dependency | Recommendation and interpretation |
|---|---|---|---|---|---|---|
| `/home/mak/flujo/pyproject.toml` | contract; LIVE/ADOPTABLE | shared refs: `codex/three-plane-consolidation`, `iskvw`, `main`, `mak`, `mak-svg`, `rd` plus corresponding remotes | 2026-06-28 checkpoint / 2026-08-13 `307631a`; 28 changes | SHARED/UNKNOWN; package metadata, `flujo = flujo.cli:app`, dependencies and test contract | flujo maintainer; packaging and venv launcher; setuptools, Typer, pydantic, yaml, rich, jsonschema, requests, boto3 | keep candidate. A long maintained path with successive repairs/version bumps; the Debian venv contract supersedes ad-hoc/system-Python and parallel deployment alternatives operationally, but history does not prove a user decision. |
| `/home/mak/flujo/src/flujo/cli.py` | source; LIVE/ADOPTABLE | same shared ref family | 2026-06-28 checkpoint / 2026-08-12 `cd5ab70`; 28 changes | SHARED/UNKNOWN; maintained Typer CLI and user-facing command router | flujo maintainer; venv `flujo` launcher and users; Typer plus project dependencies | keep candidate. History shows iterative hardening, integrations and cleanup, not a superseded replacement. Current Debian venv path is the verified first-working operational contract; subjects remain inferred signals. |
| `/home/mak/flujo/src/flujo/__main__.py` | source; LIVE/ADOPTABLE | same shared ref family | 2026-06-28 checkpoint / 2026-06-30 `bee102e4`; 2 changes, both added | SHARED/UNKNOWN; thin `python -m flujo` module entrypoint | flujo maintainer; `python -m flujo`; local `flujo` package | keep candidate. This is a small first-working module shim, not a competing implementation; the venv contract makes it usable on Debian while system Python remains an explicitly observed contrast. |
| `/home/mak/flujo/src/flujo/autonomia.py` | consumer; LIVE/ADOPTABLE | same shared ref family | 2026-08-06 `6681a86` / 2026-08-13 `f588ecf`; 10 changes | SHARED/UNKNOWN with MAK domain signals; routes autonomy/external batches through MAK | flujo maintainer; CLI autonomy commands; `cultura.mak_plataforma` ledger/providers/tandas | keep candidate, defer execution/promotion. It is a recent first-working integration/improvisation path with durable-status and budget repairs; no evidence says superseded, but live-state behavior still needs an isolated fixture. |
| `/home/mak/flujo/tests/test_cli_smoke.py` | test; LIVE/ADOPTABLE | same shared ref family | 2026-06-28 checkpoint / 2026-07-18 `0cd8909`; 3 changes | SHARED/UNKNOWN; smoke contract for CLI/module behavior | flujo maintainer; pytest suite; pytest plus flujo package | keep candidate, defer runtime verification. History shows a test repair for `sys.modules` order dependence, not replacement. Current test contract is retained, but pytest is unavailable in this Debian environment. |

## Current contract versus historical alternatives

The evidence supports one physical current candidate set, `/home/mak/flujo`,
with the venv launcher as the verified Debian 12 consumer. The historical
branch family converges many refs and includes package bumps, repairs,
voice/RD/hub integrations, MAK autonomy work and a later three-plane branch
boundary. These are historical generations and first-working paths, not proof
that any branch is current or that a commit is a confirmed decision. The
Windows copies and `/home/mak/flujo-deploy` parallel generation remain
non-authoritative evidence; no matching tip or path was treated as a duplicate
physical tool.

## Commands and exit codes

- Required file/report reads and targeted CSV queries: exit 0.
- ODT ZIP metadata/content extraction and embedded JSON parsing: exit 0.
- Targeted full-history JSON lineage query: exit 0; no Git command was run.
- Physical `find`/`stat` check for all five paths: exit 0; all five exist.
- Prior recorded `PYTHONPATH=/home/mak/flujo/src python3 -m flujo --help`:
  exit 0.
- Prior recorded `/home/mak/venvs/flujo/bin/flujo --help` and `version`:
  exit 0.
- Prior recorded `/usr/bin/python3 -m flujo --help`: exit 1, expected
  `No module named flujo` contrast.
- Prior recorded `pytest`: exit 127 / `python3 -m pytest` exit 1 with
  `ModuleNotFoundError`; no dependency was installed.

## Uncertainty

History confidence is high for exact path lineage, dates, counts and refs;
medium for domain/purpose and lifecycle interpretation because the evidence
itself marks subjects and branch relations as inferred. The ODT says Git
cannot prove physical currentness, branch `mak` is not the MAK Linux box,
duplicate tips are ref convergence, and commit subjects are not user
decisions. `pyproject.toml` has a 28-change historical path, but its package
metadata alone cannot prove dependency installation. `autonomia.py` has a
current import contract but no isolated live-state execution. The smoke test
cannot be runtime-confirmed until pytest is available.

## Next action

Keep all five as traced LIVE/ADOPTABLE candidates with no source changes. If
integration is reopened, verify the venv package/dependency contract and run
the smoke suite in a bounded Debian fixture; separately build an isolated,
non-live-state fixture for `flujo.autonomia` before executing or promoting
autonomy behavior. Preserve Windows and parallel-generation paths as evidence.
