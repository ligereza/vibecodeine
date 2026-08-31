# Phase 441 — venue and portfolio cross-domain gate

## Scope

This phase verifies the venue HTML owner and its portfolio consumer. It
deliberately keeps three concerns separate: the open technical venue registry,
the ISKVW venue viewer, and the RD knowledge database. The common venue JSON
is the bridge; the databases are not merged by HTML projection.

## Owner chain

- Registry source: `data/venues/*.json`.
- Generator: `tools/venue.py sitio`.
- Open catalogue consumer: `web/venues/index.html`.
- Portfolio/VJ venue consumer: `iskvw/piel/venue/index.html`.
- Portfolio feature switch: `iskvw/datos/tablero.json`,
  `mejoras.venue3d = true`.
- Current venue seed: `data/venues/scd-plaza-egana.json`.
- Separate RD knowledge surface: `knowledge/venues/` and `data/rd.db`; no
  RD producer/entity was inserted into the technical venue catalogue.

## Foreground validation

Commands and observed results:

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m py_compile tools/venue.py
exit 0

PYTHONDONTWRITEBYTECODE=1 python3 tools/venue.py validar
exit 0 — 3 venues, 0 errors, 0 warnings

PYTHONDONTWRITEBYTECODE=1 python3 tools/venue.py geometria
exit 0 — SCD has 56 polylines / 503 edges / 0 zero-length segments;
1 of 3 venues has geometry

PYTHONDONTWRITEBYTECODE=1 python3 tools/venue.py sitio
exit 0 — 3 rooms, 27 KB
```

The generated catalogue hash stayed unchanged:
`f8604f03828727b826975a9ea49899449a3ec42c43b98be556f84728e5af5145`.
Focused assertions exited 0: the catalogue embeds exactly three records,
includes `scd-plaza-egana`, excludes `openklub` and `paralelo_89`, and retains
search behavior. The portfolio venue HTML JavaScript parsed with
`new Function` (exit 0, one script), its deploy projection compares equal,
and cross-domain assertions confirmed the SCD registry path, the
`?venue=<id>` route, the `venue3d` switch and the declared no-data fallback.

## Role and data disposition

SCD is a technical venue record used by the VJ/portfolio venue viewer and by
the open catalogue. It is not automatically an RD producer or an RD event
venue. RD `knowledge/venues` remains a separate evidence/curation domain; the
FRVR/Sala Metronomo and OpenKlub corrections stay governed by their own role
evidence. This is the intended cross-domain connection without corrupting
either database.

No source, JSON, HTML or historical evidence was edited, moved or deleted.

Disposition: `VENUE_CATALOGUE_GREEN; PORTFOLIO_VENUE_BRIDGE_GREEN; SCD_ROLE_SEPARATED; RD_DB_NOT_MERGED`.

Next action: inspect the next active HTML owner from the physical MAK surface,
prioritizing the remaining Plano/Rider and RD projections while preserving
the venue registry boundary.
