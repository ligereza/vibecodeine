# LAST_HANDOFF - Faro

Updated: 2026-08-09
Status: published state verified; continue with the first durable vertical circuit.

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
- Windows branch: `mak`, aligned with `origin/mak` at `623b961e`.
- `origin/main`, `origin/mak`, `origin/rd`, and `origin/iskvw` all point to
  `623b961e`. No remote tags or open PRs remain.
- The Windows worktree is clean after the explicit commit and push requested by
  the user. The promoted block is `8f1bd37`; `main` records the promotion in
  merge commit `5f690fa`; `d12ef137` records the first published branch state;
  `623b961e` corrects this handoff after the final sync.
- The promoted work covers `cultura/mak_plataforma/` (ledger, identity,
  providers, decisions, Hub, batches, routing, service/watchdog),
  `iskvw/editor.html`, the README/SVG text layer, operational docs, tests, and
  portfolio/dossier documents.

## MAK box: verified truth

Fresh SSH check on 2026-08-09:

- Host: `mak@192.168.50.2`, hostname `dell-11m`.
- The extra Capataz checkout was inventoried into
  `/home/mak/quarantine/flujo-20260809-branch-reconcile/` before cleanup. Its
  local branches were removed after the unique work was preserved; the runtime
  checkout is now clean on `mak` at `623b961e`.
- The MAK checkout has exactly the four local branches `main`, `mak`, `rd`, and
  `iskvw`, all aligned with their four remote counterparts.
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
  records and the Hub now exposes exactly five pending review items.

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

## Current boundaries and pauses

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
mass audit. The first vertical circuit is complete. Continue with its
evidence, not another blind batch:

1. Inspect the five AWS candidates and their exact manifest rows; keep them as
   audiovisual records until the human or metadata resolves their context.
2. Add explicit human context for known collaborations and usernames before
   another provider call; the model cannot convert a misspelled username into
   evidence.
3. Use Watsonx only for bounded event triangulation against declared date,
   venue, artist, producer, and XIO/RD evidence; do not rerun the rejected
   mixed curation batch.
4. Keep hypotheses separated by date, visual, audio, event, venue, artist,
   client, and collaboration. Use XIO data only where an actual event/setlist
   source exists; do not pretend one event is a universal source.
5. Send every result through the local judge/deterministic fallback and record
   candidate, review, refutation, or archive in the common ledger. No public
   promotion.
6. Expose only the resulting next action in the Hub. The human should review
   grouped visual candidates, not read a wall of model prose.

The extra Capataz checkout has already been preserved and removed. After this
circuit, make only one deliberate mechanical promotion when the evidence is
ready; do not create small PRs for cosmetic work. The domain remains last.

## Session close rule

At the end of every future session, update this file with measured facts, not
intentions: exact branch/commit, MAK process, files changed, tests run, external
calls, failures, user decisions, and one next action. Keep historical detail
in `_logs/cauce_director/20260805/`; keep this file short enough that a fresh
agent can actually read it.
