# Phase 353 — bilingual email/pedido parser gate

Date: 2026-08-15 (America/Santiago)

## Scope

Validated the pure parser surface in
`/home/mak/flujo/src/flujo/intake/email_parser.py` with Spanish and English
fixtures, normalized Instagram URLs, section extraction, hub pedido shape
and temporary file reading. The mutating email-to-jobs pipeline was not run.

## Results

```text
EMAIL_PARSER_ES=PASS
EMAIL_PARSER_EN=PASS
PEDIDO_HUB_SHAPE=PASS
EMAIL_FILE_READONLY=PASS
PYCOMPILE_RC=0
```

Spanish and English labels resolve to the same internal sections, Instagram
URLs normalize without query strings, pedido classification preserves volume
and audience, and `parse_email_file` reads a temporary file without creating a
job or project.

## Disposition

`VERIFIED_BILINGUAL_PARSER; MUTATING_PIPELINE_SEPARATED`

This confirms the local parser contract used before intake side effects. It
does not authorize Instagram downloads, job creation, project creation or
external email processing.

## Rollback and boundary

No source, real file, database, service, provider, Git state or WIN evidence
changed. No rollback is required. The next gate must isolate JSON-schema
validation from job creation writes.
