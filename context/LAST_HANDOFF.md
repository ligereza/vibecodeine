# SINGLE CHECKPOINT -- repo state

## READ YOUR MEMORY FIRST. Before anything else. Now.

If you are an incoming agent -- new session, or the same one after a compaction
-- **stop and read the assistant's local memory before you touch anything.**

This is not a suggestion and it is not optional. On 2026-07-27 the user had to
order it THREE TIMES in one session, and every time the answer he needed was
already written down. Each time, the agent had a compaction summary and believed
it was enough. It was not.

What that costs, measured that same night: an agent "discovered"
`_master_contraportadas.json` and its generator as if they were findings, hours
after the same session had built them. It reported a stale ten-minute state as a
defect. It asserted a cause it had invented. It asked the user two questions he
had already answered.

**How to actually read it** -- two mechanisms make a memory search come back
empty while the answer sits there, and both were hit on 2026-07-26:

1. `.remember/` is INVISIBLE to the Grep tool. That folder has a `.gitignore`
   containing `*`, ripgrep honours it, and says nothing. Search it from
   PowerShell with `Select-String -Path "<repo>\.remember\*"`, which does not
   honour gitignore. **Never conclude "it does not exist" from a Grep over paths
   that might be ignored.**
2. Older memories are written in English while the conversation runs in Spanish.
   `curatoria` is filed as `curation`. Search both languages, or the shared stem.

Read `.remember/now.md` and today's `.remember/today-*.md` IN FULL, not by
grepping for a word. Grepping is how you miss what you did not know to look for.
The full transcript of a compacted session is also on disk; extract the relevant
stretches with a script -- never open 25 MB whole.

Then read this file, `CLAUDE.md` and `MAPA.md`. Then work.

---

This is the ONLY state file. There used to be seven competing ones (LAST_HANDOFF,
SESSION_STATE, PLAN_SIGUIENTE_AGENTE, PLAN_SEMANAL_OPUS, ORQUESTACION_SUCESOR,
WALKTHROUGH, failed-handoff), which is why every agent rebuilt the state from
scratch and asked the user things he had already answered. They were merged here
on 2026-07-26. The old ones live on in git history and in docs/handoffs/archive/.

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
- **Big steps, not baby steps.** Do not commit and wait for CI every two changes;
  the user asked for this explicitly.
- The repo is a USB stick. The conversation is the center, not the repo.
- Measuring exists to answer something that was asked. Measuring beyond that is
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

Working and verified live: the DREF show chain (LTC -> Chataigne -> OSC -> phone
-> PWA panel), the RD database with normalized events, the hub split into 3
profiles, and the documentation ratchets (`test_mapa_completo`,
`test_higiene_docs`).

## Security diagnosis status (2026-07-28)

Eight of ten findings are closed. VCD-06 now caps request bodies at 8 MB in the
two previously uncapped `src/flujo` handlers (`serve/server.py`, `web/hub.py`)
and returns 413 on excess; the three `cultura/` handlers were already capped.
VCD-07 remains partial: pin Actions to SHAs and add Dependabot. VCD-10 was
assigned to MAK but has not been verified running.

## 2026-07-28: Fable handoff recovered

The final session left two PRs. VCD-06 gained direct 413 regressions and merged
as #372 with five green checks. `PROYECCION.md` is a requested compass, not
backlog; #373 was rebased after #372 and still requires green CI.

Branch `mejoras-operativas-20260728` stops MAK checkpointing failed perceptions
as successes, retries them, quarantines unchanged files after three failures,
and repairs the legacy checkpoint from the latest JSONL row. Live measurement:
49/5,463 attempts contain errors. It also aligns the Windows verifier with the
already-live `mak_curatoria -> ~/curatoria` mirror and unifies Windows launchers.
Merge through the gate; do not copy to MAK manually.

## Stash triage (2026-07-28)

- `stash@{0}` is valuable ASCII-skin work, preserved on
  `origin/rescate/ascii-campo`; do not merge without the user's aesthetic call.
- `stash@{1}` is redundant with main.
- `stash@{2}` is ambiguous and includes rejected documents; do not apply whole.

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
| 2026-07-27 | **The phone risk is CLOSED, and it was the project's open one.** "Fluidez en un telefono de gama media con 697 nodos" had never been measured. Measured now, in a real browser with the phone viewport (390x844), density 3 -- which is 1.3 million canvas pixels, what a phone actually draws -- and CPU throttled through CDP, while dispatching a continuous gesture: CPU x1 60.4 fps / worst frame 17.6 ms, **CPU x4 (mid-range) 59.9 fps / 33.2 ms**, CPU x6 (low-end) 49.1 fps / 50.1 ms. So mid-range holds 60 with an occasional dropped frame and low-end is noticeably slower but usable. Two traps found while measuring: the first throttled pass read 1.1 fps at EVERY rate including x1, which was the measurement and not the page -- the skin cancels its rAF on `document.hidden` (correct of it) and a reload left the tab in the background, so `bringToFront()` is required; and density matters more than CPU here, because it multiplies canvas pixels by 9. What this does NOT cover: a real phone's GPU and memory bandwidth |
| 2026-07-27 | **A loop advances verifiable work; it does not author documents.** `iskvw/DIRECCION.md` and `iskvw/MAPA.md` were written by agents on a 5-minute loop while the user was away, he rejected them outright, and they were deleted UNREAD so their framing would not leak into the replacement (PR #342). Anyone auditing branches will find them missing from main and be tempted to "recover" them: do not. They were rejected, not lost. What the loop is for is code, tests, measurements and merges -- things CI can judge. `iskvw/MAPA.md` is still owed and it gets written WITH the user, from the conversation, because a map is what/style and that is his call |
| 2026-07-27 | **The curation criterion is CONFIGURATION, never a gate waiting on someone.** The system swallows whatever arrives: `data/iskvw_campo_filtro.json` ships entering EVERYTHING, adding a hundred works is running the generator again, and a missing or broken file enters everything and says so on stderr. It is the same lesson already written here for the RD tariff, the floor-plan symbols and the piece kinds. The filter runs BEFORE the projection, because t-SNE places each work relative to the others and dropping works afterwards would leave the rest positioned by neighbours that are gone. Verified: default 697 works / 0 out / 48.9% neighbourhood, restricted to obra+tatuaje 378 works / 319 out / 46.5% recomputed |
| 2026-07-27 | **The perception classifies at the SOURCE, with a closed vocabulary.** Measured on 937 ig fichas: `vision.tipo_obra` had 20 distinct values, `tatuaje`(42) and `tattoo`(16) were the same type split in half, and `categoria` said 354 works where `tipo_obra` said 503 -- two fields answering one question and drifting. Worse, the new ig prompt had stopped asking for a type at all, so the archive came out with NO classification, and that is what made an agent ask the user to hand-classify 697 works. `TIPOS_OBRA_VALIDOS` invents no name: they are the ones MAK already wrote, collapsed. Anything outside the vocabulary empties instead of becoming a value someone discovers later by counting |
| 2026-07-27 | **What the people who use this get is a FILE, never a console.** Two self-contained HTMLs, no install, no server, no internet: `plano_rd.html` for the events manager and `herramientas_rd.html` for the rest. Verified by opening them in a browser -- zero console errors across every tab. Regenerated with `py tools/gen_rd_standalone.py` + `npm run build:rd` + `npm run build:plano`. If a feature answers "open the app with py -m flujo app", that feature is broken for its actual user |
| 2026-07-27 | **Her layout travels as a preset.** She builds the plan, exports the SVG and the rider PDF, and saves a `.json` that carries the elements, the event, the pack and the symbols she created. It goes to the director, gets associated with the database, comes back. Adding a symbol and tracing an image both work offline: the browser tracer is the same algorithm as the Python one, verified byte-for-byte on identical pixels |
| 2026-07-27 | **An export, not a cut-down branch.** The user asked for an RD line without his own material. A branch that deletes files becomes a SUBSET, and a subset cannot merge back -- that is exactly why `mejoras` was retired. So `rd` stays a full line and what the RD people receive is a generated bundle: it INCLUDES what it names instead of deleting what does not belong. Deleting always forgets something; including cannot |
| 2026-07-27 | **A branch does not hide history.** Anyone cloning `rd` gets every commit, including everything personal. The board therefore receives a file, never a repository. If a separate repo is ever needed it has to be a fresh one, not a branch |
| 2026-07-27 | **MAK attends the flyer issues on its own, and it is proven.** Issue #328 arrived by mail, and the box took it from cron, paused the perception, rendered on its GPU, uploaded to Drive, commented and closed -- with nobody launching anything. Then #330 did the same honouring `img_index=2`, and the delivered flyer was the second slide, verified by eye. The bridge is `cultura/mak_plataforma/puente_issues.py`, cron `MAK-PUENTE-ISSUES` every 10 minutes. It PAUSES the perception instead of waiting for it: a corpus takes hours and a request from the user should not queue behind background work. It never opens issues, never publishes disk paths, and closes an issue only when nothing is pending |
| 2026-07-27 | **What MAK cannot do stays visible instead of failing.** Video goes to Windows by the user's decision (the 600-frame render stays there). A post whose embed returns Instagram's own error page says so. Shadowbanned profiles land in the same bucket. All of it appears in the render department of MAK's face, with the reason, above what was delivered |
| 2026-07-27 | **Instagram blocks the TLS fingerprint, not the User-Agent.** parth-dl gets a login wall from the box before it can read any metadata, so the chain is parth-dl (from Windows, honours the carousel index) -> the public embed with Chrome impersonation (what reaches from Linux) -> the mirror. The embed's `contextJSON` carries the whole carousel, which is how `img_index` is honoured: get the list, pick one, download only that |
| 2026-07-27 | **The fast GPU backend is not the same on every machine.** Measured on the same scene: the box's GTX 1650 does 300s on CUDA against 459s on OptiX, because it is the only Turing card without RT cores. The laptop's RTX 4070 is the opposite. `FLUJO_GPU_BACKEND` overrides per machine; MAK's render cron sets CUDA. Do not make either one the global default |
| 2026-07-27 | **The face is not the cost, the algorithm is.** MAK's browser pinned one of eight cores at 97% with nobody watching. Giving VRAM to a browser would take it from the 4 GB the model and the renders fight over, so the answer was not GPU acceleration: the map's physics compared every node against every other one sixty times a second. The map now converges, caches its layout, and draws a single frame for pan/zoom/hover. User's correction, kept verbatim: "organismo vivo" means it answers instantly, not that it spins |
| 2026-07-27 | **The printed supplement pieces are the two-sided PDFs; the repo SVGs are the regenerable contraportada of the SAME content.** Compared word by word on CREATINA: identical except line breaking and one copy variant ("En 60 gomitas" vs "En gomitas - 60 gomitas"). The user's decision: leave it as it is. The live pipeline is `_master_contraportadas.json` + `gen_contraportadas.py`; three generators writing into folders deleted weeks ago were archived |
| 2026-07-27 | **Piece kinds are configuration, not code.** They were a closed TypeScript union plus seven chained ternaries, so adding "pendon" meant recompiling. Now `data/piezas_tipos.json`, served by `/api/piezas-tipos`. Today flyers and back covers; tomorrow banners or labels |
| 2026-07-27 | **The triangulation queue was asking wrong things and asking them twice.** The user read a task and caught it: "what producer organised the event of 23:00 HRS with LIVE JAM". A time went in as a date, a tagline went in as a line-up, and OCR variants of a venue produced twin questions. 92 questions -> 52 against the real fichas. An event is now its date plus its headliner; the venue is out of the dedup key because it is the field OCR reads differently every time |
| 2026-07-26 | **RD splits into three areas: eventos, suplementos, and general posts.** For SUPPLEMENTS, the text on flyers and labels ALWAYS comes from a file an RD manager sends, and that file wins over research, over the database, over anything an agent produced. Never invent product names, never look up properties, never invent descriptions. Research is legitimate when the user orders it (e.g. researching a post) — the rule is only that a file, when it exists, overrides it. The link to reduciendodano.cl and the QR stay constant on every flyer |
| 2026-07-26 | **Three working modes**: *modo calma* (answer, execute nothing), *modo repo* (branches/PRs/CI; exits at 0 open PRs, 0 open issues and only the named branches), *modo local* (this machine: config, memory, understanding). Ask which one is active when it is not obvious |
| 2026-07-26 | **The two portfolio directions on disk are REFERENCES, not competing options**: the live six-section archive and the Cyber Terminal prototype. Both feed the design; neither is "the choice" |
| 2026-07-26 | **Language split**: Spanish to talk, English for everything inside the repo, correct Spanish with diacritics for anything a human reads as a product |
| 2026-07-26 | **The portfolio is `iskvw`**: the automated line and the ONLY site. This repo stays PUBLIC. The separate `portfolio-auto` repo is discarded -- it existed because one agent advised making this repo private and the next one patched that by creating a second repo for the site. Both moves were wrong |
| 2026-07-26 | **No agent opens issues.** The user and his Google Script do: issues are the Gmail -> issue -> render channel, not a task board. Commenting, labelling and closing is fine; opening is not. Verified: nothing in the repo creates them |
| 2026-07-26 | MAK delivers against the `mak` inbox, not the retired `mejoras` line. If that branch ever stops draining into main, it has become a line and must be fixed |
| 2026-07-26 | Agent worktrees under `.claude/worktrees/` are pruned when the task ends. There were 7 abandoned ones, each a full copy of the repo: they multiplied every handoff, checkpoint and doctrine file by 8, so any search returned hundreds of hits with no way to tell which one ruled |
| 2026-07-26 | MAK's doctrine (`CAPATAZ.md`, `DOCTRINA_CLAUDE.md`) lives in `cultura/mak_plataforma/doctrina/`. It was written for the box's local model, and the Claudes kept reading it as their own |
| 2026-07-26 | Two useless crons removed: the 30-minute sweep in `issue_descarga_ig` (it re-commented on open issues, GitHub emailed each comment, and the Gmail script turned every email back into an issue) and the weekly `portfolio` job (it published to the discarded repo) |
| 2026-07-26 | **Every money value is configurable, none is fixed.** The user's answer when asked whose the quote figures were: "esos valores son configurables cierto? cada archivo de illustrator es distinto y los valores igual". So the question was never "are these the right numbers" but "why are they frozen". Three editable files now, all tracked and all with a loud fallback: `data/rd_packs.json` (field-service tariff, read by the rider, the Python quote and the app), `data/cotizacion_servicios.json` (the quote tool's line items and presets — design and printing, which change per job) and `data/plano_simbolos.json`. No figure was altered: they were moved out of the code as they stood. The same rule governs the pending Illustrator re-exports — settings per file, not one global setting |
| 2026-07-26 | **A symbol added by the events manager reaches BOTH the printed plan and the editor.** It was a two-step day: first the catalogue only fed `flujo plano`, because `PlanoTool.tsx` kept its own list of icons named after a component library, where a designer's `.svg` had no slot. Then the component learnt to draw raw markup for a custom key, on the same 160x160 convention Python already used, and the palette shows each one with its OWN drawing so several are told apart. If she has no SVG, an image is traced and shown before saving. Nothing here is guessed: it was verified in a browser, from an empty catalogue to a symbol drawn on the plan |
| 2026-07-26 | **The floor-plan symbol catalogue is open.** Acceptance criterion, verbatim: "can the events manager add an icon? if not, it is not configurable". She now drops an `.svg` into `data/plano_simbolos/` and declares it in `data/plano_simbolos.json` (that file carries the instructions, in Spanish, because she is the one reading it). No code, no TypeScript. The catalogue ADDS to the 17 built-ins and can also relabel or recolour one of them. A symbol may declare `cuando` (siempre / testeo / jornada_larga / masivo / manual) and a zone. Two real defects fixed on the way: a key absent from `_ZONAS_ICONOS` used to be dropped from the plan SILENTLY, and the zone list was about to become a second copy — it now derives from `engine._ZONAS_ICONOS`. Anything wrong in the file warns on stderr and the rest of the plan still renders. `data/plano_simbolos/_ejemplo_hidratacion.svg` is a sample to copy and is deliberately NOT declared: it is not a real RD symbol |
| 2026-07-26 | Placeholder phone numbers: gone. The only remaining match in the repo is the comment recording the incident |
| 2026-07-26 | **MAK works on the user's material, not on its own output.** It ran at 8% of its daily quota writing cultural genealogies while 57 GB of his material sat untouched. Root cause: ONE prompt for two different jobs, and it never asked for headliners -- half of his own formula ("headliner + fecha = productora encontrable"). Splitting the prompt was not enough: the ficha builder had the old schema hardcoded and silently dropped every new field. Now a verb `atender` goes FIRST and consumes a queue built from what was perceived. **The autonomous mode was NOT removed** -- he designed it for when there is no new material or no internet; it is a fallback again instead of the default. Mirrored in `cultura/mak_*`, PR #316 |
| 2026-07-26 | **MAK's own reports are acted on, not just filed.** It had written "mitigar la degradacion de groq" and nobody executed it: groq led the provider order with 40% measured success while cerebras (91.4%) came third. Reordered by measurement. The pattern to watch: the box can diagnose itself and cannot act on itself |
| 2026-07-26 | **Brand is information, never a restriction.** User's words: "como info sirve, como limitante o restriccion no -- un dia puedo hacer un post con otra estetica o cuando toque cambio de flyers la app no debe restringir". So the palette is a DEFAULT any caller, event or config may override, and nothing validates a piece against it. Removed: the `flujo brand` CLI group (it only printed that it had been retired), the dead `export_tokens` bridge, and a block in `render/piezas.py` that printed "flujo aplicado automaticamente" while applying nothing inside a silent `try/except`. The quote engine's palette now resolves caller > event `estilo` block > default palette, and the document sent to a productora no longer carries hex codes or the words "usa flujo para consistencia de marca". `flujo.brand` STAYS as the palette reader -- deleting it is exactly how it broke before |
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
- **Design exports.** The entry that used to sit here was wrong twice, which is
  the lesson: a pending task carrying a measurement gets re-measured before
  anyone acts on it. Real state: one source 7.5 days ahead of its two SVGs, a
  second source never exported, and no 0-byte file anywhere. Settings are per
  file, answered ("cada archivo de illustrator es distinto y los valores igual").
  Missing is only his word on WHICH files to re-export, because the sources are
  485 MB and 78 MB and running Illustrator over them acts on his design assets.

## Las cuatro capas: no confundirlas (2026-07-27)

El mismo material vive en cuatro lugares con roles distintos, y mezclarlos ya
costo sesiones enteras. Tabla completa y las dos formas de romperlo en
`docs/handoffs/archive/20260727_capas.md`. El resumen:

| el dato | va a |
|---|---|
| como funciona algo, por que se decidio, que se midio | el **REPO** (este archivo, CLAUDE.md, el codigo) |
| donde esta un archivo en el disco, una IP, una MAC, un nombre de usuario | la **MEMORIA LOCAL** del asistente |
| material pesado y herramientas con licencia | la **CARPETA LOCAL**, que NO se respalda desde el repo |
| lo que la percepcion vio | **MAK**, y entra al repo por PR |

Se rompe en las dos direcciones: un dato personal en el repo queda publicado
para siempre (paso: MAC, BSSID de vecinos y el usuario de Windows -- VCD-08), y
una decision guardada solo en la memoria local se pierde al cambiar de maquina
(paso: las referencias del portafolio, dadas por perdidas tres veces).

### Still open from 2026-07-26

Detalle en `docs/handoffs/archive/20260726_pendientes.md`: `ideas.py` (CONECTADO
y probado el 2026-07-27, el checkpoint decia lo contrario), MAK como renderizador
por defecto (falta UNA medicion), root en el Samsung J6+ (decidido, pospuesto),
y `tools/bridge_issue_render.py`, que NO corre solo aunque el panel lo dibuje
como automatico.

**Measured care when delegating:** a subagent ran `find / -iname *.png` on
Windows and burnt 2124 s of CPU. When delegating verification with screenshots,
ALWAYS bound where to look for them.

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
- **The thi.ng libraries are IN, vendorized, and one of my claims about them was
  false.** `data/iskvw_librerias.json` declares them and
  `py tools/vendorizar_iskvw.py` bundles each as a self-contained ESM module in
  `iskvw/piel/lib/` plus its README alongside -- the skin is static, so no CDN and
  no build at deploy, and the minified bundle does not say how anything is called.
  Adding one is an entry in that file and the command. In today, 21.6 KB total:
  `tsne`, `geom-trace-bitmap` (the tracer), `rstream-gestures` (the diaphragm
  gesture WITH multi-touch, the phone, the risk never measured), `distance-transform`.
  **The correction: `@thi.ng/tsne` does NOT replace scikit-learn.** I wrote that it
  would let the box project on its own. Measured by running it: `DEFAULT_OPTS` has
  no output-dimension option and `init` does `this.dim = datos[0].length`, so 3D in
  gives 3D out, 6 gives 6, 12 gives 12. It cannot take 768 down to 2. It converges
  (the cost drops) and it is useful on already-low-dimensional data, and
  `gen_campo_iskvw.py` still needs sklearn. `tests/test_iskvw_librerias.py` pins
  this: if the library ever gains the option, that test fails and the conclusion
  gets redone. What does NOT serve: the sci-fi reference's `node-network`
  compares every pair every frame at `nodeCount || 80` -- the same defect this
  repo already measured and fixed in MAK's micelio. Its `objParser.ts`, which
  normalises any geometry into one scene, IS the answer to how 2D and 3D coexist.
- **DONE 2026-07-27: the archive is ONE file.** Position is now an optional field
  of the contract, so `archivo.json` carries relations AND positions: 1004 pieces,
  3188 links, 697 with position, measured against the box. It was 0 before,
  because the micelio ids carried the file extension and the field's did not, so
  the keys never met. Generators stay separate on purpose -- projecting needs the
  768-dimension vectors and the contract neither has nor wants them. Loose thread
  noticed, not chased: the contract counts 705 obras and the field 697.
- **iskvw, what it is actually asking for.** Not a style: the SUBSTRATE. Today
  the data/contract/skin split exists only for iskvw, and MAK's micelio has its
  own nodes and its own drawing -- the same work done twice, and a new skin
  serves only one of them. What is missing is the layer in between: a contract
  of PIECES and RELATIONS that does not know whether the works are the artist's
  or MAK's reports. A skin asks for "the nodes and their links" and always gets
  the same shape. Then the terminal skin can show the micelio untouched, an
  external agent can produce a new aesthetic from ONE document, and when the
  curation adds concepts and technique per work the old skins keep working --
  a field you do not know is a field you ignore. MAK does not build this: it
  FEEDS it, from the archive perception that starts on its own when RD ends.
  The rule it inherits is the doublecup thesis, already applied all session:
  **no element may claim a datum it does not encode.**
- **MAK is re-perceiving and nobody should touch it.** 1239 files at 05:00 on
  2026-07-27, eight hours in; it chains into the artist's archive on its own.
  Six traps cost real time and are in the assistant's
  memory: a process launched over SSH does not survive the session, `pgrep`
  alone let two perceptions run on a 4 GB GPU -- which is exactly what killed
  the July run -- `procesados.txt` must not be touched while the job holds it, a
  running process still has the OLD code loaded after a patch, nested heredocs
  over SSH break, and **copying a file to the box does not restart the service
  that already loaded it**.
- **When it finishes, read what it produced before giving it more work.**
- **The last hop to the RD database is still missing, and the tool for it
  already exists.** `cultura/mak_plataforma/mineria_rd.py` was never executed:
  it walks the material and writes DRAFTS in the real schema of
  `data/productoras/*.json`, into a separate folder, to enter by human-reviewed
  PR. Do NOT run it as it stands -- it would re-OCR the same files the
  perception is already processing and fight for the same GPU. What is worth
  taking is its OUTPUT side: wire the draft writer to the fichas the perception
  already produces. The user's constraint: the database in the repo is fine, so
  the extraction must be clean, must not create duplicates, and must not
  generate garbage on top of what is already right.
- **Logos are missing** and live in the user's `Documents\logos` (absolute path
  in the assistant's memory, not here: this repo is public).

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
