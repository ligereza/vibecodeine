# Phase 55 — RD field-data read-only gate

## Finding and fix

`/home/mak/flujo/data/rd_datos.db` is still zero bytes. The reader
`src/flujo/rd/informe.py::resumen_json()` previously called the schema-creating
`conectar()` function, contradicting its documented GET-only contract. The
reader now returns `{"disponible": false}` for absent/zero-byte files and
opens non-empty files with SQLite `mode=ro`.

## Foreground validation

```text
find /home/mak/* then bounded data inspection
exit=0; active field database remains /home/mak/flujo/data/rd_datos.db, 0 bytes

real empty-file summary probe
result: {'disponible': False}; size and mtime unchanged

temporary non-empty SQLite fixture + read-only summary
result: disponible=True, total_testeos=1, total_atenciones=0,
total_encuestas=0; mtime unchanged

AST parse of informe.py
exit=0
```

## Decision

The field-data read contract is now safe and truthful. No real rows were
inserted; demo CSVs and historical evidence remain non-authoritative. Real
field data requires an approved handoff/acta, privacy-screened CSV or operator
input, and an identified owner before ingestion. The next executable slice is
the RD mutator gate, using temporary fixtures and rollback only.
