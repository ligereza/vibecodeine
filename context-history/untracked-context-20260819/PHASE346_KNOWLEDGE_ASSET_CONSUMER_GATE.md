# Phase 346 — knowledge/asset consumer gate

Date: 2026-08-15 (America/Santiago)
Scope: `flujo.knowledge.store` as the RD productora/venue/asset consumer.

## Foreground validation

Using temporary YAML entities and a temporary dossier:

- `list_entities()` resolved a productora alias.
- `classify_event_text()` classified Spanish and English event text as
  `mainstream`, resolved `thegrid`/`espacio_riesco`, and derived rider/flyer/
  Instagram deliverables when a real `https://instagram.com/...` URL was
  present.
- `build_dossier_index()` extracted title, subject, multiline status, sections
  and content hash without copying the dossier body.

```text
KNOWLEDGE_CONSUMER_FIXTURE=PASS
PYAML_TEMP_ONLY_WRITES=True REAL_KNOWLEDGE_UNCHANGED=True
```

The first probe expected the word `Instagram` alone to create the download
deliverable; the actual contract correctly requires an `instagram.com` URL.
The corrected fixture passed. No source, real knowledge YAML or asset changed.

## Disposition

`VERIFIED_KNOWLEDGE_ASSET_CONSUMER; TEMP_ONLY_WRITES`.

This consumer remains the owner for entity classification and dossier metadata;
it does not duplicate the RD catalog database or copy dossier bodies into the
knowledge store.

