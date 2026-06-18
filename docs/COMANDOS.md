# Comandos recomendados — flujo

## Comandos portables (funcionan en Windows y Linux)

```bash
# Health
python -m flujo health

# Instalar
python -m pip install -e .

# Tests
python -m pytest tests/ -q --tb=no
```

## En Windows (recomendado)

```bash
py -m flujo health
py -m pip install -e .
py -m pytest tests/ -q --tb=no
```

## En Linux / macOS

```bash
python3 -m flujo health
python3 -m pip install -e .
python3 -m pytest tests/ -q --tb=no
```

## Nota importante

Evita usar `py` en scripts que corran en CI (GitHub Actions usa Linux).
