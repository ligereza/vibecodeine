# Phase 66 — ledger source/projection parity gate

## Slice

`/home/mak/flujo/cultura/mak_plataforma/ledger.py` is the canonical FLUJO
implementation and `/home/mak/plataforma/ledger.py` is its exact projection.
The module has real consumers in `src/flujo/autonomia.py` and
`cultura/mak_curatoria/diagnostico_proyectos.py`.

## Validation

- `cmp -s` source/projection: exit 0; both are 34,051 bytes.
- `PYTHONPATH=/home/mak/flujo python3 -m cultura.mak_plataforma.ledger --help`:
  exit 0; all four entrypoint groups rendered; stderr empty.
- Pure fixture `build_work_envelope` + `validate_work_envelope`: valid with no
  filesystem action.
- Pure fixture `normalize_item` + `validate_item`: valid with no filesystem
  action.
- `/home/mak/plataforma/common_ledger.jsonl` size/mtime was checked before and
  after; no ledger row was appended.
- No provider, queue, worker, cron or service was started.

## Decision

The ledger slice is `PROJECTION_PARITY_VERIFIED`: no merge edit is needed.
Canonical ownership is `cultura/mak_plataforma/ledger.py`; the root copy is
retained as a protected projection until the wider one-way projection policy
is implemented. The next tool candidate must be equally bounded and must not
depend on live locks, providers or stateful workers.
