# MAP

This is the only operational map for `/home/mak/flujo`. `context/LAST_HANDOFF.md`
is the continuity record; phase files are evidence and must not override it.
The `MAPA.md` files under `/home/mak/vibecodeine` and `/home/mak/WIN` belong to
other worktree/historical surfaces and are not current MAK instructions.

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

Git topology is intentionally small: `main` is the only canonical trunk.
`source/*` contains the exact preserved copies of the historical local branch
tips and is not an active runtime source. `work/*` is temporary delivery
space; the currently published `work/mak-ownership` slice is retained for
traceability until its promotion lifecycle closes. No permanent portfolio,
RD or MAK domain branches exist, and no old branch name is an active source of
truth.

Ignored `web/dist*` and `dist_compartir/` files are generated delivery artifacts,
not sources of truth. If they contain an older snapshot, use the tracked source
and regenerate them only after the documented Node/Rollup build gate is repaired.
