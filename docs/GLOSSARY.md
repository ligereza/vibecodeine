# GLOSSARY — Spanish code, English rule

> **Why this file exists.** The repository language policy says everything except human-facing
> product is written in English. The tree says otherwise, measured 2026-07-30:
> **236 Python files carry Spanish comments against 36 in English.** So an agent
> reads the rule, searches in English, finds nothing, and concludes the thing
> does not exist — then rebuilds it or reports it missing. That is not a style
> problem. It is how `curatoria` was recorded in memory as `curation` and a
> Spanish search answered "nothing found" while the answer sat right there.
>
> Renaming 236 files is not the fix: cron lines, systemd units and the box's
> running copies all reference those names, so a rename breaks the machine that
> works. The fix is that **a search in either language finds the other side.**

## The rule from here on

| What | Language |
|---|---|
| NEW code, identifiers, comments, docstrings, file names | **English** |
| Commit messages, PR titles and bodies, `context/*.md`, this file | **English** |
| Existing Spanish names already referenced by cron, systemd or the box | **left alone** until their consumer changes |
| Anything a human reads as a product (RD, iskvw curation, reports) | **Spanish with diacritics**, always |

A rename is only worth it when the file has no live consumer. `coherencia.py`
was renamed to `coherence.py` the day it was born, before anything invoked it;
`entregar.py` is not renamed, because a cron line calls it every 6 hours.

## The map

Domain terms that appear in file and identifier names across the tree. Search
either column.

| Spanish (in the code) | English | Where it lives |
|---|---|---|
| `algebra` | algebra (VSA over meaning) | `mak_codex/motor_semantico/` |
| `archivo` | archive (the pieces + links contract) | `contrato_archivo.py`, `iskvw/` |
| `campo` | field (the 2D projection of the corpus) | `iskvw/piel/campo/` |
| `capataz` | foreman (picks the next action) | `mak_plataforma/capataz.py` |
| `cola` | queue | `mak_research/cola.py` |
| `compilador` | compiler (spec -> SVG) | `motor_semantico/compilador.py` |
| `contexto` | context | `tools/contexto_repo.py` |
| `contraportada` | back cover | `svg/suplementos_rd/` |
| `corregir` | correct / fix (language pass) | box `lenguaje/corregir.py` |
| `cotizacion` | quote (money) | `data/cotizacion_servicios.json` |
| `critico` | critic (perceptual QA over pixels) | `motor_semantico/critico.py` |
| `curatoria` | curation | `cultura/mak_curatoria/` |
| `ensayo` | essay (the long research format) | `docs/cultura/FORMATO_ENSAYO.md` |
| `entregar` | deliver (harvest pieces -> PR) | `mak_plataforma/entregar.py` |
| `esquema` | schema | `motor_semantico/esquema.py` |
| `eventos` | events | `flujo eventos`, RD database |
| `fuentes` | sources (the source gate) | `mak_research/fuentes.py` |
| `guardia` | guard / watchdog loop | `curatoria_guardia.sh` |
| `iconos` | icons | `tools/iconos_conjunto.py`, codex mode |
| `ideas` | ideas (declare one, the micelio relates it) | `mak_plataforma/ideas.py` |
| `informe` | report | research output |
| `junta` | board (governance round) | `mak_plataforma/junta.py` |
| `latido` | heartbeat | `mak_plataforma/latido.py` |
| `lenguaje` | language (55k dictionary, tilde signal) | box `lenguaje/` |
| `material` | material (the user's own input) | `mak_plataforma/material.py` |
| `medir` | measure | box `lenguaje/medir.py` |
| `memoria` | memory | `mak_research/memoria/` |
| `micelio` | mycelium (the relation graph) | `corpus_a_micelio.py` |
| `mineria` | mining (RD candidate extraction) | `src/flujo/rd/mineria_rd.py` |
| `ordenes` | orders (remote whitelist handler) | `mak_curatoria/ordenes.py` |
| `panel` | read-only web view; it observes and does not imply control of the underlying organism | several |
| `puente` | bridge between a monitor and another service; its direction and write capability must be declared | `cultura/mak_xio_puente/` |
| `showcontrol` | active XIO plugin for guarded OSC/Art-Net/sACN traffic; not the same as the read-only panel | `xio/new-plugins/showcontrol/` |
| `Face A` / `Face B` | XIO network contexts: studio/development and live-show/hotspot; neither label proves runtime installation | `xio/FACES.md` |
| `pausa` | pause (stop on error, wait for a human) | `mak_research/pausa.py` |
| `percepcion` | perception (what the box sees) | `mak_curatoria/percepcion.py` |
| `piel` | skin (the site's presentation layer) | `iskvw/piel/` |
| `piezas` | pieces (codex output, archive entries) | `codex/piezas/`, archive |
| `plano` | floor plan | `src/flujo/plano/` |
| `propuestas` | proposals (RD drafts) | `tools/gen_propuestas_rd.py` |
| `rasterizador` | rasteriser (SVG -> PNG/GIF) | `motor_semantico/rasterizador.py` |
| `red` | network | `mak_plataforma/red_watch.py` |
| `revisor` | reviewer (votes and can merge PRs) | `mak_plataforma/revisor.py` |
| `salud` | health (measured provider reliability) | `salud_proveedores.json` |
| `semillas` | seeds (hand-written input rows) | `data/venues/` |
| `simbolos` | symbols (plan catalogue) | `data/plano_simbolos.json` |
| `suplementos` | supplements (RD product line) | `svg/suplementos_rd/` |
| `tapiz` | tapestry (art instrument) | `projects/tapiz/` |
| `tilde` | tilde (the accent, and the meter) | `tools/tilde_meter.py` |
| `trabajo` | work (the box's job loop) | `mak_plataforma/trabajo.py` |
| `trazos` | strokes (traced silhouettes) | `iskvw/piel/trazos/` |
| `triangular` | triangulate (cross-check records) | `tools/triangular_fichas.py` |
| `vigilar` | watch / monitor | `mak_plataforma/vigilar_red.py` |
| `vocabulario` | vocabulary (the closed word list) | `motor_semantico/vocabulario.py` |

## Two searches that already failed

- `curatoria` was written in memory as `curation`; searching the Spanish word
  returned "nothing found" while the note existed. Fixed at the root by writing
  memory in English from 2026-07-26 — and by this table, which lets the Spanish
  word reach it.
- `.remember/` is invisible to ripgrep (its `.gitignore` is `*`). Search it with
  PowerShell `Select-String -Path "<repo>\.remember\*"`. A Grep that returns
  nothing over an ignored path is not evidence of absence.

Retirement: when the tree is English enough that the table has fewer than ten
rows worth keeping.
