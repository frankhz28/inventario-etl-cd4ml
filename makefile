.PHONY: help setup infra-up run-etl app-up app-down up-docker down-docker test-unit test-ci test-all all clean

.DEFAULT_GOAL := help

setup: ## Instalar dependencias en el entorno virtual local
	pip install -r requirements.txt

infra-up: ## Levanta SOLO la base de datos de producción
	docker compose up -d postgres-db
	@echo "Esperando 3 segundos a que PostgreSQL abra sus puertos..."
	@sleep 3

run-etl: infra-up ## Enciende la BD y luego ejecuta el pipeline de extracción y transformación
	@echo "Ejecutando el Pipeline ETL..."
	export DATABASE_URL="postgresql+psycopg2://admin:password123@localhost:5432/condor_analytics" && python3 -m src.pipeline

app-up: run-etl ## El comando supremo: BD -> ETL -> Dashboard
	@echo "Levantando la interfaz visual..."
	docker compose up -d dashboard
	@echo "Sistema completo en línea. Visita: http://localhost:8501"

app-down: ## Apaga toda la infraestructura de producción
	docker compose down

up-docker: ## Levantar toda la infraestructura base con Docker Compose
	docker compose up -d

down-docker: ## Detener infraestructura y eliminar volúmenes persistentes
	docker compose down -v

test-unit: ## Ejecutar pruebas unitarias locales
	PYTHONPATH=. pytest tests/unit/ -v

test-ci: ## Ejecuta el patrón SUT completo (Construye imagen, testea en BD efímera y destruye)
	docker compose -f docker-compose.test.yml up --build --abort-on-container-exit
	docker compose -f docker-compose.test.yml down -v

test-all: ## Ejecutar toda la suite localmente
	PYTHONPATH=. pytest tests/ -v

clean: ## Elimina cachés y archivos temporales
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -f data/*sanitizado.csv
	@echo "Entorno limpio."

all: clean test-ci app-up ## Purga, pasa tests en Docker aislando errores y despliega a producción
	@echo "Integración y Despliegue Continuo finalizado con éxito."

help: ## Mostrar ayuda
	@grep -E '^[a-zA-Z0-9_-]+:.*?## ' $(MAKEFILE_LIST) | awk -F':|##' '{printf "  %-15s %s\n", $$1, $$3}'