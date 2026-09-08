# RD diagnostic contract

Use this packet for RD packs, quotes, riders, plano, venues, productoras,
logos and RD database reads.

Read only the routed RD modules, the relevant web panel and the named fixture.

The RD modules themselves are motor code and are not in this checkout: they are
`rd/` and `plano/` inside the FLUJO checkout, on this box at
`flujo/src/flujo/`. That path is a separate worktree excluded from this branch,
so it exists here and not in CI. This branch carries the RD pieces and their
documentation (`svg/suplementos_rd`, `docs/rd`, `data/rd_packs.json`), which is
what the routed read paths name. Recorded 2026-09-02, because the routing table
used to name the motor paths as if they were tracked here and the report
published them as missing files.

Everything this area outputs is read by a human: correct Spanish with
diacritics, never stripped to ASCII.
Prefer GET-only or pure render checks. Do not upload, mutate SQLite, call live
providers or expose RD media while diagnosing.

Suggested branch: `rd/<short-slug>`.
