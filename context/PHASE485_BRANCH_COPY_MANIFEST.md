# Phase 485 — exact historical branch-copy manifest

## Scope

These are source copies of the nine historical non-main branch tips. They are
created only to make each input explicit before triangulation. They are not
declared permanent development branches and must not be treated as current
runtime truth.

| Source copy | Historical source | Exact tip commit | Intended target consumer |
| --- | --- | --- | --- |
| source/mak | mak | 814b74c1f5335170bf5ed1ee8c054565d6e3fc3e | MAK ownership and house integration |
| source/ddbase | ddbase | 4b8453cbf17b25431e091a4a6fe3f09a819a0ffb | MAK mirror/ownership boundary |
| source/rd-evidence | codex/nudo-rd-evidence | 0bb5abe2dd9140807da837c042fa3297464841d7 | RD evidence and field review |
| source/mak-authority | codex/mak-local-authority-reconciliation-20260813 | 1d0b877f20ea7f373fecc3e5c495e98c8226bac5 | MAK authority/runtime reconciliation |
| source/mak-linux | codex/mak-linux-only | 5b7c54f9674fef628383bad80812c1d18a3280b9 | Linux runtime compatibility |
| source/web-20260813 | codex/mak-web-restructure-20260813 | 69ec8c8c4bf24cb282994f48999d9139503ec611 | Portfolio/public web and RD assets |
| source/web-20260814 | codex/mak-web-restructure-20260814 | 1b86a58ea2d4a38b91e233213f3af607c41d797f | Web dependency and validation follow-up |
| source/iskvw | iskvw | 66b6b470ee38b538eb1a194563cb4ed3ee3aeb50 | Portfolio rebuild and deploy contract |
| source/rd | rd | 338ec99ceafbafffee4c4e5c70cdb6a0f75f867e | RD entity, venue and delivery consumers |

## Copy gate

For every row, the following must be true before any update:

    git rev-parse source/<name>
    git merge-base --is-ancestor source/<name> archive/house-history^{commit}

The first command must equal the exact tip in the table. The second command
proves the one-tag preservation point still reaches the copied source. A
branch copy is not integration; integration requires physical MAK/WIN
triangulation, a bounded consumer, and foreground validation.

## Target architecture

After the copy gate, update one source copy at a time into the consumer
boundaries in Phase 461:

- main remains the reviewed integration trunk;
- portfolio work owns public catalog/deploy output;
- RD work owns event, venue, quote, plano and rider consumers;
- MAK/research work owns provenance and Fondart/context slices;
- tools work owns one canonical adapter per function;
- WIN remains historical evidence only.

No source copy may overwrite a database, generated product, credential or
historical evidence. Ambiguous or duplicated content remains classified until
its consumer and provenance are known.
