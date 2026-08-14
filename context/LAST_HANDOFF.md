# LAST_HANDOFF - Faro

## CURRENT GIT WEB TRANSPORT - 2026-08-13 23:06 LOCAL

The verified MAK scope is now committed and published as a draft pull request.
The Linux physical state remains the authority; Git transports only this
verified scope. No canonical branch was merged, reset, cleaned, deleted, or
otherwise rewritten.

- Proposal branch: `codex/mak-web-restructure-20260813`.
- Runtime reconciliation commit: `dc082c5962c4be5d1cfc2f2fdb06b70771f0ca23`,
  subject `feat(mak): reconcile runtime and Git web`.
- Publication handoff commit: `d11261dc7d6ce09f0b8579747625c9330187e427`,
  subject `docs(hand): record Git web publication`.
- Final bug-hunt commit: `7926d20daeaf9b04d8f624f2b2e68ebfdac87eba`, subject
  `fix(tests): close archived contract gap`.
- Remote ref verification: `git ls-remote origin
  refs/heads/codex/mak-web-restructure-20260813` returned final commit
  `7926d20daeaf9b04d8f624f2b2e68ebfdac87eba`.
- Draft PR: #531,
  `https://github.com/ligereza/vibecodeine/pull/531`, base `main`, head
  `codex/mak-web-restructure-20260813`, head SHA
  `7926d20daeaf9b04d8f624f2b2e68ebfdac87eba` exact.
- GitHub connector creation returned 403; the authenticated `gh` fallback
  created the draft PR successfully. No browser was used.
- `gh pr checks 531 --repo ligereza/vibecodeine` reported no checks for the
  branch at publication time.
- Next action: human review of PR #531; do not merge into `main`, `mak`, `rd`,
  or `iskvw` without explicit review of the verified scope.

## BUG HUNT AND TEST CLOSURE - 2026-08-13 23:18 LOCAL

The only prior suite skip was traced to stale test logic, not a missing runtime
dependency or contract. Commit `1fc8871` intentionally archived
`context/DIRECTOR_CONTRACT.md`; the active repo has no such file and no live
documentation cites its `I1-IN` range. `tests/test_higiene_docs.py` previously
skipped this condition. It now asserts the archive boundary and fails if an
active document resurrects those citations. No historical contract was
restored and no WIN material was imported.

- Full regression command: `PATH=/home/mak/research/.venv/bin:$PATH
  PYTHONPATH=/home/mak/flujo/src:/home/mak/flujo/cultura:/home/mak/flujo/cultura/mak_codex:/home/mak/flujo/cultura/mak_research:/home/mak/flujo/cultura/mak_plataforma
  /home/mak/research/.venv/bin/python -m pytest -q -rs --tb=short`.
- Result: collection previously measured at 2,855 tests; 100% completed,
  exit 0, zero failures, zero skips. Only existing Pillow deprecation
  warnings were emitted.
- Focused hygiene command: `... -m pytest -q -rs --tb=short
  tests/test_higiene_docs.py`; result `3 passed`, zero skips.
- The test change is committed in `7926d20` and pushed to PR #531 after the
  final full-suite measurement.

## CURRENT PHYSICAL MAK HANDOFF - 2026-08-13 FINAL AUDIT (REVALIDATED 22:34)

Authority is the measured Linux body under `/home/mak`. The checkout is
`/home/mak/flujo`, physical audit branch `main`, HEAD
`559fa6075e1cfb7a51be380c6d354d2af90dffb2` at audit time. Git was read only
during that physical audit; the later verified proposal is recorded in the
current Git web transport section above. `/home/mak/WIN`
was used as provenance/evidence only; no WIN file was executed and no Windows
provider, endpoint, command, or library is part of active MAK runtime.

### Inventory and classification

The deterministic inventory command classified every physical file in the
requested roots. The path/extension rules assign each file to exactly one of
`runtime_active`, `shared_code`, `tool`, `candidate`, `generated`, `historical`,
`memory`, `operational_state`, `product`, or `credential`; the explicit
review queue is `candidate`, so unclassified count is zero. Counts:

- `/home/mak/flujo`: 15195 files; candidate 273, credential 3, generated
  12731, historical 10, memory 21, operational_state 22, product 1089,
  runtime_active 14, shared_code 835, tool 197.
- `/home/mak/research`: 17598; candidate 143, credential 2, generated
  14525, historical 1047, operational_state 11, product 1678,
  runtime_active 4, shared_code 188.
- `/home/mak/plataforma`: 5023; candidate 244, credential 3, generated 4035,
  historical 73, memory 2, operational_state 246, product 120,
  runtime_active 5, shared_code 295.
- `/home/mak/codex`: 616; candidate 2, generated 124, historical 463,
  operational_state 5, product 2, runtime_active 3, shared_code 17.
- `/home/mak/xio_puente`: 12; candidate 1, credential 1, generated 3,
  memory 0, operational_state 1, product 1, runtime_active 1, shared_code 4.
- `/home/mak/WIN/codex`: 8212; credential 6, historical 8206. WIN remains
  archive and never runtime.

Duplicate audit covered the physical source/config/product scope after
excluding generated, rollback, historical, venv, node_modules, and lock
material. The repeat bug-hunt now finds 245 same-hash groups (643 files),
including 197 groups (413 files) touching the checkout. One authorized group
was added when the verified rasterizer was promoted to the live Codex mirror;
the earlier pre-promotion count was 244 groups (641 files). The earlier wider
audit found 299 groups (747 files); the remaining difference is the documented
exclusion scope, not a merge or deletion. Representative exact groups are
`fallback_util.py` hash `011560a85400dc82738cc4b595c4c8ddde6777433ee0f8aebe307a10ca290aba`,
`research_lib.py` hash
`020069a00000fe6492a6b5bd3ce4e6dde3792a47cf544f2221c9a35b5702e989`, and
`calidad_svg.py` hash
`0363f61a6841010e2dd6f92192162e182e04613baa2f0120b3f19d8e95cd1539`.
They are runtime/source mirrors or generated/history duplicates with no
proven authority for consolidation. No duplicate was moved, deleted, or
overwritten.

### Dependency, compile, import, and test evidence

- `/home/mak/research/.venv/bin/python -m pip check` and
  `/home/mak/plataforma/.venv/bin/python -m pip check`: both `No broken
  requirements found`.
- Existing Research venv now has Flask 3.1.3, CairoSVG 2.9.0, vpype 1.15.0,
  pyflakes 3.4.0, pytest-cov 7.1.0, pre-commit 4.6.2, and pytest 9.1.1.
  The Codex system interpreter now has Debian `python3-cairosvg` 2.5.2 and
  Pillow 12.3.0. No new venv, provider, browser, or framework was created.
  System Node is 18.20.4 and npm is 9.2.0. `npm run typecheck` in
  `/home/mak/flujo/web` passes.
- Active Python source excluding explicit rollback/piezas/history and the
  known candidate `/home/mak/plataforma/panel_directivo.py` compiles with
  `python3 -m py_compile`; active shell files pass `bash -n`. Runtime import
  smoke passes for platform Hub/providers/energia, Research interfaz/
  research_lib/worker, Codex calidad_svg/iconos, and XIO monitor.
- Full regression command, with the real venv executable on PATH, exited 0 on
  the final rerun:
  `PATH=/home/mak/research/.venv/bin:$PATH PYTHONPATH=/home/mak/flujo/src:/home/mak/flujo/cultura:/home/mak/flujo/cultura/mak_codex:/home/mak/flujo/cultura/mak_research:/home/mak/flujo/cultura/mak_plataforma /home/mak/research/.venv/bin/python -m pytest -q -rs --tb=short`.
  Every executed test passed. The only skip is 1 missing
  `DIRECTOR_CONTRACT.md`; all 17 SVG animation tests now execute through the
  deterministic CairoSVG CSS adapter and pass. vpype is installed and no
  longer skipped.
- After this handoff was reread, a redundant full-suite attempt was stopped at
  21% rather than rerun against the already recorded result. It raised
  `KeyboardInterrupt` in `energia_log.py`, made no file or runtime-data change,
  and is not reported as a test result. The current focused regression then
  passed every selected executable test with exactly the one authorized
  documentation skip.

### Runtime, routes, services, and sync

All four user units are `active` and `enabled`, after `systemctl --user
daemon-reload` and restart. There is exactly one process/listener for each:

- Hub PID 111669: `/home/mak/plataforma/.venv/bin/python /home/mak/plataforma/hub.py`,
  `0.0.0.0:8900`.
- Research PID 72229: `/home/mak/research/.venv/bin/python
  /home/mak/research/interfaz.py`, `127.0.0.1:8890`.
- Codex PID 96805: `/usr/bin/python3 /home/mak/codex/interfaz_codex.py`,
  `127.0.0.1:8891`.
- XIO PID 72225: `/usr/bin/python3 /home/mak/xio_puente/monitor.py`,
  GET-only monitor with no listener.

The desktop input bridges are intentionally outside the MAK department
runtime: `clip-bridge.service` is active for the shared clipboard and
`barrier-server.service` is active on MAK at `192.168.50.2:24800` for the
shared mouse/keyboard. `barrier-client.service`, which would connect to the
separate WIN host at `192.168.50.1`, is inactive. These human-interface
bridges are not Codex, Research, Hub, or XIO dependencies and are not used as
runtime evidence for those departments.

Department endpoint probes used MAK loopback (`127.0.0.1`) for Research and
Codex. Hub is bound to `0.0.0.0:8900` on MAK, meaning all MAK interfaces; it
does not mean the service runs on WIN. `findmnt -T /home/mak/WIN` resolves to
MAK's root filesystem (`/dev/sda2`), so WIN is a local archive directory, not
an attached runtime mount.

Canonical source mirrors and live units are byte-identical by hash:

- Hub unit `e491c5b938f0007bcf4cbffc4ec7f839fd0f7ba5c868ed7b8c77df049201135c`.
- Research unit `da1e992a255b727a115f92718fc326e5ba629158f1fe76ed89bf3317b6b0ab37`.
- Codex unit `4603a6382f28062e73188d496dd345730a737c07f934b8a754f5d38689c6b580`.
- XIO unit `e28791f8645536dbf66b39017485e3677858fd432431ca9f9bdcb019b06d585d`.

Active runtime/source code hashes also match: Hub
`9a8b861d6065606fcef3c9c4ba13350cfe94f6e8c806ad07df7cfccdb96b0255`,
Research `c7cf09854729ee4e83e50a62d5557dd5815d0e805d50ed1d14a471bf33458114`,
Codex `b5c551fa228be777253a1ea7bd2e8918ff35799d81cff7802168e43e0b57cc25`,
XIO `633695ea015384ea5c8066fc42d9398e50522e157113361a5bd5e2d384bb24d0`,
providers `e344564b3ae0f2640e369e52801e1d6ab5be900cdc05b22675a9537e36ec6153`,
energia `61890334893d2fdab6c062a27cc94ae2a669acb749a2480abf84bbf9c51a4ff9`,
and calidad_svg `0363f61a6841010e2dd6f92192162e182e04613baa2f0120b3f19d8e95cd1539`.
The live and checkout Codex rasterizer both hash to
`bb82b8af96a3fe4e728d6afd5e4a07a09412cdb84ccc848263bf1ded6a20cb27`.
The live and checkout Hub health route now hash to the same Hub source above;
GET and HEAD `/health` return `application/json` under schema
`mak-hub-health-v1`, so the watchdog no longer mistakes the Hub HTML page for
a healthy API response.
The live and checkout coherence checker hash to
`f62abba0e20d5de72f1e672460cb066305ba859a590f587a142184a76ef05269`.
The live and checkout curatoria perception hash to
`f3589397262e37651b81f688beaf5a5e4e72b066152679513a335365b4857081`.

GET matrix returned HTTP 200 for Hub `/`, `/health`, `/portafolio/`,
`/research/`, `/codex/`; Research `/`, `/api/jobs`, `/api/workflow`, and
`/api/memoria/grafo?umbral=0.35`; and Codex `/` and `/api/jobs`.
Codex `/api/graph` returned the expected 404 because it is not a declared
route. `MAK_PORTFOLIO_ROOT` is unset and resolves to `/home/mak/flujo/iskvw`.
The served hashes equal the checkout hashes for `editor.html`
`81f3e9589184a1a15b99532ed6833d03ad79da1c5bfa0b1e2ae623cd05c4ac7f` and
`mesa_montaje.js` `6b87410c20005d0e4818cb176e6d14364c265472d04ac4e01bf762f53121ab82`.

`cultura/mak_plataforma/crontab.mak` and `/home/mak/plataforma/crontab.mak`
match at `c7c7c045ec5e2727f7bb62a753c20210c975d8acf67624ceb39147ea5dbb5122`.
The effective crontab has zero active sync lines and one `# PAUSED-FARO`
repo-sync line. `systemctl --user list-timers --all` reports zero timers.
No fetch, pull, merge, reset, clean, checkout, browser, or automatic sync was
run. The historical duplicate `cultura/mak_plataforma/mak-xio.service` was
marked non-canonical with current hash
`ce4a11343d3b1b06c4ccd3cb724bb12ce5b5afbd8bce4f3c35d949dea0da7a33`; the
canonical XIO source is `cultura/mak_xio_puente/mak-xio.service`.

### Provenance and safety changes

- The stale service mirrors were reconciled from the measured live units into
  `cultura/mak_plataforma/mak-hub.service`, `cultura/mak_research/interfaz.service`,
  `cultura/mak_codex/mak-codex.service`, and the new canonical
  `cultura/mak_xio_puente/mak-xio.service`. Source and live destination hashes
  are recorded above; the previous files remain recoverable in the worktree
  diff and no runtime code was replaced by a WIN file.
- ESM metadata was added at `docs/cultura/lib/package.json` and
  `iskvw/piel/lib/package.json` with `{ "type": "module" }`. This repaired
  Node module-boundary failures without adding a framework; the 13 previously
  failing Node tests now pass.
- Windows WoL fields were removed from live and mirror `energia.py`; source
  HEAD hash was `6102c89091ad41251f48938a6d4fb18ae74dd3b7bbd1b955d01987f7f34d7c11`,
  current live/mirror hash is recorded above. The old Windows field is not an
  active dependency.
- `cultura/mak_curatoria/ingesta_archivo.py` was renamed only at identifier
  level to English ASCII after its archived/source hash
  `6e68de9e4033864c217d2a90ff3a12a9f5e6cf54810a73a6c34d0dbbf2d298be`; current
  checkout hash is `73c83c70783df5a5716eaf600ec80a4959c5b3325c1871396ab83aa467818c1b`.
  Its archive copy was not overwritten.
- The ignored credential file `cultura/.dev` had old hash
  `01347186de8b1335cfffd73fd9418e2216217f75143ec09208d011fcc3ae12dc` and
  was relocated to `/home/mak/.config/mak/flujo.dev` with mode 600 and that
  same hash. The checkout path is now a no-secret ASCII template with hash
  `0b5098b8b4f057a55f509fa4e361edc5810c00ec8de0fa90b5e797060a6ea29c`.
  No credential value was printed or promoted. No credential pattern was
  found in promoted source; existing runtime env files remain external and
  mode 600.

### Final bug hunt and boundary verification

- The focused regression found and covered a false-positive Hub health route:
  `/health` previously fell through to portfolio HTML with HTTP 200. The
  route was added, deployed with a rollback copy, restarted only for
  `mak-hub.service`, and verified with GET and HEAD. The focused route test
  passes.
- The coherence checker previously matched basenames across departments and
  scanned venv site-packages as live code. It now matches absolute runtime
  paths, excludes environment packages, and records the two reviewed
  curatoria candidates as repo-only. `python3
  cultura/mak_plataforma/coherence.py --strict` exits 0: all five organs have
  zero different and zero not-copied files, with zero invoked box-only files.
- Live `/home/mak/curatoria/percepcion.py` contained an opt-in conductor/GPU
  integration absent from checkout. That physical runtime code was reconciled
  into the checkout by measured patch; source/live hashes now match. The
  curatoria guardia remains paused and no new service or framework was added.
- The read-only mirror checker could not read through SSH because host-key
  verification failed before file access for both loopback and MAK-address
  attempts. This is a transport limitation, not an unexplained source drift;
  local source/live SHA-256 checks and `coherence --strict` are the accepted
  evidence for this pass. Known-host policy was not weakened.
- The former static-only rasterizer path was tested against the real compiled
  SVG and the 16 hand-authored RAVE icons. CairoSVG now evaluates the bounded
  CSS vocabulary emitted by MAK, translates CSS transforms to native SVG
  attributes, and measured 4 distinct frames for the live RAVE smoke. The
  adapter is not a general browser or a second framework.
- `/usr/bin/python3` imports `cairosvg` and `PIL`; live Codex reports
  `backend_disponible() == cairosvg` and
  `backend_disponible(anima=True) == cairosvg-css-animation`. The earlier
  failed smoke used an unresolved `var()` SVG; the resolver-backed smoke then
  passed 4/4 distinct frames.
- Final checks: `git diff --check`, Python compilation, platform/research/
  Codex/XIO import smoke, both `pip check` commands, web TypeScript check,
  endpoint matrix, and active-service process count all pass. One process is
  present for each service; no user timers exist and effective active sync
  lines remain zero.
- A deliberately broad live-tree compile also exposed two non-runtime
  classified artifacts: `/home/mak/plataforma/panel_directivo.py` fails at line
  145 and one prose response under `/home/mak/codex/piezas/` is not Python.
  The first remains a candidate and is not referenced by systemd/cron; the
  second remains historical generated material. The corrected active compile,
  excluding those classified areas, passes for live and checkout Python.
- A repeat source scan found no active runtime entrypoint containing Windows
  commands, providers, endpoints, or libraries. One historical/documentation
  reference remains inside the rasterizer module comments; it is not an
  executable path or dependency. The only true secret-pattern match is the
  external `/home/mak/research/research.env`, not promoted source.
- Mirror/service discrepancies are classified, not unexplained: the active
  user units match canonical checkout sources (Hub
  `e491c5b938f0007bcf4cbffc4ec7f839fd0f7ba5c868ed7b8c77df049201135c`,
  Research `da1e992a255b727a115f92718fc326e5ba629158f1fe76ed89bf3317b6b0ab37`,
  Codex `4603a6382f28062e73188d496dd345730a737c07f934b8a754f5d38689c6b580`,
  XIO `e28791f8645536dbf66b39017485e3677858fd432431ca9f9bdcb019b06d585d`).
  The stale non-runtime files `/home/mak/codex/mak-codex.service`
  (`bddea798647e3e239935a4808614a3319b27ffe460a3dc3398d6dac44e63d6fb`),
  `/home/mak/research/interfaz.service`
  (`dbf7fb7f6e4e4fd6fdf7745ea724c0bb0496dfd80b3c40c65103a02e1347567d`),
  and `/home/mak/plataforma/mak-hub.service`
  (`64aa7c58a8c6884066303b539f12ef8d0d83d55c7eda907c5b2f371fb20792bd`)
  retain old installer text/defaults. `/home/mak/plataforma/mak-xio.service`
  (`d7701b21a9a29ec5fcf1f477be4b3c28349fd33155b1381734906b7672cebae4`) is
  the preserved historical duplicate; canonical XIO is
  `cultura/mak_xio_puente/mak-xio.service`
  (`e28791f8645536dbf66b39017485e3677858fd432431ca9f9bdcb019b06d585d`).
  None was moved, overwritten, or installed; all remain reversible in their
  original paths.
- The optional static `mak-research-queue.service` is inactive and has no boot
  enablement; its live and checkout `cola.py` hashes both equal
  `c9cb650c73b1cc8d40c2013cad3379e4e9c81852de0670e9ff35f8742b5832ca`. The
  active watchdog only asks systemd to start declared units
  and does not launch detached duplicate processes.
- No writer was found that can auto-sync, pull, fetch, merge, reset, clean, or
  overwrite the human checkout from WIN. The external helper
  `/home/mak/bin/mak_sync_safe.py` (mode 755, hash
  `4f8284ccc793eee277ccf205e5ddcbeb6593b40d467fcc8ec0f4192489018e55`) is
  manual-only, has no systemd/cron reference or live process, requires the
  separate `/home/mak/flujo-deploy` worktree, and resets only that disposable
  worktree before copying; the effective cron line for it is paused. The
  checkout candidate `tools/mak_ops/repair_mak_sync.py` contains legacy remote
  sync/reset commands and Windows SSH text, but has no caller and was never
  run. Both are classified non-runtime; no duplicate was consolidated.
- Stale prose in `CLAUDE.md`, `RELEVO_MAK.md`, and related historical docs still
  describes the former active repo-sync policy. It is not an executable path;
  current physical crontab and systemd evidence above supersede it. No old doc
  was rewritten because the requested metadata update is limited to this
  current handoff.
- Third consecutive blocker audit at `2026-08-13T21:40:34-04:00`: the focused
  hygiene test still skips at `tests/test_higiene_docs.py:134`, the complete
  local search still finds zero contract files, all four endpoint probes return
  HTTP 200, all four runtime services are active, process count is four, user
  timer count is zero, and the four `pip check`/mirror hash checks remain
  green. No external-state change occurred that could resolve the contract.

### Status and escalation

STATUS: OPERATIONAL_WITH_DOCUMENTATION_WAIVER
AREA: Physical MAK runtime, checkout boundary, and regression bug hunt
OBSERVED: Inventory is fully classified; dependencies, imports, compilation,
  focused regression, services, routes, hashes, cron ownership, credentials,
  and active-runtime boundary checks pass. The only omitted test is the
  documentation hygiene assertion for absent `DIRECTOR_CONTRACT.md`.
EVIDENCE: The director explicitly authorized the waiver for
  `test_el_rango_de_invariantes_citado_coincide_con_el_contrato`; the current
  focused suite passes all executable tests with exactly one authorized skip;
  `/portafolio/` and portfolio APIs return 200; all four MAK user services are
  active with one process each; `coherence --strict` exits 0; pip checks are
  clean; and checkout/live hashes match for the reconciled runtime files.
CONFLICT: The missing contract remains a documentation-only omission and is
  explicitly waived. No runtime, WIN-boundary, credential, or provenance gate
  is waived.
OPTIONS: Continue with Git web restructuring after this physical MAK audit,
  or keep the verified checkout unchanged for a later human contract addition.
RECOMMENDATION: Start Git web restructuring only from this verified MAK scope;
  preserve the current local worktree and keep repo-sync paused.
EXACT DECISION NEEDED: None for the physical MAK audit; the documentation test
  waiver is already authorized by the director.
COMMANDS_NOT_RUN: Git transport or remote synchronization; browser-based
  validation; destructive cleanup; a second full-suite rerun after the
  handoff. The one redundant full-suite attempt was interrupted at 21% and
  made no changes.
FILES_NOT_MODIFIED: `/home/mak/WIN`, protected README/SVG geometry,
  `panel_directivo.py`, active runtime env values, and historical source.

### Git web proposal state

The verified physical scope is staged locally on
`codex/mak-web-restructure-20260813` from the audited checkout tree. The
staging contains 97 approved code, service, workflow, test, metadata, handoff,
and standby files. GitHub CI now runs only on `ubuntu-latest`, and pull
requests target only the four canonical branches. The branch audit is
read-only and protects `mak` alongside `main`, `rd`, and `iskvw`. The airdrop
gate no longer creates a branch or PR, and the historical Claude workflow is
manual-disabled with read-only permissions. Pages publication is now
workflow-dispatch-only. The two curatoria intake files were reviewed and
staged: `diagnostico_proyectos.py` is byte-identical to `mak`;
`ingesta_archivo.py` is the reviewed ASCII identifier/API delta used by the
staged conductor. No
generated data, credentials, WIN material, protected media, reset, clean,
merge, fetch, push, or commit was performed. The canonical branches remain
`main`, `mak`, `rd`, and `iskvw`; this `codex/` branch is a reversible proposal,
not a fifth canonical branch.

### Git transport provenance audit - 2026-08-13 23:02 - REVALIDATED

- The current proposal HEAD and `main`/`origin/main` are
  `559fa6075e1cfb7a51be380c6d354d2af90dffb2`. `mak`/`origin/mak` are
  `814b74c1f5335170bf5ed1ee8c054565d6e3fc3e`. Read-only
  `git rev-list --left-right --count main...mak` reports `6 12`; the two
  canonical lines diverge and were not merged or rebased.
- `git diff --name-only main..mak` reports 247 tree paths. The staged proposal
  contains 97 paths, all present in `mak`; 44 staged blobs are byte-identical
  to `mak` and 53 differ. The 53 differences are explicit proposal/runtime
  scope: 6 workflows, 5 Codex, 1 conductor registry, 1 curatoria API source,
  9 platform, 6 Research, 1 XIO unit, 17 tests, 1 docs metadata, 1 portfolio
  metadata, 1 tool, 2 dependency metadata files, and the handoff/standby
  records. No staged path was silently taken from a missing branch path.
- The proposal has zero staged deletions. Staged path exclusion scan found
  zero credentials, generated/data trees, protected media, virtualenvs,
  database files, and zero blobs over 1 MiB. `git status` reports zero
  unstaged and zero untracked paths.
- All 11 workflow YAML files parse successfully. A read-only scan found zero
  `git push`, PR creation, branch deletion, write permission, Windows runner,
  PowerShell, `cmd.exe`, or uppercase `WIN` references under `.github`.
- Revalidation at `2026-08-13T23:02:15-04:00`: the focused regression passed
  49 tests with one authorized skip at
  `tests/test_higiene_docs.py:134`; Python compilation and staged diff
  checks passed. `mak-hub.service`, `mak-research.service`,
  `mak-codex.service`, and `mak-xio.service` are active with one matching
  process each; listeners remain `8900`, `8890`, and `8891`; the four tested
  endpoints returned HTTP 200. Effective sync cron entries and user timers
  remain zero.
- `rg` was unavailable in this shell during one first pass; that pass was
  discarded. The static scan was rerun with `grep` and produced the zero
  counts above. No remote or runtime state changed during this audit.
- The staged conductor initially exposed an API mismatch against the `mak`
  base: `ingesta_archivo.py` accepted `fuente`, while the reviewed ASCII
  contract uses `source_name`. The local candidate was reviewed as a
  deterministic identifier-only delta, staged, and guarded by
  `test_organism_ingest_contract_uses_ascii_keyword`; the mismatch now passes
  in the `mak` validation tree.
- Existing development tests required DuckDB without declaring it. The
  existing Research venv now has `duckdb 1.5.5`; `pyproject.toml` and
  `requirements-dev.txt` declare `duckdb>=1.4.0`, and `pip check` is clean.
- The complete `mak` validation tree, with all 97 staged blobs overlaid on
  `mak` at detached HEAD `814b74c1f5335170bf5ed1ee8c054565d6e3fc3e`, ran
  2,855 tests with zero failures and one authorized documentation skip. The
  validation tree is local-only; no canonical ref or remote changed.
- At `2026-08-13T23:05:50-04:00`, SHA-256 comparison of every staged blob
  against the validation files at `/tmp/mak-transport-validation-9IeG4b`
  reported 97 files and zero mismatches.
- The Watsonx fallback test now inspects the actual branch instead of a
  brittle 1,400-character slice. The privacy ratchet excludes only
  `docs/recovered/` provenance exports and the explicit sanitizer fixture
  `tests/test_recovered_import.py`; raw historical evidence was not rewritten
  or deleted.

STATUS: DECISION_REQUIRED
AREA: Git transport of the verified MAK scope
OBSERVED: The local proposal is complete and staged, but the current rules do
  not authorize a commit or remote publication from this session.
EVIDENCE: Branch `codex/mak-web-restructure-20260813` has 97 staged files;
  staged diff check, secret scan, generated/media exclusion checks, the full
  `mak` validation suite (2,855/2,855 with one authorized skip), and
  `tests/test_git_web_contract.py` are clean. The issue-download workflow no
  longer describes WIN as a render runtime.
CONFLICT: Publishing now would create external Git state without an explicit
  commit/push decision and would choose a remote target while `main` and `mak`
  are divergent canonical lines.
OPTIONS: Authorize a local commit only; authorize commit plus push of this
  proposal branch; or keep the reviewed staging unchanged.
RECOMMENDATION: Keep staging unchanged until the director explicitly chooses
  the commit and publication target.
EXACT DECISION NEEDED: May MAK commit this staged proposal, and if yes, should
  it push `codex/mak-web-restructure-20260813` to `origin`?
COMMANDS_NOT_RUN: `git commit`, `git push`, remote fetch/sync, merge, reset,
  clean, branch deletion, and browser validation.
FILES_NOT_MODIFIED: Remote refs, canonical branch tips, WIN archive, active
  runtime env values, generated data, credentials, protected media, and
  rollback material.

### Next action

The physical MAK audit is complete under the authorized documentation waiver.
Keep WIN archival and repo-sync paused. Review the staged proposal scope before
any commit or publish; transport only approved code, contracts, migrations,
tests, and products whose current local evidence remains green.

## Historical physical MAK handoff superseded by final audit - 2026-08-13

Authority is the live Linux body under /home/mak. Git and old handoffs are
transport/evidence only. /home/mak/WIN is archive and provenance; no file from
WIN was executed. MAK runtime uses Linux Python and local Ollama/NIM/Watson
paths only.

### Measured inventory and classification

- /home/mak/flujo: 14905 files: shared_code 564, tool 439, generated 12399,
  memory 1261, product 155, operational_state 84, credential 3.
- /home/mak/research: 5420 files: runtime_active 40, candidate 2990,
  generated 2324, historical 14, memory 17, operational_state 34,
  credential 1.
- /home/mak/plataforma: 4907 files: runtime_active 89, candidate 743,
  generated 3894, historical 105, memory 36, operational_state 39,
  credential 1.
- /home/mak/codex: 504 files: runtime_active 19, candidate 427, generated
  12, historical 37, memory 2, operational_state 6, credential 1.
- /home/mak/xio_puente: 9 files: runtime_active 1, tool 2, historical 1,
  memory 2, operational_state 2, credential 1.
- /home/mak/WIN/codex: 8212 files: tool 64, generated 8008, historical 140.
- The physical classifier produced zero unclassified files. Duplicate is a
  separate evidence overlay, not a replacement class. Hash audit found 17
  same-hash groups in the checkout; generated research corpora and rollback
  copies remain separate because no authority was proven. No duplicate was
  moved or overwritten.

### Dependency and code checks

- Python is 3.11.2. Research and platform venvs both report pip check:
  No broken requirements found. Codex and XIO use /usr/bin/python3.
- Pytest was installed only into the existing research venv from the already
  declared test dependency. No runtime provider or framework was added. The
  full suite was started with the checkout PYTHONPATH but was interrupted;
  it is not reported as passed.
- AST parse: 142 live Python files, 141 pass and one candidate fails:
  /home/mak/plataforma/panel_directivo.py:145, expected except/finally. No
  systemd or cron caller references this file; it remains candidate/failed,
  not promoted.
- Checkout source AST parse: 122 files, 0 failures. Import smoke passed for
  mak_conductor, runtime, queue_store, handler_registry, mak_research.worker,
  mak_codex.worker_codex, mak_codex.interfaz_codex, research_lib, and
  codex_lib.
- Manual isolated conductor smoke passed: idempotent enqueue, claim, start,
  validation, completion, and COMPLETED state. Provider filter smoke passed:
  input win,ollama resolves only to ollama.
- git diff --check passed. No credentials were found in promoted source
  patterns. Credential-bearing environment files remain external state:
  /home/mak/flujo/.env, /home/mak/research/research.env, and
  /home/mak/xio_puente/.env. Values were not printed. Their modes are now
  600; /home/mak/flujo/.env was 644 and was changed to 600.

### Runtime and service evidence

- After daemon-reload and restart, exactly one process/listener exists for
  each active service: Hub PID 400243 on 0.0.0.0:8900, Research PID 400240
  on 127.0.0.1:8890, Codex PID 400242 on 127.0.0.1:8891, and XIO remains
  GET-only under mak-xio.service.
- GET checks returned 200 for Hub /health and /, Research / and /api/jobs,
  Codex / and /api/jobs. Research /api/workflow and
  /api/memoria/grafo?umbral=0.35 returned 200. /api/graph returned 404
  because it is not a declared route; UI and handler code use workflow/grafo.
- Hub route authority is measured: MAK_PORTFOLIO_ROOT is unset and therefore
  resolves to /home/mak/flujo/iskvw; /portafolio/ serves that root and
  mesa_montaje.js?v=20260811-atlas-audit. Current hashes:
  editor.html 81f3e9589184a1a15b99532ed6833d03ad79da1c5bfa0b1e2ae623cd05c4ac7f;
  mesa_montaje.js 6b87410c20005d0e4818cb176e6d14364c265472d04ac4e01bf762f53121ab82.
- Codex live unit now has Environment=CODER_CHAIN=nim-pro,nim-flash,ollama
  and MAK_SERVICE_HOST=127.0.0.1. New live unit hash is
  4bce553a4529bcab0b5a58de1185d858188ebc745cb301c3ee47844bb3d3b9e7;
  previous live hash was 3d9800606edc1178918d359fe2b9d1d38e1662dc085d9086beec3f8d60ed5407.
- Active source no longer contains WIN_BASE_URL, WIN_MODEL, the remote
  192.168.50.1 endpoint, or a win provider route. Historical rollback and WIN
  archive references are retained as evidence only.

### Sync and provenance changes

- The dangerous live declarative repo-sync line was paused in
  /home/mak/plataforma/crontab.mak. New hash is
  c7c7c045ec5e2727f7bb62a753c20210c975d8acf67624ceb39147ea5dbb5122,
  equal to the paused checkout mirror. Effective crontab and systemd timers
  contain no active repo-sync. No fetch, checkout, reset, pull, merge, clean,
  or automatic synchronization was run.
- The existing mak_conductor package was restored into the checkout from
  /home/mak/WIN/flujo/cultura/mak_conductor because its ten archived source
  files matched the live pyc code-object signatures exactly. Destination
  source hashes matched each archive source hash. The package remains
  untracked and its two archived tests are untracked; it is not wired into
  cron or active service execution.
- Runtime provider files and their checkout mirrors were reconciled in
  measured per-file patches. Active entrypoints and shared executable modules
  now match by hash; remaining differences are documentation or operational
  state and are recorded below. No broad copy was performed.

### Unresolved discrepancies

- Functional runtime/source hash differences for the reconciled service
  entrypoints are closed. Remaining intentional documentation/state pairs
  differ and were not copied: `DEPLOY_OPEN.md` runtime
  `83842d3492b6292cf19feb2565426e2df50b664f06c016b1959a63101a75fb55` vs
  mirror `783c34819700b05e6be316a06a1b85355bbeb2bfc9582379f0db524a5f588784`;
  `MAK_RESEARCH.md` `cfc12a2c4d3846ec965d3243a12590f00fefd1280b0aa42dcccbac5207dcd1a9`
  vs `ffb9854cf2b90fd20f5d33c633b1d3824802d7fd8eb06d1a1335c57fecbe9e80`;
  `RELEVO_MAK.md` `7cf5a789ea9e34391d58819b31b1fcd60fbda9c97cf7b5f81908e2fd649151da`
  vs `0b1d271846b965d724fa24b1f9e6621aac50c49cbd41e5e93bf5c45fd5aeecda`;
  `GENESIS.md` `fc4ef87d1a4bee6cbedb9224fedefb1485c2f73faa3eb952264137bbfb626285`
  vs `1444b907919e4993ee69f495d3ee6ecfdf4557c8b68167c6c955140ccfe10ec2`;
  and `backlog_codex.txt`
  `02ac722c8ff1a48666bb8111efeb8e313a845a73ee65e2736fd319600b7eb92a`
  vs `99893cb7ccd15fac38d3f360950e08cfce2aaacad51dd5b914de0a15d1620f0c`.
  These are memory or operational-state authority conflicts, not executable
  runtime drift; do not overwrite them without a separate provenance record.
- Focused conductor, provider, and Codex tests pass. Two icon tests remain
  blocked because no local Linux backend can rasterize and animate SVG. The
  production result is explicitly `visual_validation.status=unverified` and
  `smoke_ok=false`; do not install a browser or Windows dependency to bypass
  this evidence gap.
- The full pytest run reached 24 percent and showed three visible failures
  before SIGINT. Its result is incomplete and must be rerun with the real
  checkout PYTHONPATH.

STATUS: BLOCKED
AREA: SVG perceptual validation and incomplete regression suite
OBSERVED: MAK services and reconciled entrypoints are healthy, but the real
  Linux host has no animation-capable SVG rasterizer and the full pytest run
  was interrupted after visible failures.
EVIDENCE: focused conductor tests 16/16; pip check green; AST 122/122 source
  files pass; `backend_disponible(anima=True)` returns None; full pytest was
  stopped with SIGINT at PID 407024; no pytest process remains.
CONFLICT: `smoke_ok=true` would promote an SVG whose animation was not
  measured. Installing a browser or Windows dependency would violate the
  MAK-only runtime boundary.
OPTIONS:
  1. Keep icon output unverified and blocked until an approved Linux backend
     exists, then rerun visual tests.
  2. Decide that deterministic compile-only output is sufficient for this
     candidate lane and explicitly change the promotion contract.
RECOMMENDATION: Option 1. Keep the safety gate closed and complete the full
  suite and remaining bug hunt first.
EXACT DECISION NEEDED: If no approved Linux rasterizer is available, decide
  whether icon candidates remain blocked or compile-only output may be
  promoted with `visual_validation.status=unverified`.
COMMANDS_NOT_RUN: complete full pytest result; final endpoint/hash/cron
  regression pass after the standby pause.
FILES_NOT_MODIFIED: panel_directivo.py; rollback files; WIN archive; runtime
  env values; README/SVG protected geometry.

### Next action

Read `STANDBY.md`, verify the physical state, rerun the complete pytest suite,
resolve every non-environment failure, then repeat the final service,
dependency, hash, duplicate, cron, watchdog, and active-WIN scans. Keep
repo-sync paused, keep WIN archival, and do not declare success until no
missing dependency, unexplained hash difference, broken candidate route,
omitted test, or process duplication remains.

Updated: 2026-08-11 - canonical branch promotion and final validation
Status: The Hub boundary, XIO human-link circuit, writer ownership block, and
language slices are consolidated in the four canonical branches. Local,
GitHub, MAK checkout, and runtime mirror are clean and synchronized; no
auxiliary branch or worktree remains.
This block is the current operational source. Later sections preserve dated
historical evidence and must not be read as present state.

## Read this first

This file is the operational checkpoint. The order for a fresh agent is:

1. `AGENTS.md` - current rules and boundaries.
2. This file - measured state, completed work, and next action.
3. `CAPACIDADES.md` - reusable tools and provider inventory.
4. `MAPA.md` - CLI, repo zones, and commands.
5. Source files and focused logs only for the selected next circuit.

Do not treat raw logs, old plans, Downloads, chat memory, or an old branch as
instructions. Verify any statement that affects a destructive or remote action.

## Current verified state - 2026-08-11

- Windows canonical: `C:\IA\flujo`, branch `mak`, clean. After the final
  promotion, the four canonical refs (`main`, `mak`, `rd`, and `iskvw`) were
  measured with identical trees; README/SVG have no diff. Use
  `git for-each-ref` to read their current commit ids instead of copying an
  old id from this document.
- The isolated audit checkout and all auxiliary worktrees were removed after
  normalized-content comparison proved their useful source was preserved in
  `mak`; no unique active code was discarded. Generated audit artifacts were
  excluded from the canonical commit.
- MAK: `/home/mak/flujo`, branch `mak`, clean and matched to `origin/mak`
  after the final branch promotion. The prior manual state is
  preserved in stash `preserve manual MAK deployment before canonical branch
  cleanup 2026-08-11`; the effective repo-sync line remains `# PAUSED-FARO`.
- Runtime: `mak-hub.service` active, PID `74023`; research `interfaz.py` PID
  `71790`; Codex `interfaz_codex.py` PID `71774`. Listeners are
  `0.0.0.0:8900`, `127.0.0.1:8890`, and `127.0.0.1:8891`.
  Runtime SHA-256 values are Hub
  `5e33a22142276177b35ff0d3d714b20bd10e09245819ada71c85bd805dcca107`,
  Research `73d488f0265c021d5ffa6ece33eb86ab99b0b037967b3442dd9ddeee90ca05fb`,
  and Codex `154c5e702742f126c7c9cb8c3ea97af896a9f2d66c2413170614679bb7d209b6`.
  Hub `/research/` and `/codex/` return the proxied service pages and their
  same-origin fetch shims. Direct LAN access to `:8890` and `:8891` is
  unreachable from Windows.
- Operational editor: Hub serves `/portafolio/` from
  `/home/mak/flujo/iskvw`. Current repo/served hashes: `editor.html`
  `90e90b1ebb1d2f33db8cf60d131a5a20b109c3e61ec1879aa5cfb6064e6c324e` and
  `mesa_montaje.js`
  `e139ccdefec5a2d320803842645a37cd878d554bfda3bfd49b4f867ef9229109`.
- Integrity: the 49-entry mirror check reports `49 PASS / 0 MISMATCH`, and
  `coherence.py --strict` reports `0 different`, `0 not copied`, and
  `0 box-only invoked`. The live Hub route matrix and service contract checks
  passed; the common ledger fingerprint was unchanged during the GET matrix.
- Current Atlas: `7044` records, `91` labels, `58` records with current
  state, `automation_ready=false`; XIO is available as separate evidence,
  and its explicit human-link endpoint/UI are live. No productive XIO link,
  provider call, or AWS/Watson call was made in the last batch.

## Canonical branch promotion - 2026-08-11

- Measured `git diff --stat` and tree hashes before promotion: `main`, `rd`,
  and `iskvw` were byte-identical to each other but lacked the 88-file MAK
  consolidation. The delta contained no README/SVG file.
- Promoted `mak` into each canonical branch with `git merge --no-ff`, keeping
  the previous branch histories. The only merge conflict was blank-line
  context in `tests/test_readme_svg.py`; the protected geometry assertions
  were retained unchanged.
- Focused SVG and language tests passed after the conflict resolution. The
  three branch pushes completed: `main=72bd6db2`, `rd=61ffc0db`, and
  `iskvw=0f2cb9b9`; `mak` remains `5f7e2e09`.
- A full local `python -m pytest -q` attempt was stopped by the 124-second
  command timeout before producing a result; it is not counted as passed.
- The follow-up handoff correction was then merged into all four canonical
  branches, so documentation and code now share one final tree as well.

## Current next action

Continue the open audit circuits in the prior handoff without creating another
branch or touching README/SVG. The final branch hash/tree check, remote
cleanliness check, and focused regression suite were completed after the
promotion; the full suite timeout remains recorded as an unresolved validation
limit, not as a pass.

## Audit circuit - 2026-08-11

- Strategy: use a strangler migration around the existing Hub. Keep one human
  Web surface at `:8900`, route Research/Codex through `/research/` and
  `/codex/`, preserve existing JSON/form contracts and historical data, and
  leave internal service ports as loopback implementation details. Curatoria
  remains a cron/batch worker with no separate human panel.
- Care boundary: do not create a second UI, ledger, graph, policy engine, or
  parallel archive; preserve user-authored context and historical evidence;
  keep human decisions append-only and public promotion gated.
- Consolidation work in the isolated checkout includes the fixed Hub proxy,
  Hub-based machine delegation, loopback defaults for both services, the
  canonical Hub route in the archive generator, and current operational docs.
  No README/SVG geometry or public archive contract was changed.
- Language guard measured `63` changed Python files with zero new Spanish
  identifiers and zero new Spanish comment/docstring offenders. Focused tests
  passed with six environment skips; the full repository suite then passed
  with no failures and only expected environment skips. Targeted
  `py_compile`, Ruff, and `git diff --check` passed. The full suite also caught
  and the guard confirmed the handoff contains no literal Windows username.
- Manual transport is complete and verified: 36 reviewed source files and
  the two active systemd units were backed up under
  `/home/mak/rollback/atlas-hub-boundary-20260811/` before copy/restart. The
  effective repo-sync remained paused. No README/SVG or provider data was
  transported.
- Canonical reconciliation is complete: `74` reviewed files reached Windows,
  with generated `data/rd_packs.json` and `iskvw/piel/campo/piel.json`
  intentionally excluded. The canonical full pytest suite passed 100%; the
  mirror check reports `49 PASS / 0 MISMATCH`; strict coherence reports zero
  drift; and the final read-only Hub route matrix returned HTTP 200 while the
  ledger fingerprint stayed unchanged.
- Follow-up XIO circuit is deployed: `POST /api/portfolio/copilot/xio-link`
  validates the show work, portfolio source, and optional segment, appends to
  the existing human-resolution JSONL, and is idempotent. The live evidence
  route reports `available=true`, `linked_to_source_id=false`, and the UI
  serves the explicit link action without auto-linking.
- Writer ownership circuit is classified: `puente_issues.py` has one active
  cron caller, a non-blocking `fcntl` process lock, and atomic state replace;
  source/runtime hashes match. `energia_log.py` has zero active cron/systemd
  callers and matching source/runtime hashes, so no new lock or duplicate
  runtime path was introduced. The stale four-hour grep process was stopped by
  exact PID; no MAK service was touched.
- Post-transport regression passed: `25` focused tests, privacy, language
  ratchet, operational-entrypoint checks, Python compile, Ruff, JS syntax,
  and `git diff --check`. The change ratchet measured `63` changed or
  untracked Python files with zero new Spanish identifiers or comment offenders.
- AST comparison of every changed Python module found no removed public
  function, class, or entry point; added public helpers are intentional
  writer/cache or test helpers. The duplicate review found no duplicate active
  module, only separate package or historical basenames.
- The operational-entrypoint guard now asserts that active docs use the Hub
  routes, contain no direct LAN Research/Codex URLs, and keep Curatoria's old
  `panel.py` outside the live mirror map.

## Next action - current

The Hub boundary, XIO human-link circuit, writer ownership circuit, language
guard, canonical branch cleanup, runtime reconciliation, and full validation
are verified. Keep repo-sync paused, do not bulk-rename legacy public names,
do not touch README/SVG, and continue the next language migration as a bounded
compatibility slice with aliases and a new validation pass.

## Bounded language migration - 2026-08-11

- The first compatibility-preserving slice translated comments and docstrings
  in active `cultura/mak_plataforma/ideas.py`, while retaining the historical
  public functions (`cargar`, `relacionar`, `anotar`, `encargar`, `priorizar`),
  JSON keys, routes, and Spanish product/error values.
- The second slice translated comments and docstrings in the active cron
  writers `cultura/mak_plataforma/latido.py` and
  `cultura/mak_plataforma/red_watch.py`. No identifiers, cron lines, systemd
  units, data keys, or runtime behavior changed.
- The third slice translated comments and docstrings in the active append-only
  writer `cultura/mak_plataforma/mutaciones.py`. Its lock, `fsync`, public API,
  JSON keys, and audit semantics remain unchanged.
- Measured result: the three files classify as English (`ideas.py` es=0/en=110;
  `latido.py` es=3/en=23; `red_watch.py` es=1/en=18); the change ratchet reports
  zero new Spanish identifiers and zero new Spanish comment offenders. The
  four files classify as English (`mutaciones.py` es=1/en=74); the change
  ratchet reports zero new Spanish identifiers and zero new Spanish comment
  offenders. The bounded suites passed `104` tests for the first two slices and
  `15` additional tests for the append-only writer; `py_compile` and
  `git diff --check` passed.
- The canonical full suite was rerun after the first two slices and passed 100%
  of executable tests; the append-only writer then passed its focused suite.
  After the privacy-fixture correction, the full suite passed again at 100%,
  with only the known environment skips and existing deprecation warnings.
  README/SVG protection still reports zero changed protected files.
- The four language files are now committed in `d1977e02` and mirrored to the
  live MAK source with a rollback copy. No service restart was needed because
  the slice changes comments/docstrings only; coherence now reports zero drift.

## Canonical branch cleanup - 2026-08-11

- The useful audit block and compatibility slices were committed to `mak` as
  `d3d31d7e`, rebased onto `origin/mak`, and pushed as `7172616d`; the privacy
  fixture correction was then committed and pushed as `d1977e02`.
- Local `main`, `rd`, and `iskvw` were fast-forwarded to their matching remote
  heads. The only remaining local/remote branches are `main`, `mak`, `rd`, and
  `iskvw`; the only worktree is `C:\IA\flujo`.
- Removed redundant local and remote branches:
  `agent/fix-ubuntu-path`, `codex/sync-iskvw`, `codex/sync-mak`, and
  `codex/sync-rd`. Their patches were already present in canonical history.
  The uncommitted `codex/atlas-audit` worktree was removed only after every
  useful file was verified against the committed `mak` tree.
- The MAK checkout was fast-forwarded to `d1977e02` after stashing its manual
  deployment/backups; runtime remains active on the same listeners, and
  `coherence.py --strict` reports zero drift in all five organs.

## Identity and user direction

- The current director is Faro/Codex. Cauce was the previous name used in old
  sessions. Claude is historical context, not a current dependency.
- The user is an artist, graphic designer, VJ, and RD collaborator. The system
  must serve the user's daily artistic practice first, not optimize for a
  generic sellable product.
- The user wants a flexible system that can distinguish artwork, audiovisual
  record, research, opportunity, client work, venue, event, artist, producer,
  and collaboration without forcing one output format onto all of them.
- Posts and reels may be artworks or work records. Stories are records by
  default, not artworks. Instagram descriptions are preserved as source data;
  they can be poetic artwork material or uncertain metadata, but they are not
  factual proof by themselves.
- Portfolio relations must keep artist, username, client, collaborator, event,
  festival, venue, producer, location, date, and source separate. A username is
  not automatically an artist. Human corrections are evidence and learning
  signals, never silent overwrites.
- The artist's own work has two top-level ownership values: personal or client.
  Client work can be visual/live-show or promotional/web; RD can be print or
  web; personal work can be 2D, 3D, mixed, collaboration, mathematical,
  generative, or conceptual. Do not turn this into a rigid taxonomy without a
  real need.

## Repository state

- Windows workspace: `C:\IA\flujo`.
- Verified checkout: branch `mak`, commit
  `d1977e02fc803c9daf17d5bbce221b8954839048`; the Windows worktree is clean
  and matches `origin/mak`. Local and remote canonical refs are synchronized:
  `main=d0c9a594`, `mak=d1977e02`, `rd=b79f1476`, `iskvw=d887771c`. No
  README/SVG diff exists.
- The separate clean `main` worktree under the local `.roo/worktrees/`
  directory was removed after verifying it had no uncommitted changes. The
  local `main` branch is now available for a new session; no branch or commit
  was deleted.
- The current visible editor is not the old list/card interface. It is the
  GTM/map relation surface served by MAK at
  `http://192.168.50.2:8900/portafolio/`; the endpoint returned HTTP 200 and
  contains `data-editor-mode`, `mesa-order-hud`, `revisión humana`, and GTM
  markers. It shows actual media, a selected piece, relation actions and the
  copilot layer in the same Hub route.
- The Hub defaults `MAK_PORTFOLIO_ROOT` to
  `/home/mak/flujo/iskvw`, so `/home/mak/flujo/iskvw/editor.html` is the
  operational editor. The canonical Windows, audit, repo, and served editor
  share SHA-256
  `90e90b1ebb1d2f33db8cf60d131a5a20b109c3e61ec1879aa5cfb6064e6c324e`.
- The canonical Windows, repo, served, and runtime
  `/portafolio/mesa_montaje.js` share SHA-256
  `e139ccdefec5a2d320803842645a37cd878d554bfda3bfd49b4f867ef9229109`.
  The reviewed block is committed in `mak` at `d1977e02`.
- The promoted work covers `cultura/mak_plataforma/` (ledger, identity,
  providers, decisions, Hub, batches, routing, service/watchdog), the current
  `iskvw/editor.html`, the README/SVG text layer, operational docs, tests, and
  portfolio/dossier documents. README/SVG geometry remains protected.

## MAK box: verified truth

Fresh SSH check on 2026-08-11:

- Host: `mak@192.168.50.2`, hostname `dell-11m`.
- The actual Git checkout is `/home/mak/flujo`, currently on `mak` at
  `d1977e02fc803c9daf17d5bbce221b8954839048`; `origin/mak` is the same
  commit and the worktree is clean. The previous manual deployment/backups
  remain recoverable in the named stash recorded above.
- The runtime Hub is healthy and is managed by the user systemd unit
  `/home/mak/.config/systemd/user/mak-hub.service`, PID `74023`; research is
  PID `71790` and Codex is PID `71774`.
- Runtime hashes are Hub
  `5e33a22142276177b35ff0d3d714b20bd10e09245819ada71c85bd805dcca107`,
  Research `73d488f0265c021d5ffa6ece33eb86ab99b0b037967b3442dd9ddeee90ca05fb`,
  and Codex `154c5e702742f126c7c9cb8c3ea97af896a9f2d66c2413170614679bb7d209b6`.
- The listeners are `127.0.0.1:8890`, `127.0.0.1:8891`, and
  `0.0.0.0:8900`. Hub `/research/` and `/codex/` return the proxied service
  pages; direct LAN access to `:8890` and `:8891` is unreachable from Windows.
- Do not copy Windows credentials to MAK. MAK already loads its own provider
  environment. Never print or commit credential values.
- Use MAK for long scans and model batches. Use Windows for orchestration,
  focused edits, transport, and short verification.

## What is completed

### Core traceability

- Existing ledger/tandas/discernment machinery now carries the universal
  `mak-work-v1` envelope. It includes work identity, parent task, lane,
  purpose, format, evidence, provider, status, owner, next action, allowed
  decisions, fallback chain, and identity.
- Invalid envelopes are rejected before local judging and ledger promotion.
  Historical products remain intact and untyped legacy material remains
  `legacy_unknown` rather than being rewritten.
- Decision records use the existing decision vocabulary and preserve the work
  envelope. Public promotion remains human-gated.

### Provider mesh

- `providers.py` exposes a provider registry and route plan without secrets.
- Current intended routes: AWS for visual evidence, Watsonx for research and
  hypotheses, Ollama for local judging, and deterministic fallback when a
  model is unavailable or slow. Cerebras/Groq remain optional future/free
  lanes under the same contract.
- `tandas.py` routes through the provider registry and preserves existing
  batch compatibility. Empty explicit paths no longer erase area evidence.

### Portfolio, vision, and GTM

- The portfolio editor is part of the MAK Hub at `:8900/portafolio/`; no new
  port was created. Search, association basket, boards, triangulation, and
  promotion remain separate actions.
- The editor shows actual media and a copilot layer. GTM is a local projection
  over the archive, not a second database. Human board scope and feedback
  affect ranking but do not rewrite canonical archive data.
- `GET /api/portfolio/organism` returns a projection-only organism with common
  entity envelopes. `GET /api/portfolio/identity-graph` returns the explicit
  metadata graph. It never parses a description into an artist or venue.
- `GET /api/portfolio/copilot/learning` exposes bounded feedback learning.
- AWS visual analysis is limited to actual image evidence. Videos are not sent
  without an existing still/contact sheet/poster. The first real AWS call on
  `18108033539083566.jpg` persisted `faro-portfolio-vision-v1` features in
  `/home/mak/plataforma/director_runs/portfolio-editor-20260808/`.
- A five-reel visual circuit passed the local judge and entered the common
  ledger as local curation candidates. A five-story circuit used contact
  sheets and `portfolio_record`; it remained audiovisual records, not works.
- Current inbox scale is 7,044 pieces: 5,919 stories and 1,125 published media.
  Do not scan or send all of them to a model. A prior story projection found
  106 explicit-signal candidates across 102 dates; five high-signal stories
  have contact sheets for controlled follow-up.

### Research rescue and separation

- Watsonx and AWS reviewed the same 23 legacy reports. Adjudication produced
  12 `rescue` candidates and 11 `review` items; there was no deletion or public
  promotion. The adjudication file is on MAK under
  `/home/mak/plataforma/director_runs/faro-report-action-queue-20260808/`.
- The public iskvw archive is separate from research by default. Research
  essays/icons enter only through an explicit opt-in flag; they are not trash,
  but they are not public substrate by default.
- `story_record` uses `format=registro`, `evidence_kind=media_metadata`, and
  actions such as `triangulate`, `archive`, `review`, and `reject`.

### Opportunity verification 2026-08-09

- The existing Fondart/opportunity corpus contained current-looking 2026/2027
  cards mixed with a stale 2023 report. A first Watsonx pass failed the product
  gate because one item omitted `next_action`; no data entered the ledger.
- The repair is now deterministic and conservative: it may add only the human
  action `verificar bases y fecha exacta de cierre`; it never fills dates,
  eligibility, amounts, or source facts.
- The second bounded Watsonx pass accepted five opportunity candidates through
  Ollama. They remain `revisar` with `next_action=verificar bases y fecha exacta
  de cierre`; nothing was submitted or promoted. The ledger now preserves that
  product action instead of dropping it.

### Durable vertical circuit 2026-08-09

- MAK created `/home/mak/plataforma/director_runs/vertical-curation-20260809/`
  with a 38-item stratified manifest: 18 stories and 20 published media,
  including explicit-signal records, year spread, images, videos, and
  description-bearing media. Promotion is `none`.
- Watsonx first exposed a real integration defect: relative portfolio media
  paths were rejected even when the manifest declared the asset root. The
  batch gate now resolves manifest-declared assets without accepting invented
  paths.
- AWS visual pass accepted five candidates into the common ledger as
  `revisar` records with next action `triangulate`; it did not publish them.
  Empty provider relations are retained as explicit unknowns, not facts.
- Watsonx passed the path and product gates on its third pass, then Ollama
  rejected the mixed batch because two records still needed artist/context
  clarification. This is the intended local stop, not a provider loop.
- `providers.route_task("judge")` now reports `requires_external=false` when
  Ollama is the selected local judge, so the cheap fallback is represented
  honestly after premium credits disappear.
- The event-triangulation manifest also exposed a second path-shape variant:
  Watsonx returned `/portfolio-media/...` and the focused manifest used
  `candidate_rows`. Both forms are now resolved against the declared asset
  root. The third bounded run reached the local judge and was rejected because
  Watsonx proposed unsupported `tomas.pcaa` evidence absent from the XIO file;
  no event relation was promoted.
- The Hub review queue initially showed zero items because generic accepted
  `portfolio_record` rows stopped at the ledger and lacked the portfolio
  candidate projection. The ledger now bridges each record to a pending
  candidate with its media identity, explicit unknowns, and next action
  `triangulate`. The Ollama-backed AWS retry degraded to `revise` when its
  verdict was invalid; a bounded deterministic-fallback retry accepted five
  records and the Hub now exposes exactly five pending review items. The
  external-candidate panel now renders each candidate's actual image or video
  beside its evidence and accept/revise/reject actions; it no longer asks for a
  prose-only decision.
- A fourth bounded Watsonx triangulation was run with the manifest, human
  clarifications, and XIO evidence. It returned five `story_record` hypotheses,
  but Ollama rejected the batch because relations and unknowns were still too
  broad; no new ledger entries or promotions were created. Do not rerun this
  same mixed batch: the five AWS candidates remain the controlled review set.

## Verification already done

- Focused Windows tests passed:
  `py -m pytest tests/test_mak_tandas.py tests/test_mak_ledger.py tests/test_mak_discernment.py tests/test_mak_portfolio_bridge.py tests/test_copilot.py tests/test_iskvw_editor_contract.py -q`
- Modified Python modules compile; the editor JavaScript syntax check passed;
  `git diff --check` passed.
- The full suite was attempted with a 180-second limit and timed out without
  output. Do not make a full-suite rerun the next task. Diagnose it only after
  a meaningful circuit is complete.
- Closing documentation verification passed:
  `py -m pytest tests/test_higiene_docs.py tests/test_mapa_completo.py -q`
  (`5 passed, 1 skipped`), `git diff --check` passed, and this handoff is
  ASCII-only (198 lines).
- The focused tanda gate now passes `45` tests with
  `py -m pytest tests/test_mak_tandas.py -q`; modified MAK modules compile.
- The combined tanda/ledger focus passes `70` tests; the Hub service was
  restarted after the ledger bridge update.
- The visual review contract plus tanda/ledger focus passes `72` tests after
  the candidate-card update; MAK serves the updated editor and the Hub remains
  active.
- The opportunity repair and ledger propagation tests pass in the same focused
  run; current focused collection is `74` tests.

### Visual distinction correction 2026-08-09

- The live review queue was verified at `GET /api/portfolio/review-queue`: it
  contains exactly five pending external candidates.
- The study view was the source of the apparent seven-image count: it renders
  one active piece plus up to six visual neighbors. Those neighbors are context
  unless their source id is present in the pending review queue.
- `iskvw/editor.html` now marks the active piece, pending candidates, and visual
  context with separate labels, colors, and a visible media/candidate count.
- The corrected editor was copied to `/home/mak/flujo/iskvw/editor.html`; the
  MAK Hub remains active and HTTP verification found `foco-visual-legend`,
  `candidato pendiente`, and `contexto visual` in the served page.
- Focused editor tests pass (`2 passed`) and `git diff --check` passes. No
  provider call, ledger mutation, public promotion, commit, or push was made.

### Visible Estudio correction 2026-08-09

- The first visual correction targeted the legacy `#inbox-foco` surface, but
  `body.estudio-principal` hides that surface. The screenshot-visible UI is
  `#estudio-app`; the prior change therefore did not solve the user's view.
- `#estudio-app` now loads the real review queue before rendering, exposes the
  five pending candidates in a compact visual review strip, and adds direct
  `revisar` actions in the same Hub page.
- The active piece and orbit neighbors now carry explicit `candidato` or
  `contexto` roles. The screen count says how many media are visible and how
  many are actual review candidates; orbit context is not silently promoted to
  the queue.
- Review details and accept/revise/reject actions now render inside the visible
  study action panel. The existing review endpoint remains the only write path;
  no second store or port was added.
- The current editor was copied to `/home/mak/flujo/iskvw/editor.html` with
  SHA-256 `d21e30f9fc44cdf3d8dcad1b77a46ccbdad5d7d9d34b52db48b65a187ee441f6`.
  HTTP verification confirms the Hub serves the queue surface, the Hub is
  active, and the review endpoint still reports five candidates.
- Focused editor tests pass (`2 passed`), the inline JavaScript passes
  `node --check`, and `git diff --check` passes. Current Windows changes are
  intentionally uncommitted; no provider call or ledger mutation occurred.

### Candidate review identity fix 2026-08-09

- The user's first review exposed the actual persistence bug: the five legacy
  portfolio rows share the historical ledger id `deb490421de0`. The GET queue
  could distinguish them by `source_id`, but the POST handler searched only by
  ledger id and hit an older non-candidate row, returning
  `candidato_no_encontrado`.
- The review handler now requires or derives `source_id` and selects the
  matching `portfolio_candidate` row. Review history is keyed by ledger id plus
  source id, so a decision for one record cannot bleed into the other four.
- The visible Estudio sends the source id with the human decision. The legacy
  surface now also derives the active source when it is used.
- Focused bridge tests pass (`26`), editor tests pass (`2`), Python compilation,
  JavaScript syntax, and `git diff --check` pass. MAK was updated and restarted;
  source-specific HTTP verification returns exactly one candidate for
  `18408020584187134.jpg`, while the global queue remains five pending items.
- No review decision was written while diagnosing this error, no provider was
  called, and no commit or push was made. Current Windows changes remain
  intentionally uncommitted.

### First human review result 2026-08-09

- The user successfully reviewed the first visible candidate
  `18408020584187134.jpg` and left a note about an emotional-diary area and a
  message addressed to close contacts.
- MAK confirms the note was persisted with decision `revise` at
  `2026-08-09T04:35:20-0400`. It remains in the pending queue by design because
  `revise` means keep the candidate available for another pass.
- Source-specific queue verification returns exactly one row for each of the
  five candidate source ids. The server path is healthy; a hard refresh is
  required if the browser retained the previous editor JavaScript.
- The current five-candidate review state is: `18408020584187134.jpg` remains
  `revise`; `18095439206064834.jpg`, `18010334341143699.jpg`, and
  `17879297036002321.jpg` are `reject`; `17851384777775576.jpg` is `accept`.
- The accepted paper-work candidate now carries the user's added description,
  relation `obras en papel`, and process context for the analog sketchbook
  drawing with pencils and markers related to future illustration.

### Review reliability hardening 2026-08-09

- The review endpoint now refuses an ambiguous legacy ledger id without a
  `source_id`, instead of guessing the first duplicate row. The visible editor
  always sends both identities.
- Review buttons disable while the request is in flight, network failures
  restore the controls and show an explicit unconfirmed error, and successful
  decisions show a confirmation before the view refreshes.
- The duplicate-id disambiguation suite passes (`26` bridge tests), the editor
  contract passes (`2`), Python and JavaScript syntax checks pass, and MAK was
  restarted with the hardened `hub.py` and `editor.html`. The remaining queue
  is one intentional `revise` candidate.

### Candidate learning and GTM performance 2026-08-09

- Human candidate decisions now become a bounded learning profile instead of
  disappearing into raw ledger history. `copilot.review_profile()` preserves
  accept/revise/reject counts, the dimensions attached by the user, and
  deduplicated context signals; it never promotes those signals to facts.
- The learning surface `/api/portfolio/copilot/learning` now exposes
  `candidate_reviews`. The current MAK data reports `8` reviewed candidates:
  `4` accepted, `1` revise, and `3` rejected. The accepted paper drawing is
  recorded under `process` with the user's analog/croquera description; other
  accepted context includes the already-confirmed event, artist, venue and
  collaboration records. Promotion remains `none`.
- Accepted human context is merged into copied item projections before the
  local copilot builds future suggestions. Original inbox metadata is not
  mutated. Rejected candidate decisions remain negative review memory and do
  not become relation penalties.
- The visible `#estudio-app` now displays a compact `memoria humana` summary
  next to the review queue and loads it from the same learning endpoint. This
  makes the feedback loop inspectable without opening a second tool or reading
  raw JSON.
- The GTM fit now samples at most `1024` vectors for codebook fitting when the
  archive is larger, then positions every item against that fitted topology.
  The response declares `fit.items`, `fit.total`, and `fit.sampled`. The live
  suggestions request for the 7k-scale archive completed in about `9.6s`
  including SSH transport after this change; the previous request exceeded a
  `34s` client limit. The server was restarted with the user unit
  `systemctl --user restart mak-hub.service` and is active.
- Focused validation passes: `43` tests across copilot, bridge, and editor
  contracts; Python compilation; inline JavaScript `node --check`; and
  `git diff --check`. No Watsonx/AWS call, public promotion, commit, or push
  was made. Windows changes remain intentionally uncommitted.

### Decision traceability spine 2026-08-09

- External candidate decisions now receive their own `mak-work-v1` envelope
  with a stable `work_id`, parent task, lane, evidence requirements, allowed
  decisions, fallback chain, source ids, and human owner. The review row no
  longer reuses the candidate's work envelope as if the review were the same
  operation.
- Historical review rows remain intact. The new decision index derives a
  deterministic `legacy-portfolio-review:<candidate_id>:<source_id>` work id
  for old rows and marks its traceability as derived, instead of silently
  rewriting history. New decisions use `portfolio-review:<source_id>:<ts>`.
- MAK now serves `/api/portfolio/decision-index`, a compact view of candidate
  reviews, relation feedback, and portfolio selections. Current live counts
  are `8` candidate reviews, `1` relation feedback row, and `4` selections;
  promotion remains `none`.
- The index and review surface preserve `source_id` and `work_id` together,
  so a future department can continue one thread without guessing from a
  title, duplicate ledger id, or free-text note.
- Focused validation passes (`71` tests across copilot, bridge, editor, and
  ledger contracts), Python compilation and `git diff --check`. MAK was
  restarted with the new Hub and is active. No provider call, public
  promotion, commit, or push was made.
- The read-only legacy report index now serves `/api/research/legacy-reports`.
  Its live MAK snapshot contains `950` files: `870` `paired_family`, `79`
  `quarantine`, and `1` `orphan_candidate`. `paired_family` means related
  sidecars were found, not that duplicate content was proven; no report is
  classified as valid or promotable by this index. Original reports and the
  earlier raw Watsonx review remain untouched and quarantined.
- A bounded Watsonx challenge was run against three closed report paths after
  the local structural filter. The first output was rejected as invalid because
  it omitted the common product contract; the corrected second output passed
  JSON/evidence shape but the deterministic local policy rejected the batch
  because one item had low confidence. The raw outputs remain at
  `/home/mak/plataforma/director_runs/legacy-report-challenge-20260809/`;
  common-ledger status is `reject`, promotion is `none`, and no public surface
  changed. This proves the external provider cannot bypass the local gate.

### Phase 2 curatorial topology 2026-08-09

- The copilot now separates relation evidence into two readable classes:
  `declared` for exact metadata (publication, date, artist, venue, event,
  client, collaboration, period) and `exploratory` for shared description
  terms. The latter remains a low-confidence clue and never becomes identity.
- Suggestions carry structured `evidence`, `scope`, `source_role`, and
  `candidate_role`; the editor displays the evidence facet instead of asking
  the user to trust a bare title or prose reason. The API contract is now
  `faro-portfolio-copilot-v4` and explicitly reports `promotion: none`.
- Human context still enters through the existing feedback/ledger path. This
  is not a second learning system: exact declared relations rank above textual
  coincidence, GTM remains a projection for topology, and rejection remains
  negative review memory rather than deletion.
- The existing identity graph now exposes explicit layers on nodes and edges:
  source records (`registro`), declared works (`obra` only when explicitly
  declared), entities (`entidad`), and temporal/publication context
  (`context`); unresolved media stays `candidate`. Generic null/unknown values
  no longer become fake entity nodes. Live MAK graph counts are `5919`
  `registro`, `8639` `context`, and `1125` unresolved `candidate` nodes; no
  public promotion occurred.
- Repeated relation rows are now grouped by candidate in the same response.
  `suggestions` remains backward-compatible, while `suggestion_groups` gives
  the editor one visual card per candidate with all its relation channels,
  evidence, scope, and primary feedback facet. A live 24-row response now
  renders as 23 candidate groups instead of repeating the same media card.
- MAK was updated with `copilot.py`, `hub.py`, and `iskvw/editor.html`; the
  user service is active. Live `/api/portfolio/copilot/suggestions` returns v4
  with the policy and evidence payload. Focused validation passes (`74` tests
  in the copilot/bridge/editor/ledger set), compilation, and diff checks.

### Phase 1 visual provider challenge 2026-08-09

- A closed stratified sample was created on MAK at
  `/home/mak/plataforma/director_runs/phase1-stratified-visual-20260809/`:
  one video contact sheet, two story images, and two published-media images.
  The manifest keeps local date/type as evidence and forbids visual material
  from establishing artist, venue, or event identity by itself.
- Watsonx and AWS processed the same five visual files independently. Both
  returned five atomic candidates and agreed on `record_kind` and date for
  all five files. Neither invented a non-unknown artist, venue, or event.
- Watsonx received local `revise` because two items had low confidence. AWS
  passed the deterministic candidate gate with five items. AWS required the
  MAK provider venv at `/home/mak/venv-providers/bin/python`; system Python
  failed only because `boto3` was unavailable. This is an execution-path
  fact, not a missing AWS credential.
- The AWS candidates were written as awaiting-review evidence in the common
  ledger, not as truth or public promotion. No public surface changed. Raw
  outputs remain preserved, and the normalized comparison is at
  `/home/mak/plataforma/director_runs/phase1-stratified-visual-20260809/COMPARISON.json`.
- The comparison is a contract/prudence result, not a curatorial accuracy
  score. The next useful challenge is one candidate with added human/event
  evidence, not another blind batch.

### Phase 2 human-accepted work correction 2026-08-09

- The accepted work is `17851384777775576.jpg`, not the emotional-text record.
  Its human decision is `hacer`; the declared relation is `obras en papel`,
  with analog croquera process and future-illustration context. The original
  note remains in the ledger unchanged.
- The prior provider output incorrectly called this file `story_record`
  because it followed the Instagram `stories/` path. That was a real
  classification overwrite risk, not a harmless label difference.
- `tandas.py` now reads the latest human candidate review before the local
  profile gate. An accepted human work forces product `record_kind=obra`,
  preserves context, relation, and note inside structured relations, and
  keeps the batch format `registro` so the portfolio profile remains valid.
  This changes candidate classification only; it does not promote publicly.
- The correction was copied to MAK and compiled there. A new AWS run for this
  single accepted work passed the local gate and wrote `record_kind=obra` with
  `classification_source=human` to the common ledger. The first Watsonx run
  returned invalid JSON and was safely rejected; its raw output is preserved.
- Focused `tandas` and `ledger` tests pass after the regression test. No public
  promotion, commit, or push was made.

### Live Copilot / controlled pass 2026-08-09

- The Estudio de Obra now loads all `7,044` inbox items into a visible archive
  panel without duplicating media or generating thumbnails. The visible pass is
  paginated and ordered by `fecha antigua -> nueva` by default, with an option
  for reverse order and a pass size of `10` or `20` items.
- Each card exposes its real image/video, date, content kind, open action, and
  selection action. Selecting a card records `session_id` and `pass_size`, puts
  it in the live table, makes it the active piece, and opens the copilot beside
  the media. The selection is append-only and does not promote or delete data.
- The live suggestion endpoint now defaults to the lightweight hypothesis
  engine. GTM/elastic map calculation is optional with `?map=1`; it is not run
  for every click. This prevents the 7,044-item map from blocking a human pass.
- A deployment bug in that lightweight path was fixed: `source_position` is now
  explicitly empty when the optional map is not requested. MAK was updated and
  `mak-hub.service` is active. Live verification: inbox `200` / `7,044` items,
  portfolio `200`, copilot `200` in about `1.65s`, schema `faro-portfolio-copilot-v4`,
  `23` suggestion groups, map engine `not_requested`.
- Focused validation passes for the bridge/editor suite (`35` tests) and
  `hub.py` compiles locally and on MAK. No real selection was fabricated during
  deployment; the next controlled pass is the user's own ten selections.
- After the first live clicks, the user reported that reasons were not clear
  and the repeated `mesa` label made the frame confusing. The editor now keeps
  the pass strip in one horizontal filmstrip, labels a selected card
  `seleccionada`, expands each grouped suggestion into explicit relation rows
  with evidence, and disables a feedback button while its write is in flight.
  This prevents ambiguous repeated clicks without changing the append-only
  ledger history. MAK received the updated editor and the service is active.
- The user then defined the intended interaction: suggestions belong inside
  the active piece, a colored border marks them, one click accepts and turns
  green, and double click opens the suggested work. The live copilot now renders
  up to six suggestion cards around the active media in that same canvas; the
  former lower suggestion section is hidden. Single/double click timing is
  guarded, accepted cards return green, and the previous per-relation buttons
  no longer compete for attention. JS syntax, focused tests, remote page
  markers, and active MAK service were verified after deployment.
- The next live test found that a suggested target could also remain visible as
  an orbit card behind it. Suggestion targets are now deduplicated and matching
  orbit cards are hidden. Suggestion cards are draggable inside the canvas with
  pointer input; their positions persist for the active source during the
  session, and a drag no longer triggers acceptance. MAK was redeployed and
  the service is active after JS syntax, focused tests, and remote marker checks.
- The user clarified that a click must open a decision popover, not silently
  accept. The active-canvas card now opens an anchored popover with `aceptar
  vínculo`, `rechazar vínculo`, and `descartar · no es obra`; double click still
  opens the target. `descartar` uses the existing selection ledger path with
  `decision_scope=record` and `reason_code=no_es_obra`, preserves media, and
  excludes the target from future copilot suggestions. The click/drag boundary
  remains explicit and no real discard was fabricated during deployment.

### Mesa scene engine and contextual popover 2026-08-09

- The replacement `iskvw/mesa_montaje.js` now uses a persistent scene engine:
  it mounts the page once, updates nodes/edges/camera in place, and uses
  `requestAnimationFrame` for camera motion. A click no longer replaces the
  page with `innerHTML`, so selection does not force a visible refresh.
- The old right inspector is removed from the active renderer. One contextual
  popover appears next to the selected node with `poner al centro`,
  `relacionar`, `descartar · no es obra`, and explicit `abrir`.
- Suggestion popovers expose `poner al centro`, `abrir`, `aceptar`, and
  `rechazar`. SVG lines are decorative only; they have no click decision path.
  Selection is animated through border/scale/glow, while the camera remains a
  separate gesture.
- The scene contract now declares `decision_surface: scene_popover` rather
  than `inspector`. MAK returned HTTP `200`, `10` records, `9` relations and
  `scene_popover` after service restart.
- MAK inspection of the live files found `14` relation feedback rows, all
  `accept`, and `7` record-level `descartar` rows with `reason_code=no_es_obra`.
  The acceptance path was reaching MAK, but the UI had no note field and the
  old interaction could repeat writes. The current popover now includes a
  1,000-character human note for relation and discard decisions, sends it to
  the existing ledger/JSONL paths, and disables accept/reject while writing.
- Local checks passed: `38` bridge/editor tests, Node syntax check, Python
  compilation, and diff check. No browser tab was opened and no user
  interaction was fabricated.

## Current boundaries and pauses

### New active direction: Mesa de Montaje

- The current live-card implementation is experimental and must not receive
  more interaction patches. The replacement plan is in
  `context/PLAN_MESA_DE_MONTAJE.md`.
- The key correction is semantic: a media item is a `registro`, not an
  automatic `obra`; suggestions are relations over existing records; event,
  venue, artist and client are context entities.
- The next implementation must rebuild the Estudio as one fixed scene with a
  timeline, unique nodes, relation halos, and one in-canvas inspector. It must
  separate navigation, pass selection, relation decisions and record
  classification. Do not add another lower panel, popup layer, or duplicate
  card renderer.

- No new framework, ledger, graph, policy engine, or duplicate tool.
- No automatic public promotion, contact, Instagram automation, or deletion
  of rejected material. Rejection is a traceable decision, not disappearance.
- No mass curation of 7,044 items. Use a stratified sample and preserve a
  manifest.
- The user explicitly reopened the README text layer on 2026-08-09. `README.md`
  now carries the current identity, map, branches, MAK boundary, work envelope,
  lanes, provider roles, and autonomy criterion from the supplied brief.
  `arte-ascii-readme.svg` was regenerated through the existing tool; the
  double-cup geometry remains protected. Do not redesign the vessel without a
  new artistic instruction.
- Domain migration is last. First keep the archive, organism, RD surface, and
  export independent of iskvw.cl.
- The old general plans are not active: `PLAN.md`,
  `PLAN_ANUAL_2026-2027.md`, `PROYECCION.md`, and the deleted
  `context/PLAN_CIERRE_PRE_COMPACT.md` are historical references only.

## Historical next action - 2026-08-09

Do not start with Git cleanup, branch deletion, a full test suite, or another
mass audit. The first vertical circuit is complete. The immediate user-facing
checkpoint is the five-card visual review in `/portafolio/`; continue with its
evidence, not another blind batch:

1. Hard-refresh `/portafolio/`, open the visible `revisión humana` strip, and
   review the five AWS candidates and their exact manifest rows; the source id
   now travels with each decision and only that candidate is affected.
2. Attach explicit human context to one candidate at a time; a username is not
   an artist, and a story is not an event merely because a model names one.
3. If one candidate gains date, venue, artist, producer, or XIO evidence, run
   one bounded Watsonx triangulation for that candidate only. Do not rerun the
   rejected mixed batch.
4. Keep hypotheses separated by date, visual, audio, event, venue, artist,
   client, and collaboration. Use XIO only where an actual event/setlist
   source exists; do not pretend one event is a universal source.
5. Send every result through the local judge/deterministic fallback and record
   candidate, review, refutation, or archive in the common ledger. No public
   promotion.
6. Keep the Hub action-oriented: show the media and one next decision, not a
   wall of model prose.

The extra Capataz checkout has already been preserved and removed. After this
circuit, make only one deliberate mechanical promotion when the evidence is
ready; do not create small PRs for cosmetic work. The domain remains last.

## Session close rule

At the end of every future session, update this file with measured facts, not
intentions: exact branch/commit, MAK process, files changed, tests run, external
calls, failures, user decisions, and one next action. Keep historical detail
in `_logs/cauce_director/20260805/`; keep this file short enough that a fresh
agent can actually read it.

## Correccion de sugerencias y descarte 2026-08-09

- La escena ya no propone candidatos cuyo ultimo estado sea `descartar` ni
  relaciones cuyo ultimo feedback sea `reject`; el descarte permanece en
  `selections.jsonl` y el ledger, no se borra.
- La mesa separa hipotesis nuevas de vinculos ya aceptados y oculta rechazos
  del conjunto activo. El contador del popover muestra solo sugerencias nuevas.
- Descartar desde el popover retira la pieza de la escena actual y centra la
  siguiente pieza disponible sin recargar la pagina. Si no quedan piezas,
  muestra un cierre de pasada; no vuelve a presentar el registro descartado.
- Verificacion local: `node --check`, `pytest` focalizado (`56 passed`) y
  `git diff --check`. MAK activo; escena remota sin descartados visibles y JS
  servido con `pendingRelations` y `advanceAfterDiscard`.
- Pendiente real: una prueba humana en `/portafolio/` para confirmar el avance
  automatico con la interaccion visible. No iniciar otra tanda externa antes
  de esa prueba.

## Vinculos estructurados 2026-08-09

- La decision de una sugerencia ya no depende de escribir un comentario: el
  popover ofrece facetas estructuradas disponibles (`misma obra`, `registro
  emocional`, `fecha`, `evento`, `venue`, `artista`, `cliente`, `colaboracion`,
  `concepto/texto`, etc.). El comentario queda opcional para memoria adicional.
- La faceta elegida se conserva en el feedback existente y alimenta el perfil
  de aprendizaje; no se creo otro ledger ni otra taxonomia paralela.
- Feedback y conexiones identicas ahora son idempotentes: no se vuelven a
  escribir si el usuario pulsa aceptar varias veces con la misma razon.
- MAK activo; escena remota servida con selector de faceta, un vinculo
  aceptado y ocho hipotesis nuevas en la muestra consultada.

## Medicion de aprendizaje antes de la pasada 2026-08-09

- MAK recibio `19` feedbacks historicos de relacion, pero `5` eran
  duplicaciones exactas. La normalizacion de lectura los deja en `11` señales
  unicas sin borrar los JSONL antiguos.
- Perfil recalculado: `text` peso `8.0`, `publication` `6.0`, `date` `1.5`.
  Es una mejora de señal, no una prueba de que el modelo ya clasifique bien:
  todavia no hay rechazos de relaciones y el perfil esta sesgado hacia texto y
  carrusel por la primera ronda.
- Las decisiones externas ya aportan contexto mas valioso: `4 accept`, `1
  revise`, `3 reject`, con señales aceptadas de colaboracion, proceso, artista,
  fecha y venue. Esas señales solo reordenan candidatos; no se promueven como
  hechos.
- Tests focalizados actuales: `58 passed`. Antes de usar Watsonx/AWS en una
  tanda mayor, hacer una pasada corta que incluya al menos una aceptacion y un
  rechazo de facetas distintas.

## Carruseles como unidad 2026-08-09

- `publicacion_id` es ahora una frontera de obra editorial: los medios del
  mismo post dejan de producir relaciones entre si, aunque conserven sus
  archivos, indices y metadata.
- La escena expone `publication_group` con sus medios, indice y estado; el
  popover lo presenta como una sola obra editorial, no como siete sugerencias
  repetidas.
- MAK verificado con un carrusel real de `7` medios: ningun hermano del mismo
  `publicacion_id` aparece como candidato y el grupo queda disponible en la
  pieza activa.
- Siguiente bloque, no mezclarlo aun: leer texto de ubicacion en stories como
  evidencia de venue/lugar. Debe entrar como dato de registro, no como obra ni
  como afirmacion automatica.

## Interfaz de archivo agrupada 2026-08-09

- El archivo visual antiguo tambien agrupa por `publicacion_id`: un carrusel
  aparece como una tarjeta editorial, no como medios individuales.
- La tarjeta muestra una galeria con los archivos existentes, permite `abrir
  carrusel` y `seleccionar carrusel`; seleccionar aplica la decision a todos
  sus medios sin duplicar la obra en la mesa.
- Los hermanos del mismo post ya no aparecen como vecinos ni sugerencias. La
  agrupacion fue desplegada en MAK y validada con un carrusel real de `7`
  medios. La ubicacion de stories queda como fase posterior.

- Los registros con decision `descartar` ahora se excluyen del archivo visual.
  En un carrusel se ocultan solo los medios descartados y permanecen los
  miembros no descartados.

## Agrupacion por misma obra y lentes del copiloto 2026-08-09

- Una relacion aceptada con faceta `obra` crea una agrupacion visual temporal:
  sus piezas se muestran como una sola tarjeta compuesta y dejan de ocupar
  nodos separados. La evidencia y los archivos originales permanecen.
- La mesa ahora ofrece lentes reales para recargar sugerencias: `copiloto`,
  `fecha`, `concepto`, las facetas declaradas y `shuffle`. El shuffle cambia
  la muestra; no cambia decisiones ni crea hechos.
- La agrupacion se sostiene por feedback humano y se puede deshacer si la
  relacion se rechaza; no se inventa una obra nueva en el ledger.

## Correccion de arranque y carruseles de candidatos 2026-08-09

- Se encontro un bug real: el arranque elegia el primer archivo con media aun
  si estaba `descartar`, y la escena podia mostrar hermanos de un mismo post
  como candidatos separados.
- El arranque ahora omite descartados; la escena devuelve una unidad por
  `publicacion_id` tambien para candidatos y expone su galeria completa.
- Los descartados se excluyen de la galeria del carrusel y una relacion
  repetida sobre sus medios se fusiona en una sola arista con sus miembros.

## Clasificacion individual en la pieza 2026-08-09

- El popover de cada pieza ahora contiene toggles independientes de relacion:
  capa `RD/iskvw/MAK/personal/research`, propiedad, proposito, naturaleza y
  formato.
- El contexto puede marcarse como `artista`, `venue`, `evento`, `cliente`,
  `colaboracion` o `registro`, con nombre libre; por ejemplo `artista + dref`.
- Se persiste en `classifications.jsonl` mediante el contrato existente y no
  crea una conexion ni exige candidato. La seleccion queda disponible para
  la siguiente escena y para el indice del archivo.

## Diseno visual del popover 2026-08-09

- El popover ya no repite la pieza con una imagen grande: conserva una
  miniatura de anclaje y deja la obra visible en la mesa.
- Las acciones usan una composicion de herramientas con iconos y etiquetas
  breves: centro, relacionar, abrir y retirar. El comentario no ocupa la
  pantalla; solo aparece bajo demanda dentro de una decision de vinculo.
- Las sugerencias son tarjetas visuales con miniatura, destino y evidencia.
  El hover amplia la miniatura sin abrir otra ventana.
- El filtro local oculta del conjunto principal las coincidencias de texto
  exploratorias y debiles. Si solo existen, la interfaz lo dice en vez de
  presentarlas como relaciones utiles.
- En la pieza central, `relacionar` abre el cajon de sugerencias; no intenta
  relacionar la pieza consigo misma ni muestra un mensaje ambiguo.
- Verificacion: `node --check iskvw/mesa_montaje.js`, editor focalizado `2
  passed`, servicio MAK `active`, HTTP sirve los nuevos marcadores.

## Next action

Probar en `/portafolio/` una sugerencia con evidencia declarada y otra pieza
sin evidencia fuerte. Confirmar que la primera muestra miniatura y acciones,
que el comentario solo se abre al decidir, y que la segunda explica por que
no inventa una sugerencia. No iniciar otra tanda externa antes de esa prueba.

## Revision de jerarquia visual 2026-08-09

- Se retiro el titular abstracto `una pieza, sus relaciones, ninguna copia`.
  El encabezado ahora identifica la superficie como `MAK · Estudio de obra`
  y la mesa como `mesa de montaje`.
- El popover se rehizo como composicion de dos columnas: lectura de la pieza
  a la izquierda y clasificacion/acciones a la derecha. Las sugerencias
  ocupan el ancho completo como galeria visual.
- La misma estructura se aplica al detalle de una sugerencia: evidencia a la
  izquierda y decision a la derecha. En pantallas estrechas vuelve a una sola
  columna sin perder el orden.
- Verificacion: editor focalizado `2 passed`, `node --check`, `git diff
  --check`; MAK `mak-hub.service` activo; HTTP confirma titulo, encabezado,
  columnas y CSS servidos.

## Next action

Hacer una unica prueba visual humana en MAK con una pieza que tenga evidencia
declarada. Si la composicion funciona, continuar con la curatoria; no volver
a abrir el layout por microajustes sin una falla observada.

## Correccion de redundancia visual 2026-08-09

- Se retiro la miniatura de la pieza seleccionada del popover: esa pieza ya
  esta visible en la mesa y la miniatura tapaba justamente el objeto de
  lectura.
- El popover conserva identidad, fecha, formato, descripcion y decisiones;
  las miniaturas quedan reservadas para sugerencias de otras piezas y para el
  detalle de un vinculo.
- Verificacion: editor focalizado `2 passed`, `node --check`, `git diff
  --check`; MAK `mak-hub.service` activo y HTTP confirma que la miniatura
  redundante no se sirve.

## Next action

Probar el popover de la pieza central y comprobar que no cubre su imagen. No
hacer otro ajuste visual hasta observar una falla concreta.

## Correccion de columna fantasma 2026-08-09

- La identidad del registro aun conservaba una primera columna vacia de 72px
  despues de retirar la miniatura. Esa reserva creaba el bloque negro y
  ensanchaba el popover.
- Se elimino el nodo vacio del markup y la identidad ahora es una sola columna.
- MAK reiniciado; `2 passed`, `node --check`, `git diff --check` y verificacion
  HTTP confirman que la columna fantasma no se sirve.

## Next action

Volver a probar una pieza central en `/portafolio/`; si ya no tapa la seleccion,
seguir con uso real y no continuar con microajustes.

## Eliminacion de columna vacia 2026-08-09

- El bloque rojo del usuario correspondia a una columna de contexto sin
  contenido: solo mostraba `ver descripcion original`.
- Se elimino ese `details` y la columna ya no se renderiza cuando el registro
  no tiene descripcion, nota de carrusel ni agrupacion de obra.
- En ese caso identidad y decisiones ocupan una sola columna; si existe
  contexto real, se mantienen dos columnas con contenido real.
- MAK reiniciado; `2 passed`, `node --check`, `git diff --check` y HTTP
  confirman `mesa-popover-grid-single` y ausencia del bloque vacio.

## Next action

Probar una story sin descripcion y otra pieza con descripcion. Confirmar que
la primera ya no crea un lado negro y que la segunda muestra el texto real,
no un titulo vacio.

## Popover de un solo bloque 2026-08-09

- El usuario aclaro que no queria columnas internas: el popover debe ser el
  bloque compacto a la derecha de la pieza, no una superficie que se extiende
  a izquierda y derecha sobre las imagenes.
- Se elimino la grilla interna completa, se redujo el ancho a `420px` y todo
  el contenido ahora fluye en una sola columna.
- La tarjeta de detalle de una sugerencia tambien usa un flujo unico; conserva
  su miniatura porque representa otra pieza, no la seleccionada.
- Verificacion: editor focalizado `2 passed`, `node --check`, `git diff
  --check`; MAK `mak-hub.service` activo y HTTP confirma `mesa-popover-flow`.

## Next action

Hacer `Ctrl+F5` y comprobar una pieza central. Verificar que el popover quede
compacto a la derecha y no cubra las tarjetas vecinas; no abrir otra ronda de
layout hasta observar una falla.

## Composicion codificada por zonas 2026-08-09

- El popover ya no tiene columnas internas ni contenido a izquierda/derecha.
  Es un solo flujo compacto de `420px`, anclado al borde derecho de la pieza.
- Las seis dimensiones son una grilla compacta; las opciones de la dimension
  activa son otra grilla; el texto real queda limitado y las coincidencias
  debiles no ocupan espacio.
- Las cuatro acciones de pieza son iconos con `aria-label` y `title`, sin
  texto al lado: centro, relacionar, abrir y retirar.
- La sugerencia solo abre una galeria cuando hay candidatos utiles; el bloque
  vacio de sugerencias desaparece.
- MAK reiniciado; `2 passed`, `node --check`, `git diff --check` y HTTP
  confirman flujo unico, ancho compacto y anclaje a la derecha.

## Next action

Hacer `Ctrl+F5` y validar visualmente las cuatro zonas marcadas por el usuario:
dimensiones, opciones, texto y acciones. No agregar mas estructura hasta esa
prueba.

## Mapa topologico GTM conectado 2026-08-09

- El editor dejo de calcular una orbita radial como posicion principal. La
  escena ahora consume coordenadas de la proyeccion GTM existente: cada nodo
  recibe su posicion relativa, confianza y capa; los choques locales se
  separan solo para conservar legibilidad sin alterar la coordenada de origen.
- `_portfolio_scene` entrega un mapa acotado a los nodos visibles, con `schema`,
  `engine`, `fit` y `items`; el ajuste completo se calcula/cachea en MAK y no
  se manda al navegador como 7044 registros.
- El contrato de escena declara `decision_surface: map_hud`,
  `projection: gtm` y `feedback_updates_topology: true`. Las decisiones siguen
  entrando por el ledger existente; no se creo un grafo ni una base paralela.
- La superficie visible identifica el editor como `mapa de relaciones`,
  muestra las capas `obra`, `registro`, `entidad/contexto` y `candidato`, y
  conserva el HUD contextual solo como herramienta del nodo seleccionado.
- Verificacion local: `pytest -q tests/test_copilot.py
  tests/test_mak_portfolio_bridge.py tests/test_iskvw_editor_contract.py` ->
  `65 passed`; `node --check iskvw/mesa_montaje.js`; `py_compile` de Hub y
  contrato; `git diff --check` sin errores.
- Verificacion MAK: `mak-hub.service` `active`; escena real para
  `18108033539083566.jpg` devuelve `map_engine=elastic_latent_grid`,
  `projection=gtm`, `map_items=10`, `fit_total=7044`, `decision_surface=map_hud`.

## Next action

Probar visualmente el mapa en MAK y observar una decision real. El siguiente
bloque no es otro ajuste de CSS: implementar aprendizaje incremental tipo GNG
sobre las decisiones aceptadas/rechazadas y reflejar el cambio de vecindad en
la siguiente escena. No llamarlo deep learning ni promoverlo hasta medirlo.

## Orden rapido separado de relacion 2026-08-09

- El editor ahora abre en modo `ordenar`: click en un nodo lo selecciona sin
  abrir un popup; se pueden acumular nodos y la barra contextual ofrece `obra`,
  `registro`, `revisar` y `descartar`.
- `relacionar` queda como modo explicito o como resultado de doble click. Asi
  la primera pasada no obliga a resolver parejas ni a leer texto de cada
  sugerencia.
- Las tres primeras decisiones usan `/api/portfolio/classify-batch` y el
  campo `triage` del contrato existente. `descartar` conserva la evidencia y
  usa la seleccion de registro existente para sacar el nodo de la escena.
- Verificacion local: `pytest -q tests/test_copilot.py
  tests/test_mak_portfolio_bridge.py tests/test_iskvw_editor_contract.py` ->
  `66 passed`; `node --check iskvw/mesa_montaje.js`; `py_compile` de Hub.
- Verificacion remota: `mak-hub.service` `active`; `/portafolio/mesa_montaje.js`
  sirve `data-editor-mode`, `classify-batch` y `mesa-order-hud`; el endpoint
  rechaza un lote vacio sin escribir datos.

## Next action

Probar una seleccion de 3 nodos en modo `ordenar` y marcarla como `registro`.
Luego medir si el siguiente grupo cambia por la señal `triage`. Solo despues
implementar el aprendizaje GNG; no volver a convertir la relacion en el primer
paso.

## Aprendizaje local y primera tanda externa 2026-08-09

- El bloque siguiente se implementó sin esperar más input humano. `copilot.py`
  ahora deriva `faro-ordering-learning-v1` desde clasificaciones `triage` y las
  selecciones históricas `seleccionar`/`descartar`. Usa prior de Laplace y hasta
  128 vecinos etiquetados en el vector local; no crea otra base, ledger ni
  framework.
- Cada posición GTM entrega `triage_prediction` con recomendación, confianza,
  probabilidades, vecinos y conteos. `hub.py` lo entrega en la escena y el HUD
  muestra la señal solo como sugerencia breve. El mapa conserva la proyección
  GTM; esto es aprendizaje por vecindad sobre GTM, no debe llamarse todavía
  GNG ni deep learning.
- La primera lectura real en MAK tiene 14 decisiones etiquetadas: `work=4`,
  `discard=10`, `record=0`, `review=0`. La primera versión daba demasiada
  seguridad a `discard`; se corrigió para que una sola clase observada siempre
  quede en confianza `baja`, aunque tenga una probabilidad alta por prior.
- MAK responde la escena real en aproximadamente 2.3 segundos medidos en tres
  solicitudes consecutivas. `mak-hub.service` de usuario sigue `active`.
- Se ejecutó una tanda externa acotada sobre
  `18108033539083566.jpg`: Watsonx produjo solo un desconocido de contexto y
  cero hipótesis normalizadas; AWS produjo observaciones visuales de baja
  confianza (`bottle`, `cap`, `blender`, colores y composición) sin inventar
  artista, venue o evento. Se guardaron en los archivos existentes
  `copilot_external.jsonl` y `vision_features.jsonl`; ninguna salida se
  promovió.
- Verificación local completada: tests focalizados de copilot, bridge e editor;
  `node --check iskvw/mesa_montaje.js`; `py_compile` de Hub y copilot; `git diff
  --check`. Verificación MAK: endpoint de escena, estado de proveedores y
  reinicio del servicio confirmados.
- La siguiente iteración ya está desplegada: `faro-ordering-field-v1` aplica
  una atracción suave hacia anclas de clases humanas con al menos dos ejemplos.
  En la escena real las anclas son `work=4` y `discard=10`; movió suavemente
  `6042` de `7044` nodos con desplazamiento medio `0.006343`. Comparado con
  GTM sin campo, conservó `74.61%` de las vecindades de una muestra de 256,
  redujo el área envolvente `9.95%` y tuvo desplazamiento máximo `0.032752`.
  No mueve piezas etiquetadas, no elimina registros y no altera el ledger.
- Se comprobó además en dos escenas reales (`17934891079242401.jpg` y
  `18117638056796755.jpg`): ambas entregan 10 registros, 14 decisiones
  etiquetadas y el mismo campo medido; no dependen de que la pieza activa sea
  la primera lectura externa.

## Calibración de masa crítica 2026-08-09

- La lectura de la escena reveló que `14/7044` etiquetas no bastaban para
  mostrar confianza alta aunque los vecinos locales coincidieran. Se añadió
  `ORDER_MIN_COVERAGE=0.01`: MAK necesita aproximadamente 71 decisiones antes
  de activar confianza media/alta o mover el campo elástico.
- Estado actual verificado en MAK: cobertura `0.001988`,
  `learning_ready=false`, `alta=0`, `media=0`, `baja=7044`, campo con
  `moved_items=0`. Esto reemplaza la medición anterior del campo activo; la
  medición de `6042` movimientos queda como experimento histórico, no como
  comportamiento actual.
- El HUD ahora declara `falta masa crítica` en vez de presentar una seguridad
  falsa. Las clases ausentes siguen visibles como `record` y `review`; no se
  inventan desde AWS, Watsonx ni texto libre.

## Tanda visual multimodal 2026-08-09

- Se ejecutó una tanda nueva sobre tres piezas no descartadas:
  `18122826199703813.mp4`, `18091692476565937.mp4` y
  `18120751399766397.jpg`. Watsonx respondió las tres como candidatos sin
  hipótesis normalizadas y con desconocidos explícitos; no se promovió nada.
- AWS leyó inicialmente la imagen y rechazó los dos videos porque el bridge no
  tenía still. La causa fue un bug real: el bridge encontraba el video, luego
  sobrescribía esa ruta con `None` al buscar posters antes de llamar al
  generador.
- Se corrigió `hub.py` para reutilizar la herramienta existente
  `cultura/mak_curatoria/percepcion.py`, generar un único contact sheet 3x3 por
  video y cachearlo en `/home/mak/portfolio_media/media/_contact_sheets/`.
  No se creó otra herramienta ni se almacenaron fotogramas sueltos.
- Tras la corrección AWS leyó ambos videos con `evidence_kind` explícito
  `video_contact_sheet`; uno quedó en confianza alta y el otro alta en la
  segunda lectura. El sheet se sirve por MAK con HTTP 200. Quedaron 2 sheets
  cacheados y se eliminaron los archivos de diagnóstico temporales.
- La instrucción visual ahora distingue `video_contact_sheet` de `still_image`
  y evita llamar “imagen estática” a los fotogramas muestreados.
- Verificación: tests focalizados pasan, `py_compile` de Hub, estado del
  servicio `active`, ejecución AWS posterior y HTTP 200 del media bridge.

## Impacto visual medido 2026-08-09

- Se comparó el mapa real de `7044` registros con y sin las observaciones
  visuales guardadas para cuatro piezas. La media de desplazamiento fue
  `0.000020`, la máxima `0.093059` y la estabilidad de vecinos en una muestra
  de 256 fue `99.61%`.
- Las tres piezas nuevas movieron localmente `0.027869`, `0.093059` y
  `0.016856`; el resto del archivo permaneció prácticamente estable. La
  evidencia visual entra como señal débil del vector, nunca como artista,
  venue, evento o cliente.

## Next action

Usar las observaciones visuales ya guardadas como evidencia débil del mapa y
no repetir la tanda externa sobre las mismas piezas salvo que cambie la
evidencia. La siguiente expansión debe trabajar con nuevas marcas humanas
`record`/`review`, no inventarlas desde la visión.

## Next action

No pedir otra clasificación manual todavía. El bloque topológico suave está
cerrado para esta tanda; la próxima expansión debe ser una comparación contra
una escena con nuevas marcas `record`/`review`, no otra ronda de CSS. El campo
actual es una proyección reversible, no una verdad del archivo.

## Next action

Continuar con una tanda externa nueva solo para generar evidencia candidata y
conservar el aprendizaje en baja confianza hasta superar la masa crítica. No
activar el campo ni declarar autonomía estadística antes de `1%` de decisiones.

## Tanda externa de incertidumbre 2026-08-09

- Se eligieron tres registros nuevos y no descartados sin repetir los cinco
  identificadores ya procesados: una historia sin descripción
  (`18114751558928682.mp4`), un reel visual de Marlon Breeze en Lollapalooza
  (`18097295537071643.mp4`) y un reel promocional de RD
  (`18125627794588368.mp4`).
- Watsonx respondió en los tres casos sin error, con `0` hipótesis
  normalizadas y `2`, `1` y `2` desconocidos respectivamente. Es evidencia de
  que no debe inventar relaciones cuando el sobre no alcanza, no un fracaso
  que se deba ocultar.
- AWS respondió en los tres casos usando `video_contact_sheet`: confianza
  `high`, `high` y `low`. Se almacenaron tres nuevos sheets 3x3, sin fotogramas
  sueltos ni promoción al ledger.
- Estado verificable posterior: `external rows=9`, `unique=8`,
  `vision_features rows=10`, `unique=7`, `contact_sheets=5`, servicio MAK
  `active`. El learner sigue en `14/7044`, cobertura `0.001988`,
  `learning_ready=false`, `0` altas, `0` medias y `7044` bajas.
- Comparación GTM con/sin las siete observaciones visuales: desplazamiento
  medio `0.000045`, máximo `0.111464`, sin movimiento del campo de decisiones.
  La señal visual altera vecindades locales, pero no justifica una identidad.

## Next action

No repetir proveedores sobre estas tres piezas ni convertir sus desconocidos en
categorías. La siguiente fase útil es instrumentar el registro/review humano
en la misma superficie del editor y alcanzar una muestra mínima de decisiones
`work`, `record`, `review` y `discard`; recién entonces medir si el campo GTM
aprende. Mantener AWS/Watsonx como productores de evidencia aislada y no como
jueces de promoción.

## Puente AWS a Watsonx 2026-08-09

- Se corrigió el sobre existente de `inference_prompt`: cuando una pieza ya
  tiene observaciones AWS, Watsonx recibe `visual_observations` acotadas junto
  a fecha, publicación y descripción. No recibe una identidad inferida ni una
  imagen convertida en hecho.
- La política del prompt ahora exige que visión sea señal débil y que la falta
  de convergencia produzca desconocidos en vez de una relación inventada.
- Verificación focalizada: `68` tests pasan, `py_compile` y `git diff --check`
  pasan; `copilot.py` fue desplegado a MAK y `mak-hub.service` quedó `active`.
- Corrida real de integración en una pieza nueva
  (`18081505238653333.mp4`): AWS produjo un contact sheet 3x3 con confianza
  `high`; inmediatamente después Watsonx respondió sin error y sin hipótesis
  normalizadas. El puente funciona, pero respeta la incertidumbre.
- Estado posterior en MAK: `external rows=13`, `unique=12`,
  `vision_features rows=14`, `unique=11`, `contact_sheets=8`; las decisiones
  humanas siguen en `14/7044` y la cobertura continúa `0.001988`.

## Next action

No confundir el puente multimodal con aprendizaje terminado. Mantener los
resultados como candidatos y construir la próxima ronda alrededor de una
superficie de revisión humana `record/review`, cuyos cuatro destinos ya existen
en el editor. El campo GTM debe permanecer inmóvil hasta superar `1%` de
decisiones etiquetadas.

## Semilla humana de aprendizaje 2026-08-09

- Se añadió `ordering_seed` al motor existente. No clasifica ni decide: elige
  hasta `24` registros sin etiqueta en un recorrido balanceado por tipo de
  contenido, mes, descripción y presencia de evidencia visual.
- Cada candidato queda marcado como `human_candidate` con alcance
  `record_or_review`; conserva `item_id`, fecha, publicación y disponibilidad
  de media para que la revisión pueda hacerse desde el editor sin asignar una
  categoría por anticipado.
- La superficie `/api/portfolio/copilot/learning` ya entrega la semilla y
  explicita que faltan las etiquetas `record` y `review`. Verificación MAK:
  `seed_count=24`, `14/7044`, cobertura `0.001988`, `learning_ready=false`.
- Se ejecutó otra tanda acotada AWS → Watsonx sobre tres reels nuevos con
  metadata fuerte: Sweettooth, archivo de Harry Nach y outro de Drefquila en
  Movistar Arena. AWS respondió `high` en los tres contact sheets; Watsonx
  terminó sin error con `0` hipótesis y `1/1/2` desconocidos.
- Estado MAK posterior: `external rows=16`, `unique=15`, `vision rows=17`,
  `unique=14`, `contact_sheets=11`, servicio `active`. Tests focalizados:
  `69` pasan.

## Next action

Conservar la semilla como interfaz de revisión, no rellenarla con decisiones
automáticas. La siguiente fase es conectar esos `24` candidatos al flujo visual
del editor y registrar una primera muestra humana equilibrada; hasta entonces
AWS y Watsonx siguen siendo proveedores de evidencia, no maestros del orden.

## Semilla conectada al editor 2026-08-09

- La mesa GTM ahora tiene una acción única `revisión humana`. Consulta la
  semilla viva, lleva un candidato sin etiqueta al centro, lo deja seleccionado
  y muestra las cuatro decisiones `obra`, `registro`, `revisar` y `descartar` en
  el HUD de ordenar; no abre una tabla ni crea una relación.
- La selección se vuelve a pedir en cada avance, por lo que un candidato
  etiquetado deja de aparecer en la siguiente semilla. La media sigue visible
  en la mesa y la decisión se guarda por el endpoint existente de clasificación.
- MAK sirve el JS actualizado, el servicio permanece `active`, la API entrega
  `24` candidatos con `review_scope=record_or_review` y la verificación focalizada
  queda en `69` tests, `node --check` local y `git diff --check` correctos.
- La tanda externa de esta fase procesó tres reels nuevos (Sweettooth,
  Harry Nach y Drefquila/Movistar Arena) con AWS primero y Watsonx después:
  AWS `high` en los tres, Watsonx `0` hipótesis y `1/1/2` desconocidos.

## Next action

El sistema ya puede entregar un candidato visual por decisión humana sin
mezclarlo con relacionar. No fabricar todavía esas decisiones: la siguiente
medición válida requiere que el usuario marque una muestra. Mientras no ocurra,
mantener el campo GTM inmóvil y usar proveedores solo para evidencia nueva y
acotada.

## Tanda de evidencia para semilla 2026-08-09

- Se procesaron tres candidatos nuevos de la semilla sin repetir piezas:
  `17871572163624966.mp4`, `18600090475048906.jpg` y
  `18107658344073381.mp4`. AWS corrió primero para que Watsonx recibiera la
  observación visual guardada.
- AWS respondió `low`, `high`, `high`; Watsonx terminó sin error con `0`
  hipótesis normalizadas y `1/1/1` desconocidos. La salida sigue siendo
  evidencia candidata, no etiqueta.
- MAK queda con `external rows=19`, `unique=18`, `vision rows=20`,
  `unique=17`, `contact_sheets=13`; la semilla permanece en `24` y el learner
  en `14/7044`, cobertura `0.001988`, `learning_ready=false`.

## Next action

La siguiente fase no es seguir acumulando texto de proveedores: es observar una
primera decisión humana sobre la semilla ya conectada, y medir si el registro se
guarda, desaparece de la siguiente semilla y altera solo el campo permitido.
Hasta entonces, continuar solo con evidencia externa que cubra medios nuevos y
no convertir volumen en aprendizaje.

## Perfil de rendimiento externo 2026-08-09

- Se añadió al endpoint de aprendizaje un resumen derivado, no otro ledger:
  `external_evidence` informa filas, piezas únicas, cruce AWS/Watsonx,
  hipótesis normalizadas, desconocidos, confianza visual, tipo de evidencia y
  promoción. Su promoción es siempre `none`.
- Verificación MAK después de la implementación: `external_rows=19`,
  `external_unique=18`, `vision_rows=17`, `vision_unique=17`,
  `cross_provider_items=17`, `normalized_hypotheses=0`, `unknowns=29`.
- Se ejecutó otra tanda acotada en tres historias nuevas
  (`17977292262022460.mp4`, `18445318405139883.mp4`,
  `18124869271628978.mp4`): AWS `high/high/high` con `3/0/2` desconocidos;
  Watsonx sin error, `0` hipótesis y `1/1/1` desconocidos.
- Estado final de la tanda: `external rows=22`, `unique=21`, `vision rows=23`,
  `unique=20`, `contact_sheets=16`, servicio MAK `active`, semilla `24` y
  decisiones `14/7044`. Tests focalizados: `70` pasan.

## Next action

El sistema ya mide cuánto rinde cada proveedor y evita llamar “aprendizaje” a
una acumulación de respuestas. La siguiente etapa de alto valor es consumir la
semilla humana en el editor y comprobar el ciclo completo; no aumentar el
volumen externo mientras la tasa de hipótesis siga en cero.

## Avance de flujo continuo 2026-08-09

- La acción `revisión humana` ahora avanza automáticamente al siguiente
  candidato después de guardar `obra`, `registro`, `revisar` o `descartar`.
  Si el usuario empieza a seleccionar nodos manualmente, el avance automático
  se desactiva para no secuestrar el modo ordenar.
- Esto convierte la semilla en una pasada continua de una decisión por vez:
  media visible, cuatro destinos claros, persistencia por endpoint existente y
  siguiente candidato sin refrescar ni volver a buscar.
- MAK sirve el JS actualizado; comprobación HTTP confirma la función, el
  endpoint de aprendizaje y el autoavance; servicio `active`; tests focalizados
  `70` pasan y `node --check` local es correcto.
- La última lectura del perfil conserva `24` candidatos, `21` piezas externas
  y `20` piezas visuales únicas; hipótesis normalizadas `0`, promoción `none`.

## Next action

La herramienta ya tiene el ciclo de revisión humana completo sin inventar
labels. El próximo paso no debe ser otro parche de interfaz: debe ser medir una
pasada controlada y comprobar que el candidato decidido desaparece de la
semilla y que solo el campo `triage` cambia. No llamar más proveedores hasta
que esa prueba confirme que las decisiones llegan al learner.

## Corrección de carga del editor 2026-08-09

- El código desplegado en MAK sí contenía `loadHumanSeed` y `advanceSeed`, pero
  una pestaña abierta podía conservar el JS anterior en memoria. Se versionó la
  referencia como `mesa_montaje.js?v=20260809-seed-loop` para forzar la carga de
  la implementación actual al recargar la superficie.
- El servidor entrega ahora la versión nueva por HTTP, el servicio sigue
  `active`, y la API de aprendizaje continúa respondiendo con la semilla y el
  perfil externo.
- Verificación local: `70` tests focalizados, `node --check` y `git diff --check`.

## Next action

Recargar una vez la superficie y repetir una sola decisión de la semilla. El
resultado esperado es que el candidato se guarde y el siguiente aparezca sin
recarga; si no ocurre, el próximo diagnóstico debe leer el error concreto del
endpoint, no volver a tocar el diseño.

## Correccion de autoavance de semilla 2026-08-09

- La API confirmo que la decision anterior si persistio: el perfil vivo paso a
  `work=6`, `discard=10`, `labeled=16`, y la semilla ya comienza en un id nuevo.
  Por tanto, el problema no era el guardado ni la seleccion de candidatos.
- El fallo de interfaz era que al hacer click sobre el candidato ya centrado
  para volver a ver sus controles `toggleOrderSelection` apagaba
  `humanSeedActive`; la decision se guardaba, pero el autoavance quedaba
  desactivado.
- La semilla ahora conserva `humanSeedItemId`. Click sobre su pieza activa no
  la deselecciona ni apaga el avance; click sobre otro nodo si cambia
  deliberadamente a orden manual. El avance solo ocurre para una decision
  individual de la semilla, nunca para un lote manual.
- Se desplegaron `mesa_montaje.js` y `editor.html` en MAK con la referencia
  `mesa_montaje.js?v=20260809-seed-autoadvance2`; `mak-hub.service` quedo
  `active`. Hash remoto del JS:
  `d66a6b00c0ff5b14353b146328ef9401e6e56c5e4608d203f764794a50fd0a85`.
- Verificacion Windows: tests focalizados de editor, copilot y bridge pasan;
  `node --check iskvw/mesa_montaje.js` y `git diff --check` pasan.

## Next action

Recargar una vez y pulsar `revision humana`; se puede clickear la pieza activa
sin perder los controles. Marcar una sola decision y comprobar que cambia a
otro id sin recarga. Si falla, registrar el texto exacto de `mesa-status` y
el id visible; no volver a redisenar la superficie.

## Correccion de continuidad visual 2026-08-09

- El usuario confirmo que podia marcar `obra`, pero la interfaz parecia volver
  a `ordenar` y no mostraba con claridad el siguiente candidato.
- Se uso Watsonx en dos revisiones adversariales acotadas. La primera fue
  demasiado generica; la segunda identifico la omision relevante: `loadHumanSeed`
  cargaba la escena nueva pero no centraba el nodo ni marcaba visualmente la
  revision humana como activa.
- Verificacion del codigo confirmo que faltaba `centerNodeInView(candidate.item_id)`
  despues de `rebuildScene`. El nodo podia existir y la API funcionar, pero
  quedar lejos de la vista por sus coordenadas GTM.
- La correccion reinicia la camara, reconstruye la escena, centra el siguiente
  candidato y marca el boton `revision humana` activo. El HUD ahora declara que
  al guardar aparecera el siguiente candidato. El modo ordenar manual conserva
  su comportamiento cuando el usuario elige otro nodo.
- Se desplego `mesa_montaje.js` y `editor.html` en MAK con la referencia
  `mesa_montaje.js?v=20260809-seed-autoadvance3`; `mak-hub.service` quedo
  `active`. Hash remoto del JS:
  `fe277e914063b38d55f97fb7380e2c219e1efde05f35a6c1b09346e1d8c96ea4`.
- Verificacion: tests focalizados de editor, copilot y bridge pasan; `node
  --check iskvw/mesa_montaje.js`; `git diff --check`; API de escena valida el
  candidato vivo `18004788223027705.jpg` con `ok=true`.

## Next action

Recargar una vez la pestaña, pulsar `revision humana`, marcar una sola obra y
comprobar que el siguiente id aparece centrado sin volver visualmente al modo
manual. Si falla, capturar `mesa-status`, id visible y la red; no volver a
parchar sin esa evidencia.

## Fast path de orden 2026-08-09

- El usuario pudo discriminar dos piezas, pero la pasada seguia lenta. La
  medicion directa en MAK con 7,044 items encontro `scene` relation en 10.245 s
  y `scene` order en 8.171 s la primera vez; la segunda llamada order fue
  0.828 s.
- La causa no era solo el mapa: el modo order estaba entrando al motor completo
  de hipotesis, que recalcula sugerencias sobre todo el archivo. Ordenar no
  necesita relacionar ni producir evidencia de vinculo.
- Se agrego `surface=order` al mismo endpoint de escena. Usa una topologia GTM
  estable y devuelve vecinos espaciales como contexto exploratorio sin
  evidencia ni promocion. `surface=relate` conserva el motor de hipotesis y
  sus evidencias.
- La topologia estable ignora unicamente `selection` y
  `classification.triage` al ajustar geometria, por lo que una decision humana
  no vuelve a recalcular el mapa completo. Los conteos de aprendizaje se
  refrescan en cada respuesta y el mapa se mantiene estable durante la pasada.
- La carga inicial, el centro desde order, el descarte y el cambio de modo ahora
  envian la superficie correcta. La referencia del script se versiono como
  `mesa_montaje.js?v=20260809-order-fastpath1` para no conservar JS viejo en la
  pestaña.
- MAK fue actualizado: `mak-hub.service` sigue `active`, HTTP order devuelve
  `200`, `provider=gtm_order_projection`, 10 records y 9 relaciones de contexto.
  Watsonx reviso el diseño y lo acepto; sus porcentajes no sustituyen la
  medicion local.
- Verificacion Windows: `78` tests focalizados (`77 passed, 1 skipped`),
  `node --check`, compilacion de `copilot.py` y `hub.py`, y `git diff --check`
  pasan. No hubo mutacion de
  ledger, promocion publica, commit ni push.

## Next action

Revisar una sola pasada en MAK con `revision humana`: la primera apertura puede
costar el ajuste inicial del GTM; las siguientes deben usar el camino order
rapido. Si la experiencia sigue lenta, medir la llamada exacta y separar carga
de aprendizaje del render, no reactivar el motor de relacion para ordenar.

## Fase 1 teorica ejecutada: atlas y campo 2026-08-09

- El GTM dejo de ser a la vez mapa, predictor y selector. Ahora entrega un
  atlas versionado que permanece estable durante la pasada; el aprendizaje
  rapido se aplica encima sin mover coordenadas.
- El campo rapido usa los vectores estructurales de 32 dimensiones para
  prediccion y la posicion GTM 2D solo para medir cobertura cartografica. Cada
  item expone probabilidades, incertidumbre, margen, cobertura y ganancia de
  informacion.
- `human_seed` ya no recorre buckets mecanicos. Usa active learning para elegir
  casos informativos y diversos. Un carrusel cuenta como una unidad y conserva
  `publication_media_count`.
- Las relaciones declaradas exponen `space=evidence`; las coincidencias
  conceptuales exponen `space=resonance`. Resonancia conserva valor curatorial
  pero no cambia identidad ni habilita promocion.
- El motor incorpora evaluacion leave-one-out y un gate de automatizacion. MAK
  tiene 21 labels: 10 `work`, 11 `discard`, cero `record` y cero `review`.
  Resultado actual: accuracy 0.857143, macro-recall 0.859091,
  `active_learning_ready=true`, `automation_ready=false`. La precision no se
  interpreta como suficiente porque faltan dos clases completas.
- Gate implementado: al menos 100 labels, 1% de cobertura, cinco ejemplos por
  clase y macro-recall 0.75. Ninguna prediccion se promueve automaticamente.
- Medicion MAK: topologia `16f75b4075c1d263`; ajuste frio 9.258 s; aprendizaje
  caliente 0.784 s; escena order 0.751 s. `mak-hub.service` esta `active`.
- Watsonx hizo una revision adversarial acotada. Acepto topologia estable,
  incertidumbre y seleccion activa; marco correctamente la falta de labels y
  el riesgo de depender del plano 2D. El motor responde usando vector 32D para
  prediccion y un gate verificable.
- Validacion local: 75 tests focalizados pasan, Python compila y
  `git diff --check` pasa. No hubo decision humana simulada, mutacion del
  ledger, promocion publica, commit ni push.

## Next action

La fase 2 es la superficie cartografica: consumir el atlas y el campo ya
existentes para mostrar incertidumbre, evidencia y resonancia sin formularios
dominantes; introducir decisiones comparativas o regionales; y mantener la
misma escena entre ordenar y relacionar. No modificar el motor ni exigir una
clasificacion masiva antes de construir esa traduccion visual.

## Fase 2 ejecutada: superficie cartografica 2026-08-09

- `iskvw/mesa_montaje.js` consume el atlas estable como campo vivo. La
  geometria no cambia por feedback; la superficie permite alternar
  incertidumbre, vacios de cobertura, evidencia y resonancia.
- La vecindad GTM de la ruta rapida tiene `space=topology`. Ya no se cuenta ni
  se dibuja como resonancia conceptual. Evidencia usa linea continua;
  resonancia usa linea discontinua; topologia solo organiza la ventana.
- La ventana local magnifica la zona del atlas alrededor de la pieza activa y
  relaja colisiones de forma determinista. Esto conserva posicion relativa sin
  amontonar diez medios que comparten una celda GTM.
- El panel inferior fue reemplazado por un compas radial alrededor de la
  seleccion. Ofrece obra, registro, revisar, descartar, detalle y una region
  comparativa de hasta seis piezas. La region se previsualiza antes de guardar
  una decision comun.
- Ordenar y relacionar usan la misma topologia estable. Pedir evidencia o
  resonancia activa el motor relacional de forma explicita; ordenar sigue por
  la ruta rapida sin crear hipotesis.
- MAK sirve `mesa_montaje.js?v=20260809-cartographic-field4` y
  `mak-hub.service` esta `active`. Medicion caliente de la escena order: 906
  ms, 10 registros, `space=topology`, `feedback_updates_topology=false`.
- Hashes de `hub.py`, `contrato_archivo.py`, `editor.html` y
  `mesa_montaje.js` coinciden entre Windows y MAK. La verificacion focalizada
  pasa 76 tests; JavaScript y Python compilan; `git diff --check` pasa.
- Captura headless de control:
  `_logs/cauce_director/20260805/PHASE2_CARTOGRAPHIC_FIELD_V3.png`. No se uso
  la pestana del usuario, no hubo decision simulada, mutacion de ledger,
  llamada premium, commit ni push.
- El checkout Windows estaba en `arreglo-readme` durante esta fase por el
  trabajo paralelo autorizado del README. Sus SVG y herramientas temporales no
  pertenecen a la cartografia y se preservaron sin editar, borrar ni promover.

## Next action

Ejecutar la fase unica `calibracion activa de la distancia` descrita en
`context/PLAN_MESA_DE_MONTAJE.md`, seccion 13. Primero medir la linea base viva
en MAK; luego instrumentar una pasada de 20 unidades y aprender pesos sobre el
vector existente sin mover el atlas. Comparar contra replay aleatorio y contra
el campo previo antes de llamar Watsonx/AWS como challengers ciegos.

Orientacion obligatoria para el siguiente agente: no volver a redisenar la
mesa, no crear otra taxonomia, motor, ledger, UI o script paralelo. Pensar en
categorias como atractores transitorios dentro de un espacio de fases; usar
`topology` solo para vecindad, `evidence` para hechos respaldados y `resonance`
para lectura curatorial. La mejora debe verse en calibracion, abstencion,
transferencia y decisiones por minuto, no en volumen de outputs. Trabajar el
circuito en MAK antes de git; preservar el README paralelo y dejar dominio,
publicacion y promociones fuera de esta fase.

## Fase 3 ejecutada: distancia activa con gate de replay 2026-08-09

- El campo existente ahora puede aprender una metrica pairwise sobre el mismo
  vector estructural de 32 dimensiones. Usa pares de misma etiqueta como
  atraccion y pares de etiquetas distintas o relaciones humanas rechazadas
  como separacion. Las restricciones contradictorias se conservan como
  conflicto y no se usan para mover la distancia.
- La metrica esta acotada, es determinista y no toca la geometria GTM. Su
  perfil expone soporte positivo/negativo, dimensiones con mayor peso,
  confianza, activacion y razon de abstencion. Sin pares suficientes vuelve a
  distancia identidad.
- La activacion no depende de que la metrica parezca sofisticada: se compara
  contra el mismo replay leave-one-out. Si no mejora accuracy o macro-recall,
  el candidato pairwise queda retenido como evidencia negativa y el campo usa
  identidad. No se reajusto ningun umbral para fabricar mejora.
- MAK midio 21 labels, 111 pares positivos y 110 negativos. El candidato
  pairwise quedo rechazado por empate exacto: baseline y candidato tienen
  accuracy `0.857143` y macro-recall `0.859091`. El campo vivo informa
  `method=identity`, `candidate_method=pair_contrast`,
  `activation=held_out_no_replay_gain`.
- El orden caliente sigue por debajo de 1 s: tres escenas order midieron
  `821.970`, `801.371` y `828.312` ms con 10 registros. El servicio
  `mak-hub.service` sigue `active`. La interfaz muestra `distancia base` y
  conserva el candidato retenido sin venderlo como aprendizaje activo.
- Despues del replay, Watsonx y AWS recibieron ciegamente el mismo subconjunto
  de 21 piezas sin labels humanos. Watsonx respondio 21/21 pero acerto 1
  (`0.047619`); AWS respondio 21/21 y acerto 9 (`0.428571`). Son challengers,
  no gold labels. El raw aislado esta en
  `C:\IA\flujo\_logs\cauce_director\20260805\DISTANCE_CHALLENGE_20260809.json`
  y en MAK bajo
  `/home/mak/plataforma/director_runs/distance-challenge-20260809/`.
- La corrida externa no escribio ledger, no creo etiquetas, no promovio
  contenido ni movio archivos. La fase no demostro mejora predictiva; si dejo
  algo durable fue el mecanismo de gate y la medicion de fracaso.
- El checkout Windows permanece en `arreglo-readme` con cambios acumulados de
  sesiones anteriores; no se hizo commit, push, merge, reset ni limpieza. Los
  hashes de `copilot.py`, `hub.py`, `mesa_montaje.js` y `editor.html` coinciden
  entre Windows y MAK; `mak-hub.service` esta activo.

## Next action

No llamar otra vez Watsonx/AWS para esta misma muestra y no activar
`pair_contrast` por entusiasmo. El siguiente circuito util es una pasada
humana de 20 unidades editoriales desde `revision humana`, buscando agregar
las clases ausentes `record` y `review` y al menos algunos pares rechazados.
Despues repetir exactamente el replay: solo si hay ganancia se activa la
metrica; si no, se conserva identidad y se pasa a mejorar abstencion o
seleccion activa. Mantener la mesa y el atlas; no abrir otra interfaz, motor,
ledger, taxonomy ni tarea de Git. Watsonx/AWS quedan como criticos acotados,
no maestros del orden.

## Correccion de cola repetida y consolidacion de decisiones 2026-08-09

- El usuario confirmo que sus decisiones recientes deben tratarse como
  correctas para el aprendizaje; no se reemplazan por la prediccion de un
  modelo. El perfil vivo conserva `63` labels de orden: `22 work`, `4 record`,
  `37 discard` y `0 review`. El perfil de candidatos conserva `8` decisiones:
  `4 accept`, `1 revise` y `3 reject`.
- La cola externa mostraba `7` filas, pero una misma fuente aparecia tres
  veces. La causa estaba en que `_portfolio_external_candidates` proyectaba
  cada fila historica del ledger como una entrada visual, aunque la identidad
  humana de la revision ya estaba asociada al `source_id`.
- La superficie ahora deduplica por `source_id`, aplica la revision mas
  reciente de esa fuente a todas sus filas historicas y conserva la evidencia
  unificada. No borra ni modifica el ledger; expone `candidate_occurrences`
  para hacer visible la procedencia repetida.
- Despliegue MAK verificado: `/home/mak/plataforma/hub.py` compila, el servicio
  `mak-hub.service` esta `active`, y `GET /api/portfolio/review-queue` baja de
  `total=7` a `total=5`. La fuente repetida queda como una sola entrada con
  `candidate_occurrences=3`; `revise` permanece pendiente por diseño.
- Hash Windows/MAK de `hub.py` coincide:
  `ca898829c0e3a4b2bcd75da82555780291868eeed9679e520f1fab3fbb5d5efb`.
- Verificacion local: tests focalizados de bridge, copilot y editor pasan;
  `py_compile`, `node --check` previo y `git diff --check` no muestran
  errores. No se llamo a Watsonx/AWS, no hubo promocion, commit ni push.

## Next action

Recargar `http://192.168.50.2:8900/portafolio/` y comprobar que cada fuente
aparece una sola vez en la bandeja. Las decisiones ya tomadas se conservan
como verdad humana; no volver a revisarlas ni volver a llamar proveedores para
esa muestra. El siguiente bloque debe usar el aprendizaje resultante para
mejorar el orden de la siguiente tanda, no para rehacer historicamente la
cola. Si la interfaz aun repite una tarjeta, registrar su `source_id` exacto
antes de tocar mas codigo.
## Seed siguiente verificado 2026-08-09

- La superficie de aprendizaje entrega `24` unidades nuevas en
  `ordering.human_seed`; la primera es `18107498155769997.jpg` y no pertenece
  a la cola de candidatos externos ya revisada.
- La escena order con esa unidad como foco responde `ok=true` y entrega `10`
  registros. El camino esta listo para la segunda pasada humana sin llamar a
  Watsonx/AWS ni reabrir las fuentes antiguas.
- La siguiente ronda debe tomar hasta `20` de esas unidades y conservar las
  decisiones humanas como labels de replay. No se debe inventar `review` para
  completar una cuota: si una pieza no es obra ni registro, se usa la decision
  humana correspondiente y el modelo queda en abstencion cuando falte clase.
## No reentrada de decisiones confirmada 2026-08-09

- Verificacion directa en MAK con `active_ordering_seed`: `63` unidades ya
  etiquetadas, `24` unidades en el seed siguiente y `overlap=[]`.
- Por tanto, una unidad marcada como `obra`, `registro` o `descartar` no vuelve
  a la bandeja de revision humana. Puede seguir visible como contexto espacial
  del atlas, pero no vuelve a ser elegida como siguiente decision.
## Flujo de ficha, avance y precarga 2026-08-09

- La observacion del usuario confirmo que `obra` o `registro` deben ser una
  clasificacion, no una relacion. La mesa ahora lo declara en el HUD y no
  crea conexiones al guardar una decision de orden.
- En `revision humana`, la decision se limita a la pieza central. Los nodos
  vecinos no pueden convertirse accidentalmente en una seleccion multiple.
  La clasificacion puede guardarse primero; el boton `siguiente` aparece en
  el detalle y avanza solo despues de que la ficha tenga `triage`.
- El seed se conserva en memoria durante la pasada. La siguiente escena se
  precarga en segundo plano y no se vuelve a pedir el aprendizaje completo en
  cada avance. El cache queda limitado a tres escenas.
- Al descartar la pieza central, la mesa elige otra disponible de la ventana o
  del inbox; no deja una escena vacia solo porque el centro anterior fue
  retirado. Las piezas ya decididas quedan ocultas durante la revision humana.
- Verificacion Windows: `node --check`, tests focalizados de editor, bridge y
  copilot, y `git diff --check` pasan. El despliegue a MAK quedo pendiente:
  SSH a `192.168.50.2:22` devolvio `Permission denied` y el host no respondio
  al ping. No afirmar que esta version esta activa hasta copiarla y verificar
  el hash remoto.

## Next action

Cuando MAK vuelva a responder, copiar `iskvw/mesa_montaje.js` y
`iskvw/editor.html`, reiniciar `mak-hub.service` y verificar la referencia
`mesa_montaje.js?v=20260809-review-packet1`. Despues hacer una prueba corta:
clasificar una pieza como `obra`, abrir `detalle`, agregar una marca, pulsar
`siguiente` y confirmar que el siguiente centro aparece sin esperar otra
llamada completa de aprendizaje.

## Despliegue de ficha y precarga 2026-08-09

- El VPN volvio a permitir SSH a `mak@192.168.50.2`; el bloqueo anterior era
  de conectividad LAN, no de credenciales.
- La raiz servida por el proceso no es `/home/mak/plataforma/iskvw`, sino
  `/home/mak/flujo/iskvw` (`MAK_PORTFOLIO_ROOT` no aparece en el entorno del
  proceso y `hub.py` usa esa ruta por defecto). Copiar a la primera ruta no
  cambia el editor visible.
- Se copiaron `iskvw/mesa_montaje.js` y `iskvw/editor.html` a
  `/home/mak/flujo/iskvw/` y la respuesta local `http://127.0.0.1:8900/portafolio/`
  confirma `mesa_montaje.js?v=20260809-review-packet1`.
- El proceso real de MAK sigue activo como PID `65683` ejecutando
  `/home/mak/plataforma/hub.py` y escuchando en `0.0.0.0:8900`; no existe una
  unidad `mak-hub.service` instalable para reiniciar. No se detuvo el proceso.

## Next action

Hacer una prueba corta en la interfaz servida por MAK: clasificar una pieza
como `obra`, abrir detalle, agregar una marca, pulsar `siguiente` y confirmar
que el siguiente centro aparece sin una llamada completa de aprendizaje.

## Smoke test remoto 2026-08-09

- MAK responde por SSH y el proceso de `/home/mak/plataforma/hub.py` mantiene
  `:8900` activo.
- `GET /api/portfolio/copilot/learning` responde con `human_seed=24`,
  `labeled=83`, `missing_labels=1`; no devuelve un seed vacio.
- El primer seed `17844722936371604.jpg` produce una escena valida con
  `10` records y `9` relaciones. La lectura anterior de `items=0` era solo
  una inspeccion contra una clave equivocada; el contrato usa `records`.
- El siguiente trabajo no es otro parche de servidor: es comprobar en la UI
  que una decision `obra` se guarda en la ficha y que `siguiente` avanza sin
  repetir la llamada completa de aprendizaje.

## QA adversarial sin ventana 2026-08-09

- Se ejecutaron rondas de razonamiento desde MAK con Watsonx y AWS Bedrock.
  Watsonx fue demasiado generico y Ollama excedio su timeout; AWS respondio
  despues de usar el entorno `.venv` que contiene `boto3`. Ningun resultado
  externo se promovio como verdad.
- Se agregaron frenos de doble accion en
  `iskvw/mesa_montaje.js`: `advance-seed` evita dos avances concurrentes y
  `discard:<source_id>` evita dos descartes del mismo registro.
- La verificacion de codigo en MAK paso: alcance central unico, avance,
  descarte, guardia de vecinos, precarga/cache y persistencia de ejes.
  La API remota mantuvo `human_seed=24`, `labeled=86`, escena de `10` records
  y `9` relaciones.
- Se copio esta version a `/home/mak/flujo/iskvw/`; las pruebas Windows de
  sintaxis JS, contrato del editor, bridge, copilot y `git diff --check`
  tambien pasan.

## Next action

No abrir navegador ni hacer clics automaticamente. El siguiente bloque es
revisar por codigo la persistencia de las marcas multiples y el avance; la
interaccion humana queda solo para confirmar la experiencia si el usuario lo
decide.

## Persistencia idempotente y reinicio MAK 2026-08-09

- La simulacion por codigo descubrio el bug real que una ronda de Watson/AWS
  solo describia: `_portfolio_select` y `_portfolio_classify` siempre
  anexaban otra fila aunque la accion o clasificacion fuera identica.
- Se agrego deduplicacion por estado semantico: una repeticion exacta devuelve
  `duplicate=true`; un cambio real de eje, nota o decision sigue siendo una
  nueva actualizacion. Las marcas nuevas conservan los ejes anteriores.
- Se agregaron pruebas locales de seleccion y clasificacion repetidas; el
  conjunto focalizado paso (`editor_contract`, `mak_portfolio_bridge`,
  `copilot`).
- Se copio `cultura/mak_plataforma/hub.py` a `/home/mak/plataforma/hub.py` y
  se reinicio correctamente `systemctl --user restart mak-hub.service`.
  MAK quedo activo con PID nuevo y memoria inicial de `24.3M`.
- La simulacion remota con archivos temporales paso: una seleccion repetida
  dejo `1` fila, una clasificacion repetida dejo `1` fila y el siguiente eje
  produjo exactamente `{"triage":"work","lane":"rd"}`.

## Next action

Revisar por codigo la transicion de `siguiente` contra el estado persistido y
el filtro de candidatos decididos. No abrir ventanas ni hacer clics durante
esa verificacion.

## Filtro persistido y siguiente candidato 2026-08-09

- La verificacion remota sobre el inbox real paso: `24` seeds unicos, sin
  interseccion con las `86` unidades etiquetadas, sin assets ausentes y sin
  publicaciones/carruseles duplicados dentro del seed.
- La simulacion sintetica de transicion excluyo correctamente `work`,
  `record` y `discard`, dejando solo la siguiente unidad sin etiqueta.
- El filtro vive en `copilot.active_ordering_seed`; la decision persistida se
  convierte en `classification.triage` o `selection=descartar`, por lo que no
  depende del estado temporal de la interfaz.
- No se modifico ningun registro real durante esta prueba.

## Next action

El circuito de persistencia y avance esta cerrado para esta ronda. El
siguiente bloque puede atacar errores funcionales nuevos reportados desde la
interfaz, sin volver a probar manualmente lo ya cubierto.

## Correccion de contexto en ficha 2026-08-09

- Se encontro otro bug funcional por inspeccion de codigo: el boton `guardar
  nombre` del contexto buscaba un selector inexistente (`data-class-context-kind`),
  por lo que una marca como artista, venue o evento nunca podia guardar su
  nombre.
- Ahora toma el `context_kind` ya persistido o el toggle activo y conserva el
  `context_value`; el cambio no crea relaciones ni depende del texto libre.
- Se incremento la version de cache del editor a
  `mesa_montaje.js?v=20260809-review-packet2`, se desplego a MAK y la respuesta
  de `:8900` confirma esa referencia.
- Pruebas focalizadas y verificacion estatica remota pasan; `mak-hub.service`
  sigue activo.

## Next action

Seguir con una auditoria de codigo de las acciones del popup que escriben
comentarios y relaciones, buscando selectores muertos o estados que no
persistan, sin abrir navegador.

## Auditoria de cinco bugs adicionales 2026-08-09

- Bug 1: limpiar `context_kind` dejaba un `context_value` huerfano. Ahora la
  limpieza borra ambos campos y evita conservar un nombre de artista, venue o
  evento sin tipo.
- Bug 2: la ficha podia imprimir dos veces la misma descripcion original.
  `pieceContext` ya no incluye el bloque que la ficha renderiza por separado.
- Bug 3: dos cambios rapidos de lente podian resolver fuera de orden y dejar
  visible una escena vieja. `viewRequestId` invalida la respuesta tardia.
- Bug 4: dos centrados rapidos tenian la misma carrera y una respuesta lenta
  podia devolver el centro anterior. El mismo guard protege `centerRecord`.
- Bug 5: el cache de escenas podia conservar relaciones y clasificaciones
  anteriores despues de una decision humana. `sceneCacheRevision` invalida
  el cache tras clasificar, descartar o resolver una relacion.
- La prueba focalizada paso: `node --check`, 81 tests de editor, bridge y
  copilot, y `git diff --check`.
- La version actual se copio a `/home/mak/flujo/iskvw/mesa_montaje.js` y
  `/home/mak/flujo/iskvw/editor.html`. MAK sirve `review-packet2`, el Hub esta
  `active` y la verificacion HTTP paso. No hubo clicks, proveedor premium,
  mutacion del ledger, commit ni push.

## Next action

Auditar por codigo la escritura de comentarios y relaciones en el popup:
seguir cada respuesta de red hasta su estado visual, comprobar que una nota
no se duplique y que una relacion no sobreviva despues de retirar la pieza.
Hacerlo en MAK sin abrir navegador; solo despues de esa verificacion decidir
si hace falta otro cambio.

## Auditoria de diez bugs adicionales 2026-08-09

- Bug 1: invalidar escenas limpiaba el cache visible, pero dejaba promesas de
  red antiguas reutilizables. Ahora invalida tambien `sceneCachePromises` y
  cada promesa solo puede borrar su propia entrada.
- Bug 2: entrar a `relacionar` podia cargar el modo `copilot` mientras la
  lente visual seguia en `fecha`, `venue` u otra anterior. La lente y el modo
  ahora se sincronizan antes de renderizar.
- Bug 3: `siguiente frontera` podia terminar despues de un cambio de escena y
  reemplazarlo con una respuesta vieja. La carga tiene guard de request y no
  muta el estado hasta tener la escena vigente.
- Bug 4: cuando no quedaba otra semilla, el fallback podia devolver la misma
  pieza central sin marcarla como nueva. El candidato siempre debe ser otro
  id no procesado.
- Bug 5: la semilla anterior se marcaba antes de que cargara la siguiente; un
  fallo de red podia perder una decision valida de la pasada. Ahora se excluye
  durante la carga y se registra como procesada solo despues del exito.
- Bug 6: `nextAvailableRecord` devolvia una pieza ya decidida si no encontraba
  una nueva, haciendo reaparecer trabajo cerrado. Ahora devuelve vacio y deja
  la pasada cerrarse honestamente.
- Bug 7: las decisiones hechas fuera de la frontera humana no ocultaban nodos
  ya clasificados mientras el modo seguia en `ordenar`. Esos nodos ya no
  vuelven a ocupar la mesa como candidatos activos.
- Bug 8: descartar desde el popup y clasificar desde el HUD podian actuar al
  mismo tiempo sobre la misma pieza y avanzar dos veces. Se agrego un cerrojo
  comun por `item_id`.
- Bug 9: cambiar el tipo de contexto de artista a venue conservaba el nombre
  anterior y producia una identidad mezclada. Cambiar `context_kind` limpia
  `context_value`; clasificaciones rapidas ahora quedan en cola en vez de
  perderse.
- Bug 10: el grafo marcaba como relacionadas solo las piezas destino; la
  fuente podia quedar visualmente sin vinculo. Ahora ambos extremos se marcan,
  y la ficha reconoce relaciones en cualquiera de las dos direcciones.
- Verificacion: `node --check`, 81 tests focalizados y `git diff --check`
  pasan. MAK sirve `mesa_montaje.js?v=20260809-review-packet3`; el Hub esta
  `active` y la prueba HTTP/estatica remota paso. No hubo clicks, proveedor
  premium, mutacion de ledger, commit ni push.

## Next action

Hacer una auditoria equivalente del backend de relaciones por faceta: una
misma pieza puede tener fecha, evento y obra como hipotesis distintas, y una
decision sobre una no debe ocultar las otras. Verificarlo con fixtures locales
antes de desplegar otro cambio de MAK.

## Auditoria de veinte fallos y endurecimiento 2026-08-09

- La auditoria encontro 22 fallos concretos en la columna de persistencia y
  relaciones: mezcla de ids numericos/textuales, inbox corrupto, JSONL con una
  linea rota que podia ocultar todas las resoluciones, batches parcialmente
  escritos, rechazo facetado que ocultaba otros canales, fallback de ordering
  sin media visible, conexiones rechazadas que seguian en el organismo,
  candidatos externos huerfanos o sin media, revisiones que podian sangrar
  entre candidatos, filtros de provider con descartados o hermanos de
  carrusel, y boards con ids repetidos.
- `cultura/mak_plataforma/hub.py` ahora normaliza ids, tolera payloads y filas
  invalidas, lee todos los JSONL validos, valida batches antes de escribir,
  conserva feedback por faceta, filtra candidatos externos accionables y
  normaliza boards antes de guardarlos.
- `cultura/mak_plataforma/copilot.py` ya no usa un rechazo de texto como
  rechazo global del par; fecha, artista, evento, venue y texto mantienen
  canales independientes. El seed de orden solo devuelve media visible.
- `cultura/mak_plataforma/contrato_archivo.py` conserva las decisiones de
  cada faceta en la escena y calcula el estado sin destruir la evidencia de
  los otros canales.
- `cultura/mak_plataforma/providers.py` corrige una fuga de entorno: un `.env`
  explicito ya no queda ignorado por una credencial vieja cargada en el mismo
  proceso. Los valores nunca se imprimen ni se guardan en el repo.
- Regresion Windows: 100 por ciento de los tests focalizados de editor,
  bridge, copilot y tandas pasan; tambien pasan `py_compile`, `node --check`
  y `git diff --check`. El test de aliases de provider, que fallaba por el
  entorno contaminado, ahora pasa sin tocar credenciales reales.
- MAK fue actualizado en `/home/mak/plataforma/` para `hub.py`, `copilot.py`,
  `contrato_archivo.py` y `providers.py`. `mak-hub.service` esta `active`,
  `/api/portfolio/inbox` responde HTTP 200 con 3.6 MB y los marcadores del
  endurecimiento estan presentes en los cuatro modulos.
- No se abrio navegador, no se hicieron clicks, no se modifico el ledger real,
  no se llamo Watsonx/AWS para repetir una auditoria que los fixtures locales
  podian probar, y no se hizo commit, push, merge ni limpieza de ramas.

## Next action

No abrir otra ronda ciega de parches. Recargar el editor servido por MAK y
hacer una pasada humana controlada de 20 unidades con estas garantias:
decidir obra/registro/revision/descartar, conservar las facetas independientes
y confirmar que una pieza decidida no reaparece. Despues usar esas 20 decisiones
como replay medible antes de pedir otro desafio a Watsonx/AWS.

## Auditoria de continuidad y gasto seguro 2026-08-09

- La siguiente auditoria busco fallos de continuidad, no nuevos features. El
  resultado fue un bloque de 20 riesgos de reaparicion, perdida silenciosa o
  gasto duplicado en la mesa: dos rutas de seed que separaban carruseles, una
  semilla siguiente que ignoraba publicaciones ya decididas, contexto viejo al
  cambiar de tipo, vision AWS repetida, seleccion y feedback escritos antes de
  pasar por el ledger, vecinos sin media, y respuestas HTTP ignoradas en carga,
  clasificacion, relacion, descarte y precarga.
- `cultura/mak_plataforma/copilot.py` ahora trata una publicacion/carrusel como
  unidad de avance en las dos rutas de ordering. Cuando un hermano ya tiene una
  decision, el resto no reaparece como candidato separado ni se usa para llenar
  otra semilla.
- `cultura/mak_plataforma/hub.py` limpia el valor de contexto al cambiar
  `context_kind`, evita repetir una lectura AWS ya persistida, y no conserva una
  seleccion o feedback si el ledger la rechaza. El orden visual omite registros
  sin media disponible.
- `iskvw/mesa_montaje.js` ahora distingue HTTP fallido de payload valido,
  conserva una clasificacion pendiente si falla su primer envio, ignora errores
  de solicitudes antiguas, no carga metadata-only como pieza central y no deja
  que una respuesta de precarga reemplace una escena vigente.
- La prueba local ejecutada fue: `node --check iskvw/mesa_montaje.js`,
  `py -m pytest tests/test_copilot.py tests/test_mak_portfolio_bridge.py
  tests/test_iskvw_editor_contract.py tests/test_mak_tandas.py -q`,
  `py -m pytest tests/test_higiene_docs.py tests/test_mapa_completo.py -q` y
  `git diff --check`; todos terminaron correctamente.
- MAK ya recibe el bloque en `/home/mak/plataforma/` y el editor en
  `/home/mak/flujo/iskvw/`. `mak-hub.service` queda `active`; el endpoint
  `/api/portfolio/inbox` responde HTTP 200 con 3,678,477 bytes; el editor
  sirve `review-packet4` y los marcadores de feedback, duplicate e idempotencia
  estan presentes. No se llamo Watsonx/AWS en esta ronda porque el problema
  podia reproducirse con fixtures y llamar modelos antes de cerrar la
  persistencia habria quemado credito sin aumentar evidencia.
- No hubo navegador, clicks, watcher, commit, push, merge ni borrado de ramas.

## Next action

Ejecutar una replay automatizada de 20 decisiones con fixtures controlados
contra el backend activo de MAK: diez obras/registros con hermanos de carrusel,
cinco cambios de contexto y cinco fallos HTTP/ledger. Medir que cada decision
se conserva una sola vez, que sus facetas no se pisan y que ningun candidato
cerrado reaparece. Solo si esa replay pasa se lanza una tanda pequena y ambigua
de Watsonx/AWS; sus salidas entran como candidatos, nunca como verdad.

## Replay de veinte decisiones 2026-08-09

- El replay encontro una pequena superficie adicional: la semilla humana
  podia reutilizar una respuesta cacheada despues de una decision, comparar
  ids con tipos distintos, intentar abrir una pieza sin media, o volver a
  separar un hermano de carrusel ya decidido. Tambien el contador de nodos
  podia mostrar registros ocultos por la mesa en vez de los visibles.
- `iskvw/mesa_montaje.js` incorpora `seedCandidateAllowed`: valida id, media,
  decision vigente y publicacion antes de reutilizar una semilla o precargarla;
  la respuesta de aprendizaje ahora valida HTTP y payload. El grupo visual
  tolera datos incompletos y el contador usa la proyeccion visible.
- Se corrigio el contrato estatico para reflejar `candidateId`; `node --check`
  y los tests focalizados vuelven a pasar despues del cambio.
- Replay Windows: 20 items sinteticos, 5 carruseles, 20 selecciones, 20
  clasificaciones, 20 feedback facetados y 40 entradas de ledger, sin
  reaparicion del carrusel decidido. Replay en MAK con los modulos realmente
  desplegados: `mak_replay=20 ok selections=20 classifications=20 feedback=20
  ledger=40`.
- MAK queda con el frontend actualizado, `mak-hub.service` `active` y
  `/api/portfolio/copilot/learning` responde HTTP 200 con 19,170 bytes. El
  chequeo remoto de sintaxis JavaScript no pudo ejecutarse porque la caja no
  tiene `node`; el mismo `node --check` local paso y el archivo remoto fue
  verificado por marcadores y checksum durante el despliegue.

## Next action

El circuito mecanico ya esta en condiciones de recibir una tanda externa
acotada. Antes de gastar Watsonx/AWS, ejecutar una sola tanda ambigua de 10
items con evidencia visual y metadata, guardarla como candidatos aislados y
medir: duplicados, ids sin fuente, relaciones sin faceta, media ausente y
promociones indebidas. Si el juez local la rechaza limpiamente, repetir con
otros 10; no convertir el sistema en un loop infinito de auditoria sin salida.

## Cierre de replay y despliegue 2026-08-09

- La inspeccion posterior al replay encontro un ultimo borde de robustez: un
  `work_group.member_ids` malformado podia romper la mesa al llamar `forEach`.
  Se normalizo tambien ese lector; no se agrega otro sistema de datos.
- `node --check`, los dos grupos de pytest focalizados, el chequeo documental
  y `git diff --check` pasan nuevamente.
- MAK recibio el archivo final en `/home/mak/flujo/iskvw/mesa_montaje.js`;
  el marcador remoto confirma `seedCandidateAllowed` y el guard de grupos,
  `mak-hub.service` sigue `active` y learning responde HTTP 200 con 19,170
  bytes. No hubo mutacion del archivo real de portfolio durante el replay.

## Next action

Ejecutar ahora una unica tanda externa ambigua de 10 items, separando Watsonx
para hipotesis de metadata y AWS para evidencia visual. Pasarla por el juez
local y conservar cada salida como candidato aislado; medir duplicados, ids sin
fuente, facetas sin evidencia, media ausente y promociones indebidas antes de
aceptar otra tanda.

## Primera tanda externa controlada 2026-08-09

- El replay habilito una tanda real de 10 items con media disponible. La
  lectura AWS visual completo 10/10 sin duplicados: creo evidencia de still o
  contact sheet para videos y no promovio ninguna obra.
- Se intento Watsonx sobre esos mismos 10 items. Las 10 respuestas regresaron
  `provider_error`; el diagnostico directo de MAK no fue una suposicion de
  credenciales: IBM devolvio HTTP 500 porque el certificado de la instancia
  privada `us-south` expiro el 2026-08-09 23:59:59 UTC. No desactivar TLS ni
  aceptar ese certificado; Watson debe quedar bloqueado hasta que IBM renueve
  el endpoint o se configure otra URL valida.
- `cultura/mak_plataforma/providers.py` ya no llama `ready` a un proveedor solo
  porque existen variables de entorno: ahora expone `configured` y
  `runtime=unverified`. Toda ruta sin fallback conserva `local_deterministic`,
  evitando que un fallo premium parezca una verdad o un bloqueo silencioso.
- MAK fue reiniciado con ese cambio. Capacidades verificadas: AWS y Watson
  configurados pero runtime no verificado, Ollama configurado; visual y
  research muestran fallback local. El servicio sigue `active`.
- La tanda AWS quedo aislada como candidatos/evidencia en los archivos de
  portfolio; no escribio promocion publica, no cambio ramas y no toco el
  ledger de curatoria humana. Los 10 items y sus respuestas estan en MAK para
  la siguiente revision local.

## Next action

Revisar el paquete AWS de 10 candidatos con Ollama/determinista y medir
duplicados, ids, facetas y promociones. Mantener Watsonx en cuarentena tecnica
hasta renovar el certificado; no repetir llamadas que ya demostraron el mismo
HTTP 500. Si el paquete pasa el filtro local, continuar con la siguiente tanda
AWS de 10 y usar Watsonx solo despues de que su endpoint vuelva a ser valido.

## Filtro local de la tanda AWS 2026-08-09

- Se auditaron las 10 filas AWS de hipotesis y las 10 filas AWS visuales
  almacenadas en MAK. Resultado: 10/10 ids unicos en cada superficie,
  evidencia presente, facetas normalizadas, ninguna fila sin item y cero
  promociones publicas.
- La salida queda como candidato aislado; no se acepta automaticamente ni se
  mezcla con la curatoria humana. El sistema ya puede gastar AWS por tandas
  acotadas sin contaminar el archivo.

## Next action

Usar Ollama para juzgar esas 10 filas sin mutar el ledger y guardar solo el
resumen de calidad. Watsonx permanece en cuarentena tecnica por el certificado
expirado; cuando IBM lo renueve se repite una sola prueba de salud antes de
volver a consumir una tanda.

## Juez local y compuerta de hipotesis 2026-08-09

- Ollama reviso las 10 salidas AWS, pero su primera lectura fue insuficiente:
  aceptaba piezas sin hipotesis. La inspeccion mecanica real mostro 1/10 con
  hipotesis evidenciadas y 9/10 sin hipotesis; ninguna de esas nueve debe
  promoverse por la opinion del modelo local.
- Para no confiar ciegamente en Ollama, `cultura/mak_plataforma/copilot.py`
  ahora expone `inference_quality`, una compuerta pura que marca `revise` si
  no hay hipotesis o si falta evidencia, y nunca cambia `promotion` desde
  `none`. `hub.py` la adjunta a cada futura salida externa sin borrar el raw.
- Tests focalizados pasan; MAK fue actualizado y reiniciado. El endpoint de
  capacidades responde HTTP 200. Los diez resultados anteriores conservan su
  raw y su evidencia; esta compuerta se aplica desde la proxima tanda y deja
  la historia intacta.

## Next action

Repetir una tanda AWS de 10 solo despues de que el usuario pueda revisar la
calidad mecanica de la primera: hipotesis evidenciada, faceta, fuente y
desconocidos. Watsonx queda bloqueado por el certificado IBM expirado. No
seguir gastando modelos para compensar un juez que acaba de demostrar que
puede aceptar vacios; primero se mide la compuerta determinista.

## Cierre de promocion y limpieza 2026-08-09

- El bloque de MAK, Hub, ledger, copilot, providers, tandas y Estudio de obra
  quedo integrado con la superficie README/SVG y el plan de mesa de montaje.
- La rama README se reconcilio con `origin/main`; los conflictos se resolvieron
  conservando la geometria ASCII seleccionada y el texto actualizado mediante
  `tools/update_readme_svg.py`. El generador ahora reconoce las capas antiguas
  y las actuales sin crear otra herramienta.
- Las variantes SVG experimentales no referenciadas se conservaron fuera del
  repositorio en `_logs/cauce_director/20260805/readme_experiments_20260809/`
  con `MANIFEST.json`; no se borraron ni se dejaron como basura versionada.
- Verificacion local completa: `py -m pytest -q` termino sin fallos; tambien
  pasaron `node --check iskvw/mesa_montaje.js`,
  `py tools/update_readme_svg.py --check`, `py_compile` de la plataforma y
  `git diff --check`.
- La prueba que fallaba por una variable GEMINI residual quedo aislada para
  que no dependa de credenciales del entorno. El contrato documental se
  actualizo: `AGENTS.md` es la entrada Faro actual y `CLAUDE.md` queda como
  compatibilidad historica.

## Next action

Pushear el commit reconciliado a `main` y sincronizar desde ese mismo hash las
ramas canonicas `mak`, `rd` e `iskvw`. Despues verificar los cuatro refs,
eliminar `arreglo-readme` local/remota solo cuando su trabajo sea ancestro de
las cuatro, y comprobar que no existan tags ni ramas extra. No volver a
consumir Watsonx hasta que IBM renueve el certificado; la siguiente tanda
externa segura sigue siendo AWS acotado + juez local.

## Verificacion de la caja MAK despues de la promocion 2026-08-09

- `/home/mak/flujo` quedo limpio en `main` con el mismo hash `1352e29f` y
  solamente las ramas locales `main`, `mak`, `rd` e `iskvw`.
- Los cinco modulos desplegados en `/home/mak/plataforma/` coinciden por
  SHA-256 con `cultura/mak_plataforma/` del checkout canonico. La interfaz
  `iskvw/editor.html` y `iskvw/mesa_montaje.js` tambien estan en ese checkout.
- El Hub responde HTTP 200 en `127.0.0.1:8900` y el proceso activo es
  `/home/mak/plataforma/.venv/bin/python /home/mak/plataforma/hub.py` (PID
  observado 128089). No existe una unidad `mak-hub.service` activa; no se
  debe afirmar lo contrario. La persistencia de arranque queda como tarea
  separada, no se inventa durante esta limpieza.

## Auditoria de MAK antes de sincronizar 2026-08-09

- `origin/mak` tenia dos commits que no estaban en la linea comun:
  `9e18dc4f` y `500209bc`. Ambos eran drafts autogenerados por DeepSeek para
  revisar: uno filtraba CSV por texto y el otro abria un servidor minimo en
  8901, sin contrato `mak-work-v1`, sin Hub, sin ledger y sin pruebas del
  circuito real.
- No se rescatan en la rama operativa. Sus hashes y su razon de descarte
  quedan registrados aqui; el estado canonico se sincroniza desde el main
  probado, sin borrar la evidencia del analisis local.

## Promocion final verificada 2026-08-09

- El hash publicado es `ec0e1499` en `main`, `mak`, `rd` e `iskvw`; los cuatro
  refs remotos y locales coinciden.
- `origin/arreglo-readme`, `origin/ligereza-patch-1` y
  `origin/ligereza-patch-2` fueron retiradas despues de archivar sus parches
  y hashes en `_logs/cauce_director/20260805/retired_branches_20260809/`.
- `git ls-remote --tags origin` no devuelve tags y `gh pr list --state open`
  devuelve `[]`. El remoto queda con exactamente las cuatro ramas canonicas.
- El checkout Windows actual esta limpio en `iskvw`; el worktree de `main`
  tambien quedo limpio y apunta al mismo hash. La caja MAK ya recibio el
  bloque operativo antes de esta promocion; el siguiente chequeo remoto debe
  validar servicio y hash, no repetir la auditoria completa.

## Next action

En la proxima sesion empezar por `context/LAST_HANDOFF.md`, comprobar el
servicio `mak-hub` y revisar una sola tanda AWS de 10 candidatos con la
compuerta local. Watsonx continua en cuarentena por el certificado vencido de
IBM. No abrir otra rama ni otro PR: cualquier bloque estable se promueve
directamente por el flujo de las cuatro ramas canonicas.

## Investigacion repo-wide de herramientas 2026-08-10

- La busqueda se amplio mas alla de curatoria: runtime Flujo, Hub MAK,
  research, XIO, SVG/GLSL, Blender, Adobe, RD, superficies publicas y
  almacenamiento.
- El repo ya contiene piezas para casi todos esos frentes: `mak_plataforma`,
  `mak_research`, `mak_curatoria`, `mak_codex`, `mak_xio_puente`, `xio`,
  `iskvw/piel`, `svg`, `projects` y el frontend React/Vite de `web`.
- MAK tiene 23 MB en `director_runs`, 492 KB de ledger comun y 996 KB de
  material; Windows tiene grandes dependencias locales en `venv` y `web`,
  pero eso no equivale a catalogo de archivos del usuario.
- La recomendacion no es adoptar una plataforma completa sin prueba. Se
  estudiaran patrones de Hydrus (tags y API), PhotoPrism (EXIF/XMP y
  sidecars), Recoll/Tropy (busqueda y objetos de investigacion), SQLite FTS5
  (indice derivado), Sigma/Pixi (render WebGL) y AcoustID/Essentia (audio).
- Kestra/n8n se consideran referencias para reintentos, webhooks y gates
  humanos, no reemplazos inmediatos de Capataz/tandas. Gradio queda como
  cockpit de modelos, no como editor principal.
- Referencias artisticas: thi.ng/umbrella, Shadertoy y Blender Python siguen
  siendo candidatas para una capa creativa declarativa, separada del catalogo.
- No se instalaron herramientas, no se movieron archivos y no se cambio el
  codigo. Se verificaron MAK y endpoints: escena ~0.95 s, sugerencias con mapa
  ~1.9 s y mapa completo 11.5 s en la primera carga, con 4.3 MB de respuesta.

## Next action

Construir en MAK un laboratorio aislado de comparacion, no productivo: una
prueba de catalogo/index, una prueba de mapa con 7000 nodos y una prueba de
audio/metadata. Medir valor, memoria, licencia, integracion con los contratos
existentes y capacidad de degradar sin modelos externos. Solo despues elegir
que pieza entra al sistema; el ledger y el Hub siguen siendo las superficies
de integracion y no se crea otro sistema de verdad.

## Auditoria de orden repo-wide 2026-08-10

- No hay una quinta rama: el checkout y los remotos exponen solo `main`,
  `mak`, `rd` e `iskvw`. No se hizo ninguna operacion destructiva.
- La duplicacion real mas clara esta en `xio/new/plugins/`: es una copia stale
  de tres plugins. La ruta viva es `xio/new-plugins/`, confirmada por
  `xio/RUNBOOK.md` y `xio/new/server.py`.
- `mak_codex/fallback_util.py` y `mak_research/fallback_util.py` son espejos
  byte-a-byte exigidos por el despliegue plano y por un ratchet; no son dos
  comportamientos. Consolidarlos requiere cambiar el mecanismo de despliegue,
  no borrar uno a mano.
- `src/flujo/index/db.py`, `src/flujo/index/indexer.py`, `src/flujo/rd/database.py`,
  `src/flujo/knowledge/store.py`, `contrato_archivo.py` y el inbox de portfolio
  tienen alcances distintos. El problema principal es frontera y contrato,
  no que todos sean copias.
- Existen varias superficies HTTP: Flujo React/Vite, servidor Flujo stdlib,
  Hub MAK, interfaz Research, interfaz Codex e editor `iskvw/editor.html`.
  El editor ya es servido por Hub MAK; el panel React de Portafolio es solo
  catalogo publico de lectura. No deben convertirse en dos editores.
- Se escribio el informe operativo
  `_logs/cauce_director/20260805/REPO_ORDER_AUDIT_20260810.md` con hashes,
  alcances, duplicados exactos y la arquitectura recomendada.

## Next action

Ejecutar en MAK un laboratorio aislado y no productivo que compare el indice
JSONL actual, una proyeccion SQLite FTS5 derivada y la proyeccion GTM cacheada
con una muestra pequena del portfolio. Medir cold/warm latency, memoria,
bytes, rebuild y degradacion sin modelos. No instalar una plataforma externa,
no borrar `xio/new/plugins/`, no centralizar el fallback todavia y no tocar
la interfaz hasta que el motor ganador este medido.

## Resultado laboratorio de indice MAK 2026-08-10

- Corrida aislada contra 7,044 items del inbox, sin tocar el run vivo.
- Carga JSON: 28.08 ms; proyeccion SQLite FTS5 en memoria: 57.15 ms.
- Veinte consultas FTS5: 0.22 ms total, 0.01 ms promedio en el termino
  medido. La memoria maxima del proceso fue 52,876 KB (+33,084 KB).
- El mapa actual respondio 4,360,447 bytes; en esta corrida tardo 108.17 ms y
  136.46 ms en dos llamadas cacheadas. El dato confirma que el problema a
  resolver es la proyeccion/tamano de respuesta, no el HTML.
- No se promovio SQLite, no se agrego dependencia y no se escribio en la
  persistencia viva. Informe completo:
  `_logs/cauce_director/20260805/REPO_ORDER_AUDIT_20260810.md`.

## Next action

Repetir el laboratorio con SQLite en disco y un mapa reducido que conserve
identidad, fecha, tipo y relaciones explicitamente declaradas. Comparar
rebuild, warm query, bytes, memoria y caida sin Ollama. Si gana, conectar esa
proyeccion detras de los endpoints existentes; no crear un catalogo paralelo.

## Storage audit MAK 2026-08-10

- `lsblk` confirma `/dev/sdb3`: NTFS, label `Disco local M2`, 446.5G,
  actualmente sin montar. No se monto ni se escribio.
- La raiz de MAK tiene 136G libres. `portfolio_media` usa 5.5G; el catalogo
  no necesita copiar los originales para indexarlos.
- Direccion elegida: SSD como fuente de originales, montado primero read-only;
  indice y ledger en ext4 interno; cache de miniaturas/proxies con limite;
  respaldo separado mediante Syncthing o rclone. Los paths deben registrar
  volumen/UUID + ruta relativa, no depender solo de `/mnt/...`.
- No usar mergerfs/SnapRAID todavia: primero separar fuente, indice, cache y
  backup; un pool prematuro oculta que disco contiene cada original.

## Next action

Montar `/dev/sdb3` en MAK en modo read-only, comprobar UUID, contar archivos y
medir una muestra de metadata sin generar thumbnails. Luego decidir si el
indice admite el volumen sin copiar datos. Solo despues habilitar cache y
respaldo; nunca reorganizar fisicamente los originales durante esa prueba.

## Piloto herramienta visual externa MAK 2026-08-10

- La auditoria anterior de herramientas fue insuficiente porque comparo
  nombres de aplicaciones y no midio el cuello de botella real. Se mantuvo la
  decision de no instalar un DAM monolitico y se abrio un laboratorio aislado
  en MAK, fuera del repo y sin tocar el inbox vivo.
- Se creo `~/venvs/visual-index-pilot` y se instalaron `torch 2.13.0+cu130`,
  `faiss 1.15.0` y `open_clip 3.3.0`; MAK confirmo CUDA activo en una NVIDIA
  GeForce GTX 1650. No se agregaron dependencias al repo.
- OpenCLIP ViT-B-32 no pudo descargar sus pesos desde Hugging Face dentro del
  limite; el proceso fue terminado y se elimino la descarga incompleta. No se
  considero ese modelo valido por defecto.
- Se cambio a MobileCLIP-S0 desde el repositorio oficial de Apple. El peso
  `~/models/mobileclip/mobileclip_s0.pt` quedo descargado fuera del repo y el
  codigo se instalo en `~/src/ml-mobileclip` dentro del entorno aislado.
- Corrida real: 100 imagenes de `/home/mak/portfolio_media`, sin generar
  thumbnails persistentes. Carga del modelo 1.116 s; codificacion 0.644 s;
  155.2 items/s; vector de 512 dimensiones; indice FAISS de 204,845 bytes.
  El proceso uso hasta 1,588,140 KB de RSS durante la corrida, por lo que no
  debe convertirse aun en un daemon permanente: debe correr como worker
  acotado y liberar memoria al terminar.
- Artefactos de laboratorio: `~/labs/visual-index-pilot/mobileclip-s0-100.json`
  y `mobileclip-s0-100.index`. No se copio ningun original ni se escribio en
  la curatoria, el ledger o el repo.

## Decision and next action

La herramienta con mejor relacion entre tiempo ahorrado y riesgo no es
Immich, PhotoPrism, Hydrus ni ResourceSpace como segundo sistema. Es una capa
visual derivada sobre el catalogo existente: MobileCLIP para vectores, FAISS
para vecinos, y GTM para la proyeccion que ya tiene el repo. Debe conservar
fuente, modelo, version, score y estado humano de cada relacion; no debe
convertir similitud visual en verdad ni copiar archivos.

Repetir el piloto con una muestra que mezcle imagenes, carruseles y un frame
representativo por video; comparar vecinos visuales contra metadata y las
selecciones reales ya guardadas. Medir RAM de un worker y extrapolar el costo
para 7,044 items. Solo si la precision de candidatos y el costo son utiles,
conectar los vectores como indice derivado detras de los endpoints existentes.

## Web verification 2026-08-10

- The first push of the refreshed handoff had one real failure in
  `tests/test_privacidad_repo.py`: the documentation contained the literal
  personal Windows user path, which violates the repository privacy gate.
- The handoff now describes the `.roo/worktrees/` location without embedding a
  Windows username. The focused privacy test passes locally (`3 passed`).
- The repair is commit `db235527`, and all four remote branches plus MAK's
  local branches point to it. GitHub checks for this repair were still running
  at handoff time; do not call the web repo green until CI and security finish.

## Next action — current director checkpoint 2026-08-10

The next agent must not reopen the old portfolio interface or start another
UI patch cycle. The active surface is the GTM/map editor already served by the
MAK Hub at `/portafolio/`; its current limitation is the byte-level drift
between the Windows editor and the deployed MAK copy, not proof that the old
editor is still active.

1. Treat `/home/mak/flujo/iskvw/editor.html` as the current operational winner
   because it is the file served by Hub and has the newer modification time.
   Diff it against `C:\IA\flujo\iskvw\editor.html`, preserve the MAK winner,
   and sync back only after the difference is understood.
2. Keep the isolated MobileCLIP-S0 + FAISS pilot outside the repo. Extend it
   to a 100-item mixed sample containing image, carousel and representative
   video frames; do not generate permanent thumbnails or process all 7,044
   records.
3. Compare visual neighbors against explicit metadata and the user's already
   recorded decisions. Report precision, abstentions, RAM, cold start and
   index size. Similarity alone is not a curatorial truth.
4. If the sample is useful, connect only the derived vector lookup to the
   existing catalog/GTM/copilot endpoints. Do not add a second DAM, database,
   editor or ledger. If it is not useful, remove only the isolated pilot
   artifacts and retain the measured conclusion.

The branch state is not fully synchronized: Windows `main` is `cb7214b2`,
while Windows `mak`/`rd`/`iskvw` and all MAK branches are `fdc966f0`. The
README restoration is therefore a separate promotion decision, not something
to silently copy while reconciling the editor.

No commit, push, merge, branch deletion or public promotion is authorized by
this checkpoint. The next durable update must record the branch decision, the
editor diff and the mixed-sample measurement here before any integration
decision.

## Implementacion visual derivada MobileCLIP/FAISS 2026-08-10

- Se trabajo en la rama `mak`, sin commit ni push. Se extendio el catalogo
  existente; no se creo otro editor, ledger, base de datos o framework.
- Archivos del circuito: `cultura/mak_plataforma/visual_index.py`, cambios en
  `copilot.py`, `hub.py`, `contrato_archivo.py`, `iskvw/mesa_montaje.js`,
  `iskvw/editor.html` y pruebas focalizadas en `tests/`.
- El worker incremental vive fuera del repo en
  `/home/mak/plataforma/derived/visual-index/`. Guarda FAISS, vectores y
  metadata por `work_id`, `source_id`, hash, modelo, version, fecha y
  dimension. Los carruseles se agrupan por `publication_id`; los videos usan
  frame temporal de `ffprobe`/`ffmpeg`; no quedan thumbnails permanentes.
- Corrida real medida en MAK con MobileCLIP-S0 + FAISS: 100 unidades, 216
  entradas, 34 carruseles, 38 unidades con video, 42 frames temporales,
  512 dimensiones, 293 vecinos elegibles, 507 abstenciones, 0 fallos,
  indice de 205,690 bytes y 19.529 s. Segunda corrida: 0 codificaciones,
  100 reutilizaciones por hash y 6.105 s.
- El Hub expone `visual_similarity` con score, margen, modelo, version y
  motivo. La lente visual del editor GTM/mapa muestra la sugerencia en la
  pieza activa y conserva el filtro contra relaciones metadata duplicadas.
  La escena comprobada devolvio una relacion visual con evidencia y acciones
  humanas `accept`/`reject`.
- La persistencia accept/reject fue probada en un archivo temporal aislado:
  dos filas con facet/evidence `visual_similarity`, `MobileCLIP-S0` y
  `work_id`; no se escribio una decision humana ficticia en el catalogo real.
- Fallback comprobado: indice ausente devuelve superficie vacia sin importar
  `torch`. `mak-hub.service` siguio activo con RSS de 149320 KB y sin mappings
  de `torch`, `mobileclip` o `faiss`.
- Pruebas focalizadas: `102 passed` en visual index, copilot, bridge del Hub
  y contrato del editor; tambien pasaron `py_compile`, `node --check` y
  `git diff --check`.
- Hub y editor desplegados de forma intencional en MAK; no se reinicio el
  servicio despues de generar el indice. La primera corrida fallo antes de
  ejecutar porque faltaba el worker en el checkout MAK; se copio solo ese
  archivo y la segunda ejecucion fue correcta.

## Next action — visual integration block

Comparar en la muestra de 100 las sugerencias `visual_similarity` contra las
relaciones metadata y las decisiones humanas existentes; ajustar umbrales o
ranking solo con esa evidencia. Despues extender el contrato de feedback y
la vista de evidencia si la precision justifica el cambio. No procesar los
7,044 registros, no generar thumbnails, no cambiar README/SVG y no hacer
commit o push sin instruccion explicita.

## Ronda 4 — cierre de despliegue MAK 2026-08-10

- Rama Windows: `mak`, commit base sin cambios de commit. El diff semantico
  del editor es una sola linea: `mesa_montaje.js?v=20260810-visual-index1`.
  No se normalizaron CRLF/LF porque el archivo operativo de MAK y Windows ya
  son byte-identicos; normalizarlo habria creado ruido innecesario.
- Hashes SHA256 Windows = runtime MAK en los seis archivos comprobados:
  `hub.py` `e18b1a9583a5e1718dc101165a781a4b9a7a1347b431bb84dc33ae17ceba6c35`;
  `copilot.py` `a4a23b3cc4c2a5e7e96952d1504371e06d56af49a601fee1fce28992ee1ff56d`;
  `contrato_archivo.py` `1ea03c209c09f13f6c7a41f7942d2d7ce9423af7e23f657abbfec6283881e9fa`;
  `visual_index.py` `2cbca673c1edaada07a1371fdc84f6a152ece623b89134b966886fc37298e184`;
  `editor.html` `757017bf3c64beeb594034f7bef827fbfae67706cd47c47de655914e14d11d5a`;
  `mesa_montaje.js` `379dd8104191eb24c91eb583d4259090d97fcc339733b86b503cec29eacb5643`.
- No hubo archivos que copiar en esta ronda: los seis ya estaban desplegados
  y coincidian. Se verifico `/home/mak/plataforma` como runtime del Hub y
  `/home/mak/flujo/iskvw` como editor servido. El indice sigue fuera del repo
  en `/home/mak/plataforma/derived/visual-index/`.
- Sintaxis comprobada antes del reinicio: `py_compile` local y en MAK,
  `node --check` local. `mak-hub.service` activo despues del reinicio,
  PID 28909, RSS 108372 KB y sin mappings de `torch`, `mobileclip` o `faiss`.
- Endpoints comprobados: `/api/organismo`, `/api/salud`,
  `/api/portfolio/copilot/status`, `/api/portfolio/copilot/scene`,
  `/api/portfolio/copilot/suggestions` y `/portafolio/`. La escena visual
  devolvio `visual_similarity` con score, margen, modelo y evidencia; el
  editor servido mantiene el GTM/mapa y la lente visual.
- Carrusel comprobado como una unidad `publication:posts_1.json:403` con
  tres medios; video comprobado con `video_representative_frame` temporal.
  Fallback de indice ausente devolvio superficie vacia. Accept/reject produjo
  dos filas temporales con modelo y facet visual, sin escribir ledger real.
- Resultado de corrida real sin cambios: 100 unidades, 216 entradas, 34
  carruseles, 38 videos, 42 frames, 293 vecinos elegibles, 507 abstenciones,
  0 fallos; incremental posterior 0 codificaciones y 100 reutilizaciones.

## Next action — precision visual

No queda diferencia funcional pendiente de despliegue en esta fase. El bloque
pendiente es comparar precision `visual_similarity` contra metadata y
decisiones humanas en la muestra de 100 antes de cambiar ranking o umbrales.

## Reorientacion — integraciones permanentes 2026-08-10

- Se inspeccionaron sin escaneo masivo `C:\IA\Ascii-Motion`, `web/`,
  `src/flujo`, `xio/`, `tools/` y las referencias vendorizadas de thi.ng.
  `adobe/` y `blender/` no existen como directorios raíz; los bridges reales
  están bajo `tools/`. La matriz durable queda en
  `context/INTEGRATION_MATRIX_20260810.md`.
- Integración visual permanente realizada: `iskvw/mesa_montaje.js` adopta el
  patrón comprobable de Ascii-Motion de mutaciones directas coalescidas por
  `requestAnimationFrame`. Cámara y popover comparten un scheduler por frame;
  el editor expone fps/calidad de render y reduce transiciones/halos cuando la
  media de frame supera 32 ms. No se creó React, servidor, base, frontend ni
  thumbnail paralelo.
- Integración de evidencia permanente realizada:
  `cultura/mak_plataforma/xio_evidence.py` lee solo el show kit local
  comprobable (setlist, cues, duración y anotación), construye `mak-work-v1`
  con `ledger.build_work_envelope`, y expone átomos separados para evento,
  fecha y timecode. Artista, venue y productora quedan `unknown`; no se
  vinculan automáticamente a una pieza ni se escribe una decisión al ledger.
  Hub y editor lo muestran como `xio_evidence` dentro de la escena existente.
- Endpoint nuevo focalizado: `GET /api/portfolio/copilot/xio-evidence`.
  La escena comprobada `GET /api/portfolio/copilot/scene?item_id=17991310565372795.mp4&facet=visual_similarity&surface=relate`
  devuelve simultáneamente `visual_similarity`, carrusel agrupado y
  `xio_evidence`. El show kit devolvió 21 setlist/cues, fecha `2026-07-24`,
  evento `DREF CHOCOLATE` y `work_valid=true`.
- Archivos funcionales desplegados tras comparar SHA256: `hub.py`,
  `xio_evidence.py`, `iskvw/editor.html` y `iskvw/mesa_montaje.js`.
  Hashes runtime MAK: `hub.py`
  `5d20cd75ed58aabc8ecdc0444390bb73cb9ed5d74fd8c086d13e558e6fb8f382`;
  `xio_evidence.py`
  `4577a72645a91e41f3a86abc7ecd1f7ed89c298fde20191f7866b139ae51e541`;
  `editor.html`
  `d38ea83933ff7facc339f508c71dd0b263dccb03660b5cc412e4a681d7a79e72`;
  `mesa_montaje.js`
  `3c83ed4ad0a22a92e7bc1164cf94a371ad3cc015dce73e2c6886585292852c6a`.
- Verificación MAK real: `systemctl --user is-active mak-hub.service` =
  `active`; `GET /portafolio/` = HTTP 200 y sirve
  `mesa_montaje.js?v=20260810-visual-index2`; PID 31840, RSS 106892 KB,
  mappings de `torch|faiss|mobileclip` = 0. La comprobación inicial con
  `systemctl is-active` fue un falso negativo por consultar el ámbito de
  sistema; la unidad existe y opera en el ámbito de usuario.
- Pruebas focalizadas: 74 passed en XIO, visual index, copilot, bridge y
  contrato del editor; `py_compile` remoto/local y `node --check` pasaron.
  La única corrección de prueba fue actualizar el sufijo cache-busting de
  `visual-index1` a `visual-index2`.
- Tanda externa posterior a las interfaces: 10 unidades ya abstinentes en
  `derived/visual-index/neighbors.json`, 5 Watsonx y 5 AWS, 0 errores.
  Salida aislada: `/home/mak/plataforma/derived/external-candidates/round-20260810-172526.jsonl`.
  Las 10 filas conservan `work_id`, evidencia local, proveedor, confianza,
  abstención y siguiente acción `human_review`; permanecen candidatas y no
  fueron promovidas al ledger.
- Fallo/limitación registrada: el endpoint no implementa HEAD (501); la ruta
  operativa fue verificada con GET. No se procesaron los 7.044 registros, no
  se modificó README/SVG, no hubo commit/push/merge ni ramas auxiliares.

## Next action — evidencia y rendimiento

Hacer una revisión humana acotada de los 10 candidatos externos y de la
presentación `xio_evidence` en la pieza activa; solo después decidir si el
scheduler o la confianza visual requieren ajuste. Mantener artista,
venue/productora como desconocidos hasta una fuente declarativa y no promover
los JSONL externos al ledger automáticamente.

## Correccion de rumbo — Flow, Ascii-Motion e Instagram 2026-08-10

- XIO queda fuera del circuito de cierre de esta ronda. No se hicieron nuevas
  consultas, no se usaron sus candidatos y no se actualizo la matriz de
  integracion.
- Flow fue localizado en `web/`; su capacidad concreta reutilizada es el
  patron de `web/public/mapping.html`: canvas con `translate/scale` alrededor
  del centro y render por lotes. `iskvw/mesa_montaje.js` lo integra como una
  capa `mesa-flow-canvas` dentro del escenario GTM existente. La capa dibuja
  halos y nodos en lotes de 72 con `requestAnimationFrame`, expone
  `data-flow-render` y el progreso en el readout del editor. No se creo otro
  frontend, servidor ni superficie paralela.
- Ascii-Motion fue usado desde `C:\\IA\\Ascii-Motion\\src\\types\\easing.ts`.
  La implementacion permanente porta `evaluateEasing`/Bezier de
  `interpolateBetweenKeyframes` como `asciiMotionEase` y
  `asciiMotionInterpolate`; centra la pieza activa con `ease-out` en el mismo
  movimiento de camara del editor. No se carga Ascii-Motion como dependencia
  runtime.
- `instagram_source.py` genera referencias, nunca copias, bajo el contrato
  `mak-work-v1`. La muestra real produjo 6 archivos de metadata, 8.241 medios
  observados, 100 unidades seleccionadas y 213 referencias; 34 unidades son
  carruseles, 32 stories y 1 reel. Las stories son `story_record` con
  `stories_are_not_works=true`; los carruseles conservan un unico
  `publication_id` y sus miembros.
- El indice canonico sigue siendo
  `/home/mak/plataforma/derived/visual-index/`. La comprobacion remota no
  encontro un segundo motor `visual-index2`; solo existe
  `/home/mak/plataforma/visual_index.py` (ademas del checkout de flujo). Se
  agrego una sola opcion `--instagram-catalog` y una sola cache/contrato.
- Catalogo desplegado sin medios originales:
  `/home/mak/plataforma/derived/visual-index/instagram_catalog_20260810.json`.
  Hash `5e4059000d4bac35187365f53acaeaa39a2f5b2c296b3a48c75f3655b6742cf0`.
- Corrida real del worker con
  `/home/mak/venvs/visual-index-pilot/bin/python`: 100 unidades, 209 entradas,
  34 carruseles, 22 frames temporales, 80 filas con provenance Instagram,
  29 stories y 32 carruseles dentro de `vectors.jsonl`, 73 codificaciones,
  27 reutilizaciones, 0 fallos, 333 vecinos elegibles y 14,287 s.
- Tanda externa posterior a la integración: 20 casos reales del catálogo,
  10 Watsonx y 10 AWS; 20 hipótesis candidatas, 0 errores finales, todas con
  `work_id`, `source_id`, evidencia, proveedor, confianza, abstención,
  `next_action=human_review` y `promotion=not_promoted`. Salida aislada en
  `/home/mak/plataforma/derived/instagram-external/round-20260810.jsonl`.
  El primer intento AWS con el worker visual dio `boto3_unavailable`; se
  reejecutaron esos mismos 10 casos con `/home/mak/venv-providers`, sin
  ampliar la muestra ni promover resultados.
- Hashes Windows = runtime MAK para los archivos activos: `hub.py`
  `5d20cd75ed58aabc8ecdc0444390bb73cb9ed5d74fd8c086d13e558e6fb8f382`,
  `copilot.py`
  `c4bcaad96d9f5c06e92efb4bd9a7d4274e9e28110b3c22d52edf2510ab5d9142`,
  `contrato_archivo.py`
  `1ea03c209c09f13f6c7a41f7942d2d7ce9423af7e23f657abbfec6283881e9fa`,
  `visual_index.py`
  `8b9ffbc866695d75416263b403803dbc3c5dfad15f11535c1f05a3ade773a96c`,
  `instagram_source.py`
  `239b445046c8a5f8b1318feb6633fe576a95eb04be3fd5a88a086b1f144147a4`,
  `iskvw/editor.html`
  `8a6fc0de4f240927ad0b949a90224045168f35a86d39e32b5d17483af9f7d302`,
  `iskvw/mesa_montaje.js`
  `90f3aa90a568e5df5cce032e23c49e4c7734fdbb6f09901788a4f0c92300e425`.
- Verificacion MAK final: `systemctl --user is-active mak-hub.service` =
  `active`, PID 37858, RSS 33.944 KB y mappings `torch|faiss|mobileclip` = 0.
  `/portafolio/` devolvio el editor con `mesa-flow-canvas`; status reporto
  `indexed_units=100`, `source_catalog=faro-instagram-source-v1` y 333
  vecinos elegibles. `visual-index` y la escena existente devolvieron
  `visual_similarity` con score, margen, modelo y provenance.
- Verificacion focalizada final: `py_compile` local/remoto, `node --check`
  local, `git diff --check` y tests de visual index, copilot, editor y bridge:
  74 tests pasaron. No hubo commit, push, CI, cambios a README/SVG ni
  movimiento de medios.

## Next action — gate humano de evidencia externa

Revisar únicamente las 20 filas aisladas de
`derived/instagram-external/round-20260810.jsonl` dentro del flujo existente;
decidir cuáles, si alguna, pueden entrar al circuito humano. Mantenerlas fuera
del ledger hasta esa decisión y conservar XIO como adaptador opcional no
bloqueante.

## Correccion — hypotheses externas visibles en el editor 2026-08-10

- Se corrigio el circuito que faltaba: la interfaz de curatoria ya no depende
  de que una hipótesis externa haya sido ingerida previamente como candidato
  del ledger. `hub.py` lee el JSONL aislado
  `/home/mak/plataforma/derived/instagram-external/round-20260810.jsonl` y lo
  proyecta en la cola existente `/api/portfolio/review-queue`.
- La cola MAK devuelve 20 candidatos pendientes. El endpoint por pieza
  `/api/portfolio/external-candidates?item_id=17884747708722082.jpg` devuelve
  proveedor, hipótesis, confianza, evidencia, `story_record`/agrupación y
  `promotion=not_promoted`.
- Las acciones existentes del editor (`aceptar candidato`, `dejar en
  revisión`, `rechazar candidato`) funcionan también para los IDs
  `instagram-external:<work_id>`. La decisión se guarda como revisión humana
  append-only en el ledger común; no muta el JSONL original, no publica y no
  promueve automáticamente.
- Archivos funcionales desplegados: `cultura/mak_plataforma/hub.py` y el
  test focalizado `tests/test_mak_portfolio_bridge.py`. Pruebas finales:
  74 pasaron; `py_compile`, `node --check` y `git diff --check` pasaron.
  `mak-hub.service` quedó `active` después del reinicio.

## Next action — usar la interfaz de curatoria

Abrir `/portafolio/`, expandir `revisión humana` y revisar los 20 candidatos
desde sus miniaturas y evidencia. La decisión debe hacerse allí; el chat no es
la superficie de curatoria. Mantener las hipótesis como candidatas hasta que
exista una decisión humana explícita.

## Gate tecnico de evidencia externa — cierre 2026-08-10

- Se contrastaron las 20 filas de
  `/home/mak/plataforma/derived/instagram-external/round-20260810.jsonl`
  contra el catalogo, `vectors.jsonl` y `neighbors.json`. Informe aislado:
  `/home/mak/plataforma/derived/instagram-external/round-20260810-review.jsonl`;
  resumen:
  `/home/mak/plataforma/derived/instagram-external/round-20260810-review-summary.json`.
- Resultado: 20/20 con catalogo, 20/20 con vector local, 20/20 candidatas,
  6 `story_record`, 7 carruseles, 0 flags tecnicos y 20/20 con
  `promotion=not_promoted`. Se agrego al JSONL aislado el marcador
  determinista `stories_are_not_works=true` para las 6 stories.
- Se corrigio `visual_index.py`: la muestra de 100 prioriza explicitamente
  las unidades de `instagram_export` antes de completar con fallback del inbox,
  y `group_portfolio_items` conserva provenance Instagram si cualquier miembro
  de la unidad la trae. El export tiene 98 unidades unicas indexables; dos
  referencias del catalogo son el mismo medio repetido entre archivos del
  export y se mantienen como referencia, no como obras duplicadas.
- Nueva corrida incremental: 100 unidades, 209 entradas, 34 carruseles, 32
  stories, 18 codificaciones, 82 reutilizaciones, 0 fallos, 345 vecinos
  elegibles y 6,484 s. Hash Windows/runtime de `visual_index.py`:
  `72b05fd972bf00b08967f5b3adf772ed6207e4e020739df8a23f3d4055f67876`.
- Tras el reinicio, `mak-hub.service` sigue `active`, PID 40444, RSS 33908 KB,
  mappings de `torch|faiss|mobileclip` = 0. Status mantiene 100 unidades,
  345 vecinos elegibles y `faro-instagram-source-v1`.
- Pruebas finales: 74 tests focalizados, `py_compile` remoto, `node --check`
  local y `git diff --check` pasaron. No hubo ledger, commit, push ni CI.

## Next action — decision humana

Las 20 hipótesis están técnicamente listas para revisión humana. La siguiente
acción es decidir aceptar, rechazar o abstener cada una dentro del flujo
existente; solo después de esa decisión se puede evaluar una promoción al
ledger o un ajuste de ranking. XIO sigue opcional y no bloquea este circuito.

## Corrección de superficie — una sola mesa operativa 2026-08-10

- Se eliminó la confusión visible con la superficie antigua en `/portafolio/`:
  el documento ahora se titula `MAK · Campo de orden · archivo vivo`; la
  cabecera histórica y los paneles antiguos se ocultan cuando
  `body.mesa-active` monta la mesa GTM/mapa. No se borró código histórico ni se
  creó otra interfaz.
- La mesa actual conserva GTM/mapa, canvas Flow, pieza activa, carruseles
  agrupados y decisiones humanas. El HUD muestra `evidencia externa` y abre la
  siguiente hipótesis dentro del mismo mapa; el popover de la pieza muestra
  proveedor, confianza, hipótesis, agrupación, estado no canónico y acciones de
  aceptar, revisar o rechazar. Las decisiones usan el endpoint existente
  `/api/portfolio/external-candidates/review` y permanecen no publicadas.
- Hashes desplegados y comprobados:
  `iskvw/editor.html` Windows/MAK =
  `c481339ed061ebad1a41f2c07492c2fae9028288025bf54e1490f1560031552f`;
  `iskvw/mesa_montaje.js` Windows/MAK =
  El SHA comprobado es
  `843c38aa9a21bbb9b184e0678aea93588732821a69dedc532ea8287f0ee8246d`.
- Comandos reales: `scp` de los dos archivos a
  `/home/mak/flujo/iskvw/`; `systemctl --user is-active mak-hub.service` =
  `active`; `/portafolio/`, `/api/portfolio/inbox`,
  `/api/portfolio/external-candidates` y `/api/portfolio/copilot/scene`
  respondieron `200`. El JS servido correcto es
  `/portafolio/mesa_montaje.js?v=20260810-visual-index2` y contiene el HUD,
  la revisión externa y el endpoint de decisión.
- El endpoint vivo devolvió 27 candidatos externos combinados, 20 pendientes
  y 16 filas aisladas `instagram-external:*`; la superficie cuenta solo los
  pendientes. La cola antigua no se expone como panel separado.
- Verificación: `node --check iskvw/mesa_montaje.js`,
  `python -m py_compile cultura/mak_plataforma/hub.py`,
  `git diff --check` y pruebas focalizadas de editor, bridge, índice visual y
  copilot pasaron. El primer intento de pytest falló solo por `PYTHONPATH`
  ausente; se repitió con el raíz del repo y pasó. No hubo commit, push, CI ni
  reinicio del servicio durante esta corrección.

## Next action — revisión humana en la mesa actual

Abrir o recargar `/portafolio/` con `Ctrl+F5`. Usar el botón `evidencia
externa` del HUD para centrar una hipótesis y decidirla dentro del popover de
la pieza. No abrir ni mantener la superficie antigua como flujo de trabajo.

## Corrección — frontera humana no bloquea vecinos 2026-08-10

- Reporte reproducible: después de descartar varias piezas y marcar una pieza
  semilla como `registro`, los nodos vecinos parecían inactivos.
- Causa: `applyOrderDecision()` conservaba `humanSeedActive=true` después de
  una decisión explícita distinta de `descartar`. `toggleOrderSelection()`
  rechazaba entonces cualquier vecino para mantener aislada la frontera humana.
  No era una mezcla con la superficie antigua; ocurría en el `mesa_montaje.js`
  servido por `/portafolio/`.
- Corrección: después de guardar `obra`, `registro` o `revisar`, la frontera se
  libera, se limpia `humanSeedItemId` y los vecinos vuelven a ser seleccionables
  e interactivos. `siguiente frontera` sigue iniciando otra revisión aislada.
  El descarte continúa avanzando automáticamente a la siguiente semilla.
- Verificación: `node --check iskvw/mesa_montaje.js`, pruebas focalizadas de
  editor y bridge, y `git diff --check` pasaron. El hash Windows/runtime del
  JS corregido es
  `85e3c5b41037360a2ddf62ea3f44023aa3449a981bd7b1d5618bf11949fa0019`.
  MAK devolvió el mismo hash, `mak-hub.service` = `active` y el JS servido por
  `/portafolio/mesa_montaje.js?v=20260810-visual-index2` contiene el nuevo
  desbloqueo.

## Next action — comprobar la interacción vecina

Recargar `/portafolio/` con `Ctrl+F5`, marcar una pieza como `registro` y luego
hacer clic en una obra vecina. Debe volver a seleccionarse y mostrar su HUD;
`siguiente frontera` queda como acción explícita para volver al modo aislado.

## Verificación de clic — `registro` 2026-08-10

- El último clic confirmado en MAK fue para `18408020584187134.jpg`, una
  `story` de `stories.json:330`, fecha `2025-10-24`.
- La clasificación quedó persistida en
  `/home/mak/plataforma/director_runs/portfolio-editor-20260808/classifications.jsonl`
  a las `2026-08-10T18:39:34-0400` como `triage=record`,
  `status=human_draft`, `promotion=none`.
- `/api/portfolio/inbox` devuelve para esa pieza `classification.triage=record`
  y `selection=pendiente`. No se movió ni modificó el original, no se publicó
  y no se escribió una verdad canónica en el ledger.
- La respuesta corresponde al circuito de clasificación de la mesa; el JS
  servido ya contiene la liberación de vecinos después de una decisión
  explícita. Si la pestaña aún muestra el estado anterior, recargar con
  `Ctrl+F5` reinicia únicamente el estado visual del cliente.

## Corrección de funcionamiento — decisión semilla avanza automáticamente 2026-08-10

- La regla operativa queda aclarada: una decisión `obra`, `registro` o
  `revisar` en la frontera humana debe persistir la clasificación y cargar la
  siguiente semilla pendiente. `descartar` ya tenía ese comportamiento.
- Se corrigió `iskvw/mesa_montaje.js`: el branch `advanceSeed` ahora llama
  siempre `loadHumanSeed({ refresh: false, excludeId: itemIds[0] })` después de
  cualquier triage válido. No borra el registro anterior ni modifica el medio.
  La salida de la semilla es la siguiente pieza, no una pantalla bloqueada.
- Estado acumulado comprobado en MAK antes del despliegue: 75 clasificaciones
  persistidas (`work=45`, `record=17`, `review=1`, 12 filas sin triage) y 76
  selecciones (`descartar=54`, `seleccionar=13`, `deseleccionar=9`). No se
  necesitó input adicional ni se usó navegador.
- Despliegue y verificación: hash Windows/MAK del JS
  `0d586680a941ce5f7b3dda32d8d00f2440e0dd266f5a80fac6dc0c845672122d`;
  JS servido por `/portafolio/mesa_montaje.js?v=20260810-visual-index2`
  responde `200` y contiene el avance automático; `mak-hub.service` sigue
  `active`. Pasaron `node --check`, `git diff --check` y las pruebas focales
  de editor, bridge, índice visual y copilot.

## Next action — validar por contrato, no por clicks simulados

La siguiente ejecución humana de `registro` debe producir una nueva llamada de
escena para la siguiente semilla. Si se reporta otra anomalía, revisar primero
handler, payload, respuesta y archivos persistidos antes de pedir evidencia al
usuario.

## Tanda de funcionamiento por código — cierre 2026-08-10

- Auditoría estática de la mesa: handlers de selección, clasificación,
  descarte, relación, feedback, navegación, semilla humana, evidencia externa,
  Flow/Canvas y Ascii-Motion revisados con `rg`, `node --check` y el contrato
  focal del editor. Las rutas usadas por la mesa tienen implementación en el
  Hub: `inbox`, `classify`, `classify-batch`, `select`, `feedback`,
  `copilot/learning`, `copilot/scene` y `external-candidates/review`.
- Tanda MAK sin navegador ni clicks simulados: tres escenas reales consultadas
  (`18408020584187134.jpg`, `18117694279761685.jpg`,
  `17890131999386365.jpg`). Resultado: 3/3 `ok`, 30 registros, 27 relaciones
  y mapas con 10, 9 y 8 datos respectivamente. La pieza de prueba devolvió
  una hipótesis externa y su media respondió `200 image/jpeg`.
- Endpoints de superficie comprobados: `/portafolio/`, JS servido,
  `/api/portfolio/inbox`, `classifications`, `boards`, `triangulation`,
  `contract`, `review-queue`, `external-candidates`, `copilot/suggestions`,
  `copilot/scene`, `copilot/map`, `copilot/visual-index`, `copilot/status` y
  `copilot/learning` respondieron con éxito. El inbox reporta 7.044 elementos,
  pero la tanda procesó solo tres escenas acotadas.
- Se encontró y corrigió un fallo de robustez del Hub: respuestas canceladas
  por el cliente producían trazas `BrokenPipeError`. `_send_bytes()` ahora las
  trata como desconexión normal. Se desplegó `hub.py`, se verificó sintaxis y
  se reinició `mak-hub.service`; quedó `active`, sin mappings de
  `torch|faiss|mobileclip`. RSS después de la tanda: 147076 KB.
- Verificación final: `py_compile`, `node --check`, pruebas focales de editor,
  bridge, índice visual y copilot, y `git diff --check` pasaron. No se abrió
  navegador, no se tomaron capturas, no se simularon clicks, no hubo commit ni
  push.

## Next action — mantener la ronda basada en contratos

Si aparece otro fallo, reproducirlo primero mediante el handler y su endpoint,
consultar la persistencia y añadir una prueba focal antes de pedir una nueva
acción humana. No usar la interacción del usuario como sustituto de la
verificación del código.

## Pasada de bug hunting estático — 2026-08-10

- Herramientas disponibles comprobadas: `ruff` local; `semgrep`, `opengrep`,
  `eslint`, `pyright` y `codeql` no estaban instalados. No se descargaron
  dependencias ni se gastaron créditos IBM/AWS.
- `ruff check` encontró 14 hallazgos iniciales: 4 accionables (variables e
  import sin uso en `contrato_archivo.py`, `visual_index.py` y su prueba) y 10
  semicolones heredados del render Markdown del Hub. Se corrigieron todos;
  segunda pasada: `All checks passed!`.
- Se verificó nuevamente `py_compile`, `node --check`, pruebas focales de
  editor, bridge, índice visual y copilot, y `git diff --check`: todo pasó.
- Se desplegaron y se compararon hashes de `hub.py`, `contrato_archivo.py` y
  `visual_index.py` en `/home/mak/plataforma/`; `mak-hub.service` quedó
  `active`. Tanda posterior sobre tres escenas reales: 3/3 `ok`, 30 registros
  y 27 relaciones. Sin Traceback, `BrokenPipe`, `Exception` ni `ERROR` en los
  logs recientes; el Hub sigue sin mappings `torch|faiss|mobileclip`.

## Next action — analizador semántico opcional

La siguiente herramienta útil sería Semgrep sobre `mesa_montaje.js` y el Hub,
si se decide instalarla localmente. ESLint puede revisar JavaScript y CodeQL
queda para una pasada de flujo de datos más pesada. Ninguno es necesario para
ejecutar la interfaz ni reemplaza las pruebas y endpoints ya verificados.

## ESLint — bug funcional corregido 2026-08-10

- `npx eslint@9` sobre `iskvw/mesa_montaje.js` encontró una colisión de nombres:
  la variable local `suggestionMarkup` ocultaba la función del mismo nombre
  dentro de `showRecordPopover()`. Al abrir esa ruta, el `map()` podía resolver
  la variable antes de inicializarla y romper el popover de relaciones.
- Se renombró la variable a `suggestionsDrawerMarkup` y se conectó
  explícitamente `selectRelation()` al handler de relación. ESLint quedó sin
  errores ni warnings con reglas de variables sin uso, código inalcanzable y
  expresiones constantes.
- Se añadió una aserción de contrato para evitar que vuelva la colisión. Pasaron
  `node --check`, las pruebas focales y `git diff --check`.
- Hash Windows/MAK del JS desplegado:
  `5eaa44d3ef1909882a473309098cc9f47aa82d503fe9f9493054f81a3ed0a335`.
  El JS servido por `/portafolio/mesa_montaje.js?v=20260810-visual-index2`
  devuelve `200` y contiene la corrección.

## Next action — mantener lint y regresiones en la ronda de funcionamiento

Continuar con los contratos de decisión y persistencia. No usar otra tanda
IBM/AWS mientras los analizadores locales sigan encontrando y corrigiendo
fallos reproducibles.

## Semgrep — pasada estática 2026-08-10

- Se instaló Semgrep localmente para esta revisión. La instalación generó
  advertencias de compatibilidad en paquetes Python globales no relacionados
  (`opentelemetry`, `open-interpreter`, `open-webui`); no modificó el repo ni
  el runtime MAK.
- Comando principal: `semgrep scan --config p/python --config p/javascript
  --metrics=off` sobre `iskvw/mesa_montaje.js` y los módulos MAK. Resultado:
  5 archivos, 219 reglas, 0 hallazgos.
- `iskvw/editor.html` fue omitido por Semgrep porque es un contenedor HTML con
  JavaScript embebido (`Nothing to scan`). No se afirmó cobertura falsa: ese
  bloque queda cubierto por `node --check`, el contrato focal del editor y las
  pruebas del Hub.
- Verificación posterior: `ruff` = `All checks passed!`, `py_compile`,
  `node --check`, pruebas focales y `git diff --check` pasaron.

## Next action — revisar solo hallazgos reproducibles

Semgrep no dejó hallazgos en los archivos ejecutables principales. El siguiente
paso útil es continuar con regresiones de contratos y rutas; instalar ESLint o
CodeQL solo si aparece un caso que Semgrep y las pruebas locales no puedan
explicar.

## Regresión de contratos y JS inline — 2026-08-10

- Se extrajeron los dos bloques `<script>` de `iskvw/editor.html` y se
  comprobaron con `vm.Script`: 2/2 sin errores de sintaxis y sin nombres de
  función duplicados.
- ESLint 9 sobre el JS inline, con reglas de nombres no definidos, código
  inalcanzable, expresiones constantes, redeclaraciones, casos duplicados y
  `finally` inseguro: 0 errores.
  Los 50 avisos de variables no usadas corresponden a funciones invocadas por
  atributos HTML inline o `catch` heredados; no son fallos de ejecución. El
  JS activo de `mesa_montaje.js` ya quedó limpio en la pasada anterior.
- Prueba MAK por endpoint, sin navegador: se repitió exactamente la
  clasificación existente de `17934891079242401.jpg` mediante
  `/api/portfolio/classify-batch`; respondió HTTP 200, `ok=true` y
  `duplicate=true`, sin crear otra decisión. Un payload vacío respondió
  `ok=false`, `error=grupo_o_clasificacion_vacios`. La escena de esa pieza
  respondió HTTP 200, `ok=true`, 10 registros y 9 relaciones.
- Verificación focal: 74 tests pasaron; `node --check`, `py_compile` y
  `git diff --check` pasaron. El único aviso de diff es la conversión
  automática LF→CRLF ya conocida de Git.
- MAK sigue activo: `mak-hub.service=active`, PID 44548, `VmRSS=147528 kB`,
  sin mappings `torch|faiss|mobileclip` y sin errores recientes en el journal.
  No hubo commit, push, CI, navegador, clicks simulados ni créditos IBM/AWS.

## Next action — contrato de error del bloque histórico

No queda un fallo funcional reproducible en la mesa activa. Si se continúa,
hacer una pasada pequeña para cubrir explícitamente los errores de POST del
JS histórico embebido en `editor.html` o mantenerlo retirado de la superficie
operativa; no usar esa parte legacy como sustituto de la mesa GTM actual.

## Harness de decisiones y fallback — 2026-08-10

- Se ejecutó un harness Node sobre las funciones reales de
  `iskvw/mesa_montaje.js`, con DOM y red visual mockeados; no se abrió
  navegador ni se simularon clicks.
- Las cuatro decisiones de semilla pasaron: `work`, `record` y `review`
  enviaron `/api/portfolio/classify-batch` con `fields.triage` correcto;
  `discard` envió `/api/portfolio/select` con `decision=descartar`,
  `decision_scope=record`, `reason_code=no_es_obra` y `target_id` correcto.
- Las cuatro llamaron a `loadHumanSeed({refresh:false, excludeId:"seed-a"})`;
  ninguna dejó `feedbackBusy` bloqueado ni creó relaciones. El descarte retiró
  la pieza de la escena mockeada.
- El mismo harness verificó el fallback real de `load()`: un HTTP 503 del inbox
  y un fallo de escena producen `mesa-empty-state`, sin excepción no atrapada.
- MAK volvió a responder 200 en `/portafolio/`, `copilot/status`,
  `copilot/visual-index` y una escena acotada. No hubo mutación de decisiones,
  commit, push, CI, navegador ni créditos IBM/AWS.

## Next action — cierre técnico de esta ronda

La lógica activa de decisión, avance y fallback queda cubierta por código.
Solo queda como mantenimiento opcional endurecer el bloque legacy inline; no
es un bloqueo de la mesa GTM/mapa operativa.

## Replay de elecciones humanas — 2026-08-10

- Se integró `replay_ordering_evaluation()` en el `copilot` existente como
  superficie diagnóstica `faro-ordering-replay-v1`. Usa leave-one-out real,
  excluye la respuesta del caso de sus vecinos, separa aciertos de abstenciones
  y nunca muta items, ledger ni promoción.
- Regresiones: tests de copilot, editor y bridge pasaron; Ruff y `py_compile`
  pasaron. El runtime MAK recibió `copilot.py` tras comparar hashes:
  `b1ffcbc7ee1b36138e4c717acc20724e448c2fb6f807aa563d4e006955272aa4`.
  `mak-hub.service` quedó `active`, RSS 34100 kB y sin mappings
  `torch|faiss|mobileclip`.
- Primera muestra real acotada: 24 escenas individuales, 159 registros y 159
  vectores. Se evaluaron 23 etiquetas: 17 `work`, 6 `record`, 0 `review`, 0
  `discard`; cobertura 0.956522, abstención 0.043478, accuracy global
  0.73913 y accuracy selectiva 0.772727. No se afinó el ranking porque la
  muestra no representa las cuatro decisiones.
- La muestra estratificada de selecciones confirmó otra limitación: la escena
  operativa omite piezas ya descartadas. De 12 objetivos, solo 5 aparecieron y
  el replay quedó en 4 casos evaluables (3 `work`, 1 `record`); tampoco se
  usó para calibración.
- Tras el reinicio, una primera escena excedió el timeout de 10 s durante el
  calentamiento; un único reintento acotado respondió 200 en 4.682 s. No hubo
  error persistente en el Hub.

## Next action — muestra balanceada sin fuga

No activar ajustes automáticos con esta muestra. El siguiente bloque debe
exponer una lectura acotada de decisiones históricas, incluyendo descartes sin
hacerlos pasar por la escena que los filtra, y repetir el replay con separación
explícita entre etiquetas `triage` y selección. Solo si hay cobertura mínima
por clase se evalúa ajustar ranking/confianza; la promoción sigue en `none`.

## Separación de etiquetas del replay — 2026-08-10

- `replay_ordering_evaluation()` ahora distingue `label_source=triage` de
  `label_source=selection`, incluye `source_counts`, métricas por fuente y la
  fuente de cada caso. Así `seleccionar` no se presenta como prueba de
  `obra`, aunque el predictor histórico pueda usarlo como señal débil.
- La regresión focal pasó con 74 tests; Ruff, `py_compile` y `git diff --check`
  pasaron. Hash final desplegado de `copilot.py` en Windows y MAK:
  `26444cddff06316a87ba3d5f8c9962bbe47915d60569da3569fae51070373050`.
  `mak-hub.service` sigue `active`, RSS 34308 kB y sin torch/FAISS/MobileCLIP.
- Replay real balanceado por decisiones, con 12 objetos recuperados mediante
  búsquedas dirigidas de sus IDs: 2 etiquetas `triage` y 10 `selection` (4
  seleccionar, 6 descartar). En `triage`: 2 evaluados, 100% abstención por
  muestra insuficiente. En `selection`: 10 evaluados, 8 comprometidos, 20%
  abstención y 50% de accuracy selectiva; cuatro selecciones fueron clasificadas
  como `discard`. El resultado confirma que selección y triage no deben
  mezclarse para calibrar el copiloto.
- No se ajustó ranking, confianza ni ledger; `promotion=none`. La prueba sirve
  para detectar fuga/semántica incorrecta, no para entrenar con solo 12 casos.

## Next action — ampliar solo el conjunto de triage

Construir una muestra acotada con suficientes etiquetas explícitas `work`,
`record`, `review` y `discard`; mantener las selecciones como evaluación
separada de comportamiento de mesa. No promover ni llamar IBM/AWS hasta que
el replay tenga cobertura mínima por clase y los descartes/selecciones no se
usen como sustituto de triage.

## Corrección de descarte y triage — 2026-08-10

- Causa reproducida: la mesa enviaba `descartar` a
  `/api/portfolio/select`; ese endpoint persistía la selección y el ledger,
  pero no escribía la clasificación explícita `triage=discard`. Por eso había
  54 descartes operativos y cero descartes en las métricas de triage.
- `cultura/mak_plataforma/hub.py` ahora conserva la selección y, únicamente
  para `decision=descartar`, `decision_scope=record` y
  `reason_code=no_es_obra`, persiste además `triage=discard` en el contrato de
  clasificación. La evidencia queda marcada como `human_selection`, con
  idempotencia. No se migraron silenciosamente los 54 registros históricos.
- `tests/test_mak_portfolio_bridge.py` cubre el doble registro, la
  idempotencia y la evidencia de origen. Pasaron las pruebas focales de
  portfolio, copilot, editor e índice visual; también `py_compile`, Ruff y
  `git diff --check`.
- Hash local y runtime de `hub.py`:
  `e0172e9f9a3f7aafbef3275315135a0cefef20c41d9cfcb5ce9e50dc16854003`.
  Se comparó antes de copiar y MAK recibió solo este archivo.
- Verificación MAK: `mak-hub.service=active`, `/api/portfolio/copilot/status`
  y `/portafolio/` respondieron 200, el índice visual sigue disponible y el
  proceso no tiene mappings `torch|faiss|mobileclip`. El primer curl tras el
  reinicio llegó antes de abrir el puerto; el reintento acotado pasó y no hubo
  errores del servicio desde el reinicio.
- Estado de datos sin mutación durante la verificación: 54 filas de
  selección `descartar`, 0 filas históricas `triage=discard`, 75 filas de
  clasificación. El cero histórico es intencional: la nueva ruta se aplica a
  los próximos descartes o a una llamada explícita de reparación.

## Next action — usar elecciones históricas sin falsear triage

Mantener los 54 descartes como señal `selection` para el replay y usar la
nueva etiqueta `triage=discard` solo desde decisiones explícitas futuras. No
llamar IBM/AWS ni ajustar el ranking todavía; primero reunir cobertura real
por las cuatro clases sin pedir más clicks al usuario.

## Hunting de invariantes de decisiones — 2026-08-10

- Se trazó el circuito activo por código: `mesa_montaje.js` → endpoint del
  Hub → validación → JSONL/ledger/proyección → escena → navegación. Las rutas
  verificadas fueron `select`, `classify`, `classify-batch`, `feedback`,
  `board`, `external-candidates/review`, `copilot/scene` y
  `copilot/learning`.
- El primer bug confirmado fue la divergencia ya registrada: `descartar`
  escribía `selections.jsonl` y ledger, pero no `triage=discard`.
- El hunting de errores parciales encontró y corrigió cuatro divergencias
  adicionales:
  1. selección guardada con triage fallido devolvía `ok=true`;
  2. feedback aceptado guardado con conexión fallida devolvía `ok=true`;
  3. `board add` ignoraba feedback fallido y guardaba el tablero;
  4. `board add` descartaba IDs inexistentes y fingía éxito.
- La tanda cruzada también encontró dos fallos de visibilidad de estado:
  `classify-batch` no marcaba resultados parciales y el descarte por lote no
  reflejaba en la escena los elementos que sí habían sido guardados cuando
  otro elemento fallaba. Ambos quedaron corregidos; la mesa ahora informa
  `saved`, `partial`, cantidades guardadas y triage/conexión pendientes.
- Pruebas añadidas en `tests/test_mak_portfolio_bridge.py` cubren fallos de
  triage, conexión, feedback de tablero, IDs desconocidos y persistencia
  parcial. El contrato de la mesa comprueba los mensajes de degradación.
- Comando focal: `python -m pytest -q tests/test_mak_portfolio_bridge.py
  tests/test_iskvw_editor_contract.py tests/test_copilot.py
  tests/test_visual_index.py`; resultado: 112 tests pasaron. También pasaron
  `py_compile`, `node --check`, Ruff y `git diff --check`.
- Hashes desplegados tras comparar antes de copiar:
  `hub.py` = `84b2c0e204bfb324e490b6b62751a3329bbf43e0f04a09161c088e7a3e8de727`;
  `mesa_montaje.js` =
  `3d417a15f633e33e04b9172ec54c4db254680858efb6455d6be61a7a58a1ab49`.
  El `py_compile` remoto pasó. MAK no tiene Node instalado; el `node
  --check` se ejecutó localmente y pasó.
- Verificación MAK sin navegador ni mutación humana: `mak-hub.service=active`,
  `/portafolio/`, `copilot/status`, `copilot/learning` y tres escenas reales
  respondieron 200; las tres escenas devolvieron `ok=true`, 10 registros, 9
  relaciones y visual similarity. RSS del Hub: 138908 KB; mappings
  `torch|faiss|mobileclip`: 0; sin errores recientes del servicio.
- POST inválidos dirigidos (`select`, `classify-batch`, `feedback`, `board`)
  devolvieron `ok=false` con error específico y no cambiaron la persistencia.
  Tras la tanda: 58 selecciones efectivas, 20 feedbacks, 31 conexiones y 0
  elementos en tableros; los conteos permanecieron iguales.
- Semgrep y ESLint no están disponibles como comandos persistentes en este
  entorno; no se instalaron dependencias. La cobertura ejecutable queda en
  AST/rg, pruebas focales, `node --check` y endpoints MAK.

## Next action — hunting de superficies aún no cerradas

No migrar todavía los descartes históricos ni ajustar aprendizaje. El próximo
bloque debe aplicar la misma matriz de invariantes a revisión de candidatos
externos, caché de escenas, `board remove` y respuestas HTTP del bloque legacy,
buscando nuevamente escrituras parciales, estados visuales obsoletos y éxitos
falsos antes de proponer otra mejora.

## Cierre de hunting cruzado — 2026-08-10

- Se verificó el siguiente bloque de la matriz sin navegador ni clicks: caché de
  escenas, superficie activa `surface=order`, revisión de candidatos externos,
  `board remove` y handlers HTTP de la superficie legacy.
- Bug confirmado y corregido en `iskvw/mesa_montaje.js`: una clasificación por
  lote actualizaba objetos locales y reconstruía la escena, pero podía dejar una
  escena copilot cacheada anterior. Ahora invalida `sceneCache` después del
  guardado exitoso.
- Bug confirmado y corregido en `cultura/mak_plataforma/hub.py`: la ruta activa
  GTM/mapa `surface=order` omitía `visual_similarity` aunque el índice derivado
  estuviera disponible. La escena operativa ahora expone el canal visual sin
  cargar MobileCLIP, torch ni FAISS en el Hub.
- Bug confirmado y corregido en la revisión externa: repetir el mismo payload
  humano creaba una nueva fila por usar timestamp en el ID. El mismo candidato,
  fuente, decisión, nota, relación y contexto devuelve `duplicate=true`; una
  decisión o nota distinta conserva historial append-only.
- En `iskvw/editor.html` se corrigieron degradaciones del bloque legacy: no se
  retira una pieza de la bandeja antes de confirmar el endpoint; selecciones y
  limpiezas masivas informan parciales; fallos HTTP de tableros, sugerencias,
  revisión, triangulación, contrato, dispatch y feedback ya no se presentan
  como respuesta vacía o éxito visual. `cargarTableros` falla de forma aislada
  para que no aborte la carga del resto del archivo.
- Regresiones focales: 113 tests pasaron (`copilot` 37, contrato/editor 2,
  puente MAK 70, índice visual 4). También pasaron `py_compile`,
  `node --check`, compilación de los scripts inline del editor y `git diff
  --check` (solo advertencias conocidas de normalización LF/CRLF).
- Hashes finales desplegados y comparados antes de copiar:
  `editor.html` =
  `252d14d006d342c8e7a514801d3f35e33840bffde668ed928e638c5aea8906a1`;
  `mesa_montaje.js` =
  `2497814250ae295f27dd5eefded43d2480fe35844b59ca8a47d98d82d33256b6`;
  `hub.py` =
  `8032b467a7104b284cdc4e2e4aa41d7edb30c6f684a7b07e332dbdbb85282093`.
- MAK comprobado tras reinicio: `mak-hub.service=active`, el hash del HTML
  servido por `/portafolio/` coincide con el editor desplegado, `/api/portfolio/
  copilot/status`, `/api/portfolio/copilot/learning` y
  `/api/portfolio/external-candidates` respondieron 200. Una escena real de
  `surface=order` respondió `ok=true`, 10 registros, 9 relaciones y 5
  relaciones `visual_similarity` con MobileCLIP-S0, score 0.783021/margen
  0.051527 en la primera sugerencia. El proceso quedó sin mappings
  `torch|faiss|mobileclip`; RSS tras reinicio 34.4 MB.
- POST inválidos dirigidos volvieron a responder `ok=false` sin cambiar
  `selections.jsonl`, `classifications.jsonl`, `copilot_feedback.jsonl`,
  `connections.jsonl` ni `boards.json`.

## Next action — cerrar informe antes de cualquier promoción

No migrar los descartes históricos, no ajustar ranking y no gastar Watsonx/AWS.
El circuito de decisiones y la superficie GTM/mapa quedan listos para una
última comparación dirigida entre estados persistidos y escena sobre una
muestra pequeña; si no aparecen divergencias, recién entonces se puede decidir
si la migración histórica de descartes merece una ronda separada.

## Comparación persistencia ↔ escena — 2026-08-10

- Se cruzaron 11 escenas reales en MAK, elegidas desde las decisiones y
  clasificaciones existentes: seleccionar, deseleccionar, descartar, triage
  `work`, `record` y `review`. No se escribieron archivos ni se ejecutaron
  clicks.
- Resultado: 4 escenas activas conservaron `ok=true`, el elemento activo fue el
  primer registro, las relaciones solo apuntaron a registros presentes y los
  estados de selección coincidieron con JSONL. Dos descartes devolvieron
  explícitamente `ok=false`, `error=item_descartado`, sin escena falsa.
- Una muestra `triage=record` conservó esa clasificación en la pieza de escena.
  Una muestra `seleccionar` conservó `selection=seleccionar`; una muestra
  `deseleccionar` quedó fuera de la mesa sin borrar el historial. No apareció
  divergencia persistencia → escena.
- Tres feedbacks históricos fueron cruzados con la escena copilot: dos
  relaciones mostraron `status=accepted`, `decisions=[accept]`, nota y peso
  aprendido; el tercero no entró en el top-9 actual, pero sigue persistido y no
  se presentó como relación confirmada. Esto es ranking acotado, no pérdida de
  persistencia.
- La ruta operativa `surface=order` mantiene el canal visual: una muestra real
  devolvió 5 relaciones `visual_similarity` con MobileCLIP-S0, scores 0.783021
  y 0.731494, márgenes 0.051527 y 0.068693. El primer cálculo GTM frío midió
  11.896 s y los siguientes 0.022 s con caché; queda registrado como medición
  de rendimiento, no como fallo semántico.
- MAK sigue con `mak-hub.service=active`; HTML servido y editor coinciden en
  hash `252d14d006d342c8e7a514801d3f35e33840bffde668ed928e638c5aea8906a1`.
  No se cargaron mappings `torch|faiss|mobileclip` en el Hub.

## Next action — decisión separada sobre rendimiento y migración

La comparación de invariantes queda sin divergencias semánticas confirmadas.
Antes de migrar descartes históricos, el siguiente bloque debe decidir si se
acepta el calentamiento GTM de 11.9 s como coste de primera apertura o se añade
una mejora acotada de caché/preparación; no usar IBM/AWS, no ajustar ranking y
no migrar mientras esa decisión no esté documentada.

## Optimización GTM focalizada — 2026-08-10

- Se perfiló solo la construcción GTM estable sobre la ruta existente, sin
  navegador ni carga de MobileCLIP. El cuello confirmado era
  `_vector_distance`: millones de llamadas Python creaban una lista de pesos y
  recorrían un generador para vectores de 32 dimensiones.
- `cultura/mak_plataforma/copilot.py` ahora usa `math.dist` únicamente en la
  ruta no ponderada; la ruta ponderada conserva su cálculo explícito. No cambió
  el vector, el mapa, las etiquetas, el contrato ni el ranking.
- Medición MAK antes/después: construcción GTM fría de 11.896 s a 4.590 s; las
  llamadas siguientes permanecen en 0.022–0.023 s por la caché existente. La
  escena HTTP real `surface=order` respondió 200 en 6.125 s con `ok=true`, 10
  registros, 9 relaciones y 5 relaciones visuales MobileCLIP-S0, scores
  0.783021 y 0.731494.
- Regresiones focales locales después del cambio: 113 tests pasaron; también
  `py_compile`, `node --check`, compilación del script inline y `git diff
  --check` pasaron.
- Despliegue controlado tras comparar hashes: `copilot.py` runtime =
  `b24cad60210c2df852cb7bf63301e3b8c3efa4e6a43fec4b673e2d79076fe878`.
  `editor.html`, `mesa_montaje.js` y `hub.py` mantuvieron los hashes ya
  verificados. `mak-hub.service=active`, HTML servido coincidente, RSS 128960
  KB/HWM 132720 KB y mappings `torch|faiss|mobileclip=0`.

## Next action — conservar el circuito y no abrir otra migración aún

La mejora de rendimiento queda aplicada y medida. Mantener sin migración los
descartes históricos, sin promoción de aprendizaje y sin IBM/AWS. El siguiente
bloque técnico solo debe añadir una regresión de rendimiento o revisar el
calentamiento si la medición vuelve a degradarse; si permanece estable, el
trabajo pasa a documentar la decisión sobre la migración histórica en una ronda
separada, no a mezclarla con la superficie operativa.

## Corrección de descarte parcial con red incierta — 2026-08-10

- Se encontró otra violación de la cadena activa: el `Promise.all` del descarte
  por lote podía rechazar toda la tanda ante una respuesta HTTP o JSON ausente,
  sin reconciliar los elementos que sí habían sido guardados en MAK.
- `iskvw/mesa_montaje.js` ahora convierte cada solicitud en un resultado explícito
  `respuesta_no_confirmada`; los elementos confirmados se retiran de la escena,
  los no confirmados permanecen seleccionables y el HUD ya no conserva IDs de
  nodos que fueron retirados.
- La regresión contractual comprueba la reconciliación de `savedIds`, el filtro
  de `orderSelectedIds` y la degradación de respuesta incierta. Pasaron 113
  pruebas focales, `node --check` y la compilación inline del editor.
- Hash final servido para `mesa_montaje.js`: `edaf95e34259459862c8c610f6e9b4d9711736210e4a48318eaa3484b9158569`;
  `/portafolio/mesa_montaje.js?v=20260810-visual-index2` coincide. MAK sigue
  `mak-hub.service=active`; no fue necesario reiniciar el Hub porque solo cambió
  el recurso estático.

## Next action — terminar el hunting de transporte del editor activo

Mantener bloqueadas migración, ranking e IBM/AWS. Revisar únicamente si quedan
otras tandas `Promise.all` o respuestas no confirmadas en `mesa_montaje.js`; cada
una debe preservar parciales, hacer visible el pendiente y ser idempotente antes
de cerrar el circuito.

## Transporte de descarte por lote — cierre — 2026-08-10

- La revisión estática de `mesa_montaje.js` confirmó que el único `Promise.all`
  de decisiones es el descarte por lote y ahora cada promesa tiene fallback
  explícito `respuesta_no_confirmada`. No quedan tandas paralelas que oculten
  fallos de transporte en la superficie activa.
- El arreglo quedó desplegado y servido: hash de
  `mesa_montaje.js` = `edaf95e34259459862c8c610f6e9b4d9711736210e4a48318eaa3484b9158569`;
  `mak-hub.service=active`, sin restart porque fue un recurso estático, y el
  Hub conserva `model_map=0`.
- Regresiones focales: 113 tests, `node --check` y compilación inline del
  editor pasaron. La persistencia histórica no fue alterada.

## Next action — mantener cierre técnico acotado

El transporte del editor activo ya tiene manejo explícito de éxito, parcial,
duplicado y respuesta incierta. No abrir otra mejora visual ni migrar datos en
esta línea; cualquier siguiente ronda debe ser una regresión dirigida si vuelve
a observarse una divergencia real, o una decisión independiente sobre los
descartes históricos.

## Auditoría de discrepancias del handoff — 2026-08-10 (antes de reconciliar)

- La cabecera `Repository state` quedó obsoleta: la comprobación real muestra
  rama `mak` y HEAD `d09327fe8d5b`; `main`, `mak`, `rd` e `iskvw`, junto con sus
  refs `origin/*`, apuntan a ese commit. El worktree de Windows tiene cambios
  modificados y archivos no rastreados además del handoff.
- La sección `MAK box: verified truth` también conserva hechos antiguos: el
  checkout `/home/mak/flujo` está en `mak`, HEAD `d09327fe8d5b`, y tiene cambios
  en `editor.html`, `mesa_montaje.js` y `visual_index.py` no reflejados en el
  texto inicial.
- La afirmación de que `ledger.py` runtime coincide es falsa. SHA-256 del
  checkout/Windows: `7e7cb2ffdad7dc35750803f831edcf823631443cd36d972cb9da3ded934d11ae`;
  runtime `/home/mak/plataforma/ledger.py`:
  `bcbaca74fecec9e56be1084cefe7288953686161819f7f14a5ad87d3f1cadf7c`. El
  runtime no conserva la lectura de `product.next_action` presente en el
  checkout. No se sincronizó durante aquella auditoría; la reconciliación
  posterior queda documentada en la sección siguiente.
- La afirmación de que el handoff era `ASCII-only (198 lines)` es falsa:
  comprobación local: 3.078 líneas, 178.526 bytes y 1.552 bytes no ASCII.
- Estado actualmente confirmado: `systemctl --user is-active mak-hub.service`
  devuelve `active`, el proceso sirve en `0.0.0.0:8900`, `/health` y
  `/api/portfolio/copilot/status` responden 200, `/portafolio/` sirve el editor
  SHA-256 `252d14d006d342c8e7a514801d3f35e33840bffde668ed928e638c5aea8906a1`,
  el JS servido coincide con `edaf95e34259459862c8c610f6e9b4d9711736210e4a48318eaa3484b9158569`,
  y la escena `surface=order` responde 200.
- Acción resultante: reconciliar `ledger.py` runtime en una operación separada
  y controlada, y después corregir las secciones iniciales obsoletas. Ambas
  acciones están documentadas en las secciones posteriores.

## Reconciliación de ledger runtime — 2026-08-11

- Se validó sintaxis en Windows y MAK antes del despliegue. El archivo objetivo
  fue exactamente `/home/mak/plataforma/ledger.py`; no se creó backup ni se
  modificaron datos, ramas o commits.
- Se copió mediante temporal controlado y verificación SHA-256. El runtime
  ahora coincide con el checkout:
  `7e7cb2ffdad7dc35750803f831edcf823631443cd36d972cb9da3ded934d11ae`.
- Se reinició únicamente el servicio de usuario `mak-hub.service`. Quedó
  `active/running`, PID `77841`, con `VmRSS=100996 kB`, `VmHWM=131764 kB` y
  cero mappings `torch|faiss|mobileclip`.
- Verificación posterior: `/health`, `/portafolio/`,
  `/api/portfolio/copilot/status` y la escena `surface=order` respondieron
  HTTP 200. El módulo cargado por Python es
  `/home/mak/plataforma/ledger.py` y conserva `product_next_action`.
- Siguiente acción: corregir las secciones iniciales obsoletas de este handoff
  para que no contradigan el estado actual; no abrir una nueva integración ni
  IBM/AWS hasta terminar esa limpieza documental.

## Regresión de contrato portfolio_record — 2026-08-11

- Se añadió `tests/test_mak_ledger.py::test_portfolio_record_surfaces_product_next_action_when_not_triangulating`.
  La prueba cubre la ruta real `portfolio_record` cuando la acción es
  `verify_source`: conserva `product.next_action` en la fila del ledger y
  mantiene `record_kind` dentro de `portfolio_candidate`.
- Verificación local: pruebas focales de ledger, bridge, copilot, editor,
  índice visual y XIO pasaron; `ledger.py` compila y `node --check
  iskvw/mesa_montaje.js` pasa. No se modificó el runtime por esta prueba.
- Verificación MAK posterior: `mak-hub.service=active`, `/health` HTTP 200 y
  escena `surface=order` HTTP 200; el runtime `ledger.py` conserva el hash
  `7e7cb2ffdad7dc35750803f831edcf823631443cd36d972cb9da3ded934d11ae`.
- Siguiente acción: mantener este circuito como regresión y elegir solo otra
  violación reproducible de contrato antes de tocar ranking, migraciones,
  IBM/AWS o una nueva superficie visual.

## Reconciliación de clasificación parcial — 2026-08-11

- Hunting del circuito `mesa_montaje.js → /api/portfolio/classify-batch`:
  MAK podía persistir parte de una tanda y devolver `partial=true`, mientras
  el editor descartaba toda la respuesta y conservaba seleccionados también
  los elementos ya guardados.
- Corrección aplicada en `iskvw/mesa_montaje.js`: el editor lee
  `payload.results`, actualiza solo los `savedIds`, los retira de
  `orderSelectedIds`, invalida la caché de escena y deja los pendientes
  visibles con el mensaje de clasificación parcial.
- Regresión contractual añadida en
  `tests/test_iskvw_editor_contract.py`. Pasaron las pruebas focales de ledger,
  bridge, Copilot, editor, índice visual y XIO; también `node --check` y
  `git diff --check`.
- Despliegue controlado al checkout operativo
  `/home/mak/flujo/iskvw/mesa_montaje.js`: hash local, remoto y servido
  `ddf3968273935bbe8f9df1e78b67290997022a4c034857979bca4cd7eb9f50e8`.
  No se reinició el Hub por ser un recurso estático.
- Verificación MAK posterior: `mak-hub.service=active`, `/health` HTTP 200,
  escena `surface=order` HTTP 200 y el recurso servido contiene la ruta de
  reconciliación parcial.
- Siguiente acción: continuar con la siguiente acción del harness solo si
  aparece otra escritura parcial reproducible; no abrir proveedores externos,
  migraciones ni otra interfaz.

## Cierre publicado para el siguiente agente — 2026-08-11

- Commit publicado en `origin/mak`: `4bb71f2f37b7` (`integrate MAK portfolio
  visual circuit`). No se hicieron commits ni pushes a `main`, `rd` o
  `iskvw`; esas ramas permanecen limpias en `d09327fe8d5b`.
- Windows `mak` y el checkout `/home/mak/flujo` están limpios en
  `4bb71f2f37b7`. La versión anterior de `visual_index.py` que estaba sin
  rastrear en MAK fue clasificada como stale y archivada fuera del checkout en
  `/home/mak/plataforma/derived/visual-index/legacy/visual_index.py.pre-4bb71f2`,
  SHA-256 `2cbca673c1edaada07a1371fdc84f6a152ece623b89134b966886fc37298e184`.
- Verificación focal final: seis módulos Python compilan, el editor inline
  compila, `node --check iskvw/mesa_montaje.js` pasa y las pruebas de ledger,
  bridge, Copilot, editor, índice visual y XIO pasan.
- La suite histórica completa (`225` archivos) agotó `184 s` sin terminar; no
  se declara aprobada. No bloqueó el cierre focal del circuito MAK y queda como
  limitación explícita para una ronda separada.
- MAK posterior al push: `mak-hub.service=active`, `/portafolio/`, `/health`,
  `/api/portfolio/copilot/status` y la escena `surface=order` respondieron
  HTTP 200. No se reinició el Hub durante el cierre porque el cambio servido
  fue estático, y el runtime conserva cero mappings de torch/FAISS/MobileCLIP.
- Siguiente agente: comenzar en esta sección y ejecutar solo otra regresión
  reproducible del harness; no reabrir la interfaz legacy ni sincronizar las
  otras ramas sin una decisión explícita.

## Cierre de suite y privacidad — 2026-08-11

- La corrida completa definitiva se ejecutó con
  `python -m pytest -q --capture=no --durations=20`: terminó con código 0 en
  231,1 s. Los fallos iniciales no eran del circuito MAK: uno detectaba una
  ruta personal escrita en este handoff y otro detectaba que el SVG generado
  no conservaba un marcador verificable.
- Se eliminó del handoff la ruta personal. Se corrigió
  `tools/update_readme_svg.py` para conservar el marcador de capa generada
  también en vasos SVG antiguos sin `<desc>` y para dejar `MAK` en ese
  marcador. `arte-ascii-readme.svg` se regeneró mediante esa herramienta; no
  se editó geometría ni se tocó `README.md`.
- La verificación focal de privacidad y del generador pasó; `git diff --check`
  pasó. La suite completa solo dejó warnings/deprecaciones existentes de
  Pillow y salidas diagnósticas de pruebas.
- Publicación y verificación completadas: Windows `mak` y
  `/home/mak/flujo` están limpios y alineados con `origin/mak`; el checkout
  MAK está en la misma revisión publicada. `mak-hub.service` permanece
  `active`; `/health`, `/portafolio/` y
  `/api/portfolio/copilot/status` responden HTTP 200.
- Los hashes operativos siguen siendo editor
  `1c0efe456f80ac13c90cc0a76dc44cfddf90ff2cf101c8c263c5f19d6b967a5d`, JS
  `ddf3968273935bbe8f9df1e78b67290997022a4c034857979bca4cd7eb9f50e8` e
  índice `31e271c90345434ac6a6b4f6fc441ec17ab03808a75c33be5f5d2634b5bf52bc`.
  El proceso Hub sigue sin mappings `torch|faiss|mobileclip`.
- Las referencias remotas `main`, `rd` e `iskvw` siguen en
  `d09327fe8d5b`; solo `mak` contiene esta integración. No queda una acción
  técnica pendiente de esta ronda; el siguiente bloque debe comenzar con una
  nueva violación reproducible del harness.

## Corrección de protección de la obra SVG — 2026-08-11

- Se detectó que una regeneración anterior trató el SVG artístico como un
  artefacto intercambiable. La versión canónica debe conservar `viewBox`, 30
  frames, 9 s, orden de frames, máscaras, `readme-source-static` y delays.
- `arte-ascii-readme.svg` y `tools/update_readme_svg.py` se restauraron desde
  `d09327fe`. No se conservará ninguna variante experimental en las ramas
  canónicas.
- `tests/test_readme_svg.py` ahora protege la forma canónica: 150 máscaras,
  100 `tspan`, 30 frames/9 s y ausencia de `clipPath` experimental. El test
  ya no exige insertar un marcador modificando la obra.
- Siguiente acción: publicar esta restauración y la regla durable en las cuatro
  ramas; verificar métricas estructurales antes de cerrar.

## Auditoría CI Ubuntu del SVG canónico — 2026-08-11

- Se verificó `origin/main` en `53b5935f` y el run de CI
  `31456257637` (`test (ubuntu-latest)`, job `93670544159`).
- El SVG no es la causa del rojo: conserva 30 frames, 150 máscaras, 100
  `tspan`, 9 s y cero `clipPath`; `tests/test_readme_svg.py` pasa en el run
  actual y Windows también termina correctamente.
- El fallo real es preexistente en
  `tests/test_mak_portfolio_bridge.py:538`: el test exige
  `posts\\a.jpg`, pero Ubuntu entrega `/posts/a.jpg`. El commit de restauración
  no toca ese test ni el código de visión de portafolio.
- Comando medido: `python -m pytest -q tests/test_readme_svg.py` y el test
  focal de visión pasan en Windows; el log Ubuntu confirma que solo falla la
  aserción de separador de ruta dentro de `python -m flujo verify`.
- Siguiente acción: si se autoriza una corrección aparte, hacer la aserción
  independiente del sistema operativo con `pathlib.Path`; no modificar el
  SVG para intentar resolver este fallo.

## Corrección de ruta del test Ubuntu — 2026-08-11

- Se aplicó únicamente en `tests/test_mak_portfolio_bridge.py` la aserción
  portable `Path(...).parts[-2:] == ("posts", "a.jpg")`; la ruta lógica queda
  protegida en Windows y Ubuntu sin comparar separadores literales.
- Pasaron los checks focales: el test de visión y la suite combinada de
  `tests/test_readme_svg.py` más `tests/test_mak_portfolio_bridge.py`; también
  pasó `git diff --check`.
- `flujo verify` no terminó en Windows tras 364 s y fue detenido por timeout;
  el intento anterior con `python -m fluxo verify` no aplicaba porque el
  módulo no estaba instalado. Se instaló localmente `.[dev,render]` y el
  ejecutable `flujo` sí inició la suite.
- No se modificó `arte-ascii-readme.svg`, no se hizo commit ni push.
- Siguiente acción: ejecutar CI Ubuntu con este único cambio y publicar solo
  con autorización explícita.

## Publicación de la corrección portable — 2026-08-11

- La corrección se publicó en la rama `agent/fix-ubuntu-path` mediante el
  commit `cbcd6df25d140ccc6dffe5e7b41ade84547a85b3` y PR #520:
  `https://github.com/ligereza/vibecodeine/pull/520`.
- El run `31484420597` pasó completo: Ubuntu terminó en 2m52s y Windows en
  7m28s; los checks de seguridad también pasaron.
- El PR quedó mergeado a `main` con `d0c9a5947b8ab4e6e67dd4627c92cc324b87c5a1`.
  El cambio fusionado solo afecta la aserción portable del test; el SVG
  canónico no fue modificado.
- Comandos medidos: `gh pr view 520 ...` confirmó `MERGED` y
  `git ls-remote origin refs/heads/main` confirmó el hash de `main`.
- El checkout de trabajo `mak` conserva sus cambios locales no publicados;
  no se mezclaron ni se limpiaron.
- Siguiente acción: mantener protegido el SVG canónico y no reabrir
  experimentos de geometría, máscaras o timing dentro de `main` sin una nueva
  instrucción artística explícita.

## Plan de sincronización de ramas — 2026-08-11

- Estado verificado en remoto: `main`=`d0c9a594`, `mak`=`abe27c22`,
  `rd`=`c1c92574`, `iskvw`=`fde9afc8`. Respecto de `main`, `mak` tiene
  3 commits menos y 5 propios; `rd` e `iskvw` tienen 3 menos y 2 propios.
- Orden de trabajo: primero auditar `mak` sin limpiar sus cambios locales;
  luego auditar `rd`; finalmente `iskvw`. Cada rama se trabajará en un
  worktree temporal y mediante PR independiente.
- Regla de integración: no hacer merge completo de `main` a las ramas
  artísticas. Solo portar correcciones compartidas verificadas, preservando
  el SVG canónico con 30 frames/9 s, 150 máscaras, 100 `tspan` y sin
  `clipPath` experimental.
- Gates por rama: inventario de archivos divergentes, comparación estructural
  del SVG, suite focal de la rama, `git diff --check` y CI Ubuntu/Windows.
  Si una rama contiene una variante artística o histórica, se conserva y se
  documenta en vez de sobreescribirla.
- `mak` conserva cambios locales no publicados en `context/LAST_HANDOFF.md` y
  `tests/test_mak_portfolio_bridge.py`; no se deben resetear ni mezclar hasta
  revisar su intención.
- Siguiente acción concreta: producir el inventario de divergencias de `mak`
  y decidir qué corrección compartida se porta mediante PR.

## Sincronización completa de ramas — 2026-08-11

- La auditoría confirmó que `rd` e `iskvw` ya tenían las mismas protecciones
  del SVG canónico que `main`; el único desfase compartido era la aserción de
  ruta dependiente de Windows en `tests/test_mak_portfolio_bridge.py`.
- Se portó esa corrección en tres worktrees aislados. En `mak` también se
  añadió `mak` al disparador `pull_request.branches` de
  `.github/workflows/ci.yml`, porque esa rama no recibía la matriz CI.
- PRs fusionados: #521 a `iskvw` con `d887771c`, #522 a `rd` con
  `b79f1476`, y #523 a `mak` con `160b94d3`. `main` permanece en
  `d0c9a594`.
- CI final verde en las tres ramas: Ubuntu, Windows, dependencias, secretos
  y datos reales. La corrida de `rd` necesitó relanzarse porque el primer
  Windows runner quedó atascado en `flujo verify`; la relanzada terminó bien.
- Las tres ramas conservan 150 máscaras, 100 `tspan`, 30 frames, 9 s y cero
  `clipPath` experimental. No se modificó la geometría ni el timing del SVG.
- Comandos medidos: suites focales en los tres worktrees, `git diff --check`,
  métricas estructurales y `gh pr view`/`git ls-remote` tras cada merge.
- El worktree principal `mak` conserva sus cambios locales no publicados;
  no se limpiaron ni se mezclaron. Los worktrees temporales y ramas `codex/*`
  se conservan como evidencia de la integración.
- Siguiente acción: ninguna sincronización pendiente; cualquier cambio nuevo
  debe entrar por PR de la rama correspondiente y mantener la protección del
  SVG canónico.

## Inicio de revisión humana de la cola — 2026-08-11

- Verificación viva por `GET http://192.168.50.2:8900/api/portfolio/review-queue`:
  20 candidatos, 14 AWS y 6 Watsonx; 16 con `next_action=human_review`, 4
  con `next_action=triangulate`, 19 `human_decision=pending` y 1 ya en
  `revise`.
- Primer bloque acotado para revisión humana: `18099450649867322.jpg`,
  `17874296566294009.jpg`, `17913338554295932.jpg`,
  `17884747708722082.jpg` y `18141507463300316.jpg`.
- No se enviaron decisiones ni se escribió el ledger. La cola sigue fuera de
  promoción pública; las decisiones deben hacerse desde `/portafolio/` y una
  pieza a la vez.
- Siguiente acción: revisar visualmente este primer bloque y devolver la
  decisión explícita de cada pieza (`aceptar`, `rechazar` o `abstenerse`), con
  contexto solo cuando corresponda.

## Desglose de aprendizaje verificado — 2026-08-11

- `GET /api/portfolio/copilot/learning` confirma que las 91 decisiones del
  ajuste GTM son etiquetas de ordenamiento: `work`=27, `record`=13,
  `review`=1 y `discard`=50.
- No son 91 selecciones de piezas. El contador separado de selecciones es
  `selected`=4 y `excluded`=3.
- Otros contadores independientes: feedback de relaciones `12` (`date`=1,
  `publication`=4, `text`=7); revisiones de candidatos `8` (`accept`=4,
  `revise`=1, `reject`=3); feedback visual MobileCLIP `0`.
- La evaluación deja `automation_ready=false`, con accuracy `0.549451` y
  macro-recall `0.25`; no se debe ajustar ranking ni automatizar promoción
  con este resultado.
- Siguiente acción: tratar por separado selección, triage, feedback de
  relaciones y revisión de candidatos; no pedir selecciones adicionales como
  si fueran etiquetas de aprendizaje.

## Aclaración de estados de decisión — 2026-08-11

- Las 91 decisiones sí son decisiones humanas del usuario, pero el motor las
  lee como etiquetas históricas de ordenamiento (`classification.triage` o,
  cuando no existe, la selección que quedó registrada). No representan una
  bandeja activa de piezas.
- `selected=4` es el estado actual deduplicado de piezas con decisión
  `seleccionar`; `excluded=3` es el estado actual deduplicado de piezas
  excluidas. Deseleccionar una pieza no borra su etiqueta histórica del
  conjunto de aprendizaje.
- No hay contradicción entre 91 etiquetas humanas y 4 piezas actualmente en
  mesa. No se deben solicitar más selecciones solo para aumentar el contador
  de aprendizaje.

## Atlas de decisiones verificable — 2026-08-11

- Se implementó en un worktree aislado la superficie de solo lectura
  `GET /api/portfolio/audit` con schema `faro-portfolio-audit-v1`.
- El contrato separa explícitamente estado actual de selección, historial de
  selecciones, historial de clasificaciones, etiquetas triage, feedback de
  relaciones, feedback visual y revisiones externas. También declara sus
  fuentes, promoción `none` y `read_only=true`.
- La auditoría acepta `source_id` y devuelve la pieza, su estado vigente y una
  línea temporal ordenada con selección, clasificación, feedback y revisión
  externa. Las fuentes append-only no se reescriben ni se eliminan.
- `/portafolio/` añade el botón visible `auditoría`; muestra el resumen
  verificable y permite abrir la trazabilidad de la pieza activa sin crear
  decisiones ni relaciones.
- Regresión medida en el worktree `codex/atlas-audit`:
  `python -m pytest -q tests/test_mak_portfolio_bridge.py tests/test_copilot.py
  tests/test_iskvw_editor_contract.py tests/test_mak_ledger.py
  tests/test_mak_tandas.py` terminó `152 passed`; también pasaron
  `python -m py_compile cultura/mak_plataforma/hub.py cultura/mak_plataforma/copilot.py`,
  `node --check iskvw/mesa_montaje.js` y `git diff --check`.
- El diff no contiene `arte-ascii-readme.svg` ni `README.md`; la obra SVG
  permanece protegida. No se hizo commit, push, despliegue ni mutación de
  ledger durante esta implementación.
- Siguiente acción: revisar este contrato en el worktree operativo y, con
  autorización explícita, portarlo por PR a `mak`; luego verificar el endpoint
  vivo y la UI servida antes de integrar otra rama.

## Bug hunting posterior al Atlas — 2026-08-11

- La verificación viva del circuito `mesa_montaje.js -> Hub -> /portafolio/`
  encontró una integración incompleta: `GET /api/portfolio/audit` en el
  runtime MAK respondió HTTP 200 con `text/html` y la portada antigua, no JSON.
  El frontend habría intentado parsear ese HTML y fallado con un error opaco.
- El runtime confirmado sigue en `/home/mak/plataforma/.venv/bin/python
  /home/mak/plataforma/hub.py`, servicio `mak-hub.service=active`; el checkout
  `/home/mak/flujo` está en `abe27c22`, mientras `origin/mak` está en
  `160b94d3`. La UI servida no contiene `mesa-audit` y su hash JS sigue siendo
  `ddf3968273935bbe8f9df1e78b67290997022a4c034857979bca4cd7eb9f50e8`.
- Corrección local en `codex/atlas-audit`: la ruta nueva devuelve JSON, las
  rutas GET `/api/*` desconocidas devuelven 404 JSON en vez de HTML 200, y el
  frontend comprueba `Content-Type` antes de leer la auditoría. La consulta de
  una pieza inexistente sale antes de construir el mapa GTM completo; una pieza
  sin etiqueta ya no se atribuye falsamente al origen `selection`.
- Se agregó una regresión HTTP con servidor efímero: `/api/portfolio/audit`
  debe responder JSON y `/api/does-not-exist` debe responder 404 JSON. El
  circuito frontend no tiene otra llamada API sin handler literal en el Hub.
- Verificación medida en `codex/atlas-audit`: los contratos de portfolio,
  Copilot, ledger, tandas, documentación y SVG pasan (`1` skip existente),
  Python compila, `node --check` pasa y `git diff --check` pasa. El SVG no
  aparece en el diff; sus métricas siguen 30 frames, 150 máscaras, 100
  `tspan`, 9 s, `readme-source-static` presente y cero `clipPath`.
- No se llamó Watsonx/AWS ni se mutó el ledger: el fallo era de transporte y
  despliegue, no de evidencia externa. Siguiente acción: portar esta corrección
  al checkout operativo mediante el flujo de integración autorizado, reiniciar
  solo `mak-hub.service` si cambia Python y verificar JSON, hash servido y
  regresión 404 antes de abrir otra tanda de proveedores.

## Bug hunting continuado — rendimiento y aislamiento de proveedores — 2026-08-11

- La medición viva repitió la divergencia: `/api/portfolio/audit` sigue
  devolviendo HTTP 200 `text/html` con la portada antigua; en cambio
  `/api/portfolio/copilot/status` devuelve JSON y marca AWS/Watsonx
  configurados, y `/api/portfolio/external-candidates` devuelve 27 filas en
  aproximadamente 1,64 s. El runtime aún no contiene la ruta Atlas ni la UI
  `mesa-audit`; por eso no se debe confundir ese 200 con una integración
  funcional.
- Se reprodujo en código la causa de latencia: `_portfolio_external_candidates`
  llamaba `_portfolio_item()` dentro del recorrido del ledger, releyendo el
  inbox de 7.044 piezas y sus sidecars una vez por candidato. La corrección
  local construye un índice `source_id -> item` una sola vez y conserva el
  filtro de huérfanos, la deduplicación y la separación de candidatos externos.
  Una regresión cuenta la lectura del inbox y exige una sola para varias filas.
- `_portfolio_scene` dejó de hacer la primera búsqueda separada mediante
  `_portfolio_item()` y usa el inbox ya cargado para resolver la pieza activa.
  Esto elimina una lectura completa redundante antes de construir el mapa o la
  escena.
- Se encontró y corrigió un defecto independiente en `providers.py`:
  `provider_registry({})` heredaba el entorno real porque un diccionario vacío
  era tratado como falso. Ahora un entorno explícito vacío significa ningún
  proveedor configurado; queda cubierto por una regresión. No se expusieron
  credenciales ni se hicieron llamadas externas nuevas.
- Verificación local en el worktree de auditoría: suite protegida de SVG,
  Hub/bridge, Copilot, editor, ledger, tandas, higiene y mapa termina al 100%
  con el skip existente; `ruff check` en archivos tocados, `py_compile`,
  `node --check` y `git diff --check` pasan. El diff contiene solo Hub,
  providers, la mesa y pruebas; no contiene `README.md` ni
  `arte-ascii-readme.svg`.
- Intento de comprobar el checkout MAK por SSH durante esta pasada terminó
  por timeout de conexión; la evidencia HTTP sigue mostrando el servicio
  activo pero desfasado. No se reinició el servicio, no se escribió el ledger,
  no se gastaron créditos AWS/Watsonx y no se hizo commit/push.

## Next action

Portar el worktree de auditoría por el flujo de integración de `mak` y
reiniciar solo `mak-hub.service` si se integra `hub.py`. Verificar después
`/api/portfolio/audit` como JSON, el 404 JSON para una ruta API inexistente,
los hashes servidos de `editor.html`/`mesa_montaje.js` y la latencia de
`external-candidates`. Solo si esa ruta queda estable, abrir una tanda externa
nueva; la cola actual continúa bajo compuerta humana y sin promoción automática.

## Integración viva del Atlas y segunda regresión de rendimiento — 2026-08-11

- Se verificó acceso SSH real como `mak@192.168.50.2`; el checkout estaba en
  `mak`, `abe27c2`, limpio antes de la copia. Se respaldaron los archivos
  funcionales bajo `rollback/atlas-audit-20260811` y
  `rollback/atlas-audit-before-ordering-20260811`; no se eliminó ningún
  histórico.
- Se portaron `hub.py` y `providers.py` al runtime `/home/mak/plataforma/` y
  a su espejo `/home/mak/flujo/cultura/mak_plataforma/`, además de
  `editor.html` y `mesa_montaje.js` al editor operativo. El cache-buster pasó a
  `mesa_montaje.js?v=20260811-atlas-audit`. Los hashes del runtime y del
  worktree coinciden: Hub `73e6c7a6f9eb281c147a8a0e32256c1a4329b3dfc4a6090407a786f334352973`,
  providers `7b550aacae993076def5b4b5abe4f2bfee09c5dc539752968a1be4990f36a03b`,
  editor `22bf7e9ea8913916e6ae2bd2b179aec3dce54b2ae1f1d4839c652f4f0d9a8acd`
  y JS `445cea5709711dd8420c8060b993c7923aaaefa4e0871e761292c8b43c5ea340`.
- `mak-hub.service` fue reiniciado solo después de `py_compile` remoto y quedó
  `active` con PID nuevo. HTTP verificó: `/api/portfolio/audit` 200 JSON con
  schema `faro-portfolio-audit-v1`, `/api/does-not-exist` 404 JSON con
  `ruta_api_no_encontrada`, `/portafolio/` contiene `mesa-audit` y el nuevo
  cache-buster, y `/api/portfolio/external-candidates` 200 JSON.
- La primera medición de auditoría tras reinicio fue `4431 ms` porque el
  endpoint construía el mapa GTM completo. Se sustituyó esa dependencia por
  `_portfolio_ordering_audit`, que calcula únicamente vectores estables,
  conteos y evaluación leave-one-out. Tras el segundo despliegue: auditoría
  fría `365 ms`; siguientes lecturas `297, 307, 299 ms`; evaluación `91`.
- La regresión de rendimiento de candidatos quedó resuelta en vivo:
  `external-candidates` mide `49, 68, 50 ms` después de indexar el inbox una
  sola vez, frente a aproximadamente `1.64 s` antes. Escenas `surface=order`
  calientes miden `162, 166 ms`; escena sin surface `552, 569, 548 ms`;
  sugerencias `385, 413, 387 ms`.
- La auditoría sigue siendo de solo lectura: antes y después de un GET,
  `/home/mak/plataforma/common_ledger.jsonl` conservó exactamente inode,
  tamaño y mtime (`1867614`, `541958`, `1786445117`). No se llamaron AWS ni
  Watsonx y no se promovió ninguna hipótesis.
- Verificación local posterior: suite protegida termina al 100% con el skip
  existente; `ruff`, `py_compile`, `node --check` y `git diff --check` pasan.
  La única latencia restante medida es el primer mapa GTM tras reinicio
  (`2530 ms`); después queda caliente. Es un problema independiente de la
  auditoría y de la cola externa, y queda como siguiente circuito de
  rendimiento a decidir tras conservar esta evidencia.

## Next action

Revisar el primer mapa GTM frío (`/api/portfolio/copilot/map` y la primera
escena `surface=order`) para decidir si conviene precalentar o reducir el fit
sin alterar la geometría ni el contrato GTM. Mantener el runtime y el espejo
con sus cambios locales respaldados; no hacer commit, push ni abrir otra tanda
de proveedores hasta terminar esa medición.

## Laboratorio SQLite FTS5 en disco — 2026-08-11

- Se repitió en MAK, fuera del runtime y con base temporal en `/tmp`, la
  integración pendiente que el handoff había dejado abierta. Se cargaron los
  7.044 items reales del inbox en una tabla FTS5 derivada y se eliminó la base
  temporal al terminar.
- Medición: rebuild `49,454 ms`, veinte consultas `0,820 ms` total (`0,041 ms`
  promedio), base temporal `1.482.752` bytes y RSS máximo `52.736 KB`.
  La consulta de control devolvió conteos reproducibles, incluido `blender=41`
  y `story=5.919`; no se confundió búsqueda textual con identidad curatorial.
- El mapa GTM actual sigue respondiendo `4.360.202` bytes; FTS5 no resuelve
  ese payload ni debe reemplazar el contrato GTM. Por eso SQLite queda como
  candidato de proyección de búsqueda, no se conecta como segundo almacén ni
  se añade una interfaz paralela.
- No se escribieron datos persistentes, no se movieron medios y no se llamó a
  proveedores externos. La integración FTS5 queda evaluada con evidencia y no
  promovida; el circuito activo continúa siendo inbox + Hub + mesa GTM.

## Proyección compacta para la mesa móvil — 2026-08-11

- Se reprodujo que el editor activo descargaba el inbox completo de
  `3.681.556` bytes aunque `mesa_montaje.js` solo necesita identidad, fecha,
  publicación, media, selección y clasificación. Se añadió la proyección
  existente del mismo endpoint, no un almacén nuevo:
  `/api/portfolio/inbox?surface=mesa`.
- La proyección conserva los ocho campos operativos y declara
  `surface=mesa_compact`; omite descripción, visión y referencias de export que
  no son leídas por la mesa. La respuesta real bajó a `1.922.874` bytes
  (`47,8%` menos) y sigue entregando los `7.044` ids. El inbox completo queda
  intacto para las superficies que sí necesitan la evidencia rica.
- `mesa_montaje.js?v=20260811-atlas-audit` ya solicita la proyección compacta.
  La UI servida y el endpoint fueron comprobados por HTTP; no se abrió
  navegador ni se usaron screenshots.
- Regresión añadida: la proyección compacta solo contiene
  `id,tipo_contenido,fecha,publicacion_id,asset_path,asset_available,selection,classification`.
  Suite protegida, sintaxis, Ruff y `git diff --check` siguen pasando.
- Medición posterior al despliegue: inbox compacto `101 ms`, auditoría
  `278 ms`, escena GTM fría `4.535 ms` por el fit inicial y escenas calientes
  `200, 182, 158 ms`. El tamaño del inbox ya no es el cuello principal; el fit
  GTM frío continúa separado y documentado.

## Next action

Medir una precarga controlada del fit GTM frente al costo de mantener el Hub
disponible durante el reinicio. Si la precarga no mejora el circuito completo,
conservar el comportamiento actual y no reducir la muestra de vecinos sin una
comparación de calidad; la compresión de la mesa ya quedó integrada y
verificada.

## Precarga GTM auditada y rechazada — 2026-08-11

- La precarga síncrona se probó en MAK con el Hub real. El Hub quedó marcado
  `active` antes de abrir `:8900`: el comando de reinicio tardó `601 ms`, pero
  las primeras solicitudes no pudieron conectar mientras el ajuste ocurría.
  El log del servicio muestra que el socket apareció aproximadamente cinco
  segundos después del arranque. Una escena posterior ya caliente respondió
  `205 ms`.
- Se probó una variante en hilo daemon para abrir el socket antes del ajuste.
  La solicitud de escena inmediata compitió con la precarga y tardó `9205 ms`;
  después de cinco segundos las escenas respondieron `185 ms` y `166 ms`.
  La carrera duplicaba el trabajo frío y no es aceptable para la primera
  interacción. La variante quedó rechazada, no se dejó activa.
- Se restauró el Hub seguro anterior desde el respaldo fechado
  `rollback/gtm-prewarm-20260811`; runtime y espejo quedaron en el hash
  `91e750c147247ed4d332c6091711f1e35da85c90e542e5a040b19a863005f5e3`.
  Tras restaurar: escena fría `4495 ms`, caliente `187 ms`, auditoría
  `297 ms`, servicio `active`, y el 404 JSON siguió correcto. Los respaldos
  `gtm-background-warm-20260811` y `gtm-lock-20260811` conservan las variantes
  experimentales; no se borró evidencia.
- Conclusión: no precalentar en `main()` ni en un hilo sin coordinación. El fit
  frío queda como costo conocido; cualquier mejora futura debe compartir una
  caché de forma coordinada o reducir el cálculo con comparación de calidad.

## Proyección compacta sin lectura visual innecesaria — 2026-08-11

- Se reprodujo que `_portfolio_inbox(compact=True)` cargaba las features
  visuales completas para descartarlas al construir la proyección de la mesa.
  La corrección deja la superficie completa intacta, pero omite
  `_portfolio_vision()` en la superficie `mesa`; una regresión hace fallar el
  test si esa lectura vuelve a ocurrir.
- El Hub desplegado quedó en el hash
  `819365d6c4469c10b0cf4a451d039c66e2752d11247cedca4f19cf2ac6854dd2` durante
  esta corrección. La respuesta compacta conservó `7.044` piezas y
  `1.922.874` bytes; las lecturas controladas fueron `131, 91, 77 ms` antes y
  `105, 78, 80 ms` después. El inbox completo siguió en `3.681.556` bytes.
- No se escribió el ledger: antes y después de la comprobación controlada
  conservó `1867614:541958:1786445117`. El runtime fue respaldado bajo
  `rollback/mesa-compact-vision-20260811`.

## Soporte HEAD y regresión de transporte — 2026-08-11

- La limitación documentada de `HEAD` quedó corregida en el Hub: reutiliza la
  resolución de `GET`, conserva `Content-Type` y `Content-Length`, pero no
  envía cuerpo. La prueba cubre una auditoría `200` y una ruta API inexistente
  `404` sin bytes de respuesta.
- Verificación viva: `HEAD /api/portfolio/audit` devolvió
  `200|application/json|Content-Length=3218|body=0`; `HEAD
  /api/does-not-exist` devolvió `404|application/json|Content-Length=79|body=0`;
  el GET de auditoría siguió devolviendo JSON `200`. Hash runtime/espejo:
  `bcc1d58dcd027c90c6192a3b05b58e4314ff1d45575a82e5c40c3031765ed1b8`.
- El respaldo previo quedó bajo `rollback/transport-head-20260811` y el
  servicio permaneció `active`. No se modificó README/SVG ni se hizo commit,
  push o merge.

## Serialización del fit GTM entre workers — 2026-08-11

- Se reprodujo que dos workers del `ThreadingHTTPServer` podían ejecutar el
  mismo fit frío al mismo tiempo y competir por la caché global. Se añadió el
  cerrojo local `_PORTFOLIO_GTM_LOCK` alrededor de los fits solicitados por el
  Hub; las lecturas y el render siguen fuera del cerrojo.
- La regresión local ejecuta dos fits simultáneos y exige `max_active=1`.
  En MAK, después del despliegue hash
  `0b580c0433ca404a49a256e82ad47d6a2f415d87fe51febfae63befaaf8142f3`, dos
  escenas reales concurrentes respondieron `4750` y `4762 ms`, ambas `200` y
  con `31098` bytes; la siguiente lectura caliente respondió `182 ms`. La
  duplicación de `~9 s` de la variante sin cerrojo desapareció.
- La suite protegida completa pasó al `100%` con el skip existente; también
  pasaron `py_compile`, `node --check`, Ruff y `git diff --check`. El respaldo
  anterior quedó bajo `rollback/gtm-lock-20260811`.
- Durante la medición reapareció una mutación externa del ledger: se añadieron
  filas `vigia:*` del dominio `opportunities` a las `09:45:15`, hasta
  `387` filas y `544266` bytes. No fue causada por los GET: una comprobación
  controlada de auditoría conservó exactamente
  `1867614:544266:1786455915` antes/después. No se revirtió ni se borró esa
  evidencia; queda clasificada como escritura externa del proceso `vigia`.

## Next action

Auditar el circuito de revisión externa ya servido: comparar en código y en
lecturas vivas `review-queue` contra `external-candidates`, comprobar que sus
identificadores y estados no se mezclan, y verificar la idempotencia sobre un
ledger temporal. No emitir decisiones humanas ni abrir otra tanda AWS/Watsonx;
la cola sigue bajo compuerta humana y el SVG canónico permanece protegido.

## Auditoría de cola externa y estados — 2026-08-11

- La comparación viva encontró `review-queue=20` y
  `external-candidates=27`: los 20 candidatos pendientes tienen fuente
  compartida, no hay fuentes pendientes fuera de la cola, y los 7 restantes
  están en estados ya aceptados o rechazados. Ambos contratos tienen fuentes
  únicas; no hay duplicados de `source_id`.
- Para las 20 fuentes compartidas coincidieron `ledger_id`, proveedor,
  decisión, siguiente acción, decisión humana, estado de revisión y
  `public_promotion`. La consulta filtrada por `source_id` devolvió una sola
  fila correcta; una fuente inexistente devolvió `total=0` sin error. La
  repetición de la decisión no se probó contra el ledger vivo: los tres tests
  focales de idempotencia y desambiguación de IDs duplicados pasan sobre
  fixtures temporales.
- No se emitió POST, no se tomó una decisión humana y no se modificó el JSONL
  aislado. El estado sigue bajo `human_review_required`; no se promovió nada.

## Verificación XIO sin enlace automático — 2026-08-11

- El adaptador y la escena viva entregan el mismo contrato
  `faro-xio-evidence-v1`: `available=true`, `work_valid=true`, 21 cues y 21
  segmentos, evento declarado `DREF CHOCOLATE`, fecha declarada
  `2026-07-24`, y `artist`, `venue`, `producer` explícitamente `unknown`.
- La escena `17991310565372795.mp4` contiene el mismo bloque XIO y mantiene
  `visual_similarity` disponible. `linked_to_source_id=false` y
  `next_action=link manually to portfolio source` se conservan; no se inventó
  una relación artística ni se escribió el ledger.
- La integración técnica está viva; el enlace XIO→pieza sigue siendo una
  decisión semántica humana pendiente. No se añadirá un almacén paralelo ni
  se usará `connect` automáticamente para resolverla.

## Next action

Inspeccionar el contrato existente de enlace humano (`connect`/
`triangulation/context-link`) para decidir si puede representar un vínculo
XIO→pieza sin perder la separación de evidencia, o si debe permanecer como
acción manual documentada. Hacer primero una fixture temporal y una prueba de
no promoción; no emitir decisiones reales ni abrir otra tanda externa.

## Frontera de enlace XIO protegida — 2026-08-11

- La inspección confirmó que `connect` solo acepta dos IDs presentes en el
  inbox, mientras `triangulation/context-link` exige una resolución humana
  aceptada y un grupo de triangulación existente. `xio:show:show_kit` no es una
  pieza del inbox ni un contexto humano aceptado; usar cualquiera de esos
  endpoints para enlazarlo sería una falsa relación.
- Se añadió una regresión negativa en fixture: intentar enlazar el work_id XIO
  no crea `connections.jsonl` ni `human_resolutions.jsonl` y devuelve los
  errores explícitos `items_invalidos` / `contexto_humano_no_encontrado`.
  Pasaron los tests XIO y de revisión externa focalizados (`6 passed`).
- No se creó un almacén paralelo ni se desplegó un endpoint inventado. El
  enlace XIO→pieza queda correctamente como acción semántica humana pendiente;
  para implementarlo hace falta definir primero un contrato de evidencia-link
  explícito, no reutilizar por fuerza una relación entre obras.

## Next action

Mantener esta frontera sin auto-enlace y pasar a la regresión final del
worktree aislado: suite protegida completa, hashes del runtime/espejo y
verificación de que el SVG/README no entró en ningún diff. Si más adelante se
define el significado del vínculo XIO→pieza, extender el contrato existente
por PR y con compuerta humana; no hacerlo implícitamente.

## Bug de orden del fallback API corregido — 2026-08-11

- La suite ampliada reprodujo que el fallback `ruta_api_no_encontrada` estaba
  antes de las rutas legacy. `/api/archivo` caía en 404 JSON y no entregaba el
  contrato público `version=1`; el test `test_hub_sirve_el_contrato` lo detectó.
- Se movió el fallback al final del bloque de rutas GET API, después de
  `/api/archivo`, `/api/organismo`, `/api/decisiones`, `/api/oportunidades`,
  `/api/eventos`, `/api/actividad`, `/api/render`, `/api/salud` y `/api/cuotas`.
  El 404 JSON para rutas realmente desconocidas se conserva.
- La corrección se desplegó con respaldo
  `rollback/legacy-api-order-20260811`; runtime y espejo comparten el hash
  `59825700e146a56d27acc278ec7dfd3a8001147f436cfc9ddcd290f305a12d51`.
  MAK confirmó `active`: `/api/archivo` volvió a `200`, `version=1`,
  `589` piezas y `1348` vínculos; la auditoría siguió en JSON, el 404 quedó
  `404|application/json|79 bytes` y HEAD siguió sin cuerpo.
- La lectura controlada de estas rutas conservó el ledger exactamente en
  `1867614:544266:1786455915`. No se modificó README/SVG ni se hizo
  commit/push/merge.

## Next action

Repetir la suite protegida completa después de este arreglo de orden, comparar
hashes finales entre worktree aislado, runtime y espejo, y cerrar la auditoría
solo si el diff sigue excluyendo `README.md` y `arte-ascii-readme.svg`. El
enlace XIO continúa siendo semántico/humano y no debe auto-promoverse.

## Regresión final y matriz de rutas — 2026-08-11

- La suite protegida ampliada terminó `100%` verde con el único skip existente,
  incluyendo SVG, bridge/Hub, Copilot, editor, ledger, tandas, higiene, mapa,
  XIO, índice visual, contrato de archivo y la regresión que detectó el orden
  del fallback. También pasaron `py_compile`, `node --check`, Ruff y
  `git diff --check`.
- El worktree aislado solo contiene cambios en Hub/providers, editor/mesa y
  pruebas; `git diff --name-only -- README.md arte-ascii-readme.svg` no devolvió
  nada. El checkout primario conserva únicamente sus cambios intencionales en
  `context/LAST_HANDOFF.md` y `tests/test_mak_portfolio_bridge.py`.
- La matriz viva de rutas legacy respondió JSON `200` en organismo, micelio,
  archivo, decisiones, oportunidades, eventos, actividad, ideas, render,
  salud y cuotas. La ruta inexistente respondió `404` JSON de 79 bytes. El
  servicio siguió `active`, el Hub runtime/espejo siguió en
  `59825700e146a56d27acc278ec7dfd3a8001147f436cfc9ddcd290f305a12d51`, y el
  ledger permaneció en `1867614:544266:1786455915` durante la matriz.

## Next action

No abrir otra tanda externa ni tocar el SVG. El siguiente trabajo debe entrar
por PR desde el worktree aislado, después de definir con el usuario el
significado del vínculo XIO→pieza; hasta entonces la frontera humana y los
respaldos de runtime quedan preservados. La auditoría técnica de este bloque
queda documentada, pero el objetivo general permanece abierto para nuevas
regresiones reproducibles.

## Carrera de persistencia en conexiones corregida — 2026-08-11

- Se reprodujo una carrera real en `_portfolio_connect`: dos workers podían
  leer `connections.jsonl` vacío antes de que cualquiera escribiera, dejando
  dos líneas idénticas para un doble clic humano simultáneo. La prueba aislada
  produjo `2` resultados y `2` filas antes de la corrección.
- Se añadió `_PORTFOLIO_CONNECTION_LOCK` solo alrededor del chequeo/escritura
  de esa relación. La validación de IDs y el render quedan fuera del cerrojo;
  el segundo worker devuelve `duplicate=true` y no vuelve a escribir.
- Regresión local y proceso aislado en MAK: `max_active=1`, `rows=1`,
  `duplicates=1`, `results=2`. No se envió POST al Hub real ni se tocó el
  ledger; el archivo temporal fue descartado al terminar.
- Despliegue respaldado en `rollback/connection-race-20260811`; runtime y
  espejo comparten hash
  `dd5804d2e47f302c49786ae2a0826ebed34ba4d2e69bdda4f6914ee9d4c5dd40`, el
  servicio está `active`, y las lecturas de auditoría, archivo y 404 siguen
  correctas. El ledger conserva `1867614:544266:1786455915`.

## Next action

Repetir la suite protegida completa incluyendo esta regresión de persistencia,
actualizar la matriz de riesgos de escrituras concurrentes y mantener el
contrato XIO como frontera humana. No usar proveedores externos ni publicar
los cambios sin autorización explícita.

## Carreras de persistencia del editor humano corregidas — 2026-08-11

- La revisión de los escritores append-only del Hub encontró cuatro ventanas
  de lectura-comprobación-escritura: selección, clasificación, conexiones y
  feedback. Las dos primeras ya tenían regresiones locales; se mantuvieron
  sus candados y se comprobó que dos workers dejan `rows=1`,
  `duplicates=1`, `results=2` y `max_active=1`.
- El segundo bloque reprodujo y corrigió tres ventanas adicionales: dos
  reintentos de `triangulation/context-link` podían duplicar la relación;
  dos lecturas visuales del mismo item podían llamar AWS y persistir dos
  veces; y dos decisiones iguales de revisión externa podían pasar la
  comprobación previa antes de escribir el ledger. Se añadieron el cerrojo
  de triangulación, cerrojos por `item_id` para visión, el cerrojo de revisión
  externa y `_portfolio_ledger_append_unique` para serializar los append del
  Hub.
- Las pruebas locales nuevas cubren `context-link`, visión concurrente y
  revisión externa; el bridge completo pasó `100%`. La prueba temporal en
  MAK confirmó: context-link `max_active=1`, `rows=1`,
  `already_linked=1`, `results=2`; visión `calls=1`, `max_active=1`,
  `rows=1`, `duplicates=1`; selección/clasificación mantuvieron la misma
  idempotencia. No hubo POST real, llamada AWS real ni escritura en JSONL
  productivo durante estas pruebas.
- Despliegue respaldado bajo `rollback/evidence-race-20260811`; runtime y
  espejo comparten hash `031299e10544934c2a1d45906768e04fa920180e08357912ea4a7a468cbb422c`.
  El proceso real escucha en `0.0.0.0:8900` bajo el supervisor del host; no
  existe una unidad `mak-hub.service`, por lo que no se debe reportar como
  systemd activo.
- Verificación viva posterior: auditoría `200` y
  `faro-portfolio-audit-v1` en `3218` bytes; inbox compacto `200` en
  `1922874` bytes; XIO `200`, `available=true`, `work_valid=true`; ruta
  desconocida `404` JSON; `HEAD` de auditoría `200`, `Content-Length=3218`,
  cuerpo `0`. El ledger permaneció exactamente en
  `1867614:544266:1786455915116045067`. No se tocó README/SVG ni se hizo
  commit, push o merge.

## Next action

Continuar con una auditoría de los escritores restantes fuera de este circuito
(ideas/render, colas de jobs y logs legacy), buscando la misma clase de carrera
sin convertir lecturas en mutaciones. Verificar cada candidato con fixture
temporal y, si corresponde, desplegarlo con backup; no usar proveedores
externos salvo que una integración concreta lo requiera y mantener XIO bajo
compuerta humana.

## Cola de ideas y material protegida — 2026-08-11

- La inspección encontró que `ideas.anotar`, `encargar` y `priorizar` hacían
  read-modify-write sin coordinarse con el worker `trabajo.py`, que consume
  `material.jsonl` en otro proceso. Se añadió `_IDEAS_LOCK` y se movieron las
  mutaciones de cola a `material.encolar_al_frente` y
  `material.reordenar_por_patron`.
- `material.py` ahora serializa `pop_pendiente`, encolado, reordenamiento,
  reconstrucción y degradación con lock de hilo y lock de archivo `fcntl` en
  MAK; las escrituras siguen siendo temporales + `os.replace`. Fixtures
  concurrentes confirmaron un solo despacho (`claimed=1`, `empty=1`) y un
  solo encolado (`true=1`, `false=1`, `rows=1`).
- Despliegue respaldado bajo `rollback/queue-race-20260811`. Hashes runtime y
  espejo: `ideas.py`
  `fa6e6c0b9418bc44d4e191e9c8e49b6521a0b4bac328bdab7be9f018a3481f89`;
  `material.py`
  `978a13418c00467588a48cb1583633dab02d2a529e7ff7b1d25f29dc7f00b361`.
  El proceso del Hub siguió escuchando en `:8900` tras reinicio.

## Revisiones humanas protegidas — 2026-08-11

- `revision.py` y `revision_episodios.py` tenían la misma ventana de doble
  clic: `_review_map()` podía devolver vacío a dos workers antes del append.
  Se añadieron locks de módulo y regresiones temporales; ambos circuitos
  confirmaron `max_active=1`, `rows=1`, `duplicates=1`, `results=2`.
- Despliegue respaldado bajo `rollback/review-race-20260811`. Hashes runtime y
  espejo: `revision.py`
  `48cecebf2d9d958e8d07ba16f5a1e791d3feeeebe488b01de67de8a253801503`;
  `revision_episodios.py`
  `58ea66a5e0fb51f6c199b8e44b3f0dbab0adbd6757f0a786661d1a404e09a2f0`.
- Matriz viva de solo lectura: `/api/revision` `200`, schema
  `mak-reel-review-v1`, 40 filas; `/api/revision/episodios` `200`, schema
  `mak-episode-review-v1`, 12 filas; `/api/ideas` `200`; auditoría y XIO
  siguen `200`; ruta desconocida sigue `404` JSON. El ledger quedó exactamente
  en `1867614:544266:1786455915116045067` antes/después.
- Suite final del circuito: `100%` verde con el skip existente; pasaron
  `py_compile`, `node --check`, Ruff y `git diff --check`. No se modificó
  README/SVG, no hubo POST real, ni llamada AWS/Watsonx, ni commit/push/merge.

## Next action

Seguir con un circuito acotado de `capataz`/`mutaciones` y `revision` de
trabajo: verificar si sus logs append-only tienen la misma ventana y si el
contrato de atribución de mutaciones está realmente conectado a sus escritores.
Usar fixtures y lectura de estado antes/después; no convertir el escaneo en
una migración masiva ni tocar el SVG canónico.

## Capataz, vigia y puente de issues — 2026-08-11

- `capataz._research_guard` tenía una carrera de cooldown: dos cron podían
  leer `research_intents.jsonl` antes de anexar y despachar el mismo tema. Se
  añadió lock de hilo + lock de archivo para el read-check-write; la misma
  protección cubre el fallback `backlog_codex.txt` y `bitacora_capataz.jsonl`.
  Fixture local y MAK: `max_active=1`, `rows=1`, `allowed=1`, `blocked=1`.
- `vigia.correr` podía repetir una novedad cuando dos callers compartían
  `vistos.jsonl`; la guardia shell evitaba el cron doble, pero no protegía al
  módulo frente a otros callers. Se añadió lock por directorio de estado,
  también aplicado a compactación. Fixture local y MAK: `fcntl=true`,
  `max_active=1`, `new_items=1`, `rows=1`. El cron real continúa en
  `/home/mak/vigia/vigia_guardia.sh`.
- `puente_issues._sin_rutas` llamaba a `_RUTA_ABS` inexistente: se reprodujo
  como `NameError` al importar/usar esa sanitización. Se definió la regex para
  rutas Windows/Linux sin tocar URLs y se corrigió además el import de `fcntl`
  para que el módulo pueda cargarse en Windows; la prueba local y la
  importación de `/home/mak/plataforma/puente_issues.py` pasan.
- Backups y despliegues: `rollback/capataz-race-20260811`,
  `rollback/vigia-race-20260811` y `rollback/puente-issues-20260811`.
  Hashes runtime/espejo: capataz
  `938ecf99a1da5804f39ca1621c6c8b7d3e0fbb5438c1940f8d9e8738826be0ac`;
  vigia `1ef53bdefefc821e7ea170ab96cebcc9115147f555dba798dd4c74188c8a7f95`;
  puente `29852eaa55a58477b7f3978a57bc1cdd671cf6c0a8feb3f71e1dfb203bd05bea`.
- La suite extendida de todos los circuitos modificados terminó `100%` verde
  con el skip existente; pasaron compilación Python, sintaxis JS, Ruff de
  archivos modificados y `git diff --check`. La suite total del repositorio
  se intentó con 180 s: colección `>1000` tests, no concluyó dentro del límite
  y el runner la abortó; no se clasifica como verde ni como fallo funcional
  localizado. El lint global aún reporta avisos preexistentes fuera de este
  circuito (por ejemplo `_RUTA_ABS` ya corregido, variables sin uso y un
  `puente_issues` ahora limpio); no se arreglaron cosméticos ajenos.
- Verificación viva solo lectura después del despliegue: `/api/revision`
  `200`/40 filas, `/api/revision/episodios` `200`/12, `/api/ideas` `200`,
  auditoría `200`, XIO `200` con `available=true` y `work_valid=true`,
  desconocida `404` JSON, `HEAD` de auditoría cuerpo `0`; el Hub sigue
  escuchando en `0.0.0.0:8900`. El ledger permanece
  `1867614:544266:1786455915`. No se hicieron POST reales, llamadas externas,
  commit, push o merge; README/SVG siguen fuera del diff.

## Next action

Continuar con el siguiente circuito de escritores no cubiertos por estos
locks: revisar `director_work/decision`, `ledger.append_item` y los logs de
entrega para distinguir duplicado semántico de historial legítimo. Mantener
fixtures temporales, medir estado antes/después y corregir solo bugs
reproducibles; conservar XIO y el SVG canónico bajo sus compuertas actuales.

## Director persistente y contrato de acciones del ledger — 2026-08-11

- Se reprodujo que `director_work` usaba `append_item` para un ID estable
  `work:<work_id>`: un retry podía duplicar el trabajo. Se cambió a append
  único serializado; `director_decision` también usa el append único bajo el
  lock de ledger, conservando historial cuando cambia el ID temporal.
- La misma prueba descubrió que persistir un `rd_evidence` válido generaba
  `action=review`, que el ledger RD rechaza. Se añadió el mapa de contrato
  área→acción (`rd_evidence=verify_source`, `iskvw_curation=curate`,
  `tool_archaeology=test`, `svg_pipeline=measure`, etc.). La fixture local y
  MAK confirmaron `decision_ok=true`, `decision_action=verify_source`,
  `work_duplicate=true`, `decision_duplicate=true`, `rows=2`.
- Despliegue respaldado bajo `rollback/director-ledger-20260811`; Hub runtime
  y espejo comparten el nuevo hash verificado durante el despliegue. La
  matriz viva posterior devolvió auditoría `200` (`3218` bytes), archivo
  `200` (`version=1`), desconocida `404` JSON y `HEAD` con cuerpo `0`; el
  ledger permaneció `1867614:544266:1786455915116045067`.
- Suite extendida de los circuitos modificados sigue `100%` verde con el skip
  existente, más `py_compile`, `node --check`, Ruff focal y `git diff --check`.
  La suite global ya quedó registrada como no concluyente por timeout de 180 s,
  no como éxito. No se hicieron POST productivos, llamadas externas, commit,
  push o merge; README/SVG permanecen fuera del diff.

## Next action

Continuar con los escritores de entrega/logs legacy (`entregar`,
`revision`/`mutaciones` y cualquier append de jobs) y comprobar si sus IDs,
locks y contratos se alinean. Mantener la regla: fixture temporal, prueba
concurrente o de integración, lectura viva antes/después, backup de runtime y
sin tocar SVG/README ni usar proveedores externos sin necesidad.

## Entrega de jobs protegida — 2026-08-11

- `entregar.main()` leía `codex_delivered.json`, elegía jobs y solo guardaba el
  estado al final. Dos ticks solapados podían abrir dos PR draft antes de
  marcar el job. Se añadió lock de hilo + lock de archivo alrededor de la
  corrida completa; la fixture local y MAK confirmaron `fcntl=true`,
  `max_active=1`, `results=[0,0]`, sin git, PR ni estado productivo.
- Despliegue respaldado bajo `rollback/delivery-race-20260811`; runtime y
  espejo comparten hash
  `93ae6b589f6f31a2cef2b2d67a79368e89fc543c3ba572e76779ad4b5f598ceb`.
- La suite extendida de los circuitos tocados pasó `100%` con el skip
  existente; también pasaron `py_compile`, `node --check`, Ruff focal y
  `git diff --check`. La suite global sigue marcada como no concluyente por
  timeout de 180 s, no como verde. No hubo entrega real, POST productivo,
  proveedor externo, commit, push ni merge; README/SVG siguen fuera del diff.

## Next action

Terminar la revisión de `mutaciones` y append de jobs restantes, comprobando
si la atribución se escribe de forma atómica y si hay copias runtime que no
coinciden con su espejo. Después repetir la matriz viva y mantener abiertos
los circuitos que aún tengan evidencia pendiente; no declarar cierre global.

## Atribución de mutaciones, salud y eventos de jobs — 2026-08-11

- La revisión reprodujo dos ventanas de persistencia fuera del Hub: `mutaciones.registrar()` hacía append sin lock entre procesos, y `_salud_registrar()` hacía lectura–modificación–escritura sin coordinación; su propia documentación aceptaba incrementos perdidos. `research_lib.emitir_evento()` compartía el mismo borde para `eventos.jsonl`.
- Se añadieron locks de hilo + `fcntl` por archivo a los tres escritores. Salud ahora escribe a un temporal del mismo directorio y hace `os.replace`, para que un lector nunca vea JSON a medio escribir. Los eventos y mutaciones hacen `flush()` antes de liberar el lock.
- Fixtures locales focales: suite de `mutaciones`, salud, eventos y vigia `100%`; Ruff focal, `py_compile` y `git diff --check` pasan. La prueba MAK con 8 procesos conservó `8` mutaciones JSON válidas, `8` incrementos `api_errors` y `8` eventos JSON válidos; `fcntl=true`, todos los exit codes `0`.
- Despliegue respaldado bajo `rollback/mutaciones-health-events-20260811`. Runtime y espejo comparten: `mutaciones.py` `f5ed62f00ebf009784112ecd5523263198b57651df55ef2eb8218fcbaea3022b`; `research_lib.py` `c896826c36cfb2759df33daa84c96ce057c123c6ebf82bbc99e1dfc79598c7c5`.
- La matriz viva siguió sin mutaciones: auditoría `200`/`faro-portfolio-audit-v1`/`3218` bytes; inbox compacto `200`/`1922874` bytes; revisión `200`/`mak-reel-review-v1`; episodios `200`/`mak-episode-review-v1`; ideas `200`; XIO `200` con `available=true` y `work_valid=true`; desconocida `404` JSON; `HEAD` de auditoría cuerpo `0`. El ledger permaneció `544266:1867614:1786455915` antes y después.
- No se usaron AWS/Watsonx, no hubo POST productivo, entrega, commit, push ni merge. El proceso de interfaz de investigación está fuera de una unidad instalada; no se reinició a ciegas. La copia runtime sí quedó reemplazada y los siguientes workers cargarán el hash nuevo; el Hub de `:8900` siguió activo bajo su supervisor del host.

## Next action

Revisar los append restantes de `emitir_evento` ya cubierto y de los logs/colas legacy (`backlog_codex`, `descargar`, `energia_log`, `puente`), separando los que admiten callers concurrentes de los que tienen un solo dueño. Probar cada candidato con fixture temporal, preservar el borde XIO humano y volver a medir hashes y matriz viva; mantener el objetivo abierto.

## Colas legacy y destino de descargas corregidos — 2026-08-11

- `backlog_codex.main()` calculaba el backlog fuera de cualquier exclusión y anexaba después. Dos cron solapados podían leer la misma cola y escribir el mismo candidato automático. Se añadió un lock de hilo + archivo alrededor del ciclo completo, incluido el re-chequeo de deduplicación.
- `descargar.descargar()` tenía dos fallos de integración: `dest=...` no cambiaba el `MANIFEST` global, por lo que el registro terminaba en el destino por defecto; y dos descargas del mismo nombre compartían `archivo.part`. El lock por destino serializa esa ruta y el manifiesto se deriva ahora de `dest`.
- Prueba local y focal: suite extendida `100%` con el skip existente; Ruff focal, `py_compile`, `node --check iskwv/mesa_montaje.js`, `git diff --check` y protección README/SVG pasan. No se abrió navegador ni se procesó media.
- Despliegue respaldado bajo `rollback/backlog-download-race-20260811`. Runtime y espejo comparten: `backlog_codex.py` `d5af62745b8a654c2f4d5865b85652ddea77b9b0e66736b8f59df4668c665f9d`; `descargar.py` `d785e647c7796a05a4dde06be2a8d454262985401bb8dddd7a4667609e2c6170`.
- Fixture MAK multiproceso: dos cron dejaron `backlog_lines=1`, `backlog_unique=1`, ambos exit codes `0`; dos descargas dejaron el archivo final íntegro, dos líneas de manifiesto JSON válidas y ambos exit codes `0`. No se usó una URL real: `urlopen` fue falso y todo quedó en `/tmp` remoto.

## Next action

Revisar ahora los escritores de energía y puente para decidir con evidencia si tienen un solo dueño operativo o si también necesitan lock; comprobar copias runtime/espejo de esos módulos y cualquier integración que aún consuma rutas antiguas. Mantener el circuito humano XIO, repetir la matriz viva después de cada despliegue y no declarar cierre global.

## Interfaz de investigación y jobs.jsonl corregidos — 2026-08-11

- La interfaz real de `:8890` es `ThreadingHTTPServer`. `JOBS_LOCK` solo protegía `JOBS` en memoria; `_cerrar_job`, el bloqueo por guardia y `reanudar/abortar` anexaban `jobs.jsonl` sin lock. Callers concurrentes podían intercalar escrituras y dejar una línea JSON ilegible para `entregar`/los lectores.
- Se añadió lock de hilo + archivo (`fcntl`) y `_append_job_record()`; las tres rutas de escritura pasan por el mismo helper y hacen `flush()` antes de liberar la exclusión.
- Despliegue respaldado bajo `rollback/interfaz-jobs-race-20260811`. Runtime y espejo comparten `interfaz.py` `69ea555f88d895f51f324432cd5536372c7d4df0dc86e30ee95d27332256c955`. El proceso fue reiniciado de forma controlada por el watchdog y quedó escuchando en `0.0.0.0:8890` con PID `42843`.
- Fixture MAK multiproceso: `12/12` procesos terminaron `0`, `12` líneas JSON válidas y `12` IDs únicos. Verificación viva solo lectura: `/` `200`/`143956` bytes y `/api/jobs` `200`/`[]`; no se lanzó ningún job real.
- En Windows la prueba que requiere `fcntl` queda marcada como skip esperado; la misma prueba se ejecutó en MAK, donde está el dueño operativo Linux. README/SVG no entraron al diff.

## Next action

Auditar las escrituras restantes de la interfaz (`workflow.json`, configuración/env, memoria y repair) contra sus locks existentes y separar cualquier mutación POST que todavía no tenga exclusión. Luego repetir hashes, proceso `:8890`/`:8900`, matriz GET/HEAD y ledger; mantener abierta la búsqueda de integraciones sin desarrollar.

## Configuración de interfaz protegida — 2026-08-11

- `/api/workflow` ya estaba protegido por `WORKFLOW_LOCK` y escritura temporal; la inspección aisló la brecha restante en `/config`: `_guardar_config()` hacía backup + lectura + reescritura de `research.env` sin exclusión.
- Se añadió `CONFIG_FILE_LOCK` más lock de archivo y se dejó el read-modify-write en `_guardar_config_unlocked()`. La prueba MAK con 8 procesos confirmó `config_max_active=1`; no se cambió el `research.env` productivo.
- Despliegue respaldado bajo `rollback/interfaz-config-race-20260811`. Runtime y espejo comparten `interfaz.py` `feb522577b67127bfb64f4a02c8f9326e0dc9010883d1d274e6f5aab46c3f8bd`. El watchdog reinició el proceso y `:8890` quedó activo en PID `43252`.
- Matriz viva solo lectura: `:8890/` `200`/`143956` bytes; `:8890/api/jobs` `200`/`[]`; `:8900/api/portfolio/audit` `200`/`3218` bytes; XIO `200`/`7746` bytes; `HEAD` de auditoría `200`, `Content-Length=3218`; Hub e interfaz escuchando en `:8900` y `:8890`.
- Ledger antes/después de la matriz: `544266:1867614:1786455915` sin cambio. No hubo POST, job real, proveedor externo, commit, push, merge ni modificación README/SVG.

## Next action

Revisar el contrato de memoria/repair y las integraciones de `interfaz.py` que disparan `/api/fructificacion`, `/api/fusion`, `/api/ideas/anotar` y `/api/memoria/index`: comprobar si cada mutación delegada tiene idempotencia y lock en su dueño, sin duplicar almacenes ni ejecutar acciones productivas. Después repetir la batería focal y dejar documentada cualquier frontera humana aún pendiente.

## Mutaciones de research protegidas — 2026-08-11

- `fructificacion.decidir()` tenía la misma carrera read-modify-write en el registro de decisiones humanas; se añadió lock de hilo + archivo, temporal único, `fsync` y `os.replace`. La prueba MAK con 8 procesos conservó 8 decisiones distintas.
- `memoria.indexar()` tenía lock solo en el caller HTTP; una invocación standalone podía compartir `index.jsonl.tmp`. Se añadió exclusión dentro del módulo, incluyendo `fcntl`; 8 procesos MAK midieron `index_max_active=1` sin tocar el índice productivo.
- `fusion.crear()` escribía directamente el primordio final. Se cambió a temporal único + `fsync` + `os.replace`; 8 procesos MAK convergieron en un único archivo válido para la misma fusión.
- Despliegue respaldado bajo `rollback/research-mutations-race-20260811`. Runtime/espejo comparten: `fructificacion.py` `4fd656cf6f0836a805fcd43d48dc0e27e659ce7da760db572ac3281973084440`; `fusion.py` `c7b772b6aa821d7d3b52d3a78cf4457101c7c30635c895c3ec74e1ae33269fba`; `memoria.py` `b86fd6a01f6cd9d60195aa2f41cfcf8173e67d880fe7fffd43abf32994cd6efe`.
- La batería focal completa pasó `100%` con los skips esperados; `py_compile`, Ruff focal, `node --check iskvw/mesa_montaje.js`, `git diff --check` y protección README/SVG pasan. No hubo POST productivo, proveedor externo ni índice real reescrito.
- La interfaz fue reiniciada por el watchdog y quedó en `:8890` PID `44060`; el Hub sigue en `:8900` PID `37398`. Las lecturas GET/HEAD y XIO siguen sanas; el ledger no se modificó.

## Next action

Auditar la última capa de integraciones delegadas: `ideas_a_micelio.sincronizar`, `memoria`/grafo cache y los writers de `fructificacion`/`fusion` desde rutas HTTP y standalone. Buscar duplicación de almacenes, estados que se pierdan al reiniciar y contratos que no lleguen al ledger; mantener fixtures, backups y compuertas humanas, sin declarar cierre global.

## Adaptador de ideas y regresión viva final — 2026-08-11

- `ideas_a_micelio.sincronizar()` podía escribir adaptadores `.md` directamente mientras otro indexador tomaba un snapshot distinto: el último en limpiar podía retirar una idea válida, y un lector podía observar un documento incompleto. Se añadió lock de destino (`fcntl` en MAK) y temporal único + `fsync` + `os.replace` por documento.
- Fixture MAK corregido: la primera ejecución del harness escribió el texto literal `\\n` y produjo `0` adaptadores; se repitió con saltos reales (`chr(10)`) y confirmó `8/8` procesos `0`, `idea-a.md` y `idea-b.md` presentes y válidos, `fcntl=true`. No fue un fallo del módulo.
- Despliegue respaldado bajo `rollback/ideas-micelio-race-20260811`; runtime/espejo comparten `ideas_a_micelio.py` `93e65cfd98f98a799da9eefbd78451ca26e04d4164597292ed02cb252094ae79`.
- La última batería focal terminó `100%` con skips esperados; Ruff, `py_compile`, `node --check iskvw/mesa_montaje.js`, `git diff --check` y exclusión de README/SVG pasan. La primera matriz final falló únicamente en el harness al tratar la lista JSON de `/api/jobs` como dict; se repitió corrigiendo el parser.
- Matriz GET/HEAD final corregida: `:8890/` `200`/`143956`; `/api/jobs` `200`/lista vacía; auditoría `200`/`3218`; inbox compacto `200`/`1922874`; revisión `200`/`25209`; episodios `200`/`20542`; ideas `200`/`1081`; XIO `200`/`7746`, `available=true`, `work_valid=true`; `HEAD` auditoría `200`, cuerpo `0`. Los procesos quedaron `:8890` PID `44597` y `:8900` PID `37398`; runtime/espejo comparten hashes de todos los módulos desplegados.
- Ledger antes/después: `544266:1867614:1786455915` sin cambio. No hubo proveedores externos, POST productivos, trabajos reales, commit, push, merge ni modificación del README/SVG.

## Next action

Mantener abierta la auditoría para la siguiente sesión: revisar contratos de estado tras reinicio, especialmente el cruce `jobs.jsonl`→`entregar`, la lectura de caches del grafo y la sincronización pausada de repo/runtime. Si aparece otra carrera reproducible, aislarla y respaldarla igual; no usar proveedores ni publicar cambios sin una integración concreta y una compuerta humana.

## Caché del grafo e invalidación desde mutaciones — 2026-08-11

- `memoria.grafo_semantico()` leía, calculaba y escribía con el mismo
  `grafo_cache.json.tmp` sin exclusión. Dos requests de `ThreadingHTTPServer` o
  dos callers standalone podían pisar el temporal o instalar un caché de otra
  reconstrucción. Además `/api/fructificacion` borraba el archivo directamente
  y `/api/fusion` no invalidaba el caché después de crear un primordio.
- Se añadió lock de hilo + archivo (`fcntl`) alrededor de lectura, cálculo,
  reemplazo e invalidación; `invalidate_grafo_cache()` es ahora la única puerta
  para invalidar desde ambos endpoints. La suite focal pasó `9/9`; el fixture
  MAK de dos procesos midió `graph_max_active=1`, `invalidation=true` y
  `fcntl=true`.
- Despliegue respaldado bajo `rollback/graph-cache-race-20260811`. Runtime y
  espejo comparten `memoria.py`
  `15353a6cc2296c929a1eb573213aa0d1e86bf2b9f1b37eb0bdf84063629d2dd8` e
  `interfaz.py`
  `a5f815038377d3f3c4f42f7dbd1df8694f53f222734182516cede9aa9496411a`.
- Verificación viva sin UI: `/api/memoria/grafo?umbral=0.9&limite=5` devolvió
  `200`, `5` nodos proyectados, `1` arista y `1828` nodos en meta, sin error;
  `:8890` quedó activo en PID `45936`. El ledger de fichas permaneció
  `2829673:6425091:1786160844` antes y después.
- El primer harness remoto falló por transporte Base64 y por no incluir el
  path de `research_lib`; se corrigió y la segunda ejecución fue la evidencia
  válida. El primer intento de reinicio también fue bloqueado por mi propio
  patrón `pgrep` dentro del comando; se repitió separado y el watchdog levantó
  la interfaz correctamente. No se usaron proveedores ni POST productivos.

## Ledger Codex compartido con el entregador — 2026-08-11

- `research/jobs.jsonl` y `codex/jobs.jsonl` son colas separadas de forma
  intencional; `entregar.py` debe consumir únicamente la cola Codex. La brecha
  real era que `interfaz_codex.py` y `agente_libre.py` escribían sin lock, y
  `entregar.py` podía leer mientras una línea estaba siendo anexada.
- Se añadió el mismo sidecar `codex/jobs.jsonl.lock` a los dos productores y al
  lector del entregador; `interfaz_codex._cargar_jobs()` también lee bajo esa
  exclusión. Los append pasan por un helper común local y hacen `flush()`.
- Despliegue respaldado bajo `rollback/codex-jobs-ledger-lock-20260811` y
  `rollback/codex-jobs-ledger-lint-20260811`. Runtime/espejo comparten:
  `interfaz_codex.py`
  `3392e4e2d37f3caff8e0a28b7be107c727caaf3f5f1b413e3bda491ff26fd5d9`,
  `agente_libre.py`
  `03cd6de4ef397466d88b6fc57c0c7cba45befe42e6ef3efe69e2c7f64d212628` y
  `entregar.py`
  `acb4883554291811dc611ffc3909a737d9ca9b7f29c843fa48dc795589d2735c`.
- Fixture MAK: `8` productores, `8` líneas JSONL, `8` IDs únicos y el lector
  del entregador terminó viendo `8`; todos los procesos salieron `0`,
  `fcntl=true`. `mak-codex.service` está activo en PID `47411`; `:8891/` y
  `:8891/api/jobs` devolvieron `200`. No se abrió PR, no se ejecutó entrega y
  no se modificó el ledger productivo.
- La regresión focal completa pasó con skips Linux esperados; `py_compile`,
  Ruff focal y `git diff --check` quedaron limpios. Ruff inicialmente marcó un
  import muerto y una condición antigua en `interfaz_codex.py`; ambos se
  corrigieron antes del despliegue final.

## Next action

Continuar con contratos de estado después de reinicio y con la sincronización
pausada repo/runtime: comparar qué módulos desplegados todavía no tienen una
fuente canónica o una comprobación de hash automática. Después auditar los
lectores de caches y los logs de entrega que aún no comparten lock, usando
fixtures temporales y una matriz GET/HEAD; mantener el objetivo abierto, sin
declarar cierre global ni tocar README/SVG.

## Coherence y archivos de rollback — 2026-08-11

- `coherence.py --strict` produjo `23` drift points falsos después de preservar
  backups: `BOX_OWNED` no conocía `rollback/` y el detector marcaba cualquier
  `hub.py`/`entregar.py` archivado como invocado porque buscaba sólo el basename
  en cron/systemd. Se reprodujo en el box; no se borró ningún backup.
- Se añadió `rollback/` a `BOX_OWNED`. La diferencia real restante de
  `rescue_adjudicator.py` era sólo una docstring en español del runtime; se
  respaldó y se alineó con el espejo, sin cambio ejecutable. Test local,
  `py_compile` y Ruff pasan.
- Despliegue respaldado bajo `rollback/coherence-rollback-drift-20260811`.
  `coherence.py` runtime/espejo comparte hash
  `4d1e08ee7681c7eaaf60d1ce2fee9db792b26e6c41ede94ee1ae1930d0ea7675` y
  `rescue_adjudicator.py` comparte
  `7b6b00ba96ccf4d9def28ee727c5b5b904399951aabd0556ca87120d1c5d9bbd`.
- La verificación MAK volvió a dar `0 different`, `0 not copied` y `0 box-only
  invoked` para todos los órganos: `No drift: the box runs what the repo says.`
  El checkout remoto sigue con cambios de auditoría y `rollback/` sin trackear,
  pero esa evidencia queda fuera de los órganos ejecutables y el repo-sync
  continúa pausado para no sobrescribir runtime manual.

## Next action

Auditar la frontera de sincronización pausada: listar los módulos que el
runtime ejecuta pero que aún viven sólo como cambios sucios del checkout de
auditoría, comprobar qué puede perder el próximo `git checkout/reset` y dejar
un informe de reconciliación sin hacer merge automático. Después revisar los
lectores de estado tras reinicio y los logs legacy restantes; mantener la
compuerta humana y el objetivo abierto.

## Recuperación de jobs de research después de reinicio — 2026-08-11

- Se reprodujo una pérdida de proyección: `/home/mak/research/jobs.jsonl` tenía
  `462` líneas, pero `interfaz.py` definía `_load_jobs()` y nunca la llamaba en
  `main()`. Tras reiniciar, `/api/jobs` devolvía `[]` (`2` bytes), mientras el
  ledger seguía intacto. Codex sí tenía su llamada equivalente.
- `main()` ahora recarga los últimos `15` jobs al arrancar y `_load_jobs()` usa
  el mismo sidecar lock de `jobs.jsonl`; el ledger sigue siendo append-only y
  las líneas corruptas se omiten sin reescribirlo. Test local: conserva dos
  jobs válidos y la línea corrupta, sin modificar el archivo.
- Despliegue respaldado bajo `rollback/research-restart-state-20260811`.
  Runtime/espejo comparten `interfaz.py`
  `6d36bd9b9bdf7bff22bf7851c5ab06dcd7e1daa5320b4f7ba542b413d5fd25e4`.
  Tras reinicio controlado, `:8890/api/jobs` devolvió `200`, `11278` bytes y
  `15` jobs visibles; el ledger medía `183513` bytes. No se lanzó ningún job.
- Un primer llamado combinado al watchdog no dejó el proceso visible; se
  repitió en una llamada separada y el watchdog informó `interfaz.py no esta
  corriendo. Lanzando...`; el proceso quedó en PID `48610`. La segunda
  verificación es la válida y no mostró error de Python.

## Next action

Comparar ahora los otros estados que sobreviven en disco pero se reconstruyen
en memoria al arrancar (`workflow`, grafo, decisiones humanas y entregas), y
verificar que el repo-sync pausado no pueda reinstalar una versión anterior
sin una reconciliación explícita. Mantener pruebas temporales, hashes y GETs;
no hacer reset/merge/push ni declarar cierre global.

## Estado de entregas resistente a corte — 2026-08-11

- `entregar.guardar_estado()` escribía directamente
  `codex_delivered.json`. Un corte durante `json.dump` podía dejar JSON
  truncado; `cargar_estado()` lo interpretaba como vacío y el siguiente tick
  podía volver a intentar una entrega ya abierta.
- Se cambió a temporal único en el mismo directorio, `flush()`, `fsync()` y
  `os.replace`, con limpieza del temporal si falla. La prueba local y el
  fixture MAK confirmaron JSON válido, orden estable y `temp_left=0` sin tocar
  el estado real.
- Despliegue respaldado bajo `rollback/delivery-state-atomic-20260811`.
  Runtime/espejo comparten `entregar.py`
  `4a37c0d026bfb1f27a9e0e39906541df7e673525e04d4dc3c795e6b4769b2969`;
  el cron real sigue siendo `0 */6 * * * ... entregar.py --limit 1`.

## Next action

Revisar los estados restantes que se materializan al arranque y el informe de
reconciliación repo/runtime: workflow, caché/decisiones del grafo, estado de
entrega y cualquier `*.json` leído sin instalación atómica. Mantener fixtures
temporales, backups y GETs; el siguiente cambio debe estar respaldado por una
falla reproducible y no por una suposición.

## Orquestador de trabajo serializado — 2026-08-11

- `trabajo.py` corre por cron cada `30` minutos y no tenía exclusión de tick ni
  escritura atómica de `.trabajo_state.json`. Dos ejecuciones superpuestas
  podían despachar dos unidades con el mismo estado y dejar el contador
  perdido; un corte durante `json.dump` podía dejar el estado inválido.
- Se añadió lock de hilo + archivo alrededor del tick completo y estado
  temporal único + `flush()`/`fsync()`/`os.replace`. Fixture local y MAK con dos
  ticks falsos confirmaron `count=1`, `temp_left=0` y `fcntl=true`, sin POST ni
  llamadas a proveedores.
- Despliegue respaldado bajo `rollback/trabajo-state-race-20260811`.
  Runtime/espejo comparten `trabajo.py`
  `d7e9327513ca1da7688c0a499774c243fb69536d2326283f1e4a8e2ca71b001f`;
  el cron real sigue activo cada 30 minutos.

## Next action

Completar la auditoría de writers de estado de cron (`latido`, `red_watch`,
`junta`) sólo si su duración y ownership permiten solapamiento real; después
revisar la reconciliación pausada de repo/runtime y actualizar el circuito
vivo. No ampliar a proveedores ni modificar datos productivos sin una
reproducción concreta.

## Reanudación humana de research serializada — 2026-08-11

- Dos requests concurrentes a `/api/reanudar` sobre el mismo job `PAUSADO`
  podían pasar la lectura del estado antes de que alguna lo cambiara, modificar
  el checkpoint y lanzar dos workers. El lock de `JOBS` sólo protegía la
  búsqueda, no la reclamación.
- La ruta ahora reclama el job como `REANUDANDO` bajo `JOBS_LOCK` antes de
  tocar el checkpoint; el segundo request recibe `400`, y los errores restauran
  `PAUSADO`. Fixture MAK: `reanudar_requests=2`, `accepted=1`, `rejected=1`,
  `checkpoint_actions=1`, sin ejecutar research.
- Despliegue respaldado bajo `rollback/research-reanudar-claim-20260811`.
  Runtime/espejo comparten `interfaz.py`
  `dc39e7918131d310d99a50fc5c46debd95eb24a5dfa193e92312dcb278c3d15e`;
  `:8890` quedó activo en PID `50036` y devolvió `200`/`11278` bytes en
  `/api/jobs` tras el reinicio.

## Next action

Cerrar la revisión de ownership de `latido`, `red_watch` y `junta` mediante
duraciones/cron reales y no por intuición; después volver a medir la matriz
completa y el drift. Si aparece otro writer sin exclusión, aislarlo en un
fixture y respaldarlo antes de tocar runtime.

## Estados de cron instalados atómicamente — 2026-08-11

- `latido` (cada 4 h), `red_watch` (cada 2 min) y `junta` (cada 6 h) tienen un
  solo dueño cron y sus ventanas no justifican bloquear toda la ejecución;
  sí escribían estados/ajustes JSON directamente. Un corte podía dejar `.state`
  o `ajustes_junta.json` truncado y hacer perder el cupo o una transición de
  red/decisión.
- Se añadió helper local de temporal en el mismo directorio con `flush()` +
  `fsync()` + `os.replace` para los estados e índices afectados. Suite local:
  `13` tests verdes; fixture MAK: `cron_states=latido,red_watch,junta
  atomic=true temp_left=0`. No hubo llamadas de red ni proveedor.
- Despliegue respaldado bajo `rollback/cron-state-atomic-20260811`.
  Hashes runtime/espejo: `latido.py`
  `844f2a53371de477180f61091b00487e522805541bcce38b87c48068a9f7c0db`;
  `red_watch.py`
  `025d400d2f69182ef55ed2e2977851e44f9323123d25eb5bf93b92f0e46ba357`;
  `junta.py`
  `2fc45907daa161257e17c8bf5c7310c345e28a0eb99d4dace46a41c1790df1dc`.

## Next action

Ejecutar la matriz GET/HEAD y `coherence --strict` después de todo este bloque,
comparar hashes del runtime y espejo una vez más y revisar el estado del
checkout auditado. Mantener como pendientes los writers que no tengan un
caller operativo demostrado; no declarar cierre global.

## Matriz viva posterior al bloque — 2026-08-11

- La regresión focal ampliada terminó `100%` verde con skips Linux esperados;
  `py_compile`, Ruff focal, `git diff --check` y la protección README/SVG
  también pasan. No se abrió navegador, no se usaron proveedores y no hubo
  POST productivos.
- `coherence --strict` devolvió `0`: `0 different`, `0 not copied` y `0
  box-only invoked` en los cinco órganos. Quedan `948`/`5` archivos box-only
  no invocados (estado/backups), clasificados como tales por contrato.
- Matriz solo lectura: `:8890/` `200`/150441; research `/api/jobs`
  `200`/11278; grafo `200`/2797; `:8891/` `200`/18744; Codex `/api/jobs`
  `200`/8452; auditoría `200`/3218; inbox `200`/1922874; revisión
  `200`/25032; episodios `200`/20084; ideas `200`/1081; XIO `200`/7741 con
  `available=true`. Hub y Codex están `active`; research PID `50036`.
- El ledger de fichas permaneció `2829673:6425091:1786160844` antes y después.
  Runtime/espejo siguen iguales para research, Codex y trabajo; no hubo
  commit, push, merge ni reset.

## Next action

Mantener abierta la auditoría en el checkout de auditoría: documentar la
reconciliación pendiente entre esa rama sucia y el `mak` canónico sin aplicar
reset automático; revisar cualquier writer que aparezca en el siguiente
inventario de cron y sus contratos tras reinicio. La siguiente sesión debe
empezar por esa frontera, no por reabrir los circuitos ya medidos.

## Reconciliación del espejo y persistencia de configuración — 2026-08-11

- El detector `tools/mak_ops/check_mak_mirror.py` sólo cubría ocho archivos y
  podía leer el checkout equivocado porque usaba `Path.cwd()`. Se amplió a
  `32` entradas en plataforma, research, Codex, vigia y curatoria, y ahora la
  raíz se resuelve desde `Path(__file__).resolve().parents[2]`. Una prueba
  estática evita que el comando vuelva a validar otra rama por accidente.
- La medición del checkout de auditoría dio `32 PASS / 0 MISMATCH` contra
  `/home/mak/flujo/cultura` y los órganos vivos. La medición independiente de
  `C:\IA\flujo` dio `6 PASS / 26 MISMATCH`: el canónico sigue en `mak`
  `abe27c22`, mientras GitHub `origin/mak` es `160b94d3`. El checkout remoto
  también sigue en `abe27c22`, sucio (`29` entradas), con el repo-sync
  pausado. No se hizo reset, merge, commit ni push.
- La divergencia no se ocultó: quedó en
  `_logs/cauce_director/20260805/mak_mirror_canonical_post_20260811.md` y la
  comprobación limpia en `mak_mirror_post_interfaz_20260811.md`. El primer
  `git ls-remote` remoto falló por ejecutarse fuera del checkout; repetido
  dentro de `/home/mak/flujo` confirmó que el `origin` sí existe. Ese fallo es
  del harness, no del repositorio.
- Se reprodujo y corrigió una frontera de persistencia: `workflow.json` y
  `research.env` tenían temporal fijo o escritura directa. Ahora usan
  temporal único en el mismo directorio, `flush` + `fsync` + `os.replace`, y
  limpian el temporal si la instalación falla. La batería Atlas/reanudación/
  checkpoints/entrypoints terminó verde (`100%` de los tests ejecutables;
  `fcntl` sólo se saltó en Windows). La prueba Linux confirmó que un fallo de
  `replace` conserva el archivo anterior y no deja basura.
- Se desplegó `cultura/mak_research/interfaz.py` al repo espejo y a
  `/home/mak/research/interfaz.py`, con copias en
  `rollback/research-config-atomic-20260811`. Tras el reinicio, el watchdog y
  un arranque manual coincidieron durante unos segundos y crearon dos
  procesos; se terminó únicamente el manual `53654`. La verificación final
  dejó un solo proceso `53620`, un listener en `:8890`, `15` jobs visibles y
  `/api/workflow` recuperado (`mode=single`, `5` conexiones).
- Matriz viva posterior: `:8890/`, `/api/jobs` y grafo `200`; `:8891/` y
  `/api/jobs` `200`; Hub `/api/portfolio/audit` `200` con esquema
  `faro-portfolio-audit-v1`; inbox `200` con esquema
  `faro-portfolio-inbox-v1`. El Atlas remoto mide `7044` registros, `91`
  etiquetas (`work=27`, `record=13`, `review=1`, `discard=50`), y mantiene
  `automation_ready=false`; esas cifras son proyección verificable, no una
  promoción automática.
- `coherence.py --strict` volvió a dar `0 different`, `0 not copied` y `0
  box-only invoked` en los cinco órganos. La igualdad del espejo auditado no
  elimina la brecha del checkout canónico; el próximo transporte debe
  resolverla de forma explícita y preservando sus cambios locales.

## Next action

Reconciliar la rama `mak` canónica con el checkout auditado mediante una
decisión explícita de transporte, sin reset automático; antes de eso, conservar
los informes de `check_mak_mirror` como evidencia. Después auditar los demás
writers de estado no incluidos en los 32 entrypoints (checkpoints de pausa,
logs legacy y artefactos de entrega) con fixtures de corte/reinicio, y revisar
las integraciones aún no conectadas a la superficie Atlas. Mantener la
compuerta humana, no usar proveedores sin una tanda concreta y no tocar
README/SVG.

## Writers restantes e integraciones Atlas verificadas — 2026-08-11

- La revisión de cron encontró tres writers que aún usaban temporales fijos o
  no hacían `fsync`: checkpoints humanos (`pausa.py`), estado de ejecución del
  worker (`worker.py`) y estado/compactación de vigia (`vigia.py`). Se añadió
  lock sidecar para acciones de checkpoint entre procesos y temporales únicos
  con limpieza ante fallo para los tres. La prueba local pasó y la prueba
  remota Linux confirmó que un `replace` fallido conserva el archivo anterior
  y deja `0` temporales.
- Se desplegaron los tres módulos al espejo y runtime, con rollback en
  `rollback/checkpoint-state-atomic-20260811`. Se amplió el detector de espejo
  para incluir `pausa.py` y `worker.py`: la medición final da `34 PASS / 0
  MISMATCH`. El checkout canónico independiente permanece en `6 PASS / 28
  MISMATCH`; esa brecha sigue pendiente y no se resolvió con reset.
- El reinicio de research se hizo mediante `/home/mak/research/watchdog.sh`,
  que es su dueño real. Quedó un solo `interfaz.py` (`PID 55177`) en `:8890`;
  no se repitió la superposición manual. `:8890`, `:8891` y `:8900` siguen con
  un listener cada uno.
- La regresión final ejecutable pasó completa: Atlas/bridge, reanudación,
  pausa, vigia, concurrencia de interfaz y entrypoints; Ruff, `py_compile`,
  `git diff --check` y la protección README/SVG también pasan. Los skips son
  únicamente los tests Linux que requieren `fcntl` cuando corren en Windows.
- La matriz de integración read-only confirmó los esquemas:
  `faro-portfolio-decision-index-v1` (`58` selecciones, `20` feedback de
  relaciones, `8` revisiones externas), `faro-portfolio-contract-surface-v1`,
  `faro-portfolio-review-queue-v1`, `faro-portfolio-organism-v1` (`7044`
  bloques, `7` canales, `21` conexiones, `12` decisiones) y
  `faro-xio-evidence-v1` (`work_valid=true`, `21` setlist/cues/segmentos).
  Una escena válida conserva XIO separado, `promotion=none` y
  `next_action=link manually to portfolio source`; no se creó un vínculo
  automático ni se escribió una decisión.
- Matriz viva final sin POST: `:8890/` `200`/150441, `/api/jobs`
  `200`/11278, grafo `200`/2797; `:8891/` `200`/18744, jobs `200`/8452;
  auditoría Hub `200`/3218 e inbox `200`/3663485. El Atlas permanece en
  `7044` registros, `91` etiquetas, `58` piezas con estado actual y
  `automation_ready=false`. `coherence --strict` mantiene cero drift.

## Next action

Mantener abierta la reconciliación del `mak` canónico (`abe27c22` frente a
`origin/mak=160b94d3`) y decidir el transporte preservando los cambios locales.
Después revisar los logs append-only legacy y el vínculo humano pendiente de
XIO con una compuerta explícita; seguir probando cortes/reinicios y cualquier
writer nuevo que no esté cubierto por los 34 hashes. No promover predicciones,
no activar el repo-sync y no tocar README/SVG.

## Puente/minería y frontera final del espejo — 2026-08-11

- Se reprodujo otra frontera de persistencia en los writers de
  `puente_issues.py` y `mineria_rd.py`: ambos podían dejar un temporal fijo o
  un archivo parcialmente instalado si el proceso caía durante la escritura.
  Ahora usan temporal único en el mismo directorio, `flush` + `fsync` +
  `os.replace`, con limpieza ante fallo. Las pruebas locales, Ruff,
  `py_compile` y la prueba remota Linux de fallo de `replace` pasaron; el
  archivo anterior se conserva y no quedan temporales.
- Se desplegaron ambos módulos al repo espejo y al runtime, con rollback en
  `rollback/bridge-mining-state-atomic-20260811`. El detector cubre ahora `36`
  entrypoints: el checkout de auditoría da `36 PASS / 0 MISMATCH` contra repo
  y runtime; el checkout canónico independiente da `7 PASS / 29 MISMATCH`.
  Esta divergencia sigue siendo una frontera de transporte, no se ocultó ni se
  resolvió con reset, merge, commit o push.
- La batería focal ejecutable sigue verde al `100%`; Ruff, `py_compile`,
  `git diff --check`, la matriz viva y `coherence.py --strict` también. No se
  modificó `README.md` ni `arte-ascii-readme.svg`.
- La verificación Atlas permanece read-only: `7044` registros, `91` etiquetas,
  `58` piezas con estado actual, `automation_ready=false`; XIO conserva
  `work_valid=true` pero exige vínculo manual con la fuente de portafolio. No
  se promovieron predicciones ni se escribieron decisiones.

## Next action

Mantener abierta la reconciliación del `mak` canónico (`abe27c22` frente a
`origin/mak=160b94d3`) preservando sus cambios locales. Auditar ahora los
writers append-only legacy (`energia_log`, `puente`, `mutaciones`, `capataz`,
`conversacion`) y su ownership real en cron/callers antes de modificar;
después cerrar la inspección del vínculo humano XIO con una compuerta explícita.
Conservar la cobertura de `36` hashes, seguir con pruebas de corte/reinicio y
no activar repo-sync ni tocar README/SVG.

## Writers activos y cron declarativo — 2026-08-11

- `mutaciones.log` sí es un writer activo: `retencion.py` y `vigia.py` lo
  invocan. `mutaciones.py` conserva ahora lock de archivo entre procesos,
  `flush` + `fsync`, y la prueba remota de ocho procesos concurrentes dejó
  ocho líneas JSON válidas. Se preservó rollback en
  `rollback/mutaciones-fsync-20260811`.
- `capataz.py` también es activo (`10,40 * * * *`). Su lock ya cubría la
  carrera de intents; ahora sus tres append críticos (ledger de research,
  backlog Codex y bitácora) fuerzan persistencia. La prueba local y la prueba
  remota entre procesos pasaron; rollback en
  `rollback/capataz-fsync-20260811`.
- La copia declarativa `cultura/mak_plataforma/crontab.mak` discrepaba del
  crontab efectivo: `MAK-REPO-SYNC` estaba activo en el archivo y pausado en
  el box. En el checkout de auditoría quedó marcado `# PAUSED-FARO` y una
  prueba evita reactivarlo por reaplicación accidental. El crontab efectivo no
  se tocó.
- Hub tenía locks de hilo pero sus JSONL de selección, clasificación,
  relaciones, feedback, triangulación, revisión externa y visión no hacían
  `fsync`. Se centralizó `_portfolio_append_jsonl`, se probaron sus escritores
  y se desplegó con rollback en `rollback/hub-jsonl-fsync-20260811`; el único
  dueño `mak-hub.service` fue reiniciado por systemd, sin duplicar procesos.
  Hashes auditados: `36 PASS / 0 MISMATCH`; canónico independiente:
  `7 PASS / 29 MISMATCH`.
- Ownership legacy verificado: `puente.py` no está en cron ni tiene proceso
  vivo; `conversacion.log` conserva solo el arranque histórico. `energia_log.py`
  tampoco está en el cron efectivo. No se modificaron esos módulos inactivos.
- Matriz posterior al reinicio: listeners únicos en `:8890`, `:8891` y
  `:8900`; `/api/portfolio/audit`, decision-index, XIO evidence y organism
  responden `200`. Atlas sigue en `7044` registros, `91` etiquetas, `58`
  piezas con estado actual y `automation_ready=false`. XIO sigue separado y
  requiere vínculo humano explícito; no se creó un vínculo automático.

## Next action

No cerrar la auditoría: resolver la frontera de transporte del `mak` canónico
sin reset, revisar los writers de los cron activos que aún no están en los 36
hashes y diseñar/probar el vínculo humano XIO sin convertir evidencia en hecho.
Después ejecutar la batería focal completa y volver a medir la matriz. Mantener
repo-sync pausado y no tocar README/SVG.

## Regresión final de esta tanda — 2026-08-11

- La batería focal terminó `100%` verde: `pytest` ejecutó la cobertura Atlas,
  persistencia, Capataz, Hub, cron y entrypoints sin fallos; los únicos
  `14` skips son los fixtures que requieren `fcntl` al correr en Windows.
  Ruff, `py_compile` y `git diff --check` también pasaron.
- `coherence.py --strict` en MAK volvió a medir `0 different`, `0 not copied`
  y `0 box-only invoked` en los cinco órganos. La comprobación de espejo más
  reciente conserva `36 PASS / 0 MISMATCH` para auditoría/repo/live y
  `7 PASS / 29 MISMATCH` al comparar el canónico `C:\IA\flujo`.
- Matriz de código posterior: `:8890/` `200`/151221, `/api/jobs`
  `200`/11288, grafo `200`/2801; `:8891/` `200`/18772, jobs `200`/8506;
  Hub auditoría `200`/3218 e inbox `200`/3681556. Quedó exactamente un
  listener en cada puerto `8890`, `8891` y `8900`.
- No se usaron AWS/Watson en esta tanda: no había una hipótesis que necesitara
  inferencia externa y no se generaron decisiones de producto. No se tocó
  README/SVG ni se hizo commit, push, merge o reset.

## Next action

Continuar desde dos frentes abiertos: (1) transporte explícito del checkout
canónico, preservando sus cambios, y (2) integración humana del vínculo XIO y
auditoría de los writers de cron aún fuera de los 36 hashes. Cualquier vínculo
XIO debe quedar como decisión humana append-only, con fuente, identidad,
confianza y promoción `none`; no convertir la evidencia separada en relación
automática. Mantener el repo-sync pausado.

## Cobertura completa de cron — 2026-08-11

- La auditoría del inventario efectivo de cron encontró que la cobertura de
  `36` no incluía todos los targets ejecutados. El checker se amplió a `47`
  archivos, incorporando watchdogs, guardias, `revisor`, `vigilar_red`,
  `retencion`, `corpus_a_micelio` y los dos scripts de lenguaje.
- La medición completa dio `47 PASS / 0 MISMATCH` contra el checkout auditado,
  repo MAK y live MAK. La medición del canónico Windows, sin reconciliar, dio
  `18 PASS / 29 MISMATCH`; esa diferencia es evidencia de transporte pendiente,
  no un motivo para resetear.
- `tests/test_operational_entrypoints.py`, Ruff y el checker pasan. El reporte
  está en `mak_mirror_full_cron_20260811.md`; su equivalente canónico en
  `mak_mirror_canonical_full_cron_20260811.md`.

## Next action

Two circuits remain open: reconcile the canonical checkout while preserving its
changes, and provide a verifiable human XIO link without auto-linking. Then
test the 47 cron targets across stop/restart boundaries, starting with the
watchdog and retention jobs, and record any real discrepancy before editing.
Do not activate repo-sync or touch README/SVG.
