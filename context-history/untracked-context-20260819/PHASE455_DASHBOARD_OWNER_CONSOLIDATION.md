# Phase 455 — Dashboard owner consolidation

## Alcance

Se encontró una duplicación real en el consumidor local del dashboard:
`scripts/flujo_daily.py` contenía su propio scoring/render y coexistía con el
owner canónico `src/flujo/dashboard/{scoring,report}.py`, mientras
`python -m flujo daily` ya usaba el segundo. Esto podía producir dos reportes
distintos para los mismos jobs, flyers y piezas.

## Acción realizada

Se reemplazó el cuerpo duplicado de
`/home/mak/flujo/scripts/flujo_daily.py` por un adaptador de compatibilidad que
delegará siempre a:

```text
python -m flujo daily [--md PATH] [--html PATH]
  -> src/flujo/dashboard/scoring.py
  -> src/flujo/dashboard/report.py
```

Se conservaron las rutas antiguas (`scripts/flujo.py daily`,
`scripts/flujo_pipeline.py`, `scripts/nuevo_pedido.sh` y
`scripts/abrir_dashboard.sh`) sin copiar árboles ni mantener una segunda
implementación. El adaptador añade `src/` al `PYTHONPATH` de su subproceso y
mantiene el código de salida.

La salida canónica se regeneró mediante el nuevo owner en:

- `context/DAILY.md`
- `context/dashboard.html`

## Validación foreground

```text
python scripts/flujo_daily.py                         -> exit 0
python scripts/flujo.py daily                         -> exit 0
py_compile scripts/flujo_daily.py                     -> exit 0
python -m flujo daily --md /tmp/... --html /tmp/...   -> exit 0
```

Los cuatro recorridos produjeron 19 items: 10 alta, 7 media y 2 baja. El
dashboard actual tiene 8,912 bytes, contiene `19 Total items` y fue generado
por el owner canónico. El adapter no contiene funciones `score_*`,
`collect_items` ni `render_html`; esas funciones existen solo bajo
`src/flujo/dashboard/`.

Se intentó ejecutar la suite focalizada:

```text
/home/mak/venvs/flujo/bin/python -m pytest -q tests/test_dashboard.py -> exit 1
No module named pytest
```

No se instaló pytest. La ausencia del runner queda como riesgo documentado,
no como fallo del dashboard; los smoke checks directos pasaron.

## Dictamen

```text
DASHBOARD_CANONICAL_OWNER_UNIFIED
LEGACY_ENTRYPOINT_COMPATIBLE
DASHBOARD_OUTPUT_REGENERATED
DASHBOARD_FOREGROUND_SMOKE_GREEN
PYTEST_RUNNER_UNAVAILABLE
```

## Rollback y riesgos

- El rollback funcional es devolver el adaptador anterior, pero eso
  reintroduciría dos owners; se conserva la evidencia en el handoff y no se
  recupera la duplicación salvo decisión explícita.
- `context/DAILY.md` y `context/dashboard.html` son salidas generadas; deben
  regenerarse con `python -m flujo daily`, nunca editarse a mano.
- No se tocaron jobs, manifests, configs de piezas, base RD, HTML de otras
  áreas ni evidencia histórica.

## Siguiente acción

Continuar el auditoría HTML desde `/home/mak/*` con la siguiente superficie
no cubierta, manteniendo el dashboard bajo un único owner y dejando pytest
pendiente de un entorno que lo contenga.
