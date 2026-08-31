.PHONY: help install clean test test-fast test-contract test-machine test-optional test-area test-full test-lanes audit render new-flyer daily dashboard pipeline

PYTHON ?= $(if $(wildcard .venv/bin/python),.venv/bin/python,python3)
AREA ?= research

help:
	@echo "Comandos disponibles:"
	@echo "  make install     Instalar dependencias (setup.sh autodetecta py|python3)"
	@echo "  make clean       Limpiar basura"
	@echo "  make audit       Auditar web, referencias activas y bases locales (solo lectura)"
	@echo "  make test        Ejecutar tests"
	@echo "  make test-fast   Ejecutar candidatos pequenos y hermeticos"
	@echo "  make test-contract Ejecutar contratos"
	@echo "  make test-machine Ejecutar tests fisicos/externos"
	@echo "  make test-optional Ejecutar tests de dependencias opcionales"
	@echo "  make test-area AREA=research Ejecutar un area"
	@echo "  make test-full   Suite completa"
	@echo "  make test-lanes  Reportar clasificacion sin ejecutar"
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

# The lane labels are conservative collection metadata. They do not delete or
# rewrite tests; unknown cases remain in lane_review until classified.
test-fast:
	$(PYTHON) -m pytest -m lane_fast -q

test-contract:
	$(PYTHON) -m pytest -m lane_contract -q

test-machine:
	$(PYTHON) -m pytest -m lane_machine -q

test-optional:
	$(PYTHON) -m pytest -m lane_optional -q

test-area:
	$(PYTHON) -m pytest -m "area_$(AREA)" -q

test-full:
	$(PYTHON) -m pytest tests/ -q

test-lanes:
	$(PYTHON) -m pytest --collect-only --area-report -q

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
