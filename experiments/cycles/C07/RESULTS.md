# C07 — resultados

Implementación mínima ejecutable completada.

Gate:

```text
python3 runner.py
tests_exit_code=0
py_compile_exit_code=0
case_count=5
candidate_count=17
```

Cobertura mínima: extracción de PNG/XMP, secuencias, candidato
`component_of`, contraparte ausente, mismo nombre con hashes distintos,
proporciones distintas, publicación JPEG y contrato JSON de candidatos.

Comprobación adicional directa:

```text
python3 -m unittest discover -s tests -p 'test_*.py'  # EXIT 0, 5 tests
python3 -m py_compile practice_graph.py runner.py fixtures/build_fixtures.py tests/test_practice_graph.py  # EXIT 0
```

El contrato implementa las cinco relaciones: `component_of`, `version_of`,
`manifestation_of`, `same_series_candidate` y `published_as`. En las fixtures
ejecutadas aparecen las relaciones que tienen señales aplicables; los estados
observados son `pending_relation` y `unresolved_candidate`; no se emite
`unknown`.

Revisión adicional: un frame numerado ya no puede ser destino de otro frame,
un sidecar XML/XMP ya no puede convertirse en destino de una relación de
medios solo por contener `export` en el nombre y `published_as` exige una
fuente de medios exportable y un destino de medios publicado.
