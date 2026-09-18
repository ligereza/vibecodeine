import pytest
from cultura.mak_research.research_lib import _compact_search_query


def test_removes_stopwords():
    query = "obtener los resumenes de datos para una clave"
    result = _compact_search_query(query)
    assert "obtener" not in result
    assert "los" not in result
    assert "resumenes" not in result
    assert "datos" not in result
    assert "para" not in result
    assert "una" not in result
    assert "clave" not in result


def test_removes_tokens_shorter_than_three():
    query = "un yo ir de en la el es"
    result = _compact_search_query(query)
    assert result == ""


def test_keeps_tokens_with_three_or_more_chars():
    query = "abc def ghi jkl"
    result = _compact_search_query(query)
    assert "abc" in result
    assert "def" in result
    assert "ghi" in result
    assert "jkl" in result


def test_deduplicates_repeated_tokens_preserving_first_order():
    query = "alpha beta alpha gamma beta delta alpha"
    result = _compact_search_query(query)
    tokens = result.split()
    assert tokens == ["alpha", "beta", "gamma", "delta"]


def test_truncates_to_max_eighteen_tokens():
    query = " ".join([f"token{i:03d}" for i in range(25)])
    result = _compact_search_query(query)
    assert len(result.split()) == 18


def test_empty_string_returns_empty_string():
    assert _compact_search_query("") == ""


def test_none_returns_empty_string():
    assert _compact_search_query(None) == ""


def test_preserves_internal_hyphen_as_single_token():
    query = "gpt-oss es un modelo avanzado"
    result = _compact_search_query(query)
    assert "gpt-oss" in result


def test_preserves_internal_dot_as_single_token():
    query = "archivo.config.xml lectura datos"
    result = _compact_search_query(query)
    assert "archivo.config.xml" in result


def test_mixed_stopwords_and_short_tokens_are_removed():
    query = "el gato con botas y un perro de agua"
    result = _compact_search_query(query)
    tokens = result.split()
    assert "el" not in tokens
    assert "con" not in tokens
    assert "y" not in tokens
    assert "un" not in tokens
    assert "de" not in tokens
    assert len(tokens) > 0


def test_case_insensitive_stopword_removal():
    query = "Obtener Resúmenes Completos Datos Clave"
    result = _compact_search_query(query)
    assert result == ""


def test_result_is_string_type():
    result = _compact_search_query("alguna consulta de prueba")
    assert isinstance(result, str)
