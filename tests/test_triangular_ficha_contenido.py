from cultura.mak_curatoria.triangular import _ficha_contenido


def test_fecha_no_participa_en_la_comparacion():
    a = {"categoria": "flyer", "datos_evento": {"fecha": "2026-01-01", "nombre": "X"}}
    b = {"categoria": "flyer", "datos_evento": {"fecha": "2026-02-02", "nombre": "X"}}
    assert _ficha_contenido(a) == _ficha_contenido(b)


def test_fecha_evento_tampoco_participa():
    a = {"categoria": "flyer", "datos_evento": {"fecha_evento": "2026-01-01", "nombre": "X"}}
    b = {"categoria": "flyer", "datos_evento": {"fecha_evento": "2026-03-03", "nombre": "X"}}
    assert _ficha_contenido(a) == _ficha_contenido(b)


def test_categoria_se_normaliza_a_minuscula():
    a = {"categoria": "FLYER", "datos_evento": {}}
    b = {"categoria": "flyer", "datos_evento": {}}
    assert _ficha_contenido(a) == _ficha_contenido(b)


def test_ficha_vacia_no_truena():
    assert _ficha_contenido({}) == ("", "{}", "{}", "")


def test_un_campo_distinto_si_cambia_la_tupla():
    a = {"categoria": "flyer", "datos_evento": {"nombre": "X"}}
    b = {"categoria": "flyer", "datos_evento": {"nombre": "Y"}}
    assert _ficha_contenido(a) != _ficha_contenido(b)
