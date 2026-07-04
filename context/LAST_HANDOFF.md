Date: 2026-07-04
Version: 0.48.5 (pyproject.toml / src/flujo/version.py, matching)

PROTOCOLO DE SEGURIDAD OBLIGATORIO ANTES DE CERRAR SESION (ver tools/vibo_voz/SEGURIDAD.md):
1. Cerrar la voz (ESC), no dejar escuchando.
2. py tools/vibo_voz/limpiar.py (matar agentes colgados).
3. VIBO_AGENTS_ENABLED vacio en el .env si no se seguira usando.
4. git status limpio; nada sensible trackeado (.env/estado/agentes/proyectos.json).
5. Actualizar LAST_HANDOFF.md y SESSION_STATE.json (fecha/version reales).
6. Si el equipo es compartido: cerrar Gmail/Google y la terminal.
Sin estos 6 pasos la sesion NO esta cerrada.

Done:
- SEGURIDAD ASISTENTE DE VOZ (2026-07-04): cerrado el vector de riesgo (que alguien o un
  descuido gaste el Claude de pago via la voz, o que el microfono capte sin saberlo).
  (1) Agentes Claude de PAGO APAGADOS por defecto: encargar_a_claude no lanza nada salvo
  VIBO_AGENTS_ENABLED=1 en el .env. (2) Tope de gasto VIBO_MAX_AGENTES=15 + freno anti-bucle
  5/60s + un secretario a la vez. (3) Microfono se abre SOLO mientras se aprieta F8 (en reposo
  cerrado, no captura). (4) Auto-apagado por inactividad VIBO_IDLE_MIN=5. (5) leer/escribir_archivo
  acotados al repo/proyectos y bloquean .env/llaves/secrets. (6) limpieza automatica de agentes
  colgados al arrancar. Doc completo + protocolo obligatorio en tools/vibo_voz/SEGURIDAD.md.
- SEGURIDAD GITHUB (2026-07-04): .github/workflows/claude.yml BLINDADO (seguia siendo un vector:
  cualquiera con @claude podia disparar Claude de pago con write). Ahora: gate por autor
  OWNER/MEMBER/COLLABORATOR, ignora bots (anti-bucle/re-disparo), permisos minimos (sin id-token),
  concurrency por issue/PR, y trata el issue como pedido (no instrucciones), prohibido revelar
  secretos. Sigue INACTIVO (sin secret ANTHROPIC_API_KEY ni app). Otros workflows (ci, validar-piezas,
  publicar-catalogo, render) revisados: limpios (sin pull_request_target, sin secretos, sin inyeccion).
- ASISTENTE DE VOZ 3 PERSONAS (2026-07-04): tools/vibo_voz/ - asistente de voz local
  con Gemini Live (audio en tiempo real + voz natural, sin reconocedores locales).
  Tres system prompts diferenciados en prompts.py: CODE (nucleo privado, joven, maxima
  apertura a variables, minima responsabilidad, no toca el trabajo), VIBO (cara publica
  / pseudonimo, la voz por defecto para lo personal/general), REDU (modo trabajo ONG
  confidencial, sesion aparte, GitHub SOLO LECTURA). Runtime: 2 sesiones Live (publico
  CODE/VIBO <-> redu) con handoff automatico via tools abrir_redu / volver_a_publico;
  la separacion de sesiones ES la confidencialidad. Push-to-talk global F8 (no estorba
  al escribir). Keys (GEMINI_API_KEY + token GitHub read-only) solo en tools/vibo_voz/.env
  (gitignored, nunca en codigo). github_tools.py: pedidos_abiertos/existe/cambios_recientes/
  guardar_idea (solo REDU). Enganchado a la CLI como 'flujo voz' (ingreso de dato por voz),
  OPCIONAL: extra [voz] en pyproject, lazy import, NO es dependencia de flujo (avisa si
  faltan libs o .env). Es un starter: falta probar en el PC (micro/audio) y confirmar el id
  de modelo Live real de la cuenta (VIBO_LIVE_MODEL en .env). NOTA: NO se renombro VIBO->CODE
  en el repo; VIBO se queda como cara publica (decision del usuario).
- CORRECCION continuidad: el "git push pending" del Adobe toolkit ya estaba resuelto
  (main == origin/main, 0/0). Nota vieja.
- ADOBE TOOLKIT (2026-07-03, Vibo): new tools/ automation set for Illustrator/Photoshop/After Effects + a CEP panel (addon) covering all three. Illustrator: titles_to_photos (text block -> per-line PNG/JPG), logo_revector_extrude (JPEG -> image trace + vector 3D extrude -> SVG/EPS/PDF + PNG), logo_revector_batch (whole-folder). Photoshop: layers_to_photos (per-layer PNG, transparent). After Effects: titles_to_comps (one comp per title) and auto_titles_mixer_ae (one comp per title with Audio Spectrum equalizer + title pulsing to volume via Convert Audio to Keyframes; match names/indices so it works in ES or EN AE). Panel: tools/adobe_panel/ (CEP manifest + minimal CSInterface + main.js dispatcher; buttons per host; build_zxp.ps1 to sign a .zxp). Docs: tools/ADOBE_TOOLKIT.md + tools/adobe_panel/README.md. Pure .jsx/panel, no src/flujo change. Auto-checkpoint already committed to main (commit 257157a); git push pending. See docs/handoffs/HANDOFF_2026-07-03_adobe_toolkit.md.
- EVENTOS: general quotation package for marketing agency (no venue/date) in datadrops/cotizacion_general_eventos/ (md + branded printable html + plano with PlanoTool symbology/legend 2970x2100 + rider 17-item checklist). Rates set by boss (CLP/day): informativo 250k; informativo+testeo 300k (6 vol); full service massive event 500k (15 vol) with exact breakdown. See docs/handoffs/HANDOFF_2026-07-02_cotizacion_eventos_y_flyers_suplementos.md.
- SUPLEMENTOS: 2 new QR backs in svg/suplementos_rd/02_editables_svg/ (09_post_fiesta_back_qr, 10_linea_suplementos_back_qr), cream system, content verbatim from approved master JSON, QR decodes to https://reduciendodano.cl, validator 10/10 OK. These replace the failed datadrops/flyers/BACK.SUPLEMENTOS.pdf (black/neon, empty).
- DARK/NEON variants (boss request): flyers 11/12 dark in 02_editables_svg, dark quotation html + dark plano in datadrops/cotizacion_general_eventos/, official rave palette v4.1 (black #0A0A0A / magenta #C800C8 / yellow #FFD21F). Real RD logo Version A extracted (crop + chroma key, NOT AI-regenerated) to assets/logo/RD_logo_A_transparente.png (was PENDIENTE in v4.1 inventory). Cream versions remain the print-valid ones per v4.1 6.H.
- FULL DARK LINE (2026-07-03): all 8 supplement FRONTS adapted to the rave dark system in svg/suplementos_rd/05_dark_neon/ via new generator gen_dark_fronts.py (skill entregas-rd, receta E): dynamic card heights with vertical centering, pixel-budget line wrapping, real logo embedded, validator 8/8 OK. Pre Fiesta accent switched to magenta RD to differ from Hongos violet.
- VECTORIZED SET (2026-07-03): gen_vectorizar.py (fontTools, real DejaVu curves) produced 12 text-to-curves files: 8 dark fronts + 2 dark backs in 06_dark_vectorizado_svg/, cream backs 09/10 in 03_final_vectorizado_svg/ (historic pending closed). New gallery 04_preview/preview_flyers_dark.html links editable+vectorized per piece.
- AUTOMATION (2026-07-03, boss request 'revision sin revision'): new CI quality gate .github/workflows/validar-piezas.yml (validates ALL supplement SVGs on every push/PR touching svg/) + docs/AUTOMATIZACION_FLUJO.md (mold analogy + 4-phase roadmap to cloud-only work: enable write access + install Claude GitHub App -> @claude on issues generates pieces via skill entregas-rd -> validated PR -> approve from phone).
- CLOUD LOOP (2026-07-03): .github/workflows/claude.yml added - @claude mention on any issue/PR wakes Claude on a GitHub runner (PC off), loads Vibo identity + skill entregas-rd, opens validated PR. Activation pending (user): install Claude GitHub App (/install-github-app) + ANTHROPIC_API_KEY secret. TODO: custom SMTP email step if native GitHub notifications are not enough.
- VITRINA (2026-07-03, 'piensa en grande'): publicar-catalogo.yml deploys the public catalog to GitHub Pages on every merge to main (cream/dark galleries + quotation as a shareable URL) + proposals/VISION_FABRICA_AUTONOMA.md (5-station autonomous factory + license-flujo horizon). Activate: Settings > Pages > GitHub Actions.
- SECURITY FIX (boss street knowledge): testeo data is prized by dealers and can signal gang presence - NEVER broadcast night data to the crowd. Corrected model in the proposal: data flows VERTICAL only (stand person-to-person, closed channel to production/security/MEDICAL, delayed aggregated observatory); screen keeps presence/mission layer only; public alert only in extreme vital risk, human-decided, never automated.
- ORIGINAL IDEA (Vibo, 2026-07-03): proposals/IDEA_SEMAFORO_RD_TESTEO_VIVO.md - live harm-reduction layer on party screens: anonymous aggregate testeo results rendered as VJ visuals (reagent-color brand palette) via the EXISTING Resolume/Chataigne automator; alert takeover when adulterants detected. New sellable tier + post-event substance report; gives the .noisette blocker a business reason. Pilot spec included.
- LA GOTA v2 (improved): dropper forming the drop, spring-physics water surface, splash+ripples, flow-field ink diffusion (additive), TIME-EVOLVING reaction color, synthesized drip audio, installation/projection mode, and the NIGHT CANVAS (each drop stains a persistent collective artwork, downloadable PNG). State machine driven by rAF timestamp (deterministic, verified frame-by-frame with a synthetic harness). Drops fall on the sides so the panel never hides the bloom.
- LA GOTA (boss idea, 2026-07-03): tools/gota_rd/index.html - abstract web experience of the reagent drop (canvas generative bloom), reagent+color selection or CAMERA color sampling with perceptual match, anonymous local DB + export + ENDPOINT constant for Apps Script. Reaction table is DEMO (flagged on screen) - RD must supply official chart (v4.1 rule). Published by vitrina at /gota/.
- Assistant identity: the repo assistant is now named "Vibo" (user request). Canonical definition in CLAUDE.md (repo root, new file, auto-loaded by Claude Code each session) plus an "Identidad del asistente" section in AGENTS.md. If the user renames it, update both files together. (branch claude/custom-name-preference-543qs0, docs-only)
- Resolume/Chataigne automator (src/flujo/resolume/automator.py) generates XML pre-flight, CSV OSC, README, and an experimental .noisette (v0.48.2 to v0.48.5, 4 rewrites, still unverified against a real file).
- SVG Studio, Plano/Rider, Cotizacion, Jobs, Intake, Commands stable in web/ (React/Vite single-file build into context/*.html).
- Web hub tools list is defined in web/src/components/AppShell.tsx (RD_NAV / STUDIO_NAV) plus a view case in web/src/App.tsx.

Doing (this session, committed locally by auto-checkpoint, push pending):
- Adobe toolkit above (tools/illustrator, tools/photoshop, tools/after_effects, tools/adobe_panel, tools/ADOBE_TOOLKIT.md). Working tree clean; git push pending to origin (https://github.com/ligereza/vibecodeine).
- To verify in the user's Adobe apps (regla de oro): run each .jsx from File > Scripts; confirm image-trace params and the Convert Audio to Keyframes menu name in the user's AE locale.

REPO HYGIENE PASS (2026-07-03, Vibo, uncommitted): audited duplicate tools + stale docs on user request.
- Fixed docs/REPO_MAP.md (was v0.34.10, contradicted AGENTS.md by naming AGENT_OPERATING_MANUAL.md as the agent entry point instead of AGENTS.md): version bumped to v0.48.5, entry-point section corrected. Marked docs/AGENT_GUIDE.md and docs/AGENT_OPERATING_MANUAL.md OBSOLETO at the top (both v0.34-era). Bumped docs/HIGIENE_REPO.md version stamp.
- Removed root-level HANDOFF_2026-07-02_cotizacion_eventos_y_flyers_suplementos.md and HANDOFF_2026-07-02_nombre_asistente_vibo.md: confirmed as older/incomplete duplicates of the same-named files already in docs/handoffs/ (per REPO_MAP.md rule, handoffs belong there, not root).
- Archived 34 orphaned legacy scripts from scripts/ to _archive/legacy_20260703_1413/ via (fixed) scripts/cleanup_legacy_aggressive.sh: flyer_*, ig_*, job_*, most piezas_*/project_*/privacy_*/rider_* wrappers superseded by the `flujo ...` Typer CLI. Verified none referenced by Makefile, .github/workflows/*.yml, tests/, or src/flujo/ before moving. IMPORTANT: the original script list was wrong and would have archived piezas_generar.py + piezas_check_outputs.py (live in .github/workflows/render_piezas_vectoriales.yml) and flyer_create_project.py (live in `make new-flyer`) — those 3 are now excluded and kept in scripts/. compileall + pytest verified green after the move.
REPO HYGIENE PASS ROUND 2 (2026-07-03, Vibo, user said "resuelve todo lo que pueda significar desorden"):
- docs/handoffs/: moved 37 loose top-level files + 3 from the undocumented current/ subfolder into new docs/handoffs/archive/handoffs/ (2026-06-16 to 2026-06-30). Top level of docs/handoffs/ now has only the 3 current-week handoffs + README.md. Both READMEs (docs/handoffs/README.md and archive/README.md) updated to document the convention: root of docs/handoffs/ stays small (<5 files), anything not "this week" moves to archive/handoffs/.
- CLI docs group consolidated: docs/CLI.md rewritten from scratch against the real src/flujo/cli.py (was v0.35.3, missing suplementos/knowledge/eventos/resolume/hub groups, wrongly implied `flujo plano` didn't exist — it does, verified directly, don't trust secondhand claims about missing commands without grepping cli.py yourself). docs/COMANDOS.md and docs/COMANDO_UNIFICADO.md reduced to one-line redirect stubs pointing to CLI.md. docs/INTEGRACION_CLI.md left untouched (verified accurate: hub_app/cli_addons.py architecture doc, genuinely distinct topic, not a duplicate).
- Airdrop docs group consolidated: merged the "que valida validate_airdrop.py" checklist and the real (verified against actual scripts/run_airdrop_checks.py source) runner step order + flags (--resume/--skip-hub-smoke/--skip-checkpoint/--skip-push) into docs/AGENT_AIRDROP_PROTOCOL.md. docs/AIRDROP.md and docs/AIRDROP_REVIEW.md reduced to redirect stubs (AIRDROP_REVIEW.md had a stale/self-contradicting step list mentioning apply_airdrop.sh/checkpoint.sh bash calls that no longer happen). docs/RELEASE_NOTES_AIRDROP.md (one-off historical release note, referenced only the dead scripts/flujo.py wrapper) moved to docs/handoffs/archive/handoffs/.
- Hygiene docs group consolidated: docs/HIGIENE_REPO.md is now the single source (merged in the jobs/20*+projects/piezas_vectoriales/20* git-ignore policy, the intentional-examples whitelist, and scripts/flujo_clean_generated.py + scripts/flujo_health.py usage from the other two). docs/CLEANUP.md and docs/MANTENIMIENTO_REPO.md reduced to redirect stubs. docs/REPO_HYGIENE_ACTION_PLAN_2026-06-30.md verified fully completed (checked: the 3 root files it flags are gone, tags v0.48.0-v0.48.3 exist) and moved to archive with a COMPLETADO note. docs/LIMPIEZA_HISTORIAL.md left untouched (distinct topic: .git history size, not repo hygiene).
- Deliberately NOT touched: gen_plano.py/gen_plano_dark.py and gen_backs.py/gen_dark_backs.py duplication (.claude/skills/entregas-rd/generadores/) — real but low-severity (cosmetic color-palette diffs in one-shot commercial SVG generators for RD supplement flyers), refactoring risks a silent visual regression in a printed deliverable. Needs its own pass with before/after output diffing, not folded into a docs/scripts hygiene sweep. Also not touched: fusing archived flyer_latest.sh+flyer_list.sh (already inert in _archive/, no longer live so no longer "disorder" in the active tree).
- compileall + pytest + flujo health verified green after this round too.

Next:
- git push the Adobe toolkit commits to origin (user said "lo subo") — this hygiene pass is also uncommitted, ask user before pushing.
- Verify the Adobe .jsx in the user's Illustrator/Photoshop/After Effects (batch trace with 2-3 real JPEG; AE Convert Audio to Keyframes locale; optional .zxp via build_zxp.ps1 + ZXPSignCmd).
- Get a real .noisette file exported from the user's Chataigne 1.10.3 and save it as a fixture under tests/ before touching build_chataigne_noisette_experimental again.
- Bring context/SESSION_STATE.json and context/LAST_HANDOFF.md current every session end (see AGENTS.md rule).

Blockers:
- build_chataigne_noisette_experimental has no real .noisette to validate against; do not guess the schema again, ask the user for the exported file.
- GitHub push: this LOCAL session (user LIGEREZA, origin owner) can push; earlier REMOTE cloud sessions were read-only (push 403), so those deliveries were packaged as airdrop ZIP. New design-chat material did NOT reach the repo (origin/main unchanged, no issues after Jun 24) nor Adobe CC storage; ask the user where it lives.
- Pending: real RD WhatsApp number; direct contact info for the quotation doc; QR backs for products 02-07; issue #6 Omega 3 label.
