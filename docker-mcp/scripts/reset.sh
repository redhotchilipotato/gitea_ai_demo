#!/usr/bin/env bash
set -euo pipefail


docker compose down -v || true
rm -f .env.bak || true
echo "Stack stopped and data deleted."
