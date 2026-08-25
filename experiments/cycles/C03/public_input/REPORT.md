# C03 public input — normalizador experimental

## Resultado

Se implementó un normalizador cerrado y local para entradas públicas
declaradas. No existe un export público real local con posts, reels, stories y
medios; por eso la ausencia real se representa sólo mediante
`catalog_status=unavailable` y `completeness.status=unavailable`. Los archivos
de `fixtures/` están marcados como benchmark sintético y no son datos reales.

## Archivos producidos

- `/home/mak/flujo/experiments/cycles/C03/public_input/public_normalizer.py` — parser, validación y normalización stdlib.
- `/home/mak/flujo/experiments/cycles/C03/public_input/run_normalizer.py` — runner/CLI, sin red.
- `/home/mak/flujo/experiments/cycles/C03/public_input/fixtures/canonical_declared.json` — forma canónica declarada, sintética.
- `/home/mak/flujo/experiments/cycles/C03/public_input/fixtures/declared_json_export.json` — envoltorio JSON declarado, sintético.
- `/home/mak/flujo/experiments/cycles/C03/public_input/fixtures/html_json_incomplete.html` — envoltorio HTML con JSON incompleto interpretable, sintético.
- `/home/mak/flujo/experiments/cycles/C03/public_input/fixtures/invalid_missing_archive_id.json` — negativo sintético.
- `/home/mak/flujo/experiments/cycles/C03/public_input/fixtures/invalid_unknown_type.json` — negativo sintético.
- `/home/mak/flujo/experiments/cycles/C03/public_input/fixtures/invalid_media_without_origin.json` — negativo sintético.
- `/home/mak/flujo/experiments/cycles/C03/public_input/fixtures/invalid_uninterpretable.html` — negativo sintético.
- `/home/mak/flujo/experiments/cycles/C03/public_input/tests/test_public_normalizer.py` — tests stdlib `unittest`.

## Contrato implementado

Se aceptan únicamente estas formas declaradas:

- `schema=c03.public_input.canonical.v1` con `records` y `type` explícito.
- `wrapper=c03.public_input.declared_json_export.v1` con arrays `posts`,
  `reels` y `stories`.
- `wrapper=c03.public_input.html_json_incomplete.v1` dentro de exactamente un
  `<script type="application/json">`.

Todas exigen `archive_id` explícito. Se conservan los tipos `post`, `reel` y
`story`, sus media, `origin`, `evidence_refs`, `hashes` y
`completeness` cuando están declarados. Para una media declarada, `origin` es
obligatorio y no se obtiene desde nombre de archivo, URL, timestamp,
basename, similitud o proximidad.

El normalizador falla cerrado con error y código CLI `2` ante `archive_id`
ausente, forma/tipo no declarado o desconocido, media sin `origin`, JSON no
interpretable, HTML sin exactamente un bloque JSON interpretable, listas con
tipo incorrecto o campos declarados con estructura inválida.

La salida no contiene `generated`, `RENDERS_TO`, `relations`, autoría,
joins ni decisiones de procedencia. Los timestamps y URLs sólo pasan si ya
están declarados en la entrada; nunca se crean. No se importa C02.

## Comandos y resultados verificados

Todos usan Python stdlib, `-B` y no requieren red ni instalación de paquetes.

```text
PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s /home/mak/flujo/experiments/cycles/C03/public_input/tests -p 'test_*.py' -v
exit code: 0
resultado: 7 tests, OK
```

```text
python3 -B /home/mak/flujo/experiments/cycles/C03/public_input/run_normalizer.py /home/mak/flujo/experiments/cycles/C03/public_input/fixtures/canonical_declared.json
exit code: 0
resultado: JSON normalizado con archive_id explícito y los tres tipos
```

```text
python3 -B /home/mak/flujo/experiments/cycles/C03/public_input/run_normalizer.py --catalog-unavailable --archive-id archive-arica-001
exit code: 0
resultado: catalog_status=unavailable, sin records ni media
```

```text
python3 -B /home/mak/flujo/experiments/cycles/C03/public_input/run_normalizer.py /home/mak/flujo/experiments/cycles/C03/public_input/fixtures/invalid_media_without_origin.json
exit code: 2
resultado: error por media sin origin
```

## Límites exactos

- Sólo se leen archivos locales con sufijo `.json`, `.html` o `.htm`.
- HTML no se ejecuta: se inspecciona con `html.parser` y requiere exactamente
  un script `application/json` cuyo contenido sea un objeto JSON interpretable.
- No se consulta red, APIs, catálogos, Git, C02 ni dependencias externas.
- La función `catalog_unavailable(archive_id)` y el flag CLI requieren un
  `archive_id` explícito y producen un estado, no una observación de export.
- La normalización valida y estructura observaciones; no reconcilia ni decide
  procedencia. La conexión posterior con artefactos locales queda fuera de
  este experimento.
