# C03 — resultado de entrada pública y puente ciego

**Estado:** completado como experimento aislado
**Fecha:** 2026-08-25
**Gate:** PASS

## Evidencia real del supuesto export

Se inspeccionó sólo el directorio de un ZIP local, sin extraerlo ni ejecutar
HTML:

```text
/media/mak/PortableSSD/descargas hasta RDFLYER 2050/instagram-iskvw-2025-04-08-jyAjQO7Z.zip
SHA-256: ce12e0bb043989d4397578b705fab221793db661a818ef33e824babf5cf73d50
```

Tiene 9 archivos reales dentro del ZIP (12 entradas contando directorios):
`start_here.html`, relaciones de followers/following y
`files/Instagram-Logo.png`. No contiene posts, reels, stories ni medios de
publicación. El resultado reproducible es `catalog_status=unavailable` y
`public_join=unknown`; el logo no se trata como publicación.

La auditoría está en [`real_input_status.json`](real_input_status.json) y se
ejecuta con [`real_input_audit.py`](real_input_audit.py). No se modificó el ZIP.

## Trabajo implementado

### Entrada pública

[`experiments/cycles/C03/public_input/public_normalizer.py`](public_input/public_normalizer.py)
acepta únicamente formas declaradas: canónica, JSON envuelto y HTML que
contenga exactamente un `application/json`. Exige `archive_id`, conserva
`post`/`reel`/`story`, media, origen, evidencias, hashes y completitud; falla
cerrado cuando faltan campos indispensables o el formato es desconocido.
`--catalog-unavailable` representa la ausencia real sin fabricar records.

No produce joins, autoría, `generated` ni `RENDERS_TO`.

### Puente ciego

[`experiments/cycles/C03/blind_bridge/bridge.py`](blind_bridge/bridge.py) recibe únicamente
observaciones normalizadas. La verdad está separada en `experiments/cycles/C03/blind_bridge/fixtures/truth.json`
y se carga después de ejecutar ambos resolvers; el resolver no puede leerla.
Los casos incluyen hash exacto, reencode, decoy técnico, publicación sin local,
ambigüedad, conflicto nativo y local sin publicación.

## Evidencia reproducible

```text
PYTHONPATH=. .venv/bin/python experiments/cycles/C03/verify_cycle.py
EXIT 0 — 18 pruebas, auditoría real, reportes y restricciones del bridge pasan

PYTHONPATH=. .venv/bin/python experiments/cycles/C03/blind_bridge/runner.py
EXIT 0 — benchmark ciego ejecutado

PYTHONPATH=. .venv/bin/python experiments/cycles/C03/blind_bridge/runner.py --catalog-absent
EXIT 0 — ambos caminos devuelven unknown sin candidatos

git diff --check
EXIT 0
```

## Resultado del benchmark ciego

| estrategia | TP | FP | abstenciones | contradict | cobertura linkable |
|---|---:|---:|---:|---:|---:|
| baseline directo | 2 | 2 | 2 | 0 | 0.6667 |
| puente mediado conservador | 3 | 0 | 3 | 1 | 1.0000 |

La mejora no es “inteligencia” estadística: el baseline escoge
deliberadamente el primer candidato técnico, mientras que el puente puede
usar una `bridge_observation_key` nativa explícita y respeta un conflicto.
Eso demuestra que la composición de evidencia puede reducir falsos enlaces en
el contrato; no demuestra que dicha clave pueda extraerse todavía de un
Instagram real, ni que el vínculo causal esté probado.

## Conclusión arquitectónica

C03 separa tres estados que antes podían confundirse:

```text
no hay catálogo público -> unknown
hay catálogo pero sólo similitud -> candidate / abstención
hay evidencia nativa compatible y explícita -> confirmed en el benchmark
```

El primer caso es el real de ARICA. Por eso todavía no existe una
reconciliación pública de ARICA ni un portafolio reconstruido. C02 aporta
observaciones nativas reales; C03 deja listo el contrato para consumir un
export real sin reescribir el puente.

## Límites y siguiente paso

Los fixtures del puente son sintéticos y están separados de la entrada del
resolver. No prueban OCR, lectura de un export social real, equivalencia
visual, causalidad temporal ni intención artística. No se entrenaron modelos,
no se usó GPU y no se modificaron router, `active_policy` ni producción.

El siguiente ciclo debe tomar un export público real del artista y sustituir
únicamente la observación pública normalizada. Si faltan campos o el medio no
puede verificarse, el resultado correcto sigue siendo `unknown` o
`candidate`, no una inferencia por nombre.
