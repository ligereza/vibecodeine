Date: 2026-07-04
Version: 0.48.5 (matches pyproject.toml / src/flujo/version.py)
Assistant: Cauce (formerly Vibo)

== ESTADO ACTUAL ==
Foco: AI Operating Layer v1 -- dejar el repo listo para trabajo multi-agente API-only
y bajo consumo de contexto. Claude Opus 4.8 como arquitecto/revisor final; Qwen / NVIDIA
NIM / OpenRouter (via Aider) como editores baratos. Repo estable; sin cambios en
src/flujo ni web/ en esta pasada (solo docs + config + tools/contexto_repo.py).

== LISTO ==
- AI Operating Layer v1: docs/AI_OPERATING_LAYER.md, docs/AI_PROVIDER_ROUTING.md,
  docs/AIDER_API_SETUP.md, docs/TASK_PROMPTS.md, .aider.conf.example.yml, .env.example.
  tools/vibo_voz/contexto_repo.py con subcomandos (map / task). Handoff + SESSION_STATE al dia.
- Piezas SVG editables en Illustrator (rama feat/piezas-svg-editables-illustrator, pusheada
  a origin): fuente Arial (Illustrator no tiene DejaVu), logo RD vectorial inline (crisp,
  sin raster roto), titulo centrado, parrafos/items como bloque (tspan). Flyers dark (8+2) +
  brief packs eventos (svg/eventos_rd). Skill nueva taller-svg-rd. Controles de fuente/peso
  Black/alinear-margen en el hub web.
- Prior (detalle en docs/handoffs/ y src/flujo/version.py get_changelog): asistente de voz
  CODE/VIBO/REDU (tools/vibo_voz, seguridad cerrada), Adobe toolkit (tools/), higiene de repo
  2 rondas, linea dark suplementos + vectorizados, cotizacion general eventos, workflows CI/vitrina.

== PENDIENTE ==
- Mergear rama feat/piezas-svg-editables-illustrator a main (por PR):
  https://github.com/ligereza/vibecodeine/pull/new/feat/piezas-svg-editables-illustrator
  El guardrail bloqueo el push directo a main; main sigue en 1a7e551.
- Probar Aider real con los perfiles de .aider.conf.example.yml (Claude+Qwen / NIM / OpenRouter).
- Verificar Adobe .jsx en las apps del usuario (Illustrator/PS/AE).
- Logo RD color vectorial (lo prepara el usuario) -> cambiar variante dark de 'blanco' a 'color'.

== BLOQUEADORES ==
- Cuota: Claude API / plan del usuario casi agotados. Reservar Claude para arquitectura y
  revision final; hacer lo barato con Qwen/NIM/OpenRouter (ver docs/AI_PROVIDER_ROUTING.md).
- build_chataigne_noisette_experimental: sin .noisette real para validar. No adivinar el
  schema de nuevo; pedir el archivo exportado de Chataigne 1.10.3 y guardarlo en tests/.
- Push a main bloqueado por guardrail (requiere PR o autorizacion explicita del usuario).

== PROXIMO PASO RECOMENDADO ==
1. Mergear la rama a main via PR (link arriba).
2. Configurar Aider: copiar .aider.conf.example.yml -> .aider.conf.yml y .env.example -> .env
   (claves reales por env var, nunca en el repo).
3. Delegar con docs/TASK_PROMPTS.md: Qwen mastica contexto -> Claude valida el plan ->
   Aider implementa -> Claude revisa el diff -> cerrar handoff.
