import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_readme_svg_preserves_canonical_animation_shape():
    svg = (ROOT / "arte-ascii-readme.svg").read_text(encoding="utf-8")
    assert 'viewBox="0 0 936 720"' in svg
    assert "frames: 30; duration: 9s;" in svg
    assert "readme-source-static" in svg
    assert "animation:showFrame 9s step-end infinite" in svg
    assert len(re.findall(r"<mask\b", svg)) == 150
    assert len(re.findall(r"<tspan\b", svg)) == 100
    assert "<clipPath" not in svg
    assert "MAK" in svg
