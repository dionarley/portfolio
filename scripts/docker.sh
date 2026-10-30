#!/bin/sh
# Atalhos de Docker com fallback automático para Podman.
#
# Uso: scripts/docker.sh {dev|prod|build|down}
set -e

root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$root"

command_name=${1:-help}

detect_compose() {
    if command -v docker >/dev/null 2>&1 && docker info >/dev/null 2>&1; then
        echo "docker compose"
    elif command -v podman-compose >/dev/null 2>&1; then
        echo "podman-compose"
    elif command -v podman >/dev/null 2>&1 && podman info >/dev/null 2>&1; then
        echo "podman compose"
    fi
}

compose=$(detect_compose)

if [ -z "$compose" ]; then
    echo "Docker ou Podman não encontrado (ou daemon indisponível)." >&2
    exit 1
fi

# $compose pode ter duas palavras ("docker compose"), por isso o split é intencional.
run_compose() {
    # shellcheck disable=SC2086
    exec $compose "$@"
}

case "$command_name" in
    dev)
        run_compose up --build portfolio
        ;;
    prod)
        run_compose up --build portfolio-prod
        ;;
    build)
        run_compose build portfolio-prod
        ;;
    down)
        run_compose down
        ;;
    *)
        echo "Uso: scripts/docker.sh {dev|prod|build|down}" >&2
        exit 2
        ;;
esac
