"""
Script de ejemplo para demostrar la estructura correcta de un archivo Python.
Este módulo no contiene información confidencial de MAK.
"""

def saludar(nombre: str) -> str:
    """
    Retorna un saludo personalizado.

    Args:
        nombre: Nombre de la persona a saludar.

    Returns:
        Cadena con el saludo.
    """
    return f"¡Hola, {nombre}! Bienvenido al departamento Codex."


def main() -> None:
    """Función principal del script."""
    mensaje = saludar("Ingeniero")
    print(mensaje)


if __name__ == "__main__":
    main()
