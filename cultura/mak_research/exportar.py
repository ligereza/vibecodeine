#!/usr/bin/env python3
"""Convierte un informe markdown a HTML autocontenido sin dependencias externas."""
from __future__ import annotations

import html
import re
import sys
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parent


def process_inline(text: str) -> str:
    text = html.escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)
    text = re.sub(r"\[(.+?)\]\((https?://[^)]+)\)", r'<a href="\2">\1</a>', text)
    return text


def render_markdown(text: str) -> str:
    lines = text.splitlines()
    body: list[str] = []
    in_ul = False
    in_ol = False

    def close_lists() -> None:
        nonlocal in_ul, in_ol
        if in_ul:
            body.append("</ul>")
            in_ul = False
        if in_ol:
            body.append("</ol>")
            in_ol = False

    for raw_line in lines:
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped:
            close_lists()
            continue
        if re.match(r"^#{1,6}\s+", line):
            close_lists()
            level = len(re.match(r"^(#{1,6})", line).group(1))
            body.append(f"<h{level}>{process_inline(stripped[level:].strip())}</h{level}>")
            continue
        if re.match(r"^[-*]\s+", line):
            if not in_ul:
                body.append("<ul>")
                in_ul = True
            body.append(f"<li>{process_inline(stripped[2:].strip())}</li>")
            continue
        if re.match(r"^\d+\.\s+", line):
            if not in_ol:
                body.append("<ol>")
                in_ol = True
            body.append(f"<li>{process_inline(stripped.split('.', 1)[1].strip())}</li>")
            continue
        close_lists()
        body.append(f"<p>{process_inline(stripped)}</p>")
    close_lists()
    return "\n".join(body)


def export_markdown(in_path: Path) -> Path:
    text = in_path.read_text(encoding="utf-8")
    content = render_markdown(text)
    html_text = f"""<!doctype html>
<html lang=\"es\">
<head>
<meta charset=\"utf-8\">
<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">
<title>{in_path.name}</title>
<style>
body {{background:#0b0a09;color:#d8d3c8;font-family:monospace;max-width:720px;margin:2rem auto;padding:0 1rem;line-height:1.6;}}
a {{color:#9db67c;}}
strong {{color:#f0e7c9;}}
code {{background:#171512;padding:0 .25rem;border-radius:3px;}}
</style>
</head>
<body>
<main>{content}</main>
</body>
</html>
"""
    out_path = in_path.with_suffix(".html")
    out_path.write_text(html_text, encoding="utf-8")
    return out_path


def iter_targets(paths: Iterable[str]) -> list[Path]:
    targets: list[Path] = []
    for raw in paths:
        path = Path(raw)
        if not path.is_absolute():
            path = (ROOT / path).resolve()
        if path.is_dir():
            targets.extend(sorted(path.glob("*.md")))
        elif path.suffix.lower() == ".md":
            targets.append(path)
    return targets


def main() -> int:
    args = sys.argv[1:]
    if not args:
        args = [str(ROOT / "informes"), str(ROOT / "paneles")]
    targets = iter_targets(args)
    if not targets:
        print("No se encontraron archivos .md para exportar", file=sys.stderr)
        return 1
    for target in targets:
        out_path = export_markdown(target)
        print(f"wrote {out_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
