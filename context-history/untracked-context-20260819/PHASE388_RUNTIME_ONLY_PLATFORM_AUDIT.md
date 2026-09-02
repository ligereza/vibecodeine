# Phase 388 — runtime-only Platform candidate audit

Date: 2026-08-15 (America/Santiago)

## Scope

The Phase 302 matrix named four runtime-only Platform files. The current
physical surface was checked from `/home/mak/*`; no Git inventory, service,
worker or external call was used.

| Candidate | Current physical state | Consumer/provenance result | Disposition |
|---|---|---|---|
| `plataforma/agente_real.py` | Absent from active root; exists in `context/quarantine/phase305_orphan_optional_tools/` and rollback evidence | No active consumer found in bounded source scan; quarantine copy parses | Keep reversible quarantine |
| `plataforma/memoria.py` | Absent from active root; active owner is `/home/mak/research/memoria.py` | Research runtime is a compatibility projection to canonical `flujo/cultura/mak_research/memoria.py`; py_compile exit 0 | No Platform merge; owner already resolved to Research |
| `plataforma/panel_directivo.py` | Absent from active root; malformed copy in Phase 305 quarantine and rollback | No active consumer; quarantine parse reproduces SyntaxError at line 145 | Preserve historical evidence; do not repair/promote |
| `plataforma/vigia.py` | Absent from Platform root; active owner `/home/mak/vigia/vigia.py` | `/home/mak/vigia/vigia.py` is byte-identical to `flujo/cultura/mak_vigia/vigia.py`; py_compile exit 0 | Owner already resolved to Vigia |

## Validation

```text
active candidate path checks: absent as expected
quarantine agente_real.py: py_compile exit=0
quarantine panel_directivo.py: SyntaxError line 145 (preserved evidence)
research/memoria.py: py_compile exit=0; compatibility projection confirmed
vigia/vigia.py vs cultura/mak_vigia/vigia.py: byte parity confirmed
bounded active consumer scan: no Platform runtime-only consumer found
```

No source, data, credential, WIN, service or rollback file changed. The four
“runtime-only” rows do not expose an unintegrated active Platform owner:
two are already owned by Research/Vigia and two are quarantined historical
orphan artifacts.

Disposition: `RUNTIME_ONLY_PLATFORM_RESOLVED; NO_NEW_QUARANTINE`.
