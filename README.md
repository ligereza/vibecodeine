<p align="center">
  <a href="https://github.com/ligereza/vibecodeine/">
    <img src="arte-ascii-readme.svg" alt="CODE.IN" width="936">
  </a>
</p>

<!--

The visible README is the artwork above (`arte-ascii-readme.svg`, the animated
codeine cup). Its artwork shell is preserved, while its text layer is refreshed
from this README with `py tools/update_readme_svg.py`. This keeps the piece
recognizable without letting the public cover lie about the current system.

# VIBECODEINE — operational workspace. Main program: FLUJO

`vibecodeine` is the repository, `flujo` is the program, `Dimensiones del Orden`
is the system. Local-first workspace for requests, jobs, briefs, design work,
the RD (NGO) line, the iskvw line (shows, art-research, portfolio), the
on-device Xiaomi controller (`xio`), the web hub, and agent-delivered patches.

The repo assistant is named `Faro`. The mission is to spend the strong model
now to build a base that free/cheap agents can maintain later, off-PC and
without a Claude account — success is measured by how little the repo needs the
strong model once it is gone.

## Where the real documentation lives

This file deliberately does NOT duplicate it. Four documents used to compete for
"the state" and every agent rebuilt it from scratch; that was fixed on
2026-07-26, so read these instead:

```txt
MAPA.md                  what the repo is, every command, what to configure
CLAUDE.md                how work is done here: the one rule and the conduct
context/LAST_HANDOFF.md  the single checkpoint: state, decisions, what is blocked
```

If there is a conflict, this order wins:

```txt
1. Direct user instruction
2. CLAUDE.md
3. context/LAST_HANDOFF.md
4. Specific docs
5. README.md
```

## The four branches, and what each one is for

There are FOUR and no more. If you find a fifth, it is work in flight or
something that should have been deleted.

```txt
main    EVERYTHING, without exception. The complete, working, verifiable
        version. The lines come DOWN from main, never the other way around.
        Protected with enforce_admins: NOBODY pushes directly, not the admin
        and not an agent holding the credential. Every change is a PR with
        green CI.

rd      The NGO line: Reduciendo Dano. Data, grants, supplements, events.
        What the RD people receive is a generated FILE, never this repo --
        a branch does not hide history, and anyone cloning it gets every
        commit including everything personal.

iskvw   The artistic line: curation, archive, portfolio. Its current public
        host is transitional; the repo must not depend on that domain forever.

mak     NOT a line: it is MAK's INBOX. Nothing lives here. The box opens a PR
        against it and the only exit is a PR into main. If it ever stops
        draining, it has become a line and that is a bug, not a state.
```

To bring a line up to date: `git merge origin/main`, never a rewrite. A line is
promoted to main by a curated PR with green CI. Work that fits no line gets
escalated before inventing a loose branch.

Why it matters, measured: a `mejoras` line was retired because it kept turning
main into a SUBSET, and a subset cannot merge back.

## Language

Everything in the repo is written in English: code, docs, commits, PRs. The one
exception is anything a human reads as a product — RD pieces and data, iskvw
curation — which goes in correct Spanish **with diacritics**. A title reading
"reduciendo ano" instead of "reduciendo daño" is not a typo, it reaches the
client.

## Environment

```txt
Primary user environment: Windows + Git Bash
User-facing Python command: py
Do not tell the user to run python
Keep context/LAST_HANDOFF.md ASCII-only
Do not store tokens, credentials, cookies, client secrets, or sensitive real data
Remote repo: https://github.com/ligereza/vibecodeine/
```

## Daily commands

```bash
py -m flujo app
py -m flujo app --desktop
py -m flujo verify
py -m flujo health
py -m flujo version
```

## Core workflow

```txt
request / email / issue
  -> intake
  -> job
  -> brief
  -> design / automation / review
  -> deliverable
  -> handoff
```

Useful commands:

```bash
py -m flujo job new "nombre pedido" --email inbox/correo.txt
py -m flujo job prepare jobs/<job>
py -m flujo intake json inbox/pedido.json
py -m flujo brief paquete-cotizacion jobs/<job>
```

## Operational areas

### RD / Suplementos

Institutional RD work: supplements, quotes, SVG labels/back covers, stand plans,
rider/costs. Map of the area, in Spanish because the people who use it read
Spanish: **[`docs/rd/MAPA_RD.md`](docs/rd/MAPA_RD.md)**.

The people who do this work do not open a console. What they get are files that
open by double-click, with no install, no server and no internet:

```bash
py tools/gen_rd_standalone.py    # bakes the database into the bundle
cd web && npm run build:rd       # -> dist_compartir/herramientas_rd.html
cd web && npm run build:plano    # -> dist_compartir/plano_rd.html
```

- `plano_rd.html` — the events manager builds the stand plan, exports the SVG
  and the rider PDF, adds her own symbols (an SVG, or an image the file traces
  by itself), and saves her layout as a preset that travels and comes back.
- `herramientas_rd.html` — database, quote, events and order intake.
- `docs/rd/propuesta_directiva.html` — what goes to the board.

The database inside the bundle comes from the same function the app serves, with
its privacy allowlist: field by field, contacts excluded on purpose. It is not a
copy, because a second copy of that allowlist is how a contact field leaks.

```bash
py -m flujo suplementos list
py -m flujo suplementos validate svg/suplementos_rd/09_contraportadas_dark/*.svg
py -m flujo rd-db productora <nombre>
py -m flujo plano projects/plano/ejemplos/evento_ejemplo.json --validate
```

### Studio / Eventos

Personal/studio work: flyers, Instagram inputs, VJ/club workflow, Resolume/Chataigne automation.

```bash
py -m flujo eventos flyer-auto "https://www.instagram.com/p/XXXX/"
py -m flujo resolume automatizar jobs/<job_id>
```

Rule (corrected 2026-07-26):

```txt
Real download = parth-dl (pip install parth-dl), primary path in flyer_auto.py
since 2026-07-22. curl_cffi is the secondary path on Linux: it imitates Chrome's
TLS fingerprint, which is what gets past the login wall there.
imginn.com is DEAD (403 Cloudflare). instaloader does not work (Instagram
demands login). Do not use yt-dlp.
```

### Cultura (art-research)

Descriptive/cultural layer: tapiz, tilde, psicosis, precursor. Third workspace of the web hub.
Hard limits: descriptive/cultural only, nothing generative-synthetic, psicosis never profiles real people.
The `README.md` art (`arte-ascii-readme.svg`, the animated codeine cup) is a finished artist piece: preserve its artwork shell and refresh only its generated text layer with `py tools/update_readme_svg.py`.

```bash
py projects/tapiz/vibecode_spaces.py archivo.py -m void --svg pieza.svg
```

### MAK (research + codex station)

MAK is a Linux box (LAN) running research (:8890) and codex (:8891) departments plus the hub (:8900).
Source code lives loose in ~/research, ~/codex, ~/plataforma (NOT a repo clone). The repo mirrors are
cultura/mak_research, mak_codex, mak_plataforma. Deploy = copy files + restart via systemd unit or
watchdog. Provider chains fall back cloud -> WIN (Windows notebook ollama) -> local ollama. Provider
health (salud_proveedores) demotes failing providers for 6h.

### xio (on-device Xiaomi controller)

`xio/` is a Flask controller + plugin engine that runs ON the phone (Termux + Shizuku/rish, non-root, HyperOS)
so it survives PC-off and screen-off. It turns the phone into the team's router + a show node: connectivity
supervisor, non-root charge limiter (USB port-role), two-layer self-heal (Shizuku + server), autonomous
reboot/hotspot recovery, and `showcontrol` (OSC + Art-Net + sACN sender for VJ/lighting). Send-only, pure stdlib.

The read-only surface is not the whole XIO server: `foh_monitor` and the MAK
bridge observe state, while `showcontrol` is an active, guarded sender/receiver
when that plugin is installed and enabled. See `xio/CAPACIDADES.md`; repository
presence is not proof of Xiaomi deployment.

```bash
cd xio/new && py server.py          # off-device dev run -> http://0.0.0.0:5000
# on-device deploy: push to /sdcard/xio_termux, then run_server.sh (see xio/new/README.md)
```

Security note: the server binds `0.0.0.0`, so every loaded plugin (including
`showcontrol` send routes) may be reachable by hotspot clients. Use the
show-control token and explicit source limits before exposing active routes to
untrusted devices; a trusted crew LAN is not an authorization mechanism.

### Web hub

Source:

```txt
web/src/
```

Generated context HTML:

```txt
context/flujo_hub.html
context/plano_demo.html
context/svg_visualizer.html
```

Build:

```bash
cd web
npm run typecheck
npm run build:context
cd ..
```

## Airdrop protocol

Agents without push access must deliver a ZIP containing `_airdrop/` at the top level.

Correct:

```txt
_airdrop/HANDOFF_2026-06-30_description.md
_airdrop/context/LAST_HANDOFF.md
_airdrop/src/flujo/module.py
_airdrop/tests/test_module.py
_airdrop/docs/something.md
```

Incorrect:

```txt
airdrop/
_airdrop/_airdrop/
v0.48/_airdrop/
files outside _airdrop/
Markdown links instead of real files
```

Every airdrop must include:

```txt
HANDOFF_*.md or HOTFIX_*.md
context/LAST_HANDOFF.md updated
real files in final repo paths
verification report
```

Validate and apply:

```bash
py scripts/validate_airdrop.py
py scripts/run_airdrop_checks.py "short message"
```

Resume if apply already happened but later checks failed:

```bash
py scripts/run_airdrop_checks.py --resume "short message"
```

If touching `src/flujo/airdrop.py`, explicit user approval is required:

```bash
py scripts/validate_airdrop.py --allow-airdrop-engine
py scripts/run_airdrop_checks.py "short message" --allow-airdrop-engine
```

## Verification

Python changes:

```bash
py -m compileall src/flujo
py -m pytest tests/ -q
py -m flujo verify
```

Web changes:

```bash
cd web
npm run typecheck
npm run build:context
cd ..
```

Airdrop changes:

```bash
py scripts/validate_airdrop.py
py scripts/run_airdrop_checks.py "short message"
```

Do not report success unless the relevant verification was actually run.

## Cleanup

Safe local cleanup:

```bash
rm -rf _airdrop
find . -type d -name "__pycache__" -prune -exec rm -rf {} +
rm -rf .pytest_cache
rm -rf _logs
git status --short
```

Do not commit or include in airdrops:

```txt
__pycache__/
.pytest_cache/
node_modules/
dist/
build/
_airdrop/
_airdrop_backups/
_logs/
*.zip
*.db
credentials
heavy real assets
```

Historical docs should be archived, not deleted blindly.

## Repository map

```txt
src/flujo/        core Python package and CLI
web/              React/Vite local web hub
context/          current handoff and generated local HTML
tests/            pytest suite
scripts/          validation, airdrop, maintenance scripts
docs/             operational manuals
tools/            helper tools and external workflow specs
projects/         operational project folders and delegated work
jobs/             local jobs
schemas/          intake schemas
.github/          CI, issue templates, repo automation
knowledge/        versioned operational memory
```

## Closing a task

THERE IS NO DELIVERABLE (2026-07-26, user's order). The mandatory closing ritual
that used to live here — a formal verification report with a fixed format —
pushed agents into fabricating a product, a report or a plan nobody asked for,
and that derailed several sessions in a row. It was removed.

What replaces it: if you touched code, run what that code covers and paste the
real output, not an "OK". If you did not touch code, there is nothing to report.
Verification exists to find out whether it works, not to decorate a closing. The
verdict on a PR is its CI matrix, never the local pytest.

## License

MIT
-->
