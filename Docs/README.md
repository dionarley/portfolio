# Documentação do Projeto

Este diretório contém a documentação completa do portfólio.

## Arquivos

| Arquivo | Descrição |
|--------|-----------|
| [README.md](README.md) | Visão geral e instalação |
| [DEVELOPER.md](DEVELOPER.md) | Guia para desenvolvedores |
| [AGENTS.md](AGENTS.md) | Regras para agentes IA |

## Estrutura do Projeto

```
portfolio/
├── Docs/              # Documentação
├── index.html        # Página principal
├── styles.css        # Estilos CSS
├── script.js         # JavaScript
├── Dockerfile       # Container Docker
├── nginx.conf       # Configuração nginx
├── docker-compose.yml # Orquestração Docker
├── Makefile          # Atalhos de desenvolvimento
├── scripts/          # Servidor local e atalhos Docker
├── tests/            # Verificações antes do commit
└── .github/          # CI
```

## Quick Start

```bash
# Desenvolvimento local com recarga automática
make dev

# Verificações antes do commit
make check

# Produção com Docker
make docker-prod
```

## Tecnologias

- HTML5 semântico
- CSS3 com variáveis
- JavaScript vanilla
- nginx:alpine
- Docker + Compose
- Python (apenas scripts de desenvolvimento)
