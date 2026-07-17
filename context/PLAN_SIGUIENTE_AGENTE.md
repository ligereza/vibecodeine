# PENDIENTES + FUERTE/DEBIL -- checkpoint limpieza (Cauce, 2026-07-16)

Estado del repo: v0.52.0, suite VERDE 2026-07-16 (450+ tests, compileall OK,
flujo verify OK). main con PRs #45-#47 y #50-#55 mergeados (checkpoint +
MASTER_PLAN + olas 1-3 + noisette real). ABIERTOS #48 (MAK grafo+canvas) y
#49 (MAPA_GENERATIVO), esperan review del usuario -- OTRO Claude trabaja en
MAK: no tocar cultura/, el worktree mak-research-cultural ni esos PRs.
Plan largo y doctrina: context/MASTER_PLAN.md.

## Reglas que NO se negocian (leer antes de tocar nada)
- NO activar Claude via API en GitHub Actions (decision del usuario, 2026-07-12).
- `puente/` es TEORICO (ver `puente/README.md`). No se ejecuta, no se limpia.
- `README.md` del repo es obra terminada del artista: no se le agrega nada.
- Limites cultura: descriptivo si; nada generativo de sintesis; psicosis no
  perfila personas reales; precursor solo cultura/ley/estetica.
- `.noisette`: NUNCA especular sobre el schema. La fuente de verdad es la
  fixture real (tests/fixtures/chataigne_1103_real*.noisette) y su suite
  tests/test_noisette_real_fixture.py debe quedar verde en todo cambio.
- Nunca commitear secretos (`.env`, `config.json`, `*.key`, `cultura/.dev*`).
- `CLAUDE.md` y `context/*.md`: ASCII-only.

## FUERTE (verificado 2026-07-16)
- Suite y CI: 394 tests verdes, compileall OK, flujo verify OK; CI real en
  `.github/workflows/ci.yml`.
- xio on-device: server Termux+Shizuku VIVO en el telefono (23+ plugins),
  showcontrol OSC/Art-Net/sACN desplegado, charge-control no-root, self-heal
  de hotspot; MAK aislado del xio via 403.
- MAK (caja Linux): organismo de research funcionando (4 APIs gratis + LLM
  local); su codigo llega a main via PRs #48/#49.
- Portfolio publico LIVE (ligereza.github.io/portfolio-auto), 8 obras reales,
  sin Claude API, workflow con PORTFOLIO_TOKEN corriendo solo.
- RD entregables: pipeline contraportadas/flyers/cotizaciones validado
  end-to-end + hardening de auditoria (39 hallazgos aplicados 2026-07-13/15).
- Higiene: 0 __pycache__/.pytest_cache, 0 ramas muertas, unico worktree = MAK
  (PR #48), ~190M de basura/duplicados removidos en este checkpoint.

## DEBIL (con evidencia)
- [RESUELTO 2026-07-16, PR #51] Sellos de docs: CLI.md, AIRDROP_PROTOCOL.md y
  SCRIPTS_INVENTORY.md re-verificados comando por comando contra v0.52.0.
- Branch protection en main: AUSENTE (gh api 404, verificado 2026-07-13).
  Accion del usuario en la web de GitHub (require CI verde).
- [RESUELTO 2026-07-16, PR #55 + validacion en vivo] resolume automator:
  fixture real en tests/fixtures/, 9 tests estructurales verdes, y el
  .noisette generado desde jobs/test_resolume CARGA en el Chataigne 1.10.3
  real (titulo de ventana con la sesion, registrado en recentFiles) y corre
  estable en modo -headless -f <ruta absoluta> (30s sin crash, cierre
  limpio). Nota honesta: falta solo inspeccion visual humana del State
  Machine con las 12 acciones (1 min del usuario cuando quiera).
- Gemini PARKED sin reemplazo cableado: desktop/ y tools/vibo_voz quedan
  documentados pero sin uso; el intake /go (vibo_voz/proyectos/) nunca se uso.
- [CORREGIDO 2026-07-16, PR #51] projects/tilde: el render YA existia
  (sobrevivencia.py cumplia el SPEC; status stale). Tests nuevos contra el
  instrumento real. Sigue pendiente el corpus real (P2.6).
- xio reboot gap: xio/hotspot_boot_service (AccessibilityService) necesita
  build/install/grant DEL USUARIO en el telefono; sin eso un reboot mata el
  server hasta intervencion manual.
- Peso del repo: svg/suplementos_rd trackea ~51M de SVG que se regeneran;
  .git ya pesa 36M y crece con cada regeneracion. Vigilar antes de agregar
  mas binarios/vectoriales pesados a git.
- SEGURIDAD local: cultura/.dev.limpio tiene keys vivas duplicadas en disco
  (ya cubierto por .gitignore cultura/.dev*, no puede commitearse). Borrarlo.

## PENDIENTES priorizados
P1 (mecanico, ya):
1. Usuario: revisar y mergear PR #48 y #49 (CI verde requerido).
2. Usuario: borrar el duplicado de credenciales: `rm cultura/.dev.limpio`
3. Usuario: mover leftovers de cultura/ (copias ya guardadas en historia git;
   el clasificador de permisos bloqueo esta movida a los agentes):
   `cd cultura && mv BLENDER.trilogy_450frames.py blend-math-lab.html research_agent_documentacion.md research_agent_free_apis.json research_agent_free_apis.md research_agent_mistral_nemo.json trilogia.3d.blender.html xio-concept.html /c/IA/_flujo_local/cultura_leftovers/`
   (cultura/xiotech.md SE QUEDA: contenido unico, ya commiteado en este
   checkpoint).
P2 (deuda tecnica con criterio):
4. Branch protection en main (web GitHub; no necesita API ni Claude).
5. Re-verificar sellos de docs/CLI.md + AGENT_AIRDROP_PROTOCOL.md +
   SCRIPTS_INVENTORY) contra v0.52.0.
6. Corpus tilde real (desktop/tilde_meter.py) para el render sobrevivencia-01.
7. Fixture de flyer real en tests/fixtures/ para smoke de productoras.py
   (pedir un .jpg/.png al usuario).
P3 (piezas nuevas del MANIFIESTO; motor-omega OBLIGATORIO, semilla + Omega11):
8. Candidatas self-contained: #4 esteganografia (changelog en canal ilegible
   de los SVG), #8 cartografia de filtros (descriptivo, no cruza bloqueos),
   #6 cron nocturno con borrado semanal. Bloqueadas: #2 (falta 2do modelo),
   #5 (hardware ESP32), #7 (orden del usuario: no tocar), #11 (infra training).
9. gota_rd backend: decidir donde vive la data de reactivos antes de servir
   endpoint real.
10. SPEC-only stubs (tools/asistente_pedido, tools/canva_data,
    tools/privacidad_datos, tools/slowmo_blender_ae): pedir alcance al usuario
    o archivarlos en el proximo checkpoint.

## Verificacion (siempre, antes de cerrar)
```
py -m compileall src/flujo
py -m pytest tests/ -q
py -m flujo verify
# si tocas web:
cd web && npm run typecheck && npm run build:context && cd ..
```

## Entrada rapida para el que llega
1. `context/LAST_HANDOFF.md` (estado corto de la ultima sesion).
2. Este plan (pendientes + fuerte/debil).
3. Contexto de una tarea: `py tools/vibo_voz/contexto_repo.py task "<keywords>"`.
4. `puente/README.md` aclara que puente es teorico (no confundir con codigo).
