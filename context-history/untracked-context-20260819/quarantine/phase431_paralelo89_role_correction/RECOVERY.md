# Phase 431 recovery

Original file:

`/home/mak/flujo/knowledge/venues/paralelo_89.yaml`

Quarantined copy:

`/home/mak/flujo/context/quarantine/phase431_paralelo89_role_correction/paralelo_89.yaml`

Original SHA-256:

`9ba9b1785954227325b31292e02d794068867a7466c59ec87963ec6a97d0f4c9`

To restore the source only if later primary evidence confirms a venue:

```bash
mv /home/mak/flujo/context/quarantine/phase431_paralelo89_role_correction/paralelo_89.yaml /home/mak/flujo/knowledge/venues/paralelo_89.yaml
/home/mak/venvs/flujo/bin/python -m flujo rd-db build
```

Do not restore solely because a generated projection expects the old ID.
