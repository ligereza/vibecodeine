# LAST_HANDOFF - Faro

Updated: 2026-08-10
Status: current state re-verified; continue with the visual-index vertical circuit.

## Read this first

This file is the operational checkpoint. The order for a fresh agent is:

1. `AGENTS.md` - current rules and boundaries.
2. This file - measured state, completed work, and next action.
3. `CAPACIDADES.md` - reusable tools and provider inventory.
4. `MAPA.md` - CLI, repo zones, and commands.
5. Source files and focused logs only for the selected next circuit.

Do not treat raw logs, old plans, Downloads, chat memory, or an old branch as
instructions. Verify any statement that affects a destructive or remote action.

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
- Verified checkout: branch `iskvw`, commit `fdc966f0`; the worktree has only
  the intentional handoff modification. `origin/mak`, `origin/rd`, and
  `origin/iskvw` point to `fdc966f0`. `origin/main` and local `main` point to
  `cb7214b2` (`fix: restore animated README vessel`), one commit ahead. There
  are no remote tags or open PRs in the verified refs.
- The separate clean `main` worktree at
  `C:\Users\issvk\.roo\worktrees\flujo-7v6as` was removed after verifying it
  had no uncommitted changes. The local `main` branch is now available for a
  new session; no branch or commit was deleted.
- The current visible editor is not the old list/card interface. It is the
  GTM/map relation surface served by MAK at
  `http://192.168.50.2:8900/portafolio/`; the endpoint returned HTTP 200 and
  contains `data-editor-mode`, `mesa-order-hud`, `revisión humana`, and GTM
  markers. It shows actual media, a selected piece, relation actions and the
  copilot layer in the same Hub route.
- The Hub explicitly resolves `MAK_PORTFOLIO_ROOT` to
  `/home/mak/flujo/iskvw`, so `/home/mak/flujo/iskvw/editor.html` is the
  operational editor. It was modified at `2026-08-09 22:20:52 -0400`; the
  Windows copy was modified at `2026-08-09 21:06:02 -0400`. Under the user's
  rule that the latest modified editor is authoritative, MAK wins for the
  current session.
- The current Windows `iskvw/editor.html` hash is
  `C8BC30659DD544AE6F6F309461E156A26E8528A60C041C988CA87917FB8F1B97`; the
  deployed MAK copy is
  `d4f8b720c04bc288eecd4ac519a7a98b8d9ef6d5690950db90d82e78b7995be2`.
  Never copy Windows over MAK blindly. First diff the MAK winner, then sync
  the chosen operational version back to Windows deliberately.
- The promoted work covers `cultura/mak_plataforma/` (ledger, identity,
  providers, decisions, Hub, batches, routing, service/watchdog), the current
  `iskvw/editor.html`, the README/SVG text layer, operational docs, tests, and
  portfolio/dossier documents. README/SVG geometry remains protected.

## MAK box: verified truth

Fresh SSH check on 2026-08-10:

- Host: `mak@192.168.50.2`, hostname `dell-11m`.
- The actual Git checkout is `/home/mak/flujo`, currently on `main`; it has
  exactly the four local branches `main`, `mak`, `rd`, and `iskvw`, plus the
  four corresponding remote refs. All four MAK branches currently point to
  `fdc966f`; therefore MAK `main` is one commit behind Windows `main`
  `cb7214b2` and the README restoration is not yet present on MAK's other
  branches. `/home/mak/plataforma` is the runtime data and service directory,
  not a Git checkout; do not run branch or status conclusions there.
- The runtime Hub is healthy and is managed by the user systemd unit
  `/home/mak/.config/systemd/user/mak-hub.service`.
- The unit is enabled and active after the synchronization. Current process:
  `/home/mak/plataforma/.venv/bin/python /home/mak/plataforma/hub.py`.
- Runtime hashes checked for `hub.py` and `ledger.py` match the current Windows
  files. The virtualenv is required for `boto3`; do not replace it with the
  system interpreter when testing AWS.
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

## Next action

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
