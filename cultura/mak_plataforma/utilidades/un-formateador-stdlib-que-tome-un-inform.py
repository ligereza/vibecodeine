def _procesar_tachado(linea: str) -> str:
    """
    Elimina el formato de tachado ~~texto~~ dejando solo el texto.
    """
    return re.sub(r"~~(.+?)~~", r"\1", linea)
