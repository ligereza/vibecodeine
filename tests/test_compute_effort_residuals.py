#!/usr/bin/env python3
"""Contracts for `tools/compute_effort_residuals.py`, 304 lines untested.

`robust_scale` names its own method: "MAD, then scaled mean absolute
deviation". Robustness is not decoration here -- the whole reason to pick MAD
over a standard deviation is that one runaway measurement must not redefine
what counts as normal effort, and a residual computed against a scale an
outlier moved would flag ordinary work as anomalous.

So the central test is not that the function returns a number. It is the
contrast: measured on [10,11,12,13,14] plus a single 1000, MAD goes 1.0 -> 1.5
while the standard deviation goes 1.58 -> 403. That difference is the reason
the function exists in this form.

`source_topic` has the other contract worth holding: it prefers a declared
topic and falls back to the filename, never to silence.
"""
from __future__ import annotations

import json
from pathlib import Path
import statistics

import pytest

from tools.compute_effort_residuals import (
    artifact_dimensions,
    robust_scale,
    source_topic,
)


class TestRobustScaleEarnsItsName:
    BASE = [10.0, 11.0, 12.0, 13.0, 14.0]

    def test_an_outlier_barely_moves_it(self) -> None:
        before = robust_scale(self.BASE)
        after = robust_scale(self.BASE + [1000.0])
        assert after < before * 2, (
            f"a single 1000 moved the scale from {before} to {after}; that is "
            "not a robust scale"
        )

    def test_the_same_outlier_wrecks_a_standard_deviation(self) -> None:
        # Without this the test above proves nothing: it could pass on data
        # where no method would have been disturbed.
        before = statistics.stdev(self.BASE)
        after = statistics.stdev(self.BASE + [1000.0])
        assert after > before * 100, (
            "the outlier chosen does not disturb a naive scale, so the "
            "robustness comparison is vacuous"
        )

    def test_it_matches_the_median_absolute_deviation_it_claims(self) -> None:
        median = statistics.median(self.BASE)
        expected = statistics.median([abs(v - median) for v in self.BASE])
        assert robust_scale(self.BASE) == pytest.approx(expected)

    def test_it_is_unchanged_by_the_order_of_the_values(self) -> None:
        assert robust_scale(self.BASE) == robust_scale(list(reversed(self.BASE)))

    def test_it_scales_with_the_data(self) -> None:
        doubled = [v * 2 for v in self.BASE]
        assert robust_scale(doubled) == pytest.approx(robust_scale(self.BASE) * 2)

    def test_a_shift_leaves_it_alone(self) -> None:
        shifted = [v + 500 for v in self.BASE]
        assert robust_scale(shifted) == pytest.approx(robust_scale(self.BASE))


class TestTheFallbackWhenTheMedianDeviationIsZero:
    def test_a_majority_of_identical_values_still_yields_a_scale(self) -> None:
        # MAD is 0 when more than half the values sit on the median. Returning
        # 0 there would make every residual infinite or undefined, so the
        # docstring's second clause takes over.
        values = [5.0, 5.0, 5.0, 5.0, 9.0]
        assert statistics.median([abs(v - statistics.median(values)) for v in values]) == 0
        assert robust_scale(values) > 0

    def test_the_fallback_is_the_scaled_mean_absolute_deviation(self) -> None:
        values = [5.0, 5.0, 5.0, 5.0, 9.0]
        median = statistics.median(values)
        deviations = [abs(v - median) for v in values]
        expected = (sum(deviations) / len(deviations)) / 1.4826
        assert robust_scale(values) == pytest.approx(expected)

    def test_values_with_no_spread_at_all_return_zero(self) -> None:
        # There is no scale to report, and inventing one would manufacture
        # residuals out of identical measurements.
        assert robust_scale([7.0, 7.0, 7.0]) == 0.0


class TestTooFewValuesToScale:
    @pytest.mark.parametrize("values", [[], [7.0]])
    def test_fewer_than_two_values_return_zero_rather_than_raise(
        self, values: list[float]
    ) -> None:
        assert robust_scale(values) == 0.0


class TestSourceTopicPrefersWhatWasDeclared:
    def _write(self, tmp_path: Path, name: str, payload) -> Path:
        target = tmp_path / name
        target.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        return target

    @pytest.mark.parametrize("key", ["tema", "topic", "titulo", "title"])
    def test_a_declared_topic_wins_over_the_filename(
        self, tmp_path: Path, key: str
    ) -> None:
        path = self._write(tmp_path, "20260904-algo_generico.json", {key: "Tema real"})
        assert source_topic(path) == "Tema real"

    @pytest.mark.parametrize("key", ["tema", "topic", "titulo", "title"])
    def test_a_topic_nested_under_meta_is_found(self, tmp_path: Path, key: str) -> None:
        path = self._write(tmp_path, "doc.json", {"meta": {key: "Tema anidado"}})
        assert source_topic(path) == "Tema anidado"

    def test_a_blank_declaration_does_not_count_as_declared(
        self, tmp_path: Path
    ) -> None:
        path = self._write(tmp_path, "20260904-nombre_util.json", {"tema": "   "})
        assert source_topic(path) == "nombre util"

    def test_the_filename_carries_the_topic_when_nothing_is_declared(
        self, tmp_path: Path
    ) -> None:
        path = self._write(tmp_path, "20260904-estudio_de_campo.json", {})
        assert source_topic(path) == "estudio de campo"

    def test_unreadable_json_falls_back_instead_of_raising(
        self, tmp_path: Path
    ) -> None:
        path = tmp_path / "20260904-roto.json"
        path.write_text("{no es json", encoding="utf-8")
        assert source_topic(path) == "roto"

    def test_a_missing_file_falls_back_instead_of_raising(
        self, tmp_path: Path
    ) -> None:
        assert source_topic(tmp_path / "20260904-ausente.json") == "ausente"

    def test_a_nameless_document_says_so_rather_than_returning_empty(
        self, tmp_path: Path
    ) -> None:
        # An empty topic string would read as a real topic downstream.
        path = self._write(tmp_path, "20260904-.json", {})
        assert source_topic(path) == "(sin tema)"

    @pytest.mark.parametrize("separator", ["-", "_"])
    def test_the_date_is_stripped_whatever_separator_follows_it(
        self, tmp_path: Path, separator: str
    ) -> None:
        # Both forms are on disk, 13 against 8. Accepting only `-` left the
        # date inside the topic for the other, so the same subject filed on two
        # days read as two topics -- and residuals are grouped by topic, so a
        # split group means a scale computed from fewer samples.
        path = self._write(tmp_path, f"20260726{separator}estudio_de_campo.json", {})
        assert source_topic(path) == "estudio de campo"

    def test_a_timestamped_name_loses_the_time_too(self, tmp_path: Path) -> None:
        path = self._write(tmp_path, "20260726-1430-estudio.json", {})
        assert source_topic(path) == "estudio"

    def test_a_number_that_is_not_a_date_is_kept(self, tmp_path: Path) -> None:
        # The topic of a document about the year 1999 is not "".
        path = self._write(tmp_path, "1999-retrospectiva.json", {})
        assert source_topic(path) == "1999 retrospectiva"


class TestArtifactDimensions:
    def test_the_mode_is_the_first_path_component(self, tmp_path: Path) -> None:
        doc = tmp_path / "doc.json"
        doc.write_text(json.dumps({"tema": "T"}), encoding="utf-8")
        mode, topic, route = artifact_dimensions(str(doc), "informes/2026/doc.json")
        assert mode == "informes"
        assert topic == "T"
        assert route == "research/informes/2026"

    def test_a_bare_filename_reports_no_mode_rather_than_crashing(
        self, tmp_path: Path
    ) -> None:
        doc = tmp_path / "doc.json"
        doc.write_text(json.dumps({"tema": "T"}), encoding="utf-8")
        mode, _topic, route = artifact_dimensions(str(doc), "doc.json")
        assert mode == "doc.json"
        assert route == "research"

    def test_the_route_always_starts_at_research(self, tmp_path: Path) -> None:
        doc = tmp_path / "doc.json"
        doc.write_text(json.dumps({"tema": "T"}), encoding="utf-8")
        for relative in ("a/doc.json", "a/b/doc.json", "doc.json"):
            _mode, _topic, route = artifact_dimensions(str(doc), relative)
            assert route.split("/")[0] == "research"
