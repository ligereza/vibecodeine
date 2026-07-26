# SINGLE CHECKPOINT -- repo state

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
| 2026-07-26 | **The floor-plan symbol catalogue is open.** Acceptance criterion, verbatim: "can the events manager add an icon? if not, it is not configurable". She now drops an `.svg` into `data/plano_simbolos/` and declares it in `data/plano_simbolos.json` (that file carries the instructions, in Spanish, because she is the one reading it). No code, no TypeScript. The catalogue ADDS to the 17 built-ins and can also relabel or recolour one of them. A symbol may declare `cuando` (siempre / testeo / jornada_larga / masivo / manual) and a zone. Two real defects fixed on the way: a key absent from `_ZONAS_ICONOS` used to be dropped from the plan SILENTLY, and the zone list was about to become a second copy — it now derives from `engine._ZONAS_ICONOS`. Anything wrong in the file warns on stderr and the rest of the plan still renders. `data/plano_simbolos/_ejemplo_hidratacion.svg` is a sample to copy and is deliberately NOT declared: it is not a real RD symbol |
| 2026-07-26 | Placeholder phone numbers: gone. The only remaining match in the repo is the comment recording the incident |
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

## Open

- **The floor-plan symbol catalogue reaches the Python plan, not the web
  editor.** Measured live on 2026-07-26 against a running hub: a symbol added to
  `data/plano_simbolos.json` renders in `flujo plano`, but `PlanoTool.tsx` keeps
  its own `SYMBOL_CATALOG`, whose entries name icons from a component library
  rather than SVG files, so a designer's `.svg` has no place in it yet. Closing
  the gap means teaching that component to draw raw markup for custom keys, and
  it is the piece that produces the printed A4 a venue receives, so it is worth
  doing carefully rather than quickly. The instructions the events manager reads
  now say this outright: a symbol that does not show up in the editor is not
  broken, it just does not reach there yet.


- **The `mak` inbox has no defined drain, and that is the one thing that would
  turn it back into a line.** MAK opens a PR into `mak` every 6 hours; nothing
  moves `mak` into `main`. Verified working on 2026-07-26: the box fetches all
  branches before checking out, so delivery against the inbox does run. What is
  missing is the exit — today that is a human-curated PR, same as any
  line -> main promotion. If the inbox ever holds work `main` has not seen for
  long, the topology has quietly broken and needs fixing, not tolerating.
- Two design exports lag behind their source. That is re-exporting, not backing up.
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
