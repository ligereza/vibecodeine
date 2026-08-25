# C04 — resultado de observación de medio y fuerza de evidencia

**Estado:** completado como experimento aislado
**Fecha:** 2026-08-25
**Gate:** PASS

## Dato real observado

Se observó únicamente el archivo declarado por `ARICA.aep`:

```text
/home/mak/curatoria_inbox/ARICA/tottem_ojo.mp4
SHA-256: b7253320e7a23917439dd6ad2fa084a68510469517b76b6428c54f9856ca0776
bytes: 12092541
```

`ffprobe` terminó con `EXIT 0`. La observación técnica fue:

- contenedor QuickTime/MOV;
- video H.264, 1070 frames, `256×1536`;
- audio AAC estéreo;
- stream data adicional;
- duración de video `44.627917 s`.

La dimensión `256×1536` se conservó literalmente. No se reescaló ni se
comparó contra un formato convencional.

## Integración real

[`materialize_real_evidence.py`](materialize_real_evidence.py) conectó la
declaración `C:\ARICA\tottem_ojo.mp4` observada en C02 con la observación real
del MP4 y ejecutó el evaluador, sin escanear la carpeta.

Resultado en [`real_evidence.json`](real_evidence.json):

```text
native_declaration: observed
local_media:       observed
uses:              supported
dimensions:        observed {width: 256, height: 1536}
output_role:       unknown
generated/RENDERS_TO relations: 0
```

La conclusión exacta es: el `.aep` referencia un archivo existente cuyo estado
técnico fue observado. No se probó que el `.aep` lo haya generado, exportado o
aprobado como obra final.

## Evaluación adversarial

El segundo endpoint evaluó seis casos y 13 claims separados:

- declaración + existencia → `uses=supported`;
- existencia sin declaración → `uses=unknown`;
- basename ambiguo → `candidate`;
- metadata técnica igual pero hash contradictorio → `contradicted`;
- evento de export explícito con refs → permite `generated`/`RENDERS_TO`;
- dimensiones no convencionales → `observed`, sin normalización.

El benchmark obtuvo `0` falsos positivos en sus claims evaluados. Es un
benchmark de contrato sintético, no una tasa estadística sobre archivos
artísticos. Sin evento de exportación, el evaluador no emite relaciones de
salida; incluso la coexistencia exacta de `.aep` y MP4 queda limitada a
`uses`.

## Evidencia reproducible

```text
PYTHONPATH=. .venv/bin/python experiments/cycles/C04/verify_cycle.py
EXIT 0 — 20 pruebas, hashes de AEP/MP4, observación real y reportes pasan

PYTHONPATH=. .venv/bin/python experiments/cycles/C04/evidence_evaluator/run_evaluator.py --compact
EXIT 0 — 6 casos, 13 claims, 0 falsos positivos

PYTHONPATH=. .venv/bin/python experiments/cycles/C04/media_observer/runner.py \
  /home/mak/curatoria_inbox/ARICA/tottem_ojo.mp4
EXIT 0 — hash antes/después idéntico, ffprobe 0

git diff --check
EXIT 0
```

## Conclusión arquitectónica

C04 confirma que observar el producto sigue siendo necesario, pero cumple una
función distinta a la de descubrir su historia:

```text
metadata/hash del producto -> identidad y estado técnico del artefacto
declaración nativa          -> referencia/uso
evento de exportación      -> única evidencia adicional para output
```

El producto no es el único extremo de análisis y el `.blend`/`.aep` no son el
producto. El sistema necesita ambos, unidos por evidencia tipada y con la
causalidad ausente representada como `unknown`.

## Límites y siguiente paso

No se abrió After Effects, no se escribió el MP4, no se renderizó, no se
transcodificó, no se usó GPU y no se modificaron router, `active_policy` ni
producción. El siguiente experimento seguro debe buscar un witness de actividad
real —logs, metadata nativa o export declarado por una herramienta— sin
renderizar ni mutar archivos artísticos. Si no existe ese witness, la relación
de output debe permanecer desconocida.
