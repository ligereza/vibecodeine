# Phase 163 — research entrypoint gate

Date: 2026-08-15
Owner: LUNA-PRINCIPAL

## Source, target and consumer

- Canonical source: `/home/mak/flujo/cultura/mak_research/research.py`
- Runtime entrypoint: `/home/mak/research/research.py`
- Shared dependency checked: `research_lib.py` in both surfaces
- Consumer: standalone research command and the research service worker

## Result

Both research runners and both `research_lib.py` files compiled with exit 0.
Canonical and runtime `research.py --help` output matched byte-for-byte and
exposed the same topic, depth, provider, density, format, resume and output
contracts. The check did not start the research service, call providers, read
credentials, write an informe or leave a process. The runtime research runner
was already a compatibility projection; no edit was needed.

## Decision

Keep this existing projection and move to the next unresolved research
consumer. Provider-backed execution remains gated until a fixture or explicit
provider authority exists.
