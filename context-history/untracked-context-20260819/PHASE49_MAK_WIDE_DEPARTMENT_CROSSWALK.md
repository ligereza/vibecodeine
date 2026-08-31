# Phase 49 — MAK-wide department crosswalk

## Scope and method

This is a physical crosswalk, not a cleanup or deletion list. The search
started at `/home/mak/*`, then narrowed to department roots and compared the
corresponding WIN genealogy under `/home/mak/WIN/flujo/cultura/`. Vocabulary
covered Spanish and English operational terms: `consumer/consumidor`,
`owner/dueno`, `runtime/ejecucion`, `evidence/evidencia`, `rollback`,
`watchdog`, `cron`, `webhook`, `adb`, `Windows`, `Linux`, `n8n`, `puente` and
`pipeline`.

## Physical result

| MAK root | bounded result | WIN relationship | classification | decision |
|---|---:|---|---|---|
| `/home/mak/plataforma` | 5,024 files; 2,327 code/config/docs candidates (includes `.venv`) | `cultura/mak_plataforma` exists | LIVE MAK control/ledger plus rollback evidence | preserve; no migration from WIN |
| `/home/mak/research` | 17,756 files; 9,064 code/config/docs candidates | `cultura/mak_research` exists | LIVE research state and evidence; contains locks/state | preserve; no whole-tree merge |
| `/home/mak/codex` | 618 files; 388 code/config/docs candidates | `cultura/mak_codex` exists | LIVE/evidence mixed creative and Codex artifacts | classify consumers before adoption |
| `/home/mak/curatoria` | 175 files; 155 code/config/docs candidates | `cultura/mak_curatoria` exists | LIVE curation queue/watchdog plus generated material | preserve; validate one consumer later |
| `/home/mak/post` | 3 files; 2 code files | `cultura/mak_post` exists | small adoptable pipeline candidate | static/import contract next |
| `/home/mak/n8n-local` | 3 environment files; no code | no active migration target | discarded by user clarification | do not integrate or inspect as candidate |
| `/home/mak/xio_puente` | 12 files; 7 code/docs/config candidates | `cultura/mak_xio_puente` exists | optional phone bridge; GET-only monitor and staged push | last test only; requires ADB tools and user/device availability |

## Interpretation

The large `plataforma`, `research`, `codex` and `curatoria` roots are not
duplicates of the former FLUJO hub. They are MAK's own operational house and
contain live state, rollback snapshots, generated evidence or creative
outputs. Copying WIN trees would create false integration. The first small
department candidate outside the already-proven hub is `/home/mak/post`, but
it must earn a real consumer and a foreground import/contract check.

`xio_puente` has a clear bounded consumer: the local monitor reads only four
phone GET routes and writes local telemetry. Its staged `mak_link.py` is not
deployed and would introduce a POST path; it remains deferred. The final
validation may download/use ADB tools only after explicit execution of that
last test, and must not be conflated with hub migration.

## Evidence commands and results

```text
find /home/mak -mindepth 1 -maxdepth 1 -printf '%f\\n' | sort
exit=0; all active top-level roots were enumerated

find <root> -type f | wc -l; find <root> -type f \\( -name '*.py' ... \\) | wc -l
exit=0; counts recorded above (the code count includes vendored `.venv` files where present)

find /home/mak/WIN/flujo/cultura/mak_<department> -maxdepth 2 -type f
exit=0 for plataforma/research/codex/curatoria/post/xio_puente; n8n has no migration counterpart used

command -v adb || true
result: not executed as an integration step; ADB download/test intentionally deferred to final xio gate
```

## Residual risks

- Counts are orientation only; they do not establish active consumers.
- `plataforma` and `research` contain state, locks, rollback and environment
  material; do not run watchdogs, cron, queues or mutators during inventory.
- `n8n-local` contains environment material; it is discarded by user decision,
  not a deletion target.
- `xio_puente` references a phone/router topology and external network; no
  network probe, SSH, ADB install or staged plugin deployment was performed.

## Gate decision

Phase 49 completes the MAK-wide orientation crosswalk. It does not claim that
all departments are integrated. The next executable slice is the small
`/home/mak/post` static/import/consumer gate. After that, test `xio_puente`
last with ADB only if the user supplies/authorizes the device-side test.
