# Archivo 2026-07-17 14:00 -- SPEC-stubs de tools/ (usar-o-archivar, T-F3)

Movidos via git mv (historial en git log --follow). Eran directorios con SOLO
un SPEC.md, cero implementacion, sin tocar en 16+ dias. Decision usar-o-archivar
del MASTER_PLAN (T-F3): sin alcance del usuario -> archivar.

- `asistente_pedido/`  -- SPEC "diseno desde cero", nunca implementado.
- `canva_data/`        -- SPEC "diseno desde cero", nunca implementado.
- `privacidad_datos/`  -- SPEC solo.
- `slowmo_blender_ae/` -- SPEC solo.
- `resolume_chataigne_automator/` -- SPEC doc-stub; el automator REAL vive en
  `src/flujo/resolume/automator.py` (validado contra fixture .noisette real,
  2026-07-16), este doc era redundante.

Revivir: `git mv` de vuelta y cablear. La idea/spec no se pierde, esta aca.
