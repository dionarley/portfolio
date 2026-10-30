# Developer Guide - Portfolio Project

## Quick Start

```bash
# Servidor local com recarga automática (sem Docker)
make dev

# Verificações antes de commitar
make check

# Produção com Docker
make docker-prod
```

Sem `make`: `python3 scripts/dev.py` (recarga) ou `python3 -m http.server 8000`.

## Docker Overview

### Services

| Service | Port | Description | Volumes |
|---------|------|-------------|---------|
| portfolio | 8080 | Dev server | ./ -> /usr/share/nginx/html (ro) |
| portfolio-prod | 8080 | Production | none |

### Images

- **Base**: nginx:alpine
- **Build**: Multi-stage not needed (static files only)

## Local Development

| Comando | Descrição |
|---------|-----------|
| `make dev` | Servidor local com recarga automática (porta 8000) |
| `make serve` | Servidor estático simples, sem recarga |
| `make check` | Verificações de HTML, CSS, JS e contexto Docker |
| `make test` | Atalho para `make check` |
| `make build` | Constrói a imagem de produção |
| `make docker-dev` | Sobe o container de desenvolvimento |
| `make docker-prod` | Sobe o container de produção |
| `make docker-down` | Para os containers |
| `make clean` | Remove caches locais |

O `scripts/dev.py` usa só a biblioteca padrão: serve o site, injeta um cliente
de recarga no HTML e observa `index.html`, `styles.css` e `script.js`. Para
testar no celular na mesma rede: `python3 scripts/dev.py --host 0.0.0.0`.

Os atalhos de Docker (`scripts/docker.sh`) detectam automaticamente
`docker compose`, `podman-compose` ou `podman compose`.

## Workflows

### Development

```bash
# Servidor local com recarga automática (sem Docker)
make dev

# Container de desenvolvimento (volume + porta 8080)
make docker-dev

# Parar os containers
make docker-down
```

### Production

```bash
# Build and run detached
docker-compose up -d --build portfolio-prod

# Check status
docker-compose ps

# Stop
docker-compose down
```

## Project Files

```
├── Dockerfile        # nginx:alpine image
├── nginx.conf        # Server config with caching
├── docker-compose.yml  # Service definitions
├── .dockerignore     # Excludes
├── tests/check.py    # Verificações antes do commit
├── .githooks/        # Hook de pre-commit
├── .github/          # Workflow de CI
├── index.html       # Main page
├── styles.css       # Styles
└── script.js        # Interactivity
```

## Common Tasks

### Add new file to site

1. Edit `index.html`, `styles.css`, or `script.js`
2. Changes auto-refresh (dev mode)
3. Rebuild for production:
   ```bash
   docker-compose build portfolio-prod
   ```

### Modify nginx config

1. Edit `nginx.conf`
2. Restart:
   ```bash
   docker-compose restart portfolio
   ```

### Add new dependencies

- Font Awesome (icons) and Google Fonts (Inter, JetBrains Mono): CDN in `index.html`
- No npm/pip - pure static site

## Troubleshooting

### Container won't start

```bash
# Check logs
docker-compose logs

# Rebuild from scratch
docker-compose down --rmi all
docker-compose build --no-cache
```

### Port already in use

```bash
# Kill process on port 8080
lsof -ti:8080 | xargs kill
```

### Volume not updating

```bash
# Recreate container
docker-compose down
docker-compose up --build
```

## Validation

```bash
make check
# ou: python3 tests/check.py
```

O hook de pre-commit roda o mesmo script. Ative uma vez por clone:

```bash
git config core.hooksPath .githooks
```

O workflow `.github/workflows/ci.yml` repete as verificações no push e em
pull requests, constrói a imagem e testa os arquivos servidos (`/`,
`/styles.css`, `/script.js`, `/LICENSE`).

## Git Workflow

```bash
# Create branches
git branch dev
git branch canary
git branch new-feat

# Tag version
git tag -a v1.0.0 -m "Description"

# Push
git push origin master
git push origin v1.0.0
```