Date: 2026-07-03
Version: 0.48.5 (pyproject.toml / src/flujo/version.py, matching)

Done:
- EVENTOS: general quotation package for marketing agency (no venue/date) in datadrops/cotizacion_general_eventos/ (md + branded printable html + plano with PlanoTool symbology/legend 2970x2100 + rider 17-item checklist). Rates set by boss (CLP/day): informativo 250k; informativo+testeo 300k (6 vol); full service massive event 500k (15 vol) with exact breakdown. See HANDOFF_2026-07-02_cotizacion_eventos_y_flyers_suplementos.md.
- SUPLEMENTOS: 2 new QR backs in svg/suplementos_rd/02_editables_svg/ (09_post_fiesta_back_qr, 10_linea_suplementos_back_qr), cream system, content verbatim from approved master JSON, QR decodes to https://reduciendodano.cl, validator 10/10 OK. These replace the failed datadrops/flyers/BACK.SUPLEMENTOS.pdf (black/neon, empty).
- DARK/NEON variants (boss request): flyers 11/12 dark in 02_editables_svg, dark quotation html + dark plano in datadrops/cotizacion_general_eventos/, official rave palette v4.1 (black #0A0A0A / magenta #C800C8 / yellow #FFD21F). Real RD logo Version A extracted (crop + chroma key, NOT AI-regenerated) to assets/logo/RD_logo_A_transparente.png (was PENDIENTE in v4.1 inventory). Cream versions remain the print-valid ones per v4.1 6.H.
- FULL DARK LINE (2026-07-03): all 8 supplement FRONTS adapted to the rave dark system in svg/suplementos_rd/05_dark_neon/ via new generator gen_dark_fronts.py (skill entregas-rd, receta E): dynamic card heights with vertical centering, pixel-budget line wrapping, real logo embedded, validator 8/8 OK. Pre Fiesta accent switched to magenta RD to differ from Hongos violet.
- VECTORIZED SET (2026-07-03): gen_vectorizar.py (fontTools, real DejaVu curves) produced 12 text-to-curves files: 8 dark fronts + 2 dark backs in 06_dark_vectorizado_svg/, cream backs 09/10 in 03_final_vectorizado_svg/ (historic pending closed). New gallery 04_preview/preview_flyers_dark.html links editable+vectorized per piece.
- AUTOMATION (2026-07-03, boss request 'revision sin revision'): new CI quality gate .github/workflows/validar-piezas.yml (validates ALL supplement SVGs on every push/PR touching svg/) + docs/AUTOMATIZACION_FLUJO.md (mold analogy + 4-phase roadmap to cloud-only work: enable write access + install Claude GitHub App -> @claude on issues generates pieces via skill entregas-rd -> validated PR -> approve from phone).
- Assistant identity: the repo assistant is now named "Vibo" (user request). Canonical definition in CLAUDE.md (repo root, new file, auto-loaded by Claude Code each session) plus an "Identidad del asistente" section in AGENTS.md. If the user renames it, update both files together. (branch claude/custom-name-preference-543qs0, docs-only)
- Resolume/Chataigne automator (src/flujo/resolume/automator.py) generates XML pre-flight, CSV OSC, README, and an experimental .noisette (v0.48.2 to v0.48.5, 4 rewrites, still unverified against a real file).
- SVG Studio, Plano/Rider, Cotizacion, Jobs, Intake, Commands stable in web/ (React/Vite single-file build into context/*.html).
- Web hub tools list is defined in web/src/components/AppShell.tsx (RD_NAV / STUDIO_NAV) plus a view case in web/src/App.tsx.

Doing (uncommitted local changes on the user's machine, not pushed):
- Added a new Studio tool "Mapping LED" (Event Rigging Master Console) wired via iframe: web/src/components/MappingTool.tsx, web/public/mapping.html, web/scripts/copy-context.mjs extended, AppShell.tsx / App.tsx updated.
- INDEX_FORMATOS.json cleanup: reconciled tools/piezas_vectoriales/plantillas/INDEX_FORMATOS.json with formats actually used in code (carrusel, etiqueta horizontal generica) and removed an unused duplicate at repo root.

Next:
- Get a real .noisette file exported from the user's Chataigne 1.10.3 and save it as a fixture under tests/ before touching build_chataigne_noisette_experimental again.
- Decide if/when to commit and push the Mapping LED tool changes above.
- Bring context/SESSION_STATE.json and context/AVANCES_BLOCK.txt current every session end (see AGENTS.md rule); they had drifted 6 versions behind real state before this handoff.

Blockers:
- build_chataigne_noisette_experimental has no real .noisette to validate against; do not guess the schema again, ask the user for the exported file.
- Remote session has READ-ONLY GitHub access (push 403 on every branch); deliveries also packaged as airdrop ZIP. New design-chat material did NOT reach the repo (origin/main unchanged, no issues after Jun 24) nor Adobe CC storage; ask the user where it lives.
- Pending: real RD WhatsApp number; direct contact info for the quotation doc; QR backs for products 02-07; issue #6 Omega 3 label.
