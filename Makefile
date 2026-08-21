.PHONY: help install clean test audit render new-flyer daily dashboard pipeline

PYTHON ?= python3

help:
	@echo "Comandos disponibles:"
	@echo "  make install     Instalar dependencias (setup.sh autodetecta py|python3)"
	@echo "  make clean       Limpiar basura"
	@echo "  make audit       Auditar web, referencias activas y bases locales (solo lectura)"
	@echo "  make test        Ejecutar tests"
	@echo "  make render      Generar piezas de ejemplo"
	@echo "  make new-flyer   Crear flyer (NAME=\"nombre\")"
	@echo "  make daily       Generar dashboard"
	@echo "  make dashboard   Abrir dashboard"
	@echo "  make pipeline    Ejecutar pipeline (NAME=\"nombre\" EMAIL=inbox/correo.txt)"

install:
	bash scripts/setup.sh

clean:
	bash scripts/limpiar_basura.sh

test:
	$(PYTHON) -m pip install -e ".[dev]"
	$(PYTHON) -m pytest tests/ -q

audit:
	$(PYTHON) tools/repo_audit.py

render:
	$(PYTHON) scripts/piezas_generar.py projects/piezas_vectoriales/etiquetas_ejemplo/config.json

new-flyer:
	$(PYTHON) scripts/flyer_create_project.py "$(NAME)"

daily:
	$(PYTHON) scripts/flujo_daily.py

dashboard:
	bash scripts/abrir_dashboard.sh

pipeline:
	$(PYTHON) scripts/flujo_pipeline.py "$(NAME)" "$(EMAIL)" --confirm
