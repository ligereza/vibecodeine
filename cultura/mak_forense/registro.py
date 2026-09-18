#!/usr/bin/env python3
"""Minimal model for analyzing the PROVENANCE of a record.

Born from analyzing `Testeo 2025` (2026-09-16): a spreadsheet where each
volunteer built their session's sheet by copying the previous event's and
overwriting rows. Whatever didn't get overwritten stayed as a sample
nobody tested. 2,856 rows, of which 645 were a block stitched 31 times
and 132 came from ANOTHER session.

The module isn't about the spreadsheet. It's about the shape of the
problem, which repeats in any human record made under urgency:

    annotation + another annotation from another date -> are they the same?
    and if so, which is the original and which is the copy?

That's why the record here is abstract: a comparable `contenido`, a
`grupo` it belongs to, an `orden` within that group, and -- when it
exists -- the real instant it was recorded. That's enough for XIO-RD (a
sample loaded under the wrong event), for the old spreadsheet, and for
any other MAK area that records facts over time.

Three RD-domain rules that are structure here, not commentary:

1. Nothing gets discarded. A finding MARKS a record, never deletes it.
   The decision to exclude it is human and comes later.
2. Certainty is declared. `confirmado` / `probable` / `pendiente` are not
   decoration: they separate what the math proved from what merely
   suggests.
3. The analysis declares what it couldn't see. `Cobertura.limites`
   exists so a total is never read as complete. A detector silent about
   its blind spots lies by omission.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict

# What the analysis was able to prove about a finding.
#
#   confirmado -- two independent signals agree (e.g. the run's weight
#                 and the date say the same thing about who copied whom)
#   probable   -- a single signal, with nothing contradicting it
#   pendiente  -- there is signal, and the signals contradict each other,
#                 or the deciding fact is missing. It's still a finding:
#                 pending is shown, not hidden.
CERTEZAS = ("confirmado", "probable", "pendiente")


@dataclass(frozen=True)
class Registro:
    """An annotation, with the minimum needed to judge if it repeats and where it comes from.

    `contenido` is the tuple of fields that define "the same annotation".
    Which fields go in is a decision for the area, not this module: in
    the tests it's substance/format/reagents/results; in another area it
    will be others. What this module guarantees is that two records with
    the same `contenido` are treated as the same fact annotated twice.

    `orden` is the position within the group (spreadsheet row,
    sequential id, load index). It's the axis a repetition is measured
    as contiguous or periodic against, and that's why it has to be
    comparable within the group -- it doesn't need to be global.

    `fecha_declarada` is what the record SAYS about itself (the event
    date). `instante_registro` is when it was REALLY recorded (epoch).
    The distance between the two is the most useful detector that exists
    for a record made in an app: if they don't match, someone picked the
    wrong event.
    """

    id: str
    grupo: str
    orden: int
    contenido: tuple
    fecha_declarada: str | None = None
    instante_registro: float | None = None
    es_encabezado: bool = False
    etiqueta: str = ""


@dataclass(frozen=True)
class Hallazgo:
    """A pattern found, with the evidence that supports it.

    `explicacion` is in Spanish and one line because its recipient isn't
    a log: it's the person who has to decide what to do with the record.
    """

    patron: str
    certeza: str
    grupo: str
    n: int
    explicacion: str
    registros: tuple[str, ...] = ()
    origen: str | None = None
    evidencia: dict = field(default_factory=dict)

    def __post_init__(self):
        if self.certeza not in CERTEZAS:
            raise ValueError(f"certeza desconocida: {self.certeza!r}")


@dataclass(frozen=True)
class Cobertura:
    """What the analysis saw, and above all what it could NOT see.

    This exists because of a concrete, recent mistake: the copied-run
    detector only compared sheets within the same run, so a 2025 sheet
    copied from a 2024 one was invisible to it -- and the report didn't
    say so. A number without its coverage reads as a total, and it
    wasn't one.
    """

    registros: int
    grupos: int
    pares_comparados: int
    sin_fecha_declarada: int
    sin_instante_registro: int
    limites: tuple[str, ...] = ()


@dataclass(frozen=True)
class Analisis:
    hallazgos: tuple[Hallazgo, ...]
    cobertura: Cobertura

    def por_patron(self) -> dict[str, int]:
        cuenta: dict[str, int] = {}
        for h in self.hallazgos:
            cuenta[h.patron] = cuenta.get(h.patron, 0) + h.n
        return dict(sorted(cuenta.items(), key=lambda kv: -kv[1]))

    def por_certeza(self) -> dict[str, int]:
        cuenta = {c: 0 for c in CERTEZAS}
        for h in self.hallazgos:
            cuenta[h.certeza] += h.n
        return cuenta

    def como_dict(self) -> dict:
        return {
            "hallazgos": [asdict(h) for h in self.hallazgos],
            "cobertura": asdict(self.cobertura),
            "por_patron": self.por_patron(),
            "por_certeza": self.por_certeza(),
            "principio": (
                "un hallazgo marca un registro, nunca lo borra; "
                "la exclusion es una decision humana posterior"
            ),
        }

    def como_json(self, indent: int | None = None) -> str:
        return json.dumps(self.como_dict(), ensure_ascii=False, indent=indent,
                          default=str)
