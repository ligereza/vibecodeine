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

## Security diagnosis: 9 of 10 closed (2026-07-29)

VCD-06 (8 MB body cap, 413 on excess) and VCD-07 (every workflow `uses:` pinned
to a commit SHA + `dependabot.yml`) are closed. Only VCD-10 remains: assigned to
MAK, never verified running.

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

Where things are: the essay and its 16 animated icons at
`docs/cultura/ensayos/rave/`; the motor as a codex capability at
`cultura/mak_codex/motor_semantico/` + mode `iconos`; the new research format in
`docs/cultura/FORMATO_ENSAYO.md` (`research.py --formato ensayo`); the why, with
its measurements and honest limits, in `docs/cultura/MOTOR_SEMANTICO.md`.

Five decisions of that landing, not to be re-litigated:

1. **The style is NOT unified**: `coro` by default, `sistema` the argued exception.
2. **The artefact is an ANIMATION and it is EDITABLE**: every layer is a named
   group declaring `data-rol/figura/gesto/ritmo` with a `<title>`, so it opens in
   Illustrator/Inkscape and each element answers for what it encodes.
3. **Verification is a GIF, never a PNG** -- a single frame cannot tell still
   from animated. An instrument, not a deliverable: GIFs do not enter the repo.
4. **Each icon declares the passage that justifies it** (`ancla`, pinned by a
   test): the text is the organ that justifies the content that sustains the form.
5. **thi.ng is IN USE, not noted**: `hiccup` + `hiccup-svg` + `color` in
   `docs/cultura/lib/compilador.js`, the browser twin, verified headless; the
   geometry is EXPORTED from the Python vocabulary, never ported by hand.
   **`CAPACIDADES.md` section 6 is the index to read BEFORE writing a generator,
   a pipeline or a graph from scratch** (`tests/test_thing_registro.py` keeps it
   honest). Next candidates: `graph`, `transducers`, `validate`.

Four defects the CI matrix caught that a green local Windows run did not: a
backend that EXISTS and does not rasterize counts as absent (probed per binary);
vendorized `*.README.md` are THIRD-PARTY, in a declared `ZONA_AJENA`; the doc
ratchet reads `git ls-files`, so **an uncommitted `.md` is invisible to it**;
and **rasterizing is not animating** -- cairosvg runs no CSS, so ubuntu got 16
identical frames and the guard read that tie as "the file lies". Movement now
demands a backend PROVED to animate (never an ambiguous 1), and `--no-sandbox`
is Linux-only: on Windows it returns a blank PNG.

## What a real model did to a boundary a mock never touched (2026-07-30)

The `iconos` mode had only been exercised with a FAKE model -- one that returns
exactly the types you expect. The first run against a real one (gpt-4.1-mini via
GitHub Models; NOT the Azure account SOL drained) found two things in the first
attempt. Detail and numbers: `docs/cultura/MOTOR_SEMANTICO.md`.

1. **The boundary with a model is validated by TYPE before value.** It returned
   `composicion` as a dict; that raises `TypeError`, and the mode only catches
   `ValueError` -- so it was not a rejection with its reason, it was the mode
   falling over. Fixed, with a wrong-typed value REJECTED instead of silently
   defaulting.
2. **A closed vocabulary stops invented words; it does not fix the SHAPE.**
   Vocabulary alone -> 1 of 3 briefs reached an SVG, with up to three repair
   rounds. Vocabulary + ONE complete example spec -> **3 of 3 on the first
   round**. The example is `esquema.EJEMPLO` and a test demands it stay.

**A measurement that was WRONG, corrected everywhere:** "one of the sixteen
icons is nearly static" was a defect of the INSTRUMENT (the animation advance
was injected after `infinite`, killing a `... infinite alternate` rule). All
sixteen give 10/10 distinct frames, and the guard is coherence, not a threshold:
an icon that declares `@keyframes` must move within ITS OWN cycle.

**Still NOT closed, named so nobody finds it by surprise:** the full `iconos.py`
-- resource guard, saved piece, job -- has never run in its place on the box.
What was measured is the same prompt and the same compiler, from Windows.

## iskvw: the substrate is consumed, and MAK's essays reach it (2026-07-30)

The portfolio had none of `PROYECCION.md`'s integrations wired. Three cuts, all
verified running; detail in `iskvw/MAPA.md` and `iskvw/ESQUEMA_ARCHIVO.md`:

1. **An essay enters the archive through the same contract**
   (`contrato_archivo.desde_ensayo` + `--fuente ensayos`): 1 essay + 16 concepts
   + 16 icons = 33 pieces, 32 links; `--fuente todo` gives 41 and 50. Links are
   `manual` and never `semantico`, an icon absent from disk produces NO piece,
   and `declara_animacion` is READ from the file.
2. **The skin asks for the substrate**: `archivo.json` first, degrading exactly
   as before. It is not versioned, so the fallback IS today's live path.
3. **A session is a reproducible seed** (`#semilla=&centro=&escala=`), pinned by
   a test that runs the PUBLISHED file's own functions in node.

**The links are DRAWN: always, faint, by weight** (his call). They go underneath
the works, a link needs BOTH ends in frame, and the neighbours are indexed once
-- the every-pair-every-frame defect is pinned by a test. Measured: 207 to 615
segments per frame against the 23,871 pairs an all-against-all would cost. NOT
measured, so not claimed: frames per second on a phone.

**Still the user's, and he wants to DEBATE it first:** whether the essays get
published on iskvw.cl. The bridge is built and unused.

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
