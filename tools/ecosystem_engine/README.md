# ecosystem_engine

Self-contained, zero-dependency diagnostic-to-frontend compilation pipeline for the
**Tapiz ↔ Psicosis ↔ Fungi** bio-cybernetic art ecosystem. Standard library only
(Python 3.10+).

## Files

| File | Role |
|------|------|
| `complete_engine.py` | The engine. Builds a mock ecosystem, runs three diagnostic analyzers, and compiles the results into a frontend payload. |
| `system_map.py` | Pure declarative contract (no runtime code). Describes the exact shape of the output JSON plus the engineering→aesthetic rendering directives the frontend consumes. |

> Incorporated from the working drafts `TODO.py` (→ `complete_engine.py`) and
> `EXPLAINING TODO.py` (→ `system_map.py`); names match the `FILE:` headers in each
> module docstring.

## Run

```bash
python complete_engine.py
```

Writes `dist/system_status.json` (relative to the current working directory; the
`dist/` folder is git-ignored). The JSON conforms to `system_map.API_CONTRACT_SCHEMA`.

## Pipeline

1. **Domain models** — `ArtAsset` / `EcosystemState` (active vs. decaying populations).
2. **Analyzers** —
   - `TokenVolumetricAnalyzer`: estimates BPE token pressure from symbol density.
   - `GuardrailSimulationAnalyzer`: keyword-based risk scoring with artistic-context mitigation.
   - `ConcurrencyLogicAnalyzer`: detects state-machine race conditions / logic flaws.
3. **MetamorphicBridge** — transmutes diagnostics into CSS variables, filters, keyframes,
   a steganographic payload (Base64+Shift42, chunked), and a SHA-256 integrity sigil.
4. **Export** — `dist/system_status.json`.

The steganographic round-trip is verified in-process; a decode mismatch aborts the run.
