# Phase 254 — hub command allow-list gate

Date: 2026-08-15 America/Santiago  
Owner: LUNA principal  
Subagents: none

## Scope

Run only `tests/test_hub_comandos.py`, whose cases exercise the command gate
without starting the hub. The positive subprocess cases are bounded `version`
or intentionally invalid CLI arguments; unknown/destructive strings are
rejected before execution. No provider, automation, POST route or live
mutator is called.

## Validation

```text
pytest -q --disable-warnings tests/test_hub_comandos.py
exit 0; 13 tests passed
rd_datos.db hash before = 70feaf43b5269b6c0341d1ba3debdac60e40fb902cc4bedb41254fdc84d1f703
rd_datos.db hash after  = 70feaf43b5269b6c0341d1ba3debdac60e40fb902cc4bedb41254fdc84d1f703
```

## Result

The generated command manifest and hub gate reject unknown, free-form,
destructive and unclassified commands as designed, while bounded version and
invalid-argument fixtures report their result without notification side
effects. The read-only command boundary is green.

## Risk and rollback

No persistent source, database, job, service or provider state changed. No
rollback is needed. Live command execution, automation routes and mutating
POSTs remain gated.

## Next concrete action

Promote the next fixture-only RD asset/symbol contract group, keeping actual
symbol creation and all live POST paths out of scope.
