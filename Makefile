# Atalhos de desenvolvimento local.
# O site continua 100% estático: nada aqui é necessário para publicá-lo.

PORT ?= 8000

.DEFAULT_GOAL := help
.PHONY: help dev serve check test build docker-dev docker-prod docker-down clean

help: ## Mostra os comandos disponíveis
	@echo "Comandos:"
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

dev: ## Servidor local com recarga automática (PORT=8000)
	python3 scripts/dev.py --port $(PORT)

serve: ## Servidor estático simples, sem recarga
	python3 -m http.server $(PORT)

check: ## Verificações estáticas (HTML, CSS, JS e contexto Docker)
	python3 tests/check.py

test: check ## Atalho para check

build: ## Constrói a imagem de produção
	scripts/docker.sh build

docker-dev: ## Sobe o container de desenvolvimento (porta 8080)
	scripts/docker.sh dev

docker-prod: ## Sobe o container de produção
	scripts/docker.sh prod

docker-down: ## Para os containers
	scripts/docker.sh down

clean: ## Remove caches locais (__pycache__)
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
