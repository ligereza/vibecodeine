# Phase 171 — Codex testear isolation fix and fixture gate

Date: 2026-08-15
Owner: LUNA-PRINCIPAL

## Finding

The initial fixture exposed a real defect in
`/home/mak/flujo/cultura/mak_codex/testear.py`: it copied the module and
generated tests into a temporary directory, then invoked `python -I -m
unittest`. Python isolated mode removed the temporary directory from
`sys.path`, so the valid fixture failed with `ModuleNotFoundError` before the
test ran.

## Fix

The canonical source now keeps `-I` and runs a tiny isolated `-c` runner that
inserts the known temporary directory into `sys.path` before invoking
`unittest.main(module='test_pieza')`. The runtime
`/home/mak/codex/testear.py` is already a canonical compatibility wrapper and
was not edited.

## Foreground result

Both source and runtime compiled. With the provider replaced by a local fake
coder and `REVISIONES` redirected to temporary directories, both paths generated
and executed the same pure-Python test successfully: `SOURCE_OK=True RC=0`,
`RUNTIME_OK=True RC=0`, report status `OK`, process gate clear. No provider,
real piece, manifest, worker, service or persistent process was touched.

## Next action

Run the core compile/health/web checks after this source fix, then continue the
Codex surface with `generar.py`/`iconos.py` only through provider-free validation
or fixtures.
