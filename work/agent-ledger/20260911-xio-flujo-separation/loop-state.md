run_id: 20260911-xio-flujo-separation
objective: >-
  Separar y terminar FLUJO escritorio, FLUJO móvil, XIO-RD y XIO-FOH sin
  duplicar servidores ni bases: RD recolecta en terreno y FOH escucha/visualiza
  señales; el dispositivo que corre XIO es dueño de la DB offline.
scope: C:\IA\flujo + C:\IA\XIO + runtime Xiaomi ya desplegado
core_acceptance_criteria:
  - FLUJO desktop existente permanece intacto; las adaptaciones móviles son responsive.
  - XIO-RD y XIO-FOH quedan como productos separados, compartiendo listener/host sólo donde corresponde.
  - RD APK conserva captura de foto/silueta, selección de sustancia, tests y resultados, evento por productora/logo.
  - FOH sigue HTML/PWA y su host escucha OSC/Art-Net/timecode; no se convierte en APK.
  - Base de datos del host se visualiza gráficamente: productora -> eventos -> venue/rider/layout pendiente -> evidencia 2025 con porcentajes descriptivos.
  - No se inventan enlaces de productora/venue/evento desde nombres de hojas; se conserva event_id exacto.
  - Xiaomi puede ser host offline; PC puede ser host y Xiaomi cliente visual.
authorized_extensions:
  - Documentar los dos modos de host y la regla de IP dinámica.
status: active

completed:
  - item: XIO-RD/FOH desplegado y separado en runtime Xiaomi; no se confunden APK RD y HTML FOH.
    evidence: XIO tests/runtime smoke previously passed; current XIO branch is clean and pushed.
  - item: Host modes documentados.
    evidence: xio/FACES.md, commit 3041db6f.
  - item: FLUJO Base de datos expone productoras y ficha de eventos/venue.
    evidence: web/src/components/RdDbPanel.tsx, commit 3041db6f.
  - item: Evidencia histórica 2025 se proyecta desde rd.db en modo solo lectura.
    evidence: src/flujo/rd/panel.py; 42 event_id source events; embedded bundle regenerated.
  - item: Adaptación responsive inicial de Base de datos, Plano y Mapping.
    evidence: typecheck/build/build:rd passed before this continuation; commit 3041db6f.
  - item: PWA RD ahora comparte la política de catálogo de la APK.
    evidence: xio/new-plugins/rd_field/static/app.js agrupa por productora, exige
      logo_loaded y conserva el orden del catálogo; static/index.html deja la
      razón visible cuando no hay una productora habilitada.
  - item: FLUJO declara la vista efectiva del navegador sin duplicar la app.
    evidence: web/src/components/AppShell.tsx usa matchMedia para indicar
      celular/escritorio; typecheck y ambos builds pasaron después del cambio.
  - item: Host real comprobado en MAK y Xiaomi.
    evidence: MAK /home/mak/flujo/data/rd.db en sólo lectura tiene 37 tablas y
      42 eventos; Xiaomi mantiene servidor :5000 y rd_field/rd.db local de
      3067904 bytes.
  - item: XIO y el espejo FLUJO sincronizados y publicados.
    evidence: XIO commit 1759038; FLUJO commits f91bd057 y e8d0fe59; bridge,
      PWA y recursos estáticos comparten hash entre ambos equipos y staging
      `/sdcard/xio_termux/new-plugins/rd_field`.

current_state:
  files_or_resources:
    - C:\IA\flujo\src\flujo\rd\panel.py
    - C:\IA\flujo\web\src\components\RdDbPanel.tsx
    - C:\IA\flujo\web\src\components\PlanoTool.tsx
    - C:\IA\flujo\web\src\components\MappingTool.tsx
    - C:\IA\flujo\xio\FACES.md
  tests_and_checks:
    - node --check XIO and FLUJO rd_field/static/app.js: passed
    - py -m compileall XIO rd_field: passed
    - npm run typecheck (web): passed after current changes
    - npm run build (web): passed after current changes
    - npm run build:rd (web): passed after current changes
    - XIO check_xio_rd_bridge.py: passed
    - XIO check_xio_rd_plugin.py: passed
    - XIO field staging against Windows copy: intentional NO-GO; copy lacks
      xio_eventos and xio_signal_events
    - MAK read-only database inspection: passed; no required tables missing
    - py direct datos_panel: 20 productoras, 42 evidence events
  assumptions:
    - Current local rd.db is the existing regenerated evidence projection; no rows are written by the UI.
    - Existing XIO runtime files/tests are authoritative for phone behavior; do not replace MAK dirty worktree wholesale.
  open_questions:
    - The static files were pushed to Xiaomi staging, but the existing Termux
      server copies them into its private runtime only when run_server.sh is
      relaunched. Android RUN_COMMAND from adb is not authorized, so the live
      process still serves the previous static copy until the existing Termux
      launch path is used. No server logout or forced restart was performed.
    - Need one final review of FOH live route and the exact deployed APK/source
      distinction before closing the objective.
  blockers: runtime static reload requires the already-configured Termux path;
    source and staging are ready, but avoid forcing a user-visible phone
    session solely for a static refresh. The server remains healthy and the
    existing bridge is already live; only the new PWA selector awaits reload.
  research_refs: none
  delegation_refs: none
  last_critique: >-
    This milestone closed the previously observed PWA/APK catalogue mismatch and
    added explicit viewport detection. The remaining uncertainty is deployment
    reload, not an unbounded redesign; keep the live server and DB untouched.
  estimated_remaining_effort: low
  next_action: Keep the normal Termux launch path as the only remaining runtime
    action; do not force it from adb. Report host ownership, source/staging
    status, and the exact live-reload limitation.
next_checkpoint_trigger: After the audit and one coherent corrective milestone.

## Checkpoint 2026-09-11 — corrected split and live RD host read

status: active

completed:
  - item: FLUJO-ISKVW has its own reduced entry and FOH section; FLUJO-RD
      remains a separate RD-only entry without ISKVW or Main panels.
    evidence: web/src/mainIskvw.tsx, web/iskvw.html, web/vite.iskvw.config.ts,
      web/src/mainRd.tsx, build:iskvw and build:rd passed.
  - item: XIO routes now distinguish the RD browser hub from the optional
      browser capture surface, and FOH /view serves the ISKVW/FOH hub.
    evidence: xio/new-plugins/rd_field/__init__.py routes /view and /field;
      xio/new-plugins/foh_monitor/__init__.py route /view.
  - item: RD hub reads host bootstrap and exact-event samples when served by
      XIO, while file:// standalone remains embedded and request-free.
    evidence: web/src/components/RdDbPanel.tsx; build:rd passed; live Xiaomi
      bootstrap returned schema xio-flujo-rd-v1, 42 events and samples endpoint
      returned a valid zero-sample result for an exact event_id.
  - item: XIO source and FLUJO mirror target plugin files were synchronized;
      updated RD/FOH hub bundles were staged to Xiaomi without restarting it.
    evidence: hashes match for target plugin source/static files; adb push of
      rd_field/static/hub.html and foh_monitor/static/hub.html succeeded.
  - item: Phone runtime checker no longer rejects a healthy large plugin list
      because of response truncation.
    evidence: tests/check_xio_phone_runtime.py now reads the complete JSON;
      HTTP=PASS against http://10.248.64.39:5000/api/plugins.

files_or_resources:
  - C:\IA\flujo\web\src\components\RdDbPanel.tsx
  - C:\IA\flujo\web\src\components\FohPanel.tsx
  - C:\IA\flujo\web\src\mainIskvw.tsx
  - C:\IA\flujo\web\src\mainRd.tsx
  - C:\IA\XIO\xio\new-plugins\rd_field
  - C:\IA\XIO\xio\new-plugins\foh_monitor
  - Xiaomi /sdcard/xio_termux/new-plugins/{rd_field,foh_monitor}

tests_and_checks:
  - XIO compileall, check_xio_rd_bridge.py, check_xio_rd_plugin.py: PASS
  - FLUJO check_xio_foh_context.py: PASS
  - web typecheck, build, build:rd, build:iskvw: PASS
  - phone runtime: HTTP, listener, DB and files PASS; source sync NO-GO only
      because the existing live Termux process has not been relaunched.

assumptions:
  - The RD hub may show the embedded historical projection plus a live host
      section; this preserves offline standalone use without pretending the
      embedded snapshot is the current Xiaomi DB.
  - No phone restart is necessary to validate source/build correctness and is
      not forced while ADB lacks the configured Termux RUN_COMMAND permission.

blockers:
  - Normal existing Termux launch path is required before the new static hub
      is visible at the live /view routes. Current server and DB remain healthy.

last_critique: >-
  Continuing with a small host-read section had lower total risk than changing
  the standalone RD bundle into a server-dependent build. It satisfies the
  distinction between historical projection and Xiaomi-owned live records;
  the remaining uncertainty is runtime reload, not architecture.
estimated_remaining_effort: low
next_action: Run final targeted diffs/tests, commit only the separation and
  host-read changes in each repository, and push their existing branches;
  preserve unrelated dirty worktree files.
next_checkpoint_trigger: Before each explicit commit/push and after verifying
  the exact staged paths.

## Checkpoint 2026-09-11 — published

status: active
completed:
  - item: Published the corrected XIO separation.
    evidence: XIO commit 11fbf66 pushed to
      origin/codex/obras-experimental-rehearsal-xio-root.
  - item: Published FLUJO reduced hubs, live RD host read, docs and checks.
    evidence: FLUJO commit 1e1edea5 pushed to origin/DIRECTOR.
  - item: Confirmed XIO worktree is clean and FLUJO worktree retains only
      unrelated pre-existing changes outside the published paths.
    evidence: post-push git status review.
  - item: Revalidated the Xiaomi after publication without changing its session.
    evidence: staged hashes for both plugin init files and both hub bundles
      match XIO commit 11fbf66 byte-for-byte; live rd_field/info still reports
      the old shape and rd_field/view is 6214 bytes, while foh_monitor/view is
      still 404. This proves staging is correct and only runtime reload is left.
current_state:
  files_or_resources:
    - XIO source and Xiaomi staging contain both generated hub.html files.
    - FLUJO source can rebuild rd.html and iskvw.html independently.
  tests_and_checks:
    - typecheck, build, build:rd, build:iskvw: PASS
    - XIO RD bridge/plugin and FOH context checks: PASS
    - phone HTTP/listener/files/DB checks: PASS
  assumptions:
    - The normal Termux launch path remains the only safe way to activate the
      staged HTML in the running phone process.
  blockers:
    - Live Xiaomi process has not reloaded staged hub/plugin files; ADB
      RUN_COMMAND is denied and no force-stop/relogin was performed.
  next_action: When the existing Termux launch path is next used, verify /view
    and /info once; no code or database migration is required.
  next_checkpoint_trigger: live Termux launch or user interruption.
