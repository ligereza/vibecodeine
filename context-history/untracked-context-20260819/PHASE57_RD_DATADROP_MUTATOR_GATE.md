# Phase 57 — RD datadrop upload mutator gate

## Finding and fix

`HubRequestHandler._handle_datadrop_upload()` created the output directory
before validating Base64. Invalid uploads could therefore leave empty
directories. The handler now decodes with strict validation, rejects empty
payloads, and creates the output directory only after validation succeeds.

## Foreground validation

```text
invalid Base64 fixture with temporary datadrops root
result: error; no output directory created

valid 1x1 PNG fixture with temporary datadrops root
result: image and manifest created successfully

temporary fixture rollback
exit=0; only temporary root removed

AST parse /home/mak/flujo/src/flujo/web/hub.py
exit=0
```

## Decision

Datadrop upload is `PASS_WITH_ROLLBACK_FIXTURE`. The real datadrops surface
was not touched. Remaining mutators are auto-pending flyers, symbol/logo
persistence and real render output; each still needs its own bounded gate.
