from pathlib import Path

from flujo.export.illustrator import prepare_svg_for_illustrator


def test_prepare_svg_for_illustrator_creates_package(tmp_path: Path) -> None:
    svg_dir = tmp_path / "svg_src"
    svg_dir.mkdir()
    svg_file = svg_dir / "pieza.svg"
    svg_file.write_text('<svg xmlns="http://www.w3.org/2000/svg"><rect width="100" height="100" fill="#000"/></svg>', encoding="utf-8")

    output_dir = tmp_path / "out"
    package_dir = prepare_svg_for_illustrator(svg_file, output_dir=output_dir, project_name="demo")

    assert package_dir.exists()
    assert (package_dir / "svg" / "pieza.svg").exists()
    assert (package_dir / "import_svg.jsx").exists()
    assert (package_dir / "README.md").exists()
    assert (package_dir / "manifest.json").exists()
