import pytest
from cultura.mak_vigia.vigia import plegar, _titulo_util


class TestPlegar:
    def test_quita_acentos(self):
        assert plegar("canción") == "cancion"

    def test_convierte_a_minuscula(self):
        assert plegar("HOLA") == "hola"

    def test_texto_vacio_da_cadena_vacia(self):
        assert plegar("") == ""

    def test_texto_none_da_cadena_vacia(self):
        assert plegar(None) == ""

    def test_texto_con_acentos_y_mayusculas(self):
        assert plegar("Árbol ÉLÉGANTE") == "arbol elegante"


class TestTituloUtil:
    def test_texto_corto_menos_de_12_chars_false(self):
        assert _titulo_util("corto") is False

    def test_texto_corto_con_3_palabras_false(self):
        assert _titulo_util("a b c") is False

    def test_texto_largo_menos_de_3_palabras_false(self):
        assert _titulo_util("palabralarga12345") is False

    def test_titulo_real_largo_y_con_sentido_true(self):
        assert _titulo_util("Nueva exposicion de arte contemporaneo en el museo") is True

    # Verified by the agent: no NAVEGACION value has both 12+ characters
    # and 3+ words at once, so the NAVEGACION filter itself (independent
    # of length) cannot be tested with a real case from that set.
