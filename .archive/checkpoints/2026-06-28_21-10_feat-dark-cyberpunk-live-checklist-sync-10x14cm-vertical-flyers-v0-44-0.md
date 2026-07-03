# Checkpoint — feat: dark cyberpunk, live checklist sync & 10x14cm vertical flyers - v0.44.0

Fecha: 2026-06-28_21-10

## Estado

# LAST_HANDOFF - flujo continuation state

IMPORTANT: This file is intentionally ASCII-only to avoid mojibake on Windows + Git Bash/cp1252.
Do not use accents, enye, emoji, smart quotes, or special arrows here.
Daily commands for owner on Windows/Git Bash must use `py`, not `python`.

Date: 2026-06-28
Current version: 0.44.0
Main daily entry: `py -m flujo app`
Desktop entry: `py -m flujo app --desktop`
Verify on Windows: `py -m flujo verify`
Airdrop check on Windows: `py scripts/validate_airdrop.py` then `py scripts/run_airdrop_checks.py "message"`

## Current state

The repo is healthy after the v0.40 hub airdrop, v0.41.0 unified React hub, v0.42.1 example ingest templates, and the new v0.44.0 release that integrates Claude's dark layout with restored and repaired 17-item Rider Checklist with procedural Lucide icons (no emojis), persistent checkbox printing, layer reordering (bring to front on select), and checklist Markdown exports.

Real package CLI:
- `py -m flujo health`
- `py -m flujo doctor`
- `py -m flujo verify`
- `py -m flujo app`
- `py -m flujo hub serve --open`
- `py -m flujo hub index ...`
- `py -m flujo hub route ...`

## Recent completed work

### v0.44.0 - Rider requirements restore 17 items + icons + layer ordering + export
- Fully merged Claude's dark styling with our 17-item requirements checklist, mapping each to a custom Lucide icon instead of emojis.
- Implemented real-time synchronization: checking items in the checklist automatically places the corresponding elements/symbols on the black SVG canvas.
- Configured SVG canvas viewBox to 2970x2100 px to match the official dimensions of `rider_eventos_a4_horizontal` in the format index.
- Swapped SVG canvas background to black `#09090b` for design mode.
- Aligned flyer fallbacks in the Python rendering engine (`piezas.py` and `brief_to_project.py`) to vertical 10x14 cm (2000x2800 px).

### v0.43.2 - Fix CI health check - ignore node_modules and web
- Updated `scripts/flujo_health.py` `check_jsons(
... (truncado para checkpoint)

## Cambios realizados

-

## Próximo paso

-
