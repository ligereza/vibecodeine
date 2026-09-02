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

Selected legacy producers now have opt-in shadow adapters. They still execute
through their legacy path and write only evidence while the flag is enabled;
they do not silently become queue workers.

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
plan.
