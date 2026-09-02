# Phase 370 — projection owner matrix

Date: 2026-08-15 (America/Santiago)

| Family | Canonical source | Live path | Consumer/parity result | Disposition |
|---|---|---|---|---|
| Research | `cultura/mak_research` | `/home/mak/research` | five changed pairs exact; local imports pass | `OWNER_VERIFIED` |
| Platform | `cultura/mak_plataforma` | `/home/mak/plataforma` | provider pair exact; active n8n refs absent | `OWNER_VERIFIED` |
| Codex | `cultura/mak_codex` | `/home/mak/codex` | wrapper + exact interface; imports/unit pass | `WRAPPER_INTENTIONAL` |
| Curatoria | `cultura/mak_curatoria` | `/home/mak/curatoria` | wrappers + exact guard; imports pass | `WRAPPER_INTENTIONAL` |
| Vigia | `cultura/mak_vigia` | `/home/mak/vigia` | exact pair; parser/golden rules pass | `OWNER_VERIFIED` |
| Lenguaje | `cultura/mak_lenguaje` | `/home/mak/lenguaje` | exact pair; bilingual signal pass | `OWNER_VERIFIED` |
| XIO | `cultura/mak_xio_puente` | `/home/mak/xio_puente` | user excluded; no test | `EXCLUDED` |
| n8n | none | `/home/mak/n8n-local` | no tool/service; credential evidence only | `DISCARDED_PROTECTED` |

## Conclusion

The declared projection families now have explicit owners, live paths and
consumer/parity results. Similar filenames are not merged when the live path
is an intentional wrapper or when data/state belongs to the runtime root.

## Remaining material gates

This matrix does not close RD field-data authority, live mutator authority,
optional provider execution, broad document mutation, protected cleanup,
external-risk coverage or Git branch operations. Those remain explicit in the
13-objective audit and handoff.
