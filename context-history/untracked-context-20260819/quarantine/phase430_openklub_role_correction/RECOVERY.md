# Phase 430 - OpenKlub role correction recovery

Target removed from active venue sources:

`knowledge/venues/openklub.yaml`

Original SHA-256:

`40c8ef77770c6581ca2d772f98408f801e6c41b7e167de8c7627f9af7711ebf9`

Reason: user-confirmed OpenKlub is a producer/brand, not a venue. The file was
an inferred venue record and its own notes said the role was uncertain.

The original file is preserved in this same quarantine directory. Rollback:

```bash
mv context/quarantine/phase430_openklub_role_correction/openklub.yaml knowledge/venues/openklub.yaml
```

After rollback, rebuild `data/rd.db` from sources and revalidate the venue
catalogue. Do not use this evidence file as a venue until a real venue
identity is established.
