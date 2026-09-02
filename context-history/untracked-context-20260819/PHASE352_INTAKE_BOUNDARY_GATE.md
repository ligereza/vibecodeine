# Phase 352 — intake and airdrop boundary gate

Date: 2026-08-15 (America/Santiago)

## Scope

Validated the local boundary in
`/home/mak/flujo/src/flujo/intake/reception.py`: safe ZIP extraction,
traversal rejection, disabled email automation and the signed-artifact gate.
No mailbox, provider, subprocess or live airdrop was invoked.

## Results

```text
INTAKE_SAFE_ZIP=PASS
INTAKE_TRAVERSAL_GATE=PASS
INTAKE_EMAIL_DISABLED=PASS
INTAKE_SIGNATURE_GATE=PASS
PYCOMPILE_RC=0
```

Safe members extracted into a temporary destination; `../escape.txt` was
rejected and did not escape the destination. With automation disabled, the
email path returned before any IMAP connection. Without the HMAC key, the
signed-artifact gate refused application.

## Disposition

`VERIFIED_LOCAL_INTAKE_GUARDS; EXTERNAL_EMAIL_AIRDROP_DISABLED`

This slice is locally safe for parsing/guard behavior. It is not approval to
enable IMAP automation or apply an airdrop. The user-confirmed EVENTO issue/URL
bridge remains separate from this unused email airdrop path.

## Rollback and boundary

No real file, database, service, provider, Git state or WIN evidence changed;
all extraction occurred in a temporary directory. No rollback is required.
Enabling IMAP or airdrop application requires explicit authority and a later
foreground validation.
