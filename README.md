# AIRDROP v0.17 — Fixes Críticos

## Archivos corregidos:
1. `src/flujo/jobs/lifecycle.py` — `scan["risk"]` → `scan.risk`
2. `src/flujo/intake/email_parser.py` — regex medidas inline
3. `scripts/app.py` — Gradio 6.0 CSS fix
4. `tests/test_jobs_lifecycle.py` — monkeypatch correcto
5. `tests/test_dashboard.py` — monkeypatch correcto

## Aplicar:
```bash
bash scripts/apply_airdrop.sh --apply
pip install -e .
py -m pytest tests/ -v
```
