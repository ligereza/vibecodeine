# Phase 194 — platform coherence audit

Status: `READ_ONLY; PROJECTION_DRIFT_CLASSIFIED`

The canonical `mak_plataforma/coherence.py` was run in report mode. It exited
`0` and did not write state. It reported 36 apparent drift points:

- `plataforma`: 15 different, 0 not-copied, 30 box-only; 0 invoked.
- `research`: 9 different, 0 not-copied, 7 box-only; 0 invoked.
- `codex`: 6 different, 0 not-copied, 0 box-only; 0 invoked.
- `curatoria`: 6 different, 0 not-copied, 0 box-only; 0 invoked.
- `xio_puente`: 0 different, 0 not-copied, 0 box-only; excluded from current
  work by user instruction.

## Interpretation

The 36 count is not automatically 36 defects. The 15/9/6 groups include
intentional thin runtime projections, and the coherence reader compares their
hashes as if source and runtime had to be byte-identical. The 30/7 box-only
groups are not invoked according to its cron/systemd reference check, so they
are candidates for later historical classification, not immediate deletion.

One meaningful drift remains separately tracked: the canonical `testear.py`
was fixed in Phase 171 while its runtime wrapper delegates to it; the
projection is intentional. Similarly the Research wrappers received the
runtime import path fix in Phase 183. These should not be “synced” back into
old full copies by a blind mechanism.

## Validation

- Command: `python /home/mak/flujo/cultura/mak_plataforma/coherence.py`.
- Exit: `0`.
- Installed crontab and user-unit checks found all checked units inactive and
  no relevant matching process.
- No service, cron, provider, package, network, WIN, Git, move or delete.

Next: use the coherence output as a reconciliation input, not a cleanup
command. Select one real `plataforma` projection mismatch, compare its
consumer/role and wrapper contract, and only then choose no-change or a
reversible projection update.
