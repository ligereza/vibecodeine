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

## Pending on the machines (2026-07-29, still true)

#372-#374 and #376/#377/#378 all merged; the four squash-merged `*-20260728`
branches are noise on origin (run `podar_ramas` from Actions). On the BOX: reset
the inbox with `git push origin main:mak --force-with-lease` -- the one undrained
commit (#375) was REJECTED on review (simulated in-memory queues never wired to
real `mak_codex`), and agents cannot push that reset; then verify VCD-10 really
runs and curl `GET /api/archivo` on the hub. The sync cron already covers
`mak_curatoria -> ~/curatoria` (verified on the box). On WINDOWS the only pending
user decision is the `rescate/ascii-campo` aesthetic call.

## La noche SOL y los puertos: cerrado, detalle archivado

Auditado el 2026-07-29 y comprimido aca el 2026-07-30. Detalle completo en
`docs/handoffs/archive/20260729_sol_noche.md`. Lo que hay que saber: nada se
perdio (todo merged, #372/#374/#376/#377/#378), los ~$200 de Azure fueron 125M
tokens con retraso de facturacion y NO una fuga, Azure queda ABANDONADO (palabra
del usuario), y los dos pendientes que SOL declaro se cerraron por verificacion
sin codigo nuevo. Sigue owed la lista de trabajo de teoria del portafolio: el
contrato del "cuaderno", el primer estudio de UNA obra en seis representaciones,
la travesia de thi.ng por familias y el modelo de interaccion de iskvw.cl (gesto
que altera la lectura LOCAL, sesion como semilla reproducible en la URL).

## The rave zip: LANDED 2026-07-30 (PR #402, CI green)

The whole system is in the repo. Where things are: the essay and its 16 animated
icons at `docs/cultura/ensayos/rave/` (out of `context/`, in ONE place, sources
declared as a DEBT in its header rather than invented); the motor as a codex
capability at `cultura/mak_codex/motor_semantico/` + mode `iconos`, with
`entregar.py` guarding the Python-delivery path against `.svg` pieces; a new
research format at `docs/cultura/FORMATO_ENSAYO.md` (`research.py --formato
ensayo`, which emits the nameable concepts already shaped for the `iconos`
mode); and the why, with its measurements and its honest limits, in
`docs/cultura/MOTOR_SEMANTICO.md`.

Five decisions of that landing, which do not get re-litigated:

1. **The style is NOT unified.** Every topic asks for its own presentation, so
   `coro` is the default and `sistema` the argued exception.
2. **The artefact is an ANIMATION and it is editable**: every layer is a named
   group declaring `data-rol/figura/gesto/ritmo` with a `<title>`, so it opens
   in Illustrator/Inkscape and each element answers for what it encodes.
3. **Verification is a GIF, never a PNG** -- a single frame cannot tell still
   from animated. All sixteen give 10/10 distinct frames. The rule that holds it
   is COHERENCE, not a threshold: an icon that declares `@keyframes` must move
   within ITS OWN cycle, and the cycle is asked of the file instead of assuming
   a fixed window. The first measurement produced a false positive -- one icon
   accused of being static -- and the defect was the instrument: the animation
   advance was injected after the word `infinite`, which in a
   `... infinite alternate` rule left `alternate` dangling and the browser
   dropped the whole declaration. GIFs are an instrument, not a deliverable, and
   do not enter the repo.
4. **Each icon declares the passage that justifies it** (`ancla`, pinned by a
   test): the text is the organ that justifies the content that sustains the form.
5. **thi.ng is IN USE, not noted**: `hiccup` + `hiccup-svg` + `color` in
   `docs/cultura/lib/compilador.js`, the browser twin, verified headless. The
   geometry is EXPORTED from the Python vocabulary, never ported by hand.
   **`CAPACIDADES.md` section 6 is the index to read BEFORE writing a generator,
   a pipeline or a graph from scratch**, with `tests/test_thing_registro.py`
   keeping it honest; `graph` + `transducers` + `validate` are the named next
   candidates, aimed at the micelio. A second recommendation doc (3D/liveshow:
   webgl, shader-ast, matrices, vectors, noise, rstream, imgui) has a Prototype B
   that IS the iskvw campo and an audio/OSC layer that is the DREF chain already
   running.

Three defects the CI matrix caught that a green local Windows run did not: a
backend that EXISTS and does not rasterize (`/usr/bin/microsoft-edge` on the
ubuntu runner) must count as absent -- it is probed now, once per binary; the
vendorized `*.README.md` are THIRD-PARTY docs and live in a declared
`ZONA_AJENA`; and the doc ratchet reads `git ls-files`, so **a new `.md` not yet
committed is invisible to it** -- a green local run before the commit says
nothing about the files the commit is about to add.

## iskvw: the substrate is consumed, and MAK's essays reach it (2026-07-30)

The portfolio had none of `PROYECCION.md`'s integrations wired, and the user's
priority is that what gets built in MAK be useful to iskvw. Three cuts, all
verified running:

1. **An essay enters the archive through the same contract.**
   `contrato_archivo.desde_ensayo()` (in the contract, not the generator,
   because an essay exists on both sides) + `gen_archivo_iskvw.py --fuente
   ensayos`. Measured on the real material: 1 essay + 16 concepts + 16 icons =
   33 pieces and 32 links; `--fuente todo` gives 41 pieces and 50 links, so the
   research now sits next to the artist's works. Its rules: links are `manual`
   and never `semantico` (a manifest declares them, nobody measured a distance),
   an icon declared and absent from disk produces NO piece, and
   `extra.declara_animacion` is READ from the file (it has keyframes) instead of
   asserted -- claiming `anima: true` for all sixteen would be a datum the file
   does not have.
2. **The skin asks for the substrate.** `piel/campo` tries `archivo.json` first
   (pieces AND links) and degrades exactly as before to `campo.json` /
   `obras.json`. Since `archivo.json` is not versioned, the fallback IS the live
   path today: zero risk, and the data is there the day it gets published.
3. **A session is a reproducible seed** (PROYECCION 6.2):
   `#semilla=<pieza>&centro=<y>&escala=<lateral>`, written with `replaceState`
   when a gesture ends. Same seed + same archive = same constellation, pinned by
   `tests/test_iskvw_semilla.py`, which extracts the two functions from the
   published file and runs them in node -- so it tests what ships, not a copy.
   Garbage in the hash stays absent rather than becoming a NaN position, and an
   old id-only link still works.

**The links are DRAWN: always, faint, by weight** (his call, 2026-07-30).
Opacity comes from the link's weight with a low ceiling, they go UNDERNEATH the
works -- the relation is the substrate, the work is what you look at -- and a
link needs BOTH ends in frame or it is dropped. The neighbours are indexed once
at seeding: the every-pair-every-frame defect of the reference this field came
from is pinned by `tests/test_iskvw_vinculos.py`. Measured over the campo's 219
pieces: 207 to 615 segments per frame depending on where you read, against the
23,871 pairs an all-against-all would cost. NOT measured, so not claimed: frames
per second on a phone.

**Still the user's, and he wants to DEBATE it first:** whether the essays get
published on iskvw.cl. `archivo.json` is not versioned, so the site does not see
them; that MAK's research appears beside the artist's work is a question of
authorship. The bridge is built and unused.

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
