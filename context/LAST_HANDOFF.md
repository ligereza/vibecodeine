Date: 2026-07-02
Version: 0.48.5 (pyproject.toml / src/flujo/version.py, matching)

Done:
- CRT phosphor dot-scanline/Rutt-Etra converter tool added (tools/crt_phosphor/), committed directly to main by the user (commit 343d08c).
- Assistant identity: the repo assistant is named "Vibo" (user request). Canonical definition in CLAUDE.md (repo root, auto-loaded by Claude Code each session) plus an "Identidad del asistente" section in AGENTS.md, including a note that real visual QA goes through the user's local Illustrator, not headless renderers.
- EVENTOS: general quotation package for a marketing agency (no venue/date), dark/neon style per explicit user decision, in datadrops/cotizacion_general_eventos/ (md + branded printable html + PDF + plano with PlanoTool symbology/legend 2970x2100 + rider 17-item checklist). Rates set by boss (CLP/day): informativo 250k; informativo+testeo 300k (6 vol); full service massive event 500k (15 vol) with exact breakdown. See HANDOFF_2026-07-02_cotizacion_eventos_y_flyers_suplementos.md.
- SUPLEMENTOS: 2 new QR backs in svg/suplementos_rd/02_editables_svg/ (09_post_fiesta_back_qr_dark, 10_linea_suplementos_back_qr_dark), dark/neon system, content verbatim from approved master JSON, QR decodes to https://reduciendodano.cl, validator OK. These replace the failed datadrops/flyers/BACK.SUPLEMENTOS.pdf (black/neon, empty) -- note: user explicitly chose dark/neon here despite v4.1 SS6.H mandating cream for PRINT of these pieces; a cream version is still needed before physical printing.
- Real RD logo (Version A) recovered without AI: assets/logo/RD_logo_A_transparente.png, crop + HSV chroma-key from datadrops/2026-06-22_154643_0_raveeditrdrealv5/rave_edit_rd_real_v5.png. Fills the asset v4.1's inventory marked PENDING.
- New skill .claude/skills/entregas-rd/ (SKILL.md + generadores/ + plantillas/) documenting the whole playbook (rules, recipes, Windows-specific notes: Edge headless instead of cairosvg for quick visual checks, Illustrator as the real QA tool) so future sessions do not reinvent this flow.
- Resolume/Chataigne automator (src/flujo/resolume/automator.py) generates XML pre-flight, CSV OSC, README, and an experimental .noisette (v0.48.2 to v0.48.5, 4 rewrites, still unverified against a real file).
- SVG Studio, Plano/Rider, Cotizacion, Jobs, Intake, Commands stable in web/ (React/Vite single-file build into context/*.html).
- Web hub tools list is defined in web/src/components/AppShell.tsx (RD_NAV / STUDIO_NAV) plus a view case in web/src/App.tsx.
- Mapping LED (Event Rigging Master Console) Studio tool: this handoff previously said it was "uncommitted" -- it was already committed in 9970575 before this session started. Corrected here; do not re-flag it as pending.
- INDEX_FORMATOS.json reconciled with formats actually used in code (carrusel, etiqueta horizontal generica).

Next:
- Get a real .noisette file exported from the user's Chataigne 1.10.3 and save it as a fixture under tests/ before touching build_chataigne_noisette_experimental again.
- If the new suplementos flyers (09/10 dark) are meant for physical print, generate the cream version too (v4.1 SS6.H hard rule) before sending to imprenta.
- Get user QA on the new flyers/plano/logo in their local Illustrator before wide distribution.
- Confirm direct contact info (email/phone) for the events quotation document before sending to the agency.
- Bring context/SESSION_STATE.json and context/AVANCES_BLOCK.txt current every session end (see AGENTS.md rule) -- this file had drifted since 2026-07-01 with stale info about Mapping LED; corrected now.

Blockers:
- build_chataigne_noisette_experimental has no real .noisette to validate against; do not guess the schema again, ask the user for the exported file.
- Cream (print-safe) versions of the 2026-07-02 suplementos flyers and plano do not exist yet; only dark/neon was produced this session per explicit user decision.
