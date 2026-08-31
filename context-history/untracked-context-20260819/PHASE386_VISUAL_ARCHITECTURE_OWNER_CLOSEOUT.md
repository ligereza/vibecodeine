# Phase 386 — visual architecture and owner closeout

Date: 2026-08-15 (America/Santiago)

## Owner map

```mermaid
flowchart LR
    WIN["/home/mak/WIN<br/>historical Windows archive"]:::historical
    RD["/home/mak/RD<br/>protected data and media"]:::protected
    FLUJO["/home/mak/flujo<br/>canonical authoring + FLUJO APP"]:::active
    CATALOG["data/rd.db<br/>catalog owner"]:::active
    PRIVACY["data/rd_datos.db<br/>privacy/field store<br/>empty, integrity ok"]:::protected
    DEPLOY["/home/mak/flujo-deploy<br/>external deploy owner"]:::external
    SYNC["bin/mak_sync_safe.py<br/>gated mutator"]:::gated
    PROJ["runtime projections<br/>research · plataforma · codex<br/>curatoria · vigia · lenguaje"]:::active
    EVIDENCE["context + indexes + labs + state<br/>evidence/recovery"]:::protected
    QUAR["context/quarantine<br/>reversible containment"]:::protected
    N8N["/home/mak/n8n-local<br/>discarded; credentials preserved"]:::excluded
    XIO["/home/mak/xio_puente<br/>user-excluded"]:::excluded

    WIN -. provenance/crosswalk only .-> FLUJO
    RD --> FLUJO
    FLUJO --> CATALOG
    FLUJO --> PRIVACY
    FLUJO --> PROJ
    FLUJO --> EVIDENCE
    DEPLOY -. gated, never automatic .-> SYNC
    SYNC -. authorized deployment only .-> PROJ
    N8N -. protected evidence, no active consumer .-> EVIDENCE
    XIO -. excluded from migration .-> EVIDENCE
    QUAR -. rollback only .-> FLUJO

    classDef active fill:#173f35,stroke:#63d6a0,color:#fff;
    classDef protected fill:#3e315b,stroke:#c8a9ff,color:#fff;
    classDef historical fill:#374151,stroke:#9ca3af,color:#fff;
    classDef external fill:#60451d,stroke:#f4c95d,color:#fff;
    classDef gated fill:#612b2b,stroke:#ff8f8f,color:#fff;
    classDef excluded fill:#252525,stroke:#777,color:#ddd;
```

## Operating rules

| Class | Allowed action | Forbidden shortcut |
|---|---|---|
| Active owner/projection | Compile, import, focused consumer test; edit smallest target | Copy whole trees or create parallel owner |
| Protected data/evidence | Read metadata/counts and preserve provenance | Delete, ingest, rewrite or normalize by filename |
| Historical WIN | Crosswalk and provenance comparison | Treat archive presence as active integration |
| External/deploy | Static audit and contract documentation | Git fetch/reset, SSH, provider or deploy execution |
| Gated/mutating | Fixture and rollback design | Live write without named authority |
| Excluded | Preserve and omit from plan | Use as an excuse to block unrelated local work |

## Closeout interpretation

- The active house is owner-based: `flujo` is canonical and department roots
  are projections only when a consumer exists.
- Similar tools fuse by consumer contract and parity, not by names, language
  or timestamps. Intentional wrappers remain thin projections.
- `rd.db` and `rd_datos.db` are logically related but physically separate;
  the field store remains empty until the review packet is approved.
- Cleanup means reversible quarantine for confirmed residue. WIN, databases,
  credentials, media, generated products and evidence remain protected.

Evidence: Phases 362, 370, 381, 382, 383, 384 and 385.

Disposition: `VISUAL_OWNER_ARCHITECTURE_CLOSED; GATES_REMAIN_EXPLICIT`.
