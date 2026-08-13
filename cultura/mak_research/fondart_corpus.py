#!/usr/bin/env python3
"""Build a source-preserving Fondart selected-project corpus.

This is a research project, not an opportunity card.  It records the gap
between a public result document, a normalized application row, and a possible
cross-document coincidence.  A coincidence is never promoted to one project
silently: the match method and its evidence remain queryable.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sqlite3
from typing import Any, Callable
from urllib.parse import urlsplit

from source_pipeline import (SourceCorpusStore, canonical_url, capture_url,
                             discover_urls, is_official_fondart_url, is_pdf_url)


DEFAULT_SEEDS = (
    "https://www.fondosdecultura.cl/resultados-anteriores/",
    "https://www.fondosdecultura.cl/resultados/",
)
DEFAULT_QUERY = (
    "site:fondosdecultura.cl Fondart resultados proyectos seleccionados "
    "Fondart Regional PDF"
)
DEFAULT_DISCOVERY_YEARS = tuple(range(2015, 2026))
ROW_SPLIT = re.compile(r"\s{2,}")
FOLIO = re.compile(r"^\d{5,}$")
YEAR = re.compile(r"\b(20\d{2})\b")
RESULT_YEAR = re.compile(r"RESULTADOS\s+FONDOS\s+(20\d{2})", re.I)
CALL_YEAR = re.compile(r"CONVOCATORIA\s+(20\d{2})", re.I)
ROW_ANCHOR = re.compile(
    r"^\s*(?P<order>\d+)\s+(?P<region>.*?)\s+(?P<folio>\d{5,})\s+(?P<tail>.+?)\s*$"
)
AMOUNT = re.compile(r"\$\s*[\d.]+")


def _fold(value: str) -> str:
    import unicodedata
    value = unicodedata.normalize("NFKD", value.lower())
    value = "".join(char for char in value if not unicodedata.combining(char))
    return re.sub(r"[^a-z0-9]+", " ", value).strip()


def _reported_year(text: str) -> int | None:
    match = RESULT_YEAR.search(text)
    if match:
        return int(match.group(1))
    match = CALL_YEAR.search(text)
    if match:
        return int(match.group(1))
    for line in text.splitlines()[:80]:
        if "FONDART" in line.upper():
            match = YEAR.search(line)
            if match:
                return int(match.group(1))
    return None


def _url_year(url: str) -> int | None:
    matches = YEAR.findall(url)
    return int(matches[-1]) if matches else None


def _columns(line: str) -> list[str]:
    return [value.strip() for value in ROW_SPLIT.split(line.strip()) if value.strip()]


def _new_row(line: str) -> dict[str, Any] | None:
    columns = _columns(line)
    if len(columns) < 5 or not columns[0].isdigit():
        return None
    folio_at = next((index for index, value in enumerate(columns[1:], 1)
                     if FOLIO.fullmatch(value)), None)
    if folio_at is None or folio_at + 2 >= len(columns):
        return None
    amount_at = next((index for index in range(len(columns) - 1, folio_at, -1)
                      if columns[index].startswith("$")), None)
    if amount_at is None:
        return None
    between = columns[folio_at + 2:amount_at]
    if not between:
        return None
    return {
        "source_order": int(columns[0]),
        "region": columns[folio_at - 1],
        "folio": columns[folio_at],
        "area_or_modality": columns[folio_at + 1],
        "title": between[0],
        "responsible": between[1] if len(between) > 1 else "",
        "amount_raw": columns[amount_at],
        "raw_lines": [line.rstrip()],
        "partial": len(between) < 2,
    }


def _anchored_partial_row(line: str) -> dict[str, Any] | None:
    """Keep a table row when the PDF interleaves its visual columns.

    ``pdftotext -layout`` can place title and responsible fragments before or
    after the line carrying number/folio/amount.  Inventing those fragments
    would create false application identities, so the fallback keeps only the
    anchor fields visible on one line and marks the record partial.
    """
    match = ROW_ANCHOR.match(line)
    if not match:
        return None
    amount = AMOUNT.search(match.group("tail"))
    if not amount:
        return None
    before_amount = match.group("tail")[:amount.start()].strip()
    fields = _columns(before_amount)
    return {
        "source_order": int(match.group("order")),
        "region": match.group("region").strip(),
        "folio": match.group("folio"),
        "area_or_modality": fields[0] if fields else "",
        "title": " ".join(fields[1:]),
        "responsible": "",
        "amount_raw": amount.group(0),
        "raw_lines": [line.rstrip()],
        "partial": True,
    }


def _table_columns(row: list[str]) -> dict[str, int]:
    columns: dict[str, int] = {}
    for index, cell in enumerate(row):
        folded = _fold(cell)
        if "folio" in folded:
            columns["folio"] = index
        elif "region" in folded:
            columns["region"] = index
        elif "modalidad" in folded:
            columns["modality"] = index
        elif "titulo" in folded:
            columns["title"] = index
        elif "responsable" in folded:
            columns["responsible"] = index
        elif "monto" in folded:
            columns["amount"] = index
    return columns


def _cell(row: list[str], columns: dict[str, int], name: str) -> str:
    index = columns.get(name)
    return row[index].strip() if index is not None and index < len(row) else ""


def parse_selected_table_rows(tables: list[dict[str, Any]], *, source_url: str,
                              capture_id: str, reported_year: int | None) -> list[dict[str, Any]]:
    """Normalize PDF table cells while retaining selection boundaries.

    A table-aware backend provides cells, but result PDFs can include selected
    and waiting-list tables on the same page. The text labels still control
    whether a row is admissible; a table alone never implies selection.
    """
    rows: list[dict[str, Any]] = []
    selected = True
    waiting_list = False
    columns: dict[str, int] = {}
    source_year = _url_year(source_url)
    for table in tables:
        raw_rows = [row for row in table.get("rows") or [] if isinstance(row, list)]
        table_has_wait_marker = any(
            any(token in _fold(" ".join(str(cell or "") for cell in row))
                for token in ("lista de espera", "no seleccion", "proyectos no seleccion"))
            for row in raw_rows
        )
        table_has_header = any(
            "folio" in _table_columns([str(cell or "").strip() for cell in row])
            and "title" in _table_columns([str(cell or "").strip() for cell in row])
            for row in raw_rows
        )
        # Some PDFs put a waiting-list label in one table and the next
        # selected line's header/data in the following table. The waiting
        # state is row-local inside one table; it must not leak across that
        # explicit table boundary.
        if table_has_header and not table_has_wait_marker:
            selected = True
            waiting_list = False
        for raw_row in raw_rows:
            if not isinstance(raw_row, list):
                continue
            row = [str(cell or "").strip() for cell in raw_row]
            folded = _fold(" ".join(row))
            if not folded:
                continue
            if ("lista de espera" in folded or "no seleccion" in folded
                    or "proyectos no seleccion" in folded):
                selected = False
                waiting_list = True
                continue
            candidate_columns = _table_columns(row)
            if "folio" in candidate_columns and "title" in candidate_columns:
                columns = candidate_columns
                continue
            if waiting_list and folded.startswith("linea "):
                selected = True
                waiting_list = False
                continue
            if "linea " in folded and "espera" not in folded and not columns:
                selected = True
                waiting_list = False
                continue
            folio = _cell(row, columns, "folio")
            source_order = row[0] if row else ""
            amount = _cell(row, columns, "amount")
            if not selected or not source_order.isdigit() or not FOLIO.fullmatch(folio) or not amount:
                continue
            title = _cell(row, columns, "title")
            responsible = _cell(row, columns, "responsible")
            rows.append({
                "source_order": int(source_order),
                "region": _cell(row, columns, "region"),
                "folio": folio,
                "area_or_modality": _cell(row, columns, "modality"),
                "title": title,
                "responsible": responsible,
                "amount_raw": amount,
                "raw_lines": [" | ".join(row)],
                "partial": not bool(title and responsible),
                "source_text": " | ".join(row),
                "reported_year": reported_year,
                "source_url_year": source_year,
                "source_url": source_url,
                "capture_id": capture_id,
                "selected_status": "selected",
            })
    return rows


def parse_selected_records(text: str, *, source_url: str,
                           capture_id: str) -> list[dict[str, Any]]:
    """Parse only explicit selected-project table rows from a result PDF.

    Layout changes between years are preserved as partial records instead of
    being guessed.  A row under "LISTA DE ESPERA" is intentionally excluded.
    """
    selected = False
    waiting_list = False
    active: dict[str, Any] | None = None
    rows: list[dict[str, Any]] = []
    reported_year = _reported_year(text)
    source_year = _url_year(source_url)

    def flush() -> None:
        nonlocal active
        if active is None:
            return
        active["source_text"] = "\n".join(active.pop("raw_lines"))
        active["reported_year"] = reported_year
        active["source_url_year"] = source_year
        active["source_url"] = source_url
        active["capture_id"] = capture_id
        active["selected_status"] = "selected"
        rows.append(active)
        active = None

    for line in text.splitlines():
        folded = _fold(line)
        if "nomina de proyectos seleccionados" in folded:
            flush()
            selected = True
            waiting_list = False
            continue
        if ("lista de espera" in folded or "no seleccion" in folded
                or "proyectos no seleccion" in folded):
            flush()
            selected = False
            waiting_list = True
            continue
        if waiting_list and folded.startswith("linea "):
            # The PDF repeats a selected table for each line. A wait list
            # belongs only to the preceding line, not to the remainder of the
            # document.
            selected = True
            waiting_list = False
        if not selected:
            continue
        candidate = _new_row(line) or _anchored_partial_row(line)
        if candidate:
            flush()
            active = candidate
        elif active is not None and line.strip():
            active["raw_lines"].append(line.rstrip())
    flush()
    return rows


def _amount(value: str) -> int | None:
    digits = re.sub(r"[^0-9]", "", value or "")
    return int(digits) if digits else None


def _candidate_key(record: dict[str, Any]) -> tuple[str, str]:
    """Return a merge key only when the document itself provides enough data."""
    year = record.get("reported_year")
    title = _fold(str(record.get("title") or ""))
    person = _fold(str(record.get("responsible") or ""))
    if year and title and person:
        raw = "title-responsible-year|%s|%s|%s" % (year, title, person)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest(), "title_responsible_year"
    raw = "source-folio|%s|%s" % (record["capture_id"], record["folio"])
    return hashlib.sha256(raw.encode("utf-8")).hexdigest(), "source_folio_only"


class FondartCorpusStore:
    def __init__(self, root: str | Path) -> None:
        self.sources = SourceCorpusStore(root)
        self.root = self.sources.root
        with self.sources._connect() as conn:  # shared project provenance database
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS fondart_applications (
                    application_id TEXT PRIMARY KEY, capture_id TEXT NOT NULL,
                    source_folio TEXT NOT NULL, source_order INTEGER,
                    reported_year INTEGER, source_url_year INTEGER,
                    region TEXT NOT NULL, area_or_modality TEXT NOT NULL,
                    project_title TEXT NOT NULL, responsible TEXT NOT NULL,
                    amount_raw TEXT NOT NULL, amount_clp INTEGER,
                    selected_status TEXT NOT NULL, partial INTEGER NOT NULL,
                    source_text TEXT NOT NULL, source_url TEXT NOT NULL,
                    UNIQUE(capture_id, source_folio)
                );
                CREATE TABLE IF NOT EXISTS fondart_coincidence_groups (
                    group_id TEXT PRIMARY KEY, match_key TEXT UNIQUE NOT NULL,
                    match_method TEXT NOT NULL, review_status TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS fondart_application_coincidences (
                    application_id TEXT NOT NULL, group_id TEXT NOT NULL,
                    match_method TEXT NOT NULL, confidence TEXT NOT NULL,
                    PRIMARY KEY(application_id, group_id),
                    FOREIGN KEY(application_id) REFERENCES fondart_applications(application_id),
                    FOREIGN KEY(group_id) REFERENCES fondart_coincidence_groups(group_id)
                );
            """)

    def ingest(self, records: list[dict[str, Any]]) -> int:
        inserted = 0
        with self.sources._connect() as conn:
            for record in records:
                application_id = hashlib.sha256(
                    (record["capture_id"] + "|" + record["folio"]).encode("utf-8")).hexdigest()
                result = conn.execute("""
                    INSERT OR IGNORE INTO fondart_applications
                    (application_id, capture_id, source_folio, source_order, reported_year,
                     source_url_year, region, area_or_modality, project_title, responsible,
                     amount_raw, amount_clp, selected_status, partial, source_text, source_url)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (application_id, record["capture_id"], record["folio"],
                      record.get("source_order"), record.get("reported_year"),
                      record.get("source_url_year"), record.get("region") or "",
                      record.get("area_or_modality") or "", record.get("title") or "",
                      record.get("responsible") or "", record.get("amount_raw") or "",
                      _amount(record.get("amount_raw") or ""), record["selected_status"],
                      int(bool(record.get("partial"))), record.get("source_text") or "",
                      record["source_url"]))
                inserted += int(result.rowcount > 0)
                # The application key is the immutable source boundary. A
                # second parser variant for the same capture/folio must not
                # create a second coincidence group for the already stored
                # application.
                if result.rowcount == 0:
                    continue
                key, method = _candidate_key(record)
                group_id = hashlib.sha256(("group|" + key).encode("utf-8")).hexdigest()
                conn.execute("""
                    INSERT OR IGNORE INTO fondart_coincidence_groups
                    (group_id, match_key, match_method, review_status)
                    VALUES (?, ?, ?, 'unreviewed')
                """, (group_id, key, method))
                conn.execute("""
                    INSERT OR IGNORE INTO fondart_application_coincidences
                    (application_id, group_id, match_method, confidence)
                    VALUES (?, ?, ?, ?)
                """, (application_id, group_id, method,
                      "candidate" if method == "title_responsible_year" else "source_only"))
        return inserted

    def summary(self) -> dict[str, Any]:
        with self.sources._connect() as conn:
            count = conn.execute("SELECT COUNT(*) FROM fondart_applications").fetchone()[0]
            partial = conn.execute("SELECT COUNT(*) FROM fondart_applications WHERE partial=1").fetchone()[0]
            years = [row[0] for row in conn.execute(
                "SELECT DISTINCT reported_year FROM fondart_applications "
                "WHERE reported_year IS NOT NULL ORDER BY reported_year")]
            group_count = conn.execute("SELECT COUNT(*) FROM fondart_coincidence_groups").fetchone()[0]
        return {"applications": int(count), "partial_records": int(partial),
                "reported_years": years, "coincidence_groups": int(group_count),
                **self.sources.summary()}


def _official_candidates(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [row for row in rows if is_official_fondart_url(row["url"])]


def _fondart_document_priority(url: str, *, evidence_text: str = "") -> tuple[int, int, str] | None:
    """Rank actual Fondart result documents ahead of adjacent fund PDFs.

    The official results archive contains Libro, Musica, Audiovisual, juror,
    and legal-resolution documents next to Fondart tables. The bounded crawl
    must not spend its document budget on those neighbors merely because they
    appear earlier in the page.
    """
    normalized = canonical_url(url)
    folded = _fold(normalized)
    evidence = _fold(evidence_text)
    if not is_official_fondart_url(normalized) or not is_pdf_url(normalized):
        return None
    combined = folded + " " + evidence
    fondart_marker = any(token in combined for token in ("fondart", "fdrt", "fregional"))
    result_marker = any(token in combined for token in
                        ("resultado", "result", "nomina", "seleccion", "seleccionado",
                         "selected"))
    if (not fondart_marker or not result_marker or any(token in combined for token in
                                                       ("jurado", "evaluador", "bases concurso",
                                                        "bases tecnicas", "antecedentes de la convocatoria",
                                                        "presentacion fondart", "se publicara",
                                                        "postulacion", "requisitos de la convocatoria"))):
        return None
    score = 0
    if any(token in combined for token in ("resultado", "nomina", "seleccion")):
        score += 100
    if "regional" in folded:
        score += 10
    if "nacional" in folded:
        score += 5
    if "rex" in folded:
        score -= 5
    year = _url_year(normalized) or 0
    return (-score, -year, normalized)


def _prioritized_fondart_candidates(
        candidates: list[dict[str, Any]], *,
        preferred_years: tuple[int, ...] = ()) -> list[dict[str, Any]]:
    deduped: dict[str, dict[str, Any]] = {}
    for candidate in candidates:
        url = canonical_url(str(candidate.get("url") or ""))
        if not url:
            continue
        current = deduped.setdefault(url, dict(candidate, url=url))
        for field in ("title", "snippet"):
            value = str(candidate.get(field) or "").strip()
            if value and value not in str(current.get(field) or ""):
                current[field] = (str(current.get(field) or "") + " " + value).strip()
    preferred = set(preferred_years)
    ranked = []
    for candidate in deduped.values():
        evidence = "%s %s" % (candidate.get("title") or "", candidate.get("snippet") or "")
        priority = _fondart_document_priority(candidate["url"], evidence_text=evidence)
        if priority is not None:
            year = _url_year(candidate["url"])
            scope_penalty = 0 if not preferred or year in preferred else 1
            ranked.append(((scope_penalty, *priority), candidate))
    ranked.sort()
    first_by_year: list[tuple[tuple[int, int, int, str], dict[str, Any]]] = []
    remainder: list[tuple[tuple[int, int, int, str], dict[str, Any]]] = []
    seen_years: set[int] = set()
    for priority, candidate in ranked:
        year = _url_year(candidate["url"])
        if year is not None and year not in seen_years:
            first_by_year.append((priority, candidate))
            seen_years.add(year)
        else:
            remainder.append((priority, candidate))
    # One high-quality candidate per named year first prevents a fixed document
    # budget from being spent on Nacional/Regional variants of the same call.
    return [candidate for _priority, candidate in first_by_year + remainder]


def _prioritized_fondart_documents(urls: list[str]) -> list[str]:
    return [candidate["url"] for candidate in _prioritized_fondart_candidates(
        [{"url": url} for url in urls]
    )]


def _is_result_index_url(url: str) -> bool:
    if not is_official_fondart_url(url) or is_pdf_url(url):
        return False
    parts = urlsplit(canonical_url(url))
    path = parts.path.casefold()
    host = (parts.hostname or "").casefold()
    return "resultado" in path or "archivo" in path or host.startswith("archivos.")


def _year_query(year: int) -> str:
    return "site:fondosdecultura.cl Fondart Regional resultados nomina seleccionados %d PDF" % year


def _dedupe_candidates(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    deduped: dict[str, dict[str, Any]] = {}
    for row in rows:
        url = canonical_url(row.get("url") or "")
        if not url:
            continue
        deduped.setdefault(url, dict(row, url=url))
    return list(deduped.values())


def _candidate_in_year_scope(row: dict[str, Any], years: tuple[int, ...]) -> bool:
    """Keep unlabelled sources eligible, but do not spend a bounded run on a
    document explicitly labelled outside its requested historical range."""
    year = _url_year(str(row.get("url") or ""))
    return year is None or year in set(years)


def plan_fondart_corpus(*, query: str = DEFAULT_QUERY,
                        seed_urls: tuple[str, ...] = DEFAULT_SEEDS,
                        search: Callable[..., dict[str, Any]] | None = None,
                        discovery_years: tuple[int, ...] = DEFAULT_DISCOVERY_YEARS) -> dict[str, Any]:
    """Discover official candidates without downloading a source document."""
    if search is None:
        from research_lib import web_search
        search = web_search
    discoveries = _official_candidates(discover_urls(query, search, max_results=40))
    for year in discovery_years:
        discoveries.extend(_official_candidates(discover_urls(
            _year_query(year), search, max_results=8)))
    discovered = _dedupe_candidates(discoveries)
    known = {row["url"] for row in discovered}
    for index, url in enumerate(seed_urls, 1):
        normalized = canonical_url(url)
        if normalized and normalized not in known:
            discovered.append({"query": "seed", "rank": index, "url": normalized,
                               "title": "Official Fondart results seed", "snippet": "",
                               "search_backend": "seed"})
            known.add(normalized)
    return {
        "schema": "mak-fondart-corpus-plan-v1",
        "status": "unreviewed",
        "query": query,
        "candidates": discovered,
        "discoveries": discoveries,
        "discovery_years": list(discovery_years),
        "execution": {
            "capture_only_official_hosts": True,
            "source_first": True,
            "promotion": "none",
            "next_action": "capture planned official result pages and PDF records",
        },
    }


def build_fondart_corpus(root: str | Path, *, query: str = DEFAULT_QUERY,
                         seed_urls: tuple[str, ...] = DEFAULT_SEEDS,
                         search: Callable[..., dict[str, Any]] | None = None,
                         capture: Callable[..., dict[str, Any]] = capture_url,
                         max_documents: int = 12,
                         discovery_years: tuple[int, ...] = DEFAULT_DISCOVERY_YEARS) -> dict[str, Any]:
    """Run discovery -> capture -> selected-row normalization -> quality gate."""
    store = FondartCorpusStore(root)
    plan = plan_fondart_corpus(query=query, seed_urls=seed_urls, search=search,
                               discovery_years=discovery_years)
    discovered = list(plan["candidates"])
    store.sources.record_discovery(list(plan["discoveries"]))

    page_rows = [row for row in discovered if _is_result_index_url(row["url"])][:8]
    pdf_candidates = [row for row in discovered
                      if is_pdf_url(row["url"])
                      and _candidate_in_year_scope(row, DEFAULT_DISCOVERY_YEARS)]
    captures: list[tuple[dict[str, Any], dict[str, Any]]] = []
    for row in page_rows:
        result = capture(row["url"])
        receipt = store.sources.record_capture(result)
        captures.append((result, receipt))
        linked_records = result.get("link_records") or []
        seen_links: set[str] = set()
        for record in linked_records:
            if not isinstance(record, dict):
                continue
            link = str(record.get("url") or "")
            seen_links.add(link)
            linked = {"url": link}
            if (is_official_fondart_url(link) and is_pdf_url(link)
                    and _candidate_in_year_scope(linked, DEFAULT_DISCOVERY_YEARS)):
                pdf_candidates.append({
                    "url": link, "title": str(record.get("title") or ""),
                    "snippet": "", "query": "result_index_link", "rank": 0,
                    "search_backend": "capture",
                })
        for link in result.get("links") or []:
            if link in seen_links:
                continue
            linked = {"url": link}
            if (is_official_fondart_url(link) and is_pdf_url(link)
                    and _candidate_in_year_scope(linked, DEFAULT_DISCOVERY_YEARS)):
                pdf_candidates.append({"url": link, "title": "", "snippet": "",
                                       "query": "result_index_link", "rank": 0,
                                       "search_backend": "capture"})
    pdf_candidates = _prioritized_fondart_candidates(
        pdf_candidates, preferred_years=DEFAULT_DISCOVERY_YEARS)
    for candidate in pdf_candidates[:max(0, int(max_documents))]:
        url = candidate["url"]
        result = capture(url)
        receipt = store.sources.record_capture(result)
        captures.append((result, receipt))

    parsed: list[dict[str, Any]] = []
    source_errors: list[dict[str, str]] = []
    for result, receipt in captures:
        if result.get("status") != "captured":
            source_errors.append({"url": receipt["url"], "error": str(result.get("error") or "capture_failed")})
            continue
        if not is_pdf_url(receipt["url"], str(result.get("content_type") or "")):
            continue
        records = parse_selected_records(str(result.get("text") or ""),
                                         source_url=receipt["url"],
                                         capture_id=receipt["capture_id"])
        table_records = parse_selected_table_rows(
            result.get("tables") or [], source_url=receipt["url"],
            capture_id=receipt["capture_id"],
            reported_year=_reported_year(str(result.get("text") or "")),
        )
        if table_records:
            table_folios = {record["folio"] for record in table_records}
            records = table_records + [record for record in records
                                        if record["folio"] not in table_folios]
        if not records:
            source_errors.append({"url": receipt["url"], "error": "no_selected_rows_parsed"})
        parsed.extend(records)
    inserted = store.ingest(parsed)
    summary = store.summary()
    duplicate_source_rows = max(0, len(parsed) - inserted)
    complete_records = max(0, summary["applications"] - summary["partial_records"])
    requested_years = list(range(2015, 2026))
    covered = set(summary["reported_years"])
    missing = [year for year in requested_years if year not in covered]
    # Historical coverage alone is not a green light. A row without a stable
    # title/responsible boundary may be useful source evidence, but it cannot
    # support a coincident-application claim without a later table parser or
    # a human validation pass.
    quality_status = (
        "ready" if summary["applications"] and not missing and not summary["partial_records"]
        else "review_required"
    )
    quality = {
        "status": quality_status,
        "promotion": "none",
        "claim_safety": {
            "status": "ABSTAIN",
            "reason": "normalized selected rows require a human interpretation gate",
        },
        "requested_years": requested_years,
        "reported_years": summary["reported_years"],
        "out_of_scope_reported_years": [year for year in summary["reported_years"]
                                         if year not in requested_years],
        "missing_years": missing,
        "complete_records": complete_records,
        "partial_records": summary["partial_records"],
        "duplicate_source_rows": duplicate_source_rows,
        "source_errors": source_errors,
        "requirements": {
            "official_discovery": bool(discovered),
            "captured_sources": summary["captured"],
            "selected_application_records": summary["applications"],
            "complete_normalization": not bool(summary["partial_records"]),
            "source_provenance": True,
        },
    }
    report = (
        "Corpus Fondart: %d postulaciones adjudicadas normalizadas desde %d capturas "
        "(%d fallidas). Cobertura declarada: %s. Estado: %s."
        % (summary["applications"], summary["captured"], summary["failed"],
           ", ".join(map(str, summary["reported_years"])) or "sin anos verificados",
           quality_status)
    )
    return {
        "schema": "mak-fondart-corpus-v1", "project": "fondart_historical_selected",
        "query": query, "plan": plan, "discovered": discovered, "captures": [
            {"url": receipt["url"], "capture_id": receipt["capture_id"],
             "status": result.get("status"), "backend": result.get("backend"),
             "attempts": result.get("attempts", [])}
            for result, receipt in captures],
        "records_parsed": len(parsed), "records_inserted": inserted,
        "duplicate_source_rows": duplicate_source_rows,
        "summary": summary, "quality": quality, "report": report,
        "database": str(store.sources.db_path),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a source-preserving Fondart corpus")
    parser.add_argument("--root", required=True)
    parser.add_argument("--query", default=DEFAULT_QUERY)
    parser.add_argument("--max-documents", type=int, default=4)
    args = parser.parse_args()
    result = build_fondart_corpus(args.root, query=args.query,
                                  max_documents=args.max_documents)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["quality"]["status"] == "ready" else 2


if __name__ == "__main__":  # pragma: no cover - CLI exercised through integration use
    raise SystemExit(main())
