# Developer Guide - Portfolio Project

## Quick Start

```bash
# Development with hot reload
docker-compose up --build

# Production build
docker-compose up -d portfolio-prod
```

## Docker Overview

### Services

| Service | Port | Description | Volumes |
|---------|------|-------------|---------|
| portfolio | 8080 | Dev server | ./ -> /usr/share/nginx/html (ro) |
| portfolio-prod | 8080 | Production | none |

### Images

- **Base**: nginx:alpine
- **Build**: Multi-stage not needed (static files only)

## Workflows

### Development

```bash
# Start with hot reload
docker-compose up --build

# View logs
docker-compose logs -f

# Stop
docker-compose down
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
# Validate HTML
npx html-validate index.html
```

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