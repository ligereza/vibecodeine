# C02 — endpoint nativo After Effects / LUNA B

## Resultado

Se leyó exclusivamente `/home/mak/curatoria_inbox/ARICA/ARICA.aep` mediante la
API existente `flujo.substrate.aepfile.read_references`, más un hash SHA-256
acotado dentro de este adaptador aislado. No se abrió After Effects, no se
escribió el `.aep`, no se solicitó render y no se recorrió recursivamente
`ARICA`.

El hash observado coincide con el esperado:

```text
99247d6506c6d1d9ce3023f4a1e044da47c806e3cd606d47b61e70fb32f5c460
```

La API observó un contenedor `Egg!`, 30 chunks, sin truncamiento, con
completitud `exhaustive` y cinco declaraciones `fullpath`: cuatro archivos y
la carpeta `C:\ARICA`.

## Regla de resolución local

Cada declaración se conserva como `observation_status=observed`. La resolución
local sólo hace una comprobación directa de la ruta explícitamente mapeada por
basename, o de una lista de candidatos que el llamador ya entregó. Registra
`exists`, `is_file`, `is_dir`, basename y cardinalidad. No usa `glob`, no
enumera el directorio y no busca coincidencias por proximidad.

Existencia + basename produce sólo `classification=candidate`. Una cardinalidad
mayor que uno produce `status=ambiguous`; ausencia de evidencia produce
`classification=unknown` con causa `MISSING_EVIDENCE`. En todos los casos,
`output_claim.status=unknown`: una referencia existente, una extensión o una
carpeta no prueban que el objeto sea output. Este endpoint no emite relaciones
`generated` ni `RENDERS_TO`.

En la observación real, las cinco declaraciones tienen candidato local único:

| declaración | evidencia local | clasificación | afirmación de output |
|---|---|---|---|
| `512 CIELO.png` | existe, archivo, basename coincide | candidate | unknown |
| `BANNER.png` | existe, archivo, basename coincide | candidate | unknown |
| `CENTRAL.png` | existe, archivo, basename coincide | candidate | unknown |
| `tottem_ojo.mp4` | existe, archivo, basename coincide | candidate | unknown |
| `C:\ARICA` | existe, carpeta, basename coincide | candidate | unknown |

Esto no promueve ninguna referencia a render ni a entregable.

## Catálogo público

No hay un catálogo social real local disponible. Por tanto, no existe un join
público verificable: el puente público devuelve `status=unknown`, causa
`MISSING_EVIDENCE`, `verifiable=false` y `reason=no_real_local_social_catalog`.
No se usan fixtures públicos sintéticos para simular ese join.

## Pruebas adversariales

La suite ejecutable cubre explícitamente:

- referencia inexistente → `unknown/MISSING_EVIDENCE`;
- basename ambiguo con dos candidatos existentes → `ambiguous`, cardinalidad 2;
- referencia existente → candidato local, pero `output_claim=unknown`;
- carpeta declarada → carpeta observada, pero `output_claim=unknown`;
- puente público ausente → `unavailable` y join `unknown`;
- payload sin relación de output prohibida.

Comando ejecutado:

```text
PYTHONPATH=/home/mak/flujo/src:/home/mak/flujo/experiments/cycles/C02/aep_endpoint python3 -m unittest discover -s tests -p 'test_*.py' -v
```

Resultado exacto:

```text
Ran 6 tests in 0.003s

OK
```

La invocación equivalente con `pytest` no estuvo disponible en el entorno:
`/usr/bin/python3: No module named pytest`. Las pruebas no dependen de pytest.

## Runner y artefactos

Runner ejecutado:

```text
PYTHONPATH=/home/mak/flujo/src:/home/mak/flujo/experiments/cycles/C02/aep_endpoint python3 run_observation.py --output observation.json
```

Salida exacta del runner:

```json
{"ambiguous_count": 0, "candidate_count": 5, "declared_reference_count": 5, "hash_status": "PASS", "output": "observation.json", "public_join_status": "unknown", "unknown_count": 0}
```

El JSON completo de observación está en `observation.json`. El adaptador y el
wrapper aislado son `aep_endpoint.py` y `run_observation.py`; las pruebas están
en `tests/test_aep_endpoint.py`.
