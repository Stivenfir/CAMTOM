#!/usr/bin/env bash
set -euo pipefail

if [[ ! -f .env ]]; then
  echo "No existe .env. Copiando desde .env.example..."
  cp .env.example .env
  echo "Listo. Edita .env y pon PROVIDER_API_KEY real antes de continuar."
  exit 1
fi

python run.py
