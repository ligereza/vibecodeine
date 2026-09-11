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
  - item: Audited and rebuilt the native XIO-RD APK as the active measuring
      device, separate from both browser hubs and FOH.
    evidence: XIO/projects/rd-field/android source uses CAMERA/INTERNET,
      local RdFieldDb/PhotoStore, exact host bootstrap event selection and
      /api/plugins/rd_field/sync; Gradle testDebugUnitTest and assembleDebug
      completed successfully; APK output is app/build/outputs/apk/debug/
      app-debug.apk (7,564,079 bytes).
current_state:
  files_or_resources:
    - XIO source and Xiaomi staging contain both generated hub.html files.
    - FLUJO source can rebuild rd.html and iskvw.html independently.
  tests_and_checks:
   - typecheck, build, build:rd, build:iskvw: PASS
   - XIO RD bridge/plugin and FOH context checks: PASS
   - phone HTTP/listener/files/DB checks: PASS
    - XIO-RD Android Gradle unit tests and debug assembly: PASS
  assumptions:
    - The normal Termux launch path remains the only safe way to activate the
      staged HTML in the running phone process.
  blockers:
    - Live Xiaomi process has not reloaded staged hub/plugin files; ADB
      RUN_COMMAND is denied and no force-stop/relogin was performed.
  next_action: When the existing Termux launch path is next used, verify /view
    and /info once; no code or database migration is required.
  next_checkpoint_trigger: live Termux launch or user interruption.

## Checkpoint 2026-09-11 — reload audit

status: active
completed:
  - item: Audited the existing XIO relaunch and selective reload paths.
    evidence: run_server.sh copies /sdcard/xio_termux/new and
      /sdcard/xio_termux/new-plugins into private $HOME paths before starting;
      the generic HTTP plugin reload would therefore reload the old private
      copy in the current process, not the staged files. ADB cannot read the
      process environment due Android /proc permission denial.
current_state:
  files_or_resources:
    - Staged source remains hash-identical to XIO commit 11fbf66.
    - Live server remains healthy on port 5000 with durable RD DB present.
tests_and_checks:
  - No reload request sent; no force-stop, logout, login, or DB mutation.
blockers:
  - Activating staged files requires the existing normal Termux launch path.
next_action: Wait for that normal launch or a user-visible external state change;
  then verify the four route surfaces and hashes.
next_checkpoint_trigger: Termux launch or user interruption.

## Checkpoint 2026-09-11 — verified wait

status: active
completed:
  - item: Polled the live Xiaomi host again using its current wlan1 address.
    evidence: server and RD DB remain healthy; rd_field/info is the old
      response without hub_surface_present; rd_field/view has no RD hub marker;
      foh_monitor/view remains HTTP 404.
current_state:
  - No external reload occurred. Staged files and published commits remain
    unchanged; no further source mutation is justified until Termux launches.
next_action: Stop active changes and resume verification only after the
  existing Termux launch path changes the live process.
next_checkpoint_trigger: live route change or user interruption.

## Completion audit — 2026-09-11

status: blocked
requirements:
  - requirement: Native RD APK measures locally and syncs exact host events.
    result: proved; Android source and Gradle unit/build checks pass.
  - requirement: FLUJO-RD is RD-only and has responsive graphical database
      fichas plus descriptive result distributions.
    result: proved by isolated rd build and bundle marker checks; live host
      section uses bootstrap/samples without inventing event links.
  - requirement: FLUJO-ISKVW is separate and includes FOH/VJ tools.
    result: proved by isolated iskvw build and marker checks.
  - requirement: XIO-RD and XIO-FOH serve those surfaces offline on port 5000.
    result: source and staged files proved; live runtime not proved because it
      still serves the pre-staging process.
  - requirement: No session/logout/DB destruction and no whole-repo copy to
      Xiaomi.
    result: proved by command history, staging hashes and clean XIO worktree.
blocker:
  - The existing Termux process must be launched through its normal path to
      copy staged files into private runtime. ADB RUN_COMMAND is denied; a
      force-stop, UI injection, logout or relaunch was not authorized/safe.
evidence:
  - Final phone probe: DB/listener/files/HTTP PASS, source sync NO-GO for
      stale server.py; rd_field/info lacks hub_surface_present and
      foh_monitor/view is HTTP 404.
stop_reason: No safe productive source action remains until the external
  Termux runtime state changes; goal remains resumable, not complete.

## Completion audit — 2026-09-11, runtime activated

status: complete
completed:
  - item: Relaunched the existing Termux server path without logout or Azure
      session changes.
    evidence: new python server process observed; no installation or DB reset.
  - item: Activated both XIO browser hubs and preserved RD capture separately.
    evidence: live Xiaomi HTTP 200 for rd_field/view, rd_field/field and
      foh_monitor/view; RD view 603222 bytes with Base de datos RD marker; FOH
      view 416194 bytes with Monitor FOH marker.
  - item: Verified host data and exact event wiring in the active runtime.
    evidence: rd_field/info reports hub_surface_present=true and
      field_surface_present=true; bootstrap returns 42 events; samples returns
      the requested exact eventRef; manifests expose /view, /field and FOH
      /view.
  - item: Completed source/build/runtime validation and published verifier fix.
    evidence: phone runtime, dynamic host, RD plugin and FOH context checks
      PASS; web typecheck/build:rd/build:iskvw PASS; XIO Android Gradle tests
      and assembleDebug PASS; FLUJO commit 9ef5b2b7 pushed.
remaining: the user has explicitly reopened the objective with the following
  core additions: create/build/install a native XIO-FOH APK with its own menu;
  make it the active signal listener rather than treating foh_monitor HTML as
  a substitute; finish automated graphical RD event fichas and explicit
  event-to-rider/venue links; and verify the physical/runtime paths.

## Reopened objective — 2026-09-11

status: active
requirements:
  - Native XIO-FOH APK exists as a separate Android package and has its own menu.
  - XIO-FOH can actively listen to OSC, Art-Net, sACN and timecode locally,
    persist an offline FOH log, and expose the host ISKVW hub for viewers.
  - FLUJO-ISKVW remains the visualization/tool hub and does not become RD.
  - FLUJO-RD produces graphical producer/event fichas with automated host
    result summaries, and links event -> venue -> rider/layout explicitly.
  - RAIDER is part of the RD workflow, not only an APK shortcut.
  - Both APKs and their required buttons/navigation are verified on Xiaomi.
verification_required:
  - Gradle unit/build checks for the new FOH project.
  - ADB install/package evidence for the second APK without removing RD.
  - Physical UI navigation evidence for RD and FOH.
  - Real UDP loopback probes for OSC, Art-Net, sACN and timecode.
  - Offline persistence/reload and browser view of the resulting FOH log.
  - RD fixture/event graph and explicit rider-link behavior.
current_state:
  - XIO-RD APK exists and is built; no FOH Android project/package exists yet.
  - XIO foh_monitor is a Python/server listener plus HTML hub, useful as the
    protocol reference but not a replacement for the requested APK.
  - RD graphical panel and RAIDER route exist, but automatic event/rider
    linking is partial and not yet proven end-to-end.
  - XIO and FLUJO worktrees were inspected; unrelated FLUJO dirty files remain
    preserved and must not be swept into targeted commits.
last_critique: >-
  The previous completion claim used server routes and source/build evidence as
  a proxy for the stronger user requirement of a second active APK and physical
  verification. That proxy is invalid. Direct implementation of an independent
  FOH APK has lower total risk than further polishing the HTML first; the APK
  can reuse the proven UDP contracts and link to the existing hub.
selected_action: change_method
next_action: scaffold a separate FOH Android project from the proven Gradle
  baseline, implement the active listener and menu, then build before any
  device install.
next_checkpoint_trigger: FOH project compiles or a build blocker repeats.

## Checkpoint — densidad de fichas corregida 2026-09-11

status: active
completed:
  - item: Detectada y corregida la expansión vertical innecesaria de fichas RD.
    evidence: `RdDbPanel.tsx` usa micrográficos por evento y chips flexibles;
      no se añadieron filas a la base de datos.
  - item: La proyección RD expone claves estables y estados separados para
      venue, rider y layout, sin inventar enlaces.
    evidence: `src/flujo/rd/panel.py` `_wire_event_links` y build pendiente.
current_state:
  - FOH APK compila, pero su instalación en Xiaomi fue rechazada por
    `INSTALL_FAILED_USER_RESTRICTED`; APK está staged en Download esperando
    autorización visible del dispositivo.
  - XIO plugin mirror incluye modo `app_proxy` y `/ingest`.
  - RD UI acaba de compactarse; aún falta verificar build y, después, la
    automatización efectiva de rider/layout.
last_critique: La densidad visual era una regresión aunque la información fuese
  correcta; conservar gráficos pero cambiar a microvisualización minimiza
  espacio y mantiene el requisito de fichas gráficas.
next_action: Ejecutar typecheck/build:rd, luego implementar el enlace/acción
  explícita de rider/layout usando los consumidores existentes de `flujo.plano`
  sin crear una tabla paralela.
next_checkpoint_trigger: build RD pasa o se detecta una incompatibilidad de
  datos en los nuevos campos.

## Checkpoint — ruido de datos corregido 2026-09-11

status: active
completed:
  - item: La proyección RD omite `rider_ref`/`layout_ref` vacíos.
    evidence: `datos_panel` read-only: 7 eventos, 0 refs vacíos emitidos.
  - item: Las fichas no repiten placeholders vacíos; muestran micrográficos
      compactos y un contador agregado de enlaces faltantes.
    evidence: `RdDbPanel.tsx`; typecheck y `build:rd` PASS; bundle regenerado
      y sincronizado con XIO/FLUJO mirror.
current_state:
  - FOH APK build PASS; package `cl.xio.foh` staged on Xiaomi but install is
    blocked by device policy `INSTALL_FAILED_USER_RESTRICTED`.
  - XIO/FLUJO foh_monitor source mirror includes `app_proxy` and `/ingest`.
  - RD event links are deterministic and safe but rider/layout generation is
    not yet wired to the existing `flujo.plano` consumer.
next_action: Implement one reversible RD action/endpoint that consumes the
  existing plano renderer for an exact event record, without making a second
  DB or guessing absent venue/rider data; then add its UI action compactly.
next_checkpoint_trigger: endpoint/consumer test or a confirmed missing source
  parameter that must remain review-pending.

## Revisión de espacios vacíos y consumidor Plano-Rider — 2026-09-11

status: active
completed:
  - item: La proyección de enlaces ya no serializa `ref: ""`, `id: null` ni
      nombres vacíos; sólo conserva valores fuente o estados verificables.
    evidence: datos_panel inspeccionado: siete eventos, cero valores vacíos y
      cero claves `ref` sin contenido.
  - item: La ficha de productora dejó de ocupar una tarjeta completa con un
      placeholder de venue no calculado; ahora muestra sólo el resumen de
      venues que existe y un conteo real cuando corresponde.
    evidence: `RdDbPanel.tsx`, typecheck y build:rd PASS.
  - item: El event_key exacto ahora consume el motor existente `flujo.plano`
      mediante `/api/rd-db/event-link`, sin tabla paralela ni escritura.
    evidence: `tests/test_rd_event_links.py`: pendiente exacto cuando faltan
      parámetros y render listo con un draft explícito; ambos PASS.
  - item: El runtime de Termux fue relanzado por la ruta normal, sin logout ni
      cambios de cuenta, y quedó en modo `app_proxy` para que la APK sea dueña
      de la escucha.
    evidence: Xiaomi `foh_monitor/status`: `listener_mode=app_proxy`, canales
      con mensaje `listener delegado a XIO-FOH APK`, IP actual `10.129.201.10`.
current_state:
  - FOH APK compilada y staged en `/sdcard/Download/xio-foh-debug.apk`; la
    instalación automática fue bloqueada por `INSTALL_FAILED_USER_RESTRICTED`.
      Falta la aprobación visible de Android para obtener evidencia física.
  - XIO responde por la IP dinámica actual; no se conserva la IP histórica
      `10.248.64.39` como configuración fija.
  - `foh_monitor` y el contrato APK pasan sus pruebas estáticas/dinámicas;
      los probes reales de UDP y navegación física dependen de instalar la APK.
next_action: Obtener aprobación visible de instalación en Xiaomi, abrir
  `cl.xio.foh`, probar navegación, persistencia offline y cuatro entradas UDP;
  después ejecutar probes de visualización y sincronización al host.
next_checkpoint_trigger: package `cl.xio.foh` aparece instalado o la política
  Android vuelve a rechazar la instalación con una causa nueva.
