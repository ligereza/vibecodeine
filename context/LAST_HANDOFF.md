# SINGLE CHECKPOINT -- repo state

## READ YOUR MEMORY FIRST. Before anything else. Now.

New session, or the same one after a compaction: **read the assistant's local
memory before touching anything.** Not optional. On 2026-07-27 the user had to
order it THREE times in one session and every answer was already written down;
that night an agent "discovered" files the same session had built, reported a
stale state as a defect and asked two answered questions.

Two mechanisms make a memory search come back empty while the answer sits there:
`.remember/` is INVISIBLE to Grep (its `.gitignore` says `*` -- use PowerShell
`Select-String -Path "<repo>\.remember\*"`), and older memories are in English
while the conversation runs in Spanish (`curatoria` = `curation`; search both).
Read `.remember/now.md` and today's `today-*.md` IN FULL. A compacted session's
transcript is on disk: extract stretches with a script, never open 25 MB whole.

Then read this file, `CLAUDE.md` and `MAPA.md`. Then work.

---

This is the ONLY state file. There used to be seven competing ones, which is why
every agent rebuilt the state from scratch and asked the user what he had already
answered; they were merged here on 2026-07-26 and live on in git history and in
`docs/handoffs/archive/`.

Together with `CLAUDE.md` and `MAPA.md`, this is everything an incoming agent
needs to read.

**How it is kept:** it stores ANSWERS, not questions. When the user decides
something, it gets written here IN THE SAME SESSION. An item stays under "Open"
ONLY while nobody has answered it; the moment it is answered it moves to
"Already decided" and leaves the pending list.

**What does NOT belong here:** absolute paths, IPs, phone numbers, credentials or
anything personal. This repo is public. That lives in the assistant's local
memory.

---

## The one rule (2026-07-26, user's words)

> The user is not a software expert; he is an expert on what he wants.
> If the assistant believes a path is optimal for TECHNICAL reasons, go ahead,
> no need to ask -- code, rules or configuration alike. If the assistant assumes
> a STYLE, an aesthetic, or what the user wants, that is an error: ask.

Corollaries, learned from the sessions that failed:

- **There is no deliverable.** Do what was asked. Never invent a product, a plan,
  a report or a backup nobody requested. A finding along the way gets one line
  and you move on.
- **Big steps, not baby steps.** Do not commit and wait for CI every two changes.
- The repo is a USB stick. The conversation is the center, not the repo.
- Measuring exists to answer something that was asked; measuring beyond that is
  how you lose the thread.

## Language (2026-07-26, user's decision)

- **Talking to the user: Spanish.**
- **Everything else: English** -- code, comments, this checkpoint, CLAUDE.md,
  agent docs, commit messages, PR titles and bodies, the assistant's memory. The
  system is already English (Python, git, identifiers, labels), and a Spanish
  term inside it becomes unsearchable: the `curatoria` subsystem was recorded in
  memory as `curation`, so searching the Spanish word returned "nothing found"
  while the answer sat there.
- **The exception, and it is not negotiable: anything a human reads as a
  product.** RD pieces and data, iskvw curation, anything shown to the board or
  to a client goes in correct Spanish WITH diacritics. A title reading
  "reduciendo ano" instead of "reduciendo dano" is not a typo, it is the user
  getting fired. Mangled diacritics in a product are a defect, never a style.

## Who each agent is (this decides which rules apply)

- **Claude Code local** (this session): reads the repo and pushes. The tests that
  protect the software apply. The airdrop validators are not its path.
- **Web / arena agent**: clones the repo but does NOT push. Delivers a ZIP the
  user applies, then asks for a review. `_airdrop/`,
  `scripts/validate_airdrop.py` and the documentation ratchets exist for it.
- **MAK** (Linux box): runs research/codex/plataforma. Its doctrine lives in
  `cultura/mak_plataforma/doctrina/`, NOT in `context/`.

## State

Version 0.56.1. Topology: THREE lines and no more -- `main` (everything, working
and verifiable), `rd` (NGO/data/grants), `iskvw` (curation/artwork), plus `mak`,
which is MAK's INBOX and not a line: nothing lives there, its only exit is a PR
into main. Nobody pushes to main directly: it is protected with `enforce_admins`,
everything lands through a PR with green CI.
User decision 2026-07-28: `main` is the artwork; RD=NGO, iskvw=artist, MAK=server/
generator/curator (Git inbox, third organ). The finished README SVG is
never altered. New tools need no technical permission when they remove manual
work, produce evidence, or add a verified capability -- never utility slop.
Working and verified live: the DREF show chain (LTC -> Chataigne -> OSC -> phone
-> PWA panel), the RD database with normalized events, the hub split into 3
profiles, and the documentation ratchets (`test_mapa_completo`,
`test_higiene_docs`).

## Venue layer deepened: measured geometry, camera as data, flag consumed (2026-07-31)

On top of PR #418 (venue polylines + orbitable viewer): `tools/venue.py
geometria` now measures the geometry block (edges per tier/capa, bbox, closed/
open, zero-length segments, declared measure vs drawn stage -- coherencia warns
when they disagree by >0.15 m); camera paths are DATA (`schemas/
orbita.schema.json`, `data/orbitas/vuelta-completa.json` reproduces the default
turn frame for frame, `venue_secuencia.mjs --orbita`); the viewer takes
`?venue=<id>` (registry form) and `?giro/alto/dist` with the shipped values as
defaults; and the campo skin finally CONSUMES `mejoras.venue3d` -- off (today's
value) changes nothing, on shows a `sala` link. Both branches are asserted in
the smokes. Nothing new is visible by default.

## Security diagnosis: 9 of 10 closed (2026-07-29)

VCD-06 (8 MB body cap, 413 on excess) and VCD-07 (every workflow `uses:` pinned
to a commit SHA + `dependabot.yml`) are closed. Only VCD-10 remains: assigned to
MAK, never verified running.

VCD-09 got its REAL fix on 2026-07-31 (it was only mitigated before, by keeping
the mail path off): signed airdrops. `flujo airdrop sign` writes a SHA-256
manifest + detached HMAC-SHA256 signature (key in `FLUJO_AIRDROP_HMAC_KEY`);
`verify` names the exact file that fails; with the key set, `apply` refuses
unsigned/tampered payloads and the only escape is a human typing
`--allow-unsigned`. The IMAP autoapply path now demands key + valid signature
even when `FLUJO_IMAP_AUTOAPLICAR=1`, and never uses the override. No key
configured = behavior byte-for-byte as before. Detail:
`docs/AGENT_AIRDROP_PROTOCOL.md` "Airdrop firmado".

## Branches: the four lines, and one rescue (2026-07-30)

`main`, `rd`, `iskvw`, `mak` -- plus `rescate/ascii-campo`, which STAYS: it
holds the ASCII-skin work and merging it is the user's aesthetic call. Cleaned
up that day: two stale worktrees (`flujo-organos`, `flujo-sin-gptmini`, whose
content main already had -- verified file by file, not by SHA, because squash
merges rewrite them), three local branches, and two remote branches already
merged. `.vscode/` is ignored now, for the same reason `.agents/` and `.codex/`
are: it is the user's and a `git add -A` swallowed its cousins twice.

## Pending on the machines, and the SOL night (archived detail)

Full detail: `docs/handoffs/archive/20260729_sol_noche.md`. Nothing was lost
that night, the Azure figure was billing lag and not a leak, and Azure is
ABANDONED (his word). On the BOX: reset the inbox with
`git push origin main:mak --force-with-lease` -- the one undrained commit (#375)
was REJECTED on review and agents cannot push that reset -- then verify VCD-10
really runs and curl `GET /api/archivo`. The sync cron already covers
`mak_curatoria`. Still owed from the portfolio-theory debate: the "cuaderno"
contract, one work across six representations, thi.ng traversed by families, and
the iskvw.cl interaction model.

## The rave zip: LANDED 2026-07-30 (PR #402, merged)

Where things are: essay + 16 animated icons in `docs/cultura/ensayos/rave/`; the
motor as a codex capability in `cultura/mak_codex/motor_semantico/` + mode
`iconos`; the research format in `docs/cultura/FORMATO_ENSAYO.md`; the why,
measured, in `MOTOR_SEMANTICO.md`.

Five decisions of that landing, not to be re-litigated:

1. **The style is NOT unified**: `coro` by default, `sistema` the argued exception.
2. **The artefact is an ANIMATION and EDITABLE**: every layer is a named group
   declaring `data-rol/figura/gesto/ritmo` with a `<title>`, so it opens in
   Illustrator/Inkscape and each element answers for what it encodes.
3. **Verification is a GIF, never a PNG**: one frame cannot tell still from
   animated. An instrument, not a deliverable -- GIFs stay out of the repo.
4. **Each icon declares the passage that justifies it** (`ancla`, pinned).
5. **thi.ng is IN USE, not noted**: `hiccup` + `hiccup-svg` + `color` in the
   browser twin `docs/cultura/lib/compilador.js`, verified headless; geometry is
   EXPORTED from the Python vocabulary, never ported by hand. **`CAPACIDADES.md`
   section 6 is the index to read BEFORE writing a generator, a pipeline or a
   graph from scratch** (`tests/test_thing_registro.py`).

Defects the CI matrix caught that a green local Windows run did not, all ONE
lesson -- **the instrument must earn the right to accuse a file**: vendorized
`*.README.md` are THIRD-PARTY (`ZONA_AJENA`); the doc ratchet reads
`git ls-files`, so **an uncommitted `.md` is invisible to it**; rasterizing is
not animating (cairosvg runs no CSS); binary AND flags are picked by PROBE,
since the runner's first browser cannot draw; and the blank frames were
`--window-size` -- below ~100 px the new headless captures from a viewport that
never painted, so the window is asked large and the result CROPPED. `flujo
verify` runs pytest with `-rs`: a guard that skips must not look like one that
measured.

## What a real model did to a boundary a mock never touched (2026-07-30)

The `iconos` mode had only met a FAKE model -- one returning exactly the types
you expect. The first real one (gpt-4.1-mini via GitHub Models; NOT the Azure
account SOL drained) found two things at once. Numbers: `MOTOR_SEMANTICO.md`.

1. **The boundary with a model is validated by TYPE before value.** It returned
   `composicion` as a dict, raising `TypeError` while the mode caught only
   `ValueError`: not a rejection with its reason, a fall. Now REJECTED.
2. **A closed vocabulary stops invented words; it does not fix the SHAPE.**
   Vocabulary alone -> 1 of 3 briefs reached an SVG. Vocabulary + ONE example
   spec -> **3 of 3 on the first round** (`esquema.EJEMPLO`, pinned).

**A measurement that was WRONG:** "one icon is nearly static" was the INSTRUMENT
(the advance injected after `infinite` killed a `... infinite alternate` rule).
All sixteen move within their own cycle.

**Still NOT closed:** the full `iconos.py` -- resource guard, saved piece, job
-- has never run in its place on the box; what ran was the same prompt and
compiler, from Windows.

## iskvw: the substrate is consumed, and MAK's essays reach it (2026-07-30)

The portfolio had none of `PROYECCION.md`'s integrations wired. Three cuts, all
verified running; detail in `iskvw/MAPA.md` + `ESQUEMA_ARCHIVO.md`:

1. **An essay enters the archive through the same contract**
   (`contrato_archivo.desde_ensayo` + `--fuente ensayos`): 33 pieces, 32 links;
   `--fuente todo` gives 41 and 50. Links `manual`, never `semantico`.
2. **The skin asks for the substrate**: `archivo.json` first, degrading exactly
   as before. It is not versioned, so the fallback IS today's live path.
3. **A session is a reproducible seed** (`#semilla=&centro=&escala=`), pinned by
   a test that runs the PUBLISHED file's own functions in node.

**The links are DRAWN: always, faint, by weight** (his call). Underneath the
works, both ends in frame, neighbours indexed once -- the every-pair-every-frame
defect is pinned by a test. Measured: 207 to 615 segments per frame against the
23,871 pairs an all-against-all would cost. NOT measured: fps on a phone.

**The frame cost now has an instrument (2026-07-31):**
`node tools/iskvw_piel_medir.mjs` runs the PUBLISHED skin's functions in node
(smoke technique), enters through the real seed model, and COUNTS the work per
frame deterministically. Reference-machine numbers (2-core Linux container,
node 22): archivo substrate 479 pieces / 269 links indexed once, worst grid
scenario 30 segments per frame; campo fallback 219 works, 0 segments always
(no vinculos shipped), dense open band 217 gradients + 434 arcs per frame at
4-6 ms. `tests/test_iskvw_piel_medir.py` pins the COUNTS (never ms) and a
1200-segment ceiling against the 23,871-pair defect. The phone fps stays the
user's to take -- now WITH a comparator. Finding, one line: with archivo.json
the skin ignores the measured positions (conXY looks only at piezas[0], the
'vola' tool piece, which has none), so the whole 479 field falls back to
hash positions; not touched here, it is how the live site draws today.

**Still the user's, and he wants to DEBATE it first:** whether the essays get
published on iskvw.cl. The bridge is built and unused.

## The works deform the field: the effects patch (2026-07-30, PR pending)

The artist's idea, and it is doublecup's: a work is not EXHIBITED in the field,
it DEFORMS it -- with what the work itself measures. `iskvw/datos/tablero.json`
is a modular-synth patch bay: each row wires a SIGNAL of the piece (tilde marks,
vector subtrazos, how much of what was perceived carries hue, the break tag, its
mass) to an EFFECT it exerts on its neighbours -- `pulso` (their glyph time
dilates and contracts), `curvatura` (they turn around the work), `sangrado`
(its colour bleeds onto them), `desgarro` (glyphs tear by rows) and `gravedad`
(the reading leans on a heavy piece when passing). No datum, no effect: the
coefficient is zero. An effect is an assertion, and no piece asserts what it
does not have.

**The master flag `mejoras.patch_efectos` SHIPS OFF.** Turning the portfolio's
rendering on is the artist's call, not a side effect of merging a branch.

What makes "off changes nothing" a number instead of a claim: the smoke tool
boots the skin three times -- no board, the shipped board, the flag on -- and
demands the first two draw mark for mark the same (7.647 marks identical) while
the third deforms measurably. Measured in headless chromium too: 7.824 marks
identical with the shipped board; with the flag on, 4.080 of them displaced and
1.248 colour changes. One neighbour, named: (609.32, 361.41) -> (585.62, 426.69)
and `rgba(239,231,231)` -> `rgba(239,238,231)`, pulled toward the emitter's hue.

**Cost:** the first version did sin/cos INSIDE the node loop -- 4,5 ms per frame
at 479 nodes (+14%). The rotation is now resolved once per frame per emitter and
the node only walks a fraction of it; the difference against OFF is then within
noise (+-3% over two independent runs, at 219 and at 479 nodes), 58-60 fps at
479. At most THREE works emit per frame, chosen in one scalar pass: no pair of
nodes is ever visited, which is the defect this field was built to avoid.

Found while editing that loop and fixed in the same commit: `abstr` was a free
variable in the glyph branch, only evaluated under the `industrial` regime -- a
ReferenceError waiting for the artist to switch regimes.

**Re-landed on top of venue+vigia (2026-07-31).** Main moved after the branch
(PRs #417 and #418); the merge had ONE conflict, in `tablero.json`: main added
the `venue3d` flag, the branch added `patch_efectos` plus the wiring. Resolved
keeping BOTH flags off plus the full wiring. All piel/venue/vigia tests green
after the merge (full suite 1762 passed, 42 skipped).

**Per-effect switches (2026-07-31), same session:** the patch was all-or-nothing
under the master. Now `efectos` in `tablero.json` gives each of the five its own
switch, all SHIPPED ON so the master alone behaves as before; a switch in false
drops that effect's routes at compile time (coefficient exactly zero, zero cost
per frame). Measured effect by effect in the smoke -- each runs ALONE and must
leave the signature only it can leave (curvatura displaces without recolouring,
sangrado recolours without displacing, desgarro tears x-only, pulso alters the
glyph trace, gravedad drifts the reading), and with all five off the loud board
draws mark for mark like no board at all. The pytest demands the six new
measurements by name.

**Integration (2026-07-31):** effects and the venue layer now share ONE
`tablero.json` fetch in `arrancar()` -- `aplicarTablero(t)` feeds the patch,
`capaVenue(t)` gates the sala link behind `mejoras.venue3d`. The venue smoke
assertions were ported into the `correr({tablero})` architecture of
`tools/iskvw_piel_smoke.mjs`: the shipped board must leave the sala link
exactly as `venue3d` says, and forcing the flag on must create it.

## iskvw: the curation chain closed in a loop (2026-07-31)

The chain from #414/#416 (panel -> curaduria.json -> aplicar_curaduria)
grew three things, all tested; detail in `iskvw/MAPA.md`:

1. **Three optional fields, inert until written**: `peso` (>0, displaces the
   contract's measured peso), `serie` (extra.serie) and `nota` (extra.nota,
   human-read: correct Spanish pinned by test). No skin draws them yet on
   purpose -- what a skin does with them is the artist's call, not an agent's.
2. **`tools/validar_curaduria.py`**: says out loud what the consumer swallows
   silently (unknown/duplicate ids, absent signed svg, invalid values,
   mangled diacritics = ERROR). Exit 1 on errors; the CLI runs over the repo's
   real files inside `tests/test_validar_curaduria.py`, so it is already a CI
   gate.
3. **Panel robustness**: import a downloaded curaduria.json to continue
   editing, beforeunload guard against losing edits, and unknown per-piece
   fields travel out untouched. `tests/test_curaduria_roundtrip.py` runs the
   REAL construirCuraduria() from editor.html in node, feeds the output to
   the validator (0 errors) and then to aplicar_curaduria(): the three
   parties provably speak one dialect. No look change to the panel.

## The repo is not the truth: the two machines are (2026-07-30)

Measured by diffing the disks, which is the check that had never been run.
`coherence.py` does it now, on the box, in both directions.

- **Did SOL's work reach MAK? YES, all of it.** SOL never entered the box -- its
  own session log says three times it had no LAN or SSH access -- so everything
  arrived through the sync cron. The only file the cron cannot update is
  `revisor.py`, frozen since 2026-07-20, which is BEFORE SOL and has exactly two
  commits. Nothing of SOL's was lost. This is the answer to a question that was
  asked twice; it is written here so it is not asked a third time.
- **Six live files existed on one disk only.** `.github/workflows/ordenes_curatoria.yml`
  -- in this repo -- executes `/home/mak/curatoria/ordenes.py`, which was
  nowhere in git. `xio_puente/monitor.py` (172 lines) is started by a systemd
  unit and had no copy either. All rescued; the sync cron now covers
  `mak_xio_puente`.
- **Why it happened: `cp -ru`.** `-u` means "only if the source is NEWER", so one
  edit on the box freezes that file forever. repo -> box is forced every 10
  minutes; box -> repo never happens. `revisor.py` was 165 lines here and 216
  there, and those 51 lines were `enforce_pr()` -- code that merges PRs by
  itself, running every 6 hours, unreviewed. **Pending and ordered: switch the
  cron to `cp -r` AFTER this merges**, never before, or the sync overwrites the
  live reviewer with the old copy.
- **SOL's Azure spend gate was in a stash, not lost** (`stash@{0}`, 2026-07-29):
  Azure leaves the chain unless `RESEARCH_AZURE_ENABLED=1`. Applied. The other
  three stashes were checked by CONTENT: two are already in main or in
  `rescate/ascii-campo`, and the fourth would delete `iskvw/MAPA.md`, which main
  deliberately has.
- **The language rule finally has its measurement**: 236 Python files with
  Spanish comments against 36 in English, while `CLAUDE.md` claims English. That
  gap is why an agent searches in English, finds nothing and declares the thing
  missing. `docs/GLOSSARY.md` maps both sides; new code is English; names that a
  cron line or a systemd unit already invokes are NOT renamed.
- **IBM watsonx works from BOTH machines**, verified 4/4 before a line was wired
  (`tools/watsonx_smoke.py`). Stage 1 fits in the free tier; the $200 credit is
  untouched.
- **watsonx is now FIRST in the default chain (2026-07-30), by measured health,
  not by trust.** Real batch on the MAK box, 8 short `research.py` reports on
  scientific harm-reduction topics with `--providers watsonx`: 8/8 reports,
  32/32 LLM calls, 0 errors, 0 timeouts, 33.7-48.9 s per report (mean 42.1 s,
  search and fetch included). Two of the eight hit the source gate's `cl_legal`
  domain and BOTH found primary sources (bcn.cl, ispch.gob.cl x2), so no report
  needed the SIN FUENTE PRIMARIA mark. Promoted in `LLM.__init__`, in
  `research.py --providers` (the one that actually routes the queue: worker.py
  never passes `--providers`) and in `_SLOTS["razonar"]`. `MODELO_CAPAZ` stays
  `cerebras`: nobody measured llama-3-3-70b against gpt-oss-120b for synthesis,
  and that is a judgement call, not a technical default. Retirement: when the
  credit runs out or expires (~2026-08-18).
- **The source gate HAS a scientific domain since 2026-07-31.** `fuentes.py`
  `DOMINIOS` used to cover `cl_legal`, `cl_fondos` and `norma_tecnica` only, so
  six of those eight biomedical topics got `dominio: None` and no
  primary-source requirement at all. Now `biomedico` (pubmed/ncbi, scielo and
  its country hosts, who.int, euda/emcdda, ispch, cochrane) gates biomedical /
  harm-reduction / pharmacology / epidemiology topics exactly like `cl_legal`;
  it sits LAST in the dict so legal topics that mention harm reduction keep
  hitting `cl_legal` first. Same commit: `dominio_de_tema` now folds
  diacritics before matching, because harvested questions come from human-read
  reports WITH tildes while the pistas are ASCII -- "farmacologia" used to
  miss "farmacologia" with an accent, and "codigo penal" missed the accented
  form too. Pinned in `tests/test_fuentes.py`.

## THE INVENTORIES (2026-07-30). Measured on the DISKS, not on GitHub

The mistake that cost this session repeatedly: asking git when the question was
about a machine. These three were taken by walking the filesystems. They are
written HERE because the first time they were only printed to a conversation,
which is the same defect this whole file is about -- measuring and leaving the
result where nobody finds it.

### 1. Python in the WIN folder `c:\IAlujo` -- 695 files, 129.952 lines

    tests 159 (25.766)   src/flujo 95 (20.921)   mak_plataforma 62 (12.198)
    xio/new-plugins 56 (12.730)   mak_research 32 (8.674)   tapiz 32 (3.173)
    tools 31 (7.487)   scripts 24 (2.995)   projects/cultura 19 (5.171)
    mak_codex 17 (4.061)   + 78 files across nine _archive/legacy_* folders

    By last change: 551 in July, 144 stayed in June (pre-Claude).

### 2. Python on MAK, outside its clone -- 398 files, 83.756 lines

    Apps/llama.cpp 108 (29.405)   codex/piezas 97 (11.904)   research 32 (8.416)
    utilidades 32 (4.275)   plataforma 29 (7.713)   curatoria_inbox 46 (10.056)
    codex 10 (2.216)   OneDrive/MAK 9 (3.202)   curatoria 7 (2.619)
    motor_semantico 7 (1.845)   lenguaje 4   RD 6   xio_puente 3

    By last change: 364 in July, 34 from April-June (curatoria_inbox: the
    user's own material, sent WIN -> MAK to offload; not the box's code).

### 3. Markdown on both machines -- 2.636 files, 231.715 lines

    WIN  784 files / 75.134 lines. Biggest: _archive/legacy_historico_previo 226
         (RETIRED today), docs/handoffs 103 (93 RETIRED today), docs 49,
         .claude/skills 26, .agents/skills 26 (UNVERSIONED FORK: 10 of 41 differ,
         paths rewritten to .Codex/, a directory that does not exist),
         projects/cultura 24, .remember 20.
         By last change: 377 July, 407 June.

    MAK  1.852 files / 156.581 lines, and 57% is what the box wrote itself:
         research/corpus 697, research/informes 266, codex/piezas 97.
         The repo knew 26 of MAK's documents. The machine had 1.852.

**What the three say together:** the repo's own inventory counts 946 .md across
six branches and reads as complete; against the disks it covers about a third.
The heaviest things in this system are not code someone wrote -- they are output
a machine produced, and until today nothing measured whether any of it was read.

## VERDICT (2026-07-30)

**The root defect is one: this organism produces and nothing consumes.** Every
finding of the day is that shape, and the fixes that matter are the ones that
close a loop rather than add another producer.

What was true this morning and is not true now:

- The box ran code that existed on ONE disk (`revisor.py` merging PRs by itself
  for ten days, `xio_puente/monitor.py` started by a systemd unit, three
  curatoria files one of which a workflow IN THIS REPO invokes by absolute
  path). All rescued; drift is now zero across five organs and the sync is
  authoritative (`cp -r`, never `--delete`).
- The safety frame was being sent to the SEARCH ENGINE, which is why the same
  Peruvian pedagogy PDF appears in four RD reports about four unrelated
  subjects. It now goes to the model's system prompt; the search gets the
  subject alone.
- `win` -- a machine the user retired -- sat first in the provider chain with a
  300 s timeout while its docstring promised "cae rapido". 22 of the 37 failed
  codex jobs are `timeout 900s`. Removing it from the chain IS the fix for the
  dominant failure; the retry the organism asked for three times is not needed.
- The routing that produced 4.275 inert lines is closed at the source, and the
  hole that let PR #407 through one hour later ("crear ... cron jobs": artifact
  verb, operational target) is closed by checking the TARGET before the verb.
- Deleted, not disconnected: `agente_real` (repo, box, and its 1,5 MB log),
  `utilidades/` (32 files), `_archive/legacy_2026*` (181), the archive inside
  the archive (283), 93 version checkpoints, 4 cleanup scripts nobody invoked,
  4 files pretending to be tests. **Criterion, so it stops being decided case by
  case: where git holds the history, DELETE; where nothing holds it -- the box
  -- archive. A tag is not accumulation: it is a name for a commit git already
  keeps.**
- `rescate/ascii-campo` and the `mak` inbox: retired and emptied, both anchored
  in permanent tags (`ascii-campo-20260730`, `mak-buzon-20260730`), their value
  extracted first -- the ASCII technique into `iskvw/piel/campo/ASCII_REFERENCIA.md`,
  the inbox's into a measurement (37 codex jobs in FALLO, zero retry logic).

**The portfolio, and the mistake that matters most.** Removing a misplaced
`Math.max(0, -1)` was correct -- it made a written fallback reachable for the
first time -- but that fallback opened the site in the MIDDLE of the archive
instead of the first work, and `publicar_iskvw.yml` deploys from `main` on any
change under `iskvw/**`. The technical fix changed the product. The entry is now
explicit on the first work, stated as a decision instead of inherited from a
bug. **Lesson: a correct fix to dishonest code can still change what a visitor
sees, and that is not the assistant's call to make.**

**What is NOT fixed and is named so nobody finds it by surprise:** `expulsion.py`
is badly DESIGNED, not badly wired -- it watches `_SLOTS` while the failing
provider lives in `LLM.__init__`'s order, and its vigilance depends on another
LLM choosing to vigilate. Do not implement its `--enforce` stub: giving a blind
watchman power automates the blindness. The other defect this paragraph named
-- the harvest never checking what it already answered -- is closed since
2026-07-31 (see "Still open, measured and not rushed").

## The organism writes and nobody reads (2026-07-30, the day's thesis)

Everything measured on the two DISKS -- not on GitHub, which is the trap that
produced this whole class of miss -- says one thing: **this system produces and
nothing consumes.** Nine measurements, one shape:

- `trabajo.py` answers up to 24 questions a day from a backlog that REFILLS
  ITSELF (`cosecha: +3 preguntas al backlog generativo`). Result: 50 reports,
  11 distinct topics, 40 of them sharing one prefix. The same question answered
  forty times.
- `latido.py` is healthy and has produced 44 cultural reports nobody read.
- `agente_real.py` has failed every 30 minutes since 2026-07-23 -- it points at
  WIN's ollama, which the user deliberately retired -- writing 1.5 MB of
  tracebacks into a log nobody opens. It is NOT silent; it is unread.
- `expulsion.py` watches `_SLOTS` while the provider that actually fails
  (`win`) lives in `LLM.__init__`'s default order. A watchman that by
  construction cannot see the failure, invoked only when another LLM feels
  like it.
- `retencion.py` was written 2026-07-17 with the right policy (keep 50, move to
  archive/, never delete) and was never wired to cron.
- `utilidades/` is a WRITE-ONLY directory, verified with a runtime-shaped check
  and not just grep: one process writes, one watches "observationally", zero
  read, import, list or execute.
- **217 reports were moved into an archive/ at 16:28:34 and nobody could
  attribute it.** Not the capataz (it chose `vetear`), not a dry run (same md5,
  the code only moves under `--apply`), not the hub, not the shell history.
  That is not a mystery to solve: it is what three autonomous loops, a dozen
  crons and SSH sessions sharing a filesystem without a log produce by default.

### What changed today, and what it cost to learn

**The sync is authoritative now.** `cp -ru` became `cp -r` (never `--delete`,
which would erase the box's own state) AFTER verifying drift is zero across the
five organs. Until today, one edit on the box froze that file forever: that is
how `revisor.py` came to merge PRs by itself, for ten days, from a copy that
existed on one disk only.

**`mutaciones.py`** signs state mutations, inside the tools that already exist.
Not a fourth loop, not a dashboard -- the point 9 defect is fixed by SUBTRACTING
loops, not by adding observers.

**A Fable subagent was asked to reason about its own artifacts.** Its diagnosis
matched the measurements and its ordering was better than mine (make the sync
authoritative FIRST, because a fix edited in the repo does not land while the
box holds frozen copies). Its distinction is worth keeping: `retencion` is well
designed and badly wired; `expulsion` and the `codificar` channel are badly
DESIGNED, and that changes the repair. Two things it got wrong, both caught:
it proposed `rsync --delete` (would erase the box's state) and placed `tavily`
in the LLM chain when tavily is the search provider.

### The rule the assistant adopted, so it stops asking

Act without asking on anything REVERSIBLE -- the whole repo (git returns it) and
anything on the box that ADDS or MOVES. Stop only for what DELETES on the box or
STOPS a service. Fear applied to everything is not caution, it is paralysis;
applied to the irreversible, it is the job.

### Still open, measured and not rushed

- DONE 2026-07-31: the backlog dedup. `backlog.cosechar` (the harvest
  `trabajo.py` calls every tick) no longer enqueues a question whose slug --
  `research_lib.slug`, THE function that names report files, reused, never
  reimplemented -- already exists as a report in the informes dirs or as any
  backlog entry in any state. This is the cause of the 40-of-50 shared-prefix
  pile: two questions differing only after the 40-char slug hashed differently
  but produced the SAME report file. Pinned in `tests/test_mak_backlog.py`,
  including `backlog.slug is research_lib.slug`.
- Wiring `retencion.py` to cron (the policy was decided thirteen days ago).
- `agente_real`: it is a THIRD decision loop competing with capataz. Decide
  which one lives before rewiring it to watsonx.
- `expulsion`: badly designed, so do NOT implement its `--enforce` stub. Giving
  a blind watchman the power to act automates the blindness.

## MAK como motor: sirve, y el checkpoint mentia

`cultura/mak_plataforma/ideas.py` SI esta conectado al hub y funciona -- este
archivo decia "NO esta conectado ni probado" y por eso nadie lo usaba. Probado
el 2026-07-27: se declara una idea, el micelio la relaciona solo con obras del
archivo, y `encargar()` la pone al frente de la cola. Devuelve ok.

El defecto real de MAK es otro y esta medido: `entregar: 107 listos, 37
entregados, 18 pendientes`, a UNO cada 6 horas. Genera volumen sobre un backlog
que el mismo se autorellena y lo drena a cuentagotas. El mecanismo para
dirigirlo existia y estaba invisible.

## Already decided -- do not reopen

| Date | Decision |
|---|---|
| 2026-07-27 | Las 16 decisiones de ese dia, vigentes: `docs/handoffs/archive/20260727_decisiones.md` (riesgo telefono CERRADO 60fps x4, el loop no escribe docs, curacion=configuracion, vocabulario cerrado en la fuente, archivos no consola, preset viaja, export no rama, MAK atiende issues solo, TLS no UA, CUDA vs OptiX por maquina, la cara no es el costo, PDFs=piezas, tipos=config, cola de triangulacion) |
| 2026-07-26 | Las 17 decisiones de ese dia, vigentes: `docs/handoffs/archive/20260726_decisiones.md` (tres modos de trabajo, iskvw es el portafolio, nadie abre issues, valores de dinero configurables, catalogo de simbolos abierto, brand como info, MAK atiende material del usuario, idioma dividido, referencias como referencias, worktrees podados, crons inutiles fuera) |
| 2026-07-30 | `utilidades/` trazado hasta el origen. Dos fuentes: (a) mejora_libre -> `agente_libre.py` sin `--objetivo` -> sus 6 semillas fijas; funciona como fue disenado. (b) `capataz.py:297` accion "codificar" con pedidos de forma OPERATIVA (actualizar ajustes_junta.json, ejecutar backlog_codex, cron) enrutados a un canal cuyo contrato es un archivo stdlib autocontenido que NUNCA se ejecuta. Un pedido de ops no puede satisfacerse con un archivo que nadie corre: el coder inventa rutas y CLIs porque no puede verificarlas. El defecto es de ENRUTAMIENTO, no del codigo ni de la infra (ajustes_junta.json, backlog_codex.py y salud_proveedores.json SI existen). NADA SE BORRA. Los 3 PR del buzon (#375 #400 #404) quedan sin mergear hasta resolver el enrutamiento. Trabajo siguiente, NO en este cierre: que el prompt de codificar rechace pedidos con forma de ops, o que exista un verbo real para "cambiar un ajuste en la caja" (hoy solo esta "mantener", que es dry-run). |
| 2026-07-10 a 07-25 | Decisiones mas viejas, vigentes pero fuera de la lista viva: `docs/handoffs/archive/20260722_25_decisiones.md` (panel de suplementos innecesario, la carpeta de diseno no se respalda desde el repo, los dos planes grandes RECHAZADOS, `desktop/` archivado, Instagram via parth-dl, n8n descartado, Gemini fuera, nada de Oh My Posh) |

## Built on 2026-07-26, waiting for the user to look

Tres prototipos, todos regenerables por comando desde datos reales. Detalle en
`docs/handoffs/archive/20260726_prototipos.md`: la propuesta a la directiva RD,
el prototipo del archivo iskvw, y MAK + portafolio visibles en la app.

## Blocked, waiting on the user

- **Portfolio aesthetic references: FOUND, not lost**, and the paths are in the
  assistant's local memory because they are personal. Three sessions declared
  them gone in ephemeral cloud containers while they sat one level above the repo
  on his own disk -- everyone searched the repo and their own memory, then
  declared absence. Which direction is current is style, so it gets asked.
- **Design exports: RESOLVED (user's word, 2026-07-29).** This entry had
  already been wrong twice; the third failure was staying listed as pending
  after the user resolved it -- an agent repeated it back to him as open and
  he had to correct it. Details live on his machines, not here. The lesson
  compounds: an answer not written in-session gets asked again.

## Las cuatro capas: no confundirlas (2026-07-27)

Repo = como/por que/medido; memoria local = rutas/IPs/personal; carpeta local
= material pesado; MAK = lo percibido, entra por PR. Tabla completa y las dos
formas de romperlo: `docs/handoffs/archive/20260727_capas.md`.

### Still open from 2026-07-26

Detalle en `docs/handoffs/archive/20260726_pendientes.md` (ideas.py CONECTADO,
render por defecto sin medir, root J6+ pospuesto, bridge_issue_render no corre
solo). Delegating: bound every search -- a subagent's `find /` burnt 2124s.

## Open

- **The order the user set for the last stretch (2026-07-27, his words):**
  RD presentable with zero errors -> MAK working and autonomous -> iskvw
  (references + the svg bundle: a structure with CLEAR CONNECTORS so the
  presentation or the style can be swapped) -> a `MAPA.md` per line so
  navigation is obvious -> README updated -> the handoff updated on every line.
  **RD and MAK are done. iskvw is what remains.** Its map is
  `docs/rd/MAPA_RD.md` for RD; **iskvw's own map EXISTS since PR #368
  (`iskvw/MAPA.md`)** -- this entry previously said it was missing and that
  was stale.
- **What the 2026-07-27 iskvw stretch got wrong.** Detail archived in
  `docs/handoffs/archive/20260727_iskvw_lo_que_fallo.md` (it treated the curation
  as a blocker, dismissed two references without opening them, invented a GPU
  limit, built on the wrong source, shipped positions from a hash the repo had
  already warned about, left 60 zero-byte SVGs, tuned a parameter without
  measuring). The one line that matters: **if you are about to say "this does not
  apply" about something the user sent you, open it first.**
- **thi.ng libraries IN, vendorized** (`data/iskvw_librerias.json` +
  `py tools/vendorizar_iskvw.py` -> self-contained ESM in `iskvw/piel/lib/`,
  21.6 KB: tsne, geom-trace-bitmap, rstream-gestures, distance-transform).
  **Correction, measured: `@thi.ng/tsne` cannot take 768 down to 2** (output
  dim = input dim), so `gen_campo_iskvw.py` still needs sklearn;
  `tests/test_iskvw_librerias.py` pins it. The sci-fi reference's
  `node-network` has the every-pair-every-frame defect; its `objParser.ts` IS
  the 2D/3D answer.
- **DONE 2026-07-27: the archive is ONE file.** Position is now an optional field
  of the contract, so `archivo.json` carries relations AND positions: 1004 pieces,
  3188 links, 697 with position, measured against the box. It was 0 before,
  because the micelio ids carried the file extension and the field's did not, so
  the keys never met. Generators stay separate on purpose -- projecting needs the
  768-dimension vectors and the contract neither has nor wants them. Loose thread
  noticed, not chased: the contract counts 705 obras and the field 697.
- **iskvw, what it is actually asking for: the SUBSTRATE -- first brick laid
  2026-07-29.** The micelio -> pieces+relations conversion now lives in ONE
  place, `cultura/mak_plataforma/contrato_archivo.py` (pure function), shared
  by `tools/gen_archivo_iskvw.py` and by the box's face at `GET /api/archivo`
  (hub.py is covered by the sync cron), so any skin or external agent asks
  "the pieces and their links" and always gets the ESQUEMA_ARCHIVO shape --
  without knowing the micelio's internal node schema. Id formation can no
  longer fork (the 1004-pieces/0-positions trap); `tests/test_contrato_archivo.py`
  pins the delegation. Still open of the substrate vision: no skin CONSUMES
  archivo.json yet (the live campo skin reads campo.json, which carries no
  vinculos), and drawing measured links on the site is a style call for the
  user. The rule it inherits is the doublecup thesis: **no element may claim
  a datum it does not encode.**
- **MAK re-perceives on its own; do not touch it mid-run.** The six traps
  that cost real time (SSH-launched processes die, pgrep let two perceptions
  share 4 GB, procesados.txt is held, patched code is not loaded code, nested
  heredocs break, copying a file does not restart its service) are in the
  assistant's memory. When it finishes, read its output before feeding it.
- **DONE 2026-07-29: the last hop to the RD database is wired.**
  `tools/gen_propuestas_rd.py` feeds `mineria_rd.proponer()` from the repo's
  own `candidatos_db.jsonl` (no OCR, no GPU, no box), re-matching against the
  CURRENT catalogues, reporting dudosos without drafting them, requiring
  evidence >= 2. Measured on the real 970 rows: 0 new productoras (7 already
  known), 2 real venue drafts (Club Hipico, Teatro Caupolican), 0 garbage.
  Two defects found and fixed on the way: "Reduciendo Dano Chile" escaped the
  own-identity deny-list (pattern added + regression test), and cities came
  out as venues (geography filter). Drafts enter only by human-reviewed PR.
- **Logos: RESOLVED (user's word, 2026-07-29).** This file and
  `docs/rd/MAPA_RD.md` ("6 de 20") kept it listed as pending after the fact;
  the standalone already bakes the vector logos in (#335). If MAPA_RD's count
  is re-measured, do it against the real `knowledge/logos/`, not this note.

**How this list is kept honest:** on 2026-07-26 it carried an item that had
already been fixed that same day, plus a second copy of the Illustrator entry
that contradicted the corrected one. A pending list nobody prunes stops being a
list of what is pending. Before working an item, check it is still true.

- **The `mak` inbox has no defined drain, and that is the one thing that would
  turn it back into a line.** MAK opens a PR into `mak` every 6 hours; nothing
  moves `mak` into `main`. Verified working on 2026-07-26: the box fetches all
  branches before checking out, so delivery against the inbox does run. What is
  missing is the exit — today that is a human-curated PR, same as any
  line -> main promotion. If the inbox ever holds work `main` has not seen for
  long, the topology has quietly broken and needs fixing, not tolerating.
- **`rd` and `iskvw` point at the SAME commit (`abc26891`)** while the README
  calls them different lines. Written down, not resolved: whether that is
  intentional is the user's call.
- **4 local stashes never examined** (none from this session):
  `sol-azure-optin-gate-redundante`, `ascii-wip-ultimo-agente`,
  `mak-vocab-ultimo-agente`, and a WIP of `retirar-destinos-muertos`. A local
  stash is invisible to the repo and dies with the machine. Pending: open them
  one by one. The first matters most -- the user suspected for days that work
  from the SOL session was never applied and was told it did not exist.
- The hourly `[OBS]` issue emitter is still unidentified. Ruled out: the repo and
  MAK (nothing there creates issues). A session on 2026-07-24 already ran this
  hunt and logged it unresolved. Not urgent, and not worth chasing again without
  a reason.
- The Gmail bridge still turns GitHub's own notification e-mails into new issues.
  The workflow already ignores those echoes, so they do no work, but they keep
  being created: the filter has to live in the user's Apps Script, discarding
  anything sent by `notifications@github.com`. Outside this repo.
- The repo's front door is honest again but the CLI still speaks Spanish to the
  operator, so `MAPA.md`'s generated command table does too. That is deliberate
  (it mirrors what the user sees when he runs a command), not an oversight.

## The night session (2026-07-30, Fable): the field is ALIVE, and the laser line opened

The portfolio breakage the user reported was found by EXECUTING, not reading:
PR #403's refactor left `destino`/`dy` out of scope -- ReferenceError on frame
one, frozen canvas, every python test green because nothing ran the skin's JS.
Fixed, plus the guard so the class dies: `tools/iskvw_piel_smoke.mjs` runs the
real inline script in node in CI, walks the field so the per-node code
executes, fails on async errors and on a vacuously-empty field (verified both
ways: exit 1 on the broken skin). PRs #408-#412, all merged:

- #408 skin fix + smoke guard + archivo.json generated at publish time.
- #409 venue commons base (block B of paqueteintegrar; block A landed in #405).
- #410 crontab.mak versioned + reference ratchet (see the correction below).
- #411 a pieza_grafica presents ITS OWN animated svg on the stay-still gesture.
- #412 the artist's works: 219 curated pieces (campo.json under the user's
  filter) become first-class contract pieces via `desde_campo` -- the
  CI-generated archive used to carry NO artist works when the micelio was
  unreachable -- and each derives its animated piece with the motor semantico
  (deterministic: measured tilde -> latir (160 works), measured colors -> tono,
  id-seeded elsewhere). Field measured live: 479 pieces, 269 links, 61 fps,
  doublecup texture (the glyphs ARE each work's perceived vocabulary,
  diacritics included). The user's corrections that shaped it: the 8 obras.json
  entries are TOOLS, not works; the rave essay was the DEMO of the mechanism.

A correction of my own inside the night: I restored `agente_real.py` citing a
cron that the day session had already retired -- stale evidence, my own
crontab capture proved it and I did not re-read it. Reverted (file out of repo
and box again); the crontab ratchet stays and would have caught exactly this.

The laser line (user's toolkit now in-repo at `docs/laser/TOOLKIT_INDICE.md`,
his real rig: 2x Pangolin, FB3-QS, QuickShow without BEYOND): `flujo laser`
CLI (hatched / flow / lote -> manifest), the 600-1000 points-per-frame budget
built in (declared tolerances in order, over-budget REPORTED never cropped),
`desde_laser` joins pieces to curated works by media id. Upstream state,
measured: vpype installs fine; the hatched and flow-imager PLUGINS are broken
against numpy 2.x (flow: kdtree TypeError; hatched: empty output) -- numpy<2
pin under verification at close. The tool degrades honestly (estado + clear
install instructions) either way.

Deploy state at close: iskvw.cl serves the #411 build (41 pieces, essay icons
reachable). The 479-piece field ships when the laser-tool PR merges: it
carries the workflow fix (mirror iskvw-internal piece dirs at their repo
paths) for the deploy that the new coherence gate correctly blocked.

## Laser line, second pass (2026-07-31, Fable worktree): route B closes in-repo

The toolkit's own restrictions were the spec: QuickShow imports ONLY
.ILD/.LDA/... never SVG (restriction 5), and no ILDA package exists on PyPI
nor as a vpype plugin (restriction 7) -- until now the SVG->.ild step needed
Modulaser (subscription) or msvg2ild (monochrome, AGPL). `src/flujo/laser.py`
now carries, pure Python and vpype-free:

- `flujo laser ild pieza.svg`: ILDA format 5 (2D true color, NEVER palette --
  the toolkit's golden rule) with blanked dwell points per stroke, byte
  deterministic, and the CLI re-reads every file it writes before reporting
  (`leer_ild` is the verification half). Smoke-run measured: 3-stroke SVG ->
  320-byte .ild, 32 points (24 blanked), format 5, re-read matches.
- `flujo laser medir pieza.svg`: vertices, subpaths (<8 rule), drawn length
  and PEN-UP TRAVEL in numbers. `--medir-viaje` on hatched/flow measures the
  blanked travel before AND after linemerge/linesort (one extra vpype pass;
  test fixture: 198.0 ud -> 98.0 ud), so the sort benefit is a number.
- `flujo laser lote --ild` drops a QuickShow-importable .ild next to each SVG;
  manifest rows gain ild/puntos_ild/trazos/viaje_apagado (additive, contract
  join untouched). Defaults unchanged: SVG-only, same vpype pipeline args.

The geometry layer refuses curves/rects/text with the vpype flattening
instruction instead of silently dropping shapes. Restriction 7 in
TOOLKIT_INDICE.md now carries the in-repo note so nobody re-researches an
external converter that the repo already has. Still pending from the night:
a completed flow_img run (experimental), scanner kpps confirmation.
## The language rule has its ratchet (2026-07-31)

`tools/idioma.py` measures the language of COMMENTS AND DOCSTRINGS ONLY
(never identifiers, never product strings) in every tracked `*.py`
(`git ls-files`, archive + vendorized zones excluded, same convention as
`test_higiene_docs`). Measured on the real tree: 581 files = 388 Spanish +
96 English + 38 mixed + 59 none, so 426 files carry Spanish -- the 07-30
"236 vs 36" note undercounted because it did not read docstrings.
`tests/test_idioma_ratchet.py` pins that set in
`tests/fixtures/idioma_baseline.txt`: a NEW file carrying Spanish comments
fails the suite with the offender named; cleaning files never fails, and the
pin is lowered with `python3 tools/idioma.py --baseline > <fixture>`.
Renames are NOT demanded: cron/systemd consumers keep their names, per
`docs/GLOSSARY.md`. The tool also prints a soft FYI (not enforced) of
widespread Spanish identifiers the glossary does not map yet -- top spread:
`nombre` (69 files), `salida` (63), `ruta` (62), `linea` (46), `datos` (45).

## 2026-07-31: the zip landed, and the field was lying since the substrate

The ten area branches produced overnight arrived as a bundle on the user's
disk, audited by a web agent. All of it is in `main` now (#421 + #422), plus
three defects that only surfaced BECAUSE it landed. Verified by content, not by
SHA -- squash merges rewrite them.

**The one defect that mattered.** `iskvw/piel/campo/index.html` decided for the
WHOLE field whether the archive carried a projection by reading `obras[0]`.
True while `campo.json` was the only source (219 works, all projected); false
the moment `archivo.json` arrived (479 pieces, 219 with a measured position and
260 without -- the derived animated pieces, MAK's essays, and the 8 `obras.json`
entries that are TOOLS and not works). The first entry is one of those, so the
published site spread everything by hash and the measured projection was never
used. Measured with the substrate on disk: 203 marks per frame instead of 7647,
field stretched to ~220.000 px, effects patch INERT. Whole suite green.

**Why the suite could be green: the instrument measured the easy world.**
`archivo.json` is gitignored and only `publicar_iskvw.yml` generated it, so CI
tested a one-source world while the site served another. `ci.yml` now generates
it before the tests, and the smoke compares the drawn field against the data on
disk (red on the old skin, green on the new). That is the cut that kills the
class.

**Landing the areas then exposed a SECOND link layer that had never drawn.** It
joins pieces by shared tag, all-against-all, per frame. It drew ZERO while
`campo.json` was the source (those pieces carry no `tags`); the substrate gives
all 479 `etiquetas` and lit it up: 35.902 segments and 31,7 ms per frame against
a ceiling of 1200 the repo itself declares. Now gated on there being no measured
links -- `archivo.json` brings 269 MEASURED ones, drawn by weight underneath
(the artist's call of 2026-07-30). 99 segments, 1,0 ms. Nothing a visitor ever
saw was removed: it only ever drew where it still draws. The pinned counts were
re-taken for the same reason -- 0/6/30/0/9/14/14 counted a defect, not a cost.

**The render bridge, same shape.** `renderizar` and `entregar` were one act
against a fixed `render_output.png`, so a failed upload cost a whole new render:
issue #420 rendered twice (~7 min each) while rclone had written 363 MB trying
to deliver 16,6 MB -- an internal retry loop, not a slow link (8 MB went up at
306 KiB/s in the same window). The render is saved under its own name, a pass
that finds it only delivers, and rclone's retries are bounded.

**MAK does its work well, and the handoff's own measurement was wrong.** This
file said 40 of 50 reports shared one prefix. Measured 2026-07-31: 83 reports,
53 of them the productora triangulation, and those 53 are 53 DISTINCT events --
the slug truncates at 40 chars and collapses them in a listing. 35 of 53
identified the productora, 18 did not, and the ones that failed say so in the
RESUMEN and open a LAGUNAS section. That is the good behaviour, not the
dangerous one.

**watsonx is on the FREE Lite plan and the $200 credit is untouched.** Measured
with `tools/watsonx_smoke.py` on the box: IAM bearer OK in 475 ms, 24 models
visible, and the chat call returns `429 consumption_limit_reached -- the total
number of free concurrent requests for model meta-llama/llama-3-3-70b-instruct
has reached its limit 10`. `/home/mak/n8n-local/research.env` carries ONLY the
four `WATSONX_*` keys, so `refutar.py`'s default chain (groq, cerebras, azure,
ollama) has no credentials at all and dies with "Todos los proveedores
fallaron. Ultimo: None". Consequence, and it is the answer to "how does IBM
raise quality": `refutar.py` cannot run today -- 83 reports, ONE refutation,
from 2026-07-16, about mate. Moving the watsonx Runtime instance from Lite to a
paid plan is a console action in IBM Cloud and it is the user's; it is what
makes the adversarial pass viable and what starts consuming the credit.

**Branch topology is back to the four lines.** `main`, `rd`, `iskvw` (both
fast-forwarded to main, 0 behind), `mak` (the inbox, 14 behind, untouched).
Three stale branches deleted AFTER tagging them (`archivo/<branch>-20260731`,
plus `efectos-419-20260731`), per the repo's own criterion: a tag is a name for
a commit git already keeps. PR #419 closed as superseded.

**Still the user's, and not touched:** whether MAK's essays get published on
iskvw.cl, and where the 260 unpositioned pieces belong beyond not breaking the
field. `MEMORIA_DIRECCION.md` -- the document that orders the income lines --
is NOT in the repo; it lives only on his disk.

## 2026-07-31, second half: the two departments that could not reach their provider

IBM watsonx moved off the free Lite plan to a paid instance (the user's console
action; the API key never changed and the project needed re-associating, which
took a few minutes to propagate). That unblocked a measurement that had been
impossible, and it found the same defect twice.

**`refutar.py` could not be run at all, and it was not the rate limit.** It
filtered its `--orden` against a literal `("groq", "cerebras", "azure",
"ollama")` written by hand, which predates `watsonx` and `win`. So
`--orden watsonx` was dropped without a word, the list came out empty, the
default chain took over, and every provider in it was skipped for having no
key: `RuntimeError: Todos los proveedores fallaron. Ultimo: None` -- a message
that names nobody because nothing was ever attempted. On the box,
`/home/mak/n8n-local/research.env` carries ONLY the four `WATSONX_*` keys, so
the tool discarded the only provider with credentials and blamed the providers.
That is why the adversarial pass had run ONCE since 2026-07-16: 83 reports, one
refutation, about mate. Fixed in #426: `PROVIDERS` / `PROVIDER_ENV_KEY` in
`research_lib` are the single source, `call()` derives its dispatch from them,
and an unknown name is dropped OUT LOUD.

**The same shape in codex, one hour later (#427).** The live chain was
`CODER_CHAIN=win,nim-pro,nim-flash,ollama` -- `win` FIRST, and `win` is the
notebook the user retired; probed from the box it does not answer. Of 109 codex
jobs in FALLO, 22 read literally `timeout 900s`. The department that writes
code began every job waiting on a machine that is off, while watsonx was not
even a key in the map. `watsonx_chat()` is now a module function shared by both
departments (codex gets no second copy of the endpoint, and asks for
temperature 0.1 because a warm coder invents APIs). `win` leaves the default
and stays in the map.

**The model is measured, never chosen by its name.**
`tools/watsonx_coder_bench.py`, two runs on the real account, six
interval-merging cases EXECUTED: four of five candidates 6/6 between 1,3 and
2,8 s, and `ibm/granite-8b-CODE-instruct` 5/6 -- the only one labelled "code"
is the only one that fails, and it fails by keeping the invalid interval
instead of dropping it. A measurement that did NOT hold is recorded with it:
mistral-small took 39 s on the first run and 1,7 s on the second, so that was a
spike and not a property. Two runs is the reason it is known.

**The adversarial pass RUNS now, and as first wired it would have rubber
stamped the lie.** Run against the claim of the most dangerous report in the
repo it answered "sostiene parcialmente", citing UNAM cultural-studies papers
and a Swedish Wikipedia stats dump. Cause: `refutar.py` glued the cultural
frame onto the topic and searched with the whole string -- exactly what
`marco_solo()` was written to cut in `research.py` on 2026-07-30, still alive
there. With the frame going to the MODEL, the source gate choosing the queries
(`fuentes.dominio_de_tema` -> `sugerir_queries` -> `evaluar` ->
`instruccion_sintesis`), and a different model per role, the same claim comes
back: `dominio cl_legal -- 6 de 10 fuentes son primarias`, sources reaching
`bcn.cl/leychile`, the proponent refusing to argue it, and the verdict
**"REFUTADA por falta de respaldo en las fuentes primarias"**.

**MAK does its work well, and this file's own measurement was wrong.** It said
40 of 50 reports shared one prefix. Measured: 83 reports, 53 of them the
productora triangulation, and those 53 are 53 DISTINCT events -- the slug
truncates at 40 characters and collapses them in a listing. 35 of 53 identified
the productora, 18 did not, and the ones that failed say so in the RESUMEN and
open a LAGUNAS section.

**Named, not fixed:** the search itself is flaky. `web_search` goes to a
self-hosted SearXNG first and falls back to Tavily, and the box has no Tavily
key, so a pass can come back with zero sources. With zero the gate reports
honestly (0 of 0) and the verdict softens -- the reasoning is right, the
evidence was not there. And `refutar` is NOT wired as an automatic per-report
gate: doing that before the search is reliable would stamp "adversarially
verified" on invented claims.

**On automating the model choice (the user asked).** The BENCH can run alone --
it executes code against cases, there is no judgement in it. Letting a model
decide which model leads is the `expulsion.py` pattern and must not be built:
today's run is the proof, since a model asked "which one codes best" would have
answered "the one called code-instruct", which is the one that failed.

**Deploy verified against the LIVE site, not the repo:** `iskvw.cl` serves
`const medida = o =>` (1 hit), `conXY` (0 hits), and `datos/archivo.json` with
479 pieces / 269 links / 219 positioned. The published portfolio draws the
works where they were measured.

## The comments in a file are its incident log. Read them BEFORE editing it

2026-07-31, and it is the best thing found that day. The same defect was hit
THREE times in one afternoon, and the third time the bite was already written
three lines above the line being edited.

The shape, every time: **a hand-written list that stopped matching reality,
discarding in silence the only thing that worked, and an error blaming
something else.**

    #426  refutar.py     a literal ("groq","cerebras","azure","ollama") that
                         predates watsonx -> dropped the ONLY provider with a
                         key -> died saying "Todos los proveedores fallaron.
                         Ultimo: None". Nothing had been attempted.
    #427  codex_lib.py   _CODER_CHAIN_MAP with no watsonx and `win` -- a
                         retired machine -- first -> 22 jobs reading
                         `timeout 900s`.
    (3rd) percepcion.py  CLAVES_VISION, a hand-written allow-list of keys,
                         swallowed the `_motor` field -> a whole run reported
                         "motor watsonx: 0" and the transport got blamed for a
                         path that had worked all along.

And `percepcion.py` carried this, three lines above the line in question:

> "Antes esto estaba cableado a un solo esquema y descartaba en silencio todo
> lo que pedia el prompt nuevo (headliners, conceptos, oportunidad_codigo...)"

The file had been bitten by that exact dog before and wrote it down. Nobody
read it. **A comment is not decoration and it is not documentation: it is the
scar of an incident, and it is the cheapest warning in the repo.** Read the
comments around what you are about to touch before touching it.

Three rules that follow, and they are mechanical, not moral:

1. **What is discarded, is discarded OUT LOUD.** Any allow-list must report
   what it dropped, with the id of the record. Two lines:
   `set(recibido) - set(declarado)` and a print.
2. **A default that fills an absence destroys the field that measures it.**
   `motor = vision.get("_motor") or "ollama"` turns "nobody attributed this"
   into "ollama did it", and the next count counts ghosts. If it did not come,
   it says so (`sin_atribucion`).
3. **An empty value and a value that never arrived are not the same fact.**
   `if vision.get(k)` collapses them, and then no consumer can tell a
   measurement that found nothing from a key nobody sent.

Retirement: when a check enforces rule 1 across the repo.

## Do not debug: COUNT

Same day, same session. An hour was spent chasing a symptom that a grouped
count answered in one step: 127 fichas, and grouping the failures by their
LITERAL message gave `10 contact_sheet_fallo` and nothing else. One failure
mode, ffmpeg on `.mp4`, with zero relation to what was being debugged.

Earlier the same day the same technique had already paid: 22 identical
`timeout 900s` entries in the codex job log WERE the diagnosis, not noise.

Before opening a debugger: group the failures by literal message and look at
the distribution. The information is almost always already written, many times
over, in a log nobody reads.

## Where this was left, 2026-07-31 night (PR #428)

Everything below is IN PR #428, green on the full matrix at close.

**The skin is swappable now, and it was never verified.** There were THREE
skins -- `campo` (1323 lines), `terminal` (772), `venue` (505) -- and both
`iskvw_piel_smoke.mjs` and `iskvw_piel_medir.mjs` read the literal path
`.../piel/campo/index.html`. Two of three had NO verification and NO
measurement of any kind. Pointing the battery at them broke three times and
NONE of the breaks was the skin: the canvas was only returned for the id "c",
element-level `querySelectorAll` was never stubbed, and the "work done" metric
counted gradients and glyphs -- how CAMPO draws, while venue draws polylines.
The instrument was shaped like one skin and called that a verification. Both
skins work: venue draws 503 edges, terminal 3.480 marks.

What exists now: `schemas/piel.schema.json` + a `piel.json` per skin declaring
what it fetches, HOW WHAT IT DREW IS COUNTED (`medida`), and per layer THE
DATUM IT ENCODES. The battery is a common CORE plus extras gated on declared
capabilities. Stubs live once in `tools/lib/piel_dom.mjs`. A manifest that lies
FAILS -- there is a test that breaks one on purpose and restores it.

**The substrate: watsonx sees, and the model was chosen by measurement.**
Probe first (`tools/watsonx_vision_smoke.py`) because vision was inferred from
model NAMES. Then a bench with two ground truths already on disk and never
used: tesseract's OCR (non-empty in 24% of fichas) and the ficha gemma3
produced. Invention counts AGAINST. Result, and it is the second time in one
day that a model's name lied:

    llama-3-2-11b-VISION   solape 0.414   3 inventados   40.175 tok
    mistral-small-3-1-24b  solape 0.807   0 inventados    7.710 tok
    llama-4-maverick-17b   solape 0.807   1 inventado    12.019 tok

`PERCEPCION_VISION=ollama|watsonx`, ollama by default: without the variable the
behaviour is byte for byte today's. Run in progress at close: **610 of 1401 ig
fichas, 0 errors**, ~4 s/file, ~964 tokens/image -> the whole corpus is about
US$2. The credit still cannot be burned by this work; what rises is what is
seen. Measured on 105 attributed fichas: `tipo_obra` 0% -> 100% (the field
whose absence forced classifying 697 works by hand), `colores` 87% -> 100%,
`texto_visible` 22% -> 20% (WORSE, said because it is worse).

**Buttons, behind a gate made of generated data.** `context/comandos.json` is
the CLI as DATA (91 commands, 16 groups), generated from the same tree as
MAPA.md's table so they cannot fork; each entry carries `estado` (`listo`, or
`falta: <what>`) so an interface can show OBJECTIVES instead of commands.
`GET /api/comandos` and `POST /api/comando` run one command FROM the manifest
only -- no free-form string, no shell. `destructivo: True` demands
`confirmar`; `null` demands it too, because "nobody classified it" is not "it
is safe". `FLUJO_NTFY_TOPIC` notifies FAILURES only, and the answer declares
whether anyone was actually told.

### The count that closed a question, and the unit that fooled me

Asked where "the other 8" failures were between `10 fallos.json` and `18
medicion.vision=fallo`: there was no gap. `fallos.json` counts FILES, the
ficha field counts ROWS, and a retried file writes a ficha per attempt -- 8
files x2 + 2 files x1 = 18 rows over 10 files. Two units measuring one fact,
reported by me as if they were two populations.

The real finding underneath: **retrying is useless when the cause is
structural.** All 10 were the missing `_tmp` directory, so every retry only
duplicated the ficha. After the fix: 0 files, 0 rows.

### Next, in order

1. Finish the ig run (~800 left) and re-measure coverage over the full 1401
   with attribution. Then the same for 10 RD flyers as a probe -- RD is more
   OCR than description and its database is partly done.
2. `B.2` has the API but NO UI yet: the hub does not draw the buttons.
   `context/comandos.json` is there and `/api/comandos` serves it; what is
   missing is the panel that renders it.
3. The search is still the weak link for `refutar`: SearXNG first, no Tavily
   key, so a pass can come back with zero sources. Until that is fixed,
   wiring refutar as an automatic per-report gate would stamp "adversarially
   verified" on invented claims.

## The IBM credit is burned by the CLOCK, not by the work (2026-07-31, measured)

This corrects, with billing data, something said earlier the same night. It is
the most expensive thing in this file.

The question was where two million tokens came from. They were real -- the
perception run, 1.946 tokens per image measured on the production path, 715 of
720 fichas attributed to watsonx. But they are not what costs money. The
account's own billing API says:

    agosto (desde 00:00 UTC), instance mak-watsonx-runtime
      INSTANCES                    0,0323 instancia   ->  US$ 35,81
      MODEL_INFERENCE_THIRD_PARTY  1.834 RU           ->  US$  0,19
                                                          ---------
                                                          US$ 36,00
    julio entero, en el plan Lite
      448 RU third-party + 15 RU IBM                  ->  US$  0,05

**99,5% of the spend is a fixed charge for HAVING the paid plan.** `0,0323
instancia` is the fraction of the month elapsed -- about one day -- so the plan
prorates to roughly US$1.110 a month. The 1,34 million tokens of perception are
those nineteen cents.

Consequence, and it inverts what was said before: the US$200 credit is NOT
safe from being spent. Earlier that night the conclusion was "this work cannot
burn the credit", and that is true of TOKENS and false of the TOTAL. At ~US$36
a day the credit is gone in under six days, not on 2026-08-18.

Two things follow, and both are the user's call because they are money:

1. **While the plan is on, using it is free.** The day is already paid; the
   marginal cost of a run is cents. So anything worth measuring should be
   measured NOW, not scheduled.
2. **Going back to Lite stops the clock.** Lite caps concurrency at 10, which
   breaks `refutar`'s parallel refuters, but sequential perception works there.
   Nobody has checked whether the paid plan has a cheaper variant; only the
   `plan_id` is visible from the API, not the catalogue.

How to read it again, without a console:
`billing.cloud.ibm.com/v4/accounts/<bss>/usage/<YYYY-MM>`, with the account id
read from the `account.bss` claim of the IAM token. Cost per metric is in
`resources[].plans[].usage[].cost`.

**And a measuring trap found on the way:** the bench reported 964 tokens per
image and the real run spends 1.946. Not the model -- the SIZE. The bench
resizes to 1024 px, `percepcion.py` to 1280 (`MAX_LADO_VISION`). That doubles
the token cost, and nobody has measured whether those 256 px of side buy any
accuracy: the `solape 0.807` that chose the model was obtained at the CHEAP
size. In money it is pennies; as a habit it is paying double for something
never measured.

**State at close:** the ig run is left going on purpose -- the day is paid.
720 of 1401 fichas, 0 errors, ~4 s/file, output in `/tmp/fichas_v4` on the box
(NOT over `fichas.jsonl`; comparing the two passes is the only way to show it
improved). When it finishes: coverage over the full 1401 with attribution, and
then the same 1024-vs-1280 comparison.
