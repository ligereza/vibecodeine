# LAST_HANDOFF - flujo continuation state

IMPORTANT: This file is intentionally ASCII-only to avoid mojibake on Windows + Git Bash/cp1252.
Do not use accents, enye, emoji, smart quotes, or special arrows here.
Daily commands for owner on Windows/Git Bash must use `py`, not `python`.

Date: 2026-06-28
Current version: 0.43.2
Main daily entry: `py -m flujo app`
Desktop entry: `py -m flujo app --desktop`
Verify on Windows: `py -m flujo verify`
Airdrop check on Windows: `py scripts/validate_airdrop.py` then `py scripts/run_airdrop_checks.py "message"`

## Current state

The repo is healthy after the v0.40 hub airdrop, v0.41.0 unified React hub, v0.42.1 example ingest templates, the v0.43.1 release with automatic back covers (contraportadas) and vertical flyers, and the new v0.43.2 hotfix that prevents health checks from scanning node_modules or web workspace.

Real package CLI:
- `py -m flujo health`
- `py -m flujo doctor`
- `py -m flujo verify`
- `py -m flujo app`
- `py -m flujo hub serve --open`
- `py -m flujo hub index ...`
- `py -m flujo hub route ...`

## Recent completed work

### v0.43.2 - Fix CI health check - ignore node_modules and web
- Updated `scripts/flujo_health.py` `check_jsons()` to ignore `node_modules/` and `web/` directories, preventing scans of node packages (which contain tsconfig JSONC and trigger validation failures).
- Guaranteed completely clean and fast CI and local repository health runs.

### v0.43.1 - Supplement Back Covers (Contraportadas) with Automation and CLI
- Automated the generation of SVG back covers in `jobs/{job_id}/flows/contraportada.svg` when creating a job in the Hub with area=suplementos.
- Added CLI option `--brief / -b` to the `py -m flujo suplementos contraportada` command to easily overwrite benefits or campaign text.
- Unified supplement lookup to search in both `suplementos_config.py` (real production data) and the Illustrator spec JSON, supporting all 11 supplements dynamically.
- Fixed a critical layout bug that occurred when replacing the "NOMBRE DEL SUPLEMENTO" placeholder with split/multiline names (e.g. "Pre Fiesta", "Post Fiesta").
- Documented full pre-press guidelines and operation in a new manual: `docs/CONTRAPORTADAS_SUPLEMENTOS_OPERATIVO.md`.
- Integrated contraportada specifications and margin checklists into `linea_editorial/v4.1.md` Section H.

### v0.43.0 - Example Ingest Templates
- Added templates `knowledge/templates/*.for_ai.json` for AI visual analysis.
- Knowledge ingest now writes `manifest.json`, `for_ai.json`, and `README.md`.
- Supports templates for cartelera digital, flyer 10x14, supplement flyer, and logo source.

### v0.42.0 - Knowledge Base Skeleton
- Added `knowledge/` with productoras, venues, logos, and examples.
- Seeded Creamfields, The Grid, Rave Under template, and Espacio Riesco.
- Added commands: `py -m flujo knowledge list/show/classify/ingest-example/logo-source`.

## Airdrop model - keep this intact

Airdrop is the safe patch delivery path for agents without direct push.

Expected package:
- A ZIP containing `_airdrop/` at the top level.
- Files inside `_airdrop/` mirror their final repo paths.
- Include a `HANDOFF_*.md` or `HOTFIX_*.md` in the airdrop.
- Do not include caches, build output, credentials, binaries, or generated local data.

Apply path:
```bash
py scripts/validate_airdrop.py
py scripts/run_airdrop_checks.py "short message"
```

If the airdrop modifies `src/flujo/airdrop.py`, explicit review is required:
```bash
py scripts/validate_airdrop.py --allow-airdrop-engine
py scripts/run_airdrop_checks.py "short message" --allow-airdrop-engine
```

Runner behavior:
- validates `_airdrop/`;
- performs dry-run using `flujo.airdrop.scan_airdrop()`;
- applies with backup and manifest;
- installs editable dev package;
- runs compileall, pytest, health, version, changelog check and hub smoke when available;
- only then writes checkpoint/commit/push unless skipped.

## Daily operating direction

flujo is focused on a free local-first request/work-status flow:

Gmail / WhatsApp / GitHub Issue
  -> ordered request
  -> flujo job / brief or IG download
  -> design / review / delivery
  -> visual portal for boss/client

Recommended free stack:
- Gmail routing by subject: `eventos` -> EVENTOS, `suplementos` -> SUPLEMENTOS.
- Google Apps Script bridge: `tools/gmail_to_github_issues.gs`.
- GitHub Issues: request/change inbox with area labels.
- GitHub Projects: visual kanban for boss.
- `py -m flujo portal`: static HTML status portal.
- `py -m flujo app`: daily hub for operator.

## Important Windows/Git Bash rules

- Use `py -m flujo ...`, not `python -m flujo ...`, in user-facing docs and handoff.
- Keep this file ASCII-only.
- Avoid special symbols in terminal output when possible.
- Do not store tokens, credentials or sensitive client data.
- Privacy scan/sanitize before sending real request data to external AI.

## Current command examples

Install/editable:
```bash
py -m pip install -e .
```

Daily:
```bash
py -m flujo app
```

Verify:
```bash
py -m flujo verify
```

Portal:
```bash
py -m flujo portal --repo-url https://github.com/ligereza/vibecodeine
```

Hub server:
```bash
py -m flujo hub serve --open
```

Hub route:
```bash
py -m flujo hub route where --area eventos --pieza flyer
```

Hub index:
```bash
py -m flujo hub index agent-brief "etiqueta creatina"
```

## Cleanup policy

Safe to remove locally but do not include in airdrops:
- `__pycache__/`
- `.pytest_cache/`
- `src/flujo.egg-info/`
- `_airdrop/`
- `_airdrop_backups/`
- `_logs/`

Historical material should be archived, not deleted blindly.

## Next recommended changes

1. Create a validation tool or command for contraportadas (such as `py -m flujo suplementos validate`) to ensure compliance with the technical margin and contrast specs of Section H of the style guide.
2. Extend `prepare_supplement_job_assets` to support generating multipage PDFs from the command line or hub directly.
3. Split the very large `src/flujo/cli.py` into submodules (`cli_jobs.py`, `cli_suplementos.py`, etc.) for cleaner maintenance.
