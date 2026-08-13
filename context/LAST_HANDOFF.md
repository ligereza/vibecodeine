# LAST_HANDOFF - MAK

Updated: 2026-08-13
Status: MAK archive and runtime reconciliation are verified; the MAK-originated
checkpoint is committed and pushed for review.

## Authority and topology

- MAK is the physical operational producer, curator, researcher, and
  coordinator. Windows is a separate director and archive node.
- RD and Portfolio retain separate ownership, safety, authorial, and
  publication gates. They share one logical knowledge database target.
- Local physical surfaces determine material truth. Git is reviewed transport
  only; no bidirectional sync is active.
- Machine-facing code and operational metadata use English ASCII where
  practical. Human RD and Portfolio products retain correct Spanish.
- Do not confuse the MAK computer, /home/mak paths, the mak Git branch, or the
  historical archive under /home/mak/WIN.

## Active checkout and local structure

- Active checkout: /home/mak/flujo, branch mak.
- Active services use /home/mak/research, /home/mak/plataforma,
  /home/mak/codex, and /home/mak/xio_puente. They do not execute from WIN.
- NUDO code/tests, the three-plane contract, unified-knowledge migration and
  reconciliation code, branch policy, and operational gates are present in
  the selected checkpoints.
- Old refs mak, rd, iskvw, mejoras, and mak-svg remain transition history.
  New work uses temporary codex/* branches and returns through review.
- The obsolete RELEVO_MAK.md remains only in the rollback snapshot.
- PostgreSQL mak_knowledge is a prepared target, not current authority.
  RD SQLite remains physically divergent; no writer was selected.

## Windows historical archive

- /home/mak/WIN is an append-only historical archive, not a checkout,
  runtime input, database authority, or Git source.
- Base flujo capture: 23,546 files / 1,003,789,128 bytes; base
  claude_sesiones capture: 21,298 files / 769,263,561 bytes. Both aggregate
  hashes match their Windows sources.
- Codex transfer capture was 8,210 files / 6,420,220,106 bytes. After
  verification, one archived file containing a real HF_TOKEN value was removed;
  the current sanitized archive is 8,209 files / 6,420,219,944 bytes. The
  Windows source was not touched. Live Codex drift remains documented
  separately because the application writes during capture.
- The post-archive Windows reconciliation measured 35 worktree entries:
  14 content changes and 21 metadata-only entries, zero hash errors. The 14
  content versions are under
  /home/mak/WIN/updates-20260813/flujo-working-tree/; the base was preserved.
- Reconciled archive index:
  /home/mak/indexes/win-archive-20260813/win_archive_reconciliation_index.json.
  Its report proves 53,053 base documents plus 14 versioned content objects.
- Secret sanitation manifest:
  /home/mak/WIN/manifests/codex-secret-sanitization-20260813.json.
- Current live Codex observation is recorded at
  /home/mak/WIN/manifests/codex-live-observation-20260813.json: 8,211 files
  / 6,425,014,662 bytes. It is recorded live drift, not a claim of
  instantaneous archive equality.
- Transfer manifests and origin contract are under /home/mak/WIN/manifests/
  and /home/mak/WIN/README_ORIGIN.md. Credentials were excluded.

## Runtime evidence

- Validation report:
  /home/mak/indexes/mak-runtime-validation-20260813.json.
- Focused MAK tests passed with exit 0 in /home/mak/vibecodeine/.venv,
  covering reconciliation, NUDO, RD, research, sync, operational entrypoints,
  and resume scopes.
- In-memory compilation with real service interpreters passed: Research 35,
  Platform 51, Codex 18, XIO 3; 107 active-scoped entrypoints total.
- The only excluded syntax error is the unreferenced legacy prototype
  /home/mak/plataforma/panel_directivo.py. It ends inside a try, has no active
  systemd or cron reference, and remains preserved broken evidence.
- mak-research.service, mak-hub.service, mak-codex.service, and mak-xio.service
  are active. Health endpoints on 8890, 8891, and 8900 returned HTTP 200.
- There are 22 active cron lines; MAK-REPO-SYNC remains paused.
- Full runtime comparison:
  /home/mak/indexes/mak-runtime-reconciliation-20260813.json.
  Rollbacks, generated pieces, utilities, revisions, and unrouted legacy files
  remain classified outside active runtime and Git projection.

## Transport and next action

- MAK source checkpoint is based on mak at 814b74c; current publishing branch is codex/mak-local-authority-reconciliation-20260813. Windows checkpoint
  is codex/three-plane-consolidation at f588ecf. NUDO source remains at
  codex/nudo-rd-evidence. No checkpoint is merged to main.
- This handoff is the only current handoff in the MAK checkout context.
- The published checkpoint contains only the reviewed MAK handoff; the WIN
  archive, databases, raw media, derived indexes, and runtime candidates stay
  outside Git. Human review may decide whether to merge it to main.
- Do not reset, clean, merge, delete history, or start a sync job.
