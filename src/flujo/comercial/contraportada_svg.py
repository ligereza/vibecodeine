"""Generador SVG para contraportadas de suplementos RD.

Lee la plantilla base (01_contraportada_base_10x14cm.svg) y reemplaza
placeholders de texto con los datos del suplemento.

Uso:
    from flujo.comercial.contraportada_svg import generar_contraportada
    svg = generar_contraportada(suplemento_obj, output_path)
"""

from pathlib import Path
from typing import Optional
from xml.etree import ElementTree as ET

# Registrar el namespace SVG por defecto para que tree.write no emita prefijos
# ns0: en los <text>/<rect>/... generados (Illustrator y el validador esperan el
# namespace por defecto, igual que la plantilla ASCII base).
ET.register_namespace("", "http://www.w3.org/2000/svg")

from .suplementos_config import Suplemento


def _get_base_svg_path() -> Path:
    """Obtener ruta a la plantilla base SVG."""
    from ..paths import repo_root

    base = repo_root() / "svg" / "suplementos_rd" / "04_contraportadas" / "01_contraportada_base_10x14cm.svg"
    if not base.exists():
        raise FileNotFoundError(f"Plantilla base no encontrada: {base}")
    return base


def _replace_text_in_svg(root: ET.Element, old_text: str, new_text: str) -> int:
    """Reemplazar texto dentro de elementos <text> en un árbol SVG.

    Args:
        root: Elemento raíz del SVG
        old_text: Texto a buscar
        new_text: Texto de reemplazo

    Returns:
        Número de reemplazos realizados
    """
    count = 0
    ns = {"svg": "http://www.w3.org/2000/svg"}

    for text_elem in root.findall(".//svg:text", ns):
        if text_elem.text and old_text in text_elem.text:
            text_elem.text = text_elem.text.replace(old_text, new_text)
            count += 1

    return count


def _replace_required(root: ET.Element, old_text: str, new_text: str, campo: str) -> int:
    """Reemplazar un placeholder OBLIGATORIO y fallar si no aparece.

    Protege contra el bug de plantilla desincronizada: si el texto de busqueda
    no coincide con ningun <text> de la plantilla base, _replace_text_in_svg
    devuelve 0 y la pieza saldria con el placeholder crudo. Para un campo
    obligatorio eso es un error duro, no algo que se resuelve en QA visual.
    """
    count = _replace_text_in_svg(root, old_text, new_text)
    if count == 0:
        raise ValueError(
            f"Campo obligatorio '{campo}' no reemplazado: el texto de busqueda "
            f"'{old_text}' no coincide con ningun placeholder de la plantilla "
            "01_contraportada_base_10x14cm.svg. Sincronizar contraportada_svg.py "
            "con el texto real de la plantilla."
        )
    return count


def generar_contraportada(
    suplemento: Suplemento,
    output_path: Optional[Path] = None,
    brief: Optional[str] = None,
) -> Path:
    """Generar SVG de contraportada para un suplemento.

    Reemplaza placeholders en la plantilla base con datos del suplemento:
    - NOMBRE DEL SUPLEMENTO → Suplemento.nombre
    - DESCRIPCIÓN → Suplemento.descripcion
    - Texto de beneficios y info nutricional

    Args:
        suplemento: Objeto Suplemento con datos
        output_path: Ruta de salida (default: svg/suplementos_rd/04_contraportadas/[nombre]_final.svg)
        brief: Texto breve personalizado para el beneficio o campaña

    Returns:
        Path del archivo generado

    Raises:
        FileNotFoundError: Si no existe la plantilla base
        ET.ParseError: Si la plantilla SVG está corrupta
    """
    base_path = _get_base_svg_path()

    # Parsear SVG base
    tree = ET.parse(str(base_path))
    root = tree.getroot()

    # Reemplazar placeholders
    nombre_upper = suplemento.nombre.upper()
    palabras = nombre_upper.split()
    if len(palabras) == 1:
        _replace_text_in_svg(root, "NOMBRE DEL", palabras[0])
        _replace_text_in_svg(root, "SUPLEMENTO", "")
    elif len(palabras) == 2:
        _replace_text_in_svg(root, "NOMBRE DEL", palabras[0])
        _replace_text_in_svg(root, "SUPLEMENTO", palabras[1])
    else:
        _replace_text_in_svg(root, "NOMBRE DEL", " ".join(palabras[:-1]))
        _replace_text_in_svg(root, "SUPLEMENTO", palabras[-1])

    # Los textos de busqueda deben coincidir EXACTO con la plantilla ASCII
    # (svg/suplementos_rd/04_contraportadas/01_contraportada_base_10x14cm.svg):
    # sin tildes/enies y sin vinetas.
    _replace_required(root, "DESCRIPCION", suplemento.descripcion, "descripcion")

    # Reemplazar beneficios (lineas 1-2)
    beneficio_1 = brief if brief else suplemento.beneficio_1
    _replace_required(
        root,
        "Beneficio principal o idea de campana para la pieza.",
        beneficio_1,
        "beneficio_1",
    )
    if suplemento.beneficio_2:
        _replace_text_in_svg(root, "Texto breve y claro para acompanar el producto.", suplemento.beneficio_2)

    # Reemplazar info nutricional
    _replace_required(
        root,
        "Ingredientes o perfil principal del suplemento.",
        suplemento.info_nutricional[0] if suplemento.info_nutricional else "",
        "info_nutricional[0]",
    )
    if len(suplemento.info_nutricional) > 1:
        _replace_text_in_svg(root, "Indicaciones de uso del producto.", suplemento.info_nutricional[1])
    if len(suplemento.info_nutricional) > 2:
        _replace_text_in_svg(root, "Recomendacion de seguimiento del producto.", suplemento.info_nutricional[2])

    # El QR es fijo en la plantilla (horneado en el .ai/base, no cambia por
    # suplemento); no se inyecta desde qr_text. Plantilla real de produccion:
    # Escritorio/ai_illustrator (modelo ops.json/state.json sobre el .ai).

    # Determinar ruta de salida
    if output_path is None:
        from ..paths import repo_root

        output_dir = repo_root() / "svg" / "suplementos_rd" / "04_contraportadas" / "generadas"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"{suplemento.nombre.lower().replace(' ', '_')}_final.svg"
    else:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

    # Escribir SVG generado
    tree.write(
        str(output_path),
        encoding="utf-8",
        xml_declaration=True,
    )

    return output_path
