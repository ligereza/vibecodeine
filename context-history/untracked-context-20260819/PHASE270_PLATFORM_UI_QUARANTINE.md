# Phase 270 — legacy platform UI reversible quarantine

Date: 2026-08-15 America/Santiago  
Owner: LUNA principal  
Subagents: none

## Decision

`/home/mak/plataforma/interfaz.py` was a legacy 150,949-byte Research UI with
no active launcher or unit reference. The active consumer is
`/home/mak/research/interfaz.py`, byte-identical to the canonical source
`/home/mak/flujo/cultura/mak_research/interfaz.py`.

## Action

Moved one file, not the platform directory:

```text
/home/mak/plataforma/interfaz.py
  -> /home/mak/flujo/context/quarantine/phase270_platform_ui/interfaz.py
```

Preflight: target absent, source regular file, mode `644`, size `150949`,
SHA-256 `6712ddff059eab2c3633fc1bf8199944cf6d0f7d602b72`.

The source hash was preserved at the quarantine target. WIN was untouched.

## Validation

```text
move exit: 0
source absent / target present: yes
AST parse: active canonical, runtime projection and quarantine copy = exit 0
active references to /home/mak/plataforma/interfaz.py: none
mak-research.service: inactive
mak-research-queue.service: inactive
mak-hub.service: inactive
mak-codex.service: inactive
mak-xio.service: inactive
focused tests: 8 passed, exit 0
```

## Consumer/dependency impact

No active consumer points to the old path. The real Research unit continues to
point to `/home/mak/research/interfaz.py`; no service was restarted. No Python
dependency, database, data, generated product or provider changed.

## Rollback

If a future consumer is discovered, the reversible rollback is:

```text
mv /home/mak/flujo/context/quarantine/phase270_platform_ui/interfaz.py \
   /home/mak/plataforma/interfaz.py
```

Then rerun the consumer search and focused tests. The quarantined file was not
deleted.

## Next concrete action

Reconcile the objective matrix for this path-level architecture/cleanup gate,
then audit the remaining platform root candidates (`install_mak.sh`, legacy
installer, optional provider tools) without executing them.
