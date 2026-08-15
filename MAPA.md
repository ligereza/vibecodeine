# MAP

This repository is the reviewed projection of the MAK system.

- `src/flujo/` is the canonical Python runtime and CLI.
- `web/` is the frontend surface for Main, RD and Portfolio/ISKVW.
- `cultura/` contains research and curation consumers owned by MAK.
- `data/` contains bounded read-oriented sources and projections.
- `tools/` contains deterministic generators and adapters, not competing runtimes.
- `WIN/` is historical evidence and is never an active runtime source.

RD and Portfolio share typed entity boundaries, but retain separate ownership:
RD governs events, venues, quotes and riders; Portfolio governs works and public
authorial presentation. MAK coordinates research, provenance and projections.

Machine-facing identifiers and contracts use English ASCII. Human-facing
products may use correct Spanish. Run `python3 -m flujo --help` for the current
CLI contract and `python3 -m flujo doctor` for local diagnostics.

Git topology is intentionally small: `main` is the reviewed trunk;
`integration/house-restructure` is the current promotion lane; `portfolio/web`,
`rd/runtime` and `mak/ownership` are bounded domain lanes. Domain lanes are
temporary delivery surfaces, not permanent silos or competing applications.
