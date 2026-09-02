# Operational Handoff

## CURRENT AUTHORITATIVE CHECKPOINT — Phase 571

Read this block first after compaction. The compact architectural synthesis is
`docs/MAK_CURRENT_STATE.md`; this handoff remains the evidence ledger.

- Current objective: keep `/home/mak/flujo` publishable and easy to resume by
  exposing one current architecture, one active consumer map and one truthful
  continuity record. Historical phase files remain evidence, not competing
  instructions.
- Physical authority: `/home/mak/*` is authoritative; `/home/mak/flujo` is
  the authoring baseline; `/home/mak/WIN` is historical evidence and is not a
  runtime dependency. README and the current SVG artwork are protected.
- Current interfaces: MAK hub `127.0.0.1:8900`; SearXNG backend
  `127.0.0.1:8888`; FLUJO `app/serve` remains a portable on-demand path with
  historical default `8765`, not a permanent service.
- Current event consumer: GitHub Actions runner `mak` calls
  `flujo.ig.download.download_post`, preserves media early to OneDrive and
  dispatches image/video to `render_flyer_mak.py` or
  `render_video_sequence_mak.py`. Legacy Windows bridge files are not called
  by this active path.
- Current data boundary: `data/rd.db` is the RD catalog; `data/rd_datos.db`
  remains a separate empty privacy store; venue JSON is declarative source;
  generated indexes are projections.
- Current media contract: image `fitwidth_fade`; video `cover_center` with
  real source dimensions, centered X/Y, preserved ratio, no stretch and no
  black bars; Cycles 128 samples and verified GPU for sequence rendering.
- Repository consolidation completed in this phase: added
  `docs/MAK_CURRENT_STATE.md`; corrected current pointers in `CAPACIDADES.md`
  and `MAPA.md`; corrected the active MAK renderer and hub documentation; made
  the historical video smoke explicit.

## Open integration items

1. Observe a new real issue in Actions to confirm early OneDrive preservation
   and final/partial publication; no real issue replay has been invented.
2. Run one bounded real-video manifest smoke when a source is available; do
   not render a full reel solely to test layout metadata.
3. Keep provider/API status tied to a recent read-only probe, consumer and
   cost; keys alone are not operational evidence.
4. Treat legacy cleanup as a separate compatibility phase. Do not delete
   `flyer_auto.py`, `bridge_issue_render.py` or `render_video_rd.py` until
   imports, CLI entrypoints, tests and rollback are measured.

## Next concrete action

Validate the consolidated documentation and source labels in the foreground,
then publish only the intentional files. Preserve unrelated dirty worktree
changes and untracked phase evidence.

Last verified: 2026-08-18 America/Santiago — Phase 571.

## Phase 572 — correccion del ultimo issue y smoke de video

La referencia de Phase 562 no era el ultimo issue. La consulta read-only de
GitHub confirmo que el ultimo evento es `#534`, con URL
`https://www.instagram.com/reel/DcJZR2RR88m/`; el run `32091946775` termino
cancelado durante `render flyer` y no publico `onedrive:MAK/eventos/issue-534`.
El handoff anterior habia dejado `#533` como si fuera el ultimo y eso llevo a
probar el video equivocado.

Se recupero el input correcto con el downloader existente, sin login:
`/tmp/rd-issue-534-real-20260818/input_ig.mp4`. La descarga devolvio
`media_type=video`, H.264, 960x718, 24 fps, 384 frames y 16 segundos.

Smoke foreground ejecutado, solo frame central:

```text
python3 tools/render_video_sequence_mak.py \
  --video /tmp/rd-issue-534-real-20260818/input_ig.mp4 \
  --blend /home/mak/RD/AUTOMATIZACION/RD.blend \
  --out-dir /tmp/rd-issue-534-real-render-current-20260818 \
  --frame-start 192 --frame-end 192 --min-size 20000
```

Codigo 0; `RENDER_OK`; salida
`/tmp/rd-issue-534-real-render-current-20260818/frame_0192.png`,
1080x1920, Cycles 128 samples, GPU CUDA GTX 1650. Manifest: `cover_center`,
fuente 1.337047, ventana 0.734976, `crop_axis=lateral`, centrado, sin
deformacion y sin barras negras. No se modifico ni guardo `RD.blend`.

## Next concrete action

Esperar confirmacion visual del usuario antes de iniciar los 384 frames del
issue `#534`. Si se confirma, ejecutar la misma ruta con
`--frame-start 1 --frame-end 384`, conservando el manifest y la fuente local;
si no se confirma, detenerse y corregir solo el encuadre solicitado.

Last verified: 2026-08-18 America/Santiago — Phase 572.

## Phase 573 — preservacion de issue 534 y preview glass-fitwidth

Se corrigio una ambiguedad del handoff anterior: el issue #534 no es el
video del issue #533 usado en la prueba previa. El input correcto de #534 es
`https://www.instagram.com/reel/DcJZR2RR88m/`, H.264 960x718, 24 fps, 384
frames. Para impedir que el runner vuelva a eliminar la unica copia
temporal, se preservo el archivo en:

`/home/mak/curatoria_inbox/flujo_events/issue-534/input_ig.mp4`

y en `onedrive:MAK/eventos/issue-534/input_ig.mp4`, con SHA-256
`24b78be534b7f0bea276d1604b83acf757e98df6b1902f738c91eecc788a7d55`.
Tambien se guardo `media.json` junto al input en ambos destinos.

Se renderizo unicamente el frame 288/384 con `RD.blend`, Cycles 128, CUDA
GTX 1650; codigo 0, sin procesos Blender persistentes. El renderer activo
continua siendo `cover_center`. Sobre ese PNG se genero un preview temporal,
no una modificacion del `.blend`, con politica experimental
`glass_fitwidth`: fit lateral preservando proporcion, extension superior e
inferior desenfocada, fade vertical y lineas de vidrio:
`/tmp/rd-issue-534-glass-fitwidth-frame288-preview-20260818.png`.

La referencia visual aprobada por el usuario aun no es un contrato de
produccion: la politica `glass_fitwidth` y sus parametros deben formalizarse
solo despues de confirmacion visual. No iniciar los 384 frames hasta esa
confirmacion.

## Next concrete action

Confirmar con el usuario si el preview corresponde al tratamiento deseado.
Si se aprueba, convertir `glass_fitwidth` en una politica explicita y
reproducible del workflow, manteniendo `cover_center` como fallback; si no,
corregir solo los parametros del preview sin borrar el input preservado.

Last verified: 2026-08-18 America/Santiago — Phase 573.

## Historical checkpoint — Phase 539

Read this block first after compaction. It supersedes older provider and
service notes below.

- Current objective: keep the user-selected API/backend set installed,
  configured and foreground-tested without exposing secrets or performing
  uncontrolled external writes.
- Physical authority remains `/home/mak/*`; `/home/mak/flujo` is the authoring
  baseline; `/home/mak/WIN` and protected databases remain evidence.
- Verified on 2026-08-17: selected Research env keys for Ollama, Groq and
  Firecrawl; also MAK hub `127.0.0.1:8900`, SearXNG `127.0.0.1:8888`,
  Crawl4AI with Chromium, GitHub read API, public Instagram metadata, Google
  Drive and OneDrive rclone remotes. Watsonx and Tavily remain valid in the
  protected legacy env. NVIDIA and two Gemini keys passed read-only catalog
  probes but remain outside the active MAK research roster.
- Installed change: `pyproject.toml` now declares the reproducible optional
  extra `.[research]` with `crawl4ai>=0.9.2,<1.0`; project `.venv` has it and
  `pip check` is clean. Existing SearXNG container `searxng` is running on
  localhost with Docker restart policy `unless-stopped`.
- Cerebras is configured but its account returned HTTP 402 `Payment Required`;
  Azure, Canva and ntfy are absent by deliberate user selection. These are not
  installation failures and must not be represented as active providers.
- No API upload, notification publish, GitHub issue creation, or real EVENT
  replay was performed. The single user-facing MAK interface remains 8900.

## Historical checkpoint — Phase 495

Read this block first after compaction. Later phase notes are historical
evidence unless they are superseded by this checkpoint or a newer checkpoint.

- The active Git baseline is `/home/mak/flujo` on `main`; `origin/main` is
  identical. The topology-policy commit and this continuity record are
  identified in Phase 495 and by the current `HEAD`, respectively.
- The repository now has exactly one local branch and one remote branch:
  `main`. The only tag is the annotated `archive/house-history`, whose peeled
  commit is `b9f9a472deaeee6002a96fc8236d75b06bfe24c4`.
- The nine historical branch tips are preserved and reachable from that tag:
  `source/ddbase` `4b8453c`, `source/iskvw` `66b6b47`, `source/mak`
  `814b74c`, `source/mak-authority` `1d0b877`, `source/mak-linux` `5b7c54f`,
  `source/rd` `338ec99`, `source/rd-evidence` `0bb5abe`,
  `source/web-20260813` `69ec8c8` and `source/web-20260814` `1b86a58`.
  `work/mak-ownership` was already an ancestor of `main` before its ref was
  removed; no useful commit was lost.
- `.github/workflows/git-topology.yml` now guards the final topology. CI runs
  from `main`; Pages remains explicit-dispatch; domain separation is physical
  ownership and consumer paths, not permanent Git branches.
- This Git operation did not modify `WIN`, databases, generated portfolio
  data, runtime source, credentials or the dirty deploy worktree. The remaining
  broader house gates are recorded below and must not be confused with branch
  restructuring: local Node/Rollup build parity, RD field/live mutation and
  external-provider authority, and physical cleanup decisions.

## Historical continuity before Phase 495

- Latest continuation: Phases 347–359 verified the asset index/duplicate,
  SVG, ZIP export, intake guards, bilingual parser, JSON schema, job
  lifecycle, project activation, render catalog/config and rescale consumers.
  These checks used temporary roots or read-only canonical files; no render
  engine, external provider, live mutator or real config rewrite was run.
- Phase 361 removed the discarded `n8n-local` path from six active
  Research/platform credential consumers. The mode-600 n8n environment files
  remain protected evidence; `/home/mak/research/research.env` is now the
  active owner path. No provider or service was started.
- Phases 363–369 verified the remaining declared projection families with
  local owner/parity/import gates; wrappers were retained where intentional.
- Phase 376 passed core health, doctor, dependencies, SQLite, cron and active
  source AST. Seven malformed generated scripts under `/home/mak/codex/piezas`
  remain a protected classified exception.
- Phases 377–380 quarantined those seven malformed generated outputs and the
  unreferenced destructive sync repairer; post-quarantine health/AST/SQLite
  checks remain green.
- Phase 381 consolidated the 13-objective current state. Local work is green;
  RD field authority/data quality, one live mutator decision, optional
  external edges, path-specific cleanup review and user-directed Git remain
  explicit gates. Evidence: `context/PHASE381_FINAL_OBJECTIVE_STATE.md/.csv`.
- Phase 382 triaged the remaining root-level files. The two dangerous
  installers were already reversibly quarantined in Phase 339; root Python
  and shell utilities parse successfully and no new move was justified.
  Evidence: `context/PHASE382_ROOT_SURFACE_TRIAGE.md/.csv`.
- Phase 383 audited `flujo-deploy` and `/home/mak/bin/mak_sync_safe.py` as a
  separate deploy owner. The mutator parses but remains gated; active and
  WIN sync implementations differ and were not merged or executed.
  Evidence: `context/PHASE383_DEPLOY_OWNER_MUTATOR_GATE.md`.
- Phase 384 classified model/search configuration, old Blender and Python
  environments by metadata and bounded references. No candidate met the
  confirmed-junk threshold and no external process was started.
  Evidence: `context/PHASE384_EXTERNAL_SURFACE_CLASSIFICATION.md`.
- Phase 385 ran the final local guard: `pip check=0`, AST `443/443`, cron
  `0`, matching processes `0`, active `.pyc` `0`, and `rd_datos.db` intact
  with all four tables empty. Evidence: `context/PHASE385_FINAL_LOCAL_SAFETY_GUARD.md`.
- Phase 386 produced the visual owner architecture and operating rules for
  active, protected, historical, external, gated and excluded surfaces.
  Evidence: `context/PHASE386_VISUAL_ARCHITECTURE_OWNER_CLOSEOUT.md`.
- Phase 387 audited all 13 requirements against their actual proof scope;
  completion is intentionally not claimed for field data, live mutations,
  external edges, physical duplicate fusion or Git operations.
  Evidence: `context/PHASE387_REQUIREMENT_EVIDENCE_AUDIT.md/.csv`.
- Phase 388 resolved the four historical Platform runtime-only rows: Research
  and Vigia own the active paths; `agente_real.py` and `panel_directivo.py`
  remain reversible quarantine evidence.
  Evidence: `context/PHASE388_RUNTIME_ONLY_PLATFORM_AUDIT.md`.
- Phase 389 repaired stale non-serve command references in `cli.py` and the
  dashboard. The current venv passed version, health, formats, jobs, lists
  and RD help checks in foreground.
  Evidence: `context/PHASE389_NONSERVE_COMMAND_CONTRACT_REPAIR.md/.csv`.
- Phase 390 refreshed the complete 13-objective matrix after the runtime and
  command audits; it preserves every scope-specific open gate.
  Evidence: `context/PHASE390_CURRENT_13_OBJECTIVE_MATRIX.md/.csv`.
- Phase 391 refreshed base/optional dependency ownership against the current
  FLUJO venv. Base imports and `pip check` pass; optional/provider/GPU/build
  packages remain slice-gated and no requirements file changed.
  Evidence: `context/PHASE391_DEPENDENCY_SLICES_REFRESH.md`.
- Phase 392 compared the exact duplicate Curatoria candidate family. The
  FLUJO docs path is the active proposal consumer; the Curatoria copy remains
  preserved generated evidence, with no unsafe move or symlink.
  Evidence: `context/PHASE392_CURATORIA_DOCUMENT_DUPLICATE_GATE.md`.
- Phase 393 verified the EVENTO issue/URL bridge owner and runtime projection
  statically. GitHub, rclone, Blender/Ollama, issue-close and state writes
  remain visible external boundaries; no replay or cron was run.
  Evidence: `context/PHASE393_EVENTO_BRIDGE_STATIC_OWNER_GATE.md`.
- Phase 394 refreshed the objective matrix after the duplicate and EVENTO
  gates. Local results are current; human data, live/external execution and
  Git remain explicit open boundaries.
  Evidence: `context/PHASE394_CURRENT_OBJECTIVE_MATRIX.md/.csv`.
- Phase 395 recomputed and ran the conservative safe suite: 68 files/485
  test items passed with exit 0. The 177-file risk surface remains excluded
  by design and is not counted as complete coverage.
  Evidence: `context/PHASE395_SAFE_LOCAL_TEST_SUITE.md/.csv`.
- Phase 396 promoted two mocked/temporary test files for the EVENTOS/bridge
  boundary: 6 tests passed with exit 0; no external or durable state ran.
  Evidence: `context/PHASE396_PROMOTED_EVENTOS_BRIDGE_FIXTURES.md`.
- Phase 397 promoted `test_reception.py`: 2 mocked IMAP fixture tests passed
  with exit 0; no mailbox or durable state was touched.
  Evidence: `context/PHASE397_PROMOTED_RECEPTION_FIXTURE.md`.
- Phase 398 promoted `test_mak_hub_eventos.py`: 15 temporary/monkeypatched
  hub EVENTOS fixture tests passed with exit 0; no live hub or HTTP ran.
  Evidence: `context/PHASE398_PROMOTED_HUB_EVENTOS_FIXTURES.md`.
- Phase 399 promoted `test_cron_nocturno.py`: 13 isolated temporary cleanup
  fixtures passed with exit 0; the real scheduler and MAK files were untouched.
  Evidence: `context/PHASE399_PROMOTED_CRON_FIXTURES.md`.
- Phase 400 refreshed coverage and physical invariants: safe suite 68/485,
  promoted groups 36/36, AST 550/550, pip 0, cron 0, processes 0, pyc 0,
  and `rd_datos.db` intact/empty.
  Evidence: `context/PHASE400_COVERAGE_AND_PHYSICAL_GUARD.md/.csv`.
- Phase 401 promoted four deterministic contract groups: 19 tests passed
  with environment/temporary/pure fixtures; IMAP, OSC, Blender, GPU and
  network surfaces were not executed.
  Evidence: `context/PHASE401_DETERMINISTIC_CONTRACT_FIXTURES.md`.
- Phase 402 refreshed the 13-objective matrix after Phases 395–401. The safe
  suite remains 68 files/485 cases and promoted deterministic groups total
  55 cases. Local proof advanced; RD field authority, live mutations,
  external/provider edges, remaining risk tests and Git remain open.
  Evidence: `context/PHASE402_CURRENT_13_OBJECTIVE_MATRIX.md/.csv`.
- Phase 403 promoted `test_cli_v035.py`: 2/2 isolated CLI fixture tests passed
  with `PYTHONDONTWRITEBYTECODE=1`; only a pytest temporary workspace was
  written. A separate pre-existing `/home/mak/src/ml-mobileclip` surface has
  18 `.pyc` files; they remain preserved pending owner/residue proof.
  Evidence: `context/PHASE403_PROMOTED_CLI_V035_FIXTURE.md`.
- Phase 404 refreshed the current 13-objective matrix. The safe suite remains
  68 files/485 cases and promoted deterministic groups total 57 cases. The
  remaining excluded tests have no second isolated candidate under the AST,
  import, call and write-set gate; live/external/authority boundaries remain
  open. Evidence: `context/PHASE404_CURRENT_13_OBJECTIVE_MATRIX.md/.csv`.
- Phase 405 reconciled the physical `/home/mak/*` surfaces with the owner,
  cleanup and branch plan. It defines canonical, projection, protected,
  historical, gated, excluded and optional surfaces without moving or
  deleting anything. Evidence:
  `context/PHASE405_OWNER_CLEANUP_BRANCH_HANDOFF.md`.
- Phase 406 closed the RD catalog fusion: active `flujo/data/rd.db` and the
  state snapshot have identical normalized schemas and rows in 20 tables /
  7,587 rows. The Windows catalog snapshot and temporary integration check
  match as well; the 12-table/113-row `mak_rd.db` is an older incomplete
  artifact. The active database is newer (`schema_version 37`), so it was
  retained; historical copies remain preserved evidence. `rd_datos.db` was
  not merged. Evidence: `context/PHASE406_RD_DB_FUSION_CLOSURE.md/.csv`.
- Phase 407 re-parsed the current hub POST dispatcher and found all 16 literal
  routes. The existing matrix is complete; routes are separated into
  transient/read, local output, job/automation and asset/datadrop write sets.
  No POST was sent. Evidence: `context/PHASE407_RD_MUTATION_STATIC_AUDIT.md/.csv`.
- Phase 408 confirmed the portfolio web owner: `flujo/tools/portfolio`,
  `flujo/web`, `flujo/iskvw` and the read-only `/api/portafolio` path are the
  canonical active surface. `flujo-deploy` and `vibecodeine` portfolio tools
  are exact projections. The dedicated branch `codex/portfolio/web` was added
  to the proposal; media remains protected and is not bulk-copied. Evidence:
  `context/PHASE408_PORTFOLIO_WEB_OWNER_GATE.md`.
- Phase 409 researched the three relevant branch models using primary GitHub,
  GitLab and Trunk-Based Development documentation. It supersedes the old
  sequential branch-chain proposal with one protected `main`, short-lived
  topic branches merged directly to `main`, and only an optional temporary
  `release/vX.Y`. Evidence: `context/PHASE409_GIT_STRATEGY_RESEARCH.md`.
- Phase 410 audited the portfolio publishing connection read-only. The active
  workflow `/home/mak/flujo/.github/workflows/publicar_iskvw.yml` publishes the
  generated `iskvw/` site through GitHub Pages actions, only by manual
  `workflow_dispatch`; it generates `_sitio/CNAME` from repository variable
  `PUBLIC_DOMAIN`, defaulting to `iskvw.cl`. Its deployment copy is byte-identical
  in `flujo-deploy`. No operational Cloudflare/Workers/Pages configuration was
  found locally, and read-only DNS lookups for `iskvw.cl` returned no answers;
  this does not prove the external Cloudflare dashboard state. No hosting,
  domain or source was changed. Evidence:
  `context/PHASE410_PORTFOLIO_HOSTING_CONNECTION_AUDIT.md`.
- Phase 411 confirmed that `VENUE` is a cross-domain entity: RD catalog rows
  live in canonical `data/rd.db`, while VJ technical records live in
  `data/venues/*.json`, `knowledge/venues/*.yaml` and the venue skin/tools.
  `rd_datos.db` is separate, empty privacy/field state and is not the venue
  owner. The safe merge is a logical `venue_id` crosswalk with provenance,
  confidence and public/private projection, not a blind physical database
  merge. No database or venue file changed. Evidence:
  `context/PHASE411_RD_VENUE_CROSS_DOMAIN_GATE.md`.
- Phase 412 built a read-only venue crosswalk from the active RD catalog,
  technical JSON/YAML records, schema and venue skin. It found 3 canonical RD
  venue IDs, 8 producer relations, 7 event rows and 7 unresolved/raw event
  venue names; none was auto-merged by name. No database, venue record or
  portfolio surface changed. Evidence:
  `context/PHASE412_VENUE_CROSSWALK.md`.
- Phase 413 recorded the user's cross-domain product vision and verified the
  SCD venue proof slice: technical JSON, geometry generator, 3D skin, smoke
  test, schema and portfolio catalogue. The strategic units are venue-3D,
  Curatoria indexing/proposals, RD-VJ layout/rider and safe portfolio cases;
  they share IDs/provenance but not one undifferentiated database. No runtime,
  data, provider or Git mutation occurred. Evidence:
  `context/PHASE413_CROSS_DOMAIN_SERVICE_ARCHITECTURE.md`.
- Phase 414 found the theater seating primitive the user identified:
  `projects/plano/referencia_plano_teatro.py`. It is the interactive SCD v3.4
  model with radial rows, butacas, aisles, balcony and PNG/PDF/SVG plus
  Blender-outline exports. `tools/venue_geometria_scd.py` is its headless
  derivative feeding the SCD JSON and venue skin. Canonical, deploy,
  vibecodeine and WIN copies are byte-identical; no GUI/export/data/source
  mutation occurred. Evidence:
  `context/PHASE414_THEATER_SEATING_PRIMITIVE_GATE.md`.
- Phase 415 traced the cultural genealogy from the artist's
  `projects/cultura/RAINSTORM_2026-07-10.md`: ASCII/Borradura, Tilde, Psicosis,
  Tapiz/Cauce and Precursor follow `dossier -> instrumento -> material ->
  pieza`. ASCII is documented as a Windows encoding scar that became an
  instrument and then an artwork; Tilde, Psicosis and Tapiz have distinct
  instruments; Precursor remains primarily a dossier/stub. No source, artwork,
  data or Git state changed. Evidence:
  `context/PHASE415_CULTURAL_GENEALOGY_MAP.md`.
- Phase 416 incorporated the user's clarification that Tilde is the source of
  the present language boundary: marks carry meaning, the ASCII/Windows scar
  motivated machine-safe English ASCII, and human-facing RD/Curatoria/Portfolio
  material remains correct Spanish UTF-8. `tools/idioma.py` and
  `validar_curaduria.py` make that boundary live. The crosswalk maps Tilde,
  Borradura, Tapiz/Cauce, Psicosis, Precursor, Curatoria and RD/VJ to current
  consumers and maturity. No source, data, artwork or Git state changed.
  Evidence: `context/PHASE416_CULTURE_TO_CURRENT_REPO_CROSSWALK.md`.
- Phase 417 began active Markdown consolidation. Seven `corpus_olvido/corpus.md`
  copies share one exact SHA-256 and are now represented by one active master
  pointer; raw copies remain. Three recovered `nombre-cauce.md` sessions were
  compared: two normalize equal and one differs by 546 diff lines. New masters
  separate operational context from cultural ideas:
  `context/MD_CONTEXT_MASTER.md` and `projects/cultura/MD_IDEAS_MASTER.md`.
  Ranks 21–30 of unique Markdown contents were recorded; vendor/dependency
  files are excluded from idea fusion. Evidence:
  `context/PHASE417_MD_CONSOLIDATION.md`.

- Identity: LUNA principal. No subagent is active.
- Physical authority: `/home/mak/*`; `/home/mak/flujo` is canonical authoring
  and integration; `/home/mak/WIN` is historical read-only; `RD`, media,
  databases, labs, recovery and credentials are protected.
- Stable verified slices: RD asset/index reconciliation, Research/Codex/
  Curatoria/platform projections, read-only hub/CLI/RD routes, empty field
  report, demo privacy ingest fixture, dependency matrix, architecture map,
  duplicate/tool role ledgers and confirmed-junk quarantine.
- Current cleanup: Phase 247 permanently removed the 92 quarantined
  `.DS_Store` files and seven confirmed shell-residue objects. Empty
  `/home/mak/curatoria_encolado` was
  moved reversibly to `context/quarantine/phase219_empty_staging/`; the
  confirmed empty `/home/mak/workspace` directory tree was moved reversibly to
  `context/quarantine/phase228_empty_workspace/`; nine malformed empty shell/
  path directories were moved reversibly to
  `context/quarantine/phase229_empty_shell_residue/`.
- Current open gates: date/required-field/privacy review and authority for the
  concrete RD field-testing candidate; live RD mutator
  authority; optional provider/GPU checks if required; historical
  quarantined `/home/mak/flujo/context/quarantine/phase305_orphan_optional_tools/panel_directivo.py` remains incomplete historical evidence; the
  legacy platform UI is reversibly quarantined with Phase 270 evidence; root
  installers, diagnostics and optional provider tools remain preserved and
  execution-gated; the Git branch proposal is ready and no branch operation
  has been authorized.
- Automation status: installed crontab has 0 active non-comment entries and 24
  paused entries; the `crontab.mak` file is only a manifest. The user-confirmed
  `EVENTO ...` issue/URL bridge remains classified as working but operationally
  paused; it was not called against the external provider. `n8n-local` and XIO
  remain excluded.
- Non-`serve` CLI status: version, health, RD read surfaces, jobs list/next,
  valid job status, knowledge list, datadrop list and render formats passed in
  the base venv; `job status` without its required path returned expected usage
  code 2. `src/flujo/cli.py` compiles. All 17 top-level/group `--help`
  dispatch checks also returned exit 0.
- RD database status: `/home/mak/flujo/data/rd.db` has 20 tables/7,587 rows
  and is the already-merged canonical catalog. The WIN and state `rd.db`
  copies have identical per-table content and integrity. The recoverable
  `/home/mak/flujo/data/rd.db.premerge-20260815` retains the older 12-table
  source. `/home/mak/flujo/data/rd_datos.db` has 4 schema tables/0 rows and
  remains a separate privacy store; it is not silently merged into the catalog.
- RD consumer map: six operational source files own or consume the databases;
  `rd.db` is rebuildable catalog state and `rd_datos.db` is accumulative
  privacy-first field state. The table schemas can coexist but their lifecycle
  boundaries differ; no silent physical merge is authorized by evidence.
- RD mutator surface: Phase 250 classifies all 16 hub POST paths. Temporary-root
  tests for symbol creation, datadrop upload,
  datadrop analysis and review-package generation returned exit 0; the prior
  logo fixture also passed. No live POST, job, asset, database or provider was
  touched.
- Active projection AST gate: the current broad active roots parse 550/550
  files; operational roots excluding generated Codex pieces parse 444/444.
  The old incomplete `panel_directivo.py` is absent from the active root and
  preserved in the Phase 305 quarantine; it was not reconstructed or promoted.
- Final local health matrix: 7/7 core imports, `pip check`, read-only CLI,
  SQLite integrity and physical invariants passed; cron has 0 active entries
  and six relevant user units are inactive.
- Objective reconciliation: the historical/catalog `rd.db` fusion is verified;
  the concrete RD field candidate passes a temporary strict-ingest dry-run but
  remains pending date/field/privacy review and authority; local
  read/ownership/cleanup slices are verified or classified, while live mutator
  authority and optional runtime promotion remain open; the incomplete panel
  is quarantined historical evidence rather than an active runtime.
  Objective 13 has a ready branch proposal;
  creating branches is a separate operation and is not needed to prove the
  proposal. Full completion is not claimed.
- Final surface disposition now maps canonical source, runtime projections,
  RD/media/data/evidence, external infrastructure, historical WIN, language
  surfaces and reversible quarantines to owner/consumer/language/platform and
  rollback. It aligns with the existing branch proposal; no Git operation was
  performed.
- Platform tool ledger: 56 shared direct files were compared locally; 36 are
  exact projections and 20 are divergent variants. Thirty-two active source or
  test files consume the canonical `cultura.mak_plataforma` package. The safe
  fusion is one owner plus retained runtime paths; no files moved.
- Document duplicate disposition: a bounded scan covered 4,143 small
  text/metadata files, yielding 99 exact-hash groups/334 paths. Corpus captures,
  dated reports, source/runtime projections and generated outputs were
  classified by provenance; no document was removed.
- Divergent Platform gate: the 20 variants comprise 17 Python files (all AST
  pass), 2 non-empty shell wrappers and 1 non-empty text data contract. Runtime
  entrypoints delegate or remain required by paused manifests; none qualified
  for quarantine.
- Phase 251 active documentation/test gate: `/home/mak/flujo/MAPA.md` and
  `/home/mak/flujo/CAPACIDADES.md` were adopted individually from WIN and
  corrected to remove stale SSH instructions; WIN remains untouched. The
  missing active `RELEVO_MAK.md` was not fabricated because the box-level
  projection lives at `/home/mak/plataforma/`. The targeted 28-test contract
  set and the conservative 754-test/93-file safe suite both passed. Evidence:
  `context/PHASE251_ACTIVE_DOCS_SAFE_SUITE.md`.
- Phase 252 static risk inventory: the remaining 177 test files were not
  executed as a batch because they mention process/service, network/provider,
  media/GPU or external integration surfaces. All 177 parse successfully;
  2,164 test-function declarations remain for per-file promotion triage.
  Evidence: `context/PHASE252_EXCLUDED_TEST_RISK_INVENTORY.md`.
- Phase 253 RD fixture gate: `test_rd_database.py`, `test_rd_datos.py`,
  `test_rd_db_logos.py` and `test_privacy.py` passed 62 tests using temporary
  fixtures. The live `rd_datos.db` hash remained
  `70feaf43b5269b6c0341d1ba3debdac60e40fb902cc4bedb41254fdc84d1f703` and
  `registros_testeo` remained at 0 rows. Evidence:
  `context/PHASE253_RD_DATA_FIXTURE_GATE.md`.
- Phase 254 hub command gate: `tests/test_hub_comandos.py` passed 13 bounded
  cases. The allow-list rejects unknown/free-form/destructive/unclassified
  commands; only version/invalid-argument fixtures reached the bounded CLI.
  The live `rd_datos.db` hash remained unchanged. Evidence:
  `context/PHASE254_HUB_COMMAND_GATE.md`.
- Phase 255 RD symbol fixture gate: the catalogue, symbol-save and image-tracer
  groups passed 28 tests using temporary roots only. No live POST, active
  catalogue, generated product, database or service changed. Evidence:
  `context/PHASE255_RD_SYMBOL_FIXTURE_GATE.md`.
- Phase 256 RD render fixture gate: format selection, config rescaling,
  Illustrator package preparation and SVG validation passed 33 tests with
  temporary output roots. No browser, service, provider or external delivery
  was used. Evidence: `context/PHASE256_RD_RENDER_FIXTURE_GATE.md`.
- Phase 257 RD catalogue/proposal fixture gate: catalogue reconciliation,
  proposal drafts, multiformat packages and price-safety checks passed 50
  tests using temporary outputs. No external delivery, provider or database
  mutation occurred. Evidence:
  `context/PHASE257_RD_CATALOGUE_FIXTURE_GATE.md`.
- Phase 258 Research/Codex contract gate: source/configuration-only contracts
  for formats, sandbox honesty, provider roster, prompts, source gates and
  MAPA coverage passed 81 tests. No provider or network call was made.
  Evidence: `context/PHASE258_RESEARCH_CODEX_CONTRACT_GATE.md`.
- Phase 259 local Research state gate: checkpoints/resume, pause behavior,
  routing, simulated provider-health state, process-guard discovery and
  interface configuration passed 58 fixture-only tests. No worker, provider,
  service or live queue was used. Evidence:
  `context/PHASE259_LOCAL_RESEARCH_STATE_GATE.md`.
- Phase 260 Curatoria/platform fixture gate: watchdog/panel decision logic,
  opportunity ledger, review gates, metrics, queue classification, energy
  parsing and MAK batch surfaces passed 71 tests with faked external calls
  and temporary state. No watchdog, worker, GitHub command, GPU probe or
  service was launched. Evidence:
  `context/PHASE260_CURATORIA_PLATFORM_FIXTURE_GATE.md`.
- Phase 261 organs/GPU fixture gate: organ inventory and portable activity/GPU
  state checks passed 5 tests with the worker stubbed and state redirected to
  temporary paths. Thread/worker/provider tests remain separately gated.
  Evidence: `context/PHASE261_ORGANS_GPU_FIXTURE_GATE.md`.
- Phase 262 objective matrix refresh: after the bounded fixture gates, RD
  assets, local commands, Research/Codex, Curatoria/platform and organ/GPU
  slices are green in isolation. The 13-objective matrix still keeps field
  ingest, live mutators, automation re-enable, optional runtime, incomplete
  panel and Git operations gated. Physical recheck found cron active count 0,
  no persistent FLUJO/hub/worker/n8n/ollama process, `rd.db` integrity `ok`,
  and empty byte-stable `rd_datos.db`. Evidence:
  `context/PHASE262_OBJECTIVE_MATRIX_REFRESH.md`.
- Phase 263 residual risk triage: after removing 39 already-promoted files,
  138 excluded tests remain. AST refinement classifies 76 as executable-risk
  and 62 as keyword/fixture candidates; all parse. The first analyzer attempt
  failed internally with exit 1 and no side effect; the corrected run exited 0.
  Evidence: `context/PHASE263_RESIDUAL_RISK_TRIAGE.md`.
- Phase 264 airdrop/CLI contract gate: signed airdrop, CLI smoke, atomic state,
  shared file contract, micelio snapshot and flyer index fixtures passed 68
  tests. The autonomy group with its historical SSH contract was not run.
  No active source, database, job, service, cron, Git, SSH or external state
  changed. Evidence: `context/PHASE264_AIRDROP_CLI_CONTRACT_GATE.md`.
- Phase 265 local ISKVW/Research fixture gate: filters, cartography, model
  debate contracts, micelio snapshot delivery, extraction, reports, intake,
  editor, latido, benchmark and watchdog checks passed 105 tests. No live URL,
  Git operation, watchdog, worker, database or provider ran. Evidence:
  `context/PHASE265_LOCAL_ISKVW_RESEARCH_FIXTURE_GATE.md`.
- Phase 266 disabled Claude workflow gate: the missing active
  `.github/workflows/claude.yml` was restored as a manual-only, permanently
  disabled contract with no permissions or external triggers. The historical
  writable WIN workflow was not promoted. The 16-file candidate group then
  passed 188 tests. Evidence:
  `context/PHASE266_DISABLED_CLAUDE_WORKFLOW_GATE.md`.
- Phase 267 CLI manifest reconciliation: the stale generated command contracts
  were regenerated from the current CLI after removing the obsolete SSH
  requirement from the generator. `MAPA.md` and `context/comandos.json` now
  report 95 commands and `--check` exits 0. The focused ISKVW/validator group
  passed 110 tests. Evidence:
  `context/PHASE267_CLI_MANIFEST_RECONCILIATION.md`.
- Phase 268 residual boundary: after 91 promoted test files, 89 remain outside
  the local fixture gate: 63 executable-risk and 26 explicitly bounded by
  SSH/provider, worker/thread, destructive cron, Git, IMAP/IG, show/render or
  XIO surfaces. No AST parse failures. Local safe candidates are exhausted;
  work now moves to physical consumer/owner architecture. Evidence:
  `context/PHASE268_RESIDUAL_BOUNDARY_AND_ARCHITECTURE_HANDOFF.md`.
- Phase 269 physical architecture gap list: current `/home/mak/*` was compared
  to the frozen architecture. `searxng`, `model-config`, deploy tooling,
  installers, diagnostics, host directories and root narratives now have
  explicit external/history/output dispositions; no move, delete, Git or
  service action occurred. Evidence:
  `context/PHASE269_PHYSICAL_ARCHITECTURE_GAP_LIST.md`.
- Phase 270 legacy platform UI quarantine: `/home/mak/plataforma/interfaz.py`
  had no active launcher/consumer and was moved reversibly to
  `context/quarantine/phase270_platform_ui/interfaz.py`, preserving mode,
  size and SHA-256. The active Research owner/projection stayed in place;
  AST, reference, unit-status and 8 focused tests passed. No service ran.
  Evidence: `context/PHASE270_PLATFORM_UI_QUARANTINE.md`.
- Objective reconciliation update: objectives 9 and 10 now have consumer/
  provenance dispositions (`CLASSIFIED_BY_PROVENANCE_AND_CONSUMER` and
  `OWNER_FUSED_WITH_RUNTIME_PROJECTIONS`). The remaining material gates are
  field-candidate review/authority, live mutator authority, optional runtime
  requirements, incomplete historical-panel review and explicit Git operation.
  A physical DB choice is only relevant if a separate future migration of the
  privacy store is explicitly requested.
- Canonical Platform import gate: 17 canonical implementations imported in
  isolated subprocesses with bytecode disabled; all returned exit 0. No
  provider, network, scheduler, job, upload or durable-write path executed.
- Dependency slice closure: Phase 243 scanned 118 slice files with 0 parse
  failures; all nine declared base distributions are present in the canonical
  venv and `pip check` returned exit 0. Optional render/desktop/build,
  provider, GPU and local-source paths are classified without promotion to
  the base runtime.
- Objective closeout: Phase 244 reconciles all 13 requested objectives. Local
  verification and confirmed-junk cleanup are complete within scope; field
  candidate authority, live mutator authority, optional runtime promotion,
  incomplete historical-panel review and explicit Git operation remain open by
  evidence, not omission.
- RD historical fusion closure: Phase 245 verified identical per-table content
  across active, WIN and state `rd.db` sources. The pre-merge backup remains
  recoverable; `rd_datos.db` remains separate by privacy/lifecycle contract.
- RD field candidate audit: Phase 246 found and hashed the preserved `Testeo
  2025` source/derived evidence (42 events, 1,831 rows, 5,394 observations).
  Its status is pending human review; no rows were copied into `rd_datos.db`.
- RD field dry-run: Phase 249 joined the candidate through the actual
  `rd-datos ingest` contract in a temporary DB: 762 rows passed, 19 were
  rejected by privacy scan and 4,613 failed form validation; the live DB hash
  stayed unchanged. The route itself returned exit 0 after a corrected harness.
- RD POST route matrix: Phase 250 parsed `hub.py` and classified all 16 POST
  paths by transient/read/asset/job/command/automation write set. No live POST
  was sent; prior temporary mutator fixtures remain the validation evidence.
- Confirmed junk removal: Phase 247 removed exactly 92 `.DS_Store` files and
  seven previously quarantined shell-residue objects after count/type
  preflight. Other quarantines containing evidence, code or products remain.
- Cleanup gate: `/home/mak/workspace` had 0 files and 0 symlinks and no bounded
  active consumer, so it was quarantined without evidence loss. The legacy
  `/home/mak/plataforma/interfaz.py` remains at its original path because its
  historical tests/import references and incomplete runtime require review.
- Cleanup gate: the nine Phase 229 paths contained 0 files and 0 symlinks and
  had no bounded active consumer. They are quarantined, not deleted. Named
  storage paths such as `/home/mak/tmp`, `GoogleDrive`, user folders, `WIN`
  incoming and disconnected `OneDrive` were deliberately preserved.
- Safety: `mak-research`, `mak-research-queue`, `mak-codex`, `mak-hub`,
  `mak-interfaz` and `mak-xio` reported inactive; no scheduler, worker,
  provider or deploy sync was started.
- Next concrete action: keep the local audit at this safe boundary and monitor
  only for the concrete RD candidate review/authority, live mutator authority,
  optional runtime promotion or explicit Git operation. Preserve the current
  handoff and rollback maps; do not invent field records, enable providers,
  merge privacy stores or create branches.
- Post-cleanup health: Phase 248 selected RD/no-automerge tests passed; health,
  RD packs, job list/next, knowledge, datadrop, SQLite integrity and process/
  cron safety all passed. No package was installed.
- Latest evidence: `context/PHASE250_RD_POST_ROUTE_MATRIX.md` and `.csv`;
  field dry-run: `context/PHASE249_RD_FIELD_DRYRUN_GATE.md` and `.csv`;
  health: `context/PHASE248_POST_CLEANUP_HEALTH_GATE.md` and `.csv`;
  cleanup: `context/PHASE247_CONFIRMED_JUNK_REMOVAL.md` and `.csv`;
  field candidate: `context/PHASE246_RD_FIELD_CANDIDATE_AUDIT.md` and `.csv`;
  RD fusion: `context/PHASE245_RD_HISTORICAL_DB_FUSION_CLOSURE.md` and
  `.csv`; objective matrix: `context/PHASE244_OBJECTIVE_CLOSEOUT_MATRIX.md`
  and `.csv`;
  dependency closure: `context/PHASE243_DEPENDENCY_SLICE_CLOSURE.md` and
  `.csv`; canonical Platform import gate:
  `context/PHASE242_PLATFORM_CANONICAL_IMPORT_GATE.md` and `.csv`; objective
  update: `context/PHASE241_OBJECTIVE_RECONCILIATION_UPDATE.md`
  and `.csv`;
  AST gate: `context/PHASE234_ACTIVE_PROJECTION_AST_GATE.md` and `.csv`;
  mutator gate: `context/PHASE233_RD_MUTATOR_FIXTURE_GATE.md` and `.csv`;
  database consumer map: `context/PHASE232_RD_DATABASE_CONSUMER_MAP.md` and
  `.csv`;
  merge probe: `context/PHASE231_RD_DATABASE_MERGE_PROBE.md` and `.csv`;
  CLI dispatch gate: `context/PHASE230_NON_SERVE_CLI_DISPATCH_GATE.md` and
  `.csv`; residue quarantine: `context/PHASE229_EMPTY_SHELL_RESIDUE_QUARANTINE.md`
  and `.csv`;
  CLI gate: `context/PHASE227_NON_SERVE_CLI_GATE.md` and `.csv`;
  automation audit: `context/PHASE226_AUTOMATION_SURFACE_AUDIT.md` and `.csv`;
  prior final gates: `context/PHASE224_FINAL_OPEN_GATES.md` and `.csv`;
  checkpoint repair: `context/PHASE225_HANDOFF_CHECKPOINT_REPAIR.md`.

## Historical phase archive — preserved evidence

**Historical snapshot (not current authority):** Phase 77 was the completed
slice at the time of that note. Any older phase summaries below are historical
evidence; they do not reopen XIO,
hardware, ADB or n8n-local. Resume from the `Next concrete action` section
near the end of this file.

- Identity: LUNA principal. No delegated agent is active. `LUNA-28`,
  `LUNA-29` and `LUNA-30` completed their disjoint Phase 27 slices and were
  closed; `LUNA-27` completed Phase 25 and is also closed.
- Historical phase snapshot: Phase 48 was complete. Phase 40 was deferred at a safe boundary. Phase 28 repaired the RD packs
  dependency declaration, Phase 29 completed the RD quote/plano contract,
  Phase 30 completed the RD database read-only contract, Phase 31 completed
  the ISKVW SVG visualizer/index read-only contract, Phase 32 completed the
  ISKVW portfolio catalog read-only contract and Phase 33 completed the ISKVW
  show-kit/setlist read-only contract, Phase 34 classified the MAK status
  fallback without network, Phase 35 classified the automation queue as an
  external-provider boundary, Phase 36 integrated the local jobs listing
  read-only contract, Phase 37 integrated the dashboard summary and Phase 38
  integrated the RD event-presets reader and Phase 39 integrated the hub's
  read-only role catalog with a LUNA policy boundary and Phase 40 classified
  the empty RD field-data source without mutation. Phase 26 Windows
  evidence and the 15-record
  anchor metadata report are received.
- Correct scope: migrate and adapt WIN's `flujo serve`/`flujo app` hub and its
  RD/ISKVW/CULTURA tools. Do not reengineer MAK, do not treat all WIN paths as
  legacy, and do not use the MAK-only semantic triage as the migration list.
- Provenance fact: `/home/mak/WIN/flujo` contains FLUJO plus the MAK genealogy
  (`cultura/mak_*`, `tools/mak*`, RD, ISKVW and the hub) in one archive tree.
- Date rule: WIN birth time and ctime mostly record the 2026-08-13 archive
  import. `mtime` is only an auxiliary signal; join it to content, route,
  consumer and Git history before ranking a candidate.
- Last delivered artifacts:
  `context/PHASE23_SCOPE_CORRECTION_AND_MAK_ORIGIN.md`,
  `context/PHASE24_WIN_FLUJO_MAK_GENEALOGY_CROSSWALK.md` and `.csv`,
  `context/PHASE25_WIN_HUB_ROUTE_CROSSWALK.md` and `.csv`,
  `tools/probe_flujo_windows.ps1`,
  `context/PHASE26_WINDOWS_PROBE_REVIEW.md`,
  `tools/probe_flujo_windows_metadata.ps1`,
  `/home/mak/curatoria_inbox/flujo_windows_probe/anchors-metadata.json`,
  `context/PHASE27_ROUTE_DEPENDENCY_MATRIX.md` and `.csv`,
  `context/PHASE27_MAK_CONSUMER_SURFACE.md` and `.csv`,
  `context/PHASE27_RUNTIME_COMPATIBILITY_GATE.md` and `.csv`,
  `context/PHASE29_RD_QUOTE_PLANO_STATIC_GATE.md` and `.csv`,
  `context/PHASE30_RD_DATABASE_READONLY_GATE.md` and `.csv`,
  `context/PHASE31_ISKVW_SVG_VISUALIZER_READONLY_GATE.md` and `.csv`,
  `context/PHASE32_ISKVW_PORTFOLIO_READONLY_GATE.md` and `.csv`,
  `context/PHASE33_ISKVW_SHOW_KIT_READONLY_GATE.md` and `.csv`,
  `context/PHASE34_MAK_STATUS_NO_NETWORK_GATE.md` and `.csv`,
  `context/PHASE35_AUTOMATION_QUEUE_EXTERNAL_GATE.md` and `.csv`.
- Delegation status: no active agent. The ceiling remains three LUNA agents;
  the heartbeat interval is twelve minutes. Open a new agent only for a new,
  disjoint large slice.
- Key result: `WIN/flujo/src/flujo/serve/server.py` equals the MAK copy by
  SHA; `cli.py`, `web/hub.py`, `context/flujo_hub.html` and `abrir_hub.bat`
  differ and are the migration anchors. The RD packs read contract already
  exists in MAK and passed foreground validation; `Pillow>=12.3.0` is now
  declared in the base dependency set because `web.hub` imports it directly.
  Phase 30 proved `/api/rd-db` with HTTP 200 and `writes_detected=0`; its
  canonical JSON/YAML counts match the read-only `rd.db` projection. The
  zero-byte `rd_datos.db` remains explicitly deferred and was not seeded.
- Phase 31 proved both SVG listing GET routes with HTTP 200 and equal payloads;
  MAK has 11 SVG assets in two groups, and the WIN/MAK paths and normalized
  content match. Raw hash differences are CRLF versus LF line endings only.
- Phase 32 proved `/api/portafolio` with HTTP 200 and 10 allowlisted projects;
  MAK/WIN catalog IDs and the existing prototype's embedded IDs match. Eight
  local routes exist and two entries are explicit external URLs; the temporary
  server closed with `writes_detected=0`.
- Phase 33 proved `/api/show-kit` with HTTP 200 and a local read-only contract:
  21 topics, 21 cues, 1 record group and 2,384 valid JSONL rows. The six
  read-surface files match WIN after line-ending normalization; hardware/OSC
  modules were not executed and the temporary server closed with
  `writes_detected=0`.
- Phase 34 proved the `/api/mak` local fallback without network: with
  `FLUJO_MAK_URL` unset, direct and temporary-HTTP GET checks returned
  `disponible=false`, `configurado=false`, a truthful missing-variable error
  and local tandas data. External `urlopen` calls were `0` and
  `writes_detected=0`; the configured `/api/organismo` branch remains deferred.
- Phase 35 classified `/api/automatizaciones` as external-provider runtime:
  physical `/usr/bin/gh` would call `gh issue list` for GitHub issues. The real
  provider was not contacted. A no-provider fixture verified the fallback with
  HTTP 200, zero subprocess calls and `writes_detected=0`; the local
  `run_pending_flyers` mutating runner was not executed.
- Phase 36 integrated `/api/list-jobs` as a local read-only consumer. AST and
  imports passed; the direct reader and one temporary GET-only request both
  returned HTTP 200 with 8 jobs, equal payloads and the expected six item
  keys. Eight common WIN/MAK briefs were equal after line-ending
  normalization; MAK's `2026-07-05_contraportadas` is MAK-only. The job-tree
  snapshot reported `writes_detected=false`; no lifecycle mutator ran.
- Phase 37 integrated `/api/dashboard-summary` as a local read-only consumer.
  AST/import passed; scoring found 19 items from jobs, flyers and vector
  configs and returned 10 alta, 7 media and 2 baja. Direct and temporary
  HTTP payloads were equal at HTTP 200; protected input snapshots reported
  `writes_detected=false`.
- Phase 38 integrated `/api/event-presets` as a local RD read-only consumer.
  AST/import, the three-preset/14-key schema, deep-copy boundary and
  normalized WIN/MAK source parity passed. The temporary GET returned HTTP
  200 with the same payload as the direct reader and
  `writes_detected=false`.
- Phase 39 integrated `/api/agents-roles` as a read-only UI contract. Five
  unique ASCII role IDs, five-key role schemas, `{task}` templates and
  bounded WIN/MAK role-ID parity passed. The temporary GET returned HTTP 200
  with an equal payload and `writes_detected=false`; no dispatch occurred.
  These generic app roles remain separate from the active LUNA-only policy.
- Phase 40 classified `/api/rd-datos-summary` as
  `DEFERRED_EMPTY_DATA_SOURCE`. A MAK-wide exact-name scan found only the
  zero-byte active `/home/mak/flujo/data/rd_datos.db`; SQLite read-only mode
  saw zero objects. Historical `rd.db` copies in `WIN/flujo/data` and
  `state/windows-director-20260813/rd` were recorded as evidence, not used as
  field data. The separate `/home/mak/flujo/data/rd_datos_demo/` CSVs are
  explicitly synthetic, and `/home/mak/flujo/data/rd_fuentes/` is controlled
  research evidence pending human review; neither is an ingestion source. A
  guarded direct/HTTP check returned HTTP 200 without calling the normal
  schema-creating connector; `writes_detected=false`.
- Phase 41 validated `/api/status` with AST/import and temporary HTTP: HTTP
  200, version `0.56.1`, root `/home/mak/flujo`, SVG/proyectos present and
  `writes_detected=false`. The separate `/home/mak/RD` surface was bounded at
  1,743 files/192 directories and classified as creative asset evidence, not
  a hub data source or a copy candidate.
- Phase 42 validated the CULTURA `projects/tapiz/` static consumer. MAK/WIN
  had 66/66 bounded relative paths in common; representative README and SVG
  GETs returned HTTP 200, while non-allowlisted `projects/cultura/README.md`
  returned HTTP 404. No artwork or README was regenerated, copied or changed.
- Phase 43 classified the broader `projects/cultura/` tree as
  `EVIDENCE_ONLY_NO_ACTIVE_HUB_CONSUMER`: 55 bounded MAK files, 56 WIN files,
  54 common paths, one local pyc-only difference and two WIN-only documents.
  No active hub route consumes `projects/cultura/`; no tree merge or cleanup
  was performed.
- Phase 44 validated both MAK `flujo serve --help` entrypoints with exit 0;
  no service started. `serve/server.py` is normalized-identical to WIN,
  `abrir_hub.bat` is normalized-identical, and `cli.py` remains an explicit
  open migration anchor because its content differs without a proven behavior
  mismatch.
- Phase 45 ran the real MAK process temporarily with
  `flujo serve --no-abrir --host 127.0.0.1 --port <ephemeral>`. `/api/ping`
  and `/api/status` both returned HTTP 200/version 0.56.1; the process was
  explicitly terminated, no forced kill was needed, `process_alive=false` and
  `writes_detected=false`.
- Phase 46 ran one real temporary hub process and a safe GET matrix of 12
  endpoints: ping/status, RD packs/database, SVG aliases, portfolio, show-kit,
  jobs, dashboard, event presets and roles. All returned HTTP 200; explicit
  external/mutating/empty-data boundaries were skipped; shutdown was clean and
  `writes_detected=false`.
- Phase 47 resolved the open `cli.py` migration anchor for the actual entrypoint:
  MAK/WIN `serve` and `app_alias` ASTs are equal. Full-file CLI differences
  remain non-serve evidence only.
- Phase 48 consolidated the evidence: local read-only RD/ISKVW/CULTURA hub
  surface is integrated; only explicit external, mutating, empty-data and
  non-serve evidence boundaries remain open.
- Do not resume: `discernment.py` adoption, MAK-only candidate promotion,
  `panel_directivo.py`, `repair_mak_sync.py`, SSH, services, cron, workers,
  SVG/artwork regeneration or any Git mutation. The isolated
  `discernment.py` test is secondary evidence only.
- Next concrete action: reconcile one explicit remaining boundary only when
  its authority exists: populate/approve real RD field data, authorize the
  external automation/MAK provider, or name a concrete non-serve CLI
  mismatch. Until then preserve the proven local runtime and do not invent a
  migration by copying assets, demo data or historical trees.

## Current objective

Direct the migration of the former Windows FLUJO APP into the Debian 12 MAK
environment. The historical application ran with `flujo serve` and exposed a
hub divided into `RD`, `ISKVW` and `CULTURA`. MAK is the existing Linux house
with working departments, bugs and improvements; it is not the object of a
fresh reengineering. Preserve MAK while mapping each WIN tool to a concrete
MAK destination, adapting only what the migration requires and proving it
with the real hub/consumer.

## General plan checkpoint

- Covered: WIN evidence/genealogy, hub route crosswalk, RD/ISKVW/CULTURA
  read-only consumers, real `flujo serve` process, safe GET matrix and
  serve/app CLI contract.
- Remaining migration boundaries: real RD field data, external automation and
  optional external MAK provider, mutating job/upload/render/hardware paths,
  and any non-serve CLI command with a concrete mismatch.
- MAK-wide house work still pending: crosswalk `/home/mak/plataforma`,
  `research`, `codex`, `curatoria`, `post` and other
  department roots by active consumer, owner, dependency, language and
  platform; classify obsolete, Windows-only, evidence-only and adoptable
  slices without treating the result as a deletion list.
- Final architecture work still pending: propose the new Git branch system
  after physical consumers are known; branches must represent live domains and
  integration slices, not historical folder duplication.
- Operating rule: every new physical search starts at `/home/mak/*`, then
  narrows to the consumer and uses `/home/mak/WIN` for provenance comparison.
- User clarification applied: `/home/mak/n8n-local` and `/home/mak/xio_puente`
  are excluded from the migration scope. Their historical reports remain
  evidence only; do not install ADB, probe hardware or treat either surface as
  a pending migration candidate.

## Physical authority and migration status

- Inventory rule: every physical search starts at `/home/mak/*` to cover the
  entire active MAK house; only then narrow to `/home/mak/flujo`, another MAK
  department or `/home/mak/WIN` according to the discovered consumer and
  provenance.
- `/home/mak/*`: active MAK operational surface and migration target.
- `/home/mak/flujo`: authoring and integration baseline.
- `/home/mak/WIN`: Windows FLUJO APP source/evidence to migrate; not runtime.
- Git is historical orientation only; physical WIN/MAK files decide reality.

## Scope correction and MAK origin

- The user corrected the working premise: the main goal is WIN → MAK
  migration, not repairing or consolidating MAK's existing departments.
- The former WIN application used `flujo serve`; its hub exposed tools grouped
  under `RD`, `ISKVW` and `CULTURA`. The Linux MAK environment was created to
  carry that work forward.
- `context/PHASE23_SCOPE_CORRECTION_AND_MAK_ORIGIN.md` records the evidence
  from `historia git.odt`. Its key historical marker is commit
  `6a2b147097e169d42fdc3defe9f0e160de52cc41` on 2026-07-17:
  `feat(cultura): cierre organismo MAK -- WIN LLM provider, hub DOM+SVG,
  emisor de eventos (#48)`.
- The immediate follow-up history includes a MAK Linux bridge, a live MAK
  generative system and `v0.55.0` with `workship Win-MAK probado`. This is the
  origin of the migration line, not evidence that every current MAK module
  must be rebuilt.
- The prior MAK semantic triage and `discernment.py` fixture test remain
  secondary evidence. They do not define the migration target and must not
  displace the WIN hub crosswalk.
- `WIN/flujo` literally contains both the former FLUJO APP and the later MAK
  genealogy: `src/flujo`, `context/flujo_hub.html`, `cultura/mak_codex`,
  `mak_conductor`, `mak_curatoria`, `mak_lenguaje`, `mak_plataforma`,
  `mak_post`, `mak_research`, `mak_vigia` and `mak_xio_puente`, plus `tools/mak`
  and `tools/mak_ops`. Therefore `WIN` is not one legacy generation; it is a
  chronological archive of the system's evolution.
- The WIN archive has 53,103 files. Files retain varied `mtime` values, but
  53,095 filesystem birth dates and 53,092 `ctime` dates are 2026-08-13, the
  import date. Birth/ctime cannot rank original age; mtime is a useful signal
  only when connected to content, route and Git history.

## Language coverage protocol

- Every inventory or discrepancy search must cover Spanish and English names,
  accented and unaccented forms, case variants, localized directory names,
  aliases/slugs and human labels as well as exact machine identifiers.
- Subagents must search by function, owner and consumer in addition to literal
  path/text matches; a monolingual search is insufficient evidence.
- Each subagent report must record its search vocabulary and residual
  false-negative risk. Machine-facing keys remain English ASCII; human-facing
  RD/Portfolio text may retain correct Spanish diacritics.

## Completed work with command and result

- Read `agents.md` and this handoff before acting.
- Delegation ledger: `LUNA-01` (`agent_id`
  `01a0025e-a3db-7ed3-92fe-635a6d4f2746`, platform nickname Lagrange) completed
  phase 1 inventory and was closed; `LUNA-02` (`agent_id`
  `01a00265-243f-7a63-9723-91354b38003e`, platform nickname Dalton) completed
  phase 2 reconciliation and was closed. Platform nicknames are not work
  identities and must not be reused as labels.
- `LUNA-03` (`agent_id` `01a0026a-f2b0-7031-95c9-12d66921504c`, platform
  nickname Parfit) completed phase 3 classification and was closed. It was
  the sole subagent for that phase and deployed no descendants.
- `LUNA-04` (`agent_id` `01a00271-6ef6-76a1-a9fb-8616e29857e5`, platform
  nickname Hilbert) completed phase 4 entrypoint verification and was closed.
  It was the sole subagent for that phase and deployed no descendants.
- `LUNA-05` (`agent_id` `01a00274-05da-7981-a2bf-243ec5e2587e`, platform
  nickname Pauli) completed phase 5's read-only mirror probe and was closed.
  It was the sole subagent for that phase and deployed no descendants.
- `LUNA-06` (`agent_id` `01a00277-8ded-7541-b495-0244605c615a`, platform
  nickname Hegel) completed phase 6 local comparison and was closed. It was
  the sole subagent for that phase and deployed no descendants.
- `LUNA-07` (`agent_id` `01a00279-a17b-73d1-8091-9c72eeecf7ad`, platform
  nickname Gauss) completed phase 7 static audit and was closed. It was the
  sole subagent for that phase and deployed no descendants.
- `LUNA-08` (`agent_id` `01a0027c-c938-7c00-a67a-aea2173bd354`, platform
  nickname Ohm) completed phase 8 mapping `mak_plataforma` with bilingual
  coverage and was closed; it was the sole subagent for that phase and
  deployed no descendants.
- `LUNA-09` (`agent_id` `01a00281-d4c2-7762-a961-9f32310b5266`, platform
  nickname Archimedes) completed phase 9 and was closed. It was the sole
  subagent for that phase, deployed no descendants, and produced no_change.
- Compared exactly 35 manifest routes from the final, postarchive, and update
- LUNA-10 (agent_id 01a00291-3b5a-71a1-87f8-2e2e5d817ca5, platform nickname
  Confucius) is triaging the platform department semantically.
- LUNA-11 (agent_id 01a00291-3ae2-78f2-bfb3-df73013055ea, platform nickname
  Plato) is triaging research, curatoria and codex departments.
- LUNA-12 (agent_id 01a00291-3a70-7cb3-b497-e6d5021d8664, platform nickname
  Pasteur) is triaging operational declarations and entrypoints.
- LUNA-13 (agent_id 01a00291-3a3c-74d2-b64e-7a88b47a1ad7, platform nickname
  Ptolemy) is triaging tools, flujo, tests and RD interfaces.
- LUNA-14 (agent_id 01a00291-3bc5-7e43-8a0b-b99aad708a18, platform nickname
  Dirac) is triaging historical and redundancy surfaces. These five are the
  only active subagents and may not deploy descendants.
- LUNA-15 (agent_id 01a00298-5c8c-7b20-9dbf-baab8a983164, platform nickname
  Aristotle) completed phase 16 and was closed. Its ledger/visual_index
  review ended no_change because of write boundaries and unresolved visual
  dependencies.
- LUNA-16 (agent_id 01a002a2-98ff-79f1-8667-cdd5b40604d7, platform nickname
  Hume) completed platform candidate history tracing and was closed.
- LUNA-17 (agent_id 01a002a2-9988-7983-b19f-60bbe7a185c5, platform nickname
  Epicurus) completed providers/tandas history tracing and was closed.
- LUNA-18 (agent_id 01a002a2-9934-7672-a015-93a5b1676963, platform nickname
  Goodall) completed ledger/visual_index history tracing and was closed.
- LUNA-19 (agent_id 01a002a2-9a19-7071-b66e-b7fa8a86a1f4, platform nickname
  Halley) completed flujo core history tracing and was closed.
- LUNA-20 (agent_id 01a002a2-9ad0-7600-8b61-aa359422af7d, platform nickname
  Boyle) completed residual candidate history tracing and was closed.
- LUNA-21 (agent_id 01a002a8-7334-7941-a107-a0ae01cfb822, platform nickname
  Carver) completed phase 19 and was closed. Flujo core is an adoptable
  candidate, but autonomy and pytest remain deferred and wheel is absent.
- LUNA-22 (agent_id 01a002ac-c1d4-7ab3-9c66-33eb4638238b, platform nickname
  Aquinas) completed phase 20 and was closed. Its mak_plataforma core
  contract review covered 18 paths: 2 `ADOPTABLE_CANDIDATE` paths
  (`discernment.py` source/runtime) and 16 `DEFER`; it deployed no
  descendants and modified no source, runtime or data.
- LUNA-25 is the principal LUNA scope-correction pass. It searched the
  strategic ODT history and documented the WIN FLUJO APP → MAK origin in
  `context/PHASE23_SCOPE_CORRECTION_AND_MAK_ORIGIN.md`; no source or runtime
  change was made.
- LUNA-27 (agent id `01a002c5-a041-7c41-9ae6-0c768e11cad6`, platform nickname
  Dewey) completed Phase 25 and was closed. It created only the bounded WIN
  hub-route crosswalk MD/CSV and did not delegate.
- LUNA-28 (agent id `01a002e6-d4f8-71a2-8343-015e2185386d`, platform nickname
  Lovelace) completed the route/consumer/dependency matrix and was closed; it
  created only `PHASE27_ROUTE_DEPENDENCY_MATRIX.md/.csv`.
- LUNA-29 (agent id `01a002e8-dcf8-7610-abcb-0089e6f25ebe`, platform nickname
  McClintock) completed the physical MAK consumer/destination surface and was
  closed; it created only `PHASE27_MAK_CONSUMER_SURFACE.md/.csv`.
- LUNA-30 (agent id `01a002e8-dd2b-7883-8d42-5e2b4a3b709d`, platform nickname
  Maxwell) completed the Windows-to-MAK runtime/dependency compatibility gate
  and was closed; it created only `PHASE27_RUNTIME_COMPATIBILITY_GATE.md/.csv`.
- Phase 27 selected the read-only RD packs/tariff contract as the smallest
  complete vertical slice: `flujo` CLI → `web.hub` → hub HTML →
  `/api/rd-packs` → `data/rd_packs.json`. Route, UI, data, imports and AST
  passed foreground validation with exit 0.
- Phase 28 repaired the dependency declaration gap only: `Pillow>=12.3.0`
  was added to base `pyproject.toml` and `requirements.txt`, and removed from
  duplicate `render`/`desktop-extras` declarations. No source, runtime, WIN,
  data or artwork files were changed.
- Phase 29 validated the complete RD quote/plano contract. Static fixtures and
  a temporary localhost HTTP server passed with exit 0 for service data, quote
  render and plano render; the server shut down and tracked files had
  `writes_detected=0`. No source adapter was needed because MAK already held
  the complete consumer chain.
- Phase 30 validated the RD database read-only contract. AST/import/schema,
  canonical JSON/YAML parsing and SQLite `mode=ro` projection counts passed
  with exit 0. A temporary in-process GET-only server returned HTTP 200 for
  `/api/rd-db`, then shut down cleanly with `writes_detected=0`. No source or
  data adapter was needed. `/api/rd-db/logo` and uploads were not called;
  `data/rd_datos.db` was observed as zero-byte/empty and left untouched.
- Phase 31 validated the ISKVW SVG visualizer/index read-only contract. Hub
  and preview modules parsed/imported, the UI/allowlist and in-memory preview
  fixture passed, and both `/api/list-svg-works` and `/api/svg-index` returned
  HTTP 200 with equal 11-item payloads. The temporary server shut down with
  `writes_detected=0`; no SVG was copied, regenerated or edited.
- Phase 32 validated the ISKVW portfolio read-only contract. Hub/catalog
  schema, MAK/WIN IDs, eight local route targets, two explicit external URLs
  and the prototype's embedded 10 IDs passed. A temporary GET-only server
  returned HTTP 200 and shut down with `writes_detected=0`; generators and
  publication were not run.
- Phase 33 validated the ISKVW show-kit/setlist read-only contract. Four
  modules parsed, 21 setlist lines, 21 cues, 2,384 valid JSONL records and the
  normalized six-file WIN/MAK read surface passed. `/api/show-kit` returned
  HTTP 200 and the temporary server shut down with `writes_detected=0`; no
  hardware, OSC or relay path was executed.
- Phase 34 validated the optional MAK status fallback. With
  `FLUJO_MAK_URL` unset, direct and temporary localhost GET checks returned
  the unconfigured read-only response without calling external `urlopen`; the
  server shut down with `writes_detected=0`. The configured external branch is
  explicitly deferred.
- Phase 35 validated only the automation fallback. Static evidence showed the
  real `/api/automatizaciones` path invokes external `/usr/bin/gh` for GitHub
  issues, so it was not called. A no-provider temporary GET returned HTTP 200
  with the unavailable fallback, zero subprocess calls and
  `writes_detected=0`; job preparation/activation remains deferred.
  JSON files against `/home/mak/flujo`; no recursive large-tree scan.
- Created `context/PHASE2_FLUJO_RECONCILIATION.md` and `.csv`; CSV validation
  exit 0, 35 rows, 9 columns, 14 content_changed, 21 metadata_only.
- All 35 target routes exist; target hashes are recorded. No code or WIN files
  were modified.
- `python3 -m flujo --help`: exit 1, module unavailable without installation.
  `PYTHONPATH=/home/mak/flujo/src python3 -m flujo --help`: exit 0; CLI help
  observed for v0.56.1.
- Historical `context/LAST_HANDOFF.md` conflict classified as provenance-only:
  final/postarchive/update manifests record successive hashes, but all five
  declared historical destination paths are absent. Current MAK handoff is
  the only live operational handoff; no restore/copy/merge performed.
- Created `context/PHASE3_CHANGED_ROUTES_REVIEW.md` and `.csv`; 14/14
  `content_changed` routes classified, all decisions `no_change`.
- The candidate `README.md -> tools/update_readme_svg.py ->
  arte-ascii-readme.svg -> tests/test_readme_svg.py` was tested without
  promotion. Generator output caused a structural regression, so the SVG was
  restored from `/home/mak/flujo-deploy/arte-ascii-readme.svg` with verified
  SHA-256 `2bda5d95340a56cad6ac8c2450aa33a127966a1db358497a5b4374863546f9db`.
- Focused structural assertions passed after restore. `pytest` is unavailable
  (`command -v pytest` exit 127; `python3 -m pytest` exit 1); no dependency
  was installed.
- Phase 4 entrypoint verification completed by `LUNA-04`: the venv launcher
  imports `/home/mak/flujo/src/flujo/__init__.py`; `flujo --help` and
  `flujo version` passed with exit 0; `/usr/bin/python3 -m flujo --help`
  failed with exit 1 and `No module named flujo`. CSV validation passed with
  Python stdlib: 5 rows, 8 columns. No code or WIN files were modified.
- `rmlint`, `jdupes`, `diffoscope` and `meld`: `command -v` reported all four
  unavailable; no installation or deletion script was attempted.
- `check_mak_mirror.py` used its built-in remote default `mak@192.168.50.2`;
  SSH exit 255 (`Host key verification failed`) made all 68 reported
  `MISMATCH` rows non-evidence. They mean remote hashes were unavailable, not
  that 68 real differences were measured. No SSH configuration was changed.
- Phase 6 local comparison: 15 routes, 8 same, 4 different and 3 WIN-only;
  all `no_change`. The material divergence is `repair_mak_sync.py`; its WIN
  variant is historical and neither variant has an authorized integration
  contract.
- Phase 7 audit: both `repair_mak_sync.py` variants pass AST, but the active
  variant can reset Git, rewrite cron, copy four live roots and use SSH; WIN
  uses a disposable worktree and provisions a WIN-only helper. No owner,
  consumer or authorized contract identified; decision `no_change`.
- Phase 8 local map: source has 60 files, runtime 133 and WIN 64; 60 common
  routes were compared. `PHASE8_MAK_PLATAFORMA_MAP.csv` validates with 21
  rows and 13 columns; all decisions are `no_change`. AST validation covered
  325 files, with the known `panel_directivo.py` SyntaxError at line 145.
  The real consumer `mak_conductor.handler_registry` imported 30 handlers;
  foreground help for `flujo`, `trabajo` and `ledger` passed. No source,
  runtime or WIN file was modified, and no service, cron, watchdog or worker
  was run.

## Semantic triage consolidation

- Phase 10 platform triage: 47 rows; 26 LIVE/ADOPTABLE, 5 BLOCKED,
  10 WINDOWS_LEGACY and 6 EVIDENCE_ONLY. No source/runtime/WIN changes.
- Phase 11 department triage: 40 rows; 29 BLOCKED, 6 WINDOWS_LEGACY,
  3 EVIDENCE_ONLY and 2 SUPERSEDED. AST covered 47 Python files with 0
  errors; no runtime execution or source changes.
- Phase 12 operational declaration triage: 38 rows; 15 BLOCKED, 7
  WINDOWS_LEGACY and 16 EVIDENCE_ONLY. No services, timers, cron,
  watchdogs or workers were started.
- Phase 13 tools/flujo/RD triage: 30 rows; 7 LIVE/ADOPTABLE, 6 BLOCKED,
  9 EVIDENCE_ONLY, 3 SUPERSEDED and 5 WINDOWS_LEGACY. AST covered 188
  files with 0 errors; foreground CLI and registry checks passed.
- Phase 14 historical/redundancy triage: 45 rows; 32 EVIDENCE_ONLY, 4
  WINDOWS_LEGACY, 4 OBSOLETE, 3 SUPERSEDED, 1 BLOCKED and 1 UNDEVELOPED.
  No historical files were moved, deleted or executed.
- Phase 15 consolidated the five reports into
  context/PHASE15_HOUSE_SEMANTIC_MATRIX.csv and .md: 200 rows, 14
  columns, 33 LIVE/ADOPTABLE candidates and 167 non-adoptable or blocked
  rows. Classification is normalized from status; no candidate is integrated.

## Candidate history consolidation

- Phase 17 traced all 33 LIVE/ADOPTABLE candidate rows through five LUNA
  reports. The reports contain 61 trace rows and 32 unique physical paths
  because source/runtime pairs and the duplicate ledger row are preserved.
- Phase 18 produced context/PHASE18_CANDIDATE_HISTORY_MATRIX.csv and .md:
  32 unique paths; 23 KEEP_CANDIDATE, 5 DEFER and 4 NO_CHANGE.
- The 4 NO_CHANGE paths are ledger.py and visual_index.py across source and
  runtime, honoring the Phase 16 write/dependency boundary.
- The 5 DEFER paths require fixtures, dependencies, lineage or owner
  clarification. No Git operation, source edit or runtime promotion occurred.
- History confidence is mixed. Runtime paths with an absent exact historical
  path remain physical candidates only; history does not prove obsolescence.

## Historical Git orientation

- Strategically read /home/mak/Descargas/historia git.odt without loading its
  full body into conversational context. It is valid JSON under schema
  git-history-mega-summary-v1, generated 2026-08-14T23:08:00Z, with SHA-256
  510ca28cb0bc1222a659b0077704344a77c8fa3438298a35f18b1e6f562e6a56.
- Its governing rule matches this handoff: Git explains historical intent and
  ref relationships; physical MAK/WIN files decide current reality. No Git
  state was modified.
- The document records 6 local refs, 12 remote refs, 403 decision events and
  450 retained path journeys. Shared tips are ref convergence, not proof of
  duplicate physical tools. The branch named mak is explicitly not the MAK
  Linux box.
- Future branch design is deferred until semantic house-ordering finishes.
  It must use verified responsibility and lifecycle, not historical branch
  names or department identity.

## Recent Git orientation authorized by the user

- The user expressly authorized a read-only review of the last 20 commits of
  local refs `mak` and `main`; this is recorded in
  `context/PHASE21_GIT_RECENT_20_REVIEW.md`.
- `main` tip is `032822b` (`chore: remove obsolete agent routes`) and `mak`
  tip is `814b74c` (`feat: reconcile local structure and mak research`).
  `main...mak` is `18 1` with merge-base `4b8453c`; no Git state changed.
- The recent history confirms `mak` as recovery/integration lineage and
  `main` as merge/promotion/pruning lineage. Neither ref is physical truth
  for `/home/mak` or `/home/mak/WIN`, and neither branch name identifies the
  Debian host or a current department.
- `eaa5b22` introduced the conductor shadow queue/services; `814b74c` added
  broad reconciliation/knowledge tooling; `9e9abb6` retired obsolete paths;
  `857ede5`, `a04093c` and `032822b` removed historical handoff/instruction/
  route material. These are historical signals only. Current local handoff
  and phase reports remain untracked working-tree evidence for this process.
- The future branch system remains deferred until physical house-ordering is
  complete; it must encode verified lifecycle and ownership, not reproduce
  historical refs.

## Open migration items

- Reframe the earlier MAK-only candidate matrix as secondary evidence. It is
  not the WIN migration backlog, and its 167 non-adoptable rows are not
  evidence that WIN tools are obsolete or should be deleted.
- The physical WIN → MAK crosswalk for `flujo app`/`flujo serve`, the hub and
  `RD`/`ISKVW`/`CULTURA` is complete in Phases 24–27. Use it as the route,
  consumer and dependency baseline; do not rebuild the archive inventory.
- Treat `WIN/flujo` as a genealogy, not a single legacy snapshot: separate
  pre-MAK FLUJO, MAK-era additions and later recovery/archive material before
  assigning a migration status.
- Preserve the existing MAK departments. A migration change requires a
  concrete WIN source, MAK destination, owner, hub consumer, dependency
  adaptation and bounded foreground verification.

- Phase 9 handler audit completed with no execution and no source/runtime/WIN
  changes. repo_delivery and issue_render were classified BLOCKED; WIN copies
  were classified WINDOWS_LEGACY; registry/catalog evidence was classified
  EVIDENCE_ONLY. PHASE9_HANDLER_DRY_RUN.csv validates with 9 rows and 13
  columns, all decision no_change. panel_directivo.py remains unchanged with
  SyntaxError at line 145.

- Strategic triage is mandatory before adoption: classify each candidate as
  LIVE/ADOPTABLE, SUPERSEDED, WINDOWS_LEGACY, OBSOLETE, UNDEVELOPED, BLOCKED
  or EVIDENCE_ONLY. A historical caller that no longer works on Debian 12 is
  not an integration candidate merely because its code is present.

- The 14 `content_changed` routes are classified and remain `no_change`.
- The SVG/tool/test slice is explicitly `no_change` because the SVG is an
  artwork; do not regenerate or overwrite it unless the user reopens that
  decision.
- The Phase 4 entrypoint slice is explicitly `no_change`: the declared
  `flujo = flujo.cli:app` contract reconciles with the active venv and source
  tree. Keep the system Python as contrast only.
- Phase 8 map is evidence-only and explicitly `no_change`; do not repair or
  promote `panel_directivo.py`, and do not let the old MAK-only handler
  candidate displace the active WIN hub migration sequence.
- `/home/mak/OneDrive` remains inaccessible; do not retry broadly.
- Phase 30 RD database read-only gate is integrated for productoras, venues,
  event metadata and logo existence. The field-data sibling is not integrated:
  `data/rd_datos.db` is zero-byte/empty, and calling its normal connector would
  create schema as a side effect. Keep ingestion deferred until a separate
  authorized privacy/rollback slice.
- Phase 31 ISKVW SVG visualizer/index is integrated read-only. The MAK allowlist
  and two API aliases enumerate the existing 11-item SVG root; artwork remains
  untouched and optional rasterizers remain outside scope.
- Phase 32 ISKVW portfolio catalog is integrated read-only. The real
  `tools/portfolio` catalog, hub allowlist and existing prototype passed; no
  generator or publication was run.
- Phase 33 ISKVW show-kit/setlist is integrated read-only. Local setlist,
  cues and historical records pass; hardware/OSC relay activation remains
  explicitly deferred.
- Phase 34 optional MAK status panel remains open. It must not contact an
  external MAK URL during this integration pass; the unconfigured fallback is
  integrated locally and the configured external runtime is deferred.
- Phase 35 local automation queue read-only surface remains open. It must keep
  file parsing separate from Gmail/provider calls, command execution, workers
  and queue mutation. The route was classified deferred because its source is
  GitHub via `gh`, not a local queue.
- Phase 36 local jobs listing is integrated read-only. Lifecycle actions
  (`create_job`, prepare, activate, render and workers) remain outside scope.
- Phase 37 dashboard summary is integrated read-only. It reads jobs, flyer
  manifests and vector configs; lifecycle and external-provider branches are
  outside this gate.
- Phase 38 event presets is integrated read-only; its configured event catalog
  is local and parity-matched to WIN.
- Phase 39 agent roles is integrated read-only with a policy boundary: generic
  UI role catalog only; no dispatch.
- Phase 40 RD field-data summary is safely deferred: the active field-data DB
  is empty and must remain untouched until a separately authorized
  privacy/rollback slice exists.
- Phase 41 status/RD surface is integrated read-only; `/home/mak/RD` remains
  asset evidence pending a named consumer and visual validation.
- Phase 42 CULTURA tapiz static allowlist is integrated read-only; the broader
  `projects/cultura/` tree remains intentionally non-public.
- Phase 43 broader CULTURA classification is complete as evidence-only; there
  is no active hub consumer to migrate.
- Phase 44 actual `flujo serve` entrypoint help/import is integrated; CLI
  behavioral difference remains open only as an evidence-backed anchor.
- Phase 45 real-process hub smoke is integrated; no persistent service remains.
- Phase 46 real-process safe GET matrix is integrated; all selected local
  readers work together.
- Phase 47 CLI `serve` content difference is resolved for the active entrypoint;
  non-serve differences remain evidence-only.
- Phase 48 consolidated status is complete; remaining work is boundary-gated
  by real data/provider authority or a concrete new consumer.

## Tool and dependency verification matrix

| Item | Source/path | Verification | Result |
|---|---|---|---|
| Phase 1 inventory document | `context/PHASE1_INVENTORY.md` | file/stat + required-section scan | PASS |
| Structured inventory | `context/PHASE1_INVENTORY.csv` | `python3` CSV reader | PASS; 144 rows |
| DuckDB store | `context/PHASE1_INVENTORY.duckdb` | import probe | UNAVAILABLE; `ModuleNotFoundError` |
| MAK/WIN physical roots | `/home/mak`, `/home/mak/WIN` | foreground metadata scan | PARTIAL; inventory checkpoint complete |
| Phase 2 reconciliation | `context/PHASE2_FLUJO_RECONCILIATION.csv` | Python stdlib CSV reader | PASS; 35 rows |
| Flujo module entrypoint | `PYTHONPATH=/home/mak/flujo/src python3 -m flujo --help` | foreground CLI help | PASS; exit 0 |
| Historical handoff provenance | `/home/mak/WIN/manifests/*handoff*` and declared destinations | metadata + path existence check | PASS; payloads absent, provenance-only disposition |
| Phase 3 changed-route review | `context/PHASE3_CHANGED_ROUTES_REVIEW.csv` | Python stdlib CSV reader | PASS; 14 rows; all no_change |
| SVG artwork preservation | `/home/mak/flujo/arte-ascii-readme.svg` | SHA-256 + structural assertions | PASS; restored; artwork preserved |
| SVG generator | `tools/update_readme_svg.py --check` | foreground check | FAIL/intentional; exit 2; artwork drift retained |
| Phase 4 venv entrypoint | `/home/mak/venvs/flujo/bin/flujo --help`; `version`; direct import | foreground CLI/import + stdlib CSV reader | PASS; exit 0 for venv checks; active import path verified; CSV 5 rows/8 columns |
| Phase 4 system contrast | `/usr/bin/python3 -m flujo --help` | foreground contrast | PASS as expected failure; exit 1; `No module named flujo` |
| Duplicate/diff utilities | `rmlint`, `jdupes`, `diffoscope`, `meld` | `command -v` | UNAVAILABLE; native fallback retained |
| Local mak_ops comparison | `context/PHASE6_LOCAL_MAK_OPS_COMPARE.csv` | stdlib pathlib/hashlib + AST/help | PASS; 15 routes; all no_change |
| Phase 8 mak_plataforma map | `context/PHASE8_MAK_PLATAFORMA_MAP.csv` | stdlib CSV reader + hash/AST/import records | PASS; 21 rows; 13 columns; all no_change; 1 known AST_FAIL |
| Phase 8 foreground CLI checks | `mak_conductor.handler_registry`, `flujo`, `trabajo`, `ledger` | import and `--help` in foreground | PASS; 30 handlers imported; no persistent execution |
| Phase 20 mak_plataforma core contract | `context/PHASE20_MAK_PLATAFORMA_CORE_CONTRACT_REVIEW.csv` | stdlib CSV/hash/AST + bounded `--help` | PASS; 18 rows; 13 columns; 2 candidate, 16 deferred |
| Phase 21 recent Git orientation | `context/PHASE21_GIT_RECENT_20_REVIEW.md` | read-only `git log`, divergence and graph checks | PASS; 20 commits per ref; no Git state change |
| Phase 23 scope correction | `context/PHASE23_SCOPE_CORRECTION_AND_MAK_ORIGIN.md` | strategic ODT parse + targeted MAK/WIN history search | PASS; migration scope corrected; no source/runtime change |
| Phase 24 WIN FLUJO/MAK genealogy crosswalk | `context/PHASE24_WIN_FLUJO_MAK_GENEALOGY_CROSSWALK.csv` | physical route scan + metadata/hash comparison | PASS; hub anchors and MAK-in-WIN roots recorded; no source/runtime change |
| Phase 25 WIN hub-route crosswalk | `context/PHASE25_WIN_HUB_ROUTE_CROSSWALK.md` and `.csv` | bilingual route scan + 10-anchor hashes/mtimes + stdlib CSV validation | PASS; MD identity exact, 18 rows/14 columns, 0 malformed rows; no source/runtime/WIN change |
| Phase 26 Windows environment probe | `tools/probe_flujo_windows.ps1` | embedded Python AST syntax check on MAK; received real Windows report | PASS; 4 usable reports; no package install/server/API calls |
| Phase 26 Windows probe review | `context/PHASE26_WINDOWS_PROBE_REVIEW.md` | received JSON/text reports + stdlib summary | PASS; 4 files usable; route-scoped filtering required; no source/runtime change |
| Phase 26 metadata probe | `tools/probe_flujo_windows_metadata.ps1` | bounded NTFS timestamps, direct child counts and SHA-256 | PASS; 15/15 records valid; no source/runtime change |
| Phase 27 route dependency matrix | `context/PHASE27_ROUTE_DEPENDENCY_MATRIX.md` and `.csv` | Windows runtime evidence + anchor metadata + bilingual route/consumer analysis | PASS; 25 rows/10 columns; no source/runtime/WIN change |
| Phase 27 MAK consumer surface | `context/PHASE27_MAK_CONSUMER_SURFACE.md` and `.csv` | physical MAK/WIN route-to-destination analysis | PASS; 17 routes/10 columns; no source/runtime/WIN change |
| Phase 27 runtime compatibility gate | `context/PHASE27_RUNTIME_COMPATIBILITY_GATE.md` and `.csv` | Windows reports + MAK venv/package/import checks | PASS; 25 rows/8 columns; no source/runtime/WIN change |
| Phase 28 RD packs declaration integration | `pyproject.toml`, `requirements.txt`, `/api/rd-packs` contract | venv imports + AST + JSON data + CLI help | PASS; exit 0; Pillow base declaration repaired; no route mutation |
| Phase 29 RD quote/plano contract | `context/PHASE29_RD_QUOTE_PLANO_STATIC_GATE.md` and `.csv` | AST + JSON fixtures + temporary localhost GET/POST contract | PASS; HTTP 200 for 3 routes; server shutdown and writes_detected=0 |
| Phase 30 RD database read-only contract | `context/PHASE30_RD_DATABASE_READONLY_GATE.md` and `.csv`; `src/flujo/rd/*`; `data/rd.db` | AST/import + canonical JSON/YAML + SQLite mode=ro + temporary GET-only `/api/rd-db` | PASS; HTTP 200; projection counts match; server shutdown and writes_detected=0; `rd_datos.db` deferred empty |
| Phase 31 ISKVW SVG visualizer/index | `context/PHASE31_ISKVW_SVG_VISUALIZER_READONLY_GATE.md` and `.csv`; `src/flujo/web/svg_preview.py`; `svg/` | AST/import + UI route/allowlist + in-memory SVG fixture + temporary GET-only listing aliases | PASS; HTTP 200 for both aliases; 11 items; equal payloads; server shutdown and writes_detected=0 |
| Phase 32 ISKVW portfolio catalog | `context/PHASE32_ISKVW_PORTFOLIO_READONLY_GATE.md` and `.csv`; `tools/portfolio/proyectos.json`; `docs/iskvw/prototipo.html` | AST/schema + MAK/WIN catalog IDs + hub allowlist + temporary GET-only `/api/portafolio` | PASS; HTTP 200; 10 projects; prototype present; server shutdown and writes_detected=0 |
| Phase 33 ISKVW show-kit/setlist | `context/PHASE33_ISKVW_SHOW_KIT_READONLY_GATE.md` and `.csv`; `xio/show_kit/` | AST + JSON/JSONL schema + WIN/MAK read-surface crosswalk + temporary GET-only `/api/show-kit` | PASS; HTTP 200; 21 topics/21 cues/2,384 valid rows; hardware excluded; server shutdown and writes_detected=0 |
| Phase 34 MAK status no-network fallback | `context/PHASE34_MAK_STATUS_NO_NETWORK_GATE.md` and `.csv`; `/api/mak`; `FLUJO_MAK_URL` unset | AST + direct no-urlopen fallback + temporary localhost GET-only check | PASS; HTTP 200; configured=false/disponible=false; network_contacted=0; server shutdown and writes_detected=0; external branch deferred |
| Phase 35 automation queue external gate | `context/PHASE35_AUTOMATION_QUEUE_EXTERNAL_GATE.md` and `.csv`; `/api/automatizaciones`; `src/flujo/automation.py` | AST + external `gh issue list` boundary + no-provider fallback fixture/temporary GET | DEFERRED_EXTERNAL_RUNTIME; real provider not contacted; fallback HTTP 200; subprocess=0; server shutdown and writes_detected=0 |
| Phase 36 local jobs list | `context/PHASE36_JOBS_LIST_READONLY_GATE.md` and `.csv`; `/api/list-jobs`; `src/flujo/jobs/*` | AST/import + direct list + WIN/MAK brief crosswalk + temporary GET-only | PASS; HTTP 200; 8 jobs; direct/http equal; 8 common briefs equal after line-ending normalization; writes_detected=false; lifecycle mutators excluded |
| Phase 37 dashboard summary | `context/PHASE37_DASHBOARD_SUMMARY_READONLY_GATE.md` and `.csv`; `/api/dashboard-summary`; `src/flujo/dashboard/scoring.py` | AST/import + direct scoring + temporary GET-only | PASS; HTTP 200; 19 items; 10 alta/7 media/2 baja; direct/http equal; writes_detected=false |
| Phase 38 RD event presets | `context/PHASE38_RD_EVENT_PRESETS_READONLY_GATE.md` and `.csv`; `/api/event-presets`; `src/flujo/eventos/presets.py` | AST/import + schema/deepcopy + WIN/MAK normalized source check + temporary GET-only | PASS; HTTP 200; 3 presets; 14-key schema; direct/http equal; source parity equal; writes_detected=false |
| Phase 39 hub agent roles | `context/PHASE39_HUB_AGENT_ROLES_READONLY_GATE.md` and `.csv`; `/api/agents-roles`; `HubRequestHandler._get_agents_roles` | AST/import + role schema + bounded WIN/MAK IDs + temporary GET-only | PASS_WITH_POLICY_BOUNDARY; HTTP 200; 5 roles; direct/http equal; dispatch=false; writes_detected=false |
| Phase 40 RD field-data boundary | `context/PHASE40_RD_FIELD_DATA_BOUNDARY.md` and `.csv`; `/api/rd-datos-summary`; `src/flujo/rd/informe.py` | MAK-wide exact DB-name scan + AST/import + SQLite mode=ro + guarded connector + temporary GET-only | DEFERRED_EMPTY_DATA_SOURCE; active `rd_datos.db` 0 bytes/0 objects; guarded HTTP 200; normal connector not called; writes_detected=false |
| Phase 41 status and RD asset surface | `context/PHASE41_STATUS_RD_SURFACE_GATE.md` and `.csv`; `/api/status`; `/home/mak/RD` | AST/import + status schema/direct check + temporary GET-only + bounded MAK-wide asset metadata | PASS_READ_ONLY; HTTP 200; version 0.56.1; 1743 RD files/192 dirs classified evidence; writes_detected=false |
| Phase 42 CULTURA tapiz static gate | `context/PHASE42_CULTURA_TAPIZ_STATIC_GATE.md` and `.csv`; `projects/tapiz/`; hub allowlist | AST/import + bounded MAK/WIN paths + temporary GET allowed/blocked checks | PASS_READ_ONLY; 66/66 paths common; README/SVG HTTP 200; broader `projects/cultura` HTTP 404; writes_detected=false |
| Phase 43 broader CULTURA boundary | `context/PHASE43_CULTURA_BOUNDARY_CLASSIFICATION.md` and `.csv`; `projects/cultura/` MAK/WIN | bounded MAK/WIN path crosswalk + bilingual source-reference search | EVIDENCE_ONLY_NO_ACTIVE_HUB_CONSUMER; 55 MAK files; 56 WIN files; 54 common; no active hub route; writes_detected=false |
| Phase 44 FLUJO serve entrypoint | `context/PHASE44_FLUJO_SERVE_ENTRYPOINT_GATE.md` and `.csv`; `src/flujo/cli.py`; `src/flujo/serve/server.py` | venv/module help + AST/import + bounded WIN entrypoint crosswalk | PASS_ENTRYPOINT_NO_SOURCE_EDIT; both help commands exit 0; server not started; server.py parity equal; cli.py open anchor |
| Phase 45 real FLUJO serve process | `context/PHASE45_FLUJO_SERVE_REAL_PROCESS_GATE.md` and `.csv`; `flujo serve` | temporary process + GET ping/status + explicit shutdown | PASS_TEMPORARY_PROCESS; both HTTP 200; version 0.56.1; process_alive=false; writes_detected=false |
| Phase 46 real hub safe GET matrix | `context/PHASE46_REAL_HUB_SAFE_GET_MATRIX.md` and `.csv`; real `flujo serve` | one temporary process + 12 safe GET endpoints + explicit shutdown | PASS_REAL_RUNTIME_MATRIX; all 12 HTTP 200; excluded external/mutating/empty-data routes; process_alive=false; writes_detected=false |
| Phase 47 CLI serve contract | `context/PHASE47_CLI_SERVE_CONTRACT_CROSSWALK.md` and `.csv`; MAK/WIN `cli.py` | bounded AST comparison of `serve` and `app_alias` | RESOLVED_NO_SERVE_MISMATCH; both ASTs equal; full-file non-serve difference retained; writes_detected=false |
| Phase 48 status and gaps ledger | `context/PHASE48_INTEGRATION_STATUS_AND_GAPS.md` and `.csv`; all completed gates | evidence consolidation and explicit boundary ledger | CONSOLIDATED_EVIDENCE; local safe GET surface integrated; deferred boundaries named; no source/runtime mutation |

## Conflicts and risks

- Duplicate-looking folders or tools may be parallel generations, wrappers,
  replacements or historical evidence. Do not merge or delete based only on
  names, paths, hashes or age; compare function, current consumer, owner,
  dependencies, platform contract and verification result.

- `/home/mak/OneDrive` is inaccessible.
- One duplicate path was caused by overlapping scan batches.
- Functional duplicates may exist; reconciliation evidence is not integration.
- Historical `LAST_HANDOFF.md` hashes differ across successive manifests, but
  the conflict is classified and has no available archive payload to merge.
- SVG generator drift is known and intentionally retained; the artwork must
  not be normalized as part of ordinary integration.
- Sensitive contents were excluded; only metadata was recorded for those paths.
- No permanent services, cron jobs or watchdogs were started.
- The remote mirror probe is blocked by SSH host-key verification and is not a
  valid mismatch result. Do not retry it or modify `known_hosts` automatically.
- `repair_mak_sync.py` may perform Git reset/checkout, copy and SSH actions;
  it is not to be executed until owner, consumer and dependency are explicit.
- Phase 7 is blocked only for promotion: exact recovery is an explicit owner,
  named consumer, dependency contract, approved target paths and a bounded
  dry-run procedure. Work may continue on unrelated local departments.
- `panel_directivo.py` has a known SyntaxError at line 145 in the Phase 8
  source/runtime map. It is historical/diagnostic evidence only until an
  owner, consumer and repair contract are identified; do not repair as part
  of the next dry-run.
- Recent Git pruning commits remove tracked handoff/instruction material while
  this live process keeps a local untracked handoff and phase reports. Do not
  clean or stage those artifacts automatically.
- The Phase 20 candidate `discernment.py` has a bounded Ollama boundary and
  no direct persistent-write pattern found, but endpoint/import/fixture and
  no-network behavior are still unverified. `ADOPTABLE_CANDIDATE` is not an
  adoption decision.
- `WIN` filesystem birth/ctime metadata mostly records the 2026-08-13 archive
  import, while mtime includes preserved and post-archive timestamps. Never
  sort WIN candidates by creation/ctime alone; use mtime only as one signal
  joined to the hub route, genealogy and Git history.
- `data/rd_datos.db` is physically present but zero bytes with no SQLite
  objects. `flujo.rd.datos.conectar()` creates/commits schema, so no field-data
  summary call belongs in a read-only database gate.
- The 11 SVG files under MAK and WIN have raw hash differences caused by
  CRLF/LF line endings; normalized content and relative paths match. Do not
  normalize the artwork as a side effect of migration.
- The portfolio catalog includes two explicit external URLs and an existing
  generated prototype. The read-only hub contract passes, but no external URL
  or portfolio generator was invoked; publication parity remains outside this
  phase.
- The show-kit records are historical evidence and local operational input;
  they do not prove current phone, OSC, Art-Net or venue hardware availability.
  Keep `artnet_relay.py`, `cue_engine.py`, `map_dref.py` and Windows launchers
  outside the Linux hub read-only path.
- `/api/mak` has a verified local fallback, but the configured branch calls
  another process at `FLUJO_MAK_URL/api/organismo`. It was not contacted and
  remains deferred external runtime; do not turn that into a network mismatch
  or retry it automatically.
- `/api/automatizaciones` is not backed by a local queue: it shells out to
  `/usr/bin/gh issue list` when available. GitHub/Gmail/provider access and the
  `run_pending_flyers` job mutator are intentionally deferred.
- Phase 49 completed the MAK-wide department orientation in
  `context/PHASE49_MAK_WIDE_DEPARTMENT_CROSSWALK.md/.csv`. It starts from
  `/home/mak/*`, records physical counts and WIN genealogy, and classifies
  `plataforma`, `research`, `codex` and `curatoria` as live MAK/evidence
  surfaces; `post` as a small candidate; and `n8n-local`/`xio_puente` as
  excluded by the user's clarification.
- Phase 50 completed the bounded POST candidate gate. AST and normalized WIN
  parity passed for `/home/mak/post/pipeline.py` and `__init__.py`; the
  producer registry and handler are real consumers in
  `/home/mak/flujo/cultura/mak_conductor`; the direct valid/rejected contract
  probe passed. The focused pytest command was attempted in the FLUJO venv
  but exited 1 because that venv has no `pytest`; no package was installed.
  XIO is excluded by the user; no hardware or ADB action is part of the
  remaining work.
- Phase 51 completed the remaining-root orientation in
  `context/PHASE51_REMAINING_MAK_ROOTS_CROSSWALK.md/.csv`. It classifies
  apps/labs/curatoria_inbox/RD as host or evidence surfaces, workspace as
  empty, src as an optional external-model tool, and lenguaje/vigia as the
  only small local candidates pending a named consumer. No scripts,
  dictionaries, models, cron entries or services were executed.
- Phase 52 verified the `/home/mak/lenguaje` consumer. The operational
  declaration `/home/mak/flujo/cultura/mak_plataforma/crontab.mak` references
  both its lexicon rebuild and ten-minute hook; historical hook logs show
  successful runs. Four Python modules are AST-valid and normalized-identical
  between `/home/mak/lenguaje` and `cultura/mak_lenguaje`; a read-only
  `medir_archivo()` probe exited 0 and shell syntax passed. Pytest is absent,
  so no package was installed. No cron, dictionary, source or data mutation
  occurred.
- Phase 53 verified the `/home/mak/vigia` consumer in read-only mode. Its
  hourly guard is declared in `crontab.mak`; runtime/source AST parses,
  behavior-only AST parity, shell syntax, both `fuentes.json` files and an
  offline HTML extraction/filter fixture passed. No watcher, network opener,
  notification, ledger enqueue or state write was executed. The focused
  pytest command is unavailable on MAK, so no package was installed.
- Phase 54 merged the enriched historical RD catalog into active
  `/home/mak/flujo/data/rd.db` additively. Backup:
  `/home/mak/flujo/data/rd.db.premerge-20260815`. The eight `testeo_*` tables
  and two `productora_eventos` columns were added with their rows/indexes;
  foreign-key check and `quick_check` passed, and a temporary real hub GET
  `/api/rd-db` returned HTTP 200 before clean shutdown. Both historical files
  remain unchanged. `rd_datos.db` remains zero-byte and separate.
- Phase 55 fixed and validated the RD field-data read contract in
  `src/flujo/rd/informe.py`: `resumen_json()` no longer calls the
  schema-creating connector and now uses SQLite `mode=ro`, returning false for
  absent/zero-byte files. The real empty database's size/mtime stayed unchanged;
  a temporary non-empty fixture returned correct counts with unchanged mtime.
  No real/demo/evidence rows were inserted.
- Phase 56 validated the first RD mutator slice, `/api/create-job-draft`,
  using a temporary job root and monkeypatched `create_job`. The fixture
  created the expected traceability files and was rolled back; the real jobs
  tree was untouched. Hub AST parsing passed. Remaining mutator subroutes are
  datadrop upload, auto-pending flyers, symbol persistence and real render
  output.
- Phase 57 fixed and validated `/api/datadrop-upload`: strict Base64 decoding
  now occurs before directory creation, preventing empty garbage directories
  on invalid uploads. Invalid and valid PNG fixtures passed in a temporary
  datadrops root; rollback passed; the real datadrops surface was untouched.
- Phase 58 validated symbol persistence with a temporary repository/catalog
  and validated the empty-input contract of `run_pending_flyers()` with a
  temporary base; both passed and no MAK job/data surface was touched. The
  remaining mutator routes are now explicitly bounded: logo upload, datadrop
  analyze/package/scan-incoming, disposable-job automation and production
  render/output policy.
- Phase 59 validated logo replacement and datadrop analysis with temporary
  productora/datadrop roots. Invalid logo input preserved the old bytes; valid
  replacement, source note and manifest reanalysis passed; both fixtures were
  rolled back. Real logos/datadrops were untouched. Remaining mutators are
  datadrop review-package/scan-incoming and disposable-job automation.
- Phase 60 completed the remaining RD mutator fixtures: review-package,
  scan-incoming and disposable-job automation dispatch all passed with
  rollback. Combined with Phases 29 and 56–59, the route-mutator surface is
  `FIXTURE_VERIFIED`; no production job, datadrop, logo, render or external
  provider was changed.
- Phase 61 recorded the user-confirmed automation chain
  `EVENTO ...` email -> issue -> URL -> processing as an accepted external
  contract; no provider was contacted. The non-serve CLI crosswalk passed
  help for all major groups, version/health/doctor exited 0, and
  `rd-db testeos` exposed the merged evidence counts without publication.
  Mutating CLI families are explicitly listed in
  `context/PHASE61_AUTOMATION_CLI_CROSSWALK.md` and were not run broadly.

Phase 96 is the current bounded slice. `autonomia run` completed a local
`rd_evidence` dry-run with exit 0, producing one temporary contract brief and
no provider calls, SSH, Ollama or ledger writes. The next concrete action is
remaining ownership merges and explicit external/mutator gates; the dry-run
must not be promoted to a published result.

Phase 95 is the current bounded slice. The RD mutator continuity check found
all expected hub/automation functions, no fixture residue in bounded real
roots, and no persistent hub/Blender/provider/automation process. RD remains
`FIXTURE_VERIFIED_WITH_ROLLBACK`; production execution is still deferred. The
next concrete action is the automation/provider boundary and remaining
ownership merges.

Phase 94 is the current bounded slice. All 13 explicitly mutating or
external-capable CLI entrypoints expose help with exit 0. Their write,
provider, render, Blender and SSH boundaries are visible, but no production
mutation ran. The next concrete action is review of fixture/rollback contracts
for those mutators, preserving explicit operational authority.

Phase 93 is the current bounded slice. `PHASE93_OBJECTIVE_CLOSEOUT_MATRIX.md`
and `.csv` reconcile all 13 objectives against current evidence. The objective
remains active: runtime is substantially verified, but field data, production
mutators, pytest/web dependencies, semantic ownership merges, path-level
cleanup and Git application are not falsely marked complete. The next
concrete action is explicit mutator/external-automation boundary review.

Phase 92 is the current bounded slice. A bounded AST hygiene scan found no new
unlabelled reader mutation after the index/datadrop fixes. Remaining matches
are explicitly named report/automation/lifecycle writers or in-memory JSON
serialization. The next concrete action is explicit mutator/automation
boundary review, while pytest recovery and external provider authority remain
separate gates.

Phase 91 is the current bounded slice. `flujo datadrop list` no longer creates
missing workspace/datadrops directories: `workspace_root` and
`datadrops_dir` now support explicit `create=False`, while scan/ingest/prepare
retain writer behavior. Empty-root and real-root foreground checks passed, and
the next concrete action is another list/status/read contract audit.

Phase 90 is the current bounded slice. The flyer index reader/writer boundary
was corrected: `flyer-list` and duplicate lookup now use SQLite `mode=ro`,
while only explicit rebuild/init paths write. Real `data/flujo.db` stayed at
20,480 bytes with unchanged mtime; the temporary rebuild/read fixture passed.
The next concrete action is another local mutator/read contract or bounded
tool ownership slice.

Phase 89 is the current bounded slice. Full `flujo verify` reaches only the
pytest step and exits 1 because pytest is absent from the canonical venv.
`flujo verify --no-pytest` passes compileall, health, version and temporary hub
smoke with exit 0, and no process remains. The next concrete action is to
continue MAK-wide duplicate/tool ownership work while preserving the exact
dev-dependency recovery condition; do not install pytest automatically.

Phase 88 is the current bounded slice. `research_lib.py` is byte-identical
across canonical, root and WIN, but `roles.MODULOS`, `backlog_codex.py`,
`trabajo.py`, mirror tooling and tests explicitly consume the root path. It is
therefore a protected projection, not confirmed junk. The next concrete action
is another pure consumer-backed duplicate or a bounded ownership adapter after
the consumer map is complete.

Phase 87 is the current bounded slice. Curatoria `diagnostico_proyectos.py`
is byte-identical across canonical, root projection and WIN, and both MAK
locations pass compile/help. The root is protected rather than deleted because
it has direct entrypoint semantics plus fichas, drainage data and logs. Hash
equality alone is not a cleanup gate. The next concrete action is another pure
consumer-backed duplicate or an explicit root ownership adapter.

Phase 86 is the current bounded slice. The exact duplicate root package
`/home/mak/post` was consolidated into the consumer-backed canonical
`/home/mak/flujo/cultura/mak_post`; its two files and regenerable cache were
removed, while WIN and the canonical source remain intact. AST, compile and
POST fixture validation passed. The next concrete action is another bounded
MAK duplicate/tool slice with a real consumer and rollback.

Phase 85 is the current bounded slice. The canonical `flujo verify
--no-pytest --no-hub-smoke` passed compileall, health and version with exit 0;
canonical-venv `pip check` also passed with no broken requirements, and the
core imports passed. The next concrete action is the MAK-wide
consumer/dependency audit; web, optional render/provider and mutating paths
remain separately gated.

Phase 84 is the current bounded slice. Knowledge `classify` and `show`
consumers now pass through the installed launcher after the repo namespace
adapter: Creamfields + Espacio Riesco resolves to the mainstream preset, and
both YAML entities load with exit 0. No writes or external calls occurred. The
next concrete action is the remaining static dependency/entrypoint audit.

Phase 83 is the current bounded slice. The installed `rd-datos informe`
read/report command now has foreground evidence: exit 0 with a temporary
output, truthful empty tables and the mandatory no-real-data disclaimer. The
real `data/rd_datos.db` remained zero bytes with unchanged mtime. The next
concrete action is another read-only consumer or static dependency gate;
`rd-datos ingest` remains deferred until approved field data exists.

Phase 82 is the current bounded slice. The installed CLI now exposes the
repo-level `cultura` namespace at import time, fixing
`/home/mak/venvs/flujo/bin/flujo autonomia status` from `ModuleNotFoundError`
to exit 0. Knowledge readers also pass through the canonical launcher. No
provider, SSH or Git operation ran. The next concrete action is another
bounded local consumer; autonomy `run`, providers and Git remain out of scope.

Phase 81 is the current bounded slice. The read-only non-serve CLI matrix
passed for version, health, jobs, datadrops, RD readers and autonomia. The
knowledge reader initially failed only under system Python because PyYAML was
absent; with the canonical `/home/mak/venvs/flujo/bin/python`, which contains
PyYAML 6.0.3 as declared, productoras and venues passed. The shell has no
`flujo` executable on PATH, so the next concrete action is to audit/document
the project launcher or activation path without installing dependencies.

Phase 80 is the current bounded slice. The web TypeScript gate passed with
exit 0, but the temporary Vite build is `BLOCKED_LOCAL_RUNTIME`: Node is
18.20.4 while installed Vite requires 20.19+ or 22.12+, and the optional
Rollup native module `@rollup/rollup-linux-x64-gnu` is absent. No package
install, lockfile edit or node_modules replacement is authorized here. The
next concrete action is another local static/read-only consumer while this
recovery path remains documented; revisit the web build only with a supported
runtime and dependency authority.

Phase 79 is complete. The RD indexer was built against `/home/mak/RD` into a
temporary `/tmp` output and its `stats`, `find`, `dupes` and `cleanup` readers
all exited 0. It classified 1,743 files without creating the absent
operational index or deleting the estimated cleanup candidates. Phase 78 is
complete. The active RD route consumer now adapts the historical
`C:\\rd` index to Linux through `FLUJO_RD_ROOT` or `--base-dir`, while the
index remains unchanged and the real command is documented as `flujo hub
route`. The bounded route and doctor checks passed with exit 0; doctor found
one expected not-yet-generated pipeline artifact. The next concrete action is
to select the next unresolved live consumer or external boundary from the
objective matrix. Do not reopen XIO, hardware, ADB or n8n, and do not delete
evidence or install dependencies.

Phase 77 is complete. Two pure source/projection modules (`ledger.py` and
`contrato_archivo.py`) passed parity and fixture gates, and
`PHASE68_PROJECTION_OWNERSHIP_MANIFEST.md/.csv` defines bounded ownership,
Phase 69 preserves broken generated evidence, and Phase 70's active health
gate passes. Phases 71–72 removed only 485 regenerable bytecode caches from
explicit active/source roots; health remained green. The current closeout
verification reran health/doctor with exit 0; Python regenerated 17 bytecode
cache files as normal, so they are not source changes. The next concrete action
is final disposition of external gates and any semantic merge that has a real
consumer; no evidence or consumer file may enter cleanup. Do not install
packages or propose additional Git branches yet. XIO, hardware and ADB are
removed from the plan. The objective
matrix in `PHASE73_OBJECTIVE_AUDIT_MATRIX.md/.csv` records evidence and
remaining boundaries for all 13 objectives; Phases 74–75 classify unresolved
MAK roots, web build projections, labs and recovered evidence without treating
size as proof of junk. Phase 77 proposes the branch system without mutating
Git.

## Last verified

- Phase 49 completed: `/home/mak/*` was re-enumerated first, then the MAK
  department roots were bounded and compared with WIN genealogy. The report
  is `context/PHASE49_MAK_WIDE_DEPARTMENT_CROSSWALK.md/.csv`. It classifies
  plataforma/research/codex/curatoria as live MAK surfaces or mixed evidence,
  post as the next small candidate, n8n-local as discarded by user decision,
  and xio_puente as the final ADB-dependent gate. Commands exited 0; no source,
  runtime, data, environment or device files were changed.
- Phase 50 completed: POST AST/normalized parity and direct contract probe
  passed; the focused pytest attempt exited 1 only because `pytest` is absent
  from `/home/mak/venvs/flujo/bin/python`. `adb` is absent, so XIO remains the
  final deferred test. Reports and this handoff are the only intentional text
  changes; no package, source, runtime, data or device change was made.
- Phase 51 completed: remaining MAK roots were re-enumerated from
  `/home/mak/*` and classified in `PHASE51_REMAINING_MAK_ROOTS_CROSSWALK`.
  No runtime or external action was taken; no unsafe process remains running.
- Phase 52 completed: lenguaje consumer declaration, source parity, AST,
  shell syntax and read-only measurement passed. `pytest` is unavailable and
  was not installed. Next candidate is vigia; xio remains last with ADB absent.
- Phase 53 completed: vigia consumer, behavior parity, shell/JSON validation
  and offline fixture passed. No network/state mutation occurred. XIO is now
  the final deferred gate and `adb` remains absent.
- Phase 54 completed: additive `rd.db` merge passed schema/data integrity and
  real `/api/rd-db` HTTP 200 validation. Backup was created; historical files
  and `rd_datos.db` were not altered.
- Phase 55 completed: fixed `rd_datos.db` GET-only behavior and proved empty
  and non-empty temporary read contracts without writes to the real database.
- Phase 56 completed: create-job-draft fixture and rollback passed; real jobs
  tree untouched. Remaining RD mutators are explicitly listed above.
- Phase 57 completed: datadrop invalid/valid fixtures and rollback passed;
  strict Base64 validation fix is in hub.py and real datadrops were untouched.
- Phase 58 completed: symbol persistence fixture/rollback and empty automation
  fixture passed. Remaining mutators are listed in the Phase 58 report.
- Phase 59 completed: logo and datadrop-analyze fixtures/rollbacks passed;
  real surfaces untouched. Remaining mutators are listed in Phase 59.
- Phase 60 completed: review-package, scan-incoming and disposable-job
  automation fixtures/rollbacks passed. RD mutator surface is fixture-verified
  with no production writes.
- Phase 61 completed: automation contract accepted from user evidence; CLI
  help/diagnostics and merged RD evidence reader passed. Mutating CLI families
  remain explicitly bounded.
- Phase 62 completed: `/home/mak/RD` was classified by physical surface,
  consumer and dependency in `context/PHASE62_RD_ASSET_DEPENDENCY_CROSSWALK.md`
  and `.csv`. The bounded inventory is approximately 1,743 files and 192
  directories; `AUTOMATIZACION` is a mixed workflow/evidence surface, not a
  bulk-copy candidate. `default_base_dir()` was verified unset, with
  `FLUJO_RD_ROOT=/home/mak/RD`, and with an explicit override; the CLI help and
  six relevant Python files passed AST parsing. No network, Blender,
  Photoshop, render, source, runtime or asset mutation occurred.
- Phase 63 completed: `context/PHASE63_MAK_FOLDER_ARCHITECTURE_AND_CLEANUP_POLICY.md`
  and `.csv` define canonical ownership, classification states, exact/variant
  duplicate rules, consumer-based tool merge gates and a path-level cleanup
  gate. No files were moved, merged or deleted; `/home/mak/WIN` is explicitly
  historical and protected.
- Phase 64 completed: `context/PHASE64_EXACT_DUPLICATE_AND_TOOL_CROSSWALK.md`
  and `.csv` record a bounded text/document hash pass: 6,678 files hashed,
  320 exact groups and 843 files in collisions. Active FLUJO imports point to
  `cultura/mak_*`; root department trees are projections or human surfaces,
  not automatically removable duplicates. No files were changed.
- Phase 65 completed: `context/PHASE65_MAK_PROJECTION_OWNERSHIP_GATE.md` and
  `.csv` validate the source/projection boundary. Active FLUJO imports point
  to `cultura/mak_*`; source/projection AST counts are recorded, with one
  known incomplete `panel_directivo.py` and seven malformed generated Codex
  pieces. They remain untouched and are not merge candidates.
- Phase 66 completed: `ledger.py` source/projection parity, real consumers,
  CLI help and pure envelope/item fixtures passed; the real ledger mtime/size
  stayed unchanged.
- Phase 67 completed: `contrato_archivo.py` source/projection parity, AST,
  real hub/laser/micelio consumers and pure portfolio fixtures passed. No
  source, projection, data, network or generated output changed.
- Phase 68 completed: `context/PHASE68_PROJECTION_OWNERSHIP_MANIFEST.md` and
  `.csv` define the canonical `cultura/mak_*` sources, protected root
  projections, verified slices and bounded refresh contract. No projection,
  runtime, state or evidence file changed.
- Phase 69 completed: `context/PHASE69_BROKEN_GENERATED_ARTIFACT_CLASSIFICATION.md`
  and `.csv` classify `/home/mak/plataforma/panel_directivo.py` and seven
  malformed dated Codex pieces as broken generated evidence. Targeted consumer
  searches found no active route for them; no repair-by-guessing or deletion
  occurred.
- Phase 70 completed: `context/PHASE70_ACTIVE_MAK_HEALTH_AUDIT.md` and `.csv`
  record health/doctor/rd-db checks (exit 0), 208 active Python AST passes,
  10 shell syntax passes, no persistent MAK process and no active user
  schedule. No runtime, state, evidence or output was changed.
- Phase 71 completed: `context/PHASE71_SAFE_CACHE_CLEANUP.md` and `.csv`
  removed exactly 235 regenerable bytecode caches from explicit active roots;
  zero remained, `flujo health` exited 0 and 218 Python files passed AST after
  cleanup. No source, data, evidence, output, logs, documents or WIN files
  were changed.
- Phase 72 completed: `context/PHASE72_ROOT_PROJECTION_CACHE_CLEANUP.md` and
  `.csv` removed exactly 250 additional regenerable bytecode caches from
  explicit root projections, excluding virtual environments and rollback;
  zero remained and `flujo health` exited 0.
- Phase 73 completed: `context/PHASE73_OBJECTIVE_AUDIT_MATRIX.md` and `.csv`
  audit all 13 objectives. They confirm local runtime gates without falsely
  marking field data, production mutators, semantic duplicate decisions,
  full department audit or Git branches as complete.
- Phase 74 completed: `context/PHASE74_REMAINING_MAK_SURFACE_AUDIT.md` and
  `.csv` classify apps, labs, optional `ml-mobileclip`, empty workspace,
  quarantine, web builds, outputs and recovered documents. No unresolved root
  was confirmed junk; no files were changed.
- Phase 75 completed: `context/PHASE75_WEB_AND_LAB_OUTPUT_CROSSWALK.md` and
  `.csv` prove the web build/share projection chain and classify dated labs as
  evidence/experiments. No build, lab, dependency, output or evidence file
  changed.
- Phase 76 completed: `context/PHASE76_QUARANTINE_AND_RECOVERED_EVIDENCE_GATE.md`
  and `.csv` protect rollback snapshots, patches, recovered sessions and
  source/data provenance. No evidence was deleted.
- Phase 77 completed: `context/PHASE77_GIT_BRANCH_SYSTEM_PROPOSAL.md` and
  `.csv` propose short-lived `codex/` branches by live domain/write set and a
  merge order. No branch, commit, merge, reset, checkout or push occurred.
- Phase 78 completed: `context/PHASE78_RD_ROUTE_LINUX_ADAPTER.md` and `.csv`
  record the bounded Linux route adapter. `flujo hub route` now resolves the
  historical `C:\\rd` index under `FLUJO_RD_ROOT` or `--base-dir`; the index
  SHA-256 remained `e9bbc598765c68b0606bdc1f7a0d43127b6a5a7c238e54627cd10c9d2f1b0bd8`.
  Compile, local `where`, explicit `where` and local `doctor` exited 0. The
  doctor result was 28 routes with one expected pipeline artifact absent. No
  data, asset or historical evidence changed.
- Phase 79 completed: `context/PHASE79_RD_INDEXER_TEMPORARY_GATE.md` and `.csv`
  validate the RD indexer against `/home/mak/RD` using a temporary output.
  Build/stats/find/dupes/cleanup all exited 0; 1,743 files were classified,
  no operational `index_rd.json` was created, and no cleanup candidate was
  deleted. A production index build remains an output-policy decision.
- Phase 80 completed: `context/PHASE80_WEB_RUNTIME_GATE.md` and `.csv` record
  web `typecheck` exit 0 and the reproducible build boundary. Vite cannot
  build with Node 18.20.4 and the missing optional Rollup native module; no
  package, lockfile, node_modules, source or dist mutation occurred.
- Phase 81 completed: `context/PHASE81_NON_SERVE_CLI_RUNTIME_MATRIX.md` and
  `.csv` record read-only CLI results. The canonical venv passes the knowledge
  readers and health; system-Python PyYAML absence is an environment mismatch,
  not a source defect. No data, provider, job, datadrop or dependency changed.
- Phase 82 completed: `context/PHASE82_CLI_REPO_NAMESPACE_GATE.md` and `.csv`
  record the minimal CLI import-path adapter. The installed autonomy status
  and knowledge list now exit 0; no provider, SSH, Git, job, ledger or data
  mutation occurred.
- Phase 83 completed: `context/PHASE83_RD_FIELD_REPORT_READONLY_GATE.md` and
  `.csv` validate `rd-datos informe`. The report exited 0 into `/tmp`,
  represented the empty real field dataset truthfully, and left
  `data/rd_datos.db` at 0 bytes with unchanged mtime. No ingest or schema
  mutation ran.
- Phase 84 completed: `context/PHASE84_KNOWLEDGE_READ_CONSUMER_GATE.md` and
  `.csv` validate knowledge classify/show through the installed launcher.
  Producer, venue and mainstream preset resolution passed with exit 0; no
  source, YAML, database, provider or output mutation occurred.
- Phase 85 completed: `context/PHASE85_CORE_VERIFY_AND_DEPENDENCY_GATE.md` and
  `.csv` record the canonical core verifier and dependency checks. Compileall,
  health, version, pip check and required imports passed; no package install,
  provider, Git, data or persistent process was used.
- Phase 86 completed: `context/PHASE86_POST_DUPLICATE_CONSOLIDATION.md` and
  `.csv` record removal of the exact, consumerless `/home/mak/post` duplicate.
  The canonical `cultura.mak_post` fixture and compile pass; WIN evidence and
  all consumer-backed files remain unchanged.
- Phase 87 completed: `context/PHASE87_CURATORIA_PROJECTION_GATE.md` and
  `.csv` record exact parity and help/compile validation for curatoria
  `diagnostico_proyectos.py`. The root projection remains protected due to
  state/log/direct-entrypoint ownership; no evidence or operational output was
  deleted.
- Phase 88 completed: `context/PHASE88_RESEARCH_LIB_PROJECTION_GATE.md` and
  `.csv` record three-way parity and active root-path consumers for
  `research_lib.py`. No deletion, provider, worker, queue or service action
  occurred.
- Phase 89 completed: `context/PHASE89_FULL_VERIFY_GATE.md` and `.csv` record
  the full verifier boundary. Runtime verification and hub smoke pass; the
  full suite remains blocked solely by missing pytest in the dev environment.
  No package install or persistent process occurred.
- Phase 90 completed: `context/PHASE90_FLYER_INDEX_READONLY_GATE.md` and `.csv`
  record the explicit reader/writer separation in `src/flujo/index/db.py`.
  Real index integrity and temporary rebuild/read fixtures passed; no
  production database or other MAK surface changed.
- Phase 91 completed: `context/PHASE91_DATADROP_LIST_READONLY_GATE.md` and
  `.csv` record the non-creating datadrop reader. Empty-root and real-root
  checks passed; writer commands remain explicit and no real datadrop changed.
- Phase 92 completed: `context/PHASE92_READ_CONTRACT_STATIC_AUDIT.md` and
  `.csv` record the bounded AST read-contract scan. No unlabelled reader
  mutation was found and no repository state changed.
- Phase 93 completed: `context/PHASE93_OBJECTIVE_CLOSEOUT_MATRIX.md` and
  `.csv` reconcile the complete 13-item objective. It records verified,
  deferred, blocked and proposed states without redefining completion around
  the already-green runtime.
- Phase 94 completed: `context/PHASE94_MUTATOR_ENTRYPOINT_GATE.md` and `.csv`
  record help/entrypoint verification for 13 mutating or external-capable
  commands. All exited 0; no production mutation or external action ran.
- Phase 95 completed: `context/PHASE95_RD_MUTATOR_ROLLBACK_CONTINUITY.md` and
  `.csv` recheck the RD mutator functions, bounded real roots and persistent
  process state. Fixture rollback continuity passed; no production surface
  changed.
- Phase 96 completed: `context/PHASE96_AUTONOMIA_LOCAL_DRYRUN_GATE.md` and
  `.csv` validate local automation preparation in dry-run mode. One temporary
  brief was generated with exit 0; no provider, SSH, Ollama, ledger or
  publication action occurred.
- Verification incident recorded: one earlier broad hash command remained as
  orphaned PID `442339` after the tool returned; a stale inventory grep was
  also found as PIDs `436570`/`436575`. All three exact scan PIDs were
  terminated. A follow-up check found no FLUJO, Blender, worker, vigia or
  scan process; user crontab has no active (non-comment) entries and user
  timers list is empty. The system `/usr/sbin/cron` daemon is normal and was
  not altered.

2026-08-14 America/Santiago — Phase 78 completed: the RD route consumer was
adapted to MAK Linux without changing the historical index; remaining work is
the next live-consumer audit and external-gate disposition.

## Phase 97 — latest authoritative update

Phase 97 completed the bounded `contrato_archivo.py` ownership merge. The
implementation was byte-identical in `/home/mak/plataforma`, canonical
`/home/mak/flujo/cultura/mak_plataforma` and the WIN historical copy. The root
file was replaced with a 35-line compatibility projection to the canonical
1,177-line implementation; WIN, rollback snapshots, data and logs were not
edited. Root direct imports, canonical imports, `hub` import-only, compile and
pure fixtures passed with exit 0. No server or persistent process remained.
Evidence: `context/PHASE97_CONTRATO_ARCHIVO_OWNERSHIP_MERGE.md` and `.csv`.

## Next concrete action

Continue the remaining ownership/tool merge audit from `/home/mak/*`, starting
with one bounded candidate that has a real consumer and disjoint source and
projection ownership. Compare active MAK paths to WIN only as provenance; do
not scan rollback trees broadly, copy whole trees, or promote dry-run
automation. After the next safe merge, validate compile/import/entrypoint in
the foreground and record exact paths, exit codes, rollback and consumer
impact. External providers, production mutators, empty `rd_datos.db`, missing
pytest and the blocked web build remain explicit open gates.

Last verified: 2026-08-15 America/Santiago — Phase 97 root compatibility
projection and canonical contract fixtures passed; no persistent process.

## Phase 98 — latest authoritative update

Phase 98 completed the bounded research `memoria.py` ownership merge. The root
department copy, canonical source and WIN historical copy were byte-identical.
The root file is now a compatibility projection that preserves imports and
forwards its direct `__main__` entrypoint to the canonical implementation.
Root import, `python memoria.py --help`, compile and process checks passed with
exit 0. Memory indexes, logs, outputs, WIN and rollback evidence were not
changed. Evidence: `context/PHASE98_RESEARCH_MEMORIA_OWNERSHIP_MERGE.md` and
`.csv`.

## Next concrete action

Continue the ownership audit with the next active projection candidate, using
the same bounded method: verify exact parity and real consumers, preserve
direct entrypoints, edit only the active root projection, then compile/import
and help-check in foreground. Do not touch indexed research data, rollback
trees, WIN, external providers or production mutators. Remaining open gates
are field data, production mutation authority, pytest, web build dependency,
semantic tool merges, confirmed-junk cleanup and later Git branch application.

Last verified: 2026-08-15 America/Santiago — Phase 98 research memory bridge
and direct help contract passed; no persistent process.

## Phase 99 — latest authoritative update

Phase 99 completed the bounded research runner ownership merge. The root
`/home/mak/research/research.py`, canonical source and WIN copy were
byte-identical. The root file is now a compatibility projection that preserves
imports and forwards its direct `__main__` command to the canonical runner.
Root import, `research.py --help`, compile and process checks passed with exit
0. No provider, search, LLM, notification, report, checkpoint or job action
ran. Evidence: `context/PHASE99_RESEARCH_RUNNER_OWNERSHIP_MERGE.md` and `.csv`.

## Next concrete action

Continue with the next active root projection only after bounded parity and
consumer checks. Prefer a non-external read/CLI contract; preserve direct
entrypoints and keep data, logs, reports, checkpoints, rollback trees and WIN
untouched. After validation, reconcile remaining tool ownership, cleanup
criteria and full MAK audit evidence before proposing Git branch application.

Last verified: 2026-08-15 America/Santiago — Phase 99 research runner bridge,
help and compile passed; no persistent process or external call.

## Phase 100 — latest authoritative update

Phase 100 completed the bounded research `panel.py` ownership merge. The root,
canonical and WIN copies were byte-identical. The root file is now a
compatibility projection preserving imports and forwarding the direct
`__main__` command. Root import, `panel.py --help`, compile and process checks
passed with exit 0. No panel, model, provider, notification, report,
checkpoint or job action ran. Evidence: `context/PHASE100_RESEARCH_PANEL_OWNERSHIP_MERGE.md`
and `.csv`.

## Next concrete action

Continue the remaining active projection audit, selecting the next module only
after confirming parity and real consumers. Preserve direct entrypoints and
keep indexed data, logs, generated reports, checkpoints, rollback trees and
WIN unchanged. External-capable research paths, production mutators, empty
RD field data, pytest/web dependency gates, confirmed-junk cleanup and Git
branch application remain open and must not be hidden by these consolidations.

Last verified: 2026-08-15 America/Santiago — Phase 100 panel bridge, help and
compile passed; no persistent process or external call.

## Phase 101 — latest authoritative update

Phase 101 completed the bounded `cadena.py` ownership merge. The active MAK
root and canonical source were byte-identical; the WIN copy was a distinct
historical variant and was preserved untouched. The root file is now a
compatibility projection that preserves imports and forwards its direct
`__main__` command. Root import, `cadena.py --help`, compile and process checks
passed with exit 0. No model/provider, notification, report, checkpoint or job
action ran. Evidence: `context/PHASE101_RESEARCH_CADENA_OWNERSHIP_MERGE.md` and
`.csv`.

## Next concrete action

Move to the next active root projection or a different MAK department slice.
For any root/canonical/WIN disagreement, treat WIN as historical provenance,
compare semantics before adopting it, and never overwrite it. Continue
foreground validation and keep external providers, field-data ingest,
production mutators, generated outputs, rollback trees and Git application
gates explicit.

Last verified: 2026-08-15 America/Santiago — Phase 101 cadena bridge, help and
compile passed; no persistent process or external call.

## Phase 102 — latest authoritative update

Phase 102 completed the bounded research runner-family merge for `refutar.py`,
`grafo.py`, `cola.py` and `worker.py`. Active MAK root/canonical parity was
confirmed; WIN matched three files and retained a distinct historical
`grafo.py`. Four root compatibility projections now preserve consumers and
entrypoints. Imports, safe help checks and compilation passed with exit 0; the
queue, workers, models, providers, notifications, reports, checkpoints and
jobs were not run. Evidence: `context/PHASE102_RESEARCH_RUNNER_FAMILY_OWNERSHIP_MERGE.md`
and `.csv`.

## Next concrete action

Leave the research family and audit the next department-level projection with
real consumers, starting from `/home/mak/*`. Preserve WIN, stateful service
loops, data, logs, generated outputs and rollback trees. The remaining open
gates are field data, production mutators, external automation/provider
authority, dependency/test gaps, architecture/cleanup policy and Git branch
application.

Last verified: 2026-08-15 America/Santiago — Phase 102 runner-family bridges,
imports/help/compile passed; no persistent or external process.

## Phase 103 — latest authoritative update

Phase 103 completed the first CODEX ownership slice: `codex_lib.py` and
`generar.py`. MAK root/canonical parity was confirmed; WIN `generar.py` matched
but WIN `codex_lib.py` remained a distinct historical variant. Root
compatibility projections preserve imports and the generator entrypoint.
Import, `--help` and compilation passed with exit 0. No generation, sandbox,
provider, model, worker or output mutation ran. Evidence:
`context/PHASE103_CODEX_CORE_OWNERSHIP_MERGE.md` and `.csv`.

## Next concrete action

Continue the CODEX consumer audit with the next bounded family, prioritizing
read-only/help contracts before any generator or sandbox execution. Preserve
WIN, generated pieces, logs, state and rollback trees. Document semantic
divergences instead of copying WIN over MAK; external provider authority,
field data, production mutators, dependency gates, cleanup and Git branches
remain open.

Last verified: 2026-08-15 America/Santiago — Phase 103 CODEX core bridges,
import/help/compile passed; no persistent or external process.

## Phase 104 — latest authoritative update

Phase 104 completed the CODEX consumer family merge for `revisar.py`,
`testear.py` and `worker_codex.py`. All three were byte-identical across MAK
root, canonical source and WIN; root compatibility projections now preserve
their consumers and safe entrypoints. Imports, help and compilation passed
with exit 0, and no review/test generation, worker, provider, model, sandbox or
output action ran. `agente_libre.py` was deliberately not merged because its
canonical MAK content differs from root/WIN. Evidence:
`context/PHASE104_CODEX_CONSUMER_FAMILY_OWNERSHIP_MERGE.md` and `.csv`.

## Next concrete action

Compare `agente_libre.py` semantics and ownership before deciding whether it is
an active canonical tool, a root projection, or a historical fork. Do not run
its free-agent mutation path. Then leave CODEX and continue the next department
slice; preserve WIN, generated pieces, logs, state and rollback trees.

Last verified: 2026-08-15 America/Santiago — Phase 104 CODEX consumer bridges,
imports/help/compile passed; no persistent or external process.

## Phase 105 — latest authoritative update

Phase 105 closed the CODEX ownership audit. `agente_libre.py` differed only in
comments between canonical MAK and root/WIN; its active root is now a
compatibility projection to canonical. Import, `--help` and compilation
passed with exit 0. No free-agent pipeline, model, provider, file write,
worker or output mutation ran. Evidence:
`context/PHASE105_CODEX_FREE_AGENT_OWNERSHIP_MERGE.md` and `.csv`.

## Next concrete action

Leave CODEX and begin the next department-level audit from `/home/mak/*`.
Prefer a bounded read/entrypoint slice, preserve WIN and stateful surfaces,
and keep external providers, mutators, generated outputs, dependency gaps,
confirmed-junk cleanup and Git application as explicit gates.

Last verified: 2026-08-15 America/Santiago — Phase 105 CODEX free-agent bridge,
help and compile passed; no persistent or external process.

## Phase 106 — latest authoritative update

Phase 106 began curatoria and consolidated `panel.py` plus `watchdog.py`.
Active MAK root/canonical/WIN parity was confirmed; root compatibility
projections now preserve direct imports and entrypoint shapes. Imports and
compilation passed with exit 0. No panel server, watchdog, perception,
notification, worker or state mutation ran. `percepcion.py` remains separate:
its WIN copy differs in fallback diagnostics/path handling. Evidence:
`context/PHASE106_CURATORIA_PANEL_WATCHDOG_OWNERSHIP_MERGE.md` and `.csv`.

## Next concrete action

Audit `percepcion.py` as a read/fixture/static gate, especially its local
`research_lib` resolution and `PERCEPCION_VISION` fallback, without running OCR,
vision, watchdogs or writing fichas. Then continue the remaining curatoria
slice and preserve WIN, state, generated outputs and rollback trees.

Last verified: 2026-08-15 America/Santiago — Phase 106 curatoria panel/watchdog
bridges and compile passed; no persistent or external process.

## Phase 107 — latest authoritative update

Phase 107 completed the curatoria `percepcion.py` ownership merge. Active MAK
root/canonical parity was confirmed; WIN remained an unmodified historical
variant with only fallback comments/message differences. The root is now a
compatibility projection preserving imports and the direct CLI. Corrected
deterministic fixtures and compilation passed with exit 0; the custom
`correr|estado` usage contract correctly returns exit 2 for `--help`. No OCR,
vision, Tesseract, ffprobe, provider, fiche write, watchdog or worker ran.
Evidence:
`context/PHASE107_CURATORIA_PERCEPCION_OWNERSHIP_MERGE.md` and `.csv`.

## Next concrete action

Continue the remaining curatoria read/fixture audit (`ingesta_archivo.py`,
`extraccion_db.py`, `reporter.py`, `ordenes.py`), selecting only bounded
contracts and never invoking OCR/vision or fiche writes. Preserve WIN, state,
generated outputs and rollback trees before moving to the next department.

Last verified: 2026-08-15 America/Santiago — Phase 107 perception bridge,
fixtures/help/compile passed; no persistent or external process.

## Phase 108 — latest authoritative update

Phase 108 consolidated curatoria `ingesta_archivo.py`, `reporter.py` and
`ordenes.py`. All three were byte-identical across active MAK root, canonical
source and WIN; root compatibility projections preserve imports and direct
entrypoints. Imports, safe ingestion help and compilation passed with exit 0.
No ingestion, report writing, perception launch, process control, database or
external action ran. `extraccion_db.py` remains separate because canonical MAK
differs from root/WIN. Evidence:
`context/PHASE108_CURATORIA_INGEST_REPORT_ORDERS_OWNERSHIP_MERGE.md` and `.csv`.

## Next concrete action

Audit `extraccion_db.py` statically and with pure candidate fixtures; do not
write candidate JSONL, reports or databases. Resolve whether canonical MAK or
root/WIN owns its semantic changes, then close curatoria before moving on.

Last verified: 2026-08-15 America/Santiago — Phase 108 curatoria bridges,
imports/help/compile passed; no persistent or external process.

## Phase 109 — latest authoritative update

Phase 109 closed curatoria ownership for `extraccion_db.py`. The active MAK
root/canonical difference was documentation-only and root/WIN were identical;
the root is now a compatibility projection to canonical. Corrected pure
fixtures using the real nested `datos_evento` schema and compilation passed
with exit 0. No candidate JSONL, report, database, perception, OCR, vision or
external action ran. Evidence:
`context/PHASE109_CURATORIA_EXTRACCION_OWNERSHIP_MERGE.md` and `.csv`.

## Next concrete action

Leave curatoria and begin the next department-level slice from `/home/mak/*`.
Preserve WIN, stateful services, generated outputs, databases and rollback
trees; keep all production writers and external providers behind explicit
foreground gates.

Last verified: 2026-08-15 America/Santiago — Phase 109 extraction bridge,
corrected pure fixtures and compile passed; no persistent or external process.

## Phase 110 — latest authoritative update

Phase 110 began `mak_plataforma` and consolidated `salud.py` plus `roles.py`.
Both were byte-identical across active MAK root, canonical source and WIN;
root compatibility projections now preserve the health snapshot and role
policy consumers. Imports, read-only snapshot and compilation passed with exit
0. No hub, worker, service, Blender, Ollama or external action ran. Divergent
`tandas.py` and `coherence.py` remain untouched. Evidence:
`context/PHASE110_PLATFORM_HEALTH_ROLES_OWNERSHIP_MERGE.md` and `.csv`.

## Next concrete action

Continue the platform read-only audit with `tandas.py` and `coherence.py`
semantics; do not run external batches, sync/deploy commands or mutators.
Preserve WIN, state, logs, generated outputs and rollback trees.

Last verified: 2026-08-15 America/Santiago — Phase 110 platform health/roles
bridges, snapshot and compile passed; no persistent or external process.

## Phase 111 — latest authoritative update

Phase 111 consolidated platform `coherence.py`; root/canonical/WIN differences
were documentation-only. Import, `--help` and compilation passed with exit 0;
no coherence sync, Git inspection, batch, provider or external action ran.
`tandas.py` was not merged because root, canonical and WIN differ
functionally in evidence paths and external-batch payload fields. Evidence:
`context/PHASE111_PLATFORM_COHERENCE_OWNERSHIP_MERGE.md` and `.csv`.

## Next concrete action

Resolve `tandas.py` ownership with pure contract fixtures: compare
`build_brief`, `validate_result`, `validate_evidence_paths` and dry-run CLI
help, without calling providers or writing ledgers/briefs. Preserve all three
variants until the active consumer contract is explicit.

Last verified: 2026-08-15 America/Santiago — Phase 111 coherence bridge,
help and compile passed; no persistent or external process.

## Phase 112 — latest authoritative update

Phase 112 audited `tandas.py` across canonical MAK, root MAK and WIN with
isolated pure fixtures. Provider planning, brief construction, result/product
validation and the external-batch signature passed in all variants with exit
0, but evidence paths and WIN dispatch payload fields differ functionally.
No merge was applied; this is a documented semantic ownership fork, not
confirmed junk. No provider, queue, Ollama, ledger, brief, batch or external
action ran. Evidence:
`context/PHASE112_PLATFORM_TANDAS_SEMANTIC_OWNERSHIP_GATE.md` and `.csv`.

## Next concrete action

Continue the platform audit with the next read-only consumer, or open a
dedicated reconciliation slice for `tandas.py` only when its evidence-manifest
and external-payload owner is explicit. Preserve all three variants, WIN,
ledgers, state, generated outputs and rollback trees.

Last verified: 2026-08-15 America/Santiago — Phase 112 tandas semantic gate
passed across three variants; no persistent or external process.

## Phase 113 — latest authoritative update

Phase 113 consolidated platform `junta.py`, `backlog.py` and `revision.py`.
All three were byte-identical across active MAK root, canonical source and
WIN; root compatibility projections preserve imports and consumers. Imports,
pure backlog/revision reads and compilation passed with exit 0. No council
model call, backlog write, revision POST, provider, worker, hub or generated
output action ran. Evidence:
`context/PHASE113_PLATFORM_COUNCIL_BACKLOG_REVISION_OWNERSHIP_MERGE.md` and
`.csv`.

## Next concrete action

Continue the remaining platform audit and keep `tandas.py` as an explicit
semantic fork until its evidence/payload owner is reconciled. Preserve WIN,
ledgers, backlog/revision state, generated outputs and rollback trees; do not
run production writers or external providers.

Last verified: 2026-08-15 America/Santiago — Phase 113 platform bridges,
pure-read/import/compile validation passed; no persistent or external process.

## Phase 114 — latest authoritative update

Phase 114 consolidated platform `trabajo.py` and `backlog_codex.py`. Both were
byte-identical across active MAK root, canonical source and WIN; root
compatibility projections preserve their automation imports and entrypoints.
Imports and compilation passed with exit 0. No work tick, backlog refill,
provider, queue, worker, state, ledger or output action ran. `capataz.py` and
`chat_agente.py` remain separate because their WIN copies differ. Evidence:
`context/PHASE114_PLATFORM_WORK_AUTOMATION_OWNERSHIP_MERGE.md` and `.csv`.

## Next concrete action

Audit `capataz.py` and `chat_agente.py` semantics against their WIN variants
without invoking PR review, delivery, providers or writes. Then perform the
remaining platform automation dry-run gates explicitly.

Last verified: 2026-08-15 America/Santiago — Phase 114 automation bridges and
compile passed; no persistent or external process.

## Phase 115 — latest authoritative update

Phase 115 consolidated platform `capataz.py` and `chat_agente.py`. Active MAK
root/canonical parity was confirmed. WIN `capataz.py` differed only in
documentation; WIN `chat_agente.py` retained the obsolete remote Ollama target
`192.168.50.1`, while MAK now uses the local `127.0.0.1:11434` projection.
Corrected capataz fixtures and compilation passed with exit 0. Chat runtime
import is gated by missing `qwen_agent` in the canonical venv; AST confirms the
active endpoint remains local. No installation was attempted, and no chat,
capataz cycle, PR review, delivery, HTTP, provider, Ollama or state write ran.
Evidence:
`context/PHASE115_PLATFORM_CAPATAZ_CHAT_OWNERSHIP_MERGE.md` and `.csv`.

## Next concrete action

Run the remaining platform automation dry-run/read-only gates and reconcile
the `tandas.py` semantic fork. Keep chat tools, capataz actions, external
providers, ledgers, state, generated outputs, WIN and rollback trees untouched
unless a bounded foreground gate explicitly requires them.

Last verified: 2026-08-15 America/Santiago — Phase 115 capataz/chat bridges,
fixtures/import/compile passed; no persistent or external process.

## Phase 116 — latest authoritative update

Phase 116 validated the `tandas.py` CLI contracts across canonical MAK, root
MAK and WIN: `areas`, `brief` and `summary` all exited 0 with matching basic
outputs and temporary-only paths. The canonical `flujo autonomia run` local
dry-run also exited 0 with `ok=true,status=briefed`, producing one temporary
brief and no provider/Ollama/SSH/AWS/ledger action. The existing dirty worktree
was reported by preflight; no Git operation ran. Evidence:
`context/PHASE116_TANDAS_CLI_AUTONOMIA_DRYRUN_GATE.md` and `.csv`.

## Next concrete action

Continue the remaining full MAK audit and objective closeout: reconcile the
`tandas.py` semantic fork, verify dependency/test gaps, review folder/duplicate
ownership, confirm only safe cleanup candidates, and keep production mutators,
field data, external providers, WIN and Git application explicitly gated.

Last verified: 2026-08-15 America/Santiago — Phase 116 tandas CLI and autonomy
dry-run passed; no persistent or external process.

## Phase 117 — latest authoritative update

Phase 117 reconciled the 13 integration objectives against the physical MAK
state and refreshed the objective matrix. `/home/mak/venvs/flujo/bin/flujo
verify --no-pytest` exited 0; compile/health, version checks and temporary hub
smoke passed, with no persistent Flujo process left behind. The canonical venv
does not contain `pytest` or `qwen_agent`. The web gate remains explicit:
Node 18.20.4 is below the Vite requirement and the native Rollup module is
absent; no package installation was attempted. Evidence:
`context/PHASE117_OBJECTIVE_RECONCILIATION.md` and `.csv`.

## Phase 118 — latest authoritative update

Phase 118 consolidated the MAK root `plataforma/tandas.py` into a compatibility
projection to canonical `flujo/cultura/mak_plataforma/tandas.py`. Static
consumer evidence identifies the canonical module in FLUJO CLI, autonomy,
conductor and tests. Root and canonical compile, import, pure provider/result
fixtures and `areas` CLI output passed with exit 0. The historical WIN variant
at `WIN/flujo/cultura/mak_plataforma/tandas.py` was not edited because it
contains a distinct historical external-dispatch payload. No provider, ledger,
database, output or persistent process was touched. Evidence:
`context/PHASE118_TANDAS_ROOT_PROJECTION_MERGE.md` and `.csv`.

## Next concrete action

Continue the full MAK audit from `/home/mak/*`: run the remaining read-only
department and entrypoint gates, then re-audit exact/semantic duplicates by
consumer and provenance. Keep WIN, empty field data, production mutators,
external providers, generated outputs, ledgers and Git application closed.
Resolve the recorded `pytest`/`qwen_agent`/web runtime gaps only with explicit
authority; do not install packages or start permanent services.

Last verified: 2026-08-15 America/Santiago — Phase 118 tandas root projection,
compile/import/pure fixtures/areas parity passed; no persistent or external
process.

## Phase 119 — latest authoritative update

Phase 119 statically gated the remaining visible non-FLUJO surfaces
`/home/mak/RD` and `/home/mak/src/ml-mobileclip`, starting from `/home/mak/*`.
The RD surface had 6 Python files: 5 AST-valid and one documentary
`IndentationError` in `RD/py.py`; its automation files contain Windows paths,
Instagram download, Blender scene mutation and filesystem writers, so they
remain deferred external/mutating evidence. MobileCLIP had 26/26 AST-valid
files but is an isolated optional library with its own Torch/OpenCLIP/model
requirements and no confirmed active runtime consumer. No import, dependency
installation, Blender, network, database or output action ran. Evidence:
`context/PHASE119_NONCANONICAL_SURFACES_STATIC_GATE.md` and `.csv`.

## Next concrete action

Continue the remaining consumer-backed duplicate and folder-ownership review
from `/home/mak/*`. Keep RD automation as a protected external-writer slice,
MobileCLIP isolated, WIN historical, XIO excluded, and all mutators/providers,
empty field data, generated outputs, ledgers and Git application closed.

Last verified: 2026-08-15 America/Santiago — Phase 119 RD/MobileCLIP AST gate
passed with the documented RD documentary-file exception; no persistent or
external process.

## Phase 120 — latest authoritative update

Phase 120 consolidated `/home/mak/research/fuentes.py` into a compatibility
projection to canonical `flujo/cultura/mak_research/fuentes.py`. Static
consumer evidence identified the canonical source-quality gate in RD/research
and refutation tests; the root variant differed only in a comment. Isolated
imports, primary/non-primary source fixtures and compilation passed with exit
0 for both paths. No network lookup, report, database, provider or WIN action
ran. Evidence:
`context/PHASE120_RESEARCH_SOURCES_PROJECTION_MERGE.md` and `.csv`.

## Next concrete action

Continue the root/canonical ownership audit with the next pure, consumer-backed
difference. Keep `entregar_micelio.py` behind its external writer gate because
it can use network, write logs/data and invoke Git. Preserve RD automation,
MobileCLIP, WIN, empty field data, generated outputs, ledgers and Git
application; do not run external writers or install dependencies.

Last verified: 2026-08-15 America/Santiago — Phase 120 research source gate,
projection import/pure fixtures/compile passed; no persistent or external
process.

## Phase 121 — latest authoritative update

Phase 121 ran a bounded SHA-256 ownership audit over canonical MAK packages
and root department projections, excluding virtual environments, caches and
generated corpus/output trees. After the prior projection merges, the only
remaining non-projection semantic Python difference is
`/home/mak/plataforma/entregar_micelio.py`; curatoria, research and codex
differences are now documented projections or protected data/evidence
surfaces. The scan exited 0 and performed no imports, network, Git, database,
provider, output or service action. Evidence:
`context/PHASE121_MIRROR_RESIDUAL_OWNERSHIP_AUDIT.md` and `.csv`.

## Next concrete action

Statically gate `entregar_micelio.py` against its current consumer and dry-run
contract without calling the micelio, Git, network or log writer. If root and
canonical semantics are equal, project the root path; otherwise preserve the
external fork. Then continue the folder/duplicate cleanup re-audit with all
department data, corpus, ledgers, outputs, RD automation, MobileCLIP, WIN and
Git application protected.

Last verified: 2026-08-15 America/Santiago — Phase 121 mirror residual audit
isolated one external writer candidate; no persistent or external process.

## Phase 122 — latest authoritative update

Phase 122 consolidated the root `plataforma/entregar_micelio.py` into a
compatibility projection to canonical
`flujo/cultura/mak_plataforma/entregar_micelio.py`. The pre-merge AST gate
found identical function surfaces and only documentation drift. Post-merge
root/canonical compilation, isolated imports, pure empty-snapshot fixture and
root `--help` all exited 0. No micelio HTTP call, log/data write, Git or PR
action ran. Evidence:
`context/PHASE122_MICELIO_DELIVERY_PROJECTION_MERGE.md` and `.csv`.

## Next concrete action

Re-run the mirror ownership inventory to confirm no non-projection semantic
Python candidates remain, then refresh the folder/duplicate cleanup matrix.
Keep the canonical micelio delivery gate external-action-only, and preserve
all data, evidence, generated outputs, logs, WIN and Git state.

Last verified: 2026-08-15 America/Santiago — Phase 122 micelio delivery root
projection, compile/import/pure fixture/help passed; no external action.

## Phase 123 — latest authoritative update

Phase 123 re-ran the read-only mirror ownership inventory after the micelio
projection. The four families `mak_plataforma`, `mak_curatoria`,
`mak_research` and `mak_codex` now have `0` remaining non-projection semantic
Python candidates. Canonical code ownership is closed for these families;
root non-code surfaces remain protected data/evidence/state/output material.
No source, database, evidence, state, output, log, provider or Git action ran.
Evidence: `context/PHASE123_MIRROR_OWNERSHIP_CLOSURE.md` and `.csv`.

## Next concrete action

Refresh the folder/duplicate cleanup matrix at path level. Identify only
confirmed junk candidates with no consumer, provenance, evidence or recovery
value; never delete by hash alone. Preserve unresolved data, corpus, ledgers,
outputs, RD automation, MobileCLIP, WIN and Git state.

Last verified: 2026-08-15 America/Santiago — Phase 123 mirror ownership
closure returned zero non-projection semantic Python candidates.

## Phase 124 — latest authoritative update

Phase 124 applied the first path-level cleanup after ownership closure. A
bounded preflight found exactly 92 Finder metadata files named `.DS_Store`
under `/home/mak/curatoria_inbox`, with no scoped code references. All 92 were
moved reversibly, preserving relative paths, to
`context/quarantine/phase124_ds_store`. The move exited 0 and validated
`source_after=0`, `quarantined=92`. No `.bak`, `~`, lock, rollback, corpus,
output, database, WIN or source file was touched. Evidence:
`context/PHASE124_CLEANUP_QUARANTINE_DS_STORE.md` and `.csv`.

## Next concrete action

Run a focused post-cleanup read-only health/entrypoint check, refresh the
objective/cleanup matrix and keep the deletion scope narrow. Do not infer that
`.bak`, `~`, zero-byte locks, rollback trees or generated artifacts are junk;
they remain unresolved/protected pending their own consumer and recovery gate.

Last verified: 2026-08-15 America/Santiago — Phase 124 reversible quarantine
of 92 exact `.DS_Store` metadata files passed; no persistent or external
process.

## Phase 125 — latest authoritative update

Phase 125 validated the post-cleanup state in the foreground: `python -m flujo
health` exited 0, `python -m flujo version` exited 0 with version `0.56.1`,
root `plataforma/tandas.py areas` exited 0, and no Flujo/hub/Ollama/Blender/
media/micelio process remained. The initial `--version` form correctly failed
with CLI exit 2 and was recovered by using the `version` subcommand; no state
changed. The refreshed 13-objective matrix remains explicit about deferred,
partial and blocked gates. Evidence:
`context/PHASE125_POST_CLEANUP_OBJECTIVE_REFRESH.md` and `.csv`.

## Next concrete action

Continue the remaining read-only path/consumer audit and update the cleanup
matrix. Preserve all unresolved `.bak`, `~`, zero-byte locks, rollback,
corpus, output, database, RD automation, MobileCLIP and WIN material. Do not
install dependencies, run external writers or apply Git branches.

Last verified: 2026-08-15 America/Santiago — Phase 125 post-cleanup health,
version, platform entrypoint and process gates passed.

## Phase 126 — latest authoritative update

Phase 126 quarantined seven path-specific shell residues: the 55-byte literal
file `/home/mak/\\;` containing escaped command residue, plus six empty
directories whose names were literal backslash-escaped MAK paths. The exact
move exited 0 and validated `source_empty_artifacts_remaining=0`. No canonical
package, source, database, evidence, output, rollback or WIN path was touched.
Evidence: `context/PHASE126_STRAY_SHELL_ARTIFACT_QUARANTINE.md` and `.csv`.

## Next concrete action

Continue the duplicate-document/asset ownership audit, starting with exact RD
reference PDFs and related job assets. Preserve every source/output/evidence
copy until its human consumer and provenance are identified; do not widen
cleanup based on emptiness or hash alone.

Last verified: 2026-08-15 America/Santiago — Phase 126 reversible quarantine
of seven exact shell residues passed; no persistent or external process.

## Phase 127 — latest authoritative update

Phase 127 classified the RD document/asset duplicate family. The inspected
`REFERENCIA_VALORES.pdf` copies share SHA-256
`e0a45846613943f97b70a1d56ef9bfd27bfa83ce6bc9db0ab564680985a65321`, 3 A4
pages and 364382 bytes, but have distinct RD source, FLUJO mirror, deployment,
separate-project, runner and WIN roles. The related `brief_packs_plano_dark`
family spans live job output, RD assets and WIN evidence. No document was
moved or deleted. Evidence:
`context/PHASE127_RD_DOCUMENT_ASSET_OWNERSHIP_GATE.md` and `.csv`.

## Next concrete action

Map the RD job asset manifest and `/home/mak/RD` editable/delivery roles, then
refresh the cleanup matrix with only path-specific candidates. Do not
deduplicate PDFs, SVGs, Blender files or office assets by hash alone.

Last verified: 2026-08-15 America/Santiago — Phase 127 RD document/asset
ownership gate passed; no persistent or external process.

## Phase 128 — latest authoritative update

Phase 128 repaired the RD job generator
`jobs/2026-07-04_eventos-brief/flows/gen_packs.py` for MAK. It now resolves
the repository and asset inputs from `__file__`, avoids writes during import,
uses a local MAK scratch path and accepts bounded output directories. A fresh
`/tmp` run compiled and generated 3 job files, 2 SVG files and 4 HTML scratch
files with total `500000`; no live job or SVG output was modified and no old
Windows scratch path appeared. Evidence:
`context/PHASE128_RD_PACK_GENERATOR_LINUX_GATE.md` and `.csv`.

## Next concrete action

Register the job source/output ownership in the RD asset matrix and run the
remaining read-only asset index checks. Do not regenerate live deliverables or
delete related RD copies without a human delivery decision.

Last verified: 2026-08-15 America/Santiago — Phase 128 RD generator compile
and isolated Linux output gate passed; no persistent or external process.

## Phase 129 — latest authoritative update

Phase 129 validated the RD event-pack consumer chain without writing outputs:
the plano input, vector/mono logos, both editable SVGs and both `svgIndex.ts`
event URLs all existed. The canonical venv read-only check exited 0; the
generator input was 112615 bytes, logos 5142/3100 bytes and editable SVGs
23354 bytes each. No generator, browser, hub, PDF renderer, network,
database, provider or output writer ran. Evidence:
`context/PHASE129_RD_ASSET_CONSUMER_INDEX_GATE.md` and `.csv`.

## Next concrete action

Continue the RD asset audit with remaining asset families and delivery
manifests, then refresh the 13-objective matrix. Keep human deliverables,
templates, Blender/Adobe sources, generated outputs and WIN protected.

Last verified: 2026-08-15 America/Santiago — Phase 129 RD asset consumer
index gate passed; no persistent or external process.

## Phase 130 — latest authoritative update

Phase 130 checked every static SVG URL in
`web/src/data/svgIndex.ts` against `/home/mak/flujo/svg`. The read-only gate
exited 0 with 10 indexed URLs, 0 missing targets, 11 SVG files, 1 JSON master
and 4 directories. The only unindexed SVG is the supplement template
`svg/suplementos_rd/_plantilla/contraportada_cambios.svg`. No hub, browser,
generator, renderer, database, network or output writer ran. Evidence:
`context/PHASE130_SVG_SURFACE_INDEX_GATE.md` and `.csv`.

## Next concrete action

Compare the six non-indexed SVG files with job manifests and RD asset maps,
then refresh the duplicate/asset matrix. Preserve unindexed editable or
historical artifacts until a consumer decision exists.

Last verified: 2026-08-15 America/Santiago — Phase 130 SVG surface index gate
passed with zero broken static targets.

## Phase 131 — latest authoritative update

Phase 131 validated the RD supplements asset chain through existing FLUJO
consumers. `flujo suplementos list` exited 0 and read 8 approved supplements;
`flujo suplementos validate` on
`svg/suplementos_rd/09_contraportadas_dark/02_impulso.svg` exited 0 with
`2000x2800` and no mechanical findings. The unindexed
`_plantilla/contraportada_cambios.svg` is a live editable source referenced by
the CLI/config, not junk. No regeneration, file write, Illustrator, browser,
provider, network, database or service action ran. Evidence:
`context/PHASE131_SUPPLEMENTS_ASSET_CONSUMER_GATE.md` and `.csv`.

## Next concrete action

Refresh the objective matrix with the RD event and supplement asset gates,
then continue the remaining dependency and full-MAK read-only audit. Keep
actual field data, mutating generators, external tools, WIN and human
deliverables protected.

Last verified: 2026-08-15 America/Santiago — Phase 131 supplement asset list
and SVG validation passed; no persistent or external process.

## Phase 132 — latest authoritative update

Phase 132 refreshed the 13-objective matrix with the current foreground and
physical evidence. RD event generation, SVG index coverage and supplement
list/validation are now recorded under objective 6; code projection ownership
has zero remaining non-projection Python candidates in the four audited
families; cleanup has quarantined 92 `.DS_Store` files plus 7 exact shell
residues, with WIN untouched. Real field data, pytest, web Node/Rollup,
qwen-agent, provider-backed writers and Git application remain explicit open
gates. Evidence:
`context/PHASE132_OBJECTIVE_RECONCILIATION_REFRESH.md` and `.csv`.

## Next concrete action

Finish RD source/output/document ownership manifests, then close read-only
dependency and entrypoint gaps where the current environment supports them.
Keep external writers, real field data, provider calls, human deliverables,
WIN and Git application behind their existing gates.

Last verified: 2026-08-15 America/Santiago — Phase 132 objective matrix
refreshed through the RD asset gates; no persistent or external process.

## Phase 133 — latest authoritative update

Phase 133 closed the dependency checks supported by the current environment:
`python -m pip check` exited 0 with no broken requirements; imports of six
core FLUJO/MAK modules exited 0; and web `npm run typecheck` exited 0 with
`tsc --noEmit`. `pytest` and `qwen_agent` remain absent, while the web build
still has the documented Node/Rollup gate. No installation, provider,
database, service, network, output or Git action ran. Evidence:
`context/PHASE133_DEPENDENCY_READONLY_GATE.md` and `.csv`.

## Next concrete action

Continue the full-MAK read-only audit and source/output ownership mapping;
revisit pytest, qwen-agent and web-build gates only when the required runtime
authority exists. Preserve external writers, field data, human deliverables,
WIN and Git application.

Last verified: 2026-08-15 America/Santiago — Phase 133 dependency/import and
web typecheck gates passed; environment gates remain explicit.

## Phase 134 — latest authoritative update

Phase 134 ran the broad foreground verifier after the RD asset changes:
`/home/mak/venvs/flujo/bin/flujo verify --no-pytest` exited 0, including
compile/health/version checks and temporary hub smoke (`version=0.56.1`). The
post-run process gate found no prohibited Flujo, hub, Ollama, Blender, media,
generator or micelio process. Pytest, provider-backed writers, real field data
and the Node production build remain open and are not hidden by this result.
Evidence: `context/PHASE134_FULL_VERIFY_NO_PYTEST_GATE.md` and `.csv`.

## Next concrete action

Finish the remaining source/output ownership and cleanup review, then prepare
the final branch proposal against the still-open gates. Keep Git application
and external runtime actions separate from this verification.

Last verified: 2026-08-15 America/Santiago — Phase 134 full verify without
pytest passed; no persistent or external process.

## Phase 135 — latest authoritative update

Phase 135 refreshed the Git branch proposal without inspecting or mutating Git.
The proposal now separates ownership, pure tool consolidation, RD assets, real
data, mutators, EVENTO automation, dependency gates, confirmed-junk quarantine
and release verification into disjoint slices with explicit gates. It records
the current partial/blocked statuses instead of presenting reports as green.
Evidence: `context/PHASE135_GIT_BRANCH_PROPOSAL_REFRESH.md` and `.csv`.

## Next concrete action

Complete the remaining physical ownership/cleanup matrix and re-audit the
13-objective evidence. Only after that, and only if explicitly requested,
apply the proposed Git branch system. Continue local read-only checks and
bounded asset work while external data, provider, pytest, qwen-agent and web
runtime gates remain open.

Last verified: 2026-08-15 America/Santiago — Phase 135 branch proposal
refreshed; no Git operation or external process.

## Phase 136 — latest authoritative update

Phase 136 gated the live root departments `vigia` and `lenguaje` read-only.
AST passed for `vigia` 1/1 and `lenguaje` 4/4 files; `vigia.py --help` exited
0; and `lenguaje/medir.py` measured the bilingual fixture with exit 0 (2354
words, score 96). Writer, cron, notification and model paths were not
executed, and no state/lock/ledger/output changed. Evidence:
`context/PHASE136_VIGIA_LANGUAGE_READONLY_GATE.md` and `.csv`.

## Next concrete action

Add these department statuses to the objective matrix and continue the final
root-surface inventory. Preserve state/locks and do not enable cron or watcher
execution as part of migration.

Last verified: 2026-08-15 America/Santiago — Phase 136 vigia/lenguaje
read-only gates passed; mutating and cron paths remain gated.

## Phase 137 — latest authoritative update

Phase 137 classified lateral `/home/mak/*` surfaces so they are not confused
with the canonical MAK runtime: `flujo-deploy`, `vibecodeine`, `actions-runner`,
`bucle`, discarded `n8n-local`, `searxng`, `venv-providers`, test fixtures,
`vigia` and `lenguaje`. The inventory exited 0; credential contents, runner
state and provider files were not opened. No side surface, service, runner,
n8n, SearXNG, provider or Git action ran. Evidence:
`context/PHASE137_SIDE_SURFACE_BOUNDARY_AUDIT.md` and `.csv`.

## Next concrete action

Use the boundary map in the final folder/cleanup matrix. Continue only with
MAK consumers and exact confirmed junk; keep side repositories, credentials,
runner logs, provider environments and discarded-service secrets protected.

Last verified: 2026-08-15 America/Santiago — Phase 137 side-surface boundary
audit passed; no persistent or external process.

## Phase 138 — latest authoritative update

Phase 138 mapped the remaining large physical MAK containers by role and
observed size: RD 57G, curatoria_inbox 173G, portfolio media 5.5G, models
206M, state 301M, indexes 113M, backups 166M, quarantine 185M, rollback 240M
and tmp 872K. The bounded inventory exited 0 after reading only sizes and
shallow names; media, model weights, credentials, backups, indexes, rollback
trees and WIN were not opened. No large surface was classified as junk by
size. Evidence: `context/PHASE138_PHYSICAL_ARCHITECTURE_SURFACE_MAP.md` and
`.csv`.

## Next concrete action

Use this map to finish the folder architecture matrix and select only small,
path-specific cleanup candidates. Do not copy or recursively reorganize the
large media/evidence surfaces.

Last verified: 2026-08-15 America/Santiago — Phase 138 physical architecture
surface map passed; no persistent or external process.

## Phase 139 — latest authoritative update

Phase 139 quarantined the two dated temporary conductor-shadow directories
from `/home/mak/tmp`. A first preflight was corrected because the snapshots
contained nested package trees; no action occurred in that failed attempt.
The exact second move exited 0, preserving 34 files as complete units under
`context/quarantine/phase139_tmp_conductor_shadow`; `/home/mak/tmp` now has
zero files and subdirectories. No database, source, evidence, output,
provider, service or WIN path was touched. Evidence:
`context/PHASE139_TMP_CONDUCTOR_SHADOW_QUARANTINE.md` and `.csv`.

## Next concrete action

Re-run post-cleanup health and process gates, then refresh the physical
architecture/objective matrix. Continue only with exact path-specific cleanup
or consumer-backed ownership work.

Last verified: 2026-08-15 America/Santiago — Phase 139 reversible quarantine
of 2 temporary conductor-shadow directories passed; no persistent process.

## Phase 140 — latest authoritative update

Phase 140 validated the post-cleanup baseline: `flujo health` exited 0,
`flujo verify --no-pytest` exited 0 with temporary hub smoke at version
`0.56.1`, and the filtered process gate found no prohibited Flujo/hub/Ollama/
Blender/media/generator/micelio/conductor process. No live job, database,
ledger, source, output, provider, external service or WIN path changed.
Evidence: `context/PHASE140_POST_CLEANUP_VERIFY_GATE.md` and `.csv`.

## Next concrete action

Refresh the current physical architecture/objective matrix and continue the
remaining consumer-backed ownership review. Do not widen cleanup without a new
exact-path gate.

Last verified: 2026-08-15 America/Santiago — Phase 140 post-cleanup health,
verify and process gates passed.

## Phase 141 — latest authoritative update

Phase 141 refreshed the current 13-objective reconciliation with the new
vigia/lenguaje gates, side-surface boundaries, RD asset chain and three
reversible cleanup quarantines (92 `.DS_Store`, 7 shell residues, 2 temporary
conductor-shadow directories). The matrix still marks real data, pytest,
provider writers, mutators, web runtime and Git as open gates; no requirement
was falsely closed. Evidence:
`context/PHASE141_OBJECTIVE_RECONCILIATION_CURRENT.md` and `.csv`.

## Next concrete action

Finish RD source/output/delivery manifests and semantic document decisions,
then run final verification after any authorized change. Keep real data,
provider writers, mutators, environment dependencies, side surfaces, WIN and
Git application behind their explicit gates.

Last verified: 2026-08-15 America/Santiago — Phase 141 current objective
matrix refreshed; no persistent or external process.

## Phase 142 — latest authoritative update

Phase 142 removed the duplicate hardcoded RD tariff from
`web/src/rdBrand.ts`; the web now imports canonical `data/rd_packs.json` while
preserving the runtime override/reset APIs. The first path typo was caught by
TypeScript (`exit 2`) and corrected without output changes. The corrected
`npm run typecheck` exited 0 and JSON parity fixtures confirmed pack order,
prices and proportions. Evidence:
`context/PHASE142_RD_TARIFF_SINGLE_SOURCE_MERGE.md` and `.csv`.

## Next concrete action

Run post-merge FLUJO verification and refresh the objective matrix. Keep the
production web build separately gated by Node/Rollup compatibility.

Last verified: 2026-08-15 America/Santiago — Phase 142 RD tariff single-source
merge and web typecheck passed; no persistent or external process.

## Phase 143 — latest authoritative update

Phase 143 ran post-merge verification: `flujo verify --no-pytest` exited 0
with compile/health/version and temporary hub smoke at `0.56.1`; `pip check`
exited 0 with no broken requirements; and the filtered process gate found no
prohibited process. The web TypeScript gate remains green from Phase 142. No
database, ledger, job output, provider, external service or Git state changed.
Evidence: `context/PHASE143_POST_TARIFF_VERIFY_GATE.md` and `.csv`.

## Next concrete action

Refresh the objective matrix and continue remaining semantic
document/source-ownership review. Keep external data, writers, environment
gates, WIN and Git application explicit.

Last verified: 2026-08-15 America/Santiago — Phase 143 post-tariff verify and
dependency gates passed.

## Phase 144 — latest authoritative update

Phase 144 refreshed the 13-objective matrix after the real RD tariff
single-source merge. Objective 10 now records the web tariff consolidation in
addition to the closed Python projection families; objective 7 separates the
green core/typecheck gates from Node/Rollup, pytest and qwen-agent gaps. No
objective was promoted to complete without its required evidence. Evidence:
`context/PHASE144_OBJECTIVE_RECONCILIATION_AFTER_TARIFF.md` and `.csv`.

## Next concrete action

Finish RD source/output/delivery and semantic document manifests. Keep field
data, provider writers, mutators, unavailable dependencies, human deliverables,
WIN and Git application behind explicit gates; use reversible quarantine for
any new exact cleanup candidate.

Last verified: 2026-08-15 America/Santiago — Phase 144 objective matrix
refreshed after tariff merge; no persistent or external process.

## Phase 145 — latest authoritative update

Phase 145 reconciled every RD-named database found from `/home/mak/*` within
the bounded local inventory. `/home/mak/flujo/data/rd.db` is the only active
canonical projection; `/home/mak/flujo/data/rd_datos.db` is a separate,
privacy-first field accumulator with an intact four-table schema and zero real
rows. The two must not be merged. WIN, state and temporary integration copies
were integrity-checked read-only and classified as historical/recovery evidence;
none was promoted to a runtime source and none was deleted. The read-only
field summary returned zero totals and the mandatory disclaimer with exit 0.
Evidence: `context/PHASE145_RD_DATABASE_SOURCE_RECONCILIATION.md` and `.csv`.

## Next concrete action

Continue with the remaining RD source/output/delivery manifest and semantic
document ownership review, starting at `/home/mak/*` and narrowing to the
canonical MAK consumer. Keep `rd_datos.db` empty until an authorized real-data
handoff; keep WIN/state/log database copies protected; use reversible quarantine
only for a new exact confirmed junk path. After the next bounded ownership
slice, run the existing foreground verification and refresh the objective
matrix. Do not apply Git branches or delete evidence.

Last verified: 2026-08-15 America/Santiago — Phase 145 RD database source
reconciliation passed; no persistent or external process.

## Phase 146 — latest authoritative update

Phase 146 removed the second hardcoded RD tariff from
`jobs/2026-07-04_eventos-brief/flows/gen_packs.py`. The generator now consumes
`data/rd_packs.json` for pack names, prices, inclusions, complete-pack
proportions and add-on deltas. `py_compile` and an isolated generation run both
exited 0; the generated breakdown totals 500000 CLP and matches the canonical
60/14/10/9/7 proportions. Existing job/RD PDFs, JSON, SVGs and WIN/history
were not overwritten or deleted; old delivery variants remain protected until
their promotion gate. Evidence: `context/PHASE146_RD_GENERATOR_CANONICAL_TARIFF_GATE.md`
and `.csv`.

## Next concrete action

Review the isolated canonical generator output against the current RD delivery
surface, then promote only explicitly identified active job/delivery files if
the output contract is satisfied. After promotion (or a documented no-promote
decision), run `flujo verify --no-pytest` and the web typecheck, then refresh
the objective matrix. Continue classifying semantic documents and equivalent
tools by consumer; preserve human deliverables, evidence, state, WIN and
database snapshots. Do not merge `rd.db` with `rd_datos.db`, ingest field data,
apply Git branches, or delete by hash alone.

Last verified: 2026-08-15 America/Santiago — Phase 146 RD generator canonical
tariff gate passed; no persistent or external process.

## Phase 147 — latest authoritative update

Phase 147 ran the post-generator gates with the configured runtime:
`/home/mak/venvs/flujo/bin/flujo verify --no-pytest` exited 0, including
compileall, health, version and temporary hub smoke; `npm run typecheck` exited
0; and the bounded process check found no persistent hub, serve, generator or
Vite process. Two wrong invokers were corrected without mutation (`flujo` was
not on PATH; the legacy dispatcher has no `verify` command). Evidence:
`context/PHASE147_POST_GENERATOR_VERIFY_GATE.md` and `.csv`.

## Next concrete action

Run the bounded promotion review for the isolated canonical RD generator
output. Enumerate exact active job/delivery paths, compare semantics and
provenance, and either promote only an explicitly approved set with backups or
record `NO_PROMOTE`. Then refresh the objective matrix and continue to the
next consumer-backed ownership slice. Keep human deliverables, WIN, databases,
state and evidence protected; no Git application or field-data ingestion.

Last verified: 2026-08-15 America/Santiago — Phase 147 post-generator
verification passed; no persistent or external process.

## Phase 148 — latest authoritative update

Phase 148 promoted the canonical RD generator outputs. The five stale derived
JSON/SVG files owned by `gen_packs.py` were moved individually to
`context/quarantine/phase148_rd_precanonical_outputs/` for rollback, then
regenerated at their active job/SVG consumer paths. PDFs, human RD deliveries,
databases, WIN, source documents and unrelated assets were not touched.
The generated JSON contract passed; post-promotion
`/home/mak/venvs/flujo/bin/flujo verify --no-pytest` exited 0, web typecheck
exited 0, and the process gate found zero persistent matching processes.
Evidence: `context/PHASE148_RD_GENERATED_OUTPUT_PROMOTION.md` and `.csv`.

## Next concrete action

Refresh the 13-objective matrix with the completed canonical generator/output
slice, then select the next bounded consumer-backed tool family from the
remaining MAK surface. Continue the same rule: start at `/home/mak/*`, identify
the real consumer and source, merge only semantic duplicates, quarantine exact
confirmed junk reversibly, and validate foreground. Keep PDFs/human delivery,
field data, providers, mutators, side surfaces, WIN and Git application behind
their explicit gates.

Last verified: 2026-08-15 America/Santiago — Phase 148 RD generated output
promotion passed; rollback evidence preserved; no persistent or external
process.

## Phase 149 — latest authoritative update

Phase 149 refreshed the 13-objective matrix after the RD generator and derived
output promotion. Objective 6 now records the canonical generator as verified
partial; objective 10 records the Python/web/generator tariff consolidation;
objective 9 keeps human PDFs and delivery variants as semantic decisions, not
hash duplicates; objective 12 records the reversible output quarantine while
WIN remains historical and untouched. Evidence:
`context/PHASE149_OBJECTIVE_RECONCILIATION_AFTER_RD_OUTPUT.md` and `.csv`.

## Next concrete action

Finish the bounded RD PDF/human-delivery manifest without replacing files by
hash alone. Start at `/home/mak/*`, narrow to active RD/FLUJO consumers, map
source -> generator -> derived output -> human delivery, and record a
promote/no-promote decision. Then select the next active MAK consumer family,
run foreground verification, and update this handoff. Keep field data,
providers, mutators, unavailable dependencies, side surfaces, WIN and Git
application behind their gates; do not use SSH, services or recursive copies.

Last verified: 2026-08-15 America/Santiago — Phase 149 objective matrix
refreshed after RD output promotion; no persistent or external process.

## Phase 150 — latest authoritative update

Phase 150 completed the bounded RD PDF/human-delivery manifest. The active
JSON/SVG chain is canonical and promoted; the existing PDFs are older human or
Windows delivery snapshots with distinct provenance. Exact hashes were
classified by role, not deleted. `brief.yaml` and `resultado.md` contain a
metadata conflict (delivered vs not activated and old pack wording), so they
were not silently rewritten. Read-only `pdfinfo`, `pdftotext`, hashes and
comparisons passed. MAK has no Edge/Chromium/WeasyPrint renderer, so PDF
promotion is explicitly `NO_PROMOTE`; no files changed. Evidence:
`context/PHASE150_RD_PDF_DELIVERY_MANIFEST.md` and `.csv`.

## Next concrete action

Select the next active MAK consumer slice outside the blocked human-PDF gate.
Start at `/home/mak/*`, identify a real source/consumer/output chain, merge only
semantic duplicates, and validate foreground. The likely open candidates are
the non-serve CLI/runtime gates or the local automation contract; choose from
physical evidence rather than inventing a new framework. Keep field data,
providers, mutators, side surfaces, WIN and Git application behind their
explicit gates.

Last verified: 2026-08-15 America/Santiago — Phase 150 RD PDF manifest passed;
PDF promotion remains explicitly gated; no persistent or external process.

## Phase 151 — latest authoritative update

Phase 151 verified the active non-serve FLUJO CLI at
`/home/mak/venvs/flujo/bin/flujo`: version, health, doctor, supplements list,
RD command help, `rd-db packs` and `rd-db eventos` all exited 0. The launcher
resolves to `/home/mak/flujo/src/flujo`; the legacy `scripts/flujo.py` remains a
tested retired-command boundary, not a competing runtime. `rd.db` stats were
unchanged before/after the read commands, and no persistent process remained.
Evidence: `context/PHASE151_NONSERVE_CLI_FOREGROUND_GATE.md` and `.csv`.

## Next concrete action

Inspect the local FLUJO automation contract and execute its safe dry-run/read
path. Keep provider-backed email/issue writers and external mutations gated;
use the existing EVENTO -> issue -> URL contract and verify exact local
artifacts. Then update the objective matrix and continue to the next unresolved
MAK consumer.

Last verified: 2026-08-15 America/Santiago — Phase 151 non-serve CLI gate
passed; pytest remains unavailable; no persistent or external process.

## Phase 152 — latest authoritative update

Phase 152 validated the local FLUJO automation contract in an isolated
temporary workspace. `run_pending_flyers()` processed one fixture job, created
`brief.yaml` and `reporte_job.md`, and left the state at `pendiente_datos`; the
assertions passed with exit 0. No live job, database, issue, email, provider,
URL or permanent process was touched. The Gmail -> issue -> URL path remains
external and explicitly gated. Evidence:
`context/PHASE152_LOCAL_AUTOMATION_FIXTURE_GATE.md` and `.csv`.

## Next concrete action

Refresh the objective matrix with Phases 150–152, then select the next
unresolved MAK consumer/dependency slice. Prefer a real local source and
foreground output; keep provider writers, field-data ingestion, mutators,
unavailable PDF renderer, side surfaces, WIN and Git application behind their
explicit gates.

Last verified: 2026-08-15 America/Santiago — Phase 152 local automation
fixture gate passed; no persistent or external process.

## Phase 153 — latest authoritative update

Phase 153 refreshed the 13-objective matrix with the RD PDF manifest, the
canonical generator/output promotion, the non-serve CLI foreground gates and
the isolated local automation fixture. No deferred external writer, XIO, n8n,
human-PDF renderer or pytest gap was falsely promoted to complete. Evidence:
`context/PHASE153_OBJECTIVE_RECONCILIATION_AFTER_CLI_AUTOMATION.md` and `.csv`.

## Next concrete action

Select the next active MAK consumer/dependency slice from `/home/mak/*`,
excluding deferred external writers, XIO, n8n and human-PDF rendering. Use a
real source/consumer/output chain, make the smallest needed integration or
compatibility edit, validate it in foreground, and update this handoff. Keep
WIN, field data, providers, mutators, side surfaces and Git application behind
their explicit gates.

Last verified: 2026-08-15 America/Santiago — Phase 153 objective matrix
refreshed after CLI and local automation gates; no persistent or external
process.

## Phase 154 — latest authoritative update

Phase 154 merged the real issue-bridge projection duplication. The paused
runtime target `/home/mak/plataforma/puente_issues.py` is now a wrapper to the
canonical `/home/mak/flujo/cultura/mak_plataforma/puente_issues.py`; the former
28 KB copy is preserved in reversible quarantine. Wrapper/canonical help matched,
both compiled, and a safe stubbed canonical dry-run returned 0 with no issues.
No cron was created/enabled, no external writer ran, and no WIN/deployment copy
was touched. Evidence: `context/PHASE154_ISSUE_BRIDGE_PROJECTION_MERGE.md` and
`.csv`.

## Next concrete action

Run the relevant core verification and refresh the objective matrix after the
bridge projection merge. Then select the next active MAK department/tool
surface from `/home/mak/*`; keep cron, provider writers, field data, mutators,
PDF rendering, side surfaces, WIN and Git application gated.

Last verified: 2026-08-15 America/Santiago — Phase 154 issue-bridge projection
merge passed; no persistent or external process.

## Phase 155 — latest authoritative update

Phase 155 ran post-bridge verification: core `flujo verify --no-pytest` exited
0, web typecheck exited 0, and no bridge/hub/serve/generator/Vite process
remained. The objective matrix now records the issue bridge and tariff merges
without falsely closing real data, provider writers, PDF rendering, pytest,
folder placement or Git. Evidence:
`context/PHASE155_POST_BRIDGE_VERIFY_AND_OBJECTIVE_MATRIX.md` and `.csv`.

## Next concrete action

Select the next active MAK department/tool or dependency slice from
`/home/mak/*`, using a real consumer and output. Exclude already consolidated
tariff/bridge projections, deferred external writers, XIO, n8n and the
unavailable PDF renderer. Validate any change foreground and preserve WIN,
field data, mutator evidence, side surfaces and rollback files.

Last verified: 2026-08-15 America/Santiago — Phase 155 post-bridge verification
and matrix refresh passed; no persistent or external process.

## Phase 156 — latest authoritative update

Phase 156 audited the physical `plataforma` projection surface from
`/home/mak/*`: 46 code files were exact, 15 differed, and the root-only
remainder was classified as state, environment, logs, locks or rollback
evidence. Bulk replacement was rejected. The next bounded target was selected
as `material.py`, which has a real queue consumer and a read-only `--contar`
contract. Evidence: `context/PHASE156_PLATFORM_PROJECTION_AUDIT.md` and `.csv`.

## Phase 157 — latest authoritative update

Phase 157 consolidated `/home/mak/plataforma/material.py` into a wrapper for
the canonical `/home/mak/flujo/cultura/mak_plataforma/material.py`. The exact
old target was preserved in quarantine. Both files compiled; canonical and
wrapper `--contar` output matched at `3269` queued tasks; the queue hash and
metadata stayed unchanged; and no matching process remained. The
`MAK-MATERIAL` cron line is only a paused template/installed entry and was not
enabled. Evidence: `context/PHASE157_MATERIAL_PROJECTION_MERGE.md` and `.csv`.

## Next concrete action

Inspect the next real consumer-backed MAK platform/departments slice from
`/home/mak/*`, excluding state/evidence, the consolidated tariff and issue
bridge projections, deferred external writers, XIO, n8n and unavailable PDF
rendering. Prefer a bounded non-mutating contract. If no safe read path exists,
perform static/compile validation and document the mutation boundary before
editing. Preserve field data, providers, mutators, side surfaces, WIN and all
rollback evidence; do not enable cron or start services.

Last verified: 2026-08-15 America/Santiago — Phase 157 material projection
merge passed; queue unchanged; no persistent or external process.

## Phase 158 — latest authoritative update

Phase 158 consolidated the exact `latido.py` runtime projection into a wrapper
for the canonical source. The old 6,014-byte target is preserved in
`context/quarantine/phase158_latido_projection/`. Both files compiled. A
foreground isolated-HOME harness stubbed only the loopback request and load
average; canonical and wrapper each produced the same heartbeat state/index/log
contract without touching `/home/mak`. The installed `MAK-LATIDO` cron remains
paused and no process or service was started. Evidence:
`context/PHASE158_LATIDO_PROJECTION_GATE.md` and `.csv`.

## Next concrete action

Inspect the next real consumer-backed MAK platform slice from `/home/mak/*`.
The remaining exact operational projections include `vigilar_red.py`,
`backup.sh` and `watchdog_mak.sh`, but their network, backup and systemd repair
boundaries must stay explicit. Prefer static/compile or isolated fixture gates;
do not execute live cron behavior, enable cron, start services, touch field
data/providers/mutators, alter side surfaces or use WIN/Git as runtime.

Last verified: 2026-08-15 America/Santiago — Phase 158 latido projection
merge passed; isolated contract equal; no persistent or external process.

## Phase 159 — latest authoritative update

Phase 159 consolidated the exact `vigilar_red.py` runtime projection into a
canonical-source wrapper. The old target is preserved in
`context/quarantine/phase159_vigilar_red_projection/`. Both files compiled and
the wrapper import contract resolved the canonical path without invoking its
network/logging `main()` path. The `MAK-VIGILAR` cron remains paused; no `ss`
scan, ntfy call, log write, service or persistent process occurred. Evidence:
`context/PHASE159_VIGILAR_RED_PROJECTION_GATE.md` and `.csv`.

## Next concrete action

Inspect the remaining exact operational projections from `/home/mak/*`.
`backup.sh` and `watchdog_mak.sh` are the next candidates, but they write
backups or can repair/start systemd units. Keep them behind static/shell syntax
and dependency gates unless an isolated fixture can prove behavior without
touching real data or services. Continue with the smallest reversible wrapper
where the consumer is real; preserve field data, providers, mutators, side
surfaces, WIN and rollback evidence, and do not enable cron.

Last verified: 2026-08-15 America/Santiago — Phase 159 vigilar_red projection
merge passed; live network path not called; no persistent process.

## Phase 160 — latest authoritative update

Phase 160 consolidated the exact `backup.sh` runtime projection into an
executable wrapper for the canonical source. The previous target is preserved
in `context/quarantine/phase160_backup_projection/`. Both shell files passed
`bash -n`; isolated temporary-HOME fixtures showed direct and wrapped scripts
create the same non-empty backup artifact; no real backup/retention ran and no
backup process remained. The target mode is `0755` because its paused cron
declaration invokes it directly. Evidence:
`context/PHASE160_BACKUP_PROJECTION_GATE.md` and `.csv`.

## Next concrete action

Inspect and gate `watchdog_mak.sh` from `/home/mak/*`. It is an exact
source/runtime projection with a paused direct cron consumer, but it can call
`guardia.py`, `curl` and `systemctl --user start/restart`. Consolidate only via
a reversible wrapper after `bash -n` and static dependency/contract checks;
do not execute it, enable cron, start/restart services, touch logs/data or
modify side surfaces. Preserve WIN and rollback evidence.

Last verified: 2026-08-15 America/Santiago — Phase 160 backup projection merge
passed; isolated artifact gate passed; no persistent process.

## Phase 161 — latest authoritative update

Phase 161 consolidated the exact `watchdog_mak.sh` runtime projection into an
executable wrapper for the canonical source. The old target is preserved in
`context/quarantine/phase161_watchdog_projection/`. Both shell files passed
`bash -n`; the declared `flock`, `timeout`, `curl`, `systemctl`, `guardia.py`
and service-unit dependencies were verified present/readable. No watchdog,
systemd, HTTP, lock or log behavior was invoked, and no process remained.
Evidence: `context/PHASE161_WATCHDOG_PROJECTION_GATE.md` and `.csv`.

## Next concrete action

Refresh the objective/integration matrix with Phases 156–161, then inspect the
next active MAK consumer family outside `plataforma` from `/home/mak/*`.
Prioritize a real department/tool output and compare its canonical source with
runtime projection before editing. Keep the now-consolidated projections,
field data, providers, mutators, side surfaces, WIN, PDF gate and Git
application classified; do not enable cron or start services.

Last verified: 2026-08-15 America/Santiago — Phase 161 watchdog projection
merge passed; live repair path not called; no persistent process.

## Phase 162 — latest authoritative update

Phase 162 reconciled the objective matrix after the platform projection family:
`material.py`, `latido.py`, `vigilar_red.py`, `backup.sh` and
`watchdog_mak.sh` now have canonical-source runtime projections with separate
rollback evidence. RD field data, mutators, PDF rendering, provider conflicts,
department surfaces, destructive cleanup and Git remain explicitly open. The
next department is the physical research pair. Evidence:
`context/PHASE162_OBJECTIVE_RECONCILIATION_AFTER_PLATFORM_PROJECTIONS.md` and
`.csv`.

## Next concrete action

Verify `/home/mak/research/research.py` as the next real consumer-backed FLUJO
department entrypoint. Begin with compile/import/help-only checks, confirm its
canonical source and expected output contract, and do not start
`mak-interfaz`, call providers, write research artifacts, enable cron or touch
WIN/Git. After that choose the smallest unresolved research slice and update
the handoff.

Last verified: 2026-08-15 America/Santiago — Phase 162 objective matrix
reconciled after platform projection merges; no persistent process.

## Phase 163 — latest authoritative update

Phase 163 verified the existing research runtime projection. Canonical and
runtime `research.py` plus both `research_lib.py` files compiled; canonical and
runtime `research.py --help` outputs matched byte-for-byte and exposed the same
command contract. No service, provider, credential, research artifact or
persistent process was touched. Evidence:
`context/PHASE163_RESEARCH_ENTRYPOINT_GATE.md` and `.csv`.

## Next concrete action

Select the next unresolved research consumer from `/home/mak/research` and its
canonical `/home/mak/flujo/cultura/mak_research` source. Prefer a local
read-only/fixture contract such as corpus/index/statistics; leave provider
calls, service startup, report writes, cron, field data, mutators, side
surfaces, WIN and Git application gated. If the runtime already projects the
canonical source, verify its real command/output rather than duplicating it.

Last verified: 2026-08-15 America/Santiago — Phase 163 research entrypoint
gate passed; no provider call or persistent process.

## Phase 164 — latest authoritative update

Phase 164 verified the exact source/runtime `estadisticas.py` research
consumer. Both compiled; an isolated metadata fixture produced identical
source/runtime usage summaries and exit 0. The real department `USO.md` files
were not rewritten. This pair remains intentionally data-bound because its
`ROOT` controls the owning input/output folders; no wrapper was introduced.
Evidence: `context/PHASE164_RESEARCH_STATISTICS_FIXTURE_GATE.md` and `.csv`.

## Next concrete action

Continue through the research department with a real local read-only consumer,
prioritizing index/statistics/corpus inspection. For any exact pair whose code
binds to its own `ROOT`, keep the copies separate unless a data-root contract
is first proven. Avoid provider calls, service startup, report writes, cron,
field data, mutators, side surfaces, WIN and Git application.

Last verified: 2026-08-15 America/Santiago — Phase 164 research statistics
fixture gate passed; real research artifacts unchanged; no persistent process.

## Phase 165 — latest authoritative update

Phase 165 verified the data-bound research `indice.py` and `digest.py`
consumers. Both source/runtime pairs compiled; isolated fixtures generated
identical indexes and digest outputs with exit 0. Real research artifacts were
not rewritten, and no provider/network/service process ran. These exact copies
remain separate because each binds `ROOT` to its owning department data.
Evidence: `context/PHASE165_RESEARCH_DERIVED_READS_GATE.md` and `.csv`.

## Next concrete action

Find a path-independent research consumer or an explicit data-root contract in
`/home/mak/research` and `/home/mak/flujo/cultura/mak_research`. Prefer shared
library/import/CLI verification before any report-writing path. Do not create
wrappers that redirect department data, and keep providers, service startup,
cron, field data, mutators, side surfaces, WIN and Git application gated.

Last verified: 2026-08-15 America/Santiago — Phase 165 research derived-read
fixtures passed; real research artifacts unchanged; no persistent process.

## Phase 166 — latest authoritative update

Phase 166 verified the real curatoria triangulation consumer. Canonical and
runtime `triangular.py` compiled; an isolated fixture with malformed input,
RD/non-RD rows, known producer and discovery candidate produced identical
two-row queues with exit 0. Real fichas/triangulation data, research providers
and persistent processes were untouched. The exact copies remain separate
because their input/output roots are data-bound. Evidence:
`context/PHASE166_CURATORIA_TRIANGULATION_FIXTURE_GATE.md` and `.csv`.

## Next concrete action

Continue through curatoria with the project-diagnostic consumer and its
SQLite/JSON derived output contract. Use a temporary fixture only, validate
source/runtime behavior and rollback shape, and do not run against real media,
SQLite data, GPU perception, guardia, providers, mutators, cron, WIN or Git.

Last verified: 2026-08-15 America/Santiago — Phase 166 curatoria triangulation
fixture gate passed; real data unchanged; no persistent process.

## Phase 167 — latest authoritative update

Phase 167 verified the curatoria project-diagnostic consumer. Canonical and
runtime `diagnostico_proyectos.py` compiled; a temporary SQLite fixture was
processed through the real CLI contract and both produced identical six-file
outputs with exit 0, including one project/family/representative and the
editable-first strategy. No real SQLite/media/ledger/provider/GPU artifact or
persistent process was touched. Evidence:
`context/PHASE167_CURATORIA_DIAGNOSTIC_FIXTURE_GATE.md` and `.csv`.

## Next concrete action

Continue the physical department audit from `/home/mak/*` with the next
unresolved curatoria consumer or move to `/home/mak/codex` if curatoria's next
candidate is only a guardia/GPU mutator. Prefer a local fixture/read-only
contract, preserve data-bound roots, and keep real media, SQLite writes,
perception, providers, cron, services, mutators, side surfaces, WIN and Git
application gated.

Last verified: 2026-08-15 America/Santiago — Phase 167 curatoria diagnostic
fixture gate passed; real data unchanged; no persistent process.

## Phase 168 — latest authoritative update

Phase 168 verified the Codex semantic engine. All canonical/runtime
`motor_semantico` files compiled; the source and runtime compiler CLIs produced
byte-identical SVG from the same temporary semantic specification, exit 0,
`3802` bytes and the expected viewBox. Real Codex pieces, manifests, providers,
workers, services and persistent processes were untouched. Evidence:
`context/PHASE168_CODEX_SEMANTIC_ENGINE_FIXTURE_GATE.md` and `.csv`.

## Next concrete action

Inspect the Codex job/worker boundary at
`/home/mak/flujo/cultura/mak_codex/codex_lib.py`, `worker_codex.py` and their
runtime projections. Start with compile/import/help and an isolated local
fixture; do not call LLM providers, launch workers/services, write real jobs or
pieces, enable cron, touch field data, mutators, side surfaces, WIN or Git.

Last verified: 2026-08-15 America/Santiago — Phase 168 Codex semantic-engine
fixture gate passed; no provider or persistent process.

## Phase 169 — latest authoritative update

Phase 169 verified the Codex library/worker boundary. Canonical and runtime
`codex_lib.py` and `worker_codex.py` compiled; coder-chain parsing matched,
invalid keys fell back safely, and worker unknown-mode/out-of-scope-path
rejections occurred before provider/subprocess work. No LLM, Ollama, NIM,
Watson, lock, event, job, service or persistent process was started. Evidence:
`context/PHASE169_CODEX_JOB_BOUNDARY_GATE.md` and `.csv`.

## Next concrete action

Validate the local Codex quality path at
`/home/mak/flujo/cultura/mak_codex/calidad_loop.py` or `testear.py` using a
temporary fixture and no provider. Confirm its input/output contract, preserve
real jobs/pieces/manifests, and keep worker launch, GPU, cron, services,
providers, field data, mutators, side surfaces, WIN and Git application gated.

Last verified: 2026-08-15 America/Santiago — Phase 169 Codex job boundary
gate passed; no provider or persistent process.

## Phase 170 — latest authoritative update

Phase 170 verified the Codex quality loop. Canonical and runtime
`calidad_loop.py` compiled; a temporary jobs/delivery/backlog fixture produced
identical `CALIDAD_LOOP.md` output with exit 0 and expected metrics. Real jobs,
delivery state, backlog, pieces, providers and services were untouched.
Evidence: `context/PHASE170_CODEX_QUALITY_FIXTURE_GATE.md` and `.csv`.

## Next concrete action

Validate the local Codex `testear.py` path with a temporary pure-Python piece
and no provider. Confirm syntax/smoke input/output, preserve real pieces and
manifests, and do not launch workers, execute generated code outside the
fixture, enable cron, start services, call providers, touch field data,
mutators, side surfaces, WIN or Git.

Last verified: 2026-08-15 America/Santiago — Phase 170 Codex quality fixture
gate passed; no provider or persistent process.

## Phase 171 — latest authoritative update

Phase 171 fixed a real Codex test gate bug in the canonical
`cultura/mak_codex/testear.py`: `python -I -m unittest` excluded the temporary
module directory and caused valid generated tests to fail before execution.
The source now uses an isolated `-c` runner with an explicit temporary path;
the runtime wrapper was unchanged. Both source/runtime fake-coder fixtures now
execute successfully (`OK`, rc 0), compile, and leave no process. No provider,
real piece, manifest, worker or service was touched. Evidence:
`context/PHASE171_CODEX_TESTEAR_FIXTURE_GATE.md` and `.csv`.

## Next concrete action

Run core `flujo` compile/health/web checks after the `testear.py` fix. Then
inspect `generar.py` and `iconos.py` as the next Codex consumers, using only
provider-free fixtures or help/compile paths. Preserve real Codex jobs,
pieces, manifests and rollback evidence; do not launch workers, call
providers, enable cron, start services, touch field data, mutators, side
surfaces, WIN or Git.

Last verified: 2026-08-15 America/Santiago — Phase 171 testear isolation fix
and fixture gate passed; no provider or persistent process.

## Phase 172 — latest authoritative update

Phase 172 revalidated the core surface after the `testear.py` fix:
`/home/mak/venvs/flujo/bin/flujo verify --no-pytest` exited 0, including
compileall/health/version/hub smoke, and `npm run typecheck` from the actual
`/home/mak/flujo/web` root exited 0. An initial npm call from the repo root
returned the expected missing-`package.json` error and changed nothing; it was
corrected by using the web root. No persistent process remained. Evidence:
`context/PHASE172_POST_TESTEAR_CORE_VERIFY.md` and `.csv`.

## Next concrete action

Inspect Codex `generar.py` and `iconos.py` from their canonical/runtime paths.
Use provider-free help/import or isolated fixtures, preserve real pieces and
manifests, and do not launch workers, call providers, enable cron, start
services, touch field data, mutators, side surfaces, WIN or Git.

Last verified: 2026-08-15 America/Santiago — Phase 172 core post-fix checks
passed; no persistent process.

## Phase 173 — latest authoritative update

Phase 173 verified canonical/runtime `iconos.py`: local planner fixture,
semantic compiler, visual validation and duplicate check all passed; output SVG
was byte-identical, `smoke_ok=True`, visual valid and unique. Real pieces and
providers were untouched. Evidence: `context/PHASE173_CODEX_ICONOS_FIXTURE_GATE.md`
and `.csv`.

## Phase 174 — latest authoritative update

Phase 174 verified canonical/runtime `generar.py` through the full local
plan->code->scan->sandbox->piece contract with planner/coder/sandbox stubs.
Both returned `ok=True` and `smoke_ok=True`, produced identical code and wrote
only temporary artifacts. No LLM/provider, real piece, worker, lock, service or
persistent process was used. Evidence:
`context/PHASE174_CODEX_GENERAR_FIXTURE_GATE.md` and `.csv`.

## Next concrete action

Refresh the objective matrix with Phases 163–174, then inspect the remaining
MAK department surfaces (`vigia`, `post`, `apps`, `labs`, `src`, `RD`) from
`/home/mak/*`. Choose the next real consumer/output slice, keeping provider
execution, media/database mutation, cron/services, side surfaces, WIN and Git
application gated until their own foreground contracts pass.

Last verified: 2026-08-15 America/Santiago — Phase 174 Codex generator/icon
fixtures passed; no provider or persistent process.

## Phase 175 — latest authoritative update

Phase 175 reconciled the objective matrix after the department gates from
research through Codex. Their local source/runtime contracts now have
foreground evidence, including the fixed canonical `testear.py` path. The
matrix keeps RD field data/mutators, PDF rendering, provider dependencies,
remaining departments, destructive cleanup and Git explicitly open. Evidence:
`context/PHASE175_OBJECTIVE_RECONCILIATION_AFTER_DEPARTMENTS.md` and `.csv`.

## Next concrete action

Inventory and select the next real consumer-backed slice among the remaining
physical top-level MAK surfaces: `vigia`, `post`, `apps`, `labs`, `src` and
`RD`. Start at `/home/mak/*`; preserve data/evidence and avoid provider,
service, cron, mutation, WIN and Git actions until their own gates are proven.

Last verified: 2026-08-15 America/Santiago — Phase 175 objective matrix
reconciled after research/curatoria/Codex gates; no persistent process.

## Phase 176 — latest authoritative update

Phase 176 reconciled the one stale runtime documentation line in
`/home/mak/vigia/vigia.py` with the canonical source. Source/runtime hashes
now match; both compiled and `vigia_guardia.sh` passed `bash -n`. A local HTTP
fixture validated identical first/second runs (two new listings, then zero)
and identical temporary state without real network, ntfy, ledger, cron or
service activity. Evidence: `context/PHASE176_VIGIA_PARITY_FIXTURE_GATE.md` and
`.csv`.

## Next concrete action

Inventory the remaining top-level surfaces from `/home/mak/*`, prioritizing the
empty `/home/mak/post`, derived `/home/mak/labs` databases and RD asset/data
surface. Select one real consumer/output chain; preserve evidence and avoid
network/providers, media/database mutation, GPU, cron, services, WIN and Git
application until a bounded foreground gate exists.

Last verified: 2026-08-15 America/Santiago — Phase 176 vigia parity/fixture
gate passed; no persistent process.

## Phase 177 — latest authoritative update

Phase 177 confirmed the POST architecture: `/home/mak/post` is absent by
design after prior duplicate consolidation; the active implementation is the
canonical `/home/mak/flujo/cultura/mak_post` used by the conductor registry.
Its pipeline compiled, accepted a valid temporary spec and rejected an invalid
one deterministically. No real POST artifact/provider/service/process was
touched. Evidence: `context/PHASE177_POST_ROOT_ABSENCE_GATE.md` and `.csv`.

## Next concrete action

Inspect `/home/mak/labs` as derived evidence rather than an active department,
then select the next real RD asset/data consumer. Preserve every SQLite/WAL,
media and historical artifact; do not merge lab databases or run perception,
providers, GPU, cron, services, mutators, WIN or Git actions without a bounded
read-only/fixture contract.

Last verified: 2026-08-15 America/Santiago — Phase 177 POST canonical gate
passed; root remains absent; no persistent process.

## Phase 178 — latest authoritative update

Phase 178 classified `/home/mak/labs` as dated derived evidence rather than an
active department. RD and PortableSSD summaries were read: their duplicate
relations, pending hashes, candidate rows, SQLite/WAL and perception states are
provenance-bound and must not be merged or promoted automatically. No lab
database, lock, media or perception process was touched. Evidence:
`context/PHASE178_LABS_DERIVED_EVIDENCE_CLASSIFICATION.md` and `.csv`.

## Next concrete action

Build a read-only RD asset metadata/duplicate crosswalk from `/home/mak/*`:
compare `/home/mak/RD`, its current index/database readers and the dated lab
summary without copying media or merging SQLite. Use hashes/paths/roles to
separate exact duplicates from semantic/historical variants; preserve all
assets, evidence, databases, providers, mutators, WIN and Git.

Last verified: 2026-08-15 America/Santiago — Phase 178 labs evidence
classification passed; no persistent process.

## Phase 179 — latest authoritative update

Phase 179 built the read-only RD asset metadata/duplicate crosswalk from
`/home/mak/*`. The physical `/home/mak/RD` walk observed 1,742 files and
60,865,045,370 bytes. `data/rd.db` passed read-only integrity and remains the
operational catalog projection consumed by Curatoria (20 productoras, 3
venues, 7 producer events). `data/rd_datos.db` passed read-only integrity with
three empty field tables and remains separate. The lab index currently has
1,749 asset rows, 1,585 full hashes, 164 pending hashes and 49 exact-duplicate
relations, while its embedded summary says 1,742 assets and 47 relations.
That snapshot discrepancy is recorded as reconciliation-required, not as a
deletion or merge authorization. A direct catalog and field-summary consumer
check passed with exit 0; no persistent process remained. The attempted venv
pytest command returned 127 because `/home/mak/venvs/flujo` has no pytest; no
package was installed. Evidence: `context/PHASE179_RD_ASSET_METADATA_CROSSWALK.md`
and `.csv`.

## Next concrete action

Reconcile the 1,742-file physical walk against the 1,749 current lab rows by
relative path and metadata only, then validate the existing RD asset/index
consumer (`cultura/mak_curatoria/ingesta_archivo.py` and its temporary
`archivo_index.sqlite` read path) on a bounded fixture. Output candidates and
provenance only; do not modify `/home/mak/RD`, any live SQLite/WAL, media,
providers, mutators, WIN, Git, cron or services.

Last verified: 2026-08-15 America/Santiago — Phase 179 RD asset crosswalk
passed read-only DB, physical inventory and consumer checks; no persistent
process.

## Phase 180 — latest authoritative update

Phase 180 reconciled `/home/mak/RD` against the RD source-key subset of the
derived lab index using relative paths, byte sizes and nanosecond mtimes. The
tree has 1,742 regular files and one symlink; all 1,742 regular files have
exactly one index row with zero size or mtime mismatches. The symlink is
`AUTOMATIZACION/cartelera.blend -> AUTOMATIZACION/RD.blend` and is not indexed
as a separate asset. The seven extra index rows belong to the separately
declared `/home/mak/GoogleDrive/RD/renders` evidence root, so they are not
local RD missing files. Evidence: `context/PHASE180_RD_INDEX_RECONCILIATION.md`
and `.csv`. The reconciliation exited 0 and did not alter media or databases.

## Next concrete action

Validate the existing `cultura/mak_curatoria/ingesta_archivo.py` index
reader/writer boundary on a small temporary fixture: confirm its metadata
schema, path containment, exact-hash relation behavior and safe output, then
remove only the temporary fixture. Keep `/home/mak/RD`, the lab SQLite/WAL,
the seven external render rows, databases, providers, mutators, WIN, Git,
cron and services untouched.

Last verified: 2026-08-15 America/Santiago — Phase 180 RD path/metadata
reconciliation passed; no persistent process.

## Phase 181 — latest authoritative update

Phase 181 validated the existing RD indexer on a temporary four-entry fixture:
three regular files plus one symlink. The source/runtime boundary indexed the
three regular files, excluded the symlink, produced one exact-duplicate
relation from complete hashes, and rejected an output directory inside the
source root. Perception was disabled (`perception_limit=0`), so no provider or
vision call occurred. The fixture exited 0 and left no persistent process;
the live RD corpus and lab SQLite/WAL were untouched. Evidence:
`context/PHASE181_RD_INDEX_FIXTURE_GATE.md` and `.csv`.

## Next concrete action

Move from RD index correctness to the next department slice: inventory the
active `/home/mak/apps` and `/home/mak/src` surfaces by consumer and runtime
entry point, beginning with bounded metadata and static import checks. Keep
`/home/mak/RD` and all derived evidence preserved; do not install dependencies,
start services, run providers/GPU, enable cron, touch WIN or Git, or delete
anything until a consumer-backed candidate has a foreground gate.

Last verified: 2026-08-15 America/Santiago — Phase 181 RD index fixture gate
passed; no persistent process.

## Phase 182 — latest authoritative update

Phase 182 classified `/home/mak/apps` as installed application layers rather
than mergeable MAK code, with no direct runtime imports found. It identified
`/home/mak/src/ml-mobileclip` as a real external source consumed lazily by
`cultura/mak_plataforma/visual_index.py`. The visual index compiled, passed a
temporary grouping/path fixture, and its existing derived read-only status
returned exit 0 with 100 indexed units, 345 eligible neighbors and 455
abstentions. The configured MobileCLIP checkpoint exists. No package was
installed and no GPU/model rebuild was run. Evidence:
`context/PHASE182_APPS_SRC_CONSUMER_GATE.md` and `.csv`.

## Next concrete action

Continue the active consumer audit through the remaining platform/research
bridges: inspect `mak_research` bridge entry points and the canonical platform
projections for static imports, file boundaries and bounded fixtures. Keep
application binaries and external model source in place. Do not run GPU or
providers, install dependencies, enable cron, start services, touch WIN/Git,
or delete evidence without a distinct foreground gate.

Last verified: 2026-08-15 America/Santiago — Phase 182 apps/src consumer and
visual-index read gate passed; no persistent process.

## Phase 183 — latest authoritative update

Phase 183 found and repaired a real runtime boundary bug in nine `/home/mak/research`
compatibility projections: they delegated to canonical `mak_research` modules
without adding the canonical directory to `sys.path`, causing a direct
`research.py` import to fail on `formato_ensayo`. A guarded path insertion was
added to `cadena.py`, `cola.py`, `fuentes.py`, `grafo.py`, `memoria.py`,
`panel.py`, `refutar.py`, `research.py` and `worker.py`. Isolated imports now
pass 9/9 with exit 0; no provider, network, worker, service or output was
started. Stale `.cola.pid` and `.webui.pid` values have no live process.
Runtime-only extra scripts remain preserved as evidence. Evidence:
`context/PHASE183_RESEARCH_WRAPPER_IMPORT_GATE.md` and `.csv`.

## Next concrete action

Run a bounded no-provider contract gate for research input validation and the
platform bridge: invalid/missing local inputs must reject or pause
deterministically without network, provider, worker, or output side effects.
Then continue the remaining platform projections. Preserve generated research,
mailboxes, checkpoints, locks, runtime extras, WIN and Git; do not install,
delete, enable cron or start services.

Last verified: 2026-08-15 America/Santiago — Phase 183 research wrapper import
gate passed after path fix; no persistent process.

## Phase 184 — latest authoritative update

Phase 184 ran the bounded no-provider Research/bridge gate. The direct runtime
command without a topic returned exit 2 before `investigar()`, provider calls,
outputs or notifications. A temporary local fixture validated the bridge hash
helper for existing and missing files; its permanent polling `main()` was not
called. The bridge fixture exited 0, the process gate was empty, and no
provider/network/worker/GPU/service/cron action occurred. Evidence:
`context/PHASE184_RESEARCH_INPUT_BRIDGE_GATE.md` and `.csv`.

## Next concrete action

Continue the platform projection audit with static/import/fixture checks for
the remaining operator-facing wrappers and maintenance routes. Keep
`/home/mak/research` outputs, mailboxes, checkpoints, locks and runtime extras
as evidence. Do not invoke real providers, permanent loops, GPU, cron,
services, mutators, installs, WIN, Git or destructive cleanup.

Last verified: 2026-08-15 America/Santiago — Phase 184 Research input and
bridge gate passed; no persistent process.

## Phase 185 — latest authoritative update

Phase 185 audited remaining platform imports and fixed the optional local-agent
boundary. `chat_agente.py` and runtime-only `agente_real.py` now import safely
without `qwen-agent` and return controlled exit 2 with an explicit dependency
message when executed. No package was installed, no Ollama/model session or
mutator ran, and the final process gate was empty. Evidence:
`context/PHASE185_OPTIONAL_AGENT_GATE.md` and `.csv`.

## Next concrete action

Continue the platform audit with a static inventory of remaining runtime-only
extras and maintenance entry points, separating canonical projections,
historical artifacts and optional dependencies. Validate only pure/local
helpers and reject missing inputs deterministically. Preserve output,
mailboxes, locks, databases, WIN and Git; do not install qwen-agent or other
packages, call providers, enable cron or start services.

Last verified: 2026-08-15 America/Santiago — Phase 185 optional local-agent
gate passed after controlled dependency fix; no persistent process.

## Phase 186 — latest authoritative update

Phase 186 classified platform runtime-only extras. `agente_real.py` is now an
optional-dependency boundary from Phase 185. `interfaz.py`, `memoria.py` and
`vigia.py` are preserved legacy candidates with identifiable canonical owners
or comparison paths. `panel_directivo.py` remains an incomplete artifact with
the known SyntaxError at line 145; no active service points to it, and it was
not reconstructed or deleted. Static/import checks passed for 13 of 14
remaining projections; the one failure is this preserved incomplete artifact.
Evidence: `context/PHASE186_PLATFORM_EXTRA_CLASSIFICATION.md` and `.csv`.

## Next concrete action

Compare `/home/mak/plataforma/interfaz.py` with `/home/mak/research/interfaz.py`
by routes, ports, output roots and dependencies using static/fixture evidence.
Do not start either UI or merge/delete either candidate. Preserve all runtime
extras, outputs, locks, databases, WIN and Git; no package/provider/cron/service
action.

Last verified: 2026-08-15 America/Santiago — Phase 186 platform extras
classification recorded; no persistent process.

## Phase 187 — latest authoritative update

Phase 187 compared the two Research UI candidates without starting either.
`/home/mak/research/interfaz.py` is selected by the user systemd service and
has the newer Hub-bound implementation. `/home/mak/plataforma/interfaz.py` is
an older same-port duplicate-shaped candidate; isolated import/direct launch
fails with missing `pausa`, and launching it would collide on port 8890. The
legacy file remains untouched and preserved. Evidence:
`context/PHASE187_RESEARCH_UI_CROSSWALK.md` and `.csv`.

## Next concrete action

Inspect launchers/configuration references for `/home/mak/plataforma/interfaz.py`
and draft the reversible final folder architecture: one canonical source,
one active runtime projection per department, explicit external-app and
historical evidence areas, and quarantine candidates without deletion. Do not
move/delete the legacy UI, start services, install packages, use providers,
enable cron, touch WIN or Git.

Last verified: 2026-08-15 America/Santiago — Phase 187 Research UI crosswalk
selected the service-backed owner; no persistent process.

## Phase 188 — latest authoritative update

Phase 188 documented the reversible folder-architecture proposal before any
cleanup or Git branch work. It assigns `/home/mak/flujo` as authoring source,
one runtime projection per department, `/home/mak/RD` as the creative corpus,
separate catalog/field databases, `/home/mak/labs` as derived evidence,
`/home/mak/apps` and `/home/mak/src` as external layers, `/home/mak/WIN` as
historical only, and phase quarantine as the only future reversible cleanup
area. It defines exact-hash, semantic-variant, document and tool-fusion rules;
no move/delete/branch occurred. Evidence:
`context/PHASE188_FOLDER_ARCHITECTURE_PROPOSAL.md` and `.csv`.

## Next concrete action

Finish the top-level `/home/mak/*` consumer audit against this architecture,
then build the path-level duplicate ledger for only the next bounded family.
Record hashes, roles, consumers and rollback before any quarantine. Preserve
all evidence, generated outputs, databases, WIN and Git; do not delete, move,
start services, enable cron, install packages or invoke providers.

Last verified: 2026-08-15 America/Santiago — Phase 188 folder architecture
proposal recorded; no persistent process.

## Phase 189 — latest authoritative update

Phase 189 completed a bounded immediate-child audit from `/home/mak/*` and
classified the top-level house into authoring, active runtimes, RD assets,
derived labs, external apps/source/models, state/evidence, discarded n8n,
excluded XIO and historical WIN. The disconnected `/home/mak/OneDrive` mount
was recorded as external state (`Errno 107`) with no repair attempt. No
recursive copy, delete, move, mount, service, cron, package, provider, WIN or
Git action occurred. Evidence: `context/PHASE189_TOP_LEVEL_SURFACE_AUDIT.md`
and `.csv`.

## Next concrete action

Start the path-level duplicate ledger with one bounded documentation/tool family
inside active MAK (not RD media yet): identify exact hashes, semantic owners,
consumers, runtime paths and reversible quarantine destinations. Use it to
prepare the first selective merge candidate; do not move/delete until the
ledger and rollback are complete.

Last verified: 2026-08-15 America/Santiago — Phase 189 top-level surface audit
passed; no persistent process.

## Phase 190 — latest authoritative update

Phase 190 built the first bounded path-level Research duplicate ledger. It
compared only direct source/runtime files, excluding outputs, corpus,
checkpoints, logs, locks and subdirectories. It recorded 13 exact
documentation/operational matches, 19 exact Python matches and 9 semantic
runtime wrappers. The wrapper shape is retained as the intended canonical
source plus runtime projection. No file was quarantined, moved or deleted;
service/crontab consumers must be proven inactive or redirected before a future
reversible move. Evidence: `context/PHASE190_RESEARCH_DUPLICATE_LEDGER.md`
and `.csv`.

## Next concrete action

Select one exact Research script from the ledger and prove its launcher state,
consumer references, file mode and rollback before any quarantine. Prefer a
paused/non-active script; if no safe candidate exists, record no-change and
move to the next bounded family. Preserve all evidence and do not delete,
install, start services, enable cron, invoke providers, touch WIN or Git.

Last verified: 2026-08-15 America/Santiago — Phase 190 Research duplicate
ledger recorded; no persistent process.

## Phase 191 — latest authoritative update

Phase 191 checked launcher state for the exact Research duplicate family. The
installed crontab returned exit 0 and every relevant Research automation line
was visibly `PAUSED-*`; no active launcher invokes `research.sh`. The exact
shell scripts are mode 0644, and the manual wrapper remains a valid historical
runtime path. No quarantine was safe to perform, so this phase recorded
no-change with no process/service/provider/package/database/WIN/Git action.
Evidence: `context/PHASE191_RESEARCH_LAUNCHER_GATE.md` and `.csv`.

## Next concrete action

Build the final role matrix for the Research family and then move to the next
bounded duplicate family only when it has a clear consumer owner. Keep the
current source/runtime pairs and paused declarations intact; no deletion,
quarantine, install, provider, service, cron, WIN or Git action.

Last verified: 2026-08-15 America/Santiago — Phase 191 Research launcher gate
recorded safe no-change; no persistent process.

## Phase 192 — latest authoritative update

Phase 192 completed the Research role matrix. It confirms canonical source plus
runtime projection ownership for runner/worker/UI, paused/manual status for
exact helpers, and preservation of docs, outputs, logs, locks, checkpoints and
corpus as durable evidence. Read-only unit checks returned `inactive` for
`mak-research`, `mak-codex`, `mak-hub` and `mak-interfaz`, with no matching
runtime process. No safe deletion candidate exists in this family. Evidence:
`context/PHASE192_RESEARCH_ROLE_MATRIX.md` and `.csv`.

## Next concrete action

Select the next bounded duplicate family from Codex or platform projections,
build its role/consumer/rollback matrix, and make at most one reversible
projection change if the consumer gate is complete. Preserve Research as
classified; do not delete/quarantine, install, invoke providers, start
services, enable cron, touch WIN or Git.

Last verified: 2026-08-15 America/Santiago — Phase 192 Research role matrix
complete; all checked runtime units inactive; no persistent process.

## Phase 193 — latest authoritative update

Phase 193 completed the Codex role matrix: four exact shared helper/entry
points and six semantic runtime projections, with no source-only or
runtime-only module in the paired set. `/home/mak/flujo/cultura/mak_codex` is
the semantic owner and `/home/mak/codex` remains the historical runtime path;
the test runner fix and fixture gates are already recorded. No deletion,
provider, service, worker, package, cron, WIN or Git action occurred. Evidence:
`context/PHASE193_CODEX_ROLE_MATRIX.md` and `.csv`.

## Next concrete action

Audit the remaining platform projection set with one consumer-backed pure
fixture, focusing on maintenance/state readers rather than inactive services.
Preserve exact helpers and semantic wrappers; no cleanup move, package,
provider, cron, service, WIN or Git action without a distinct rollback gate.

Last verified: 2026-08-15 America/Santiago — Phase 193 Codex role matrix
complete; no persistent process.

## Phase 194 — latest authoritative update

Phase 194 ran the canonical platform coherence reader in read-only mode. It
reported 36 apparent drift points (15 platform, 9 research, 6 Codex, 6
Curatoria; XIO excluded), with 30 platform and 7 research box-only files but
zero invoked box-only files. The differing groups include intentional thin
runtime projections and must not be synchronized or deleted blindly. Command
exit was 0; no service, cron, provider, package, network, WIN, Git or file
mutation occurred. Evidence: `context/PHASE194_PLATFORM_COHERENCE_AUDIT.md`
and `.csv`.

## Next concrete action

Choose one real platform projection mismatch from the coherence output, verify
its consumer and wrapper contract, and record either no-change or one
reversible projection update. Treat coherence as evidence, not cleanup
authority. Preserve all runtime extras and paused declarations; no delete,
move, install, provider, service, cron, WIN or Git action.

Last verified: 2026-08-15 America/Santiago — Phase 194 coherence audit
completed; no persistent process.

## Phase 195 — latest authoritative update

Phase 195 validated the `roles.py` coherence mismatch as an intentional
projection: source and runtime matched across `VERBOS`, all timing/load limits,
module paths and seeds. The pure fixture exited 0 with no provider, worker,
service, cron, package, output, WIN or Git action. Decision: no change; keep
canonical owner plus runtime projection. Evidence:
`context/PHASE195_PLATFORM_ROLES_PROJECTION_GATE.md` and `.csv`.

## Next concrete action

Select the next platform mismatch with a pure/read-only consumer contract and
repeat the projection gate. Prioritize `salud.py` or `coherence.py`; do not
run mutating platform actions, enable paused automation, install packages,
start services, invoke providers, touch WIN or Git.

Last verified: 2026-08-15 America/Santiago — Phase 195 platform roles
projection gate passed; no persistent process.

## Phase 196 — latest authoritative update

Phase 196 validated the `salud.py` source/runtime projection. Both snapshots
exposed the same eight-key contract and all stable values matched; only free
memory varied by 32 MB between sequential reads, which is expected dynamic
state. Services remained inactive and no XIO action was taken. The gate exited
0 with no writes, provider, service, cron, package, WIN or Git action. Evidence:
`context/PHASE196_PLATFORM_HEALTH_PROJECTION_GATE.md` and `.csv`.

## Next concrete action

Run the final selected pure/read-only platform projection gate for
`coherence.py`, then reconcile the resulting role matrix with the Phase 188
folder proposal. Preserve all runtime/state evidence; no cleanup,
installation, provider, service, cron, WIN or Git action.

Last verified: 2026-08-15 America/Santiago — Phase 196 platform health
projection gate passed; no persistent process.

## Phase 197 — latest authoritative update

Phase 197 completed the pure `coherence.py` projection gate with a temporary
fixture: source and runtime returned identical classifications for equal,
different and box-only files, and the invoked predicate matched only an exact
launcher reference. The gate exited 0 with no real tree scan, service, cron,
provider, package, output, WIN or Git action. Evidence:
`context/PHASE197_PLATFORM_COHERENCE_PROJECTION_GATE.md` and `.csv`.

## Next concrete action

Reconcile Phases 188–197 into one current progress/role matrix, identify the
remaining open objective slices (RD mutators/field data, automation, final
folder cleanup and Git branch proposal), and select the next bounded consumer
gate. Preserve all evidence; no deletion, quarantine, installation, provider,
service, cron, WIN or Git action during reconciliation.

Last verified: 2026-08-15 America/Santiago — Phase 197 coherence projection
gate passed; no persistent process.

## Phase 198 — latest authoritative update

Phase 198 reconciled the current 13-objective matrix. RD assets/indexing,
Research/Codex ownership, platform pure projections, wrapper import gates,
top-level inventory and folder architecture proposal are evidenced. RD field
data remains empty, mutators remain deferred, automations remain paused,
duplicate ledgers and full audit remain in progress, cleanup has not started,
and Git branch design remains deferred. Evidence:
`context/PHASE198_CURRENT_OBJECTIVE_MATRIX.md` and `.csv`.

## Next concrete action

Continue with the next bounded duplicate-role ledger for platform or selected
RD/document assets. Choose one candidate only after launcher, consumer, hash,
mode and rollback are proven; otherwise record no-change and proceed. After
that revalidate the local gate and update the visual progress summary. Keep all
mutators, databases, generated evidence, WIN and Git untouched.

Last verified: 2026-08-15 America/Santiago — Phase 198 objective matrix
reconciled; work remains; no persistent process.

## Phase 199 — latest authoritative update

Phase 199 built the RD exact-duplicate role ledger from the current 49 measured
relations. It grouped them into delivery/label, named-source, asset-library,
workspace/export and render-output role pairs. The grouping is explicitly a
candidate navigation aid, not deletion authority. The next focused family is
`packs_servicios_rd*`/`plano_rider*`, where canonical tariff/plano readers must
be mapped against job/RD delivery outputs. No media/database/provider/service/
cron/package/WIN/Git mutation occurred. Evidence:
`context/PHASE199_RD_DUPLICATE_ROLE_LEDGER.md` and `.csv`.

## Next concrete action

Build the focused RD delivery-family crosswalk (`packs_servicios_rd*` and
`plano_rider*`): identify source authority, active readers, generated outputs,
exact duplicates and rollback paths. End with preserve/no-change or a
reversible candidate; do not delete or merge artwork/data automatically.

Last verified: 2026-08-15 America/Santiago — Phase 199 RD duplicate role
ledger recorded; no persistent process.

## Phase 200 — latest authoritative update

Phase 200 completed the focused RD delivery-family crosswalk. The canonical
tariff owner is `/home/mak/flujo/data/rd_packs.json` through
`src/flujo/plano/packs.py`; RD and job JSON snapshots preserve the same numeric
250k/300k/500k pack contract but differ in wording/schema. Exact RD/job PDFs
and SVG variants were classified by delivery/editable role. No merge or delete
was justified. Evidence: `context/PHASE200_RD_DELIVERY_FAMILY_CROSSWALK.md`
and `.csv`.

## Next concrete action

Move to the remaining RD authority gate: static/read-only validation of field
data and mutating routes, documenting exact inputs, outputs, mutation boundary
and rollback. Keep `rd_datos.db` empty, do not ingest demo/evidence as real
data, and do not call mutators without explicit bounded authority. Preserve all
delivery assets, WIN and Git.

Last verified: 2026-08-15 America/Santiago — Phase 200 RD delivery crosswalk
passed; no persistent process.

## Phase 201 — latest authoritative update

Phase 201 classified the RD field-data and route authority boundary. The
read-only catalog, pack and empty field-summary routes remain valid; logo
upload, symbol writes, live render delivery and datadrop mutators were not
called. `rd.db` and `rd_datos.db` remain separate by authority/lifecycle, with
no demo/evidence promotion. Evidence:
`context/PHASE201_RD_MUTATION_AUTHORITY_GATE.md` and `.csv`.

## Next concrete action

Create the visual progress summary and final cleanup ledger from the completed
role matrices. Keep mutators deferred, field data empty, and all media,
databases, outputs, WIN and Git untouched until explicit authority supplies a
bounded mutation request.

Last verified: 2026-08-15 America/Santiago — Phase 201 RD mutation authority
gate classified; no persistent process.

## Phase 202 — latest authoritative update

Phase 202 created the visual progress summary and sequence from the current
13-objective matrix: 5 gated/integrated, 4 classified/proposed and 4
open/deferred. The remaining order is role matrices -> cleanup ledger with
rollback -> at most one reversible candidate -> full validation -> visual
review -> Git branch proposal. No cleanup, database merge, provider execution
or Git branch work occurred. Evidence:
`context/PHASE202_PROGRESS_VISUAL_SUMMARY.md` and `.csv`.

## Next concrete action

Build the final cleanup ledger for the already-classified candidate families,
starting with explicit hashes, consumer references, modes, and rollback paths.
Do not execute a move/delete yet; the ledger must first show a reversible,
consumer-safe candidate.

Last verified: 2026-08-15 America/Santiago — Phase 202 progress visual created;
no persistent process.

## Phase 203 — latest authoritative update

Phase 203 created the final cleanup ledger with full SHA-256 hashes, modes,
consumer roles, decisions and rollback paths. Exact RD delivery duplicates are
protected evidence and remain preserved; the old platform UI is only a
reversible quarantine candidate and was not moved; the incomplete platform
panel remains preserved without repair. Evidence:
`context/PHASE203_FINAL_CLEANUP_LEDGER.md` and `.csv`.

Commands and results: targeted `sha256sum` and `stat` both exit 0 for all five
ledger paths; bounded consumer search found no active launcher/config reference
for `plataforma/interfaz.py`; `systemctl --user is-active` returned four
`inactive` states. No move, delete, database write, install, service start or
Git operation occurred.

## Phase 204 — latest authoritative update

Phase 204 validated the safe non-`serve` FLUJO command surface with the
canonical venv interpreter. `version`, `rd-db --help`, `rd-db packs`,
`rd-db eventos`, `rd-db testeos`, `rd-db venues`, `health`, and `render formats`
rendered successfully; two exit code 1 results were caused by `head` closing a
pipe after output. The actual RD namespace is `rd-db`; no source correction was
needed. Database writers, renderers, job creators, datadrop ingestion,
providers and services remain deferred. Evidence:
`context/PHASE204_FLUJO_NON_SERVE_COMMAND_GATE.md` and `.csv`.

## Next concrete action

Continue the open functional audit by mapping read-only `knowledge`,
`job list/status/next/report`, `rd-db productora/lookup`, and `datadrop list/scan`
to their consumers and mutation class. Keep write commands deferred. Feed any
new confirmed duplicate or legacy family into the Phase 203 ledger, then
reconcile the 13-objective matrix before selecting any reversible quarantine or
preparing the Git branch proposal.

Last verified: 2026-08-15 America/Santiago — Phase 204 non-serve gate passed;
all relevant user services inactive; no persistent process.

## Phase 205 — latest authoritative update

Phase 205 mapped the remaining read-only consumer surfaces. Knowledge
productoras/venues/logos and classifier, job list/next, RD producer/lookup and
datadrop list all returned exit 0. Knowledge `events` is empty but is a
separate store from the two RD events exposed by `rd-db eventos`; no merge is
authorized. `job report`, datadrop scan/ingest and knowledge example ingest
remain deferred because they write or process evidence. Evidence:
`context/PHASE205_READ_SURFACE_CONSUMER_GATE.md` and `.csv`.

Commands and results: read-only command set passed; no database, job,
datadrop, knowledge, service, package, provider or Git mutation occurred.

## Next concrete action

Reconcile the 13-objective matrix with Phases 203–205 and select one bounded
write-capable functional slice for fixture validation. Prefer a disposable,
minimal fixture only if it can be created without copying a tree and with a
documented rollback; otherwise continue static validation and keep mutation
deferred. Do not merge databases or delete preserved evidence.

Last verified: 2026-08-15 America/Santiago — Phase 205 read-surface gate passed;
all relevant user services inactive; no persistent process.

## Phase 206 — latest authoritative update

Phase 206 found and fixed one real MAK CLI compatibility bug: `job status`
crashed when a valid RD brief represented products and optional pending items
as YAML mappings. The CLI now renders those mappings safely. `py_compile` and
the corrected `job status` both exit 0; `knowledge show productora thegrid`
also exits 0. The 13-objective reconciliation is recorded in
`context/PHASE206_JOB_STATUS_FIX_AND_MATRIX.md` and `.csv`.

No brief, database, generated output, runtime projection, service, package,
provider or Git state was changed. The four relevant user services remain
inactive.

## Next concrete action

Select and document the first bounded write-capable fixture gate. Prefer a
minimal hand-authored job fixture for `job report` only if it can be created
without copying a tree and reverted safely; otherwise continue static audit of
remaining writers. Keep real jobs, RD databases, media, WIN and Git untouched.

Last verified: 2026-08-15 America/Santiago — Phase 206 CLI fix and objective
matrix validated; no persistent process.

## Phase 207 — latest authoritative update

Phase 207 validated the deferred `job report` writer against the minimal,
hand-authored fixture `context/fixtures/phase207_job_report/`; no existing job
tree was copied. The command exited 0 and wrote exactly the expected fixture
projections `estado.md` and `reporte_job.md`; the input brief remained intact.
No real job, database, datadrop, delivery, service, provider or Git state was
mutated. Evidence:
`context/PHASE207_JOB_REPORT_FIXTURE_GATE.md` and `.csv`.

## Next concrete action

Run final local validation of the changed CLI and fixture outputs, then update
the cleanup/architecture status. Do not process real datadrops, ingest field
data, render live outputs, start services or mutate Git.

Last verified: 2026-08-15 America/Santiago — Phase 207 job-report fixture gate
passed; no persistent process.

## Phase 208 — latest authoritative update

Final local validation of the changed CLI and fixture slice passed:
`py_compile`, full `flujo --help`, real-job read-only `job status`, `rd-db
packs`, `health`, and fixture output presence all returned exit 0. The only
nonzero shell status was the expected aggregate status from
`systemctl --user is-active` because all four checked units are inactive. No
persistent process was created. Evidence:
`context/PHASE208_FINAL_LOCAL_VALIDATION.md`.

## Next concrete action

Update the folder architecture and cleanup disposition from the validated
consumer evidence, then prepare a visual closeout snapshot. Git branch design
remains last and must not be applied until the cleanup candidate and remaining
functional gates are explicitly closed.

Last verified: 2026-08-15 America/Santiago — Phase 208 local validation passed;
all relevant user services inactive; no persistent process.

## Phase 209 — latest authoritative update

Phase 209 froze the physical MAK architecture from `/home/mak/*`: `flujo` is
the canonical owner; department roots are runtime projections; RD and
curatoria_inbox are protected corpus/inbound surfaces; labs/indexes/state are
derived evidence; applications/models/source remain external; WIN is
historical read-only. Forty top-level architecture rows were CSV-validated.
OneDrive traversal returned the known disconnected-mount error (Errno 107) and
was left untouched. No broad move, delete, merge, service start, install or
Git operation occurred. Evidence:
`context/PHASE209_FINAL_MAK_ARCHITECTURE_DISPOSITION.md` and `.csv`.

## Phase 210 — latest authoritative update

Phase 210 created a visual architecture/13-objective closeout with Mermaid
maps. The remaining path is review surfaces -> decide the single platform UI
quarantine candidate -> final MAK runtime audit -> close field/mutator and
dependency gates -> Git branch proposal. Evidence:
`context/PHASE210_VISUAL_CLOSEOUT.md` and `.csv`.

## Next concrete action

Run the final bounded consumer audit for `REVIEW_BY_CONSUMER` surfaces
(`bucle`, `workspace`, `curatoria_encolado`, `flujo-deploy`, `lenguaje` and
remaining platform references), then make a path-specific disposition. Keep
all protected surfaces, WIN, databases, media and Git untouched.

Last verified: 2026-08-15 America/Santiago — Phase 210 visual closeout created;
all relevant user services inactive; no persistent process.

## Phase 211 — latest authoritative update

Phase 211 audited the remaining review surfaces. `flujo-deploy` is a real
disposable deploy owner consumed by `/home/mak/bin/mak_sync_safe.py`, not junk;
`lenguaje` has active code/role references and remains a department surface;
`bucle` is an unreferenced but provenance-bearing cultural project;
`workspace` contains unreferenced document-parser tools; `curatoria_encolado`
is empty; and `plataforma` is mixed but has active ledger/memory consumers.
No additional root surface passed the confirmed-junk gate. Evidence:
`context/PHASE211_REVIEW_SURFACES_AUDIT.md` and `.csv`.

Commands/results: bounded reference searches exited 0; filesystem `diff -qr`
between `flujo` and `flujo-deploy` returned expected exit 1 with 498 difference
records; no Git inventory, deploy sync, cron, provider, service or external
automation ran.

## Next concrete action

Close remaining functional gates with a static dependency/runtime matrix for
language and deploy consumers, then a read-only route audit for RD field-data
and mutation boundaries. Keep field data empty, mutators deferred, and all
protected/history surfaces untouched.

Last verified: 2026-08-15 America/Santiago — Phase 211 review-surface audit
completed; all relevant user services inactive; no persistent process.

## Phase 212 — latest authoritative update

Phase 212 closed the static dependency/runtime matrix for language and deploy.
Nine Python files compiled, four shell scripts passed `bash -n`, and isolated
imports of the language/deploy modules returned exit 0. Language has real
Research/Codex output consumers and paused write-capable hooks; deploy has a
real disposable-worktree consumer with Git/filesystem side effects, but was
not run. Neither surface is dead duplicate junk. Evidence:
`context/PHASE212_LANGUAGE_DEPLOY_RUNTIME_MATRIX.md` and `.csv`.

## Next concrete action

Run the read-only RD route/field-data audit: enumerate every route touching
`rd.db` or `rd_datos.db`, classify GET/POST and filesystem/database side
effects, and validate only the GET surface. Do not ingest field data or call a
mutating route.

Last verified: 2026-08-15 America/Santiago — Phase 212 static dependency gate
passed; all relevant user services inactive; no persistent process.

## Phase 213 — latest authoritative update

Phase 213 audited the RD route/field-data boundary. A temporary loopback hub
served only GET requests: `/api/rd-db`, `/api/rd-packs` and
`/api/rd-datos-summary` returned HTTP 200; the logo preview returned HTTP 404
for `thegrid` without writing. A second run proved `rd.db` and `rd_datos.db`
SHA-256 values unchanged and shut the temporary server down. Catalog rebuild,
field ingest, report output, logo/symbol writes, renders and datadrop routes
remain explicitly deferred. Evidence:
`context/PHASE213_RD_ROUTE_FIELD_DATA_AUDIT.md` and `.csv`.

## Next concrete action

Validate the field-data read/report path against the existing empty database
without ingesting rows, then reconcile dependency declarations and remaining
runtime slices. Do not call a POST route, rebuild `rd.db`, or promote demo/
evidence data to real field data.

Last verified: 2026-08-15 America/Santiago — Phase 213 RD route audit passed;
temporary server shut down; no persistent process.

## Phase 214 — latest authoritative update

Phase 214 validated `rd-datos informe` against the existing empty
`rd_datos.db`, writing only temporary Markdown outside the repository. Full and
`2026-Q3` reports exited 0, included the mandatory no-real-field-data
disclaimer and rendered `(sin datos)`. SHA-256 for both RD databases was
unchanged before/after. No CSV ingest, POST route, merge or service occurred.
Evidence: `context/PHASE214_RD_EMPTY_REPORT_GATE.md` and `.csv`.

## Next concrete action

Reconcile dependency declarations with the validated route/CLI slices and
identify remaining runtime incompatibilities. Keep real field data and all
mutating routes deferred until the corresponding authority is supplied.

Last verified: 2026-08-15 America/Santiago — Phase 214 empty field-data report
gate passed; no persistent process.

## Phase 215 — latest authoritative update

Phase 215 reconciled dependency declarations by slice. `requirements.txt` and
the base `pyproject.toml` constraints match for nine runtime packages;
`/home/mak/venvs/flujo/bin/python -m pip check` returned exit 0. Twelve
canonical/runtime modules across CLI, RD, web, language, platform and visual
index imported successfully. Optional render/web/model/provider/GPU packages
remain scoped to their slices; no installation or global-Windows conflict was
promoted. Evidence: `context/PHASE215_DEPENDENCY_SLICE_MATRIX.md` and `.csv`.

## Next concrete action

Run the final static/foreground audit of remaining active projections and their
entrypoints, then update the 13-objective closeout. Keep provider/GPU,
datadrop, field-ingest and live-mutator paths deferred.

Last verified: 2026-08-15 America/Santiago — Phase 215 dependency matrix and
venv check passed; no persistent process.

## Phase 216 — latest authoritative update

Phase 216 parsed 110 Python files across active root projections; 109 passed
and the known incomplete `/home/mak/plataforma/panel_directivo.py` failed at
line 145. It has no verified consumer and remains preserved evidence, not an
active runtime failure. Foreground `health`, `rd-db packs`, real-job `job
status` and `datadrop list` all exited 0. Evidence:
`context/PHASE216_ACTIVE_PROJECTION_ENTRYPOINT_AUDIT.md` and `.csv`.

## Next concrete action

Create the final objective/cleanup status snapshot, then decide whether the
single platform UI candidate and empty staging directory have enough evidence
for reversible quarantine. Do not delete the incomplete panel, WIN,
databases, media or recovery surfaces.

Last verified: 2026-08-15 America/Santiago — Phase 216 projection audit
completed; all relevant user services inactive; no persistent process.

## Phase 217 — latest authoritative update

Phase 217 refreshed the objective/cleanup snapshot. Confirmed shell residue is
absent from active surfaces: 92 `.DS_Store` files and 7 stray shell objects
remain recoverable in their phase quarantines; the current staging directory is
empty but was not deleted. Architecture, database separation, asset index and
read gates are stable; field authority, live mutators, remaining audit and
Git proposal remain open. Evidence:
`context/PHASE217_CLEANUP_OBJECTIVE_CLOSEOUT.md` and `.csv`.

## Next concrete action

Write the new Git branch-system proposal against the frozen architecture,
without creating branches. Define ownership, naming, merge gates and rollback
for each vertical slice. Then return to the remaining field/mutator and
historical-surface gates.

Last verified: 2026-08-15 America/Santiago — Phase 217 cleanup/objective
snapshot validated; all relevant user services inactive; no persistent process.

## Phase 218 — latest authoritative update

Phase 218 wrote the new Git branch-system proposal without creating branches or
reading Git as inventory. It defines `main`, ASCII `codex/mak/<slice>` branches,
disjoint write sets, predecessor/successor traceability, merge gates, rollback
and the explicit rule that WIN remains filesystem history. Evidence:
`context/PHASE218_GIT_BRANCH_SYSTEM_PROPOSAL.md` and `.csv`.

## Next concrete action

Do not create branches yet. Return to the remaining open/deferred objectives:
field-data authority, mutating RD route authority, optional dependency/runtime
closure, full historical-surface audit and any path-specific cleanup candidate.
Only create the first branch after the corresponding write set is authorized
and the architecture snapshot is accepted.

Last verified: 2026-08-15 America/Santiago — Phase 218 branch proposal created;
no Git operation and no persistent process.

## Phase 219 — latest authoritative update

Phase 219 quarantined the one exact empty staging candidate,
`/home/mak/curatoria_encolado`, after verifying zero entries, mode 0755, no
bounded consumer references and an absent destination. Move exit 0; original
path is absent, quarantine path exists and remains empty. The inverse move is
recorded. No file, source, database, media, WIN or Git state changed. Evidence:
`context/PHASE219_EMPTY_STAGING_QUARANTINE.md` and `.csv`.

## Next concrete action

Run post-quarantine health/import/route checks and update the objective
snapshot. Keep the legacy platform UI preserved until its evidence status is
resolved; do not broaden cleanup.

Last verified: 2026-08-15 America/Santiago — Phase 219 reversible quarantine
passed; no persistent process.

## Phase 220 — latest authoritative update

Post-quarantine validation passed: `health`, `rd-db packs`, real-job
`job status`, and core imports returned exit 0; the staging path is absent from
the active root; all four relevant user services remain inactive. Remaining
open items are authority-dependent: real field data, live mutators, optional
external/provider/GPU checks and the preserved historical incomplete panel.
Evidence: `context/PHASE220_POST_QUARANTINE_VALIDATION.md` and `.csv`.

## Next concrete action

Maintain this boundary without fabricating field data or external authority.
If no new authority arrives, produce only a read-only evidence report of the
remaining gates; no further broad cleanup is justified. The Git branch proposal
exists but has not been applied.

Last verified: 2026-08-15 America/Santiago — Phase 220 post-quarantine checks
passed; no persistent process.

## Phase 221 — latest authoritative update

Phase 221 validated RD field ingestion in isolated temporary databases. The
demo testeo CSV inserted 30 temporary rows with exit 0; a temporary row
containing an email was rejected under strict privacy with 0 persisted rows.
`data/rd_datos.db` remained empty and untouched. No demo/evidence file was
promoted to real field data. Evidence:
`context/PHASE221_RD_FIELD_INGEST_FIXTURE_GATE.md` and `.csv`.

## Next concrete action

Keep `rd_datos.db` empty until a real CSV/acta and authority arrive. Continue
the final read-only audit of remaining active surfaces; do not promote demo or
historical evidence and do not call live mutators.

Last verified: 2026-08-15 America/Santiago — Phase 221 field/privacy fixture
gate passed; no persistent process.

## Phase 222 — latest authoritative update

Phase 222 fixture-validated the RD logo mutator against a temporary root. A
valid producer/SVG/source created only temporary logo and source-sidecar files;
no live POST request and no MAK target write occurred. Production write set is
confirmed as `knowledge/logos/descargas/<slug>.<ext>` plus optional source
sidecar. Evidence: `context/PHASE222_RD_LOGO_MUTATOR_FIXTURE_GATE.md` and
`.csv`.

## Next concrete action

Perform equivalent static/fixture checks for symbol writes and render output
paths without calling live POST routes. Keep databases, assets, datadrops and
real job outputs unchanged.

Last verified: 2026-08-15 America/Santiago — Phase 222 logo mutator fixture
gate passed; no persistent process.

## Phase 223 — latest authoritative update

Phase 223 corrected the RD route ledger: `POST /api/plano/render` and `POST
/api/cotizacion/render` are transient in-memory payload generators in the
current implementation, not persistent file/database mutators. Direct INFO
plan and quote fixtures passed; both RD database hashes were unchanged. Logo
upload, symbol add, job creation, datadrop operations and database
ingest/rebuild remain true mutators. Evidence:
`context/PHASE223_RD_PURE_RENDER_CORRECTION.md` and `.csv`.

## Next concrete action

Update the route matrix with this corrected classification and continue
transient fixture validation only. Keep live POST calls and database writers
deferred.

Last verified: 2026-08-15 America/Santiago — Phase 223 render classification
corrected; no persistent process.

## Phase 224 — latest authoritative update

Phase 224 consolidated the remaining open gates with exact evidence and
recovery actions. Real field data is absent (only demo/evidence inputs exist),
mutators are fixture-mapped but live-deferred, base dependencies are healthy,
the incomplete panel remains preserved, the legacy platform UI remains at its
original path, and the Git system is proposal-only. Verified invariants include
separate RD databases, intact WIN, quarantined confirmed residue and inactive
services. Evidence: `context/PHASE224_FINAL_OPEN_GATES.md` and `.csv`.

## Next concrete action

No further local mutation is justified without one of the exact missing inputs
in Phase 224. Continue read-only checks only, or resume the named gate when its
source or authority becomes available.

Last verified: 2026-08-15 America/Santiago — Phase 224 final open-gate ledger
written; no persistent process.

## Phase 225 — latest authoritative update

Repaired handoff continuity: the current Phase 225 checkpoint is now at the
top of this file, while stale Phase 77/48 notes are explicitly historical and
preserved. No physical target, database, WIN path, service or process changed.
Evidence: `context/PHASE225_HANDOFF_CHECKPOINT_REPAIR.md` and `.csv`.

## Next concrete action

Read the top checkpoint first on every continuation. Continue only read-only
work until real field/mutator authority arrives.

Last verified: 2026-08-15 America/Santiago — Phase 225 handoff repair
validated; no persistent process.

## Phase 228 — latest authoritative update

Phase 228 quarantined the physically empty `/home/mak/workspace` tree
reversibly. It contained three nested directories, zero files and zero
symlinks, with no bounded active consumer. The original path is absent and the
quarantine path contains zero files. The legacy platform UI was preserved
because historical tests/import references and an incomplete runtime contract
make it evidence, not confirmed junk. Foreground `health`, `rd-db packs`,
`job list` and valid `job status` all returned exit 0 afterward. Evidence:
`context/PHASE228_EMPTY_WORKSPACE_QUARANTINE.md` and `.csv`.

## Next concrete action

Continue the remaining candidate ledger by consumer, Spanish/English language
and platform. Preserve semantic variants, working assets and historical
evidence; quarantine only an exact empty/confirmed-residue path with a stated
rollback. Do not re-enable external automation, call live mutators, create
branches or remove the legacy UI without explicit authority.

Last verified: 2026-08-15 America/Santiago — Phase 228 empty workspace
quarantine and foreground regression gate passed; no persistent process.

## Phase 229 — latest authoritative update

Phase 229 quarantined nine malformed empty shell/path directories: four at the
MAK root and five under the canonical FLUJO root. Every candidate contained
zero files and zero symlinks; all moves returned exit 0 and all original paths
are absent. Named storage paths and `/home/mak/tmp` were preserved. Foreground
`health`, `rd-db packs` and `job next` all returned exit 0 afterward. Evidence:
`context/PHASE229_EMPTY_SHELL_RESIDUE_QUARANTINE.md` and `.csv`.

## Next concrete action

Do not broaden physical cleanup. Continue only with read-only functional
verification or a named gate when real field data/mutator authority exists;
the user-confirmed issue/URL workflow remains working but paused. The Git
branch system remains a proposal until explicitly authorized.

Last verified: 2026-08-15 America/Santiago — Phase 229 empty shell-residue
quarantine and foreground regression gate passed; no persistent process.

## Phase 230 — latest authoritative update

The full non-`serve` CLI dispatch surface was checked with `--help`: 17
top-level/group commands returned exit 0, and `src/flujo/cli.py` compiles.
This proves registration/option wiring, not execution of mutating commands.
Evidence: `context/PHASE230_NON_SERVE_CLI_DISPATCH_GATE.md` and `.csv`.

## Phase 231 — latest authoritative update

The RD database fusion was probed in a disposable SQLite candidate. The live
sources have 20/7,587 catalog rows and 3/0 privacy-field rows, with no table
name collision; the temporary 23-table candidate passed integrity and both live
hashes remained unchanged. No live merge occurred because physical
co-location would change the privacy boundary; the choice between physical
migration and logical unification remains explicit. Evidence:
`context/PHASE231_RD_DATABASE_MERGE_PROBE.md` and `.csv`.

## Next concrete action

Map every RD database consumer and document the selected merge contract, then
continue the remaining objective audit. Keep both live stores intact until the
privacy-boundary decision is resolved; do not call live mutators, promote demo
data, re-enable external automation or create branches.

Last verified: 2026-08-15 America/Santiago — Phase 231 merge probe passed with
no live database change or persistent process.

## Phase 232 — latest authoritative update

The RD consumer map is now explicit: six operational source files own or
consume the two databases. `rd.db` is rebuildable catalog state; `rd_datos.db`
is accumulative privacy-first field state. The schemas can coexist without
table collisions, but a physical merge would require changing lifecycle,
privacy and path contracts. No live database changed. Evidence:
`context/PHASE232_RD_DATABASE_CONSUMER_MAP.md` and `.csv`.

## Next concrete action

Continue with the remaining RD route mutator fixtures using temporary roots and
no live POST. Preserve both database owners until a physical migration is
explicitly selected and rollback-tested.

Last verified: 2026-08-15 America/Santiago — Phase 232 consumer map validated;
no persistent process.

## Phase 233 — latest authoritative update

Temporary-root fixtures for symbol creation, datadrop upload, datadrop analysis
and review-package generation all returned exit 0; the prior logo fixture also
passed. The temporary write sets were isolated and removed automatically;
`LIVE_WRITE=False`. Live POSTs, real jobs, databases, assets and providers were
untouched. Evidence: `context/PHASE233_RD_MUTATOR_FIXTURE_GATE.md` and `.csv`.

## Next concrete action

Continue the complete MAK audit with the remaining non-RD department/runtime
surfaces. Keep mutator write sets documented and defer live POST/provider
boundaries; if physical database fusion is selected, name migration, backup,
privacy review and rollback first.

Last verified: 2026-08-15 America/Santiago — Phase 233 RD mutator fixture gate
passed; no persistent process.

## Phase 234 — latest authoritative update

The active projection AST gate parsed 445 current Python files and passed 444.
The sole failure is the known truncated, unconsumed
`/home/mak/plataforma/panel_directivo.py` at line 145. It remains preserved
as incomplete evidence rather than being reconstructed. No source, data,
service, provider, WIN or Git path changed. Evidence:
`context/PHASE234_ACTIVE_PROJECTION_AST_GATE.md` and `.csv`.

## Next concrete action

Run the final department/runtime health matrix, excluding generated evidence
and the inactive incomplete panel. Keep mutator/provider boundaries deferred
and retain the explicit database merge decision.

Last verified: 2026-08-15 America/Santiago — Phase 234 active AST gate
validated; no persistent process.

## Phase 235 — latest authoritative update

The final local health matrix passed: 7/7 core imports, base `pip check`,
read-only CLI, both SQLite integrity checks and physical path invariants. Cron
has zero active entries; research, queue, codex, hub, interfaz and XIO units
are inactive. No source, database, asset, provider, service, WIN or Git path
changed. Evidence: `context/PHASE235_FINAL_LOCAL_HEALTH_MATRIX.md` and `.csv`.

## Next concrete action

Reconcile the 13-objective matrix against all current evidence, then produce
the final folder/duplicate/tool disposition and Git branch proposal. Keep real
field data, live mutators and the physical database decision explicitly open.

Last verified: 2026-08-15 America/Santiago — Phase 235 final local health
matrix passed; no persistent process.

## Phase 236 — latest authoritative update

Reconciled all 13 objectives against current evidence. The local health and
read/fixture slices pass within scope, while real field data, physical DB
choice, live mutator authority, optional runtimes, residual duplicate/tool
decisions and Git authorization remain explicitly open. No completion claim was
made. Evidence: `context/PHASE236_CURRENT_OBJECTIVE_RECONCILIATION.md` and
`.csv`.

## Next concrete action

Produce the final top-level MAK disposition artifact with owner, consumer,
Spanish/English language, platform, status and rollback, then compare it with
the existing branch proposal. Keep deferred boundaries untouched.

Last verified: 2026-08-15 America/Santiago — Phase 236 objective
reconciliation written; no persistent process.

## Phase 237 — latest authoritative update

Produced the current final MAK surface disposition: canonical FLUJO owner,
runtime projections, RD/media/data/evidence, language/platform surfaces,
external infrastructure, historical WIN and both reversible quarantines are
mapped to owner, consumer, language/platform, disposition and rollback. It is
aligned with the Phase 218 branch proposal; no Git operation occurred.
Evidence: `context/PHASE237_FINAL_MAK_SURFACE_DISPOSITION.md` and `.csv`.

## Next concrete action

Use Phase 237 as the architecture baseline. Any next change must name one
surface, one consumer, one write set and one rollback. Continue only with an
explicit external gate or a read-only verification; do not broaden cleanup or
create/switch Git branches.

Last verified: 2026-08-15 America/Santiago — Phase 237 disposition validated;
no persistent process.

## Phase 238 — latest authoritative update

Compared the canonical Platform source with its Linux runtime projection using
local SHA-256 and AST consumer evidence. Of 56 shared direct files, 36 are
exact copies and 20 are divergent; 32 active source/test files consume the
canonical package. The correct fusion is one semantic owner plus retained
runtime paths, not flattening or deletion. The SSH-based mirror checker was not
run. No file, service, cron, provider, WIN or Git path changed. Evidence:
`context/PHASE238_PLATFORM_TOOL_OWNER_LEDGER.md` and `.csv`.

## Next concrete action

Apply the same consumer-ledger method to remaining document families and the 20
divergent Platform files. Quarantine only a file with a proven redundant
launcher and rollback; preserve runtime paths and historical evidence.

Last verified: 2026-08-15 America/Santiago — Phase 238 Platform owner ledger
validated; no persistent process.

## Phase 239 — latest authoritative update

The bounded document scan covered 4,143 small text/metadata files and found 99
exact-hash groups covering 334 paths. Research captures, dated reports,
source/runtime projections, Curatoria candidate outputs and generated director
results were classified by provenance and consumer; none was removed. Evidence:
`context/PHASE239_DOCUMENT_DUPLICATE_DISPOSITION.md` and `.csv`.

## Next concrete action

Review the 20 divergent Platform files individually where a real consumer
exists. Keep classified document families untouched unless an exact
path-specific quarantine has consumer proof and inverse move.

Last verified: 2026-08-15 America/Santiago — Phase 239 document disposition
validated; no persistent process.

## Phase 240 — latest authoritative update

Closed the local Platform divergent projection gate: 17 divergent Python files
all parse, 2 shell surfaces are non-empty wrappers, and 1 text file is a data
contract. Runtime paths remain required by manifests/units and no file
qualified for quarantine. No SSH, service, cron, provider, deploy sync, move or
Git operation occurred. Evidence:
`context/PHASE240_PLATFORM_DIVERGENT_PROJECTION_GATE.md` and `.csv`.

## Next concrete action

Close the local duplicate/tool audit with a no-change decision for this family,
then continue only on explicit external gates: real RD field input, live
mutator authority, optional runtime requirements and any physical DB choice.

Last verified: 2026-08-15 America/Santiago — Phase 240 Platform divergent gate
passed; no persistent process.

## Phase 241 — latest authoritative update

Updated the 13-objective reconciliation: document duplicates are classified by
provenance/consumer, equivalent Platform tools have one canonical owner with
retained runtime projections, and local cleanup/health gates remain verified.
Only real field input, live mutator authority, optional runtime requirements
and physical/logical database choice remain material gates. Evidence:
`context/PHASE241_OBJECTIVE_RECONCILIATION_UPDATE.md` and `.csv`.

## Next concrete action

Maintain the current architecture and handoff. If no new external input exists,
perform only bounded read-only health checks; do not invent field records,
enable providers, merge privacy stores or create branches.

Last verified: 2026-08-15 America/Santiago — Phase 241 objective update
validated; no persistent process.

## Phase 242 — latest authoritative update

Loaded 17 canonical `cultura.mak_plataforma` implementations in isolated
subprocesses with bytecode disabled; all returned exit 0. No provider, network,
scheduler, job, upload, durable write, service, WIN or Git path was touched.
The Platform family is therefore integrated by canonical ownership plus
compatibility projections. Evidence:
`context/PHASE242_PLATFORM_CANONICAL_IMPORT_GATE.md` and `.csv`.

## Next concrete action

Keep the local audit at this safe boundary and monitor only for a named external
gate or new physical evidence. Preserve the handoff and rollback maps.

Last verified: 2026-08-15 America/Santiago — Phase 242 canonical import gate
passed; no persistent process.

## Phase 243 — latest authoritative update

Closed the dependency map by slice. The canonical venv has all nine declared
base distributions and `pip check` returned exit 0. Optional render, desktop,
build, provider and GPU dependencies, plus local MAK modules and the separate
visual-index environment, were classified without installation or promotion.
Evidence: `context/PHASE243_DEPENDENCY_SLICE_CLOSURE.md` and `.csv`.

## Next concrete action

Reconcile the 13-objective closeout and keep all external-boundary gates
explicit. Do not alter requirements, enable providers, merge privacy stores or
start services.

Last verified: 2026-08-15 America/Santiago — Phase 243 dependency slice
closure passed; no persistent process.

## Phase 244 — latest authoritative update

Reconciled all 13 requested objectives. Local verification, canonical ownership
and reversible cleanup are complete within scope. Real RD field input, live
mutator authority, optional runtime promotion, the physical database decision
and explicit Git operation remain open with exact next gates. No source,
database, asset, WIN, dependency, service, cron or Git state changed.
Evidence: `context/PHASE244_OBJECTIVE_CLOSEOUT_MATRIX.md` and `.csv`.

## Next concrete action

Maintain this safe boundary and continue only when a named external gate or new
physical evidence exists. Otherwise run a bounded read-only health recheck; do
not invent records, enable providers, merge privacy stores, delete evidence or
create branches.

Last verified: 2026-08-15 America/Santiago — Phase 244 objective closeout
validated; no persistent process.

## Phase 245 — latest authoritative update

Verified the completed historical/catalog `rd.db` fusion. The active MAK,
WIN and state copies each contain 20 tables and 7,587 rows, with identical
per-table schema/row digests and SQLite integrity `ok`. The 12-table pre-merge
backup remains recoverable. `rd_datos.db` has four schema tables and zero rows;
it remains a separate privacy store rather than an unrequested catalog merge.
Evidence: `context/PHASE245_RD_HISTORICAL_DB_FUSION_CLOSURE.md` and `.csv`.

## Next concrete action

Advance to the next unresolved objective: real RD field data. Search only for
new authoritative CSV/acta input; do not invent rows, copy demo data or merge
`rd_datos.db` into the catalog.

Last verified: 2026-08-15 America/Santiago — Phase 245 historical RD database
fusion closure passed; no persistent process.

## Phase 246 — latest authoritative update

Found a concrete historical RD field-testing candidate rather than an empty
surface: the preserved `Testeo 2025` source and active derived evidence contain
42 events, 1,831 test rows and 5,394 observations. The evidence status is
`candidate_evidence_pending_human_review`; it is already catalog evidence in
`rd.db`, but it was not copied into the empty privacy-first `rd_datos.db`.
Evidence: `context/PHASE246_RD_FIELD_CANDIDATE_AUDIT.md` and `.csv`.

## Next concrete action

Obtain or detect the missing provenance/period/duplicate/link review and
explicit privacy-store ingest authority. Until then preserve the source and
keep `rd_datos.db` empty; continue with other local gates without inventing
field records.

Last verified: 2026-08-15 America/Santiago — Phase 246 field candidate audit
passed; no persistent process.

## Phase 247 — latest authoritative update

Removed exactly the 92 quarantined `.DS_Store` files and seven confirmed
shell-residue objects after a type/count preflight. Post-check found zero
remaining objects in those two quarantine sets. All other quarantines,
historical evidence, WIN, sources, products, databases and runtime surfaces
were preserved. Evidence: `context/PHASE247_CONFIRMED_JUNK_REMOVAL.md` and
`.csv`.

## Next concrete action

Run the post-cleanup local health matrix, then continue with the remaining
named external gates: field candidate review/authority, live mutator authority,
optional runtime promotion and explicit Git operation.

Last verified: 2026-08-15 America/Santiago — Phase 247 confirmed junk removal
passed; no persistent process.

## Phase 248 — latest authoritative update

Post-cleanup validation passed: selected RD/database/no-automerge tests exited
0; health, RD packs, job list/next, knowledge, datadrop, SQLite integrity and
cron/process safety passed. The base venv was not modified; pytest ran from
the existing research venv. Evidence: `context/PHASE248_POST_CLEANUP_HEALTH_GATE.md`
and `.csv`.

## Next concrete action

Continue only with named external gates: review and authority for the concrete
RD field candidate, live mutator authority, optional runtime promotion or an
explicit Git operation. No further broad cleanup is justified by current
evidence.

Last verified: 2026-08-15 America/Santiago — Phase 248 post-cleanup health
gate passed; no persistent process.

## Phase 249 — latest authoritative update

The concrete `Testeo 2025` candidate passed a temporary, strict privacy dry-run
through the real `rd-datos ingest` CLI: 762 rows inserted into the temporary
DB, 19 rejected by privacy scan and 4,613 invalid by form. The live
`rd_datos.db` hash stayed unchanged. The route returned exit 0; the initial
harness-only `None` date error was corrected and recorded. Evidence:
`context/PHASE249_RD_FIELD_DRYRUN_GATE.md` and `.csv`.

## Next concrete action

Resolve the candidate's date/required-field/privacy review and obtain explicit
authority before live ingest. Continue other local gates without inventing
field records or modifying the live privacy DB.

Last verified: 2026-08-15 America/Santiago — Phase 249 RD field dry-run passed;
no persistent process.

## Phase 250 — latest authoritative update

Parsed the canonical hub POST handler and classified all 16 literal POST paths
by effect and write set. Transient quote/plano paths are verified; symbol,
logo and datadrop helper mutators have temporary fixture passes. Job,
automation, command, incoming-scan and live asset/data mutators remain gated.
No live POST or persistent process was used. Evidence:
`context/PHASE250_RD_POST_ROUTE_MATRIX.md` and `.csv`.

## Next concrete action

Keep live writes deferred until one named mutator, input, output and rollback
are explicitly authorized. Continue only with safe local audit work; do not
call command, automation or provider-backed routes.

Last verified: 2026-08-15 America/Santiago — Phase 250 RD POST route matrix
validated; no persistent process.

## Phase 251 — latest authoritative update

The active documentation projections and two stale test contracts were repaired
without changing runtime behavior. Two documents were selected individually
from WIN; stale SSH wording was removed from active projections while WIN was
preserved. The targeted contract set passed its checks. The conservative safe
suite completed with exit 0. Evidence:
`context/PHASE251_ACTIVE_DOCS_SAFE_SUITE.md`.

## Next concrete action

Continue with the next active consumer slice using static/isolated validation.
Do not perform live RD field ingestion, live mutator POSTs, provider/GPU
promotion or Git branch creation without explicit authority, named input/output
and rollback. Keep the incomplete historical panel preserved as evidence.

Last verified: 2026-08-15 America/Santiago — Phase 251 active documentation
and safe-suite gate passed; no persistent process.

## Phase 252 — latest authoritative update

The remaining test surface was statically classified from `/home/mak/*` down
to the canonical test tree. 177 files and 2,164 test-function declarations
were conservatively excluded from batch execution because of process,
network/provider, media/GPU or external-integration markers; all parsed with
zero syntax failures. No test, service, provider, database, network route or
external integration was invoked. Evidence:
`context/PHASE252_EXCLUDED_TEST_RISK_INVENTORY.md`.

## Next concrete action

Derive a per-file promotion shortlist from executable AST imports/calls, then
run one bounded fixture-only group. Keep live RD ingest, mutator POSTs,
provider/GPU promotion and Git branch creation deferred until explicit
authority and a named rollback. Preserve the incomplete panel as evidence.

Last verified: 2026-08-15 America/Santiago — Phase 252 static risk inventory
passed; no persistent process.

## Phase 253 — latest authoritative update

The bounded RD database/privacy fixture group passed 62 tests. It used only
temporary SQLite/filesystem fixtures and static logo/source checks. The live
privacy database remained byte-identical, with zero `registros_testeo` rows;
no route, provider or external integration was invoked. Evidence:
`context/PHASE253_RD_DATA_FIXTURE_GATE.md`.

## Next concrete action

Promote the hub command allow-list gate only for version and invalid-command
fixtures, confirming no live command, automation, provider or mutator route is
called. Keep field ingest and Git operations gated by explicit authority.

Last verified: 2026-08-15 America/Santiago — Phase 253 RD fixture gate passed;
no persistent process.

## Phase 254 — latest authoritative update

The hub command allow-list passed 13 bounded fixture cases. Unknown,
free-form, destructive and unclassified commands were rejected; version and
invalid-argument cases stayed bounded. No provider, automation, live POST,
database or persistent process was invoked. Evidence:
`context/PHASE254_HUB_COMMAND_GATE.md`.

## Next concrete action

Promote the next fixture-only RD asset/symbol contract group. Keep actual
symbol creation, live POST routes, field ingest and Git operations deferred
until explicit authority and rollback are named.

Last verified: 2026-08-15 America/Santiago — Phase 254 hub command gate passed;
no persistent process.

## Phase 255 — latest authoritative update

The RD symbol catalogue, user-facing symbol registration and image tracer
passed 28 fixture-only tests. Writes were isolated under temporary roots; the
hub was not started and no live POST route was called. Evidence:
`context/PHASE255_RD_SYMBOL_FIXTURE_GATE.md`.

## Next concrete action

Promote the render/export fixture group using temporary outputs only. Keep the
live symbol POST, field ingest, provider/GPU promotion and Git operations
deferred until explicit authority and rollback are named.

Last verified: 2026-08-15 America/Santiago — Phase 255 RD symbol fixture gate
passed; no persistent process.

## Phase 256 — latest authoritative update

The RD render/export fixture group passed 33 tests. It exercised temporary
packages and configuration outputs only; active products, assets, database,
browser and external delivery remained untouched. Evidence:
`context/PHASE256_RD_RENDER_FIXTURE_GATE.md`.

## Next concrete action

Promote the next pure RD catalogue/proposal fixture group, keeping generated
outputs temporary and external delivery disabled. Live field ingest, mutators,
providers/GPU and Git operations remain gated.

Last verified: 2026-08-15 America/Santiago — Phase 256 RD render fixture gate
passed; no persistent process.

## Phase 257 — latest authoritative update

The pure RD catalogue/proposal fixture group passed 50 tests. Drafts,
manifests and generated packages stayed in temporary roots; active products,
databases, providers and delivery systems were untouched. Evidence:
`context/PHASE257_RD_CATALOGUE_FIXTURE_GATE.md`.

## Next concrete action

Promote the next read-only Research/Codex fixture group, excluding provider
calls and network-backed execution. Keep live RD ingest, mutator POSTs,
provider/GPU promotion and Git operations deferred.

Last verified: 2026-08-15 America/Santiago — Phase 257 RD catalogue fixture gate
passed; no persistent process.

## Phase 258 — latest authoritative update

The read-only Research/Codex contract group passed 81 tests. It verified source
and configuration boundaries without contacting providers or network-backed
research. No persistent state changed. Evidence:
`context/PHASE258_RESEARCH_CODEX_CONTRACT_GATE.md`.

## Next concrete action

Promote one bounded local research-state/queue fixture group, keeping worker
threads and provider/network calls disabled. Live RD ingest, mutator POSTs,
provider/GPU promotion and Git operations remain gated.

Last verified: 2026-08-15 America/Santiago — Phase 258 Research/Codex contract
gate passed; no persistent process.

## Phase 259 — latest authoritative update

The local Research state/queue fixture group passed 58 tests. Checkpoints,
pause/resume and health/routing boundaries were exercised with temporary files
and monkeypatched dependencies; no worker, provider, service or live queue was
used. Evidence: `context/PHASE259_LOCAL_RESEARCH_STATE_GATE.md`.

## Next concrete action

Promote the next local Curatoria/platform fixture group, keeping watchdogs,
workers, issue creation and external integrations disabled. Live RD ingest,
mutator POSTs, provider/GPU promotion and Git operations remain gated.

Last verified: 2026-08-15 America/Santiago — Phase 259 local Research state
gate passed; no persistent process.

## Phase 260 — latest authoritative update

The local Curatoria/platform fixture group passed 71 tests. External calls were
faked and queue/ledger state was temporary; no watchdog, worker, GitHub,
service or GPU probe ran. Evidence:
`context/PHASE260_CURATORIA_PLATFORM_FIXTURE_GATE.md`.

## Next concrete action

Run the remaining static/local platform projections that do not invoke workers,
issue providers or external integrations. Then refresh the objective matrix
before considering any authorized live gate. Keep field ingest, mutator POSTs,
provider/GPU promotion and Git operations deferred.

Last verified: 2026-08-15 America/Santiago — Phase 260 Curatoria/platform
fixture gate passed; no persistent process.

## Phase 261 — latest authoritative update

The organ inventory and portable activity/GPU fixture group passed 5 tests.
The worker was stubbed and state/locks were temporary; no worker, hardware
probe, service or external integration ran. Evidence:
`context/PHASE261_ORGANS_GPU_FIXTURE_GATE.md`.

## Next concrete action

Refresh the objective matrix and residual inventory with the fixture gates now
closed. Preserve the thread/worker/provider tests as separately gated work;
keep live field ingest, mutator POSTs and Git operations deferred.

Last verified: 2026-08-15 America/Santiago — Phase 261 organs/GPU fixture gate
passed; no persistent process.

## Phase 262 — latest authoritative update

Refreshed the 13-objective matrix after the fixture gates. Local RD,
Research/Codex, Curatoria/platform and organ/GPU slices are validated in
isolation; external gates remain explicit. Physical recheck: 0 active cron
entries, no persistent FLUJO/hub/worker/n8n/ollama process, `rd.db` integrity
ok, and `rd_datos.db` integrity ok with zero rows and unchanged hash. Evidence:
`context/PHASE262_OBJECTIVE_MATRIX_REFRESH.md`.

## Next concrete action

Keep the matrix as the decision boundary. Without a new external authorization,
continue only per-file static triage of the remaining risk tests; preserve live
ingest, worker/provider/mutator surfaces and Git operations.

Last verified: 2026-08-15 America/Santiago — Phase 262 objective matrix
refresh passed; no persistent process.

## Phase 263 — latest authoritative update

The residual test exclusion was refined with executable AST imports/calls.
After removing promoted fixture groups, 138 files remain: 76 executable-risk
and 62 keyword/fixture candidates; all parse. An initial analyzer bug exited 1
without side effects, then the corrected analyzer exited 0. Evidence:
`context/PHASE263_RESIDUAL_RISK_TRIAGE.md`.

## Next concrete action

Inspect the 62 keyword/fixture candidates in small source-only or `tmp_path`
groups. Do not batch-run the 76 executable-risk files; preserve XIO, n8n,
worker, provider and live mutation surfaces.

Last verified: 2026-08-15 America/Santiago — Phase 263 residual risk triage
passed; no persistent process.

## Phase 264 — latest authoritative update

The bounded airdrop/CLI/contract fixture group passed 68 tests. Airdrop
apply/rollback was simulated only under temporary roots; the autonomy group
with its historical SSH path was excluded. No persistent or external state
changed. Evidence:
`context/PHASE264_AIRDROP_CLI_CONTRACT_GATE.md`.

## Next concrete action

Continue with remaining keyword/fixture candidates, prioritizing pure
source/configuration and temporary index/data tests. Keep autonomy, workers,
providers, XIO, n8n and live mutators excluded.

Last verified: 2026-08-15 America/Santiago — Phase 264 airdrop/CLI contract
gate passed; no persistent process.

## Phase 265 — latest authoritative update

The local ISKVW/Research fixture group passed 105 tests. Temporary fixtures and
faked URL/Git boundaries were used; no live external or persistent state ran.
The destructive cron-nocturno test remains intentionally excluded. Evidence:
`context/PHASE265_LOCAL_ISKVW_RESEARCH_FIXTURE_GATE.md`.

## Next concrete action

Continue with remaining pure fixture candidates, then recalculate the residual
static count and refresh the objective matrix. Keep live ingest, workers,
providers, XIO, n8n, mutators and Git operations gated.

Last verified: 2026-08-15 America/Santiago — Phase 265 local ISKVW/Research
fixture gate passed; no persistent process.

## Phase 266 — latest authoritative update

The missing active Claude workflow contract was repaired safely: manual-only,
`if: false`, no permissions, no issue/PR trigger and no writes. The historical
WIN workflow remains evidence only. The affected 16-file local candidate group
passed 188 tests after the repair; no workflow was dispatched. Evidence:
`context/PHASE266_DISABLED_CLAUDE_WORKFLOW_GATE.md`.

## Next concrete action

Recalculate the residual candidate inventory, then continue only with pure
fixture groups. Keep external/provider/worker/XIO/n8n and live mutation paths
deferred.

Last verified: 2026-08-15 America/Santiago — Phase 266 disabled Claude
workflow gate passed; no persistent process.

## Phase 267 — latest authoritative update

The CLI command manifest was reconciled from the real CLI. The generator now
describes `autonomia run` without SSH, regenerated `MAPA.md` and
`context/comandos.json` for 95 commands, and its check passed exit 0. The
focused ISKVW/validator group passed 110 tests. WIN and runtime data were
untouched. Evidence:
`context/PHASE267_CLI_MANIFEST_RECONCILIATION.md`.

## Next concrete action

Recalculate the residual risk inventory after these 13 additional promoted
tests. Continue only with pure local candidates; keep XIO, n8n, workers,
providers, external integrations and live mutators deferred.

Last verified: 2026-08-15 America/Santiago — Phase 267 CLI manifest
reconciliation passed; no persistent process.

## Phase 268 — latest authoritative update

The residual inventory is now quantified after the local fixture gates: 91
promoted files, 89 residual, 63 executable-risk and 26 explicitly bounded by
external/worker/destructive/XIO surfaces; all parsed. The next work is the
physical architecture/consumer gap, not another blanket test batch. Evidence:
`context/PHASE268_RESIDUAL_BOUNDARY_AND_ARCHITECTURE_HANDOFF.md`.

## Next concrete action

Compare the existing architecture disposition against current physical
consumers under `/home/mak/*`; produce the gap list of paths still needing a
real owner/consumer decision before Git branch work.

Last verified: 2026-08-15 America/Santiago — Phase 268 residual boundary
passed; no persistent process.

## Phase 269 — latest authoritative update

The physical architecture gap list is now explicit for all previously
unmapped root side surfaces. External configuration, deploy tooling, host
directories, installers, diagnostics, narratives and optional tools are
preserved with owner/disposition; no broad move or deletion was performed.
Evidence: `context/PHASE269_PHYSICAL_ARCHITECTURE_GAP_LIST.md`.

## Next concrete action

Audit `/home/mak/plataforma/interfaz.py` against all non-Git active consumers
and its canonical projection. If it has no consumer and the replacement is
verified, prepare a reversible quarantine record; do not delete it.

Last verified: 2026-08-15 America/Santiago — Phase 269 physical architecture
gap list passed; no persistent process.

## Phase 270 — latest authoritative update

The unconsumed legacy platform Research UI was moved to a phase quarantine,
not deleted. Hash `6712ddff059e...` and mode `644` were preserved; the active
Research projection remained canonical and all five relevant units stayed
inactive. Focused AST/reference/tests passed. Evidence:
`context/PHASE270_PLATFORM_UI_QUARANTINE.md`.

## Next concrete action

Reconcile the objective matrix for this path-level architecture/cleanup gate,
then audit remaining platform-root candidates (`install_mak.sh`, legacy
installer and optional provider tools) without executing them.

Last verified: 2026-08-15 America/Santiago — Phase 270 legacy platform UI
quarantine passed; no persistent process.

## Phase 271 — latest authoritative update

The remaining root installer, diagnostic and optional-provider surfaces were
audited from `/home/mak/*`. Five shell scripts passed `bash -n`, two Python
tools passed AST parsing, and the bounded active-consumer scan found no
references in the canonical/runtime departments. The installers were not run:
one mutates token/service state and the other installs/starts Docker with a
restart policy. Provider tools remain credential/network gated. No files were
moved or deleted. Evidence:
`context/PHASE271_ROOT_TOOL_SURFACE_AUDIT.md`.

## Next concrete action

Refresh the objective matrix, then enumerate the final canonical folder tree
and select only named duplicate document/tool families with a consumer-backed
merge plan. Keep root installers, providers, diagnostics, XIO, n8n, workers,
live mutators and Git operations gated.

Last verified: 2026-08-15 America/Santiago — Phase 271 root tool surface audit
passed; no persistent process.

## Phase 272 — latest authoritative update

The physical architecture was refreshed into a layered closeout and merge
queue. `/home/mak/flujo` remains canonical; department roots remain
consumer-backed projections; RD, media, databases, evidence, recovery and
WIN remain protected. The 13-objective matrix now records the remaining gates
and the ordered next review surfaces. No filesystem, database, service,
provider or Git state changed. Evidence:
`context/PHASE272_ARCHITECTURE_CLOSEOUT_AND_MERGE_QUEUE.md`.

## Next concrete action

Audit `/home/mak/lenguaje` statically, beginning from `/home/mak/*`, then
compare its consumers with the canonical FLUJO owner and runtime projection.
Do not move files until the bounded consumer/rollback report exists. Keep
root installers, providers, diagnostics, XIO, n8n, workers, live mutators and
Git operations gated.

Last verified: 2026-08-15 America/Santiago — Phase 272 architecture closeout
and merge queue passed; no persistent process.

## Phase 273 — latest authoritative update

The language surface is load-bearing. `/home/mak/lenguaje` is directly used by
platform manifests/hooks and owns dictionaries plus lexicon state, while the
six matching files under `flujo/cultura/mak_lenguaje` are byte-identical
semantic projections. A safe fusion is not a deletion: the root projection
stays in place until a path-injection migration exists. Three Python files and
two shell files parsed successfully; five relevant units were inactive, the
installed crontab had zero active entries, and the focused language/mirror/
organ/entrypoint suite passed with code 0. Evidence:
`context/PHASE273_LANGUAGE_CONSUMER_GATE.md`.

The language ratchet was corrected to exclude reversible quarantine evidence;
two local CLI variable names were made ASCII-English without changing the
user-facing `valor_dia_clp` key. No hook, cron, service, provider, database,
WIN or external system was executed or changed.

## Next concrete action

Audit `/home/mak/trazos` statically from the physical root, then compare its
creative-source consumers with canonical FLUJO and generated RD outputs. Keep
source, deliveries, WIN, root installers, providers, diagnostics, XIO, n8n,
workers, live mutators and Git operations gated.

Last verified: 2026-08-15 America/Santiago — Phase 273 language consumer gate
passed; no persistent process.

## Phase 274 — latest authoritative update

The `trazos` gate found 649 XML-valid SVGs in `/home/mak/trazos` and 208
consumer-backed SVGs in `flujo/iskvw/piel/trazos`. All 208 published contents
occur in the root corpus, but the root also contains 429 additional paths and
29 duplicate-hash groups. Active code consumes the published projection and
index, not the root path directly. The source corpus therefore remains
protected creative/evidence material; no hash-based deletion or merge is safe.
The focused ISKVW/SVG/plano projection suite passed with code 0.
Evidence: `context/PHASE274_TRAZOS_SOURCE_PROJECTION_GATE.md`.

## Next concrete action

Audit `/home/mak/bucle` statically from the physical root, then compare its
source/project role with canonical FLUJO consumers. Keep cultural source,
generated media, root installers, providers, XIO, n8n, workers, live
mutators and Git operations gated.

Last verified: 2026-08-15 America/Santiago — Phase 274 trazos source/
projection gate passed; no persistent process.

## Phase 275 — latest authoritative update

The `bucle` surface was classified as a preserved visual/source project: two
valid SVGs, six PNGs, a license and a short README, with no code or active
references to its path. It is neither an active FLUJO tool nor confirmed
junk, and it will not be merged into RD, `trazos`, portfolio or renders by
extension/hash. No file or runtime state changed. Evidence:
`context/PHASE275_BUCLE_SOURCE_SURFACE_GATE.md`.

## Next concrete action

Audit `/home/mak/vibecodeine` statically from the physical root, separating
source project, active consumers, generated outputs and optional dependencies.
Do not launch creative tooling or merge by filename/hash; keep providers,
XIO, n8n, workers, mutators and Git operations gated.

Last verified: 2026-08-15 America/Santiago — Phase 275 bucle source surface
gate passed; no persistent process.

## Phase 276 — latest authoritative update

`/home/mak/vibecodeine` was identified as a 440 MB historical FLUJO snapshot,
not a loose tool. In bounded comparable trees it has 792 common relative paths,
635 byte-identical and 157 divergent. No active MAK consumer points to its
absolute path, but divergent departments/workers/contracts mean it cannot be
called garbage or removed by hash. It remains intact as historical/source
evidence while a family-level crosswalk is prepared. Evidence:
`context/PHASE276_VIBECODEINE_SNAPSHOT_GATE.md`.

## Next concrete action

Build the first bounded divergence report for `vibecodeine/src` versus active
`/home/mak/flujo/src`, prioritizing files with active MAK consumers. Keep
Windows launchers, workers, providers, XIO, n8n, mutators and Git operations
gated.

Last verified: 2026-08-15 America/Santiago — Phase 276 vibecodeine snapshot
gate passed; no persistent process.

## Phase 277 — latest authoritative update

The bounded `vibecodeine/src` crosswalk found 103 common paths: 87 identical,
16 divergent, 8 snapshot-only and 1 active-only. AST symbols show the active
FLUJO side is ahead in the examined source slice, so no historical function
was promoted. The focused active RD/CLI/hub/intake/airdrop/ISKVW suite exposed
and then passed a checkout fix: the hub now supplies `<repo>/src` to its safe
child command runner only for source checkouts. No package, service, provider,
database, worker, WIN or snapshot state changed. Evidence:
`context/PHASE277_VIBECODEINE_SRC_DIVERGENCE_GATE.md`.

## Next concrete action

Crosswalk `vibecodeine/cultura/mak_plataforma` and `mak_research`, the largest
divergent department families, by active consumer and platform. Do not copy
trees, launch workers/services or promote snapshot code without a named
consumer and foreground gate.

Last verified: 2026-08-15 America/Santiago — Phase 277 vibecodeine source
divergence gate passed; no persistent process.

## Phase 278 — latest authoritative update

The snapshot department crosswalk is complete for `mak_plataforma` and
`mak_research`. Platform has 49 snapshot files vs 61 active, with 16 exact and
28 divergent common paths; Research has 41 vs 41, with 20 exact and 20
divergent. All divergent Python files parsed on both sides. Active-only files
show current providers, ledger, routing, review, batching and runtime gates;
snapshot-only files are doctrine/history. No historical file was promoted or
deleted. Evidence:
`context/PHASE278_VIBECODEINE_DEPARTMENT_CROSSWALK.md`.

## Next concrete action

Finish the snapshot gate with bounded `vibecodeine/data` and generated-output
crosswalk, distinguishing configuration/catalog from protected products. Do
not compare or remove full media trees; use manifests and consumer paths.

Last verified: 2026-08-15 America/Santiago — Phase 278 vibecodeine department
crosswalk passed; no persistent process.

## Phase 279 — latest authoritative update

The bounded vibecodeine data/output crosswalk found 111 common declarative
paths, 111 byte-identical and six divergent; all 53 snapshot and 64 active
JSON files parsed validly. The two `datadrops` trees share 19 named product
files, which remain protected generated/source evidence. Vibecodeine is now
classified as a historical snapshot pending only future family-level review;
no whole-tree fusion or cleanup occurred. Evidence:
`context/PHASE279_VIBECODEINE_DATA_OUTPUT_GATE.md`.

## Next concrete action

Audit `/home/mak/flujo-deploy` and `/home/mak/bin/mak_sync_safe.py` statically
as an external deployment surface. Check references and syntax only; do not
deploy, sync, copy trees, use Git or start services.

Last verified: 2026-08-15 America/Santiago — Phase 279 vibecodeine data/output
gate passed; no persistent process.

## Phase 280 — latest authoritative update

The separate deploy surface was audited. `/home/mak/bin/mak_sync_safe.py`
parses successfully, but it performs fetch/reset/copy, drift backups and an
atomic deploy manifest write; its only operational manifest references are
paused and the installed crontab has zero active entries. It remains a
separate external deploy owner and was not run. Evidence:
`context/PHASE280_DEPLOY_SURFACE_GATE.md`.

## Next concrete action

Reconcile the final root-side review list (`model-config`, `searxng`, old
Blender/provider environments and loose narratives) against the owner map,
then produce the visual architecture closeout and Git-branch proposal update.
Keep external/mutating surfaces, WIN and Git operations gated.

Last verified: 2026-08-15 America/Santiago — Phase 280 deploy surface gate
passed; no persistent process.

## Phase 281 — latest authoritative update

The remaining root external surfaces were reconciled. `model-config`,
`searxng` and `venv-providers` remain protected optional infrastructure;
current and old Blender installations remain separate because their binaries
differ and active render tools may resolve Blender by PATH. Loose root files
retain the Phase 271 dispositions. No external process, provider, renderer,
installer, secret, database, WIN or Git state changed. Evidence:
`context/PHASE281_ROOT_EXTERNAL_REVIEW.md`.

## Next concrete action

Create the visual architecture closeout and reconcile it with the existing
branch proposal. Keep branch creation/merge, deploy, providers/GPU, Blender,
XIO, n8n and live mutators gated.

Last verified: 2026-08-15 America/Santiago — Phase 281 root external review
passed; no persistent process.

## Phase 282 — latest authoritative update

The visual architecture closeout is ready. It shows canonical FLUJO,
consumer-backed projections, protected RD/data/media, evidence/recovery,
external infrastructure, historical WIN/vibecodeine and excluded n8n/XIO as
separate layers. It also aligns the proposed disjoint-write-set branch order
without creating or switching any branch. Evidence:
`context/PHASE282_VISUAL_ARCHITECTURE_CLOSEOUT.md`.

## Next concrete action

Use the closeout to select the first explicitly authorized architecture slice.
Until that authority exists, continue only with safe static/provenance checks;
do not create branches, merge, deploy, run providers/GPU/Blender, start
workers/services or execute live mutators.

Last verified: 2026-08-15 America/Santiago — Phase 282 visual architecture
closeout passed; no persistent process.

## Phase 283 — latest authoritative update

The 13-objective requirement audit is now current. Catalog fusion, local
non-serve commands, asset fixtures, dependency checks and architecture are
verified; RD field/live mutators, automation re-enable, optional runtimes,
full operational coverage, further cleanup and Git operation remain explicitly
gated or partial. The audit does not claim completion. Evidence:
`context/PHASE283_OBJECTIVE_REQUIREMENT_AUDIT.md`.

## Next concrete action

Select the next pure local residual-test family from Phase 268, verify its
write set is temporary/read-only, run it foreground and record the result.
Keep live RD ingest/mutators, providers, workers, XIO, n8n, deploy and Git
operations gated.

Last verified: 2026-08-15 America/Santiago — Phase 283 objective requirement
audit passed; no persistent process.

## Phase 284 — latest authoritative update

The selected safe residual family passed 32 tests: visual review/idempotency
fixtures, Research routing and mocked Research-library network behavior. All
writes were temporary or mocked; no real URL, provider, worker, service,
mutator, XIO, n8n or Git boundary was executed. Evidence:
`context/PHASE284_SAFE_RESIDUAL_REVIEW_GATE.md`.

## Next concrete action

Continue with one more pure/mock-only residual family if its temporary write
set can be proven; otherwise return to provenance crosswalk and keep all
externally bound residual tests gated.

Last verified: 2026-08-15 America/Santiago — Phase 284 safe residual review
gate passed; no persistent process.

## Phase 285 — latest authoritative update

The next pure/mock residual group passed 87 tests: Codex fallback, icon
compilation with a fake model, temporary micelio sync, Research formats and
source-quality gates. Only existing Pillow deprecation warnings appeared. No
provider, worker, service, cron, XIO, n8n, Git, live database or external
system was touched. Evidence:
`context/PHASE285_SAFE_MOCK_FIXTURE_GATE.md`.

## Next concrete action

Inspect the residual inventory for another pure/mock family. If none remains,
refresh the objective audit with measured local coverage and continue only
with provenance/authority-gated work.

Last verified: 2026-08-15 America/Santiago — Phase 285 safe mock/fixture gate
passed; no persistent process.

## Phase 286 — latest authoritative update

The next safe local group passed 61 tests: image analysis, autofit, brand,
coherence, cotizaciones, dashboard, datadrop and debate fixtures. Writes were
temporary or monkeypatched; no real RD media/data, service, provider, worker,
cron, XIO, n8n, Git or external state changed. Evidence:
`context/PHASE286_SAFE_LOCAL_SURFACE_GATE.md`.

## Next concrete action

Refresh the objective audit and residual coverage ledger with Phases 284–286,
then inspect whether any unexecuted residual file has a provably temporary
write set. Do not widen execution authority by filename alone.

Last verified: 2026-08-15 America/Santiago — Phase 286 safe local surface gate
passed; no persistent process.

## Phase 287 — latest authoritative update

Phases 284–286 add 180 passing test executions across review, mocked Research,
fallback, icon, micelio, format, source, image, dashboard, datadrop and debate
surfaces. This expands bounded local evidence but does not claim full MAK
runtime completion. Workers, subprocess, network/provider, live issue bridge,
destructive scheduler, render/show, Git, XIO, n8n, deploy and live RD mutator
boundaries remain gated. Evidence:
`context/PHASE287_RESIDUAL_COVERAGE_REFRESH.md`.

## Next concrete action

Inspect the remaining unexecuted files one at a time for a temporary-only write
set. If none qualifies, stop execution expansion and preserve the authority
boundary while maintaining the handoff.

Last verified: 2026-08-15 America/Santiago — Phase 287 residual coverage
refresh passed; no persistent process.

## Phase 288 — latest authoritative update

The offline subprocess candidate passed 8 tests: ISKVW measurement with a dead
local port and temporary output, Adobe read-only checks and flyer activation in
`tmp_path`. No effective network, provider, service, worker, cron, live RD
data, XIO, n8n, Git or external state was touched. Evidence:
`context/PHASE288_OFFLINE_SUBPROCESS_GATE.md`.

## Next concrete action

Refresh the objective audit with Phases 284–288 and perform a final physical
invariant check. Leave authority-gated objectives open; do not claim full
completion.

Last verified: 2026-08-15 America/Santiago — Phase 288 offline subprocess gate
passed; no persistent process.

## Phase 289 — latest authoritative update

The objective refresh records 188 bounded passing test executions from Phases
284–288 and rechecked physical invariants: cron active count 0, both RD
databases integrity `ok`, `rd_datos.db` field rows 0, five MAK units inactive,
and no matching MAK runtime process observed. The 13 objectives remain
explicitly classified; authority-gated requirements are not claimed complete.
Evidence:
`context/PHASE289_OBJECTIVE_REFRESH_AND_INVARIANTS.md`.

## Next concrete action

Maintain this checkpoint and continue only with a new static/provenance slice
or explicit authority. The next safe candidate is a path-specific consumer
audit; no broad test execution, cleanup, deploy or Git operation follows from
this refresh alone.

Last verified: 2026-08-15 America/Santiago — Phase 289 objective refresh and
physical invariants passed; no persistent process.

## Phase 290 — latest authoritative update

The Curatoria candidate family was compared directly. Five documents and the
970-row `candidatos_db.jsonl` are exact byte/hash duplicates between
`/home/mak/curatoria/db` and the canonical FLUJO docs path. The active producer
uses the canonical path, but the old copy is generated evidence, so it is
classified `PROTECTED_EXACT_DUPLICATE`, not junk; no move, symlink or deletion
was performed. Evidence:
`context/PHASE290_CURATORIA_DUPLICATE_GATE.md`.

## Next concrete action

Review the next named duplicate family only if it is not protected evidence.
Inspect source/runtime consumers and preserve generated outputs; do not widen
this into broad duplicate deletion.

Last verified: 2026-08-15 America/Santiago — Phase 290 Curatoria duplicate
preservation gate passed; no persistent process.

## Phase 291 — latest authoritative update

The fallback helper was confirmed as logically fused by consumer: four
load-bearing copies share one SHA-256, Codex is the declared semantic owner,
Research is a byte-identical mirror, and both runtime projections are required
by their department imports. The fallback/provider-health suite passed 44
tests without provider calls. No file moved or changed. Evidence:
`context/PHASE291_FALLBACK_TOOL_OWNER_GATE.md`.

## Next concrete action

Apply the same owner/projection check to the next shared tool only when its
consumer paths are explicit. Do not consolidate divergent provider or worker
variants by filename similarity.

Last verified: 2026-08-15 America/Santiago — Phase 291 fallback tool owner
gate passed; no persistent process.

## Phase 292 — latest authoritative update

The `contrato_archivo` family is correctly fused: one 1,177-line canonical
implementation in `flujo/cultura/mak_plataforma` and a 1,132-byte compatibility
shim at `/home/mak/plataforma/contrato_archivo.py` serving historical direct
callers. Hub, ISKVW, Curatoria and laser consumers were covered by 29 passing
tests. No shim, service, database, provider or external state changed.
Evidence: `context/PHASE292_ARCHIVE_CONTRACT_OWNER_GATE.md`.

## Next concrete action

Use this owner/shim pattern as the reference for the next equivalent-tool
family; prioritize thin projections and do not merge divergent implementations.

Last verified: 2026-08-15 America/Santiago — Phase 292 archive contract owner
gate passed; no persistent process.

## Phase 293 — latest authoritative update

The `filtro_entrada.py` family is now fused by owner: the canonical
implementation remains at `/home/mak/flujo/cultura/mak_plataforma/filtro_entrada.py`
and `/home/mak/plataforma/filtro_entrada.py` is a 1,499-byte compatibility
projection preserving direct Research/Codex imports and its CLI. The root
projection, canonical module, heuristic contract, direct path import and CLI
were validated in the foreground. Research router, GPU activity and research
library unittest files passed (the available Python has no pytest module, so no
installation was attempted). No data, WIN evidence, service, provider,
scheduler or external state changed. Evidence:
`context/PHASE293_FILTER_OWNER_GATE.md`.

## Next concrete action

Continue the owner/projection audit with the next exact platform family, first
checking direct consumers and entrypoint semantics. Candidate order is
`hub.py`, `actividad.py`, then `research_router.py`; do not touch divergent
platform modules (`backlog.py`, `capataz.py`, `salud.py`, `vigilar_red.py`,
`roles.py`, `trabajo.py`) without a separate semantic crosswalk. Preserve
runtime projections that have named consumers and do not remove evidence.

Last verified: 2026-08-15 America/Santiago — Phase 293 filter owner gate
passed; no persistent process.

## Phase 294 — latest authoritative update

The `actividad.py` family is now fused by owner: the canonical implementation
remains in `flujo/cultura/mak_plataforma` and `/home/mak/plataforma/actividad.py`
is a compatibility projection preserving direct imports, path overrides and
the CLI. Existing pytest cases for GPU/activity and Research routing passed
(24 tests) using the already-installed Research virtual environment; a
temporary record/read/inventory contract and read-only CLI check also passed.
No activity log, database, WIN evidence, service, provider or scheduler was
changed. Evidence: `context/PHASE294_ACTIVITY_OWNER_GATE.md`.

`hub.py` was inspected but not shimmed: its exact duplicate imports divergent
platform modules and a naive canonical loader would change `sys.path` and
dependency resolution. That is a deferred semantic crosswalk, not a blocker.

## Next concrete action

Audit `research_router.py` as the next exact platform projection. Verify its
direct consumers, import path, entrypoint behavior and tests before any
projection edit. Keep `hub.py`, `backlog.py`, `capataz.py`, `salud.py`,
`vigilar_red.py`, `roles.py` and `trabajo.py` unchanged until their divergent
dependency surfaces are mapped.

Last verified: 2026-08-15 America/Santiago — Phase 294 activity owner gate
passed; no persistent process.

## Phase 295 — latest authoritative update

The `research_router.py` family is now fused by owner: the canonical
deterministic router remains in `flujo/cultura/mak_plataforma` and
`/home/mak/plataforma/research_router.py` is a 1,013-byte compatibility
projection. The route suite passed, and direct root-path import plus
an RD factual-event contract passed. The first shim attempt exposed and fixed
a `dataclass` loader registration issue; no data or runtime state changed.
Evidence: `context/PHASE295_RESEARCH_ROUTER_OWNER_GATE.md`.

## Next concrete action

The simple exact projection queue is exhausted. Begin a dependency crosswalk
for `/home/mak/plataforma/hub.py` before any edit: map every imported platform
module, compare canonical versus runtime versions, identify which imports are
intentional projections, and validate a temporary import/health contract only.
Do not shim Hub blindly; do not start its service or call POST/render/provider
routes. Keep divergent `backlog.py`, `capataz.py`, `salud.py`,
`vigilar_red.py`, `roles.py` and `trabajo.py` unchanged until the crosswalk is
complete.

Last verified: 2026-08-15 America/Santiago — Phase 295 research router owner
gate passed; no persistent process.

## Phase 296 — latest authoritative update

The Hub dependency crosswalk found no remaining divergent implementation in
its local runtime set: apparent differences (`salud`, `backlog`, `revision`,
`roles`, `trabajo`, contrato, actividad and filtro) are already canonical
shims, while the rest are exact or intentionally Curatoria-owned. The root
`/home/mak/plataforma/hub.py` is now a 1,044-byte runtime alias to the
canonical Hub. Hub event, health and durable-writer tests passed (30 tests),
plus root import/global-patch and static CLI forwarding checks. The service
remained inactive. Evidence: `context/PHASE296_HUB_DEPENDENCY_OWNER_GATE.md`.

## Next concrete action

Move from exact projections to the first semantic crosswalk: inspect
`/home/mak/flujo/cultura/mak_plataforma/salud.py` against its runtime callers,
root shim, health data paths and focused tests. Then inspect `roles.py` and
the other divergent families. Do not alter live service state or providers;
do not treat a small shim, a generated report or a stale runtime path as junk
without consumer and rollback proof.

Last verified: 2026-08-15 America/Santiago — Phase 296 Hub owner gate
passed; no persistent process.

## Phase 297 — latest authoritative update

The `salud.py` family was inspected and required no edit: the root path is
already a working compatibility shim with CLI forwarding to the canonical
read-only system snapshot. Health/provider/capataz tests passed (52 tests),
the root CLI returned valid JSON with all required fields and 5 service
entries, and `mak-hub.service` remained inactive. Evidence:
`context/PHASE297_SALUD_PROJECTION_GATE.md`.

## Next concrete action

Crosswalk `/home/mak/flujo/cultura/mak_plataforma/roles.py` against
`/home/mak/plataforma/roles.py`, `trabajo.py`, `crontab.mak`, installed user
units and the current paused scheduler state. Determine whether the root shim
preserves direct CLI/module contracts and whether any stale path or platform
assumption remains. Inspect only; do not re-enable cron, workers, providers or
services.

Last verified: 2026-08-15 America/Santiago — Phase 297 salud projection gate
passed; no persistent process.

## Phase 298 — latest authoritative update

The `roles.py` and `trabajo.py` projections are valid canonical shims. Their
policy/runner imports passed, backlog and maintenance tests passed (75 tests),
the installed crontab has 0 active entries, and all five MAK user units remain
inactive. The scheduler template is evidence only and was not installed.
The broader tanda batch exposed three stale/invalid fixture expectations:
strict evidence validation correctly returns `revise` for nonexistent
`tools/contexto_repo.py`, while those tests expect `accepted`. No scheduler,
provider, worker or source runtime was changed. Evidence:
`context/PHASE298_ROLES_SCHEDULER_GATE.md`.

## Next concrete action

Reproduce and resolve the three `tandas` strict-product fixture failures using
only temporary evidence paths. Keep `validate_evidence_paths` strict; either
repair the tests to create/provide the evidence fixture or document a real
contract bug with a focused source fix. Run the corrected test family and
record changed files, rollback and result. Do not activate the scheduler or
call external providers.

Last verified: 2026-08-15 America/Santiago — Phase 298 roles/scheduler gate
passed; no persistent process.

## Phase 299 — latest authoritative update

The three `tandas` strict-evidence failures were repaired at the fixture
level: each test now creates a temporary `contexto_repo.py` and passes it via
the existing `paths` allow-list. Production evidence validation stayed
strict, and the full `tests/test_mak_tandas.py` suite passed (49 tests).
Evidence: `context/PHASE299_TANDAS_EVIDENCE_FIXTURE_GATE.md`.

## Next concrete action

Audit `/home/mak/flujo/cultura/mak_plataforma/vigilar_red.py` and its runtime
projection/consumers from `/home/mak/*`. Map whether it is a read-only health
check, a network mutator or an obsolete Windows path. Compile/import only;
do not call network endpoints, start services, or re-enable the scheduler.

Last verified: 2026-08-15 America/Santiago — Phase 299 tandas evidence fixture
gate passed; no persistent process.

## Phase 300 — latest authoritative update

The `vigilar_red`/`red_watch` family was statically classified. The canonical
monitor reads connections, writes a state JSON and can notify an external
`ntfy` destination; the companion probes external Internet and records
transitions. Both compile, their wrapper/atomic-state tests pass (10 tests),
and no network, notification, file state, scheduler or service was touched.
The installed crontab remains empty. Evidence:
`context/PHASE300_NETWORK_MONITOR_BOUNDARY_GATE.md`.

## Next concrete action

Return to a local deterministic consumer family. Start with `backlog.py` and
`capataz.py`: verify their canonical/runtime projections, callers, focused
tests and write sets without invoking autonomous work. Keep network monitors,
providers, cron, workers, services, XIO and mutating routes gated.

Last verified: 2026-08-15 America/Santiago — Phase 300 network boundary gate
passed; no persistent process.

## Phase 301 — latest authoritative update

The local platform risk family (`backlog`, `capataz`, `revision`) was compiled,
imported through runtime projections and covered by 96 passing mock/temporary
tests. Their write/subprocess/HTTP boundaries remain gated; no live path was
executed. Evidence: `context/PHASE301_LOCAL_PLATFORM_RISK_GATE.md`.

## Next concrete action

Build a bounded projection matrix for every Python file under
`/home/mak/flujo/cultura/mak_plataforma` versus `/home/mak/plataforma`,
classifying exact, shim, source-divergent and missing pairs. Use the matrix to
choose the next unreviewed consumer family and avoid repeating existing owner
gates. No services, providers, workers, cron, external network or mutators.

Last verified: 2026-08-15 America/Santiago — Phase 301 local platform risk gate
passed; no persistent process.

## Phase 302 — latest authoritative update

The complete top-level platform projection matrix is now measured: 50 paired
Python files, 25 exact pairs, 21 canonical shims, 0 source-divergent pairs,
and 4 runtime-only files. The remaining unowned candidates are
`/home/mak/plataforma/agente_real.py`, `memoria.py`, `panel_directivo.py` and
`vigia.py`; they are not classified as junk yet. No file changed. Evidence:
`context/PHASE302_PLATFORM_PROJECTION_MATRIX.md`.

## Next concrete action

Audit those four runtime-only files from `/home/mak/*`: identify active
consumers, department ownership, Windows/history provenance, dependencies,
language and write sets. Start with static AST/import/path checks and bounded
text references; do not execute them or quarantine anything until a real
consumer and rollback decision exists.

Last verified: 2026-08-15 America/Santiago — Phase 302 platform projection
matrix passed; no persistent process.

## Phase 303 — latest authoritative update

Two confirmed unconsumed stale projections were moved reversibly to
`context/quarantine/phase303_orphan_platform_projections`: the old platform
copies of Research `memoria.py` and Vigia `vigia.py`. Canonical active
consumers remain `/home/mak/research/memoria.py` and `/home/mak/vigia/vigia.py`.
Hashes, modes and sizes were preserved; no evidence was deleted. Evidence:
`context/PHASE303_RUNTIME_ONLY_QUARANTINE.md`.

## Phase 304 — latest authoritative update

The material runtime contract was repaired: `/home/mak/plataforma/material.py`
now aliases the canonical module for imports and still forwards its CLI.
`trabajo` can again call `material.pop_pendiente()`. The selected work,
micelio and tanda tests passed; no queue, scheduler, provider or external state
changed. Evidence: `context/PHASE304_MATERIAL_IMPORT_OWNER_GATE.md`.

## Next concrete action

Classify the remaining runtime-only files
`/home/mak/plataforma/agente_real.py` and
`/home/mak/plataforma/panel_directivo.py`: find active consumers, optional
manual entrypoints, dependencies, writes and historical provenance. Preserve
them unless a concrete redundant path and rollback are proven.

Last verified: 2026-08-15 America/Santiago — Phase 304 material owner gate
passed; no persistent process.

## Phase 305 — latest authoritative update

The final two platform runtime-only files were classified and quarantined
reversibly: broken unowned `panel_directivo.py` and unconsumed optional
`agente_real.py`. Their hashes/modes/sizes are preserved, reference/entrypoint
tests pass (7 tests), and no active cron/unit/process points to them. Evidence:
`context/PHASE305_OPTIONAL_TOOL_QUARANTINE.md`.

## Next concrete action

Run a fresh physical invariant and active Python AST summary across `/home/mak`
after the selective quarantine and material import repair. Reconcile the
objective ledger: distinguish completed local slices from still-gated live RD
mutators, paused automation, providers, external monitors, optional runtimes,
cleanup and Git proposal. Do not claim full completion while those gates are
open.

Last verified: 2026-08-15 America/Santiago — Phase 305 optional-tool
quarantine passed; no persistent process.

## Phase 306 — latest authoritative update

Physical invariants remain clean after the selective quarantines and material
repair: both RD databases pass SQLite integrity, `rd_datos.db` has 0 test
rows, installed crontab has 0 active entries, all five MAK units are inactive,
and no matching persistent process was observed. The objective ledger now
separates completed local owner/projection work from live RD, automation,
optional-runtime and Git authority gates. Evidence:
`context/PHASE306_PHYSICAL_INVARIANT_REFRESH.md`.

## Next concrete action

Prepare the visual/objective closeout from the current evidence, then continue
only with a named authority gate: real RD field input, one live mutator with
rollback, optional dependency promotion, automation re-enable or Git branch
operation. Until such authority is explicit, preserve the clean local state,
WIN history and quarantine rollback paths; do not claim the house is 100%
operational beyond the verified local surface.

Last verified: 2026-08-15 America/Santiago — Phase 306 physical invariant
refresh passed; no persistent process.

## Phase 307 — latest authoritative update

The visual/objective closeout is recorded in
`context/PHASE307_VISUAL_OBJECTIVE_CLOSEOUT.md`. It maps the canonical FLUJO
owner, runtime projections, WIN history, separate RD databases, reversible
quarantines, local proof and the five remaining authority gates. This is a
continuity artifact, not a completion claim; local work is stable and no
service, cron, provider, network, live mutator or Git operation was performed.

## Next concrete action

Use the closeout as the resume point. Continue automatically only on a safe
local verification or when one of the named authority gates becomes explicit;
otherwise preserve the current state and do not invent external authority.

Last verified: 2026-08-15 America/Santiago — Phase 307 visual objective
closeout recorded; no persistent process.

## Phase 308 — latest authoritative update

The language department was audited from `/home/mak/*`. The four Python
modules in `/home/mak/flujo/cultura/mak_lenguaje` and
`/home/mak/lenguaje` are byte-identical and parse successfully, but the root
department owns live dictionary data, lexicon output and the hard-coded data
contract used by the code. Therefore it is a consumer-backed protected
projection, not disposable duplication. Pure measurement parity, temporary
lexicon generation, temporary-file CLI JSON, shell syntax and static consumer
crosswalk all passed. No MAK file, database, output, cron entry, provider or
service changed. Evidence: `context/PHASE308_LANGUAGE_CONSUMER_GATE.md`.

## Next concrete action

Audit `/home/mak/trazos` as the next low-mutation review surface. Begin again
at `/home/mak/*`, identify source/output/evidence ownership and active
consumers in Spanish and English, then run only static or temporary fixture
checks. Do not move creative files, contact providers, activate language
automation or services, or modify WIN.

Last verified: 2026-08-15 America/Santiago — Phase 308 language consumer gate
passed; no persistent process.

## Phase 309 — latest authoritative update

The `/home/mak/trazos` surface was audited from the physical MAK roots. It
contains 649 one-path SVGs, all passed `flujo.laser.medir()` geometry
validation; 29 exact-hash groups cover 59 files. No metadata, job manifest,
same-basename output match or direct active runtime reference identifies a
canonical survivor. The active laser/trazador consumers write to FLUJO output
surfaces, not this root. The corpus is therefore valid generated/historical
creative material with unresolved human ownership, not confirmed junk. No
file changed. Evidence: `context/PHASE309_TRAZOS_CORPUS_GATE.md`.

## Next concrete action

Audit `/home/mak/bucle` from `/home/mak/*`, mapping its physical files,
Spanish/English consumers, provenance and any overlap with FLUJO projects.
Use static or temporary read-only validation only; do not merge cultural
source, delete creative evidence, contact providers, activate services or
modify WIN.

Last verified: 2026-08-15 America/Santiago — Phase 309 trazo corpus gate
passed; no persistent process.

## Phase 310 — latest authoritative update

The independent cultural surface `/home/mak/bucle` was audited excluding its
embedded Git metadata. It contains 10 non-Git visual/project files: 2 valid
SVGs, 6 valid PNGs, README and LICENSE; there are no internal exact duplicate
groups and no exact active runtime path consumer. Generic references to tapiz
or vibecodeine do not establish a consumer for this project. It remains
protected independent cultural source; no file changed. Evidence:
`context/PHASE310_BUCLE_CULTURAL_SURFACE_GATE.md`.

## Next concrete action

Audit `/home/mak/vibecodeine` from `/home/mak/*` as a separate source/dependency
surface. Exclude Git metadata from inventory, map exact active consumers and
platform/dependency boundaries, and run only static checks. Do not inspect Git
history, install packages, call providers, merge the project or modify WIN.

Last verified: 2026-08-15 America/Santiago — Phase 310 bucle cultural surface
gate passed; no persistent process.

## Phase 311 — latest authoritative update

The separate `/home/mak/vibecodeine` source clone was audited without using
its Git metadata. Outside Git it contains 10,655 files and its own runtime,
data, projects, tools, tests, web, XIO and virtual environment. There are zero
active local references to its filesystem path. A bounded comparison found
three exact shared modules (`lenguaje`, `laser`, `trazador`) but divergent CLI,
dependency, platform-role and research-source files, so the tree is not
mergeable as a unit. Selected clone files parsed 5/5. No file changed.
Evidence: `context/PHASE311_VIBECODEINE_SOURCE_GATE.md`.

## Next concrete action

Audit `/home/mak/flujo-deploy` and `/home/mak/bin/mak_sync_safe.py` as a
separate deploy/synchronization boundary. Inspect static consumers, write
sets, credentials/configuration and rollback only; do not run sync, Git,
services or external providers.

Last verified: 2026-08-15 America/Santiago — Phase 311 vibecodeine source gate
passed; no persistent process.

## Phase 312 — latest authoritative update

The remaining root-side external surfaces were classified. `/home/mak/blender`
has real static consumers and remains the live external runtime;
`/home/mak/blender-4.5.3-viejo` is an old unowned runtime candidate but was
not removed. `model-config`, `venv-providers`, SearXNG configuration and the
two host narratives remain protected external/operational evidence. Installer
syntax and standalone provider AST checks passed; no provider, Blender,
SearXNG, Ollama, sync or service process ran. No file changed. Evidence:
`context/PHASE312_EXTERNAL_RUNTIME_SURFACE_GATE.md`.

## Next concrete action

Build the bounded candidate manifest needed before any Git-branch proposal:
compare the old Blender installation at path level without launching it,
enumerate only confirmed regenerable residue and select exact duplicate
document families with a real consumer/owner. Do not print sensitive config,
delete evidence, merge trees, run providers or modify Git/WIN.

Last verified: 2026-08-15 America/Santiago — Phase 312 external runtime
surface gate passed; no persistent process.

## Phase 313 — latest authoritative update

The bounded candidate cleanup removed exactly 278 regenerable `*.pyc` files
from explicit active source/department roots, excluding environments,
rollback, backups, quarantine, logs and evidence. Source SHA remained
unchanged; safe cache count is now 0. The first health command failed only
because of an invalid PYTHONPATH and is recorded; the corrected
`PYTHONPATH=/home/mak/flujo/src:/home/mak/flujo python3 -m flujo health` passed
rc=0. Three critical modules parse, cron has 0 active entries and five MAK
units are inactive. Evidence: `context/PHASE313_REGENERABLE_RESIDUE_CLEANUP.md`.

## Next concrete action

Select and revalidate one named exact duplicate/projection family with a real
consumer and owner, then add it to the candidate manifest as
`CONSOLIDATE`, `PROTECT`, `QUARANTINE_CANDIDATE` or `UNRESOLVED`. Preserve
runtime projections until their launcher, language, write set and rollback
are proven. Do not modify WIN, Git, providers, services or protected data.

Last verified: 2026-08-15 America/Santiago — Phase 313 bounded cache cleanup
passed; no persistent process.

## Phase 314 — latest authoritative update

The archive contract family was revalidated as a real consumer-backed fusion:
`/home/mak/flujo/cultura/mak_plataforma/contrato_archivo.py` is the sole
1177-line implementation and `/home/mak/plataforma/contrato_archivo.py` is a
35-line importlib compatibility projection. The divergent hashes are
intentional; root import, symbol parity and portfolio/laser fixtures matched.
No file changed, process started or data touched. Evidence:
`context/PHASE314_ARCHIVE_CONTRACT_PROJECTION_GATE.md`.

## Next concrete action

Continue the bounded candidate manifest with the next unresolved duplicate
family that has a real consumer. Prefer one document/tool family with known
owner, consumer, language/platform contract and reversible disposition; do not
repeat exact projection families already closed or merge evidence by hash
alone.

Last verified: 2026-08-15 America/Santiago — Phase 314 archive contract
projection gate passed; no persistent process.

## Phase 315 — latest authoritative update

The curatoria diagnostic family was verified: canonical
`cultura/mak_curatoria/diagnostico_proyectos.py` and root
`/home/mak/curatoria/diagnostico_proyectos.py` are byte-identical, parse, show
CLI help and match on pure fixtures. Real consumers exist in the conductor,
producer catalog and coherence checks. An exploratory object-identity
assertion was invalid across separate module loads; behavioral parity passed
on rerun. No file changed. Evidence:
`context/PHASE315_CURATORIA_DIAGNOSTIC_PROJECTION_GATE.md`.

## Next concrete action

Review the next exact consumer-backed curatoria family,
`/home/mak/flujo/cultura/mak_curatoria/triangular.py` versus
`/home/mak/curatoria/triangular.py`, including direct entrypoint, language
paths and write set. Keep the same one-family boundary; do not touch data,
providers, services, Git or WIN.

Last verified: 2026-08-15 America/Santiago — Phase 315 curatoria diagnostic
projection gate passed; no persistent process.

## Phase 316 — latest authoritative update

The exact `mak_curatoria/triangular.py` pair was checked. Both paths are
byte-identical and their pure headliner helper matches, but `main()` is a
writer for `~/curatoria/triangulacion.jsonl` and has no active exact consumer;
the conductor uses `tools.triangular_fichas` instead. It remains protected
legacy/projection, not confirmed junk or a merge candidate. No file changed.
Evidence: `context/PHASE316_CURATORIA_TRIANGULAR_BOUNDARY_GATE.md`.

## Next concrete action

Select the next bounded Research or platform duplicate family from its actual
consumer and write set. Prefer a pure reader/projection and record whether it
is `CONSOLIDATE`, `PROTECT`, `QUARANTINE_CANDIDATE` or `UNRESOLVED`; do not
execute queue builders, output writers, live providers or services.

Last verified: 2026-08-15 America/Santiago — Phase 316 triangular boundary
gate passed; no persistent process.

## Phase 317 — latest authoritative update

The exact `corpus_a_micelio.py` family was revalidated. The canonical
`/home/mak/flujo/cultura/mak_research/corpus_a_micelio.py` and root
`/home/mak/research/corpus_a_micelio.py` are byte-identical and parse. The
conductor imports the canonical implementation; the root path is only named
by a paused historical cron projection. The pure `documento()` fixture passed
without invoking the corpus writer. The repository pytest attempt returned
rc=1 because the system Python has no `pytest`; no package was installed. No
source, data, cron, service or process changed. Evidence:
`context/PHASE317_CORPUS_PROJECTION_GATE.md`.

Disposition: `PROTECT_CONSUMER_BACKED_WRITER_PROJECTION`; do not merge or
delete either copy until launcher ownership, corpus snapshot and rollback are
explicitly validated.

## Next concrete action

Select the next bounded Research or platform duplicate family with a real
consumer, preferring a pure reader or compatibility projection. Record its
language/platform contract, write set and disposition before any edit. The
pytest environment gap remains open but is not a reason to install packages;
use direct static/fixture checks where safe. Do not execute corpus writers,
queue builders, providers or services, and do not modify WIN or Git.

Last verified: 2026-08-15 America/Santiago — Phase 317 corpus projection gate
passed; cron_active=0 and no persistent process observed.

## Phase 318 — latest authoritative update

The platform `copilot.py` family was validated as a pure, consumer-backed
contract. `/home/mak/flujo/cultura/mak_plataforma/copilot.py` and
`/home/mak/plataforma/copilot.py` are byte-identical, parse successfully and
are imported by the corresponding hub implementations. Feedback deduplication
and indexing fixtures passed with no provider calls, writes or service startup.
No source or data changed. Evidence:
`context/PHASE318_COPILOT_CONTRACT_GATE.md`.

Disposition: `PROTECT_EXACT_CONSUMER_BACKED_PROJECTION`; preserve the pair and
defer any import-root consolidation until both launchers have a focused test.

## Next concrete action

Continue the candidate manifest with one bounded consumer-backed Research or
platform family, preferring a pure reader/compatibility projection. Validate
language/platform contract, write set and owner first. The pytest environment
gap stays documented; do not install packages. Do not execute writers,
providers, queue builders or services, and do not modify WIN or Git.

Post-validation: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/home/mak/flujo/src:/home/mak/flujo python3 -m flujo health` returned rc=0; jobs, inbox, projects, scripts, tools and docs are OK. The two phase reports and this handoff exist. `cron_active=0`; no matching persistent process was observed.

Last verified: 2026-08-15 America/Santiago — Phase 318 copilot contract gate
and post-validation health check passed; no persistent process observed.

## Phase 319 — latest authoritative update

The existing objective, folder and branch evidence was consolidated into a
single current matrix without changing runtime files. It records the 13
objectives, canonical owners, verified/partial states, remaining gates, target
folder architecture, tool-fusion rules and invariants. Evidence:
`context/PHASE319_ARCHITECTURE_CONSOLIDATED_MATRIX.md` and `.csv`.

This is an active baseline, not a completion claim: field-data authority,
live RD mutators, optional providers, residual operation coverage, confirmed
cleanup candidates and Git operations remain gated. WIN remains read-only;
`rd.db` and `rd_datos.db` remain separate; no process or cron was started.

## Next concrete action

Use the consolidated matrix to execute the next bounded pure consumer-backed
Research/platform gate, then refresh the objective audit. Prefer one named
reader or compatibility projection, record its Spanish/English and
Windows/Linux contract, and do not execute writers, providers, queue builders
or services. No Git/WIN mutation or package installation.

Last verified: 2026-08-15 America/Santiago — Phase 319 matrix created and
validated as non-runtime documentation; no persistent process observed.

## Phase 320 — latest authoritative update

The four-path `fallback_util.py` family was validated as a true equivalent
pure utility: Research and Codex consumers use the same error classification,
failure aggregation, provider scoring and chain ordering contracts. All four
files are 6,100-byte AST-valid copies with SHA-256
`011560a85400dc82738cc4b595c4c8ddde6777433ee0f8aebe307a10ca290aba`; pure
fixtures passed without network or writes. Evidence:
`context/PHASE320_FALLBACK_CONSOLIDATION_GATE.md`.

Disposition: `CONSOLIDATE_SEMANTIC_OWNER_KEEP_FLAT_PROJECTIONS`. The family is
logically fused, but its root copies remain required projections until an
explicit package/import migration proves both flat launchers and the drift
ratchet. No file changed.

## Next concrete action

Continue the consolidated matrix with the next open functional slice rather
than repeating exact-copy checks: audit a bounded non-serve FLUJO command or
dependency contract with a read-only/fixture path, then refresh the objective
matrix. Keep live RD field ingest/mutators, providers, workers, services,
package installation, Git and WIN operations gated.

Last verified: 2026-08-15 America/Santiago — Phase 320 fallback utility gate
passed; no persistent process observed.

## Phase 321 — latest authoritative update

The deferred read-only FLUJO surface was executed with the existing virtual
environment. Help contracts passed; `knowledge list`, `job list`, `job next`,
RD productora/lookup/reactivo readers, `knowledge show` and `datadrop list`
returned expected data with rc=0. Invalid command-shape probes returned rc=2
and were corrected; they caused no mutation. No database, source, output,
service or process changed. Evidence:
`context/PHASE321_NONSERVE_READONLY_CONSUMER_GATE.md`.

Disposition: `VERIFIED_READ_ONLY_CONSUMER_SURFACE`. Writer commands remain
separate gates and are not implied complete by this result.

## Next concrete action

Continue the open functional audit with one bounded local slice that does not
start a service or provider: map the remaining writer commands and dependency
contracts, starting with `rd-db build`/`rd-datos ingest` only through static
write-set and fixture inspection, not execution. Keep live field ingest,
mutating routes, workers, providers, package installation, Git and WIN gated.

Last verified: 2026-08-15 America/Santiago — Phase 321 non-serve read-only
consumer gate passed; no persistent process observed.

## Phase 322 — latest authoritative update

The remaining RD writer contracts were statically inspected and executed only
against temporary paths. `build_rd_db(temp/rd.db)` rebuilt 20 tables and 7,587
rows with SQLite integrity `ok`. `ingest_csv()` processed a synthetic fixture
as expected: 1 valid insertion, 1 malformed row and 1 PII rejection. SHA,
size and mtime tuples for canonical `rd.db` and `rd_datos.db` were unchanged.
Evidence: `context/PHASE322_RD_TEMPORARY_WRITESET_GATE.md`.

Disposition: `VERIFIED_TEMPORARY_WRITER_CONTRACT; LIVE_AUTHORITY_PENDING`.
The implementations are functional within their contracts, but this does not
authorize real field ingest, publication or a destructive catalog rebuild.

## Next concrete action

Continue the functional audit with the next non-mutating RD/FLUJO slice and
refresh the objective matrix. Use the temporary-writer result to close only
the implementation gate; keep real field data, live mutating routes, provider
calls, workers, services, package installation, Git and WIN operations gated.

Last verified: 2026-08-15 America/Santiago — Phase 322 temporary RD writer
gate passed; canonical databases unchanged and no persistent process observed.

## Phase 323 — latest authoritative update

The RD field report/read layer was validated on an isolated temporary store.
`informe_trimestral()` preserved the mandatory presumptive and
`DEMO/FICTICIOS` disclaimers and generated the expected Q3 aggregation.
`resumen_json()` returned the expected totals/rate without changing the DB,
and a missing-path summary returned unavailable without creating a file.
Evidence: `context/PHASE323_RD_REPORT_READ_GATE.md`.

Disposition: `VERIFIED_READ_REPORT_CONTRACT; REAL_DATA_AUTHORITY_PENDING`.
The empty real field store remains separate and untouched.

## Next concrete action

Refresh the objective matrix with Phases 321–323, then continue one bounded
non-mutating route/dependency slice. Keep live field ingest, mutating RD
routes, providers, workers, services, package installation, Git and WIN
operations gated.

Last verified: 2026-08-15 America/Santiago — Phase 323 RD report/read gate
passed; no persistent process observed.

## Phase 324 — latest authoritative update

The objective matrix was refreshed after the temporary RD builder, privacy
ingest, report and GET-summary gates. RD implementation contracts are now
verified locally while real field authority and live mutators remain open;
`rd.db` and `rd_datos.db` retain separate lifecycles. The updated 13-objective
matrix is in `context/PHASE324_OBJECTIVE_MATRIX_REFRESH.md`.

The next bottleneck is no longer a missing RD implementation: it is the
remaining dependency/consumer audit and the externally gated operations.

## Next concrete action

Select the next unresolved dependency contract for an active consumer (not a
provider or service), validate it with static/import/fixture evidence, and
record whether it is `CONSOLIDATE`, `PROTECT` or `UNRESOLVED`. Then refresh
the dependency matrix. Do not install packages, run providers, start workers,
call live mutators, alter Git or modify WIN.

Last verified: 2026-08-15 America/Santiago — Phase 324 objective refresh
passed; no persistent process observed.

## Phase 325 — latest authoritative update

The base dependency slice for `flujo.cli`, RD database/data/report, privacy
and hub passed in the existing `/home/mak/venvs/flujo` environment. All six
imports returned rc=0 and `pip check` returned rc=0 with no broken
requirements. Observed versions satisfy the base `pyproject.toml` lower
bounds; optional/provider/Windows-global environments remain separate.
Evidence: `context/PHASE325_BASE_RD_DEPENDENCY_GATE.md`.

Disposition: `VERIFIED_BASE_SLICE_NO_DEPENDENCY_EDIT`; no package was installed
or changed.

## Next concrete action

Audit the next named optional dependency slice by consumer, starting with the
render/plano path or the research provider boundary, using import/static
checks only. Do not install packages, call providers, start services, execute
live mutators, alter Git or modify WIN.

Last verified: 2026-08-15 America/Santiago — Phase 325 base dependency gate
passed; no persistent process observed.

## Phase 326 — latest authoritative update

The optional laser dependency slice was audited. The pure local measurement
path parsed `/home/mak/trazos/2ac2c3508c8b.svg`; it measured 1,069 points and
158 subtraces against an 800-point budget and therefore returned rc=1 with a
quality warning. `flujo laser estado` also returned the expected rc=1 because
vpype/hatched/flow are not installed. No package or asset was changed.
Evidence: `context/PHASE326_LASER_OPTIONAL_DEPENDENCY_GATE.md`.

Disposition: `UNRESOLVED_OPTIONAL_DEPENDENCY; PURE_MEASUREMENT_AVAILABLE`.
The corpus is preserved; no generation dependency is promoted without an
explicit bounded decision.

## Next concrete action

Continue the optional-slice audit with the next actual consumer, likely the
render/plano image path that uses the already-installed Pillow rather than
the missing laser toolchain. Validate a pure fixture and record whether any
optional dependency is genuinely required. Do not install packages, call
providers, start services, mutate live data, alter Git or modify WIN.

Last verified: 2026-08-15 America/Santiago — Phase 326 laser dependency gate
passed with the optional chain explicitly unresolved; no persistent process
observed.

## Phase 327 — latest authoritative update

The installed Pillow/plano slice passed in-memory foreground validation:
PNG-to-SVG symbol tracing, event validation, SVG layout and rider generation
all succeeded. The corrected fixture produced 189-character symbol SVG,
8,695-character plano SVG and 655-character rider, with `FILES_WRITTEN=0`.
The initial missing-name fixture failed as designed and was corrected without
source changes. Evidence: `context/PHASE327_PIL_PLANO_CONSUMER_GATE.md`.

Disposition: `VERIFIED_INSTALLED_DEPENDENCY_SLICE`; no package or runtime
output was changed. Laser's separate vpype dependency remains unresolved.

## Next concrete action

Refresh the dependency/objective matrix with Phases 325–327, then select the
next active consumer outside the already-verified RD/plano core. Prefer a
pure local Research or FLUJO slice; keep provider, worker, service, live
mutator, package installation, Git and WIN actions gated.

Last verified: 2026-08-15 America/Santiago — Phase 327 Pillow/plano gate
passed; no persistent process observed.

## Phase 328 — latest authoritative update

The bilingual Research source gate was validated as a real RD dependency.
Spanish and English harm-reduction topics classified consistently; secondary
URLs were marked `SIN FUENTE PRIMARIA`, and a Passline event URL was accepted
as primary. The RD database consumer preserved the primary-source verdict in
both cases. No network or file write occurred. Evidence:
`context/PHASE328_SOURCE_GATE_BILINGUAL_CONSUMER.md`.

Disposition: `VERIFIED_CONSUMER_DEPENDENCY_BILINGUAL`.

## Next concrete action

Refresh the dependency/objective matrix with Phases 325–328, then continue to
the next unresolved active consumer or residual local-risk group. Prefer pure
static/import/fixture validation and stop repeating closed families. Do not
install packages, call providers, start services, execute live mutators,
alter Git or modify WIN.

Last verified: 2026-08-15 America/Santiago — Phase 328 bilingual source-gate
consumer passed; no persistent process observed.

## Phase 329 — latest authoritative update

The dependency matrix was refreshed with the base, RD temporary, Pillow/plano,
laser, source-gate, provider and desktop results. The active Linux baseline is
verified with no dependency edit; only laser generation and external/provider
or Windows desktop surfaces remain explicitly optional/gated. Evidence:
`context/PHASE329_DEPENDENCY_MATRIX_REFRESH.md`.

## Next concrete action

Run one bounded local health/diagnostic check for the remaining MAK surface,
then select the next residual consumer-risk group. Do not install optional
packages, call providers, start services, execute live mutators, alter Git or
modify WIN.

Last verified: 2026-08-15 America/Santiago — Phase 329 dependency matrix
refreshed; no persistent process observed.

## Phase 330 — latest authoritative update

The read-only `flujo doctor` gate returned rc=0. Python, workspace, jobs,
inbox, datadrops, index state, airdrop state and local port availability were
OK; only an existing local-working-tree warning was reported. A physical
recheck found `cron_active=0` and no matching persistent process. Evidence:
`context/PHASE330_LOCAL_DOCTOR_GATE.md`.

Disposition: `LOCAL_HOST_HEALTH_VERIFIED`; no Git mutation was performed.

## Next concrete action

Select the next residual local-risk consumer group from the existing Phase 268
inventory, avoiding all already-closed families. Use static/import/fixture
validation only and update the objective matrix afterward. Keep providers,
workers, services, live mutators, package installation, Git and WIN gated.

Last verified: 2026-08-15 America/Santiago — Phase 330 doctor gate passed;
no persistent process observed.

## Phase 331 — latest authoritative update

The two Blender installations were checked without full-tree hashing or
rendering. The active `/home/mak/blender/blender` is 4.5.4 LTS and has real
consumer references. The older `/home/mak/blender-4.5.3-viejo/blender` is a
distinct 4.5.3 LTS binary with no bounded active reference; both version probes
returned rc=0. It is not confirmed junk, so neither tree was moved or deleted.
Evidence: `context/PHASE331_BLENDER_RUNTIME_PROVENANCE_GATE.md`.

Disposition: `PROTECT_CURRENT_RUNTIME; OLD_EXTERNAL_RUNTIME_REVIEW`.

## Next concrete action

Refresh the objective/architecture matrix with the latest dependency,
consumer and Blender evidence, then select the next unresolved path-specific
candidate. Do not move the old runtime without project provenance and
rollback; keep providers, workers, services, live mutators, package
installation, Git and WIN gated.

Last verified: 2026-08-15 America/Santiago — Phase 331 Blender provenance
gate passed; no persistent process observed.

## Phase 332 — latest authoritative update

The bounded Blender asset scan found 110 `.blend`/`.blend1` files under RD,
zero under FLUJO, no old-runtime code/config references, and four active
references to the current 4.5.4 runtime. This strengthens preservation of the
old 4.5.3 runtime pending project-specific provenance; it is not confirmed
basura. Evidence: `context/PHASE332_BLENDER_ASSET_PROVENANCE_REFRESH.md`.

## Next concrete action

Refresh the architecture/objective matrix with Phases 329–332, then choose the
next non-external unresolved consumer. Do not open/render the full Blender
corpus, move the old runtime, install packages, call providers, start
services, mutate live data, alter Git or modify WIN.

Last verified: 2026-08-15 America/Santiago — Phase 332 bounded Blender asset
provenance scan passed; no persistent process observed.

## Phase 333 — latest authoritative update

The architecture/objective matrix was refreshed with Phases 329–332. The
active Linux/RD core is increasingly verified, while live authority, optional
dependencies, external providers/runtimes, final cleanup candidates and Git
operations remain explicitly open. Evidence:
`context/PHASE333_ARCHITECTURE_OBJECTIVE_REFRESH.md`.

## Next concrete action

Select one remaining active non-external consumer or pure residual test family
and validate it in foreground. Preserve the layered folder architecture,
WIN, databases and external Blender assets; do not install packages, call
providers, start services, move runtimes, mutate live data, alter Git or
modify WIN.

Last verified: 2026-08-15 America/Santiago — Phase 333 architecture/objective
refresh passed; no persistent process observed.

## Phase 334 — latest authoritative update

Two residual local-risk families were exercised directly because the existing
venv lacks `pytest`: hub event integrity and Research-to-Codex icon queueing.
Temporary fixtures passed malformed-JSON handling, job union/orphan marking,
annex queueing and best-effort external failure. No external call or
persistent write occurred. Evidence:
`context/PHASE334_HUB_ICON_RESIDUAL_GATE.md`.

Disposition: `VERIFIED_DIRECT_FIXTURE; TEST_RUNNER_MISSING`.

## Next concrete action

Refresh residual coverage/objective status with Phase 334, then select another
provably temporary local-risk family if one remains. Keep the pytest gap
documented; do not install packages, call providers, start services, run live
mutators, move external runtimes, alter Git or modify WIN.

Last verified: 2026-08-15 America/Santiago — Phase 334 direct residual gate
passed; no persistent process observed.

## Phase 335 — latest authoritative update

The delegation client residual slice was run with the existing unittest
runner: 15 tests passed in 0.012 seconds. Research/Codex payloads, validation,
iteration bounds, mocked HTTP success and timeout/error handling all passed;
no real network or hub call occurred. Evidence:
`context/PHASE335_DELEGATION_CLIENT_UNIT_GATE.md`.

Disposition: `VERIFIED_MOCKED_UNIT_SURFACE`.

## Next concrete action

Refresh residual coverage/objective status with Phase 335, then choose the
next local unit/fixture family that has no provider, worker or live-mutation
boundary. Keep the missing pytest runner documented and do not install it;
preserve all Git/WIN/database/runtime restrictions.

Last verified: 2026-08-15 America/Santiago — Phase 335 delegation client gate
passed; no persistent process observed.

## Phase 336 — latest authoritative update

The backlog utility's local contract was exercised directly: normalization,
accent folding, deterministic dedup hashes, gap parsing, provenance,
corrupt-JSONL tolerance and temporary append/pop/mark operations all passed.
Writes stayed in a temporary directory and no provider/worker ran. Evidence:
`context/PHASE336_BACKLOG_LOCAL_CONTRACT_GATE.md`.

Disposition: `VERIFIED_DIRECT_FIXTURE; BACKLOG_WRITERS_TEMPORARY_ONLY`.

## Next concrete action

Refresh residual coverage/objective status with Phases 335–336, then select
another local consumer slice or finish the remaining architecture ledger. Keep
live backlog/queue execution, providers, services, mutators, package
installation, Git and WIN gated.

Last verified: 2026-08-15 America/Santiago — Phase 336 backlog gate passed;
no persistent process observed.

## Phase 337 — latest authoritative update

Residual coverage now includes the direct hub/icon fixtures, 15 delegation
client unittest cases and the backlog direct contract, in addition to the 188
previous bounded passes. The measured evidence is local/temporary only; live
providers, workers, mutators, optional laser generation, old-runtime cleanup,
XIO/n8n and Git remain open boundaries. Evidence:
`context/PHASE337_RESIDUAL_COVERAGE_REFRESH.md`.

## Next concrete action

Continue with a path-specific provenance/consumer ledger for one remaining
candidate, or a pure local fixture if it has a provably temporary write set.
Do not widen execution authority, install pytest/packages, start services,
call providers, mutate live data, alter Git or modify WIN.

Last verified: 2026-08-15 America/Santiago — Phase 337 residual coverage
refresh passed; no persistent process observed.

## Phase 338 — latest authoritative update

The two root installers were statically classified. Both pass `bash -n`, have
no active code consumer in the bounded scan, and are operationally dangerous:
`install_mak.sh` creates cron/systemd and modifies projections; `instalar.sh`
installs/enables Docker and starts Open WebUI. Neither was executed or moved.
Evidence: `context/PHASE338_ROOT_INSTALLER_CANDIDATE_GATE.md`.

Disposition: `QUARANTINE_CANDIDATE_PRESERVE_PROVENANCE`; a later reversible
quarantine requires the exact ledger and inverse move, not deletion.

## Next concrete action

Add these candidates to the cleanup/architecture ledger and inspect the next
root standalone tool for an active consumer. Keep the installers, WIN,
databases and external runtimes untouched until the reversible cleanup set is
explicitly assembled; do not run services, providers, packages or Git.

Last verified: 2026-08-15 America/Santiago — Phase 338 installer candidate
gate passed; no persistent process observed.

## Phase 339 — latest authoritative update

The cleanup ledger now records the two root installer candidates with exact
hashes, consumer results, dispositions and inverse actions, alongside the old
Blender runtime and the existing Phase 270 quarantine. It is ledger-only:
nothing moved or deleted. Evidence:
`context/PHASE339_CLEANUP_CANDIDATE_LEDGER.md` and `.csv`.

## Next concrete action

Inspect one next root standalone tool for active consumers and add it to the
same ledger if warranted. Do not move candidates until the cleanup slice has a
complete reversible set and post-move validation plan; do not run installers,
providers, services, packages, Git or WIN operations.

Last verified: 2026-08-15 America/Santiago — Phase 339 cleanup ledger refreshed;
no persistent process observed.

## Phase 340 — latest authoritative update

The two ledgered root installers were moved reversibly into
`context/quarantine/phase339_root_installers/`. Bash syntax, mode, size and
SHA-256 remained identical; original paths are absent and no installer ran.
Post-check found `cron_active=0` and no running Docker containers. A
pre-existing root `dockerd` (PID 3169, started 2026-08-13) remains untouched;
stopped `searxng` and `open-webui` containers are preserved. Evidence:
`context/PHASE340_ROOT_INSTALLER_QUARANTINE_VALIDATION.md`.

Disposition: `QUARANTINED_REVERSIBLY; EXTERNAL_DOCKER_STATE_PRESERVED`.

## Next concrete action

Refresh the cleanup ledger with the actual quarantine result, then inspect the
next root standalone candidate for consumers. Keep Docker state, databases,
WIN, external runtimes and remaining candidates untouched unless a separate
reversible action is justified; do not run providers, services, installers or
Git.

Last verified: 2026-08-15 America/Santiago — Phase 340 reversible quarantine
passed; no running container and no MAK persistent service observed.

## Phase 341 — latest authoritative update

The cleanup ledger now reflects physical state: C339-01 and C339-02 are
reversibly quarantined with hashes/modes preserved; C339-03 Blender remains
protected pending provenance; C339-04 remains in its prior quarantine. No
evidence or protected data was deleted. External Docker state was documented
but not modified. Evidence: `context/PHASE341_CLEANUP_LEDGER_RESULT.md`.

## Next concrete action

Select and inspect the next root standalone candidate by consumer, beginning
with the optional provider/tool files only through static provenance checks.
Do not execute them, install dependencies, stop Docker, alter databases/WIN,
start services or perform Git operations.

Last verified: 2026-08-15 America/Santiago — Phase 341 cleanup ledger result
matches physical state; no running container or MAK service observed.

## Phase 342 — latest authoritative update

The remaining root standalone surface was classified. `mak_sync_safe.py` has
an external deploy owner; WatsonX/Qwen tools are optional provider/local
launchers without active consumers; the three `diag-*.sh` files are host
diagnostics. AST/bash syntax passed for all six and no tool executed. Evidence:
`context/PHASE342_ROOT_STANDALONE_SURFACE_GATE.md`.

Disposition: preserve as classified external evidence; no additional cleanup
candidate was confirmed.

## Next concrete action

Refresh the architecture/cleanup matrix with Phases 340–342, then select the
next unresolved consumer or dependency slice inside the canonical FLUJO/RD
surface. Keep external tools, Docker state, databases, WIN and Git untouched;
do not execute providers, installers or services.

Last verified: 2026-08-15 America/Santiago — Phase 342 root standalone gate
passed; no running container or MAK service observed.

## Phase 343 — latest authoritative update

The canonical EVENTO automation/issue bridge passed direct temporary fixtures:
Instagram URL parsing, simulated flyer/palette flow, simulated render,
path-sanitization and atomic-state rollback all passed. No email, Instagram,
GitHub, Blender, network or cron call occurred. Optional `parth_dl` and
`curl_cffi` modules remain absent but were not needed for the mocked gate.
Evidence: `context/PHASE343_EVENTO_ISSUE_BRIDGE_GATE.md`.

Disposition: `VERIFIED_LOCAL_AUTOMATION_CONTRACT; EXTERNAL_EDGE_GATED`.

## Next concrete action

Refresh the objective/automation matrix with Phase 343, then continue with the
next canonical consumer/dependency slice. Preserve the user-confirmed bridge
without re-enabling cron; do not call external services, install packages,
start workers/services, mutate live data, alter Git or modify WIN.

Last verified: 2026-08-15 America/Santiago — Phase 343 EVENTO/issue bridge
gate passed; no running container or MAK service observed.

## Phase 344 — latest authoritative update

The EVENTO dependency slice was separated explicitly: stdlib + Pillow support
the validated local path; `parth_dl` and `curl_cffi` are missing optional
external edges; Blender/Photoshop are render handoffs, not base Linux
requirements. AST/import discovery passed and no package was installed.
Evidence: `context/PHASE344_EVENTO_DEPENDENCY_SLICE.md`.

Disposition: `BASE_EVENTO_PATH_VERIFIED; OPTIONAL_EXTERNAL_EDGES_GATED`.

## Next concrete action

Refresh the objective/dependency matrix with Phase 344, then select the next
canonical consumer outside the already-verified EVENTO/RD/plano slices. Keep
optional acquisition, providers, workers, services, live mutators, Docker,
Git and WIN untouched.

Last verified: 2026-08-15 America/Santiago — Phase 344 EVENTO dependency slice
passed; no running container or MAK service observed.

## Phase 345 — latest authoritative update

The 13-objective matrix was refreshed after the EVENTO dependency slice. The
local automation path is verified with its optional external edges separated;
RD/catalog/CLI/plano/dependency and cleanup statuses remain explicit rather
than silently promoted. Evidence:
`context/PHASE345_OBJECTIVE_DEPENDENCY_REFRESH.md`.

## Next concrete action

Select the next canonical FLUJO consumer outside the verified RD/plano/EVENTO
families and run a bounded static/import/fixture gate. Keep live mutators,
providers, workers, services, Docker state, Git and WIN untouched.

Last verified: 2026-08-15 America/Santiago — Phase 345 objective/dependency
refresh passed; no running container or MAK service observed.

## Phase 346 — latest authoritative update

The `flujo.knowledge` productora/venue/asset consumer passed temporary YAML
fixtures for Spanish/English event classification, deliverable derivation and
dossier indexing. The real knowledge store and assets remained unchanged. A
first expectation about bare “Instagram” was corrected to the actual URL
contract and then passed. Evidence:
`context/PHASE346_KNOWLEDGE_ASSET_CONSUMER_GATE.md`.

Disposition: `VERIFIED_KNOWLEDGE_ASSET_CONSUMER; TEMP_ONLY_WRITES`.

## Next concrete action

Refresh the objective/asset matrix with Phases 343–346, then select the next
canonical consumer outside the verified RD/plano/EVENTO/knowledge slices.
Keep external acquisition, providers, workers, services, Docker, live
mutators, Git and WIN untouched.

Last verified: 2026-08-15 America/Santiago — Phase 346 knowledge/asset gate
passed; no running container or MAK service observed.

## Phase 347 — latest authoritative update

The canonical asset indexer exposed and received a minimal bug fix: filenames
using underscores such as `creatina_final.svg` now group with `creatina final`
and `creatina copia` before duplicate/version queries. Exact hash detection,
cleanup classification, search grouping and py_compile passed on a temporary
fixture; the real index and assets were untouched. Evidence:
`context/PHASE347_INDEXER_BASEKEY_FIX.md`.

Changed source: `/home/mak/flujo/src/flujo/index/indexer.py`.

## Next concrete action

Refresh the asset/duplicate matrix with Phase 347, then inspect the next
consumer that depends on index grouping. Do not rebuild the real index or move
assets until the corrected grouping has a path-level consumer review; keep
providers, services, Docker, Git and WIN untouched.

Last verified: 2026-08-15 America/Santiago — Phase 347 indexer fix passed;
no running container or MAK service observed.

## Phase 348 — latest authoritative update

The read-only consumer in `flujo.index.db` passed a temporary SQLite gate after
the Phase 347 grouping correction. Missing-index lookup did not create a file;
status listing and duplicate-shortcode grouping returned the expected results.
Only the temporary database was written and the canonical index remained
unchanged. Evidence: `context/PHASE348_INDEX_DB_CONSUMER_GATE.md`.

Disposition: `VERIFIED_READONLY_INDEX_CONSUMER; TEMP_ONLY_WRITES`.

## Next concrete action

Refresh the asset/duplicate matrix with Phases 347–348, then inspect the next
canonical consumer outside the verified index/knowledge/EVENTO/RD slices. Keep
real index rebuilds, asset moves, external acquisition, providers, services,
Docker, Git and WIN untouched.

Last verified: 2026-08-15 America/Santiago — Phase 348 index database consumer
gate passed; no running container or MAK service observed.

## Phase 349 — latest authoritative update

The asset/duplicate matrix was refreshed with Phases 347–348:
`context/PHASE349_ASSET_DUPLICATE_MATRIX_REFRESH.md/.csv`. The corrected
indexer and its read-only SQLite consumer now form one verified classification
slice. The real index, assets, databases, WIN evidence and Git state remain
untouched.

## Next concrete action

Inspect the next canonical path-level asset validator outside the index
database, starting with static/import checks and temporary fixtures. Do not
rewrite, move or delete real assets; preserve providers, services, Docker, Git
and WIN.

Last verified: 2026-08-15 America/Santiago — Phase 349 asset/duplicate matrix
refresh recorded; no running MAK service or container observed.

## Phase 350 — latest authoritative update

The canonical SVG validator passed static compilation, temporary valid/error
fixtures, batch validation and a read-only check of `RIDER-01.svg`. It accepts
viewBox-only dimensions and catches placeholders and wrong sizes. No real
asset, index, database, service, provider, Git state or WIN evidence changed.
Evidence: `context/PHASE350_SVG_VALIDATOR_CONSUMER_GATE.md`.

Disposition: `VERIFIED_ASSET_VALIDATOR; TEMP_FIXTURES_PLUS_READONLY_CANONICAL_CHECK`.

## Next concrete action

Inspect the next canonical asset/export consumer with static/import checks and
temporary fixtures, prioritizing a read-only path outside the verified
index/validator slice. Preserve real assets, external renderers, providers,
services, Docker, Git and WIN.

Last verified: 2026-08-15 America/Santiago — Phase 350 SVG validator gate
passed; no running MAK service or container observed.

## Phase 351 — latest authoritative update

The delivery ZIP exporter passed a temporary project gate: manifest/source
collection, generated Photoshop/Illustrator/Blender handoff scripts, email
draft and archive membership all passed; scripts were included before the ZIP
was created. No real project or asset tree changed. Evidence:
`context/PHASE351_ZIP_EXPORT_CONSUMER_GATE.md`.

Disposition: `VERIFIED_TEMP_EXPORT_CONSUMER; EXTERNAL_EDITOR_HANDOFF`.

## Next concrete action

Inspect the next canonical export/intake boundary with static checks and a
temporary fixture, separating safe local parsing from external editor/provider
edges. Do not run real exports, mutate live projects, start services, alter
Docker/Git, or touch WIN.

Last verified: 2026-08-15 America/Santiago — Phase 351 ZIP export gate passed;
no running MAK service or container observed.

## Phase 352 — latest authoritative update

The local intake boundary passed safe ZIP extraction, traversal rejection,
disabled-email behavior and HMAC signature refusal in temporary fixtures.
No IMAP, provider, subprocess, live airdrop, real file or database was
accessed. Evidence: `context/PHASE352_INTAKE_BOUNDARY_GATE.md`.

Disposition: `VERIFIED_LOCAL_INTAKE_GUARDS; EXTERNAL_EMAIL_AIRDROP_DISABLED`.

## Next concrete action

Inspect the next canonical parser/consumer with static checks and temporary
fixtures, keeping external email, provider calls, live mutators, services,
Docker, Git and WIN disabled and untouched.

Last verified: 2026-08-15 America/Santiago — Phase 352 intake boundary gate
passed; no running MAK service or container observed.

## Phase 353 — latest authoritative update

The pure intake parser passed Spanish/English fixtures, Instagram URL
normalization, section extraction, hub pedido shape and temporary file reading.
The mutating email-to-jobs pipeline was not run. Evidence:
`context/PHASE353_EMAIL_PARSER_GATE.md`.

Disposition: `VERIFIED_BILINGUAL_PARSER; MUTATING_PIPELINE_SEPARATED`.

## Next concrete action

Isolate JSON-schema intake validation from job/project creation using a
temporary or in-memory fixture. Preserve real jobs, projects, external email,
providers, services, Docker, Git and WIN.

Last verified: 2026-08-15 America/Santiago — Phase 353 bilingual parser gate
passed; no running MAK service or container observed.

## Phase 354 — latest authoritative update

The pure JSON intake schema boundary passed valid/invalid/additional-property
fixtures and temporary JSON reading. Job creation, brief writing and project
mutation were not called. Evidence:
`context/PHASE354_JSON_INTAKE_SCHEMA_GATE.md`.

Disposition: `VERIFIED_SCHEMA_GATE; JOB_CREATION_SEPARATED`.

## Next concrete action

Inspect job creation/lifecycle in a temporary repository or mocked path, then
validate prepare/status behavior without activating or touching real jobs.
Preserve real projects, external edges, services, Docker, Git and WIN.

Last verified: 2026-08-15 America/Santiago — Phase 354 JSON schema gate passed;
no running MAK service or container observed.

## Phase 355 — latest authoritative update

The job creation/prepare/status lifecycle passed in an isolated temporary
repository. The incomplete fixture correctly remained `pendiente_datos`, and
the real `/home/mak/flujo/jobs` entry set was unchanged. Activation was not
run. Evidence: `context/PHASE355_JOB_LIFECYCLE_TEMP_GATE.md`.

Disposition: `VERIFIED_JOB_PREPARE_STATUS; ACTIVATION_NOT_RUN`.

## Next concrete action

Inspect the activation boundary in a temporary project root, verifying brief
to project/config generation and rollback without activating any real job.
Keep external renderers, live projects, providers, services, Docker, Git and
WIN untouched.

Last verified: 2026-08-15 America/Santiago — Phase 355 temporary job lifecycle
gate passed; no running MAK service or container observed.

## Phase 356 — latest authoritative update

The brief-to-project activation boundary passed in a temporary repository:
project/config generation and the `en_diseno` state transition worked without
running a renderer or touching real jobs. Evidence:
`context/PHASE356_JOB_ACTIVATION_TEMP_GATE.md`.

Disposition: `VERIFIED_TEMP_JOB_ACTIVATION; RENDER_EXTERNALIZED`.

## Next concrete action

Inspect the local render/config validator boundary with a temporary project,
then consolidate the verified intake/export/job slices into the architecture
matrix. Do not render real assets, activate real jobs, start services, alter
Docker/Git or touch WIN.

Last verified: 2026-08-15 America/Santiago — Phase 356 temporary activation
gate passed; no running MAK service or container observed.

## Phase 357 — latest authoritative update

The render input boundary passed without rendering: the canonical format
catalog loaded 14 formats, suggestions/filter/lookup worked, and temporary
valid/error configs were classified correctly. Evidence:
`context/PHASE357_RENDER_CONFIG_CATALOG_GATE.md`.

Disposition: `VERIFIED_RENDER_INPUT_GATE; RENDER_ENGINE_NOT_RUN`.

## Next concrete action

Consolidate the verified intake/export/job/render slices into the architecture
and cleanup matrix, then select the next unresolved MAK consumer. Preserve
real assets/projects, external renderers, providers, services, Docker, Git
and WIN.

Last verified: 2026-08-15 America/Santiago — Phase 357 render input gate
passed; no running MAK service or container observed.

## Phase 358 — latest authoritative update

The intake → render vertical was consolidated in
`context/PHASE358_INTAKE_RENDER_ARCHITECTURE_REFRESH.md/.csv`. Phases 347–357
now have explicit local state, external boundaries and mutation scope. No
source merge or historical-artifact deletion was inferred from the matrix.

## Next concrete action

Select the next unresolved downstream local render/asset consumer from the
canonical tree, beginning with static/import checks and a temporary fixture.
Keep real rendering, live job activation, provider downloads, services,
Docker, Git, WIN and cleanup of protected/generated artifacts untouched.

Last verified: 2026-08-15 America/Santiago — Phase 358 architecture refresh
recorded; no running MAK service or container observed.

## Phase 359 — latest authoritative update

The downstream render rescale consumer passed pure and temporary-file gates:
DPI scaling preserved the input, proportion changes emitted the expected
warning, and explicit output preserved the source config. Evidence:
`context/PHASE359_RESCALE_CONSUMER_GATE.md`.

Disposition: `VERIFIED_RESCALE_CONSUMER; REAL_CONFIG_MUTATION_UNRUN`.

## Next concrete action

Refresh the 13-objective reconciliation with Phases 347–359 and identify the
next unresolved item that can be advanced locally. Keep real config mutation,
field ingest, live POSTs, external providers, services, Docker, Git and WIN
gated or untouched.

Last verified: 2026-08-15 America/Santiago — Phase 359 rescale consumer gate
passed; no running MAK service or container observed.

## Phase 360 — latest authoritative update

The 13-objective requirement audit was refreshed in
`context/PHASE360_OBJECTIVE_REQUIREMENT_AUDIT_REFRESH.md/.csv`. It preserves
the original scope and distinguishes verified local evidence from open
authority, external, physical-move and Git gates. No status was promoted by
absence of errors, and no source/data/WIN/Git mutation occurred.

## Next concrete action

Reconcile the physical folder/disposition ledger against current top-level MAK
roots and identify one additional reversible cleanup or ownership decision
with active-consumer proof. Do not delete protected evidence or touch WIN.

Last verified: 2026-08-15 America/Santiago — Phase 360 objective requirement
audit refreshed; no running MAK service or container observed.

## Phase 361 — latest authoritative update

The discarded n8n automation surface was separated from active credential
ownership. Six Research/platform consumers now default to the existing
`/home/mak/research/research.env`; the n8n directory and mode-600 environment
files remain protected and unchanged. Python/bash syntax, static reference
check and `systemd-analyze verify` all passed without starting a unit.
Evidence: `context/PHASE361_N8N_CREDENTIAL_OWNER_MIGRATION.md`.

Disposition: `N8N_TOOL_DISCARDED; CREDENTIAL_STORE_PROTECTED; RESEARCH_OWNER_ACTIVE`.

## Next concrete action

Refresh the physical architecture/objective matrix with Phase 361, then audit
the next active root for a similar owner/path conflict. Keep credential files,
real data, live providers, services, Docker, Git and WIN untouched.

Last verified: 2026-08-15 America/Santiago — Phase 361 n8n credential-owner
migration passed; no running MAK service or container observed.

## Phase 362 — latest authoritative update

The physical architecture/disposition map was refreshed in
`context/PHASE362_PHYSICAL_ARCHITECTURE_REFRESH.md/.csv`. It records
Research as credential owner, n8n as protected discarded evidence, XIO as
user-excluded, WIN as historical, `/home/mak/post` as absent, and the
disconnected OneDrive mount as uninspectable. No root was copied, deleted or
activated.

## Next concrete action

Use the refreshed owner map to audit one remaining active projection family
for duplicate ownership and consumer parity. Preserve protected data,
credentials, generated products, Docker, Git and WIN.

Last verified: 2026-08-15 America/Santiago — Phase 362 physical architecture
refresh recorded; no running MAK service or container observed.

## Phase 363 — latest authoritative update

The Research credential-owner change was reconciled across canonical and live
projection files. Five paired files now have exact local SHA-256 parity,
active `n8n-local` references are absent, and Python/bash/static/unit checks
pass. The remote SSH mirror checker was not used. Evidence:
`context/PHASE363_RESEARCH_PROJECTION_PARITY_GATE.md`.

Disposition: `RESEARCH_OWNER_PARITY_VERIFIED; N8N_FALLBACK_REMOVED`.

## Next concrete action

Refresh the architecture/objective matrix with Phases 361–363, then select the
next active projection family or unresolved local consumer. Preserve protected
credentials/data, generated products, Docker, Git and WIN.

Last verified: 2026-08-15 America/Santiago — Phase 363 Research projection
parity gate passed; no running MAK service or container observed.

## Phase 364 — latest authoritative update

The platform provider projection was reconciled with the Research credential
owner. Canonical/live `providers.py` content is identical, active
`n8n-local` references are absent across the platform/Research surface, and
syntax/static checks pass. No provider, service or credential was executed.
Evidence: `context/PHASE364_PLATFORM_PROVIDER_PARITY_GATE.md`.

Disposition: `PLATFORM_PROVIDER_OWNER_PARITY_VERIFIED; N8N_SURFACE_FULLY_DECOUPLED`.

## Next concrete action

Refresh the architecture/objective matrix with Phases 361–364, then audit the
next active projection family for exact owner/consumer parity. Preserve
protected credentials/data, generated products, Docker, Git and WIN.

Last verified: 2026-08-15 America/Santiago — Phase 364 platform provider parity
gate passed; no running MAK service or container observed.

## Phase 365 — latest authoritative update

The architecture/objective matrix was refreshed after the credential-owner
work in `context/PHASE365_ARCHITECTURE_OBJECTIVE_REFRESH.md/.csv`. It records
the verified Research/platform parity and the separate protected/excluded
n8n, XIO and WIN surfaces. The RD authority, live-mutator, optional-provider,
cleanup and Git gates remain explicitly open.

## Next concrete action

Select the next active projection family and run a bounded local parity and
consumer check, excluding data, caches, credentials, generated products and
historical evidence.

Last verified: 2026-08-15 America/Santiago — Phase 365 architecture/objective
refresh recorded; no running MAK service or container observed.

## Phase 366 — latest authoritative update

The declared Codex projection set passed local import, compilation and unit
verification. `agente_libre.py` is confirmed as an intentional compatibility
wrapper, while `interfaz_codex.py` is exact between canonical/live paths. No
server or job mutation ran. Evidence: `context/PHASE366_CODEX_PROJECTION_GATE.md`.

Disposition: `CODEX_OWNER_PROJECTION_VERIFIED; WRAPPER_INTENTIONAL`.

## Next concrete action

Audit the next declared active projection family with the same bounded
owner/consumer/parity method. Keep POST/job execution, providers, services,
Docker, Git, credentials, generated products and WIN untouched.

Last verified: 2026-08-15 America/Santiago — Phase 366 Codex projection gate
passed; no running MAK service or container observed.

## Phase 367 — latest authoritative update

The declared Curatoria projection set passed canonical and live-wrapper import,
Python compilation and shell syntax checks. Root Python files are intentional
wrappers and the guard shell file is exact. No perception, extraction, worker
or service executed. Evidence: `context/PHASE367_CURATORIA_PROJECTION_GATE.md`.

Disposition: `CURATORIA_OWNER_PROJECTION_VERIFIED; WRAPPERS_INTENTIONAL`.

## Next concrete action

Audit the remaining declared mirror family (`mak_vigia` or language) with the
same bounded owner/consumer/parity method. Keep workers, providers, services,
databases, Docker, Git, credentials, generated products and WIN untouched.

Last verified: 2026-08-15 America/Santiago — Phase 367 Curatoria projection
gate passed; no running MAK service or container observed.

## Phase 368 — latest authoritative update

The declared Vigia projection set passed exact local parity, Python/shell
checks and temporary HTML/JSON/feed/filter/hash/golden-rule fixtures. No URL,
watcher state, notification or cron ran. Evidence:
`context/PHASE368_VIGIA_PROJECTION_GATE.md`.

Disposition: `VIGIA_OWNER_PARITY_VERIFIED; NETWORK_STATE_GATED`.

## Next concrete action

Audit the remaining declared language projection with the same bounded
owner/consumer/parity method, then refresh the objective matrix. Keep network,
cron, workers, providers, databases, Docker, Git, credentials, generated
products and WIN untouched.

Last verified: 2026-08-15 America/Santiago — Phase 368 Vigia projection gate
passed; no running MAK service or container observed.

## Phase 369 — latest authoritative update

The declared language projection set passed exact local parity, imports,
Python/shell checks and bilingual signal fixtures. No document barrido,
lexicon rebuild or cron ran. Evidence:
`context/PHASE369_LANGUAGE_PROJECTION_GATE.md`.

Disposition: `LANGUAGE_OWNER_PARITY_VERIFIED; DOCUMENT_MUTATION_CRON_GATED`.

## Next concrete action

Refresh the 13-objective and projection matrix with Phases 363–369, then
return to the remaining material gates: RD field authority/live mutators,
optional providers, path-specific cleanup and Git proposal handoff. Preserve
data, credentials, generated products, Docker and WIN.

Last verified: 2026-08-15 America/Santiago — Phase 369 language projection
gate passed; no running MAK service or container observed.

## Phase 370 — latest authoritative update

The declared projection owner matrix was consolidated in
`context/PHASE370_PROJECTION_OWNER_MATRIX.md/.csv`. Research, Platform,
Codex, Curatoria, Vigia and Lenguaje now have explicit canonical/live owner
and consumer dispositions; XIO and n8n remain excluded/protected as directed.

## Next concrete action

Return to the remaining material gates from the 13-objective audit: first
review the preserved RD field candidate and its exact strict-ingest decision,
then continue with live-mutator authority, path-specific cleanup and the Git
branch proposal handoff. Do not invent records, enable providers, delete
protected evidence or mutate Git.

Last verified: 2026-08-15 America/Santiago — Phase 370 projection owner matrix
recorded; no running MAK service or container observed.

## Phase 371 — latest authoritative update

The preserved RD field candidate was re-audited read-only and a decision
packet was created at `context/PHASE371_RD_FIELD_REVIEW_PACKET.md`. It confirms
10/42 date candidates, 20 partial/ambiguous dates, 6 duplicate-sheet
candidates, 84 pending links and 357 missing-reagent observations. The
corrected aggregation exited 0; live `rd_datos.db` remained byte-stable.

Disposition: `REVIEW_PACKET_READY; LIVE_INGEST_BLOCKED_BY_DATA_QUALITY_AND_AUTHORITY`.

## Next concrete action

Keep the candidate and `rd_datos.db` untouched until the documented human
decisions arrive. In parallel, advance the next locally executable material
gate: read-only audit of the RD mutator rollback/entrypoint surface without
sending live POSTs.

Last verified: 2026-08-15 America/Santiago — Phase 371 RD field review packet
created; no running MAK service or container observed.

## Phase 372 — latest authoritative update

Removed 6,060 regenerable `*.pyc` files from explicit active MAK roots,
including environment caches because they were inside the selected roots; no
source, package metadata, data, credentials, generated product, WIN or Git
file was removed. The post-cleanup base `pip check` and `flujo health` both
returned 0, and active bytecode count is 0. Evidence:
`context/PHASE372_REGENERABLE_BYTECODE_CLEANUP.md`.

Disposition: `REGENERABLE_RESIDUE_REMOVED; SOURCES_AND_DATA_PRESERVED`.

## Next concrete action

Audit the next bounded RD mutator/rollback or cleanup candidate without live
POSTs, provider calls, service starts, database writes or Git/WIN mutation.

Last verified: 2026-08-15 America/Santiago — Phase 372 bytecode cleanup and
post-cleanup health gate passed; no running MAK service or container observed.

## Phase 373 — latest authoritative update

The current RD hub source was rechecked statically: all 16 POST paths and five
mutator helpers are present; `rd_datos.db` passes integrity, remains empty and
retains its known SHA-256. No HTTP request or write ran. Evidence:
`context/PHASE373_RD_MUTATOR_STATIC_CONTINUITY_GATE.md`.

Disposition: `RD_MUTATOR_ROUTE_CONTINUITY_VERIFIED; LIVE_WRITE_AUTHORITY_OPEN`.

## Next concrete action

Refresh the objective/architecture matrix with Phases 371–373, then continue
with path-specific cleanup or a read-only operational audit. Keep live POSTs,
field ingest, providers, services, Docker, Git and WIN untouched.

Last verified: 2026-08-15 America/Santiago — Phase 373 RD mutator continuity
gate passed; no running MAK service or container observed.

## Phase 374 — latest authoritative update

The objective matrix was refreshed after the RD review packet, mutator
continuity gate and regenerable cleanup:
`context/PHASE374_OBJECTIVE_MATRIX_AFTER_371_373.md/.csv`. It keeps field
authority, live writes, path-specific cleanup and Git as open gates while
promoting only evidence-backed local results.

## Next concrete action

Continue with a bounded read-only operational audit of remaining non-protected
cleanup candidates, then prepare the final handoff/branch proposal without
mutating Git or protected data.

Last verified: 2026-08-15 America/Santiago — Phase 374 objective matrix
refresh recorded; no running MAK service or container observed.

## Phase 375 — latest authoritative update

The Git branch system was refreshed as a proposal in
`context/PHASE375_GIT_BRANCH_SYSTEM_REFRESH.md/.csv`. It separates RD data,
RD runtime, EVENTO bridge, RD assets, MAK ownership, tool consolidation,
confirmed cleanup and final audit into disjoint write sets. No Git operation
was performed.

## Next concrete action

Keep the objective active at the remaining authority boundaries: RD field
review/live mutator, optional provider decisions, path-specific cleanup and
final audit. If Git work is explicitly authorized later, review the current
worktree snapshot before creating the ownership branch.

Last verified: 2026-08-15 America/Santiago — Phase 375 Git branch proposal
refresh recorded; no running MAK service or container observed.

## Phase 376 — latest authoritative update

The local MAK audit passed health, doctor, base dependency, SQLite integrity,
cron safety and 371/371 active-source AST checks. A broad 484-file AST scan
returned exit 1 only for seven malformed generated scripts under protected
`/home/mak/codex/piezas`; they were preserved and explicitly classified, not
deleted or promoted to source. Evidence:
`context/PHASE376_LOCAL_FINAL_AUDIT_GATE.md`.

Disposition: `LOCAL_CORE_HEALTH_PASS; ACTIVE_SOURCE_AST_PASS; GENERATED_OUTPUT_EXCEPTION`.

## Next concrete action

Keep the objective open at the documented human/external gates. Before any
final closeout, review the seven generated-output exceptions and the remaining
RD field/live-mutator authority; then use the Phase 375 branch proposal only
after explicit Git direction.

Last verified: 2026-08-15 America/Santiago — Phase 376 local audit gate passed
with the generated-output exception documented; no running MAK service or
container observed.

## Phase 377 — latest authoritative update

Seven malformed generated Codex scripts with zero active references were moved
reversibly from `/home/mak/codex/piezas` to
`context/quarantine/phase376_malformed_generated_codex/`, preserving mode,
size and SHA-256. The active generated surface now has 106 Python files and
zero AST failures. Evidence:
`context/PHASE377_CODEX_MALFORMED_OUTPUT_QUARANTINE.md`.

Disposition: `MALFORMED_GENERATED_OUTPUT_QUARANTINED; REVERSIBLE`.

## Next concrete action

Re-run the local final audit after this quarantine, refresh the objective
matrix, and keep only the documented RD authority/external/Git gates open.

Last verified: 2026-08-15 America/Santiago — Phase 377 Codex generated-output
quarantine validated; no running MAK service or container observed.

## Phase 378 — latest authoritative update

The post-cleanup local audit is green: health, doctor, `pip check`, active AST
371/371, RD privacy DB integrity/empty state and cron safety all pass. The
remaining open gates are explicitly limited to human RD authority, one live
mutator decision, optional external execution and user-directed Git work.
Evidence: `context/PHASE378_POST_CLEANUP_FINAL_AUDIT.md`.

Disposition: `POST_CLEANUP_LOCAL_AUDIT_GREEN; EXTERNAL_AUTHORITY_OPEN`.

## Next concrete action

Maintain the handoff at these exact gates; do not invent field decisions,
enable providers, start services or mutate Git. If no new authority arrives,
the objective remains incomplete but locally ready for the documented handoff.

Last verified: 2026-08-15 America/Santiago — Phase 378 post-cleanup local audit
passed; no running MAK service or container observed.

## Phase 379 — latest authoritative update

The unreferenced destructive sync-repair script was moved reversibly from
`tools/mak_ops` to `context/quarantine/phase379_legacy_sync_repair/`. It could
create cron, use SSH, reset Git and overwrite projections, so it no longer
remains an active tool. Thirteen regenerable mak_ops bytecodes were removed;
the nine remaining active tool files parse. Evidence:
`context/PHASE379_LEGACY_SYNC_REPAIR_QUARANTINE.md`.

Disposition: `LEGACY_DESTRUCTIVE_SYNC_QUARANTINED; REVERSIBLE`.

## Next concrete action

Re-run the post-cleanup local audit after this quarantine, then update the
objective matrix and final handoff. Keep the read-only mirror checker,
protected evidence and WIN untouched; do not run SSH or Git.

Last verified: 2026-08-15 America/Santiago — Phase 379 legacy sync-repair
quarantine validated; no running MAK service or container observed.

## Phase 380 — latest authoritative update

The post-quarantine audit remains green: health, doctor, `pip check`, active
AST 371/371, RD privacy DB integrity/empty state and cron safety pass. The
legacy repairer is absent from `tools/mak_ops` and present only in its
reversible quarantine. Evidence:
`context/PHASE380_POST_SYNC_QUARANTINE_AUDIT.md`.

Disposition: `POST_SYNC_QUARANTINE_AUDIT_GREEN`.

## Next concrete action

Refresh the 13-objective matrix with Phases 377–380 and produce the final
current-state handoff: verified, quarantined, protected, excluded and still
authority-gated items. Do not run SSH, Git, cron, services or live mutators.

Last verified: 2026-08-15 America/Santiago — Phase 380 post-sync quarantine
audit passed; no running MAK service or container observed.

## Phase 381 — latest authoritative update

The 13 objectives are consolidated in
`context/PHASE381_FINAL_OBJECTIVE_STATE.md` and `.csv`. The local MAK surface
is verified through health, doctor, `pip check`, active AST, SQLite,
projection-parity and cron-safety gates. Remaining work is deliberately
separated into authority-gated RD data/mutator decisions, optional external
edges, path-specific cleanup review and a user-authorized Git branch
operation. WIN, protected databases, credentials and generated evidence
remain unchanged.

Disposition: `LOCAL_OBJECTIVES_CONSOLIDATED; AUTHORITY_GATES_EXPLICIT`.

## Next concrete action

Continue with the next executable non-authority step: prepare the final
visual architecture/owner closeout from Phases 362, 370, 381–384, then keep
the RD authority, live mutator, external-boundary, cleanup-review and Git
gates explicit. Do not run SSH, Git, cron, services, providers or live
mutators; no physical move is justified without a named consumer and
rollback.

Last verified: 2026-08-15 America/Santiago — Phase 384 external surfaces
classified; no running MAK service or container observed.

## Phase 385 — latest authoritative update

The final local safety guard is green: `pip check=0`, AST `443/443`, cron
`0`, matching processes `0`, active bytecode `0`, and `rd_datos.db` integrity
`ok` with `atenciones=0`, `encuestas=0`, `registros_testeo=0` and
`sqlite_sequence=0`. Seventy regenerable bytecodes were removed from
explicit active roots; no source, data, credentials, evidence, WIN or
configuration changed. Evidence:
`context/PHASE385_FINAL_LOCAL_SAFETY_GUARD.md`.

Disposition: `FINAL_LOCAL_GUARD_GREEN; EXTERNAL_AUTHORITY_OPEN`.

## Phase 384 — latest authoritative update

The remaining small external surfaces were classified without activation.
`model-config`, `searxng`, the old Blender runtime and the Python environments
are preserved because their provenance or possible consumers remain plausible;
none met the confirmed-junk threshold. No file, database, credential, WIN
surface, service, provider or Git state changed.

Disposition: `EXTERNAL_SURFACES_CLASSIFIED; PRESERVE_AND_GATE`.

## Phase 386 — latest authoritative update

The visual owner architecture is documented in
`context/PHASE386_VISUAL_ARCHITECTURE_OWNER_CLOSEOUT.md`. It separates the
canonical FLUJO owner, runtime projections, protected RD/data/evidence, WIN
history, external deploy, gated mutators, reversible quarantine, discarded
n8n evidence and user-excluded XIO. The remaining gates are explicit and no
new runtime or filesystem mutation was required.

Disposition: `VISUAL_OWNER_ARCHITECTURE_CLOSED; GATES_REMAIN_EXPLICIT`.

## Next concrete action

Stop local mutation at this safe boundary. Continue only when a named
authority arrives for RD field/privacy ingest or one live mutator, or when
the user explicitly authorizes the proposed Git worktree/branch operation.
Otherwise preserve the verified local state and use the Phase 386 diagram as
the architecture reference. Do not run SSH, Git, cron, services, providers
or live mutators automatically.

Last verified: 2026-08-15 America/Santiago — Phase 386 visual owner
architecture closed; no running MAK service or container observed.

## Phase 387 — requirement audit

Phase 387 audited all 13 objectives against current physical evidence. It
keeps field data/privacy, live RD writes, external replay/render/provider
edges, physical duplicate fusion and Git operations open; it confirms the
scope-limited results for catalog fusion, non-serve commands, architecture,
cleanup and branch proposal. Evidence:
`context/PHASE387_REQUIREMENT_EVIDENCE_AUDIT.md/.csv`.

## Phase 388 — runtime-only Platform audit

The four runtime-only Platform rows are resolved by current ownership or
reversible quarantine. Research owns `memoria.py`, Vigia owns `vigia.py`,
and the two orphan artifacts remain protected quarantine evidence.
Evidence: `context/PHASE388_RUNTIME_ONLY_PLATFORM_AUDIT.md`.

## Phase 389 — latest authoritative update

The non-serve command contract was repaired for the two stale human-facing
references. Foreground checks in the FLUJO venv passed version, health,
formats, `job list`, `job next`, datadrop/knowledge lists and RD help; the
dashboard fixture emits the canonical nested command. Evidence:
`context/PHASE389_NONSERVE_COMMAND_CONTRACT_REPAIR.md/.csv`.

Disposition: `NONSERVE_COMMAND_CONTRACT_REPAIRED; LOCAL_GATE_GREEN`.

## Next concrete action

Refresh the 13-objective matrix after Phases 387–389, then continue with the
next unresolved local slice that has a real consumer. Preserve RD field data,
credentials, evidence, generated products and WIN; do not run external
providers, live mutators, SSH, Git, cron or services.

Last verified: 2026-08-15 America/Santiago — Phase 389 non-serve contract
repair and foreground checks passed; no running MAK service observed.

## Phase 390 — current objective matrix

Phase 390 refreshed all 13 objectives after the runtime-only and non-serve
audits. It marks catalog fusion, local commands, architecture design, local
cleanup and the branch proposal at their verified scope, while preserving
open field-data, live-mutator, external-edge, document-fusion and Git gates.
Evidence: `context/PHASE390_CURRENT_13_OBJECTIVE_MATRIX.md/.csv`.

## Phase 391 — latest authoritative update

Phase 391 refreshed dependency ownership from the current `pyproject.toml`,
requirements files and `/home/mak/venvs/flujo`. All nine base modules are
available and `pip check` is green; optional render, desktop, build, dev,
provider and GPU modules remain explicitly gated. No package or requirements
file changed. Evidence: `context/PHASE391_DEPENDENCY_SLICES_REFRESH.md`.

Disposition: `DEPENDENCY_SLICES_CURRENT; BASE_GREEN; OPTIONAL_GATED`.

## Next concrete action

Continue with one bounded duplicate-document family that has a named consumer
and a reversible disposition; do not merge generated evidence or delete by
hash alone. Then refresh the objective matrix. Keep RD field/privacy data,
credentials, WIN, external providers, live mutators, SSH, Git, cron and
services untouched.

Last verified: 2026-08-15 America/Santiago — Phase 391 dependency slice
refresh passed; no running MAK service observed.

## Phase 392 — latest authoritative update

The bounded Curatoria candidate family is byte-identical across five matching
files. `tools/gen_propuestas_rd.py` consumes the FLUJO docs copy; the
`/home/mak/curatoria/db` copy is preserved generated evidence with no active
consumer. Ownership is assigned semantically, but no delete, symlink or path
rewrite was justified.
Evidence: `context/PHASE392_CURATORIA_DOCUMENT_DUPLICATE_GATE.md`.

Disposition: `EXACT_DUPLICATE_OWNER_ASSIGNED; EVIDENCE_PRESERVED; NO_MOVE`.

## Next concrete action

Run the static owner/consumer gate for the user-confirmed EVENTO issue/URL
bridge, without calling the external provider or enabling cron. Then refresh
the objective matrix and handoff with the result.

Last verified: 2026-08-15 America/Santiago — Phase 392 duplicate family
classified; no running MAK service observed.

## Phase 393 — latest authoritative update

The EVENTO issue/URL bridge has a verified canonical owner and a thin runtime
projection used by the paused manifest. Static inspection confirmed issue
reading, URL extraction, local handoff and visible external boundaries. No
GitHub, Instagram, Blender/Ollama, rclone, issue-close or state mutation was
executed; the user-confirmed behavior remains operationally paused here.
Evidence: `context/PHASE393_EVENTO_BRIDGE_STATIC_OWNER_GATE.md`.

Disposition: `EVENTO_BRIDGE_OWNER_VERIFIED; EXTERNAL_REPLAY_DEFERRED`.

## Next concrete action

Refresh the 13-objective matrix with Phases 392–393, then select the next
local consumer slice. Preserve evidence and keep external replay, live RD
writes, providers, SSH, Git, cron and services disabled.

Last verified: 2026-08-15 America/Santiago — Phase 393 bridge owner gate
passed; no running MAK service observed.

## Phase 394 — latest authoritative update

The 13-objective matrix is current after the duplicate-family and EVENTO
bridge gates. Local owner/consumer work is verified at its stated scope; RD
field authority, one live RD write, external replay/render/provider edges,
physical duplicate fusion and Git operations remain open and are not hidden
by fixture success.
Evidence: `context/PHASE394_CURRENT_OBJECTIVE_MATRIX.md/.csv`.

Disposition: `MATRIX_CURRENT; OPEN_AUTHORITY_BOUNDARIES`.

## Next concrete action

Run the final current physical guard (AST, pip, SQLite, cron, process and
bytecode invariants), then continue only with a newly discoverable local
consumer slice. Preserve evidence and keep external replay, live RD writes,
providers, SSH, Git, cron and services disabled.

Last verified: 2026-08-15 America/Santiago — Phase 394 objective matrix
refreshed; no running MAK service observed.

## Phase 395 — latest authoritative update

The current conservative safe suite completed with exit 0 in
`/home/mak/research/.venv`. It excludes the 177-file risk surface
and therefore expands local evidence without claiming full MAK coverage.
No external or durable state changed. Evidence:
`context/PHASE395_SAFE_LOCAL_TEST_SUITE.md/.csv`.

Disposition: `SAFE_LOCAL_COVERAGE_GREEN; EXTERNAL_RISK_UNEXECUTED`.

## Next concrete action

Select one excluded test file/group only after AST call inspection proves a
temporary fixture and no external/durable side effect. Keep live RD data,
providers, workers, services, Git, SSH, XIO and external automation gated.

Last verified: 2026-08-15 America/Santiago — Phase 395 safe suite passed;
no running MAK service observed.

## Phase 396 — latest authoritative update

A bounded excluded test group was promoted after AST/fixture inspection:
`test_puente_issues.py` and `test_eventos_flyer_auto.py` passed 6/6 with
temporary paths and mocked download/render/state collaborators. No external
or durable state was touched. Evidence:
`context/PHASE396_PROMOTED_EVENTOS_BRIDGE_FIXTURES.md`.

Disposition: `BOUNDED_FIXTURE_PROMOTED; EXTERNAL_RUNTIME_UNEXECUTED`.

## Next concrete action

Inspect one more excluded test group only if its collaborators are fully
mocked and writes are temporary. Keep live RD ingest/mutations, providers,
workers, services, Git, SSH, XIO and external automation gated.

Last verified: 2026-08-15 America/Santiago — Phase 396 bounded fixture group
passed; no running MAK service observed.

## Phase 397 — latest authoritative update

`tests/test_reception.py` passed 2/2 using monkeypatched IMAP and environment
fixtures. No mailbox, email, provider or durable state was accessed. Evidence:
`context/PHASE397_PROMOTED_RECEPTION_FIXTURE.md`.

Disposition: `MOCKED_RECEPTION_FIXTURE_PROMOTED; IMAP_UNEXECUTED`.

## Next concrete action

Continue only with one more excluded test group if its AST proves full mock
and temporary isolation; otherwise refresh the 13-objective matrix and keep
the external/live boundary open.

Last verified: 2026-08-15 America/Santiago — Phase 397 reception fixture
passed; no running MAK service observed.

## Phase 398 — latest authoritative update

`tests/test_mak_hub_eventos.py` passed 15/15 with temporary JSONL paths and
monkeypatched HTTP proxy calls. The hub was imported only; no server, network,
provider or durable MAK state ran. Evidence:
`context/PHASE398_PROMOTED_HUB_EVENTOS_FIXTURES.md`.

Disposition: `HUB_EVENTOS_FIXTURE_PROMOTED; LIVE_HUB_UNEXECUTED`.

## Next concrete action

Refresh the current coverage/objective matrix with Phases 395–398, then
inspect one remaining excluded group only if it is fully isolated. Do not
batch-run the remaining risk surface or activate external boundaries.

Last verified: 2026-08-15 America/Santiago — Phase 398 hub fixture group
passed; no running MAK service observed.

## Phase 399 — latest authoritative update

`tests/test_cron_nocturno.py` passed 13/13 using only pytest temporary
directories, including its permanent-delete assertions. The real scheduler,
MAK files, WIN and durable state were untouched. Evidence:
`context/PHASE399_PROMOTED_CRON_FIXTURES.md`.

Disposition: `ISOLATED_CLEANUP_FIXTURES_PROMOTED; REAL_SCHEDULER_UNEXECUTED`.

## Next concrete action

Refresh the current coverage/objective matrix with Phases 395–399 and run
the final physical guard. Do not batch-run remaining risk tests or activate
external/live boundaries.

Last verified: 2026-08-15 America/Santiago — Phase 399 isolated cleanup
fixtures passed; no running MAK service observed.

## Phase 400 — latest authoritative update

Coverage and physical guards are current: 68 safe files/485 cases passed,
four promoted groups add 36/36 passing cases, active AST is 550/550, pip
check is 0, active cron is 0, matching processes are 0, active bytecode is
0, and `rd_datos.db` integrity is good with all four tables empty. No
external/live/durable/WIN/Git state changed. Evidence:
`context/PHASE400_COVERAGE_AND_PHYSICAL_GUARD.md/.csv`.

Disposition: `LOCAL_COVERAGE_REFRESHED; PHYSICAL_GUARD_GREEN`.

## Next concrete action

Promote one additional excluded test group only after the same AST/mock/tmp
proof, or refresh the 13-objective matrix if no safe group remains. Keep RD
field authority, live mutation, providers, workers, services, Git, SSH, XIO
and external automation gated.

Last verified: 2026-08-15 America/Santiago — Phase 400 coverage and physical
guard passed; no running MAK service observed.

## Phase 401 — latest authoritative update

Four deterministic contract groups passed 19/19 using only environment
monkeypatches, temporary JSON/XML and pure transformations. The real IMAP,
OSC, Blender, GPU, network and provider boundaries remain unexecuted.
Evidence: `context/PHASE401_DETERMINISTIC_CONTRACT_FIXTURES.md`.

Disposition: `DETERMINISTIC_CONTRACTS_PROMOTED; LIVE_SURFACES_UNEXECUTED`.

## Next concrete action

Refresh the coverage/objective matrix after Phases 395–401, then continue
only with another fully isolated group or preserve the explicit live-boundary
gates. Do not run external providers, workers, services, Git, SSH, XIO or
live RD mutations.

Last verified: 2026-08-15 America/Santiago — Phase 401 deterministic
contracts passed; no running MAK service observed.

## Phase 402 — latest authoritative update

The current 13-objective matrix was refreshed after Phases 395–401. It records
55 promoted deterministic cases, the 68-file/485-case conservative suite,
the 550/550 broad and 444/444 operational AST gates, `pip check=0`, zero
active cron entries and an intact empty `rd_datos.db`. No source, database,
credential, generated product, WIN or Git state changed.
Evidence: `context/PHASE402_CURRENT_13_OBJECTIVE_MATRIX.md/.csv`.

Disposition: `MATRIX_REFRESHED; LOCAL_PROOF_ADVANCED; AUTHORITY_BOUNDARIES_OPEN`.

## Next concrete action

Perform a bounded static classification of the remaining excluded test files,
selecting at most one group only if its imports, writes and external edges
are provably isolated. If no such group remains, preserve the live-boundary
gates and prepare the final owner/cleanup/branch handoff. Do not run external
providers, workers, services, Git, SSH, XIO or live RD mutations.

Last verified: 2026-08-15 America/Santiago — Phase 402 matrix refreshed; no
running MAK service observed.

## Phase 403 — latest authoritative update

The statically isolated `test_cli_v035.py` group passed 2/2 with exit 0. The
CLI used only temporary workspace paths; no real MAK state, database, WIN,
provider, service, Git or external endpoint changed. The separate
`/home/mak/src/ml-mobileclip` surface exposed 18 pre-existing `.pyc` files;
they were preserved because ownership and confirmed-junk evidence are not
established.
Evidence: `context/PHASE403_PROMOTED_CLI_V035_FIXTURE.md`.

Disposition: `CLI_V035_FIXTURE_PROMOTED; SEPARATE_ML_BYTECODE_PRESERVED`.

## Next concrete action

Refresh the objective matrix with Phase 403 and inspect the remaining
excluded tests only through the same AST/import/write-set gate. Do not run
another group unless it is independently temporary and side-effect-free.
Keep RD field authority, live mutations, providers, workers, services, Git,
SSH, XIO and external automation gated.

Last verified: 2026-08-15 America/Santiago — Phase 403 CLI fixture passed;
no running MAK service observed.

## Phase 404 — latest authoritative update

The objective matrix was refreshed after the CLI fixture promotion. Local
proof now totals 57 promoted deterministic cases plus the 68-file/485-case
safe suite. Static classification found no second new fixture-only group;
the remaining queue is risk-bound or externally gated. The 18 pre-existing
`.pyc` files under `/home/mak/src/ml-mobileclip` remain preserved as a
separate owner surface. No source, data, WIN, credential, generated product,
service, provider or Git state changed.
Evidence: `context/PHASE404_CURRENT_13_OBJECTIVE_MATRIX.md/.csv`.

Disposition: `MATRIX_CURRENT; SAFE_LOCAL_QUEUE_EXHAUSTED; AUTHORITY_BOUNDARIES_OPEN`.

## Next concrete action

Prepare the final owner/cleanup/branch handoff: reconcile the Phase386 folder
architecture with physical `/home/mak/*`, record the ML bytecode owner
decision and restate the exact externally gated actions. Do not move/delete
anything, run providers, start services, use Git/SSH/XIO or perform live RD
mutations without the corresponding explicit authority.

Last verified: 2026-08-15 America/Santiago — Phase 404 matrix current; no
running MAK service observed.

## Phase 405 — latest authoritative update

The physical owner map and cleanup/merge order are now explicit. `flujo`
remains canonical, department roots remain consumer-backed projections,
`rd.db` and `rd_datos.db` remain separate, WIN remains historical, n8n is
discarded/protected, XIO remains excluded, and optional/external roots remain
gated. The proposed branch system is recorded but no Git operation occurred.
No physical move, deletion, source, data, credential, generated-product,
provider, service or WIN state changed.
Evidence: `context/PHASE405_OWNER_CLEANUP_BRANCH_HANDOFF.md`.

Disposition: `OWNER_MAP_READY; CLEANUP_ORDER_DEFINED; BRANCH_PROPOSAL_HANDOFF_READY`.

## Next concrete action

Stop local promotion here unless a new concrete consumer appears. The next
actions are authority-bound: approve field data/privacy decisions, name one
live RD mutation and rollback, approve any physical duplicate fusion or
residue quarantine, then separately request Git branch creation. Preserve all
gates and do not use external providers, services, Git, SSH, XIO or live RD
mutations implicitly.

Last verified: 2026-08-15 America/Santiago — Phase 405 owner map current;
no running MAK service observed.

## Phase 406 — latest authoritative update

The RD database fusion is now closed at the data/consumer level. The
canonical `rd.db` already contains the complete row set; the state snapshot
contributes no missing rows or columns and remains protected historical
evidence. Overwriting it into the canonical path would regress schema
metadata, so no database file was rewritten. `rd_datos.db` remains separate
and empty. Evidence: `context/PHASE406_RD_DB_FUSION_CLOSURE.md/.csv`.

Disposition: `RD_DB_FUSION_CLOSED; CANONICAL_OWNER_CONFIRMED; SNAPSHOT_PRESERVED`.

## Next concrete action

Advance to the next unresolved objective: perform a read-only static audit of
the RD mutation entrypoints and their rollback contracts, then update the
matrix. Do not send live POSTs or rewrite databases until a named mutation
authority exists.

Last verified: 2026-08-15 America/Santiago — Phase 406 RD database fusion
closed; no running MAK service observed.

## Phase 407 — latest authoritative update

The RD mutation entrypoint surface is current: 16 literal POST routes parse
successfully and match the Phase250 matrix. The two parse routes share one
branch and explain the 15 matrix rows. Durable effects remain classified and
authority-gated; no live POST or database/file mutator was called.
Evidence: `context/PHASE407_RD_MUTATION_STATIC_AUDIT.md/.csv`.

Disposition: `RD_MUTATION_ROUTES_STATIC_CURRENT; LIVE_POSTS_UNEXECUTED`.

## Next concrete action

Keep live mutators gated and move to the next local objective: reconcile the
automation owner and non-serve command contract against current consumers,
then refresh the objective matrix. Do not activate providers, services,
workers, Git, SSH, XIO or live RD writes.

Last verified: 2026-08-15 America/Santiago — Phase 407 RD mutation static
audit passed; no running MAK service observed.

## Phase 408 — latest authoritative update

The portfolio web now has a clear owner and branch: `flujo` is canonical,
`iskvw` is the public site, `tools/portfolio/proyectos.json` is the catalogue
input, the React panel and `/api/portafolio` are read-only consumers, and
`portfolio_media` is protected asset storage. The duplicate tool folders in
`flujo-deploy` and `vibecodeine` are byte-identical projections. No media,
source, database, WIN or Git state changed.
Evidence: `context/PHASE408_PORTFOLIO_WEB_OWNER_GATE.md`.

Disposition: `PORTFOLIO_OWNER_CONFIRMED; DUPLICATE_TOOLS_PARITY; BRANCH_ADDED_TO_PROPOSAL`.

## Next concrete action

When portfolio work is authorized, validate only the isolated
`codex/portfolio/web` write set with local typecheck/build and catalogue/path
fixtures. Keep shared hub edits, publishing, external media operations, Git,
XIO and live RD mutations separately gated.

Last verified: 2026-08-15 America/Santiago — Phase 408 portfolio owner gate
passed; no running MAK service observed.

## Phase 409 — latest authoritative update

The recommended 2026 strategy for MAK is trunk-based development with a
GitHub-Flow review boundary. The earlier list of area branches is now a set of
topic-name templates, not a set of permanent branches or a sequential merge
chain. `main` is the only permanent development branch; `release/vX.Y` is
temporary and only created for an actual hardening window. No Git operation
was performed.
Evidence: `context/PHASE409_GIT_STRATEGY_RESEARCH.md`.

Disposition: `TRUNK_BASED_PR_RECOMMENDED; LONG_LIVED_BRANCHES_REJECTED; GIT_UNTOUCHED`.

## Next concrete action

Keep Git untouched until a concrete slice is ready. When authorized, create
one short-lived topic branch from the current baseline, validate its exclusive
write set, merge it directly to protected `main`, and delete the topic branch
after integration. Do not create the entire branch list in advance.

Last verified: 2026-08-15 America/Santiago — Phase 409 strategy research
completed; no running MAK service observed.

## Phase 410 — latest authoritative update

The portfolio publishing connection was audited read-only. The active
workflow publishes only the generated `iskvw/` surface through GitHub Pages
actions and only after manual `workflow_dispatch`. It writes `_sitio/CNAME`
from repository variable `PUBLIC_DOMAIN`, falling back to `iskvw.cl` when the
variable is absent. The deployment copy in `flujo-deploy` is byte-identical.
No operational Cloudflare deployment configuration was found locally, and
local DNS lookups for `iskvw.cl` returned no answers; this cannot prove the
external Cloudflare dashboard state. Domain renewal/migration remains
deferred. No hosting, domain, Git or source mutation was performed.
Evidence: `context/PHASE410_PORTFOLIO_HOSTING_CONNECTION_AUDIT.md`.

Disposition: `PORTFOLIO_GITHUB_PAGES_CONFIRMED; CLOUDFLARE_EXTERNAL_STATE_UNVERIFIED; DOMAIN_MIGRATION_DEFERRED`.

## Next concrete action

Keep Cloudflare, DNS, domain renewal and `PUBLIC_DOMAIN` untouched. Continue
the next unresolved MAK integration gate. If domain migration is later
authorized, first inspect GitHub Pages custom-domain and Cloudflare DNS as one
read-only bounded external check, then set `PUBLIC_DOMAIN` before dispatching
the workflow.

Last verified: 2026-08-15 America/Santiago — Phase 410 portfolio hosting
connection audit completed; no running MAK service observed.

## Phase 411 — latest authoritative update

The venue relationship is now classified as a cross-domain integration gate.
RD owns the operational catalog in `data/rd.db`; VJ owns technical venue
records and geometry in the JSON/YAML venue surfaces; Curatoria and the
portfolio may consume safe projections. `rd_datos.db` remains a separate empty
privacy/field store. No physical database merge was performed.
Evidence: `context/PHASE411_RD_VENUE_CROSS_DOMAIN_GATE.md`.

## Next concrete action

Create a read-only venue crosswalk with stable IDs, aliases, provenance,
confidence, RD/VJ/Curatoria consumers and public/private status. Validate the
crosswalk before changing any database, venue file or portfolio publication.

Last verified: 2026-08-15 America/Santiago — Phase 411 venue cross-domain gate
classified; no running MAK service observed.

## Phase 412 — latest authoritative update

The read-only venue crosswalk is complete for the current evidence. RD owns 3
canonical venue IDs in `data/rd.db`; the technical VJ JSON/YAML records are
not yet joined to those IDs, and 7 event venue strings remain unresolved or
non-canonical. Name similarity was not treated as proof. No database, venue
file or public portfolio data changed.
Evidence: `context/PHASE412_VENUE_CROSSWALK.md`.
Foreground verification exited 0: physical root enumeration, read-only
SQLite/JSON/YAML/schema inspection and exact `uvicorn`/`gunicorn` absence
guard. Files modified: the Phase 412 report and this handoff only. Risk:
raw venue names remain unresolved and must not be promoted by fuzzy matching.

## Next concrete action

Validate explicit venue aliases and provenance against the RD read consumers
and `venue.schema.json`. Only then consider a cross-domain venue artifact;
keep physical databases separate and keep public portfolio projection gated.

Last verified: 2026-08-15 America/Santiago — Phase 412 venue crosswalk built;
no running MAK service observed.

## Phase 413 — latest authoritative update

The integration model now treats MAK as a shared service box: Curatoria
indexes and produces dossiers/proposals; RD supplies event-specific tools;
the VJ layer supplies venue/screen/scenography reality; and the portfolio
publishes approved cases. SCD is the verified venue-3D prototype. The current
record remains a demonstrator because dimensions are `aportado` and projection
is `desconocido`; no certification is claimed.
Evidence: `context/PHASE413_CROSS_DOMAIN_SERVICE_ARCHITECTURE.md`.

## Next concrete action

Map `venue-3d`, `curatoria-index`, `rd-vj-layout` and `portfolio-cases` to exact
existing consumers, contracts and write sets. Keep databases physically
separate, preserve provenance and do not create branches until a vertical
slice is ready.

Last verified: 2026-08-15 America/Santiago — Phase 413 service architecture
recorded; no running MAK service observed.

## Phase 414 — latest authoritative update

The original theater-with-seats Python tool is confirmed at
`/home/mak/flujo/projects/plano/referencia_plano_teatro.py`. It is the source
genealogy behind the SCD 3D venue prototype, not an unrelated duplicate. The
headless derivative and all four physical copies have matching hashes. The
primitive should be preserved as reference/client GUI while future work
extracts reusable geometry without changing its claims.
Evidence: `context/PHASE414_THEATER_SEATING_PRIMITIVE_GATE.md`.

## Next concrete action

Map the primitive's parameter/output contract to the venue-3D and RD-VJ
vertical slices. Keep the GUI, headless derivative, measured-data tier and
public portfolio projection as separate contracts until a shared engine is
validated.

Last verified: 2026-08-15 America/Santiago — Phase 414 theater primitive
located and validated; no running MAK service observed.

## Phase 415 — latest authoritative update

The cultural projects are now classified by genealogy and maturity rather than
folder names. The source of direction is the artist's rainstorm; each line
moves from dossier to instrument to material to piece. ASCII/Borradura is a
technical Windows encoding scar transformed into measurement and art. Cauce is
a Tapiz mode, not an unrelated tool. Precursor remains dossier-first. No
source, artwork, data or Git state changed.
Evidence: `context/PHASE415_CULTURAL_GENEALOGY_MAP.md`.

## Next concrete action

Use the genealogy to classify each cultural surface as active instrument,
prototype, generated piece, dossier-only, historical WIN evidence or protected
material. Then map only the active instruments to real consumers and write sets.

Last verified: 2026-08-15 America/Santiago — Phase 415 cultural genealogy
mapped; no running MAK service observed.

## Phase 416 — latest authoritative update

Tilde is now recorded as the origin of the repository language boundary, not
just a cultural project. The active rule is two-layered: new machine-facing
code/metadata in English ASCII; human-facing RD, Curatoria and Portfolio
material in correct Spanish UTF-8. Legacy names remain until their consumers
move. The cultural lines now have an explicit relation to current tools and
services.
Evidence: `context/PHASE416_CULTURE_TO_CURRENT_REPO_CROSSWALK.md`.

## Next concrete action

Map active service slices by input language, stable ASCII IDs, UTF-8 human
values, provenance, confidence, output and consumer. Start with venue/RD/VJ and
Curatoria indexing; preserve dossiers and WIN as lineage.

Last verified: 2026-08-15 America/Santiago — Phase 416 culture/current-repo
crosswalk recorded; no running MAK service observed.

## Phase 417 — historical update

Markdown work is now being consolidated logically by exact content and by
family: context, ideas, historical evidence and vendor noise. Original files
remain intact; masters provide the active reading path. Exact duplicates are
grouped, while divergent sessions are summarized without erasing variants.
Evidence: `context/PHASE417_MD_CONSOLIDATION.md`.

## Phase 418 — historical update

Meaningful Markdown consolidation advanced before HTML. The context master now
indexes direction memory, architecture/capability maps, RD editorial rules,
RD data/venue/plano documentation, opportunity/proposal research and raw
evidence. The ideas master now records the Curatoria/archive/postulation and
RD/VJ/venue/proposal families. Fondart material is explicitly research-only
until primary-source verification; original Markdown remains untouched.
Evidence: `context/PHASE418_MD_MEANINGFUL_CONSOLIDATION.md`.

Disposition: `MD_FAMILY_CONSOLIDATION_ADVANCED; HTML_DEFERRED; SOURCES_PRESERVED`.

## Phase 419 — historical update

The next Markdown families were classified. `puente/` is theory/manifesto with
no runtime consumer. The recovered Firecrawl/Crawl4AI and quantified-self
reports are Curatoria research evidence with privacy/provider boundaries. The
RD editorial files v3, v4 and v4.1 are distinct revisions; v4.1 remains the
current human-facing contract. No originals were merged destructively.
Evidence: `context/PHASE419_MD_FAMILY_RANKING.md`.

Disposition: `MD_BRIDGE_AND_RESEARCH_CLASSIFIED; EDITORIAL_LINEAGE_PRESERVED; HTML_DEFERRED`.

## Phase 420 — historical update

The RD research Markdown family and the Tapiz/Resolume VJ specification family
were consolidated into the masters. RD reports remain generated research with
human-review debt; they are not legal, clinical, chemical, financial or field
authority. Tapiz/Resolume remains an operator specification, not a running
service. Original files remain preserved.
Evidence: `context/PHASE420_RD_RESEARCH_MD_CONSOLIDATION.md`.

Disposition: `RD_RESEARCH_CLASSIFIED; VJ_SPEC_CLASSIFIED; HTML_DEFERRED`.

## Phase 421 — historical update

The useful Markdown consolidation pass is bounded. A protected-prune scan
found 13,135 reachable Markdown files across MAK; most outside canonical
`flujo` are WIN/history, rollback/quarantine, research, projections, caches or
other evidence. Canonical families now have an owner/disposition in the two
masters. The disconnected `/home/mak/OneDrive` mount was recorded as an
external reachability issue, not treated as absent.
Evidence: `context/PHASE421_MARKDOWN_BOUNDARY_AND_HTML_GATE.md`.

Disposition: `MD_BOUNDARY_DOCUMENTED; HTML_INVENTORY_AUTHORIZED_READ_ONLY`.

## Phase 422 — historical update

The read-only HTML inventory found 814 reachable HTML/HTM files (88,356,717
bytes) across MAK, with 123 exact SHA-256 duplicate groups covering 414 files.
The canonical `flujo` surface has 59 files; WIN, quarantine, runners,
deployments and inboxes contain historical/projection/evidence copies. No HTML
was edited or merged. Exact equality was not treated as ownership proof.
Evidence: `context/PHASE422_HTML_EXACT_INVENTORY.md`.

Disposition: `HTML_HASH_INVENTORY_COMPLETE; OWNER_MATRIX_REQUIRED; NO_HTML_MUTATION`.

## Phase 423 — historical update

The active HTML owner/consumer matrix is now documented. `hub.py` serves the
three identical context aliases by pathname; `web/dist/index.html` is their
generated source candidate; RD/plano/venue and portfolio pages remain separate
projections or consumers. The current build output is 72 bytes larger than
the context aliases, so generated parity is not yet claimed and no overwrite
was performed. Legacy `projects/plano/plano_editor.html` remains explicitly
deprecated; XIO remains excluded per the user.
Evidence: `context/PHASE423_HTML_OWNER_CONSUMER_MATRIX.md`.

Disposition: `HTML_OWNER_MATRIX_BUILT; CONTEXT_BUILD_PARITY_GATED; NO_HTML_MUTATION`.

## Phase 424 — historical update

The HTML parity gate was tested without mutating canonical files. TypeScript
passed (`npm run typecheck`, exit 0). The npm build could not execute because
the local Vite wrappers are mode 644 (exit 127). Direct Vite invocation also
failed (exit 1) because Node is 18.20.4 while Vite requires 20.19+ or 22.12+,
and the optional Linux Rollup module is missing. No package or permission was
changed; no service was started.
Evidence: `context/PHASE424_HTML_BUILD_PARITY_GATE.md`.

Disposition: `HTML_SOURCE_TYPECHECK_GREEN; BUILD_ENVIRONMENT_BLOCKED; NO_HTML_OVERWRITE`.

## Phase 425 — historical update

The HTML owner map is consolidated logically. Hub aliases are one pathname-
selected generated family. RD and Plano are separate standalone bundles with
their own entries, source imports, configs and copy scripts. Venue and
Portfolio remain separate consumers/projections. Script syntax checks passed;
the Vite environment gate remains unchanged and no HTML was overwritten.
Evidence: `context/PHASE425_HTML_VERTICAL_OWNER_CONSOLIDATION.md`.

Disposition: `HTML_VERTICAL_OWNERS_CONSOLIDATED; LOGICAL_MERGE_ONLY; WRITE_GATE_CLOSED`.

## Phase 426 — historical update

The Venue/Portfolio HTML bridge is now explicit. `web/venues/index.html` is a
self-contained two-record example catalogue with `aportado` values, not the
canonical venue database. `iskvw/piel/venue/index.html` consumes the real SCD
JSON registry and `iskvw/piel/campo/index.html` exposes that link only through
`tablero.json` with `mejoras.venue3d=true`. The public catalogue, venue data and
portfolio projection remain separate owners.
Evidence: `context/PHASE426_VENUE_PORTFOLIO_HTML_BRIDGE.md`.

Disposition: `VENUE_PORTFOLIO_BRIDGE_EXPLICIT; EXAMPLE_CATALOGUE_NOT_CANONICAL; NO_DATA_MUTATION`.

## Phase 427 — historical update

The venue/producer distinction was corrected in the crosswalk: Espacio Riesco
is a venue; OpenKlub is a producer/brand. The current `data/rd.db` has
`productoras.openklub` plus a conflated `venues.openklub` row, and the knowledge
venue file repeats that conflation. The row and file were preserved; no
database mutation was made. `Central Cultural` remains an unresolved venue
candidate for an OpenKlub event.
Evidence: `context/PHASE427_VENUE_ROLE_CORRECTION_CROSSWALK.md`.

Disposition: `OPENKLUB_ROLE_CORRECTED; RD_VENUE_CONFLATION_GATED; NO_DB_MUTATION`.

## Phase 428 — historical update

The declared Venue generator regenerated `/home/mak/flujo/web/venues/index.html`
from `data/venues/*.json`: the projection moved from 2 stale examples to the 3
current public records, including `scd-plaza-egana`. Generator and validator
both exited 0. No RD database, producer file, knowledge venue, Portfolio page
or historical evidence changed. OpenKlub was not inserted as a venue.
Evidence: `context/PHASE428_VENUE_SITE_REGENERATION.md`.

Disposition: `VENUE_HTML_PROJECTION_REGENERATED; OPENKLUB_NOT_VENUE; RD_DB_UNCHANGED`.

## Phase 429 — historical update

The OpenKlub correction plan traced the source/consumer chain. OpenKlub is
already correctly owned by `data/productoras/openklub.json`; the conflated
`knowledge/venues/openklub.yaml` feeds the RD venue projection but is not
needed by its `productora_venues` record, which correctly leaves the unresolved
Central Cultural candidate without a venue ID. No mutation was executed because
the actual venue identity is unknown and the evidence must remain recoverable.
Evidence: `context/PHASE429_OPENKLUB_CORRECTION_PLAN.md`.

Disposition: `OPENKLUB_SOURCE_OWNER_CONFIRMED; VENUE_SOURCE_QUARANTINE_PLANNED; NO_DB_REBUILD`.

## Phase 430 — latest authoritative update

The OpenKlub role correction was executed reversibly. The inferred
`knowledge/venues/openklub.yaml` was moved to a named quarantine with its
original hash preserved, and `data/rd.db` was rebuilt using
`/home/mak/venvs/flujo/bin/python`. Active RD venues are now Espacio Riesco
and Paralelo 89; OpenKlub remains a producer; Central Cultural remains an
unresolved candidate with no venue ID. The independent JSON venue catalogue
still validates 3 public technical venues including SCD.
Evidence: `context/PHASE430_OPENKLUB_SOURCE_CORRECTION.md`.

Disposition: `OPENKLUB_CONFLATION_REMOVED_REVERSIBLY; RD_DB_REBUILT; PRODUCER_PRESERVED`.

## Phase 431 — latest authoritative update

The inferred `knowledge/venues/paralelo_89.yaml` was found to rely only on the
filename `FRVR.PARALELO89.png`. The flyer itself shows `FRVR` as the
user-confirmed DJ headliner, `PARALELO 86` as another artist and `SALA
METRONOMO` as the event venue. A focused web check supports Paralelo 86 as a
DJ/producer act and Sala Metronomo as a real venue; it did not support
Paralelo 89 as a venue. The YAML was moved reversibly to
`context/quarantine/phase431_paralelo89_role_correction/`, and
`data/productoras/frvr.json` now records FRVR with `tipo: artist_dj` and
`headliner: true`, retains Sala Metronomo as an unresolved event venue
(`venue_id: null`) and preserves the filename conflict. The organizer remains
unknown.

The active RD catalog was rebuilt with the FLUJO venv. `rd-db venues` exited 0
and now lists only Espacio Riesco in this affected family; `rd-db productora
frvr` exited 0 and lists Sala Metronomo. The generated RD projections were
refreshed successfully:

- `docs/rd/presentacion_db.html` (exit 0; 20 productoras/spots)
- `docs/rd/propuesta_directiva.html` (exit 0; 3 paquetes, 20 productoras,
  23 reactivos, 8 suplementos)
- `web/src/data/rdDbEmbebida.json` (exit 0; 20 productoras, 1 venue, 8 logos)

The existing `tools/triangular_fichas.py` was run read-only on
`/home/mak/curatoria/fichas/fichas.jsonl` in a temporary directory (exit 0:
3,385 fichas, 1,030 with signal, 197 event clusters, 322 producer
candidates). It surfaced ficha `8788a9b256eb` at 2026-07-10 / Sala Metronomo
but did not identify the producer, which is the correct unresolved result. No
new triangulation Python was created. The Research triangulation contract is
now recorded: resolve missing date, producer, artist or venue through the
other orthogonal keys; retain query, URL, retrieval date, matched fields,
confidence and conflicts; never promote a filename/OCR guess into a canonical
entity.

Evidence: `context/PHASE431_PARALLELO89_ROLE_CORRECTION.md`.

Disposition: `PARALELO89_VENUE_CONFLATION_REMOVED_REVERSIBLY; FRVR_HEADLINER_ROLE_RECORDED; ORGANIZER_UNRESOLVED; RD_PROJECTIONS_REFRESHED`.

## Phase 432 — latest authoritative update

The FRVR role update was rebuilt and asserted: source `data/productoras/frvr.json`
has `tipo: artist_dj` and `headliner: true`; `rd.db` has no `paralelo_89` or
`openklub` venue; Espacio Riesco remains canonical; FRVR links to unresolved
Sala Metronomo with `venue_id = NULL`. The three source-level RD projections
were regenerated with exit 0. The existing `tools/triangular_fichas.py` was
run read-only on the real curatoria corpus in a temporary directory (exit 0)
and produced the expected unresolved producer candidate for ficha
`8788a9b256eb`.

The separate Vite distribution gate was then checked. `web/dist-rd/rd.html`
and `dist_compartir/herramientas_rd.html` are exact copies (SHA-256
`11eb4eab551129f779caba4734d66736312c270cb700b96e803ad9f5c72fa175`) but
still contain stale `paralelo_89` and old `openklub` venue markers. Their owner
is `web/src/mainRd.tsx` + `vite.rd.config.ts` + `copy-rd-share.mjs`; no minified
bundle was edited. The build remains gated by the Phase 424 Node/Vite/Rollup
environment issue.

Evidence: `context/PHASE432_RD_BUNDLE_STALE_PROJECTION_GATE.md`.

Disposition: `FRVR_HEADLINER_ROLE_REBUILT; SOURCE_RD_PROJECTIONS_GREEN; RD_VITE_BUNDLE_STALE_AND_GATED`.

## Phase 433 — latest authoritative update

The next HTML family was consolidated logically. `web/public/mapping.html`,
`web/dist/mapping.html`, `web/dist-rd/mapping.html`,
`web/dist-plano/mapping.html` and `context/mapping.html` are byte-identical
(SHA-256 `e5c06dbb5491b11ed1b36e37969c3d4772d45c476997b3d887b79560c0392d3c`).
The source owner is `web/public/mapping.html`; `MappingTool.tsx` consumes it
with a relative path, and `copy-context.mjs` produces the context projection.
The HTML parser smoke check passed on source, dist and context samples (245
tags and expected Event Rigging marker). No file was deleted or edited.

Evidence: `context/PHASE433_MAPPING_HTML_OWNER_CONSOLIDATION.md`.

Disposition: `MAPPING_HTML_LOGICALLY_CONSOLIDATED; FIVE_BYTE_IDENTICAL_CONSUMER_PROJECTIONS; NO_PHYSICAL_DELETE`.

## Phase 434 — latest authoritative update

The active portfolio editor contract was verified. `iskvw/editor.html` and its
`flujo-deploy` copy are exact (SHA-256
`d90010161edb83ec1e341c00bcf203510badd70df6cadcdeb23f02ba996d9f75`); WIN,
platform and rollback variants remain distinct historical evidence. Static
contract markers passed, `tools/validar_curaduria.py` compiled with exit 0,
and Node executed the real `construirCuraduria()` with UTF-8, unknown-field
preservation, default suppression and rounding assertions passing. The
repository pytest files were not runnable because `pytest` is absent in both
available Python environments (exit 1); no package was installed.

Evidence: `context/PHASE434_ISKVW_EDITOR_CONTRACT_GATE.md`.

Disposition: `ISKVW_EDITOR_ACTIVE_CONTRACT_CONFIRMED; DEPLOY_COPY_EXACT; HISTORICAL_VARIANTS_PRESERVED; PYTEST_ENVIRONMENT_GATED`.

## Phase 435 — latest authoritative update

The active ISKVW terminal skin was validated. `iskvw/piel/terminal/index.html`
and its `flujo-deploy` projection are byte-identical; WIN, Vibecodeine,
quarantine and rollback variants remain historical evidence. The skin loads
`iskvw/datos/archivo.json` first and falls back to `iskvw/datos/obras.json`;
both active files exist. Static HTML assertions passed and both inline
JavaScript blocks passed `node --check` with exit 0. No network, service,
mutation or data write ran.

Evidence: `context/PHASE435_ISKVW_TERMINAL_HTML_GATE.md`.

Disposition: `ISKVW_TERMINAL_ACTIVE; DEPLOY_COPY_EXACT; STATIC_DATA_FALLBACK_VERIFIED; HISTORICAL_VARIANTS_PRESERVED`.

## Phase 436 — latest authoritative update

The Plano/Rider HTML owner chain was verified from source. `web/plano.html` and
`web/src/mainPlano.tsx` feed the separate `vite.plano.config.ts` bundle, which
declares no-server mode and loads local symbols. The current generated files
`web/dist-plano/plano.html` and `dist_compartir/plano_rd.html` are not byte
identical (`cmp` exit 1) and have distinct hashes; no overwrite or manual
minified edit was performed. Source/runtime build parity remains gated by the
existing Node/Vite/Rollup environment issue.

Evidence: `context/PHASE436_PLANO_RIDER_HTML_OWNER_GATE.md`.

There is one explicit cross-domain data boundary to preserve: FRVR is
role-marked `artist_dj`/headliner in its source, but the legacy RD SQLite
compatibility table is named `productoras`. That placement is not evidence of
an organizer; a future role-aware projection must consume the existing source
field before publication.

Disposition: `PLANO_RIDER_SOURCE_OWNER_CONFIRMED; GENERATED_OUTPUTS_DIVERGENT; BUILD_PARITY_OPEN; NO_OVERWRITE; FRVR_ROLE_PROJECTION_OPEN`.

## Phase 437 — latest authoritative update

The La Gota RD HTML tool was traced to its existing cultural memory and
validated. `tools/gota_rd/index.html` and its `flujo-deploy` copy are exact;
both inline scripts pass `node --check`. The page marks its reaction table as
DEMO, warns that colorimetric testing is orientative, and defaults its optional
endpoint to empty. It only reaches an external endpoint if a user configures
one through URL/localStorage. No camera, network, POST, database or service
was run. `/api/rd-datos-summary` exists separately in the Hub and was not
silently wired into Gota.

Evidence: `context/PHASE437_GOTA_RD_HTML_CONTRACT_GATE.md`.

Disposition: `GOTA_RD_ACTIVE_DEMO; DEPLOY_COPY_EXACT; OFFICIAL_TABLE_UNWIRED; NO_EXTERNAL_CALL`.

## Phase 438 — latest authoritative update

The next independent HTML consumer was consolidated: the Rave gallery is
generated from `docs/cultura/ensayos/rave/iconos/*.svg` and
`docs/cultura/ensayos/rave/iconos.json` by the shared owner
`tools/iconos_conjunto.py`. The gallery output is
`docs/cultura/ensayos/rave/galeria.html`; it is not hand-edited. The existing
guide had stale references to local `herramientas/`, `datos/` and
`exportar_png.py` copies, so `docs/cultura/ensayos/rave/GUIA-DE-EDICION.md`
was corrected to the shared builder and current paths. No SVG, manifest,
essay, generated HTML or historical evidence was deleted or changed.

Foreground evidence:

- `python3 -m py_compile tools/iconos_conjunto.py` exited 0.
- `python3 tools/iconos_conjunto.py validar --raiz docs/cultura/ensayos/rave`
  exited 0: 16 files, 0 errors, 0 warnings.
- `python3 tools/iconos_conjunto.py construir --raiz docs/cultura/ensayos/rave --titulo "EL INFORME RAVE"`
  exited 0: 16 icons, 60.2 KB.
- Focused assertions exited 0: 16 manifest files, 16 essay anchors, 16 HTML
  cards, workshop marker and `../../lib` dependency all present.
- The generated HTML hash was unchanged before and after the rebuild:
  `ab80931ca879e5c9328ff78afc823f3b21b9d05446ec2a54eb1d5a0cc4a0154c`.
- Pytest remains unavailable and was not installed; no package or service was
  started.

Evidence: `context/PHASE438_RAVE_GALLERY_HTML_OWNER_GATE.md`.

Disposition: `RAVE_GALLERY_OWNER_CONFIRMED; SHARED_BUILDER_GREEN; GUIDE_DRIFT_REPAIRED; NO_EVIDENCE_DELETED`.

## Phase 439 — latest authoritative update

The next independent HTML consumer was traced: `tools/sala3d/template.html` is
compiled by `tools/sala3d/build.js` from ten curated SVGs under
`projects/tapiz/piezas_curadas/` plus the demo input
`tools/dist/system_status.json`. Static ownership passed: `node --check` on
the builder exited 0, the compete-engine help entrypoint exited 0, and
focused assertions found all ten artwork paths, valid SVG XML and all thirteen
template tokens exactly once.

The documented demo prerequisite was run in foreground:
`python3 tools/compete_engine.py --demo` exited 0 and wrote the explicitly
classified demo projection `tools/dist/system_status.json`. A bounded build
attempt, `timeout --signal=TERM 20s node tools/sala3d/build.js`, exited 124
because the first-run external dependency fetch did not finish. It cached
`tools/sala3d/.cache/three.min.js`, did not cache `CSS3DRenderer.mjs`, and did
not produce `tools/dist/sala3d.html`. The temporary Node process was stopped;
no process remained. No source or historical evidence was deleted or edited.

Evidence: `context/PHASE439_SALA3D_HTML_BUILD_GATE.md`.

Disposition: `SALA3D_OWNER_STATIC_GREEN; DEMO_INPUT_GENERATED; EXTERNAL_ASSET_FETCH_GATED; ARTIFACT_NOT_BUILT`.

## Phase 440 — latest authoritative update

The generated RD quotation surface was classified as a protected product
family, not merged blindly with the portfolio or venue HTML. The light and
dark products under `datadrops/cotizacion_general_eventos/` are intentionally
different hashes and remain separate. The dark HTML has six exact physical
projections across canonical, deploy, worktree and WIN/evidence surfaces; the
canonical dark file compares equal to the `flujo-deploy`, `vibecodeine` and
`actions-runner` projections. The paired dark PDF, Markdown brief, SVG plan
and rider remain part of the handoff package.

Foreground evidence:

- `HTMLParser` exited 0 for both HTML products: one `html`/`body` root each,
  zero script tags.
- Static marker/URL scan exited 0: RD title, pricing, plan and service
  markers are present; only SVG/XML namespace URLs occur, with no external
  asset dependency.
- `cmp` exited 0 for each canonical dark HTML projection checked.
- `pdftotext` exited 0 and found the RD title, services and `$500.000`
  package in the PDF.
- No browser, service, POST, database write or external provider ran; no file
  was edited, moved or deleted.

Evidence: `context/PHASE440_RD_QUOTE_HTML_PROTECTED_OUTPUT_GATE.md`.

Disposition: `RD_QUOTE_PRODUCTS_VALID; DARK_PROJECTIONS_EXACT; LIGHT_DARK_VARIANTS_PRESERVED; NO_SOURCE_REWRITE`.

## Phase 441 — latest authoritative update

The venue/portfolio HTML bridge was rechecked against the current physical
MAK state. `tools/venue.py sitio` owns `web/venues/index.html` from
`data/venues/*.json`; the SCD registry record is consumed separately by
`iskvw/piel/venue/index.html`, whose `?venue=<id>` route and
`iskvw/datos/tablero.json` `mejoras.venue3d` switch are active. The bridge is
the shared technical venue JSON, not a merge of the technical venue registry
with the RD `knowledge/venues` or `data/rd.db` surfaces.

Foreground evidence:

- `PYTHONDONTWRITEBYTECODE=1 python3 -m py_compile tools/venue.py` exited 0.
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/venue.py validar` exited 0:
  3 venues, 0 errors, 0 warnings.
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/venue.py geometria` exited 0:
  SCD has 56 polylines, 503 edges and 0 zero-length segments.
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/venue.py sitio` exited 0:
  3 rooms, 27 KB; the generated hash stayed
  `f8604f03828727b826975a9ea49899449a3ec42c43b98be556f84728e5af5145`.
- Focused assertions exited 0: SCD present, `openklub` and `paralelo_89`
  absent from the technical catalogue, search present, portfolio route and
  fallback present, and `venue3d=true` active.
- Portfolio venue JavaScript parsed with `new Function` (exit 0, one script);
  its deploy projection compares equal.
- No source, JSON, HTML or historical evidence was edited, moved or deleted.

Evidence: `context/PHASE441_VENUE_PORTFOLIO_CROSS_DOMAIN_GATE.md`.

Disposition: `VENUE_CATALOGUE_GREEN; PORTFOLIO_VENUE_BRIDGE_GREEN; SCD_ROLE_SEPARATED; RD_DB_NOT_MERGED`.

## Phase 442 — latest authoritative update

The laser toolchain was traced and validated as a VJ/technical slice. The
human-facing owner is `docs/laser/toolkit.html`, routed by
`docs/laser/TOOLKIT_INDICE.md`; the stale `laser-toolkit.html` reference in
the index was corrected to the real path. The runtime owner is
`src/flujo/laser.py`, registered under `python3 -m flujo laser` in
`src/flujo/cli.py`, with the portfolio archive join in
`cultura/mak_plataforma/contrato_archivo.py`.

Foreground evidence:

- `PYTHONDONTWRITEBYTECODE=1 python3 -m py_compile src/flujo/laser.py src/flujo/cli.py`
  exited 0.
- `PYTHONPATH=src python3 -m flujo laser --help` exited 0 and exposed
  `estado`, `hatched`, `flow`, `lote`, `medir` and `ild`.
- A focused pure-Python temporary-directory check exited 0: SVG point budget,
  ILDA Type 5 RGB output, BGR byte order, blanking/dwell, read-back and
  deterministic bytes all passed.
- Optional probe returned `vpype=false`, `hatched=false`, `flow=false`.
  This gates image-to-vector modes only; direct measurement and native ILDA
  export remain available. No package was installed and no real media folder
  was processed.
- No laser HTML, SVG, ILDA, database or historical evidence was deleted or
  rewritten.

Evidence: `context/PHASE442_LASER_TOOLCHAIN_OWNER_GATE.md`.

Disposition: `LASER_ILDA_NATIVE_ROUTE_GREEN; CLI_OWNER_CONFIRMED; VPIPE_OPTIONAL_UNAVAILABLE; NO_REAL_MEDIA_MUTATION`.

## Phase 443 — latest authoritative update

The native RD Plano/Rider backend was validated without conflating it with the
unresolved Vite HTML projections. The owner chain is
`projects/plano/ejemplos/evento_ejemplo.json` -> `src/flujo/plano/engine.py`
and package exports -> `src/flujo/cli.py` (`python3 -m flujo plano`). The
icons, packs and costs modules remain part of the same backend contract. The
QA document had Windows-first `py -m` commands, so
`docs/QA_EVENTOS_SUPLEMENTOS.md` was aligned to MAK's
`PYTHONPATH=src python3 -m flujo` invocation. No engine, fixture, generated
product or HTML bundle was changed.

Foreground evidence:

- `PYTHONDONTWRITEBYTECODE=1 python3 -m py_compile src/flujo/plano/engine.py src/flujo/cli.py`
  exited 0.
- Real-fixture `--validate`, `--validate --rider`, `--validate --costs` and
  `--validate --output /tmp/mak-plano-check-moq9Pw/plano.svg` all exited 0.
- Focused assertions exited 0: SVG XML parsed; Rider contained feeding,
  testeo and low-stimulation containment; costs contained TOTAL; fixture kept
  `grid_2x`.
- Temporary outputs stayed outside MAK runtime/delivery paths.

Evidence: `context/PHASE443_PLANO_RIDER_NATIVE_CONTRACT_GATE.md`.

Disposition: `PLANO_RIDER_NATIVE_GREEN; CLI_FIXTURE_GREEN; QA_COMMANDS_MAK_ALIGNED; VITE_PROJECTION_SEPARATE`.

## Phase 444 — latest authoritative update

The portfolio proposal family under `iskvw/propuestas/` was classified and
validated. Its index embeds four model-produced candidate skins and is backed
by `iskvw/PROMPT_ESTETICA.md`; it is not the active `iskvw/editor.html` skin
and must not be fused into the live portfolio based on self-scores. All five
canonical HTML files compare exactly with their `flujo-deploy` and
`vibecodeine` projections. No candidate, deployment projection or WIN copy was
edited, moved or deleted.

Foreground evidence:

- HTMLParser exited 0 over the index and four candidates; all four links
  resolve and no external HTML navigation dependency is present.
- Node `new Function` syntax checks exited 0 for all four inline scripts.
- Static assertions exited 0: four candidates, five explicit
  `datos falsos 0/3` markers and `PROMPT_ESTETICA.md` present.
- `cmp` exited 0 for every canonical file against both deploy projections.

Evidence: `context/PHASE444_PORTFOLIO_PROPOSALS_OWNER_GATE.md`.

Disposition: `PORTFOLIO_PROPOSAL_FAMILY_VALID; CANDIDATES_GROUPED; ACTIVE_SKIN_SEPARATED; PROJECTIONS_EXACT`.

## Next concrete action

Continue the HTML owner audit on the next independent active consumer, starting
from `/home/mak/*` and keeping `/home/mak/flujo` as the authoring owner.
Keep the `tools/sala3d` external asset-fetch gate open and return to the next
unresolved RD HTML projection, verifying its source/build owner and current
physical state without promoting candidate portfolio skins or overwriting
generated bundles. Preserve the venue and laser data boundaries.
Keep quotation artifacts separate from the venue registry and Plano/Rider
projection. Do not install pytest, manually edit bundles or copy historical
trees. Keep the FRVR role-aware projection, official reaction table, privacy
database, Node/Vite repair, Portfolio publication, external research
providers and Git separate.

## Phase 445 — latest authoritative update

The next unresolved RD HTML projection was checked from the physical MAK
surface. The standalone RD owner chain is `web/rd.html` ->
`web/vite.rd.config.ts` -> `web/src/mainRd.tsx` -> the four RD panels and
`web/src/data/rdDbEmbebida.json` -> `web/dist-rd/rd.html` ->
`scripts/copy-rd-share.mjs` -> `dist_compartir/herramientas_rd.html`. The
separate `outDir` and entry preserve the boundary with the main hub and the
Plano bundle. `mainRd.tsx` has 9 imports, 0 missing relative paths and no
actual `App.tsx` import; the `App.tsx` mention is explanatory text only.

Foreground evidence:

- Static import/owner check exited 0; all four panel files and the embedded
  data source exist.
- `node --check web/scripts/copy-rd-share.mjs` exited 0.
- `cmp -s web/dist-rd/rd.html dist_compartir/herramientas_rd.html` exited 0.
- Both generated HTML files are 467466 bytes, contain two inline script tags
  and no external script URLs.
- The current source data contains `Sala Metronomo`, excludes `paralelo_89`
  and keeps OpenKlub as a producer projection. The protected generated bundle
  still contains stale `paralelo_89` and old OpenKlub markers, lacks `Sala
  Metronomo`, and has SHA-256
  `11eb4eab551129f779caba4734d66736312c270cb700b96e803ad9f5c72fa175` in
  both canonical/share locations.
- Node is `v18.20.4`. `npm run build:rd` was intentionally not run because
  the config has `emptyOutDir: true`; Phase 432 already documented the Node 20+
  / Rollup binary gate. No bundle, source, data, or historical evidence was
  edited, moved or deleted.

Evidence: `context/PHASE445_RD_VITE_BUNDLE_CURRENT_PARITY_GATE.md`.

Disposition: `RD_SOURCE_OWNER_GREEN; RD_ENTRY_BOUNDARY_GREEN; RD_SHARE_COPY_EXACT; RD_GENERATED_BUNDLE_STALE_PENDING_RUNTIME_REPAIR`.

## Next concrete action

Continue the HTML owner audit on the next independent active consumer, starting
from `/home/mak/*` and keeping `/home/mak/flujo` as the authoring owner. Keep
the `tools/sala3d` external asset-fetch gate open. Leave the RD standalone
bundle parity gate pending until an authorized compatible Node/Vite runtime is
available; do not install packages, run `npm run build:rd`, manually edit
bundles or copy historical trees. Preserve venue, laser, quotation and
Plano/Rider boundaries. Keep the FRVR role-aware projection, official reaction
table, privacy database, Portfolio publication, external research providers
and Git separate.

## Phase 446 — latest authoritative update

The next independent active HTML consumer was the ISKVW Campo skin at
`iskvw/piel/campo/index.html`. Its owner chain is the skin plus
`iskvw/datos/archivo.json`, `campo.json`, `obras.json` and `tablero.json`.
The skin uses `archivo.json` first, then the two local fallbacks, and reads the
tablero once. `mejoras.venue3d === true` conditionally creates the logical
`../venue/` link; it does not merge venue data with RD or copy records between
domains.

Foreground evidence:

- Inline JavaScript syntax check with Node `new Function` exited 0.
- HTMLParser exited 0: 19 tags, one inline script and zero external script
  sources.
- All four JSON data sources parsed successfully.
- `cmp` against `flujo-deploy/iskvw/piel/campo/index.html` exited 0. Both are
  75813 bytes with SHA-256
  `2e7548a3e7355716b7b151981287b73662299bb8666929bb8664959b4051d807`.
- `tablero.json` declares `mejoras.venue3d=true`; the two `http://` literals
  are SVG namespaces only. No server, browser, network request or data write
  ran. WIN/Vibecodeine/quarantine variants remain preserved evidence.

Evidence: `context/PHASE446_ISKVW_CAMPO_HTML_CONTRACT_GATE.md`.

Disposition: `ISKVW_CAMPO_OWNER_GREEN; DATA_FALLBACK_GREEN; VENUE_SWITCH_GREEN; DEPLOY_COPY_EXACT; HISTORICAL_VARIANTS_PRESERVED`.

## Next concrete action

Continue the HTML owner audit from `/home/mak/*` with
`tools/tapiz_renderer.html`, verifying its contract with
`tools/compete_engine.py`, `tools/system_map.py` and the explicitly classified
demo input. Keep `tools/tapiz_three.html` separate because it requires an
external Three.js CDN. Preserve the `tools/sala3d` asset-fetch gate, the RD
bundle runtime gate, venue/laser/quotation/Plano-Rider boundaries, FRVR role
projection, official reaction table, privacy database, Portfolio publication,
external research providers and Git. Do not install packages, start services,
edit generated bundles or copy historical trees.

## Phase 447 — latest authoritative update

The next independent HTML consumer was `tools/tapiz_renderer.html`. Its owner
chain is `tools/compete_engine.py --demo` -> the explicitly classified demo
input `tools/dist/system_status.json`, with `tools/system_map.py` as the schema
validator. The renderer consumes all four contract sections, supports a local
file-picker fallback, polls the sigil every 30 seconds and decodes payloads
only on interaction. `tapiz_three.html` remains separate because it requires
an external Three.js CDN.

Foreground evidence:

- `py_compile` of `system_map.py` and `compete_engine.py` exited 0.
- `system_map.py validate tools/dist/system_status.json` exited 0 for all
  contract sections.
- `compete_engine.py --help` exited 0; `--live` was not run.
- Node `new Function` parsed the single inline renderer script with exit 0.
- Independent assertions decoded both Base64+Shift42 payloads (`Psicosis`,
  `Fungi`) to non-empty UTF-8 text and confirmed required fields.
- The renderer is 12662 bytes, has 51 HTML tags, one inline script and zero
  external script sources. `cmp` against `flujo-deploy` exited 0; SHA-256 is
  `0845bbd13489ead7fdb8e81ee01dabe7adca8638af22a8603b8a4b8036028602`.
- No server, CDN request, live telemetry, database write, source edit or
  historical evidence mutation occurred.

Evidence: `context/PHASE447_TAPIZ_RENDERER_CONTRACT_GATE.md`.

Disposition: `TAPIZ_RENDERER_OWNER_GREEN; SYSTEM_SCHEMA_GREEN; PAYLOAD_DECODER_GREEN; DEMO_INPUT_VALID; DEPLOY_COPY_EXACT; THREE_CDN_SEPARATE`.

## Next concrete action

Continue the HTML owner audit from `/home/mak/*` with the next independent
tool/skin. Treat `tools/tapiz_three.html` only as a static external-dependency
gate: verify its import map, local data fallback and JavaScript syntax without
requesting the CDN. Then continue the remaining culture surfaces. Preserve the
RD Node/Vite bundle gate, Sala3D fetch gate, venue/laser/quotation/Plano-Rider
boundaries, FRVR role projection, official reaction table, privacy database,
Portfolio publication, external research providers and Git. Do not install
packages, start services, edit generated bundles or copy historical trees.

## Phase 448 — latest authoritative update

The Tapiz 3D variant `tools/tapiz_three.html` was checked as a separate static
external-dependency gate. Its input is the same explicitly classified demo
`tools/dist/system_status.json`, but its import map requires Three.js
`0.160.0` from unpkg. The HTML also contains a local JSON file-picker fallback
for `file://`; it is not merged into the dependency-free local renderer.

Foreground evidence:

- Node `SourceTextModule` parsed the 10827-byte inline module with exit 0;
  the import was not executed.
- HTMLParser and import-map/input assertions exited 0: 37 tags, one import
  map, one module script, expected `dist/system_status.json` and local `.json`
  picker.
- The import map points exactly to
  `https://unpkg.com/three@0.160.0/build/three.module.js`; no CDN request or
  browser was run.
- `cmp` against `flujo-deploy/tools/tapiz_three.html` exited 0. Both files
  are 16353 bytes with SHA-256
  `00c80dc35c014cd41ea15bd26a8e8ab3f7a2268f62c411e70a94ddd80c5006e9`.
- No source, HTML, JSON, deployment projection or historical evidence was
  edited; no server or background process remains.

Evidence: `context/PHASE448_TAPIZ_THREE_EXTERNAL_GATE.md`.

Disposition: `TAPIZ_THREE_OWNER_GREEN; MODULE_SYNTAX_GREEN; LOCAL_FILE_FALLBACK_GREEN; EXTERNAL_CDN_GATED; DEPLOY_COPY_EXACT`.

## Next concrete action

Continue the HTML owner audit from `/home/mak/*` with the next independent
cultural/visual surface, starting with `cultura/blend-math-lab.html` or
`projects/tapiz/vibecode_spaces.html`. Keep the Three.js CDN gate explicit and
separate from the local Tapiz renderer. Preserve the RD Node/Vite bundle gate,
Sala3D fetch gate, venue/laser/quotation/Plano-Rider boundaries, FRVR role
projection, official reaction table, privacy database, Portfolio publication,
external research providers and Git. Do not install packages, start services,
request CDN assets, edit generated bundles or copy historical trees.

## Phase 449 — latest authoritative update

The next cultural/visual HTML surface was `cultura/blend-math-lab.html`. It is
self-contained: Canvas 2D, inline blend formulas, synthetic sources,
histograms, algebraic property probes and local pointer interaction. It does
not consume RD/portfolio data, APIs, databases, packages or external assets,
so it remains separate from Tapiz, Venue, RD and Plano/Rider.

Foreground evidence:

- Node extracted the actual `const modes` block and evaluated all 15 modes on
  a 33x33 grid; every output stayed in `[0,1]` and the command exited 0.
- The property probe correctly reported non-monotonic behavior for
  `difference`, `exclusion` and `subtract`; those are expected formula
  properties, not suppressed failures.
- HTMLParser/static dependency assertions exited 0: 18874 bytes, 72 tags,
  one inline script, zero external sources, `fetch`, WebSocket, localStorage
  or HTTP(S) URLs.
- `cmp` against `flujo-deploy/cultura/blend-math-lab.html` exited 0. SHA-256:
  `696ea38d3725f1857e12830ce0824903174dab2dfb4246129e2ebbc73c804a16`.
- No browser, server, data write, source edit or historical evidence mutation
  occurred.

Evidence: `context/PHASE449_BLEND_MATH_LAB_CONTRACT_GATE.md`.

Disposition: `BLEND_MATH_OWNER_GREEN; FORMULA_RANGE_GREEN; PROPERTY_REPORT_HONEST; SELF_CONTAINED_GREEN; DEPLOY_COPY_EXACT`.

## Next concrete action

Continue the HTML owner audit from `/home/mak/*` with
`projects/tapiz/vibecode_spaces.html`, checking its WebGL/CSS3D dependencies,
local assets, runtime contract and deploy parity. Keep visual laboratories
separate from the active portfolio skin and from RD, Venue, Plano/Rider,
Sala3D, the Node/Vite bundle gate and the external research/provider surfaces.
Do not install packages, start services, request external assets, edit
generated bundles or copy historical trees.

## Phase 450 — latest authoritative update

The next cultural/visual HTML surface was
`projects/tapiz/vibecode_spaces.html`. Its owner is the local visual tool plus
`projects/flujo/flujo.json`, which supplies the canonical flujo palette. The
tool accepts local source files, visualizes whitespace topology through eight
local modes, and exports a static HTML frame. It links back to the hub but has
no API, database, network or external asset contract.

Foreground evidence:

- Node `new Function` parsed the 11994-byte inline script with exit 0.
- HTMLParser/static assertions exited 0: 19675 bytes, 59 tags, one inline
  script and no external script source, fetch, WebSocket, localStorage or
  HTTP(S) URL.
- `projects/flujo/flujo.json` parsed successfully and declares the exact
  canonical colors used by the tool: `#1f2a24`, `#2d5a4a`, `#f8f1e3`,
  `#675f55`, `#c2410f`.
- `cmp` against `flujo-deploy/projects/tapiz/vibecode_spaces.html` exited 0;
  SHA-256 is
  `fa6b22534036234e3207d74649741e89e0dd2b4cf2d9d3102fd8f8a67da9406e`.
- No browser, file upload, export write, service, source edit or historical
  evidence mutation occurred.

Evidence: `context/PHASE450_VIBECODE_SPACES_HTML_CONTRACT_GATE.md`.

Disposition: `VIBECODE_SPACES_OWNER_GREEN; BRAND_SOURCE_PRESENT; LOCAL_INPUT_GREEN; EXPORT_GUARD_PRESENT; DEPLOY_COPY_EXACT`.

## Next concrete action

Continue the HTML owner audit from `/home/mak/*` with
`cultura/trilogia.3d.blender.html`, checking its local Blender/asset contract,
HTML syntax and deploy parity. Keep it classified as a visual artifact unless
there is a real active consumer; do not start Blender, a server, or external
asset fetches. Preserve all RD, Venue, Plano/Rider, Sala3D, Tapiz renderer,
Node/Vite and historical boundaries. Do not install packages, edit generated
bundles or copy historical trees.

## Phase 451 — latest authoritative update

The next cultural HTML surface was `cultura/trilogia.3d.blender.html`. Despite
the historical Blender suffix, the current file is a self-contained Canvas 2D
piece: 15 blend modes, a 33x33 algebra probe, an address map and iterative
`bump`/`displacement` twin readings. It does not load a `.blend`, start
Blender, consume data, or call external assets. It remains separate from
Blend Math Lab because the two have different visual consumers and contracts.

Foreground evidence:

- Node `new Function` parsed the actual 8636-byte inline script with exit 0.
- Node extracted the actual `M` formulas and evaluated all 15 modes over a
  33x33 grid (16335 evaluations); every output stayed in `[0,1]`.
- HTMLParser/static assertions exited 0: 12673 bytes, 50 tags, one inline
  script, zero external sources, fetch, WebSocket, localStorage, HTTP(S),
  `.blend` or `.gltf` markers.
- `cmp` against `flujo-deploy/cultura/trilogia.3d.blender.html` exited 0;
  SHA-256 is
  `eeda9681fc42847fb09fc754ae3f22e67b8bfa9dcf86a06830adcd749e0ee4a5`.
- No browser, Blender, service, asset fetch, source edit or historical
  evidence mutation occurred.

Evidence: `context/PHASE451_TRILOGIA_BLENDER_HTML_CONTRACT_GATE.md`.

Disposition: `TRILOGIA_OWNER_GREEN; FORMULAS_RANGE_GREEN; CANVAS_SELF_CONTAINED; BLENDER_RUNTIME_NOT_REQUIRED; DEPLOY_COPY_EXACT`.

## Next concrete action

Continue the HTML owner audit from `/home/mak/*` with the remaining uncovered
cultural/portfolio visual surfaces. Do not reopen the already classified
Tapiz Three external gate; instead select the next physical candidate, verify
its owner and consumer, and preserve separate genealogies when they share
formulas but not runtime contracts. Keep RD, Venue, Plano/Rider, Sala3D,
Node/Vite, official reaction table, Portfolio publication, external providers
and historical evidence separate. Do not install packages, start services,
edit generated bundles or copy historical trees.

## Phase 452 — latest authoritative update

The next Tapiz surface was `projects/tapiz/vibecode_void.html`. It was
compared with `vibecode_spaces.html` and classified as a legitimate sibling
skin, not an exact duplicate: Void adds an automatic synthetic-code generator,
a sliding line window and negative/blocks projection; Spaces is the editable
multi-mode tool with protected HTML export. They share local source input and
the flujo palette but have different primary consumers.

Foreground evidence:

- Node `new Function` parsed the 8241-byte inline script and found the
  generator, tokenizer, renderer, FileReader and animation contracts; exit 0.
- HTMLParser/static assertions exited 0: 14463 bytes, 48 tags, one inline
  script, one hub link and zero external sources, fetch, WebSocket,
  localStorage or HTTP(S) URLs.
- All five colors matched `projects/flujo/flujo.json`.
- `cmp` against `flujo-deploy/projects/tapiz/vibecode_void.html` exited 0;
  SHA-256 is
  `855a5994a5152da52216d24c026b9b55785d26d8ea3ee53c8b655aa46e4d935d`.
- No browser, file load, server, export write, source edit or historical
  evidence mutation occurred.

Evidence: `context/PHASE452_TAPIZ_VOID_VARIANT_CONSOLIDATION_GATE.md`.

Disposition: `TAPIZ_VOID_OWNER_GREEN; BRAND_SOURCE_GREEN; LOCAL_INPUT_GREEN; AUTOGENERATOR_LOCAL_ONLY; VARIANT_SEPARATED_BY_CONSUMER; DEPLOY_COPY_EXACT`.

## Next concrete action

Continue the HTML owner audit from `/home/mak/*` with the next uncovered
cultural/portfolio surface. Keep `vibecode_void.html` and
`vibecode_spaces.html` grouped as Tapiz variants without forcing a code merge.
Do not reopen XIO or completed gates; preserve RD, Venue, Plano/Rider, Sala3D,
Node/Vite, official reaction table, Portfolio publication, external providers
and historical evidence. Do not install packages, start services, edit
generated bundles or copy historical trees.

## Phase 453 — latest authoritative update

The next uncovered RD/Cultura surface was
`projects/cultura/identidad/identidad_rd.html`, owned by
`projects/cultura/paleta_reactivos.py` and its committed
`identidad/reactivos.json`. This is an identity/palette artifact, not the
official reaction table, not the Gota runtime and not the RD matcher. The
separation is required because its color/reaction content is explicitly
presumptive and aesthetic.

Foreground evidence:

- `py_compile projects/cultura/paleta_reactivos.py` exited 0.
- A fresh generator run into `/tmp/mak-identidad-check.zaBGlV` exited 0 and
  produced 23 reactions + 6 brand colors.
- `cmp` of fresh JSON and HTML against canonical files exited 0 for both.
- HTMLParser and traceability assertions exited 0: 5675 bytes, 143 tags,
  zero scripts/links, disclaimer present in JSON/HTML, and every swatch hex
  traceable to the generated JSON.
- No official reaction table, Gota endpoint, RD database, provider, browser,
  source or historical evidence was changed.

Evidence: `context/PHASE453_RD_IDENTITY_PALETTE_OWNER_GATE.md`.

Disposition: `RD_IDENTITY_PALETTE_OWNER_GREEN; GENERATOR_DETERMINISTIC_GREEN; DISCLAIMER_GREEN; SWATCH_TRACEABILITY_GREEN; NOT_OFFICIAL_REACTION_TABLE; NOT_GOTA_RUNTIME`.

## Next concrete action

Continue the HTML owner audit from `/home/mak/*` with a non-sensitive visual
surface not yet covered. Keep identity palette, official reaction data, Gota
DEMO, matcher, RD database and portfolio skins separate. Do not reopen XIO or
completed gates; do not install packages, start services, edit generated
bundles or copy historical trees.

## Phase 454 — latest authoritative update

The next uncovered tool surface was `tools/adobe_panel/`. It is a Windows-only
Adobe CEP package, not a Linux MAK runtime: `index.html` dispatches through
`CSInterface.js`/`main.js` to Illustrator, Photoshop and After Effects, while
PowerShell and registry flows handle installation. The panel dispatches 7 JSX
files that all exist in the repository.

Foreground evidence:

- `node --check` passed for `js/main.js` and `js/CSInterface.js` (exit 0).
- HTMLParser/local-reference assertions passed; all three local index
  references exist.
- `config.json` parsed and `CSXS/manifest.xml` parsed successfully.
- All 7 JSX consumer paths listed by `main.js` exist.
- The 10-file panel surface has exact hash parity with
  `flujo-deploy/tools/adobe_panel` (0 missing, 0 different).
- No PowerShell, registry edit, Adobe host, JSX execution, ZXPSignCmd,
  certificate, package, source edit or historical evidence mutation occurred.

Evidence: `context/PHASE454_ADOBE_PANEL_PLATFORM_GATE.md`.

Disposition: `ADOBE_PANEL_SOURCE_INTACT; JS_XML_CONTRACT_GREEN; JSX_CONSUMERS_PRESENT; DEPLOY_COPY_EXACT; WINDOWS_EXTERNAL_CONSUMER; NOT_LINUX_RUNTIME`.

## Next concrete action

Continue the HTML owner audit from `/home/mak/*` with the next local Linux or
non-sensitive visual surface. Keep Adobe CEP classified as external platform
integration, not MAK runtime. Preserve RD, Venue, Plano/Rider, Sala3D, Tapiz,
Node/Vite, official reaction table, Portfolio publication, external providers
and historical evidence. Do not install packages, start services, run Adobe or
PowerShell flows, edit generated bundles or copy historical trees.

## Phase 455 — latest authoritative update

The dashboard HTML audit exposed and repaired a real duplicate owner. The old
`scripts/flujo_daily.py` contained an independent scorer/renderer while
`python -m flujo daily` already used the canonical
`src/flujo/dashboard/{scoring,report}.py`. The old script is now a thin
compatibility adapter that delegates to the canonical CLI, preserving legacy
callers (`scripts/flujo.py daily`, pipeline and shell entrypoints) without a
second implementation.

Foreground evidence:

- `python scripts/flujo_daily.py` exited 0.
- `python scripts/flujo.py daily` exited 0.
- `py_compile scripts/flujo_daily.py` exited 0.
- Canonical `python -m flujo daily --md /tmp/... --html /tmp/...` exited 0.
- All routes produced 19 items: 10 alta, 7 media, 2 baja.
- `context/DAILY.md` and `context/dashboard.html` were regenerated by the
  canonical owner; the dashboard contains 19 items and is 8912 bytes.
- Focused pytest was attempted but exited 1 because
  `/home/mak/venvs/flujo/bin/python` reports `No module named pytest`; no
  package was installed. Direct foreground smoke checks passed.
- No job, flyer, piece, RD database, external provider, service, historical
  evidence or unrelated HTML surface was changed.

Files changed by this phase: `scripts/flujo_daily.py`,
`context/DAILY.md`, `context/dashboard.html`.

Evidence: `context/PHASE455_DASHBOARD_OWNER_CONSOLIDATION.md`.

Disposition: `DASHBOARD_CANONICAL_OWNER_UNIFIED; LEGACY_ENTRYPOINT_COMPATIBLE; OUTPUT_REGENERATED; FOREGROUND_SMOKE_GREEN; PYTEST_RUNNER_UNAVAILABLE`.

## Next concrete action

Continue the HTML owner audit from `/home/mak/*` with the next uncovered local
or non-sensitive surface. Preserve the single dashboard owner and leave the
pytest environment gate documented. Do not reopen XIO or completed phases;
preserve RD, Venue, Plano/Rider, Sala3D, Tapiz, Adobe CEP, Node/Vite, official
reaction table, Portfolio publication, external providers and historical
evidence. Do not install packages, start services, edit generated bundles or
copy historical trees.

Last verified: 2026-08-15 America/Santiago — Phase 455 dashboard owner
consolidation recorded; no running MAK service observed.

## Phase 456 — latest authoritative update

The next recovered HTML cluster was audited from the physical MAK surface:
`docs/recovered/claude_sessions_2026-08-12/raw/{AX.html,sinreferencia.html,organismo.html}`.
The three artifacts are preserved portfolio/creative evidence, not a new
active runtime owner. Existing portfolio dossiers identify `organismo.html`
as a reference of experience and artist position, while no active consumer
was found for `AX.html` or `sinreferencia.html`.

Foreground evidence:

- Candidate-specific HTMLParser assertions exited 0 for all three artifacts:
  local markers present, one inline script each and zero external asset refs.
- `AX.html` validated at 25,510 bytes / 49 tags; its local Canvas analysis,
  object URL image loading and CSV export markers are present.
- `sinreferencia.html` validated at 16,607 bytes / 91 tags; its Canvas scenes
  and local interaction markers are present.
- `organismo.html` validated at 15,963 bytes / 173 tags; its local SVG
  construction markers are present.
- `cmp` canonical against `flujo-deploy` and `WIN` exited 0 for all three;
  their SHA-256 values are recorded in
  `context/PHASE456_RECOVERED_PORTFOLIO_HTML_GATE.md`.
- The process scan found no running `flujo`, `uvicorn`, Vite or serving Node
  process.

No source, generated bundle, active portfolio skin, database, provider,
service or historical evidence was changed. No promotion, deletion or tree
copy was performed.

Files added: `context/PHASE456_RECOVERED_PORTFOLIO_HTML_GATE.md`.

Disposition:
`RECOVERED_PORTFOLIO_REFERENCE_ONLY; NO_ACTIVE_CONSUMER_FOR_AX_OR_SINREFERENCIA;
ORGANISMO_REFERENCE_OWNER_DOCUMENTED; HISTORICAL_AND_DEPLOY_COPIES_EXACT`.

## Next concrete action

Audit the next recovered HTML cluster from `/home/mak/*`, beginning with
`/home/mak/flujo/docs/recovered/claude_sessions_2026-08-12/raw/rd_fichas_entidades_2026-08-11.html`
and
`/home/mak/flujo/docs/recovered/claude_sessions_2026-08-12/raw/rd_matriz_interactiva_2026-08-11.html`.
First locate active owners and consumers across `/home/mak/*`; then compare
canonical/deploy/WIN parity and run bounded static checks. Keep recovered
portfolio evidence separate from active RD/Portfolio consumers. Do not reopen
XIO or completed gates; do not install packages, start services, edit
generated bundles or copy historical trees.

Last verified: 2026-08-15 America/Santiago — Phase 456 recovered portfolio
HTML evidence gate recorded; no running MAK service observed.

## Phase 457 — latest authoritative update

The next recovered RD HTML cluster was audited:
`docs/recovered/claude_sessions_2026-08-12/raw/rd_fichas_entidades_2026-08-11.html`
and
`docs/recovered/claude_sessions_2026-08-12/raw/rd_matriz_interactiva_2026-08-11.html`.
They are derived sibling views over the RD entity/graph/source contract, not
duplicate owners and not a second database. The profile builder exists only
in the recovered evidence surface; the matrix has a copy under
`docs/rd/prototypes/2026-08-11/`, whose README explicitly says it is
non-operational and not mounted by `/api/rd-db`, `/portafolio/` or standalone
Plano/Rider builds.

Foreground evidence:

- `rd_fichas_entidades_build.py` exited 0 with 48 profiles, 40 connected and
  8 unconnected.
- `rd_matriz_interactiva_build.py` exited 0 with 48 entities and 52
  relations.
- Both builders ran against an isolated temporary set of bounded input files;
  generated JSON/HTML outputs matched canonical recovered outputs with
  `cmp` exit 0.
- HTML structure/data assertions exited 0 for both views: one inline script,
  expected embedded data markers and zero external asset refs.
- Extracted JavaScript passed `node --check` with exit 0 for both views.
- Canonical/deploy HTML copies are exact. WIN copies are exact with their
  historical state but stale relative to canonical: canonical/deploy SHA is
  `dd78b402...` for profiles versus WIN `0533f2d2...`, and `4a7929e1...` for
  matrix versus WIN `19655752...`.
- Registry, graph and normalized reagent inputs are exact across surfaces;
  canonical/deploy catalog and integration-index inputs differ from WIN,
  explaining the derived-view divergence.
- A preliminary symlink probe resolved the builders' output root back to the
  canonical recovered directory and rewrote the two generated files with
  identical bytes; their SHA-256 values stayed unchanged. The final builder
  run used real bounded temporary copies and did not write the repo.

No active RD route, database, portfolio skin, provider, service or production
bundle had content changed. The only intentional repository addition is the
phase report; no promotion, deletion or tree copy was performed.

Files added: `context/PHASE457_RD_GRAPH_PROTOTYPES_GATE.md`.

Disposition:
`RD_GRAPH_SOURCE_INPUTS_GREEN; RD_PROFILE_VIEW_DETERMINISTIC_GREEN;
RD_RELATION_MATRIX_DETERMINISTIC_GREEN; NON_OPERATIONAL_PROTOTYPE;
NO_ACTIVE_CONSUMER; WIN_PROJECTION_STALE_BY_PROVENANCE`.

## Next concrete action

Audit the next recovered RD HTML cluster from `/home/mak/*`, beginning with
`/home/mak/flujo/docs/recovered/claude_sessions_2026-08-12/raw/rd_post_chemsex_spec_2026-08-11.html`
and
`/home/mak/flujo/docs/recovered/claude_sessions_2026-08-12/raw/rd_post_cover_prototype_2026-08-11.html`.
Locate owners and active consumers before deciding whether either belongs to
the RD POST surface or remains a prototype. Preserve the shared RD graph
inputs and do not promote prototype views, reopen XIO, install packages,
start services, edit generated bundles or copy historical trees.

Last verified: 2026-08-15 America/Santiago — Phase 457 RD graph prototype
owner gate recorded; no running MAK service observed.

## Phase 458 — latest authoritative update

The next recovered RD HTML cluster was traced as one connected POST chain:
`CARRUSEL CHEMSEX RevCO.pdf` -> `rd_post_chemsex_spec_build.py` -> source-
preserving spec JSON/HTML -> `rd_post_chemsex_visual_brief_build.py` -> visual
brief JSON/report. `rd_post_cover_prototype_2026-08-11.html` -> editable SVG is
a separate visual sibling, not a duplicate textual owner.

The active durable boundary is `cultura/mak_post/pipeline.py`, consumed by
`tests/test_mak_post.py` and the registered conductor stage. It validates a
candidate package and keeps `public_gate=human_required`; it does not publish
or turn editorial claims into scientific relations. The prototype README
explicitly keeps these POST files outside `/api/rd-db`, `/portafolio/` and
standalone Plano/Rider builds.

Foreground evidence:

- `rd_post_chemsex_spec_build.py` exited 0: 7 slides, 5 interaction cards,
  0 unlinked relation refs.
- `rd_post_chemsex_visual_brief_build.py` exited 0: 7 briefs.
- Isolated builder outputs matched canonical/prototype outputs with `cmp`
  exit 0 for spec JSON/HTML, visual brief JSON/report and derived files.
- HTMLParser/static assertions passed: one inline script per HTML, expected
  source-preservation/claim-only markers and 0 external asset refs.
- Extracted scripts passed `node --check` with exit 0 for Chemsex spec and
  cover; cover SVG parsed as XML with exit 0 and its local HTML reference
  exists.
- Direct `cultura.mak_post` validation returned `errors=0`,
  `status=candidate`, `public_gate=human_required`.
- Source PDF SHA-256 is
  `32980f6e09df56f0773393868578694263cbfe78c3fc401734680a755ba3dd48`.

No active route, database, provider, source document, production bundle or
historical evidence was changed. No publication, promotion, deletion, POST
request, installation or service was performed. The focused pytest runner
remains unavailable in the venv; direct contract validation passed.

Files added: `context/PHASE458_RD_POST_CHEMSEX_GATE.md`.

Disposition:
`POST_SPEC_SOURCE_PRESERVING_GREEN; POST_VISUAL_BRIEF_DERIVATION_GREEN;
POST_PIPELINE_CANDIDATE_GATE_GREEN; POST_CLAIM_ONLY_BOUNDARY_GREEN;
COVER_SVG_EDITABLE_AND_LOCAL_GREEN; VISUAL_PROTOTYPE_NON_OPERATIONAL;
NO_PUBLICATION_ROUTE`.

## Next concrete action

Audit the next recovered HTML surface from `/home/mak/*`:
`/home/mak/flujo/docs/recovered/claude_sessions_2026-08-12/raw/lasertoolkit.html`.
Locate its active owner and real consumers, distinguish it from the completed
laser toolchain gate, and only then decide whether any small owner
consolidation is required. Preserve the POST candidate/human gate and visual
prototype boundary; do not reopen XIO, install packages, start services, edit
generated bundles or copy historical trees.

Last verified: 2026-08-15 America/Santiago — Phase 458 RD POST Chemsex owner
gate recorded; no running MAK service observed.

## Phase 459 — latest authoritative update

The Git branch restructuring was explicitly authorized and completed without
using Git as a physical inventory shortcut. Existing local and remote refs
were compared against `main`; historical branches were not deleted or
rewritten. `main` remains at clean baseline commit
`032822b61f3d7cb84c7b52ae1ac6330b2a1f7fcb`.

Created eight local topic refs, all at exactly that baseline:

```text
codex/rd/field-review
codex/rd/runtime
codex/rd/assets
codex/flujo/event-bridge
codex/portfolio/web
codex/mak/ownership
codex/tools/consolidation
codex/cleanup/confirmed-junk
```

The active worktree is now `codex/mak/ownership`. It carried the existing
dirty worktree unchanged: 793 modified/untracked status entries remain
unstaged. No reset, stash, commit, merge, push, fetch, deletion or content
reassignment was performed. This gives the current consolidation a named
branch while protecting `main` as the sole baseline.

Evidence: `context/PHASE459_GIT_BRANCH_RESTRUCTURE.md`.

Disposition:
`MAIN_BASELINE_SINGLE; TOPIC_REFS_CREATED_FROM_MAIN;
HISTORICAL_BRANCHES_PRESERVED; ACTIVE_WORKTREE_NAMED;
NO_REMOTE_MUTATION; UNCOMMITTED_SCOPE_REQUIRES_PARTITION`.

## Next concrete action

Partition the 793 entries on `codex/mak/ownership` into an explicit first
consumer-backed write set, beginning with current handoff/context evidence and
MAK ownership manifests. Do not stage or commit the broad worktree as one
block. After the first write set is isolated, create one focused commit,
validate it in the foreground, and only then consider merging directly to
`main`. Preserve all old branch refs and do not create a permanent develop,
staging or release branch.

Last verified: 2026-08-15 America/Santiago — Phase 459 Git branch system
created from main; active worktree on codex/mak/ownership; no remote mutation.

## Phase 460 — latest authoritative update

All ten original local branches were reviewed against `main` commit
`032822b61f3d7cb84c7b52ae1ac6330b2a1f7fcb`.

Disposition:

- `main` remains the only permanent integration baseline.
- `mak`, `ddbase`, `codex/mak-local-authority-reconciliation-20260813` and
  `codex/mak-linux-only` are historical MAK/runtime lines; their future work
  belongs under `codex/mak/ownership` and bounded slices.
- `codex/nudo-rd-evidence` is preserved evidence history; future field review
  belongs under `codex/rd/field-review`.
- The two `codex/mak-web-restructure-*` branches are historical web/CI lines;
  future work is split between `codex/portfolio/web`, `codex/rd/assets` and
  focused validation branches.
- `iskvw` and `rd` are broad merged product branches, not clean permanent
  department bases; future work is split under the new portfolio/RD branches.

Evidence: `context/PHASE460_GIT_TEN_BRANCH_REVIEW.md`.

The new topic refs remain all rooted at `main`; historical refs remain intact.
No merge, deletion, rebase, push, reset or remote mutation occurred. The
active worktree is `codex/mak/ownership`; its 794 pre-existing modified or
untracked entries remain unstaged and outside this review write set.

Disposition:
`TEN_BRANCHES_REVIEWED; HISTORICAL_LINES_CLASSIFIED;
NEW_MAIN_ROOTED_TOPOLOGY_CONFIRMED; OLD_REFS_PRESERVED;
CHECKPOINT_READY_FOR_FOCUSED_COMMIT`.

## Next concrete action

Stage and commit only the bounded branch-system checkpoint
(`PHASE459_GIT_BRANCH_RESTRUCTURE.md`, `PHASE460_GIT_TEN_BRANCH_REVIEW.md`
and the handoff), then partition the remaining dirty worktree by real
consumer. Do not stage the broad 794-entry scope.

Last verified: 2026-08-15 America/Santiago — Phase 460 all-ten-branch review
recorded; active worktree on codex/mak/ownership; no remote mutation.

## Phase 461 — target architecture correction

The proposed post-restructure architecture was compared with the physical
MAK tree. A mass move from the existing `src/flujo/`, `web/`, `iskvw/`,
`cultura/` and `tools/` surfaces into new `apps/` and `domains/` roots would
change imports, entrypoints and deployment contracts without proving a
consumer-backed migration. It is therefore recorded as a staged target, not
executed as a bulk rename or tree copy.

The authoritative mapping, identity/crosswalk boundary, Git boundary and
migration order are in `context/PHASE461_TARGET_ARCHITECTURE.md`.

Files added: `context/PHASE461_TARGET_ARCHITECTURE.md`.

Validation: `find /home/mak/flujo -maxdepth 2 -type d` exited 0 and confirmed
the current canonical surfaces. No runtime, data, deployment artifact or
historical evidence changed. No packages, services, Git refs or broad dirty
worktree entries were touched.

Disposition:
`TARGET_ARCHITECTURE_MAPPED; STAGED_MIGRATION_REQUIRED;
NO_BULK_RENAME; NO_DATABASE_BYTE_MERGE; PORTFOLIO_FIRST_SLICE_SELECTED`.

## Next concrete action

On a clean isolated portfolio worktree, inspect the current catalog boundary:
`iskvw/`, `tools/portfolio/`, `tools/gen_iskvw_prototipo.py`,
`src/flujo/web/hub.py` (`/api/portafolio`) and the related web consumer. Record
the exact source, generator, output and deployment contract, then implement a
focused portfolio catalog boundary only if it preserves the existing
foreground behavior. Do not touch the broad dirty `codex/mak/ownership`
worktree, do not stage the 794-entry scope, and do not move RD or shared hub
files in the portfolio write set.

Last verified: 2026-08-15 America/Santiago — target architecture mapped;
portfolio boundary is the next consumer-backed slice.

## Phase 462 — portfolio catalog boundary gate

The isolated `codex/portfolio/web` worktree was mapped and the portfolio
catalog boundary was implemented. `tools/portfolio/proyectos.json` (10 curated
public projects) and `iskvw/datos/obras.json` (8 visual works consumed by
ISKVW skins) are distinct contracts; neither was merged or overwritten.

Files changed in the isolated write set:

- `tools/portfolio/catalog_contract.py`
- `tools/portfolio/generar_portfolio.py`
- `tests/test_portfolio_gen.py`
- `context/PHASE462_PORTFOLIO_CATALOG_GATE.md`

Foreground evidence: Python compilation exited 0; the generator exited 0 with
10 projects and 25 bounded archive entries in `/tmp`; generated JSON contract
assertions exited 0; a duplicate-id negative probe exited 0 after rejecting
invalid input. `npm run typecheck` exited 127 because `tsc` is absent from the
isolated worktree; no dependency was installed. No API, RD data, visual works,
deployment workflow, generated repository output or WIN evidence changed.

Disposition:
`PORTFOLIO_PROJECT_CATALOG_CONTRACT_GREEN; VISUAL_WORKS_CONTRACT_PRESERVED;
GENERATOR_OUTPUT_GREEN; DUPLICATE_ID_GATE_GREEN; WEB_TYPECHECK_UNAVAILABLE`.

## Next concrete action

Inspect and refactor the isolated `web/src/components/PortafolioPanel.tsx`
consumer against the existing read-only `/api/portafolio` response. Keep
`src/flujo/web/hub.py` outside this write set unless a minimal compatibility
change is proven necessary. Re-run the catalog gate and use the existing web
toolchain if its dependencies become available without installation.

Last verified: 2026-08-15 America/Santiago — portfolio catalog contract gate
passed; web typecheck unavailable due to missing local `tsc`.

## Phase 463 — portfolio panel consumer boundary

In the isolated portfolio write set, `web/src/data/portfolio.ts` now owns the
read-only `/api/portafolio` response contract. `web/src/components/PortafolioPanel.tsx`
is presentation/filtering only; it does not write catalogue data, call POST
routes or import RD data. `src/flujo/web/hub.py` was not changed.

Evidence: the Phase 462 Python catalogue gate was rerun successfully. The new
TypeScript import path exists and the duplicated local catalogue type was
removed from the component. The existing Node smoke suite for public skins
`campo`, `terminal` and `venue` exited 0. `npm run typecheck` remains
unavailable with exit 127 because `web/node_modules/.bin/tsc` and PATH `tsc`
are absent; no package installation was attempted.

Files added/changed in the isolated worktree:

- `web/src/data/portfolio.ts`
- `web/src/components/PortafolioPanel.tsx`
- `context/PHASE463_PORTFOLIO_PANEL_GATE.md`

Disposition:
`PORTFOLIO_PANEL_CONTRACT_EXTRACTED; API_READ_ONLY_PRESERVED;
PUBLIC_SKINS_SMOKE_GREEN; RD_WRITE_SET_UNTOUCHED; TS_TOOLCHAIN_UNAVAILABLE`.

## Next concrete action

Validate the isolated TypeScript source with any already-present repository
toolchain without installing packages; if unavailable, record that boundary
and run the public `iskvw` artifact/build contract checks. Do not alter
`src/flujo/web/hub.py`, RD files, `iskvw/datos/obras.json` or the broad dirty
MAK worktree from this portfolio write set.

Last verified: 2026-08-15 America/Santiago — portfolio panel contract
extracted; TypeScript toolchain still unavailable.

## Phase 464 — public portfolio artifact gate

The public ISKVW artifact was checked from the isolated portfolio worktree.
`node tools/iskvw_piel_smoke.mjs campo`, `terminal` and `venue` all exited 0;
the public static inputs and trace index were present and non-empty. Python
compilation, the catalogue contract gate and `git diff --check` also exited 0.

The bundled workspace runtime was inspected and contains Node but no TypeScript
compiler. The isolated worktree has no `tsc`, so `npm run typecheck` remains
exit 127. No dependency installation, service startup or generated repository
write was performed.

Evidence: `context/PHASE464_PORTFOLIO_PUBLIC_ARTIFACT_GATE.md`.

Disposition:
`PUBLIC_ISKVW_SKINS_GREEN; STATIC_INPUTS_PRESENT; DIFF_WHITESPACE_GREEN;
TSC_UNAVAILABLE_WITHOUT_INSTALL`.

## Next concrete action

Prepare the isolated portfolio write set for focused review and integration.
Before any merge to `main`, obtain TypeScript verification from an authorized
existing environment or preserve the exact exit-127 limitation in the review
evidence. Do not merge the unreviewed worktree.

Additional verification: the already-present `@babel/parser` parsed both
`web/src/data/portfolio.ts` and `web/src/components/PortafolioPanel.tsx` with
TypeScript/JSX plugins and exited 0. This proves syntax, not type correctness;
the absence of `tsc` remains explicitly recorded.

Last verified: 2026-08-15 America/Santiago — public ISKVW skins green;
TypeScript compiler unavailable without installation.

## Phase 465 — portfolio write-set review and branch naming

The isolated portfolio write set was reviewed. It contains only the catalogue
contract/loader, generator integration, portfolio tests, React consumer loader
and phase evidence. No RD, Hub, WIN, visual-work source or generated deploy
artifact is included. `git diff --check` exited 0 and the branch divergence
from `main` is `0 0` because the work remains uncommitted.

The isolated branch was renamed from `codex/portfolio/web` to the requested
`portfolio/web`. No commit, merge, push or deletion of historical user
branches occurred; the old ref was a local topic ref created during this task
and had no commits of its own.

## Next concrete action

Keep `portfolio/web` as the focused review boundary. TypeScript verification is
still unavailable without installing dependencies; the existing Python and
Node gates are green. Do not merge into `main` until the user-authorized
TypeScript environment exists or the review explicitly accepts the recorded
exit-127 limitation.

Last verified: 2026-08-15 America/Santiago — portfolio write set isolated and
renamed to `portfolio/web`; no commit or merge.

## Phase 466 — no-prefix branch topology

The user-authorized branch naming decision was applied locally. New topic
branches now use the requested names without the `codex/` prefix:

```text
main
mak/ownership
portfolio/web
rd/assets
rd/field-review
rd/runtime
flujo/event-bridge
tools/consolidation
cleanup/confirmed-junk
```

The old first-level historical refs `mak`, `rd`, `iskvw` and `ddbase` blocked
the desired hierarchical names (`mak/*`, `rd/*`, etc.). They were renamed to
`archive/mak`, `archive/rd`, `archive/iskvw` and `archive/ddbase`, preserving
their commit objects and history. The older `codex/*` historical branches
remain intact. The active dirty worktree is now `mak/ownership`; its content
was not changed by the ref rename.

Validation: branch listing and worktree state exited 0; no commit, merge,
rebase, reset, push or content deletion occurred. All new topic refs still
point to the clean `main` baseline, except for the active dirty worktree
which has no new commit.

Disposition:
`NO_CODEX_PREFIX_ACTIVE_TOPOLOGY; HISTORICAL_REFS_ARCHIVED;
CONTENT_UNCHANGED_BY_RENAME; MAIN_PRESERVED`.

## Next concrete action

Keep the new no-prefix topology as the branch system. Review the isolated
`portfolio/web` write set and obtain TypeScript verification through an
authorized existing environment before any merge to `main`. Do not stage the
broad dirty `mak/ownership` worktree.

Last verified: 2026-08-15 America/Santiago — no-prefix topic topology
validated; historical first-level branches archived by ref rename only.

## Phase 467 — integration branch anchor

Created the temporary integration branch `integration/house-restructure` from
`main` at `032822b61f3d7cb84c7b52ae1ac6330b2a1f7fcb`. It is an anchor for the
full remodel, not a second permanent development line. The active checkout
remains the dirty `mak/ownership` worktree; no files were changed, staged or
committed by this operation.

Validation: `git show-ref --verify refs/heads/integration/house-restructure`
exited 0; both `integration/house-restructure` and `main` resolve to
`032822b`. Existing user changes in `mak/ownership` remain untouched.

Disposition:
`INTEGRATION_BRANCH_ANCHORED_FROM_MAIN; MAIN_UNCHANGED;
DIRTY_WORKTREE_PRESERVED; NO_CONTENT_MUTATION`.

## Next concrete action

Keep `integration/house-restructure` as the temporary integration target.
Review the uncommitted `portfolio/web` slice independently, preserving the
TypeScript exit-127 limitation until an authorized compiler is available.
Do not stage or commit the broad `mak/ownership` worktree.

Last verified: 2026-08-15 America/Santiago — integration branch anchored at
the main baseline; no content mutation.

## Phase 468 — RD/portfolio entity crosswalk gate

The physical RD/portfolio boundary was mapped from `/home/mak/*`. Populated
`data/rd.db`, empty operational `data/rd_datos.db`, technical venue JSON and
portfolio work/project JSON are distinct surfaces. A review-only explicit
crosswalk was added at
`context/PHASE468_RD_PORTFOLIO_ENTITY_CROSSWALK.json`, with its gate report in
`context/PHASE468_RD_PORTFOLIO_ENTITY_GATE.md`.

The crosswalk preserves the authoritative role corrections: Espacio Riesco is
a venue candidate, OpenKlub is a producer/brand, FRVR is the DJ/headliner with
producer/venue unresolved, and SCD Plaza Egaña is a technical venue with no
automatic RD join. No `paralelo_89` venue was created.

Foreground validation: read-only SQLite schema/count inspection across MAK,
WIN, premerge, reconciliation and state databases exited 0; JSON source
inspection exited 0. No source database, data JSON, YAML, runtime, service,
portfolio artifact or WIN evidence changed.

Disposition:
`RD_CATALOG_IDENTIFIED; RD_DATOS_EMPTY_OPERATIONAL;
ENTITY_ROLE_CROSSWALK_REVIEW_ONLY; VENUE_PRODUCER_CONFLATION_PROTECTED;
NO_DATABASE_MERGE; NO_AUTOMATIC_ID_JOIN`.

## Next concrete action

Validate the new crosswalk against read-only RD consumers and
`schemas/venue.schema.json`. Then select whether a small identity adapter
belongs in `rd/runtime` or `mak/ownership`. Do not insert database rows or
publish technical venue data before provenance, confidence and publication
status are explicit.

Last verified: 2026-08-15 America/Santiago — RD/portfolio crosswalk recorded;
source databases remain unchanged.

## Phase 469 — decisive branch reduction and portfolio integration

The user authorized a smaller, more decisive branch topology and local
dependency installation. The active branch set is now exactly:

```text
main
integration/house-restructure
mak/ownership
portfolio/web
rd/runtime
```

Fourteen redundant/historical branch refs were removed after their commit
objects were preserved as `archive/branch/*` tags. The detached temporary
worktrees for the old Linux/web branches were clean before detaching. No user
content was deleted; only redundant branch names were removed.

The isolated portfolio slice was committed on `portfolio/web` as
`792d9a7 feat(portfolio): define catalog boundary`, then fast-forwarded into
`integration/house-restructure`. The commit contains the curated project
catalog contract, generator validation, React loader/consumer boundary, tests
and three phase reports. The broad dirty `mak/ownership` worktree was not
staged or committed.

Dependency validation was performed only in `/tmp/mak-portfolio-web/web`.
`npm ci --ignore-scripts --no-audit --no-fund` installed the locked frontend
dependencies. System Node 18 produced the expected Vite engine/native-binding
failure; the existing bundled Node 24.19.0 then ran both:

- `npm run typecheck`: exit 0
- `npm run build`: exit 0; Vite transformed 1,828 modules and produced
  `dist/index.html`

No system runtime, MAK service, RD database or generated production artifact
was changed. The integration worktree is clean at `792d9a7`.

Disposition:
`FIVE_BRANCH_TOPOLOGY; HISTORICAL_REFS_TAGGED;
PORTFOLIO_BOUNDARY_COMMITTED; PORTFOLIO_INTEGRATION_FAST_FORWARD;
TYPECHECK_GREEN; WEB_BUILD_GREEN; MAK_DIRTY_SCOPE_UNTOUCHED`.

## Next concrete action

On `integration/house-restructure`, select the next large vertical slice:
the RD/portfolio entity adapter based on
`context/PHASE468_RD_PORTFOLIO_ENTITY_CROSSWALK.json`. Keep `main` unchanged,
keep `mak/ownership` dirty and uncommitted, and do not create more branches.
Implement only a read-only adapter with explicit provenance, then validate RD
consumers and the venue schema before any database mutation or public
projection.

Last verified: 2026-08-15 America/Santiago — five-branch topology active;
portfolio slice committed and integrated; no RD source mutation.

## Phase 470 — RD/portfolio read-only entity adapter

The next vertical slice was implemented and committed on
`integration/house-restructure` as
`31b283a feat(rd): add read-only entity crosswalk`.

Files in the slice:

- `data/rd_fuentes/candidates/rd_portfolio_entity_crosswalk.json`
- `src/flujo/rd/entity_crosswalk.py`
- `tests/test_entity_crosswalk.py`
- `context/PHASE470_RD_ENTITY_ADAPTER_GATE.md`

Foreground validation:

- `python3 -m py_compile ...`: exit 0.
- Adapter default load and role assertions: exit 0; 4 entities, review-only.
- Duplicate-id negative fixture: exit 0; rejected and preserved.
- `jsonschema` validation of `data/venues/scd-plaza-egana.json`: exit 0.
- An initial sweep over three venue examples exited 1 because
  `santiago-sala-ejemplo.json` and `valparaiso-otro-ejemplo.json` are not in
  the clean integration baseline; this was outside the slice. The check was
  narrowed to the referenced SCD technical venue and passed. No recovery or
  source mutation was needed.

The adapter does not import sqlite3, open a database, write data or publish
technical venue details. `main` and `mak/ownership` remain untouched.

Disposition:
`RD_ENTITY_ADAPTER_GREEN; ROLES_PRESERVED; PROVENANCE_REQUIRED;
SCD_SCHEMA_GREEN; NO_SQLITE_MUTATION; NO_PUBLICATION`.

## Next concrete action

Review the two-commit integration branch as one unit and then partition the
dirty `mak/ownership` scope by real consumer. Do not merge to `main` while its
worktree has unrelated uncommitted changes. Do not create another branch; use
the existing three working lines only.

Last verified: 2026-08-15 America/Santiago — integration branch contains the
portfolio catalog boundary and RD entity adapter; main remains unchanged.

## Phase 471 — MAK runtime consolidation and promotion

The dirty `mak/ownership` surface was partitioned before staging. It contained
798 status entries: 44 operational tracked changes, 746 context/evidence
reports, and a small set of unreviewed auxiliary files. Only the 44 audited
operational files were staged. The context reports, database backup and probe
scripts remain physically present and uncommitted as evidence.

Foreground validation before commit:

- targeted pytest: 63 passed, exit 0;
- Python compilation of changed runtime entrypoints: exit 0;
- frontend TypeScript check: exit 0;
- `git diff --check`: exit 0.

The obsolete `tools/mak_ops/repair_mak_sync.py` was not restored: it was a
historical SSH/Git-reset/cron/mirror mutator. Its stale test was converted to a
negative guard asserting that the mutator is absent. The operational block was
committed on `mak/ownership` as `9b398f1 refactor(mak): consolidate active
runtime owners` (44 files, 364 insertions, 831 deletions). It was merged into
`integration/house-restructure` as `21ae7dd`.

`MAPA.md` was added to the integration branch as a concise current architecture
contract (`9bbec3c`). The combined branch was validated in foreground:

- targeted pytest: 63 passed, exit 0;
- Python compilation: exit 0;
- frontend `npm ci --ignore-scripts --no-audit --no-fund`: exit 0 in `web/`;
- frontend `tsc --noEmit`: exit 0;
- frontend Vite build: exit 0, 1,829 modules transformed.

Promotion: `main` now points to `9bbec3c`, retaining the five-branch topology:
`main`, `integration/house-restructure`, `mak/ownership`, `portfolio/web`,
`rd/runtime`. No historical tag or WIN evidence was deleted. The working tree
of `mak/ownership` still has untracked evidence and four tracked context edits;
these are deliberately outside the functional commit.

Disposition:
`ACTIVE_RUNTIME_CONSOLIDATED; PORTFOLIO_RD_MERGED; MAIN_PROMOTED;
FOREGROUND_GREEN; EVIDENCE_PRESERVED; NO_NEW_BRANCHES`.

## Next concrete action

Run a clean checkout validation from `main` (without importing the dirty
`mak/ownership` worktree), then inspect the remaining untracked evidence for a
small set of authoritative continuity files to commit separately. Do not
stage the 746 historical reports wholesale. After that, audit the five branch
refs for convergence and decide whether domain lanes can be archived as tags;
keep `main` as the only permanent development trunk.

Last verified: 2026-08-15 America/Santiago — `main` promoted to `9bbec3c`;
combined runtime, RD adapter and Portfolio build green.

## Phase 472 — permanent trunk cleanup

The clean detached worktree at `/tmp/mak-house-restructure` was compared
against `main`: both resolve to `9bbec3c`, with no working-tree changes.
Foreground validation from that clean `main` checkout passed:

- targeted pytest: 63 passed, exit 0;
- Python compilation of runtime entrypoints: exit 0;
- frontend TypeScript check: exit 0.

All already-integrated lanes were archived as recoverable tags and their branch
refs removed:

- `archive/integrated/house-restructure-9bbec3c`
- `archive/integrated/portfolio-web-792d9a7`
- `archive/integrated/mak-ownership-9b398f1`
- `archive/integrated/rd-runtime-032822b`

The active branch topology is now deliberately minimal: `main` is the only
permanent trunk. `mak/ownership` remains only because its worktree contains
unreviewed local evidence and context changes; it is not a second development
trunk and must be archived after that evidence is classified. No source,
database, WIN evidence or archive tag was deleted.

Disposition:
`MAIN_CLEAN_CHECKOUT_GREEN; INTEGRATED_LANES_ARCHIVED;
ONE_PERMANENT_TRUNK; LOCAL_EVIDENCE_PRESERVED`.

## Next concrete action

Classify the remaining `mak/ownership` worktree by authoritative continuity
documents versus historical reports. Commit only the small continuity set if
it is demonstrably current; leave the bulk reports and physical DB backup
outside the functional history. Then decide whether `mak/ownership` can be
detached and archived, leaving only `main`.

Last verified: 2026-08-15 America/Santiago — clean `main` at `9bbec3c`, two
branch refs remain (`main`, local evidence lane `mak/ownership`).

## Phase 473 — continuity promoted to main

The six authoritative continuity documents were reviewed individually and
committed on the evidence lane as `f3ecfed docs: preserve MAK operating
continuity`: `agents.md`, `CAPACIDADES.md`, `context/LAST_HANDOFF.md`,
`context/MD_CONTEXT_MASTER.md`, `context/GIT_HISTORY_STRATEGIC_REVIEW.md` and
`projects/cultura/MD_IDEAS_MASTER.md`. The 746 historical phase reports,
disabled workflow, database backup, probe scripts and generated full MAPA copy
were not staged.

That continuity commit was merged into `main` as `3b991e3 docs: integrate MAK
continuity records` and preserved by
`archive/integrated/mak-continuity-f3ecfed`. A clean detached checkout of
`main` resolves exactly to `3b991e3` and has no status changes. Revalidation
passed: targeted pytest 63/63, Python compilation exit 0, TypeScript exit 0.

The remaining `mak/ownership` worktree is still intentionally not archived:
it carries the unreviewed context/evidence surface and must not be force-reset
or cleaned. Its functional commits are already represented in `main` and by
archive tags.

Disposition:
`CONTINUITY_DOCS_PROMOTED; MAIN_3B991E3_GREEN; BULK_EVIDENCE_UNSTAGED;
NO_FORCE_CLEANUP`.

## Next concrete action

Perform the final branch/reference audit and produce the physical-vs-Git
architecture report: confirm `main` is the only permanent trunk, list archive
tags and the remaining evidence lane, and identify any target-tree folders
that are intentionally conceptual rather than safe mass moves. Do not create
another branch or move the active source tree without a consumer-specific gate.

Last verified: 2026-08-15 America/Santiago — `main` at `3b991e3`, clean and
validated; `mak/ownership` retained solely for local evidence continuity.

## Phase 475 — RD database authority recorded

Read-only physical inspection found the actual RD databases under `/home/mak`:
`/home/mak/flujo/data/rd.db` is 2,740,224 bytes with 20 tables and differs by
SHA-256 from both `/home/mak/WIN/flujo/data/rd.db` and
`/home/mak/state/windows-director-20260813/rd/rd.db`, which match each other.
`/home/mak/flujo/data/rd_datos.db` is 20,480 bytes with only four operational
tables. They are not merged or overwritten. The result is documented in
`context/PHASE475_RD_DATABASE_PHYSICAL_AUTHORITY.md` and committed as
`23d5936`, then published to `main` as merge `61a6eea`.

Disposition:
`PHYSICAL_RD_SOURCE_CONFIRMED; WIN_SOURCE_PRESERVED; HASH_DIFFERENCE_RECORDED;
RD_DATOS_NOT_ENRICHED_CATALOG; NO_WRITE_MODE; NO_DESTRUCTIVE_MERGE`.

## Next concrete action

Run one final clean-main validation after Phase 475, audit that all archive
tags resolve and that only `main` is permanent, then stop the restructuring
phase. Any later database reconciliation must be a separately authorized
read-only comparison or an explicitly approved migration slice.

Last verified: 2026-08-15 America/Santiago — `main` promoted to `61a6eea`;
physical RD authority documented without mutation.

## Phase 476 — final closeout validation

Clean detached `main` and the `main` ref both resolve to `6b14492`; the
worktree has zero status entries. Final foreground checks passed:

- targeted pytest: 63 passed, exit 0;
- Python compilation: exit 0;
- TypeScript: exit 0;
- Vite build with bundled Node `v24.19.0`: exit 0, 1,829 modules transformed.

The five-branch proposal has therefore collapsed to one permanent trunk plus
one explicitly retained evidence lane: `main` and `mak/ownership`. Nine
`archive/integrated/*` tags preserve the integrated milestones. `/home/mak/WIN`
is present and remains historical read-only material. No service, cron, SSH,
database writer or destructive cleanup was run.

Disposition:
`RESTRUCTURE_CLOSEOUT_GREEN; MAIN_ONLY_PERMANENT; EVIDENCE_LANE_EXPLICIT;
WIN_PRESERVED; VALIDATION_COMPLETE`.

## Next concrete action

No further restructuring action is required. Any future work starts from
`main` as a bounded consumer-specific slice; database reconciliation or a
physical folder move requires its own authorization and rollback evidence.

Last verified: 2026-08-15 America/Santiago — final closeout at `6b14492`.

## Phase 477 — remote GitHub branch cleanup

The remote was checked explicitly after the user reported seeing ten branches.
`origin` had nine historical heads plus `main`; local branch cleanup had not
removed remote refs. Each historical remote head was first preserved as an
exact `archive/remote/*` tag and those tags were pushed to GitHub. Then local
`main` at `6ccd3f4` was pushed over the old remote `main` at `032822b`.

The nine remote heads were deleted:

- `codex/mak-local-authority-reconciliation-20260813`
- `codex/mak-web-restructure-20260813`
- `codex/mak-web-restructure-20260814`
- `codex/nudo-rd-evidence`
- `codex/three-plane-consolidation`
- `iskvw`
- `mak`
- `mak-svg`
- `rd`

Verification: `git ls-remote --heads origin` now returns only
`refs/heads/main` at `6ccd3f4`; all nine `archive/remote/*` tags resolve on
the remote. No commit object was discarded and no source/WIN material was
modified.

Disposition:
`REMOTE_BRANCHES_COLLAPSED_TO_MAIN; HISTORICAL_HEADS_TAGGED;
REMOTE_VERIFIED; NO_SOURCE_MUTATION`.

## Next concrete action

Resume physical integration from `/home/mak/*`, not Git branch enumeration.
The next candidate is the curatoria projection/runtime boundary: verify the
exact canonical parity and one isolated read-only consumer using the existing
fixture/tests. Do not run the guard, perception loop, cron or external
provider; keep n8n discarded and XIO out of scope.

Last verified: 2026-08-15 America/Santiago — GitHub has one branch, `main`;
remote historical heads are recoverable tags.

## Phase 478 — useful historical code audit

The user asked whether branch cleanup lost useful local progress. The answer is
no for preservation, but yes for current integration: some useful candidates
are only in the archive tags and physical MAK/WIN surfaces. The strongest
confirmed pair is `fondart_corpus.py` plus `source_pipeline.py`: their Git blob
IDs exactly match `/home/mak/research/` and `/home/mak/WIN/flujo/`, while both
are absent from current `main`. They implement source-preserving Fondart
corpus work, explicit URL capture/provenance, and optional Firecrawl/Crawl4AI
backends with a recorded stdlib fallback.

The same archive contains a three-plane manifest, read-only SQLite
reconciliation, inferential archaeology and a guarded transport planner. These
remain candidates, not active runtime. The old portfolio variants and venue
files are not restored because current `main` contains newer user corrections.
The complete audit is in `context/PHASE478_REMOTE_CANDIDATE_AUDIT.md`.

No candidate was deleted or executed against external providers. Remote branch
heads are now tags; GitHub has only `main`.

Disposition:
`REMOTE_HISTORY_SAFE; USEFUL_FONDART_CODE_FOUND;
MAIN_INTEGRATION_STILL_PENDING; NO_EXTERNAL_PROVIDER_CALL`.

## Next concrete action

Run an offline static/import/fixture gate on the physical Fondart/source
pipeline pair using temporary outputs only. If its contracts pass, promote
that bounded research slice to `main`; if not, keep the exact tag and document
the failing dependency. Do not run a live crawl, write research state or
restore the old branch.

Last verified: 2026-08-15 America/Santiago — useful Fondart/source code is
preserved in archive tags and physical MAK/WIN, not yet integrated in `main`.

## Phase 479 — Fondart source pipeline integrated

The offline gate for the physical research pair passed before promotion:

- `/home/mak/research/fondart_corpus.py` and `source_pipeline.py` matched the
  preserved archive blobs exactly;
- WIN offline suite `tests/test_source_pipeline.py`: 23 passed, exit 0;
- local AST parse, import and URL-contract checks: exit 0;
- no network, Firecrawl/Crawl4AI call, research-state write or proposal output.

The bounded slice (two source modules, 23-test suite, candidate audit and this
handoff) was committed as `9681726` and merged/published to `main` as
`33bbe3a feat(research): integrate Fondart source pipeline`. It is now the
canonical source for source-preserving Fondart capture and candidate parsing;
the physical `/home/mak/research` runtime remains unchanged.

Disposition:
`FONDART_PIPELINE_IN_MAIN; PROVENANCE_BOUNDARY_PRESERVED;
OFFLINE_GATE_GREEN; NO_EXTERNAL_CALL; NO_RUNTIME_STATE_MUTATION`.

## Next concrete action

Audit the preserved three-plane knowledge candidates (`three_plane.py`,
`reconciliation.py` and their schemas) against the actual MAK/WIN SQLite files
using read-only temporary fixtures. Do not promote Postgres or create a unified
writer; the gate must prove schema/provenance output before any migration is
considered.

Last verified: 2026-08-15 America/Santiago — `main` at `33bbe3a`; Fondart
source-preserving slice published and validated.

## Phase 480 — three-plane and RD reconciliation integrated

The next useful archive candidate was validated and integrated without a
database writer. The manifest, read-only reconciliation module, two schemas
and two test files now live in `main`. Combined Fondart/reconciliation tests:
40 passed, exit 0. Python compilation and manifest JSON Schema validation both
returned exit 0.

A real foreground read-only comparison of `/home/mak/flujo/data/rd.db` and
`/home/mak/flujo/data/rd_datos.db` produced a temporary
`mak-unified-knowledge-reconciliation-v1` plan with 23 table comparisons,
`migration.writes_performed=false` and 202,731 output bytes. SHA-256 hashes of
both source DBs were unchanged before/after. No Postgres runtime, network
provider, source mutation or public output was invoked. The gate is documented
in `context/PHASE480_KNOWLEDGE_RECONCILIATION_GATE.md`.

The slice was staged only from the preserved candidate code and is ready to
publish as the next `main` checkpoint; `sync_mak_safe.py` remains archived due
to its explicit apply/mutator path.

Disposition:
`THREE_PLANE_INTEGRATED; RD_READ_ONLY_RECONCILIATION_GREEN;
NO_DATABASE_WRITE; POSTGRES_DEFERRED; MUTATOR_DEFERRED`.

## Next concrete action

Gate `tools/inferential_archaeology.py` against temporary evidence fixtures,
without scanning or modifying session stores. Then decide whether it is a
reusable read-only tool or remains archived. Keep `sync_mak_safe.py` out until
its authority boundary is separately proven.

Last verified: 2026-08-15 America/Santiago — three-plane and RD reconciliation
slice validated locally; source databases unchanged.

## Phase 481 — inferential archaeology useful-code gate

The physical candidate /home/mak/WIN/flujo/tools/inferential_archaeology.py and
its focused suite /home/mak/WIN/flujo/tests/test_inferential_archaeology.py
were first run against temporary test fixtures only. The suite passed 27 tests,
exit 0. The source and test files were then added to the active MAK authoring
tree with byte-identical SHA-256 values:

- tools/inferential_archaeology.py:
  806ac9116f27a754cfd547d7047de9abfb1e74bcdd29db3a09dc7f45ebf5d08c
- tests/test_inferential_archaeology.py:
  c21d48d12ddd4449bb5633194dfafcee30c4419d2502306761a9845b4f0737a8

Foreground validation from the active tree:
PYTHONPATH=src:. /home/mak/vibecodeine/.venv/bin/pytest -q
tests/test_inferential_archaeology.py tests/test_source_pipeline.py
tests/test_three_plane_manifest.py tests/test_knowledge_reconciliation.py
returned 67 passed, exit 0. Python compilation of the new tool and the
already-integrated research/knowledge modules returned exit 0.

This is useful local progress: it builds a deterministic evidence index across
Codex/Claude/VS Code/MAK sources, SQLite FTS evidence, and optional relational
events without changing those sources. Its CLI defaults point at real session
roots, so those defaults remain prohibited during integration; future use must
pass explicit reviewed roots and a temporary output directory. No session
store, database, provider, network source, or generated runtime output was
touched.

Disposition:
INFERENTIAL_ARCHAEOLOGY_INTEGRATED_READ_ONLY; OFFLINE_GATE_GREEN;
REAL_SESSION_SCAN_DEFERRED; NO_SOURCE_MUTATION.

## Next concrete action

Stage only the two archaeology files and their Phase 481 evidence, commit the
bounded slice on mak/ownership, merge it into detached main, publish main and
its archive tag, then verify that GitHub still exposes exactly one head and
that all preserved remote tags resolve. Keep sync_mak_safe.py and the
postgres_* candidates archived; they are not required for the local read-only
objective and have unsafe or unproven runtime boundaries.

Last verified: 2026-08-15 America/Santiago — archaeology candidate passed
offline fixtures and active-tree validation; publication remains pending.

## Phase 482 — useful-code preservation and publication verified

The archaeology slice was committed on mak/ownership as ccd8b44, merged into
main as c99b61b, and pushed to origin. The active remote now has exactly one
head:

    c99b61b0d6376cf7092a5edbc9796ca379f4af85 refs/heads/main

The new integrated archive tag
archive/integrated/inferential-archaeology-ccd8b44 resolves on GitHub. The
nine historical remote heads deleted during restructuring still resolve as
archive/remote/* tags. Therefore useful branch work was not discarded as an
unrecoverable ref: integrated useful slices are in main, and the historical
heads remain recoverable tags.

Confirmed useful slices now in main:

1. Fondart source-preserving corpus and source pipeline with offline tests.
2. Three-plane knowledge manifest and read-only RD SQLite reconciliation.
3. Inferential archaeology evidence index with offline fixtures and tests.

Explicitly preserved but not promoted:

1. sync_mak_safe.py, because it exposes an apply/transport mutator path.
2. postgres_* candidates, because the verified MAK authority is SQLite and no
   Postgres writer/runtime was authorized.

Neither exclusion deletes the source. Both remain in WIN and/or archived Git
objects. No runtime database, session store, provider, network source or
historical evidence was modified.

Disposition:
USEFUL_PROGRESS_PRESERVED; THREE_USEFUL_SLICES_IN_MAIN;
REMOTE_HEADS_ONE; HISTORICAL_HEADS_TAGGED; MUTATORS_DEFERRED.

## Next concrete action

Leave Git restructuring closed. Resume the physical MAK-wide integration from
/home/mak/* with one bounded consumer at a time. The next safe candidate is a
read-only physical consumer audit for the remaining research/curatoria
surfaces; do not scan live session roots with archaeology defaults and do not
activate sync_mak_safe.py or postgres_* without a separate authority gate.

Last verified: 2026-08-15 America/Santiago — main c99b61b published; one remote
branch and nine historical remote archive tags verified.

## Phase 483 — single-tag synchronized Git topology

The previous archive-tag set was consolidated into one annotated tag:
archive/house-history -> preservation commit
7a3d27cb5b9084d324c61e25f2716d0295397ba6. That preservation commit has 35
historical parents covering the previous main, local branch and archive-tag
tips. Its tree is byte-identical to main:
6dc1a19f84aa6e2e696b0874d442eb1c817ecfc3.

Before deleting redundant refs, 40 local heads/tags were checked for
reachability from archive/house-history; all passed. The redundant 38 local
tags and 14 remote tags were then removed only after the single preservation
tag had been pushed and verified. Current synchronization:

- local branches: main only;
- remote branches: main only;
- local tags: archive/house-history only;
- remote tags: archive/house-history only;
- main and origin/main before this documentation checkpoint: 229852d.

The active worktree was moved from mak/ownership to main without discarding
the relevant uncommitted evidence. The only path collision was an untracked
MAPA.md with different content from the tracked main MAPA.md. That copy was
confirmed stale and moved to the desktop trash before this checkpoint; it is
not present in the repository or active search surface. The tracked main
MAPA.md remains the sole active map. Other modified and untracked evidence
remains in the worktree and was not cleaned.

Disposition:
SINGLE_TAG_PRESERVATION_GREEN; MAIN_ONLY_LOCAL; MAIN_ONLY_REMOTE;
HISTORY_REACHABILITY_VERIFIED; UNCOMMITTED_EVIDENCE_PRESERVED.

## Next concrete action

Run the focused regression on the active /home/mak/flujo main worktree, push
this handoff checkpoint, and then resume physical MAK integration. Future
development may create one short-lived bounded branch from main, but no branch
or tag is created merely for historical storage.

Last verified: 2026-08-15 America/Santiago — one local/remote main and one
local/remote archive tag; stale MAPA copy removed from the active tree.

## Phase 484 — current preservation point and branch-copy start

The single archive tag was extended after discovering three local stash tips
with MAK/platform/research changes. The current preservation commit is
b9f9a472deaeee6002a96fc8236d75b06bfe24c4 and its tree exactly matches current
main 3e0da4e3f9682ff45fbaf5bb7079fa273d80ea47. It reaches the prior
preservation commit and all three stash tips. The remote still has exactly one
tag, archive/house-history, and one branch, main.

The stale untracked MAPA copy is no longer in the repository or search surface.
The tracked main MAPA.md is the only active map. The three stash refs remain
untouched as local recovery material and are included in the single
preservation point.

The next operation is to create exact, clearly named source copies of the nine
historical non-main branch tips. Each copy must initially resolve to its exact
historical commit; only after that verification may it be triangulated and
updated into the target architecture. These copies are operational inputs, not
new historical tags or unreviewed source-of-truth maps.

Disposition:
STALE_MAP_REMOVED; STASHES_PRESERVED; SINGLE_TAG_EXTENDED;
EXACT_BRANCH_COPIES_PENDING.

## Next concrete action

Create and verify the nine source branch copies from the exact historical tip
commits recorded in Phase 460, publish those refs, and write a current manifest
mapping each source copy to its intended architecture consumer. Do not mutate
any copied branch during the copy gate.

Last verified: 2026-08-15 America/Santiago — tag b9f9a472 and main 3e0da4e
verified; exact source-branch copy gate is next.

## Phase 486 — MAK branch topology consumer slice

The exact source/mak copy was triangulated against the active branch contract.
Its useful branch-state change was isolated into work/mak-ownership rather than
copying the historical branch wholesale:

- main is the only canonical branch;
- source/* is classified as source_copy;
- work/*, integration/*, codex/* and dependabot/* are temporary_work;
- mak, rd, iskvw, mejoras and mak-svg are legacy_transition;
- unknown refs are reported and block autonomy status instead of being silently
  accepted.

The active slice changed only the autonomy branch classifier, its focused tests,
the branch-related workflow guards, the README SVG refresh source string, and
the already-present disabled Claude workflow. No runtime database, WIN source,
provider, SSH call or service was touched. The disabled workflow has manual
dispatch only, no permissions, and an always-false job.

Foreground command:

    PYTHONPATH=src:. /home/mak/vibecodeine/.venv/bin/pytest -q tests/test_autonomia_cli.py tests/test_git_web_contract.py tests/test_readme_svg.py
    python3 -m py_compile src/flujo/autonomia.py tools/update_readme_svg.py

Result: focused validation exit 0; compilation exit 0.

The nine source/* copies remain byte-exact at their historical tips. This
slice updates the first target work branch from current main while preserving
each source copy as a clean triangulation input.

Disposition:
BRANCH_POLICY_CURRENT; SOURCE_COPIES_EXACT; MAK_SLICE_GREEN;
UNKNOWN_REFS_BLOCKED; NO_RUNTIME_MUTATION.

## Next concrete action

Commit and publish the bounded work/mak-ownership slice, merge it into main,
then triangulate source/rd and source/iskvw against their physical consumers.
Do not promote broad historical diffs or stale branch metadata.

Last verified: 2026-08-15 America/Santiago — work/mak-ownership branch
topology slice passes focused tests; publication and main merge are next.

## Phase 487 — branch topology slice published

The bounded topology slice was committed on work/mak-ownership as 5b20e22,
published as origin/work/mak-ownership, merged into main as 8e5f689, and
published as origin/main. The active /home/mak/flujo worktree fast-forwarded
to that same main commit without cleaning its unrelated modified or
untracked evidence.

Post-merge foreground validation:

    PYTHONPATH=src:. /home/mak/vibecodeine/.venv/bin/pytest -q tests/test_autonomia_cli.py tests/test_git_web_contract.py tests/test_readme_svg.py
    python3 -m py_compile src/flujo/autonomia.py tools/update_readme_svg.py

Result: focused validation exit 0; compilation exit 0. The untracked local
claude.yml was byte-identical to the promoted workflow before its duplicate
was moved to trash, so no local content was lost.

Current remote branch classes are now explicit: main is canonical,
source/* are exact source copies, and work/mak-ownership is the first updated
consumer branch. The source copies remain at their original hashes until
their own triangulation gate.

Disposition:
MAK_BRANCH_SLICE_PUBLISHED; MAIN_SYNCED; FOCUSED_GATE_GREEN;
SOURCE_COPIES_UNCHANGED.

## Next concrete action

Triangulate source/rd against /home/mak/* RD consumers and the current RD
database/venue/plano contracts. Select one bounded RD slice, update its work
branch only, validate it in the foreground, and merge only that slice to main.
Do not copy the broad source/rd tree or promote stale metadata.

Last verified: 2026-08-15 America/Santiago — main 8e5f689 and
work/mak-ownership 5b20e22 published; 19 focused tests green.

## Phase 488 — stale active map removed from the current truth surface

The sole active `/home/mak/flujo/MAPA.md` still described the superseded
branch names `integration/house-restructure`, `portfolio/web`, `rd/runtime`
and `mak/ownership`. That was stale operational guidance, not useful history.
The file was updated in place to describe the verified topology: canonical
`main`, exact historical source copies under `source/*`, and temporary
`work/*` delivery branches. No second map was created and no historical
evidence was deleted.

Foreground checks:

    grep -n -E 'integration/house-restructure|portfolio/web|rd/runtime|mak/ownership|main|source/|work/' MAPA.md
    git diff -- MAPA.md

Result: exit 0 for the search; the diff contains only the topology paragraph.
The local and remote refs currently match the intended bounded topology:
`main`, nine `source/*` exact copies, and `work/mak-ownership`. The file
remains uncommitted so it can be committed with the next bounded current-truth
update; the unrelated dirty evidence in the worktree remains untouched.

RD triangulation result retained as a no-merge decision: active
`/home/mak/flujo/data/productoras/frvr.json` is the corrected authority
(artist/DJ headliner, venue Sala Metronomo); `source/rd`, WIN and
`flujo-deploy` contain the older incorrect productora/Paralelo 89 inference.
The active `rd.db` is the current 20-table/7,587-row catalog; `rd_datos.db` is
the separate empty operational/privacy store. The broad `source/rd` diff also
deletes evidence and removes tested consumers, so it is not a merge candidate.

Disposition:
CURRENT_MAP_REPAIRED; NO_STALE_ACTIVE_TOPOLOGY; SOURCE_RD_BROAD_MERGE_REJECTED;
FRVR_ACTIVE_AUTHORITY_PRESERVED; NO_DATABASE_MUTATION.

## Next concrete action

Validate the current RD venue/entity consumers from `/home/mak/*`, then select
one smallest complete read-only slice for the next temporary work branch. It
must use the active JSON/YAML/catalog authority, preserve the corrected FRVR
record, expose a real existing consumer, and have a foreground parse/test
result. Do not promote `source/rd` metadata or create another map.

Last verified: 2026-08-15 America/Santiago — MAPA.md contains only the current
branch topology; active FRVR and RD database hashes recorded above remain
unchanged.

## Phase 489 — standalone RD producer projection unified

Physical triangulation from `/home/mak/*` found a stale duplicate in the active
web consumer: `data/productoras/` contains 20 canonical JSON sources, while
`web/src/data/productoras.ts` manually listed only 15. The standalone
Plano/Rider panel consumed that incomplete list even though the hub projection
already contained 20 and the corrected FRVR record.

The manual list was replaced by a small TypeScript adapter that derives
`RD_PRODUCTORAS` from `web/src/data/rdDbEmbebida.json`. That JSON is generated by
`tools/gen_rd_standalone.py` from the same `flujo.rd.panel.datos_panel`
allowlist used by the hub. `docs/HUB_PERFILES.md` was updated to describe the
20-source projection and `MAPA.md` remains the only current topology map.
No database, source JSON, WIN evidence or runtime service changed.

Foreground validation:

    PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 tools/gen_rd_standalone.py
    npm run typecheck
    PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:. /home/mak/vibecodeine/.venv/bin/pytest -q tests/test_entity_crosswalk.py tests/test_rd_database.py tests/test_rd_db_logos.py tests/test_rd_eventos.py

Results: generator exit 0 and output hash stayed
`9f5e56cbae5cb9ff34bd8433d4b49069e3a52de947f56055d19a37c115b53c04`;
typecheck exit 0; focused RD suite exit 0. The first
`npm run build:plano` and `npm run build:rd` attempts returned exit 127 because
`web/node_modules/.bin/vite` is mode 0644. Direct Node invocation returned
exit 1 because the available system Node is 18.20.4 while Vite requires
20.19+ and the local install lacks `@rollup/rollup-linux-x64-gnu`. This is an
environment dependency gate, not a source failure; no install or node_modules
mutation was performed.

Changed current files: `MAPA.md`, `docs/HUB_PERFILES.md`,
`web/src/data/productoras.ts` and this handoff. Verified no-change projection:
`web/src/data/rdDbEmbebida.json`. The historical `source/rd` branch remains an
exact copy and is not merged; its incorrect FRVR role and destructive broad
diff remain rejected.

Disposition:
RD_STANDALONE_PROJECTION_UNIFIED; TWENTY_PRODUCER_SOURCES_REPRESENTED;
NO_STALE_MANUAL_LIST; FOCUSED_RD_GREEN; WEB_BUILD_ENVIRONMENT_GATE_OPEN;
NO_DATABASE_OR_WIN_MUTATION.

## Next concrete action

Commit and publish this bounded current-truth slice on `main`, verify the
remote topology and exact `source/*` hashes again, then select the next real
consumer from the active MAK surface. Prefer the read-only venue/entity
cross-domain consumer or the portfolio projection; do not merge broad
`source/rd`, do not create another map, and do not install Node/Rollup without
explicit authorization.

Last verified: 2026-08-15 America/Santiago — current RD snapshot has 20
productoras/1 venue, FRVR is represented as artist/DJ with Sala Metronomo, and
the focused source/runtime gates are green except the local web build
environment gate described above.

## Phase 490 — current-truth slice published and source copies rechecked

The four-file Phase 489 slice was committed to `main` as `99bbd88` and pushed
to `origin/main`. The root worktree still contains the user's unrelated
modified and untracked evidence; none was staged or cleaned.

Foreground synchronization checks:

    git fetch origin main --quiet
    test "$(git rev-parse main)" = "$(git rev-parse origin/main)"
    git ls-remote --heads origin
    git ls-remote --tags origin

Results: main/origin/main both resolve to `99bbd88`; the remote has exactly
eleven heads: `main`, nine exact `source/*` copies and the existing
`work/mak-ownership`; the remote has exactly one tag,
`archive/house-history`, whose peeled preservation commit is
`b9f9a472deaeee6002a96fc8236d75b06bfe24c4`. A nine-entry hash gate returned
`EXACT` for every source copy. `work/mak-ownership` is fully represented in
main but remains published because `/tmp/mak-branch-topology` still checks it
out; no forced deletion or worktree removal was attempted.

Disposition:
MAIN_CURRENT_TRUTH_PUBLISHED; SOURCE_COPIES_EXACT_RECONFIRMED;
SINGLE_TAG_RECONFIRMED; WORKTREE_BRANCH_PRESERVED; NO_UNRELATED_EVIDENCE_STAGED.

## Next concrete action

Inspect the active read-only venue/entity consumer from `/home/mak/*` and its
portfolio/RD projection boundary. If a missing connection is proven, update
one temporary bounded work slice with a disjoint write set and foreground
validation; otherwise record a verified no-change result and move to the next
consumer. Keep `source/rd` exact, preserve the FRVR correction, do not create a
new map, and do not run the blocked web build until Node/Rollup is explicitly
repaired.

Last verified: 2026-08-15 America/Santiago — main `99bbd88` published; nine
source copies exact; one remote preservation tag; no stale active topology
references remain in MAPA, HUB_PERFILES or the standalone producer adapter.

## Phase 491 — OpenKlub role corrected without rebuilding away local events

The physical read-only gate showed the active MAK catalog has one canonical
venue (`espacio_riesco`), while the old WIN database still contains the
historical conflations `openklub` and `paralelo_89`. The active source
`data/productoras/openklub.json` still said that OpenKlub might itself be a
venue. That ambiguity was corrected in the source: OpenKlub is a
producer/brand; `Central Cultural` remains only a raw, unconfirmed venue
candidate and is not assigned as OpenKlub's identity.

The active `data/rd.db` was not rebuilt wholesale. A full rebuild with the
correct FLUJO venv would produce the right one-venue catalog but would reduce
the local `eventos` projection from 7 source-linked rows to 2 because local
`jobs/` inputs are intentionally outside the tracked source set. The system
Python was also rejected: its missing PyYAML produced a temporary database with
zero venues. Instead, a single-row, transactional update was applied to
`productoras.slug=openklub`, after creating the recoverable backup
`data/rd.db.pre-openklub-correction-20260815`.

Foreground evidence:

    PYTHONDONTWRITEBYTECODE=1 /home/mak/vibecodeine/.venv/bin/python <one-row SQLite update>
    PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src /home/mak/vibecodeine/.venv/bin/python tools/gen_rd_standalone.py
    PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:. /home/mak/vibecodeine/.venv/bin/pytest -q tests/test_entity_crosswalk.py tests/test_rd_database.py tests/test_rd_db_logos.py tests/test_rd_eventos.py tests/test_venue.py tests/test_venue3d_smoke.py
    PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src /home/mak/vibecodeine/.venv/bin/python tools/venue.py validar

Results: targeted DB update exit 0; source note equals projected row; active
counts remained `venues=1`, `productoras=20`, `productora_venues=8`,
`productora_eventos=7`, `eventos=2`; `rd_datos.db` stayed at SHA-256
`70feaf43b5269b6c0341d1ba3debdac60e40fb902cc4bedb41254fdc84d1f703`; backup
hash equals the pre-update active DB hash
`91b748f5661ed9484da6603d474468622e93846b5935f70446e55f62ba21f32e`; the
new active DB hash is
`e8c5a86c4047cf1c99e8157044c9c3772c068abd3939fcbc7ffd7c312211a337`.
The standalone generator exited 0 with unchanged projection hash
`9f5e56cbae5cb9ff34bd8433d4b49069e3a52de947f56055d19a37c115b53c04` because
the web allowlist does not expose the internal producer note. All focused RD,
venue and SCD smoke tests exited 0; `venue.py validar` reported 3 technical
venues, 0 errors and 0 warnings.

`context/PHASE412_VENUE_CROSSWALK.md` and
`context/PHASE427_VENUE_ROLE_CORRECTION_CROSSWALK.md` were corrected in place
so they no longer present `paralelo_89` as an active venue or OpenKlub as one.
No WIN file, `rd_datos.db`, technical venue JSON, portfolio file, service or
external provider changed.

Disposition:
OPENKLUB_PRODUCER_ROLE_CURRENT; CENTRAL_CULTURAL_REVIEW_ONLY;
ACTIVE_RD_PROJECTION_TARGETED_UPDATE; LOCAL_EVENTS_PRESERVED;
PARALELO89_NOT_ACTIVE; RD_VENUE_AND_SCD_GATES_GREEN.

## Next concrete action

Commit and publish the OpenKlub source correction and current handoff, then
run the next read-only venue/entity consumer gate across `web/venues`,
`iskvw/piel/venue`, the SCD JSON and the review-only crosswalk. Keep the active
RD catalog and VJ technical registry logically linked by explicit IDs and
provenance; do not merge their databases or expose unconfirmed venues in the
portfolio. Preserve the one-file DB backup until the next checkpoint.

Last verified: 2026-08-15 America/Santiago — OpenKlub source and active
projection agree; FRVR remains artist/DJ with raw `Sala Metronomo`; no active
source names `paralelo_89` as a venue.

## Phase 492 — current venue/entity crosswalk and map authority repaired

The active cross-domain review file `data/rd_fuentes/candidates/rd_portfolio_entity_crosswalk.json`
contained two stale references: a nonexistent `knowledge/venues/openklub.yaml`
and an unresolvable free-text evidence token for the FRVR correction. It now
points only to existing sources and labels `espacio_riesco` as the active RD
canonical venue. OpenKlub remains `producer_or_brand`; `Central Cultural` stays
only as a raw `candidate_unconfirmed` claim. FRVR remains
`artist_dj_headliner`, with `Sala Metronomo` raw and no `paralelo_89` venue.

Foreground validation:

    python3 <crosswalk JSON/evidence-path assertion>
    PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:. /home/mak/vibecodeine/.venv/bin/pytest -q tests/test_entity_crosswalk.py tests/test_rd_database.py tests/test_venue.py tests/test_venue3d_smoke.py
    PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src /home/mak/vibecodeine/.venv/bin/python tools/venue.py validar
    /home/mak/vibecodeine/.venv/bin/python <read-only rd.db count/relation query>

Results: JSON and all referenced paths passed with exit 0; focused tests passed
with exit 0; `venue.py validar` passed with exit 0 (`3 venues · 0 errores · 0
avisos`); the active RD database remains `1` canonical venue and `20`
productoras; OpenKlub's only relation remains `Central Cultural`,
`venue_id=NULL`, `candidato_sin_confirmar`. The technical venue registry is a
separate VJ/3D surface and remains at three public records. No database, WIN
file, service, or generated build was changed.

`MAPA.md` now explicitly declares itself the only operational map for this
worktree, points continuity to `LAST_HANDOFF.md`, and warns that `/home/mak/vibecodeine`
and `/home/mak/WIN` maps are not current instructions. Ignored `web/dist*` and
`dist_compartir/` artifacts may retain an older build snapshot; they are not
authority and must only be regenerated after the Node/Rollup environment gate
is repaired.

Disposition:
VENUE_ENTITY_CROSSWALK_CURRENT; MAP_AUTHORITY_EXPLICIT;
RD_VENUE_AND_TECHNICAL_VENUE_BOUNDARIES_PRESERVED; NO_STALE_SOURCE_REFERENCE;
NO_DATABASE_OR_WIN_MUTATION.

## Next concrete action

Inspect the portfolio/ISKVW projection boundary from `/home/mak/*`, starting
with the tracked source and its consumer tests. Reconcile only a concrete stale
source or missing consumer; do not promote ignored builds, merge `source/rd`,
create another map, or install Node/Rollup. Keep current truth in `MAPA.md` and
this handoff only.

Last verified: 2026-08-15 America/Santiago — `main` includes `e61975e`; the
crosswalk has no missing evidence paths; the active RD and technical venue
surfaces are separated and validated.

## Phase 493 — portfolio projection refreshed from current MAK snapshot

The portfolio boundary was using an ignored generated `iskvw/datos/archivo.json`
from 2026-07-31 (479 pieces, 269 links), while the declared generator and
current MAK snapshot had advanced. The old generated artifact was preserved at
`context/quarantine/phase493_portfolio_projection/archivo.pre-refresh-20260815.json`
with SHA-256
`7c11268b0457bf6ee2e4885150c62ab06e7264f09ccbc1dd4c3435b22980b925`.

The declared command was run in the foreground:

    PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src /home/mak/vibecodeine/.venv/bin/python tools/gen_archivo_iskvw.py --fuente todo --salida iskvw/datos/archivo.json --posiciones iskvw/datos/campo.json

The live micelio request was refused, so the generator used the local
`iskvw/datos/micelio.json` snapshot (1,530 pieces, 4,921 links) and produced
`iskvw/datos/archivo.json` with 1,690 pieces, 4,729 links, 104 `codigo`, 1,586
`obra`, 4,711 `semantico`, 18 `etiqueta`, and 219 measured positions. The new
artifact SHA-256 is
`55badebf0b0d1b524f3d4a0f52198b3da088f431c6a7c72f9523fcf119d0fe7c`.

Foreground validation:

    PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src /home/mak/vibocodeine/.venv/bin/python tools/validar_curaduria.py
    PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:. /home/mak/vibecodeine/.venv/bin/pytest -q tests/test_contrato_archivo.py tests/test_gen_archivo_iskvw.py tests/test_archivo_iskvw_posicion.py tests/test_curaduria.py tests/test_validar_curaduria.py tests/test_iskvw_vinculos.py tests/test_iskvw_piel_smoke.py tests/test_iskvw_piel_medir.py
    node tools/iskvw_piel_medir.mjs

Results: curatoría exited 0 with `0 errores, 0 avisos`; the focused portfolio
suite exited 0; the Node measurement exited 0 with a worst case of 2,098
segments/frame, below the tested 6,000 ceiling. No source code, database, WIN
file, external provider or service changed. The generated artifact is ignored
by Git by design; its source and command are now explicit, and the previous
artifact is quarantined rather than active.

The stale ISKVW instructions were corrected in the existing files
`iskvw/README.md`, `iskvw/ESQUEMA_ARCHIVO.md`, `iskvw/PROMPT_ESTETICA.md` and
`iskvw/datos/ESQUEMA.md`: they now distinguish the eight-entry `obras.json`
catalog from the generated archive and point to the real executable contract
`cultura/mak_plataforma/contrato_archivo.py`; no `CONTRATO.md` is claimed to
exist.

Disposition:
PORTFOLIO_PROJECTION_CURRENT_LOCAL; OLD_GENERATED_ARTIFACT_QUARANTINED;
PORTFOLIO_SKIN_GREEN; STALE_ISKVW_INSTRUCTIONS_REMOVED;
NO_DATABASE_OR_WIN_MUTATION.

## Next concrete action

Audit the tracked portfolio publication workflow and deployment inputs from
`/home/mak/*`: prove that it regenerates `iskvw/datos/archivo.json` from the
current source or intentionally publishes a documented fallback. Do not commit
the ignored generated JSON, do not promote `web/dist*`, and do not repair Node /
Rollup without explicit authorization. Keep current operational truth in
`MAPA.md` and this handoff.

Last verified: 2026-08-15 America/Santiago — local portfolio projection is
current against the available MAK snapshot; the only remaining question is the
tracked publication path, not the archive schema or skin runtime.

## Phase 494 — portfolio publication path proven and stale workflow notes removed

The tracked publication path is coherent: `.github/workflows/publicar_iskvw.yml`
regenerates `iskvw/datos/archivo.json` with `--fuente todo` before copying
`iskvw/` into the Pages staging directory; `.github/workflows/ci.yml` performs
the same regeneration before verification. The generated JSON is therefore a
build input, not a versioned source. The workflow remains explicit-dispatch
only and does not start a local service.

The local Pages staging recipe was run in a temporary directory (no deploy):

    cp -r iskvw/. <tmp>/_sitio/
    cp iskvw/piel/campo/index.html <tmp>/_sitio/index.html
    sed -i '<relative-path rewrite>' <tmp>/_sitio/index.html
    <required-file and index/disk coherence assertions>

Exit 0: `pages_staging=OK`; the staged projection had 1,690 pieces and 4,729
links, 208 traces, 219 measured field records, zero missing trace IDs, and zero
zero-byte SVGs; the staging payload was 6.2 MB. No service, external provider,
database, WIN file or published site changed.

Comments in the tracked workflow and generator files were also corrected to
remove stale fixed counts and the historical `mak` branch reference. The
runtime commands were unchanged; only operational guidance was refreshed.

Disposition:
PORTFOLIO_PAGES_INPUTS_CURRENT; PAGES_STAGING_GREEN;
WORKFLOW_GENERATES_IGNORED_PROJECTION; NO_STALE_BRANCH_GUIDANCE;
NO_DATABASE_OR_WIN_MUTATION.

## Next concrete action

Run a final read-only synchronization audit from `/home/mak/*`: verify
`main=origin/main`, the one preservation tag, the nine exact `source/*` tips,
and the retained worktree branch; then choose the next active consumer from the
MAK surface. Do not stage unrelated evidence, commit ignored generated JSON,
delete the open worktree, or create another operational map.

Last verified: 2026-08-15 America/Santiago — portfolio source, generated
projection, Pages workflow and CI agree; publication staging passed locally.

## Phase 495 — main-only topology promoted without losing historical work

The old branch refs were audited before removal. The nine exact `source/*`
tips were each proven reachable from `archive/house-history^{commit}`; the
temporary `work/mak-ownership` tip `5b20e2251846ea033ae8fc089b2223fbaf031433`
was proven an ancestor of `main`. Its work was therefore already promoted.

The tracked topology contract was promoted first in commit
`1f5dea8bc1feba371b663b62518ee184bfb33b08`:

- `MAPA.md` now declares one permanent `main`, one archive tag and only
  short-lived topic branches during active review.
- `.github/workflows/podar_ramas.yml` was removed because it described a
  non-mutating pruning workflow that no longer matched the desired state.
- `.github/workflows/git-topology.yml` now requires remote `main` only and an
  annotated `archive/house-history` tag.
- `tests/test_git_web_contract.py` was updated for that contract; `6 passed`
  with exit 0 and `git diff --check` passed.

The remote update published `main` and deleted exactly these ten remote refs:
the nine `source/*` copies and `work/mak-ownership`. Local branch refs were
then removed with the same verified preservation gate. The final foreground
sync returned:

    local_branch_count=1
    remote_branch_count=1
    main_local=main_remote
    remote_heads=refs/heads/main
    remote_tags=refs/tags/archive/house-history

The clean temporary worktree `/tmp/mak-branch-topology` was removed. Dirty
worktrees, `/home/mak/flujo-deploy`, `/home/mak/WIN`, databases, credentials,
portfolio projections and unrelated context evidence were not removed or
staged. This is a branch/reference cleanup, not a physical-tree cleanup.

Disposition:
MAIN_ONLY_TOPOLOGY_CURRENT; HISTORICAL_TIPS_TAG_PRESERVED;
REMOTE_LOCAL_SYNC_GREEN; NO_USEFUL_COMMIT_LOST; NO_RUNTIME_OR_WIN_MUTATION.

## Next concrete action

Run the final local topology assertion and a no-service repository health
check from `/home/mak/flujo`; then continue only with the explicitly open
physical/runtime gates above. Do not recreate `source/*`, `work/*`, domain
branches or another operational map. Any future topic branch must be
short-lived, target `main` directly, pass its consumer gate and be deleted
after promotion.

Last verified: 2026-08-15 America/Santiago — GitHub and local Git expose one
branch (`main`) and one annotated preservation tag.

## Phase 496 — FLUJO APP foreground smoke passed

The live local entrypoints were checked without opening a browser, processing
pending jobs or calling mutating POST routes:

    PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src /home/mak/vibecodeine/.venv/bin/python -m flujo serve --no-abrir --host 127.0.0.1 --port 8765
    PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src /home/mak/vibecodeine/.venv/bin/python -m flujo app --no-abrir --host 127.0.0.1 --port 8766

Both processes started with exit-bound foreground sessions and printed the
real workspace/hub contract. GET-only checks returned HTTP 200 and valid JSON
for `/api/ping`, `/manifest.json`, `/api/list-svg-works` and `/api/list-jobs`;
the HTML routes `/`, `/flujo_hub.html`, `/svg_visualizer.html` and
`/plano_demo.html` also returned 200. The alias ping reported version `0.56.1`,
workspace `flujo`, status `ok` and mode `http-server`. The three HTML files
are intentionally one React single-file build; `web/src/App.tsx` selects the
view from the pathname, as documented in `web/README.md`.

Both temporary servers were stopped with Ctrl-C. No POST, job processing,
database write, external provider, browser, service unit or persistent process
was used. The local working tree remains unchanged apart from the pre-existing
unrelated dirty/context evidence listed by `git status`.

Disposition: `FLUJO_SERVE_GREEN; FLUJO_APP_ALIAS_GREEN; GET_ONLY; NO_DURABLE_STATE_CHANGE`.

## Next concrete action

When continuing the house work, use `flujo app --no-abrir` for bounded checks
and the existing CI/Pages workflow for deployment validation. Keep runtime
tests foreground and temporary; do not enable `--procesar-pendientes` without
an explicit job-processing decision.

Last verified: 2026-08-15 America/Santiago — both FLUJO entrypoints started,
served the real backend, passed GET smoke checks and were stopped cleanly.

## Phase 497 — MAK hub restricted to local-only access

The user clarified that MAK no longer serves a second Windows computer and
must not expose a LAN interface. The canonical Hub now reads `HUB_HOST` with a
safe default of `127.0.0.1`; the deployed user unit sets the same value
explicitly. Research and Codex were already loopback-only. Active files were
updated in `cultura/mak_plataforma/hub.py`,
`cultura/mak_plataforma/mak-hub.service`,
`cultura/mak_plataforma/GENESIS.md`,
`cultura/mak_research/MAK_RESEARCH.md`,
`tests/test_operational_entrypoints.py`,
`/home/mak/plataforma/GENESIS.md`,
`/home/mak/plataforma/RELEVO_MAK.md` and
`/home/mak/.config/systemd/user/mak-hub.service`.

Foreground validation:

    systemctl --user daemon-reload && systemctl --user restart mak-hub.service
    ss -ltnp | grep -E ':(8890|8891|8900)\\b'
    curl http://127.0.0.1:8900/health
    curl http://192.168.50.2:8900/health

The unit was active, local health returned HTTP 200 with the MAK schema, and
the LAN request failed with curl exit 7 / HTTP 000. No external provider,
database or WIN file changed. The Hub remains viewable locally at port 8900;
LAN access is now an explicit future decision rather than the default.

Disposition: `MAK_LOCAL_ONLY; LAN_BIND_REJECTED; NO_WIN_OR_DATABASE_MUTATION`.

## Phase 498 — portable branch contract and dependency source established

The repository already had the RD/ISKVW/Cultura tool division; no tool tree or
README artwork was moved. The global `/home/mak/flujo/agents.md` now defines
short-lived branch contracts and exclusive branch handoffs. Added templates:
`contracts/BRANCH_AGENTS_TEMPLATE.md` and
`context/BRANCH_HANDOFF_TEMPLATE.md`. `MAPA.md` records the lifecycle: a topic
branch carries `contracts/branches/<branch-id>/agents.md` and
`context/handoffs/<branch-id>.md`, promotes durable facts to
`context/LAST_HANDOFF.md`, then disappears with its temporary documents after
merge.

The dependency audit found that `pyproject.toml` was already the correct
source of truth, while setup, render CI, security CI and the first-day guide
still installed or audited duplicate requirements files. They now use
`python -m pip install -e ".[dev,render]"`. Added
`docs/DEPENDENCIES.md`; `requirements.txt` and `requirements-dev.txt` are
explicitly compatibility inputs, not branch contracts or CI authorities.

Validation:

    bash -n scripts/setup.sh
    /home/mak/vibecodeine/.venv/bin/python -m pytest -q tests/test_git_web_contract.py tests/test_operational_entrypoints.py
    /home/mak/vibecodeine/.venv/bin/python -m pip check
    /home/mak/vibecodeine/.venv/bin/python -m pip install --dry-run --ignore-installed --no-deps -e ".[dev,render]"
    git diff --check
    git diff --quiet -- README.md

Results: setup syntax exit 0; focused tests `12 passed`; pip check reported
`No broken requirements found`; editable metadata dry-run reported
`Would install flujo-0.56.1` with exit 0; diff check exit 0; README diff exit
0. No source tool, database, generated artwork or historical evidence was
changed by this phase.

Open risk: the repository has no committed lock file yet, and the full
dependency resolution still needs an isolated fresh-environment gate. Do not
create a domain branch until that gate and a real bounded improvement are
selected. Do not create one requirements file per branch; update the project
contract and the branch-scoped handoff together.

Disposition: `BRANCH_CONTRACTS_ESTABLISHED; PYPROJECT_CANONICAL;
FOCUSED_PORTABILITY_GREEN; README_PRESERVED`.

## Next concrete action

Run an isolated fresh-environment install from `/home/mak/flujo` using the
canonical project extras, capture the resolver result and `pip check`, then
choose the first real bounded improvement (RD, ISKVW, Cultura or tools) before
creating a short-lived topic branch with its exclusive contract and handoff.

Last verified: 2026-08-15 America/Santiago — branch contract templates and
canonical dependency installation metadata pass focused validation; no lock
file or topic branch has been created yet.

## Phase 499 — isolated portability gate passed

The canonical install was tested in a fresh temporary virtual environment,
without changing the active MAK environment. The command was:

    portable_dir=$(mktemp -d /tmp/flujo-portable.XXXXXX)
    python3 -m venv "$portable_dir/venv"
    "$portable_dir/venv/bin/python" -m pip install -e ".[dev,render]"
    "$portable_dir/venv/bin/python" -m pip check
    "$portable_dir/venv/bin/python" -c 'import flujo, flujo.cli'

The installation built editable `flujo-0.56.1` and exited 0; `pip check`
reported `No broken requirements found`; the import exited 0. In that same
clean environment:

    /tmp/flujo-portable.fquPM8/venv/bin/python -m pytest -q tests/test_git_web_contract.py tests/test_operational_entrypoints.py
    /tmp/flujo-portable.fquPM8/venv/bin/python -m flujo --help

Both commands exited 0; the focused suite returned `12 passed` and the CLI
listed the real command surface. The temporary environment is isolated under
`/tmp`; no MAK runtime, database, WIN file, README or generated artifact was
changed.

The portability foundation is therefore green for the declared extras. An
exact lock file is still intentionally open; the repository currently relies
on lower-bound project constraints and should choose one lock mechanism before
claiming byte-for-byte reproducibility.

Disposition: `FRESH_INSTALL_GREEN; CLEAN_IMPORT_GREEN; CLEAN_FOCUSED_TESTS_GREEN;
NO_ACTIVE_ENV_MUTATION`.

## Next concrete action

Choose the first real bounded improvement from the existing FLUJO tools (RD,
ISKVW, Cultura or tools). Create its short-lived topic branch from the clean
main baseline, copy the branch contract and handoff templates into that branch,
and include only that consumer's code, tests and dependency changes. Do not
move the existing tools or touch the README artwork.

Last verified: 2026-08-15 America/Santiago — a fresh Debian-compatible Python
environment installs the declared project extras, imports FLUJO and passes the
focused Git/entrypoint suite; no topic branch or lock file exists yet.

## Phase 500 — worktree baseline rechecked before first topic branch

The repository is on `main` at `f277094` (`docs: record flujo app smoke test`).
The portability/contract changes remain local and intentionally uncommitted;
the worktree also contains many pre-existing historical `context/PHASE*`
reports, fixtures, quarantine evidence, database backups and unrelated edits.
Those surfaces are excluded from the first branch write set and must not be
bulk-staged.

Validation run:

    git branch --show-current
    git diff --check
    git log -1 --oneline

Results: current branch `main`; diff check exit 0; latest commit `f277094`.
README remains unchanged. No branch, commit, push, service or database
mutation was performed in this check.

Disposition: `MAIN_BASELINE_RECHECKED; HISTORICAL_EVIDENCE_EXCLUDED;
NO_BULK_STAGE`.

## Next concrete action

Select one real bounded improvement from the existing consumers (RD, ISKVW,
Cultura or tools), then isolate the current contract/dependency changes from
pre-existing evidence before creating the short-lived topic branch. The first
branch must carry only its scoped code, tests, dependency metadata and its
exclusive `agents.md`/handoff contract; do not move tools or touch the README.

Last verified: 2026-08-15 America/Santiago — main baseline and dirty-surface
boundaries rechecked; no bulk staging or external publication performed.

## Phase 501 — continuous-work objective locked

The continuous objective is now explicit: complete the operational and
portable restructuring of `/home/mak/flujo` without losing useful work;
preserve the current SVG README and `WIN` as historical evidence; keep one
green synchronized `main`; use short-lived consumer branches only for real
changes; give each active branch an exclusive agent contract and handoff;
keep `pyproject.toml` as the dependency source; keep FLUJO APP and MAK
working locally with their current interfaces; integrate only tools with a
real consumer and evidence of operation; and separate or retire only verified
duplicates/obsolete artifacts. Every change must pass the appropriate tests,
imports, CLI and foreground smoke checks before merge/publication.

Every turn must record commands, exit codes, changed files, risks and the
next action here. Prohibited shortcuts remain: no deletion of historical
evidence, no README edits, no SSH, no permanent services, no divergent
requirements files or branches, and no waiting for confirmation while safe
work remains executable.

Disposition: `CONTINUOUS_OBJECTIVE_LOCKED`.

## Next concrete action

Isolate the current intentional portability/contract changes from the
pre-existing historical evidence, then prepare the first real consumer slice
for a short-lived branch without bulk-staging the worktree.

Last verified: 2026-08-15 America/Santiago — objective stored in the task goal
and in this handoff; no branch, commit or external publication performed.

## Phase 502 — archaeology output safety slice integrated

Created short-lived branch `tools/inferential-archaeology` from `main` at
`536d807`, owned by `LUNA-502`, with an exclusive contract and handoff. The
branch changed only `tools/inferential_archaeology.py` and its focused tests,
plus the temporary branch contract files.

The index now validates every generated SQLite, DuckDB and summary path before
loading history or session inputs. External paths and the ignored
`/home/mak/flujo/out` projection are allowed; paths inside repository source,
data or context trees are rejected. Symlinks are resolved before validation,
so an apparently safe path cannot redirect into a source database.

Validation:

    /home/mak/vibecodeine/.venv/bin/python -m py_compile tools/inferential_archaeology.py tests/test_inferential_archaeology.py
    /home/mak/vibecodeine/.venv/bin/python -m pytest -q tests/test_inferential_archaeology.py
    /home/mak/vibecodeine/.venv/bin/python tools/inferential_archaeology.py build --repo /home/mak/flujo --claude-root /tmp/missing-claude-root --codex-root /tmp/missing-codex-root --memory-root /tmp/missing-memory-root --output /tmp/archaeology-integrity.0Pjqz0/evidence.sqlite --summary /tmp/archaeology-integrity.0Pjqz0/summary.json
    /home/mak/vibecodeine/.venv/bin/python tools/inferential_archaeology.py report --sqlite /tmp/archaeology-integrity.0Pjqz0/evidence.sqlite --limit 1
    git diff --check

Results: compile exit 0; focused suite `29 passed`; negative output-path probe
exit 2 with the expected guard; foreground build/report exit 0 with schemas
`inferential-archaeology-v7` and `inferential-archaeology-report-v1`; 1,014
commits indexed; `data/rd.db` and README SHA-256 hashes were unchanged.
Generated outputs stayed in `/tmp`. No source, WIN, database, README, service
or provider state changed.

The branch commit is `3fd9c1b` (`fix(tools): guard archaeology output paths`).
Its temporary contract and handoff were removed during closeout; durable facts
are recorded here.

Disposition: `ARCHAEOLOGY_OUTPUT_GUARD_GREEN; READ_ONLY_GATE_GREEN;
SOURCE_HASHES_GREEN; BRANCH_CLOSED_PENDING_FAST_FORWARD`.

## Next concrete action

Fast-forward `main` with the archaeology slice, delete the short-lived branch,
then open the next bounded consumer slice for the SCD venue geometry tool:
static/compile/fixture validation of `tools/venue_geometria_scd.py`,
`tools/venue.py` and their existing tests. Keep it offline and output-only;
do not call providers or alter RD databases.

Last verified: 2026-08-15 America/Santiago — archaeology branch committed and
validated; root handoff promotion prepared; no external publication performed.

## Phase 503 — SCD venue regeneration check integrated

Created short-lived branch `tools/venue-scd` from the synchronized `main` at
`da8ab50`, owned by `LUNA-503`, with an exclusive contract and handoff. The
branch changed only `tools/venue_geometria_scd.py` and its focused test, plus
the temporary branch contract files.

The SCD geometry generator now supports `--check`: it compares the
deterministic generated document with `data/venues/scd-plaza-egana.json`,
returns exit 1 on drift, exit 2 for invalid option combination or unreadable
canonical data, and never writes in check mode. `--stdout` remains the safe
JSON export path; the default writer is unchanged.

Validation:

    /home/mak/vibecodeine/.venv/bin/python -m py_compile tools/venue_geometria_scd.py tests/test_venue.py
    /home/mak/vibecodeine/.venv/bin/python -m pytest -q tests/test_venue.py tests/test_venue3d_smoke.py
    /home/mak/vibecodeine/.venv/bin/python tools/venue_geometria_scd.py --check
    /home/mak/vibecodeine/.venv/bin/python tools/venue_geometria_scd.py --stdout | /home/mak/vibecodeine/.venv/bin/python -m json.tool
    git diff --check

Results: compile exit 0; focused suite `46 passed`; check and JSON parse exit 0;
the canonical SCD JSON and README SHA-256 hashes stayed unchanged. The venue
demo remains 56 polylines, 503 edges and zero degenerate segments. No RD
database, venue source, generated site, WIN, README, service or provider state
changed.

The branch commit is `714b5cd` (`test(venue): add non-mutating SCD check`). Its
temporary contract and handoff are removed during closeout; durable facts are
recorded here.

Disposition: `SCD_REGENERATION_CHECK_GREEN; OFFLINE_JSON_GREEN;
SOURCE_HASHES_GREEN; BRANCH_CLOSED_PENDING_FAST_FORWARD`.

## Next concrete action

Fast-forward `main` with the SCD check, delete the short-lived branch and push
the result. Then audit the next real consumer slice, prioritizing the
read-only RD/venue crosswalk against `data/rd.db` and `data/venues/*.json`;
do not merge databases or insert venue relations automatically.

Last verified: 2026-08-15 America/Santiago — SCD branch committed and
validated; root handoff promotion prepared; no external publication performed.

## Phase 504 — RD/venue crosswalk provenance integrated

Created short-lived branch `rd/venue-crosswalk` from synchronized `main` at
`2431b26`, owned by `LUNA-504`, with an exclusive contract and handoff. The
branch changed only `src/flujo/rd/entity_crosswalk.py` and its focused test,
plus the temporary branch contract files.

`EntityCrosswalk` now preserves and validates the declared relative source
database list. It exposes `('data/rd.db', 'data/rd_datos.db')` while rejecting
absolute paths, Windows-drive paths, empty path segments and `..` traversal.
The adapter remains JSON-only and review-only; it does not open, merge,
rebuild or write either SQLite source.

Validation:

    /home/mak/vibecodeine/.venv/bin/python -m py_compile src/flujo/rd/entity_crosswalk.py tests/test_entity_crosswalk.py
    /home/mak/vibecodeine/.venv/bin/python -m pytest -q tests/test_entity_crosswalk.py tests/test_rd_database.py tests/test_venue.py
    PYTHONPATH=src /home/mak/vibecodeine/.venv/bin/python -c 'from flujo.rd.entity_crosswalk import load_crosswalk; c=load_crosswalk(); print(c.source_databases)'
    git diff --check

Results: compile and combined suite exit 0; crosswalk status `review_only`,
four entities and two declared source databases; unsafe path test rejects
without writing; SHA-256 hashes for `data/rd.db` and `data/rd_datos.db` stayed
unchanged. No database, venue JSON, portfolio artifact, README, WIN, service
or provider state changed.

The branch commit is `f742844` (`fix(rd): preserve crosswalk source
provenance`). Its temporary contract and handoff are removed during closeout;
durable facts are recorded here.

Disposition: `RD_VENUE_PROVENANCE_GREEN; NO_DATABASE_MERGE;
REVIEW_ONLY_PRESERVED; SOURCE_HASHES_GREEN; BRANCH_CLOSED_PENDING_FAST_FORWARD`.

## Next concrete action

Fast-forward `main` with the crosswalk provenance slice, delete the short-lived
branch and push the result. Then audit the next bounded consumer, prioritizing
the read-only portfolio/venue publication gate; no public exposure is allowed
without explicit provenance, confidence and publication status.

Last verified: 2026-08-15 America/Santiago — crosswalk branch committed and
validated; root handoff promotion prepared; no external publication performed.

## Phase 505 — ISKVW publication scope gate integrated

Created short-lived branch `iskvw/publication-gate` from synchronized `main`
at `e0ff6a1`, owned by `LUNA-505`, with an exclusive contract and handoff.
The branch changed only `tests/test_git_web_contract.py` plus the temporary
branch contract files.

The publication boundary is now executable: the Pages workflow remains manual
dispatch only, stages `iskvw/.` and explicitly excludes RD databases,
`data/venues`, Cultura, MAK and WIN. The generator's public `--fuente todo`
filter continues to exclude research essays unless explicitly requested.

Validation:

    /home/mak/vibecodeine/.venv/bin/python -m pytest -q tests/test_git_web_contract.py tests/test_gen_archivo_iskvw.py
    /home/mak/vibecodeine/.venv/bin/python -m py_compile tools/gen_archivo_iskvw.py tests/test_git_web_contract.py
    git diff --check

Results: `17 passed`; compilation and whitespace checks exit 0; no deploy,
network call, Cloudflare change or generated public artifact was performed.

The branch commit is `ad7368a` (`test(web): guard iskvw publication scope`).
Its temporary contract and handoff are removed during closeout; durable facts
are recorded here.

Disposition: `ISKVW_PUBLIC_SCOPE_GREEN; RD_VENUE_EXCLUDED;
MANUAL_DEPLOY_PRESERVED; BRANCH_CLOSED_PENDING_FAST_FORWARD`.

## Next concrete action

Fast-forward `main` with the publication scope gate, delete the short-lived
branch and push the result. Then run a broad read-only health matrix across
FLUJO APP and MAK hub endpoints, ensuring the current local services remain
available without adding ports or changing the single-interface model.

Last verified: 2026-08-15 America/Santiago — publication branch committed and
validated; root handoff promotion prepared; no external publication performed.

## Phase 506 — local health matrix and bounded FLUJO APP startup

Verified the physical runtime state before changing anything. `ss -ltnp`
showed the existing MAK loopback services on `127.0.0.1:8890`,
`127.0.0.1:8891` and `127.0.0.1:8900`; no process was listening on
`127.0.0.1:8765`. The user services `mak-research.service`,
`mak-codex.service` and `mak-hub.service` remained active. No service was
started or reconfigured by the matrix.

The first matrix command used `python` and returned shell exit 127 because
Debian does not provide that alias in this environment; it made no request
and changed no file. The identical GET-only matrix with the canonical
interpreter `/home/mak/vibecodeine/.venv/bin/python` returned HTTP 200 for
the nine MAK routes: `/health`, `/api/organismo`, `/api/micelio`,
`/api/archivo`, `/api/oportunidades`, `/api/eventos`, `/api/actividad`,
`/api/salud` and `/api/portfolio/inbox`. Result: `ok=9 fail=0`. All responses
were JSON objects; no POST, upload, database write or external network call
was made.

Because FLUJO APP was stopped rather than failing, it was started only for a
bounded foreground check with:

    FLUJO_MAK_URL=http://127.0.0.1:8900 PYTHONDONTWRITEBYTECODE=1 timeout 20s /home/mak/vibecodeine/.venv/bin/python -m flujo app --no-abrir --host 127.0.0.1 --port 8765

The temporary process reached `GET /api/mak -> 200`, printed the expected
workspace banner, and was terminated by the check trap. It was not left as a
permanent process. No source, database, generated artifact, README, WIN or
service state changed; the only intended file update in this phase is this
handoff entry.

Disposition: `MAK_HEALTH_9_OF_9_GREEN; FLUJO_APP_STARTUP_GREEN;
NO_PERMANENT_APP_PROCESS; LOOPBACK_ONLY_PRESERVED`.

## Next concrete action

Run the complete non-mutating local verification from the canonical editable
environment (imports, CLI help, focused regression suites and the existing
MAK/FLUJO smoke paths), then record any real failure as a bounded fix target.
Keep FLUJO APP as an offline/temporary interface unless the user explicitly
requests a managed local launcher; do not add a second public port or turn the
bounded check into a permanent service. Reconcile only intentional source
changes, leaving the large `context/PHASE*` evidence surface un-staged.

Last verified: 2026-08-15 America/Santiago — MAK GET matrix and bounded FLUJO
startup passed; no persistent process or external publication performed.

## Phase 507 — portable CLI map and documentation hygiene gate

The complete canonical suite initially returned exit 1 with six documentation
failures. The runtime failures were not tool failures: `MAPA.md` lacked the
generator markers and current CLI table; `context/comandos.json` still had a
retired `handoff` row; `CAPACIDADES.md` declared absent `contexto_repo.py` and
`handoff.py`; and the documentation ratchet rejected several undifferentiated
historical suite totals in this handoff.

The generator also exposed a portability defect: its subprocess inherited the
environment's installed package, which was the historical `/home/mak/vibecodeine`
copy, instead of necessarily interrogating this checkout. `tools/gen_mapa_comandos.py`
now prepends `/home/mak/flujo/src` (computed from `RAIZ`) to `PYTHONPATH` before
asking the CLI for help. This keeps the manifest and Markdown map tied to the
editable checkout that is being tested.

Changes were limited to `tools/gen_mapa_comandos.py`, regenerated
`MAPA.md`/`context/comandos.json`, removal of the two ghost capability rows in
`CAPACIDADES.md`, and this handoff. The generated map now measures 95 current
commands, including `autonomia` and `rd-db testeos`, and documents all runtime
environment variables detected by the repository tests without adding secrets.
Historical test counts in this handoff were rewritten as dated outcomes or
commands, not as claims about the current suite total.

Validation:

    /home/mak/vibecodeine/.venv/bin/python tools/gen_mapa_comandos.py
    /home/mak/vibecodeine/.venv/bin/python tools/gen_mapa_comandos.py --check
    /home/mak/vibecodeine/.venv/bin/python -m py_compile tools/gen_mapa_comandos.py
    /home/mak/vibecodeine/.venv/bin/python -m pytest -q
    git diff --check

The focused hygiene group passed with exit 0, the regenerated map check passed,
and the complete suite passed with exit 0. Only known Pillow deprecation
warnings were emitted. No database, service, provider, network, README SVG,
WIN evidence or `context/PHASE*` evidence was changed or staged.

Disposition: `FULL_LOCAL_SUITE_GREEN; CLI_MAP_CURRENT; GHOST_ROWS_REMOVED;
CHECKOUT_PYTHONPATH_PINNED; EVIDENCE_UNSTAGED`.

## Next concrete action

Review the explicit five-file diff, commit it on `main`, push to `origin/main`,
and re-run the branch/tag/status invariants without staging any pre-existing
HTML, database backups, probe scripts or phase evidence. After publication,
continue the objective audit from the remaining physical consumer surface;
only introduce a short-lived named topic branch if a new bounded code change
is actually found.

## Phase 508 — map repair published and topology rechecked

The five-file Phase 507 slice was committed on `main` as `592f6c7`
(`fix: pin map generation to checkout`) and pushed successfully to
`origin/main`. Post-push invariants returned `main...origin/main = 0 0`, only
local `main` plus `origin/main` remained as branches, and the sole preservation
tag remained `archive/house-history`. `README.md` is byte-clean in the working
diff and the index is empty. The unrelated modified HTML/evidence surface
remains unstaged and untouched.

Disposition: `PHASE507_PUBLISHED; MAIN_SYNCHRONIZED; ONE_ARCHIVE_TAG;
README_UNCHANGED; EVIDENCE_UNSTAGED`.

## Next concrete action

Continue the physical consumer audit from `/home/mak/*`, using the current
`MAPA.md` and root handoff as navigation. Select the next bounded local slice
only if it has a real consumer, an observable input/output contract and a
non-mutating validation path. Preserve `WIN`, generated products, databases,
quarantine and session evidence; do not stage the existing evidence backlog or
create a branch for documentation-only work.

Last verified: 2026-08-15 America/Santiago — Phase 507 published as `592f6c7`;
topology and README invariants green.

## Phase 509 — physical MAK runtime and portfolio boundary audit

Started from `/home/mak/*` as required. The active user units identify the
runtime boundary precisely:

    mak-research.service -> /home/mak/research/interfaz.py (:8890)
    mak-codex.service    -> /home/mak/codex/interfaz_codex.py (:8891)
    mak-hub.service      -> /home/mak/plataforma/hub.py (:8900)

All three bind to loopback. The external directories contain live data,
queues, logs, generated products and virtual environments, so they remain
physical runtime/evidence roots rather than material to copy into Git.

The code crosswalk was read-only and excluded virtualenv files. Research had
35 external Python files versus 30 canonical files, with 30 shared names (21
byte-identical and 9 explicit compatibility projections). Codex had 125
external Python files including generated pieces, 18 shared canonical names
(12 byte-identical and 6 compatibility/divergent modules). Platform had 152
external Python files, 48 shared canonical names (27 byte-identical and 21
compatibility/divergent modules). `/home/mak/plataforma/hub.py` explicitly
loads `cultura/mak_plataforma/hub.py`; the active external surface is therefore
an adapter/data boundary, not a reason to duplicate the tree.

Validation:

    PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:cultura/mak_research:cultura/mak_codex:cultura/mak_plataforma:. /home/mak/vibecodeine/.venv/bin/python -c 'import cadena, worker, fuentes, codex_lib'
    PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:. /home/mak/vibecodeine/.venv/bin/python -m py_compile cultura/mak_research/*.py cultura/mak_codex/*.py cultura/mak_plataforma/*.py
    npm run typecheck  # from web/
    /home/mak/vibecodeine/.venv/bin/python -m pytest -q tests/test_git_web_contract.py tests/test_gen_archivo_iskvw.py tests/test_iskvw_piel_smoke.py tests/test_iskvw_campo.py

The corrected canonical import and compilation returned exit 0; the first
diagnostic attempt used the nonexistent `flujo.cultura` namespace and returned
`ModuleNotFoundError` without side effects. Web TypeScript typecheck returned
exit 0, and the portfolio/publication smoke group returned exit 0. No build
copy, deployment, browser navigation, service restart, database write,
provider call, external network request or file move was performed.

Disposition: `MAK_EXTERNAL_BOUNDARIES_EXPLAINED; CANONICAL_IMPORTS_GREEN;
PORTFOLIO_STATIC_GATE_GREEN; NO_TREE_COPY; NO_RUNTIME_MUTATION`.

## Next concrete action

Perform the final requirement-by-requirement audit against the active goal:
dependency source, local FLUJO/MAK runtime, Git topology, branch contracts,
consumer-backed integrations, evidence protection and README/WIN invariants.
Use current files and fresh command output, then either close the goal with
the exact remaining risks or create one final bounded code slice if an item is
still unproven. Do not stage the pre-existing HTML/evidence surface.

Last verified: 2026-08-15 America/Santiago — physical runtime crosswalk and
portfolio type/smoke gates green; no external state changed.

## Phase 510 — objective completion audit

Fresh evidence was collected against every explicit operational requirement:

| Requirement | Current evidence | Result |
|---|---|---|
| Preserve README SVG and WIN | `git diff --quiet -- README.md` exit 0; `/home/mak/WIN` present and untouched | GREEN |
| One synchronized main | `git rev-list --left-right --count main...origin/main` = `0 0`; only `main` and `origin/main`; `archive/house-history` present | GREEN |
| Short-lived branches/contracts | no active topic branch remains; branch templates exist and every promoted slice used a scoped owner/handoff before closeout | GREEN |
| Canonical dependencies | `pyproject.toml` is the source; requirements files declare compatibility role; editable install and `pip check` evidence are recorded in earlier portability gate | GREEN |
| FLUJO APP local interface | bounded foreground start on `127.0.0.1:8765`; `GET /api/mak` returned `200`; process terminated by trap | GREEN |
| MAK local interface | existing loopback hub returned `200` for all nine GET routes, including portfolio inbox; internal services stayed on `8890/8891` | GREEN |
| Consumer-backed integrations | full canonical pytest suite exit 0; focused RD, SCD, research, runtime, publication and portfolio gates exit 0 | GREEN |
| Duplicate/obsolete handling | only verified ghost registry rows were removed; source trees, generated products, databases, quarantine, session evidence and WIN were preserved | GREEN |
| Handoff continuity | this file records commands, exit codes, files, risks and next action for each current phase | GREEN |

Final runtime commands:

    GET-only MAK matrix: 9 of 9 routes returned HTTP 200 and valid JSON; exit 0
    bounded FLUJO APP: GET /api/mak -> 200; exit 0; temporary process terminated

The pre-existing user units for MAK remained active; this turn did not start,
stop, enable or reconfigure a service. The failed combined-shell attempt was a
tool safety rejection before execution, not a repository or runtime failure.
No files besides this handoff were changed by the audit; no staged evidence or
HTML worktree changes were absorbed.

Disposition: `OBJECTIVE_REQUIREMENTS_CURRENTLY_GREEN;
RUNTIME_AND_EVIDENCE_BOUNDARIES_PRESERVED; NO_NEW_SERVICE; NO_BULK_STAGE`.

## Next concrete action

Commit and push this final audit, then perform one post-push status/topology
check. If it remains green, the restructuring objective is achieved for the
authorized local scope; leave the goal record complete and keep future work as
separate, explicitly requested feature/bug slices rather than reopening the
house consolidation.

Last verified: 2026-08-15 America/Santiago — all current objective checks
passed; final audit publication is pending.

## Phase 511 — final audit published

The completion audit was committed as `a796ccc` (`docs: close restructuring
audit`) and pushed to `origin/main`. The post-push check returned:

    main...origin/main = 0 0
    branches = main, origin/main
    tags = archive/house-history
    README diff = clean
    index = empty

The remaining worktree entries are the pre-existing modified HTML snapshots and
untracked `context/PHASE*`, fixture/quarantine, database-backup and probe
evidence; none is staged or absorbed by the restructuring commits.

Disposition: `FINAL_AUDIT_PUBLISHED; MAIN_GREEN_AND_SYNCHRONIZED;
HISTORICAL_EVIDENCE_PRESERVED; NO_UNAUTHORIZED_CLEANUP`.

## Next concrete action

No required restructuring action remains in the authorized local scope. Keep
this handoff as the continuity boundary. Future changes must be separately
requested feature or bug slices with their own consumer, write set, rollback,
validation and temporary branch contract when code changes are real.

Last verified: 2026-08-15 America/Santiago — final audit published at
`a796ccc`; objective ready for completion.

## Phase 512 — portable context routing and diagnostic surface

Implemented the bounded, read-only support layer requested for both Git clones
and the local MAK hub. The canonical source is `/home/mak/flujo`; `/home/mak/WIN`
and the external `/home/mak/plataforma/hub.py` projection were not modified.

Changed or added only for this slice:

    src/flujo/diagnostics.py
    src/flujo/cli.py
    tools/route_idea.py
    context/diagnostics/README.md
    context/diagnostics/domains.json
    context/diagnostics/contracts/{core,rd,portfolio,cultura,research}.md
    cultura/mak_plataforma/hub.py
    tests/test_diagnostics.py
    tests/test_mak_diagnostics.py
    MAPA.md
    context/comandos.json

The common motor routes a natural-language idea or incident to one primary
domain (`core`, `rd`, `portfolio`, `cultura` or `research`) plus support domains,
lists only the relevant contract/read paths and validation candidates, and
explicitly excludes raw WIN. `python3 tools/route_idea.py ...` works from a
fresh clone without package installation. `python -m flujo route` and
`python -m flujo diagnose` expose the same behavior from the CLI. Diagnostic
reports are bounded Markdown/JSON, read-only, and redact secrets, Bearer
values, email addresses and the home path; the entered command is recorded but
never executed.

The MAK 8900 surface now has a `diagnóstico` tab, a copyable report panel,
`GET /api/diagnostics`, `POST /api/diagnostics` and
`GET /api/diagnostics/domains`. The existing `mak-hub.service` was restarted
after the code change and stayed active on loopback `127.0.0.1:8900`; no new
service, cron, worker, SSH connection or permanent process was created.

Foreground evidence:

    PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:. /home/mak/vibecodeine/.venv/bin/python -m pytest -q tests/test_diagnostics.py tests/test_mak_diagnostics.py
    -> exit 0; 7 passed
    PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:. /home/mak/vibecodeine/.venv/bin/python -m pytest -q tests/test_cli_smoke.py tests/test_cli_v035.py
    -> exit 0; 18 passed
    PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:. /home/mak/vibecodeine/.venv/bin/python -m pytest -q tests/test_mak_hub_eventos.py tests/test_mak_hub_salud.py
    -> exit 0; 24 passed
    PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:. /home/mak/vibecodeine/.venv/bin/python -m py_compile src/flujo/diagnostics.py src/flujo/cli.py cultura/mak_plataforma/hub.py tools/route_idea.py
    -> exit 0
    PYTHONPATH=src /home/mak/vibecodeine/.venv/bin/python tools/gen_mapa_comandos.py --check
    -> exit 0; MAPA.md and context/comandos.json current at 97 commands
    systemctl --user restart mak-hub.service
    -> exit 0; unit active; MainPID changed from 831884 to 872029
    curl GET /health, /api/diagnostics/domains and /api/diagnostics
    curl POST /api/diagnostics with Bearer/email fixture
    -> exit 0; valid schemas/routes; `topsecret` and `user@example.com` absent
    curl GET /
    -> exit 0; diagnostics tab, panel and copy action present

The worktree still contains the pre-existing dirty HTML snapshots, phase
evidence, fixtures/quarantine and database backups; none is part of this
slice. The report intentionally exposes only a dirty-entry count, not those
paths. The panel does not automatically intercept arbitrary iframe errors:
the user pastes the visible error and reproduction details, which is the
current privacy-safe contract for an external agent.

## Phase 513 — diagnostics published and runtime rechecked

The exact Phase 512 write set was reviewed, committed on `main` as `95de8a7`
(`feat: add portable MAK diagnostics`) and pushed successfully to
`origin/main`. Post-publication invariants returned:

    main...origin/main = 0 0
    branches = main
    tags = archive/house-history
    README_EXIT = 0
    INDEX_EXIT = 0

The post-push focused suite returned exit 0 across the diagnostic, CLI and MAK
hub contracts. The exact count is always measured by the command, not written
into this handoff. The live service remained active and
returned `GET /health` HTTP 200 plus a valid RD diagnostic report. The only
listening sockets remain the pre-existing loopback department services
`127.0.0.1:8890`, `127.0.0.1:8891` and the requested hub
`127.0.0.1:8900`; this slice created no new process or service.

The remaining dirty/untracked worktree entries are pre-existing HTML
snapshots, phase evidence, fixtures/quarantine and database backups. They are
not staged, committed or deleted. `WIN` remains present and untouched, and the
README SVG remains byte-clean.

## Next concrete action

No required action remains within this objective. Future work should be a
separately requested feature or bug slice routed through `python -m flujo route`
and reported through `python -m flujo diagnose`; do not reopen the completed
consolidation or stage the existing evidence backlog.

Last verified: 2026-08-15 America/Santiago — Phase 513 published; local hub,
CLI, routing, sanitization and Git synchronization green.

## Phase 514 — deterministic session archaeology from the two ensayos

The two source documents used were:

    /home/mak/WIN/flujo/docs/cultura/ensayos/caja-win.md
    /home/mak/WIN/flujo/docs/cultura/ensayos/guia-analisis-sesiones-claude-codex.md

Their proposed seven deliverables were executed with the existing
`tools/inferential_archaeology.py` extractor and a bounded renderer at
`tools/render_archaeology_deliverables.py`. The raw sources were read-only:
Claude web export at `/home/mak/WIN/claude_sesiones/claude_web_export_2026-08-11`,
Codex rollouts at `/home/mak/WIN/codex/sessions`, and the MAK bitácora at
`/home/mak/plataforma/bitacora_capataz.jsonl`.

Commands and results:

    PYTHONPATH=src /home/mak/vibecodeine/.venv/bin/python tools/inferential_archaeology.py build ...
    -> exit 0; 83,835 raw turns; 23,273 unique; 22,299 analysis turns; 96 sessions; 3,702 questions; 22,632 seed candidates; 1,548 proposals; 213 Codex actions; 1,028 commits
    PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src /home/mak/vibecodeine/.venv/bin/python tools/render_archaeology_deliverables.py ...
    -> exit 0; seven bounded Markdown deliverables plus analysis_manifest.json
    SQLite PRAGMA integrity_check
    -> `ok`
    DuckDB read-only validation
    -> exit 0; 18 tables; turns=83,835; proposal_followups=1,548
    py_compile tools/render_archaeology_deliverables.py + JSON manifest parse
    -> exit 0

The generated artifacts are under the ignored analysis output boundary:

    out/archaeology/claude-codex-mak-20260815/analysis_manifest.json
    out/archaeology/claude-codex-mak-20260815/{session_inventory,question_ledger,idea_catalog,decision_graph,effort_report,closure_audit,triangulation_report}.md
    out/archaeology/claude-codex-mak-20260815.sqlite
    out/archaeology/claude-codex-mak-20260815.duckdb

Principal findings: exact duplicate turns are 60,562/83,835 (72.2%);
3,698 questions require semantic review and 4 are mechanically unresolved;
proposal states are 1,150 pending review, 376 approved without direct action,
11 direct-action candidates and 11 prompt-generated-unaccepted; 2,193 lexical
closure claims have 372 nearby correction candidates (17.0%). These are
evidence-led candidates, never diagnoses or intent claims.

Important omission: `bitacora_capataz.jsonl` yielded zero valid `mak_activity`
rows because its records do not contain the expected `activity_id` field. No
energy, cost or runtime-effort value was invented. The selected recovered root
also had no Claude Code JSONL; Claude web/design and Codex rollouts were
available. Raw source SHA-256 was not recomputed over 5.1 GB; turn-level
fingerprints and source paths remain recoverable.

No source, WIN file, database, service or Git history was changed by this
analysis. The only new working-tree source is the reproducible renderer
`tools/render_archaeology_deliverables.py`; generated outputs remain outside
the tracked source surface.

## Next concrete action

The deterministic pass is complete. The next bounded analysis is semantic
review of the 3,698 question candidates and the 1,150 proposal-pending rows,
starting with the highest-impact domains and preserving source line references;
repairing the `mak_activity` adapter is a separate measurement task. Do not
promote any idea, closure or intent claim to fact without a second independent
layer of evidence.

Last verified: 2026-08-16 America/Santiago — Phase 514 artifacts generated and
validated; WIN and runtime untouched.

## Phase 515 — measured API capability inventory

Updated the canonical capability inventory at:

    /home/mak/flujo/CAPACIDADES.md

The inventory now distinguishes code-wired integrations, optional backends,
internal HTTP surfaces, historical WIN/XIO material, and declared-but-unwired
provider keys. No secret value was read or written.

Commands and results:

    AST/read-only provider audit of cultura/mak_research/research_lib.py
    -> 5 LLM adapters: watsonx, groq, cerebras, azure, ollama
    source_pipeline.py / canva.py / research_lib.py endpoint audit
    -> 13 code-wired API/service integrations under the documented counting rule
    -> 1 additional optional backend recognized: crawl4ai; package absent
    ss -ltn; systemctl --user is-active mak-hub.service
    -> 127.0.0.1:8900, :8890 and :8891 listening; mak-hub.service active
    -> :8888 SearXNG and :11434 Ollama not listening during this measurement
    curl GET /health on :8900, :8890 and :8891
    -> all returned HTTP 200
    package/CLI presence audit
    -> crawl4ai absent; parth_dl, gh, ollama and rclone present
    git diff --check -- CAPACIDADES.md
    -> exit 0

The documented totals are: 13 wired API/service integrations; 14 recognized
backends when optional crawl4ai is included; 16 operational API surfaces when
the three internal HTTP services are included; 17 if both internal services
and crawl4ai are counted. These are adapter/surface counts, not counts of
credentials, models, endpoints, websites or successful external calls.

The active inventory now treats MAK Debian 12 as the current host, WIN as a
historical read-only archive, and XIO as outside the current operational
surface. The old WIN Ollama route and the XIO APK workflow are no longer
presented as active MAK capabilities. The document remains uncommitted because
the user requested the update but did not request a Git publication.

Risk: provider availability is not equivalent to credential availability. The
current active research.env exposes only local research configuration by name;
the discarded n8n env was not used as runtime authority. No provider key was
tested or exposed in this phase.

## Next concrete action

Resume Phase 514 semantic review of the highest-impact question candidates and
proposal-pending rows, preserving source paths and independent evidence. Keep
the API inventory as the capability boundary; do not install crawl4ai or
restart Ollama/SearXNG merely to change the count.

Last verified: 2026-08-15 America/Santiago — CAPACIDADES.md updated and API
surface measured without starting services or changing WIN, databases or Git.

## Phase 516 — credential probes without secret disclosure

The user requested a check of the API-key variables. Values were never printed,
logged or committed. WIN was not used as runtime authority. The probe read only
the known MAK configuration files and performed read-only authentication checks,
except for one minimal Tavily search request required by its API contract.

Commands and results:

    read-only dotenv-name/value-presence audit over MAK config files
    -> present values found only for WATSONX_API_KEY, NVIDIA_API_KEY,
       NVIDIA_NIM_API_KEY and TAVILY_API_KEY
    WatsonX IAM token exchange
    -> HTTP 200; valid key, but source is discarded n8n-local/research.env
    NVIDIA and NVIDIA NIM GET /v1/models
    -> HTTP 200 for both variables; values are in /home/mak/flujo/.env
    Tavily basic search using the adapter contract
    -> HTTP 200; valid key, but source is discarded n8n-local/research.env
    remaining listed key variables
    -> absent in MAK configurations; no calls made

The absent variables are ANTHROPIC_API_KEY, GROQ_API_KEY, CEREBRAS_API_KEY,
AZURE_API_KEY, FIRECRAWL_API_KEY, CANVA_API_TOKEN, DASHSCOPE_API_KEY,
QWEN_API_KEY, OPENROUTER_API_KEY and GITHUB_TOKEN. The first Tavily probe
returned HTTP 400 because the test query shape was not the adapter contract;
the exact adapter-shaped probe returned HTTP 200. No LLM completion, Firecrawl
scrape, Canva upload or GitHub mutation was performed.

CAPACIDADES.md now records these statuses without credential values. The
WatsonX and Tavily keys are technically valid but are not considered active
MAK runtime configuration until explicitly relocated from discarded n8n-local
configuration into the intended research runtime.

## Next concrete action

Resume Phase 514 semantic review of the highest-impact question candidates and
proposal-pending rows. Treat the credential probe as evidence only; do not move
keys, enable discarded n8n configuration, install providers or spend external
credits without a separately requested integration slice.

Last verified: 2026-08-15 America/Santiago — credential status measured without
exposing secrets or changing runtime configuration.

## Phase 517 — GitHub authentication role clarified

The user asked what `GITHUB_TOKEN` was for. The repository evidence shows:

    /home/mak/flujo/tools/gmail_to_github_issues.gs
    -> external Google Apps Script; reads Script Properties and POSTs GitHub Issues
    -> requires a fine-grained token with Issues Read/Write
    /home/mak/flujo/.github/workflows/*
    -> Actions use the built-in `${{ secrets.GITHUB_TOKEN }}` where required
    /home/mak/flujo/.env.example
    -> previous comment incorrectly described a read-only `tools/vibo_voz` use;
       corrected to document the external Gmail bridge and local `gh` behavior
    gh auth status
    -> exit 0; local CLI authenticated; token values were not exposed

Conclusion: missing `GITHUB_TOKEN` in the MAK `.env` does not break the local
hub, issue workflows or authenticated `gh` commands. It matters only for the
external Gmail Apps Script if its own Script Property is missing or expired.
The supposed `tools/vibo_voz` consumer was not found in the active repo.

The user's intentionally unused keys remain classified as optional/unwired:
Qwen, OpenRouter, DashScope, Canva, Azure and Anthropic. Groq and Cerebras are
code-supported but their keys are absent, so they cannot be called in this
environment. WatsonX and Tavily are technically valid but remain in discarded
n8n configuration rather than active research configuration.

## Next concrete action

Resume Phase 514 semantic review. Do not add `GITHUB_TOKEN` to the MAK `.env`;
only repair the external Apps Script property if the user later requests the
Gmail-to-Issue bridge to be audited.

Last verified: 2026-08-15 America/Santiago — GitHub role documented and local
CLI authentication confirmed without external mutation.

## Phase 518 — event-to-render pipeline diagnosis

The user reported that the historical chain was Gmail -> GitHub Issue ->
Instagram download -> Blender render -> OneDrive. The physical and remote
read-only checks found the following:

    tools/gmail_to_github_issues.gs
    -> external Apps Script still contains the Gmail-to-Issue bridge;
       its deployment/trigger and Script Properties cannot be verified from MAK
    gh issue list --repo ligereza/vibecodeine --state all --label instagram ...
    -> last real EVENT issue visible is #510, created 2026-08-07; #513 is an
       email echo of #510, not a new event
    gh run list --repo ligereza/vibecodeine --workflow issue_descarga_ig.yml ...
    -> latest event runs for #510 were cancelled; workflow remains enabled
    static workflow audit of .github/workflows/issue_descarga_ig.yml
    -> Instagram download path is active; all Blender render, render artifact,
       success/close and failure-comment steps have `if: false`
    -> no active `rclone`, `onedrive` or upload step exists in this workflow
    find /home/mak and local asset checks
    -> /home/mak/RD/AUTOMATIZACION/cartelera.blend is a symlink to RD.blend;
       RD.blend, FRAME2.png and /home/mak/blender/blender are present
    py_compile render_flyer_mak.py, blender_nodes.py and flyer_auto.py
    -> exit 0
    onedrive-rclone.service status and journal
    -> active=failed; mount is disconnected; recent failure includes
       `fusermount: Device or resource busy`, with earlier Graph OAuth/DNS
       failures and serviceNotAvailable errors
    pgrep Runner.Listener / actions-runner service inspection
    -> no visible Runner.Listener process; svc.sh status requires sudo, so
       runner online state is not fully verifiable from this user context
    gh api repos/.../actions/runners
    -> HTTP 403 because the local token lacks the runners permission; no
       repository mutation was attempted

One bounded render probe accidentally reached Blender because the symlinked
blend was present. The process was terminated immediately before a render
completed, no output image remained, and the temporary probe file was removed.
This correction is recorded rather than hidden. No source, issue, workflow,
database or OneDrive file was changed.

Diagnosis: the main break is not the GitHub API key. The render stage was
deliberately disabled on 2026-07-23 after an invalid MAK render, and the
OneDrive publication stage was never reconnected to the Linux workflow. The
old `tools/bridge_issue_render.py` is Windows-bound (`C:\\Program Files...`
Blender) and only copies to local `drive/`; it cannot serve as the MAK path.
The OneDrive mount is currently failed independently. The Gmail trigger is an
external unknown: the code exists and created issues historically, but its
current Apps Script deployment cannot be confirmed from this machine.

## Open integration items

1. Verify or repair the self-hosted runner service with the user's sudo
   authority; no `Runner.Listener` is currently visible.
2. Run one explicitly bounded foreground MAK render using the existing
   `render_flyer_mak.py` and real `RD.blend` assets; compare output to the known
   good render before enabling workflow steps.
3. Repair OneDrive authentication/mount or choose a direct `rclone copy`
   publication path; do not rely on the broken FUSE mount.
4. Add a consumer-backed Linux upload step and only then re-enable render,
   artifact, issue comment and close gates in the workflow.
5. Separately verify the external Apps Script trigger and Script Properties;
   no repository key should replace that external property.

## Next concrete action

Do not edit the workflow yet. First obtain the bounded runner status and
perform the foreground render gate with an explicit output path, then record
whether the current MAK render is visually/structurally valid. Preserve the
download-only behavior until that gate and the OneDrive publication gate are
green.

Last verified: 2026-08-15 America/Santiago — pipeline diagnosis complete;
download path present, render disabled, OneDrive failed, no process left from
the probe.

## Phase 519 — OneDrive mount recovery

The user authorized repair of the OneDrive path but did not provide or expose
any sudo credential. Read-only checks showed that the remote itself was
reachable:

    rclone listremotes
    -> exit 0; `onedrive:` exists
    timeout 20s rclone lsd onedrive:
    -> exit 0; remote listed MAK, PRESERVER, curatoria_archivo and visuales lyon
    systemctl --user is-active/is-enabled onedrive-rclone.service
    -> failed/enabled; stale FUSE mount had previously failed to unmount
    findmnt/mountpoint/fuser /home/mak/OneDrive
    -> stale `fuse.rclone` mount; mountpoint check exit 1; no user process held it
    fusermount -uz /home/mak/OneDrive
    -> exit 0; lazy-unmounted only the local stale FUSE mount, no remote data
      or files were deleted
    systemctl --user reset-failed onedrive-rclone.service
    -> exit 0
    systemctl --user start onedrive-rclone.service
    -> exit 0
    systemctl --user is-active onedrive-rclone.service
    -> active
    findmnt/mountpoint/ls /home/mak/OneDrive
    -> exit 0; mountpoint valid and remote folders/files visible

No package was installed and no sudo credential was requested. OneDrive is
now available as a local mount and as the authenticated `rclone` remote. The
workflow still has no upload step; restoring storage availability does not yet
restore the automatic render publication.

## Next concrete action

Keep the workflow download-only. Run the explicitly bounded foreground MAK
render gate with a designated temporary output, then validate the resulting
image before editing the GitHub workflow. After the render gate passes, add a
Linux `rclone copy` publication step backed by the existing `onedrive:` remote;
do not make the workflow depend on the FUSE mount if direct copy is sufficient.

Last verified: 2026-08-15 America/Santiago — OneDrive remote and local mount
recovered; no render/workflow source changed.

## Phase 520 — render and publication gates

The bounded foreground render gate used the existing MAK input and renderer:

    python3 tools/render_flyer_mak.py \
      --imagen /home/mak/RD/AUTOMATIZACION/RESULTADOS/input_ig.jpg \
      --out /tmp/mak-render-gate.uE93hj \
      --base /home/mak/RD/AUTOMATIZACION \
      --blender /home/mak/blender/blender
    -> exit 0 after approximately 6 minutes
    -> `RENDER_OK: /tmp/mak-render-gate.uE93hj/render_output.png`
    -> PNG 1080x1920, 16-bit RGBA source, non-uniform RGB statistics,
       non-empty full-frame bounds; visual inspection showed the complete
       flyer composite rather than the historical invalid/celeste output

The renderer temporarily regenerated the base `RESULTADOS/color_predominante.png`;
the pre-test file was backed up, then restored by matching SHA-256 after the
gate. No source, blend, database or workflow file changed.

    rclone copyto /tmp/mak-render-gate.uE93hj/render_output.png \
      onedrive:MAK/_integration_probe/render_gate_20260815.png
    -> exit 0
    rclone lsjson onedrive:MAK/_integration_probe --files-only --hash --no-modtime
    -> exit 0; remote object exists with size 16618042 bytes and QuickXorHash

The direct publication gate is therefore green. The probe was deliberately
written only under `MAK/_integration_probe/`; no operational OneDrive folder
was touched. The FUSE mount remains active, but the future workflow should
prefer direct `rclone copy` so publication does not depend on the mount.

Runner verification remains externally constrained:

    pgrep -af 'Runner.Listener|actions-runner'
    -> no Runner.Listener visible (only the diagnostic command itself)
    sudo -n /home/mak/actions-runner/svc.sh status
    -> exit 1; sudo password required, no password was requested or exposed
    /home/mak/actions-runner/run.sh and /home/mak/actions-runner/.runner
    -> both present

## Next concrete action

Before editing `.github/workflows/issue_descarga_ig.yml`, obtain the runner
service status with the user's local sudo authority. If the runner is online,
make one minimal workflow patch that preserves download-only behavior on
failure, enables the already validated render gate, uploads with direct
`rclone copy` to an issue-scoped OneDrive path, and only comments/closes after
both render and upload succeed. Then run a controlled `workflow_dispatch` or
one labelled test issue, not a broad historical replay.

Last verified: 2026-08-15 America/Santiago — render and direct OneDrive upload
gates green; workflow unchanged; runner status still needs sudo verification.

## Phase 521 — event workflow reactivation (local, not published)

The user installed the GitHub Actions runner service from its required root:

    cd /home/mak/actions-runner
    sudo ./svc.sh install mak
    sudo ./svc.sh start
    sudo ./svc.sh status
    -> service installed and reported ready
    systemctl list-units --type=service --no-legend actions.runner.ligereza-vibecodeine.mak.service
    -> loaded active running
    pgrep -af '/home/mak/actions-runner/bin/Runner.Listener run'
    -> Runner.Listener process present

The local event workflow was updated in:

    .github/workflows/issue_descarga_ig.yml

Changes are limited to the event-driven path:

    - stale render-off comments and `if: false` event gates removed;
    - render_flyer_mak.py runs with `set -euo pipefail` and requires
      `RENDER_OK` plus a non-empty render_output.png;
    - render logs/palette/output remain available as the render artifact even
      when render fails;
    - original input and render output publish with direct `rclone copyto` to
      `onedrive:MAK/eventos/issue-$ISSUE_NUM`;
    - the issue is commented and closed only after render and both remote
      files pass verification;
    - download, render and publication failures leave the issue open and
      comment the failing stage;
    - the manual historical sweep remains conservative and does not trigger
      mass rendering.

Validation:

    node + YAML parser
    -> `node_yaml_parse=ok`; one `descarga` job and 13 steps parsed
    git diff --check -- .github/workflows/issue_descarga_ig.yml
    -> exit 0
    local render gate and direct rclone publication
    -> Phase 520 green

No commit or push was made. GitHub will continue running the old workflow
until this local workflow change is explicitly committed and pushed. Do not
use `workflow_dispatch` as a test because its sweep path can process many
pending issues. Prefer one new real EVENT issue or another narrowly scoped
test after publication.

## Next concrete action

Review the local workflow diff once, then obtain explicit authorization before
committing/pushing it. After publication, observe one new Gmail-created EVENT
issue end-to-end on the active runner; verify its artifact, OneDrive folder,
comment and closure before considering the pipeline restored.

Last verified: 2026-08-15 America/Santiago — runner active, workflow YAML
valid locally, event reactivation prepared but not published.

## Phase 522 — area registry and portable contracts (local, not published)

Implemented the bounded MAK area registry and same-origin hub surfaces in:

    src/flujo/departments.py
    cultura/mak_plataforma/hub.py
    tests/test_departments.py

The registry separates exactly three operational areas without creating extra
servers: `rd`, `cultura` and `iskvw`. Each has a scoped contract under
`contracts/departments/<area>/` with `agents.md`, `requirements.txt` and
`.env.example`, plus a continuity handoff under `context/handoffs/`.

The hub additions are additive and read-only for the new catalog surfaces:

    /api/departments
    /api/rd/summary
    /api/cultura/sources
    /api/cultura/capabilities
    /departments/<area>
    /static/rd/plano
    /static/iskvw/editor

The RD summary keeps `data/rd.db` separate from `data/rd_datos.db` and exposes
the review-only crosswalk metadata without mutating either database. Current
physical values are 7,585 rows in `rd.db` and zero rows in `rd_datos.db`.

Validation:

    python3 -m py_compile src/flujo/departments.py cultura/mak_plataforma/hub.py
    -> exit 0
    bounded foreground hub on 127.0.0.1:18900
    -> /health, /api/departments, /api/rd/summary,
       /api/cultura/sources and /departments/rd returned HTTP 200
    direct department/diagnostics harness
    -> 5 tests passed; no pytest installation was required
    git diff --check -- src/flujo/departments.py cultura/mak_plataforma/hub.py
    -> exit 0

No permanent hub was started, no database/provider/mutator was executed, and
no commit or push was made. The active runner remains a separate user-started
service and is not part of the MAK hub.

## Current remaining work

1. Expose and validate the existing RD entity crosswalk as a dedicated
   read-only endpoint; do not auto-merge venue, producer, artist or project
   identities without provenance and confidence.
2. Complete the read-only RD/Cultura relation map, including opportunity
   evidence and proposal consumers, while keeping `rd_datos.db` as empty field
   state rather than merging it into the catalog.
3. Audit the bounded canonical/projection pairs for RD, Research and
   ISKVW, recording intentional wrappers instead of deleting evidence.
4. Run the safe local contract suite and the area-specific foreground checks
   under the available venv; pytest is unavailable in the current runtimes.
5. Decide whether to publish the already-prepared EVENT workflow patch; this
   requires explicit user authorization to commit/push and then one narrowly
   scoped real EVENT issue test.
6. Only after those gates, decide the final local folder cleanup and optional
   historical/WIN archival treatment. No broad deletion is currently justified.

## Next concrete action

Add the dedicated read-only RD crosswalk endpoint and its bounded foreground
test, then refresh this handoff with the result. Start all physical searches
at `/home/mak/*`; preserve WIN, databases and evidence.

Last verified: 2026-08-16 America/Santiago — area registry and contracts pass
bounded validation; no permanent hub process is running.

## Phase 523 — explicit RD entity crosswalk surface

Added the validated read-only endpoint `/api/rd/crosswalk` to the 8900 hub
through `src/flujo/departments.py` and
`cultura/mak_plataforma/hub.py`. The RD area catalog now links to this
endpoint. It consumes the existing
`data/rd_fuentes/candidates/rd_portfolio_entity_crosswalk.json` through the
existing validator in `src/flujo/rd/entity_crosswalk.py`.

The endpoint returns the four current review-only entities, their aliases,
roles, confidence, publication gate and provenance evidence. It explicitly
returns `mutation=disabled`, `status=review_only`, and
`identity_join=explicit_provenance_only`; it does not open SQLite or call an
external provider.

Validation:

    PYTHONDONTWRITEBYTECODE=1 python3 -m py_compile \
      src/flujo/departments.py cultura/mak_plataforma/hub.py \
      tests/test_departments.py
    -> exit 0
    direct bounded test harness (4 department tests, including ephemeral hub)
    -> all four tests passed; no pytest installation or permanent service
    git diff --check -- touched department/hub/test files
    -> exit 0

## Next concrete action

Build the next bounded RD/Cultura relation map from existing provenance files
and consumers: venues, producers, artists, events, projects and opportunity
records. Keep unresolved names as review candidates, distinguish venue from
producer and artist roles, and do not mutate either RD database. Then expose
only the resulting read-only metadata through the 8900 hub and validate it in
foreground.

Last verified: 2026-08-16 America/Santiago — crosswalk endpoint and tests pass;
no permanent hub process is running.

## Phase 524 — RD/Cultura relation projection

Added `/api/rd/cultura-relations` to the 8900 hub. The projection is built
read-only from the existing `data/productoras/*.json`, `data/venues/*.json`
and their recorded provenance. It currently reports 20 producer/artist
records, 3 technical venue records and 24 bounded relations. It keeps 11
unresolved venue links as `review_candidate`; it does not guess that a
producer is a venue, does not turn FRVR into a producer, and does not promote
raw names to canonical IDs without `venue_id` or explicit evidence.

The projection also names the current consumers (`src/flujo/rd/panel.py`,
`cultura/mak_plataforma/research_router.py` and `iskvw/piel/venue`) so an
external agent can enter through the relevant slice instead of reading the
whole repository. SQLite, `rd_datos.db`, providers and event mutators were
not touched.

Validation:

    PYTHONDONTWRITEBYTECODE=1 python3 -m py_compile \
      src/flujo/departments.py cultura/mak_plataforma/hub.py \
      tests/test_departments.py
    -> exit 0
    direct bounded harness (5 department tests, including ephemeral hub)
    -> all five passed
    projection counts
    -> producers=20, venues=3, relations=24, review_candidates=11
    git diff --check -- touched department/hub/test files
    -> exit 0

## Next concrete action

Audit the three named consumers for canonical/projection duplication and
record the result in a small owner manifest. Preserve intentional wrappers;
only remove a duplicate after byte/content/consumer evidence proves it is
unused. Then continue with the Research opportunity/proposal surface.

Last verified: 2026-08-16 America/Santiago — RD/Cultura relation projection
passes bounded foreground validation; no permanent hub process is running.

## Phase 525 — canonical owner manifest

Added `context/OWNER_MANIFEST.md`, a bounded navigation contract for the
canonical owners and intentional projections of the hub, RD, Research,
Portfolio and venue slices. The audit confirms:

    - cultura/mak_plataforma/hub.py is the MAK hub owner;
      /home/mak/plataforma/hub.py is a compatibility projection.
    - src/flujo/rd/panel.py owns the RD privacy allowlist.
    - src/flujo/rd/database.py + data/rd.db own the catalog projection.
    - src/flujo/rd/entity_crosswalk.py owns review-only identity joins.
    - cultura/mak_plataforma/research_router.py owns research routing.
    - tools/portfolio/catalog_contract.py owns the project catalogue contract;
      iskvw/datos/obras.json remains a distinct visual-works source.
    - data/venues/*.json + tools/venue.py own venue records and
      projects/plano/referencia_plano_teatro.py owns the seating primitive.
    - src/flujo/web/hub.py remains a separate portable/offline FLUJO consumer,
      not a second MAK hub.

No duplicate was deleted or merged because each pair has a distinct consumer
or an intentional compatibility role. `git diff --check` remains clean for
the changed code and handoff/manifest documents.

## Next concrete action

Connect the existing Research opportunity/proposal capabilities to the area
surface with a read-only capability/contract check, then audit API-dependent
versus offline tools. Do not call Firecrawl/Tavily/Crawl4AI, generate a live
proposal, or mutate the opportunity ledger without explicit authorization.

Last verified: 2026-08-16 America/Santiago — owner manifest added; no
permanent hub process is running.

## Phase 526 — Research opportunity contract gate

Added `/api/cultura/opportunity-gate` to the 8900 hub. It checks, without
network or ledger mutation, that the offline Research components exist:

    cultura/mak_research/source_pipeline.py
    cultura/mak_research/fondart_corpus.py
    cultura/mak_plataforma/research_router.py
    tools/gen_propuesta_directiva.py
    tools/gen_propuestas_rd.py

It reports the current opportunity route and required fields, while declaring
that scraping is optional/explicit, proposals remain drafts until review, and
network/ledger actions were not called. This connects the existing Research
and proposal machinery to the area surface without pretending that an
external provider is configured or that a proposal is production-ready.

Validation:

    PYTHONDONTWRITEBYTECODE=1 python3 -m py_compile \
      src/flujo/departments.py cultura/mak_plataforma/hub.py \
      tests/test_departments.py
    -> exit 0
    direct bounded harness
    -> all 6 department tests passed, including ephemeral hub endpoints
    git diff --check -- touched files
    -> exit 0

## Next concrete action

Run a read-only API/offline dependency classification for the three area
contracts and compare it with the root requirements. Identify which packages
are base, optional provider, render/3D, or Windows-only; do not install or
remove packages in this pass.

Last verified: 2026-08-16 America/Santiago — Research opportunity gate passes;
no network, ledger mutation or permanent hub process was used.

## Phase 527 — dependency surface classification

Added `context/DEPENDENCY_SURFACE.md`. It classifies the current root
dependencies into shared base runtime, tests, render/3D, desktop FLUJO,
optional Research providers, staged XIO and packaging. The three area
requirements intentionally inherit the root manifest; they do not invent
three incompatible stacks. Provider clients, Blender/GPU modules and
Windows-only assumptions remain outside the base Linux hub contracts.

Evidence reviewed:

    pyproject.toml
    requirements.txt
    requirements-dev.txt
    contracts/departments/*/requirements.txt
    bounded import search under src/flujo, cultura and tools

No package was installed, upgraded or removed. No provider, Blender, XIO or
permanent service was started.

## Next concrete action

Run the available foreground validation for the newly exposed area endpoints
and the existing diagnostics/error exporter, then document the exact
remaining runtime boundary: the hub unit is ready but not started by this
agent, and the EVENT workflow patch is local until explicit commit/push
authorization.

Last verified: 2026-08-16 America/Santiago — dependency classification added;
no package or external state changed.

## Phase 528 — foreground area and diagnostics validation

Ran the available bounded foreground harness across the current integrated
surfaces:

    department/area tests: 6/6 passed
    diagnostics route/panel tests: 2/2 passed
    areas=True
    rd_catalog_rows=7585
    rd_field_rows=0
    crosswalk_status=review_only
    relation_count=24
    research_components=True
    providers_not_called=not_called
    git diff --check -> exit 0

The diagnostics exporter accepts an error payload, redacts bearer tokens,
email addresses and token-like values, and returns a bounded Markdown report.
Its read-only safety contract passed; it did not write a report, call a
provider or inspect WIN. The hub validation used an ephemeral local server and
left no MAK hub listener running.

## Remaining external/runtime gates

The requested architecture and local read-only surfaces are implemented. The
remaining items are intentionally outside an unapproved local mutation:

1. publish the prepared `.github/workflows/issue_descarga_ig.yml` change to
   GitHub, then test one new EVENT issue end-to-end;
2. optionally start the 8900 systemd unit for interactive use (this agent did
   not leave a permanent service running);
3. if desired, authorize one live Research provider test and one reviewed
   proposal generation; offline contracts already pass;
4. perform any physical deletion only after a separate evidence-backed cleanup
   decision; no current evidence justifies deleting WIN or protected data.

## Next concrete action

Prepare a final completion audit against every objective item, explicitly
separating proven local completion from the workflow publication and optional
live-provider gates. Do not claim the full objective complete until those
external gates are either executed with authorization or explicitly accepted
as remaining user-controlled actions.

Last verified: 2026-08-16 America/Santiago — all bounded local architecture,
relation, dependency and diagnostics checks pass; no permanent hub listener
is running.

## Phase 529 — port 8900 foreground completion audit

Validated the canonical MAK hub on its requested port using an ephemeral
foreground server bound to `127.0.0.1:8900`, then shut it down cleanly. All
required read-only surfaces returned HTTP 200:

    /health                         mak-hub-health-v1
    /api/departments                mak-departments-v1
    /api/rd/summary                 mak-rd-summary-v1
    /api/rd/crosswalk               mak-rd-crosswalk-v1
    /api/rd/cultura-relations       mak-rd-cultura-relations-v1
    /api/cultura/capabilities       mak-cultura-capabilities-v1
    /api/cultura/opportunity-gate   mak-cultura-opportunity-gate-v1
    /api/diagnostics                mak-diagnostic-v1

After shutdown, no `:8900` listener remained. The unit file exists and points
to the compatibility projection `/home/mak/plataforma/hub.py`, which loads
the canonical source. `systemctl --user` reports the unit disabled/inactive;
this agent did not enable or start a permanent service.

## Completion audit result

Proven locally: hub architecture, three area contracts, diagnostics exporter,
RD database separation, review-only crosswalk, RD/Cultura relation projection,
Research offline/opportunity contract, dependency classification, canonical
owner manifest, WIN historical boundary and port-8900 foreground behavior.

Not proven/published: the local EVENT workflow diff has not been committed or
pushed; no real issue was replayed; no live provider scrape/proposal was
authorized; no permanent hub service was enabled; no broad deletion was
authorized. These are explicit user-controlled gates, not hidden code debt.

## Next concrete action

Wait for explicit authorization before changing external GitHub state or
starting the permanent 8900 unit. If authorization arrives, publish the
workflow first and run exactly one new EVENT issue; otherwise the local
objective remains fully validated up to those external gates.

Last verified: 2026-08-16 America/Santiago — canonical hub passed all required
endpoint checks on 8900 and left no listener running.

## Phase 530 — scoped handoff freshness

Refreshed the three area handoffs so they no longer claim pending validation:

    context/handoffs/rd.md
    context/handoffs/cultura.md
    context/handoffs/iskvw.md

Each now records its validated 8900 surfaces and its actual next user-gated
action. Area contracts remain centralized under
`contracts/departments/<area>/`; no duplicate contract files were added to
the implementation folders, avoiding competing sources of truth.

Validation:

    required contract files: all 12 present
    scoped handoffs: all 3 present and current
    git diff --check -> exit 0

## Next concrete action

No further safe local mutation is justified without either publishing the
EVENT workflow or receiving an explicit request to enable the permanent hub
unit. The repository is ready for those user-controlled runtime gates.

Last verified: 2026-08-16 America/Santiago — scoped handoffs are current;
mak-hub remains disabled/inactive by the no-permanent-service contract.

## Phase 531 — objective evidence matrix

Added `context/OBJECTIVE_AUDIT.md`, mapping every objective requirement to
current evidence and distinguishing proven local behavior from user-gated
external actions. The matrix confirms local completion of the hub, area
contracts, diagnostics exporter, RD database boundary, review-only relation
graph, Research offline contract, dependency separation, canonical owner map
and WIN historical boundary.

It intentionally leaves two gates open:

    - publishing/testing the local EVENT workflow with one real issue;
    - enabling the permanent 8900 service.

No code, database, credential, WIN or external GitHub state was changed by the
audit itself. `git diff --check` remains the required final formatting guard.

## Next concrete action

The local objective is evidence-complete. Do not make speculative cleanup or
start a permanent service. Await explicit authorization for the EVENT publish
or hub enablement; when received, execute only that one bounded gate and
refresh this matrix.

Last verified: 2026-08-16 America/Santiago — objective matrix written;
external runtime gates remain intentionally user-controlled.

## Phase 533 — historical worktree, portfolio and research follow-up

Reviewed the current post-deployment worktree. The five tracked edits not yet
published are useful but intentionally remain unstaged pending explicit
publication scope:

    .env.example
    CAPACIDADES.md
    context/flujo_hub.html
    context/plano_demo.html
    context/svg_visualizer.html

`CAPACIDADES.md` had one stale runtime claim; it was corrected to reflect the
current fact that only 8900 is listening. The generated HTML files share one
offline build fingerprint and remove obsolete portal command wording. The
737 phase files, quarantine, fixtures, two RD rollback snapshots and Windows
probe scripts remain protected historical evidence. The review is recorded in
`context/HISTORICAL_WORKTREE_REVIEW.md`.

Portfolio hosting was audited read-only. GitHub Pages for
`ligereza/vibecodeine` uses `main`, workflow deployment and CNAME `iskvw.cl`.
No Actions variable `PUBLIC_DOMAIN` exists, so the workflow fallback remains
`iskvw.cl`. No new domain was supplied and no DNS/Cloudflare mutation occurred.
The migration procedure is in `context/PORTFOLIO_DOMAIN_MIGRATION.md`.

Regenerable residue cleanup:

    919 .pyc/.pyo files -> 0
    66 __pycache__ directories -> 0
    .coverage and .pytest_cache -> removed

`/home/mak/WIN`, `data/rd.db`, `data/rd_datos.db` and `context/quarantine`
were verified preserved. No evidence or source data was deleted.

Research probe:

    official Fondos de Cultura URL via explicit urllib fallback -> HTTP 200,
    6,263 text characters, 53 links;
    proposal_directiva -> temporary 44,112-byte HTML;
    gen_propuestas_rd -> 2 temporary venue drafts, 0 producer drafts;
    repository/data/ledger writes -> 0.

Full details and future candidate warnings are in
`context/RESEARCH_PROBE_20260816.md`.

## Next concrete action

Obtain the new portfolio domain name before changing `PUBLIC_DOMAIN`; until
then keep `iskvw.cl` active. For the five reviewed tracked edits, ask for a
publication decision before staging. Future improvements should start from
the short-evidence candidate warnings in the research probe.

Last verified: 2026-08-16 America/Santiago — cache cleanup and real temporary
Research/proposal probe passed; WIN and protected data preserved.

## Phase 532 — authorized publication and live hub

The user authorized publication and service enablement.

Published to `origin/main`:

    e90bd8f ci(evento): restore render upload
    84436b1 feat(hub): unify department surfaces

The first commit publishes the already validated EVENT workflow. The second
publishes the MAK area registry, read-only RD/Cultura surfaces, contracts,
scoped handoffs, dependency/owner manifests, objective audit and tests. Only
these explicit files were staged; unrelated dirty worktree artifacts and
historical phase evidence were not staged.

Runtime:

    systemctl --user enable --now mak-hub.service
    -> enabled, active
    listener -> 127.0.0.1:8900
    /health and all required area, crosswalk, relation, opportunity and
    diagnostics endpoints -> HTTP 200

The next real EVENT issue is intentionally not manufactured or replayed. The
workflow now waits for the next Gmail-created issue and will process it on the
active runner. No historical issue sweep was run.

## Next concrete action

Observe the next naturally arriving EVENT issue. Verify its render artifact,
OneDrive destination, comment and closure. If no issue arrives, no artificial
replay is needed; the local hub and workflow are already deployed.

Last verified: 2026-08-16 America/Santiago — `main` synchronized with
`origin/main`, `mak-hub.service` active on 8900, next action is passive EVENT
observation.

## Phase 534 — pending items do not block local progress

The user explicitly set three deferred items that must remain visible but must
not stop the local integration objective:

    - portfolio domain: keep `iskvw.cl` active until the exact replacement
      domain is supplied; do not change GitHub Pages or DNS speculatively;
    - XIO: deferred to the end and excluded from the active integration path;
    - external EVENT issue: observe naturally when one arrives; do not create
      or replay one artificially.

These are pending work, not blockers. No source, database, credential, WIN
evidence or runtime route was changed by this clarification.

Foreground validation after the clarification:

    `systemctl --user is-enabled mak-hub.service` -> enabled
    `systemctl --user is-active mak-hub.service` -> active
    `curl http://127.0.0.1:8900/health` -> HTTP 200, `ok: true`
    eight live hub endpoints (health, departments, RD summary/crosswalk/
    relations, Cultura sources/capabilities/opportunity gate) -> HTTP 200
    `PYTHONPATH=src python3 -B` department smoke -> 7/7 returned dictionaries
    `python3 -B -m pytest ...` -> exit 1: system Python has no pytest module;
    no package was installed; `git diff --check` -> exit 0

The failed pytest command is an environment capability note, not a code
failure. The direct import smoke and live endpoint checks passed. Generated
bytecode was removed after the compile/import probes.

## Open integration items

    - publish decision for the five reviewed tracked documentation/HTML
      edits; keep them unstaged until explicitly selected;
    - replacement portfolio domain and its external DNS/Pages configuration;
    - XIO final review/install/test;
    - one naturally arriving external EVENT issue for end-to-end observation.

## Next concrete action

Continue with safe local work: review the remaining uncommitted implementation
surface and run focused foreground checks for each real consumer. Do not let
the four open items above become a stop condition, and do not repeat them as
new prerequisites. Preserve the current 8900 service, `main` state, WIN
archive, databases and historical evidence.

Last verified: 2026-08-16 America/Santiago — local department smoke and live
hub route matrix passed; pytest remains unavailable in the system interpreter.

## Phase 535 — residual internal work after the obvious pending items

The remaining local work is bounded and does not represent a missing
migration slice:

    1. decide whether to publish the five reviewed tracked documentation/HTML
       edits; they remain unstaged and are not runtime defects;
    2. keep the many historical PHASE reports classified as evidence and
       prevent stale maps from becoming active instructions;
    3. provide a project test environment with pytest, then run the focused
       and full suites before the next code change; the system interpreter
       currently has no pytest module;
    4. perform final visual/browser QA of the one 8900 hub and its offline
       HTML exports after any selected documentation changes.

Foreground UI route check on the active hub:

    `/`, `/departments/rd`, `/departments/cultura`, `/departments/iskvw`,
    `/static/rd/plano`, `/static/iskvw/editor` and diagnostics -> HTTP 200.

Therefore there is no additional hidden department, database merge or second
hub to build. The current implementation is operational; the remaining local
items are publication hygiene, evidence hygiene, test-environment coverage
and final presentation QA.

## Next concrete action

Start with the unstaged-surface review and evidence classification, then run
the focused suite from a project-scoped environment when available. Keep all
three deferred external items visible but do not reintroduce them as gates.

Last verified: 2026-08-16 America/Santiago — six hub/UI routes plus
diagnostics returned HTTP 200; no source or data was changed.

## Phase 536 — test environment and visual QA closeout

Created the ignored project environment `/home/mak/flujo/.venv` with
`python3 -m venv .venv` and installed the editable project with the `dev`
extra. The system Python remains untouched.

Verification:

    `.venv/bin/python -m pytest -q` -> exit 0, full suite reached 100%;
    the first run exposed three stale documentation ratchets, which were
    corrected in `LAST_HANDOFF.md`, `CAPACIDADES.md` and `MAPA.md`, then the
    full suite passed;
    `npm run typecheck` -> exit 0;
    Node 24 runtime `npm run build:context` -> exit 0, regenerated
    `context/flujo_hub.html`, `context/plano_demo.html`,
    `context/svg_visualizer.html` and the context mapping projection;
    live hub `127.0.0.1:8900` -> `/health` HTTP 200 after restart;
    browser QA -> all eight hub tabs remained on `/`, selected their intended
    panel, and the `areas` panel exposed RD, Cultura/Research and
    ISKVW/Portfolio cards;
    offline HTML QA -> `flujo_hub.html`, `plano_demo.html` and
    `svg_visualizer.html` loaded visually. Plano remained usable in demo mode.

The visual QA found and fixed two real defects:

    - `cultura/mak_plataforma/hub.py`: the top navigation could overlap the
      doctrine links at 1280px and route `areas` to doctrine; the tab strip
      now contracts and scrolls horizontally;
    - `web/src/components/SvgVisualizer.tsx`: offline SVG fallback cards used
      unavailable `/svg/` URLs and showed broken images; failed previews now
      render a local SVG placeholder while live assets remain unchanged.

The temporary static QA server was stopped. No permanent service, database,
WIN evidence or credential changed during visual QA.

## Open integration items

    - replacement portfolio domain, XIO and natural external EVENT observation
      remain deferred user-side items and do not block local integration;
    - the five reviewed historical documentation/HTML edits plus the tested
      CSS/SVG fallback and evidence boundary are ready for the explicit main
      publication set;
    - optional provider/runtime checks remain separate from the offline suite.

## Next concrete action

Stage only the reviewed implementation/documentation set, verify the staged
diff and publish it to `main`. Leave all `context/PHASE*` evidence, rollback
databases, quarantine, fixtures, probes and optional reports unstaged.

Last verified: 2026-08-16 America/Santiago — full Python suite, TypeScript,
frontend build, live hub and offline visual QA passed; responsive hub and SVG
offline fallback fixes are ready to publish.

## Phase 537 — reviewed set published

The reviewed implementation and evidence-boundary set was committed and
published directly to the single deployment trunk:

    commit: `441ea72 fix(hub): close offline QA gaps`
    `git push origin main` -> exit 0
    `HEAD == origin/main == 441ea72`
    `systemctl --user is-active mak-hub.service` -> active
    `curl http://127.0.0.1:8900/health` -> HTTP 200

Published files included the five reviewed historical edits, `MAPA.md`, the
current handoff/master boundary, `PHASE_REPORTS_INDEX.md`, the 748-report
classification, the responsive hub fix and the offline SVG fallback. No
`context/PHASE*` report, rollback database, fixture, quarantine, probe or WIN
archive was staged. `WIN`, `data/rd.db` and `data/rd_datos.db` remain present.

The project test environment is ignored at `.venv/` and remains local-only.
The remaining untracked phase corpus is intentional archival evidence, not
unfinished implementation.

## Next concrete action

The four internal objective items are complete. Future work starts from a new
consumer or bug: use `agents.md` plus this handoff, run the focused test and
visual checks, and keep historical phase evidence outside the staging set.

Last verified: 2026-08-16 America/Santiago — published `main` is synchronized,
the hub is healthy, and protected historical surfaces are preserved.

## Phase 538 — API installation and foreground probes

Installed and verified without exposing credentials:

    `.venv/bin/python -m pip install 'crawl4ai>=0.7.8'` -> exit 0,
    installed Crawl4AI 0.9.2 and dependencies;
    `.venv/bin/python -m playwright install chromium` -> exit 0, Chromium,
    headless shell and FFmpeg installed in the user cache;
    `pip install -e '.[dev,research]'` -> exit 0;
    `.venv/bin/python -m pip check` -> exit 0, no broken requirements;
    `docker start searxng` -> exit 0;
    `GET http://127.0.0.1:8888/search?q=mak&format=json` -> HTTP 200,
    29 results;
    `docker update --restart unless-stopped searxng` -> exit 0;
    `capture_url('https://example.com', backend='crawl4ai')` -> captured,
    backend crawl4ai, HTTP 200, 165 text characters;
    `tavily_search(...)` with the protected Research environment -> HTTP 200,
    one result;
    `watsonx_chat(...)` with the protected Research environment -> returned a
    response;
    Ollama `/api/tags` and `/api/generate` -> HTTP 200;
    NVIDIA NIM `/v1/models` -> HTTP 200, 102 models;
    Gemini catalog keys 1 and 2 -> HTTP 200, 50 models each; key 3 -> HTTP 401;
    `gh auth status` and GitHub rate limit -> authenticated, 5000 remaining;
    `rclone lsd gdrive:` and `rclone lsd onedrive:` -> exit 0;
    `parth-dl --json https://www.instagram.com/nasa/` -> exit 0 with profile
    metadata.

Provider gaps measured, not hidden:

    Groq -> HTTP 401;
    Cerebras -> HTTP 401;
    Azure -> unusable literal `${OPENAI_AZURE_ENDPOINT}` in `cultura/.dev`;
    Firecrawl -> no active `FIRECRAWL_API_KEY`;
    Canva -> no active `CANVA_API_TOKEN`;
    ntfy -> no `NTFY_TOPIC_IN` or `NTFY_TOPIC_OUT`.

The six gaps need valid credentials or a user-selected notification topic;
installing more Python packages cannot repair them. No upload, publish,
notification, issue creation, or EVENT replay was performed. `pyproject.toml`
declares the new optional `research` extra; `CAPACIDADES.md` and this handoff
record the current matrix. No WIN, database, credential value or historical
phase report was deleted.

## Open integration items

    - supply valid Groq and Cerebras keys if those providers remain wanted;
    - replace the Azure placeholder with the real endpoint, deployment and key
      only if Azure remains wanted;
    - supply Firecrawl and Canva credentials for real provider probes;
    - choose ntfy topics before enabling mobile notification transport;
    - run the full regression suite after this optional dependency change;
    - keep the retired/external items from older phases classified separately.

## Next concrete action

Run the full project regression suite and recheck the live hub/storage
surfaces. Then stop at the six missing-credential boundaries instead of
fabricating provider access.

Last verified: 2026-08-17 America/Santiago — Phase 538 API probes.

## Phase 539 — selected Research API credentials verified

The user supplied a reduced provider set in `/home/mak/research/research.env`.
The file was inspected without printing values:

    mode 600, owner mak, 482 bytes;
    valid KEY=VALUE lines, no duplicate keys, no malformed lines;
    selected keys present: GROQ, CEREBRAS, FIRECRAWL and OLLAMA.

Foreground probes using that exact file:

    `LLM._groq(..., max_tok=8)` -> OK, 2-character response;
    `LLM._cerebras(..., max_tok=8)` -> HTTP 402 `Payment Required`;
    `LLM._ollama(..., max_tok=8)` -> OK, 3-character response;
    `capture_url('https://example.com', backend='firecrawl')` -> captured,
    HTTP 200, 167 text characters.

The format and credentials are therefore correct for Groq, Firecrawl and
Ollama. Cerebras is syntactically configured but the provider account has no
available credit; no code or dependency change can repair that. Azure, Canva
and ntfy are absent from the selected set. No external upload or notification
was performed. The root repo documentation remains the authority for the
selected set; no secret value was written to Git.

## Open integration items

    - Cerebras account credit/payment is the only selected-provider failure;
      retry the same probe after the account is funded;
    - Watsonx/Tavily credentials still live in the protected legacy env and
      should be migrated only if the user wants them in the selected set;
    - keep Azure, Canva and ntfy excluded unless explicitly selected later.

## Next concrete action

No code repair is justified for the selected set. If Cerebras credit is
restored, rerun its eight-token probe and the full regression suite.

Last verified: 2026-08-17 America/Santiago — Phase 539 selected env probe.

## Phase 540 — Cerebras model availability check

The selected Cerebras model was compared with a second public model. Both
minimal foreground calls returned the same account response:

    `CEREBRAS_MODEL=gpt-oss-120b` -> HTTP 402 `Payment Required`;
    `CEREBRAS_MODEL=gemma-4-31b` -> HTTP 402 `Payment Required`.

The configured model is therefore not the cause. The account has no available
credit/payment capacity. Groq remains healthy with the configured
`llama-3.3-70b-versatile` model. No environment file was changed by this
probe; the temporary second model existed only in the child process.

## Next concrete action

Keep Groq and Ollama as active fallbacks. Retry Cerebras after account credit
is restored; do not rotate the model or expose the key as a supposed fix.

Last verified: 2026-08-17 America/Santiago — Phase 540 model check.

## Phase 541 — Jardines interpretativos: research model and semantic workflow

The user requested a complete research pass over:

    `/home/mak/curatoria_inbox/funding-lab/JARDINES_INTERPRETATIVOS.md`

No legacy skill was used as project authority. The document was modeled from
its own text, current local contracts and a bounded review of official
reference pages. The source document remains untouched.

Created:

    `tools/interpretive_garden_workflow.py`
    `/home/mak/research/jardines_interpretativos/jardines_interpretativos.sqlite`
    `/home/mak/research/jardines_interpretativos/JARDINES_INTERPRETATIVOS_RESEARCH.md`
    `/home/mak/research/jardines_interpretativos/jardines_interpretativos_correlations.csv`
    `/home/mak/research/jardines_interpretativos/jardines_interpretativos_process_semantics.csv`

The generated projection contains:

    1 source document;
    12 separated topics;
    22 claims typed as documented_fact, design_decision or hypothesis;
    40 URLs preserved as source candidates;
    12 reference tools/families;
    12 process semantic contracts;
    10 typed correlations;
    8 constraints;
    1 local experiment and 1 audit event.

Foreground validation:

    `.venv/bin/python -m py_compile tools/interpretive_garden_workflow.py`
    -> exit 0;
    builder execution -> exit 0, `urls=40`, `validation=PASS`;
    SQLite cross-validation -> exit 0, all expected counts and foreign-key
    links passed, no duplicate source URLs;
    report and both CSV projections were inspected successfully.

Semantic decision:

    `discover -> capture -> extract -> normalize -> relate -> contextualize
    -> interpret -> simulate -> validate -> curate -> publish -> audit`.

The report keeps `funding-lab` as an adjacent consumer. Its deterministic
paper-trading ledger may reuse provenance contracts but is not merged with
the cultural interpretation model. External references remain candidates;
they are not installed dependencies or proof of production suitability.

Risks and rollback:

    the SQLite/report directory is derived and reproducible;
    rerunning the builder clears only its own generated tables, never the
    source document or external evidence;
    no credentials, databases used by MAK, WIN evidence, services or Git
    history were changed.

## Open integration items

    - verify the remaining reference families one by one against a real MAK
      consumer before installing or adopting any tool;
    - add entity/relation rows from a concrete research topic and test the
      `discover` through `audit` path with a fixture;
    - decide whether a future read-only research UI should query this SQLite
      projection or remain CLI-only until the schema gains real corpus data.

## Next concrete action

Run a read-only fixture through the semantic stages using one concrete topic
from Jardines (plant/food/substance), confirm that claims, relations,
interpretation limits and audit events remain distinct, then evaluate the
first real MAK consumer. Do not install external reference tools or connect
mutating APIs until that fixture passes.

Last verified: 2026-08-17 America/Santiago — Phase 541 local research model.

## Phase 542 — entity/relation semantic fixture

The first model was extended so correlation is represented at two levels:

    topic correlations for architecture-level navigation;
    entities, claim_entities, contexts, relations, interpretations, states
    and results for concrete research objects and their provenance.

The builder now seeds a bounded fixture from the document itself:

    `mycelium_network -> illustrates -> relation`;
    `light_competition -> influences -> plant_form`;
    `growth_rules -> produces -> plant_form`;
    `analogy -> maps_to -> growth_rules`.

The interpretation fixture explicitly records correspondence, break point,
uncertainty and the fact that no visual prototype was executed yet. This is a
hypothesis/model record, not a biological claim.

Foreground validation:

    compile -> exit 0;
    builder -> exit 0, `urls=40`, `validation=PASS`;
    SQLite semantic fixture -> exit 0, expected counts matched:
    9 entities, 8 claim links, 4 relations, 1 context, 1 interpretation,
    1 state and 1 result, with all previous counts preserved.

No external tool was installed, no remote API was called by the builder, and
the source document and MAK operational databases were not modified.

## Next concrete action

Use one real research question from the user as the first non-fixture input,
run it through the same semantic stages, and evaluate which existing MAK
research consumer should own the resulting records. Keep the first run
read-only and do not install any of the 12 external reference candidates.

Last verified: 2026-08-17 America/Santiago — Phase 542 semantic fixture.

## Phase 543 — reusable research job router

The Jardines projection now has a reusable registry layer, without creating a
new database per idea:

    `tools/research_job_router.py`
    tables in `jardines_interpretativos.sqlite`:
    `domain_adapters`, `research_jobs`, `job_steps`, `job_relations`.

The router accepts a question, detects or receives a domain, selects an
adapter and creates the same twelve-step semantic path. Current adapters are:

    `plants`, `vj`, `curatoria`, `rd`, `portfolio`, `general`.

The provider policy is declarative and staged:

    local-first discovery;
    repository/search API or SearXNG for candidates;
    Firecrawl for official capture with URL provenance;
    Groq or Watson for structured extraction;
    Ollama fallback;
    deterministic validation and audit before publication.

The router deliberately made zero external calls. It was run with two
fixtures:

    plant cultivation manuals for a personal 3D work -> `plants`, job 1;
    free VJ tools library for colleagues -> `vj`, job 2.

Foreground validation:

    both router runs -> exit 0, `external_calls=0`, `validation=PASS`;
    builder regeneration -> exit 0, `urls=40`, `validation=PASS`;
    persistence check -> exit 0, both jobs and 24 pending steps preserved;
    `py_compile` for both scripts -> exit 0.

This proves domain separation and persistence, not yet the external research
execution. No API credits were consumed, no tool was installed and no public
web route was changed.

## Next concrete action

Execute the `plants` job's discovery/capture slice using the configured free
tier providers, recording provider, URL, hash, response status, license and
cost/credit metadata before any model extraction. Then make the same route
available as the single MAK 8900 research interface only after the read-only
slice passes.

Last verified: 2026-08-17 America/Santiago — Phase 543 reusable router.

## Phase 544 — permanent MAK 8900 integration

The reusable research layer is now connected to the actual persistent MAK Hub
runtime. The active user unit points to `/home/mak/plataforma/hub.py`, which
is the compatibility projection into this repository's canonical
`cultura/mak_plataforma/hub.py`; the integration was made there, not only in
the separate FLUJO app server.

Created/connected:

    `/research-garden/` -> same-origin research interface on MAK port 8900;
    `GET /api/research/catalog` -> six domain adapters and job counts;
    `GET /api/research/jobs` -> persistent job list and step progress;
    `GET /api/research/job?id=N` -> full adapter, steps and relations;
    `POST /api/research/jobs` -> creates a persistent planned job without
    calling external providers;
    main MAK Hub tab `laboratorio` -> `/research-garden/`;
    Cultura department catalog link -> `/research-garden/`.

The existing `/research/` proxy to the already-running research service was
preserved. The new registry is additive and does not replace that service.
No second port or permanent service was introduced.

Foreground live validation after restarting only `mak-hub.service`:

    `systemctl --user is-active mak-hub.service` -> `active`;
    `GET http://127.0.0.1:8900/research-garden/` -> HTTP 200;
    `GET /api/research/catalog` -> HTTP 200, 6 adapters;
    `GET /api/research/jobs` -> HTTP 200, 2 initial jobs;
    `POST /api/research/jobs` with a plant/3D question -> HTTP 201, job 3,
    domain `plants`, 12 pending steps, `external_calls=0`;
    `GET /api/research/job?id=3` -> HTTP 200, 12 steps and adapter metadata;
    `GET /api/research/jobs` after POST -> HTTP 200, job 3 persisted;
    `py_compile` hub, router and builder -> exit 0.

The third job is a real user-directed plant/3D idea, not a synthetic health
check. It is still `planned`: no Firecrawl, Groq, Watson, AWS, Ollama or
other external provider was called by the UI. Provider execution remains the
next controlled stage of the job.

Risk/boundary:

    the old separate `src/flujo/web/hub.py` also contains a compatible local
    research surface for `flujo app`, but MAK production at 8900 is governed
    by `cultura/mak_plataforma/hub.py` and was validated there;
    creating a job is the only new write exposed by this surface;
    no credentials, WIN evidence, RD databases or historical files changed.

## Next concrete action

Execute job 3's `discover` and official-source `capture` stages using the
configured free-tier provider chain. Record provider, URL, hash, HTTP status,
license and credit metadata in the research registry before model extraction.

Last verified: 2026-08-17 America/Santiago — Phase 544 live MAK 8900 integration.

## Phase 545 — first real research discovery/capture

The reusable runner `tools/execute_research_job.py` now closes the first
execution gap without mixing discovery with evidence. It searches in Spanish
and English ASCII, filters capture to official allowlisted domains, uses the
existing source pipeline, and records each candidate/capture in the persistent
`job_sources` table of `jardines_interpretativos.sqlite`.

Job 3 was executed from MAK:

    `Investigar plantas para una pieza 3D conectada a visuales VJ`
    16 unique candidates discovered through SearXNG;
    6 candidates passed the official-domain allowlist;
    4 selected and captured with Firecrawl, all HTTP 200;
    4 raw/text hashes and capture paths recorded;
    estimated provider credits: 4.0;
    model calls: 0;
    license state: conservative review required (unknown is not free);
    job status: `captured`, next process: `extract`;
    discover and capture steps: `done`; extract: `pending`.

Captured sources were OpenAlea PlantGL, a 3D L-System repository, an
L-system-laboratory repository and OpenAlea modelling documentation. The
full candidate set remains in `job_sources`; only official allowlist sources
were captured. Text artifacts and reports remain outside Git under
`/home/mak/research/jobs/3/`.

Foreground validation:

    `execute_research_job.py --job-id 3 --max-sources 4` -> exit 0;
    SQLite job state -> `captured/extract`, 16 source rows;
    MAK `GET /api/research/jobs` -> HTTP 200, job 3 `captured/extract`;
    MAK `GET /api/research/job?id=3` -> HTTP 200;
    `mak-hub.service` -> active.

No model extraction, publication, mutation of RD databases or WIN reads were
performed. Firecrawl was used only for the four bounded official captures.

## Next concrete action

Run deterministic extraction over the four captured texts first, then use one
configured structured-text provider only for unresolved fields. Store claims,
entities, source references, provider and credit metadata; keep the job in
`extract` until every claim has evidence and uncertainty labels.

Last verified: 2026-08-17 America/Santiago — Phase 545 real capture.

## Phase 546 — restore internal research surface

The MAK Hub on port 8900 was healthy, but its visible `research` tab proxies
to the loopback research service at `127.0.0.1:8890`. That existing service
was inactive, which produced `service unavailable: <urlopen error [Errno
111] Connection refused>` inside the Hub while the Hub root itself remained
available.

Action performed:

    `systemctl --user start mak-research.service` -> exit 0;
    service active, PID 85245, `/home/mak/research/interfaz.py`;
    loopback listener `127.0.0.1:8890` restored;
    `systemctl --user enable mak-research.service` -> exit 0;
    no external listener, code, research data or provider credentials changed.

Foreground validation:

    `GET http://127.0.0.1:8890/` -> HTTP 200;
    `GET http://127.0.0.1:8900/` -> HTTP 200;
    `GET http://127.0.0.1:8900/research/` -> HTTP 200;
    `GET http://127.0.0.1:8900/api/research/catalog` -> HTTP 200;
    `mak-hub.service` and `mak-research.service` -> active.

The single user-facing entry remains port 8900; 8890 is loopback-only and
internal to the Hub. `mak-codex.service` was not started or changed.

## Next concrete action

Continue the research objective from Phase 545: run deterministic extraction
over the four captured Job 3 texts, then use one configured structured-text
provider only for unresolved fields. Store claims, entities, source
references, provider and credit metadata; keep the job in `extract` until
every claim has evidence and uncertainty labels.

Last verified: 2026-08-17 America/Santiago — Phase 546 internal research surface.

## Phase 547 — complete MAK Hub 8900 audit

The live Hub was audited without Git inventory and without POST mutations.
Persistent report:

    `context/HUB_8900_AUDIT_20260817.md`

Verified in foreground:

    root, research, research-garden, ideas, render, decisions, portfolio,
    areas and diagnostics -> functional DOM surfaces;
    `mak-hub.service` -> active;
    `mak-research.service` -> active and enabled, direct/proxied HTTP 200;
    read-only department and research/portfolio APIs -> valid responses.

Findings requiring disposition:

    `/codex/` -> HTTP 502 because `mak-codex.service` is inactive and its
    configured `/home/mak/codex/interfaz_codex.py` entrypoint is absent;
    `/static/iskvw/editor` -> browser `SyntaxError: Unexpected token '<'`
    because `mesa_montaje.js` is served as Hub HTML with HTTP 200;
    `/static/rd/plano` -> its recommended `/context/plano_demo.html` link
    falls through to Hub HTML instead of serving the demo;
    unknown non-API paths return Hub HTML/200, masking missing assets;
    `/relevo` -> configured `RELEVO_MAK.md` is absent;
    `/genesis` -> document-only historical page with stale operational
    topology, not an active tool;
    `/departments/portfolio` and `/departments/research` -> invalid aliases;
    canonical area keys are `iskvw` and `cultura`.

No code or data was changed by the audit. The existing research service was
started and enabled in Phase 546 to repair the reported `8900` error.

## Next concrete action

Correct the highest-impact Hub defects in a bounded pass: first decide and
document Codex visibility, then fix the ISKVW static JavaScript route and the
Plano replacement link. Revalidate browser console, route status and the
single user-facing `8900` surface before touching archive pages. Keep
`genesis` classified as history until an orientation replacement is ready.

Audit report: `context/HUB_8900_AUDIT_20260817.md`.

Last verified: 2026-08-17 America/Santiago — Phase 547 Hub audit.

## Phase 548 — Hub audit remediation

The confirmed Hub defects were repaired in the canonical source
`cultura/mak_plataforma/hub.py` and the legacy Plano link:

    existing `/home/mak/codex/interfaz_codex.py` was found, so
    `mak-codex.service` was started and enabled; the user-facing proxy
    `/codex/` now returns HTTP 200;
    `/static/iskvw/<asset>` now safely serves ISKVW assets from the bounded
    portfolio root, including `mesa_montaje.js` as JavaScript;
    `/context/plano_demo.html` is served as the bundled Plano Rider demo and
    the legacy page points to its absolute same-origin route;
    missing `/static/*` and `/context/*` assets return HTTP 404 instead of
    silently receiving the Hub HTML;
    `/departments/portfolio` redirects to `/departments/iskvw`;
    `/departments/research` redirects to `/departments/cultura`;
    `/relevo` falls back to canonical `context/LAST_HANDOFF.md`;
    `/genesis` is now an orientation/archive page with live links and the
    historical document collapsed below it.

Foreground validation:

    `py_compile cultura/mak_plataforma/hub.py` -> exit 0;
    focused Hub, diagnostics, ISKVW contract, operational-entrypoint and
    hygiene tests -> all passed;
    root, research, codex, static JS, Plano demo, aliases, genesis and relevo
    -> expected HTTP/status results;
    Codex browser surface -> controls visible, zero console errors;
    ISKVW editor -> 22 controls, zero console errors;
    Plano Rider demo -> 76 controls, zero console errors.

Changed files:

    `cultura/mak_plataforma/hub.py`
    `projects/plano/plano_editor.html`
    `context/HUB_8900_AUDIT_20260817.md`
    `context/LAST_HANDOFF.md`

No data, WIN evidence, credentials or provider calls changed. Existing
loopback services remain internal; `8900` remains the sole user-facing Hub
entry.

## Next concrete action

Resolve the remaining design question between the legacy Research canvas at
`/research/` and the persistent Research Garden at `/research-garden/`:
document one clear contract for each, preserve both while they have distinct
consumers, and then run the bounded POST/action tests before committing this
repair set.

Last verified: 2026-08-17 America/Santiago — Phase 548 Hub remediation.

## Phase 549 — MAK reel to PNG-sequence workflow

The user asked to stop the accidentally active image render and adapt the
existing WIN video path so MAK no longer depends on WIN. The active process
was inspected before stopping; it was `render_flyer_mak.py` over
`input_ig.jpg`, not a video render. Exact render PIDs 93069/93071/93072/93073
were sent SIGTERM. The self-hosted runner PID 92750 and runner service PID
1906 remained alive. No issue was queried or searched.

Historical and physical evidence:

- `src/flujo/eventos/blender_nodes_video.py` and
  `blender_nodes_video_seq.py` already existed in MAK/WIN.
- `RD.paravideo.blend` contains `Material.002` with a `MOVIE` texture,
  scene FPS 30 and template frame range 126..450.
- The current issue workflow previously accepted only `input_ig.jpg`.
- `puente_issues.py` had an explicit video -> Windows branch, but its cron
  entries are paused; the active test came from GitHub Actions on the
  self-hosted runner.

Implemented files:

- `src/flujo/ig/download.py`: parth-dl and curl_cffi paths now preserve the
  real video as `input_ig.mp4`; poster remains `input_ig.jpg`; metadata has
  `video_files` and `image_files`.
- `src/flujo/eventos/blender_nodes_video.py`: added a safe fallback for the
  real `RD.paravideo.blend` MOVIE node shape.
- `src/flujo/eventos/blender_nodes_video_seq.py`: requires Cycles GPU, sets
  128 samples, copies source FPS, calculates the frame range from the movie,
  writes PNGs and a manifest, and never saves the blend.
- `tools/render_video_sequence_mak.py`: MAK foreground wrapper with ffprobe
  preflight, Blender command contract and manifest validation.
- `.github/workflows/issue_descarga_ig.yml`: selects image or MP4 input and
  publishes the appropriate output directly to OneDrive; GitHub Actions
  artifacts are not part of the delivery contract.
- `tests/test_render_video_sequence_mak.py` plus updated IG/video tests.
- `context/VIDEO_WORKFLOW_MAK_20260817.md`: permanent workflow contract.

Validation evidence:

- `python3 -m py_compile ...` -> exit 0.
- Relevant pytest suite -> `36 passed`.
- Workflow YAML parsed with PyYAML -> exit 0, job `descarga` found.
- Smoke command with the existing local reel and `--frame-end 1` -> exit 0.
- Smoke manifest: source_frames=410, fps=30, samples=128,
  engine=CYCLES, gpu.device=GPU, backend=CUDA, GTX 1650; 1 PNG of
  12,464,001 bytes.
- `RD.paravideo.blend` mtime/size remained unchanged.

Known limits and risks:

- A full 410-frame Cycles render is intentionally not launched during this
  verification; the bounded frame took about 5m16s on the GTX 1650.
- If Instagram exposes only a poster and not a downloadable MP4, the new
  downloader fails the video path clearly instead of pretending the poster is
  the reel.
- The paused legacy `puente_issues.py` still needs a separate migration if it
  is ever re-enabled; the active GitHub Actions workflow is the MAK path
  tested here.
- `ruff` could not be run because it is absent from `/home/mak/flujo/.venv`;
  this is an environment limitation, not a reported lint failure.

## Next concrete action

Do not search or mutate the current issue. First review the diff and run the
full relevant local suite. Then, when the user authorizes external execution,
rerun the existing issue workflow so its downloaded MP4 is verified end to
end. Keep the full render bounded until the runner log confirms the video
file, calculated frame count, GPU manifest and available disk space.

Last verified: 2026-08-17 America/Santiago — Phase 549 video workflow.

## Phase 550 — corrected video template selection

The first smoke PNG was technically a valid GPU render but visually wrong.
It used the local sample video `Sundeck...mp4` with `RD.paravideo.blend` and
replaced that template's only MOVIE node (`frame.mp4`), which is the animated
frame layer. The output therefore lost the cyan frame, RD logo and border.

Read-only comparison established the correct contract:

- `RD.blend`: `Material.002` and `Material.008` contain `flyer_final.jpg`;
  `FRAME2.png` is present; this is the flyer composition template.
- `RD.paravideo.blend`: only `Material.002` has the historical `frame.mp4`
  MOVIE node; it is not the active PNG-sequence template.
- Existing `RD/AUTOMATIZACION/flyervideo/0001.png` visually confirms the
  expected composed output: same 3D scene plus frame/logo layer.

Correction applied:

- `tools/render_video_sequence_mak.py` now defaults to
  `/home/mak/RD/AUTOMATIZACION/RD.blend`.
- `context/VIDEO_WORKFLOW_MAK_20260817.md` now documents `RD.blend` as the
  active template and `RD.paravideo.blend` as historical alternate.

The earlier smoke was not evidence of the correct visual contract and must
not be treated as a passing end-to-end result. Its input origin was the local
Sundeck MP4, not the user's email issue. No `.blend` was modified.

## Next concrete action

Run one bounded frame with the corrected `RD.blend` path. Confirm visually
that `FRAME2.png` is preserved, both flyer materials are updated, the
manifest still reports Cycles/128/GPU, and the output matches the historical
`flyervideo/0001.png` composition before enabling any full reel run.

Last verified: 2026-08-17 America/Santiago — Phase 550 template correction.

## Phase 551 — corrected RD flyer composition validated

The bounded corrected smoke completed successfully with the active template:

```text
python3 tools/render_video_sequence_mak.py \
  --video '/home/mak/RD/AUTOMATIZACION/Sundeck vuelve para encender la temporada 🌌Después de un tiempo, nos reencontramos con una noch.mp4' \
  --out-dir /tmp/mak-video-rdblend-smoke.J4GvrB \
  --frame-end 1
```

Foreground evidence:

- exit code: 0;
- output: `frame_0001.png`, 12,464,001 bytes;
- manifest: source_frames=410, fps=24, samples=128,
  engine=CYCLES, gpu.device=GPU, backend=CUDA,
  `NVIDIA GeForce GTX 1650`;
- Blender used `/home/mak/RD/AUTOMATIZACION/RD.blend`;
- visual inspection confirms the composed flyer: the Sundeck video is
  inside the magenta frame, with RD logo and event text preserved;
- no Blender process remained after completion;
- SHA-256 checks of `RD.blend` and `RD.paravideo.blend` were collected after
  the run; the wrapper does not save either `.blend`;
- the previous visual smoke using `RD.paravideo.blend` is rejected and is not
  evidence for the workflow.

The active GitHub workflow no longer uploads GitHub Actions artifacts or
mentions an artifact in its success comment. The delivery target is
OneDrive; the run URL is retained only as operational trace.

## Next concrete action

Review the final diff and rerun the relevant local test suite. Do not search
or mutate the current issue. When external execution is authorized, run the
existing issue workflow and first confirm the downloaded `input_ig.mp4`, its
calculated frame count, GPU manifest and available disk space before allowing
the complete sequence to render and upload to OneDrive. No full 410-frame
render has been launched during this validation.

Last verified: 2026-08-17 America/Santiago — Phase 551 corrected composition.

## Phase 552 — five-frame render and GTX audit

The bounded five-frame render was allowed to complete after the user asked
for a performance audit:

```text
python3 tools/render_video_sequence_mak.py \
  --video '/home/mak/RD/AUTOMATIZACION/Sundeck vuelve para encender la temporada 🌌Después de un tiempo, nos reencontramos con una noch.mp4' \
  --out-dir /tmp/mak-video-rdblend-5frames \
  --frame-end 5
```

Evidence:

- exit code: 0; rendered=5, skipped=0, png_count=5;
- all five PNGs are 12,464,001 bytes and the manifest is valid;
- manifest confirms `CYCLES`, 128 samples, GPU device, CUDA backend and
  `NVIDIA GeForce GTX 1650`;
- `nvidia-smi` during rendering showed 100% GPU utilization, P0, 79 C,
  1,375 MiB / 4,096 MiB VRAM, 1,755 MHz SM clock and 6,000 MHz memory clock;
- no CPU fallback or VRAM exhaustion was observed;
- the active driver is `610.43.02-1`; local Debian package metadata offers
  `610.57.04-1` as an upgrade. It was not installed during the render to
  avoid interrupting the NVIDIA module or requiring a restart;
- `force_gpu(prefer=("CUDA", "OPTIX", "HIP"))` selects CUDA on this GTX.
  The existing measured evidence in `blender_gpu.py` records CUDA faster than
  OptiX on this exact machine, so no backend swap is justified;
- no `.blend` was saved or modified.

The current runtime is therefore GPU-correct but scene-bound: the 1080x1920
Cycles composition is the dominant cost, not a CPU fallback. `persistent_data`
is currently false; it is a candidate for a later animation-specific test,
but changing it without a bounded comparison would alter the validated
configuration. The driver upgrade must be scheduled separately after the
render workload is stopped.

## Next concrete action

Do not launch the complete 410-frame render yet. First decide whether to apply
the available NVIDIA package upgrade, reboot if required, and then perform one
bounded five-frame comparison with `persistent_data=True` while preserving
CUDA, 128 samples, the same `RD.blend` template and the same output contract.
Only adopt the setting if it materially lowers total wall time without
changing the visual output or exceeding the 4 GiB VRAM envelope.

Last verified: 2026-08-17 America/Santiago — Phase 552 five-frame GPU audit.

## Phase 553 — accidental inspection render stopped

The read-only Blender settings probe accidentally inherited `-f 1` and
started an unrelated background render after Phase 552. It was identified by
its exact command and stopped with SIGTERM (`blender` PID 107428 and its
shell parent PID 107417). This was not the video workflow or a persistent
service. A follow-up `pgrep` found no render process and `nvidia-smi` showed
0% GPU utilization, 6 MiB VRAM and 57 C. The five completed PNGs remain intact.

## Next concrete action

Before any new render, update the driver only as an explicit maintenance step
and use a Blender probe without `-f` if scene settings must be inspected.
Then run the bounded `persistent_data=True` comparison, or leave the current
validated configuration unchanged if avoiding another long render is more
important. Do not launch the full 410-frame job yet.

Last verified: 2026-08-17 America/Santiago — Phase 553 stray probe stopped.

## Phase 554 — poster no longer accepted as video substitute

Physical inspection after the user rejected the five-frame input found no
real `input_ig.mp4` under `/home/mak`. The only `input_ig.jpg` was an older
Creamfields image with mtime 2026-08-07, unrelated to the user's reel.
Therefore no additional render was started from that file.

Root cause in the workflow contract: a video classification with only a
poster could fall through to the image branch and render the poster as if it
were an intentional still image.

Correction:

- `.github/workflows/issue_descarga_ig.yml` now exports `media_type` from
  `media.json` and requires a non-empty `input_ig.mp4` whenever the type is
  `video`;
- a video without MP4 fails explicitly with
  `VIDEO_MEDIA_WITHOUT_MP4` and never uses `input_ig.jpg` as a substitute;
- only explicit `image` or `carousel` types enter the still-image renderer;
- unknown or missing media types fail closed;
- `src/flujo/ig/download.py` now raises `video_sin_mp4` when parth-dl declares
  video but provides no downloadable video entry;
- regression test added for the missing-MP4 case.

Validation:

- focused suite: 37 passed;
- workflow YAML: valid, job `descarga` present;
- Python compile: exit 0;
- no issue was searched or mutated, and no unrelated media was rendered.

## Next concrete action

Run the existing issue workflow only when its real Instagram link is present
again. Confirm from its own `media.json` that `media_type=video` and that the
fresh output directory contains `input_ig.mp4`; then render the requested
five frames with `RD.blend`. If the downloader fails, preserve the explicit
error instead of falling back to the poster.

Last verified: 2026-08-17 America/Santiago — Phase 554 fail-closed media gate.

## Phase 555 — no-login video provider and real issue validation

El issue real `#533` contiene el enlace público:
`https://www.instagram.com/iskvw/reel/DRA11amkRVX/`.

La comparación de proveedores dejó estos resultados:

- `parth-dl` y `curl_cffi` no entregaron un MP4 desde MAK; la vía HTML directa
  y varios Cobalt públicos devolvieron únicamente el poster JPEG.
- La ruta pública de SnapInsta (`https://snapinsta.ai/` + `action2.php`) no
  pidió login de Instagram y entregó un enlace CDN temporal real.
- El archivo descargado por el código exploratorio tuvo firma `ftyp`,
  `ffprobe` válido, H.264/AAC, 720x1280, 150 frames a 30 fps y 5.131 s.
  Los falsos positivos anteriores de 40,961 bytes eran JPEG y fueron
  rechazados.

Integración aplicada:

- `src/flujo/ig/download.py` incorpora SnapInsta como fallback solo para rutas
  video-like, desempaqueta la respuesta pública, descarga a `.part` y acepta
  solo archivos con firma MP4 y tamaño mínimo; nunca usa el poster como video.
- `tests/test_ig_download.py` cubre el fallback y rechaza JPEG disfrazado.
- `src/flujo/eventos/blender_nodes_video_seq.py` acepta FPS explícito.
- `tools/render_video_sequence_mak.py` pasa el FPS calculado por `ffprobe` a
  Blender. Esto corrige la discrepancia detectada: la plantilla heredaba 24
  fps aunque el video real era 30 fps.

Validación foreground:

- `PYTHONPATH=src .venv/bin/pytest -q tests/test_ig_download.py` -> código 0,
  `20 passed`.
- `python3 -m py_compile ...` para downloader, secuencia y wrapper -> código 0.
- El camino real `download_post()` -> código 0, `media_type=video` y
  `ffprobe` -> `format_name=mov,mp4,m4a,3gp,3g2,mj2`, `duration=5.131000`,
  `size=2148026`.
- `python3 tools/render_video_sequence_mak.py ... --frame-end 3` -> código 0;
  tres PNG renderizados, cada uno de 12,464,001 bytes, CYCLES, 128 samples,
  CUDA y `NVIDIA GeForce GTX 1650`.
- `--frame-start 75 --frame-end 75` -> código 0; frame intermedio renderizado
  y visualmente distinto del frame 1, demostrando avance de la animación.
- Revalidación con resume -> código 0, `fps=30.0`, `source_frames=150`,
  `rendered=0`, `skipped=3` para el conjunto y `skipped=1` para el frame 75;
  no se recalcularon imágenes ya válidas.
- No se modificó ningún `.blend`, no se mutó el issue y no quedó Blender
  corriendo.

Riesgos y límites:

- SnapInsta es una interfaz web pública, no una API contractual; su respuesta
  obfuscada o dominio puede cambiar. El fallback falla cerrado si no encuentra
  el enlace o si el CDN devuelve JPEG/HTML.
- El proveedor quedó limitado a reels/TV; los posts de imagen siguen en las
  rutas existentes. No se subieron los PNG a OneDrive en esta prueba acotada.

## Next concrete action

El commit `b7b19fd` ya está creado y publicado en `origin/main`; incluyó solo
los cinco archivos de integración y excluyó el worktree histórico. La suite
completa terminó verde antes del push. El siguiente test operativo es ejecutar
el workflow del issue autorizado y comprobar descarga, render completo
calculado y publicación en OneDrive; no lanzarlo en paralelo ni usar el poster
como sustituto.

Last verified: 2026-08-17 America/Santiago — Phase 555.

## Phase 556 — bake seguro de materiales estáticos RD

El usuario pidió bakear texturas, no reducir rebotes. Se auditó primero la
plantilla activa `/home/mak/RD/AUTOMATIZACION/RD.blend` con
`/home/mak/flujo/tools/audit_blend_scene.py` (código 0), sin guardar sobre la
fuente. El diagnóstico relevante fue:

- escena activa `Animated fluid in a testing tube`, Cycles, 1080x1920, cámara
  fija en los frames 1/50/100, 149 objetos y 134 meshes;
- 82 nodos de imagen en 69 materiales y 90 imágenes; la mayoría ya eran
  texturas bitmap/PBR, por lo que rehornearlas no reduciría el trabajo;
- solo tres ramas procedurales estáticas con UV y Principled Base Color aptas
  para un bake material-only: `tIGE/Material.014`,
  `Holders_Base/Rusty Metal` y `petri dish 03/Pilz 03`;
- `Material.002` y `Material.008` son las pantallas que el workflow reemplaza
  con el video en cada frame; `Decorative Glass 05`, `Glass`, `Glass.001`,
  `GlassFrosty`, `Liquid1`, `LiquidBlue.003` y `Simple Crystal.001` se
  conservaron para no congelar reflejos/transmisión ni la iluminación del
  contenido dinámico.

Se creó `/home/mak/flujo/tools/bake_static_materials.py`. El comando ejecutado
fue:

```text
/home/mak/blender/blender -b /home/mak/RD/AUTOMATIZACION/RD.blend --python /home/mak/flujo/tools/bake_static_materials.py -- --output /home/mak/RD/AUTOMATIZACION/RD.baked-static.v1.blend --resolution 2048
```

Resultado: código 0; se creó la copia
`/home/mak/RD/AUTOMATIZACION/RD.baked-static.v1.blend` con tres imágenes
2048x2048 empaquetadas (`BAKE_BASECOLOR_tIGE_0`,
`BAKE_BASECOLOR_Holders_Base_1`, `BAKE_BASECOLOR_petri dish 03_1`) y tres
materiales duplicados `__BAKED_...`. No se hizo bake de iluminación, sombras,
reflejos ni transmisión. La auditoría de la copia terminó con código 0 y
conservó la cámara, la animación, las pantallas y los rebotes originales
84/62/56/48/62/64. La fuente original no se guardó ni se reemplazó; su hash
verificado al cierre fue:
`2abb5ab6cb1a24d90ea3e745726e1f245b5d1dd8fe90dcf45260e9c9a4e2da64`.

Validación visual/operativa del bake:

- el frame 75 de la copia horneada se renderizó con Cycles, CUDA y GTX 1650;
  salió PNG de 1080x1920 en `/tmp/rd-benchmark-baked-20260817/frame_0075.png`;
- comparación contra el frame 75 de la fuente: MAE 0.0021/255, máximo 0/97
  por canal y 0.1105% de canales distintos; no se observó cambio material en
  la composición ni en el video;
- el bake por sí solo no redujo el tiempo de un frame: fuente 185.65 s,
  copia horneada 185.27 s. Esto es una medición, no un fallo del bake: el
  costo dominante está en geometría/Cycles y las texturas que ya eran bitmap.

También se dejó habilitable el cache persistente solo para la secuencia de
video: `src/flujo/eventos/blender_nodes_video_seq.py` usa `persistent_data`
por defecto y acepta `--no-persistent-data`; el wrapper
`tools/render_video_sequence_mak.py` expone la misma opción. La prueba de tres
frames 73–75 sobre la fuente terminó con código 0, 541.53 s totales y tres
PNG; el frame 75 fue visualmente equivalente (MAE 0.0022/255). El cache elevó
el pico del proceso a aproximadamente 1.76 GiB, por debajo de la memoria
disponible observada, pero no se debe activar para imagen fija.

Se rechazó la variante experimental que bajaba rebotes: aunque el tiempo no
mejoró, alteró piso/reflejos (MAE 6.93/255 y 28.46% de píxeles afectados). El
script `tools/optimize_blend_scene.py` fue corregido para preservar siempre
los rebotes; su comentario deja explícito que no es una optimización aceptada.

Validación de código: `python3 -m py_compile` de los cinco scripts modificados,
código 0; `.venv/bin/pytest -q tests/test_render_video_sequence_mak.py tests/test_blender_nodes_video.py`, código 0, 12 passed.

Archivos de repo modificados o creados en esta fase:
`tools/audit_blend_scene.py`, `tools/bake_static_materials.py`,
`tools/optimize_blend_scene.py`, `tools/render_video_sequence_mak.py`,
`src/flujo/eventos/blender_nodes_video_seq.py`,
`tests/test_render_video_sequence_mak.py`,
`tests/test_blender_nodes_video.py` y este handoff. Los `.blend` y PNG de
prueba quedaron fuera del repo, en `/home/mak/RD/AUTOMATIZACION/` y `/tmp/`.

Validación final de secuencia sobre la copia horneada:

```text
python3 tools/render_video_sequence_mak.py --video /tmp/mak-issue-533-snapinsta.mp4 --blend /home/mak/RD/AUTOMATIZACION/RD.baked-static.v1.blend --out-dir /tmp/rd-benchmark-baked-seq-20260817 --frame-start 73 --frame-end 75
```

Terminó con código 0: 3 PNG, 0 saltados, 30 fps, Cycles, 128 samples,
CUDA/GTX 1650. Los frames consecutivos sí cambian (MAE 2.69 y 2.76), y cada
frame horneado contra su equivalente de la fuente queda en MAE 0.0021/255;
por tanto el video continúa dinámico y el bake no congela la escena.

## Next concrete action

La copia horneada queda validada como variante segura, pero el wrapper conserva
`RD.blend` como default porque la copia `.blend` vive fuera del repo y no debe
convertirse silenciosamente en una dependencia no portable. Para usarla se
indica explícitamente `--blend /home/mak/RD/AUTOMATIZACION/RD.baked-static.v1.blend`.
La siguiente acción es decidir dónde versionar/distribuir esa plantilla de
render o generar una variante portable; después hacer un perfil acotado de
geometría/modificadores. No reducir rebotes ni hornear iluminación/reflejos.

Last verified: 2026-08-17 America/Santiago — Phase 556.

## Phase 557 — perfil de animación para bake híbrido

La hipótesis del usuario —cámara quieta y solo la emisión del video cambiando—
se verificó con el diagnóstico de solo lectura
`tools/profile_blender_animation.py`:

```text
/home/mak/blender/blender -b /home/mak/RD/AUTOMATIZACION/RD.blend --python /home/mak/flujo/tools/profile_blender_animation.py -- --frames 1 50 75
```

Código 0. Resultado: `camera_changes=false`, `light_changes=0`; únicamente
`Cylinder` y `Cylinder.002` cambiaron entre los tres frames, y el cambio fue
de transformación/rotación, no de topología. El resto de la geometría estática
puede entrar en una estrategia de bake híbrido. El script quedó compilado con
código 0 y no guarda el `.blend`.

Inspección específica del piso: el objeto `Base` usa `Metal04 PBR`, un grupo
con `Metal04_col.jpg`, `Metal04_met.jpg`, `Metal04_rgh.jpg`, `Metal04_nrm.jpg`
y `Metal04_disp.jpg`. No es un material procedural pendiente de bake; es PBR
bitmap y además es reflectivo. Hornear `Combined` lo convertiría en una imagen
congelada y eliminaría precisamente los reflejos dinámicos del video. La copia
`RD.baked-static.v1.blend` conserva el piso original por esta razón.

Conclusión técnica: sí existe una optimización de bake, pero debe separar
`diffuse/static` de `glossy/video/dynamic`. Un bake combinado de toda la escena
sería incorrecto. La siguiente prueba debe hornear solo iluminación difusa
estática sobre superficies no metálicas, mantener el BSDF glossy original para
reflejos, excluir `Base`, `Material.002`, `Material.008`, cristales, líquidos y
los dos cilindros animados, y comparar los frames 73/74/75 contra la fuente.

## Next concrete action

Construir una copia experimental separada para el bake híbrido: seleccionar
solo meshes estáticos no reflectivos, hornear la contribución difusa estática
sin modificar `RD.blend`, conservar mapas glossy/normal/displacement y ejecutar
una comparación visual de tres frames. Si el piso o una superficie cambia de
forma no aceptable, descartar esa variante y mantener la copia
`RD.baked-static.v1.blend` como bake material-only validado. No bajar rebotes ni
hornear la iluminación/reflexión del video.

Last verified: 2026-08-17 America/Santiago — Phase 557.

## Phase 558 — prueba de bake difuso híbrido y límite medido

Para no descartar la hipótesis sin probarla, se creó el experimento aislado
`tools/bake_static_diffuse_hybrid.py`. Solo acepta objetos estáticos,
opacos y no metálicos; excluye cámaras, geometría animada, `Tablet.002`,
materiales de video, líquidos, cristales, metales y el piso `Base`.

Sobre una copia separada se horneó `tIGE/Material.014` a 512x512 con diffuse
direct+indirect en frame 1. Después el material quedó como suma de emisión
difusa horneada y el Principled original con Base Color negro, de modo que su
respuesta glossy queda viva. La fuente no se guardó:
`/home/mak/RD/AUTOMATIZACION/RD.hybrid-test-tIGE.v1.blend`.

Como el MP4 temporal del issue ya no estaba disponible, se creó únicamente
`/tmp/rd-static-validation.mp4` a partir de la imagen local existente
`/home/mak/RD/AUTOMATIZACION/frame.png`; no se buscó ni descargó el issue.
Fuente e híbrido se renderizaron con el mismo clip sintético, un frame, CUDA,
GTX 1650, Cycles y 128 samples:

- fuente: `Time 03:02.94`;
- híbrido: `Time 03:05.43`;
- diferencia visual: MAE `0.5409/255`, máximo `110`; la composición se
  conservó, pero el tiempo aumentó aproximadamente 1.3%.

Conclusión: el bake híbrido es técnicamente posible y mantiene la imagen, pero
no es una optimización de tiempo en esta escena. El costo dominante es el
trazado de samples sobre la geometría y los reflejos, no los nodos de color de
un objeto. No se amplió el bake ni se propone activar esa variante.

## Next concrete action

Para conseguir una reducción real sin bajar rebotes, evaluar una arquitectura
de dos capas: renderizar una vez la capa estática y conservar en vivo solo
video, cilindros animados y reflejos necesarios; luego componer ambas capas.
Debe probarse primero con una copia y tres frames, porque una capa estática
simple perdería reflejos/oclusiones del video. Si no conserva el aspecto,
mantener el pipeline Cycles actual y no fabricar más mapas que no aceleran.

Last verified: 2026-08-17 America/Santiago — Phase 558.

## Phase 559 — objetivo persistente: render híbrido medido

El usuario estableció como objetivo de esta línea de trabajo encontrar y
validar una arquitectura de render Blender híbrida para RD que aproveche la
cámara y la geometría estáticas, mantenga dinámicos el video, los reflejos y
los objetos animados, reduzca el tiempo medido sin bajar rebotes ni degradar la
imagen, y documente una variante segura antes de activarla.

Estado de la investigación:

1. Mapa de animación: cámara fija, luces fijas, `Cylinder` y `Cylinder.002`
   cambian de transformación.
2. Bake de base color procedural: validado visualmente, sin ganancia de tiempo.
3. Bake difuso híbrido de prueba: visualmente cercano, pero 1.3% más lento.
4. Hipótesis activa: separar capa estática y capa dinámica, con composición y
   validación de reflejos/oclusiones antes de integrarla.

La investigación continuará en copias experimentales y con lotes pequeños;
`RD.blend` sigue siendo rollback intacto. No se aceptará una variante solo por
renderizar: debe demostrar ahorro de tiempo, equivalencia visual suficiente,
video dinámico y un camino de reversión.

## Next concrete action

Inspeccionar colecciones, pases y materiales para definir la primera separación
estática/dinámica mínima. Construir una copia de prueba que no elimine objetos:
solo marque visibilidad por capa, renderice un frame estático y un frame
dinámico, y mida si la composición puede conservar el piso reflectivo y la
pantalla. No activar ni reemplazar el wrapper hasta tener esa medición.

Last verified: 2026-08-17 America/Santiago — Phase 559.

## Phase 560 — rollback de híbrido y encuadre cover para video

Se inspeccionó la propuesta de capas estática/dinámica antes de activarla.
La prueba no se promovió: `Tablet.002` contiene marco, cristal y solo 13 caras
con materiales de video (`Material.002`/`Material.008`). Una capa aislada del
objeto pierde el entorno que necesita el cristal para sus reflejos; la
composición simple alteraba el aspecto. El `.blend` original nunca se guardó
desde esas pruebas y queda como rollback operativo. El script experimental fue
movido fuera de `tools/` a:
`context/quarantine/render-hybrid-experiment-20260817/render_layer_experiment.py`.

La auditoría de memoria confirmó una causa concreta de costo de carga: la
imagen histórica `flyer_final.jpg` mide 11925x11926 y representa unos 542.52
MiB de buffer RGBA; la escena reporta 149 objetos, 306210 vértices, 333658
polígonos, 38 SUBSURF y 62 nodos geométricos. No se eliminó ni redimensionó
esa evidencia en el proyecto activo.

Se corrigió solo el encuadre del camino de video. `fitwidth_mapping` permanece
intacto para imágenes verticales/1440. Se añadió `fitcover_mapping` en
`src/flujo/eventos/blender_nodes.py` y `blender_nodes_video.py` lo usa al
construir o actualizar materiales de video: llena la ventana portrait,
recorta simétricamente los lados de un 16:9 y centra el contenido en el marco
del cristal. No reduce samples, rebotes ni modifica el `.blend`.

Validaciones ejecutadas:

```text
.venv/bin/pytest -q tests/test_blender_nodes.py tests/test_blender_nodes_video.py tests/test_render_video_sequence_mak.py
```

Código 0; 24 pruebas pasaron. La inspección Blender sin render terminó con
código 0 y mostró para ambos materiales de video, usando un clip 720x1280,
el mismo mapping cover (`scale=(3.458425,1.945560)`, `loc=(-2.266949,-0.988602)`).
La pasada experimental de `screen_only` a 25% y 128 samples fue solo un
smoke test geométrico; no se considera validación de imagen porque el cristal
aislado no conserva su entorno. El flujo productivo sigue siendo el render
normal completo.

Riesgo controlado: `fit-cover` recorta los lados de videos horizontales por
diseño; no deforma ni desplaza el centro. Un video vertical con composición
importante en los bordes debe revisarse visualmente antes de entregar, pero la
ruta de imagen fija no cambia.

## Next concrete action

Cuando exista un MP4 de prueba disponible, ejecutar un frame foreground del
workflow productivo con `RD.blend`, verificar visualmente el marco completo y
comparar el centro del contenido. Si el crop real pasa, conservar el cambio de
mapping; si no pasa, revertir únicamente `fitcover_mapping` y sus tests. No
reactivar la arquitectura híbrida ni usar la carpeta de cuarentena como ruta
operativa.

Last verified: 2026-08-17 America/Santiago — Phase 560.

## Phase 561 — validación foreground del crop 16:9 en resolución real

Se ejecutó el workflow productivo completo, sin capas experimentales ni
guardado de plantilla:

```text
python3 tools/render_video_sequence_mak.py \
  --video /tmp/rd-dynamic-validation.mp4 \
  --blend /home/mak/RD/AUTOMATIZACION/RD.blend \
  --out-dir /tmp/rd-cover-production-20260817 \
  --frame-start 1 --frame-end 1 --min-size 20000
```

El clip de prueba era 720x1280, seis frames, 30 fps. El proceso terminó con
código 0 y `RENDER_OK`: Cycles, 128 samples, CUDA en NVIDIA GeForce GTX 1650;
el frame PNG de 1080x1920 quedó en
`/tmp/rd-cover-production-20260817/frame_0001.png`. Tiempo Blender:
`02:58.17`; el render se inspeccionó visualmente y el contenido 16:9 llena la
abertura vertical, queda centrado y recorta simétricamente los laterales del
video. El marco de cristal permanece visible alrededor. No se observó el
desplazamiento vertical de las previews anteriores.

La plantilla `/home/mak/RD/AUTOMATIZACION/RD.blend` no fue guardada ni
modificada; hash posterior confirmado:
`2abb5ab6cb1a24d90ea3e745726e1f245b5d1dd8fe90dcf45260e9c9a4e2da64`.

## Next concrete action

Mantener la arquitectura normal de Cycles como camino productivo. El único
cambio promovible de esta investigación es `fitcover_mapping` para video; la
variante híbrida queda en cuarentena y no debe conectarse al wrapper. Para
cerrar esta línea falta probar un MP4 real del workflow de evento cuando esté
disponible; no hace falta reabrir el issue ni descargarlo para conservar el
estado actual.

Last verified: 2026-08-17 America/Santiago — Phase 561.

## Phase 562 — descarga y validación del reel real del issue 533

Se recuperó nuevamente el material real asociado al issue `#533`, sin
login de Instagram y sin buscar un issue nuevo. La URL registrada en este
handoff fue:
`https://www.instagram.com/iskvw/reel/DRA11amkRVX/`.

La descarga terminó con código 0 y produjo:
`/tmp/rd-issue-533-real-20260817/input_ig.mp4`.
La inspección `ffprobe` confirmó H.264/AAC, 720x1280, 30 fps, 150 frames,
5.131 segundos y 2148026 bytes. Se extrajo el frame fuente 75 a
`/tmp/rd-issue-533-real-20260817/source-frame-0075.png` y se verificó
visualmente que es el reel real: empaque vertical con contenido oscuro y
reflejos, no una tarjeta sintética.

Se ejecutó el workflow productivo real, sin guardar la plantilla:

```text
python3 tools/render_video_sequence_mak.py \
  --video /tmp/rd-issue-533-real-20260817/input_ig.mp4 \
  --blend /home/mak/RD/AUTOMATIZACION/RD.blend \
  --out-dir /tmp/rd-issue-533-real-render-20260817 \
  --frame-start 75 --frame-end 75 --min-size 20000
```

Código 0; `RENDER_OK`; se generó
`/tmp/rd-issue-533-real-render-20260817/frame_0075.png` (1080x1920,
16-bit RGB, 12464002 bytes). Tiempo Blender: `03:01.79`. Manifest: una
fuente de 150 frames a 30 fps, Cycles, 128 samples, GPU CUDA y
`NVIDIA GeForce GTX 1650`. La plantilla conserva el hash
`2abb5ab6cb1a24d90ea3e745726e1f245b5d1dd8fe90dcf45260e9c9a4e2da64`.

La primera inspección del PNG real mostró que el `fitcover` matemáticamente
centrado no centraba el motivo visual: el sujeto del reel quedaba alto dentro
del cristal. Esa conclusión fue corregida en la fase siguiente; esta fase no
se considera una validación visual final. El marco, reflejos, iluminación,
piso y composición permanecen presentes. Se mantiene el pipeline normal
completo; no se reactivó el híbrido ni se redujeron rebotes o samples.

Hashes de evidencia:

```text
9f566ac4dc2dedb46c170dea84915311964272943ae7b0ba1ca93b01327f9c4a  input_ig.mp4
e48523dc45f4591b39795aba782a7f42dace50623c8a124be1ae676649c1d519  frame_0075.png
2abb5ab6cb1a24d90ea3e745726e1f245b5d1dd8fe90dcf45260e9c9a4e2da64  RD.blend
```

## Phase 563 — corrección del centro visual del video real

La comparación foreground de tres variantes confirmó que el problema no era
la geometría ni el `.blend`: el contenido visible del reel estaba alto dentro
de su lienzo portrait. Se agregó un parámetro reversible `offset_y` a
`fitcover_mapping`; el camino de imágenes fijas y `fitwidth_mapping` no se
modificaron. El consumidor de video usa el ajuste explícito
`VIDEO_CONTENT_OFFSET_Y = 0.05`, que desplaza el motivo 5% hacia abajo dentro
de la ventana. La prueba de 10% se descartó por pasar el centro y acercarse
demasiado al borde inferior.

Validación de código:

```text
.venv/bin/pytest -q tests/test_blender_nodes.py tests/test_blender_nodes_video.py tests/test_render_video_sequence_mak.py
Código 0; 25 pruebas pasaron.
```

Validación foreground final con el MP4 real, sin guardar la plantilla:

```text
python3 tools/render_video_sequence_mak.py \
  --video /tmp/rd-issue-533-real-20260817/input_ig.mp4 \
  --blend /home/mak/RD/AUTOMATIZACION/RD.blend \
  --out-dir /tmp/rd-issue-533-real-render-offset005-20260817 \
  --frame-start 75 --frame-end 75 --min-size 20000
```

Código 0; `RENDER_OK`; salida
`/tmp/rd-issue-533-real-render-offset005-20260817/frame_0075.png`,
1080x1920, 12464002 bytes, Cycles 128 samples, CUDA GTX 1650, tiempo
Blender `03:02.31`. La inspección visual final confirma el motivo centrado
en la abertura, sin cortar el empaque en los bordes y conservando marco,
reflejos, iluminación y piso. `RD.blend` no fue guardado ni alterado.

## Next concrete action

Conservar `VIDEO_CONTENT_OFFSET_Y = 0.05` como ajuste actual del workflow de
video y `fitwidth_mapping` para imágenes. Un render completo de los 150
frames solo debe ejecutarse cuando se solicite la entrega final y exista un
destino de almacenamiento suficiente. Antes de entregar otro video vertical
con composición distinta, revisar un frame central: el offset es una decisión
de encuadre para el contenedor RD, no una regla universal de edición. No
modificar ni guardar `RD.blend` durante esa operación.

Last verified: 2026-08-17 America/Santiago — Phase 563.

## Phase 564 — segundo reel y revisión de bordes

Se descargó y validó el segundo reel real solicitado:
`https://www.instagram.com/iskvw/reel/DZHDe7NvqOh/`.
El descargador devolvió código 0, MP4 H.264 de 720x1280, 30 fps, 491 frames
y 16.366667 segundos, además de su thumbnail JPG. Se inspeccionaron frames
fuente al inicio, centro y final para comprobar que el material tiene
gráficas próximas a los bordes.

Se renderizó el frame central 245 con el workflow productivo y el ajuste
actual de video:

```text
python3 tools/render_video_sequence_mak.py \
  --video /tmp/rd-reel-DZHDe7NvqOh-20260817/input_ig.mp4 \
  --blend /home/mak/RD/AUTOMATIZACION/RD.blend \
  --out-dir /tmp/rd-reel-DZHDe7NvqOh-render-20260817 \
  --frame-start 245 --frame-end 245 --min-size 20000
```

Código 0; `RENDER_OK`; salida
`/tmp/rd-reel-DZHDe7NvqOh-render-20260817/frame_0245.png`, 1080x1920,
12.5 MB. Cycles, 128 samples, CUDA, NVIDIA GeForce GTX 1650, tiempo Blender
`02:59.64`. La inspección visual confirma que la composición central queda
dentro del cristal y que no se pierde una gráfica relevante en los bordes
visibles de este frame.

Límite importante: la abertura del `.blend` tiene una proporción más ancha
que el video 9:16. Por eso `fitcover` recorta necesariamente parte superior e
inferior de la fuente; el offset de 5% es una decisión de encuadre del
contenedor RD y no equivale a preservar el 100% del canvas original. Si un
reel futuro usa información crítica en los bordes, debe pasar una revisión de
frame central y se debe elegir explícitamente entre cover (sin barras, con
recorte) y contain/fit-height (sin recorte, con barras laterales).

## Next concrete action

Mantener la prueba de segundo reel como validación visual, sin renderizar los
491 frames completos. Antes de entregar videos con contenido crítico en los
bordes, añadir o ejecutar una decisión explícita de `cover` versus
`fit-height`; no cambiarla globalmente basándose solo en este reel. No
modificar ni guardar `RD.blend`.

Last verified: 2026-08-17 America/Santiago — Phase 564.

## Phase 565 — política de encuadre confirmada

El usuario confirmó la decisión productiva: usar `cover` para llenar toda la
abertura del cristal, conservar la proporción original y aceptar el recorte
de franjas antes que deformar el video o mostrar bordes negros. La regla debe
leerse según la relación de aspecto: una fuente horizontal recorta franjas
laterales verticales; una fuente 9:16 dentro de esta abertura más ancha recorta
franjas superior e inferior. `fitwidth_mapping` de imágenes fijas permanece
sin cambios.

## Phase 566 — reels verticales centrados sin offset visual

Se corrigió la política anterior: el workflow de reels se considera
exclusivamente portrait. `blender_nodes_video.py` ya no aplica el offset fijo
de 5% que se había ajustado al motivo de un único reel. Ahora llama a
`fitcover_mapping` sin `offset_y`: la fuente queda centrada en X e Y, cubre
la abertura y el recorte superior/inferior es simétrico. Las imágenes fijas
siguen usando `fitwidth_mapping` sin cambios.

El helper conserva `offset_y` opcional para experimentos explícitos, pero no
forma parte del camino productivo. No se modificó ni guardó `RD.blend`.

## Next concrete action

Ejecutar una validación foreground de un frame real con esta versión centrada
para confirmar la simetría visual final. No cambiar a `contain`/`fit-height`,
no reabrir el híbrido y no renderizar todos los frames hasta que ese smoke
test sea inspeccionado.

Last verified: 2026-08-17 America/Santiago — Phase 566.

## Phase 567 — validación del centrado portrait sin offset

Se ejecutó la validación solicitada después de retirar el offset fijo:

```text
.venv/bin/pytest -q tests/test_blender_nodes.py tests/test_blender_nodes_video.py tests/test_render_video_sequence_mak.py
python3 tools/render_video_sequence_mak.py \
  --video /tmp/rd-reel-DZHDe7NvqOh-20260817/input_ig.mp4 \
  --blend /home/mak/RD/AUTOMATIZACION/RD.blend \
  --out-dir /tmp/rd-reel-DZHDe7NvqOh-render-centered-20260817 \
  --frame-start 245 --frame-end 245 --min-size 20000
```

Las pruebas terminaron con código 0 (`25 passed`) y el render terminó con
código 0 (`RENDER_OK`). El PNG resultante es
`/tmp/rd-reel-DZHDe7NvqOh-render-centered-20260817/frame_0245.png`, 1080x1920,
Cycles 128 samples, CUDA en la GTX 1650, tiempo Blender `02:59.60`. La
inspección visual confirma centrado X/Y del reel vertical y recorte simétrico
arriba/abajo. `RD.blend` no fue guardado ni alterado.

## Next concrete action

La política de encuadre de reels queda cerrada: `cover` centrado, sin
deformación, sin bordes negros y con recorte simétrico vertical. Mantener las
imágenes fijas en su camino separado. No renderizar los reels completos ni
hacer nuevos ajustes de offset salvo que un caso futuro demuestre una
composición excepcional.

Last verified: 2026-08-17 America/Santiago — Phase 567.

## Phase 568 — preservacion de media antes del render

Se corrigio el workflow de eventos para que una descarga no dependa de que
Blender termine correctamente. Antes, el MP4 y los frames vivian bajo
`$RUNNER_TEMP` y solo se copiaban a OneDrive despues de un render completo;
el issue 534 quedo sin `MAK/eventos/issue-534` y el temporal fue limpiado.

Archivo modificado:
`/home/mak/flujo/.github/workflows/issue_descarga_ig.yml`.

Cambios:

- `preservar media descargada antes de render` copia inmediatamente el MP4,
  poster, `media.json` y caption a
  `onedrive:MAK/eventos/issue-$ISSUE_NUM`.
- `publicar render en OneDrive (completo o parcial)` usa `always()`, conserva
  frames ya producidos, `render.log` y `render_manifest.json` aunque Blender
  falle, y mantiene el cierre del issue condicionado a render completo.
- `comentar render fallido con media preservada` deja el issue abierto y
  entrega la ruta remota cuando la fuente fue preservada.

Validacion foreground:

```text
node YAML parse + workflow structure check: exit 0, WORKFLOW_STRUCTURE_OK
bash -n de los tres bloques nuevos: exit 0, WORKFLOW_SHELL_BLOCKS_OK
guards de always/preserve/failure: exit 0, WORKFLOW_GUARDS_OK
git diff --check -- .github/workflows/issue_descarga_ig.yml: exit 0
rclone lsf onedrive:MAK/eventos/issue-534: exit 1, directory not found
rclone lsf onedrive:MAK/eventos: exit 0, solo issue-533 existente
```

No se tocaron `RD.blend`, el renderer ni los datos historicos. Los cambios
previos no relacionados del worktree fueron preservados.

Riesgos abiertos: aun falta observar un nuevo issue real para confirmar en
GitHub Actions que la preservacion temprana y la publicacion parcial funcionan
contra OneDrive; `actionlint` no esta instalado localmente. Una perdida
abrupta de energia puede impedir la subida de frames parciales, pero la fuente
original ya queda protegida antes de iniciar Blender.

## Next concrete action

Ejecutar el proximo issue real y verificar primero, antes de esperar el render,
que `onedrive:MAK/eventos/issue-<n>/input_ig.mp4` exista; despues comprobar que
el render completo publique manifest/frames o que un fallo deje log y media
preservada sin cerrar el issue.

Last verified: 2026-08-18 America/Santiago — Phase 568.

## Phase 569 — política audiovisual permanente

Se dejó una única fuente de verdad en
`context/VIDEO_WORKFLOW_MAK_20260817.md`, con la separación de rutas
`image`/`video`/`carousel`, la regla dinámica para cualquier proporción y el
registro de las preferencias visuales experimentadas por el usuario.

El código ahora expone `classify_cover_layout()` y registra en cada manifest
de secuencia la política, proporción de ventana, proporción real de fuente,
eje de recorte, centrado, deformación y barras negras. El validador del
manifest exige esos campos. La política activa es
`cover_center`: sin deformación, sin barras, centrada, recortando laterales si
la fuente es más ancha y arriba/abajo si es más alta. `glass_fitwidth` queda
nombrado como experimento, no se activa silenciosamente.

Validación foreground ejecutada:

```text
.venv/bin/pytest -q tests/test_blender_nodes.py tests/test_blender_nodes_video.py tests/test_render_video_sequence_mak.py: exit 0, 29 passed
python3 -m py_compile src/flujo/eventos/blender_nodes.py src/flujo/eventos/blender_nodes_video.py src/flujo/eventos/blender_nodes_video_seq.py tools/render_video_sequence_mak.py: exit 0
PYTHONPATH=src python3 aspect probe (16:9, square, 4:5, 9:16): exit 0
manifest layout source guard: exit 0, MANIFEST_LAYOUT_SOURCE_GUARD_OK
git diff --check sobre los archivos modificados: exit 0
```

La búsqueda física de `/home/mak` no encontró actualmente ningún `.mp4`,
`.mov`, `.mkv` ni `.webm`; por eso aún no se ejecutó el smoke render real que
confirme el nuevo campo en un manifest generado por Blender. No se inventó
esa evidencia y no se modificó `RD.blend`.

Archivos modificados:

- `src/flujo/eventos/blender_nodes.py`
- `src/flujo/eventos/blender_nodes_video.py`
- `src/flujo/eventos/blender_nodes_video_seq.py`
- `tools/render_video_sequence_mak.py`
- `tests/test_blender_nodes.py`
- `tests/test_render_video_sequence_mak.py`
- `context/VIDEO_WORKFLOW_MAK_20260817.md`
- `context/LAST_HANDOFF.md`

## Next concrete action

Ejecutar en primer plano la suite enfocada de helpers y una prueba real
acotada que confirme el nuevo campo `layout` del manifest. Revisar
`VIDEO_LAYOUT` en el log y `layout` en el manifest antes de inspeccionar el
PNG. No renderizar los 491 frames completos ni modificar `RD.blend`.

Last verified: 2026-08-18 America/Santiago — Phase 569.

## Phase 570 — auditoria read-only de superficie MAK/Linux

Se auditó físicamente el camino de eventos y los textos de plataforma. El
camino actualmente consumido por el workflow es Linux/MAK:

- `.github/workflows/issue_descarga_ig.yml` importa
  `flujo.ig.download.download_post`.
- Para video llama `tools/render_video_sequence_mak.py`.
- Para imagen/carrusel llama `tools/render_flyer_mak.py`.
- Los defaults activos existen físicamente:
  `/home/mak/blender/blender`,
  `/home/mak/RD/AUTOMATIZACION/RD.blend` y
  `/home/mak/RD/AUTOMATIZACION/FRAME2.png`.
- No apareció ningún path `C:/`, `C:\\` ni `/home/mak/WIN` en ese camino
  activo.

Se encontraron superficies heredadas que no son llamadas por ese workflow y
pueden confundir a futuros agentes:

1. `src/flujo/eventos/flyer_auto.py`: conserva `DEFAULT_WINDOWS_BASE`,
   Droplet/Photoshop y fallbacks de Windows.
2. `tools/bridge_issue_render.py`: puente Windows antiguo, con Blender.exe y
   estado de puente local.
3. `tools/render_video_rd.py`: ruta manual H264 sobre
   `RD.paravideo.blend`, con default Windows y compatibilidad WIN/MAK.
4. `tools/render_flyer_mak.py`: su encabezado todavía dice que reproduce
   “EXACTO el camino real de WIN”, aunque el consumidor activo es MAK y el
   runtime no depende de WIN.
5. `context/VIDEO_WORKFLOW_MAK_20260817.md`: la sección Evidence conserva la
   ruta de un smoke histórico cuyo MP4 ya no existe físicamente; es evidencia
   válida de aquel momento, pero debe quedar marcada como histórica para no
   parecer un input actual.

No se borró ni se movió evidencia durante esta auditoría. El commit `9c915c2`
no contiene esas superficies heredadas. Su disposición correcta es
`legacy/manual-only`, separada del camino MAK activo; la limpieza o
cuarentena física requiere un slice posterior con write set propio.

## Next concrete action

Corregir únicamente las etiquetas/documentación de las cinco superficies
heredadas para declarar `legacy/manual-only` y diferenciar evidencia histórica
de runtime activo. Después ejecutar import/entrypoint checks de MAK y verificar
que el workflow no importe ninguna ruta heredada. No borrar esos archivos ni
alterar `RD.blend`.

Last verified: 2026-08-18 America/Santiago — Phase 570.

## Phase 571 — consolidacion del estado actual para el repo web

Se publico una sintesis operativa para que un agente nuevo no tenga que leer
las cientos de evidencias historicas antes de trabajar:
`docs/MAK_CURRENT_STATE.md`. El documento concentra autoridad fisica,
interfaces, owners/consumidores, semantica compartida, bases RD, research,
workflow de eventos, politica de imagen/video, APIs, superficies legacy y
topologia Git. Las fases y memorias quedan conservadas como evidencia; no se
copio ningun arbol ni se elimino ningun archivo.

Se corrigieron referencias que podian confundir WIN con MAK/Linux:

- `CAPACIDADES.md` ahora apunta al estado canonico y distingue los renderers
  activos de las rutas legacy/manual-only.
- `MAPA.md` remite al estado canonico y advierte que el CLI puede conservar
  comandos legacy por compatibilidad.
- `src/flujo/web/hub.py` documenta la cadena actual del runner MAK hacia
  `render_*_mak.py` y OneDrive.
- `tools/render_flyer_mak.py` declara su dependencia de runtime Linux/MAK y
  la procedencia historica del contrato, sin presentar WIN como runtime.
- `context/VIDEO_WORKFLOW_MAK_20260817.md` marca el smoke MP4 como evidencia
  historica y no como input actual.

Validacion foreground:

```text
python3 -m py_compile src/flujo/web/hub.py tools/render_flyer_mak.py: exit 0
.venv/bin/pytest -q tests/test_blender_nodes.py tests/test_blender_nodes_video.py tests/test_render_video_sequence_mak.py tests/test_mak_hub_eventos.py: exit 0, 44 passed
git diff --check sobre los siete archivos editados: exit 0
workflow call-site check: download_post + render_*_mak presentes; legacy bridge/render_video_rd ausentes del workflow activo
```

Archivos intencionales de esta entrega:
`docs/MAK_CURRENT_STATE.md`, `CAPACIDADES.md`, `MAPA.md`,
`context/LAST_HANDOFF.md`, `context/VIDEO_WORKFLOW_MAK_20260817.md`,
`src/flujo/web/hub.py` y `tools/render_flyer_mak.py`.

Riesgos abiertos: aun no existe un nuevo issue real que permita medir la
preservacion temprana en Actions; las rutas legacy aun tienen imports/CLI o
tests y por eso no se borraron; el worktree conserva cambios y evidencias no
relacionadas que deben quedar fuera del commit.

## Next concrete action

La consolidacion ya esta publicada en `main` y `HEAD == origin/main` fue
confirmado. El siguiente trabajo funcional es observar un issue real o crear
un packet de idea con `tools/route_idea.py`; no reabrir la genealogia completa.

Last verified: 2026-08-18 America/Santiago — Phase 571.
