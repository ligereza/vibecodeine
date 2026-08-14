# MAK conductor shadow phase

This package is an internal convergence primitive. It is not a fifth human
interface and it is not enabled by cron or systemd in this phase.

The shadow phase provides:

- SQLite WAL jobs with atomic claims and expiring leases.
- Deterministic job idempotency keys.
- Byte-level artifact hashes with duplicate evidence.
- Append-only job events.
- One portable cross-process GPU lease with a VRAM ceiling.
- A dispatcher that refuses to mark a job complete before validation.

The producer catalog records every work, provider, maintenance, publication,
and control boundary. Selected legacy producers have opt-in shadow adapters;
active adapters execute through this queue while the handler runs inside a
legacy execution context, so nested calls cannot create a second job.
Publication, PR merge, retention, and explicit human-required jobs stop at a
human gate. File outputs are linked by SHA-256 and may be recorded by path
without loading the full payload into SQLite.

Flags are explicit and off by default:

- `MAK_CONDUCTOR_SHADOW=1` enables SQLite evidence jobs.
- `MAK_CONDUCTOR_GPU=1` enables the shared cross-process GPU lease.
- `MAK_CONDUCTOR_ENFORCE_BUDGET=1` makes configured external limits fail closed.
- `MAK_CONDUCTOR_ACTIVE=1` routes the supported synchronous LLM/provider calls
  through the durable queue; it also forces GPU arbitration and budget
  accounting.

The bounded queue worker exists as an internal primitive, but it is not
enabled by cron or systemd yet. Full activation still requires a bounded live
batch, producer/output comparison, complete handler coverage, and a rollback
plan. The canonical producer catalog intentionally keeps legacy task stores
and control/watchdog paths visible as pending or excluded classifications.

Legacy JSONL sources are imported by the explicit source bridge or by the
active canonical `cron_tick` handler. Shadow cron execution does not import
the same source before the legacy consumer runs, which prevents a later
cutover from replaying the task twice.
