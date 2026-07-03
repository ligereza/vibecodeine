Date: 2026-07-03
Version: 0.48.5 (pyproject.toml / src/flujo/version.py, matching)

Done:
- Root cleanup (extreme cleanup requested by user): 14 stray HANDOFF_*.md files at repo root moved out -- the 2 recent ones (2026-07-02, this session's quotation/flyers work) to docs/handoffs/, the 12 legacy ones (2026-06-30 and earlier, including a misnamed HANDOFF_1000.md) to docs/handoffs/archive/root/, matching the repo's own documented policy in docs/REPO_MAP.md. 56 stray checkpoints/*.md files (2026-06-22 to 2026-06-30) moved to .archive/checkpoints/ per docs/HIGIENE_REPO.md ("mover aqui lo viejo para mantener la raiz limpia"); checkpoints/ dir kept alive with .gitkeep since scripts/checkpoint.sh and src/flujo/airdrop.py write new checkpoints there. Local caches (.pytest_cache, __pycache__) purged.
- Closed pending item: cream (print-safe) version of the 2026-07-02 suplementos flyers (09/10) and plano will NOT be produced -- user explicitly decided dark/neon is final for these pieces (2026-07-03). Removed from next/blockers.
- User will handle direct contact info (email/phone) for the events quotation themselves; removed from agent's pending list.
- CRT phosphor dot-scanline/Rutt-Etra converter tool added (tools/crt_phosphor/), committed directly to main by the user (commit 343d08c).
- Assistant identity: the repo assistant is named "Vibo" (user request). Canonical definition in CLAUDE.md (repo root, auto-loaded by Claude Code each session) plus an "Identidad del asistente" section in AGENTS.md, including a note that real visual QA goes through the user's local Illustrator, not headless renderers.
- EVENTOS: general quotation package for a marketing agency (no venue/date), dark/neon style per explicit user decision, in datadrops/cotizacion_general_eventos/ (md + branded printable html + PDF + plano with PlanoTool symbology/legend 2970x2100 + rider 17-item checklist). Rates set by boss (CLP/day): informativo 250k; informativo+testeo 300k (6 vol); full service massive event 500k (15 vol) with exact breakdown. See docs/handoffs/HANDOFF_2026-07-02_cotizacion_eventos_y_flyers_suplementos.md.
- SUPLEMENTOS: 2 new QR backs in svg/suplementos_rd/02_editables_svg/ (09_post_fiesta_back_qr_dark, 10_linea_suplementos_back_qr_dark), dark/neon system, content verbatim from approved master JSON, QR decodes to https://reduciendodano.cl, validator OK. These replace the failed datadrops/flyers/BACK.SUPLEMENTOS.pdf (black/neon, empty). Dark/neon is final for these two pieces -- no cream version will be made (explicit user decision, see Done above).
- Real RD logo (Version A) recovered without AI: assets/logo/RD_logo_A_transparente.png, crop + HSV chroma-key from datadrops/2026-06-22_154643_0_raveeditrdrealv5/rave_edit_rd_real_v5.png. Fills the asset v4.1's inventory marked PENDING.
- New skill .claude/skills/entregas-rd/ (SKILL.md + generadores/ + plantillas/) documenting the whole playbook (rules, recipes, Windows-specific notes: Edge headless instead of cairosvg for quick visual checks, Illustrator as the real QA tool) so future sessions do not reinvent this flow.
- Resolume/Chataigne automator (src/flujo/resolume/automator.py) generates XML pre-flight, CSV OSC, README, and an experimental .noisette (v0.48.2 to v0.48.5, 4 rewrites, still unverified against a real file).
- SVG Studio, Plano/Rider, Cotizacion, Jobs, Intake, Commands stable in web/ (React/Vite single-file build into context/*.html).
- Web hub tools list is defined in web/src/components/AppShell.tsx (RD_NAV / STUDIO_NAV) plus a view case in web/src/App.tsx.
- Mapping LED (Event Rigging Master Console) Studio tool: this handoff previously said it was "uncommitted" -- it was already committed in 9970575 before this session started. Corrected here; do not re-flag it as pending.
- INDEX_FORMATOS.json reconciled with formats actually used in code (carrusel, etiqueta horizontal generica).

Next:
- Get a real .noisette file exported from the user's Chataigne 1.10.3 and save it as a fixture under tests/ before touching build_chataigne_noisette_experimental again.
- Get user QA on the new flyers/plano/logo in their local Illustrator before wide distribution.
- Bring context/SESSION_STATE.json and context/AVANCES_BLOCK.txt current every session end (see AGENTS.md rule).

Blockers:
- build_chataigne_noisette_experimental has no real .noisette to validate against; do not guess the schema again, ask the user for the exported file.
