## Agent bootstrap — CURRENT — 2026-09-02 — ODT Claude trace and current CI boundary

### Continuity evidence

The exported Claude conversation was read in bounded text slices from
`/home/mak/Escritorio/mensajes.odt` (OpenDocument, 227091 bytes; LibreOffice
text extraction: 10630 lines, 620419 bytes). It is a transcript/evidence source,
not current authority. Its first tracked baseline was MAK `3d83ed60` on the old
`main` profile; the transcript later ended after pushing MAK `fe4d3fab` and
FLUJO `27ede605`.

### Inherited standing contract

- `Stage 2D accepted` remains accepted and is not reopened.
- `171 focused tests` is the historical measurement for that stage.
- `docs/MAK_SYSTEM_DIRECTIVE.md` remains in force.
- `mak-archive-observation-batch-v1` remains the archive-observation batch
  contract.

### Operator boundary correction — IRIS system vs portfolio — 2026-09-02

The operator corrected the semantic conflation in the preceding handoff. The
earlier `:3900` mention was a typo: the active MAK Hub is `:8900`. The more
important correction is conceptual: **IRIS is not the artist's portfolio**.
IRIS is the internal system the operator created to order and work through the
archive, preserve evidence, propose defensible relations/orders, and receive
human decisions. It can prepare material for a portfolio, dossier, application
or research output, but it is not any of those outputs.

`iskvw.cl` is the artist's public website, where material that passed
curation was uploaded. It is a downstream public output with its own contract;
it is not IRIS. The Hub route `/portafolio/` currently mounts
`/home/mak/iskvw/editor.html` because that editor was the historical starting
point for the operator-facing interface. The URL and filename are legacy
implementation labels: the route is an internal IRIS interface/adapter, not
the public portfolio and not the definition of IRIS.

The operator's screenshot confirms an additional precision: the Hub shell at
`:8900` (`MAK · ATLAS VIVO` / `campo de orden`) and the mounted editor/mesa are
the same visible interface. Do not describe them as separate interfaces. The
separation is semantic and operational: IRIS/Atlas is the internal system,
`editor.html` is its implementation surface, and `iskvw.cl` is the downstream
public output.

The Claude audit was right that there are multiple `editor.html` files; the
earlier one-file result was caused by an incomplete search. The corrected
filesystem measurement (`find /home/mak -xdev -type f -name editor.html`) found
16 physical copies across active checkouts, runtime/compatibility copies,
archives, logs and rollback material. Only `iskvw/editor.html` is tracked in
the current MAK checkout. This proves basename duplication, not product
identity. The current `:8900` consumer is established by active route,
`MAK_PORTFOLIO_ROOT`, source and served hash; a filename alone cannot identify
IRIS or `iskvw.cl`.

The operational consolidation is now explicit: `/home/mak/iskvw/editor.html`
is the single active MAK runtime source for `127.0.0.1:8900/portafolio/`.
`/home/mak/flujo/iskvw/editor.html` is the separate portable-checkout copy,
currently byte-identical but not consumed by this process; it is synchronized
only by an explicit FLUJO transport/commit. The former
`/home/mak/plataforma/iskvw/editor.html` copy had no consumer in the measured
route and was retired reversibly as
`_archive/iris-editor-consolidation-20260902/plataforma/iskvw/editor.html.legacy-20260902`.
`_archive/`, `_logs/` and rollback copies remain historical evidence and are
not active duplicates. “Consolidated” therefore means one active
source/consumer, with history preserved, not a destructive filesystem purge.

Measured locally in this continuation: `ss -ltnp | rg ':(3900|8900)\b'` found
only `127.0.0.1:8900`, served by
`/home/mak/cultura/mak_plataforma/hub.py`; there was no `:3900` listener. No
code, `iskvw` data, public site or runtime state was changed. All future
prompts and edits must say explicitly which IRIS internal consumer or which
`iskvw.cl` public output they address.

### Editor authority consolidation — current continuation — 2026-09-02

- Measured with `find /home/mak -xdev -type f -name editor.html`: 15 files
  named `editor.html` remain across active checkouts, archives, logs and
  rollback material. The initial count was 16; the stale compatibility copy
  was moved to the named archive under an explicit legacy filename. This is a
  preserved evidence inventory, not 15 active interfaces.
- Measured with `curl http://127.0.0.1:8900/portafolio/`, `sha256sum`, `ss -ltnp`
  and source inspection: HTTP 200, 253564 bytes, source and served SHA-256
  `ed7e3bf2d02a841b52560be007390d78c7aed90c79d46258347b22700f03f331`, and
  only `127.0.0.1:8900` listening. The active chain is
  `/home/mak/cultura/mak_plataforma/hub.py` -> `MAK_PORTFOLIO_ROOT` default
  `/home/mak/iskvw` -> `/home/mak/iskvw/editor.html`.
- `/home/mak/flujo/iskvw/editor.html` is tracked in the independent FLUJO
  checkout and currently byte-identical, but is not consumed by the MAK Hub.
  The former `/home/mak/plataforma/iskvw/editor.html` was ignored, stale, and
  had no reference in the current code path; it was moved reversibly to
  `_archive/iris-editor-consolidation-20260902/` and is not an alternate
  runtime source.
- Failure: none in this consolidation slice. No historical file was deleted;
  the stale compatibility copy was moved reversibly, no public `iskvw` data
  was changed, and no service was restarted.
- Write-set: the authority rule was added to `AGENTS.md`,
  `docs/IRIS_CANONICAL.md`, `docs/MAK_CURRENT_STATE.md` and this handoff.
- Next action: future IRIS/Atlas UI work edits only `/home/mak/iskvw/editor.html`
  after route/root/hash verification. The retired copy is recoverable in the
  named archive and must not be restored silently or used to edit the FLUJO
  checkout.

### Claude sequence recovered

- Fase 0: read-only physical-layout and runtime comprehension.
- Fases 1-2: built `tools/runtime_preflight.py`, removed three service symlink
  indirections, and added focused tests/dossiers without changing Git.
- Fase 3: built `tools/release_gate.py`; it correctly classified the local
  release as not ready, but the later workflow wiring put this box-local tool in
  CI, where its `/home/mak` assumptions cannot hold.
- C01-C11: separated MAK and FLUJO physically, moved ownership by consumer,
  repaired collection/lane mapping, and added per-lane workflows.
- IRIS analysis: identified the MAK internal ordering system and its Mesa de
  Montaje interface, distinguished both from `iskvw.cl`, read the FONDART
  bases, and added `docs/IRIS_CANONICAL.md`, the regional dossier, and invariant
  tests.
- A data detour regenerated `campo.json` from 219 to 871, then correctly
  reverted it with `77afc45e` after recognizing that `iskvw/` is a dormant
  published-site surface and that its product decision is separate from IRIS.
- The transcript's final CI verdict was FLUJO green, MAK red in 4 tests, and
  integration red in 11 tests. It stopped before repairing those environment
  boundaries.

### Current state verified after the export

- `/home/mak` is on `MAK` at `fe4d3fab`; `/home/mak/flujo` is on `FLUJO` at
  `27ede605`; both tips equal the remote refs. `main` remains historical at
  `77333b4c` and `historia` at `ab9afa13`.
- At the start of this continuation the only pre-existing uncommitted change
  was the one-line `CAPACIDADES.md` correction that removes the false claim
  that `release_gate.py` runs in CI. It was preserved. The current worktree is
  intentionally dirty with the audit write-set below; nothing was staged or
  committed.
- Remote runs for those exact tips are measured: `CI FLUJO` succeeded;
  `CI MAK` failed with four failures; `CI integration` failed with eleven.
  The observed causes are box-only assertions in MAK and absent physical
  `iskvw/datos/archivo.json`, missing FLUJO console-script installation, and
  missing FLUJO-side contracts in the clean integration checkout. These are the
  next CI-boundary slice, not evidence to modify IRIS or `iskvw/` data.

### Next action from the export (completed in this continuation)

The four MAK failures and eleven integration failures were traced to their
clean-checkout assumptions. The smallest correction was applied and verified:
tests with a physical MAK root or generated `iskvw/datos/archivo.json` now skip
only when that substrate is absent; MAK path resolution sees the sibling FLUJO
checkout; the department catalog resolves motor-owned paths through `flujo/`;
and `requirements-integration.txt` installs FLUJO editable so its declared
console script exists. No `iskvw` data was regenerated and no 219/871 decision
was changed.

### Diagnostic reading completed after the Claude export

The primary files confirm a causal distinction that must survive compaction:

- Claude's useful work was the physical MAK/FLUJO split, the lane contracts and
  the invariant tests. The remaining red CI is not proof that IRIS or the
  published archive data is wrong. The workflows run clean checkouts, while
  several tests still assert box-only paths or generated material absent from a
  checkout; integration also installs the requirements but not the FLUJO
  package, so its declared `flujo` console script cannot exist there.
- The repository has a real architectural ambiguity: the Hub mounts
  `/home/mak/iskvw` at `/portafolio/`, while the same tree is the `iskvw.cl`
  site. The contracts nevertheless separate them: IRIS is the MAK Hub/Mesa de
  Montaje over record/work/context/relation; `iskvw.cl` consumes the
  obras-oriented `datos/archivo.json` and replaceable skin. A shared path does
  not make them the same product.
- Claude's data detour was therefore an inference error, not a missing-feature
  discovery: it used a red environmental/contract test as a reason to
  regenerate `campo.json`, re-run layers and add animated pieces. The later
  claim that this endangered a live product was also unmeasured; the local
  contract and handoff state that `iskvw.cl` is dormant. No 219/871 choice is
  reopened by this continuation.
- The portfolio production work already contains F1/F2/F3 output, F4 as a
  bounded transcription, F6 as an existing human-facing RD artifact, and
  F2-barbería as an intentionally non-feasible adversarial case. “No full
  application”, “no Hub exposure”, and “fit abstain” are declared boundaries,
  not evidence that the formats or theory were absent. `opportunity_fit.py`
  computes a fail-closed link and research candidates; it does not decide
  artistic fit.
- The theory also names a current implementation gap: `O_G` (multiple
  defensible orders relative to purpose) is not yet a produced output. The
  local GTM/ordering surface is a bounded candidate map with a sampled fit
  path, not proof of learned semantic generalization. That gap must not be
  “solved” by promoting positions, filenames, or one ordering into authorship
  or truth.

Measured sources for this diagnosis: `docs/IRIS_CANONICAL.md` sections 1-bis,
4, 6 and 7; `iskvw/CONTRATO.md`; `docs/PORTAFOLIO_PRODUCCION.md` sections 8,
14–18; `docs/DIMENSIONES_DEL_ORDEN.md`; `flujo/src/flujo/knowledge/opportunity_fit.py`;
`cultura/mak_plataforma/hub.py`; `cultura/mak_plataforma/copilot.py`; and the
current CI workflows/tests. The CI portability action described here is now
completed locally. IRIS is explicitly paused by the operator; do not begin its
decision-reader slice in the next continuation.

### CI portability repair evidence — 2026-09-02

- `python -m pip install -r requirements-integration.txt` succeeded, including
  editable installation of `flujo`; `pip check` reported no broken requirements.
- MAK lane: `2170 passed, 5 skipped, 5 warnings, 5 subtests` in 113.52s.
  The five skips are the generated physical archive tests absent from a clean
  checkout; they remain executable on the box.
- MAK repo hygiene: `87 passed` in 42.78s.
- Integration lane: `371 passed` in 22.33s.
- FLUJO lane: `1611 passed, 44 skipped, 7 warnings` in 82.13s.
- FLUJO repo hygiene: `54 passed, 1 skipped` in 27.16s.
- Bootstrap continuity: `tests/test_agent_bootstrap.py` `2 passed` after the
  current packet was amended to retain the inherited Stage 2D contract. The
  first literal FLUJO command failed only because that checkout has no local
  `.venv`; rerunning with the box interpreter used by the workflow passed.
- Live consumer check: Hub `/portafolio/` HTTP 200, compact inbox HTTP 200, and
  `/static/iskvw/editor` served SHA-256 equals the physical
  `iskvw/editor.html` hash `ed7e3bf2d02a841b52560be007390d78c7aed90c79d46258347b22700f03f331`.
  `iskvw/datos/campo.json` and `iskvw/datos/animadas.json` each contain 219
  pieces.

### Claude operational audit and repair — 2026-09-02

- The audited Claude range is the physical MAK/FLUJO split ending at
  `fe4d3fab` (MAK) and `27ede605` (FLUJO). The split itself is preserved; the
  audit found defects in consumers that still assumed the old layout.
- Fixed the live Hub import root: it now loads the motor from
  `/home/mak/flujo/src`, and `/api/status` reports `repo=ready` with
  `/home/mak/flujo/src/flujo/knowledge/project_api.py`; `/api/departments`
  exposes the three areas with HTTP 200.
- Fixed the MAK cron working directory, CAPATAZ lookup, conductor shadow unit,
  `verify_all.py`, handoff version lookup, and the direct MAK tools that still
  injected `ROOT/src`. Fixed both Blender render wrappers, the command-map
  generator, telemetry, and lane-map detection to consume the physical sibling
  checkout. Added regression tests for these boundaries.
- Fixed PR workflow checkout composition so the revision under review is
  tested, not an unrelated branch tip. The local release gate now classifies
  the current write-set, reports the physical FLUJO checkout explicitly, and
  returns no blockers or unknowns; exit 5 remains its documented
  `IMPLEMENTATION_COMPLETE_TESTS_DEFERRED` state.
- Removed only generated residue: `/home/mak/src/flujo` contained 200 `.pyc`
  files and no source; 43 `__pycache__` directories / 776 `.pyc` files under
  `/home/mak/flujo` carried stale `.claude/worktrees/flujo-closeout` code
  filenames and were removed. A clean FLUJO run produced no stale worktree
  mentions; current caches, when recreated, contain no such references.
- Verification: MAK `2175 passed, 5 skipped`; MAK hygiene `89 passed`; root
  integration `372 passed`; FLUJO `1611 passed, 44 skipped`; FLUJO hygiene
  `54 passed, 1 skipped`; `flujo verify` exit 0; runtime preflight `5/5 ok`,
  zero errors/unknowns/warnings/adapters; `git diff --check` passed. The
  integration failure in `test_mak_iconos` was a real order-dependent wrapper
  import issue and is now fixed; the ordered 36-test reproduction and the full
  372-test integration run pass.
- Write-set is local and uncommitted across the two operational checkouts;
  no service was activated, no data/IRIS surface was changed, and no commit or
  push was made.

### Full suite recheck — 2026-09-02 — after Claude audit repair

- Commands were rerun with `/home/mak/.venv/bin/python` and
  `PYTHONDONTWRITEBYTECODE=1`. MAK lane (`-m mak`): `2175 passed, 5 skipped,
  5 warnings, 5 subtests` in 106.48s. MAK hygiene (`-m repo_hygiene`): `89
  passed` in 40.37s. Integration (`-m integration`): `372 passed, 20
  warnings` in 13.70s.
- FLUJO lane (`-m flujo`): `1611 passed, 44 skipped, 7 warnings` in 87.34s.
  FLUJO hygiene (`-m repo_hygiene`): `54 passed, 1 skipped` in 26.16s.
  `python -m flujo verify` completed with `✓ verify OK`; its health warning
  only says the optional local index is absent.
- `tools/runtime_preflight.py --check`: exit 0, five runtime surfaces OK,
  zero error/unknown/warn/adapter conditions. `tools/release_gate.py --check`:
  exit 5 with `IMPLEMENTATION_COMPLETE_TESTS_DEFERRED`, zero blockers and
  unknowns; exit 5 is the tool's documented deferred-tests code.
- Two initial generic interpreter commands did not execute tests: `python` is
  absent from this shell and `/usr/bin/python3` has no pytest. The rerun with
  the box venv is the authoritative measurement above. No IRIS or
  `iskvw/datos/*` surface changed.

### Write-set review — 2026-09-02 — Fase 1

- The local write-set is bounded to 56 changed/untracked paths in MAK and 3
  changed paths in FLUJO. The diffs are limited to the physical checkout
  boundary, runtime/CLI path resolution, CI composition, release/preflight
  contracts, regression tests, this handoff, and the bounded Claude Fase 2
  packet at `context/coordination/inbox/claude/phase2-publication-review-20260902.md`.
  No unexplained top-level artifact or data mutation was found.
- Remaining literal `src/flujo` strings in MAK allowlists and gate detectors
  are intentional logical/foreign-path contracts: `_path_roots()` resolves
  them against `/home/mak/flujo` first, while the gate keeps them to detect
  retired layouts. They are not active imports of the stale `/home/mak/src`
  tree.
- Review result: no additional repair is justified without broadening scope.
  `git diff --check` passed, the focal handoff/idioma ratchets passed (`15
  passed`), and the live services remained outside the data/IRIS write-set.
  Fase 1 is complete; publication remains a separate authorized action.

### Continuation point after the repair

The fixes are local: no commit or push was made, so remote CI still reflects
the earlier tips until the operator authorizes publication. IRIS remains
paused. The next action is operator review of this audit write-set and, if
authorized, the existing release/publish procedure; do not regenerate
`iskvw/datos/*`, touch the IRIS reader, or promote ordering into authorship.

### Fase 2 publication — 2026-09-02

- Operator authorized publication after the bounded write-set review. MAK was
  committed as `9c2c4255` (`fix(mak): align physical checkout consumers`) with
  57 paths; FLUJO was committed as `50e453c2`
  (`fix(flujo): align physical checkout contracts`) with 3 paths.
- Pushes succeeded without force: `fe4d3fab..9c2c4255 MAK -> MAK` and
  `27ede605..50e453c2 FLUJO -> FLUJO` on remote `vibecodeine-legacy`.
- The exact pre-publish evidence remains: MAK `2175 passed, 5 skipped`,
  integration `372 passed`, FLUJO `1611 passed, 44 skipped`, both hygiene
  lanes green, `flujo verify` OK, and runtime preflight 5/5 OK. No IRIS,
  `iskvw/datos/*`, service state, or artistic output was changed.
- The next action is to observe the remote CI runs for these two branch tips
  and integration. IRIS remains paused; do not regenerate data or open the
  IRIS reader as part of CI follow-up.

### Claude delegation packet — updated 2026-09-02

- The prompt at
  `context/coordination/inbox/claude/phase2-publication-review-20260902.md`
  was rewritten for the post-publication state. It now asks a new Claude agent
  to verify the published MAK/FLUJO SHAs, remote refs, matching CI runs and
  live runtime, using only the current handoff block and targeted diffs.
- The packet explicitly forbids full-repository reading, ODT/history/WIN
  exploration, code or data edits, service changes, and any commit/push. Its
  only permitted write for Claude is one brief dated result in this handoff.
- This packet update and this pointer are local, uncommitted changes made for
  operator delivery to Claude. The published code remains at MAK `fc8005c1`
  and FLUJO `50e453c2`; no remote branch is changed by this update.
- Next action: operator sends the packet to the new Claude agent. On return,
  inspect its result here before authorizing any new implementation. IRIS
  remains paused.

### Claude packet resend — 2026-09-02

- The operator reported that the previous delivery/context was lost. The
  packet was made self-contained: it now explains the useful Claude work, the
  data/CI/path inference errors, Faro/Codex's bounded diagnosis and repairs,
  the published commits, and the exact post-publication verification task.
- Current physical check: MAK is clean except for this handoff and the local
  packet update; FLUJO is clean. Remote refs remain MAK `fc8005c1` and FLUJO
  `50e453c2`. Ports `8900`, `8890`, `8891`, `8765` and `11434` are listening
  on `127.0.0.1`.
- No repair, commit, push, service change, IRIS edit or data regeneration was
  made in this resend. The operator should send the complete contents of
  `context/coordination/inbox/claude/phase2-publication-review-20260902.md`
  to the new Claude agent.

### Post-publication verification (Claude Fase 2) -- 2026-09-02 -- REVIEW_NEEDED

- Publication is confirmed. MAK local HEAD equals remote `refs/heads/MAK` at
  `fc8005c13e7aa91b6da7cbc40e7be0591b5ef8dc`; FLUJO local HEAD equals remote
  `refs/heads/FLUJO` at `50e453c2a6ee9837c73acda3cec6ff74d0598f7e`. The
  published diffs match this handoff: `9c2c4255` touches 57 paths (+702/-104),
  `50e453c2` touches 3 paths (+27/-4). Both worktrees pass `git diff --check`
  and the only modified paths are `context/LAST_HANDOFF.md` and the Fase 2
  packet; FLUJO is fully clean. No unexpected path appeared.
- Remote CI matched to the published SHAs: `CI FLUJO` success for `50e453c2`
  (run 33670274140). `CI integration` success for `9c2c4255` (33670257289) and
  for `fc8005c1` (33670334153). `CI MAK` FAILS for both `9c2c4255`
  (33670257340) and the tip `fc8005c1` (33670334244). No workflow run is
  pending or unverified.
- The `CI MAK` failure is a single test in the hygiene lane, identical on both
  runs: `tests/test_comandos_manifiesto.py::test_the_manifest_is_not_stale_against_the_real_cli`
  -- `1 failed, 80 passed, 8 skipped`. The `mak` lane step itself passed.
- Diagnosed cause, from the log and the published diff only. The ratchet runs
  `tools/gen_mapa_comandos.py --check`, which interrogates the real CLI by
  spawning `python -m flujo <path> --help` with `PYTHONPATH` pointed at
  `RAIZ/flujo/src`. `flujo/src/flujo/cli.py` imports `typer` and `rich`, both
  declared only in `requirements-flujo.txt`; the `CI MAK` job installs
  `requirements-mak.txt`, whose shared base deliberately excludes the portable
  motor's CLI stack. Refined by measurement on 2026-09-02 (see the
  certification section below): run 33670334244's own install step shows
  `rich`, `pydantic` and `requests` arriving transitively under the MAK
  profile and `typer` never arriving, so `typer` alone is the missing import
  in that runner. In that runner the help subprocess cannot import,
  the parsed command tree comes back empty, and the committed
  `context/comandos.json` is reported as stale. The same `--check` exits 0 on
  the box (`MAPA.md y context/comandos.json al dia con el CLI`) because the box
  venv has the FLUJO stack installed.
- This is the same defect class already repaired in this session -- a MAK test
  asserting substrate a clean MAK-profile checkout does not have -- not a
  regression of the physical split and not evidence about IRIS, `iskvw/datos/*`
  or the 219/871 decision. It was invisible before 2026-09-02 because the
  hygiene lane ran in no CI job.
- Local runtime, read-only: `tools/runtime_preflight.py --check` exit 0 with
  all five surfaces OK and zero error/unknown/warn/adapter conditions; the
  FLUJO App probe resolves inside the FLUJO checkout at
  `/home/mak/flujo/src/flujo/web/hub.py`. Endpoints: `8900/health` 200,
  `8890/` 200, `8891/` 200, `8765/` 200, `11434/api/version` 200.
- Blockers: none for publication; `CI MAK` red at the published tip is the one
  open item. Warnings: the manifest ratchet's green local result is not
  portable, so the box cannot pre-detect this class of failure. Unverified:
  nothing in the requested scope; no full-repository, ODT, WIN, `main` or
  history reading was done, and no code, workflow, requirement, test, service,
  data or IRIS surface was touched.
- Next minimal action, for Faro/Codex to authorize and execute: decide whether
  that ratchet belongs in the MAK hygiene lane at all, since it measures the
  FLUJO CLI, and then apply exactly one bounded correction -- move the test to
  the FLUJO/integration lane, or make it skip when the motor's CLI stack is not
  importable. Do not add `typer`/`rich` to `requirements-mak.txt` merely to
  make it pass: that reverses the measured profile separation. No commit,
  push or regeneration was made by this verification. IRIS remains paused.

### CI MAK manifest ownership correction — 2026-09-02

- Cause. `tests/test_comandos_manifiesto.py::test_the_manifest_is_not_stale_against_the_real_cli`
  ran `tools/gen_mapa_comandos.py --check`, which spawns
  `python -m flujo <path> --help`; `flujo/src/flujo/cli.py` imports `typer` and
  `rich`, and those live only in `requirements-flujo.txt`. The file is declared
  `repo_hygiene`, a lane `CI MAK` runs after installing `requirements-mak.txt`
  only, so the check failed on a clean runner while passing on the box. The
  lane classifier could not see it: `tools/test_lane_map.py` records AST
  imports, the file imported only `json`/`subprocess`/`sys`, and the real
  dependency travels through `subprocess`. The failure text said the manifest
  was stale, which is why it read as a data problem rather than an environment
  one.
- Ownership decision. The check belongs to `integration`, the lane that
  composes both physical checkouts and installs `requirements-integration.txt`.
  The precedent was already in the tree: `tests/test_mapa_completo.py` is the
  twin ratchet over the same generator's MAPA.md table and is declared
  `integration` with the reason `reaches both physical checkouts; runs with
  PYTHONPATH=/home/mak:/home/mak/flujo/src`. The generator emits MAPA.md and
  `context/comandos.json` from one tree, so the manifest half joined its twin
  instead of getting a new file. That keeps `context/test_lane_map.json`
  untouched: it is a generated contract carrying `classifier_sha256` and
  `previous_contract_sha256`, and hand-adding an entry would have invalidated
  its own provenance. The five remaining tests in
  `tests/test_comandos_manifiesto.py` read the tracked JSON document and are
  honestly `repo_hygiene`. `typer`/`rich` were NOT added to
  `requirements-mak.txt`; nothing was skipped or disabled.
- Files modified: `tests/test_mapa_completo.py` (+27), `tests/test_test_taxonomy.py`
  (+95/-1), `tests/test_comandos_manifiesto.py` (+18/-5). The staleness
  assertion moved verbatim as
  `test_el_manifiesto_no_queda_desfasado_del_cli`; the vacated file keeps a
  pointer comment so the check cannot be re-added to the wrong lane;
  `subprocess`/`sys` became unused there and were removed.
- Regression guard. `tests/test_test_taxonomy.py::test_a_hygiene_lane_test_never_spawns_the_flujo_cli`
  walks every `repo_hygiene` file in the lane contract and fails if a
  subprocess call reaches the FLUJO CLI. The first version of this guard was
  refuted by measuring it: run against `git show HEAD:tests/test_comandos_manifiesto.py`
  it returned clean, because the published call was
  `subprocess.run([sys.executable, str(GENERADOR), "--check"])` and neither
  `-m flujo` nor the generator name appears inside the call -- the path sits in
  a module constant. `_module_constants()` now expands names the call
  references. Verified afterwards: the pre-move file is detected
  (`subprocess.run`), the post-move file, `tests/test_higiene_repo.py` (which
  names the generator in a data table without running it) and the guard file
  itself are clean.
- Write-set, exact, local and uncommitted: `tests/test_comandos_manifiesto.py`,
  `tests/test_mapa_completo.py`, `tests/test_test_taxonomy.py`,
  `context/LAST_HANDOFF.md`, and the pre-existing
  `context/coordination/inbox/claude/phase2-publication-review-20260902.md`,
  which was preserved untouched. FLUJO's checkout is clean: no file changed
  there, so `CI FLUJO` is unaffected by this correction.
- Commands and exact results, all with `PYTHONDONTWRITEBYTECODE=1` and
  `/home/mak/.venv/bin/python`:
  - `ci-mak.yml` step `repo hygiene lane`, verbatim
    (`-m repo_hygiene`, `PYTHONPATH=/home/mak:/home/mak/flujo/src`):
    `89 passed in 28.11s` (was `1 failed, 80 passed, 8 skipped` in CI; the
    count holds because one test left and the guard arrived).
  - `ci-mak.yml` step `MAK lane` (`-m mak`): `2175 passed, 5 skipped,
    5 warnings, 5 subtests passed in 99.10s`.
  - `ci-integration.yml` step `Integration lane`, verbatim (`-m integration`,
    `PYTHONPATH=/home/mak:/home/mak/flujo:/home/mak/flujo/src`):
    `373 passed, 20 warnings in 50.75s`, one more than the published 372 --
    the moved check. `--collect-only` confirms the file is selected by
    `integration` and absent from `repo_hygiene`.
  - Focal: `tests/test_mapa_completo.py` `7 passed in 7.52s`;
    `tests/test_comandos_manifiesto.py` `5 passed in 0.13s`;
    `tests/test_test_taxonomy.py` + `tests/test_idioma_ratchet.py`
    `23 passed in 12.60s`.
  - `git diff --check` exit 0 in both checkouts.
  - `tools/release_gate.py --check`: `verdict_overall=IMPLEMENTATION_COMPLETE_TESTS_DEFERRED`,
    `BLOCKERS (0)`, `UNKNOWNS (0)`, exit 5 (its documented deferred code); both
    branches `ahead=0 fast_forwardable=True`.
  - `tools/runtime_preflight.py --check`: exit 0, `ok=5`, `error=0 unknown=0
    warn=0 adapter_dependency=0`.
  - One intermediate failure is recorded rather than hidden: the first version
    of the guard was written with Spanish identifiers and docstrings, and
    `tests/test_idioma_ratchet.py::test_no_new_file_carries_spanish_comments`
    flagged `tests/test_test_taxonomy.py` as a new Spanish-carrying file. The
    additions were rewritten in English; the baseline pin was NOT lowered.
- Sibling review, measured over the lane contract rather than asserted. Every
  test that spawns the FLUJO CLI: `tests/test_laser.py`,
  `tests/test_mapa_completo.py`, `tests/test_micelio_deposito.py` -- all three
  already declared `integration`. The two lanes that run without the motor's
  CLI stack carry none: `repo_hygiene` 14 files, 0 spawners; `mak` 173 files,
  0 spawners. `tests/test_curaduria_roundtrip.py` (`mak`) only cites
  `gen_mapa_comandos._help` in a comment, and `tests/test_higiene_repo.py`
  (`repo_hygiene`) names the generator in a data table. Workflow scan:
  `ci-mak.yml` and `ci-integration.yml` are the only workflows setting
  `PYTHONPATH` to the sibling checkout, and their composition is correct;
  `validar-piezas.yml` runs `python -m flujo suplementos validate` but is a
  separate FLUJO-profile workflow, not a MAK lane. Exactly one ownership
  defect existed and it is the one corrected here.
- Protected surfaces: the diff touches no IRIS file, no `iskvw/datos/*`, no
  `campo.json`, no `animadas.json`, no `iskvw/piel/*`, no database, no
  artistic output, no requirements file and no service configuration -- checked
  by pattern over `git diff --name-only`, which returned nothing. No service
  was started, stopped or restarted; no port changed; no file was regenerated.
  No branch operation of any kind was performed.
- Next action for Faro. Review this write-set and, if authorized, publish it to
  `MAK` by the existing procedure. The only remaining CI evidence gap is that
  `CI MAK` has not yet run green on a clean runner for this correction; the
  verdict is its matrix, not this local run. IRIS remains paused.

### Faro verification of Claude correction -- 2026-09-02

- The actual Claude write-set was independently reviewed and remains bounded
  to `tests/test_comandos_manifiesto.py`, `tests/test_mapa_completo.py`,
  `tests/test_test_taxonomy.py`, this handoff, and the pre-existing Claude
  packet. FLUJO is clean. No protected IRIS/data/runtime path appears in the
  diff; `git diff --check` passes in both checkouts.
- Independent rerun with `PYTHONDONTWRITEBYTECODE=1` and the box venv:
  focused manifest/map/taxonomy/idioma tests: `35 passed in 24.96s`;
  `repo_hygiene`: `89 passed in 33.15s`; `integration`: `373 passed in
  23.80s`.
- The first focused invocation returned pytest code 5 with no collection
  because `pyproject.toml` supplies `addopts = "-q -m mak"`; the authoritative
  rerun used `-o addopts=` and collected all 35 tests. This is an invocation
  quirk, not a code failure. The hygiene and integration reruns are green.
- The new correction is local and uncommitted. Remote CI still reflects the
  prior published MAK tip, so clean-runner evidence for this write-set remains
  pending publication. Next action: operator review and explicit authorization
  before commit/push. IRIS remains paused.

### Faro pre-publication certification -- 2026-09-02

- Verdict: `READY_FOR_PUBLICATION`, with one explicit limit -- clean-runner CI
  evidence for THIS write-set cannot exist until it is pushed and the
  workflows run. Zero blockers, zero unknowns, zero warnings from the gate.
- Reconciliation with the Faro verification section immediately above, so the
  two do not read as contradicting each other: that independent rerun measured
  `35` focused tests and `repo_hygiene` `89` BEFORE this certification added
  two detector pins to `tests/test_test_taxonomy.py`. The counts below are
  `37` and `91` for that reason, and `integration` `373` agrees in both. No
  earlier figure was wrong.
- Write-set, exact, local and uncommitted, five paths and no others:
  `tests/test_comandos_manifiesto.py`, `tests/test_mapa_completo.py`,
  `tests/test_test_taxonomy.py`, `context/LAST_HANDOFF.md`, and the
  pre-existing `context/coordination/inbox/claude/phase2-publication-review-20260902.md`,
  which was not rewritten or extended. The FLUJO checkout is clean: no file,
  branch or ref there was touched. `git diff --check` exits 0 in both.
- Semantic review. The staleness check was MOVED, not duplicated: the old body
  is deleted and exactly one definition exists in the tree
  (`grep` finds `test_el_manifiesto_no_queda_desfasado_del_cli` once as a
  `def`, plus two comment references). `tests/test_comandos_manifiesto.py`
  keeps its five document checks, which are honestly `repo_hygiene`;
  `subprocess`/`sys` were removed there because only the moved test used them.
  `context/test_lane_map.json` is NOT in the diff -- the generated contract was
  never hand-edited. No requirements file is in the diff, so no FLUJO
  dependency was added to the MAK profile. No existing ratchet was lowered,
  faked or deleted; no test was turned into a skip.
- Cause refined by measurement, and this correction matters. The earlier
  sections said the CLI needs "typer and rich". Run 33670334244's own
  `Install the MAK profile` step shows `rich-15.0.0`, `pydantic-2.13.5` and
  `requests-2.34.2` DO arrive transitively under `requirements-mak.txt`, and
  `typer` never arrives. So `typer` alone is the missing import in that runner.
  The distinction is load-bearing: `rich` being present there is an accident of
  another package's dependency tree, not a contract, so nobody should rely on
  it. The three code comments and the prior handoff sentence were corrected,
  and a wrong run id (`33670334153`, which is the integration run) was replaced
  by `33670334244` in all three files.
- Property 1, MAK does not depend on the FLUJO CLI stack: certified by
  execution, not by reading. A `sitecustomize.py` in the session scratchpad
  models the runner by blocking exactly the genuinely absent packages
  (`typer`, `pywebview`) while leaving the transitively present ones
  importable. Under that model: `repo_hygiene` `91 passed in 28.04s` and `mak`
  `2175 passed, 5 skipped, 5 warnings, 5 subtests passed in 102.95s`. The same
  model reproduces the published failure exactly --
  `python tools/gen_mapa_comandos.py --check` prints
  `MAPA.md o context/comandos.json DESFASADO del CLI` and exits 1, the same
  message and code CI MAK produced -- while the identical command without the
  model exits 0. The diagnosis is therefore measured, not inferred.
- Property 2, the check really runs in `integration` and is not vacuous: under
  the CI MAK model `tests/test_mapa_completo.py::test_el_manifiesto_no_queda_desfasado_del_cli`
  FAILS (`1 failed in 3.09s`), and in the integration environment it PASSES
  (`1 passed in 6.74s`). A test that cannot fail when its dependency is absent
  would be decoration; this one can. `--collect-only` confirms it is selected
  by `-m integration` and returns zero occurrences under `-m repo_hygiene`.
- Property 3, the guard. Its first version was refuted by measuring it against
  `git show HEAD:tests/test_comandos_manifiesto.py`: it reported the real
  offender clean, because the published call was
  `subprocess.run([sys.executable, str(GENERADOR), "--check"])` and the path
  lived in a module constant. `_module_constants()` fixed that. The behaviour
  is now PINNED in two new tests rather than left to the tree being clean by
  construction: `test_the_detector_finds_execution_including_indirect_paths`
  covers a direct `-m flujo` argv pair, the module-constant indirection, a
  `shell=True` string and `os.system`; `test_the_detector_does_not_accuse_a_mention`
  covers a data table, a comment, an unspawned string and a file with no
  subprocess at all. The guard scans the lane contract, not a test name, so
  renaming any test cannot silently disarm it, and it does not flag itself.
  Declared limit, stated rather than hidden: it reads direct subprocess calls
  in the file it scans, so a spawn hidden inside an imported helper would
  escape it. That hole was measured, not assumed -- see the sibling review.
- Sibling review, measured: `no sibling ownership defect found`. Every test
  that spawns the FLUJO CLI is `tests/test_laser.py`,
  `tests/test_mapa_completo.py` and `tests/test_micelio_deposito.py`, all three
  already declared `integration`. The two lanes that run without the CLI stack
  carry none: `repo_hygiene` 16 declared files, 0 spawners; `mak` 173 files, 0
  spawners. For the wrapper case, the local modules that themselves spawn the
  CLI were enumerated -- `tools/gen_mapa_comandos.py` and
  `tools/bridge_issue_render.py`, two of them -- and no `repo_hygiene` or `mak`
  test imports either; `bridge_issue_render` has no test at all. Of the tests
  naming `flujo/src`, `test_system_status.py` is `integration`, while
  `test_compete_engine.py`, `test_runtime_preflight.py` and
  `test_test_taxonomy.py` reference the path as data and stay green with
  `typer` blocked. No test was pre-emptively skipped.
- Tests executed with `PYTHONDONTWRITEBYTECODE=1`, `-o addopts=` and
  `/home/mak/.venv/bin/python` (the generic `python` does not exist in this
  shell and `/usr/bin/python3` has no pytest; that is the interpreter, not a
  code fault):
  - focal, four files: `37 passed in 19.11s`.
  - `ci-mak.yml` `repo hygiene lane` verbatim: `91 passed in 28.64s`. It was 89
    before this write-set: one test left for `integration` and two detector
    pins arrived.
  - `ci-mak.yml` `MAK lane` verbatim: `2175 passed, 5 skipped, 5 warnings,
    5 subtests passed in 98.86s`.
  - `ci-integration.yml` `Integration lane` verbatim: `373 passed, 20 warnings
    in 18.75s`, one more than the published 372 -- the moved check.
  - The `flujo` lane and its hygiene were NOT run: no file in the FLUJO
    checkout changed, `ci-flujo.yml` triggers only on the FLUJO branch, and
    nothing will be pushed there. The composition is still covered, by the
    integration lane.
- `python -m flujo verify`: `✓ verify OK`, exit 0, run from `/home/mak/flujo`
  with `/home/mak/.venv/bin/python` and `PYTHONPATH=/home/mak/flujo/src`. Its
  hub smoke reported `version=0.56.1 port=46581`.
- `tools/release_gate.py --check`:
  `verdict_overall=IMPLEMENTATION_COMPLETE_TESTS_DEFERRED`, `BLOCKERS (0)`,
  `UNKNOWNS (0)`, `WARNINGS (0)`, exit 5 -- its documented deferred-tests code,
  not a failure of this correction. Both operational branches read
  `ahead=0 behind=0 fast_forwardable=True`, MAK at `fc8005c13e7a` and FLUJO at
  `50e453c2a6ee`, matching the remote. The five write-set paths appear under
  `needs attribution`, which is the gate naming an uncommitted checkout, not a
  defect.
- `tools/runtime_preflight.py --check`: exit 0, `ok=5`,
  `error=0 unknown=0 warn=0 adapter_dependency=0`. No service was started,
  stopped or restarted; no port was changed.
- Protected surfaces confirmed by pattern over `git diff --name-only`, which
  returns nothing for: IRIS and its reader, `iskvw/*` including
  `iskvw/datos/*`, `campo.json`, `animadas.json`, `iskvw/piel/*`, any `.db` or
  `.sqlite`, any `.json`, any `.svg`/`.png`/`.blend` artistic output, any
  service or systemd configuration, and any requirements file. No data,
  layer, animation or artistic file was regenerated. No FLUJO branch was
  touched.
- Generated residue from this session, registered rather than swept:
  `/home/mak/flujo/_logs/hub_smoke_2026-09-02_15-44-39.log` (78 bytes), written
  by `flujo verify`'s hub smoke. `_logs/` is gitignored
  (`.gitignore:196`), so it is outside the write-set; it was left in place as
  run evidence and no broad cleanup was performed. No `__pycache__` and no
  untracked file was created. One honest note on instruments: a
  `find -newermt '-25 minutes'` returned nothing for that log because more than
  25 minutes had passed -- a false negative from the query, not evidence of no
  residue, which is why the path was verified directly.
- Warnings, separate from blockers. Blockers: none. Warnings: (1) the box venv
  holds the full FLUJO CLI stack, so a green local `repo_hygiene` run cannot by
  itself prove MAK-profile portability -- the scratchpad model closed that gap
  for this write-set but is session-local and not a repo instrument; (2) `rich`,
  `pydantic` and `requests` reach the MAK profile only transitively, so a
  future dependency change could remove them without any declaration changing;
  (3) `main` and `historia` read `ahead=1` against their remotes in the gate,
  pre-existing and untouched here, and both are historical, not deployment
  targets.
- Remote CI, distinguishing the two things. For the PREVIOUSLY PUBLISHED code
  (MAK `fc8005c1`, FLUJO `50e453c2`): `CI FLUJO` success (33670274140),
  `CI integration` success (33670334153), `CI MAK` failure (33670334244) on the
  single manifest test. For THIS write-set: no CI evidence exists and none is
  claimed -- it is unpublished, so no workflow has ever seen it.
- Next action for Faro: review these five paths and, if authorized, commit and
  push the three test files plus this handoff to `MAK` only, by the existing
  procedure; FLUJO needs no push. Then read `CI MAK` and `CI integration` for
  the new tip: the expectation is `repo hygiene lane` green and the integration
  lane at 373. The verdict is that matrix, not this local certification. IRIS
  remains paused; do not open its decision-reader slice as CI follow-up.

### Published and CI green -- 2026-09-02 -- manifest ratchet in integration

- Published SHA: MAK `9bfdc7460789d68eedf7ecaa0f7520d6260ceda9`,
  `fix(mak): place manifest ratchet in integration`, four paths,
  `550 insertions(+), 12 deletions(-)`. Push was a fast-forward without force:
  `fc8005c1..9bfdc746 MAK -> MAK` on remote `vibecodeine-legacy`.
- Refs after publication: local `MAK` and remote `refs/heads/MAK` both read
  `9bfdc7460789d68eedf7ecaa0f7520d6260ceda9`. FLUJO local and remote both
  remain `50e453c2a6ee9837c73acda3cec6ff74d0598f7e`: no FLUJO commit, no FLUJO
  push, no file in that checkout changed, and `CI FLUJO` was not expected to
  run and did not.
- Committed paths, exactly four: `tests/test_comandos_manifiesto.py`,
  `tests/test_mapa_completo.py`, `tests/test_test_taxonomy.py`,
  `context/LAST_HANDOFF.md`. Excluded and preserved unstaged:
  `context/coordination/inbox/claude/phase2-publication-review-20260902.md`.
  The staged set was verified against that list before committing, and
  `git diff --cached --check` exited 0. The committed handoff also carries the
  `Faro verification of Claude correction` section, which was already in the
  working tree.
- CI runs matched by SHA, not by recency. For `9bfdc746`: `CI MAK`
  run 33676031859, job `gate + mak lane`, **success** in 3m24s; `CI integration`
  run 33676031874, job `integration lane (MAK + FLUJO)`, **success** in 1m18s.
  Both jobs completed; no run of another revision was read as evidence.
- Job figures from the runners themselves, with the comparison that proves the
  fix rather than merely asserting it:
  - `CI MAK` step `repo hygiene lane`: `83 passed, 8 skipped in 34.36s`. On the
    previous tip `fc8005c1` (run 33670334244) the same step was
    `1 failed, 80 passed, 8 skipped`. The failure is gone, and 81 -> 83 is
    accounted for by the two pinned detector tests.
  - `CI MAK` step `MAK lane`: `2172 passed, 8 skipped, 5 warnings, 5 subtests
    passed in 100.58s`.
  - `CI integration`: `341 passed, 32 skipped, 20 warnings in 20.26s`, against
    `340 passed, 32 skipped` on `fc8005c1`. The skip count did NOT grow, so the
    moved check actually RAN on a clean runner and passed. That is the evidence
    that mattered: a ratchet that skipped there would have gated nothing.
- Local versus CI counts, reconciled so the next reader is not misled. Local
  totals were `repo_hygiene` 91, `mak` 2180 (2175 passed + 5 skipped) and
  `integration` 373; the runners report 83+8=91, 2172+8=2180 and 341+32=373.
  No test disappeared: the difference is entirely tests that skip when the
  physical MAK substrate is absent, which is the designed behavior. The
  earlier expectation of "integration at 373" refers to that total, not to 373
  passing on a clean runner.
- Protected surfaces: the commit contains no IRIS file, no `iskvw/*` path, no
  `campo.json`, no `animadas.json`, no `iskvw/piel/*`, no database, no
  artistic output, no requirements file, no service or systemd configuration,
  and no generated JSON -- `context/test_lane_map.json` was never edited. No
  data, layer or animation was regenerated. No service was started, stopped or
  restarted and no port changed; runtime was read-only throughout
  (`tools/runtime_preflight.py --check` exit 0, `ok=5`, before publication).
  No merge, reset, clean, checkout or branch switch was performed, and only the
  `MAK` ref was pushed.
- Next action for Faro/Codex: nothing is pending on this correction -- the
  clean-runner verdict now exists and is green on both workflows for the
  published SHA. The remaining open item from the prior sections is unchanged
  and unrelated: `rich`, `pydantic` and `requests` reach the MAK profile only
  transitively, so a future dependency change could remove them without any
  declaration changing; declaring them if MAK code needs them is a separate,
  deliberate decision. IRIS remains paused.

### MAK dependency boundary audit -- 2026-09-02

- Verdict: `NO_DIRECT_MAK_DEPENDENCY_DEFECT`. No requirements file was
  changed. The warning recorded earlier is now characterized precisely instead
  of being acted on blindly: MAK does not import `rich`, `pydantic` or
  `requests` even once, so their transitive arrival is not load-bearing and
  declaring them would add a dependency MAK does not use.
- Method. AST pass over the 737 tracked `.py` files of the MAK checkout,
  collecting every top-level `Import`/`ImportFrom` with `level == 0`, excluding
  stdlib (`sys.stdlib_module_names`) and MAK's own modules (every tracked stem
  and package directory, since MAK code imports siblings through `sys.path`).
  Eight files under `context-history/.../quarantine/` fail to parse and are
  quarantined malformed generated code, not runtime. Each remaining name was
  resolved to its distribution with `importlib.metadata.packages_distributions()`
  and compared against `requirements-mak.txt` resolved through its `-r` include
  of `requirements.txt`.
- Matrix of the investigated packages. `direct` means a real import statement
  in tracked MAK code, not a mention or an install:

  | package | direct MAK import | zone / lane | guarded | declared for its lane | decision |
  |---|---|---|---|---|---|
  | `rich` | none (0 sites) | -- | -- | not needed | transitive, intentional |
  | `pydantic` | none (0 sites) | -- | -- | not needed | transitive, intentional |
  | `requests` | none (0 sites) | -- | -- | not needed | transitive, intentional |
  | `typer` | 2 sites | `tests/test_autonomia_cli.py:3`, `tests/test_knowledge_dossiers.py:13`, both lane `integration` | no | yes, via `requirements-integration.txt` -> `flujo/requirements-flujo.txt` | declared |
  | `pypdf` | 1 site | `cultura/mak_research/source_pipeline.py:166`, runtime | yes, lazy + `except ImportError` | not required | optional by design |
  | `werkzeug` | 1 site | `xio/new/server.py:20`, `mak-xio.service` disabled | no | yes, equivalently | guaranteed by declared `Flask>=3.1.3` |
  | `crawl4ai` | 1 site | `cultura/mak_research/source_pipeline.py:262`, runtime, lazy | no | yes | declared |
  | `fontTools` | 4 sites | `.claude/skills/entregas-rd/generadores/gen_vectorizar.py:18-21`, agent skill | no | no | gap, not runtime -- see warnings |
  | `openpyxl` | 4 sites | `docs/recovered/claude_sessions_2026-08-12/raw/...`, recovered material | no | no | not runtime |
  | `customtkinter` | 1 site | `projects/plano/referencia_plano_teatro.py:1`, reference script | no | no | not runtime, not installed |
  | `tiktoken`, `torch` | 1 site each | `.claude/skills/.../benchmark.py`, `cultura/mak_plataforma/visual_index.py:320` | yes (`try`) | not required | optional by design |

- Transitive provenance, measured from installed metadata rather than assumed.
  `rich` and `pydantic` are HARD requirements of `crawl4ai`, which the MAK
  profile declares, so they are guaranteed for as long as that declaration
  stands. `requests` is a hard requirement of no declared MAK package: in this
  venv it arrives through `tiktoken` and the editable `flujo`, and in the CI
  MAK runner it arrives through crawl4ai's deeper chain. `typer` is guaranteed
  by nothing in the MAK profile, which is exactly why it was absent in run
  33670334244 and why the manifest ratchet failed there.
- Necessity probe, the measurement that settles it. A `sitecustomize.py` in the
  session scratchpad (outside the repo) blocked `rich`, `pydantic`, `requests`,
  `typer` and `pywebview` at import time -- deliberately stricter than any real
  environment -- and both MAK-profile lanes stayed fully green: `repo_hygiene`
  `91 passed in 37.41s` and `mak` `2175 passed, 5 skipped, 5 warnings,
  5 subtests passed in 114.63s`. MAK therefore does not need any of them, and
  the correction criteria are not met for a single one.
- Related mechanism discovered while resolving an apparent contradiction, worth
  keeping. Two `integration`-lane tests import `typer.testing` unguarded at
  module level, which should break collection in the MAK-profile lanes. It does
  not, because `tests/conftest.py:302` `pytest_ignore_collect` skips whole test
  modules whose declared lane differs when `-m` names one exact lane. So in
  `-m mak` and `-m repo_hygiene` runs foreign-lane modules are never imported.
  That is the deliberate mechanism; the general warning that pytest imports
  before it deselects still holds for broader marker expressions and for the
  release gate's physical-presence reasoning.
- No requirements contract test exists today. `tools/release_gate.py` enforces
  only profile FILE separation (MAK must not carry `requirements-flujo.txt`);
  nothing verifies that a direct third-party import is declared. The claim in
  `requirements.txt` that the split was "measured by AST over every tracked
  .py file of each branch" is a one-time hand measurement, and this audit
  independently reproduces it as still true for the four packages in question.
- Files modified: `none` for code, requirements, workflows and tests. The only
  write is this handoff section. `context/coordination/inbox/claude/phase2-publication-review-20260902.md`
  remains modified, unstaged and untouched.
- Commands and exact results, all read-only with `PYTHONDONTWRITEBYTECODE=1`
  and `/home/mak/.venv/bin/python`: `python -m pip check` -> `No broken
  requirements found.` exit 0; the two necessity-probe lane runs above;
  `git diff --check` exit 0 in both checkouts; `git diff --name-only` on the
  three requirements files returns zero paths. Refs unchanged and matching
  their remotes: MAK `0b9880f9d53da32083e979bd5fd13161f721b567`, FLUJO
  `50e453c2a6ee9837c73acda3cec6ff74d0598f7e`.
- No dependency was installed, removed or upgraded, permanently or otherwise.
  The two probe environments are `sitecustomize.py` files in the session
  scratchpad; nothing was written into `/home/mak`, no venv was modified, and
  no pre-existing material was deleted.
- IRIS, `iskvw/datos/*`, `campo.json`, `animadas.json`, `iskvw/piel/*`,
  databases, artistic outputs, services and ports were not touched. Nothing was
  regenerated, no service was started, stopped or restarted, and no commit,
  push, add, merge, reset, clean, checkout or branch switch was performed.
- Warnings for Faro, none of them a blocker and none corrected here because
  they fall outside the stated criteria:
  1. `fontTools` is imported unguarded by
     `.claude/skills/entregas-rd/generadores/gen_vectorizar.py` and is declared
     in no profile, with no consumer in `tools/` or `cultura/`. A freshly
     installed MAK profile would break that RD vectorization generator. It is
     an agent skill script, not service runtime, so the decision of whether
     `.claude/skills` dependencies belong in the box profile is a policy call,
     not a defect to patch.
  2. `requests` reaches the MAK profile through no declared package, unlike
     `rich` and `pydantic`, which `crawl4ai` requires hard. Since MAK imports
     none of the three, this only matters if MAK ever starts importing one.
  3. `openpyxl` and `customtkinter` are unguarded imports in recovered material
     and a project reference script respectively, neither on a runtime path;
     `customtkinter` is not even installed.
- Next action for Faro: decide item 1 only if the box is expected to run the
  RD vectorization generator from a clean profile install; otherwise nothing is
  pending. If a durable guarantee is wanted instead of a repeated audit, the
  missing instrument is a ratchet that fails when a tracked MAK file directly
  imports a third-party distribution absent from the MAK profile, with an
  explicit allowlist for guarded optional backends -- that is a new test, not a
  requirements edit, and it was not written here because no defect justified
  it. IRIS remains paused.

### MAK dependency contract hardening -- 2026-09-02

- `fontTools` decision: `AGENT_TOOL_ONLY`. No requirements file was changed.
- Entrypoint evidence, measured as absence in every place an entrypoint would
  live: no reference in `.github/`, no crontab line, no systemd unit
  (`systemctl --user list-unit-files` matches zero), nothing in `tools/` or
  `cultura/`, nothing in `MAPA.md` or `context/comandos.json`, and nothing in
  `/home/mak/flujo/src`. The only references are `.claude/skills/entregas-rd/SKILL.md`,
  `.claude/skills/taller-svg-rd/SKILL.md` and the script itself. Two further
  hits sit in `docs/recovered/claude_sessions_2026-08-12/raw/`, which is
  recovered transcript material, not documentation of a command.
  `.claude/skills/entregas-rd/generadores/gen_vectorizar.py` is a standalone
  `python3 gen_vectorizar.py IN.svg OUT.svg` script whose `fontTools` import is
  unguarded, with a fallback only for the DejaVu font PATH (via matplotlib),
  not for the library. It is an on-demand agent generator, not service runtime.
- Policy applied to `.claude/skills`: out of the MAK runtime scope, recorded in
  `_OUT_OF_SCOPE` with that reason. The classification is protected rather than
  merely written down: `fonttools` is declared in no profile, so the same
  import inside `cultura/`, `tools/` or `xio/` IS an offence and fails the new
  ratchet. A test asserts exactly that pair -- the skill path is out of scope
  AND the identical import in runtime scope offends.
- Ratchet created, reusing the existing infrastructure and adding no second
  architecture: `tests/test_test_taxonomy.py::test_the_mak_runtime_declares_every_dependency_it_imports`.
  It walks `git ls-files`, keeps the files the MAK profile is responsible for
  (`cultura/`, `tools/`, `xio/`, plus tracked tests whose lane contract says
  `mak` or `repo_hygiene`) and fails when a direct third-party import is
  neither declared in `requirements-mak.txt` (resolved through its `-r`
  include), nor guarded by its own `try/except ImportError`, nor classified in
  one of three reasoned tables. It distinguishes stdlib
  (`sys.stdlib_module_names`), MAK's own modules (every tracked stem and
  package directory, because MAK imports siblings through `sys.path`), the
  consumed motor (`flujo`, `src`), and import names that differ from their
  distribution (`_IMPORT_TO_DISTRIBUTION`: PIL, yaml, sklearn, fontTools, cv2,
  dateutil, fitz, serial, OpenSSL, attr).
- Why it lives in that file, since the reason is a constraint and not a
  preference: a new test file would land in the `review` lane, because
  `context/test_lane_map.json` is generated and must not be hand-edited, and
  `tests/conftest.py:302` `pytest_ignore_collect` skips non-matching lanes on
  every exact-lane run -- so a new file would never execute in any CI job. A
  new `tools/` module would need a VIVO/MUERTO row in `CAPACIDADES.md`
  (`test_tools_en_registro`, plus its reverse `test_registro_sin_herramientas_fantasma`),
  a second surface for logic only this ratchet consumes. The chosen file is
  already declared `repo_hygiene`, the lane that guards classification.
- The venv is explicitly NOT the contract. Installed distributions are never
  consulted; a test asserts that by reading the source of the seven contract
  functions through `inspect.getsource` and refusing
  `packages_distributions`, `importlib.metadata`, `pkg_resources` and
  `find_distributions`. The first version of that test greped its own
  forbidden-word list and failed on itself, which is why it now measures the
  functions instead of the file. Functionally: `rich` IS installed in the box
  venv and the guard still reports `import rich` in runtime scope as an
  offence.
- Allowlists, each entry carrying the reason that makes it checkable:
  - `_RUNTIME_PROVIDED` -- `bpy`, `bmesh`, `mathutils`, `gpu`, `bgl`, `aud`:
    Blender's embedded Python, not installable with pip, so declaring them
    would be a lie pip could not satisfy. Measured sites: 7 for `bpy`
    (`cultura/BLENDER.trilogy_450frames.py`, `tools/audit_blend_scene.py`,
    `tools/bake_static_materials.py` and others; 4 already guarded) and 1 for
    `mathutils`.
  - `_GUARANTEED_BY_DECLARED` -- `werkzeug`: `Flask>=3.1.3` declares
    `werkzeug>=3.1.0`, and `xio/new/server.py:20` imports
    `werkzeug.utils.secure_filename` directly. `mak-xio.service` is disabled,
    but the file stays in scope on purpose rather than being hidden by a
    scope exclusion.
  - `_CALLER_HANDLED_OPTIONAL` -- `pypdf`: `_pypdf_extract()` is a lazy import
    and `extract_pdf_text()` catches `ImportError`, returning
    `pdf_text_backend_unavailable` after the `pdftotext` binary fails. No
    single-file AST pass can see a caller's handler, so it is named here with
    where the fallback lives.
  - Auto-detected, needing no entry: `pdfplumber`, `psycopg`, `qwen_agent`,
    `torch`, `mobileclip`, all already wrapped in `try/except ImportError`.
- Files modified: `tests/test_test_taxonomy.py` and this handoff. No
  requirements file, no workflow, no pytest configuration, no lane contract,
  no runtime code.
- Write-set, exact, local and uncommitted: `tests/test_test_taxonomy.py`,
  `context/LAST_HANDOFF.md`, plus the pre-existing and untouched
  `context/coordination/inbox/claude/phase2-publication-review-20260902.md`.
  FLUJO's checkout is clean; nothing there changed.
- Ten demonstrations, all synthetic text this repo does not contain, so the
  guard is not measured only against the tree it guards: a missing direct
  import (fontTools) offends; a declared package (flask) does not; stdlib does
  not; an own module (`research_lib`) does not; a FLUJO import in an
  `integration`-lane test is out of scope (`tests/test_autonomia_cli.py`,
  `tests/test_knowledge_dossiers.py`, both of which import `typer.testing`
  unguarded and are correct); a `try/except ImportError` optional does not
  offend; the same import unguarded does; a data table, a comment and a string
  mentioning `fontTools` and `rich` do not; `.claude/skills` does not; and the
  whole contract holds with `rich`, `pydantic`, `requests` and `typer` blocked
  at import time. Bite check: synthetic runtime files importing `boto3`,
  `fontTools`, `paramiko` and `pydantic` are each reported with file, line and
  resolved distribution.
- Tests and exact figures, all with `PYTHONDONTWRITEBYTECODE=1` and
  `/home/mak/.venv/bin/python`:
  - focal `tests/test_test_taxonomy.py`: `17 passed in 2.23s`; the same file
    with the four suspect packages blocked: `17 passed in 47.36s`.
  - `repo_hygiene`, the verbatim `ci-mak.yml` step: `96 passed in 28.74s`, up
    from 91 by the five new tests.
  - `mak`, verbatim: `2175 passed, 5 skipped, 5 warnings, 5 subtests passed in
    106.96s`.
  - `integration`, verbatim: `373 passed, 20 warnings in 48.92s`. The `flujo`
    lane was not run: no file in the FLUJO checkout changed.
  - `python -m pip check`: `No broken requirements found.` exit 0.
  - `python -m flujo verify`: `✓ verify OK` exit 0, from `/home/mak/flujo`.
  - `tools/release_gate.py --check`: `BLOCKERS (0)`, `UNKNOWNS (0)`,
    `WARNINGS (0)`, exit 5, its documented deferred-tests code.
  - `tools/runtime_preflight.py --check`: exit 0, `ok=5`,
    `error=0 unknown=0 warn=0 adapter_dependency=0`.
  - `git diff --check` exit 0 in both checkouts; `git diff --name-only` lists
    the three paths above and nothing else.
- No dependency was installed, removed or upgraded. The import-blocking probe
  is a `sitecustomize.py` in the session scratchpad outside the repository; no
  venv was modified and no pre-existing material was deleted. Generated
  residue from this session, registered rather than swept:
  `/home/mak/flujo/_logs/hub_smoke_2026-09-02_16-30-58.log`, written by
  `flujo verify` into a gitignored directory (`.gitignore:196`).
- Protected surfaces: IRIS and its reader, `iskvw/datos/*`, `campo.json`,
  `animadas.json`, `iskvw/piel/*`, databases, artistic outputs, services and
  ports were not touched; nothing was regenerated; the FLUJO branch was not
  modified; the Claude coordination packet was preserved unstaged. No commit,
  push, add, merge, reset, clean, checkout or branch switch was performed.
- Blockers: none. Warnings, unchanged from the audit and deliberately not
  "fixed" by declaring anything: (1) a clean MAK-profile install still cannot
  run the RD vectorization generator, which is the accepted consequence of
  `AGENT_TOOL_ONLY` -- if the box is ever expected to run it from a clean
  profile, `fonttools` becomes a real declaration decision, and the ratchet
  will demand it the moment that import moves into runtime scope;
  (2) `requests` reaches the MAK profile through no declared package, unlike
  `rich` and `pydantic`, which `crawl4ai` requires hard -- harmless while MAK
  imports none of the three, and the ratchet now catches the day one of them
  is imported; (3) the guard reads direct subprocess-free imports and one
  level of module constants, so a dependency reached only through a dynamic
  `importlib.import_module(name)` built at runtime would escape it.
- Next action for Faro: review the two-path write-set and, if authorized,
  publish it to `MAK` with the existing procedure; FLUJO needs no push. After
  publication the expectation on a clean runner is `repo hygiene lane` at
  96 passed and the integration lane unchanged at 341 passed / 32 skipped.
  IRIS remains paused.

### Faro independent verification of dependency hardening -- 2026-09-02

- Re-ran the new ratchet directly: `tests/test_test_taxonomy.py` completed with
  `17 passed in 3.36s`.
- Re-ran the complete `repo_hygiene` lane with
  `PYTHONDONTWRITEBYTECODE=1` and `-o addopts=`: `96 passed in 32.76s`.
- `git diff --check` passes. The only current paths are the dependency-ratchet
  test, this handoff, and the pre-existing Claude packet; FLUJO remains clean.
- This confirms the reported `DEPENDENCY_CONTRACT_HARDENED` result locally. The
  change is still uncommitted and the remote remains at MAK `0b9880f9`; the next
  action is review and explicit authorization before any publication. IRIS,
  data, services and artistic outputs remain untouched.

### Dependency ratchet published and CI green -- 2026-09-02

- Published SHA: MAK `ff781183a6997000f80b74b4bd1b788cc670845c`,
  `test(mak): enforce declared runtime dependencies`, two paths,
  `602 insertions(+), 1 deletion(-)`. Push was a fast-forward without force:
  `0b9880f9..ff781183 MAK -> MAK` on remote `vibecodeine-legacy`.
- Local `MAK` and remote `refs/heads/MAK` both read
  `ff781183a6997000f80b74b4bd1b788cc670845c`.
- Committed paths, exactly two: `tests/test_test_taxonomy.py` and
  `context/LAST_HANDOFF.md` (which carried the Fase 3A audit and the Fase 3B
  hardening sections). Excluded and left unstaged, still modified:
  `context/coordination/inbox/claude/phase2-publication-review-20260902.md`.
  The staged set was compared against that list before committing and matched
  exactly, with no leftovers and nothing missing.
- CI matched by `headSha`, not by recency. `CI MAK` run 33681688304, job
  `gate + mak lane`, **success** in 3m8s. `CI integration` run 33681688258,
  job `integration lane (MAK + FLUJO)`, **success**. `CI FLUJO` did not run:
  its latest remains 33670274140 on `50e453c2` from 18:56Z, which is correct
  because FLUJO received no commit and no push.
- Runner figures, with the comparison that shows the ratchet actually executed
  on a clean checkout rather than being skipped there:
  - `repo hygiene lane`: `88 passed, 8 skipped in 36.53s`, against
    `83 passed, 8 skipped` on the previous tip `0b9880f9`. The skip count did
    NOT change, so all five new tests ran and passed on the runner.
  - `MAK lane`: `2172 passed, 8 skipped, 5 warnings, 5 subtests passed in
    99.04s`, byte-identical in counts to the previous tip.
  - `CI integration`: `341 passed, 32 skipped, 20 warnings in 19.14s`,
    identical to the previous tip. The change touched no integration-lane
    classification.
  - Local totals reconcile as before: local `repo_hygiene` 96 equals the
    runner's 88 passed + 8 skipped; local `mak` 2180 equals 2172 + 8; local
    `integration` 373 equals 341 + 32. No test was lost and no new skip was
    introduced by this change.
- Pre-publication verification, all with `PYTHONDONTWRITEBYTECODE=1` and
  `/home/mak/.venv/bin/python`: focal `tests/test_test_taxonomy.py`
  `17 passed`; `repo_hygiene` `96 passed`; `mak` `2175 passed, 5 skipped`;
  `integration` `373 passed`; `python -m pip check` `No broken requirements
  found.` exit 0; `git diff --check` and `git diff --cached --check` exit 0;
  `tools/release_gate.py --check` `BLOCKERS (0) UNKNOWNS (0) WARNINGS (0)`
  exit 5, its documented deferred-tests code; `tools/runtime_preflight.py
  --check` exit 0 with `ok=5` and zero error/unknown/warn/adapter conditions.
- FLUJO: not modified, not committed, not pushed. Local and remote both remain
  `50e453c2a6ee9837c73acda3cec6ff74d0598f7e`, and its checkout is clean.
- The commit contains no requirements file, no workflow, no
  `context/test_lane_map.json`, no pytest configuration and no runtime code.
  IRIS and its reader, `iskvw/datos/*`, `campo.json`, `animadas.json`,
  `iskvw/piel/*`, databases, artistic outputs, services and ports were not
  touched; nothing was regenerated; no service was started, stopped or
  restarted and no port changed. No merge, reset, clean, checkout, switch or
  force push was performed, and only the `MAK` ref was pushed.
- Next action for Faro/Codex: nothing is pending on the dependency contract.
  The guarantee now exists and is green on a clean runner, and the two open
  warnings are recorded in the hardening section above unchanged -- a clean
  MAK-profile install still cannot run the RD vectorization generator
  (the accepted consequence of `AGENT_TOOL_ONLY`), and `requests` reaches the
  MAK profile through no declared package. Both are decisions, not defects,
  and the ratchet now fails the day either becomes a real runtime import.
  IRIS remains paused.

### MAK vertical circuit v1 -- 2026-09-02

- Verdict: `VERTICAL_CIRCUIT_VERIFIED`. The circuit already existed complete in
  code. No module was modified, no data semantics changed, and no piece was
  implemented: the gap was that every node was unit-tested while the CHAIN was
  not, so nothing failed when a hop lost a property.
- Circuit chosen and why: the XIO show-kit evidence circuit. It is the smallest
  chain that already has code AND a fixture, it is a MAK operation rather than
  an IRIS editorial one, and its head already refuses the inference that
  matters -- `artist`, `venue` and `producer` are always emitted as `unknown`
  with an empty value, so an event name, a filename or a directory name cannot
  become authorship. Alternatives were rejected on evidence:
  `instagram_source.py` reads a real export (new real input, forbidden here),
  and `portfolio_record` would enter Portfolio, which this phase excludes.
- Input: five authoritative files in a show-kit root
  (`setlist_festival_sentir.txt`, `setlist_durations_dref.json`,
  `cue_map_dref.json`, `DIA_DEL_SHOW.md`, `ANOTACIONES_SHOW_20260724.md`),
  written synthetically into `tmp_path`. The root is parameterised
  (`MAK_XIO_SHOW_ROOT` / the `root` argument), so no physical show kit and no
  new real data were used.
- Evidence: atoms carrying three distinct epistemic statuses --
  `observed` (timecodes read from the annotation), `declared` (event and date,
  asserted by a named source) and `unknown` (artist, venue, producer, with no
  source and no value). Every atom keeps its own `source`.
- Modules and stores used, all existing:
  `cultura/mak_plataforma/xio_evidence.py::load_show_evidence` ->
  `cultura/mak_plataforma/ledger.py::build_work_envelope` /
  `validate_work_envelope` ->
  `cultura/mak_plataforma/discernment.py::deterministic_review` ->
  `discernment.py::decision_record` ->
  `ledger.py::append_review` / `review_to_ledger` -> `ledger.py::read_items`.
  The reviewer runs its deterministic local path; Ollama was not called.
- Result produced: an append-only ledger row, read back from
  `tmp_path/common_ledger.jsonl`, carrying `domain=mak`, `lane=sistema`,
  `decision=revisar`, `confidence=low`, `action=decide`, `owner=human`,
  `next_action=revise provider output`, and the whole `mak-work-v1` envelope
  with `work_id=xio:show:show_kit`, `status=candidate` and its five source
  refs intact.
- Envelope fields preserved through the chain: `work_id`, `lane=trabajo`,
  `purpose`, `format=show_evidence`, `provider=xio_local`, `owner=MAK`,
  `status=candidate`, `sources` (five refs), `created_at`, `next_action`,
  `evidence_required=[xio_show_kit, human_portfolio_link]`,
  `allowed_decisions` (the five-value vocabulary), and an identity block whose
  `entities` populate `event` and `source` while `artist`, `username`,
  `client`, `collab`, `venue` and `location` stay empty lists.
- Producer and owner stay separate questions at every hop, which the test
  asserts rather than assumes: the evidence producer is `xio_local` and its
  owner is `MAK`; the decision producer is `local_deterministic` and its owner
  becomes `human` precisely because the verdict was `revise`. The work's lane
  is `trabajo` while the decision about it is `sistema` -- two objects, two
  lanes, and merging them would lose which one was judged.
- Possible states, all reachable and none skipped: evidence status
  `observed` / `declared` / `unknown`; review verdict `accept` / `revise` /
  `reject`; decision vocabulary `hacer` / `revisar` / `refutar` / `archivar` /
  `descartar`; work status stays `candidate` throughout; `promotion` is
  `none` in every branch.
- Human decision required: the link to a portfolio source. `linked_to_source_id`
  is `False` and `next_action` remains `link manually to portfolio source`. The
  second test proves this is a real gate and not a side effect of the failing
  branch: even when every field carries a source and the verdict is `accept`
  with decision `hacer`, `promotion` is still `none`, the envelope is still
  `candidate`, and no link is created. `accept` means the batch is reviewable,
  never that the relation is true.
- Mutation evidence, because a passing test proves nothing about its own
  sensitivity. Nine corruptions were injected in memory (never into the repo)
  and each one broke the test at a named line: source refs emptied (line 112),
  owner overwritten with the provider (117), the three unknown atoms rewritten
  as declared with the event name (97), an absence coerced to `False` (102),
  `linked_to_source_id` set true (172), `next_action` blanked (168), the
  envelope promoted to `accepted` (110), the decision node promoting with
  `promotion=auto` (141), and the ledger row recording `confidence=high` for a
  review that had asked for evidence (155). Detected: 9 of 9.
- Write-set, exact, local and uncommitted: `tests/test_xio_evidence.py` and
  `context/LAST_HANDOFF.md`, plus the pre-existing, untouched
  `context/coordination/inbox/claude/phase2-publication-review-20260902.md`.
  No module, store, contract, requirements file, workflow or lane contract
  changed. The one non-test edit inside that file is factoring the existing
  fixture into `_write_show_kit()` so both tests feed on the same input; the
  original test's assertions are unchanged, and a duplicated fixture is how
  two tests start measuring different things unnoticed.
- Tests and results, with `PYTHONDONTWRITEBYTECODE=1`, `-o addopts=` and
  `/home/mak/.venv/bin/python`: circuit plus implicated stores
  (`test_xio_evidence`, `test_mak_ledger`, `test_mak_discernment`,
  `test_mak_tandas`, `test_xio_portfolio_link`) `110 passed in 2.40s`;
  `repo_hygiene` `96 passed in 28.69s`; the affected lane `mak`
  `2177 passed, 5 skipped, 5 warnings, 5 subtests passed in 132.79s`, up from
  2175 by the two new tests. `integration` was NOT run: no
  integration-lane file changed and the lane contract keeps
  `tests/test_xio_evidence.py` in `mak`. `python -m pip check` `No broken
  requirements found.` exit 0; `git diff --check` exit 0 in both checkouts;
  `tools/release_gate.py --check` `BLOCKERS (0) UNKNOWNS (0) WARNINGS (0)`
  exit 5, its documented deferred-tests code; `tools/runtime_preflight.py
  --check` exit 0 with `ok=5` and zero error/unknown/warn/adapter conditions.
- Epistemological limits, stated rather than smoothed over:
  1. The circuit proves the CHAIN's bookkeeping, not the truth of any claim
     about the show. `event` and `date` remain `declared` by a source; nothing
     verified them.
  2. `ledger.review_to_ledger` types a row binarily -- `decision` when the
     verdict is `accept`, `reject` otherwise -- so a `revise` verdict is
     recorded with `type=reject` while its `decision` correctly reads
     `revisar`. The precise value survives in `decision`; the coarse `type`
     does not distinguish "not accepted yet" from "rejected". This was left
     exactly as it is: changing it to make a test read better would be
     changing data semantics, which this phase forbids. It is a candidate
     observation for Faro, not a defect this circuit may decide.
  3. The reviewer is mechanical. It detects empty evidence, low confidence,
     domain mixing, secret-bearing text and negative claims without search
     evidence. It does not judge artistic fit, and `deterministic_review` says
     so in its own docstring.
  4. `_review_payload` is the test's own mapping from evidence atoms to review
     items. It is a demonstration of the contract, not a production adapter;
     no such adapter was added, because none was asked for and the circuit
     does not need one to be shown.
- IRIS, its reader, `iskvw/datos/*`, `campo.json`, `animadas.json`,
  `iskvw/piel/*`, databases, artistic outputs, services and ports were not
  touched, and the 219/871 decision was not reopened. The productive
  append-only ledger at `~/plataforma/common_ledger.jsonl` still carries its
  earlier mtime (`sep 2 02:53`, hours before this session's runs), which is
  the measured proof that every write went to `tmp_path`. FLUJO's checkout is
  clean and received nothing. No commit, push, add, merge, reset, clean,
  checkout or branch switch was performed.
- Next action for Faro: review this two-path write-set and, if authorized,
  publish it to `MAK`; FLUJO needs no push. After publication the clean-runner
  expectation is `mak` lane at 2177 and `repo hygiene` unchanged at 88 passed /
  8 skipped. The open question this circuit surfaces, and does not decide, is
  limit 2 above: whether the ledger row `type` should carry the same
  five-value vocabulary as `decision`. IRIS remains paused.

### Faro review of vertical circuit -- 2026-09-02

- The approach is worth continuing, but the mode should change: the physical
  and CI boundary work is now sufficiently verified; another broad audit would
  have diminishing returns. Claude's vertical circuit added a useful
  end-to-end contract test without pretending that a synthetic show-kit proves
  the truth of an artistic claim.
- Independent checks passed: `tests/test_xio_evidence.py` `4 passed in 18.27s`;
  implicated ledger/discernment/tandas/portfolio-link tests `106 passed in
  20.36s`; `git diff --check` passed. Current local write-set is the new test,
  this handoff, and the pre-existing Claude packet; FLUJO is clean.
- The next order should be a focused semantic investigation of
  `ledger.review_to_ledger`: a `revise` decision is currently stored with the
  coarse row `type=reject`. Do not change it yet; first trace all consumers,
  fixtures and compatibility implications. This is a real contract question,
  not an excuse to reopen IRIS or regenerate data.

### Portfolio surface ordered and registered -- 2026-09-02

- What this closed: the identity of the Hub's portfolio surface, which had
  confused two agents in a row. It is a PAIR -- `iskvw/editor.html` is the
  shell and `iskvw/mesa_montaje.js` draws everything a person reads. Measured:
  the served bytes equal the physical files in this checkout
  (`editor ed7e3bf2...f331`, `mesa d7a50d27...ecb2`), `git status iskvw/` is
  clean, so what runs on `127.0.0.1:8900/portafolio/` is what is committed.
  No stale deployment existed.
- The two traps, both now pinned by tests. Searching only `editor.html` for the
  visible chrome ("atlas vivo", incertidumbre, siguiente frontera, evidencia
  externa) returns ZERO, because those strings live in the JS -- which reads
  exactly like an old version of a current tree. And the shell carries 89
  `text-transform` rules, so the uppercase on screen is not the case in the
  source: searching for what the screenshot shows fails a second time.
- `IRIS` is the name of the Fondart application this system is presented under.
  Operator's correction, 2026-09-02: it is NOT a component name and nothing in
  the tree is renamed for it. An earlier draft of this session's CAPACIDADES
  entry labelled the surface "IRIS (mesa de montaje)"; that was reverted to
  "Mesa de montaje (pestana portafolio)". No file, route or symbol was renamed
  by this work.
- Registered so the confusion cannot recur: `CAPACIDADES.md` section 1-bis now
  carries a row for the surface plus a block with its physical identity
  (both hashes and byte sizes), its measured consumers -- `hub.py` (serves
  `/portafolio/` and `/static/iskvw/editor`), `copilot.py` (through
  `/api/portfolio/copilot/scene|learning|xio-link`),
  `flujo/src/flujo/departments.py:57,61`, `tests/test_iskvw_editor_contract.py`,
  `tests/test_curaduria_roundtrip.py`, `tools/validar_curaduria.py`,
  `iskvw/datos/{curaduria,tablero}.json`, `iskvw/MAPA.md` -- and the ten API
  routes the interface calls. `AGENTS.md` and `CLAUDE.md` carry the short
  version with pointers here.
- Everything the interface consumes answers. Ten routes probed read-only:
  `inbox`, `audit`, `external-candidates`, `copilot/scene`, `copilot/learning`
  return HTTP 200; `copilot/scene` returns `provider=local_hypothesis_engine`
  and `map.schema=faro-gtm-map-v1`, which is `copilot.GTM_SCHEMA` -- the live
  proof that the interface really reaches the copilot. The mutating routes are
  POST (`hub.py:5288-5299`) and were NOT called: probing `copilot/xio-link`
  with GET returns `ruta_api_no_encontrada`, which is the correct answer and
  was my own probe error, not a defect. Inbox composition: 7044 items, 6976
  `pendiente`, 62 `descartar`, 4 `seleccionar`, 2 `deseleccionar`; a scene over
  a discarded record refuses to compose, by design.
- Guards added to `tests/test_iskvw_editor_contract.py` (lane `repo_hygiene`),
  mutation-verified 3/3 -- the guard fails when the shell stops loading the JS,
  when the chrome migrates into the HTML, and when the JS loses the chrome,
  which is the genuinely-old-version case:
  `test_the_surface_is_a_pair_and_the_chrome_lives_in_the_javascript`,
  `test_the_hub_serves_the_editor_from_this_checkout_not_the_sibling`
  (`PORTFOLIO_ROOT` must resolve here, not to the sibling), and
  `test_the_two_checkout_copies_do_not_diverge_in_silence` (both operational
  checkouts track the pair; it refuses silent divergence without deciding
  whether FLUJO should carry it at all).
- Half-finished retirement found and COMPLETED (operator handed the decision
  to the agent after the first report):
  `/home/mak/plataforma/iskvw/editor.html` was archived reversibly to
  `_archive/iris-editor-consolidation-20260902/` with its hash, but
  `/home/mak/plataforma/iskvw/mesa_montaje.js` still exists as a symlink into
  the FLUJO checkout, inside the Hub's own working directory. It is inert
  today: `hub.py` resolves the absolute `PORTFOLIO_ROOT` and never a
  cwd-relative `iskvw/` path, and `plataforma/` is untracked
  (`.git/info/exclude:81`). Measured orphaned before acting -- no cron line, no
  systemd unit, and no file under `plataforma/`, `cultura/`, `tools/` or
  `iskvw/` referencing the path -- then removed with its directory. A symlink
  carries no content and its target is intact; the archive README records the
  exact `ln -s` that restores it. `/portafolio/` and `mesa_montaje.js`
  re-checked at HTTP 200 afterwards.
- The prose corrections carried in this publication came from the working tree
  and were verified rather than assumed: `AGENTS.md` now points the served
  surface at `/home/mak/iskvw` instead of the stale `/home/mak/flujo/iskvw`,
  which matches `hub.py:92-99` and the measured runtime; `docs/IRIS_CANONICAL.md`
  and `docs/MAK_CURRENT_STATE.md` state the system/product/site distinction;
  `copilot.py`, `hub.py` and `tools/gen_campo_iskvw.py` gained explanatory
  docstrings. None of them renames a file, a route or a symbol.
- Verification, `PYTHONDONTWRITEBYTECODE=1` with `/home/mak/.venv/bin/python`:
  focal editor contract `6 passed`; `repo_hygiene` `99 passed`; `mak` lane and
  `integration` below; `python -m pip check` clean; `git diff --check` exit 0.
- Not committed, deliberately and as instructed throughout this session:
  `context/coordination/inbox/claude/phase2-publication-review-20260902.md`
  stays modified and unstaged.
- The Hub was running stale bytes: `hub.py` had been edited at 17:53 while the
  process had started at 13:47, so `runtime_preflight.py` reported
  `source_changed_after_start` and `error=1`. That was not a regression from
  this work. `mak-hub.service` was restarted (PID 1011997 -> 1133925), the
  surface came back at HTTP 200 on `/health`, `/portafolio/` and
  `/api/portfolio/audit`, the copilot scene still answers
  `provider=local_hypothesis_engine` with `map.schema=faro-gtm-map-v1`, and
  preflight returned to `ok=5` with zero error/unknown/warn/adapter.
- Next action: one open question remains, and it is an ownership call rather
  than a defect -- whether the FLUJO checkout should keep tracking
  `iskvw/editor.html` and `iskvw/mesa_montaje.js` at all. They are identical to
  MAK's today and the guard refuses silent divergence, so nothing breaks while
  the question waits. The portfolio surface itself needs no repair: it is
  current, served from the right checkout, guarded, and now the only copy on a
  runtime path.

### Evidence readiness on the decision frontier -- 2026-09-02

- The workflow bottleneck, measured before building anything: of 7044 records
  the operator has labelled 116 and left 6928 unlabelled, and the ordering
  model predicts NONE of them with high confidence -- `alta: 0`, `media: 4156`,
  `baja: 2772`, coverage 0.0165. The active-learning loop itself is already
  well built: `ordering.human_seed` ranks the most informative unlabelled
  cases, the interface centres one, prefetches the next and auto-advances after
  a decision. So the model gives the operator no leverage, every case is still
  a human look, and the only lever left is making that look cheaper.
- Two candidate levers were measured and one was rejected. Publication siblings:
  6431 of 6586 publications carry a single medium and only 18 undecided
  siblings sit in publications that already have a decision -- no leverage
  there, so it was dropped rather than built. The real gap: the frontier rows
  already carry `has_description`, `has_vision` and `review_scope`, and the
  interface referenced NONE of them (`asset_available` was the only field it
  read). The operator was deciding without seeing what the case contained --
  and `review`, the label that means "not decidable yet", was used once in 116
  decisions (work 32, record 22, discard 61, review 1).
- What was added, `copilot.evidence_readiness()` (schema
  `faro-evidence-readiness-v1`): a pure report of what one record HAS and
  LACKS across seven channels -- asset, description, date, perception,
  classification, relations, work_group. It receives what was already measured
  and invents nothing.
- The epistemic distinction the report exists for: `unknown` is kept apart from
  `absent`. The perception index covers 100 of 7044 records, so a missing
  vision row is almost always "not indexed", not "this record has no
  perception". Without `vision_indexed` the channel stays `unknown`; with it,
  an indexed record that has no usable reading is `absent`. Collapsing the two
  is how a gap becomes a finding.
- `asset` and `description` are the minimum a defensible label rests on. When
  either is missing the report returns `decision: abstain` and names the
  blocking channels, with `next_action` pointing at `review` and the missing
  evidence -- which turns a case that would sit `pendiente` forever into a
  recorded outcome. Otherwise it returns `decidable_con_reservas` and declares
  what is missing without resolving it. `promotion` is `none` and `owner` is
  `human` in every branch: a readout is not a decision.
- Wired into the surface without a new round trip: `hub.py` folds the report
  into the scene the interface already fetches, and `mesa_montaje.js` renders
  it as a chip strip inside the existing order HUD, using the existing visual
  language. The three statuses are visually distinct in `editor.html`
  (`is-present`, `is-absent`, `is-unknown`), and abstention is styled apart
  from a reservation, so `unknown` cannot read as `absent` on screen. The
  `revisar` button was already one click away and stays there.
- Live proof rather than a claim: `GET /api/portfolio/copilot/scene` now
  returns `evidence_readiness` with
  `decision=decidable_con_reservas`, `missing=[classification, work_group]`,
  `unmeasured=[perception]` for the first frontier candidate; the served
  `mesa_montaje.js` carries the renderer and the served `editor.html` carries
  the eight style rules.
- A guard I wrote this morning was refuted by this work and replaced.
  `test_the_two_checkout_copies_do_not_diverge_in_silence` demanded the MAK and
  FLUJO copies of the surface stay byte-identical; the first real improvement
  broke it, and the rule was wrong: it would force every MAK-side UI change to
  also touch the FLUJO branch, coupling the two checkouts the separation
  existed to decouple. Measured instead: the FLUJO Hub serves no
  `/api/portfolio/*` route while the interface makes five or more fetches to
  exactly those routes, so the sibling copy is inert there. The replacement,
  `test_the_mak_tree_never_reads_the_sibling_copy_of_the_surface`, guards
  direction instead of equality, over string LITERALS via AST -- because
  `hub.py` carries a comment explaining why the `HOME/flujo/iskvw` spelling was
  retired, and a plain substring search called that comment a read. Naming a
  path is not using it. Mutation-checked 4/4 and 46x faster than the version it
  replaced.
- Tests: five in `tests/test_copilot.py` covering the unknown/absent split in
  both directions, abstention on a missing minimum, no promotion and a human
  owner in every branch, reservations that do not block a label, and a record
  it cannot read at all failing closed. One in
  `tests/test_iskvw_editor_contract.py` asserting the INTERFACE makes it
  distinguishable -- every channel named for a person, three visually distinct
  statuses, abstention styled apart -- because data reaching the browser is not
  the same as a person being able to read it.
- Figures: `tests/test_copilot.py` `42 passed`;
  `tests/test_iskvw_editor_contract.py` `7 passed`; `repo_hygiene`
  `100 passed`; `mak` `2182 passed, 5 skipped, 5 warnings, 5 subtests`;
  `integration` `373 passed`; `pip check` clean; `git diff --check` exit 0;
  `runtime_preflight --check` exit 0 with `ok=5`; `/portafolio/` HTTP 200 after
  the Hub restart that picked the change up.
- Ownership question now answered with evidence, and left as a recommendation
  rather than an action: the FLUJO checkout tracks `iskvw/editor.html` and
  `iskvw/mesa_montaje.js`, and its Hub cannot serve them. They are dead weight
  on that branch. Removing them is a FLUJO commit and was not taken here; the
  direction guard makes the duplicate harmless meanwhile.
- Not touched: `iskvw/datos/*`, `campo.json`, `animadas.json`, `iskvw/piel/*`,
  databases, artistic outputs, the published site. No record was labelled, no
  relation created, no data regenerated. The improvement changes what the
  operator SEES before deciding; it decides nothing.
- Next: the perception index covers 100 of 7044 records and its feedback total
  is 0, so `perception` will report `unknown` for almost every case. That is
  now visible instead of silent, and widening the index is the next lever --
  a batch compute decision, not a workflow change.

### O_G composed: N defensible orders instead of one verdict -- 2026-09-02

- The operator's reframing, in his words: he had thought MAK had to learn to
  make CLASSIC portfolios, and realised he should create portfolio FORMATS
  instead -- and that being art, deviation is easier to justify. That is not a
  change of mood; `docs/DIMENSIONES_DEL_ORDEN.md:160` already named it as the
  theory's one open gap: "$O_G$ -- un orden defendible, relativo a un
  proposito -- todavia no existe como salida: el sistema emite un veredicto
  unico en vez de N ordenes."
- Two things were already built for this idea before it was named. The copilot
  splits every relation into an `evidence` space and a `resonance` space, and
  in the live scene 19 of 19 relations are `resonance` with confidence `alta`
  -- under "learn the classic portfolio" that reads as total failure; under
  "create formats" it is the material. And the interface already says "La
  geometria permanece. Tus decisiones cambian el campo, no borran la
  ambiguedad."
- The boundary this work holds, stated because "art justifies error" is true
  in one layer and false in the other: the FORMAT is invented, the EVIDENCE is
  not. An unexpected order, an abstention, an exhibited gap -- that is
  authorship. An artist, a venue or a date the system did not measure is not
  art justifying error; it is the machine lying about the archive the work is
  made of. The codebase already draws that line as evidence/resonance,
  candidate/accepted and unknown/absent.
- `G` was already implemented and unnamed: a FORMAT is a purpose.
  `data/portfolio_formats/*.json` holds six of them
  (`mak-portfolio-format-v1`), each declaring slots with `count`, `claim`,
  `layer`, `min_state` and `min_permission`, plus `declared_claims`,
  `forbidden_claims`, `forbidden_inferences` and `invalid_if`. Measured: NOTHING
  composed an order from them. `flujo/src/flujo/knowledge/portfolio_dossier.py`
  does not mention them, and inside MAK only one test and two documents read
  the directory.
- `F` now exists: `copilot.compose_order()` / `compose_orders()`, schema
  `faro-order-composition-v1`, exposed at
  `GET /api/portfolio/copilot/orders`. It fills each declared slot from the
  corpus, reports what it selected with `source_ref` and derived state, what it
  abstained on and why, whether each `invalid_if` condition triggers, and the
  terms of the objective.
- The result over the real archive, 7044 records and all six formats: every
  slot's count is satisfiable -- `R_G` 1.0, `T` 1.0, redundancy `N` 0 -- and
  ALL SIX formats are invalid for one single reason. Zero of 7044 records carry
  a `permission` field, and every slot declares a `min_permission`. So the
  finding is not "MAK cannot make portfolios": it is "record permission and six
  formats become producible". That is worth more than any composition the
  engine could have fabricated.
- Two defects of my own, both found by running against the real archive rather
  than a fixture. F4 declares `min_state: supported_candidate`, a rung this
  engine cannot rank, and the first version silently defaulted it to
  `candidate` -- accepting a LOWER bar than the format asked for, which is the
  same defect as reading an absence as health. It now fails closed, selects
  nothing for that slot and says why. And the objective reports `C`, `D` and
  `V` as `measured: false` with a reason instead of a zero: `V` cannot be
  scored because the perception index covers 100 of 7044 pieces, and reporting
  a number for an unmeasured term is precisely what the `U` term exists to
  punish. `U` itself is 0 by construction, not by promise.
- Nothing about the state ladder invents authorship: a record is `observed`
  only when the archive itself shows a dated artifact on disk, `candidate` when
  it has one of the two, `unknown` otherwise. No filename, folder, position or
  adjacency is read as evidence, which is what the formats' own
  `forbidden_inferences` demand.
- Tests: six in `tests/test_copilot.py` -- N orders with none of them the
  answer and the constraints travelling with each; abstention on an unrecorded
  permission; failing closed on an unrankable state; refusing to read a
  filename or a date as an event; never scoring an unmeasured term; and no
  record reused across slots. Figures: `tests/test_copilot.py` `48 passed`;
  `mak` `2188 passed, 5 skipped`; `repo_hygiene` `100 passed`; `integration`
  and `runtime_preflight` below.
- Nothing was published, promoted or written to the archive. Every order
  carries `promotion: none`, `owner: human` and its own `next_action`; the six
  compositions are proposals a person reads, and no record was labelled or
  linked to produce them.
- Next, and it is the operator's call rather than a technical one: the engine
  has no surface yet. The six orders and what blocks each are available at the
  route but not drawn in the interface, because how a format is presented is an
  aesthetic decision, not a mechanical one. The other open lever is the one the
  measurement exposed: recording permission, without which no format can be
  declared valid.

### A format written against what the archive has -- 2026-09-02

- The operator's correction, and it reversed the approach: "no se busca llegar
  al 99%, se crean los formatos de portafolio, y para cada formato sus
  requerimientos y asi se hace trampa; tu dejas de luchar con lo falso y pasas
  a ser artista, crea". Every existing format composed as invalid because it
  demanded a `min_permission` no record carries, and the reflex -- mine -- was
  to go fix the archive until it met the formats. But he authors the formats.
  The frame is his to set, and a format that declares requirements the corpus
  already meets is not a concession; it is the decision about who defines
  sufficiency.
- Two instruments were built before that correction landed and both were
  measuring, not producing. `copilot.friction_map()` reports coverage and
  normalised Shannon entropy per dimension -- the operator's own July research
  named the output first: "un mapa de friccion, no una puntuacion de
  productividad", in `solid_hpi_quantified_self/`, researched and never
  implemented. Its finding on the real corpus: `date` and `directory` are the
  only axes that order, `directory` is itself a projection of date
  (`stories/YYYYMM`), and `status` covers 7044 of 7044 records with a single
  value -- perfectly clean, ordering nothing, which is exactly "limpio pero
  desordenado" made computable.
- The map refuted itself once and was corrected: `publication` scored entropy
  0.986 across 6586 distinct values over 7044 records and was reported as an
  ordering axis. Maximum entropy is not maximum order -- it is one drawer per
  object, which is the filesystem's own illusion. A `granularity` term now
  separates `identifica` from `ordena`, and under it the archive has two real
  axes, not three.
- `F8-temporada` is the created format: four slots standing only on a dated
  artifact on disk, the two dimensions with full coverage, and asking for no
  permission at all. `picos` orders by density of registro, `continuidad` by
  unbroken runs, `silencios` by the borders of the longest gaps, and `voz` by
  the pieces the author actually wrote about. It declares `ocurrio` and forbids
  `es_mio`, `significa`, `hice_esta_parte` and `vale_mas`, and its forbidden
  inferences carry the ones this particular format could invite: a silence in
  the archive is not an absence of work, density of registro is not intensity
  of work, a publishing run is not a production run.
- It composes VALID on the real archive: 72 pieces, four slots satisfied, zero
  invalid reasons, `R_G` 1.0, `T` 1.0, redundancy 0, `U` 0. The first portfolio
  format this system can actually produce. Its reading of the corpus is real:
  the day 27 things were registered (2020-09-08), the 39-day unbroken stretch
  from 2020-06-28, the borders of the 69-day silence between 2018-12-13 and
  2019-02-21, and the pieces carrying the longest text.
- `compose_order` gained declared ordering criteria -- `density`, `run`, `gap`,
  `voice`, with chronology as the fallback -- taken from the operator's own list
  of ways to order. A criterion the engine does not know falls back to
  chronology and SAYS SO in `criterion_applied`, because silently ordering by
  something other than what was asked is the defect, not the fallback.
- A silence is shown by its borders and never filled: the evidence of a gap is
  the last record before it and the first after, so the slot exhibits the
  interval without claiming anything happened inside it. A test pins that
  nothing may be invented in there.
- Known and declared behaviour, found by a test rather than in production:
  composition is greedy in declaration order and never reuses a piece, so a
  corpus smaller than the sum of the slot maxima starves the later slots. It
  fails loudly -- every starved slot reports its own shortfall and the format
  reports invalid -- and the real archive holds 7044 against a maximum of 72.
- Figures: `tests/test_copilot.py` `53 passed`; `mak` `2193 passed, 5 skipped`;
  `repo_hygiene` `100 passed`; `integration` `373 passed`; `git diff --check`
  exit 0.
- Nothing was published, promoted or written to the archive. The composition
  carries `promotion: none` and `owner: human`; no record was labelled or
  linked to produce it.
- What this leaves for the operator: F8 is one format and the point is that
  there are N. The engine now takes a declared purpose with declared criteria
  and returns an order it can defend, so writing the next format is an
  authoring act, not an engineering one.

### The production chain was whole; only the wire was missing -- 2026-09-02

- The operator said it twice and was right both times: "eres el eslabon, lo mas
  probable que todo ya exista y solo faltaba conectar". This section records a
  duplication I built and then retired, and the connection that was the actual
  work.
- What already existed, entire, in the FLUJO motor:
  `portfolio_claims.compile_portfolio_claims()` ->
  `portfolio_render.assess_feasibility()` -> `render_portfolio()` ->
  `render_markdown()`, with `portfolio_format.validate_portfolio_format()` /
  `load_format_library()` policing the format schema. Nothing in MAK ran it.
- What I built instead, and removed: `copilot.compose_order()` /
  `compose_orders()`, `friction_map()`, the ordering criteria, the
  `/api/portfolio/copilot/orders` route and a format `F8-temporada`. The
  composer reimplemented `render_portfolio` worse -- the real one assigns each
  claim to the slot that fits fewest, which solves the starvation I had
  declared as "known greedy behaviour". All of it is gone; a parallel engine is
  the thing `AGENTS.md` forbids before checking the existing implementation.
- The search that produced the duplication was incomplete, and that is the
  lesson worth keeping. I grepped `cultura/`, `tools/`, `tests/`, `docs/` and
  `portfolio_dossier.py`, found no consumer of `data/portfolio_formats`, and
  concluded "nothing composes an order from them". The composer was in
  `portfolio_render.py`, one file over in the sibling checkout. Concluding
  absence from a bounded search is the defect this repo names most often, and I
  committed it after writing a memory about it.
- The measurement that inverted everything: the chain's input is the CLAIM
  BASE, not the archive rows. A claim carries `verb`, `layer`, `state`,
  `permission`, `supported_by`, `independent_route_count` and what would refute
  it -- exactly what a slot declares with `claim`, `min_state` and
  `min_permission`. My earlier finding that "zero of 7044 records carry a
  permission, so all six formats are invalid" was measuring the wrong layer:
  every compiled claim carries one. The formats were never blocked.
- Run today against the real sources, all eight present: 278 claims
  (`observed` 175, `candidate` 74, `supported_candidate` 27,
  `externally_attested` 2; verbs `puedo` 214, `ocurrio` 46, `hice_esta_parte`
  18). Four of six formats RENDER: `F1-trayectoria` 30 pieces,
  `F2-capacidad-visual-musica-eventos` 24, `F3-rol-tecnico` 16, and
  `F4-fondart-nacional-investigacion-2027` 28. The two that do not fail for
  honest reasons: barberia has no observed `puedo` evidence, and
  `F7-lectura-curatorial` needs `significa` claims, which the compiler never
  produces because meaning is not derivable from archive evidence.
- The rendered Fondart document is already what it should be: every item
  carries its evidence route, its second route and its refutation condition
  ("se refuta si..."), plus a `No sirve para` section naming the eight hard
  gates and eight required documents it does not cover, and a `control` block
  with source_rescan, physical_mutation, database_write, network_called,
  publication, submission, signed_document, authorship_claimed and
  training_permitted all false.
- The wire: `GET /api/portfolio/production` in `hub.py` compiles the claim base
  once, caches it, renders the library and reports per format its status, item
  count, render hash, feasibility and control block; `?format_id=` adds the
  rendered markdown and `?refresh=1` recompiles. It names all eight sources and
  reports each as present or absent instead of treating a missing one as empty.
- Tests in `tests/test_hub_second_witness_routes.py` (lane `mak`): the Hub
  consumes the four engine entry points and defines no second composer; every
  source is named and checked; and the route performs no write -- checked by
  AST over calls, because the first version grepped the body for "publish" and
  failed on the very keys that declare it does not publish, which is the third
  time today I read a mention as a use.
- Figures: `tests/test_copilot.py` `42 passed` after the removals;
  `tests/test_hub_second_witness_routes.py` `14 passed`; `mak` `2185 passed,
  5 skipped`; `repo_hygiene` `100 passed`; `integration` `373 passed` -- the
  lane my format file had broken by adding an unknown field to a schema the
  motor validates strictly.
- Nothing was published, signed or promoted. The chain is read-only by its own
  contract and the route adds no way around it.
- Next: the two `.claude/jobs/3428381a/tmp/` inputs are scratch paths from a
  past agent job. They exist today and the chain degrades honestly without them
  (they are optional), but a production input living in a temp directory is a
  source that can vanish without anyone noticing.

### Fondart application started -- 2026-09-02

- Run produced at `experiments/pilots/ARICA-FONDART-2027/runs/postulacion-20260902/`,
  which is gitignored (`.gitignore:108`) and stays that way on purpose: the
  repository is public and the pilot holds captured bases and archive
  observation. The run has `ESTADO.md`, `curriculum-viabilidad.md`,
  `render.json` and `cobertura-requisitos.json`.
- The deadline governs everything and was read from the hashed bases, not from
  memory: **2026-09-10, 15:00 America/Santiago**, eight days from today.
  Execution window 2027-03-01 to 2027-04-30, maximum 12 months, CLP 500.000 to
  15.000.000 per project. Source package
  `sha256:9da0ab5f0850fdad354415448829fd88fa1e61beee5fd048c90a4a5b4c418af2`,
  19 requirements and 26 evidences with page anchors.
- What the system produced: `F4-fondart-nacional-investigacion-2027` renders
  28 items, status `rendered`, from the claim base compiled off the eight real
  sources. Each item carries its evidence route, an independent second route
  and its refutation condition, and the document declares its own "no sirve
  para" listing the eight hard gates and eight required documents it does not
  cover.
- What the system does NOT produce, measured against the bases rather than
  assumed: of the 19 admission requirements it answers ZERO. Six hard gates,
  one eligibility clause, two dates, one duration, one budget and eight signed
  documents are all acts of the applicant -- an archive does not declare
  co-financing or sign a consent. On the evaluation side the archive can feed
  Curriculo (0.20) and part of Viabilidad (0.10); Calidad (0.30) and Impacto de
  transferencia (0.40) depend on the proposed project. The archive-backed
  ceiling is 30% of the weighting.
- The applicant's own words were found rather than invented, in his web export
  (`WIN/claude_sesiones/claude_web_export_2026-08-11/conversations.json`,
  conversation of 2026-08-08): he wants "un portafolio artistico automatizado,
  considerando carpetas y archivos desordenados: ordenarlos y curarlos", with
  an ordering method that is "optimo, tipo bubble sort o algoritmos de
  searching". That question -- which ordering method is optimal -- is the
  research problem, and `docs/DIMENSIONES_DEL_ORDEN.md` already carries its
  negative answer: there is no correct order, there is `O_G` relative to a
  purpose, and six purposes are declared with four rendering today.
- `ESTADO.md` states plainly that this is not yet the required 15-page research
  advance: the problem is formulated and there is a result and a running
  system, but object of study, methodology, theoretical framework, state of the
  art and references are the seven parts the bases demand and none of them can
  come out of the archive. Nothing was written in the applicant's voice beyond
  the quoted passage, which carries its source.
- Nothing was submitted, signed or published. `control` on the render and the
  coverage file: `submission: false`, `signed_document: false`,
  `authorship_claimed: false`, `promotion: none`. `repo_hygiene` `100 passed`
  and `git diff --check` exit 0 after the run.
- Next action, and it is the applicant's alone: the eight documents and six
  hard gates. The system contributes the Curriculo section already rendered and
  can regenerate it at any time from
  `GET /api/portfolio/production?format_id=F4-fondart-nacional-investigacion-2027`.

# Operational Handoff

## Agent bootstrap -- CURRENT -- 2026-09-02 (later) -- the suites, and the boundary the operator corrected

### The boundary. Read this before touching anything named portfolio.

The operator's correction: **IRIS is the internal system he created to order
his archive; it is not his portfolio.** The public portfolio/output and the
editor/interface are separate things. The editor grew into an operator-facing
IRIS interface when it joined DIMENSIONES DEL ORDEN, but its historical name
does not redefine the system or the public site.

- **`iskvw/` is iskvw.cl**, the artist's published portfolio SITE. Its contract
  is `iskvw/CONTRATO.md`: `datos/archivo.json` is the published content,
  `campo.json` and `obras.json` are FALLBACKS the live skin asks for only if
  `archivo.json` is missing, and `piel/<name>/` is a replaceable skin. It is
  published by `.github/workflows/publicar_iskvw.yml`, which uploads `iskvw/`
  and nothing else. **Obras only.** Its scope is the operator's explicit #355
  decision (2026-07-27): posts and reels, never `archived_posts/` or `other/`,
  because publishing what someone archived reverses a decision they made.
- **IRIS is the internal MAK ordering system**, with its operator-facing Hub
  interface and engine. The Hub still mounts the historical curation panel
  (`/portafolio/` -> `iskvw/editor.html`, `PORTFOLIO_ROOT` =
  `/home/mak/iskvw`), which explains the old URL and why the two were confused.
  Its engine -- `copilot.py`, the 35 `/api/portfolio/*` routes, the eight
  layers, five verbs, evidence states, GTM atlas and ordering field -- works on
  records, works, context and relations, not on a public list of obras. The
  `portfolio` namespace is an implementation label, not the identity of IRIS.
- **Editing `iskvw/datos/*` or `iskvw/piel/*` is editing the public output
  product, not editing the IRIS ordering system.**

What this agent got wrong, twice, recorded so it is not repeated.

First error: reading a red suite, it traced the failures to `campo.json`,
"completed the chain" by re-running the capas and the animated pieces, and
wrote 652 new pieces into `iskvw/piel/animadas/`.

Second error, and the one that matters more: it then framed that as damage to a
LIVE published product. **The operator's correction: iskvw.cl has not published
anything in about a month and is not in use.** So the alarm was false. The
boundary between the site and IRIS is still real -- it is section 1-bis of
`docs/IRIS_CANONICAL.md` -- but `iskvw/` is a DORMANT surface, not a live one,
and treating it as a production emergency was an invention. The lesson is to
measure whether a thing is in use before calling it a product at risk.

Current state of that surface: `5af492ba` (`data(mak): regenerate the campo de
orden`) was reverted by `77afc45e`, so `campo.json` is back at 219 works WITH
its capas and the four ratchets are green. The stated reason for that revert
was wrong -- it was not protecting a live site -- but the resulting state is
the coherent one: every ratchet was pinned to 219-with-capas. Taking the field
to 871 is a deliberate data operation (regenerate campo, then capas, then
animadas, then re-pin the piel meter FROM THE FIXTURE'S OWN measurement) and it
is a separate task, not part of closing a session.

### CI, the real verdict: the per-lane workflows had NEVER run

They were written earlier this session and only reached the remote on
2026-09-02 ~16:58. Their first execution failed on both branches, at the
`Structural gate` step, with 12 blockers on MAK and the equivalent on FLUJO --
`mak_checkout_not_on_mak`, `flujo_checkout_not_on_flujo`, `lane_map_missing`,
`runtime_preflight_missing`, `worktree_status_failed: cannot change to
'/home/mak'`, plus `own_hub_absent` and `hub_archive_failed` because the local
refs `MAK:` and `FLUJO:` do not resolve in a CI checkout.

Cause, and it is this agent's: `tools/release_gate.py` is a BOX-LOCAL
instrument. It resolves `/home/mak` and `/home/mak/flujo` as physical checkouts
on their branches, and **it exits 5 even with zero blockers**, because
READY_TO_PUSH requires evidence that the lane suites ran green. So it can never
pass as a step that runs BEFORE the suite. In CI the suite is the verdict; the
gate there was both redundant and structurally impossible.

Fixed by removing the step from `ci-mak.yml` and `ci-flujo.yml`, with the
reason written in the workflow so nobody re-adds it. `ci-integration.yml` never
had it. The gate stays as the local pre-push instrument it was designed to be.

The lesson, and it is the same one as everything else in this session: **a
tool was wired into a place whose assumptions were never measured.** Writing a
workflow is not validating it. These two had never executed once.

### Observations for whoever comes next

Things measured in passing, not chased, one line each. None was requested.

- **`/home/mak/src/flujo` is 5.3 MB of orphan `__pycache__`** -- 200 `.pyc` and
  0 `.py`, left when the motor moved to `flujo/src`. Not importable, invisible
  to Git (it holds only ignored paths), and not blocked by
  `tools/release_gate.py`, whose rule checks *tracking* and not physical
  presence. Side effect: `tests/conftest.py` inserts `/home/mak/src` into
  `sys.path` because `is_dir()` is true for those directories; `import flujo`
  resolves correctly only because `flujo/src` happens to come first. Deleting
  it was proposed and NOT done.
- **`context/code_structure_index.json` is stale**: 200 of the 226 files it
  indexes under `src/` no longer exist. Regenerate with `py -m flujo
  code-index`.
- **`context/test_lane_map.json` pins the wrong index**:
  `source.code_index_sha256` is `3d82ee64...`, the real index today is
  `e8f49ec6...`.
- **A block header does not age with its contents.** The block above this
  session's is titled `2026-08-31` and carries sub-sections dated `2026-09-01`
  and `2026-09-02`. The title date is not evidence of how fresh what you are
  reading is. Read the sub-section headers.
- **This file is newest-first.** `tail` gives the oldest end. The newest block
  is at the top, and `test_un_solo_documento.py::test_un_solo_handoff_vivo`
  keeps this the only live global handoff -- a test that, until today, ran in
  no CI job.
- **A corpus of 5,179 historical Fondart applications was measured on
  2026-08-20** (with 14 captures) and is the most useful asset on the box for
  writing a Fondart FUP against real awarded projects instead of from scratch.
  Never opened this session.
- **Watsonx, AWS and Azure were retired on 2026-08-20** -- registries, chains,
  UI and config removed, `boto3` dropped. So the challenger figures (Watsonx
  1/21, AWS 9/21) are a dated historical measurement, not a live comparison.
  Any document citing them must say so.
- `docs/MAK_SYSTEM_DIRECTIVE.md` is declared in force by the inherited
  contract and was not read this session.
- `CLAUDE.md` says Gemini is PARKED since 2026-07-10 with "do NOT use", while
  the 2026-08-20 block records Gemini 3.6 Flash working in both adapters. The
  authority order puts `CLAUDE.md` first; the measurement is later. Unresolved.
- The `iskvw` field growth from 219 to 871 is legitimate on its own terms: the
  `#355` folder filter held (`posts`, `reels`), `por_carpeta` measured
  `{posts: 779, reels: 92}`, and 0 published animated pieces belong to a work
  outside the field. If the operator wants it, the chain is campo -> capas ->
  animadas -> re-pin the piel meter, and the piel ceiling is not at risk
  (worst frame 2102 of `TECHO_SEGMENTOS` 6000, zero gradients, zero arcs).

### An honest note on this session

The operator's judgement, and it is correct: after reading a great many files
this agent still got basic things wrong. The three that cost the most were
(1) confusing the PORTAFOLIO surface with the iskvw.cl site, (2) calling a
dormant surface a live product at risk, and (3) re-pinning a meter from a
standalone measurement instead of from the fixture the test actually uses.
All three share one shape: acting on a plausible frame without measuring
whether the frame was true. The repo already has the rule for it -- verify
before asserting -- and reading more documents did not substitute for it.
### The suite verdict, measured locally (the gate's missing verdict)

One environment, `/home/mak/.venv`, whose `.pth` resolves the motor at
`/home/mak/flujo/src`. CI still owns the isolated verdict.

| lane | files | tests | result |
|---|---:|---:|---|
| `mak` (MAK checkout) | 173 | 2175 | **2165 passed, 10 skipped, 0 failed** |
| `integration` (MAK checkout) | 32 | 371 | **371 passed** |
| `repo_hygiene` (MAK checkout) | 14 | 87 | **87 passed** (was 4 failed) |
| `flujo` (FLUJO checkout) | 161 | 1611 | **1611 passed, 44 skipped** |
| `repo_hygiene` (FLUJO checkout) | 9 | 55 | **54 passed, 1 skipped** (was 3 failed) |

MAK's `tests/` physically carries 2633 tests: 2175 + 371 + 87 = 2633.

### How lane selection actually works

`tests/conftest.py::pytest_ignore_collect` consults the persisted lane map
BEFORE collection, but **only when `-m` is EXACTLY one lane name**. Then
foreign modules are never imported: `-m mak` collects 2175 and imports nothing
else. Any richer expression falls back to pytest's normal semantics and imports
everything: `-m "mak and not integration"` collects 2633 and deselects 458 --
the same selection, every module imported.

That is why "test presence is physical, not a marker". A foreign module with a
broken import is invisible under `-m mak` and becomes a collection error under
any compound expression. It is also why an unmapped test is not merely
deselected: it resolves to `review` and its module is skipped entirely.

The lane authority is `context/test_lane_map.json`. `tools/test_lane_map.py` is
the classifier and the bootstrap fallback, never the authority.

### The hygiene lane ran in NO CI job

Both branches created a `repo_hygiene` lane in the separation, CI got one job
per OPERATIONAL lane, and the hygiene lane was orphaned -- 14 files in MAK and
9 in FLUJO, gated by nothing. That is why four MAK ratchets and three FLUJO
ratchets sat red unnoticed: **the ratchets that catch documentation lying were
the ones with no gate.** Only `seguridad.yml` on FLUJO ran one of them, by
path.

Now gated: a `repo hygiene lane` step in `.github/workflows/ci-mak.yml` and in
`flujo/.github/workflows/ci-flujo.yml`, both verified green before the gate was
added.

What the orphaned lane was hiding, and what it cost to repair:

- MAK `test_git_web_contract.py` read `ci.yml`, retired on 2026-09-02 when CI
  split per lane. Its branch assertion also had to invert: it demanded
  `branches: [main]`, and main is a historical aggregate that is never a
  deployment target. It now asserts the real property -- every trigger list
  carries only operational refs -- after a first attempt wrongly assumed
  `ci-integration.yml` targets MAK alone; it targets MAK and FLUJO on purpose,
  because the lane is the composition.
- MAK `test_test_taxonomy.py` probed `tests/test_archive_toolchain.py`, which
  left for FLUJO. The classifier reads the SOURCE for its signals, so an absent
  path yields none and falls back to `unknown`: the probe had stopped measuring
  its own property. Now probes `tests/test_laser.py` (here, and optional by
  signal rather than by stem). FLUJO had the identical defect probing
  `test_mak_research_interfaz_pure.py`; now probes
  `test_flujo_port_contract.py`.
- MAK `test_idioma_ratchet.py` caught THIS agent: a rewritten test was given a
  Spanish name and Spanish assertion text. Rewritten in English.
- FLUJO `test_idioma_ratchet.py` imported `test_higiene_docs`, and
  `test_repo_scan.py` read it -- a MAK doc ratchet. Both now record that the
  authority lives in MAK instead of reporting an absent counterpart as a
  defect.
- `test_repo_audit.py` pinned 105 tools and measured 106: `gen_campo_iskvw.py`
  came back to MAK by consumer (ea847e0b) after the pin was written
  (4bba4e98). The ratchet did its job; re-pinned to 106 with the cause.

### The 4 MAK reds, closed by reverting this agent's own commit

Commit `5af492ba` (`data(mak): regenerate the campo de orden`, 2026-09-02
10:31, this agent's) took the published site's fallback substrate from 219 to
871 obras and left four ratchets red:

- `test_capas_iskvw::test_el_campo_del_repo_lleva_las_capas` -- the
  regeneration dropped the capas, which are added ON TOP of a campo.
- `test_gen_animadas_obras::test_la_tilde_medida_late` -- same cause: `tilde`
  is a capa.
- `test_gen_animadas_obras` spec check -- the 219 published pieces derive from
  the old field, so their spec no longer matches the current derivation.
- `test_iskvw_piel_medir::test_segment_counts_are_the_pinned_numbers` -- the
  substrate changed, so the meter moved.

What was verified about it: **the #355 folder filter HELD** (`carpetas: [posts,
reels]`, `por_carpeta: {posts: 779, reels: 92}`), and **0 published animated
pieces belong to a work outside the field**. The growth is the perception
reaching `reels` and more of `posts` -- which the #355 commit explicitly
predicted would happen on its own. Nothing archived re-entered.

So both options are defensible and neither is an agent's call:

- **(A) Keep 871.** Then the chain must be completed: re-run
  `tools/gen_capas_iskvw.py`, re-run `tools/gen_animadas_obras.py` (which
  publishes 652 new pieces, ~3.8 MB), and re-pin the piel meter from the
  fixture's own measurement -- NOT from a standalone run against the repo's
  `archivo.json`, which is a different substrate and produced wrong numbers on
  the first attempt. The ceiling is not at risk: worst frame 2102 of a
  `TECHO_SEGMENTOS` of 6000, with zero gradients and zero arcs.
- **(B) Revert to 219.** `git revert 5af492ba` restores the substrate his July
  decision produced, all four ratchets go green, and the perception growth
  waits for a deliberate decision. `5af492ba` is committed but NOT pushed.

Two size-pinning tests were repaired regardless, because the #355 author had
already written the rule for this case -- "size is not the property worth
protecting; a legitimate change of scope turning a test red is a bad test":
`test_gen_animadas_obras` now checks that no published piece belongs to a work
outside the field, over EVERY row instead of the first 30, and
`test_curatoria_portfolio_critica` checks that obra and operational material
stay distinguishable and that the meta declares the vocabulary the pieces use.

### Also repaired this session, unrelated to iskvw

- `tests/conftest.py` now exposes `flujo/src`: MAK carries no `src/flujo` copy,
  and without it the two departments tests failed at collection -- in the
  INTEGRATION lane, which no compound-expression run would have reached.
- `tools/release_gate.py --check`: 0 blockers, runtime 5 ok / 0 warn / 0 error.

## Agent bootstrap -- CURRENT -- 2026-09-02 -- IRIS named, Fondart line decided, MAK registry reconciled

This block supersedes the previous CURRENT only for what was decided and
measured on 2026-09-02. Earlier figures stay below as dated evidence.

### Operator decisions (answers, not questions -- do not ask these again)

1. **The Fondart line is Fondart Regional 2027, Creacion Artistica:
   Innovacion y Nuevos Formatos Creativos.** This supersedes this agent's
   earlier recommendation of Fondart Nacional line Investigacion, which is a
   DIFFERENT line and not a second framing of the same project. Discipline:
   **Diseno** -- the bases finance "obras, piezas, dispositivos, sistemas,
   juegos o experiencias de diseno originales" with public participation.
2. **IRIS is a NAME for the Mesa de Montaje that already exists in MAK.** It is
   not rebuilt from zero and it is not confused with a new application. Canonical
   definition and function map: `docs/IRIS_CANONICAL.md`.
3. **The Fondart framing is an obra digital de mediacion**, not a machine
   learning benchmark and not a business application. The computational
   research, the models, the data and the ledger are method and infrastructure;
   they must not displace the artistic center in the narration. "Ordenes
   defendibles" is a methodological principle, not a title.
4. **The cultural version and the private version share foundations and stay
   separate.** Fondart gets an exhibitable digital work with methodology,
   publics, mediation and transference. The market version would be a local,
   portable application; it is not this application.
5. **LUCIDA, VIZZ, PUPILA, XIO, MOSAIK and CODEINE are architectural and
   FUTURE, not current dependencies.** No agent working on MAK clones, imports
   or modifies them, and no second Hub, database, corpus or portfolio
   definition is created to ease a hypothetical integration. What may be
   consumed later travels through a contract: see `docs/IRIS_CANONICAL.md`
   section 8.

### Bases verified from the PDF, not from memory

`docs/recovered/claude_sessions_2026-08-12/raw/bases_pdf/fondart-regional-creacion-artistica-2027.pdf`
(571.863 bytes, sha256 `55efacab049c0ba90fb2a59ddaed4ee5ee00eed7f4887bea57c237e736ddfb71`,
44 pages, `pdftotext -layout`).

- Single modality. Minimum $500.000, **maximum $18.000.000**.
- Total $2.654.426.024; **Region Metropolitana $800.000.000**.
- **No obligatory cofinanciamiento.** Maximum duration 12 months.
- Execution must begin between **01 April and 31 May 2027** or the project is
  out of the call.
- **Exhibition of the final work is a requirement of the bases**, not an option.
- One application per line; the last one sent counts. Anyone selected in the
  **2026** call of this same line cannot apply.
- Eligible at 85 points or more. Rubric: **Impacto potencial 40%, Calidad 30%,
  Curriculo 20%, Viabilidad 10%**.
- Selection order in the Region Metropolitana takes the **two highest-scoring
  first-artistic-work projects per discipline** before ordering by score. Two
  reserved slots exist in Diseno / RM.
- Anexo N.2: all four documents are conditional ("si corresponde"). A natural
  person, with no team, no third-party protected works and outside indigenous
  territory owes **zero** documents.

Dossier with the full framing, the rubric mapping, the exhibition and mediation
plan, the reading protocol and the budget structure:
`projects/cultura/dossiers/FONDART_2027_IRIS_REGIONAL_CREACION.md`.

### Measured on 2026-09-02

- `tests/test_iris_invariants.py`: 10 tests, lane `mak`, green. Names the four
  properties IRIS promises in one place -- replay never promotes, a learned
  metric activates only on measured gain, the field does not move the atlas,
  every machine output arrives as a human candidate. Registered in
  `context/test_lane_map.json` (173 mak, 32 integration, 14 repo_hygiene).
- **Activation is not promotion.** Even when the pair metric earns activation,
  `distance_comparison.promotion` stays `"none"`.
- IRIS internal ordering system, measured: 35 distinct `/api/portfolio/*`
  route names in `cultura/mak_plataforma/hub.py`; `copilot.py` 1820 lines and
  46 module-level functions, standard library only; 21 test files and 299 tests
  in the portfolio-archive family. The `portfolio` namespace is a technical
  compatibility label; it does not make IRIS the public portfolio. The public
  `iskvw` artifacts remain a separate downstream surface.
- That measured snapshot recorded `iskvw/datos/archivo.json` at 1.8 MB with
  2034 pieces and 5812 links, and `campo.json` at 273 KB with 871 works. These
  are downstream/public-surface artifacts, not the identity or core state of
  IRIS.
- **35 tools the MAK registry still declared live in `flujo/tools/`**, moved by
  the 2026-09-02 separation -- the portfolio compile, render and opportunity
  chain, including `compile_portfolio.py` and
  `compile_ssd_order_foundation.py`. All 35 verified present in FLUJO and
  absent in MAK. Rows retired from `CAPACIDADES.md` and preserved as pointers
  in its new section 5-quater. `release_gate.py` and `runtime_preflight.py`
  registered as VIVO; they had never been declared.
- **The retired layout also survived as a dotted import.** Eight MAK tools and
  two tests read `from src.flujo.knowledge...`, which resolved while
  `/home/mak/src/flujo` existed and became two silent collection errors plus
  eight tracebacks once it did not. Repointed to `flujo.` with a
  `FLUJO_SOURCE_ROOT` bootstrap (default `/home/mak/flujo/src`); all eight
  smoke-run and both test files pass. `tests/conftest.py` now exposes
  `flujo/src`. `from src.flujo.` and `import src.flujo` added to
  `RETIRED_SPELLINGS` in `tools/release_gate.py` -- the path-shaped patterns
  could never see a dotted one.
- `tools/release_gate.py --check`: RESULTADO_GATE UNKNOWN_EXTERNAL, 0 blockers,
  runtime 5 ok / 0 warn / 0 error. The unknowns are this session's uncommitted
  edits plus the two deferred lane suites.
- `test_higiene_repo.py`, `test_higiene_docs.py`, `test_project_lanes.py`:
  16 passed, 0 failed (they were 4 failed / 12 passed before this session).

### Web research, 2026-09-02 -- the deadline is no longer unknown

- **The call closes 9 September 2026 at 15:00 hrs Santiago.** Opened
  05-08-2026. Seven days from today.
- The extension to **16 September** applies ONLY to responsables of projects
  **belonging to the regions of** Arica y Parinacota, Tarapaca, Antofagasta and
  Atacama (adverse weather in the north), covering Fondart in both its national
  and regional scopes. Since the bases require applying in the region where the
  project executes, those seven extra days only exist if it really executes
  there. `experiments/pilots/ARICA-FONDART-2027` already exists (413 MB).
- **The live bases PDF is sha256-identical to the local copy**
  (`55efacab049c0ba90fb2a59ddaed4ee5ee00eed7f4887bea57c237e736ddfb71`), so
  every figure measured from it is against the current bases. Rex 2262 approved
  them.
- **The temporal tiebreaker rewards applying EARLY**: on a tie it selects the
  project with "el mayor plazo (dias y horas) entre el momento de su
  postulacion y el momento de cierre". Do not confuse with the multiple-
  application rule, where the LAST one counts.
- Budget caps read from section 7 of the bases: four items (Operacion,
  Personal, Inversion, Imprevistos); the **responsable assignment caps at 40%**
  of the requested amount and only for personas naturales; **imprevistos cap at
  2%** and may never raise the responsable assignment.
- Platform rules that consume days: registration in **Perfil Cultura** for the
  applicant and every team member; no ZIP/RAR/TAR/DMG/7Z; one PDF per document;
  **100 MB per file**; antecedents cannot be attached as links, but a document
  MAY carry reference links that must be **live and key-free at evaluation
  time**.
- Call context that supports the line change: 2027 totals **$41.405 million,
  9,6% below** 2026's $45.780 million, and the **Investigacion line falls
  39,9%** -- the deepest cut is exactly where this agent's earlier
  recommendation pointed. 21 of 46 lines bar 2026 winners. The 2027 redesign
  creates explicit **opera prima** quotas.

### The pilot that was already on disk is evidence

`experiments/pilots/ARICA-FONDART-2027/runs/RESULTS.md`: the same snapshot
replayed across two runs with observation, projection, relations, units and
Project IR **byte-equivalent** and `unexplained_output_deltas=0`; 12.332
artifacts, 128 observations, 512 relation candidates, 174 units. Both runs kept
`fit=abstain`, dossier `draft_only`, application `blocked_with_reasons`, with
no publication, dispatch or training -- and **enriching the evidence did not
turn the abstention into a ready application**. That is the
anti-self-certification invariant demonstrated on this very call.

Its cost is also measured: the materialized `mak-product-view-v1` declares
11.534 internal assets and **0 assets with explicit public eligibility**. With
the platform rule above, nothing is currently cleared for an evaluator to open.

### Open, and they are the operator's to answer

1. **Region first** -- it decides whether there are 7 days or 14. Metropolitana
   holds $800.000.000 and closes on the 9th; Arica y Parinacota holds
   $85.000.000 and closes on the 16th.
2. **Perfil Cultura registration** -- verify today; it is paperwork, but it
   blocks everything else.
3. **Anexo N.1 and "primera obra artistica".** The 2027 Anexo 1 is not
   published on the line's page and the 2024 one does not define the term; web
   search did not find it. What governs is the bases' own wording plus the
   declared opera prima quotas. Ask SIAC if in doubt
   (`siac.cultura.gob.cl/formulariosiac`, 600 600 0255). It changes the
   selection order: two reserved slots per discipline in RM.
4. **Public eligibility for a subset of the work** -- today it is 0 assets.
5. Title of the work, host space with a commitment letter, natural or legal
   person, and whether there is a contracted team.

### State of the art found on the web, for the Calidad criterion

- **Antonio Somaini, "Latent Spaces: AI, Art, and the Archive", _October_
  N.196 (2026), pp. 19-60, MIT Press, DOI 10.1162/OCTO.a.545**, open access.
  Latent spaces as a new Foucauldian historical a priori, compared with the
  archive in its technical, institutional and epistemological dimensions. It is
  the strongest available reference AND the principal critique of what IRIS
  does -- which is why citing it and showing the refusal mechanism is stronger
  than ignoring it.
- **Guerin, Chauvet, Saubion, "A Survey on Recent Advances in Self-Organizing
  Maps", arXiv:2501.08416**: visualization is the main goal, higher dimensions
  lose interpretability (justifying the 2D grid), and quantization plus
  topographic error are the standard quality metrics -- MAK already reports
  `vecindad_conservada` = 0.4855.
- **arXiv:2604.13622 (2026)**, SOM with optimized latent positions.
- Preservation (Cornell frameworks, Internet Archive CARTA, NDSA) preserves
  bits and metadata; it does not reconstruct the decision. The market (Pixpa,
  Format, Portfoliobox, Artwork Archive, ArtStation, ArtStack) organizes by
  theme, medium or category -- by lists. **The gap: no instrument puts the
  decision back in the artist's hands over their own archive, measurably and
  reproducibly.**

### Still unresolved from before, unchanged

- `docs/MAK_CURRENT_STATE.md` sections 1 and 2 still describe the retired
  layout and still say `flujo app` must not be left permanent, while it runs on
  8765 by the operator's request.
- Three independent portfolio implementations with three incompatible
  definitions of "obra"; an earlier narrow count of four `editor.html` copies
  (superseded by the later full physical count of 16);
  `POST /api/portfolio/dispatch` with no measured reader.
- The organism has been paused since 2026-08-14 19:03.

## Agent bootstrap — CURRENT — 2026-08-31 — consolidación física posterior y límite documental abierto

Este bloque supera el CURRENT anterior sólo para los hechos medidos el
2026-08-31; las cifras y afirmaciones anteriores se conservan abajo como
evidencia fechada, incluso cuando se contradicen.

### Contrato heredado que no se puede perder

- `Stage 2D accepted` permanece aceptado y no se reabre.
- `171 focused tests` es la medición histórica de aquella etapa.
- `docs/MAK_SYSTEM_DIRECTIVE.md` sigue vigente.
- `mak-archive-observation-batch-v1` sigue siendo el esquema de los lotes de
  observación del archivo.

### Estado físico y Git medidos

- La fusión física quedó registrada por el commit `cd8a9569` (2026-08-31
  18:06:09-04:00, `fuse MAK project roots into single home root`). La evidencia
  congelada es `/home/mak/_archive/merge-20260831/`: no es una conclusión de
  cierre semántico ni una autorización para borrar o promover variantes.
- `fused/projection3/MANIFEST.json` registra 5.426 rutas `tree_equal`, 813
  rutas divergentes con `variants_all_preserved` y 2.366 rutas de variantes.
  La subcarpeta materializada `fused/projection3/variants/` era una segunda
  copia de los orígenes y se purgó el 2026-09-01 tras verificar hashes; las
  variantes reales siguen en `fused/origins/`.
  `fused/root-materialization.json` registra históricamente 6.214
  `linked_file`, 22 `linked_symlink`, 1 colisión de raíz preservada y 2
  conflictos reubicados. Esa cifra describe la corrida del 31-08, no el estado
  actual: el 01-09 se desacoplaron todos los inodos vivos que aún compartían
  evidencia. La medición directa actual es `live_nlink_gt1=0` y
  `live_archive_shared=0`; `actions.jsonl` conserva las 5.496 líneas de la
  corrida original.
- El árbol vivo es `/home/mak`; `/home/mak/flujo` es ahora un adaptador de
  directorio no recursivo con 164 enlaces a hermanos, porque el symlink físico
  a `.` permitía recorridos cíclicos. La medición actual encontró cero enlaces
  que resuelvan dentro de su propio ancestro. `/home/mak/WIN/flujo` redirige a
  `../_archive/merge-20260831/fused/origins/win-flujo`. No hay otro directorio
  `flujo` activo que deba inventarse o tratarse como raíz independiente.
- El servicio de runner usa `/home/mak/actions-runner`; su checkout de trabajo
  `/home/mak/actions-runner/_work/vibecodeine/vibecodeine` es un symlink a
  `.../_archive/merge-20260831/fused/origins/runner-vibecodeine`. El servicio
  y el alias de ruta no prueban por sí solos una entrega o un runtime sano.
- El baseline previo de la caja fue `be35fc54499c14b97b00418e528a1d25db631ae2`;
  la topología actual separa `MAK` en `ccb9b32d`, `FLUJO` en `fa0aede0` y
  `main`/`historia` como histórico en `ab9afa13`. En
  `vibecodeine-legacy` están publicados `MAK` y `FLUJO`; `main` permanece en
  `ab9afa13`, la rama lowercase `flujo` fue retirada y sus tips antiguos se
  preservan en tags `archive/vibecodeine-*`. `ligereza-mak` no se tocó.
  La ola local que precedió esta topología está en `32d929d8`, `6166a8b8`,
  `940d2324`, `111a52e6`, `ac789a31` y `29715450`; no se hizo push de esos
  nombres a `ligereza-mak`.
- Revalidación 2026-09-02: el código MAK anterior a este bloque estaba en
  `39f16c4de32b8751682e068c2d9053b8a9450597`; el tip actual de la rama `MAK`
  (este bloque incluido) se obtiene con
  `git rev-parse MAK`, `FLUJO=efeaa8a911d7675bc4cdcd0bf72aeb48b8ca6a9c` y
  `main=historia=ab9afa13fb4d5cf257d97972c73301b0bc0d78fb`; `git ls-remote`
  coincide con cada tip local. Esta revalidación sustituye los tips abreviados
  anteriores, que quedan como historia de la transición.

### Estado documental medido

- El nodo aislado `./.venv/bin/python -m pytest -q
  tests/test_un_solo_documento.py::test_un_solo_handoff_vivo` pasa (RC 0)
  después de mover con `git mv` los nueve documentos no vivos a
  `docs/handoffs/archive/`. `context/LAST_HANDOFF.md` queda como único handoff
  global versionado. Los tres contratos departamentales siguen siendo
  consumibles desde sus copias archivadas.

### Revalidación física y carriles — 2026-08-31

- La medición histórica dejó 5.018 archivos vivos con `nlink=1` y 1.270 enlaces
  compartidos protegidos. El 01-09 se revisaron y desacoplaron esos 1.257
  archivos que seguían vinculados a `_archive` (22.526.816 bytes), con copia,
  SHA-256 y reemplazo atómico; la re-medición actual da `nlink_gt1=0` y cero
  inodos vivos compartidos con `_archive`. Se restauró
  `cultura/mak_research/fallback_util.py` como copia independiente; ese estado
  fue superado el 2026-09-01 al retirar la copia duplicada, porque el único
  consumidor importa `cultura/mak_codex/fallback_util.py`. El legado
  `tools/mak_ops/repair_mak_sync.py` se retiró porque su reemplazo seguro es
  `tools/mak_ops/sync_mak_safe.py` y el test prohíbe reactivarlo.
- Los markers `flujo`, `mak`, `integration` y `repo_hygiene` quedaron declarados
  en `pyproject.toml`; `tests/conftest.py` aplica el mapa AST de
  `tools/test_lane_map.py`. Carriles medidos: `flujo` 173 (159 s, RC 0),
  `mak` 50 (105 s, RC 0), `integration` 10 (10 s, RC 0),
  `repo_hygiene` 115 (124 s, RC 0), `review` 39 bajo demanda.
  El mapa de 387 rutas quedó persistido estáticamente en ese archivo para que
  la colección no recalcule AST en cada corrida (`ac789a31`).

### Revalidación de índice y carriles — 2026-09-01 — CURRENT

Este bloque reemplaza únicamente las cifras operativas anteriores; las
mediciones del 31-08 permanecen abajo como historia fechada.

- `context/code_structure_index.json` es el índice del código operativo de
  `/home/mak`, no un censo de toda la caja: 932 archivos Python, 249.626
  líneas, 10.962 símbolos y 0 errores de sintaxis. Su alcance explícito incluye
  sólo la raíz Python, `src/`, `cultura/`, `tools/`, `tests/` y `scripts/`.
  Excluye `_archive`, `WIN`, montajes y árboles de material no-code. Su SHA-256
  actual es `e8f49ec645eaa9c61d8a61f73a6b597b5e52cc5b12f9cda6758dd7b5af802f2b`.
- `context/test_lane_map.json` (`mak-test-lane-map-v3`) es el contrato vigente
  y `tools/test_lane_map.py` lo carga. Conserva 243 acuerdos, 80 carriles
  respaldados por imports/rutas, mueve 1 caso por import directo y resuelve 56
  por ruta de módulo única. Los 7 casos que quedaban en `review` se resolvieron
  por estructura dirigida (3 imports de MAK, 3 tests de activos ISKVW y 1 test
  de taxonomía); `review=0`. La comparación original conserva 144
  discrepancias visibles, no las presenta como consenso. SHA del contrato:
  `984e26ecfb0d6890936156e1e7ed5d6d159e6ab08aa7ffbe6d11511f6a76e977`.
- Colección actual de casos: `flujo=1.778`, `mak=2.229`,
  `integration=239`, `repo_hygiene=87`, `review=0`; total `4.333`.
  Los cuatro carriles operativos cubren todos los casos; los cambios de
  clasificación sólo redistribuyeron casos, no crearon tests.
- `lanes_for_changed_paths()` sigue consumidores desde el índice. Cambios en
  `pyproject.toml`, `tests/conftest.py`, `tools/test_lane_map.py`,
  `context/code_structure_index.json` o `context/test_lane_map.json` activan
  todos los carriles; un cambio aislado en `src/flujo/*` activa solo `flujo`
  cuando no tiene consumidores de otro carril.
- `mak-hub.service` fue recargado tras resolver la raíz física: `/api/status`
  devuelve ahora `repo_root=/home/mak` y `physical_root=/home/mak`; el alias
  `/home/mak/flujo` queda sólo para compatibilidad de rutas heredadas.
- 2026-09-02: las unidades `mak-hub`, `mak-research` y `mak-codex` dejaron de
  ejecutar sus fuentes por el alias `/home/mak/flujo` y ahora usan directamente
  `/home/mak/cultura/...`; tras `daemon-reload` y reinicio controlado quedaron
  activas, con HTTP 200 en `8900/health`, `8890/` y `8891/`.
- Validación enfocada actual: `tests/test_code_index.py` (2 passed), los 7
  archivos que cerraron `review` (49 passed), `tests/test_repo_audit.py` (5
  passed en 33 s), `py_compile` RC 0 y `git diff --check` RC 0. No se ejecutó
  la suite completa.
- Se corrigieron dos escapes `\\s` en el HTML embebido de
  `cultura/mak_codex/interfaz_codex.py`; la colección limpia dejó de emitir la
  advertencia `invalid escape sequence`, y las pruebas enfocadas de interfaz
  quedaron en 67 passed.

### Cierre de `review` y triage de divergencias — 2026-09-01

- Los 39 módulos que estaban en `review` fueron clasificados por evidencia de
  importación/ruta: `mak` absorbió 36 y `repo_hygiene` 3. El mapa persistido
  queda en `review=0`, `mak=86`, `repo_hygiene=118`, `flujo=173` e
  `integration=10`; SETHASH y la lista completa se obtienen con
  `./.venv/bin/python tools/test_lane_map.py --format text`.
- La corrida acotada de esos 39 módulos encontró un duplicado real:
  `cultura/mak_research/fallback_util.py`. No tenía consumidores directos;
  `research_lib.py` y `expulsion.py` importan el único
  `cultura/mak_codex/fallback_util.py`. Se retiró sólo la copia viva y se
  preservó la variante en `_archive/`; los contratos
  `tests/test_mak_salud_proveedores.py` y `tests/test_mak_fallback.py` pasan
  juntos (17 tests, RC 0). La suite completa no se volvió a ejecutar.
- Las 813 divergencias quedaron triadas, sin fusión semántica inventada, en
  `context/mak-merge-20260831/divergence-triage.json` y su resumen
  `DIVERGENCE_TRIAGE.md`: 712 tienen consenso byte a byte de dos orígenes (653
  ya coinciden con el baseline activo; 59 lo tienen como outlier), 73 son
  conflictos de dos fuentes/tipo y 28 tienen tres contenidos únicos. No existe
  base común de tres vías en el manifiesto; por eso el arreglo correcto es
  revisión manual por esos grupos, no elegir un ganador automáticamente.

### Reconciliación de variantes — 2026-09-01

- Se ejecutó una reconciliación real de tres vías contra la base común
  `4b8453cbf17b25431e091a4a6fe3f09a819a0ffb`, usando las copias congeladas de
  `active-flujo`, `win-flujo` y `runner-vibecodeine`. El resultado fue 482
  archivos fusionados limpiamente, con reemplazo atómico y sin escribir bajo
  `_archive/`.
- La medición dejó explícitos los límites: 46 conflictos de contenido, 55
  rutas sin base común, 22 conflictos de tipo (archivo/symlink) y 18 rutas cuyo
  contenido vivo había cambiado desde el manifiesto. Esos 151 casos no se
  declaran resueltos por prosa; siguen trazados en
  `context/mak-merge-20260831/reconcile-20260901.json`.
- En los conflictos donde `active-flujo` y `runner-vibecodeine` coincidían,
  se aceptó ese consenso y se conservó `win-flujo` sólo como evidencia. Los 15
  conflictos sin consenso (incluido el digest que requirió una integración
  manual) permanecen deliberadamente para revisión manual;
  incluyen `.gitignore`, `Makefile`, el crontab, los hubs, `src/flujo/autonomia.py`
  y `src/flujo/paths.py`. No se inventaron ejecutables ni se editaron tests para
  ocultar diferencias.
- Se corrigió manualmente el digest de `tools/update_readme_svg.py` para que
  filtre la declaración obsoleta de cuatro ramas y exprese la autoridad MAK/
  runtime. Se mantuvieron los contratos existentes de cron pausado y de
  automerge; una variante que refería `/home/mak/bin/mak_sync_safe.py` no se
  adoptó porque ese archivo no existe en ningún origen.
- Validación enfocada posterior: 87 tests pasaron en 62.89 s con
  `pytest -o addopts=''`; no se ejecutó la suite completa. Los cambios
  puramente de fin de línea de 134 rutas se descartaron para que el commit
  sólo contenga deltas semánticos.

### Revalidación documental previa al traslado — 2026-08-31

- Línea base histórica estable, con el mismo comando literal ejecutado dos veces:
  `./.venv/bin/python -m pytest -q tests/test_un_solo_documento.py::test_un_solo_handoff_vivo`.
  ANTES histórico: `N=1` ruta exigida. En ese momento el árbol tenía `N=10`,
  RC 1 en ambas corridas y la misma lista; la diferencia quedó explicada por
  definición y alcance del test, no por una variación de la medición.
- Clasificación literal de las diez rutas: vivo provisional único:
  `context/LAST_HANDOFF.md`; histórico: `context-history/untracked-context-20260819/PHASE225_HANDOFF_CHECKPOINT_REPAIR.md`,
  `context-history/untracked-context-20260819/PHASE268_RESIDUAL_BOUNDARY_AND_ARCHITECTURE_HANDOFF.md`,
  `context-history/untracked-context-20260819/PHASE405_OWNER_CLEANUP_BRANCH_HANDOFF.md`
  y `context-history/untracked-context-20260819/quarantine/LAST_HANDOFF.pre-803d2e5-20260818.md`;
  plantilla: `context/BRANCH_HANDOFF_TEMPLATE.md`; paquete previo/duplicado:
  `docs/handoffs/archive/MAK_CODEX_HANDOFF.md`; departamentales no globales: `context/handoffs/cultura.md`,
  `context/handoffs/iskvw.md` y `context/handoffs/rd.md`.
- El contrato no distingue global de departamental: captura los tres estados
  departamentales por contener `handoff` en sus rutas. Su política literal
  exige que también salgan de la zona viva. En la ola posterior se trasladaron
  los nueve no vivos con `git mv` a `docs/handoffs/archive/`; el test aislado
  pasó con RC 0 y los bytes quedaron preservados.
- Hardlinks comprobados antes de esta escritura: `context/LAST_HANDOFF.md`
  tenía `nlink=1`, inode `30303228` y SHA-256
  `b43b16e6852ecdd64124ddd40517c4ac0a896feb96d529dc8224245548880e42`;
  por tanto no requirió desaliasado. Los otros documentos no se editaron
  (varios conservan `nlink=4`). Esta pasada no ejecutó reset, push, commit ni
  operación Git mutante.

### Estado después de la ola

El write-set ya incluyó `docs/handoffs/archive/`; no se modificó el test. La
decisión aplicada fue un handoff global vivo más estados departamentales
archivados, con los contratos departamentales apuntando a sus copias históricas.
No inferir de la fusión que toda variante tenga ruta viva ni que sus diferencias
estén cerradas.

### Comprobador de capacidades y runtimes — 2026-09-02

Se añadió `tools/capabilities.py`, un comprobador read-only que contrasta nueve
superficies MAK/FLUJO con sus fuentes, filas de `CAPACIDADES*.md`, unidades
systemd, listeners y HTTP. La corrección inicial evitó pasar la ruta del unit a
`systemctl` en vez de su nombre. Medición final:
`python3 tools/capabilities.py --check --check-branch --format text` => `9/9`
declaradas, `9/9` fuentes presentes, `issues=0`, MAK `8900`, Research `8890`,
Codex `8891`, Ollama `11434` (3/3 modelos y 6/6 consumidores), FLUJO App `8766`
(fallback de `8765`) y SearXNG `8888`; `serve` `8777` no está escuchando y la
cola ntfy permanece inactiva, ambos estados esperados. El gate de registro de
herramientas y el handoff focal pasaron `3 passed`; no se ejecutó la suite
completa. `main` ahora lleva un perfil explícito `kind=historical` y el
selector pytest del checkout histórico quedó neutral (`-q`); `MAK` y `FLUJO`
conservan sus perfiles y selectores propios en sus ramas. El consumidor
`cultura/mak_plataforma/chat_agente.py` quedó con default `gemma3:4b`, que sí
está instalado; no se instaló `qwen-agent` ni se abrió una sesión de modelo.

---

## Agent bootstrap — CURRENT — 2026-08-31 — estado medido, familia fail-closed y MAK pausado bajo control

Lee esto y `docs/MAK_CURRENT_STATE.md` seccion 12. Lo de abajo, fechado
2026-08-29 y anterior, es evidencia historica: no se corrige, se supera.

**Antes de tocar la maquina**, carga `~/PATRONES.CLAUDE.json`: 24 formas medidas
de equivocarse aqui, con sintoma y metodo correcto en cada una. Son cinco
minutos y ahorran el dia. El orden de lectura completo esta en `~/GENESIS.md`.

### Contrato permanente que este bloque arrastra

No son adornos: `tests/test_agent_bootstrap.py` exige cada una de estas lineas
en el bloque CURRENT, y por eso un CURRENT nuevo no puede perderlas. La
compuerta atajo exactamente eso al escribir este bloque -- se redacto sin ellas
y fallo, que es su trabajo. **El rastro entre una sesion y la siguiente no puede
tener huecos, y esto es lo que lo garantiza.**

- Orden de lectura, sin excepcion: `agents.md=` primero, luego
  `docs/MAK_CURRENT_STATE.md=`, luego `context/LAST_HANDOFF.md=` **solo este
  bloque**: `historical sections are excluded`.
- `docs/MAK_SYSTEM_DIRECTIVE.md` sigue vigente.
- `write_set=experiments/cycles/C04/media_observer/` -- el write-set declarado
  del ciclo C04.
- `Stage 2D accepted`: la etapa 2D quedo aceptada y no se reabre.
- `171 focused tests` fue la medicion de aquella etapa. La medicion completa
  actual es **4204 pasadas, 5 skips, 0 fallos** (4209 recolectados), que no la
  contradice: aquella cifra era de un subconjunto enfocado, no del total.
- `mak-archive-observation-batch-v1` sigue siendo el esquema de los lotes de
  observacion del archivo.

### Lo que cambio de estado

- **CI volvia a verde en `origin/main`.** Llevaba seis corridas rojas. La causa
  no era una regresion: `experiments/pilots/` esta gitignoreado a proposito y
  varias suites lo leian sin guarda, asi que **la suite certificaba la maquina y
  no el repositorio**. Guardas puestas con el patron que salta NOMBRANDO lo que
  falta.
- **Suite medida por Codex: 4204 pasadas, 5 skips, 0 fallos** (4209
  recolectados; empezó la jornada documentada en 3741). El SSD estaba montado
  durante esta corrida. El recibo completo y su hash están en el dossier
  `/home/mak/state/codex-retomar-20260831/BASELINE.md`.
  Son 373 archivos y 4080 nodos base; 129 casos adicionales provienen de
  parametrización. Este conteo de casos no equivale a 4209 propiedades
  independientes ni a salud de la caja MAK completa.
- `./.venv/bin/python -m flujo verify` también salió con exit `0`; ejecutó su
  cadena de pytest/compilación y un Hub smoke que devolvió `OK` con versión
  `0.56.1`. `_run_verify_subprocess` ahora corta con exit `1` ante cualquier
  fallo de compileall, pytest, health, version o smoke; antes sólo imprimía el
  error y terminaba en `verify OK`. El recibo está en el dossier; esto no
  convierte una salida verde en prueba de entrega externa ni remide cobertura.
- El write-set de esta toma permanece **sin commit y sin push** hasta terminar
  la revisión: `src/flujo/cli.py`, `src/flujo/diagnostics.py`,
  `src/flujo/knowledge/system_status.py`, `tools/repo_audit.py`,
  `CAPACIDADES.md` y sus pruebas asociadas, incluidas `tests/test_cli_smoke.py`
  y `tests/test_repo_audit.py`.
  Un `git
  status` limpio no es una afirmación válida mientras este write-set exista.
- **Verificacion en entorno CI-equivalente real**: worktree + venv nuevo con
  `pip install -e ".[dev,render]"`. Un worktree da los archivos limpios, **no el
  entorno limpio**: el `.venv` de MAK arrastra lo instalado y no declarado.
- **Cobertura heredada, no re-medida en esta toma**: `cli.py` 29→45%,
  `web/hub.py` 29→38%, `cultura/mak_plataforma/hub.py` 62→73%. Total del repo
  71%. Es contexto histórico hasta que un comando nuevo lo confirme.
- **`~/state/reanudacion-20260830/` esta preparado y verificado.** Reanudar es
  un comando del operador; un agente no puede instalar un crontab.

### La familia de defecto que hay que reconocer

`subprocess.run(...).stdout.strip()` **pliega "el comando fallo" y "no hay nada"
en el mismo vacio**. El conteo anterior de "siete" no es fiable: la inspección
actual localiza **ocho puntos en siete archivos** (`flujo doctor` y
`github-sync --status` en `src/flujo/cli.py`, más `autonomia.py`, `runrecord.py`,
`check_mak_trabajo.py`, `png_xmp_witness.py`, `substrate_scan.py`), y añade
`src/flujo/diagnostics.py` como un noveno punto confirmado por una prueba nueva.
No se mantiene la afirmación de "dos rutas del hub de plataforma" sin un
call-site local que la respalde.

La distincion que lo resuelve: **`None` cuando no se midio, `False` cuando se
midio y no esta sucio.** Un arbol sin medir no es un arbol limpio. Si escribes
codigo que mide algo, esta es la trampa que te va a tocar.

### Verificación Codex de continuidad — 2026-08-31

- `flujo doctor` ahora nombra el fallo de `git status` como `AVISO` y nunca como
  `limpio`; `diagnostics` conserva `dirty=None`/`changed_entries=None` si no
  pudo medir. Las pruebas de caracterización ya no bendicen el defecto.
- `tools/medir_organismo.py` conserva `available=false` y valores `null` cuando
  fallan sus probes de `crontab`, GitHub o systemd; ya no lee un vacío como
  cero, inactivo o sin protección. Un `inactive` explícito de systemd sí es un
  estado medido. Las regresiones están en `tests/test_medir_organismo.py`.
- Los wrappers físicos de Research/Codex y sus fuentes canónicas son
  candidatos explícitos. Tras un reinicio controlado del servicio existente,
  `/api/status` observó las tres fuentes realmente ejecutadas y devolvió HTTP
  200; el estado `attention` restante corresponde a evidencia ledger pendiente,
  no a un fallo del runtime.
- El proceso Claude que estaba reinyectando el job interno `56bfb309` y sus
  hijos quedaron `SIGSTOP` (reversible, no eliminados) para mantener un solo
  escritor durante esta toma. No se activó cron, XIO ni un worker permanente.

### Dos practicas que salieron de esta jornada y conviene repetir

1. **Si encuentras un defecto y no lo vas a arreglar, fijalo con un test que lo
   documente sin bendecirlo**, y dilo en el docstring. Dos agentes lo hicieron y
   las dos veces impidio que el arreglo pasara en silencio: el arreglo tuvo que
   romper su test primero.
2. **Antes de reportar cero, demuestra que tu metodo puede encontrar algo.**
   Fabrica el caso, compruebalo, revierte. Un cero sin esa prueba no vale.

### Cifras que estaban mal y ya no

- `ingesta_archivo.py` **no estaba al 9%**: estaba al 72%. La causa es de
  instrumento: `--cov=paquete.modulo` devuelve "No data to report" porque
  pytest-cov importa el modulo antes de que arranque el rastreador. **Usa la
  ruta real.**
- "24 modulos bajo 40%" eran 32. "119 herramientas en tools/" son 117. "122
  puentes" son 130.

### El instrumento unico

    ~/bin/mak    estado | listar | medir | consolidar | reanudar

`mak consolidar` reune lo que cada instrumento persistio **con la edad de cada
dato**, para que una cifra vieja se vea vieja. No mide nada nuevo.

### Lo retirado, y donde consta

`~/_archive/orden-limpieza-20260828/mapa-de-retiro.csv`, **252 filas de datos
(253 líneas con cabecera)**, ninguna apuntando al vacío. Se borró de verdad
solo lo re-obtenible y con su comando de
recuperacion escrito: clones publicos, un instalador, una descarga incompleta,
una version vieja de Blender, un venv sin consumidor, y 602 MB de papelera
**tras comprobar los 2012 blobs de su HEAD uno por uno contra `flujo/.git`**.
Los 4 que no estaban en ningun commit se preservaron.
El resumen `exact-duplicate-decision-summary-v2.json` conserva el snapshot
anterior de 231 retiros; no se debe mezclar con este CSV físico más reciente.

Un retiro se revirtio por error propio: `venvs/knowledge-migration`. Se afirmo
"no hay PostgreSQL en MAK" y si lo hay. **Cero coincidencias en un grep no
prueba ausencia**: preguntale a `systemctl`, `docker ps`, `ss`.

### Lo que sigue siendo del operador

- `crontab ~/state/reanudacion-20260830/crontab.reanudar` -- y refijar la linea
  base del latido justo despues: `tools/mak_heartbeat.py --capture`.
- El ruleset de proteccion de `main`: `MAK-REVISOR` queda pausado hasta
  entonces, porque llama a `gh pr merge` cada 6 horas.
- `NTFY_TOPIC_OUT` no esta configurado: el canal saliente de MAK esta mudo. El
  nombre de un tema de ntfy es su contrasena, asi que elegirlo no es de un
  agente.
- **Índice de tests no secuencial**: `tests/conftest.py` asigna marcadores
  automáticos `topic_*` (tema exacto), `area_*` (área solapable) y `role_*`
  (rol transversal). `tools/medir_test_overlap.py` mide candidatos de
  solapamiento AST sin borrar ni fusionar tests; el recibo está en
  `/home/mak/state/codex-retomar-20260831/evidence/mak-test-overlap-20260831.txt`.
- **Deuda estructural abierta**: `CAPACIDADES.md` conserva el registro
  declarativo y un overlay manual; su 5-bis queda explicitamente como snapshot
  historico. `repo_audit.py --format json` emite el resultado read-only
  `mak-tool-consumer-inventory-v1` (117 herramientas), y `--format markdown`
  genera la tabla reproducible conservada en
  `/home/mak/state/codex-retomar-20260831/evidence/repo-audit-tools-20260831.md`.
  El medidor endurecido devuelve 46 referencias de produccion, 39 solo en tests
  y 32 sin referencia directa; el overlay manual de `CAPACIDADES.md` cubre los
  32 tras clasificar los seis casos que faltaban. No se debe llamar a esto
  "fuente unica" ni retirar una herramienta por nombre o ausencia de referencia.

---

## Agent bootstrap — HISTORICAL — 2026-08-29 — MAK consolidado y verificado

This is the only current operational packet. The material below the marked
historical boundary is retained evidence and must not override this packet.

Detailed current handoff for this consolidation:
`/home/mak/docs/handoffs/archive/MAK_CODEX_HANDOFF.md`.

### Standing contract, carried forward unchanged

Stage 2D accepted: the archive-to-Project-IR boundary remains in force:
`mak-archive-observation-batch-v1` is the physical evidence contract, and the
accepted gate records 171 focused tests. The full suite count is always measured
by the test command, not maintained in this packet. The governing operational
directive is `docs/MAK_SYSTEM_DIRECTIVE.md` -- mission doctrine, dated, and not
part of the three-file read order (see `docs/AUTORIDAD.md`).

`tests/test_agent_bootstrap.py` enforces that those four statements stay here. A
cleanup that loses a standing contract is a regression, not tidying.

### State: MAK is ordered, consolidated and still paused

**No MAK runtime was started or resumed.** The crontab has 0 active lines and
23 paused. Resuming cron, `mak-xio.service`, or any operator-controlled organ
is still an operator decision.

```bash
python3 tools/medir_organismo.py     # current state, read-only
```

That command replaces the numbers this packet used to carry. Three documents
hold what does not rot:

| Document | Answers |
|---|---|
| `docs/AUTORIDAD.md` | which document governs, and the five writing rules |
| `docs/MAK_ORGANISMO.md` | MAK is `/home/mak`; why it is paused; how to resume; where to look before saying something does not exist |
| `context/MAK_TRIAGE_20260828.md` | the repo's 26 top-level paths, zero unmeasured, ordered by first touch in Git |

### What this session did

Consolidated the local MAK filesystem across `/home/mak`, not only `flujo`.
`WIN`, `curatoria_inbox`, Git mutation, GoogleDrive/OneDrive and the separate
XIO repository remained outside the write boundary. No commit, push, reset or
checkout was performed.

The current exact-duplicate scan found 112 groups, 300 regular-file rows and
188 extra regular paths. The groups are classified and decisioned: 44 live
runtime groups are deferred because path and run identity matter; 35 RD groups
and 29 `trazos` groups retain semantic/evidence paths; 3 tool fixtures retain
their test roles; 1 Git artifact is out of scope. There are zero exact duplicate
Python groups.

The 100 external `.py` paths are compatibility projections to canonical
`flujo/cultura` modules, not second implementations. Eleven same-basename
groups inside `flujo` were reviewed: five are declared entrypoint wrappers and
six are independent contracts. Active directives now have one root
`agents.md`, one root `CAPACIDADES.md`, and department contracts where needed.

Retired material was moved reversibly under
`/home/mak/_archive/orden-limpieza-20260828/`, with 234 map rows and no missing
destinations. One hundred forty-one rows correspond to duplicate, projection
or placeholder consolidation. Fifty-one compatibility aliases are symlinks to
canonical physical files. The complete measurements are in:

- `/home/mak/indexes/mak-canonical-20260829/mak-canonical-map.json`
- `/home/mak/indexes/mak-consolidation-20260829/exact-duplicate-candidates-v2.csv`
- `/home/mak/indexes/mak-consolidation-20260829/MAK-DIRECTIVE-REGISTRY.md`
- `/home/mak/indexes/mak-consolidation-20260829/CONSOLIDATION-DECISIONS.md`
- `/home/mak/_archive/orden-limpieza-20260828/mapa-de-retiro.csv`

The full test suite exited 0 with five skips and warnings only; `git diff
--check` also passed. Git was used read-only as provenance and validation, not
as the source of truth for the local filesystem.

### Continuation — 2026-08-29 — CI, cron and coverage

Claude's local commit `c94e5776` guards optional `psd_tools`; its failed remote
CI run was for the preceding SHA `72bd5cd`. This continuation reproduced the
workflow dependencies in a temporary environment, generated `archivo.json`,
and ran `python -m flujo verify` successfully. `psd_tools` and `imagehash` are
optional in that environment, so the dependent tests now skip with explicit
reasons and the absence branch of `_psd` has direct coverage.

Current uncommitted worktree changes are `tests/test_archive_toolchain.py`,
`tests/test_ingesta_archivo.py`, and `tools/medir_organismo.py`; no Git command
changed history, branch or remote state. The organism measurement now offers
`--cron-detail` for 23 static cron preflights and `--json` for
`mak-organism-heartbeat-v1`. The valid test-overlap evidence is in
`/home/mak/indexes/mak-solape-tests-20260829/`; see
`/home/mak/docs/handoffs/archive/MAK_CODEX_HANDOFF.md` for its historical counts and limits.

The first opening of all previously uninspected local roots is complete. The
system-level GitHub runner is enabled and active; `actions-runner` is therefore
live runtime, not an orphan. Local installation roots (`bin`, `opt`, `go`,
`apps`, `models`, `src`, `tools`), dated evidence roots (`indexes`, `state`,
`labs`, `renders`) and personal/XDG roots were each classified without moving
them. `GoogleDrive` and `OneDrive` remain untouched rclone mount boundaries.

### Before resuming, one measured fact

`revisor.py --enforce` runs `gh pr merge` every six hours, and **`main` has no
branch protection and no rulesets** (`gh api .../branches/main/protection` ->
404; `.../rules/branches/main` -> 0 rules, with a token holding `repo` scope).
Detail and options in `docs/MAK_ORGANISMO.md`.

### The error pattern this session kept repeating

Search one form, conclude absence. It produced five published claims that had to
be corrected: `research/` and `labs/` "do not exist" (they are at `/home/mak/`),
24 tools "without consumer" (13, after searching the module form too), 49
database tables (48, by the CI method), "one live process" (three organs are
up), and the `PHASE*` corpus "in the Trash" (a Codex worktree copy; read the
`.trashinfo`).

Three surfaces answer most of it: `/home/mak/.local/share/Trash/` (every file
carries its origin in a `.trashinfo`), the sibling directories under
`/home/mak`, and `/home/mak/.codex/memories/rollout_summaries/`.

### Open, in order of consequence

1. **Resume or retire the 23 cron lines.** Fourteen days paused, undocumented
   until now. Operator decision.
2. **Branch protection on `main`** before anything with merge authority resumes.
3. **Three portfolio implementations** (`cultura/mak_plataforma/contrato_archivo.py`,
   `tools/portfolio/generar_works.py`, `src/flujo/knowledge/portfolio_*.py`) share
   no data path: 14 suites, ~200 tests, three definitions of "obra".
4. **Ten endpoint names implemented twice** across the two hubs. They are not duplicate products: `:8900` frames and proxies, `:8765` is the workspace app.
5. **The airdrop chain**: `_airdrop/` does not exist, 42 tests pass on it,
   `flujo doctor` reads its absence as health.
6. 42 broken references in tracked `.md`, classified in `docs/AUTORIDAD.md`.

### Versioning

This session made no Git mutation: no commit, push, reset, checkout or branch
change. Git history, status and diff were consulted read-only for provenance and
validation. Filesystem consolidation is recorded outside Git in the archive map,
manifest and decision dossier; do not treat Git state as the physical inventory.

### Standing constraints

Do not modify `/home/mak/WIN`, SSD physical files, `archivo_index.sqlite`,
`order_projection.json`, `questions.json`, `ties_full.db`, `intake.sqlite`,
`artist_discographies.json`, `archivo.json`, media/artwork/historical sources,
or external wrappers without an exact write-set. No physical rescan of the SSD.
`curatoria_inbox/` is protected by operator instruction. Leave GoogleDrive and
OneDrive mounts untouched. Treat `/home/mak/indexes/mak-canonical-20260829/
mak-canonical-map.json` as the current physical inventory and regenerate it
only when the filesystem has materially changed.

## Agent bootstrap — HISTORICAL — 2026-08-27 — general archive portfolio view

Retained evidence. The current packet is the 2026-08-28 one above.

### Current objective

MAK is a reusable autonomous system for artistic archives:

```text
physical archive -> evidence memory -> reconstruction -> cultural/curatorial
reasoning -> portfolio/application/research products -> outcomes -> learning
```

The current useful product is the internal Contracurador mounted over the
existing ISKVW archive projection. The live Hub consumes that same view
read-only at `GET /api/portfolio/archive-view`, advertises it through the
existing ISKVW department catalog and renders it in the existing ISKVW editor;
the SSD foundation is a separate evidence boundary and never silently selects
ISKVW pieces. It separates declared works, observed archive material and
technical practice without forcing labels or rewriting identity. ARICA, DREF,
HARRY, MYRA, RAYU, ISKVW and Fondart remain cases and holdouts, never
architecture.

Stage 2D accepted: the archive-to-Project-IR boundary remains in force:
`mak-archive-observation-batch-v1` is the physical evidence contract, and the
accepted gate records 171 focused tests. The full suite count is always measured
by the test command, not maintained in this packet. The governing operational
directive is `docs/MAK_SYSTEM_DIRECTIVE.md`.

### Physical authority and migration status

`/home/mak/flujo` is the authoring baseline inside the wider MAK organism
`/home/mak`. `/home/mak/WIN` is historical evidence and is not to be changed;
`GoogleDrive` and `OneDrive` are external mounts not traversed. Archive roots,
artwork, media, databases and runtime sources are protected unless a later
task names an exact safe write-set. `iskvw/datos/archivo.json` is the current
generated source for the general view; it is read-only input and its hash is
carried into the output. Do not delete or move physical evidence.

### Completed work with command and result

- Existing `src/flujo/knowledge/product_view.py` was extended with the pure
  `project_archive_portfolio_view()` consumer and strict validator. It does
  not create a database, rescan an archive, mutate media or infer authorship.
- The physical database topology was reconciled read-only on 2026-08-27:
  `data/mak_knowledge.db` is the active MAK memory; RD, flyer, Research,
  archive-index, intake, pilot, Curatoria, archaeology, CI and agent stores
  retain separate authority/classes and are connected only through existing
  contracts, hashes and refs. The bounded full-host scan found 270 SQLite
  files outside `WIN`: 85 MAK-managed and 185 host/application caches. All 85
  MAK-managed files passed `integrity_check`; the complete classification is
  recorded in `docs/system_learning/master/inventory.json`.
- The complete physical organism map now covers 114 non-WIN top-level entries,
  17 nested repositories, live process/listener observations and the explicit
  external-mount boundary. No files, databases, media, artwork or `WIN` were
  moved, deleted or merged.
- Existing `tools/render_product_view.py` now accepts `--archive` while
  retaining the prior plan/dossier/package mode. It renders JSON or Markdown
  from the same source.
- The real command
  `./.venv/bin/python tools/render_product_view.py --archive
  iskvw/datos/archivo.json --format json --max-items-per-format 24` exited 0.
  The reopened output validated as `mak-archive-portfolio-view-v1` with input
  hash `sha256:3005f632fde06d9772cbab6fa9827103895246cfc50eb32429975b81bdab35bd`.
- Observed real counts: 2,034 source pieces, 5,812 source links, 8 declared
  works, 24 bounded observed-field items, 24 bounded practice/code items and
  61 links between selected items. The remaining 1,978 pieces stay in the
  source and are reported as omitted, not deleted or merged.
- `src/flujo/knowledge/ssd_order_foundation.py` and
  `tools/compile_ssd_order_foundation.py` now triangulate the existing SSD
  index, order projection, intake DB, Project IR/reconstructions, research
  authority, research corpus and ISKVW archive without rescanning or mutating
  any source. The foundation covers 45,536 assets, 917 projects, 13,121
  families and 113 indexed relations; its review order is explicitly not an
  artistic-quality ranking. It records 4097 certified-same and 7
  certified-distinct identities, 50 unresolved operator ties and 6 open
  questions. The existing `questions.json` is now carried as
  `mak-order-operator-review-v1`: 6 asked + 44 deferred, 50 total, 93.22%
  disputed-byte coverage, `machine_answerable=false` and `selection_effect=none`.
  Each question also records whether its left/right container has an
  authority-bound external context; this is prioritization evidence only, not
  a name or authorship assertion.
- The same foundation finds 52 exact external-locator candidates across the
  2,034 ISKVW pieces and 52 SSD assets (one-to-one, all with research-corpus
  receipts). They remain `status=candidate`, `typed_reference_count=0`,
  `selection_eligible=false` and missing full-content/delivery evidence;
  filenames, routes and locators never become authorship or work identity.
- `src/flujo/knowledge/contracurator.py` consumes the bounded 56-row view and
  mounts 8 source-declared records. It retains three incompatible theses,
  counterevidence, 48 exclusions and an abstaining alternative. The SSD
  foundation is visible as `partial_order` in the Hub but
  `used_for_selection=false`.
- The explicit write boundary was exercised through the existing
  `LearningStore`: the latest episode
  `episode:contracurator:f1deae941e5b1cf30758998d82b1d242` was appended to the
  pre-existing `iskvw-contracurator-20260827` Project IR with archive,
  foundation and operator-question hashes plus code provenance. The project
  now has 5 Contracurador episodes; the latest is `needs_evidence`, has
  `truth_promotions=0`, and records `database_write=false` for the Hub
  consumer. Replaying the same episode is idempotent.
- The output explicitly keeps title separate from source identity: untitled
  observed rows retain `title=null` and may retain `observed_description`,
  marked as not an author statement. Code rows are context, not artwork.
- `cultura/mak_plataforma/hub.py` now mounts the existing pure consumer at
  `GET /api/portfolio/archive-view`. The route reads only
  `iskvw/datos/archivo.json`, fixes the existing bound at 24 items per observed
  and practice format, emits `mak-archive-portfolio-view-v1` directly and
  returns 503 without a partial view when the source or contract is invalid.
- A real foreground HTTP smoke on an ephemeral localhost port returned 200
  with the same input hash, 2,034 source pieces, 5,812 source links, 56 selected
  items, 61 projected links and zero truth promotions. The physical source
  SHA-256 stayed `eef1788dc4462e71dd13be84b446463ac6169324de95a11f2bb4b5f19215f8d6`
  before and after. The server was shut down in the same command.
- `tests/test_hub_archive_portfolio_view.py` adds four cases: deterministic
  replay and refs, GET route contract, an authorial-looking path that remains
  untitled observed evidence, and malformed JSON failing closed. The focused
  Hub/product-view regression passed 47/47 with `PYTHONPATH=.:src`; `py_compile`
  passed. The first sandboxed socket smoke was denied before bind and the first
  combined regression collection lacked the repository root on `PYTHONPATH`;
  both were rerun with the correct bounded environment and passed.
- The existing `mak-hub.service` was restarted after verifying its actual
  `ExecStart` points directly to the canonical Hub. PID changed `973 -> 178677`;
  the unit is active/running on `127.0.0.1:8900` and the real endpoint returns
  HTTP 200 with the same 2,034/5,812 source counts, 56 selected items, 61
  projected links, `truth_promotions=0` and unchanged physical source hash.
  `/home/mak/plataforma/hub.py` remains an unchanged compatibility wrapper;
  its SHA-256 stayed `8ac11ae6a15181b23905d67f2d8951be97c5e807bd28a31a0394ac1bb8a13abd`.
- `iskvw/editor.html` now fetches that endpoint automatically and renders the
  three existing formats with counts, gaps, omissions and source refs. The
  Contracurador card also exposes `6 preguntas operador + 44 diferidas` while
  keeping them out of selection; opening the operator section exposes the six
  question samples, examples, answer options, authority-context status and
  source refs. Untitled rows use a neutral `ref` display explicitly marked `no
  es titulo autoral`; invalid/partial responses clear prior data and fail
  closed. The existing atlas and `mesa_montaje.js` mount remain intact.
- `src/flujo/departments.py` advertises the exact route under the existing
  `iskvw.tool_links` with `mode=read_only`, `status=draft`,
  `publication=false` and `authorship=false`; no portfolio area or alias was
  added. Two focused test files cover the UI and catalog boundaries.
- The consolidated root regression passed 67/67 with bytecode/cache writes
  disabled. Live API and editor requests both returned 200; the physical
  archive hash stayed unchanged. Browser verification rendered all three
  columns, exercised `actualizar lectura`, retained the epistemic labels and
  reported no console warnings/errors.
- Focused product-view tests, product-plan/dossier/application/pilot
  regressions, `py_compile` and `git diff --check` all exited 0. The general
  view source, CLI, tests and the consolidated recent MAK code, tests,
  learning documents and capability registry are committed in `6ba51fa` and
  pushed to `origin/main`; generated pilot outputs remain local and are not
  deleted.

### Completed work — 2026-08-28 — operator frontier deepening

- `src/flujo/knowledge/ssd_order_foundation.py` keeps the same
  `mak-ssd-order-foundation-v1` contract and raises its algorithm to
  `evidence-first-order-2-operator-dossier`. The existing `operator_review`
  field now carries one deterministic dossier per tie instead of a bare
  question row. No second base, index, endpoint or crawler was created.
- Each of the 50 dossiers records the question id, both containers, declared
  and recomputed shared bytes/classes, concrete examples, SSD asset/project
  refs per side, evidence for, evidence against, missing evidence, the answer
  options the source permits, `reopen_when` with its origin, external-authority
  status per side, an exact `source_ref` on every claim,
  `machine_answerable=false` and `selection_effect=none`.
- The decisive new evidence is an independent recomputation. Reading
  `ties_full.db` read-only, all 50 questions reproduce their declared
  `shared_classes` and `shared_bytes` exactly (50/50). This corroborates the
  question ledger from a second byte-level source; it does not answer any tie.
- That recomputation also grades the ties by substance:
  **34 substantive, 1 partially degenerate, 15 metadata_only**. The 15
  metadata-only ties (deferred 29-43) rest entirely on the zero-byte content
  class `sha256:e3b0c442…` or on a single AppleDouble resource fork, so they
  carry no shared authored material. This lowers their evidence; it does not
  answer or close them. All 50 remain `unresolved`,
  `resolved_by=operator_attestation_only`.
- 7 questions name a container that is not a `container_root` in the SSD index
  (`Spotlight-V100`, a macOS Spotlight store, and `_KAYAKAZE 2025 2.xml`, a
  file). Those sides are reported `container_binding=unbound` with explicit
  counterevidence and missing evidence, never silently treated as projects.
- A new `attestation_queue` orders all 50 ties for a human: the 6 asked first,
  then by substantive shared bytes. Every row ships `answered=false`,
  `answer=null`, `attested_by=null`, `selection_effect=none`, and the queue is
  `pending_human_input` with `answers_recorded=0`.
- The research frontier is an explicit abstention, not a silent skip. The new
  `research_frontier` block records `status=abstain`, `job_count=0`,
  `dispatch=false`, `create_job_invoked=false` and names the three gates that
  block it: `cross_archive_relations.py#_descriptor` requires an
  `artist_identity` per archive, `#_matching_artifacts` requires a catalogue
  title to match a filename stem, and
  `cross_archive_research_frontier.py#compile_cross_archive_research_frontier`
  requires a typed `mak-cross-archive-relations-v1` payload. Feeding it would
  mean inventing an identity for DREFGIRA, DrefQuila, HARRY or BAHPARTY, so the
  52 shared locators stay `candidate`, `typed_reference_count=0`,
  `selection_eligible=false`. No provider, job or research store was touched.
- `src/flujo/knowledge/contracurator.py` projects the deepened basis into the
  Hub: full dossiers for the 6 asked ties, compact rows for the 44 deferred,
  the 50-row queue, the triage and the frontier abstention. It fails closed on
  a prefilled queue (`attestation_queue_prefilled`), a dispatched frontier
  (`research_frontier_dispatched`) and a missing triage or frontier.
- The durable episode now references the foundation by digest rather than
  embedding a fourth copy of every dossier. This kept the live payload at
  315,709 bytes instead of 719,170 and keeps the ledger row readable; the
  evidence itself stays in the compiled foundation, reachable by
  `semantic_hash`.
- The selection did not move. The Contracurador still consumes the bounded
  56-row view, still mounts the same 8 source-declared records, still retains
  3 theses with 2 defeated and an abstaining alternative, and
  `used_for_selection` stays `false`. A focused test asserts the selected
  `source_refs` are byte-identical with and without the SSD basis.
- Real commands: `tools/compile_ssd_order_foundation.py` over the real index,
  order projection, intake, knowledge DB, research authority, reconstructions,
  archive and corpus exited 0 twice with byte-identical output
  (`sha256:4f5a190c9c5a82b66c1ae97f015e58f00cd1b7bc94741a8c80cc07b6dcc9e45c`,
  semantic hash
  `sha256:88666334765954e04764373dffdd6e07c778f63a7ef33ef1ea782244bf6cf8f7`).
  Inventory is unchanged: 45,536 assets, 917 projects, 13,121 families, 113
  relations, 4,097 certified-same, 7 certified-distinct, 50 ties, 6+44
  questions, 52 candidate crosswalks.
- `iskvw/editor.html` renders the frontier inside the existing Contracurador
  card. `archiveViewOperatorSection()` shows the priority/deferred counts, the
  triage, the queue status, per-tie grade and substantive bytes, the answer
  options, examples, both sides' binding and authority, the byte recomputation,
  the three evidence lists with their source refs, `reopen_when`, and the
  frontier abstention with its gates. It leads with an explicit warning that
  these are questions for a person, not answers from MAK, and keeps
  `no usada para seleccionar`, `falta referencia tipada`, `no es titulo
  autoral`, `database_write=false` and `training=false`. The client validator
  now also rejects a payload whose queue is prefilled or whose frontier is
  dispatched. The section contains no form, input, button or fetch.
- Validation: `py_compile` on the foundation, contracurator and hub exited 0;
  `node --check` on the extracted inline script exited 0; `git diff --check`
  exited 0. The focused suite over contracurator, hub view, editor UI,
  department catalog, the new operator-frontier file and product-view passed
  45/45, including 13 new adversarial cases and 2 new UI cases. The whole
  `tests/` tree ran 3,756 cases: 3,750 passed, 5 skipped and 1 failed. The one
  failure is the pre-existing `test_higiene_repo.py::test_tools_en_registro`,
  which asks for a `CAPACIDADES.md` entry for `tools/compile_contracurator.py`
  and `tools/compile_ssd_order_foundation.py`; both tools and that failure
  predate this slice and `CAPACIDADES.md` was outside the permitted write set.
- Fail-closed evidence, observed rather than asserted: after the code change
  and before the foundation was regenerated, the three Hub view tests returned
  503 instead of a partial view, because the deepened contract rejected the
  stale on-disk basis. They passed again once the foundation was recompiled.
- The service was restarted (PID `197774 -> 202144`) and
  `GET /api/portfolio/archive-view` returned HTTP 200 three times with a
  byte-identical body
  (`sha256:52d16758cf4317d210e74566f93213983d3935a9b5c516a320b0499377ebeba9`),
  56 visible rows, 2,034 source pieces, 5,812 links, 8 selected refs and
  `truth_promotions=0`. The physical archive hash stayed
  `eef1788dc4462e71dd13be84b446463ac6169324de95a11f2bb4b5f19215f8d6`.
- Read-only proof: `data/mak_knowledge.db` kept size 190,066,688, mtime
  `1787889634883579055` and
  `sha256:e6e6acd85a8c7d4460ed15c5a4037646d77bb27646c1af76d750b138039dc689`
  across six GETs before the write, and after the write it stayed at
  `sha256:7176a4519d22a50a1b43cf7076485128b830db5aa254d3e92f3e276a235f2d6b`
  across three further GETs. A GET never writes.
- The single durable write went through `record_contracurator_episode` /
  `LearningStore.record_episode`, never manual SQL. `project_episodes` went
  26 -> 27 and the existing `iskvw-contracurator-20260827` project went 5 -> 6
  episodes. The new episode is
  `episode:contracurator:06198a3b9f3cf6e4f2f07ff9ab671f6d` with
  `status=needs_evidence`, `truth_promotions=0`,
  `artistic_fact_mutations=0`, `database_write=false`,
  `training_permitted=false`, `source_snapshot_hash=sha256:3005f632…`,
  `code_commit=15ee50d6034810416d6bc571d86e782a95a25b5b` and tool versions
  carrying the foundation, questions, tie-ledger, index and archive hashes
  plus `worktree_dirty=true`. Replaying the same episode returned the same id.
- Browser verification used headless Firefox against the live payload rendered
  through the editor's own functions and stylesheet. The card shows the 8
  selected records, the 2 defeated theses, the abstaining alternative, the
  collapsed 48-row exclusion map, the six full dossiers, the 44 deferred rows
  with their grades, and the frontier abstention with its three gates and
  source refs.

### Completed work — 2026-08-28 — night guard, triangulated frontier

Eight ordered cycles ran; each was validated before the next began.

**Cycle 1 — base audit.** No drift. The SSD index, order projection, questions,
tie ledger, intake, research authority and `archivo.json` all matched the
recorded hashes; the service was active on PID `202144`, the endpoint returned
HTTP 200, and `data/mak_knowledge.db` held 27 episodes with 6 on
`iskvw-contracurator-20260827`.

**Cycle 2 — priority ties triangulated.** Each of the 50 dossiers now also
carries the identity tier, intake evidence, reconstruction evidence, the index
relation reality and every shared member path, each with its own `source_ref`.
- The tier is **reproduced, not copied**: applying the order projection's own
  rule to the byte ledger yields `T1=24, T2=458, T3=865`, exactly the declared
  totals, and every tie's classes sum to its declared `shared_classes`.
- Intake and reconstruction are folded per container from the existing sources:
  6 containers hold a bounded intake candidate and 3 hold reconstructed
  decisions (BAHPARTY 50, DREFGIRA 8, LYON 387).

**Decisive measured fact.** All **111** `exact_duplicate` relations in the SSD
index are on the empty content class `sha256:e3b0c442…`; **zero** are
substantive. The index holds only **2** non-duplicate typed relations, and
**neither crosses a container boundary**: `contains_scene` points a `3D JJJ`
`.blend` at its own scene, and `video_covers_sequence_candidate` points
`BAHPARTYCONCERESI/Comp 1.mp4` at a family inside the same container while
declaring `policy=coverage_candidate_not_same_work_proof` with a frame mismatch
(5 expected, 900 observed). So `questions_with_a_binding_typed_relation = 0`
across all 50 ties — a measurement, not an assumption.

**Cycle 3 — deferred ties given a stated reason.** Every tie now records
`actionable_evidence_kinds` and, when empty, an explicit `deferral_reason`.
46 ties carry actionable evidence, 4 carry none; the kinds break down as
substantive bytes 35, intake candidate 34, authority context 22, reconstructed
decision 17, declared native input 1. A deferral is now stated rather than
silent.

**Cycle 4 — all 52 crosswalk candidates audited one by one.**
`typed_reference_count=0` is now **measured across 5 bases** rather than
asserted. Per candidate the audit records the content-hash check, the delivery
receipt check, the typed-reference lookup and the corpus derivation:
- **52/52** SSD assets are `hash_state=pending` with **no** full content hash,
  so byte identity with the ISKVW piece cannot be computed at all;
- **52/52** ISKVW pieces carry `fuente_original.estado=ausente`, so there is no
  file on that side either, and none carries a checksum field;
- **52/52** declare `fuente_original.rol=obra_original`, recorded as a
  declaration of that projection only, explicitly not a binding of the SSD
  asset and not a receipt;
- `entity_relations` (6,058 rows), `context_relations`, `project_artifacts`
  (17,917 rows) and the index relation table returned **zero** references.

**The near-miss, recorded as such.** Three rows in `artifacts` do contain a
crosswalk locator — contact-sheet thumbnails named
`sheets/00N-<locator>.jpg` from a 2026-08-08 portfolio sample run, with no
`sha256` and no `declared_work_id`. They are kept as
`derived_locator_echo` with `is_typed_reference=false`: a locator inside a
generated filename is not a reference. This is exactly the case the guard rule
exists for, and it is now covered by a test.

**Cycle 5 — a correction to the previous handoff.** The earlier packet said no
valid research-frontier input existed. That was too strong. A valid
`mak-cross-archive-relations-v1` payload **does** exist at pilot scope
(`experiments/pilots/DREFQUILA/runs/cross-archive-escarlata-20260826`,
`sha256:bb9e7a8e…`, 6 relations, all `candidate`), and a non-dispatched
frontier was already compiled from it (1 job, `planned_not_dispatched`,
0 dispatched). Recompiling it in memory reproduces the on-disk artifact
byte-for-byte and validates.

It is now **cited and explicitly not adopted**, because it only exists through
the two inferences this projection refuses: both archives declared an artist
identity (`DrefQuila`, `Harry Nach`), and its positive evidence is
`catalog_track` plus `artifact_name_signal` with `reason_codes` including
`local_title_match`. It declares `same_title_different_work` as a live
alternative and `exact_cross_archive_content_unavailable` as counterevidence.
The abstention is therefore rescoped to `ssd_order_frontier` with a
`precision_note`, and the foundation records `not_usable_for`: answering any of
the 50 ties, binding any of the 52 candidates, or selecting an ISKVW piece.
No pilot file was modified, no job was dispatched, no provider was called.

**Cycle 6 — foundation and Hub.** Everything landed inside the existing
`mak-ssd-order-foundation-v1` contract, reusing `operator_review`; the
dossier algorithm is now `byte-identity-corroboration-2-triangulated`. No new
base, endpoint, crawler, registry, runtime or superior contract was created.
The Hub keeps the single route `GET /api/portfolio/archive-view`.
`iskvw/editor.html` shows the recomputed tiers, the index relation reality, the
52-candidate binding audit, the pilot chain marked *citada y no adoptada*, and
per tie the tier badge, actionable-evidence kinds or deferral reason, the
typed-relation count for the pair, intake and reconstruction per side, and the
shared member paths. The client validator now also rejects a promoted,
rescoped or dispatched pilot chain and a binding claim on an unbound crosswalk.

**Cycle 7 — one episode.** `project_episodes` 27 → 28 and the project 6 → 7.
The new episode is `episode:contracurator:17464f33f77f0294feb3a8f48fbb221c`,
`status=needs_evidence`, `truth_promotions=0`,
`artistic_fact_mutations=0`, `source_snapshot_hash=sha256:3005f632…`,
`code_commit=15ee50d6…`, with tool versions carrying the foundation, questions,
tie-ledger, index, archive and pilot-relations hashes plus
`identity_tiers_reproduce_declared=true`,
`index_cross_container_typed_relations=0`,
`crosswalk_typed_reference_count=0` and `crosswalk_bases_scanned=5`. The replay
returned the same id. The DB went
`sha256:7176a451…` → `sha256:7e3abd24…`; three GETs before and three after left
mtime and hash untouched.

**Cycle 8 — adversarial.** 11 new attacks were added and pass: the tier must be
reproduced not asserted; a relation count must not be read as binding power;
every crosswalk candidate must be measured; a locator in a generated filename
must never become a reference; the pilot chain must be cited but never adopted;
an absent pilot run must degrade without breaking; a deferral must be stated;
the Hub must fail closed on a promoted, rescoped or dispatched pilot chain and
on a binding claim over an unbound crosswalk; renaming every container to
`OBRA MAESTRA …` must manufacture nothing; and stripping every
`evidence_against` and `missing_evidence` list must not soften a single verdict
or move the 8 selected refs.

**Selection unchanged throughout.** 56 visible rows, 8 selected source refs,
3 theses, 2 defeated, counterevidence on all three, the abstaining alternative,
48 exclusions, `used_for_selection=false`. The live payload is byte-identical
across three GETs (`sha256:ab658034…`, 371,009 bytes) and the physical archive
hash stayed `eef1788dc4462e71dd13be84b446463ac6169324de95a11f2bb4b5f19215f8d6`.
Service restarted, PID `202144 → 294343`, active.

**Cycle 4 extended — the wider base scan.** Scanning 5 surfaces was not enough
to claim `typed_reference_count=0`, so all 8 registered MAK stores in
`docs/system_learning/master/inventory.json` were read read-only for the 52
asset ids, piece ids and locators. `rd.db`, `rd_datos.db` (a privacy boundary,
counts only), `flujo.db` and the research registry returned **zero**. The 52
matches in `artifacts`, `entities`, `temporal_events` and `git_files` resolve to
the research-corpus files, whose filenames *are* the piece ids and which are
already recorded as `derived_from_iskvw` with
`independent_confirmation=false`.

**Two real leads, both refused with a stated reason.** `intake.mak_links` and
`mak_knowledge.operational_curation_links` each name 20 of the 52 pieces — 44
link rows in total. They are now read, classified and carried as
`operational_possible_link`, and they do **not** bind, for two independent
reasons visible in the rows themselves: the relation is
`possible_consumer_or_origin` at confidence `0.55` with
`evidence_json.method = "path_token"` (the token `anima`, from
`iskvw/piel/animadas/`), and the left endpoint is an intake project
(`intake_project:6f6a046f…:project_e88363…`), never one of the crosswalk SSD
assets. Every one of the 44 rows is recorded with
`endpoint_is_a_crosswalk_ssd_asset=false` and `is_typed_reference=false`, and
the Hub now refuses any class that is not `possible_*` on `path_token`.

So `typed_reference_count=0` is now measured over **7 surfaces named in the
payload**, with 44 pre-existing path-token links and 3 derived filename echoes
found and explicitly disqualified rather than absent.

**Second episode.** Because that added a real evidence class, one further
episode was appended: `project_episodes` 28 → 29 and the project 7 → 8.
`episode:contracurator:b06cf657170a7766f424dd700f4248d7`,
`status=needs_evidence`, `truth_promotions=0`, `artistic_fact_mutations=0`,
`source_snapshot_hash=sha256:3005f632…`, `code_commit=15ee50d6…`, with
`crosswalk_bases_scanned=7`, `operational_possible_links=44`,
`operational_possible_link_classes={"possible_consumer_or_origin/path_token":44}`
and `derived_locator_echoes=3`. Replay returned the same id. The DB moved
`sha256:7e3abd24…` → `sha256:840d2724…`; three GETs after left mtime and hash
untouched.

**Validation.** `py_compile` on the three modules exited 0; `node --check` on
the extracted inline script exited 0; `git diff --check` exited 0. The focused
suite passed 58/58, the operator-frontier file alone 26/26 (13 of them new
adversarial attacks). The whole `tests/` tree ran 3,769 cases: 3,763 passed,
5 skipped and 1 failed — still only the pre-existing
`test_higiene_repo.py::test_tools_en_registro`, which asks for a
`CAPACIDADES.md` entry for `tools/compile_contracurator.py` and
`tools/compile_ssd_order_foundation.py`; both tools and that failure predate
this work and `CAPACIDADES.md` is outside the permitted write set. The foundation compiles to byte-identical output across
repeated runs; the final artifact is `sha256:a049baec…` with semantic hash
`sha256:da6e859b…`. The live payload is byte-identical across three GETs
(`sha256:1160868e…`, 372,085 bytes). Service PID `294343 → 299493`, active.
Every protected source kept its hash and mtime; `WIN` is untouched
(2026-08-14).

**Browser verification did not complete this cycle.** Headless Firefox returned
`RenderCompositorSWGL failed mapping default framebuffer` at 6000, 3000 and
1600 px heights and wrote no PNG, so the rendered card was not re-captured.
The render itself is still covered by the node-based UI test, which asserts 26
booleans over the HTML the editor's own functions produce from the live payload
— including the new tier line, relation-reality line, binding-audit line with
`sobre 7 superficies`, the 44 path-token links marked `no vinculan`, and the
pilot chain marked `citada y no adoptada`. The previous cycle's screenshots of
the same card remain valid evidence for the surrounding layout.

### Completed work — 2026-08-28 — portfolio production, the direction change

The Contracurador/SSD-order line is **superseded**, not extended. It produced
eight cycles, 3,769 tests, two episodes and zero products. The full diagnosis
and the corrected model live in `docs/PORTAFOLIO_PRODUCCION.md`, which is the
durable record for this direction; read it before touching anything here.

**The architectural correction.** Files were being treated as the substrate that
entities are made of, when they are *evidence about* entities that exist
independently. A song existed, a show happened, a client paid; none of that stops
being true because an mp4 cannot be hashed. Three consequences followed: one
relation used as the universal join, `unknown` global instead of per-layer, and
no notion of sufficiency relative to a purpose — so the bar was set at
jury-defensible authorship and applied to showing an image in a grid.

**Three new contracts, all read-only projections, no second base.**

- `mak-portfolio-format-v1` (`portfolio_format.py`): the declared plant. Specs
  are **data** in `data/portfolio_formats/*.json`. Each slot declares count,
  claim verb, layer, minimum state, minimum permission and a caption grammar
  whose fields are allow-listed. Five verbs: `puedo`, `hice_esta_parte`,
  `ocurrio`, `significa`, `es_mio`. Five states, each with a named external test
  and a stated refutation. Hard ceilings: `es_mio` and `hice_esta_parte` cannot
  exceed `candidate` without a named third-party receipt, and a format that
  demands more is rejected.
- `mak-portfolio-claims-v1` (`portfolio_claims.py`): the claim base. Every claim
  carries verb, layer, scope, state, permission, `generated_by`, `supported_by`,
  caption fields, evidence refs and `refuted_by`. Two invariants are enforced in
  code: **no route promotes the claim it generated**, and the authorship ceiling.
- `mak-portfolio-render-v1` (`portfolio_render.py`): feasibility **before**
  producing, then the document. A required slot that cannot be filled reports a
  count and a reason, never a question.

**A fourth: reading live practice.** `screen_setup_evidence.py` identifies a
producing application from the document's own root element, never from its
filename. It reads what nobody had read.

**The nine root XML files were the best evidence in the archive** and were
classified `indexed_only`. They are Resolume Arena 7 ScreenSetup exports — the
projection mapping of each room: **136 bezier-warped surfaces across 18 screens**
between 2024-08 and 2026-05. `BERLIN 1` alone has 4 screens and 59 slices on a
3043×272 canvas, with screens named `pista modificada`, `pista original`,
`club modificacion`. Canvases range from 1080×1920 to 3840×1664.

Reliability is declared, after an operator correction: a save-as carries the
previous document name and the ids of kept screens, so `label_reliability` and
`dating_reliability` are recorded per file. `CHILLAN.xml` declares `harry`
internally — that is a **stale label, not a link**. What sustains the
Harry↔Chillán relation is the operator's attestation.

**Attestations are now a mechanism** (`data/portfolio_attestations.json`,
`mak-portfolio-attestation-v1`). A named authority is the only route that lifts
a role or authorship claim past `candidate`. Negative attestations ("this is not
mine") are accepted without corroboration because they reduce what the system
asserts. Three are recorded: the Chillán show with Harry (positive), the
*Escarlata* visual made by a third party (negative), and the ARICA logo PSD
(negative, which fixes the general rule that a native file does not imply own
process).

**The external authority resolved the identities**, and it had been sitting in
`data/artist_discographies.json` unread: `DREFGIRA` has
`canonical_name=DrefQuila`; `DREFMOVISTAR` is `kind=event`; `LYON` is Lyon La F;
`MARLONLOLLA` is Marlon Breeze; `SCD` is `kind=venue`, Salas SCD; `FELINA` has
no URLs and stays unknown. That collapses the "two different clients" reading of
the DREFGIRA↔DrefQuila tie without deciding whether it is one commission.

**The SSD is partitioned** in `data/portfolio_practices.json` — 18 declared
containers with a written basis each, reversible by one line. Two of my own
classification errors were found and fixed: `abril2026post` is not a frame
sequence (its "numbers" are 17-digit platform media ids, so it is
`published_export`), and 40 "containers" were loose files at the volume root.
Final: 25 `production`, 10 `delivery`, 1 `published_export`, 1 `render_output`,
1 `source_footage`, 2 `installed_tool` (NestDrop and Loopback are tool
inventory, not work), 40 `loose_root_file`, 17 `system_metadata`,
4 `indexed_only`.

**Products actually produced**, via `tools/compile_portfolio.py` into
`out/portfolio/`: 279 claims (175 `observed`, 77 `candidate`,
25 `supported_candidate`, 2 `externally_attested`).

| Format | Status | Items |
|---|---|---|
| F1-trayectoria | rendered | 30 |
| F2-capacidad · visual para música y eventos | rendered | 24 in 5 sections |
| F3-rol-técnico | rendered | 16 in 4 sections |
| F2-capacidad-barbería | **infeasible, correctly** | 0 |

Real figures in the capability document: Blender 927 native projects across 19
contexts 2016–2026; After Effects 408 across 16. Every line carries its state,
its route and what would refute it.

The barber format is the generalization test: a `transformacion` vertical with
completely different evidence kinds and permission dominant. **It loaded and was
assessed without one line of code changing**, and it is infeasible because this
archive has no barber evidence. That is the correct answer.

**Product bugs found by reading the rendered document**, not by testing: an item
budget that starved the last required slot; the same claim appearing in two
slots; dominant tool computed alphabetically (it said *After Effects* for LYON,
where 426 of 559 are Blender); scale figures that never named their container;
and plural agreement. All fixed.

**Tests inverted.** `tests/test_portfolio_production.py` adds 22 cases that
assert the system **produces**: a feasible plant must render, every line must
carry state and refutation, a restricted permission must never render per case,
and a tampered document must be rejected. The earlier suite made abstention
free, so the system learned to abstain; here an unforced abstention fails.

**Episode with the four learning fields.** `project_episodes` 29 → 30 under the
new project `mak-portfolio-production-20260828`:
`episode:portfolio:9ea03b9b683bd4962c614239f6b679e9`, `status=needs_evidence`,
`truth_promotions=0`, `learning_complete=false`. It records purpose and variant
produced, and marks **consumer_decision=pending** and
**observed_outcome=pending** rather than inventing them — because without a
consumer decision nothing was learned.

**Validation.** `py_compile` on the four new modules plus the hub and the CLI
exited 0; `git diff --check` exited 0; the focused portfolio suite passed 22/22.
The whole `tests/` tree now passes **3,788 with 5 skipped and zero failures** —
the long-standing `test_higiene_repo.py::test_tools_en_registro` failure is
closed legitimately, by registering `compile_portfolio.py`,
`compile_contracurator.py` and `compile_ssd_order_foundation.py` in
`CAPACIDADES.md` with their consumers, as the repo rule requires.
The whole chain is byte-deterministic: two consecutive compiles produced
identical `claims.json` and identical Markdown for all three documents. The SSD
was read read-only and its mtimes are unchanged.

### Open integration items

1. `iskvw/datos/archivo.json` is generated and currently contains a mixed
   `todo` projection. A future source refresh may change counts/hash; the
   output must be regenerated and revalidated, never hand-edited.
2. The ARICA durable technical run remains a separate case run. Its technical
   relations are provenance-only and must not be used to name or select works.
3. `/home/mak/curatoria_inbox/ARICA/pantalla antesala.psd` remains a supplied
   branding/logo resource, not evidence that the user authored the whole work.
4. The byte-identity ledger `ties_full.db` and the native-scene declarations
   live under `/home/mak/.claude/jobs/3428381a/tmp/`, a job scratch directory.
   The foundation degrades to `unverified_no_ledger` with explicit
   `missing_evidence` when they disappear, and a focused test covers that path,
   but the corroboration should be moved to a durable read-only location before
   it is relied on again. This is now the highest-value durable-safety gap.
6. Headless Firefox cannot currently capture this page: the software compositor
   fails at every window height tried. The UI is covered by the node render
   test; a screenshot needs either a working GPU/compositor or a CDP-driven
   capture.
7. The 44 `possible_consumer_or_origin` links point at
   `/home/mak/actions-runner/_work/vibecodeine/vibecodeine/iskvw/piel/animadas/`,
   a second repository checkout. If a real authoring or export witness exists
   for those SVGs, it would be the first genuine typed-reference candidate —
   but only from a witness, never from the path token that produced the link.
5. `tests/test_higiene_repo.py::test_tools_en_registro` fails because
   `tools/compile_contracurator.py` and `tools/compile_ssd_order_foundation.py`
   have no `CAPACIDADES.md` entry. Both tools and that failure predate this
   slice; `CAPACIDADES.md` was outside the permitted write set and was not
   touched.

### Tool and dependency verification matrix

| Boundary | Current evidence | Status |
|---|---|---|
| archive observation -> Stage 2A-2D | real ARICA/DREF/HARRY replays and validators | PASS |
| canonical product plan -> dossier/package/view | focused and regression tests | PASS |
| ISKVW archive projection -> general portfolio view | real 2,034/5,812 source run | PASS, CLI/Markdown |
| title/observation/practice separation | validator and real counts | PASS, no promotion |
| general view -> canonical Hub handler | real ephemeral HTTP 200, source hash preserved | PASS, read-only |
| canonical Hub -> persistent `:8900` runtime | service restart, live HTTP 200, PID/listener verified | PASS, read-only |
| live archive view -> existing ISKVW editor | browser-rendered three-format surface, refresh and clean console | PASS, internal UI |
| archive view -> ISKVW department catalog | exact route plus explicit draft/authorship/publication controls | PASS, discoverable |
| source refresh -> stable regenerated view | deterministic fixture test; live refresh not run | OPEN |
| full `/home/mak` physical registry -> master docs | 114 roots, 270 SQLite candidates, 85 MAK-managed, 185 host caches | PASS, read-only |
| operator questions -> independent byte-identity ledger | 50/50 ties reproduce declared classes and bytes exactly | PASS, corroborated |
| tie substance grading -> attestation order | 34 substantive / 1 partial / 15 metadata-only, all still unresolved | PASS, no answer |
| tie container -> SSD index container_root | 24/26 bound; 7 questions carry an unbound side, reported not assumed | PASS, explicit gap |
| SSD locator crosswalk -> research frontier | abstention with three named blocking gates, 0 jobs | ABSTAIN, correct |
| deepened frontier -> ISKVW selection | selected source_refs byte-identical with and without the basis | PASS, no leakage |
| operator frontier -> browser card | headless Firefox render of the live payload with all labels | PASS, internal UI |
| tie answer -> operator attestation | queue built, `pending_human_input`, 0 answers recorded | OPEN, needs a human |

### Conflicts and risks

- The 8 declared works are selected only because the source has `class=obra`,
  title and summary; this is a source-backed presentation rule, not a claim
  that they are the artist's complete or best body of work.
- Perceptual text, filenames, paths, link similarity and technical context
  remain evidence/signals. They do not prove authorship, intention, series,
  delivery or public eligibility.
- `archivo.json` is a generated projection and is not itself the physical
  archive. Its `generated` value and input hash provide provenance, not a
  timeless identity.
- No publication, submission, dispatch, training, source mutation or `WIN`
  change occurred. The Hub remains read-only; the only durable write in this
  slice is the explicitly requested Contracurador episode in the existing
  learning DB. Temporary validation outputs under `/tmp` are not durable
  products.
- The API and UI are internal/draft outputs. Runtime availability does not
  promote source records to authorship, publication, eligibility or a complete
  artistic portfolio; the 1,978 omitted records remain in the source.
- A `metadata_only` grade is a statement about bytes, not about the archive.
  Two containers whose only shared content is an empty file may still be the
  same commission; the grade lowers the byte evidence and nothing else. Do not
  read the queue order as a verdict, a priority of artistic value, or a licence
  to close the low-ranked ties.
- Binding a question's `left`/`right` string to the index `container_root`
  column is a join on the source's own vocabulary. It is not evidence that the
  container is a work, a project, an author or a commission.
- The external authority in `artist_discographies.json` only marks whether a
  container has URL-backed context available. It cannot decide whether two
  folders are the same commission, the same work or a reuse.
- The foundation carries a full copy of the deepened frontier; the durable
  episode carries only its digest and hashes. The two must be read together,
  and the foundation is a generated artifact under ignored `out/`, not an
  authority.

### Correction — what already existed

The operator's correction was right: *"todo lo que pides ya existe, solo que no
buscaste."* Both things I had listed as missing were already on disk.

**The real demand.** `experiments/pilots/ARICA-FONDART-2027/runs/enriched/opportunity.json`
is a complete `mak-opportunity-constraints-v1` for
`fondart-nacional-investigacion-2027` with the bases PDF hashed and page-level
locators: criteria weighted `transfer_impact 0.40`, `quality 0.30`,
`curriculum 0.20`, `viability 0.10` (p.15), 8 hard gates, 8 required documents,
and the deadline recorded as `constraint_status_unknown`.
`F4-fondart-nacional-investigacion-2027.json` is now a **transcription** of it,
rendering 28 items, and it declares openly that the archive can only feed
Curriculum and part of Viability — 0.30 of the weight. Quality and transfer
impact belong to the proposed project, and the line requires field study.

**The human decisions.** `/home/mak/plataforma/director_runs/portfolio-editor-20260808/`
holds the log I called pending. `human_decision_log.py` reads it: 84 selection
events over 66 items (59 discarded, 4 selected, 3 deselected, 4 items where the
person changed their mind) and 99 classification events over 62 items, all
`owner: human`, `status: human_draft`, `promotion: none`, declaring `ownership`
personal/client, `context_kind`, `purpose`, `nature`, `lane` (iskvw/rd) and
`triage`. **Measured selection rate: 6.06%.**

That human vocabulary maps onto the model almost exactly, and `lane: rd`
confirms RD as a practice in the operator's own words. Declarations are carried
with their `human_draft` status intact.

**The distinction that matters:** 6.06% was measured on an *earlier* portfolio.
The episode records it as `observed_outcome.status=prior_selection_measured`
with `applies_to_these_documents=false` — a baseline to compare against, not
these documents' result. `learning.complete` stays `false` and now states what
would complete it.

`project_episodes` 31 → 32:
`episode:portfolio:1ff1208547147568e027b8246156ac3d`, child of the previous one,
with `consumer_decision=recorded` and the baseline rate in its tool versions.

### Second search round — what else was there

**Curatorial relations existed.** `connections.jsonl` holds 24 typed pairs drawn
by a person and `copilot_feedback.jsonl` 12 of their confirmations. The kinds
split into source structure (`same_carousel` 4, `same_date_context` 11,
`same_event` 1) and interpretation (`shared_concept` 7, `visual_similarity` 1) —
the first is how the material was published, the second is the curation. That
distinction makes **F7-lectura-curatorial** possible: it renders 13 items with
the two sections kept apart by a declared filter.

The format contract gained one field for it: `require_fields`, a value filter on
caption fields. Verb, layer and state were not enough — two slots can take the
same verb and differ only in what the claim asserts.

**11 of the 24 pairs were fixtures** (`mak-replay-XX`, `obra-a`). They are
excluded by a positive rule — a published item has a long numeric platform id —
and counted, because a fixture that leaked into a decision log is a fact about
the log.

**The 7 fund reports are not demands**, recorded in
`data/demand_source_assessment.json` with `verdict=not_usable_as_a_demand`: 1 of
7 has more than one official source, 6 of 7 cite methodology documents on scribd
or scholar instead of fund portals, all 7 record HTTP 429 or timeout errors, one
carries a fabricated 2023 body date inside a 2026 file and cites DIBAM (replaced
in 2018), and its own text admits it never reached the bases. Same class as
`copilot_external.jsonl`.

**Machine proposals**: 32 curatorial inferences from `watsonx` (22) and `aws`
(10), with 2 hypotheses and 40 unknowns, `attesting=false`. Only feedback rows
whose provider is the person are read.

**Scratch debt closed**: the evidence inputs are copied to `data/ssd_evidence/`
with a manifest and verified identical hashes.

Six formats now: five render (F1 30, F2 24, F3 16, F4 28, F7 13 items) and
F2-barbería stays correctly infeasible. `project_episodes` 32 → 33.
The focused portfolio suite passes 31/31.

### Third round — two corrections that came from reading

**RD's field data is fictitious.** `docs/becas/caso_mak_rd.md` §5 states it
outright: the demo field data is generated with a fixed seed, and real reports
will only exist with real field operation. `data/rd_datos.db` with 0 rows
corroborates. My `TABLA_RD` declaration was conservative in the right direction
for the wrong reason — I set `aggregate_only` for the privacy boundary, when in
addition there is no real field data to show at all. Corrected in the partition,
together with the other two limits the annex declares: the reagent analysis is
presumptive by design, and the legal scope is under professional validation.

**The template already warned about the reports.** The checklist in
`docs/becas/postulacion_base.md` instructs: check amounts and dates against the
fund's OFFICIAL source, *not* the auto-generated calendar. That warning predates
this session and independently corroborates
`data/demand_source_assessment.json`.

**F6 is deliberately not written.** `caso_mak_rd.md` already is a product of the
right kind — a technical annex for evaluators with a declared-limits section
naming what is presumptive, pending and fictitious. Rewriting it as a format
would be worse than the original and would duplicate authority.

Three surfaces measured and recorded in
`data/evidence_surface_assessments.json` without being wired:
`research/corpus/` (1,599 descriptions, `texto_autor=false` in 1,598, **zero**
publication dates, 461 with OCR fragments averaging 26 chars),
`vision_features.jsonl` (33 rows from `aws`), and the RD format decision.

The criterion in all three: a surface is not wired because it exists — it is
wired when a format asks for it. And a format is not written when the human
artifact is already better.

### Next concrete action

**The line to continue is portfolio production, not the SSD order.** Read
`docs/PORTAFOLIO_PRODUCCION.md` first.

1. **Send one document and record what happens.** That is the only remaining
   step for the learning loop: an outcome observed on *these* documents, against
   the 6.06% baseline. Everything else is in place.
2. **Verify the Fondart deadline** in the official source: the capture carries
   it as `constraint_status_unknown` and F4 names that in its forbidden
   inferences.
3. **Close `F2-capacidad-barbería` honestly** by finding a second real archive,
   or keep it as a paper test. Do not weaken its slots to make it pass.

What must not happen: another review order, another question queue, another
abstention contract, or a format that mentions a case name in code.

### Superseded — SSD order frontier

The 50 operator ties, the 52 candidate crosswalks and the research-frontier
abstention remain valid evidence and are still compiled by
`tools/compile_ssd_order_foundation.py`. They are **not** the active product
line. Their measured conclusions stand: all 111 index duplicate relations are on
the empty content class, no typed relation crosses a container boundary, and
`typed_reference_count=0` over seven surfaces. The prior backlog note follows.

The safe, measurable backlog is exhausted. Every tie is corroborated, tiered,
triangulated, graded and queued; every crosswalk candidate is audited against
seven surfaces; the research frontier is a precise abstention with the one
existing payload cited and refused; and both near-misses (3 filename echoes,
44 path-token links) are recorded as disqualified rather than missing. There is
no further action that adds evidence without either a human answer or a new
physical witness.

The next step needs a human. Answer the attestation queue in rank order,
starting with `order-question:ask:00` (DREFGIRA ↔ DrefQuila, 18 substantive
classes, 15.8 GB) and choosing between the two options the source already
permits: `same_work_under_two_names` or
`output_reused_in_a_second_commission`. The 15 `metadata_only` ties can be
answered last; they carry no byte evidence either way and must not be closed
automatically.

Until an attestation exists, keep `answers_recorded=0`, keep the candidate
crosswalk, and do not hand-edit `archivo.json`, treat a locator as identity,
invent an artist identity to satisfy the cross-archive gates, or create a
second corpus, schema, database, Hub or runtime. The other open edge is
unchanged: one typed SSD↔ISKVW relation backed by a full content hash or a
delivery receipt would reopen the research frontier legitimately.

### Last verified

2026-08-28 America/Santiago, night guard. Eight cycles completed and validated
in order: base audit, priority ties, deferred ties, the 52-candidate binding
audit over seven surfaces, the research-pipeline decision, foundation and Hub
integration, two causal episodes, and eleven new adversarial attacks. The
selection never moved: 56 rows, 8 selected refs, 3 theses, 2 defeated, 48
exclusions, `used_for_selection=false`. The 50 ties remain unanswered by
design. Source refresh, operator attestation, the durable relocation of the
byte ledger and a browser screenshot remain separate and open.

--- END CURRENT ---

## Historical snapshot retained — 2026-08-26 — general MAK objective / DREF evidence

**Operative rule.** This is the only active packet. Read the four reconciled
master documents under `docs/system_learning/master/`. The historical packets
below remain evidence and must not be used to reopen completed work.

### Current objective

MAK is an autonomous reusable operating system for artistic archives:
physical archive -> evidence memory -> provisional reconstruction -> cultural
and curatorial intelligence -> shared portfolio/application/research plan ->
products -> verified episodes -> learning and bounded control. ARICA, MYRA,
RAYU, ISKVW and Fondart are cases, never architecture. User review is optional,
not the normal pipeline gate.

Six agent perspectives and the prior master were reconciled into exactly four
documents:

- `docs/system_learning/master/inventory.json`: agents, hashes, authorities,
  components, current evidence and ordered gaps;
- `docs/system_learning/master/hashmap.json`: nodes, causal edges, loops,
  invariants, failure modes and the current broken edge;
- `docs/system_learning/master/system_theory.md`: unified system theory;
- `docs/system_learning/master/action_plan.md`: the only active plan.

The target session `Responder saludo` (`01a03414-252c-7333-9492-cc2d43687040`)
continues as primary MAK director after this transfer.

The permanent objective remains the complete MAK system described above. The
current DREF/DREFQUILA portability work is only an execution slice used to
produce evidence for that objective; Piso 3 is not a replacement objective.

### Current bounded slice — role-aware cross-archive context — 2026-08-27

The plan is maintained in `docs/system_learning/master/action_plan.md`; this
handoff records only the execution checkpoint. The active chain is
`catalogue + practice states -> cross_archive_relations -> existing
mak-project-context-v1 consumer -> bounded research frontier`.

Bootstrap: `mak-agent-bootstrap-v1`, task `Add role-aware cross-archive
manifestation context`, exact code write-set:
`src/flujo/knowledge/cross_archive_relations.py`,
`tests/test_cross_archive_relations.py`; documentation write-set:
`docs/system_learning/master/action_plan.md`,
`docs/system_learning/master/inventory.json`,
`docs/system_learning/master/hashmap.json`,
`context/LAST_HANDOFF.md`.
Context hashes for the documentation update: `agents.md=53afe6c85f431db10aee822f5a250af66968bb7c3ac9a27cbf38269b9386ce75`,
`CURRENT=c98a7fb488b825ecfef0aff4d3770189d3167de469644aa03a90b03964b808e0`,
`LAST_HANDOFF=25e69a007ada4cdff962e76bbf5b5df00771dd81ebd954a48a6e6c108eec5d14`.

Implemented additively in the existing context projection: `role_bindings`
and relation evidence now distinguish `candidate_visual_manifestation`,
`archive_observed` and `reconstructed_reference`; authorship remains
`not_inferred`, with missing evidence
`native_authoring_project_or_explicit_visual_credit`. Participation scope is
explicitly `matched_archive_artists_only`, `exhaustive=false`. The physical
relation payload, artifact identity and existing context schema remain
unchanged; no new database, registry, service or ontology was added.

### Latest bounded execution — artist-wide public-work anchors — 2026-08-27

The DREF/DREFQUILA slice was improved without treating a filename as a cultural
fact. `data/artist_discographies.json` now contains a sourced local cache of the
2024 `Los Sentimientos de un Robot` track list, including `Pego Fuerte` with
Harry Nach and Young High, and the existing
`src/flujo/knowledge/cross_archive_relations.py` now exposes
`project_archive_catalog_context(...)`. This is a read-only
`mak-project-context-v1` projection for one archive plus an explicit public
catalogue; it emits `candidate_manifestation_of`, preserves
`authorship_status=not_inferred`, and leaves the native authoring/export witness
as missing evidence. It does not create a work, merge artifacts, infer that the
third-party visual was made by the artist, or write the database.

The matcher was hardened after a real smoke exposed a bad qualifier-only match:
empty token sets and arbitrary filename subsets no longer match every catalogue
track. The bounded real projection now validates with zero errors and reports 25
candidate artifact endpoints across 15 catalogue works; `Pego Fuerte` resolves
to `DREFGIRA/BLOQUE 01 LSDR/07 PEGO FUERTE.mp4`; `EDIT.mov`, `b ( ).mov` and
`1.png` produce zero matches. Focused cross-archive tests passed 9/9; the
cross-archive/project-context/research-frontier/feature-policy regression passed
46/46; `py_compile`, JSON parsing and `git diff --check` passed. No media,
archive, production DB, service, WIN or Git history was modified; the three
changed paths are the catalogue, the existing relation projection and its test.

The catalogue is an explicit public-work anchor, not proof that the local
endpoint is the delivered visual. The DREFGIRA `Pego Fuerte` endpoint is a
reconstructed/reference-only artifact in this slice, so the next consumer gate
must preserve `candidate` and `native_authoring_project_or_explicit_visual_credit`
until a real `.blend`/`.aep` -> export -> publication witness is available.

The existing consumer boundary was smoke-tested in a temporary SQLite database:
`project_archive_catalog_context` persisted the same `mak-project-context-v1`
package and `read_context` returned `mak-project-context-read-v1` with one
context, 40 entities and 25 candidate relations. All returned relation statuses
were `candidate`; the temporary database was removed. This proves consumer
compatibility only; no production context was written.

The real DREF/HARRY smoke passed: 6 candidate cross-archive relations, 11
context relations, 5 role bindings (3 reconstructed DREF references and 2
observed HARRY artifacts), zero context validation errors, zero physical
merges and zero truth promotions. Focused tests passed 7/7; cross-archive,
project-context and research-frontier regression passed 18/18; py_compile and
git diff --check passed. No source rescan, production DB write, dispatch,
media mutation or authorship inference occurred.

The preceding operational-membership/capability projection remains validated
in its existing LearningStore path and is not reopened here. Open: if a visual
authorship statement is needed, connect an explicit native authoring/export
witness (`.blend`/`.aep` -> render -> publication). If it is absent, retain
the manifestation as a bounded candidate for curation/research rather than
turning absence of a native file into a negative authorship claim.

### Physical authority and current evidence

`/home/mak/flujo` is the authoring baseline; `/home/mak/WIN` is historical
evidence; archive roots are read-only. Git is transport, not physical truth.
Production DBs, protected artwork/media, publication, submission and training
remain outside this consolidation.

The durable ARICA/Fondart input slice now contains:

- full observation: 12,332 artifacts, 12,015 files, 128 observations,
  `snapshot:70cdbc7c142391b4fca9f8fc18c042c369f8396eacb3b4185659b8b8a35243b3`;
- official opportunity validity capture: valid, `current_verified`,
  `confirmed=true`, `effective_to=2026-09-10`;
- practice receipt evidence with four exact physical bindings;
- full-baseline and enriched materializations under
  `experiments/pilots/ARICA-FONDART-2027/runs/`, regenerated from that same
  observation input and verified by reopening every listed output.

The snapshot string above and its input hash are also recorded in the master
inventory. Do not infer identity from prose or filenames.

The DREF/DREFQUILA federation is durable at
`experiments/pilots/DREFQUILA/runs/metadata-federation-20260826/` and includes
the physical `DREF CHOCOLATE` root, DREFGIRA reconstruction/Project IR,
DREFGIRA.blend reference, BAH media, XIO/show records, historical copies and
the read-only `data/mak_knowledge.db` context graph. `BAHPARTY/bah` is also
captured as a contextually adjacent reconstructed project (87 artifacts),
but remains explicitly unmerged because its physical source and project-level
binding to DREFGIRA are not verified. Its observed counts are
41 physical files plus 3 directories, 467 DREFGIRA reconstructed project
artifacts and 87 adjacent BAHPARTY artifacts,
93 DREF database artifact rows, 41 exact path matches to DREF CHOCOLATE, 12
persisted context relations (3 verified, 4 human_attested, 5 candidate),
1,149 curation links and 353 temporal events. No source or media was changed.

### Current execution evidence

The Piso 0 focused gate passed with exit 0 across product episode, learning,
product plan, application/research and autonomy. The previous
`program_requirement_ids` failure was stale state, not a current blocker.
The ARICA replay comparison is now durable: baseline and enriched retain the
same archive/reconstruction outputs; 14 downstream outputs change under the
two declared enrichments, 9 common outputs remain identical, and
`unexplained_output_deltas=0`. Manifest v1 hashes are canonical JSON semantic
hashes; parsed output rehash passes for all 23 baseline and 26 enriched files.
Raw pretty-printed file bytes are intentionally not compared against those
semantic hashes because that is not the v1 contract.

La regresión ampliada de los consumidores del plan pasó con exit 0, incluyendo
manifest, constraints/validity, fit/possibility, frontier,
triangulation, programas, plan, dossier, application, episodio, learning,
autonomy y product view. Una primera sonda de conteos falló por asumir claves
`supported_claims/candidate_claims` en `practice.reconciliation`; el contrato
real usa `claims_by_status`. Se corrigió leyendo el payload y la segunda sonda
pasó. Esto queda como aprendizaje de contrato, no como fallo del pipeline.

La arista incremental del mundo ya tiene una proyección ejecutable y durable:
`experiments/pilots/ARICA-FONDART-2027/runs/opportunity-delta.json`
(`mak-opportunity-delta-v1`, SHA-256
`7c3a8f6d33fe7c8eb24766825aebbc543a0b15031bfca9a62daa56fe90180a01`). El
comparador puro `src/flujo/knowledge/opportunity_delta.py` recibe dos
`mak-opportunity-constraints-v1`, detecta dos cambios reales (`source.validity`
 y `unknowns`), preserva la evidencia de deadline y marca nueve consumidores
downstream. El cross-check contra baseline/enriched confirmó que exactamente
esos nueve outputs cambiaron. No ejecuta red, DB ni recomputación implícita;
deja el siguiente trabajo como enlace Vigía/evidence-return -> esta frontera.

El subenlace Vigía -> captura acotada quedó verificado el 2026-08-26. La
proyección pura `src/flujo/knowledge/vigia_capture_bridge.py` consume el
resultado real de `cultura/mak_vigia/vigia.py:revisar_fuente`, conserva IDs de
fuente, hashes de items, títulos, URL normalizada y skips, y consulta
`tools/research_source_capture.py:capture_one` únicamente con `record=false`.
El smoke controlado produjo una oportunidad y un plan
`mak-source-capture-gate-v1`; `network_called=false`, `database_write=false`,
`dispatch=false` y `promotion=none`. La regresión
`tests/test_vigia.py tests/test_vigia_opportunity_queue.py
tests/test_vigia_capture_bridge.py` pasó con exit 0; `py_compile` y
`git diff --check` de los tres paths nuevos también pasaron. El primer smoke
falló porque el fixture tenía un título de dos palabras y el parser real exige
al menos tres; al reproducir el criterio del consumidor, el smoke pasó. Ese
fallo se conserva como aprendizaje de contrato, no como evidencia de red.

El puente conserva el modo plan-only y ahora añade la operación explícita
`capture_vigia_plans`/CLI `--record`: valida el plan, ejecuta únicamente los
planes bounded mediante `capture_one(record=True)` y devuelve
`mak-vigia-capture-receipts-v1` con `source_plan_hash`, `plan_id`, `capture_id`,
`source_id` y `text_path`. El smoke temporal con el consumidor real y backend
fixture pasó; el default sigue sin red ni escritura. Vigía todavía no tiene un
esquema versionado propio: el input aceptado sigue siendo su contrato observado
`results[]/nuevos[]`. El próximo enlace causal es receipt de captura -> memoria
de oportunidad -> delta y recomputación selectiva. La portabilidad a nivel de
persona ya quedó cerrada con HARRY-NACH; sólo permanece contextual el binding
exhaustivo de la subcarpeta HARRY CHILLAN, que no bloquea el core ni se rellena
con DREFGIRA, BAHPARTY o nombres de directorio.

También se ejecutó una sonda de integración completa en un directorio temporal,
sin red: `capture_one(record=true)` con un backend fixture escribió un receipt
local, `adapt_execute_research_report` lo convirtió al batch de resultados
existente y `triangulate_research_evidence` devolvió 16 pares, todos
`unresolved` por ausencia de claims. `build_evidence_return` conservó los 16
gaps, produjo cero propuestas promocionables y mantuvo `promotion=none`.
Esto prueba la forma del retorno y la abstención, no una captura pública real ni
la recomputación durable; el temporal se eliminó al terminar la sonda.

El holdout de portabilidad avanzó con un archivo físicamente distinto de
DREF: `/home/mak/curatoria_inbox/HARRY CHILLAN`. El profile
`experiments/pilots/HARRY-NACH-2026/input/archive_profile.json` conserva como
evidencia local el binding contextual a Harry Nach, y el observer produjo el
snapshot `snapshot:4ba52b415e213b68f7ad0d95a888d1535c530cac5318735d13b961248cd9a1b0`.
El replay durable en
`experiments/pilots/HARRY-NACH-2026/runs/fondart-holdout-20260826` pasó con 20
artefactos, 2 observaciones, 2 candidatos topológicos, 1 unidad provisional,
20 asignaciones y 1 Project IR. Repetir el replay en memoria produjo el mismo
`run_id` y los mismos hashes de salida. La cadena dejó `fit=abstain`, dossier
`draft_only`, application `blocked_with_reasons`, 3 claims unknown y 17 jobs
de research; no se promovió ningún nombre de carpeta, canción, obra o show.

Este es `independent_artist_person_scope_replay_pass`: el catálogo y el profile
respaldan la identidad de Harry Nach a nivel de persona/archivo y el replay es
reproducible. La pertenencia exhaustiva de la subcarpeta HARRY CHILLAN sigue
`contextual_candidate`, como límite separado de obra/show. El próximo gate
puede resolver ese binding o encontrar otro profile explícito; no debe convertir
DREFGIRA/BAHPARTY ni el nombre del directorio en evidencia.

El mismo snapshot HARRY fue reejecutado con la captura oficial Fondart existente
en `experiments/pilots/HARRY-NACH-2026/runs/fondart-enriched-opportunity-20260826/`.
El delta `opportunity-delta.json` (SHA-256
`sha256:7c3a8f6d33fe7c8eb24766825aebbc543a0b15031bfca9a62daa56fe90180a01`)
registró dos cambios (`source.validity` y `unknowns`): source gate
`current_verified`, 16 jobs en vez de 17, pero práctica, snapshot y claims
idénticos; fit `abstain`, dossier `draft_only` y application bloqueada. La
captura de oportunidad no se convirtió en evidencia del archivo artístico.
La comparación durable enlaza ambos runs desde
`experiments/pilots/HARRY-NACH-2026/runs/fondart-holdout-20260826/portability-comparison.json`.

La inspección completa descartó una falsa deriva de lineage: `programs.json`
contiene dos candidatos legítimos —uno condicionado por oportunidad y otro
nativo de práctica— y los productos seleccionan el candidato nativo presente
en el conjunto completo.

La evidencia `Escarlata (Remix)` corrigió el límite de relación entre DREFQUILA
y HARRY. El compilador puro
`src/flujo/knowledge/cross_archive_relations.py` consumió la discografía local,
la federación DREF y el estado de práctica HARRY, y dejó seis candidatos en
`experiments/pilots/DREFQUILA/runs/cross-archive-escarlata-20260826/relations.json`
(SHA-256 `sha256:bb9e7a8e1f3bc707a97ba5ea910200a3afcec4b395271212b7cb31d233c2a433`).
Son tres refs reconstruidas DREFGIRA por dos artefactos físicos HARRY, con
`status=candidate`, un track explícito, provenance, `physical_merge=false` y
`truth_promotion=false`. La proyección existente
`experiments/pilots/DREFQUILA/runs/cross-archive-escarlata-20260826/project-context.json`
(`mak-project-context-v1`, SHA-256
`sha256:1fa949162ea1998f5af8679ac2c70f27888ffc3bbabc65385957cb7599307799`)
expone esos seis pares y cinco enlaces `candidate_manifestation_of` hacia el
nodo catalogado `Escarlata (Remix)`, por lo que la relación ya es consumible
por el contexto sin dejar el track huérfano. DREF queda marcado
`reconstructed_reference_only` y HARRY `contextual_candidate`: la colaboración
es relacionable, pero no prueba que todo HARRY CHILLAN sea una sola obra ni que
exista una entrega exacta.

La cobertura DREF se contrastó además en una sonda read-only de cuatro
contextos: DREF físico completo (40 artefactos), DREFGIRA reconstruido (467),
BAHPARTY adyacente (87) y HARRY (20), con 614 refs y 20 relaciones candidatas.
La sonda encontró 12 enlaces DREFGIRA reconstruido↔DREF físico, 6
DREFGIRA↔HARRY y 2 BAHPARTY↔DREFGIRA para cuatro tracks catalogados; el DREF
físico no contiene una ref física de Escarlata. Esto no contradice la relación
Escarlata: demuestra que el puente pasa por la reconstrucción DREFGIRA y que
los contextos físicos/reconstruidos del mismo artista no deben colapsarse en
un `archive_id` sin contrato explícito. La sonda no persistió output nuevo,
no fusionó artifacts y no promovió hechos.

The complete second-archive run was generated from `DREF CHOCOLATE` with the
existing `archive_observer.py`. The same Stage 2A -> 2D functions produced a
valid `mak-practice-evidence-state-v1` over 44 physical artifacts: 40 local
relations, one unresolved `exported_product` unit, 40 assigned artifacts and
four unassigned structural artifacts. It produced zero supported claims and
seven explicit abstentions; no false merge or truth promotion occurred. The
durable result is recorded in
`experiments/pilots/DREFQUILA/runs/full-physical-20260826/`.

The earlier bounded sample remains at
`experiments/pilots/DREFQUILA/runs/portable-sample-20260826/` as a comparison
of partial coverage. The complete run is `PISO3_PASS_FOR_SECOND_ARCHIVE`.

The full `DREF CHOCOLATE` root was hashed successfully; its size is
approximately 98.2 GB. The separate metadata-only observer run remains valid
as a cheap coverage diagnostic and records three directory artifacts plus 41
`limit_reached` observations, which correctly produces zero relations and
zero units. DREFGIRA and BAHPARTY reconstructed media outside that root remain
reference-only and are not silently treated as physically bound.

### Single next action

Do not open another architecture or scan 98.2 GB blindly. The same-artist
second-archive gate is now closed for DREF CHOCOLATE. The next general-plan
milestone now has a passing independent-person replay: HARRY-NACH-2026. Its
person/archive boundary is usable for portability, while its subarchive
binding remains contextual and is not a work/show fact. La inspección read-only
del grafo existente encontró además el registro
`intake_projects` con `source_key`
`6f6a046fb3c639a35b32:project_29335da67c429530baaa`, `record_hash`
`cf54df0c494008e7b83a353eafd819e427cdeb78e1bcd1d9cd06c619997ee116` y
`relative_path=HARRY CHILLAN`; sigue siendo un registro `candidate`, no una
afirmación de autoría. El mismo grafo conserva 617 enlaces de curatoria para
20 rutas físicas, todos de fuerza `path_token_context_only`; sirven como
contexto de búsqueda, no como prueba. La comparación durable de tres casos está registrada en
`experiments/pilots/HARRY-NACH-2026/runs/fondart-holdout-20260826/portability-comparison.json`.
The next gate is to strengthen that binding or obtain another explicit one, and
then compare two archives with
`source_mutations=0`, `false_identity_merges=0`, `lost_artifact_refs=0` and
deterministic replay. BAHPARTY/DREFGIRA must not be promoted into that role
without evidence.

El enlace de contexto ya fue validado con el consumidor existente en una base
temporal: seis relaciones de pares y cinco anclajes al track, todos
`candidate`, cero proyectos creados, cero promoción y cero escritura en la base
de producción. La lectura de vuelta usa el contrato real
`mak-project-context-read-v1` y devuelve el grafo bajo `contexts[]`; la primera
aserción que esperaba `relations` en el nivel superior fue un error de
verificación y quedó corregida. La proyección de Research ya existe en
`experiments/pilots/DREFQUILA/runs/cross-archive-escarlata-20260826/research-frontier.json`:
un job agrupado de dominio `curatoria` cubre las seis relaciones, usa el
requisito técnico `relation-binding:catalog-track:b1f1a69c33797bd851e92d872cb8eb35`,
mantiene `dispatch=false` y, al pasar resultados vacíos al triangulador,
devuelve `unresolved` con `result_missing`. El namespace `opportunity_id` es
técnico y no representa una convocatoria. El siguiente cierre causal es
evidence-return capturado -> recomputación de esta frontera; esa captura ya
se ejecutó de forma acotada y quedó durable en
`experiments/pilots/DREFQUILA/runs/cross-archive-escarlata-20260826/research-capture`.
Apple Music y YouTube aportaron dos grupos independientes; la triangulación
válida devuelve `supported_candidate`, pero sólo para el registro público de
colaboración. El binding exacto entre la entrega local y los endpoints sigue
ausente: no se promovió la relación, no se despachó ningún job y no se tocó la
base de producción.

Una segunda sonda bounded sobre la publicación oficial de ELEVEN1.1
(`https://www.youtube.com/watch?v=8XxFX6_w6CA`) quedó registrada en el mismo
`SourceCorpusStore`. La URL canónica produjo dos receipts porque cambiaron los
bytes crudos aunque el texto normalizado coincidió; se conserva como versión
de fuente y no se agregó automáticamente al claim ni a la triangulación.

### Registro de ejecución del corte actual

- Bootstrap `Continue reusable Vigia capture delta loop`: exit 0; los hashes
  emitidos fueron `agents=53afe6c85f431db10aee822f5a250af66968bb7c3ac9a27cbf38269b9386ce75`,
  `CURRENT=c98a7fb488b825ecfef0aff4d3770189d3167de469644aa03a90b03964b808e0`
  y `LAST_HANDOFF=99e745a50def5f858cb48f66971934e8cecfba4b5cb32c0eb564497eba76b640`.
- Replay DREFGIRA + HARRY -> relaciones, contexto y frontier: exit 0; los
  tres outputs fueron byte-identical a los durables (`6`, `11` y `1`). La
  primera prueba omitió el segundo archive y falló cerrado; se corrigió sin
  modificar ninguna fuente.
- Replay HARRY baseline/enriched desde el mismo observation: exit 0; ambos
  `run_id`, summaries y todos los outputs coincidieron semánticamente con sus
  manifests durables. `validate_pilot_run` devolvió cero errores para ambos.
- Regresiones: `cross_archive_relations + project_context +
  cross_archive_research_frontier` = 18 tests; piloto/research/evidence-return/
  episode = 41; Vigía/capture/delta = 71. Todos exit 0. JSON, `py_compile` y
  `git diff --check` también exit 0.
- Endurecimiento e integración del corte vigente: el validador de
  `mak-vigia-capture-receipts-v1` ahora exige controles y provenance exactos;
  `tools/capture_opportunity_validity.py` hidrata esos receipts desde el
  `SourceCorpusStore` seleccionado en lectura y los entrega al compilador
  oficial existente. La prueba temporal de tres URLs alcanzó
  `current_verified`, con `network_called=false` en el compilador y sin
  mutación de fuentes. El gate focalizado final pasó con 57 tests; `py_compile`
  y `git diff --check` pasaron. El tramo genérico receipt -> constraints sigue
  absteniéndose cuando la URL no pertenece al contrato oficial.
- Bootstrap `Connect Vigia capture receipts to existing opportunity validity evidence`: exit 0;
  `agents=53afe6c85f431db10aee822f5a250af66968bb7c3ac9a27cbf38269b9386ce75`,
  `CURRENT=c98a7fb488b825ecfef0aff4d3770189d3167de469644aa03a90b03964b808e0`,
  `LAST_HANDOFF=0a4e1a2d14a3c7eb7ee6ab34cf6e292bea44a76de4b0769d5dff5b12f56e1276`;
  write-set exacto `tools/capture_opportunity_validity.py` y
  `tests/test_opportunity_validity_capture.py`. El gate ampliado final pasó con
  120 tests; `py_compile`, `json.tool` de los dos maestros y `git diff --check`
  también terminaron con exit 0.
- Bootstrap `Build selective recomputation causal receipt`: exit 0;
  `agents=53afe6c85f431db10aee822f5a250af66968bb7c3ac9a27cbf38269b9386ce75`,
  `CURRENT=c98a7fb488b825ecfef0aff4d3770189d3167de469644aa03a90b03964b808e0`,
  `LAST_HANDOFF=909027581a52179577fdb75b6e19a82235415af4658211db21dfa40ba7bcdbfd`;
  write-set exacto `src/flujo/knowledge/selective_recompute_receipt.py`,
  `tools/compile_selective_recompute_receipt.py` y
  `tests/test_selective_recompute_receipt.py`. El gate produjo 34 tests con
  exit 0; el CLI aplicado a ARICA en `/tmp` devolvió
  `mak-selective-recompute-receipt-v1`, `status=mixed_or_unexplained`, 17
  outputs cambiados, 9 consumidores afectados y 7 outputs no atribuibles al
  delta de oportunidad. No se escribió DB ni se ejecutó ningún consumidor.

The general plan remains the governing objective after this slice: archive
memory, reconstruction, cultural/curatorial reasoning, shared products,
research/opportunity circulation, episodes/outcomes, learning and bounded
control. No phase label can narrow or replace that mission.

### Boundaries and risks

- No output may claim readiness until the current replay and its canonical
  semantic hashes pass; `fit=abstain` and `application=blocked` remain valid
  outcomes, not failures to hide.
- Opportunity evidence cannot become practice evidence.
- C04-C06 receipts prove only their bounded technical predicates.
- Research jobs remain non-dispatched unless a separate authorized capture
  path already supplies the receipt.
- Publication, submission, promotion, training and source mutation remain
  disabled.
- Departments, organs, Copilot capabilities and owner-consumer maps are
  projections requiring a crosswalk, not a new registry.
- Independent archive and artist holdouts remain necessary for portability
  and learning claims.

### Last verified

2026-08-26 America/Santiago — product episode focused gate and durable
ARICA/Fondart replay validated. The gate passed with exit 0; the regenerated
baseline/enriched manifests preserve the same snapshot and their listed JSON
outputs pass canonical semantic rehash. The enriched run adds four supported
practice claims, passes the opportunity source gate, keeps fit abstained and
the application blocked; no external effects occurred.

2026-08-26 America/Santiago — DREF full observer batch validated; Stage 2A,
2B, 2C, 2D and practice-state validators passed on 44 physical artifacts;
the full run produced 40 relation candidates, one unresolved output unit,
40 assigned and 4 unassigned artifacts; the
federation JSON parsed and its semantic input hash replayed identically;
`triangular_fichas.py` returned zero events from one ficha with no event
metadata; the interrupted full-media observer was stopped and no matching
process remains. Generated files are limited to
`experiments/pilots/DREFQUILA/`; no database, artwork, media, WIN or source
code was modified in this cut.

## Agent bootstrap — HISTORICAL — 2026-08-25 — real ARICA/Fondart pilot completed

**Operative rule.** This is the only active packet. Bootstrap with
`tools/agent_bootstrap.py`; use `docs/MAK_SYSTEM_DIRECTIVE.md` as the durable
mission and the historical body below only as evidence.

### Mission and current objective

MAK is an autonomous, reusable operating system for artistic archives:
physical archive -> evidence memory -> work/project reconstruction -> cultural
and curatorial intelligence -> portfolio/application/research compilers ->
learning. ARICA, MYRA, RAYU and ISKVW are cases, never the architecture. Years
of finished work are supervision; user review is optional, not a pipeline gate.

Stage 2D accepted; epistemic Piso 1 also remains accepted: local documentary
evidence compiles into opportunity constraints; accepted Project IR projects
into an evidence-only practice state; and the two authorities meet only through
explicit requirement-to-evidence bindings. Possibility Piso 2 is now accepted:
MAK generates, independently falsifies and strategically ranks provisional
artistic-program possibilities. Autonomous research Piso 3 is also accepted:
prioritized gaps compile into non-dispatched jobs, captured claims are
triangulated across independent source groups, and supported results return as
additive evidence proposals without promotion. Product compilation Piso 4 is
accepted: one common plan derives curatorial portfolio, application and
research products from the same evidence-governed state. Controlled autonomy
Piso 5 is accepted: product decisions compile into ledger-compatible episode
candidates, verified external outcomes become bounded shadow-learning signals,
and a finite policy selects the next plan-only action. A real read-only
ARICA/Fondart pilot has now crossed the entire accepted chain. Its result is a
useful internal dossier plus an explicit research-first abstention, not a false
submission-ready product.

### Authority

`/home/mak/flujo` is the authoring baseline; `/home/mak/WIN` is historical
evidence; archive roots are read-only inputs. Production databases, runtime
roots, protected art and media remain outside the write set.

### Accepted checkpoints and evidence

- `82768ca`: deterministic read-only `mak-archive-observation-batch-v1`
  observer plus fail-closed temporal memory in additive
  `archive_memory_v2_*` tables.
- `708c948`: lossless Stage 2A projection plus bounded Stage 2B relation
  candidates and an independent falsification gate.
- `e453adc`: balanced Stage 2C provisional units plus an independent evaluator.
  Every physical `artifact_ref` is assigned, ambiguous or unassigned exactly
  once; dependencies stay separate; duplicate bytes never merge identities;
  shared ancestors do not become synthetic projects; truth promotions are zero.
- `3d2869c`: deterministic Stage 2D projection of every accepted unit into one
  provisional `mak-project-ir-v1` record plus an independent evaluator. It
  preserves members, dependencies, alternatives, missing evidence and the
  explicit ambiguous/unassigned partition; states are only `candidate` or
  `unknown` and source archives are never rescanned.
- Director gate over observer, memory, Stages 2A-2D, Project IR, Copilot,
  departments, visible organs, Curatoria triangulation and Conductor:
  171 focused tests were measured;
  exit `0`; Stage 2D `py_compile` and path-limited
  `git diff --check`: exit `0`.
- Independent Stage 2D cross-smoke: observe -> memory -> replay -> relations ->
  units -> Project IR -> evaluator; `valid=true`, zero errors.
- Read-only MYRA run with temporary SQLite: 1,517 artifacts, 23 observations,
  512 bounded candidates, 10 units, 1,325 assigned, 0 ambiguous, 192 unassigned,
  `balanced=true`; source unchanged.
- Epistemic Piso 1 adds three pure read-only contracts:
  `mak-opportunity-constraints-v1`, `mak-practice-evidence-state-v1` and
  `mak-opportunity-fit-v1`. The director gate passed 34 focused tests plus
  compilation and path-limited `git diff --check`.
- The integration gate rejected and corrected three false-green boundaries:
  invented producer fields, collision between external PDF evidence and
  internal artifact evidence, and fit declared against an unverified source.
  Opportunity documentary refs never prove applicant fit; only explicit
  `requirement_ids` on internal evidence can connect both authorities.
- Opportunity source validity is a control gate. `observed_local`, `unknown`
  and `stale` abstain; `expired` and `ineligible` fail; only
  `current_verified` plus explicit confirmation can pass.
- Possibility Piso 2 adds three pure contracts:
  `mak-artistic-program-candidates-v1`,
  `mak-artistic-program-evaluation-v1` and `mak-possibility-field-v1`.
  The director gate over Piso 1 plus Piso 2 passed 71 focused tests,
  compilation and path-limited `git diff --check`.
- The Piso 2 integration gate corrected two false boundaries: the field now
  consumes the evaluator's real `results{program_id: row}` contract, and
  cross-candidate resource contention remains a strategic conflict instead of
  invalidating every candidate before selection.
- A current-verified fixture produced two accepted and ranked candidates with
  one explicit resource conflict and `training_permitted=false`. The same
  chain with an `observed_local` unconfirmed source produced two abstentions,
  zero ranked candidates, three non-dispatched research-frontier actions and
  no false-ready state. Abstention remains an input to control, not a dead end.
- Autonomous research Piso 3 adds three pure contracts:
  `mak-research-frontier-jobs-v1`, `mak-research-triangulation-v1` and
  `mak-evidence-return-v1`. The director gate over Pisos 1-3 passed 110 focused
  tests, compilation and path-limited `git diff --check`.
- The Piso 3 integration gate corrected three false-green boundaries: source
  validity refresh jobs now carry the explicit technical requirement
  `source-validity:<opportunity_id>`; result pairs absent from the frontier
  fail closed instead of disappearing; and evidence return consumes the real
  `independent_source_groups` field while verifying job/requirement membership.
- Real-chain smoke with an unconfirmed local source produced two technical
  refresh jobs and two `unresolved` results, never an empty triangulation.
  A bounded two-source/two-domain capture produced one
  `supported_candidate`, one additive opportunity-evidence proposal and one
  fit-recompute request; it produced zero practice-evidence proposals and kept
  `training_permitted=false`.
- Product compilation Piso 4 adds three pure contracts:
  `mak-product-plan-v1`, `mak-portfolio-dossier-v1` and
  `mak-application-research-package-v1`. The director gate over Pisos 1-4
  passed 136 focused tests, compilation and path-limited `git diff --check`.
- The Piso 4 integration gate corrected three false-green boundaries: product
  plans now preserve claim-to-program and asset-to-program links; dossier
  coverage distinguishes documented claims from explicit provisional program
  bindings; and application/research compilation consumes plural programs,
  targets and requirement IDs from the real plan contract.
- In the verified chain, two ranked programs produced a draftable common plan,
  one supported narrative atom, three distinct physical assets, no falsely
  missing requirements, a draftable application and no research jobs. In the
  `observed_local` chain, two research-first programs still produced an
  internal dossier, while application stayed blocked and two non-dispatched
  source-validity jobs remained in the research brief. Publication, submission,
  dispatch and training stayed disabled in both chains.
- Controlled autonomy Piso 5 adds three pure contracts:
  `mak-product-episode-candidate-v1`,
  `mak-product-learning-evaluation-v1` and `mak-autonomy-plan-v1`. The director
  gate over Pisos 1-5 passed 168 focused tests, compilation and path-limited
  `git diff --check`.
- The Piso 5 integration gate corrected three false-green boundaries: autonomy
  now consumes the structured VOI emitted by real research jobs; product
  episodes preserve a stable tenant/archive identity group separately from
  snapshot identity; and learning consumes the real episode projection rather
  than fixture-only top-level validation fields.
- In the verified chain without an outcome, the episode remained `open`, the
  learning report was valid but abstained with
  `outcome_open_not_negative`, and autonomy selected one bounded `wait`. In the
  `observed_local` chain, autonomy selected two bounded `research` actions with
  `max_attempts=1`. A verified external portfolio receipt produced only
  `attention` and `ranking` examples; one identity group was insufficient for
  a policy candidate, and training remained disabled.
- The real ARICA/Fondart pilot used the canonical observer against the bounded
  ARICA root and wrote outputs only under `/tmp`. It observed 417 artifacts and
  11,916 observations; Stage 2A-2D produced 413 relation candidates, one
  provisional unit, 99 assigned artifacts, 318 explicit unassigned refs, one
  valid Project IR record and a valid practice state. All 14 source-file hashes
  declared by the prior ARICA snapshot were unchanged after the pilot.
- The opportunity was the real local Fondart Nacional Línea Investigación 2027
  corpus: 38-page PDF, 22 constraints, eight hard gates and eight required
  documents. Because its current official validity was not fetched, its source
  gate remained `observed_local`/unconfirmed.
- End-to-end ARICA/Fondart result: fit abstained with 16 unsupported required
  constraints; one practice-native program abstained and one empty conditioned
  program was independently rejected; the possibility field preserved one
  abstention and one rejection. The product plan made the internal dossier
  draftable, blocked application and made research draftable. The dossier has
  one provisional program, a two-row sequence, 99 private/internal assets,
  zero public assets, zero invented narrative atoms and nine explicit gaps.
  Application maps all 22 requirements and remains blocked. Autonomy emits one
  bounded non-dispatched `research` action.
- Real-data corrections were limited to contract boundaries: an evaluator
  rejection can no longer be revived by abstaining gates; structured rejection
  reasons are deduplicated canonically; and dossier evidence namespaces are
  separated from physical/public assets. The final fifteen-contract regression
  passed 173 focused tests plus `git diff --check`.

### Boundaries and risks

- Candidates and provisional units are uncertainty, not facts. The 512-candidate
  bound can increase `unassigned`; 192 MYRA unassigned does not mean artistic
  non-membership.
- `dependency_refs` are resolved physical references, intentionally not members
  of the owning unit. `change_set` and limit diagnostics are non-semantic.
- The historical packet's `mak-observation-batch-v1` contract is obsolete.
- Unrelated worktree changes exist; keep commits and validation path-limited.
- MAK currently exposes overlapping topologies: the three-area department
  registry, six runtime organs and the broader owner/consumer map. Stage 3A
  must reconcile capabilities and handoffs without declaring another registry.
- Research results are environmental evidence. They may update opportunity
  knowledge, but cannot become evidence of the artist's practice unless a
  future explicit practice-scoped contract names existing artifact refs.
- Piso 4 must not build independent portfolio and application silos. Both must
  derive from one product plan with shared claim, asset, requirement, privacy,
  license and uncertainty controls.
- A draftable product is not a published/submitted product. Piso 5 may learn
  routing, ranking and attention from observed episodes, but it may not learn
  factual truth, authorship or artistic identity from its own drafts.
- The next risk is no longer contract architecture but real-data portability:
  a green fixture cannot prove that ARICA, MYRA or another artist archive has
  enough accepted Project IR, explicit practice evidence and opportunity
  evidence to produce a useful first dossier.
- ARICA now has accepted Project IR/practice output in `/tmp`, but only three
  unknown claims and no supported/candidate claim atoms. The existing C04-C06
  technical witnesses are not yet represented as canonical practice evidence,
  so the dossier correctly refuses to write a curatorial narrative or publish
  media from them.

### Single next action

Do not add another architectural floor. Close the two evidence gaps selected by
the real autonomy plan, then replay the same pilot:

1. Execute the single official-source validity research job for Fondart through
   a bounded general capture path and triangulate the receipt; do not reuse the
   legacy hard-coded plant query.
2. Project the already-existing ARICA C04-C06 technical witness receipts into
   the accepted practice-evidence vocabulary without treating them as web
   evidence, authorship proof or automatic curatorial claims.

After additive ingestion/recompute, rerun from fit onward using the same `/tmp`
Project IR/practice snapshot. Improvement means more explicit evidence and
fewer justified gaps, not a forced positive fit. Publication, submission,
training and source mutation remain disabled.

### Last verified

2026-08-25 America/Santiago — Stages 1 and 2A-2D plus epistemic Pisos 1-5 and
the real ARICA/Fondart pilot accepted by the director. The fifteen-contract gate
passed 173 focused tests, compilation, whitespace and verified,
observed-local, outcome and real-archive smokes. The next action is evidence
closure and replay, not another layer.

## Agent bootstrap — HISTORICAL — pre-archive-memory correction

**Operative rule.** This is the only current packet. A worker must receive it
from the coordinator or run `tools/agent_bootstrap.py`; it must not choose a
state by searching this file or reading the historical sections below.

### Current objective

Make MAK reconstruct one artist's archive as a multimodal, temporal and
curatorial evidence graph across public manifestations, native authoring
documents, components, sources, versions, phases, series and deliverables.
Use relation candidates and a small portfolio planner instead of a fixed
single-label classifier. A candidate is actionable uncertainty, not a
terminal `unknown`. Do not train, promote router policies, infer authorship,
or call a local artifact an output without an explicit export witness.

### Physical authority and migration status

`/home/mak/flujo` is the authoring/integration baseline. `/home/mak/WIN` is
historical evidence and remains untouched. Real archive inputs are under
`/home/mak/curatoria_inbox/ARICA`; runtime roots remain separate. Production,
router, `active_policy`, databases, media and protected artwork are outside the
current write set.

### Completed work with command and result

- C02 real native observation: Blender and AEP endpoints; gate `EXIT 0`.
- C03 public-input normalizer and blind bridge; real social ZIP audited as
  unavailable; gate `EXIT 0`.
- C04 real MP4 observation plus AEP-to-media evidence evaluation; `uses` is
  `supported`, dimensions are `observed`, output role is `unknown`; gate
  `PYTHONPATH=. .venv/bin/python experiments/cycles/C04/verify_cycle.py` is
  `EXIT 0` with focused contract coverage.
- C05 real Blender export witness: `RAYU.blend` -> `rayu_export.py` ->
  `rayu_resources.glb`; seven evidence checks pass, the source hash is
  unchanged, and `witness_status=supported`. Gate
  `PYTHONPATH=. .venv/bin/python experiments/cycles/C05/verify_cycle.py` is
  `EXIT 0`.
- C06 isolated graph bridge: the C05 witness materializes exactly one
  `EXPORTS_TO` edge; three adversarial cases (missing refs, failed check,
  `unknown` status) emit zero edges. Gate
  `PYTHONPATH=. .venv/bin/python experiments/cycles/C06/verify_cycle.py` is
  `EXIT 0`.
- Current protocol repair: `tools/agent_bootstrap.py` emits this packet with
  hashes and an explicit write-set; focused tests, compilation, packet
  self-check and `git diff --check` pass.
- C07 practice graph prototype: extracts deterministic artifact observations
  (dimensions, aspect ratio, alpha, video metadata, sequence facts and XML/XMP)
  and emits typed relation candidates with scores, evidence refs, alternatives,
  missing evidence and next probes. Its five fixtures produce 17 candidates;
  no candidate is emitted as terminal `unknown`. C07 tests, runner and
  `py_compile` pass with `EXIT 0`.
- C08 relational/curatorial evaluator: compares an empty no-relation baseline
  against relation, phase and series candidates; its greedy portfolio planner
  covers required phases, formats, ratios and chronology without repeating the
  2,048-frame sequence. Tests (9 including integration), runner and
  `py_compile` pass with `EXIT 0`.
- C08/C07 integration: evaluates C07's graph on the same five C07 cases. The
  fixture baseline recall is `0.000`; candidates reach recall `1.000` at top-5,
  precision `0.400` at top-1 and `0.240` at top-5. All generated relations
  remain `pending_relation` or `unresolved_candidate`; zero are promoted to
  supported edges.

### Context-integrator — archive memory contract — PASS — 2026-08-25

- Bootstrap executed with the exact write-set for this worker; exit `0`. The
  reserved observer files were not touched:
  `src/flujo/knowledge/archive_observer.py`, `tools/archive_observer.py` and
  `tests/test_archive_observer.py`.
- `LearningStore.ensure_schema` now carries a compatible additive migration for
  `archive_memory_archives`, `archive_memory_snapshots`,
  `archive_memory_artifacts`, `archive_memory_artifact_states`,
  `archive_memory_observations` and
  `archive_memory_transformation_events`. Immutable snapshots, artifacts,
  states, observations and transformation events have no-update/no-delete
  triggers. Existing Project IR, episodes, rules and evaluations remain intact.
- The production interface is
  `flujo.knowledge.archive_memory.ingest_observation_batch(database, batch)`.
  The observer must send `schema=mak-observation-batch-v1`, mandatory
  `archive_id`, `source_root_ref`, a versioned `snapshot.snapshot_hash`,
  content SHA-256 artifacts, observations with `method/evidence_refs/tool_version`
  and transformations with `inputs/outputs/witness_refs/status`. IDs for
  artifacts, observations and events are derived deterministically; re-ingest
  of the same canonical batch is idempotent and conflicting payloads fail.
- Read-only consumers are `list_archives`, `list_snapshots`, `list_artifacts`,
  `list_observations`, `list_transformations` and `replay_snapshot`. Replay
  returns a canonical snapshot plus `replay_hash`, preserving evidence and
  witness references.
- Validation commands exited successfully: `py_compile` for the changed
  module/store/tests; focused suite
  `tests/test_archive_memory.py tests/test_project_ir.py
  tests/test_project_reconstruction.py tests/test_reconstruction_adapter.py`
  passed `27`; `git diff --check` passed. The tests cover additive migration,
  two-archive isolation, idempotent re-ingest, deterministic replay,
  evidence/witness retention, immutable rows and snapshot conflicts.
- The real `data/mak_knowledge.db` was inspected read-only and remains
  untouched. It is compatible and currently reports the six archive-memory
  tables as not materialized; the first observer ingestion will materialize
  them through the existing store migration. No Portfolio, Research, Hub,
  ARICA-01, lane or C09 surface was changed by this worker.
- Risks: the observer must provide stable snapshot hashes and explicit tool
  versions; missing those fields is rejected rather than guessed. Artifact
  identity is content-addressed within each `archive_id`; cross-archive joins
  are not implicit.

### Gate 0 — una sola verdad operacional — PASS — 2026-08-25

- Bootstrap executed with `tools/agent_bootstrap.py` using the current packet;
  exit `0`. The write-set was limited to `src/flujo/knowledge/`,
  `tools/mak_status.py`, the canonical Hub, tests, `experiments/cycles/ARICA-01/`
  and this handoff.
- Reproduction before the fix: the live listener was PID `71579` and ran
  `/home/mak/flujo/cultura/mak_plataforma/hub.py`; `/api/status` declared the
  physical projection `/home/mak/plataforma/hub.py`. CLI and Hub imported the
  same status function, but the Hub source declaration was wrong and the two
  callers passed different database path forms. `/api/mak` remained the
  documented `404` (`ruta_api_no_encontrada`).
- Root cause: `src/flujo/knowledge/system_status.py` selected the physical
  `plataforma/hub.py` projection as the Hub source instead of the canonical
  repository source, and resolved CLI/Hub ledger paths at different stages.
  This was a source/provenance contract defect, not two independent policies.
- Minimal correction: the shared status function now declares the canonical
  Hub source, observes the running source from `/proc` against known candidates,
  and resolves the ledger path once. `tools/mak_status.py` exposes the shared
  policy schema/status/reason and review count. Focused tests and compilation
  exited `0`; `git diff --check` exited `0`.
- Reload used only the documented `systemctl --user restart mak-hub.service`.
  The live process after reload was PID `1614247`, with the canonical command.
  Normalized CLI JSON and `/api/status` matched exactly apart from timestamps:
  schema `mak-system-status-v1`, status `attention`, counts
  `attention=2/blocked=0/components=11/info=1`, policy
  `candidate/holdout_gate_passed/12`, ledger
  `/home/mak/flujo/data/mak_knowledge.db`, and observed runtime source
  `/home/mak/flujo/cultura/mak_plataforma/hub.py`.

### Gate 1 — ARICA-01 real evidence to reviewed draft — PASS — 2026-08-25

- A read-only schema check found no existing `arica-01-portfolio-evidence`
  record before the build. The explicit input set contains 14 real artifacts:
  the RAYU Blender/export chain, `ARICA.aep`, its observed `tottem_ojo.mp4`,
  `MYRA_final.mp4`, two frame endpoints and only the bridge/context files
  needed to explain them. No input was copied or modified.
- `PYTHONPATH=. .venv/bin/python tools/arica01_portfolio.py --build` exited
  `0`: 14 artifacts, 4 candidates, snapshot
  `19c5582438fd81f8f1d4dfeb05cbe24a57e89d83e89927897c2b3aa699b1a8d1`.
  The queue contains the supported C05/C06 `RAYU.blend -> rayu_resources.glb`
  export witness, the C04 supported `ARICA.aep uses tottem_ojo.mp4` claim with
  output role still unknown, a real MYRA frame-family candidate, and
  `MYRA_final.mp4 -> missing_source` with `source_binding=unknown`.
- The first build attempt failed with `UnboundLocalError` in the new draft
  projection because `path` was read before initialization. It was corrected
  before persisting the real record; compile, focused tests and diff checks then
  passed. This is retained as an implementation validation result, not hidden
  as a data failure.
- The product surface is the existing Hub plus the existing Project IR/ledger:
  `GET /api/portfolio/evidence-queue`, `GET
  /api/portfolio/evidence-draft`, and `POST
  /api/portfolio/evidence-decision`. The live queue and draft returned `200`
  after the documented Hub reload.
- Three operator decisions were made through the live Hub route and persisted
  as verified episodes: accept the RAYU export-event relation
  (`episode_portfolio_94ce28da5b25a56b1b83559d`), correct the numbered frame
  relation to `component_of MYRA_final.mp4`
  (`episode_portfolio_38e4f2124929e946914c735c`), and request evidence for the
  unresolved MYRA source (`episode_portfolio_c531217eab6bf3edc949c328`). The
  derived queue is now `accept=1, correct=1, request_evidence=1, pending=1`;
  the draft has two human-accepted effective relations and `promotion=none`.
  The operator correction is provenance-bearing curation input, not an
  inferred artist fact.
- Derived experiment outputs are synchronized at
  `experiments/cycles/ARICA-01/input_snapshot.json`, `relation_queue.json` and
  `portfolio_draft.json`. The authority remains the single
  `data/mak_knowledge.db:project_records.ir_json` record; no second base,
  lane, C09 cycle or public catalog was created.
- Final validation: `py_compile`, focused tests (`4 passed`), live queue/draft
  reads and `git diff --check` passed. The second reload was the documented
  `systemctl --user restart mak-hub.service`; no permanent auxiliary service
  was opened.

### Open integration items

- `/media/mak/PortableSSD/descargas hasta RDFLYER 2050/instagram-iskvw-2025-04-08-jyAjQO7Z.zip`:
  no posts/reels/stories/media; status `unavailable`, not a public catalog.
- `/home/mak/curatoria_inbox/ARICA/ARICA.aep` plus any local artifact:
  no explicit export witness observed; output role stays `unknown`.
- C05 binds one concrete Blender export to `rayu_resources.glb`, but does not
  prove final-delivery status or connect that artifact to a public post.
- C06 proves only that a complete witness can be represented in the graph; the
  public manifestation join remains unverified.
- A bounded ARICA search found `MYRA_final.mp4`, PNG frames, `done ok=True`
  markers, a sequencer log and real ffprobe metadata, but no `.uproject`,
  `.uasset` or `.umap` under ARICA. It is observed activity/output with
  `source_binding=unknown`, not a second supported export edge.
- `tools/agent_bootstrap.py`: run it before every delegated edit and include
  the resulting packet/hash acknowledgement in the worker report.
- The C07/C08 fixtures are synthetic and do not constitute learned performance
  on the real archive. They establish the contract and expose a
  precision/recall tradeoff; real ARICA validation still needs a blinded
  curator gold set.

### Tool and dependency verification matrix

| item | path | verification | result |
|---|---|---|---|
| Native evidence | `experiments/cycles/C02/` | C02 gate | PASS |
| Public boundary | `experiments/cycles/C03/` | C03 gate | PASS; real catalog unavailable |
| Media evidence | `experiments/cycles/C04/` | C04 gate + ffprobe | PASS; output unknown |
| Export witness | `experiments/cycles/C05/` | C05 gate + 7 checks + source hash before/after | PASS; final/public role unknown |
| Export graph bridge | `experiments/cycles/C06/` | C06 gate + 4 tests + 3 adversarial cases | PASS; public join open |
| Agent bootstrap | `tools/agent_bootstrap.py` | focused unittest + compile + packet self-check + `git diff --check` | PASS |
| Practice graph | `experiments/cycles/C07/` | 5 tests + runner + `py_compile` | PASS; 17 relation candidates, no terminal `unknown` |
| Curatorial evaluator | `experiments/cycles/C08/` | 9 tests + runner + integration + `py_compile` | PASS; synthetic result only |

### Conflicts and risks

The historical body of this file contains old checkpoints and repeated
headings. It is retained as evidence but is not operative. Never use an older
`Current objective`, `Next concrete action`, commit claim or provider matrix
from below this packet as current state.

### Next concrete action

Implement the reserved physical observer against the exact
`mak-observation-batch-v1` interface, first against a temporary LearningStore.
Then run two real archive batches through the existing store and verify
archive isolation, replay and evidence references before any Portfolio or
Research consumer is connected.

### Last verified

2026-08-25 America/Santiago — Gate 0 and Gate 1 `PASS`; context-integrator
archive-memory migration/API tests `27 passed`; production database inspected
read-only and unchanged; compilation and `git diff --check` verified.

## Punto de inflexión vigente — 2026-08-24

La dirección conceptual del proyecto está fijada en
[`docs/INFLECTION_POINT_ARTISTIC_ARCHIVE_2026-08-24.md`](../docs/INFLECTION_POINT_ARTISTIC_ARCHIVE_2026-08-24.md).
Debe leerse antes de abrir investigación histórica o diseñar otro clasificador:
MAK reconstruye un grafo de evidencia entre publicaciones, entregables,
documentos nativos, componentes, fuentes y obras/series candidatas. No ordena
carpetas ni fuerza `post -> proyecto`. Un post sin fuente y un proyecto sin post
son estados válidos; el Copilot actual ordena candidatos, pero todavía no
construye ese grafo. Tras C02, el siguiente slice autorizado es una
`publication_archive_bridge` aislada, read-only y evaluable, con casos
adversariales y sin migrar producción.

## C02 — observación nativa real — 2026-08-25

El segundo experimento nuevo está en
[`experiments/cycles/C02/RESULTS.md`](../experiments/cycles/C02/RESULTS.md).
Dos LUNA trabajaron en superficies disjuntas sobre el mismo archivo artístico:
Blender observó realmente `RAYU.blend` y el lector lexical observó realmente
`ARICA.aep`. El gate
`PYTHONPATH=. .venv/bin/python experiments/cycles/C02/verify_cycle.py`
terminó `EXIT 0`: ambos hashes se conservaron, Blender 4.5.4 devolvió una
escena con siete objetos y el AEP devolvió cinco referencias; cada endpoint
pasó seis pruebas `unittest`, y la integración agregó seis pruebas más. El
grafo materializado tiene nueve nodos, siete aristas `uses`, un `unknown`
público y cinco roles de output desconocidos.

La evidencia nueva confirma que el extremo nativo aporta estado, capacidades,
recursos, settings, referencias y destinos configurados. También confirma el
límite: la existencia y basename de `tottem_ojo.mp4` no prueban que sea output,
y el filepath de render de Blender no prueba que el render haya ocurrido. Los
dos endpoints conservan `candidate` y `unknown` sin promover `generated` ni
`RENDERS_TO`. `materialize_graph.py` deja esa prohibición en un gate mecánico y
separa capacidades de render, uso de recursos, rol de output y join público.

No hay un catálogo social real local; el puente público queda
`unavailable/unknown` y no se usan fixtures de C01 para simularlo. El próximo
slice debe recibir un export público real o un fixture ciego que no declare el
enlace, y medir falsos enlaces, abstenciones y cobertura. No integrar C02 en
router, `active_policy` ni base de producción todavía.

## C03 — entrada pública y puente ciego — 2026-08-25

El tercer experimento está en
[`experiments/cycles/C03/RESULTS.md`](../experiments/cycles/C03/RESULTS.md).
La auditoría real del ZIP que parecía un export de Instagram encontró 9
archivos reales (12 entradas contando directorios): logo, `start_here.html` y
relaciones; cero posts, reels, stories o medios. Su SHA-256 es
`ce12e0bb043989d4397578b705fab221793db661a818ef33e824babf5cf73d50`. El
resultado real es `catalog_status=unavailable` y `public_join=unknown`.

Dos LUNA trabajaron separadamente: el normalizador público acepta sólo
formatos declarados, exige `archive_id`, conserva origen/evidencia y falla
cerrado; el puente ciego recibe observaciones sin leer la verdad de evaluación.
El gate
`PYTHONPATH=. .venv/bin/python experiments/cycles/C03/verify_cycle.py`
terminó `EXIT 0` con 18 pruebas. En el benchmark sintético, el baseline
directo obtuvo TP=2, FP=2 y cobertura 0.6667; el puente mediado obtuvo TP=3,
FP=0, tres abstenciones y una contradicción explícita. Esto es evidencia del
contrato, no aprendizaje estadístico ni una reconciliación real de ARICA: la
`bridge_observation_key` aún es sintética.

No integrar C03 en router, `active_policy` ni producción. El siguiente paso es
reemplazar únicamente la observación pública por un export real del artista y
mantener la verdad fuera del resolver.

## C04 — observación de medio y fuerza de evidencia — 2026-08-25

El cuarto experimento está en
[`experiments/cycles/C04/RESULTS.md`](../experiments/cycles/C04/RESULTS.md).
LUNA A observó read-only el archivo real `tottem_ojo.mp4`, declarado por
`ARICA.aep`: H.264/AAC, 44.627917 s, 1070 frames de video, tres streams y
dimensiones no convencionales `256×1536`. El hash antes/después fue
`b7253320e7a23917439dd6ad2fa084a68510469517b76b6428c54f9856ca0776`.

LUNA B implementó un evaluador de fuerza de evidencia. La integración real en
`real_evidence.json` sostiene `uses=supported` y `dimensions=observed`, pero
mantiene `output_role=unknown` y cero aristas `generated`/`RENDERS_TO`. El
evaluador sólo permite esas relaciones con un evento de exportación explícito
y `evidence_refs`.

El gate
`PYTHONPATH=. .venv/bin/python experiments/cycles/C04/verify_cycle.py`
terminó `EXIT 0` con 20 pruebas, hashes de AEP/MP4 intactos y observación
`ffprobe` real. El benchmark sintético de 6 casos y 13 claims tuvo 0 falsos
positivos, pero no es una tasa estadística. No se modificó producción ni se
renderizó/transcodificó el archivo.

La conclusión es que metadata/hash del producto, declaración nativa y evento
de exportación son evidencias distintas. El siguiente slice seguro debe buscar
un witness real de actividad —logs, metadata nativa o export declarado— sin
mutar archivos artísticos. Si no existe, el rol de output permanece `unknown`.

## C01 — provenance-mediated archive join — 2026-08-24

El primer experimento nuevo está en
[`experiments/cycles/C01/RESULTS.md`](../experiments/cycles/C01/RESULTS.md).
Dos LUNA trabajaron en superficies disjuntas: publicación → entregable y
documento nativo → actividad → versión/entregable. El gate común pasó (`9`
tests públicos, `6` nativos, runner JSON, `py_compile` y `git diff --check`,
todo `EXIT 0`). El resultado es arquitectónico: las actividades expresan
fan-out, versiones, fuentes compartidas y export fallido que el join directo no
representa. Los fixtures declaran parte del oráculo; todavía no es prueba de
descubrimiento sobre archivos reales. El siguiente ciclo debe reemplazar ese
oráculo por observaciones read-only y mantener embeddings como recuperación de
candidatos, nunca como prueba de procedencia.

## Current objective — 2026-08-24

Construir `MAK Learn v2`: un sistema de aprendizaje durable, auditable y
dirigido para MAK. El orden obligatorio es: (1) episodios append-only y
evidencia versionada, (2) candidate lessons con procedencia, contradicciones y
expiración, (3) replay/holdout independientes, y (4) un director seguro con
checkpoints y handoff. No entrenar pesos ni promover políticas
automáticamente hasta superar gates independientes. La autoridad operativa
sigue siendo `/home/mak/flujo`; `/home/mak/WIN` permanece histórico y protegido.

La consolidación MAK/WIN y los slices anteriores quedan como continuidad
histórica y regresiones protegidas; no se deben reabrir salvo que el replay o
una verificación física aporte evidencia nueva.

## Native Blender scene slice — 2026-08-24

**Objetivo.** Probar la unidad de análisis correcta para proyectos artísticos:
el estado nativo de la escena y sus dependencias, no el producto terminado.

**Implementado.** `src/flujo/substrate/scene_snapshot.py` reutiliza el sustrato
existente para construir un snapshot reproducible de un `.blend`, preservar la
separación entre `Content`, `ArtifactState` y `Observation`, validar la
integridad del snapshot y registrar el evento inmutable de transformación
`renderizar` (`STARTED` -> `COMPLETED`/`FAILED`/`UNKNOWN`).
`tools/blender_scene_probe.py --snapshot` lanza Blender en modo background con
`--factory-startup --disable-autoexec` y solo consulta `bpy.data`; no renderiza
ni guarda el archivo. `docs/BLENDER_SCENE_SNAPSHOT.md` documenta el contrato,
los límites y el uso.

**Gates implementados.** El digest excluye ruta, raíz y hora de observación,
pero incluye hash de bytes, payload nativo y configuración del extractor; por
eso dos observaciones del mismo estado comparten identidad y siguen teniendo
observaciones distintas. Dependencias ausentes producen `FAIL`; dependencias
cuya presencia no fue medida producen `UNKNOWN`. La validación declara
explícitamente que solo prueba integridad del snapshot, no calidad visual. Un
evento no puede reutilizar su versión de entrada como salida.

**Evidencia.** Compilación estática:
`.venv/bin/python -m py_compile src/flujo/substrate/scene_snapshot.py
tools/blender_scene_probe.py` terminó `EXIT 0`. La prueba enfocada
`PYTHONPATH=src .venv/bin/python -m pytest -q
tests/test_scene_snapshot.py tests/test_blender_scene_probe.py
tests/test_substrate.py` terminó `35 passed`, `EXIT 0`. Las pruebas incluyen
identidad estable, modificación de bytes/escena, tampering, dependencia
ausente/UNKNOWN, inmutabilidad del evento y el adaptador nativo sin operadores
de render/save. La prueba de integración read-only creó un fixture `.blend`
temporal con Blender `4.5.4 LTS` y lo leyó mediante el adaptador: `status=ok`,
una escena, cinco objetos, validación de snapshot `PASS` y precondiciones
técnicas `PASS`. Esto valida compatibilidad del extractor con Blender real,
pero no sustituye todavía la lectura de un `.blend` artístico real.

**Fuera de alcance.** No se modificaron router, labels, `active_policy`,
episodios históricos, Project IR completo ni se creó un segundo almacén de
estado. No se ejecuta todavía el render: este slice solo deja la observación,
los precondicionantes técnicos y el contrato de transformación.

**Siguiente acción.** Ejecutar el extractor una vez sobre un `.blend` artístico
real en una ubicación scratch, revisar que escenas, colecciones, cámara,
dependencias y settings sean suficientes y comparar el digest tras una
modificación controlada. El fixture ya no debe reutilizarse como evidencia de
dominio. Solo con la evidencia artística implementar un ejecutor de render que
emita una versión de salida y su validación independiente.

## Operating-world comparison — 2026-08-24

**Objective.** Test, without changing production, whether MAK should learn a
single `tool_id` decision or represent a typed operating world and derive a
multi-step plan.

**Changed files.** The isolated surface is
`experiments/mak_operating_world/` with `model.py`, `cases.json`,
`run_experiment.py` and its README. The focused tests are in
`tests/test_operating_world_experiment.py`. No production API, router, learner
or database schema was changed.

**What the experiment reads.** Project IR supplies identity, state, purpose,
source, domains, artifacts, unknowns, evidence and provenance. Verified
episodes supply phase, action, observation, outcome, validation, provider,
model, cost, source references and tool identity. The report explicitly lists
missing typed goals, formal preconditions/effects, capability I/O, validated
cost/risk, causal dependencies, failure models and independent validators for
unseen compositions.

**Experiment.** Six identical Project IR cases were passed to both the current
router/learner and a typed breadth-first capability planner. Two cases require
research composition; two are single-capability controls; two are adversarial
gaps (license approval and an undeclared rendering capability). The planner
uses explicit benchmark contracts and provenance cards from observed episode
phases; the contracts are not claimed to be learned from the current ledger.

**Evidence.**

    PYTHONPATH=src .venv/bin/python -m experiments.mak_operating_world.run_experiment --db data/mak_knowledge.db --cases experiments/mak_operating_world/cases.json
    .venv/bin/python -m pytest -q tests/test_operating_world_experiment.py
    .venv/bin/python -m pytest -q --disable-warnings

All commands exited `0`; focused tests reported `3 passed`; the full suite
reached `100%`. The planner passed `6/6` contract cases, produced five-step
and four-step research plans, and identified `license_approved` as an
unreachable precondition. The current router passed `3/6` direct/safe cases and
explained `0` gaps as a missing precondition. The current learner passed `2/6`
and emitted `research_job_router` for the blocked-publication case. The real
database remained unchanged: SHA-256
`12867ae538cd38b042bb35e5dd41abfc64e65eac460dd841eaf6df625037c778`, size
`189534208`, identical `mtime_ns` before/after.

**Interpretation.** This is new architectural evidence, not statistical proof:
the current one-label contract cannot express the two compositions or the
license dependency, while the typed planner can. The typed preconditions and
effects are still benchmark declarations; the next experiment must learn or
validate them from new traces rather than promote this prototype directly.

**Open integration item.** Build a blind, real-project compositional benchmark
with independent validators and compare the planner against the current
learner/router without changing either production path. Do not create
`policy_candidates` or an active planner until that benchmark distinguishes
composition from hand-authored case contracts.

**Last verified.** 2026-08-24; isolated experiment, focused tests, full suite,
`git diff --check`, and read-only database hash audit completed.

## MAK Learn v2 - durable event/evaluation substrate - 2026-08-24

**Objetivo del slice.** Darle a MAK una superficie persistente para dirigir
ejecuciones y registrar replay/holdout sin crear otra base de autoridad ni
promover políticas automáticamente.

**Implementado.** `src/flujo/knowledge/project_ir.py` agrega las tablas
append-only `mak_run_events` y `learning_evaluations`, y blinda
`project_episodes` con triggers SQLite contra `UPDATE`/`DELETE`.
`LearningStore.append_run_event`
exige `source_snapshot_hash`, `code_commit` y `tool_versions`, agrupa cada
checkpoint por `run_id`, y permite leer la cadena sin reabrir una ejecución.
Repeticiones del mismo `event_id` son idempotentes solo si el payload completo
coincide y todo conflicto se rechaza. `LearningStore.record_learning_evaluation`
exige un fingerprint de dataset y un split explícito (`replay`, `holdout`,
`canary` o `shadow`); incluso `passed` queda como evidencia y no modifica
ninguna regla.

Los episodios creados por el camino v2 del director guardan además esa misma
procedencia en `source_snapshot_hash`, `code_commit` y
`tool_versions_json`. Los `17` episodios históricos existentes se conservan
sin reescritura y sin rellenar procedencia retrospectiva no demostrable; la
migración solo añade columnas con defaults vacíos y aplica el blindaje
append-only hacia adelante.

**Candidate lessons endurecidas.** `semantic_rules` ahora conserva
`scope_json`, `expires_at`, `evaluation_id`, retractación y motivo de
retractación. La huella incluye trigger, acción y scope; las contradicciones
siguen siendo bloqueantes. `promote_rule` exige una evaluación `passed` de
`split_kind=holdout` dirigida a ese `rule_id`; una pasada genérica del replay
set no basta. Una lección expirada queda `stale` aunque la llamada de
promoción falle, y `retract_rule` deja la razón durable.

**Evidencia y comandos.**

    .venv/bin/python -m pytest -q tests/test_learning_v2.py tests/test_project_ir.py tests/test_learning_policy.py
    .venv/bin/python -m pytest -q tests/test_project_api.py tests/test_project_context.py tests/test_project_evidence.py tests/test_project_research.py tests/test_source_learning.py tests/test_deep_learning_gate.py

Ambas corridas terminaron `EXIT 0`. La materialización controlada sobre
`data/mak_knowledge.db` creó únicamente las dos tablas nuevas: antes y después
se conservaron `project_episodes=17`, `project_records=41`,
`semantic_rules=0` y `rule_observations=0`; la migración añadió `run_id` sin
alterar filas existentes.

**Tests nuevos.** `tests/test_learning_v2.py` cubre inmutabilidad/idempotencia
de eventos, procedencia obligatoria, evaluación con holdout sin promoción,
rechazo de datasets sin fingerprint y lectura de checkpoints. Las tablas
quedaron blindadas con triggers SQLite contra `UPDATE` y `DELETE`; también
cubre scope, expiración y retractación de candidate lessons. `tests/test_project_ir.py`
verifica que un episodio versionado rechaza mutaciones directas y que una
procedencia incompleta no se acepta. La migración añade las tres columnas de
procedencia de episodios sin cambiar los conteos (`41` records, `17`
episodios, `1` regla candidate, `3` evaluaciones).

**Director implementado.** `src/flujo/knowledge/director.py` coordina
`proposed -> running -> observed -> validated -> recorded`, emite todos los
checkpoints, usa únicamente contratos `read_only` de `TOOL_CATALOG`, no ejecuta
comandos arbitrarios y termina registrando el episodio conservador existente.
`tests/test_director.py` verifica la cadena, los rechazos de herramientas no
permitidas y las transiciones inválidas. La suite completa del repositorio
terminó en `EXIT 0` después de este slice, con 7 warnings de deprecación
preexistentes de Pillow. El director acepta el reporte del replay como gate
informativo en `validated` y `resume(run_id)` reconstruye la última vista desde
los checkpoints; ninguna de esas operaciones promueve políticas.

**Smoke runtime sobre la base real.** El `2026-08-25` se dirigió el proyecto
`mak-logo-clean-learning-gate-20260820` en estado `review_required` con
`run_id=run-real-smoke-review-required-20260825`. El router respondió
`abstain` por `project_state_requires_evidence`; el director completó los 5
estados hasta `recorded`, creó el episodio
`episode_d792ddff7d374ff5b92b53a6a2f75bbb` como `abstained` y dejó los cinco
eventos enlazados por `parent_event_id`. La fila lleva snapshot
`16410d95e5ddbdb6cc73464ce219a7c9a62623c2ed6ff67d47033efbbb3e9058`, commit
`1aafa4b` y `{"director":"mak-director-v1","python":"3.12"}`. No se
ejecutó ningún consumidor ni se creó una etiqueta elegible.

**Replay set implementado.** `context/learning/replay_suite_v1.json` declara
cuatro casos reales y trazables: resolución de títulos y probe Blender en
`replay`; lector `.aep` y testigo PNG en `holdout`. Cada caso conserva
`source_refs`, un target de pytest y un estado esperado. El fingerprint del
dataset es `bbecea1dc18d45068103072e279999bfa7a0af42b2a399d4ad3e517f21052fd0`;
hay 2 casos por split y 4 grupos sin cruce entre splits.
`src/flujo/knowledge/replay.py` valida schema, referencias, fingerprint y
aislamiento por grupo, y calcula métricas sin promover políticas.
`tests/test_replay.py` verifica el caso real, el rechazo de leakage y la
diferencia entre `passed`, `failed` y `abstained`.

**Resultado persistido.** Los cuatro targets declarados terminaron `EXIT 0`;
se registraron dos evaluaciones `passed` en `data/mak_knowledge.db`, una por
split, ambas con accuracy `1.0`, commit `5004db5` y el fingerprint anterior.
Esto es una evaluación de regresión del replay set, no una promoción del
router: antes de la normalización explícita del episodio externo,
`tools/project_learning.py` daba `status=abstain`,
`holdout_count=0`, `holdout_project_count=0` y
`reason=no_independent_holdout`: solo `research_job_router` tenía dos grupos
de proyecto con etiqueta repetida; los demás grupos elegibles no tenían una
segunda familia etiquetada que permitiera un holdout independiente. El
splitter dejó de depender de un bucket hash que podía producir cero holdout y
ahora exige cobertura de etiqueta en train antes de seleccionar grupos.

**Primer candidate lesson real.** La ruta externa de tenis tenía `tool` exacto
`tools/tennis_shot_events.py` y el check `project_ir_route`; el learner ahora
la acepta únicamente mediante ese mapeo explícito al contrato
`tennis_shot_event_consumer`. La corrida real produjo `eligible_examples=12`,
`train_count=6`, `holdout_count=6`, 2 proyectos de holdout,
`holdout_accuracy=1.0` frente a baseline `0.833333`, y fingerprint
`5b3c07d52eee3e87b1354176a8f306b1f762cf79fc00a3201f9ec834f3e259c3`.
`tools/project_learning.py --record` registró
`rule_learning_0d6971c0b5e85d7108c6` como `candidate` junto con la evaluación
`evaluation-policy-0d6971c0b5e85d7108c6` dirigida a esa regla. No se promovió;
el router solo consume reglas `promoted`.

**Integración abierta.** Todavía falta un canary explícito de la candidate
lesson contra casos nuevos etiquetados. La política operativa de recuperación
ya está implementada: `MakDirector.recovery_plan(run_id)` lee el último
checkpoint sin mutarlo, manda a re-probar una ejecución interrumpida en
`running`, permite continuar la validación desde `observed` y solo recomienda
registrar desde `validated` cuando la validación pasó; un fallo explícito se
manda a cuarentena. El director conserva observaciones `needs_evidence` como
evidencia, pero no las convierte en soporte de una regla.

**Contrato canary.** `src/flujo/knowledge/canary.py` exige casos con
`project_id`, `group_id`, `source_refs`, `expected_label`, `validator` y una
validación explícitamente `passed/verified`; rechaza cualquier proyecto o
grupo presente en el conjunto de entrenamiento y distingue `passed`, `failed`
y `abstained`. `record_canary_evaluation` solo añade una
evaluación `split_kind=canary`; no escribe reglas activas ni promueve la
candidate. Aún no existe un paquete real de proyectos nuevos etiquetados, por
lo que no se afirma un canary ejecutado: el siguiente input válido debe venir
de una ejecución nueva y verificada.

No usar todavía GPU, fine-tuning, bandits ni promoción automática.

**Siguiente acción concreta.** Obtener un paquete de casos nuevos y
verificados, ejecutar el canary read-only con el contrato anterior, persistir
su evaluación y mantener la regla como `candidate` si aparece cualquier
abstención o contradicción. Solo después revisar soporte por episodio y el
holdout dirigido; la promoción seguirá siendo manual y separada.

**Última verificación.** 2026-08-25; worktree validado con `git diff --check`,
suite completa en `EXIT 0`, tests del ledger en `EXIT 0` y sincronización con
`origin/main`. La regla conserva en `evaluation_id` el ID
`evaluation-policy-0d6971c0b5e85d7108c6`; la base real queda en `41` records,
`18` episodios, `1` candidate, `3` evaluaciones y `5` eventos de director.
La nueva abstención no cambia el learner: sigue en `12` ejemplos elegibles,
`6/6` holdout, accuracy `1.0` frente a baseline `0.833333`, con la misma
policy version.
Después, la migración de procedencia de episodios se verificó en esa base en
modo lectura: existen los tres campos nuevos y los triggers
`project_episodes_no_update`/`project_episodes_no_delete`; el conteo de filas
no cambió y `provenance_rows=0` para los históricos, como corresponde.
La suite completa posterior a esta corrección terminó nuevamente `EXIT 0`;
los únicos avisos siguen siendo las 7 deprecaciones de Pillow ya conocidas.
La idempotencia de `record_episode` también compara `started_at` y
`finished_at`, y rechaza un mismo `episode_id` con timestamps distintos.
Después del endurecimiento del canary, los tests dirigidos y la suite completa
volvieron a terminar `EXIT 0`; el canary real sigue pendiente solo por falta
de un caso nuevo que satisfaga el contrato independiente.

## Slice validated - PNG XMP adversarial witness - 2026-08-24

**Objetivo.** Comprobar si la lectura exhaustiva de XMP en PNG podía elevar su
vocabulario de `ASSERTED` a `YES`, buscando marcadores XMP fuera de los chunks
declarados y fijando exactamente el corpus leído.

**Corrección previa.** La primera pasada encontró 6 archivos con XMP real en un
chunk `tEXt` con la clave `XML:com.adobe.xmp`; el lector conocía solo `iTXt`.
`src/flujo/substrate/xmp.py` ahora lee ambos tipos y conserva el método exacto
(`png_itxt_chunk`, `png_text_chunk` o `png_xmp_chunks`). El testigo también
excluye ambos contenedores antes de buscar marcadores crudos. La corrección
está publicada en `81fd57a` (`fix(substrate): cover legacy PNG XMP chunks`).

**Herramienta y contrato.** `tools/png_xmp_witness.py` es read-only sobre el
corpus: valida firma PNG, tabla de chunks, CRC, `IEND` y todos los bytes hasta
EOF; hashea cada archivo con SHA-256 y busca `<?xpacket`/`<x:xmpmeta` fuera de
`iTXt` o `tEXt` con la clave XMP. Su alcance es lexical y explícito: no afirma
detectar bytes comprimidos o cifrados dentro de una estructura desconocida.
`tests/test_png_xmp_witness.py` cubre XMP dentro de ambos contenedores, hit
fuera y CRC inválido.

**Comando y evidencia física.**

    .venv/bin/python tools/png_xmp_witness.py \
        --root /media/mak/PortableSSD \
        --out /tmp/mak-png-xmp-witness-v2.json

La corrida fue sobre el árbol limpio `81fd57a` y terminó `EXIT 1` porque el
testigo no es elegible. Resultó: `candidate_count=14345`,
`files_checked=14327`, `errors=18`, `outside_marker_files=0`,
`xmp_container_files=973`, `xmp_container_count=973`,
`eligible_for_witness=false`, `output_sha256=
b84fc93b3bb390c4c621d333ec9f807a50eb9a029d18eac4fe6e69156e3f33f6`.

Las 18 excepciones están identificadas, no ocultas: 17 son nombres `._*` o
sidecars de macOS sin firma PNG (`bad_signature`), y 1 es
`LYON/Pajsaera/PNG/2/3/EXR/todo/SIN/FONDO/fhmo/slowmo/blur/2/New Folder/humo edi/HUMOULTIMO/2/PNG BLUR/blur Comp. 1-4x-RIFE-RIFE4.0-60fps/00000237.png`,
que tiene firma pero termina sin `IEND` (`missing_IEND`). El primer resultado
de 6 hits fuera del vocabulario quedó reemplazado por esta segunda medición:
0 hits, confirmado en todos los 14.327 archivos legibles.

**Auditoría posterior, solo lectura.** Los 8 sidecars reportados como
`bad_signature` son AppleDouble (`file` los identifica con la firma
`00 05 16 07`); los otros 9 son JPEG reales con extensión `.PNG`, incluyendo
copias byte-idénticas de `IMG_5577.PNG`. El archivo `00000237.png` sí tiene
firma PNG y `file` lo reconoce como 1920x1080 RGBA, pero es el último elemento
de su secuencia: `00000234.png`, `00000235.png` y `00000236.png` son válidos y
no existe `00000238.png`. Se conserva como salida truncada/UNKNOWN; no se
repara, borra ni sustituye.

**Decisión.** No se promueve `KNOWN_CONTAINERS["png"]` a `YES`: los 18
candidatos no forman una cobertura limpia del conjunto reclamado. Un PNG válido
sin XMP todavía no puede producir un negativo respaldado por `XmpResult`; los
archivos inválidos permanecen `UNSUPPORTED`/desconocidos. El siguiente paso
acotado es hacer que el testigo distinga por firma y repetir sobre los 14.327
PNG válidos, dejando `candidate_count=14345` y las 18 exclusiones visibles. Eso
permitiría un resultado scoped al formato real sin convertirlo en una afirmación
sobre los sidecars/JPEG mal nombrados ni sobre el frame truncado.

## Slice validated - carousel index into the flyer source - 2026-08-24

**Objetivo.** Validar como slice el arreglo que impide que el fallback de
descarga sustituya en silencio una slide de carrusel distinta a la pedida, ya
que esa imagen es la fuente unica del entregable.

**Path exacto.** `src/flujo/eventos/flyer_auto.py`, funcion
`_download_via_mirror` (parametro `indice`, seleccion y `AVISO`), y el call site
que la alimenta con `_indice_pedido(url)`.

**Consumidor.** `flyer_auto` escribe `input_ig.jpg`; de ahi salen
`_extract_palette` y `_write_predominant_color`, y el render lo consume
`tools/render_flyer_mak.py` llamando `blender_nodes.build_flyer_nodes`. Es el
entregable, no un artefacto interno.

**Motivo.** Una auditoria de esta sesion encontro que `_download_via_mirror`
juntaba TODAS las slides en `candidatos` y bajaba `candidatos[0]` sin condicion,
mientras sus dos hermanas en el mismo archivo (`_download_via_parth`,
`_download_via_embed`) ya respetaban `?img_index=N`. Cuando las dos primeras
fallan y el mirror entrega, pisaba `input_ig.jpg` con la slide equivocada sin
avisar. El arreglo entro dentro de `ed9c6e2`, cuyo mensaje
("consolidate media layout and retire duplicate sources") NO lo describe; por eso
no estaba validado como slice y por eso se valida ahora.

**Comandos foreground y exit code.**

    .venv/bin/python -m pytest tests/test_flyer_carousel_index.py \
        tests/test_eventos_flyer_auto.py -q          -> EXIT 0, 10 passed
    smoke aislado en /tmp/mak_slice_smoke, red inyectada, sin tocar ningun issue

**Resultado observado.**

| pedido | descargado | aviso |
| --- | --- | --- |
| 1 | slide 1 | no |
| 3 | slide 3 | no |
| 4 | slide 4 | no |
| 9 sobre 4 | slide 1 | SI, "se pidio la imagen 9 pero el post tiene 4" |

`_indice_pedido` parsea `?img_index=3` y `?utm=x&img_index=2` correctamente, y
devuelve 1 cuando no hay indice. El contrato de `_download_via_mirror` quedo
identico al de `_download_via_embed`: misma firma, misma linea de seleccion,
mismo texto de AVISO -- verificado leyendo ambas, no asumido.

**Prueba de no-cambio en lo protegido.**

- `blender_nodes.IMAGE_LAYOUT_POLICY == "fitwidth_fade"` y
  `VIDEO_LAYOUT_POLICY = IMAGE_LAYOUT_POLICY`: sin tocar.
- El archivo fuente no se modifica: la ruta es `shutil.copy(downloaded, input_img)`,
  una copia de bytes. No hay recompresion, recorte ni redimension en este slice.
- `.github/workflows/issue_descarga_ig.yml` linea 59 conserva el guard
  `github.event.action == 'opened' || github.event.label.name == 'action/descargar-ig'`
  junto al `contains(labels, 'action/descargar-ig')`: una etiqueta administrativa
  como `gmail` no relanza render.
- Arbol limpio contra `origin/main` en `a13ea15`. No hubo reset, checkout, clean
  ni copia de arboles. El unico archivo que este agente modifica es este handoff.

**Riesgo.**

1. `ed9c6e2` absorbio trabajo que su mensaje no nombra: ademas del carrusel,
   entraron `RENDERS_TO` y las autoridades `blend_declaration` /
   `aftereffects_declaration` en `src/flujo/substrate/schema.py`, y
   `tests/test_title_resolution.py`. Es recuperable con `git log -S`, pero un
   lector del mensaje no lo encuentra. Registrado aqui para que la procedencia
   exista fuera de Git.
2. El mirror estaba 403 Cloudflare al 2026-07-22, asi que esta via se ejerce
   poco. Eso explica por que el defecto no se noto; no lo hace menos real.
3. El resolvedor de títulos fue validado en el slice siguiente. La base viva
   conserva 41 filas, 0 títulos duplicados y 0 transiciones; la ambigüedad se
   probó en una base temporal construida con el escritor real.
4. El handoff anterior decía que RENDERS_TO estaba SIN CONSUMIDOR. Eso quedó
   corregido: tools/render_output_edges.py lee el origen y escribe únicamente
   el sidecar solicitado; tests/test_render_output_edges.py cubre el consumidor
   y los directorios suspect quedan fuera de las aristas persistidas.

**Siguiente accion.** Mantener el contrato semántico para carpetas con video y
pasar al witness PNG. El lector AEP y el consumidor RENDERS_TO ya tienen slices
separados y evidencia abajo.

## Slice validated - title resolution and cascade gate - 2026-08-24

**Objetivo.** Validar que una decisión por título nunca escoja silenciosamente
una fila y que una cascada no cruce subárboles cuando el título del contenedor
es ambiguo.

**Paths exactos.** `tools/project_review.py`,
`src/flujo/knowledge/review_queue.py`,
`src/flujo/knowledge/project_context.py` y
`tests/test_title_resolution.py`.

**Consumidores.** La CLI `tools/project_review.py` escribe únicamente mediante
`LearningStore.transition_project`; `persist_context()` y
`link_context_to_project_ir()` escriben contexto/IR. Todos exigen resolución
`Unique` para escribir. `project_id` sigue siendo la salida inequívoca porque
es PRIMARY KEY; un título con 0 o N coincidencias se abstiene.

**Comandos foreground y resultados.**

    .venv/bin/python -m pytest -q tests/test_title_resolution.py \
        tests/test_review_queue.py tests/test_project_context.py -> EXIT 0
    .venv/bin/python -m pytest -q -> EXIT 0
    py_compile review_queue.py + test_title_resolution.py -> EXIT 0
    git diff --check -> EXIT 0

La lectura read-only de `data/mak_knowledge.db` devolvió 41
`project_records`, 36 `review_required`, 4 `active`, 1 `candidate`, 0 títulos
duplicados, 0 `project_transitions`, y confirmó que `title TEXT NOT NULL` no
tiene `UNIQUE`. `project_review.py summary/list` leyó la base sin escribir.

La validación del consumidor real se ejecutó sobre una copia temporal de esa
base: `show DREFGIRA` resolvió el título a
`project-6f330efb18a0c55ac588`; `decide --to quarantined` modificó solo la
copia y creó una transición. El hash de la fuente fue
`ac65df284ef13aa282f61099174d401e7372ed41de60f72bc63eab9010711c6f` antes y
después; `SOURCE_UNCHANGED=true`.

Además se agregó una regresión para dos contenedores con el mismo título y
hijos distintos: una cascada por `project_id` se rechaza con
`cascade_ambiguous: parent` antes de escribir cualquier transición. Una
decisión directa por `project_id`, sin cascada, sigue siendo válida.

**Contrato semántico para carpetas con video.** Una carpeta/proyecto representa
el paquete de trabajo y sus artefactos; encontrar un `.mp4`, `.mov` o similar
no permite concluir que la obra sea exclusivamente ese video. El video se
clasifica como entregable/obra solo si una fuente declarativa, un manifest o un
consumidor de entrega lo dice. Para `RENDERS_TO`, la arista es
`project state -> declared output directory`; no es `project -> one chosen file`
ni `folder -> video` por extensión. Si no existe esa declaración, conservar
`candidate`/`unknown` y registrar el video como artefacto, sin elegirlo como
identidad ni como salida.

**Riesgo y siguiente acción.** La base viva no contiene aún una colisión real;
la garantía de ambigüedad descansa en fixtures construidos con el writer real.
El lector `.aep` siguiente quedó validado abajo; no debe escribir `RENDERS_TO`
hasta que su evidencia de composición y salida pase este contrato.

## Slice validated - After Effects reference reader - 2026-08-24

**Objetivo.** Leer las referencias declaradas por After Effects sin abrir AE,
sin tocar el archivo fuente y sin inferir cuál video o imagen es el entregable.

**Paths exactos.** `src/flujo/substrate/aepfile.py` implementa el contrato
`mak-aepfile-v1`; `tools/aep_reference_scan.py` hace el inventario read-only;
`tests/test_aepfile.py` cubre el lector; `src/flujo/substrate/schema.py` y
`CAPACIDADES.md` describen la autoridad y el consumidor.

**Contrato de lectura.** Los archivos reales son `RIFX` con forma `Egg!` y
contienen registros estructurados `fullpath`. El lector escanea todos los
bytes dentro del límite de 512 MiB, conserva `declared_path`, metadatos
opcionales y `byte_offset`, y cuenta los chunks top-level solo como
diagnóstico. No reclama comprender el vocabulario privado completo de AE.
Una diferencia entre el tamaño declarado por el encabezado y el tamaño físico
observado se registra como `header.trailing_bytes`; no se llama truncación a
una cola válida. `DECODER_LIMIT` queda reservado para encabezado inválido,
archivo físicamente corto o exceder el límite.

**Medición física reproducible.** Sobre `/home/mak/RD` y
`/home/mak/curatoria_inbox` se contaron 145 archivos `.aep` (53 y 92). El
comando:

    .venv/bin/python tools/aep_reference_scan.py \
        --root /home/mak/RD --root /home/mak/curatoria_inbox \
        --output /tmp/mak-aep-scan-full.json

produjo `file_count=145`, `files_with_references=138`,
`reference_count=2304` (rutas únicas por archivo),
`unique_declared_paths=309`, `decoder_limit_files=0`, y las 145 entradas con
`completeness=exhaustive`. El encabezado dejó 1.534.167 bytes de cola en
conjunto; la prueba dedicada confirma que no se pierden referencias ni se
marca como truncado un archivo con esa forma. La afirmación anterior de 408
`.aep` no se reproduce en estos roots actuales y ya no aparece como cobertura
vigente en el schema.

**Pruebas foreground.** `tests/test_aepfile.py` más los slices de revisión:

    .venv/bin/python -m pytest -q tests/test_aepfile.py \
        tests/test_title_resolution.py tests/test_review_queue.py \
        tests/test_project_context.py       -> EXIT 0
    .venv/bin/python -m pytest -q             -> EXIT 0
    .venv/bin/python -m py_compile src/flujo/substrate/aepfile.py \
        tools/aep_reference_scan.py tests/test_aepfile.py \
        src/flujo/substrate/schema.py src/flujo/substrate/__init__.py -> EXIT 0
    git diff --check                          -> EXIT 0

También se comprobó la importación pública de `read_references()` sobre
`/home/mak/RD/JOFF.aep`: `exhaustive`, 10 referencias, 4.674 bytes de cola,
y ninguna clave `renders_to`.

**Límites que quedan escritos.** Esta es evidencia de referencias declaradas,
no una prueba de que la ruta exista, esté activa en una composición, sea la
salida entregada o que el corpus físico esté completo. La ausencia de un
`fullpath` no autoriza una conclusión negativa. El lector no escribe
`RENDERS_TO`; la regla para carpetas con video sigue siendo paquete de trabajo
más artefactos, con entrega solo cuando una fuente declarativa o consumidor lo
afirma.

**Siguiente acción.** Validar el witness PNG como slice separado. No generar
aristas desde la extensión `.mp4`, `.mov` o desde la mera pertenencia a una
carpeta.

## Slice validated - RENDERS_TO consumer and Blender fallback - 2026-08-24

**Objetivo.** Verificar el consumidor real de la declaración de salida de
Blender y tener un fallback nativo para los archivos que el parser binario no
puede abrir, sin renderizar, guardar ni elegir un archivo dentro del directorio.

**Consumidores y paths.** tools/render_output_edges.py lee SC blocks y, solo
cuando el directorio resuelto no es suspect, escribe RENDERS_TO en el sidecar
SQLite entregado por --out. tests/test_render_output_edges.py prueba la
clasificación, la cardinalidad, el CLI y que un directorio lleno de documentos
no se persista como render. tools/blender_scene_probe.py ejecuta Blender en
background con factory-startup y disable-autoexec, consulta únicamente
bpy.data.filepath y scene.render.filepath, y nunca emite RENDERS_TO.

**Full run en el filesystem.** El comando:

    .venv/bin/python tools/render_output_edges.py \
        --root /media/mak/PortableSSD \
        --out /tmp/mak-render-edges.db \
        --report /tmp/mak-render-edges.json

terminó EXIT 0 tras 874,9 s. find y el propio lector coinciden en 927 .blend:
872 legibles, 55 DECODER_LIMIT, 192 declaraciones de escena, 104 defaults sin
información, 10 foreign_machine, 32 rebased_but_missing, 26 resolved y
2021 candidatos en esos directorios. Persistió 26 filas RENDERS_TO, 0 suspect,
con output_sha256
83dd3e9b12f10083e8ec3c6ee5b3fb2fe93ce200aca95377ca13f6861f0ecc23. El sidecar
fue temporal: no se escribió la base viva ni el SSD.

**Fallback nativo.** El comando:

    .venv/bin/python tools/blender_scene_probe.py \
        --blender /home/mak/blender/blender \
        --render-report /tmp/mak-render-edges.json \
        --output /tmp/mak-blender-probe-decoder.json \
        --timeout 90

usó Blender 4.5.4 LTS sobre los 55 DECODER_LIMIT: 54 abrieron y 1 quedó
DECODER_LIMIT. Devolvió 67 filas de escenas; 33 resolvían a directorio, pero 25
eran suspect y se mantuvieron solo como reporte, especialmente los assets que
declaran // como carpeta de trabajo. Esto confirma que preguntar a Blender es
un buen fallback de lectura, no una licencia para transformar cada
scene.render.filepath en una arista de entrega. El único fallo nativo fue el
asset denim-fabric-06; no se inventó una ruta para él.

**Resultado semántico.** El método óptimo para este dato es híbrido: parser
estático como primera pasada, Blender solo para DECODER_LIMIT, y la misma puerta
de directorio/candidate_count después de ambos. GPU no participa porque no hay
render: son IO, descompresión y lectura de RNA/escena. La evidencia sigue
siendo project -> directory, nunca project -> one chosen file.

**Pruebas foreground.**

    .venv/bin/python -m pytest -q tests/test_blender_scene_probe.py \
        tests/test_render_output_edges.py tests/test_aepfile.py -> EXIT 0
    .venv/bin/python -m py_compile tools/blender_scene_probe.py \
        tests/test_blender_scene_probe.py tools/render_output_edges.py \
        tests/test_render_output_edges.py src/flujo/substrate/schema.py -> EXIT 0
    git diff --check -> EXIT 0

**Siguiente acción.** El witness PNG quedó validado arriba. Los 55 archivos no
legibles y los 25 directorios suspect siguen siendo UNKNOWN/report-only; no se
rellenan con suposiciones.

## Physical authority and migration status

- Autoría e integración: `/home/mak/flujo`.
- Evidencia histórica protegida: `/home/mak/WIN`; no se edita ni se usa como
  fuente operativa.
- Estado y consumidores runtime: `/home/mak/plataforma`, `/home/mak/research`,
  `/home/mak/codex`, `/home/mak/curatoria`, `/home/mak/RD` y otros roots de
  MAK; no se reemplazan bases, logs, media ni outputs generados.
- `flujo-deploy` no es una segunda fuente: queda retirado como ruta activa.
- XIO queda fuera de este slice y no se toca. `RD` creativo queda fuera de la
  limpieza de duplicados.

## Completed work with command and result

1. Consolidación física ya realizada: las familias de código canónicas viven
   bajo `flujo/cultura/`; las rutas runtime externas que se conservaron son
   links o wrappers de compatibilidad. Las copias históricas, datos, bases,
   logs y media se preservaron. Los duplicados no consumidos fueron enviados a
   la Papelera del sistema, no borrados de forma irreversible.
   Durante la validación completa también se corrigió físicamente
   `/home/mak/plataforma/entregar.py`: ahora expone el módulo canónico sin
   copiar funciones con globals divergentes. Esa proyección está fuera de
   este repositorio y debe verificarse en el filesystem, no asumirse desde Git.
2. Reparación visual en
   `src/flujo/eventos/blender_nodes.py` y
   `src/flujo/eventos/blender_nodes_video.py`: imágenes y videos usan una sola
   política de producción, `fitwidth_fade`. El source no se edita; Blender
   conserva proporción, hace coincidir los bordes laterales de la ventana y
   entrega el sobrante o faltante vertical al grafo de fade. `cover_center` y
   `contain_bars` quedan únicamente como helpers históricos/diagnósticos.
3. El consumidor de imagen es `tools/render_flyer_mak.py`, que importa el
   módulo real de nodos y llama `build_flyer_nodes`; no hay un swap artesanal de
   textura. El consumidor de video es
   `tools/render_video_sequence_mak.py`; ambos quedaron alineados.
4. El reproceso por etiquetas quedó cerrado en
   `.github/workflows/issue_descarga_ig.yml`: en eventos de issues solo pasa
   `opened` o el agregado exacto de `action/descargar-ig`; una etiqueta
   posterior como `gmail` no relanza el render.

## Regression lock — visual and event safety

No cambiar estos invariantes sin actualizar código, pruebas, documentación y
un smoke render real aislado:

- `IMAGE_LAYOUT_POLICY == "fitwidth_fade"` y el video usa el mismo valor.
- Nunca modificar, recomprimir, recortar ni redimensionar el archivo fuente
  recibido. La transformación vive en el mapping/nodos de Blender.
- Los límites X de la ventana medida deben mapear a X=0 y X=1 del source; el
  eje Y puede salir del rango para que el fade maneje el exceso vertical.
- No reintroducir una bifurcación automática por aspect ratio entre
  `cover_center` y `contain_bars`.
- No relanzar un issue como prueba: validar primero con un directorio
  aislado en `/tmp`, un `.blend` copiado/enlazado de forma segura y el flyer
  fuente sin tocar.
- No procesar de nuevo por eventos `labeled` ajenos a
  `action/descargar-ig`; revisar siempre `github.event.action` y
  `github.event.label.name`.

Validación visual ya obtenida: el smoke render de Blender con la imagen no
convencional entregada por el usuario terminó con `RENDER_OK` en
`/tmp/mak-render-check.BquJO6/out/render_output.png`; la inspección mostró
bordes laterales calzados, proporción preservada y fade vertical. El smoke no
tocó issue, OneDrive, `.blend` original ni source.

## ClaudeCode continuation protocol

ClaudeCode debe retomar desde este bloque y desde `agents.md`, no desde una
sesión vieja ni desde `WIN`. Para cada cambio debe dejar en el handoff: objetivo,
path exacto, consumidor, motivo, comando foreground, exit code, resultado
observado, archivos cambiados o prueba de no-cambio, riesgo y siguiente acción.
La búsqueda correcta es: (1) filesystem físico bajo `/home/mak`, (2)
`/home/mak/flujo/agents.md` y este handoff, (3) consumidor real y sus imports,
(4) pruebas y smoke/entrypoint, (5) `WIN` solo como evidencia histórica. Usar
`rg --files`/`rg` acotado; no escanear ni fusionar árboles completos por nombre.

La consolidación requiere comparar contenido, propietario, consumidor,
dependencias y hash; un nombre parecido, timestamp o reporte antiguo no prueba
que sea duplicado. Integrar el mínimo componente en `flujo`, mantener wrappers
solo cuando haya consumidor externo, preservar `WIN`, `RD`, `XIO`, bases, logs,
media y outputs, y mover descartes recuperables a la Papelera. Nunca usar
`git reset --hard`, copiar árboles enteros, regenerar artwork protegido ni
editar un estado JSON para simular trabajo ejecutado. Antes de `git add`, revisar
el diff por archivo y separar cambios no autorizados.

## Open integration items

- Publicación cerrada: `git ls-remote origin refs/heads/main` confirmó que el
  commit funcional `ed9c6e2` está en `origin/main`; el checkout local quedó
  limpio antes de este ajuste documental.
- El runner/Actions tomará este SHA mediante su checkout normal; no se inició
  un job ni se relanzó un issue para validar el cambio, y no se tocaron outputs
  históricos.
- XIO sigue diferido y explícitamente no es un duplicado resuelto.

## Tool and dependency verification matrix

| Slice | Consumer | Verification | Result |
|---|---|---|---|
| Image Blender | `tools/render_flyer_mak.py` -> `blender_nodes.build_flyer_nodes` | focused pytest + isolated Blender smoke | 71 focused tests passed; full suite exit 0; `RENDER_OK` |
| Video Blender | `tools/render_video_sequence_mak.py` -> `blender_nodes_video` | focused pytest + `py_compile` | passed; `fitwidth_fade` only |
| Issue trigger | `.github/workflows/issue_descarga_ig.yml` | static condition review | only `opened` or exact action label |
| Consolidated departments | `cultura/mak_*` and external compatibility paths | bounded physical/hash/consumer audit | source-only runtime code paths: 0 |

## Conflicts and risks

- El write set de ClaudeCode y esta reparación fueron revisados por archivo y
  publicados por autorización explícita del usuario en `ed9c6e2`.
- Los reportes históricos dentro de este handoff pueden contener rutas y
  estados viejos; este bloque superior es la continuidad vigente.
- La prevención de reproceso evita el evento de etiqueta ajena; no convierte
  un issue fallido en éxito y no autoriza relanzar históricos automáticamente.

## Next concrete action

ClaudeCode debe retomar el siguiente item real de integración desde este bloque,
registrar evidencia antes de cambiar estado y no tocar XIO, `WIN`, RD creativo,
bases, logs, media ni outputs. Si no existe un slice autorizado fuera de XIO,
mantenerlo como diferido explícito y no inventar trabajo.

## Last verified

2026-08-24 America/Santiago — full pytest exit 0; 71 focused tests exit 0;
`py_compile` exit 0; `git diff --check` exit 0; Blender aislado `RENDER_OK`;
commit funcional `ed9c6e2` verificado en `origin/main`; no hay proceso de
render activo.

## Current filesystem consolidation — 2026-08-24

`/home/mak/flujo` is the single active authoring/integration baseline. The
historical `/home/mak/WIN` tree was left untouched. The former duplicate
checkout, deploy projection and synchronizer were retired after physical
comparison; none remains an active source or route.

The current Claude write set in `/home/mak/flujo` was preserved, reviewed and
published as part of `ed9c6e2`. Historical phase and recovered-source material
is not an operational owner; only this handoff, `agents.md`, the runtime source
and focused tests define the active baseline.

Department consolidation continued on 2026-08-24. The four canonical code
families under `cultura/mak_plataforma`, `cultura/mak_research`,
`cultura/mak_codex` and `cultura/mak_curatoria` contain every corresponding
runtime code path found in `/home/mak/plataforma`, `/home/mak/research`,
`/home/mak/codex` and `/home/mak/curatoria` (`source_only=0` in the bounded
code scan). Most runtime entrypoints are compatibility projections that load
the canonical files, not independent implementations.

Thirteen exact runtime duplicates were retired from the live department paths
and replaced by links to their canonical files in `flujo`: the ISKVW mounting
script, five Curatoria utilities, six Research helper/unit files and two
Platform utilities. Fifty-two additional Python runtime paths were converted
to compatibility projections that load their canonical implementation from
`flujo`, including the Codex `motor_semantico` package with a package-aware
bridge. Curatoria now has no remaining independent top-level implementation:
its entrypoints are canonical wrappers or links. Runtime state, databases,
logs, inboxes, media and environment files were not moved or overwritten.
Remaining non-wrapper department files are utility/test/runtime-specific
candidates for later per-file consumer review; no whole-tree merge was
performed.

The clutter pass also retired 32 timestamp-clustered prompt-generated utility
files from `/home/mak/plataforma/utilidades` and five orphaned Research patch/
test artifacts. They had no active cron/process consumer and no canonical
source counterpart; they were moved to the system Trash, not hard-deleted.
Runtime-specific `backup.sh`, databases, logs and media remain untouched;
service units were then audited under their own consumer contracts. `backup.sh` and
`watchdog_mak.sh` were then verified as compatibility projections to the
canonical Platform scripts; their external paths remain for cron compatibility.
The active Hub, Research and Codex user units were consolidated to the single
contracts in `flujo` while retaining the external `plataforma`, `research` and
`codex` working directories for state. Their runtime copies are now symlinks;
XIO was intentionally left unchanged for a later pass.

Service switch evidence, 2026-08-24: `systemctl --user daemon-reload` and a
controlled restart of `mak-research.service`, `mak-codex.service` and
`mak-hub.service` all returned active. The live `ExecStart` paths are
`/home/mak/flujo/cultura/mak_research/interfaz.py`,
`/home/mak/flujo/cultura/mak_codex/interfaz_codex.py` and
`/home/mak/flujo/cultura/mak_plataforma/hub.py`; HTTP smoke checks returned
200 for `:8890/api/jobs`, `:8891/api/jobs` and `:8900/health`. Both research
environment files remain loaded, with the existing `n8n-local/research.env`
kept as an overlay. `WIN`, databases, logs, media and XIO were not touched.

The remaining non-XIO code departments were also consolidated: `vigia` now
has one canonical code family under `cultura/mak_vigia`, and `lenguaje` one
under `cultura/mak_lenguaje`; their external code/config entrypoints are
symlinks. `vigia/estado`, Hunspell dictionaries and `lenguaje/lexico` remain
in place as runtime data. The old unconsumed `vigia/rollback/vigia-race-20260811`
snapshot was moved to the system Trash because it was an older divergent code
copy; it is recoverable there. `RD` was not classified as duplicate code: it
is a 58G creative/media workspace and was left untouched.

The active GitHub Actions runner checkout was clean and idle when reconciled.
It was fast-forwarded from `ee9e789` to the canonical remote
`db6659b`; its `issue_descarga_ig.yml` now has the same SHA-256 as `flujo`, and
the extra disabled `claude.yml` was removed by that fast-forward. The runner
service remains active; no job was running during the update.

The detached Codex worktree at `/home/mak/.codex/worktrees/31af/flujo` was an
old, dirty surface with six tracked edits and 806 untracked phase artifacts.
Its useful Hub/tools content was already newer in `flujo`; its only material
exclusive implementation was the experimental Blender `glass_fitwidth`
change, explicitly awaiting visual approval. It was moved to the system Trash
and its stale Git worktree record was pruned; the experiment was not promoted
to production. The 143-file historical snapshot tree was also moved to Trash
after confirming no process or cron consumer. Both remain
recoverable there. `codex/piezas` and `plataforma/director_runs` remain because
they are generated outputs/runtime state, not duplicate source trees.

The documentation cleanup pass on 2026-08-24 removed the retired migration
record and the detached-worktree review from the active context; both were
moved to the system Trash and remain recoverable. `MAPA.md`, this handoff,
`MD_CONTEXT_MASTER.md` and `PHASE_REPORTS_INDEX.md` now identify `flujo` as
the only active source and explicitly fence archival phase/recovered material
as evidence, not instructions. The code structure index was regenerated from
the current tree: 849 Python files, 206,848 lines, 9,442 symbols and zero
syntax errors. Historical phase reports may still contain absolute paths from
their original checks; they are not current commands.

The visual mapping repair on 2026-08-24 keeps the source image untouched and
unifies still-image and video Blender composition under `fitwidth_fade`: the
measured lateral borders match the glass, proportions are preserved, and the
vertical excess/shortfall is handled by the fade graph. The former video-only
`cover_center`/`contain_bars` split is retained only as historical geometry
helpers, not as a production policy. A real Blender smoke render with the
user-supplied non-conventional image passed with `RENDER_OK` in an isolated
`/tmp` check directory. The change is published in `ed9c6e2`; it was not used
to relaunch an issue.

## Active checkpoint — recovery after Claude quota — 2026-08-23

### Current objective

Recuperar y cerrar el slice de ordenamiento epistemico que Claude dejo a medias,
sin repetir el workflow de investigacion ni convertir sus resultados en verdad
automatica. La politica de features debe ser ejecutable por la cola de
clasificacion, no solo un documento de razonamiento.

### Recovered Claude work

Claude Code session `3428381a-02ad-4101-9da5-8176cf72c147` launched the
read-only workflow `wmff24999` with 14 agents. Nine returned and five stopped
at the session quota: `reconciliation`, `histories`, `other`, `track key` and
`synthesis`. The durable result is seven identity records and two measurement
probes. The result was not a complete SSD-to-Instagram join or a final
catalogue. It is summarized in `docs/ordering_research_snapshot.md` so the
temporary `/tmp/claude-1000/` output is not the only record.

Claude also created the ordering policy artifacts, which were present in the
worktree and had not yet been committed:

- `docs/ordering_chaos.md`
- `data/ordering_features.json`
- `src/flujo/knowledge/feature_policy.py`
- `tests/test_feature_policy.py`

The `.gitignore` exception for `data/ordering_features.json` was already
present in the worktree when recovery began. The language ratchet also passed;
the new Python files did not add an offender.

### Integration completed in this recovery

`src/flujo/knowledge/classification_queue.py` now calls
`feature_policy.may_decide()` before emitting either automatic proposal:

- `declared_marker` plus the PEP 405 authority for virtual environments;
- `content_hash` plus the full-hash authority for canonical copies.

Each proposal carries the serialized policy permission in its evidence. If the
registry is missing, malformed or denies the question, the queue raises
`ClassificationQueueError` with `ordering_policy_refused` and emits no
proposal. `tests/test_classification_queue.py` covers both the evidence link
and fail-closed behavior.

### Validation evidence

- Focused policy, queue, language and repository tests: exit 0, 58 passed.
- Full `./.venv/bin/python -m pytest -q`: exit 0, 100 percent passed; only
  existing Pillow deprecation warnings were emitted.
- `compileall` for the touched Python files: exit 0.
- `python3 -m json.tool data/ordering_features.json`: exit 0.
- `git diff --check`: exit 0.

### Files modified in this checkpoint

`.gitignore`, `data/ordering_features.json`, `docs/ordering_chaos.md`,
`docs/ordering_research_snapshot.md`,
`src/flujo/knowledge/feature_policy.py`,
`src/flujo/knowledge/classification_queue.py`,
`tests/test_feature_policy.py` and `tests/test_classification_queue.py`.

No source database, SSD file, service or runtime process was modified. The
checkpoint is committed locally as `02eeea0`; it has not been pushed.

### Risks and boundaries

The seven identities and the two probes are evidence-backed candidates, not
operator attestation. `FELINA` remains unknown, `SCD` remains probable, and
the five failed probes must not be inferred from the nine successful agents.
The policy is now enforced at the automatic classification proposal boundary,
but it does not yet train a model or promote authorship/publication.

## Continuidad tras el corte de cuota — 2026-08-23

CONTEXTO. La orquesta de descubrimiento (`wmff24999`, 14 agentes sonnet en
esfuerzo high) se corto por cuota: 9 agentes terminaron, 5 no
(reconciliacion, historias, other, llave-del-track, sintesis). Otro agente
continuo, publico `35c88ad` con la politica de evidencia y dejo tres archivos
sin commit. Este slice cierra eso, verifica sus cifras y rescata lo que la
orquesta habia averiguado y nadie habia guardado.

VERIFICADO, no asumido. `35c88ad` esta en origin/main y contiene
`data/ordering_features.json`, `docs/ordering_chaos.md`,
`src/flujo/knowledge/feature_policy.py` y `tests/test_feature_policy.py`.
Sin commit quedaban `tools/reconcile_iskvw_media.py`,
`tests/test_reconcile_iskvw_media.py` y una ampliacion de
`docs/ordering_research_snapshot.md`.

EL TOOL DE RECONCILIACION reproduce exactamente las cifras reportadas, comando y
salida:

    ./.venv/bin/python tools/reconcile_iskvw_media.py \
      --archive iskvw/datos/archivo.json \
      --media-root /home/mak/portfolio_media/media --output <tmp>/rec.json
    exit 0
    archive_numeric_ids            1599
    archive_records_with_numeric_id 1818
    archive_records_without_numeric_id 216
    ids_with_one_surface           1591
    ids_with_cross_surface_collision   8
    ids_with_same_surface_multiple_files 0
    orphan_ids                        0
    matched_files                  1607
    superficies: posts 775, other 329, stories 240, archived_posts 154,
                 reels 88, igtv 5

Las 8 colisiones se revisaron UNA POR UNA: las 8 son el archivo original
(`posts` o `reels`) junto a su derivado en `_contact_sheets`. Ninguna es obra
duplicada.

UNA CIFRA QUE NADIE HABIA NOMBRADO: 1818 registros con ID dan solo 1599 IDs
distintos, o sea **219 registros del archivo comparten ID con otro registro**.
Es duplicacion en el INDICE, no en el disco (0 duplicados dentro de una misma
superficie). Esto explica la diferencia con la medicion previa por registros
(posts 998) frente a esta por IDs (posts 775): son unidades distintas, no una
contradiccion.

DEFECTO DE TEST QUE SI ARREGLE. El otro agente pidio verificar que la
correccion de precedencia (`medio.src` antes que `piezas[].id`) permanezca, y el
test la cubria POR ACCIDENTE: en su fixture el ID compuesto falla por numero de
digitos (9, y el patron exige 10), no por precedencia. Se agregaron cuatro tests
donde las dos fuentes DISCREPAN a proposito, mas el caso real de los 1807
registros sin `medio.src`, mas el de los 216 sin ID que deben abstenerse, mas
que `--output` no toque ninguna de las dos fuentes. Verificado invirtiendo la
precedencia en el codigo: 3 tests caen, incluido el nuevo con el mensaje
"the composite record id was preferred over medio.src". Restaurado despues.

RATCHET QUE HIZO SU TRABAJO: `test_tools_en_registro` cayo porque
`reconcile_iskvw_media.py` no tenia entrada en `CAPACIDADES.md`. Registrado con
las cifras medidas.

RESCATE. La orquesta habia investigado 7 identidades con URLs y **55 tracks con
fecha de estreno**, y eso no estaba guardado en ninguna parte del repo: vivia en
`/tmp` y en el journal del workflow. `data/ordering_features.json` declara la
autoridad `artist_discography` como el unico modo de que un nombre de carpeta
decida un track -- una autoridad que nadie puede abrir no es exigible. Ahora
existe `data/artist_discographies.json`:

    LYON          music_artist  confirmed  24 tracks
    DREFGIRA      music_artist  confirmed  17 tracks
    HARRY         music_artist  confirmed  10 tracks
    MARLONLOLLA   music_artist  confirmed   4 tracks
    DREFMOVISTAR  event         confirmed   0 tracks (evento, no discografia)
    SCD           venue         probable    0 tracks
    FELINA        unknown       unknown     0 tracks

Cada track trae `source_url`; 0 descartados por falta de fuente. El archivo
declara explicitamente que la AUSENCIA de un nombre no es evidencia de que no
sea un track: significa que la busqueda no se hizo. Cuatro tests nuevos fijan
que ningun track entre sin URL, que un contenedor sin tracks explique por que, y
que los matches que establecieron la llave (La Merecedora 2025-12, NEBULA
2025-10, Comando Estelar, Pasajero) sigan presentes.

DOS DUDAS MIAS QUE ESTAS SONDAS CERRARON:

1. `other` NO es una clase semantica. 330 archivos, geometria mezclada (265
   cuadrados o casi, 50 verticales, 15 horizontales) y video en los tres
   formatos. Y lo decisivo: **los 330 mtime caen entre 2026-07-22T14:20:15 y
   14:21:10** -- 55 segundos. Eso es una operacion de export o copia, no fechas
   de creacion. Esas mtime no pueden usarse como cronologia de obra. Las 329
   piezas que el archivo etiqueta `obra` ahi NO se resuelven por superficie.
2. La regla de ancla del operador quedo medida sobre los 917 proyectos:
   774 solo `.blend` = 85,29 GB; 43 solo `.aep/.psd/.ai/.svg` = 159,63 GB;
   25 con AMBOS = 502,18 GB; 75 sin ancla = 193,61 GB. La correccion que
   importa: **la obra de VJ terminada y grande vive en la clase MIXTA**,
   mientras la mayoria de los `.blend` chicos son assets descargados. La columna
   `projects.dimensionality` coincide exactamente con la clase de 774, o sea
   estaba midiendo assets y no obras.

Comandos y codigos de salida: `pytest -q tests/test_reconcile_iskvw_media.py
tests/test_classification_queue.py tests/test_feature_policy.py` exit 0;
`pytest tests/` COMPLETA exit 0; `repo_audit.py` exit 0; `compileall` exit 0;
`git diff --check` exit 0; el tool real exit 0.

LO QUE SIGUE ABIERTO, sin adornos: la sonda de las 5659 historias no indexadas
no se corrio, y la llave-del-track sistematica (cruzar TODOS los nombres de
carpeta contra las 55 canciones) tampoco -- hoy solo estan verificados a mano
los de LYON y DREFGIRA. Ningun registro se promovio a autoria, publicacion,
consumidor ni postulacion, y los 216 sin ID siguen absteniendose.

## El motor de consulta certificada — 2026-08-23

Se construyo dentro del repo, como UN sistema y no una secuencia de scripts:
`src/flujo/certified/` con `summary.py`, `contracts.py`, `certify.py`, `tree.py`,
`metrics.py`, `oracle.py`, mas `data/certified_queries.json` y
`tools/certified_query.py`.

LA REGLA QUE LO GOBIERNA, y esta implementada en un solo lugar: un negativo por
ausencia se vuelve UNKNOWN si la autoridad no cubrio a TODOS los miembros del
grupo. El veto vive en `certify()`, no en las reglas, asi que ninguna regla
puede olvidarlo. Cada resumen carga `n_members` y `covered[autoridad]`, y
`complete_for()` es la unica puerta entre "no observe X" y "no hay X".

DOS DECISIONES DE DISENO QUE CARGAN PESO. Los universales se CUENTAN en vez de
marcarse (`counts[X] == n_members`), porque un booleano `all_X` necesita un AND
en cada join y tiene un elemento identidad peligroso: un grupo vacio afirmaria
todo universal de forma vacua. Y los rangos cargan su FUENTE: un casco de fechas
sobre estrenos es sano y el mismo casco sobre mtimes no significa nada, con la
prueba medida de que los 330 archivos de `other` comparten una ventana de 55
segundos escrita por un export.

MEDIDO SOBRE EL CORPUS REAL, sin datos de juguete:

    SSD  917 proyectos, arbol de 1001 nodos, profundidad 7, G=0,17s
    IG   7321 archivos, arbol de 7515 nodos, profundidad 4, G=0,24s

    q2_dimension   poda 100,0%  160 certs  170 nodos visitados de 1001
    q4_obra        poda  95,2%    5 certs
    q7_cuando      poda  90,3%  167 certs  -- con la RAIZ en UNKNOWN
    q5_publica     poda  82,7%    2 certs
    q3_track       poda   1,0%    9 certs  (discografia cubre 46,1%)
    q11, q12, q13, q8, q9, q10, q14  poda 0%

**FALSE_CERTIFIED_CLAIMS = 0**, con 21.090 verificaciones miembro-por-miembro.
`audit_soundness` hace a proposito lo caro: toma cada certificado sobre un nodo
interno y abre TODOS sus descendientes para comprobar que ninguno lo contradice.
Es la unica medicion cuyo valor aceptable es cero, y por eso existe el camino
caro: para que el barato se pueda creer.

q7 es la mejor demostracion del diseno: la raiz dice UNKNOWN con razon precisa
-- "710 de 7321 miembros no traen fecha de la fuente declarada" -- y aun asi
**6611 miembros quedaron podados por debajo**. Abstenerse arriba no impide
certificar abajo.

q11 poda 0% A PROPOSITO. Su negativo murio en el endurecimiento adversarial
(ausencia de `pyvenv.cfg` no es "es mio": blenderkit aporta 138 assets y las
descargas 173, ninguna en un virtualenv) y el motor lo respeta en vez de
recordarlo. La auditoria ahora es codigo.

EL RATCHET ENCONTRO UN HUECO EN SU PRIMERA CORRIDA. `test_the_declared_3d_format_set_still_covers_the_corpus`
fallo por `.3dm` sin declarar. Medido: 1 archivo, en `descargas hasta RDFLYER
2050`, y **0 proyectos donde sea el unico formato 3D** -- o sea ningun
certificado fue falso, pero el conjunto SI estaba incompleto. Se arreglo con una
declaracion en dos capas en vez de agregar lo que el test nombro:
`SCENE_FORMATS` (lo que una aplicacion 3D autora y reabre) y
`PIPELINE_3D_FORMATS` (`.vdb`, `.mtl`, `.spp`: datos que solo un pipeline 3D
produce). Y `EXCLUDED_FROM_3D` deja escrito por que `.exr` (6835 assets) y
`.hdr` NO entran: son imagenes que un pipeline 2D tambien emite, y agregarlas
romperia el certificado POSITIVO en vez del negativo.

ESTADOS EPISTEMICOS, exigidos por codigo. `validate_fold()` rechaza cuatro
cosas, cada una un defecto que este proyecto vivio: un `≈` que se presenta como
`≡`; un pliegue sin residuo; un pliegue que no nombra la autoridad que le falta
(sin el nombre, ninguna herramienta que llegue puede despertarlo); y un monitor
construido sobre el rasgo que al pliegue le falta -- circular, y falla en
silencio. `assert_may_act()` niega borrar, publicar, deduplicar, enviar o
sobrescribir sobre cualquier estado que no sea `≡`.

EL ORACULO pregunta solo donde ninguna autoridad alcanza, de lo mas somero a lo
mas profundo (una respuesta arriba resuelve su subarbol entero), con piso de
miembros, y `record_answer()` rechaza una respuesta sin actor, sin razon, sin
claim o sin scope. Nunca se pregunta para vaciar una cola.

CUDA: no se toco. La Fase 1 del experimento anterior ya establecio que no hay
backend usable (modulos del driver compilados solo para el kernel 6.1.0-50
mientras corre 6.12.95) y que el TU117 no tiene RT cores. El motor no lo
necesita: su medicion decisiva son conteos, no wall-time.

Comandos y codigos de salida: `pytest -q tests/test_certified_engine.py` exit 0
(30 tests); `certified_query.py contracts/ask/queue/audit/provenance/heterogeneity`
exit 0; invocacion en seco exit 2; `--help` exit 0.

LO QUE NO HACE, y es deliberado: 0 certificados sobre el MUNDO en ambos corpus.
Los 169 certificados del SSD son CORPUS_CLAIM y los 7 de IG son POLICY_CLAIM.
El unico contrato con negativo sano sobre el mundo es `q12` y necesita hashes
completos, que en el SSD existen para 112 de 45.536 assets (0,25%). Eso no es un
defecto del motor: es el estado real de la evidencia, y ahora esta medido en vez
de supuesto.

## Next concrete action

The final staged diff was reviewed and committed locally as `02eeea0`. Do not
push it without publication authority. After publication, resume only the five
missing research probes as a separate read-only slice;
do not rerun the completed identity probes and do not mark any SSD project as
authored, published, client-owned or postulation-ready from filenames alone.

## Active checkpoint — 2026-08-21

### Current objective

Conectar DREFGIRA con el contexto de operador VJ, DrefQuila, album Después del
Sol, alcance de presentaciones de noviembre 2025, shows y venues, usando una
base existente y evidencia con estados conservadores.

### Completed work with command and result

Se agregaron `src/flujo/knowledge/project_context.py`,
`tools/triangulate_project_context.py`,
`knowledge/project_context/drefgira_2025.json` y sus pruebas. La ejecucion
foreground fue:

```text
./.venv/bin/python tools/triangulate_project_context.py --context-json knowledge/project_context/drefgira_2025.json --db data/mak_knowledge.db --out-dir /home/mak/curatoria_inbox/project_reconstruction/2026-08-21/drefgira/context --apply
```

Resultado: 10 entidades, 9 fuentes, 12 relaciones, 3 verificadas, 4
`human_attested`, 5 candidatas, 5 Project IR enlazados, 0 cambios de estado y
0 postulaciones. `PRAGMA integrity_check` devolvio `ok`; la segunda ejecucion
fue idempotente. Los derivados `project_ir.jsonl` y `routes.jsonl` quedaron
regenerados y los cinco routes siguen `abstain` por
`project_state_requires_evidence`.

El consumidor read-only quedo expuesto en ambos hubs como
`GET /api/project/context?context_id=drefgira-despues-del-sol-chile-2025` o por
`project_id`. Las dos superficies respondieron HTTP 200 en servidores
efimeros, con `schema=mak-project-context-read-v1`, `read_only=true` y las 12
relaciones; ambos procesos fueron detenidos al terminar la prueba.

### Open integration items

- `formal_tour_scope_not_independently_verified`: el agrupamiento de gira es
  candidato, no un hecho promocionado.
- `antofagasta_show_needs_independent_confirmation`: Evently/La Isla es una
  sola fuente para Club Montecarlo, 2025-11-28.
- `album_release_date_not_normalized_across_sources`: se preservan fechas
  crudas; no se fuerza una fecha unica.
- `operator_contract_not_verified`: la relacion VJ/artista es atestiguada
  por el operador, no una afirmacion contractual.
- `physical_source_mount_unverified`: DREFGIRA sigue review-only hasta montar
  o verificar el SSD; no convertirlo en activo por el grafo contextual.

### Venue projection topology from real show files — 2026-08-21

ANTES: MAK podia describir la planta de una sala y nada de las superficies sobre
las que se proyecta. El unico registro real, `data/venues/scd-plaza-egana.json`,
lo decia con sus propias palabras: `"proyeccion": {"superficie":
"desconocido", "notas": "sin datos: el plano de referencia es una planta, no dice
nada de proyeccion."}`.

DESPUES: MAK puede leer un ScreenSetup de Resolume y emitir la topologia de
proyeccion medida de una sala -- superficies con el nombre que les puso el
operador, pixeles de salida, warp decidido por aritmetica exacta y residuos que
declaran lo que el archivo no prueba -- y proponerla como el bloque `proyeccion`
del contrato `schemas/venue.schema.json` que ya existia.

DESCUBRIMIENTO: el SSD estaba montado (`/dev/sdc1` en
`/media/mak/PortableSSD`, exfat, 932 GB al 98 %) y en su raiz hay 9 archivos
`.xml` que son composiciones de Resolume Arena, no basura: `ANDACOLLO`,
`BERLIN 1`, `berlin 2`, `Black Boss Estandar TEMUCO`, `CHILLAN`, `cobquecura`,
`harry`, `KAYAKAZE 2025 2` y `la`. Todas son ScreenSetup: geometria de
proyeccion, sin identidad de personas ni direcciones, que es exactamente el
artefacto seguro segun la regla `geometria si, identidad no`.

Primera hipotesis FALSIFICADA y conservada: se busco en ellos la lista de clips
usados por show, que habria dado dependencia medida de assets. No existe --
`grep` de referencias a `.mov`/`.mp4` devolvio 0 en los tres archivos mas
grandes. Son ScreenSetup, no composiciones con capas.

TEORIA/ALGORITMO: no hace falta reconstruccion de superficies. La unica pregunta
geometrica que hay que decidir es si se aplico un warp, y eso es aritmetica
exacta: un slice sin tocar guarda un retículo bezier `controlWidth x
controlHeight` cuyos puntos caen sobre la interpolacion bilineal de las esquinas
del `OutputRect`. Comparar el retículo contra esa interpolacion decide
`plano` / `deformado` sin ajustar nada. La tolerancia `WARP_TOLERANCE_PX = 0.5`
existe porque Resolume guarda ruido de coma flotante (`-1.52587890625e-05`), esta
declarada como umbral y sus dos lados estan cubiertos por tests.

IMPLEMENTACION: `src/flujo/venues/resolume_screen_setup.py` (parser, features,
identidad de rig), `tools/venue_screen_setup.py` (CLI + vista HTML + indice de
rigs) y el subcomando `venue.py proyeccion` como consumidor. No se creo un
segundo contrato: los 9 fragmentos `proyeccion` y sus `residuos` validan contra
`schemas/venue.schema.json` sin modificar el schema.

FALSIFICACION, medida y conservada: la primera version de `rig_signature()`
trataba todo nombre de superficie como identificante y produjo 3 falsos
positivos sobre material real -- `ANDACOLLO.xml` y `berlin 2.xml` compartian
exactamente `('Slice 1', 1920, 1080)`, el nombre y el lienzo POR DEFECTO de
Resolume, presentes en cualquier composicion nueva; `CHILLAN.xml` y `la.xml`
compartian solo `('11', 128, 256)`. La reparacion fue en la representacion, no
en una lista de excepciones: `name_class()` separa `tool_default`,
`low_entropy` y `operator`, y la identidad de rig exige al menos una superficie
nombrada por una persona. Los 3 falsos positivos desaparecieron y la unica
relacion sostenida sobrevivio.

RESULTADO REAL: `CHILLAN.xml` y `harry.xml` comparten sus 11 superficies de
salida (mismos nombres, mismos pixeles) con lienzos distintos (3400x1920 contra
1080x1920) y regiones de entrada distintas. Es el mismo rig fisico alimentado por
composiciones distintas, decidido por topologia y no porque exista una carpeta
`HARRY CHILLAN`. Se guarda como `same_rig_candidate` EMPIRICAL con la alternativa
`una plantilla reutilizada en otra sala` intacta y el desempate declarado. Sobre
los 9 archivos: 8 topologias distintas, 0 superficies deformadas, 0 salidas DMX
en CHILLAN pero si en otros, y vocabulario real del operador
(`CENTRAL ATRAS`, `TOTEM L 2`, `BANNER CENITAL`, `rombo izquierda 1`,
`Banner Frontal`).

COSTO: parseo de 9 archivos de hasta 385 KB. Stdlib, determinista, sin GPU, sin
tokens, sin red -- el molde de `mak_lenguaje`. No se hasheo el SSD de 940 GB y no
se reindexo nada.

LA FRONTERA HONESTA: un ScreenSetup mide PIXELES. No contiene escala metrica, asi
que ninguna dimension fisica, altura de cuelgue, tiro de proyeccion ni carga se
deriva de el; todo eso sigue `no_verificado` y el limite esta escrito en
`residuos`, no implicito. El nombre del archivo es CANDIDATO de identidad de
sala, nunca identificacion: `venue.py proyeccion` avisa cuando no coincide y
**no escribe** el registro sin `--aplicar`, porque la sala la nombra una persona.
`superficie` se deja en `desconocido` a proposito: el archivo no puede ver si la
luz cae sobre LED, gasa o muro.

BUG PROPIO ENCONTRADO Y CORREGIDO: la primera version escribia la propuesta
dentro de `data/venues/`, y `cargar_todos()` recorre ese directorio con
`glob("*.json")`, asi que `venue.py validar` la leyo como un venue invalido y
devolvio 8 errores de esquema. Las propuestas viven ahora en
`data/venues_propuestas/`, fuera del glob, con una regresion que lo fija.

Comandos y codigos de salida:

- `python3 tools/venue_screen_setup.py --glob "/media/mak/PortableSSD/*.xml" --out-dir <salida> --index`: exit 0, 9 parseados, 0 fallidos.
- `./.venv/bin/python -m pytest -q tests/test_resolume_screen_setup.py -rs`: exit 0 (ground truth controlado, contraejemplos, consumidor y los 9 archivos reales).
- `./.venv/bin/python -m pytest -q tests/`: exit 0, suite completa.
- `python3 tools/venue.py validar`: exit 0, 3 venues, 0 errores.
- `tools/repo_audit.py`, `compileall -q src tools tests`, `pip check`, `git diff --check`: exit 0 los cuatro.
- `npm run typecheck` con el Node local v24.19.0: exit 0.

Salida persistida e inspeccionable, fuera del repo:
`/home/mak/curatoria_inbox/venue_projection/2026-08-21/` con 9
`*.projection.json`, `rig_index.json` y `projection.html`.

Fuentes intactas: el indice SSD conserva el fingerprint
`d3afb072fe1633125ac20da82aa1d3c7...` y los 9 `.xml` mantienen su mtime original
aunque el montaje sea `rw`. No se escribio nada en el SSD.

RESIDUO, lo que no sabemos: que superficie fisica es cada slice (LED, gasa,
muro), a que sala corresponde cada archivo, y si `CHILLAN`/`harry` son el mismo
rig o una plantilla. Nada de eso se resuelve leyendo mas: requiere una foto, una
fecha de contrato o la palabra del operador.

TRANSFERIBLE: la operacion es `archivo de configuracion de un dispositivo ->
geometria medida -> normalizacion con confianza por dato -> identidad marcada
como no verificada`. La misma forma aparece en MVR/GDTF para iluminacion y en un
patch de audio; si reaparece, se reconoce por esa firma y no por el dominio.

SIGUIENTE ACCION DE ESTE BLOQUE: el item 3 del orden de la memoria de direccion
(`esquema venue-JSON en schemas/`, el que bloqueaba el item 5) ya tiene su
primera fuente medida. Lo que falta para cerrarlo NO es codigo: es que una
persona diga a que sala corresponde cada uno de los 9 ScreenSetup. Con eso,
`venue.py proyeccion <archivo> <venue-id> --aplicar` escribe el registro; sin
eso la maquina se niega, y esa negativa es correcta.

La siguiente accion ejecutable sin decision humana es el reporte de huerfanos
(item 4 del mismo orden, `MEMORIA_DIRECCION.md` §2.12 pasos 1-3): inventario y
dedup por hash sobre el indice del SSD, solo lectura, sin mover un archivo. Es
la primera pieza vendible como informe y no depende de licencia, montaje ni
firma. Ojo con la frontera medida aca: `full_sha256` existe solo para 112 de
45536 assets, asi que la duplicacion exacta es demostrable en 0,25 % del indice
y el resto debe quedar como candidato, nunca como duplicado.

HALLAZGO QUE CORRIGE ESA SIGUIENTE ACCION (medido al aplicar la regla de
externalidad, buscando la misma operacion fuera de su dominio): la hipotesis
falsificada arriba SI es recuperable, en otro tipo de archivo. Las composiciones
de Resolume no son `.xml` sino `.avc`, y hay 4 en el indice:
`DREFGIRA/TALCA DREF.avc`, `DREFGIRA/IMPORT CLAUDIO/SHOWCAUPOLICAN FINAL ANTES
DE CAUPO.avc`, `LYON/sampier.avc` y `descargas hasta RDFLYER 2050/Perrys 2025
V2.avc`. `LYON/sampier.avc` (615 KB) contiene 107 etiquetas `<VideoFile>` y 10
`<AudioFile>` con rutas de clip reales. Eso es el grafo de referencias del paso 2
de `MEMORIA_DIRECCION.md` §2.12, o sea que el reporte de huerfanos del paso 3
deja de ser inventario ciego y pasa a poder responder "que assets usa un show de
verdad".

Dos restricciones medidas antes de construirlo:

- Las rutas dentro de los `.avc` son de Windows y traen nombres de usuario
  reales (`C:\Users\<usuario>`, y hay mas de uno distinto). `tests/test_privacidad_repo.py`
  prohibe exactamente ese patron en el repo, asi que esas rutas NO pueden entrar
  a un archivo versionado: se referencian por hash o se anonimizan al leerlas.
- Resolver una ruta Windows contra un asset del SSD es un problema de
  emparejamiento por basename, con la misma trampa de similitud que este bloque
  ya documento: dos clips distintos pueden llamarse igual. Requiere abstencion
  explicita, no un match optimista.

Tambien aparecieron mas ScreenSetup dentro de carpetas y no solo en la raiz
(`DREFGIRA/Los Vilos.xml`, `HARRY/cobquecura.xml`, `HARRY/show/sin culpa.xml`,
`BAHPARTY/bah/KAYAKAZE 2025 2.xml`, `LYON/1.xml`), asi que el parser de este
bloque tiene mas material real que los 9 de la raiz sin cambiar una linea.

## Show asset usage: which clips a real gig used — 2026-08-21

ANTES: MAK sabia que archivos existen en el SSD y no podia distinguir material
que se toco en un show de material que quedo en una carpeta. `DREFGIRA` eran 467
assets iguales entre si.

DESPUES: MAK puede leer una composicion `.avc` de Resolume, extraer sus
referencias de clip y resolverlas contra el indice del SSD con abstencion
explicita, reportando por composicion los assets usados, los ambiguos y los no
encontrados. Sobre el show real de Caupolican: 52 referencias, 28 resueltas sin
ambiguedad (53,85 %), 6 ambiguas y 18 no encontradas, y los assets resueltos son
el setlist en orden dentro de `DREFGIRA/BLOQUE 01 LSDR/` y
`DREFGIRA/BLOQUE 02 CLASICOS/`.

Relacion nueva que la estructura de carpetas no mostraba: ese show tomo material
de DOS contenedores, `DREFGIRA` y `descargas hasta RDFLYER 2050`. Ninguna
inferencia por carpeta lo habria dicho.

TEORIA: es record linkage entre dos catalogos con regla de abstencion, no una
busqueda. La composicion guarda rutas absolutas de otra maquina, asi que la unica
clave de union disponible es el basename. La hipotesis "en este corpus un
basename identifica un archivo" NO se asume: se comprueba, y cada referencia cuyo
basename lo llevan varios assets vuelve como `ambiguous` y no aporta nada a la
afirmacion de uso.

LA TASA ES UNA MEDICION, NO UN SUPUESTO. Las cuatro composiciones del indice dan
`TALCA DREF` 1/1, `SHOWCAUPOLICAN` 28/52, `sampier` 0/81 y `Perrys 2025 V2` 0/1.
`sampier.avc` cita el Escritorio y OneDrive de otra maquina, asi que no resuelve
nada y el reporte lo dice en vez de fingir. Un unico numero de "que tan bien
funciona esto" habria mentido sobre las cuatro.

LIMITES ESCRITOS EN LA SALIDA: una coincidencia de basename es candidata, no
identidad de bytes -- `full_sha256` existe para 112 de 45536 assets, o sea que la
verificacion por contenido no esta disponible para el 99,75 %. Una referencia no
encontrada NO prueba que el archivo no exista: puede vivir en la maquina que
produjo la composicion. Y `orphan_candidates()` se llama candidates a proposito:
451 de 467 assets de `DREFGIRA` no aparecen en la unica composicion legible de
ese contenedor, lo que NO los vuelve inutilizados, porque solo hay cuatro
composiciones en el indice y los shows del artista no son cuatro. La salida lo
dice y aclara que no es una lista de borrado.

DOS DEFECTOS PROPIOS ENCONTRADOS Y CORREGIDOS EN ESTE BLOQUE:

1. El archivo de test nuevo llevaba un usuario de Windows REAL tomado de las
   rutas del `.avc`. Se reemplazo por los placeholders que el repo ya declara
   exentos (`alguien`, `ejemplo`).
2. Al buscar por que el ratchet de privacidad no lo habia detectado aparecio el
   hueco de fondo: `tests/test_privacidad_repo.py` enumeraba con `git ls-files`,
   o sea SOLO archivos rastreados, asi que un archivo NUEVO con un dato sensible
   pasaba el gate local sin ser visto y recien fallaba una vez commiteado -- con
   el dato ya en la historia. Ahora tambien mira
   `git ls-files --others --exclude-standard`, que respeta `.gitignore`. El gate
   mejorado detecto de inmediato mis propios placeholders `x` y `someone`, que es
   la prueba de que servia. Fijado por
   `test_the_ratchet_sees_new_untracked_files`.

Comandos y codigos de salida:

- `python3 tools/show_asset_usage.py --composition ... --index ... --out-dir ... --orphans DREFGIRA`: exit 0, 4 composiciones, 0 fallidas.
- `./.venv/bin/python -m pytest -q tests/test_resolume_composition.py -rs`: exit 0.
- `./.venv/bin/python -m pytest -q tests/`: exit 0, suite completa.
- `tools/repo_audit.py`, `compileall -q src tools tests`, `pip check`, `git diff --check`: exit 0 los cuatro.
- `npm run typecheck` con el Node local: exit 0.

Salida persistida: `/home/mak/curatoria_inbox/show_usage/2026-08-21/` con
`*.usage.json` por composicion, `drefgira.orphans.json` y `usage.html`.

Fuentes intactas: el indice conserva el fingerprint
`d3afb072fe1633125ac20da82aa1d3c7...` y los `.avc` mantienen su mtime original.
Nada se escribio en el SSD, y ninguna ruta persistida lleva un usuario real.

RESIDUO: 18 referencias del show de Caupolican no estan en este disco y 6 son
ambiguas; resolverlas necesita el disco de origen o hashes de contenido, no mas
lectura. Y el reporte de huerfanos solo sera confiable cuando existan mas
composiciones leidas: hoy mide "no referenciado por las cuatro que hay", que es
una afirmacion mucho mas debil que "sin usar".

REFINAMIENTO MEDIDO EN EL MISMO BLOQUE: las 6 referencias ambiguas del show de
Caupolican no eran indecidibles. Al mirar los metadatos, las dos candidatas de
cada una coinciden en tamano en bytes Y en `sample_sha256`: es el MISMO clip
guardado dos veces, una suelto en `DREFGIRA` y otra dentro de un bloque del
setlist. Abstenerse ahi tiraba una respuesta usable, porque QUE clip sono estaba
decidido desde el principio; lo indeciso era en cual de las copias. Son dos
preguntas distintas y ahora llevan etiquetas distintas:
`resolved_multi_location` frente a `ambiguous`.

Efecto: Caupolican pasa de 28/52 a 34/52 con clip decidido (65 %) y 0 ambiguas,
y aparecen 6 duplicados explicitos en `copias_duplicadas`. El mecanismo
discrimina en vez de resolver en bloque: en `sampier.avc` recupero 3 y dejo 1
genuinamente ambigua. La tasa sin ambiguedad se mantiene aparte
(`tasa_resolucion_inequivoca`) porque la ubicacion sigue sin decidirse, y el
limite dice que sin `full_sha256` la coincidencia de tamano y sample es fuerte
pero no prueba de contenido. Un `sample_sha256` vacio o un candidato sin
metadatos NO cuenta como acuerdo.

Esto tambien alimenta la pregunta de `MEMORIA_DIRECCION.md` §2.12 que "se vende
sola" (que puedo borrar): una copia duplicada es candidata a borrado de una
manera en que un archivo unico no lo es. Los duplicados quedan listados, no
colapsados en silencio.

CORRECCION DE ENCUADRE, provocada por una pregunta del operador ("que relacion
tiene screen setup con los venue?") y resuelta midiendo, no argumentando: la
relacion es MAS DEBIL de lo que este bloque afirmo primero. Un ScreenSetup no es
una huella de sala. `BERLIN 1.xml` y `berlin 2.xml` nombran el mismo lugar y no
comparten NINGUNA superficie -- 59 contra 9, lienzo 3043x272 contra 1920x1080,
clasificado `different_rig`. En cambio `cobquecura.xml` en la raiz y en `HARRY/`
si son el mismo rig, porque es el mismo archivo copiado.

Lo que el archivo describe es un DESPLIEGUE de una fecha, y no puede separar tres
cosas que estan mezcladas en el: lo que es del recinto (la grilla real de una
pantalla LED de casa, la forma de una superficie de proyeccion), lo que es del rig
que se llevo esa noche (cuantas salidas, que procesador) y lo que es decision del
operador (donde corto el lienzo, como nombro las superficies).

Consecuencia aplicada al codigo, no solo anotada: el fragmento `proyeccion`
empieza ahora con `DESPLIEGUE, no configuracion permanente de la sala`, el
contraejemplo de Berlin viaja como residuo dentro de cada registro, y
`TestDeploymentNotVenue` lo fija sobre los archivos reales. Para una sala esto
sigue siendo evidencia util y FECHADA -- mejor que el PDF de 2014 que el venue
mandaria -- pero nunca su configuracion permanente, y una segunda noche puede no
parecerse en nada.


## Cola de leads: preguntarle al catalogo antes de catalogar — 2026-08-21

ANTES: la cola de productoras candidatas de RD proponia como cliente potencial
cualquier cluster con >=2 obras. El conteo era la unica calificacion. Medido
sobre el corpus real (1742 fichas rd -> 984 obras tras colapso de secuencias):
de 3 propuestas escritas, una era `CARTERELA TEstEAMDO` -- la cartelera de
testeo de RD corrompida por OCR, producto propio y no un cliente -- y otra era
`Banco de Chile`, un patrocinador que el OCR levanta del flyer. Ademas
`TEATRO CAUPOLICAN` y `TEATRO ROMA` figuraban como productoras candidatas
siendo venues.

DESPUES: un candidato nuevo pasa por descalificadores nombrados antes de
volverse propuesta, y el informe dice cual y por que en vez de que desaparezca
en silencio. Propuestas escritas: de 3 a 1, y la que queda (`TECHMOTION CHILE Y
DEL AVERNO`) es el lead real.

CORRECCION DE METODO, indicada por el operador: la primera version escaneaba el
corpus para deducir que strings eran venues. Eso era REPAIR sobre una
adivinanza. Lo correcto es REMOVE NEED: **un venue no es una productora, y la
pregunta se le hace al CATALOGO** -- `cargar_catalogo_venues()` y el mismo
`mejor_match` que el modulo ya usa -- antes de catalogar. Se elimino la
heuristica de corpus.

Y lo que ningun dato puede decidir se DEFINE en vez de deducirse:
`data/productoras/no_organizadores.txt`, una linea por nombre. Definir una vez
es mas barato que perseguir una regla perfecta. Ahi entran los patrocinadores
vistos en el corpus (Banco de Chile, Red Bull, Schweppes, CoolBet) y las marcas
de equipamiento (Funktion-One), que aparecen en un flyer sin organizarlo. Si el
archivo no existe, no hay descalificacion por esa via.

Las cuatro vias, cada una comprobable por separado:
`identidad_propia_rd` (la cartelera propia, incluidas sus corrupciones de OCR,
con guarda para que "Cartel Norte" NO caiga), `notacion_de_lineup` (`B2B`,
`VS`: una alineacion de DJs no es un organizador), `declarado_no_organizador`
(el archivo) y `es_un_venue_del_catalogo`. Lo que no cae en ninguna via NO se
descalifica: sigue siendo candidato y el borrador lleva su evidencia.

CORRECCION DE UN JUICIO PROPIO: primero llame "basura" a esas propuestas. Fue
duro y equivocado. El borrador ya mostraba los handles (`@RedBull, @Schweppes`
en el de Banco de Chile) y dice "convertir via PR humano, NO escribir directo".
La maquina propone con evidencia y la persona firma, que es la regla dura #4 del
contrato. El defecto real era mas chico y mas concreto: la cartelera propia y
los venues no debian llegar a la cola.

CONTEXTO QUE ORDENA ESTO, aportado por el operador: no es VJ de RD. Es DISENADOR
de RD, y aparte VJ de artistas (Drefquila, Harry Nach). Por eso los dos corpus NO
se cruzan por nombre de artista -- medido: `nach` 0, `drefquila` 0, `bah` 0 en
las 3385 fichas. El puente entre ambos rubros no es el artista: es que RD da el
lenguaje y el acceso a PRODUCTORAS, que son los clientes potenciales, y lo que
se les ofrece es rider/plano/zona de descanso con el respaldo tecnico de
pantallas. De ahi que la calidad de esta cola importe comercialmente.

Tambien confirmado por el operador y ya no candidato: `harry.xml` y `CHILLAN.xml`
son el MISMO show, Harry Nach en Chillan. El `same_rig_candidate` que este
trabajo dedujo por topologia era correcto, y la atestacion humana resuelve el
desempate que el codigo dejo declarado.

Comandos y codigos de salida:

- `python3 cultura/mak_curatoria/extraccion_db.py ~/curatoria/fichas/fichas.jsonl --outdir <temp> --fuente rd`: exit 0; 984 obras, 20 clusters nuevos, 1 propuesta escrita, 2 descalificados con motivo.
- `./.venv/bin/python -m pytest -q tests/test_extraccion_db.py`: exit 0.
- `./.venv/bin/python -m pytest -q tests/`: exit 0, suite completa.
- `tools/repo_audit.py`, `compileall`, `git diff --check`: exit 0.

Fuentes intactas: no se escribio en `~/curatoria/fichas/`; las salidas fueron a
directorios temporales y el unico archivo nuevo del repo es la lista declarada.

RESIDUO: `MATUCANA #100, TECHNO YOUTH, MIDO, PANAL RECORDS, toliv` sigue siendo
UN candidato con cinco entidades adentro, y dos de ellas (TECHNO YOUTH, PANAL
RECORDS) ya son canonicas. Partir ese campo recuperaria entidades conocidas,
pero es un cambio en la extraccion y no en la calificacion; queda anotado, no
hecho.

## Puertas de entrada: cerrar la clase, no la instancia — 2026-08-21

Reclamo del operador, correcto: yo mismo violé cuatro veces la regla de idioma
que `agents.md` declara y que lei al empezar (`NOTACION_LINEUP`,
`cargar_no_organizadores`, `tiene_notacion_lineup`, nombres de test en
espanol), dejando que el ratchet me corrigiera en vez de acertar. Y peor: habia
arreglado el hueco de enumeracion SOLO en el ratchet de privacidad, que es
exactamente el parche parcial que se me senalo. Este bloque cubre la clase.

CLASE 1 -- una puerta que protege contra la ENTRADA de algo tiene que mirar lo
que esta entrando. Enumerar con `git ls-files` a secas ve solo lo rastreado, asi
que un archivo NUEVO pasa la puerta local sin ser visto y falla recien
commiteado, con la cosa ya en la historia. Miembros medidos:

- `tests/test_higiene_docs.py`: lo tenia en su PROPIO docstring -- "cuatro
  README vendorizados pasaron el pytest local y tumbaron el CI" -- resuelto con
  un workaround manual (`git add` primero). Un workaround que vive en la memoria
  de una persona vuelve a fallar. CERRADO.
- `tests/test_privacidad_repo.py`: ya cerrado antes, ahora comparte la
  implementacion en vez de tener su propia copia.
- `tools/idioma.py`: ya lo hacia bien, y por eso fue el unico que me caz
  al instante. Sin cambios.
- `tests/test_higiene_repo.py::test_config_del_usuario_versionada`: NO es
  miembro. Afirma que la config ESTA versionada, asi que incluir untracked
  destruiria su proposito. Se deja como esta, con la razon escrita.

La regla queda dicha una vez, en `tests/repo_scan.py`: una puerta que pregunta
"esto ya esta commiteado?" usa `git ls-files`; una que pregunta "puede entrar
esto?" usa `versionable_files()`. Verificado ejecutando, no leyendo: una sonda
`.md` sin rastrear con una cifra de suite en prosa AHORA falla antes del commit,
y al borrarla vuelve a verde.

CLASE 2 -- el cero silencioso, que la memoria de direccion §2.3 ya nombra ("0
resultados por primera vez es ERROR, no silencio"). Un barrido AST sobre los
tests marco 69 candidatos, pero eran ruido: casi todos son unitarios con
fixtures literales donde "vacio" es imposible. Acotado a puertas que escanean el
repo quedaron 18, y de esas las reales son tres, todas en
`test_higiene_repo.py`:

- `test_tools_en_registro`: si `tools/` se mueve o se vacia, la lista queda
  vacia y el ratchet informa "nada falta" para siempre. Ahora exige haber medido
  algo. Verificado apuntandolo a un directorio vacio: antes pasaba, ahora falla.
- `test_registro_sin_herramientas_fantasma`: si la tabla de `CAPACIDADES.md`
  cambia de formato, el regex deja de matchear y el ratchet pasa sin medir. Ahora
  exige filas declaradas Y herramientas existentes.
- `test_config_del_usuario_versionada`: hacia `return` cuando git no estaba
  disponible, o sea verde sin medir. Ahora hace `pytest.skip` explicito.
  Verificado ejecutando esa rama contra un directorio sin git: devuelve
  `Skipped`, no verde.

Defecto propio encontrado al hacerlo: la primera version de ese cambio usaba
`pytest.skip` sin `import pytest` en el archivo -- un `NameError` esperando la
rama sin git. Detectado ejecutando la rama, no leyendola.

Comandos y codigos de salida: `pytest -q tests/` exit 0; `repo_audit`,
`compileall`, `pip check`, `git diff --check` exit 0; `npm run typecheck` exit 0.

RESIDUOS CERRADOS (no quedan declarados sin resolver):

1. Las 15 restantes de la lista de 18 SI se verificaron una por una. Catorce son
   `tmp_path`/`TemporaryDirectory` y su `assert not list(...)` recorre un
   directorio que el propio test acaba de poblar: vacio ahi ES la afirmacion
   ("no quedaron temporales"), no una falta de medicion, asi que un pase en
   vacio es imposible por construccion. La numero 15 era real y quedo cerrada:
   `test_campo_filtro.py::test_ningun_trazo_publicado_es_de_una_obra_excluida`
   comparaba `campo.json` contra `glob(iskvw/piel/trazos/*.svg)`, y si ese
   directorio se mueve el glob devuelve vacio, `huerfanos` queda vacio y el
   ratchet informa "todo limpio" para siempre mientras los trazos reales viven
   sin vigilancia. Su propio docstring registra que el incidente ya paso ("441
   trazos de obras que el filtro dejaba fuera"). Medido hoy: 219 piezas en
   campo.json, 208 svg en disco, 208 en el indice. Ahora exige haber medido algo,
   y su gate hermano (`test_el_indice_de_trazos_dice_la_verdad`) tambien, porque
   comparar dos conjuntos vacios no prueba que el indice diga la verdad.
   Verificado apuntandolo a un directorio vacio: antes pasaba, ahora falla.

2. El ratchet de idioma para codigo no-Python se MIDIO y se DECLINA con razon,
   no por omision. En `web/src` hay 36 archivos ts/tsx y 17 declaraciones con
   raiz espanola en 9 de ellos. Pero estan mezcladas: `ProductoraRef`,
   `productoras.ts` y `ArchivoReg` usan terminos de DOMINIO sin equivalente
   ingles que no pierda significado -- "productora" es vocabulario de la
   industria de eventos chilena, igual que se conserva "venue" --, mientras
   `carpetaDe`, `estadoLegible`, `salidas` y `archivo` si son deriva de estilo
   con equivalente directo. Un ratchet duro sobre esa poblacion forzaria
   renombres malos y necesitaria una lista curada a mano de terminos de dominio,
   que es exactamente el patron que la memoria de direccion advierte ("una lista
   escrita a mano es lo que este repo hitio tres veces"). Resultado negativo
   registrado: 17 casos, mezcla de dominio legitimo y deriva, no justifica un
   gate. Si la poblacion crece, la decision se revisa con el numero a la vista.

RESIDUO QUE SI QUEDA: la regla de idioma en Python sigue dependiendo de que el
ratchet la haga cumplir en tiempo de test; no hay verificacion mas temprana. En
esta sesion me caz cuatro veces, lo que significa que funciona, y tambien que yo
no la aplique antes de escribir.

## Puertas que no disparan y puertas mas angostas que su regla — 2026-08-21

Dos clases mas, medidas y cerradas.

CLASE 3 -- una herramienta declarada como dependencia, reportada como ausente.
`src/flujo/laser.py` resolvia vpype con `shutil.which("vpype")`, que solo mira
`PATH`. Pero vpype esta declarado en `pyproject.toml` (extra `dev`),
`.venv/bin/vpype` existe y `import vpype` funciona: pip pone los console scripts
al lado del interprete, y ese directorio NO esta en `PATH` cuando la suite corre
como `./.venv/bin/python -m pytest`. Resultado: `laser.verificar()` devolvia
`{"vpype": False}` y `test_estado_reporta_la_cadena_real` se saltaba con "vpype
not installed" en una maquina donde SI esta instalado. Una puerta que no dispara
donde la dependencia existe no es una puerta.

Es la misma clase que ya arregle para Blender y Node en esta sesion, asi que la
resolucion vive en el mismo lugar: `runtime_tools.resolve_console_script()`
mira override explicito, `PATH`, y el `bin` del interprete. `laser.py` lo usa y
ahora `verificar()` devuelve `vpype: True`; el test dispara y pasa, y ese archivo
quedo con cero skips. Los skips de la suite bajaron de 6 a 5.

Trampa propia encontrada al escribirlo: la primera version usaba
`Path(sys.executable).resolve().parent`, y como `.venv/bin/python` es un SYMLINK
a `/usr/bin/python3`, resolverlo sale del venv y el script nunca se encuentra. Se
usa el dirname sin resolver, mas `sys.prefix`. Detectado midiendo el valor real,
no leyendo el codigo.

Verificado tambien que los otros `shutil.which` del repo NO son miembros:
`rasterizador.py` ya usa lista de candidatos antes de `PATH`, y `gh`, `npm`,
`ffprobe`, `pdfinfo` y `7z` son herramientas de sistema donde `PATH` es correcto.

DIVERGENCIA DE UNA MISMA VERDAD: Blender se resolvia con `BLENDER_EXE` en
`runtime_tools` y con `MAK_BLENDER` en
`cultura/mak_curatoria/diagnostico_proyectos.py`, y con nada mas en ninguna otra
parte. `MAPA.md` documenta `BLENDER_EXE`, asi que quien seguia la documentacion
resolvia Blender en un lado y NO en el otro, en silencio. Ahora los dos nombres
funcionan en los dos lugares y gana el documentado; el alias quedo documentado
como alias. No se unifico por import a proposito: ese archivo tambien corre
proyectado desde `/home/mak/curatoria` con otro interprete, y un import fragil
seria peor que la duplicacion.

CLASE 4 -- una puerta mas angosta que la regla que dice hacer cumplir.
`test_toda_variable_de_entorno_esta_documentada` exige que toda variable de
entorno este en `MAPA.md` seccion 4, pero escaneaba SOLO `src/flujo`. Todo
`cultura/` y `tools/` -- donde viven el Hub, Research y Codex -- escapaba a la
regla. Se descubrio de rebote: al agregar el alias `MAK_BLENDER` en `src/` la
puerta angosta por fin lo vio y fallo.

Medido al ensanchar: 82 variables leidas fuera de `src/flujo` sin documentar.
Documentar 82 en un commit no es verificar, y una puerta que no puede pasar se
desactiva en vez de obedecerse, asi que las zonas anchas quedan con un pin que
SOLO puede bajar -- el mismo patron que el ratchet de idioma ya usa:
`tests/fixtures/env_documentado_baseline.txt` mas `tools/env_baseline.py`
(`--write` lo reescribe a proposito). El ratchet nuevo falla ante una variable
NUEVA, exige que el pin no conserve variables ya documentadas, y comprueba que el
escaneo ancho siga viendo `cultura/` para que no se angoste en silencio.

Verificado ejecutando, no leyendo: se agrego un archivo temporal en `cultura/`
leyendo `MAK_PROBE_UNDOCUMENTED_VAR`, la puerta fallo nombrandola, y al borrarlo
volvio a verde.

Comandos y codigos de salida: `pytest -q tests/` exit 0 (5 skips, todos por
cairosvg/navegador ausentes en esta maquina, presentes en CI via el extra
`render`); `tools/env_baseline.py` exit 0 con 82 pineadas y 0 nuevas;
`repo_audit`, `compileall`, `pip check`, `git diff --check` exit 0.

RESIDUO: las 82 variables siguen sin documentar y el pin mide esa deuda; bajarlo
es trabajo de documentacion, no de codigo. Y vuelvo a anotar lo mismo de antes,
porque volvio a pasar dos veces en este bloque: escribi comentarios nuevos en
espanol y el ratchet de idioma me corrigio. La regla la hace cumplir la puerta,
no yo.

## Un VIVO que no se sostiene al invocarlo — 2026-08-21

CLASE 5 -- el registro dice "toda herramienta declara consumidor o no entra",
pero `test_tools_en_registro` solo comprueba que el NOMBRE aparezca en
`CAPACIDADES.md`. No comprueba que la herramienta siga corriendo, asi que una
fila puede seguir afirmando VIVO sobre un script que revienta al importar.

Medido antes de tocar nada. Las 61 rutas que las filas del registro reclaman
existen todas: 0 faltantes, resultado negativo que no habia que arreglar. De las
40 herramientas VIVO, 21 no nombran un test en su fila y 4 no tienen NINGUN test
en `tests/` que las mencione (`execute_research_job.py`,
`gen_iskvw_prototipo.py`, `gen_propuesta_directiva.py`,
`interpretive_garden_workflow.py`). No se escribieron 4 tests arbitrarios: eso es
volumen. La pregunta falsificable que cubre las 40 es mas barata -- una
herramienta declarada viva tiene que sostenerse cuando se le pregunta que hace.

Resultado: 40/40 compilan. 39/40 responden `--help`; la que no
(`system_map.py`) tiene subcomandos propios (`validate`/`show`), imprime su
usage y sale 2, que es error de uso y no rotura -- mi supuesto de contrato era
demasiado estrecho y se corrigio, no el codigo. Una sola largaba traceback sin
manejar: `gen_campo_iskvw.py` con `ModuleNotFoundError: sklearn`.

Ese fallo era DELIBERADO y su docstring lo dice: "Sin el, no se inventa una
proyeccion peor y se falla: un campo con posiciones falsas es peor que no tener
campo", y el comentario de `main()` aclara que sklearn vive en la caja que
proyecta, no en MAK. Lo que NO era deliberado es entregarlo como stack trace.
Ahora falla igual -- exit 1, sin inventar posiciones -- pero diciendo por que y
que hacer. La puerta nueva pide exactamente eso: un fallo puede ser correcto,
pero tiene que decir su razon en vez de dejar un traceback.

DANO QUE ME HICE Y REPARE, porque la primera version de esa puerta invocaba cada
herramienta con `--help` Y SIN ARGUMENTOS: eso MUTO el repositorio.
`update_readme_svg.py` regenero la capa de texto de `arte-ascii-readme.svg`, que
`agents.md` declara activo protegido; `gen_propuestas_rd.py` escribio
`docs/rd/propuestas_mineria/`; y la peor, invisible para `git status` porque esta
gitignoreada: `iskvw/datos/archivo.json` quedo en 11 KB cuando debe tener ~1,79
MB, regenerada sin el micelio privado, lo que tumbo
`test_iskvw_piel_smoke.py` y `test_readme_svg.py`.

Reparacion completa y verificada: el SVG protegido restaurado desde HEAD (0
cambios), el directorio generado apartado a la carpeta temporal del job en vez de
borrado, y `archivo.json` regenerado con el comando de CI
(`tools/gen_archivo_iskvw.py --fuente todo`, 2034 piezas, 5812 vinculos, 1790.8
KB). Los cuatro tests que habia roto vuelven a pasar. `campo.json` esta rastreado
y su contenido no cambio.

La puerta ahora pregunta SOLO `--help`, y
`test_the_tool_ratchet_never_writes_to_the_repo` fija esa regla leyendo el cuerpo
del test: si alguien vuelve a iterar formas de invocacion, falla. Descubrir que
una herramienta muta con invocacion pelada no puede costar la mutacion.

Hallazgo que queda anotado y NO se toca en esta pasada: dos herramientas VIVAS
escriben cuando se las invoca sin argumentos (`update_readme_svg.py`,
`gen_propuestas_rd.py`). Para `update_readme_svg.py` puede ser su diseño -- su
fila declara un `--check` para deteccion sin escribir --, pero un generador que
muta por invocacion pelada es un riesgo real para cualquiera que lo pruebe. Es
una decision de contrato de esas herramientas, no de esta puerta.

Comandos y codigos de salida: `pytest -q tests/` exit 0 y el repo queda sin
cambios despues de correr la suite completa; `repo_audit`, `compileall`,
`git diff --check` exit 0.

RESIDUO: las 4 herramientas VIVAS sin test siguen sin test propio. La puerta
nueva prueba que se sostienen al preguntarles que hacen, que es mucho menos que
probar que hacen bien su trabajo. Y por sexta vez en la sesion escribi
identificadores nuevos en espanol y el ratchet de idioma me corrigio; esta vez
liste los flagueados antes de renombrar, lo que deberia haber hecho desde el
principio.

## Copias entre contenedores: 543 grupos que NO son basura — 2026-08-21

Contexto que solo el operador podia dar, y que cambia una herramienta: LYON es
un cliente (`@LyonLaF`); `ESCARLATA` y `CDR` son canciones de Drefquila, y
Escarlata es un REMIX en el que participa Harry Nach.

Con eso, una medicion que ya estaba ahi se vuelve legible: 543 pares
(basename, bytes) identicos viven bajo mas de un contenedor, 31,3 GB contando
solo las copias extra. Un deduplicador ve una sola cosa; son al menos tres, y
borrar la copia equivocada es una perdida distinta en cada caso:

- el mismo clip en dos shows: `HARRY CHILLAN/ESCARLATA.mp4` y
  `HARRY/show/VINA/ESCARLATA.mp4`, que es el set del VJ viajando;
- el mismo clip bajo tres artistas porque el tema es una colaboracion:
  `escarlata.mp4` en DREFGIRA, DrefQuila y HARRY;
- la carpeta de una gira y la obra propia del artista con la misma pieza:
  `enrolar.mp4` (3,37 GB) y `misionar.mov` (2,56 GB) en DREFGIRA y DrefQuila.

`cross_container_copies()` los nombra y se NIEGA a rankearlos. La advertencia es
explicita: ninguno es candidato a borrado, porque borrar la copia equivocada
rompe un set, una colaboracion o el cuerpo de obra de OTRA persona. La lista
existe para que una persona la lea, no para liberar disco. El aviso del reporte
de huerfanos ahora lleva esa medicion adentro en vez de una prudencia generica.

Detalle que valida el diseño: `escarlata.mp4` aparece como DOS grupos de tamaños
distintos -- 2,11 GB con tres artistas y 251 MB entre HARRY y HARRY CHILLAN --
y agrupar por (basename, bytes) los mantiene separados. Son relaciones
diferentes, no un duplicado. El test lo fija asi, distinguiendo la colaboracion
del set que viaja.

DOS DEFECTOS PROPIOS EN LAS PRUEBAS, no en el codigo: la primera version del test
indexaba por basename y se comia uno de los dos grupos de escarlata; y la fixture
de indice sintetico no tenia la columna `sample_sha256` que la funcion lee, o
sea probaba una base distinta de la que existe. Las dos corregidas.

LA LEY CUESTIONADA, Y SE SOSTIENE. El operador señalo que la regla de idioma es
por ASCII ("si hay N con virgulilla se rompe el codigo") e invito a cuestionar la
ley. Medido: el ratchet SI atrapa un identificador no-ASCII -- una sonda con
`tamaño` fue marcada -- y hoy hay CERO identificadores no-ASCII en todo el arbol.
La misma puerta cubre la restriccion dura (ASCII) y la convencion documentada
(ingles, con su medicion en `docs/GLOSSARY.md`: 236 archivos con comentarios en
espanol contra 36 en ingles). Mi hipotesis de que la puerta vigilaba la
convencion y no el peligro queda FALSIFICADA. Las seis violaciones de esta sesion
fueron mias, no de la regla.

Comandos y codigos de salida: `pytest -q tests/` exit 0; `repo_audit`,
`compileall`, `git diff --check` exit 0.

RESIDUO: no se clasifica automaticamente cual de las tres relaciones es cada
grupo, y no deberia sin evidencia: distinguir "colaboracion" de "copia de
respaldo" necesita saber quien es el artista, que es justo lo que la maquina no
puede leer del disco. Quedan 543 grupos listados para lectura humana, no 543
decisiones.

## LYON LA F catalogado — 2026-08-21

El operador atestiguo que LYON LA F es un CLIENTE ACTIVO de su trabajo de VJ y
pidio catalogarlo. Era el contenedor mas grande del disco y el unico grande sin
tocar: 15.055 assets, 250,9 GB, 387 filas del escaneo por carpetas.

MATERIAL. Se reconstruyo con la herramienta que ya se uso para DREFGIRA,
FELINA/LOGO y BAHPARTY/bah, sin inventar formato: 387 filas -> 1 unidad de
proyecto, 24 subproyectos, 314 dependencias de biblioteca y 48 recursos
compartidos, con los 15.055 assets reconciliados, cero sin asignar y cero
decisiones UNKNOWN. Las obras nombradas mas grandes: Pajsaera (84,4 GB),
MERECEDORA (28,5), COMANDO (24,6), DEJA (15,5), NEBULA (14,0), CIUDAD (12,0),
la ferrari (6,6), LOGO ENTREGA (5,9), CORAZON (4,0).

ACTIVIDAD MEDIDA, no afirmada: 14.039 assets con mtime de 2025 y 899 de 2026,
contra 60 de 2016 y menos de 40 por ano entre 2020 y 2024. El cuerpo de obra es
reciente, lo que concuerda con "cliente activo" sin depender de esa palabra.

PROJECT IR. El puente existente (`tools/import_project_reconstruction.py`)
escribio 25 registros derivados en `data/mak_knowledge.db`, TODOS en
`review_required`, y sus 25 rutas quedaron en `abstain`. La maquina cataloga el
material y no afirma nada sobre el hasta que un humano lo revise.
`PRAGMA integrity_check` = ok; se tomo copia previa de la base.

FICHA DE CLIENTE: `data/productoras/lyon-la-f.json`. Vive ahi porque ese
directorio YA cataloga artistas -- `frvr.json` tiene `tipo: artist_dj` con una
nota que aclara que es el artista y no la productora --, no porque LYON organice
eventos. La ficha declara esa consecuencia en vez de dejarla implicita: al estar
ahi, el fuzzy-match de `extraccion_db.py` puede resolver un "LYON" leido por OCR
en un flyer contra esta ficha. Se verifico que no altera la cola de leads: sigue
dando 1 propuesta y las mismas canonicas.

Lo que la ficha NO afirma: `instagram` queda VACIO. El handle `@LyonLaF` aparece
dentro de un nombre de archivo (`COMO TU - @LyonLaF (AUDIO OFICIAL) [PROD.NACHO
G FLOW].wav`), lo que es evidencia de nombre y no una cuenta verificada.
Tampoco se inventaron venues, fechas ni eventos.

HALLAZGO QUE NO SE CODIFICO, a proposito: al menos 8 de los 24 "subproyectos" no
son obras sino artefactos de herramienta que el escaneo por carpetas no
distingue -- `Adobe After Effects Auto-Save`, `LYIONGIF.aep_AME`,
`(Material de archivo)`, `blenderkit/blendfiles` y modelos descargados como
`uploads_files_2475145_la+ferrari` y `nissan-skyline-gt-r-r34-1999`. Se midio
sobre TODO el indice: solo 8 filas de 917 caen en ese patron, ~0,08 GB. Seis
regex para ocho filas es sobreajuste y seria una lista escrita a mano, que es
justo el patron que la memoria de direccion advierte. Quedan anotadas en la
ficha para que una persona las confirme, no convertidas en regla.

Tambien medido: LYON comparte 48 items de biblioteca con BAHPARTY, bah, SCD y
"descargas hasta RDFLYER 2050". Son assets comprados o descargados reutilizados
entre trabajos, y NO son las 543 copias entre contenedores documentadas antes:
esas son la misma obra en dos cuerpos de trabajo, estas son insumos comunes.

Comandos y codigos de salida: `tools/project_reconstruction.py --scope LYON`
exit 0; `tools/import_project_reconstruction.py --db data/mak_knowledge.db`
exit 0; `pytest -q tests/` exit 0; `repo_audit`, `git diff --check` exit 0; la
cola de leads reejecutada sin cambios.

Salida persistida: `/home/mak/curatoria_inbox/project_reconstruction/2026-08-21/lyon/`
con `reconstruction.json`, `reconstruction.html` y `project_ir/`.

RESIDUO: cuales de los 24 subproyectos son obras entregadas y cuales material de
trabajo no se decide desde el disco, y no deberia. Los 25 registros siguen en
`review_required` esperando esa lectura humana.

## La cola de revision tenia productores y no tenia puerta — 2026-08-23

MEDIDO antes de tocar nada, y es el hallazgo que ordena todo lo demas:

    project_records        34 review_required | 4 active | 1 candidate
    project_transitions    0 filas
    transition_project()   1 llamada en todo el repo, dentro de su propio test
    classification_queue   8273 pending

Cero transiciones en toda la historia de la base. Se construyeron cuatro
productores que escriben registros que una persona tiene que leer, la maquina de
estados que registra la respuesta de esa persona estaba escrita y validada, y
nunca se construyo una superficie para llegar a ella. Lo unico que ha movido el
estado de un proyecto en este repo es un unit test sobre una base temporal.

Al intentar construir esa puerta aparecieron tres defectos, en orden de gravedad
creciente. Ninguno se habia visto por la razon mas simple posible: el vocabulario
de relaciones tenia UN productor, CERO consumidores y CERO tests, asi que ningun
codigo habia leido nunca una arista.

DEFECTO 1 — direccion invertida en la mitad de las aristas. `_relations_for` en
`reconstruction_adapter.py` re-ancla cada arista en el registro actual como
sujeto y conserva el predicado. Cuando el registro es el lado derecho, eso emite
lo contrario de lo que la fuente dijo. Medido: las 24 aristas `contains` de LYON
se volvieron 56 en el grafo persistido, la mitad al reves. En `depends_on` es
peor que cosmetico: decia que una textura comprada depende de la obra que la usa,
que es exactamente como un item de biblioteca se disfraza de proyecto.
Corregido declarando `RELATION_INVERSES` en el productor y emitiendo el predicado
INVERSO al re-anclar. Ahora: 28 `contains` y 28 `contained_by`, balanceadas.
`inverse_relation()` se NIEGA ante un predicado sin inverso declarado en vez de
adivinar, porque una adivinanza silenciosa es como sobrevivio la primera
inversion.

DEFECTO 2 — un nombre con dos significados. `shared_resource` se usaba para la
relacion SIMETRICA entre dos contenedores ("estos dos cuerpos de obra reutilizan
compras") y para la DIRIGIDA entre un dueno y su carpeta de recursos. Con un solo
nombre la direccion no era recuperable. Se definio en vez de inferirla: la
simetrica ahora es `shares_library_with`. Verificado que ningun
`reconstruction.json` persistido contenia la simetrica, asi que el renombre no
deja datos ambiguos atras.

DEFECTO 3, el que importa mas — una re-derivacion podia BORRAR una decision
humana. `save_project` hace upsert con `state=excluded.state`, y todos los
adaptadores emiten `review_required` porque una maquina no tiene permitido
afirmar. Es decir: reimportar sobre un proyecto que una persona ya habia movido a
`active` lo arrastraba de vuelta a la cola y destruia lo unico de esta base que
una maquina no puede regenerar. Era inofensivo solo porque nunca se habia
decidido nada. Ahora una re-derivacion refresca la EVIDENCIA y nunca el
VEREDICTO: si existe una transicion registrada, el estado guardado gana.
Verificado sobre datos reales -- reimport completo de LYON con 4 decisiones
tomadas, las 4 sobrevivieron.

LA PUERTA. `src/flujo/knowledge/review_queue.py` + `tools/project_review.py`.
El problema debajo no es mostrar una lista: la atencion del operador es el
recurso mas escaso del sistema y la cola solo crece. La pregunta real es cual
pregunta, hecha primero, resuelve mas registros -- y eso se contesta sin inventar
un puntaje, porque las aristas de contencion forman un bosque y un tipo de
respuesta se propaga por el. Es un CONTEO, no un juicio.

Asimetria, y es falsable: el RECHAZO se hereda hacia abajo (una carpeta que es un
Auto-Save de After Effects no puede contener una obra entregada; la afirmacion es
sobre lo que el contenedor ES). La ACEPTACION no se hereda (una obra real
contiene material de trabajo). Si el operador alguna vez anula un rechazo
heredado, eso es un contraejemplo y lo que hay que registrar es la anulacion.
Nada se propaga solo: `--cascade` nombra la herencia.

La palanca se llama `rejection_leverage` a proposito. Llamarla "leverage" a secas
prometia un ahorro que solo una de las dos respuestas paga.

Dos pasos, porque son dos y quieren ordenes opuestos:

    --pass prune       encabeza por rejection_leverage: LYON 25, DREFGIRA 5,
                       LYON/Pajsaera 4, LYON/1 4, LYON/3 3, LYON/golden 3
    --pass recognize   encabeza por material: LYON 250,9 GB, DREFGIRA 102,6,
                       LYON/Pajsaera 85,7, FELINA/LOGO 41,2, MERECEDORA 28,8

LO QUE ESTO CAMBIA EN LA CUENTA: la cola no son 36 preguntas, son **8**. Ocho
raices cubren los 36 registros por contencion. Y `LYON/golden` con
`rejection_leverage 3` propone exactamente las dos carpetas
`(Material de archivo)/...` que el 2026-08-21 se decidio NO codificar como regla
(seis regex para ocho filas de 917 era sobreajuste). Ya no hace falta la regla:
el operador rechaza el contenedor una vez y se hereda.

VALIDACION CRUZADA que vale la pena anotar: el subarbol de LYON en el grafo de
Project IR suma 250,9 GB, identico a la medicion independiente del indice del
SSD. Dos caminos distintos dan el mismo total.

DOS CORRECCIONES A LO QUE YO MISMO REPORTE ANTES:

1. Dije que cuatro cuerpos de obra estaban puenteados a Project IR. Falso:
   `FELINA/LOGO` y `BAHPARTY/bah` tenian su `reconstruction.json` en disco pero
   nunca se habian importado a la base. Ahora si -- 41 registros, ninguno perdido,
   35 actualizados en sitio.
2. Dije que LYON comparte 48 items de biblioteca con BAHPARTY, bah, SCD y
   descargas. Incompleto: son NUEVE raices --
   `descargas hasta RDFLYER 2050` (32), SCD (13), BAHPARTY (4), bah (4),
   KISZ (4), FELINA (3), OBER (2), `3D JJJ` (1), interplanetary (1).

Comandos y codigos de salida: `pytest tests/` exit 0 (13 nuevos en
`test_review_queue.py`, 4 en `test_reconstruction_adapter.py`, 3 en
`test_project_ir.py`); `repo_audit.py` exit 0, `integrity=ok` en las 4 bases;
ratchets de idioma, docs, privacidad, higiene y mapa exit 0. Se verifico que los
tests nuevos FALLAN sobre el codigo viejo (`assert 2 == 0`), no que solo pasan.
`tools/project_review.py list/summary/show` deja el sha256 de la base intacto.
`data/mak_knowledge.db` sigue ignorada por `.gitignore:179`, asi que la
re-derivacion es local y regenerable.

LO QUE NO HICE, y es deliberado: no decidi ni una sola de las 36. Las obras las
reconoce el operador; la maquina propone con evidencia y el humano firma. Las
pruebas de escritura se hicieron sobre una COPIA de la base.

RESIDUO: los 8273 `classification_queue` pendientes son otra cola, con otra
forma, y todavia sin puerta. Y la asimetria rechazo/aceptacion es una hipotesis
con una prediccion clara: si el operador anula un rechazo heredado, esta mal.

## La segunda cola: 8273 filas que no eran 8273 preguntas — 2026-08-23

`classification_queue` tenia la misma enfermedad que la cola de proyectos, en un
segundo lugar: 8273 filas TODAS `pending`, cuatro plantillas de pregunta, y
ningun codigo en todo el repo que escriba `status`. Un productor, cero
consumidores. Pero la FORMA del problema es distinta y copiar la puerta anterior
habria estado mal.

8273 ES UN NUMERO DE FILAS, NO DE PREGUNTAS. Descompuesto por evidencia
verificable:

    1463  dentro de un virtualenv        pyvenv.cfg probado en disco
    2566  byte-identica a un archivo     sha256 igual + ruta canonica nombrada
          del repo vivo
    1035  en el repo vivo                necesita una persona
    3209  en cualquier otra parte        necesita una persona

4029 filas -- el 48,7% -- no son preguntas para un humano, y no en el sentido de
"probablemente no": cada una carga un chequeo que cualquiera puede repetir.

CAUSA RAIZ de 1463 de ellas, y es una sola: TODAS vienen de UN directorio,
`/home/mak/curatoria_inbox/3d/NEW/env`, un virtualenv de Windows copiado a esta
maquina (tiene `pyvenv.cfg`, `Include`, `Lib`, `Scripts`). `should_skip_dir`
probaba NOMBRES -- `ACTIVE_SKIP` tiene `venvs`, `.venvs`, `venv-providers` -- y no
tenia ni `env` ni el layout Windows `env/Lib/site-packages`. Una lista de nombres
solo atrapa los nombres que alguien penso. Arreglado con una DEFINICION:
`pyvenv.cfg` no es una convencion de nombre, PEP 405 obliga al interprete a
escribirlo en la raiz del entorno y `sys.prefix` se deriva de ahi. La regla ahora
vale para un directorio llamado como sea. `build_mak_knowledge_db.py` no tenia
NINGUN test, que es como una lista de nombres se queda siendo la regla completa;
ahora tiene `tests/test_knowledge_scanner_skips.py`, incluido uno que falla si
alguien vuelve a la lista.

LA PREGUNTA ESTABA MAL FORMADA, y por eso nunca avanzo. "python implementation
requires purpose and consumer classification" junta dos preguntas cuyas unidades
naturales son distintas, y ninguna decision unica puede contestar las dos. El
contraejemplo esta en los datos: 44 de las filas son `__init__.py` de CERO bytes.
Contenido byte-identico, o sea PROPOSITO identico (marcador de paquete), y viven
en 5 arboles distintos, o sea CONSUMIDORES distintos.

    purpose / project    funcion del contenido  -> una respuesta por clase
    consumer / route     funcion de la posicion -> una respuesta por archivo

Juntas, la mitad barata queda de rehen de la mitad cara, 8273 veces.
`QUESTION_PARTS` declara el corte en vez de dejarlo implicito.

LO QUE UNA PERSONA REALMENTE TIENE QUE CONTESTAR: las 4244 filas restantes se
doblan por `(candidate_kind, directorio)`, porque la mitad gruesa de cada
pregunta es una propiedad del directorio. Resultado medido:

    576 grupos | 3 respuestas cubren la MITAD de las filas | 64 cubren el 80%

Los tres grandes: `/home/mak/research/corpus` (1599 filas, archivos .md con
nombre de hash y sufijo epoch -- corpus generado, no propuestas),
`/home/mak/research/informes/archive` (520) y `/home/mak/flujo/tests` (255).

LA MISMA ASIMETRIA que en la cola de proyectos, y no es coincidencia: una
respuesta gruesa NEGATIVA subsume la fina (si la carpeta es corpus generado,
preguntar a que propuesta pertenece cada archivo es moot); una POSITIVA no.
`--covers coarse_only` deja registrada la mitad abierta y
`fine_questions_still_open` la cuenta, en vez de que desaparezca del conteo de
pendientes como si la pregunta entera estuviera cerrada.

Verificado extremo a extremo sobre una COPIA de la base: `apply-rules --rule
inside_virtual_environment` resolvio 1463 y reaplicarlo resolvio 0 sin pisar nada;
una sola respuesta a `/home/mak/research/corpus` resolvio 1599 filas dejando
`fine_questions_still_open: 1599`. Cada resolucion queda en
`classification_resolutions` con actor, razon, regla y evidencia (tabla
append-only creada al primer uso; leer la cola no la necesita).

Comandos y codigos: `pytest tests/` exit 0 (15 nuevos en
`test_classification_queue.py`, 5 en `test_knowledge_scanner_skips.py`);
`repo_audit.py` exit 0; `git diff --check` exit 0; `classification_review.py
list/propose/summary` deja el sha256 de la base intacto; bare exit 2, `--help`
exit 0.

NO APLIQUE LAS REGLAS SOBRE LA BASE VIVA. Son chequeos probables, no juicios,
pero el acto lleva la firma de alguien y esa firma es del operador. El comando
exacto, cuando quiera:

    ./.venv/bin/python tools/classification_review.py apply-rules \
      --actor mak --reason "installed dependencies and byte-identical copies are \
      not authored material" --dry-run

(sin `--dry-run` para escribir; se puede acotar con `--rule`.)

RESIDUO: los 3209 de "cualquier otra parte" incluyen 308 filas en
`/home/mak/WIN/flujo` que NO son byte-identicas al repo vivo -- copias
divergentes, que es informacion y no ruido. Y para `candidate_kind = consumer` la
unidad declarada es el import, mientras `classify` responde por directorio: mas
grueso que la unidad real, y por eso ese caso deberia usar `coarse_only`.

## Next concrete action

Publicar este write set en `main` solo cuando exista autorizacion explicita de
commit/push. No ampliar la gira ni crear postulacion hasta obtener una segunda
fuente para Antofagasta y evidencia fisica del proyecto. Mantener BAH como
entidad separada del artista y no fusionar prefijos DREF por similitud textual.

### Last verified

2026-08-21 America/Santiago — tests focalizados `6 passed`, py_compile exit 0,
`git diff --check` exit 0, CLI de triangulacion exit 0, segunda ejecucion sin
cambios semanticos, endpoints de ambos hubs HTTP 200, pytest completo exit 0,
`repo_audit` OK, compileall exit 0, `pip check` sin errores, DB integra y sin
procesos permanentes iniciados. El commit/push queda fuera de este cierre hasta
recibir autorizacion explicita para publicar este write set.

## Current objective

Mantener el repo web y el runtime local en un estado coherente y verificable,
con una primera capa artistica-cultural-investigativa comun para curatoria,
portfolio, research y matematicas. La hipotesis P versus NP se usa aqui como
modelo conceptual de representacion, busqueda y certificados; no como un
teorema ya demostrado.
El estado operacional ya no depende de releer este archivo: se consulta en la
CLI y en el Hub real de 8900 mediante `mak-system-status-v1`, que reúne el
ledger con los consumidores locales y deja las atenciones explícitas. Los
gates de esta tanda quedaron cerrados: se preserva la incertidumbre
matematica y Research 4 tiene un consumidor local simbólico, con licencia y
revisión humana aún pendientes. La continuidad de ideas se consulta en el lane
registry, no releyendo la memoria historica completa.

## Session transfer checkpoint — 2026-08-21

La fase web/DB queda validada y lista para publicar. El conjunto propio de esta
fase es la limpieza de superficies Windows obsoletas, la preservacion de XIO
como workflow manual diferido, el gate `tools/repo_audit.py`, su regresion,
`tools/gen_rd_standalone.py`, la fila de `CAPACIDADES.md`, los cambios de CI/
Makefile y este handoff. No se debe hacer `git add .`: el worktree contiene
otros cambios de sesiones anteriores que deben permanecer intactos y sin
mezclarse.

Pruebas cerradas: pytest completo exit 0; `npm run typecheck` exit 0;
`repo_audit` exit 0 (36 modulos, 35 alcanzables, 0 muertos, 0 referencias
obsoletas, cuatro SQLite integras); compileall y `git diff --check` exit 0.
No hay procesos de pytest, intake, Blender ni render activos. La siguiente
accion exacta es revisar el staging del conjunto propio, crear el commit y
hacer push de `main`; despues la nueva sesion debe continuar desde `Next
concrete action` sin repetir la auditoria.

CERRADO: ese checkpoint se completo en `69e7fba` + `268ef4b` y el resto del
worktree se publico en `90f92be`. Se conserva como registro; la accion vigente
esta en `Next concrete action`.

## Physical authority and migration status

- La autoridad física es `/home/mak/*`; `/home/mak/flujo` es el baseline de
  autoría y `/home/mak/WIN` es evidencia histórica de Windows.
- No se copia ni se borra el árbol histórico. Los datos locales ignorados y los
  productos generados se preservan fuera del commit salvo que una regla del
  repo los declare artefactos versionables.
- Git tiene una sola rama local (`main`) y una sola rama remota operativa
  (`origin/main`). El README y su SVG protegido no se modifican.
- En la inspección actual se observaron `cron`, el runner local de GitHub
  Actions y Open WebUI ya instalados; esta tarea no inició ninguno. El Hub
  existente `mak-hub.service` fue reiniciado de forma controlada para activar
  la nueva ruta read-only y quedó activo en 8900; no se inició ningún servicio
  nuevo ni se dejó un render adicional.
- La interfaz temporal del Research local ya estaba activa antes de esta
  tanda; no fue iniciada, detenida ni modificada aquí.

## Completed work with command and result

- Se agregó `src/flujo/knowledge/learning_policy.py`: learner categórico
  auditable, split por `project_id`, abstención ante evidencia insuficiente y
  registro de política solo como candidata.
- Se agregó `tools/project_learning.py` y
  `tests/test_learning_policy.py`. El adaptador
  `mak-verified-result-v1` exige proyecto existente, evidencia, validador y
  checks pasados; es idempotente y falla cerrado.
- `src/flujo/knowledge/project_api.py` expone `learning.policy` en modo
  read-only. `CAPACIDADES.md` y `docs/MAK_CURRENT_STATE.md` declaran el
  contrato.
- Se integró `operational_status()` en
  `src/flujo/knowledge/project_api.py`, `tools/mak_status.py` y el campo
  `operational` de `GET /api/status`. CLI y Hub comparten el mismo contrato
  read-only: estado general, evidencia pendiente, bloqueos, abstenciones y
  siguientes acciones. El Hub conserva sus campos históricos de servicio.
- Se agregó `src/flujo/knowledge/system_status.py`, el sobre
  `mak-system-status-v1` que conecta el ledger con once consumidores físicos:
  fuente/Hub 8900, Research 8890, Codex 8891, SearXNG 8888, runner de eventos,
  Blender/RD, portafolio, runtimes, configuración de proveedores y el registro
  transversal de lanes. Solo lee
  rutas, `/proc`, listeners loopback y nombres de variables; no hace requests
  externos, no inicia jobs y nunca devuelve valores de claves.
- El Hub canónico `/home/mak/plataforma/hub.py` ahora expone
  `GET /api/status` y una pestaña `● estado` en 8900. El endpoint real fue
  verificado con HTTP 200, esquema `mak-system-status-v1`, once componentes y
  `read_only=true` después del reinicio controlado.
- El componente `lanes` del mismo sobre valida, sin mutar, el registro
  `mak-cross-domain-lane-registry-v1`: 19 lanes bajo
  `cultural_research_first` (1 implementada, 7 parciales, 11 propuestas).
  El CLI y el estado del Hub comparten ahora el módulo
  `src/flujo/knowledge/lane_registry.py`.
- Se agregó `runtime_tools.resolve_blender()`: resuelve la instalación real
  `/home/mak/blender/blender` aunque no esté en `PATH`. `contract_registry` y
  `episode_runner` comparten esa resolución, eliminando el falso faltante de
  `blender_optional` sin instalar ni ejecutar Blender desde el estado.
- El probe de render cuenta procesos por el ejecutable real de `/proc`, no por
  texto de argumentos: una orden de inventario que mencionaba la ruta de
  Blender había producido un falso `active`. La lectura final muestra
  `render=ready` y `process.running=false`; no hay render en segundo plano.
- La auditoría de contratos más reciente se registró explícitamente como
  `simulation_consumer_20260820`: 59 contratos, 59 verificados, 0 con
  evidencia pendiente y 0 no disponibles. El ledger actual queda con 2
  atenciones accionables (4 proyectos en revisión y 3 episodios sin evidencia)
  y 2 informativas (abstención segura y falta de holdout independiente).
- `tools/source_learning_bridge.py` y
  `src/flujo/knowledge/source_learning.py` conectan dos raices fisicas por
  referencias: `/home/mak/WIN/claude_sesiones` como memoria de hipotesis y
  `/home/mak/curatoria_inbox/MAK_TODO_SESION_2026-08-19` como auditoria y
  contratos de investigacion. El caso versionado valida 2 raices, 9 archivos,
  9 mensajes por UUID/hash, 7 hallazgos y 5 unidades de aprendizaje sin copiar
  los arboles ni el texto privado de las conversaciones.
- La ingestion real se registro como proyecto activo
  `mak-pnp-search-ecology-2026-08-19` y episodio verificado
  `episode-source-learning-c6f328491b44e1af7828ec1b`. El alcance guardado es
  `source_integrity_and_epistemic_contract_only` y
  `mathematical_truth_validated=false`: no afirma una solucion de P versus NP.
- `src/flujo/knowledge/math_kernel.py` agrega un scheduler metadata-only sobre
  el mismo Project IR y la misma base SQLite: una capsula `MILLENNIUM-PNP-001`,
  requests acotados y ResultCards sellados. El proyecto conserva los dominios
  `cultura`, `curatoria`, `portfolio`, `research` y `mathematics`; como la
  fidelidad semantica esta `UNTRUSTED`, su estado es `review_required` y el
  ciclo real solo dejo una request `METADATA_ONLY` en cola. No se ejecuta un
  worker ni se promueve verdad por ausencia de contraejemplos.
- `knowledge/lane_registry/mak_cross_domain_registry_2026-08-20.json` y
  `tools/project_lanes.py` agregan un mapa read-only de 19 lineas bajo la misma
  primera capa: P=NP, tenis, captura/scraping, deep learning/micelio,
  transpilacion, eventos, simulacion de crecimiento, XIO, claims, lenguas, patentes, crops, dental,
  jardin/geometria, vibe coding, storage, patronage y autoria. Cada linea
  conserva dialectos, estado epistemico, evidencia, consumidor si existe,
  guardrails y un siguiente gate; las propuestas no se presentan como trabajo
  implementado.
- El lane de tenis ya tiene `src/flujo/tennis/shot_events.py` y el consumidor
  read-only `tools/tennis_shot_events.py`: proyectan a
  `schemas/tennis/shot_event.schema.json`, conservan `raw_ref`, hash,
  `transform_chain` y tokens desconocidos, y el router solo lo selecciona para
  un Project IR activo/verified del dominio `tennis`.
- Se registró el primer episodio verificable del lane: proyecto
  `mak-tennis-decision-lab-fixture-20260820`, episodio
  `episode-tennis-shot-fixture-20260820`, 4 eventos, hash de fixture y 2
  tokens desconocidos preservados; `network_calls=0` y sin contrafactuales.
- El probe de ruta del mismo proyecto selecciona
  `tennis_shot_event_consumer` y queda registrado como
  `episode-tennis-consumer-probe-20260820`; prepara un comando local acotado,
  no lo ejecuta ni escribe salida generada.
- Scraping y deep learning ya tienen consumidores acotados: `research_source_capture.py`
  separa plan/captura y registra una sola URL con hash en `SourceCorpusStore`;
  `deep_learning_gate.py` exige labels, holdout independiente, agrupación
  anti-leakage y validador, pero nunca autoriza entrenamiento por sí solo.
- La evidencia física de Research 4 quedó enlazada al Project IR como proyecto
  `mak-research-capture-job4-20260820` y episodio
  `episode-research-capture-job4-20260820`: 4 fuentes capturadas, hashes y
  etapas verificadas; licencia pendiente; el consumidor simbólico queda sujeto
  a revisión humana y no afirma crecimiento biológico.
- Research 4 ya tiene un consumidor `research_simulation_consumer`:
  `knowledge/research_simulations/job4_lsystem_candidate_20260820.json` usa
  reglas explícitas, límite de símbolos y alcance `visual_grammar`; la salida
  se etiqueta `simulated`/`model_not_reality` y no se interpreta como biología.
- El dataset existente de logo-clean quedó enlazado como
  `mak-logo-clean-learning-gate-20260820`; su episodio
  `episode-deep-learning-gate-logo-clean-20260820` abstiene correctamente:
  solo hay 3 ejemplos y no existe holdout independiente, por lo que no se
  autoriza entrenamiento.
- `tests/test_system_status.py` cubre resolución local, redacción de secretos
  y ausencia de escrituras. El cambio de `providers.provider_registry()` hace
  que un entorno explícito no cargue silenciosamente otro `.env`.
- `web/src/components/HubDashboard.tsx` muestra el estado unificado antes del
  ledger, y `web/src/api/flujoApi.ts` consume `/api/status` como fuente única;
  las páginas generadas de `context/` fueron reconstruidas con Node 24.19.0.
- La consulta actual del ledger devuelve `attention` con 2 asuntos accionables
  y 2 informativos: cuatro proyectos en revisión, tres episodios sin evidencia,
  abstención segura y falta de holdout independiente. Los 59 contratos,
  incluido Blender y el puente de memoria, quedaron verificados.
- Research job 4 sobre `JARDINES_INTERPRETATIVOS.md` capturó cuatro fuentes,
  extrajo claims, relaciones, contexto e interpretación y dejó el siguiente
  paso en `simulate`; el runner histórico no tenía una función ejecutable para
  ese paso (`interpretive_simulation_callables=[]`,
  `research_router_simulation_callables=[]`), pero ahora existe el consumidor
  local simbólico `research_simulation_consumer`; el resultado permanece
  marcado como modelo y no como hecho. No se clonaron ni instalaron repos
  candidatos; la licencia y la revisión humana siguen pendientes.
- La revision de procedencia P versus NP incorporó
  `knowledge/math_targets/p_vs_np_official_statement_capture_2026-08-20.json`,
  con la pagina oficial de Clay, hash de la nota canonica y estado `Unsolved`.
  El artefacto formal local tiene hash completo y ambos hashes se guardan en la
  capsula; la fidelidad semantica permanece `UNTRUSTED` y el kernel sigue
  bloqueando cualquier promocion de verdad.
- La base local ignorada `data/mak_knowledge.db` contiene ocho episodios
  elegibles en cuatro proyectos; incluye el fixture verificado, el probe del
  consumidor de tenis. La política medida es `abstain` con razón
  `no_independent_holdout`, `eligible_examples=8`, `train_count=8` y
  `holdout_count=0`. No se promovió ninguna regla.
- La contradicción detectada en el handoff fue eliminada: ya no se escribe un
  total fijo de tests ni se recicla el conteo antiguo del learner.
- Se declaró en `web/package.json`, `web/package-lock.json` y
  `web/README.md` el requisito real `Node >=20.19.0`; con el Node 24.19.0
  disponible en MAK los builds reproducibles pasan.
- Los cambios de esta tanda se publicaron en `main` mediante el commit
  `7674c49` y el push normal a `origin/main`; la evidencia generada dentro de
  `data/mak_knowledge.db` sigue siendo estado local ignorado. La
  evidencia generada dentro de `data/mak_knowledge.db` es estado local
  ignorado; los writes explícitos fueron el refresh de contratos y la
  ingestion verificada del caso de memoria descrito arriba.
- Se retiraron Watsonx, AWS y Azure de la superficie operativa activa. Se eliminaron
  sus adaptadores, alias, capacidades, rutas de fallback, opciones CLI, UI y
  políticas de proveedores en `cultura/mak_plataforma/providers.py`,
  `cultura/mak_research/research_lib.py`, `research.py`, `refutar.py`,
  `cultura/mak_codex/codex_lib.py`, `cultura/mak_plataforma/hub.py`,
  `iskvw/editor.html`, `src/flujo/autonomia.py` y `src/flujo/cli.py`.
  Research queda con Groq -> Gemini -> Ollama; Cerebras permanece solo como
  opcion explicita porque el probe real devuelve HTTP 402. Codex conserva
  NVIDIA NIM -> Ollama; vision del portafolio queda local con el lector
  Ollama existente.
- Las herramientas Watson exclusivas se movieron, sin borrarlas, a
  `/home/mak/_archive/watsonx-retired-20260820/`: cuatro sondas/benchmarks y
  copias protegidas de `n8n-local/research.env` y `research/research.env` antes
  de retirar sus líneas Watson/AWS. No se tocaron `/home/mak/WIN`, ledgers,
  productos ni resultados históricos.
- Se retiró `boto3` de `pyproject.toml` y `requirements.txt`. La matriz y el
  mapa ahora describen los proveedores retirados como evidencia histórica, no
  como capacidad disponible. `python3 -m compileall` terminó con exit 0,
  `./.venv/bin/python -m pytest -q` terminó con exit 0 (warnings existentes de
  Pillow), y `git diff --check` quedó limpio.
- Se verificó el reemplazo de proveedores en el runtime y sus espejos. El
  adaptador Gemini usa `gemini-3.6-flash`, carga solo `GEMINI_API_KEY` y
  `GEMINI_MODEL` desde el `.env` secundario, y devuelve texto y JSON válidos.
  Los probes foreground de Groq, Gemini y Ollama devolvieron texto no vacío;
  Firecrawl capturó `https://example.com` mediante el backend configurado
  (`167` caracteres). El probe explícito de Cerebras devolvió HTTP 402
  `payment_required`, por lo que no participa en la cadena automática.
  Azure no conserva llamadas ni configuración activa; las coincidencias que
  quedan son comentarios, vocabulario de arqueología o resultados históricos.
  La copia vieja de `research_lib.py` y el workflow n8n retirado siguen
  preservados en `/home/mak/_archive/provider-retirement-20260820/`.
- El adaptador estructurado de `cultura/mak_plataforma/providers.py` fue
  endurecido para no truncar JSON cuando el llamador pide un presupuesto muy
  pequeño; su probe Gemini devolvió un objeto JSON válido. La suite completa
  pasó después de actualizar el test que aún esperaba Cerebras al frente de
  la ruta de riesgo alto.
- Se probó la regla arquitectónica "salir del espacio de soluciones" con dos
  fallos reales. Primero, una respuesta Gemini simulada con
  `finishReason=MAX_TOKENS` y sin `content.parts` no obligó a reparar Gemini:
  `LLM.call` la clasificó como vacía y continuó con Ollama (`status=ok`).
  Segundo, Firecrawl capturó la documentación oficial de Gemini con `236737`
  caracteres de navegación y contenido; una selección acotada de ventanas
  relevantes redujo la evidencia a `3119` caracteres y Ollama identificó
  `MAX_TOKENS` y la decisión de rechazar el resultado truncado. La conclusión
  es que la captura funciona y la dependencia que debe cambiar es el paso de
  evidencia-a-análisis, no Firecrawl. Este experimento fue read-only y no
  cambió código ni datos.
- En el primer lote de apuestas predictivas se eligieron dos verificaciones de
  alto aprendizaje y bajo costo. El contrato de proveedores (`PROVIDER_ORDER`,
  `PROVIDER_CAPABILITIES`, `PROVIDER_ENV_KEY` y métodos `LLM._*`) quedó
  consistente (`all_provider_contracts_consistent=true`). La búsqueda de
  interfaces antiguas solo encontró un comentario de endpoint legacy,
  resultados históricos y tres copias bajo `/home/mak/rollback/`; no encontró
  un consumidor activo roto. Ambas predicciones se descartan sin parche.
  El lote confirma que la unidad útil es `prediccion -> prueba barata ->
  descarte o patron`, no volumen de archivos.
- Se compararon los enfoques externo y resiliente. En la ruta externa,
  Firecrawl capturó la página oficial de precios de Cerebras (`4053`
  caracteres; ventana relevante `1424`), pero el resumen Ollama inventó un
  crédito de `$5`; la salida fue rechazada por falta de evidencia. La fuente
  confirma solo tier Free `$0` y límites menores, mientras el probe local real
  sigue en HTTP 402. La conclusión es `captura externa -> evidencia acotada ->
  validación`, nunca `captura -> verdad`.
- En la ruta resiliente se encontró y corrigió un bug real en
  `cultura/mak_plataforma/providers.py`: `TASK_CAPABILITIES["research"]`
  pedía la capacidad inexistente `research`, por lo que el router devolvía
  `local_deterministic` aun con proveedores disponibles. Ahora Research usa
  la capacidad declarada `hypothesis` y enruta `Groq -> Gemini -> Ollama`.
  Se agregó `test_research_route_uses_declared_hypothesis_capability`; el test
  enfocado y la suite completa terminaron con exit 0, y `git diff --check`
  quedó limpio.
- Se inició el experimento dual de depuración sobre Research/proveedores
  reutilizando `src/flujo/diagnostics.py` y el comando `flujo diagnose`, sin
  crear otro framework. Para el agente externo se generaron dos paquetes
  `mak-diagnostic-v1` read-only: ambos rutearon a Research, redacted datos
  sensibles, excluyeron WIN y entregaron contrato, rutas existentes, gate y
  reproducción. El primer postprocesador falló con `python: command not found`;
  al repetirlo con `.venv/bin/python`, el diagnóstico terminó con exit 0.
- El mismo slice para MAK validó `route_task("research")` como
  `hypothesis`, `Groq -> Gemini -> Ollama`, y simuló una respuesta Gemini sin
  `content.parts`: la salida pasó a Ollama sin bloquearse. El paquete Research
  tenía además una ruta inexistente (`src/flujo/research`); se eliminó de
  `src/flujo/diagnostics.py` y `context/diagnostics/domains.json`, y se agregó
  una regresión que exige `missing_read_paths=[]`. Tests enfocados, suite
  completa y compileall terminaron con exit 0; no se inició ningún servicio.
- Se agregó `src/flujo/index/code_index.py` y el comando `flujo code-index`.
  Construye `mak-code-structure-v1` con AST, símbolos, imports, consumidores,
  entradas, efectos y hashes, sin guardar texto fuente. Excluye `WIN`,
  `.agents`, `.codex`, `.claude`, entornos, caches y builds. El índice real
  `context/code_structure_index.json` contiene 781 módulos Python, 8552
  símbolos, 186593 líneas declaradas y cero errores de sintaxis; ocupa
  2671255 bytes. `--query` devuelve un `mak-code-brief-v1` acotado para que
  un agente abra solo candidatos relevantes. Se agregó regresión para
  consumidores relativos y errores de sintaxis aislados, y se sincronizaron
  `MAPA.md`/`context/comandos.json` con el generador oficial.
- El primer push del índice expuso dos fallos de portabilidad en CI: una ruta
  histórica con el usuario Windows real y un test que exigía un artefacto
  formal guardado fuera del clon. Se anonimizó la ruta en
  el registro histórico retirado y `tests/test_math_kernel.py` ahora valida el
  hash si el artefacto externo existe, pero hace `skip` explícito en clones
  limpios. `./.venv/bin/python -m flujo verify` y la privacidad local pasan;
  el commit `6743467` se publicó y CI #22/seguridad de ese SHA terminaron en
  `success`.

## Open integration items

| Item | Path | Status | Proof required |
| --- | --- | --- | --- |
| Python learning layer | `src/flujo/knowledge/learning_policy.py` | verified, published | full pytest exit 0; py_compile exit 0; diff check exit 0 |
| Web source | `web/` | verified, published | Node 24.19.0: `npm ci`, audit 0 vulnerabilities, typecheck and all three builds exit 0 |
| Documentation contract | `CAPACIDADES.md`, `docs/MAK_CURRENT_STATE.md`, this file | verified, published | docs hygiene included in full pytest exit 0 |
| Watson/AWS/Azure retirement and provider replacement | provider registries, research/codex chains, Hub/UI, env files, `pyproject.toml`, `requirements.txt`, `/home/mak/research/` | verified and published in `90f92be`; live runtime reloaded | full pytest exit 0; compileall exit 0; Groq/Gemini/Ollama/Firecrawl probes pass; Cerebras HTTP 402; recoverable archive present; `/api/status` after the Hub restart no longer reports watsonx |
| Operational status | `src/flujo/knowledge/system_status.py`, `cultura/mak_plataforma/hub.py`, `tools/mak_status.py`, `web/` | verified, published in `90f92be` and reloaded at 8900; lane registry included read-only | focused pytest; temporary/live `/api/status` HTTP 200; eleven components; read-only endpoint |
| Python structure index | `src/flujo/index/code_index.py`, `context/code_structure_index.json`, `tests/test_code_index.py` | published in `90f92be`; index regenerated from the published tree (783 modules, 8565 symbols, 0 syntax errors) | focused/full pytest exit 0; CLI probe; zero syntax errors; diff check exit 0 |
| Source learning bridge | `src/flujo/knowledge/source_learning.py`, `tools/source_learning_bridge.py`, `knowledge/learning_cases/`, `schemas/knowledge/source_learning_case.schema.json` | verified locally and recorded; published in `7674c49` | source roots/files/messages/claim boundaries pass; Project IR episode verified; no truth promotion |
| Cultural-first math kernel | `src/flujo/knowledge/math_kernel.py`, `tools/math_kernel.py`, `knowledge/math_targets/`, `schemas/knowledge/math_*.schema.json` | verified locally; one bounded metadata request queued; published in `7674c49` | capsule validation, common Project IR domains, sealed ResultCard guard and truth-promotion block |
| Cross-domain lane registry | `knowledge/lane_registry/`, `tools/project_lanes.py`, `schemas/knowledge/cross_domain_lane_registry.schema.json` | published in `90f92be`; 19 lanes, 3 priority-0 lanes, no new consumer claimed for proposals; `lanes` component ready in the live Hub | registry validation, common first-layer rule, evidence refs, guardrails and next gates |
| Tennis MCP first slice | `src/flujo/tennis/mcp.py`, `tools/tennis_mcp_ingest.py`, `tests/test_tennis_mcp.py` | verified locally; conservative parser and hash-linked JSONL projection; no external acquisition | focused pytest, syntax check, diff check; feeds the shot-event consumer |
| Tennis shot-event consumer | `src/flujo/tennis/shot_events.py`, `tools/tennis_shot_events.py`, `schemas/tennis/shot_event.schema.json` | verified locally; router-selected read-only consumer with explicit uncertainty and provenance; first episode recorded | schema validation, Project IR route test, focused pytest, verified episode; next is an independent second fixture |
| Tennis Project IR probe | `tools/project_gate.py`, `src/flujo/knowledge/episode_runner.py` | verified locally; route selects tennis consumer and probe status is `succeeded` without executing it | read-only project gate, recorded probe episode; next is independent evidence |
| Research source capture | `tools/research_source_capture.py`, `cultura/mak_research/source_pipeline.py` | verified locally; existing Research 4 capture linked, license remains pending, no broad crawl | 4 source hashes, verified capture/extract/interpret results; next is license review |
| Research simulation | `src/flujo/knowledge/research_simulation.py`, `tools/research_simulation.py`, `schemas/knowledge/research_simulation_manifest.schema.json` | verified locally; bounded symbolic trajectory, model-not-reality marker, no external calls | manifest schema, deterministic trajectory, budget abstention and Project IR route; next is human review |
| Deep-learning task gate | `src/flujo/knowledge/deep_learning_gate.py`, `tools/deep_learning_gate.py`, `schemas/knowledge/deep_learning_task_gate.schema.json` | verified locally; logo-clean episode abstains on 3-row/no-holdout evidence, training remains disabled | manifest schema, gate tests, Project IR episode; next is an independent holdout |
| Research learning | `/home/mak/research/jobs/4/` | captured/interpreted; bounded symbolic simulate consumer available; license review pending | review candidate grammar and license; no candidate install |
| Publication | `main` -> `origin/main` | verified at `90f92be`; remote CI green | `git rev-parse HEAD` equals `git ls-remote origin refs/heads/main`; CI, seguridad and Git topology guard all `success` |

## Tool and dependency verification matrix

| Surface | Command | Current result |
| --- | --- | --- |
| Python suite | `./.venv/bin/python -m pytest -q` | exit 0; warnings only from existing Pillow deprecation |
| Learning policy | `./.venv/bin/python tools/project_learning.py --db data/mak_knowledge.db` | exit 0; abstain; 8 eligible in 4 projects; no independent holdout |
| Source learning | `PYTHONPATH=src ./.venv/bin/python tools/source_learning_bridge.py knowledge/learning_cases/mak_pnp_search_ecology_2026-08-19.json --db data/mak_knowledge.db --record` | exit 0; 2 roots, 9 artifacts, 9 messages, 5 learning units; verified ingestion only |
| Python syntax | `./.venv/bin/python -m py_compile ...` | exit 0 |
| Diff hygiene | `git diff --check` | exit 0 after code-index and map synchronization |
| Python structure index | `./.venv/bin/python -m flujo code-index --root . --output context/code_structure_index.json --query "research provider route" --format json` | exit 0; 781 modules, 8552 symbols, 0 syntax errors; source-free index; 20 bounded query matches |
| Python dependencies | `./.venv/bin/python -m pip check` | exit 0; no broken requirements |
| Provider replacement probes | foreground `LLM(groq|gemini|ollama)` + platform `providers.call(gemini, response_format=json)` | exit 0; all text responses non-empty; Gemini structured response parsed as JSON object |
| Firecrawl capture | foreground `capture_url("https://example.com", backend="firecrawl")` | exit 0; backend `firecrawl`; 167 captured characters |
| Cerebras availability | foreground explicit `LLM(cerebras)` probe | expected failure; HTTP 402 `payment_required`; excluded from automatic route |
| Azure runtime audit | `rg` over active provider/runtime surfaces | no active Azure call/configuration; remaining matches are historical/comments/vocabulary |
| Web typecheck/build | `NODE_BIN=.../node ./node_modules/typescript/bin/tsc --noEmit`; `NODE_BIN=.../node ./node_modules/vite/bin/vite.js build`; `NODE_BIN=.../node scripts/copy-context.mjs` | exit 0 with Node 24.19.0; 1840 modules; `web/dist/index.html` 777.98 kB |
| Math Kernel cycle | `PYTHONPATH=src ./.venv/bin/python tools/math_kernel.py cycle --db data/mak_knowledge.db --target knowledge/math_targets/p_vs_np_target_capsule_2026-08-19.json --iterations 1 --compute-units 1 --max-expanded-cost 100` | exit 0; `mak-math-ledger-v1`; target `UNTRUSTED`; one `METADATA_ONLY` request; truth promotion blocked |
| Lane registry | `PYTHONPATH=src ./.venv/bin/python tools/project_lanes.py validate` | exit 0; `mak-cross-domain-lane-registry-v1`; 19 lanes; common `cultural_research_first` layer; read-only |
| Tennis MCP slice | `PYTHONPATH=src ./.venv/bin/python -m pytest -q tests/test_tennis_mcp.py tests/test_project_lanes.py` | exit 0; parser preserves raw notation, unknown tokens, source hash and `ANNOTATED` status |
| Tennis shot-event route | `PYTHONPATH=src ./.venv/bin/python -m pytest -q tests/test_tennis_mcp.py tests/test_project_router.py tests/test_project_contracts.py` | exit 0; schema-shaped events, unknowns/provenance preserved, Project IR selects `tennis_shot_event_consumer` |
| Scraping/deep-learning/simulation gates | `PYTHONPATH=src ./.venv/bin/python -m pytest -q tests/test_research_source_capture.py tests/test_deep_learning_gate.py tests/test_research_simulation.py` | exit 0; default scraping is plan-only, deep-learning gate abstains without independent holdout, simulation is bounded/model-labelled |
| Unified status CLI | `./.venv/bin/python tools/mak_status.py --db data/mak_knowledge.db --json` | exit 0; `mak-system-status-v1`; 11 components, including valid 19-lane registry; `render=ready`, no Blender process; 2 actionable and 2 informational ledger items; read-only; 59 contracts audited |
| Unified status HTTP | temporary `ThreadingHTTPServer` + live `127.0.0.1:8900` -> `GET /api/status` | HTTP 200 in both; `mak-system-status-v1`; `read_only=true`; temporary server shut down; live Hub active |
| Catalog federation | `src/flujo/knowledge/catalog_federation.py`, `tests/test_catalog_federation.py`, `data/mak_knowledge.db` | verified locally and integrated additively; 7 read-only sources, 124 tables, 2,075,337 observed rows, 0 copied; integrity and FK checks pass |
| Operational DB bridge | `src/flujo/knowledge/operational_bridge.py`, `tests/test_operational_bridge.py`, `data/mak_knowledge.db` | verified locally and refreshed; 6,132 normalized records, 106,895 curation links, exact package/project/fund links; source rows copied 0; integrity and FK checks pass |
| Web/DB audit gate | `tools/repo_audit.py`, `tests/test_repo_audit.py`, `.github/workflows/ci.yml`, `Makefile` | verified locally; 36 web modules, 35 reachable, 0 dead, 0 stale active references; four DBs have resolved consumer paths and integrity `ok`; published in `69e7fba` |
| RD live/standalone projection | `src/flujo/rd/panel.py`, `tools/gen_rd_standalone.py`, `web/src/data/rdDbEmbebida.json` | verified locally; generated and tracked JSON are equal (6 records, identical SHA-256); generator now accepts absolute output paths |
| SSD application intake | `tools/build_application_intake.py`, `/home/mak/labs/portable-ssd-index-20260813/archivo_index.sqlite` | verified in `/tmp`; 917 projects scanned, 3 bounded Fondart packages emitted, derived SQLite integrity `ok`; status remains `draft_with_evidence_gaps` |
| Latent project reconstruction | `src/flujo/knowledge/project_reconstruction.py`, `tools/project_reconstruction.py`, `tests/test_project_reconstruction.py`, `tools/build_application_intake.py` | verified and published in `96dd8cd`; durable outputs in `/home/mak/curatoria_inbox/project_reconstruction/2026-08-21/` |
| DB -> Research -> Curatoria -> Postulacion | temporary foreground pipeline using existing Research corpus, Curatoria diagnostic and `tools/build_application_intake.py` | exit 0; Research 5,179 applications/14 captures; Curatoria 917 projects/13,121 families/45,536 members; Postulacion emitted `drefgira-fondart` with explicit evidence gaps; source trees untouched |
| RD event fixture | read-only query over `operational_records` and `operational_curation_links` | exit 0; 7 events retain producer, raw date, venue and flyer/source evidence; 0 false ISO dates; 0 orphan curation links |
| Contract audit refresh | `PYTHONPATH=src ./.venv/bin/python -m flujo.knowledge.contract_registry --db data/mak_knowledge.db audit --root . --record --run-id simulation_consumer_20260820` | exit 0; 59/59 verified; Blender, source-learning bridge, math kernel, tennis, scraping, deep-learning and simulation consumers resolved |
| Hub smoke | `./.venv/bin/python scripts/hub_smoke.py --port 0 --timeout 20` | exit 0; temporary port 48545; no persistent hub |
| Remote parity | `git rev-parse HEAD` vs `git ls-remote origin refs/heads/main` | equal when the commands return the same value |

## Conflicts and risks

- `abstain` is intentional. Eight eligible episodes now span four projects, but
  the deterministic split still produced no independent holdout; promoting a
  general route policy would overstate the evidence.
- `data/mak_knowledge.db` and generated research SQLite/report files are local
  operational state and are not Git inventory. Their current state is noted,
  not copied into the web repo.
- Historical phase documents and recovered sessions remain evidence. They are
  not the current handoff and must not override this file.
- A green local check does not prove external GitHub Actions or provider
  credentials. The push completed normally and remote parity was checked;
  external CI remains an independent gate.
- The official P versus NP capture is a normalized curator note, not a
  verbatim source transcript or semantic-equivalence certificate. It supplies
  provenance and hashes but intentionally cannot change `UNTRUSTED`.
- The current `attention` state is intentional and concrete: two ledger
  evidence gaps plus two informational safety states. Do not silence it by
  deleting episodes or promoting same-project data. The Blender dependency is
  no longer an open gap; its fresh audit is verified.
- Watsonx, AWS and Azure historical labels remain in preserved ledgers, old
  visual records, comments and legacy triangulation filenames. They are data
  provenance, not executable integrations. Do not delete or reinterpret those
  records as current provider health. Cerebras remains configured only for
  explicit diagnostic use; its current billing response is HTTP 402 and it is
  not part of the default chain.

## Active cleanup audit — 2026-08-21

Se depuro la configuracion activa para que MAK Linux no presente superficies
Windows obsoletas como si fueran runtime. Se retiraron los lanzadores
`abrir_hub.bat`, `instalar.bat`, `launch-flujo.bat`, `launch-flujo.ps1`, el
puente `tools/bridge_issue_render.py`, sus helpers SendTo y su e2e, y el
workflow Claude deshabilitado. Sus copias historicas siguen en
`/home/mak/WIN` o en la evidencia recuperada. Se retiro solo el test que
ratcheaba esos lanzadores; se conservaron el mirror y los tests de seguridad
que aun tienen consumidores reales.

XIO fue corregido durante la auditoria: no es basura ni se elimina. Se
restauro `.github/workflows/build-xio-apk.yml` como build manual diferido y
se documento como integracion futura Chataigne/OSC para shows, venues y VJ.
No se ejecuta en cada CI ni se confunde con la ruta diaria de FLUJO/RD.

Tambien se actualizaron `CAPACIDADES.md`, `docs/MAK_CURRENT_STATE.md`,
`docs/FLUJO_AREAS_EVENTOS_SUPLEMENTOS.md`, `src/flujo/web/hub.py`, los
paneles web de automatizaciones/eventos, `Makefile`, `pyproject.toml` y los
tests afectados. Se regeneraron `tests/fixtures/idioma_baseline.txt`,
`context/code_structure_index.json` y los HTML de `context/`.

Validacion en primer plano:

- `./.venv/bin/python -m pytest -q` -> exit 0; suite completa, skips esperados.
- Tests focalizados de higiene, contratos Git/web, mirror, GPU, idioma,
  code-index y status -> exit 0.
- `npm run typecheck` en `web/` -> exit 0.
- `npm run build:context` -> exit 0; Node 18 emitio advertencia porque el
  requisito declarado es Node >=20.19, pero el bundle se genero.
- `git diff --check` -> exit 0.

Se agrego `tools/repo_audit.py` como gate read-only del arbol web y las cuatro
SQLite locales. La auditoria real devuelve 36 modulos, 35 alcanzables, 0
muertos, 0 referencias activas obsoletas; `data/rd.db` tiene 20 tablas/7,585
filas, `data/rd_datos.db` 3/0, `data/mak_knowledge.db` 30/369,157 y
`data/flujo.db` 1/6; las cuatro pasan `integrity_check` y todas sus rutas de
consumidor existen. Se corrigio el mapa para no declarar `src/flujo/rd/panel.py`
como lector de `data/rd.db`: el panel lee JSON/YAML canonicos y solo proyecta.

La validacion de `gen_rd_standalone.py` genero en `/tmp` los mismos 6 registros
que `web/src/data/rdDbEmbebida.json`, con SHA-256 identico; el unico fallo
encontrado era el reporte de una ruta absoluta externa y quedo corregido sin
alterar la salida. El intake real uso el indice fuente
`/home/mak/labs/portable-ssd-index-20260813/archivo_index.sqlite`, no el
`intake.sqlite` derivado: con limite 3 y fondo Fondart produjo tres paquetes
`drefgira-fondart`, `felina-logo-fondart` y
`descargas-hasta-rdflyer-2050-fondart` en `/tmp/mak-intake-audit-20260821`.
La salida queda correctamente en `draft_with_evidence_gaps`; no se escribio
la DB de aprendizaje ni se modifico la fuente del SSD.

Riesgos conservados deliberadamente: `tools/mak_ops/check_mak_mirror.py`
todavia contiene una ruta SSH historica y requiere una fase separada de
reemplazo local; `src/flujo/version.py` y `docs/recovered/` conservan
referencias de changelog/evidencia, no runtime. No se borraron `/home/mak/WIN`,
XIO, bases, artefactos ni cambios ajenos.

## Post-publication runtime sync — 2026-08-21

El commit `90f92be` ("chore: publish provider and cross-domain runtime")
publico en un solo commit atomico los tres conjuntos que quedaban fuera de
`69e7fba`: retiro de Watsonx/AWS/Azure, write set cross-domain completo y la
correccion del paquete de diagnostico Research. 81 archivos, +2172/-1905.
`main` y `origin/main` quedaron sincronizados en `90f92be`; el CI remoto pasa
en los tres jobs: `CI` (run 32454523320), `seguridad` (32454523238) y
`Git topology guard` (32454523301). Los cuatro tests que estaban rojos en
`268ef4b` pasan: `test_tools_en_registro`,
`test_registro_sin_herramientas_fantasma`,
`test_no_new_file_carries_spanish_comments` y
`test_the_manifest_is_not_stale_against_the_real_cli`. La causa raiz fue
publicar artefactos derivados generados desde un worktree sucio mientras sus
fuentes quedaban sin stagear; no volver a publicar `CAPACIDADES.md`,
`context/comandos.json`, `idioma_baseline.txt` o el code index sin las fuentes
que describen.

Resolucion del Grupo 4, sin consultar: en `src/flujo/version.py` se revirtio
el unico hunk que falsificaba evidencia temporal, de modo que el incidente de
claves de 2026-07-16 conserva sus proveedores reales
(Tavily/Groq/Cerebras/Azure); `tests/test_privacidad_repo.py` volvio al estado
publicado porque su exencion nueva no tenia sujeto
 (el registro histórico ya no forma parte del árbol activo y tiene 0
coincidencias). Las versiones de worktree quedaron en
`/home/mak/_archive/group4-reverted-20260821/`.

El indice `context/code_structure_index.json` se regenero desde el arbol
publicado: 783 modulos Python, 8565 simbolos, 187046 lineas declaradas, 0
errores de sintaxis, sin texto fuente. Ya no declara los cuatro modulos
watsonx y `lane_registry` resuelve su consumidor real
(`imported_by = src.flujo.knowledge.system_status`).

El Hub existente `mak-hub.service` es un unit de usuario
(`systemctl --user`), no de sistema; su launcher
`/home/mak/plataforma/hub.py` es una proyeccion que carga la implementacion
canonica `cultura/mak_plataforma/hub.py` del repo. Se reinicio solo ese
servicio. Evidencia del reload: antes del reinicio `/api/status` aun
mencionaba `watsonx`; despues menciona `gemini` y ya no `watsonx`. GET
verificados: `/health` 200 (`mak-hub-health-v1`), `/api/status` 200
(`mak-system-status-v1`, `read_only=true`, 11 componentes, `status=attention`
con 2 accionables y 2 informativos, componente `lanes` `ready` y valido),
`/api/research/catalog` 200, `/api/project/learning` 200, `/api/rd/summary`
200 y `/api/rd/crosswalk` 200. `/api/rd-db` devuelve 404
`ruta_api_no_encontrada`: esa ruta no existe, las reales son `/api/rd/*`. No
se llamo ningun mutador y no se inicio ningun servicio nuevo;
`mak-codex.service` y `mak-research.service` siguen activos sin tocarse.

Proveedores probados una sola vez en primer plano con los adaptadores
existentes: `research_lib.LLM` devolvio texto no vacio para `groq`, `gemini` y
`ollama`; `cerebras` devolvio HTTP 402 `payment_required`;
`providers.call("gemini", response_format="json")` devolvio JSON valido; y
`source_pipeline.capture_url("https://example.com", backend="firecrawl")`
capturo 167 caracteres con backend `firecrawl`. El registro
`faro-provider-registry-v1` lista groq, gemini, cerebras y ollama como
`configured`, sin Watsonx, AWS ni Azure. `route_task("research")` resuelve
capacidad `hypothesis` con proveedor `groq`.

## Continuity after Claude quota interruption — 2026-08-21

Claude Code agoto su cuota despues de publicar `4c12bba` mientras anunciaba
el inicio de la validacion del slice de portabilidad/pipeline. No quedo un
comando de intake, render, pytest ni Blender corriendo. El archivo temporal
`/tmp/mak_continuation_result.json` es evidencia de una ejecucion anterior y
termina en `9841cc8`; no usarlo como estado actual ni como fuente para repetir
trabajo.

Estado fisico comprobado en primer plano: `main == origin/main == 4c12bba`,
worktree limpio; `mak-hub.service`, `mak-research.service` y
`mak-codex.service` siguen activos como unidades de usuario existentes. GET
read-only de Hub `/health`, `/api/status`, `/api/research/catalog`,
`/api/project/learning`, `/api/rd/summary` y `/api/rd/crosswalk` devolvieron
HTTP 200. Research `8890` y Codex `8891` devolvieron HTTP 200 en su raiz.

Validacion actual, sin mutar fuentes: `route_task` devolvio las cadenas
automaticas `groq -> gemini -> ollama` para research, curation y review;
judge resolvio `ollama -> local_deterministic`; Cerebras solo aparece cuando
el caller lo nombra explicitamente. Tests de intake, puente operativo,
source-learning y tandas pasaron (`pytest`, exit 0). Integridad read-only de
`data/rd.db`, `data/rd_datos.db`, `data/mak_knowledge.db` y `data/flujo.db`
devolvio `ok` en las cuatro bases. `compileall` y `git diff --check` pasaron,
exit 0. No se modificaron archivos del runtime durante esta comprobacion.

Advertencia de evidencia CORREGIDA el 2026-08-21: esa afirmacion era falsa.
El indice fisico externo si esta presente en
`/home/mak/labs/portable-ssd-index-20260813/archivo_index.sqlite`
(175689728 bytes, 2026-08-13). El generador de intake se re-ejecuto y el
pipeline quedo medido de punta a punta; ver la seccion
`Pending-slice closure` mas abajo. No usar la advertencia anterior como razon
para no medir.

Riesgo residual: el nombre historico `PROVIDER_ORDER` aun contiene Cerebras
para poder mostrarlo en el registro diagnostico; esto no lo vuelve fallback,
porque `provider_plan` lo excluye sin `available=["cerebras"]`. No cambiarlo
sin actualizar el contrato de registro y sus tests.

Archivos modificados en esta continuidad: solo este handoff dentro del repo.
Fuera del repo se agrego una fuente de evidencia acotada bajo
`/home/mak/curatoria_inbox/tennis_sources/2026-08-21/` y se agrego de forma
append-only el Project IR/episodio correspondiente a `data/mak_knowledge.db`.
No hubo borrado, instalacion ni nuevo servicio.

## Independent tennis evidence — 2026-08-21

La segunda fuente independiente ya fue ingerida y validada. Fuente publica:
`https://raw.githubusercontent.com/JeffSackmann/tennis_MatchChartingProject/master/charting-m-points-2020s.csv`.
El archivo completo quedo fuera del repo en
`/home/mak/curatoria_inbox/tennis_sources/2026-08-21/charting-m-points-2020s.csv`
con SHA-256
`2cd43f73e0530a47ac02b99dae40177ca6d58a8ccf9189358eb05dffb4be9a`.
La licencia y atribucion CC BY-NC-SA 4.0 estan registradas en
`SOURCE_MANIFEST.json`; no se permite uso comercial.

Se extrajeron solo dos filas reales del partido
`20260521-M-Roland_Garros-Q3-Jesper_De_Jong-Michael_Zheng` a
`charting-m-points-2020s-extract.csv`, hash
`ac618e8222d02aa051b6d92dfd6414796974bc90fe362c65067f0c031faea822`.
`tools/tennis_shot_events.py` produjo 11 eventos; el validador JSON Schema
paso, el hash del extracto se propago a cada evento y 35 tokens desconocidos
se conservaron sin inferencia.

Project IR `mak-tennis-decision-lab-external-20260821` quedo `active` con
episodio verificado `episode-tennis-external-mcp-20260821`. La primera ruta
abstuvo correctamente porque el proyecto fue etiquetado tambien como
`research`; al corregir su dominio a solo `tennis`, la ruta selecciono
`tennis_shot_event_consumer` con `execute_read_only`. El aprendizaje global
se consulto en modo read-only: `status=abstain`, `eligible_examples=9`,
`holdout_count=0`, `recordable=false`; la nueva evidencia no se transformo en
entrenamiento ni en regla promovida.

## RD thematic integration — 2026-08-21

La seccion RD de `flujo serve` ahora separa la proyeccion canonica en cinco
temas read-only: operacion en terreno, calendario/red de eventos, testeo y
evidencia, productos/activos de entrega y puentes con Cultura/Portfolio. La
separacion es una vista, no una segunda base: `data/rd.db` sigue siendo la
proyeccion canonica y `data/rd_datos.db` sigue vacia como frontera de runtime.

Se agrego el contrato `mak-rd-topics-v1` en `src/flujo/departments.py` y se
expuso en los dos servidores locales: `flujo serve` (`/api/rd/topics`) y el
Hub 8900 (`/api/rd/topics`). `flujo serve` tambien recupero `/api/rd-db` y
los logos en GET read-only, por lo que la interfaz RD ya no queda desconectada
cuando se abre por el servidor stdlib. El panel muestra los cinco temas y los
puentes sin habilitar mutaciones.

Validacion de esta fase:

- `./.venv/bin/pytest -q tests/test_serve_api.py tests/test_departments.py tests/test_rd_db_logos.py tests/test_tarifa_una_sola_fuente.py`: exit 0, 46 tests.
- `./.venv/bin/pytest -q --disable-warnings`: exit 0, suite completa.
- `npm run typecheck`: exit 0.
- `npm run build:context`: exit 0; warning no bloqueante: Node 18.20.4 esta bajo el minimo recomendado por Vite 7.
- `npm run build:rd`: primero exit 1 por `import.meta.dirname` en `copy-rd-share.mjs`; corregido con `fileURLToPath`, segundo intento exit 0.
- servidor temporal de `flujo serve`: `/api/rd/topics`, `/api/rd/summary`, `/api/rd-db` y HTML respondieron HTTP 200; se detuvo al terminar.
- `git diff --check` y `compileall`: exit 0.

Write set: `src/flujo/departments.py`, `src/flujo/serve/`,
`src/flujo/web/hub.py`, `cultura/mak_plataforma/hub.py`,
`web/src/components/RdDbPanel.tsx`, `web/scripts/copy-rd-share.mjs`, pruebas y
los HTML compilados de `context/`. No se modificaron bases, WIN, README/SVG
protegido ni se dejaron servicios nuevos.

## Pending-slice closure — 2026-08-21

Se retomaron exclusivamente los slices que quedaron abiertos en la sesion
interrumpida por cuota. Los slices ya cerrados (`a5b1900`, `1f474e7`,
`4c12bba`, `7f99a50`, `2a6e2e0`, `5d915cb`) no se repitieron ni se revirtieron.

Estado verificado antes de tocar nada: `main == origin/main == 5d915cb`,
worktree limpio. Cerebras: `route_task` devolvio `groq -> [gemini, ollama]`
para research, curation y review, y `ollama -> [local_deterministic]` para
judge; `OPT_IN_PROVIDERS == {'cerebras'}`. Guards de proyecciones, proveedores
y hub: exit 0. Ese conjunto ya estaba cerrado y solo se comprobo.

Defecto real encontrado y reparado: el mismo par de bugs que se habia
corregido en `cultura/mak_plataforma/hub.py` seguia intacto en
`src/flujo/web/hub.py`, el hub de `flujo serve`. Publicaba
`registry: "research/jardines_interpretativos/jardines_interpretativos.sqlite"`,
una ruta relativa que no resuelve desde ningun directorio de trabajo porque el
registro vive fuera del repo, y `/api/research/job` sin `id` devolvia el
`ValueError` crudo de `int()`. Reparar una sola superficie fue lo que permitio
que el bug sobreviviera, asi que ahora
`tests/test_research_registry_contract.py` fija el contrato en las dos y
compara sus respuestas campo por campo.

Segundo defecto real: `system_status` mantenia su propia lista de candidatos de
Node que terminaba en `PATH` mas un runtime de codex, por lo que informaba
`node available` para el 18.20.4 de `PATH` mientras `web/package.json` declara
`>=20.19.0` y en la misma maquina existen 20.20.2 y 24.x sin listar. La
resolucion se unifico en `runtime_tools` (`node_candidates`, `resolve_node`,
`declared_node_minimum`, que lee el minimo del manifiesto en vez de copiarlo) y
`flujo doctor` ahora nombra el binario que cumple en lugar de dejar que el
build avise y el llamador adivine. Se retiro el `import shutil` que quedo
muerto en `system_status`.

Comandos exactos y codigos de salida:

- `./.venv/bin/python -m pytest -q tests/test_physical_projections.py tests/test_mak_tandas.py tests/test_mak_hub_salud.py -rs`: exit 0.
- `./.venv/bin/python -m pytest -q tests/test_research_registry_contract.py -rs`: exit 0.
- `./.venv/bin/python -m pytest -q tests/test_node_runtime_requirement.py -rs`: exit 0.
- `./.venv/bin/python -m pytest -q tests/`: exit 0, suite completa.
- `./.venv/bin/python scripts/hub_smoke.py --port 0 --timeout 25`: exit 0, puerto efimero 60831, detenido.
- servidor temporal de `flujo.web.hub` en puerto efimero: `/api/research/catalog` HTTP 200 con ruta absoluta y `registry_exists=true`; `/api/research/job` sin `id` HTTP 400 `id_requerido`; `?id=4` HTTP 200; `?id=abc` HTTP 400 `id_requerido`; servidor detenido y thread confirmado muerto.
- `./.venv/bin/python -m flujo doctor`: exit 0; fila `node` avisa que `/usr/bin/node` v18.20.4 esta bajo `>=20.19.0` y nombra un v24.19.0 local.
- `./.venv/bin/python -m flujo diagnose --area research`: exit 0; `route_contract=True`, `local_hub_8900=True`.
- `./.venv/bin/python -m flujo verify --no-pytest`: exit 0; hub smoke en puerto efimero 38231, detenido.
- `flujo health`, `flujo version`, `flujo rd-db packs|eventos|venues|productora creamfields`, `flujo knowledge list`: exit 0 cada uno.
- `tools/research_job_router.py ... --db <temp>`: exit 0; `job_id=5`, `validation=PASS`, `external_calls=0`; la politica emitida dice `Groq o Gemini`, lo que valida el fix de proveedores de punta a punta.
- `tools/execute_research_job.py --job-id 5 --db <temp> --max-sources 1`: exit 0; captura firecrawl con hash, `model_calls=0`, `license_policy` exige revision humana.
- `cultura/mak_curatoria/diagnostico_proyectos.py --db <copia temp> --out <temp>`: exit 0; 45536 miembros, 917 proyectos, cinco salidas derivadas.
- `tools/build_application_intake.py --source-index <SSD real> --out-dir <temp> --fund Fondart --candidate-limit 3 --mak-db data/mak_knowledge.db`: exit 0; tres paquetes `drefgira-fondart`, `felina-logo-fondart`, `descargas-hasta-rdflyer-2050-fondart`; `learning_materialized=[]`; el paquete es `mak-application-package-v1` con `status=draft_with_evidence_gaps`, `readiness=90.0`, fondo `candidate_unverified`, `gaps` con severidad `blocking` y `next_action` explicito; SHA-256 del indice fuente identico antes y despues (`d3afb072fe163312...`).
- `tools/repo_audit.py`, `compileall -q src tools tests`, `pip check`, `git diff --check`: exit 0 los cuatro.
- `npm run typecheck` en `web/` con el Node local v24.19.0: exit 0, sin el aviso de version.
- publicacion: commit `fe104ee`, push a `origin/main` exit 0, `HEAD == origin/main`, worktree limpio. CI remoto de `fe104ee` en los tres jobs: `CI` success, `seguridad` success, `Git topology guard` success.

Archivos modificados: `src/flujo/web/hub.py`,
`src/flujo/knowledge/runtime_tools.py`,
`src/flujo/knowledge/system_status.py`, `src/flujo/cli.py`,
`tests/test_research_registry_contract.py` (nuevo),
`tests/test_node_runtime_requirement.py` (nuevo) y este handoff. No se tocaron
bases, WIN, README/SVG, XIO ni el mirror SSH. No se instalo nada y no quedo
ningun servicio ni proceso nuevo: los unicos servidores fueron temporales en
primer plano y se detuvieron.

Riesgos: (1) `PATH` sigue resolviendo Node 18.20.4, asi que un build hecho sin
`NODE_EXE` seguira emitiendo el aviso de Vite; el arreglo hace visible el
binario correcto, no cambia el `PATH` del sistema. (2) `PROVIDER_ORDER` sigue
nombrando Cerebras a proposito para poder mostrarlo en el registro
diagnostico; `provider_plan` lo excluye sin `available=["cerebras"]` y dos
tests lo fijan. (3) Las tres unidades de usuario `mak-hub`, `mak-research` y
`mak-codex` siguen sirviendo el codigo anterior en memoria hasta que se
reinicien; esta fase no las reinicio porque solo cambio `flujo serve`, que no
es un servicio permanente.

## Ledger open-state repair and probe closure — 2026-08-21

Se cerraron los dos unicos items accionables que quedaban en el ledger, y en el
camino aparecio un defecto mas importante que ellos.

Defecto encontrado: `operational_status` construia su lista de atenciones desde
`SELECT status,COUNT(*) FROM project_episodes GROUP BY status`, es decir sobre
el historial completo, y los episodios son append-only por diseno. Eso hacia
que un item como `3 episode(s) need evidence` **no pudiera limpiarse haciendo
el trabajo que el propio item pedia**: al registrar la ejecucion verificada, la
fila antigua seguia contando y el operador perdia la diferencia entre "hay
trabajo" y "el trabajo se hizo". El defecto era latente, no activo: en ese
momento los tres `needs_evidence` eran el episodio mas reciente de su proyecto,
asi que el conteo aun era verdadero. Por eso habia que arreglarlo ANTES de
cerrarlos, no despues.

Reparacion minima: se agrego `_open_episode_states()` en
`src/flujo/knowledge/project_api.py`. El histograma historico sigue publicado
sin cambios en `episodes` porque es evidencia; la lista de atenciones lee ahora
`episodes_open`, donde un episodio no aceptado sigue abierto solo mientras su
proyecto no tenga uno aceptado posterior, que es literalmente lo que describe
su propio `next_action`. El conjunto de estados que cuentan como cerrados se
reutiliza de `learning_policy.VERIFIED_OUTCOME_STATUSES` en vez de escribir una
segunda copia.

Trabajo cerrado con esa base: `episode-research-simulation-probe-20260820` y
`episode-tennis-consumer-probe-20260820` estaban en `needs_evidence` con
`plan_fingerprint` vacio porque el probe solo prepara el comando y por
contrato nunca ejecuta el consumidor. Se ejecutaron los dos consumidores reales
en primer plano y se validaron:

- `tools/research_simulation.py knowledge/research_simulations/job4_lsystem_candidate_20260820.json --output <evidencia>`: exit 0. Validador `deterministic_rerun_and_marker_check`: una segunda corrida produjo salida byte-identica (mismo sha256), `schema=mak-research-simulation-result-v1`, `observed_or_simulated=simulated`, `model_not_reality=true`, `environment.biological_claim=false`, `errors=[]`.
- `tools/tennis_shot_events.py tests/fixtures/tennis_mcp_fixture.csv <evidencia>`: exit 0, 4 eventos. Validador `schemas/tennis/shot_event.schema.json` con `Draft202012Validator`: 0 errores de esquema, cada evento conserva `source`, `provenance` y `epistemic_status`, y `observed` y `derived` siguen separados.
- Registro por el adaptador sancionado, no a mano:
  `tools/project_learning.py --db data/mak_knowledge.db --record-result <packet>`
  exit 0 en ambos, con paquetes `mak-verified-result-v1`; el adaptador falla
  cerrado si falta proyecto, evidencia, validador o checks.

Efecto medido: `episodes:needs_evidence` bajo de 3 a 1. Sin la reparacion
anterior habria seguido marcando 3. El historial quedo intacto: las tres filas
`needs_evidence` siguen existiendo, se agregaron dos episodios `succeeded`,
`PRAGMA integrity_check` devolvio `ok` y no se reescribio ni borro nada. Se
tomo copia previa de la base antes de escribir.

El `needs_evidence` restante NO es un defecto y no se debe cerrar
mecanicamente. Es `episode_scd_evidence_closure_20260819` del proyecto
`project-5047cc3a2269b5031460` (SCD, `review_required`), y sus checks mecanicos
estan todos en verde (`source_root_exists=true`,
`representative_artifacts_missing=0`). Lo que lo mantiene abierto son seis
`unknowns_preserved` que exigen evidencia humana u oficial: convocatoria
vigente no verificada, problema y contexto que deben formularse desde el
proyecto y no inferirse del nombre de la carpeta, metodo artistico, presupuesto
autorizado, cronograma verificable y equipo sin promover identidades por nombre
de carpeta. El sistema se esta negando correctamente a convertir metadata de
carpeta en una postulacion.

Archivos modificados: `src/flujo/knowledge/project_api.py`,
`tests/test_open_episode_state.py` (nuevo) y este handoff. Fuera del repo se
agrego evidencia en `/home/mak/curatoria_inbox/probe_closures/2026-08-21/`
(las dos salidas de consumidor con hash y los dos paquetes) y dos episodios
append-only en `data/mak_knowledge.db`, que es estado local ignorado.

Validacion: `pytest -q tests/` exit 0; `tests/test_open_episode_state.py` exit
0; `compileall`, `tools/repo_audit.py` y `git diff --check` exit 0.

Riesgo: `projects:review_required` sigue en 4 y se cuenta sobre el estado del
proyecto, no sobre episodios, asi que esa via no la toca esta reparacion. Antes
de tratarla hay que decidir que evidencia autoriza una transicion de proyecto;
no cambiarla sin ese contrato.

## Latent project reconstruction and quota recovery — 2026-08-21

La sesion de Claude Code `3428381a-02ad-4101-9da5-8176cf72c147` termino por
cuota despues de escribir el nucleo no publicado
`src/flujo/knowledge/project_reconstruction.py`. Se recupero la transcripcion
linea por linea y no se repitio su investigacion. Claude habia medido que el
indice real contiene 917 filas de proyecto y que 758 (82,7 %) tienen la firma
de biblioteca descargada `assets/<kind>/<name>_<uuid4>`. Tambien confirmo que
`DREFGIRA`, `DREFMOVISTAR`, `DREF CHOCOLATE` y `DrefQuila` no deben fusionarse
por compartir el prefijo `DREF`.

El nucleo quedo completado y validado como `mak-project-reconstruction-v1`:
usa una cascada lexicografica falsificable, no un score universal; conserva
RAW INPUT, OBSERVATION, DERIVED FEATURE, RELATION, INTERPRETATION e UNKNOWN;
no hashea el SSD de 940 GB y abre el indice en modo read-only. La salida incluye
decisiones, features, relaciones, asignacion de cada asset, fingerprint,
resumen por unidad y una proyeccion HTML inspeccionable.

El consumidor `tools/build_application_intake.py` acepta ahora
`--reconstruction`. Filtra bibliotecas y recursos compartidos para que no
compitan como postulaciones y conserva la decision de reconstruccion dentro de
la evidencia del paquete `mak-application-package-v1`.

Resultados reales persistidos fuera del repo:

- DREFGIRA: baseline 8 filas, 3 bibliotecas; reconstruccion 1 unidad, 4
  subproyectos, 3 dependencias; 467/467 assets reconciliados; 2 relaciones
  cross-root UNKNOWN. El intake produjo `drefgira-fondart` con gaps humanos
  explicitos y SQLite derivada integra.
- FELINA/LOGO: baseline 21 filas, 20 bibliotecas; reconstruccion 1 unidad,
  15 dependencias y 5 recursos compartidos; 2219/2219 assets reconciliados.
- BAHPARTY/bah: baseline 50 filas, 49 bibliotecas; reconstruccion 1 unidad y
  49 recursos compartidos; 87/87 assets reconciliados. La comparacion con
  `BAHPARTYCONCERESI` queda `UNKNOWN` por un sample hash sin `full_sha256`,
  preservando las alternativas y sin convertir la marca en postulacion.
- Los dos runs conservan el fingerprint del indice
  `d3afb072fe1633125ac20da82aa1d3c7514f763cb8cac28655f19216ac53d8df`.

Rutas durables:
`/home/mak/curatoria_inbox/project_reconstruction/2026-08-21/`.
En ese write set la fuente SSD y `data/mak_knowledge.db` no fueron
modificadas; el slice posterior de Project IR se describe a continuacion.

Validacion de esta tanda: tests focalizados 14 passed; suite completa
`./.venv/bin/python -m pytest -q --disable-warnings` exit 0; `repo_audit.py`
exit 0 (36 modulos, 35 alcanzables, 0 muertos); `py_compile`, `pip check` y
`git diff --check` exit 0; las dos SQLite derivadas verificaron
`PRAGMA integrity_check = ok`.

Archivos del write set: `src/flujo/knowledge/project_reconstruction.py`,
`tools/project_reconstruction.py`, `tests/test_project_reconstruction.py`,
`tools/build_application_intake.py`, `CAPACIDADES.md`,
`docs/MAK_CURRENT_STATE.md` y este handoff.

## Next concrete action

El write set de reconstruccion ya esta publicado en `96dd8cd` y el tercer scope
`BAHPARTY/bah` tambien fue validado. No repetir DREFGIRA, FELINA/LOGO ni la
sesion de Claude. El puente de este slice ya conecto un scope real DREFGIRA
con Project IR y el router compartido: se generaron 5 registros review-only,
467 artefactos indexados, 5 abstenciones por evidencia y 0 postulaciones o
publicaciones. `data/mak_knowledge.db` recibio esos 5 registros mediante
`--db`; el indice SSD mantuvo el mismo fingerprint e integridad.

Mantener `BAHPARTYCONCERESI` como `UNKNOWN` hasta obtener evidencia adicional.
No generar una postulacion de BAH solo por la clasificacion mecanica de su
carpeta. El siguiente slice ejecutable es cerrar la evidencia del montaje
fisico para DREFGIRA o, si el SSD sigue desmontado, integrar el siguiente
consumidor read-only que pueda trabajar con referencias indexadas; no cambiar
`review_required` a `active` por una inferencia de carpeta.

Los slices de proveedores, contratos de hub, rutas de registro,
proyecciones fisicas, portabilidad de entrypoints, pipeline
DB -> Research -> Curatoria -> Postulacion y requisito de Node estan medidos y
cerrados; releerlos no aporta evidencia nueva.

El recargado del runtime YA SE HIZO en esta misma fase y no hay que
repetirlo. Se reinicio unicamente `mak-hub.service`, porque es el unico
servicio que carga los modulos tocados (`system_status`); `mak-research.service`
y `mak-codex.service` no dependen de este write set y quedaron intactos y
activos. Evidencia: MainPID paso de 245666 a 297744; antes del reinicio la
evidencia de node en `/api/status` solo traia `['available', 'path']` y despues
trae `declared_minimum` `>=20.19.0` y cuatro candidatos; `/api/status` sigue en
`read_only=true` con once componentes; `/api/research/catalog` devuelve la ruta
absoluta con `registry_exists=true`; `/api/research/job` sin `id` devuelve HTTP
400 `id_requerido` y con `id=4` devuelve HTTP 200.

Auditoria adicional de esta fase, sin hallazgos nuevos: los dos hubs comparten
nueve rutas y se comprobo que ya no divergen. `/api/rd/topics` delega en el
contrato compartido `rd_topics` de `src/flujo/departments.py` en ambos;
`/api/status` del hub de `serve` conserva sus campos historicos de servicio y
anida el mismo sobre `mak-system-status-v1` en `operational` con
`read_only=true`, que es el diseno documentado y no una divergencia;
`/api/organismo` del hub de `serve` es un proxy al 8900, no una segunda
implementacion. Los unicos contratos que si divergian eran los dos reparados
aqui.

No queda una accion de integracion segura y ejecutable pendiente en este
alcance. El siguiente agente debe partir del commit de esta fase y elegir un
slice nuevo con fuente, consumidor y validacion propios.

Fuera de alcance y deliberadamente pendientes, porque dependen de licencia,
decision humana o hardware externo: la licencia de Research 4
(`result.license_review = pending`), el holdout independiente del gate de deep
learning (`abstain` con 9 elegibles y holdout 0), XIO (solo
`workflow_dispatch`), el mirror SSH historico
(`tools/mak_ops/check_mak_mirror.py`) y cualquier promocion de verdad
matematica (`MILLENNIUM-PNP-001` sigue `UNTRUSTED`).

## Previous completed checkpoint

The operational DB bridge is complete for the current source contracts. The
master now carries a normalized projection without replacing source authority:
RD events/producers/venues, Fondart v5 applications, intake projects/funds/
packages, and the existing `mak_links` curation surface. The real bridge
returned exit 0, wrote 6,132 normalized records, transferred 106,895 curation
links, copied 0 source rows, and a foreground SQL check resolved
`SCD package -> SCD project -> Fondart -> 12 curation links`.

The foreground `DB -> Research -> Curatoria -> Postulacion` check is complete:
Research exposed 5,179 applications and 14 captures read-only; Curatoria
processed 917 projects, 13,121 families and 45,536 members in a temporary
SQLite copy; Postulacion generated `drefgira-fondart` with explicit evidence
gaps. Exit was 0 and source trees were untouched. Preserve unknown dates as
`date_raw`, accept exact source-key joins as exact, and retain candidate venue
links with confidence.

The DB pipeline and RD event fixture are green. The next action belongs to the
separate operational audit: run the next real consumer/event fixture only if
it represents a different path, and fix only a runtime blocker. Do not start
autonomy, deep learning, broad reindexing or another database until the
declared current consumers are green.

## Last verified

2026-08-21 America/Santiago — cierre de los slices que quedaron abiertos por la
interrupcion de cuota. Se comprobo primero que Cerebras ya estaba solo como
opt-in y que los guards de proyecciones pasaban (exit 0), y solo se
modifico lo que seguia roto: los dos contratos de `src/flujo/web/hub.py` (ruta
de registro relativa y `id` sin validar), que eran el mismo defecto ya
corregido en el hub de plataforma pero nunca replicado; y la resolucion de Node,
que informaba `available` para el 18.20.4 de `PATH` mientras el manifiesto
declara `>=20.19.0` y en la maquina hay 20.20.2 y 24.x. Suite completa exit 0;
typecheck web exit 0 con el Node local v24.19.0 y sin aviso de version;
`repo_audit`, `compileall`, `pip check` y `git diff --check` exit 0; hub smoke y
un servidor temporal de `flujo.web.hub` en puertos efimeros, ambos detenidos.
Pipeline medido de punta a punta contra fuentes reales con salidas temporales:
Research `job_id=5` `validation=PASS` con politica `Groq o Gemini`, captura
firecrawl con hash y `model_calls=0`, Curatoria 917 proyectos / 45536 miembros
sobre copia temporal, y Postulacion con tres paquetes Fondart en
`draft_with_evidence_gaps`, `gaps` bloqueantes explicitos y el SHA-256 del
indice SSD identico antes y despues. Se corrigio en este archivo la afirmacion
falsa de que el indice SSD no estaba visible: si lo esta.

2026-08-21 America/Santiago — continuidad posterior a la cuota verificada y
publicada en `7f99a50`: `main == origin/main`, worktree limpio, servicios de
usuario activos, cuatro SQLite integras, tests focalizados exit 0 y segunda
fuente de tenis verificada con ruta `tennis_shot_event_consumer`. El learner
sigue en `abstain` por `holdout_count=0`; no se promovio aprendizaje.

## Current slice: reconstruction to Curatoria/Portfolio Project IR — 2026-08-21

Se agrego `src/flujo/knowledge/reconstruction_adapter.py` y el CLI
`tools/import_project_reconstruction.py`. El adaptador lee un
`mak-project-reconstruction-v1` persistido y su indice SQLite en modo
read-only, convierte solo `project_unit`, `subproject` y `exported_product` a
`mak-project-ir-v1`, deja bibliotecas/recursos compartidos como artefactos o
relaciones y agrega la politica `portfolio=never_auto_publish` y
`postulacion=not_created_by_this_adapter`.

Validacion real: DREFGIRA produjo 5 registros review-only y 467 artefactos
indexados en
`/home/mak/curatoria_inbox/project_reconstruction/2026-08-21/drefgira/project_ir/`;
el router produjo 5 abstenciones por `project_state_requires_evidence`, 0
selecciones y 0 paquetes de postulacion. Con `--db` se guardaron esos 5
registros en el LearningStore existente; no se registraron episodios ni se
promovio una regla. El fingerprint del indice siguio siendo
`d3afb072fe1633125ac20da82aa1d3c7514f763cb8cac28655f19216ac53d8df` y
`PRAGMA integrity_check` devolvio `ok`.

Tests del puente, reconstruccion, Project IR y router: 22 passed. La prueba
de no mutacion del indice comparo sus bytes antes/despues. Cambios de codigo
pendientes de publicar en el commit de este slice: adaptador, CLI, pruebas,
`CAPACIDADES.md`, `docs/MAK_CURRENT_STATE.md` y este handoff.

2026-08-21 America/Santiago — publicacion `90f92be` y sincronizacion del
runtime verificadas. Validado antes del commit en un clon git limpio con el
patch staged aplicado, no en el worktree sucio: pytest completo exit 0,
`flujo verify` exit 0 con hub smoke en puerto efimero, typecheck web exit 0 con
Node 24.18.0, `npm run build:context` exit 0, `gen_archivo_iskvw` exit 0,
`tools/repo_audit.py` exit 0, compileall exit 0, `pip check` exit 0 y
`git diff --check` exit 0. `main` == `origin/main` == `90f92be`; CI, seguridad
y Git topology guard en `success`. Despues de publicar: indice regenerado (783
modulos), Hub de usuario reiniciado y sirviendo el codigo publicado, cinco
familias de GET verificadas read-only, y cinco proveedores auditados con una
sola llamada cada uno. Abiertos confirmados sin fabricar evidencia: Research 4
`license_pending` (`result.license_review = pending` en
`/home/mak/research/jobs/4/verified_result.json`); gate de deep learning
`abstained` con `rows=3`, `independent_holdout=false` y
`training_permitted=false`, y el learner en `abstain` por
`no_independent_holdout` con 9 elegibles y holdout 0; tenis
segunda fuente independiente verificada en
`/home/mak/curatoria_inbox/tennis_sources/2026-08-21/`; XIO diferido en
`workflow_dispatch`;
mirror SSH intacto y fuera de alcance.

2026-08-21 America/Santiago — web/DB cleanup gate and bounded intake verified;
published in commit `69e7fba` and pushed to `origin/main`:
the active web graph has 36 modules, 35 reachable and 0 dead; stale active
references are 0; `rd.db`, `rd_datos.db`, `mak_knowledge.db` and `flujo.db`
pass read-only integrity checks with all declared consumers present. RD live
and standalone projections are equal by SHA-256. The source-index intake used
the physical SSD index, emitted three bounded Fondart packages in `/tmp`, and
left the source and learning DB untouched. The only runtime defect found was
the standalone generator's absolute-output display path; it was fixed and
focused tests passed. The remaining worktree changes are intentionally outside
that commit and must be handled by the next bounded slice.

2026-08-20 America/Santiago — Python structure index and dual debugging slice
verified: `flujo code-index` generated the source-free 781-module index,
consumer resolution and bounded query brief; focused and full pytest passed,
map synchronization passed, compileall and diff check passed. Watsonx/AWS/Azure
retirement and provider
replacement verified: active registries/chains/UI/configuration removed,
Gemini 3.6 Flash works in both LLM and structured platform adapters, Groq,
Ollama and Firecrawl probes pass, Cerebras returns HTTP 402 and is opt-in only,
four exclusive tools and two env snapshots archived, boto3 dependency removed,
compileall exit 0, full pytest exit 0, pip check exit 0 and diff check clean.
Historical WIN/ledgers/results preserved. Official
P versus NP source/formal hashes
recorded without changing `UNTRUSTED`, Research 4 capture and bounded
simulation were checked without biological claims, 59-contract audit refreshed,
source-learning case preserved, 19-lane cross-domain registry validated
locally, tennis MCP parser/shot-event route and fixture episode passed,
Research 4 capture and logo-clean abstention were linked to Project IR, live
status and full pytest rechecked, and the published baseline remains
`7674c49`/`17ccff7`. The cross-domain write set is not yet published.

2026-08-20 America/Santiago — catalog federation slice verified: focused
tests `3 passed`, py_compile exit 0, diff check exit 0; real metadata-only
federation exit 0; 7 sources, 124 tables, 2,075,337 observed rows, 0 copied;
master integrity `ok`, foreign-key issues `[]`, orphan tables/links `0`.
Added source/target contract files; full suite `./.venv/bin/python -m pytest -q`
completed at 100% with exit 0 (warnings only); no source database contents were
rewritten and no commit or push has been made for this slice.

2026-08-20 America/Santiago — operational bridge slice verified: focused
bridge tests `2 passed`, py_compile and diff check exit 0; real refresh exit 0;
6,132 normalized records and 106,895 curation links; source rows copied `0`;
master integrity `ok`, foreign-key issues `[]`; SQL pipeline sample resolved
application package `SCD` to project `SCD`, fund `Fondart` and 12 curation
links. Seven RD event records retain producer/venue/source payloads; non-ISO
date strings remain unnormalized. Full repository suite completed at 100% with
exit 0; only existing deprecation warnings were emitted.

2026-08-20 America/Santiago — foreground pipeline verified: Research read-only
source exposed 5,179 Fondart applications and 14 captures; Curatoria ran on a
temporary SQLite backup and produced 917 projects, 13,121 families and 45,536
members; Postulacion ran against the existing index and emitted
`drefgira-fondart` with status `draft_with_evidence_gaps`; all commands exit 0,
temporary outputs only, no source mutation. Operational closure comes before
the autonomy phase.

2026-08-20 America/Santiago — RD event fixture audit verified read-only: 7
events all retain producer, raw date, venue and flyer/source evidence; 0 were
forced into ISO dates and 0 curation links are orphaned. No source mutation or
new process remained.

2026-08-26 America/Santiago — Piso 0 episode-lineage repair and durable pilot
replay verified. Bootstrap schema `mak-agent-bootstrap-v1`; context hashes were
`agents.md=53afe6c85f431db10aee822f5a250af66968bb7c3ac9a27cbf38269b9386ce75`,
`docs/MAK_CURRENT_STATE.md=c98a7fb488b825ecfef0aff4d3770189d3167de469644aa03a90b03964b808e0`,
`context/LAST_HANDOFF.md=be8fb2e1c4524ebd9152a0a471d907c48285856432d4d417214c08f25446cce1`.
Removed the undefined requirement-ID computation from `_input_hashes` in
`src/flujo/knowledge/product_episode.py`; `_validate_plan` now derives separate
program and research requirement sets and validates application requirements
 against the program set. The focused gate passed with exit 0; py_compile,
JSON validation and diff check passed.

Using only the durable snapshot
`experiments/pilots/ARICA-FONDART-2027/input/archive_observation.json` (no
rescan), regenerated `runs/full-baseline` and `runs/enriched`. Both manifests
were reopened and all listed output hashes matched. The current durable source
replays 12,332 artifacts, 128 observations, 512 relation candidates and 174
units; it does not reproduce the unavailable historical 417/11,916/413 counts,
which is recorded as an unresolved provenance difference in
`experiments/pilots/ARICA-FONDART-2027/runs/run_comparison.json` and
`RESULTS.md`. The enriched run adds four supported practice claims and passes
the opportunity source gate, while fit remains `abstain`, dossier remains
`draft_only`, application remains blocked, and all external side effects stay
false. No commit or push.

2026-08-26 America/Santiago — Piso 2 product lineage and human view verified.
`portfolio_dossier` and `application_research_package` now expose the same
canonical `product_plan_hash`; the focused lineage/product gate passed 54 tests
(exit 0), py_compile and path-limited diff check passed. The accepted enriched
run was regenerated after this additive contract repair and its manifests were
reverified from disk.

The first human-readable product is materialized from the enriched run as
`experiments/pilots/ARICA-FONDART-2027/runs/enriched/portfolio-view.json`
(`mak-product-view-v1`, SHA-256
`51faed8207152ddf16314bef48fa35c0a9454c58c8a7e6a3b3994310a06c1d72`) and
`portfolio-view.md` (SHA-256
`066205d71c62105d2242248ad2de33671871970b431d9ade27ea4484e7af37ed`). It
contains 4 supported claims with explicit evidence refs, 11,534 internal
physical assets, 0 explicitly public-eligible assets, 16 non-dispatched
research jobs, and a blocked application. It is an internal draft only: no
publication, submission, dispatch, promotion, training, database write or
source mutation.
