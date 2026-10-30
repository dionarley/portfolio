# Portfolio

Personal portfolio website built with vanilla HTML, CSS, and JavaScript.

## Quick Start

### Local (sem Docker)

```bash
make dev        # http://localhost:8000 com recarga automática
```

Sem `make`, os mesmos comandos estão em `scripts/`:

```bash
python3 scripts/dev.py        # servidor com recarga automática
python3 -m http.server 8000   # servidor estático simples
```

### Docker

```bash
docker-compose up --build
```

Access at http://localhost:8080

## Development commands

| Comando | Descrição |
| --- | --- |
| `make dev` | Servidor local com recarga automática |
| `make serve` | Servidor estático simples, sem recarga |
| `make check` | Verificações de HTML, CSS, JS e contexto Docker |
| `make build` | Constrói a imagem de produção |
| `make docker-dev` | Sobe o container de desenvolvimento |
| `make docker-prod` | Sobe o container de produção |
| `make docker-down` | Para os containers |
| `make clean` | Remove caches locais |

`make help` lista todos os comandos.

## Stack

- HTML5, CSS3, JavaScript (vanilla)
- Docker + nginx:alpine
- Python (apenas para scripts de desenvolvimento)

## Documentation

See `Docs/` for full documentation.

## License

CC BY-SA 4.0 - see LICENSE file
