# C05 — resultado del witness real de exportación

**Estado:** PASS — 2026-08-25

## Gate

```text
PYTHONPATH=. .venv/bin/python experiments/cycles/C05/verify_cycle.py
EXIT 0
tests_exit_code=0
source_unchanged=true
witness_status=supported
check_count=7
```

El gate observó, sin abrir Blender ni ejecutar el script, el flujo real:

```text
ARICA/RAYU.blend
  -> ARICA/rayu_export.py
  -> ARICA/rayu_export_done.txt + ARICA/rayu_resources.glb
```

## Evidencia física correlacionada

- `RAYU.blend` SHA-256:
  `acafc1db0088016139921b1ea2c9d7a5310247658117fa7021662e13e907ce86`.
- El snapshot nativo C02 contiene `Recurso 2` y `Recurso 3`.
- `rayu_export.py` selecciona exactamente esos dos objetos y declara
  `C:\\ARICA\\rayu_resources.glb` como destino.
- El marcador real dice `OK exported=['Recurso 2', 'Recurso 3']` y apunta al
  mismo basename.
- El GLB observado es glTF 2.0 generado por Blender 4.5.49; contiene como
  nodos y meshes `Recurso 2` y `Recurso 3`.
- El orden de filesystem observado es consistente: fuente el 3 de julio;
  script el 4 de julio a las 02:50:13; salida y marcador a las 02:50:16
  (zona horaria del archivo: `-0400`).
- `rayu_resources.glb` SHA-256:
  `dfa70c3248a739959e8366dbc0eb4382ce17f97592114e51fb6bbb67ae565042`;
  `1,537,592` bytes.

Los siete checks pasaron: hash fuente/snapshot, acuerdo script/marcador,
destino, objetos en fuente, objetos en GLB, formato/generador y orden temporal.

## Conclusión acotada

Este es el primer witness real que permite elevar la relación a
`export_event=supported` / `EXPORTS_TO=supported` para el artefacto GLB
concreto. No prueba que sea la entrega final, que tenga intención artística,
que el autor sea quien ejecutó el script ni que no haya sido modificado
después. C05 no promueve por sí solo `final_deliverable`, autoría ni calidad
visual.

La conclusión arquitectónica es útil: el punto de unión no debe ser solamente
el producto ni solamente el `.blend`; es una cadena de evidencia que combina
estado nativo, acción declarada, testigo de éxito, artefacto y metadatos
internos. Cuando falta cualquiera de esos enlaces, el resultado debe volver a
`unknown`.
