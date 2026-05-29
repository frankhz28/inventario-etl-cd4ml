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

up-docker: ## Levantar toda la infraestructura base con Docker Compose
	docker compose up -d

down-docker: ## Detener infraestructura y eliminar volúmenes persistentes
	docker compose down -v

clean: ## Elimina cachés y archivos temporales
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -f data/*sanitizado.csv
	@echo "Entorno limpio."

help: ## Mostrar ayuda
	@grep -E '^[a-zA-Z0-9_-]+:.*?## ' $(MAKEFILE_LIST) | awk -F':|##' '{printf "  %-15s %s\n", $$1, $$3}'