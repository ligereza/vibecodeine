import hashlib
import sys
from pathlib import Path
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "cultura" / "mak_research"))

import fondart_corpus  # noqa: E402
import source_pipeline  # noqa: E402


class FakeResponse:
    status = 200

    def __init__(self, body, url="https://example.test/page", content_type="text/html"):
        self.body = body
        self.url = url
        self.headers = {"Content-Type": content_type}

    def read(self, _limit=None):
        return self.body

    def geturl(self):
        return self.url

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False


def test_firecrawl_capture_preserves_actual_backend_and_links():
    def request_json(_url, _body, _headers, _timeout):
        return {"data": {"markdown": "# Result\nOfficial text", "links": [
            "https://example.test/a", {"url": "https://example.test/b"}],
            "metadata": {"sourceURL": "https://example.test/source", "statusCode": 200}}}

    result = source_pipeline.capture_url(
        "https://example.test/source", env={"FIRECRAWL_API_KEY": "test"},
        request_json=request_json,
    )

    assert result["status"] == "captured"
    assert result["backend"] == "firecrawl"
    assert result["links"] == ["https://example.test/a", "https://example.test/b"]
    assert result["attempts"] == [{"backend": "firecrawl", "status": "captured"}]


def test_firecrawl_failure_is_visible_before_stdlib_fallback():
    def request_json(*_args):
        raise RuntimeError("quota")

    def opener(_request, timeout):
        assert timeout == source_pipeline.DEFAULT_TIMEOUT
        return FakeResponse(b"<h1>Fallback</h1><a href='/record.pdf'>PDF</a>")

    result = source_pipeline.capture_url(
        "https://example.test/source", env={"FIRECRAWL_API_KEY": "test"},
        request_json=request_json, opener=opener,
    )

    assert result["status"] == "captured"
    assert result["backend"] == "urllib"
    assert result["attempts"][0]["backend"] == "firecrawl"
    assert result["attempts"][0]["status"] == "failed"
    assert result["links"] == ["https://example.test/record.pdf"]


def test_pdf_capture_uses_text_extractor_and_does_not_decode_binary_as_html():
    def opener(_request, timeout):
        return FakeResponse(b"%PDF-not-utf8\xff", url="https://example.test/results.pdf",
                            content_type="application/pdf")

    with patch.object(source_pipeline, "extract_pdf_text", return_value=("FOLIO 123", "")):
        result = source_pipeline.capture_url("https://example.test/results.pdf",
                                             env={}, opener=opener)

    assert result["status"] == "captured"
    assert result["text"] == "FOLIO 123"
    assert result["backend"] == "urllib"


def test_pdf_capture_preserves_table_artifact_when_available():
    def opener(_request, timeout):
        return FakeResponse(b"%PDF-test", url="https://example.test/results.pdf",
                            content_type="application/pdf")

    with patch.object(source_pipeline, "extract_pdf_text", return_value=("FOLIO 123", "")), \
         patch.object(source_pipeline, "extract_pdf_tables", return_value=(
             [{"page": 1, "rows": [["FOLIO", "TITULO"], ["123", "Obra"]]}], "")):
        result = source_pipeline.capture_url("https://example.test/results.pdf",
                                             env={}, opener=opener)

    assert result["metadata"]["pdf_table_backend"] == "pdfplumber"
    assert result["tables"][0]["page"] == 1


def test_html_capture_preserves_anchor_titles_for_later_source_classification():
    def opener(_request, timeout):
        return FakeResponse(
            b'<a href="/resultados-2015.pdf">Resolucion Fondart Regional seleccionados</a>',
            url="https://example.test/archive",
        )

    result = source_pipeline.capture_url(
        "https://example.test/archive", env={}, opener=opener)

    assert result["links"] == ["https://example.test/resultados-2015.pdf"]
    assert result["link_records"] == [{
        "url": "https://example.test/resultados-2015.pdf",
        "title": "Resolucion Fondart Regional seleccionados",
    }]


def test_pdf_extractor_falls_back_to_optional_cross_platform_backend(monkeypatch):
    monkeypatch.setattr(source_pipeline.subprocess, "run",
                        lambda *_args, **_kwargs: (_ for _ in ()).throw(FileNotFoundError()))
    monkeypatch.setattr(source_pipeline, "_pypdf_extract", lambda _raw: "Portable PDF text")

    text, error = source_pipeline.extract_pdf_text(b"%PDF-test")

    assert text == "Portable PDF text"
    assert error == ""


def test_source_store_preserves_discovery_capture_and_failure(tmp_path):
    store = source_pipeline.SourceCorpusStore(tmp_path)
    store.record_discovery([{"query": "fondart", "rank": 1,
                            "url": "https://example.test/a", "title": "A",
                            "snippet": "s", "search_backend": "test"}])
    good = store.record_capture({"url": "https://example.test/a", "status": "captured",
                                 "backend": "urllib", "http_status": 200,
                                 "content_type": "text/html", "raw_sha256": "r",
                                 "text": "Evidence", "links": [], "error": "", "metadata": {}})
    store.record_capture({"url": "https://example.test/b", "status": "failed",
                          "backend": "none", "text": "", "links": [],
                          "error": "blocked", "metadata": {}})

    assert Path(good["text_path"]).read_text(encoding="utf-8") == "Evidence"
    assert store.summary() == {"discovered": 1, "captured": 1, "failed": 1}
    with store._connect() as conn:
        metadata = __import__("json").loads(conn.execute(
            "SELECT metadata_json FROM source_captures WHERE status='captured'").fetchone()[0])
    assert metadata["links"] == []


def test_imported_crawl4ai_batch_keeps_original_capture_boundary(tmp_path):
    export = tmp_path / "crawl.json"
    export.write_text(__import__("json").dumps({
        "batch_id": "fondart-2027", "captured_at_utc": "2026-08-11T14:37:28Z",
        "crawler": "Crawl4AI", "browser": "system Chrome", "interpretation": "none",
        "results": [{"url": "https://fondosdecultura.cl/a", "success": True,
                     "markdown": "literal source", "error_message": None},
                    {"url": "https://fondosdecultura.cl/b", "success": False,
                     "markdown": "", "error_message": "blocked"}],
    }), encoding="utf-8")
    store = source_pipeline.SourceCorpusStore(tmp_path / "derived")

    result = source_pipeline.import_crawl4ai_export(export, store)

    assert result == {"captured": 1, "failed": 1}
    assert store.summary() == {"discovered": 0, "captured": 1, "failed": 1}
    with store._connect() as conn:
        metadata = __import__("json").loads(conn.execute(
            "SELECT metadata_json FROM source_captures WHERE status='captured'").fetchone()[0])
    assert metadata["batch_id"] == "fondart-2027"
    assert metadata["interpretation"] == "none"


def test_fondart_parser_excludes_waiting_list_and_keeps_reported_year_distinct():
    text = """
    NOMINA DE PROYECTOS SELECCIONADOS
    1  Arica y  446084  Unica  Patrimonio Familia  Daniel Castillo  $4.081.000
    LISTA DE ESPERA
    2  Arica y  453688  Unica  No debe entrar  Persona Espera  $8.234.289
    RESULTADOS FONDOS 2016
    """
    records = fondart_corpus.parse_selected_records(
        text, source_url="https://fondosdecultura.cl/wp-content/uploads/2017/12/results-2018.pdf",
        capture_id="capture")

    assert len(records) == 1
    assert records[0]["folio"] == "446084"
    assert records[0]["reported_year"] == 2016
    assert records[0]["source_url_year"] == 2018
    assert records[0]["selected_status"] == "selected"


def test_fondart_parser_keeps_layout_interleaved_rows_as_partial_not_missing():
    text = """
    NOMINA DE PROYECTOS SELECCIONADOS - CONVOCATORIA 2020
    1  Arica y Parinacota  542505  Unica                                 $ 4.941.844
    2  Arica y Parinacota  539251  Unica  Fotobiblioteca                  $ 2.359.699
    LISTA DE ESPERA
    3  Arica y Parinacota  542742  Unica                                 $ 13.115.000
    """

    records = fondart_corpus.parse_selected_records(
        text, source_url="https://fondosdecultura.cl/fondart-2020.pdf",
        capture_id="capture")

    assert [record["folio"] for record in records] == ["542505", "539251"]
    assert all(record["partial"] for record in records)
    assert records[0]["reported_year"] == 2020
    assert records[1]["title"] == "Fotobiblioteca"


def test_fondart_parser_resumes_selected_rows_after_a_waiting_list_section():
    text = """
    NOMINA DE PROYECTOS SELECCIONADOS - CONVOCATORIA 2020
    1  Arica y Parinacota  542505  Unica                                 $ 4.941.844
    LISTA DE ESPERA - LINEA ACTIVIDADES FORMATIVAS
    2  Arica y Parinacota  542742  Unica                                 $ 13.115.000
    LINEA DIFUSION
    3  Arica y Parinacota  550490  Unica                                 $ 13.980.755
    """

    records = fondart_corpus.parse_selected_records(
        text, source_url="https://fondosdecultura.cl/fondart-2020.pdf",
        capture_id="capture")

    assert [record["folio"] for record in records] == ["542505", "550490"]


def test_table_rows_keep_complete_selected_cells_and_exclude_waiting_list():
    tables = [{"page": 1, "rows": [
        ["LINEA ACTIVIDADES FORMATIVAS", "", "", "", "", "", ""],
        ["Nº", "REGION", "FOLIO", "MODALIDAD", "TITULO DEL PROYECTO", "RESPONSABLE", "MONTO"],
        ["1", "Arica", "542505", "Unica", "Obra seleccionada", "Ana Persona", "$ 4.941.844"],
        ["LISTA DE ESPERA", "", "", "", "", "", ""],
        ["2", "Arica", "542742", "Unica", "No entra", "Otra Persona", "$ 13.115.000"],
        ["LINEA DIFUSION", "", "", "", "", "", ""],
        ["Nº", "REGION", "FOLIO", "MODALIDAD", "TITULO DEL PROYECTO", "RESPONSABLE", "MONTO"],
        ["3", "Arica", "550490", "Unica", "Otra seleccionada", "Bea Persona", "$ 13.980.755"],
    ]}]

    records = fondart_corpus.parse_selected_table_rows(
        tables, source_url="https://fondosdecultura.cl/fondart-2020.pdf",
        capture_id="capture", reported_year=2020)

    assert [record["folio"] for record in records] == ["542505", "550490"]
    assert all(record["partial"] is False for record in records)


def test_table_waiting_state_does_not_leak_into_next_selected_table():
    tables = [
        {"page": 1, "rows": [["LISTA DE ESPERA - LINEA A"], ["Se declara desierta"]]},
        {"page": 1, "rows": [
            ["Nº", "REGION", "FOLIO", "MODALIDAD", "TITULO DEL PROYECTO",
             "RESPONSABLE", "MONTO"],
            ["1", "Arica", "542505", "Unica", "Obra seleccionada",
             "Ana Persona", "$ 4.941.844"],
        ]},
    ]

    records = fondart_corpus.parse_selected_table_rows(
        tables, source_url="https://fondosdecultura.cl/fondart-2020.pdf",
        capture_id="capture", reported_year=2020)

    assert [record["folio"] for record in records] == ["542505"]
    assert records[0]["partial"] is False


def test_fondart_project_requires_coverage_instead_of_reporting_success_early(tmp_path):
    pdf = """
    NOMINA DE PROYECTOS SELECCIONADOS
    1  Arica y  446084  Unica  Patrimonio Familia  Daniel Castillo  $4.081.000
    RESULTADOS FONDOS 2016
    """

    def search(_query, max_results):
        assert max_results == 40
        return {"motor": "test", "results": [
            {"url": "https://fondosdecultura.cl/resultados-anteriores/", "title": "archive", "content": ""}]}

    def capture(url):
        if url.endswith("resultados-anteriores/"):
            return {"url": url, "status": "captured", "backend": "urllib",
                    "http_status": 200, "content_type": "text/html", "raw_sha256": "page",
                    "text": "archive", "links": [
                        "https://fondosdecultura.cl/results-fondart-regional-2018.pdf"],
                    "error": "", "metadata": {}}
        return {"url": url, "status": "captured", "backend": "urllib",
                "http_status": 200, "content_type": "application/pdf", "raw_sha256": "pdf",
                "text": pdf, "links": [], "error": "", "metadata": {}}

    result = fondart_corpus.build_fondart_corpus(
        tmp_path, seed_urls=(), search=search, capture=capture, max_documents=1,
        discovery_years=())

    assert result["summary"]["applications"] == 1
    assert result["quality"]["status"] == "review_required"
    assert result["quality"]["promotion"] == "none"
    assert result["quality"]["requirements"]["complete_normalization"] is True
    assert result["plan"]["status"] == "unreviewed"
    assert 2016 in result["quality"]["reported_years"]
    assert 2015 in result["quality"]["missing_years"]
    assert Path(result["database"]).exists()


def test_fondart_document_selection_avoids_adjacent_fund_and_juror_pdfs():
    urls = [
        "https://fondosdecultura.cl/uploads/resultados-fondo-libro-2020.pdf",
        "https://fondosdecultura.cl/uploads/evaluadores-fondart-2020.pdf",
        "https://fondosdecultura.cl/uploads/resultados-fondart-regional-2020.pdf",
        "https://fondosdecultura.cl/uploads/resultados-fondart-nacional-2020.pdf",
    ]

    assert fondart_corpus._prioritized_fondart_documents(urls) == [
        "https://fondosdecultura.cl/uploads/resultados-fondart-regional-2020.pdf",
        "https://fondosdecultura.cl/uploads/resultados-fondart-nacional-2020.pdf",
    ]


def test_fondart_document_selection_excludes_call_bases_without_results_marker():
    urls = [
        "https://fondosdecultura.cl/uploads/DIFUSION-FREGIONAL-2DA2024-V1.pdf",
        "https://fondosdecultura.cl/uploads/SELECCIONADOS-FREGIONAL-2024.pdf",
    ]

    assert fondart_corpus._prioritized_fondart_documents(urls) == [
        "https://fondosdecultura.cl/uploads/SELECCIONADOS-FREGIONAL-2024.pdf",
    ]


def test_fondart_document_selection_excludes_call_page_that_promises_future_results():
    candidate = {
        "url": "https://fondosdecultura.cl/uploads/01-FR-REGIONALES-2023.pdf",
        "title": "Linea Culturas Regionales",
        "snippet": "La nomina de proyectos seleccionados se publicara en la pagina web institucional.",
    }

    assert fondart_corpus._prioritized_fondart_candidates([candidate]) == []


def test_fondart_document_selection_recognizes_abbreviations_and_spreads_years():
    urls = [
        "https://fondosdecultura.cl/uploads/2023/seleccion-fdrt-regional2024.pdf",
        "https://fondosdecultura.cl/uploads/2021/seleccionados-fregional2022.pdf",
        "https://fondosdecultura.cl/uploads/2019/resultados-fondart-nacional-2020.pdf",
        "https://fondosdecultura.cl/uploads/2019/resultados-fondart-regional-2020.pdf",
    ]

    ordered = fondart_corpus._prioritized_fondart_documents(urls)

    assert ordered[:3] == [
        "https://fondosdecultura.cl/uploads/2023/seleccion-fdrt-regional2024.pdf",
        "https://fondosdecultura.cl/uploads/2021/seleccionados-fregional2022.pdf",
        "https://fondosdecultura.cl/uploads/2019/resultados-fondart-regional-2020.pdf",
    ]


def test_fondart_candidates_can_use_search_evidence_when_filename_is_generic():
    candidates = [{
        "url": "https://fondosdecultura.cl/uploads/2025/seleccionados-2025.pdf",
        "title": "Nomina de seleccionados Fondart Regional",
        "snippet": "Nomina de proyectos seleccionados convocatoria 2025",
    }]

    ordered = fondart_corpus._prioritized_fondart_candidates(candidates)

    assert [item["url"] for item in ordered] == [candidates[0]["url"]]


def test_fondart_document_selection_keeps_out_of_scope_years_after_requested_range():
    candidates = [{
        "url": "https://fondosdecultura.cl/uploads/resultados-fondart-regional-%d.pdf" % year,
        "title": "Resultados Fondart Regional",
        "snippet": "Nomina de seleccionados",
    } for year in (2026, 2024, 2023, 2022)]

    ordered = fondart_corpus._prioritized_fondart_candidates(
        candidates, preferred_years=tuple(range(2015, 2026)))

    assert [fondart_corpus._url_year(item["url"]) for item in ordered] == [2024, 2023, 2022, 2026]


def test_fondart_candidate_scope_keeps_undated_and_requested_sources_only():
    years = tuple(range(2015, 2026))
    assert fondart_corpus._candidate_in_year_scope(
        {"url": "https://fondosdecultura.cl/resultados.pdf"}, years)
    assert fondart_corpus._candidate_in_year_scope(
        {"url": "https://fondosdecultura.cl/resultados-2025.pdf"}, years)
    assert not fondart_corpus._candidate_in_year_scope(
        {"url": "https://fondosdecultura.cl/resultados-2026.pdf"}, years)


def test_fondart_ingest_deduplicates_application_and_coincidence_group_together(tmp_path):
    store = fondart_corpus.FondartCorpusStore(tmp_path)
    base = {
        "capture_id": "capture-1", "folio": "542505", "source_order": 1,
        "reported_year": 2020, "source_url_year": 2020, "region": "Arica",
        "area_or_modality": "Unica", "title": "Obra seleccionada",
        "responsible": "Ana Persona", "amount_raw": "$ 4.941.844",
        "selected_status": "selected", "source_text": "row",
        "source_url": "https://fondosdecultura.cl/results-2020.pdf",
    }
    variant = dict(base, title="Obra seleccionada variante", responsible="")

    assert store.ingest([base, variant]) == 1
    with store.sources._connect() as conn:
        assert conn.execute("SELECT COUNT(*) FROM fondart_applications").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM fondart_coincidence_groups").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM fondart_application_coincidences").fetchone()[0] == 1


def test_result_index_filter_excludes_login_and_current_call_pages():
    assert fondart_corpus._is_result_index_url("https://www.fondosdecultura.cl/resultados/")
    assert fondart_corpus._is_result_index_url("https://archivos.fondosdecultura.cl/")
    assert not fondart_corpus._is_result_index_url("https://clave.fondosdecultura.cl/")
    assert not fondart_corpus._is_result_index_url(
        "https://www.fondosdecultura.cl/fondos/fondart-regional/")
