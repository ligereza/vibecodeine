# Cierre de sesión — 2026-09-18

Esto es referencial, no una lista de tareas ni un contrato para el próximo
agente. No hay memoria persistente entre agentes: lo único que vale es lo
que ya quedó escrito en `STATUS.md`, `CAPACIDADES_MAK.md`, `DECISIONES.md`
y el propio código/tests. Este archivo es solo un mapa de dónde mirar,
nada más. Nadie está obligado a seguir ningún orden aquí.

## Qué leer si hace falta contexto

- `STATUS.md` — estado medido, incluye la sección "Integración Azure y
  calibración DeepSeek" y tres hallazgos abiertos al final.
- `CAPACIDADES_MAK.md` — registro VIVO/MUERTO de `tools/`; sección 5 tiene
  las herramientas nuevas de este ciclo con su consumidor real.
- `docs/AZURE_MAK_PLAN_2026_2027.md` — el plan que enmarca todo el trabajo
  con Azure/DeepSeek de este ciclo.
- `DECISIONES.md` — lo que el operador decidió, con fecha. No se tocó en
  este ciclo.

## Aprendizajes de este ciclo (lo no obvio, no lo que ya dice el código)

- **Buscar antes de construir, siempre.** Cada vez que se generó un tool
  nuevo sin buscar primero, ya existía algo mejor (`flujo.privacy.scan_text`
  vs. un filtro de 4 palabras hecho a mano; `LearningStore.promote_rule()`
  vs. reinventar el criterio de promoción).
- **Nunca aceptar un test generado sin ejecutarlo.** De 14 tests delegados
  a DeepSeek con hechos completos, 4 tenían errores reales (redondeo no
  considerado, framework equivocado, aserción falsa sobre dedup
  case-insensitive, mal juicio de un límite de bucle). Ninguno se habría
  detectado leyendo el código generado, solo corriéndolo.
- **Una abstención correcta es evidencia positiva, no una falla.** DeepSeek
  se negó una vez a inventar un caso de test imposible (ningún valor de
  `NAVEGACION` en `mak_vigia.py` cumple los dos umbrales a la vez) — se
  verificó manualmente que la negativa era cierta antes de aceptarla. Eso
  cuenta a favor de la calibración, no en contra.
- **Un ratchet que solo mide no traduce.** `tools/idioma.py` fija un pin,
  nunca corrige. Traducir comentarios de dominio técnico (forense RD, en
  este caso) sin entender el contenido es tan riesgoso como no traducir:
  se hizo a mano, verificando cada archivo con la suite real después.
- **Los archivos fantasma en un registro manual se acumulan solos.** Cinco
  filas de `CAPACIDADES_MAK.md` seguían señalando herramientas ya borradas
  hace tiempo; nadie lo notó hasta que un test explícito (`test_registro_
  sin_herramientas_fantasma`) lo exigió.
- **Confirmar antes de descartar un hallazgo raro.** La cuenta "Azure for
  Students" tiene 4 recursos (`MAKINTOUCH`, `makmak-7457-resource`,
  `makmak-5202-resource`, `maklinux`) que no corresponden a nada de este
  ciclo ni de DeepSeek (que vive en una suscripción y tenant totalmente
  distintos, `issvkk2-resource`). El activity log de Azure (90 días) no
  registra su creación — son más antiguos que cualquier trabajo de agente
  reciente. No se tocaron ni se investigó más allá de confirmar que no son
  míos ni de DeepSeek.

## Qué vale la pena revisar (sin urgencia declarada, cada uno con su hallazgo ya escrito en `STATUS.md`)

- Contrato de lanes desincronizado (`context/test_lane_map.json` no incluye
  `tests/test_portfolio_iris_context_dispatch.py`).
- `cultura/mak_plataforma/tandas.py:AREAS` vs `cultura/mak_plataforma/
  ledger.py:DOMAINS` — dos vocabularios de dominio sin reconciliar.
- `mak/`, `pastillas/`, `.docker/` en `/home/mak` — directorios nuevos sin
  clasificar, sin relación declarada con este ciclo.
- Los 4 recursos de Azure sin origen conocido (arriba). Solo el portal de
  Azure ("Cost Management" de la suscripción) puede decir su costo real y
  quién los creó.
- `tools/release_gate.py` podría sumar el ratchet de idioma y
  `capabilities.py --check` a su propio veredicto de cierre — quedó
  propuesto, no construido.
- Calibración real de DeepSeek: 10 aciertos / 4 fallos / 14 casos,
  accuracy 0.714, en `data/mak_knowledge.db` (`learning_evaluations`,
  `target_kind=azure_delegation_pattern`) y en MLflow
  (`makmak-ml-workspace`, experimento `mak-azure-integration`). Sigue
  siendo un número que crece con cada delegación real, no un veredicto
  final.

## `.py` que se usaron en este ciclo, sin excepción

Creados:
- `tools/raton.py`
- `tools/promover_reglas.py`
- `tools/guarda_subida_externa.py`
- `tools/consultar_mak_search.py`
- `tools/reportar_calibracion_deepseek.py`
- `tests/test_capataz_extraer_json.py`
- `tests/test_cuotas_aplanar_llmcalls.py`
- `tests/test_diagnostico_dirs_generadas.py`
- `tests/test_gen_archivo_iskvw_riqueza.py`
- `tests/test_motor_semantico_distancia.py`
- `tests/test_research_compact_search_query.py`
- `tests/test_triangular_ficha_contenido.py`
- `tests/test_vigia_titulo_util.py`
- `flujo/tests/test_rd_panel_link_helpers.py`
- `flujo/tests/test_venue_geometria_puntos.py`
- `XIO/xio/new-plugins/showcontrol/test_cueengine_validators.py`

Borrados (confirmados sin referencia antes de borrar):
- `tools/build_duplicate_decision_report.py`
- `tools/instalar_enviar_a_mak.py`
- `tools/mak_fuse_roots.py`
- `tools/mak_materialize_fused_root.py`
- `tools/mak_triangulate_roots.py`

Editados:
- `tools/repo_audit.py`
- `cultura/mak_plataforma/tandas.py` (editado y revertido; ver hallazgo AREAS/DOMAINS)
- `cultura/mak_forense/__init__.py`
- `cultura/mak_forense/estructura.py`
- `cultura/mak_forense/forense.py`
- `cultura/mak_forense/fuentes.py`
- `cultura/mak_forense/patrones.py`
- `cultura/mak_forense/registro.py`
- `tests/test_forense.py`
- `tests/test_forense_estructura.py`

Leídos como fuente real antes de delegar o verificar (no editados):
- `cultura/mak_plataforma/capataz.py`
- `cultura/mak_plataforma/cuotas.py`
- `cultura/mak_plataforma/ledger.py`
- `cultura/mak_curatoria/diagnostico_proyectos.py`
- `cultura/mak_curatoria/triangular.py`
- `cultura/mak_codex/motor_semantico/algebra.py`
- `cultura/mak_research/research_lib.py`
- `cultura/mak_vigia/vigia.py`
- `tools/gen_archivo_iskvw.py`
- `flujo/src/flujo/rd/panel.py`
- `flujo/tools/venue_geometria_scd.py`
- `flujo/src/flujo/privacy/scan.py`
- `flujo/src/flujo/knowledge/project_ir.py`
- `XIO/xio/new-plugins/showcontrol/cueengine.py`
- `XIO/xio/new-plugins/showcontrol/test_cueengine.py`

Ejecutados como herramienta de diagnóstico:
- `tools/mak_status.py`
- `tools/capabilities.py`
- `tools/idioma.py`
- `tools/test_lane_map.py`
