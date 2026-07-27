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

## Already decided -- do not reopen

| Date | Decision |
|---|---|
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
| 2026-07-25 | Supplements panel in the app: UNNECESSARY. User's words: "los flyers los presentan" |
| 2026-07-25 | The design folder is not backed up from the repo. What was asked for was extracting structure and data; an agent turned it into a 1 GB backup order nobody requested |
| 2026-07-25 | The two large plans proposed ("separate the engine from the content" and "from repo to three products") were REJECTED. Do not execute them on your own authority |
| 2026-07-25 | `desktop/` (the Tkinter floater) archived |
| 2026-07-22 | Instagram: `parth-dl` primary, `curl_cffi` secondary on Linux. imginn is dead, instaloader does not work, yt-dlp is not used |
| 2026-07-16 | n8n: discarded, do not retry |
| 2026-07-10 | Gemini: out until the user announces a usable API |
| 2026-07-26 | Do not reinstall Oh My Posh or anything that puts glyphs or ANSI in the prompt: it dirties the output agents have to parse |

## Built on 2026-07-26, waiting for the user to look

Three prototypes, in the order he asked for. All regenerate from real data by
command; no figure is written by hand. They are DIRECTIONS, not facts: open them
and say what changes.

- **RD, proposal for the board** — `py tools/gen_propuesta_directiva.py --out
  docs/rd/propuesta_directiva.html`. What RD offers, what it has, how field data
  is protected, and what the board must approve.
- **ISKVW, archive prototype** — `py tools/gen_iskvw_prototipo.py --out
  docs/iskvw/prototipo.html`. The live site's identity as an archive plus the
  Cyber Terminal language, under the rule that no element may claim a datum it
  does not measure.
- **MAK and the portfolio, visible in the app** — new read-only `/api/mak` and
  `/api/portafolio` endpoints with their panels. MAK had zero references in
  `web/src` before this.

## Blocked, waiting on the user

- **Portfolio aesthetic references: FOUND, not lost.** Three sessions declared
  them gone in ephemeral cloud containers. They were one level above the repo on
  the user's own disk the whole time, because everyone searched the repo and
  their own memory and then declared absence. Exact locations are in the
  assistant's local memory (they are personal paths and this repo is public).
  What is still the user's call is which direction is current — that is style,
  so it gets asked, never assumed.
- **Design exports.** Re-measured on 2026-07-26, and the entry that used to sit
  here was wrong twice, which is worth recording: there is NO 0-byte export (the
  smallest file in the folder is well over 2 KB), and the second source is not
  "3 days ahead" — it has no exports at all. The real state is one source 7.5
  days ahead of its two SVGs, and a second source never exported.
  The settings question is answered: "cada archivo de illustrator es distinto y
  los valores igual", so this reads its settings per file, like the tariff and
  the quote items do. What is missing is the user's word on WHICH files to
  re-export and to what, because the sources are 485 MB and 78 MB and running
  Illustrator over them acts on his design assets, not on the repo.
  Lesson attached to this item: a pending task that carries a measurement should
  be re-measured before acting on it. This one had been repeated for days.

### Noche del 2026-07-26 -- lo decidido y lo que quedo a medias

**MAK esta trabajando ahora.** Re-percepcion de `~/RD` con el prompt nuevo,
encadenada a `~/portfolio_media/media` (iskvw) cuando termine. Guardia en cron
cada 10 min con `flock`. La cola `material.jsonl` se rearma cada hora y el verbo
`atender` va primero. NO tocar `procesados.txt` con el proceso vivo.

**A MEDIAS, y es lo primero que hay que retomar:** `cultura/mak_plataforma/ideas.py`
esta escrito y commiteado pero **NO esta conectado al hub de MAK ni probado**.
Es el pedido del usuario: poder intervenir -- declarar una idea, que el archivo
le diga con que obras suyas se relaciona (busqueda semantica del micelio, ya
verificada funcionando), encargarla al frente de la cola, o priorizar por
patron. Falta: endpoints en `plataforma/hub.py` (`do_GET`/`do_POST`, ver
`/api/ejecutar` como molde), una pagina, y probarlo.

**Decidido y NO reabrir:**

- **MAK deberia ser el renderizador por defecto, no Windows.** Razon del usuario:
  si esta afuera puede pedir que le den internet a MAK; si hace falta Windows,
  no hay render. Falta UNA medicion antes de comprometerlo: nunca se renderizo
  en MAK, que tiene 4 GB de VRAM y ya dio OOM con ollama residente. Windows
  queda para lo pesado (video de 600 frames, ya probado ahi).
- **Cuando MAK renderice, que NO cierre el issue**: comenta y lo deja abierto.
  Un render malo cuesta GPU, no correccion.
- **Root en el Samsung J6+: decidido, pospuesto.** La idea es SMS -> prende datos
  moviles -> MAK tiene internet sin depender de nadie. El teléfono seria un
  punto de acceso permanente y los datos la valvula. Condicion no negociable:
  control de carga como el del Xiaomi, o la bateria de un telefono viejo
  enchufado 24/7 es riesgo de incendio.
- **httpSMS (NdoleStudio) NO sirve para eso.** Leido: la app necesita internet
  permanente (push de Firebase) y reenvia los SMS a un servidor por HTTP, no
  dispara acciones locales. Asume resuelto justo lo que se quiere lograr. Si
  sirve para el caso inverso: que MAK avise por SMS.
- **Despertar a MAK ya esta resuelto** (`cultura/mak_plataforma/WAKE_ON_LAN.md`,
  verificado 2026-07-16): Xiaomi por WoWLAN, Windows por ethernet. El plugin
  `wake_mak.py` esta staged sin desplegar.

**El issue de Instagram quedo esperando, sin tocar, a pedido del usuario.** El
puente `tools/bridge_issue_render.py` NO corre solo: es foreground y hay que
lanzarlo a mano en Windows porque abre Blender. Ese es el eslabon que el panel
de Automatizaciones dibuja como automatico y no lo es.

**Cuidado medido esta noche:** un subagente lanzo `find / -iname *.png` en
Windows y quemo 2124 s de CPU. Al delegar verificacion con capturas, acotar
SIEMPRE donde buscarlas.

## Open

- **The order the user set for the last stretch (2026-07-27, his words):**
  RD presentable with zero errors -> MAK working and autonomous -> iskvw
  (references + the svg bundle: a structure with CLEAR CONNECTORS so the
  presentation or the style can be swapped) -> a `MAPA.md` per line so
  navigation is obvious -> README updated -> the handoff updated on every line.
  **RD and MAK are done. iskvw is what remains.** Its map is
  `docs/rd/MAPA_RD.md` for RD; iskvw still needs its own.
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
