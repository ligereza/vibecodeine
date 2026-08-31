# Phase 365 — architecture/objective refresh after credential ownership

Date: 2026-08-15 (America/Santiago)

| Change | Canonical owner | Live consumer | Verification | Disposition |
|---|---|---|---|---|
| Research credential fallback | `cultura/mak_research` | `/home/mak/research` | five-file exact parity; no n8n refs | `VERIFIED` |
| Platform provider fallback | `cultura/mak_plataforma/providers.py` | `/home/mak/plataforma/providers.py` | exact parity; py_compile | `VERIFIED` |
| n8n automation root | none | none | no process/unit; credentials mode 600 | `EXCLUDED_PROTECTED` |
| XIO bridge | `cultura/mak_xio_puente` historical projection | `/home/mak/xio_puente` | user exclusion | `EXCLUDED_NO_TEST` |
| WIN archive | `/home/mak/WIN` | none | authority contract | `HISTORICAL_READ_ONLY` |

## Objective impact

This closes a concrete architecture conflict in objectives 4, 7, 8 and 10:
n8n is no longer an active credential dependency, Research owns its own
environment path, and canonical/live projections agree for the changed files.
It does not close the separate gates for RD field authority, live RD mutators,
optional provider execution, final cleanup or Git operations.

## Next concrete action

Select the next active projection family and perform the same local parity /
consumer check, beginning with a bounded file set and excluding data, caches,
credentials, generated products and historical evidence.
