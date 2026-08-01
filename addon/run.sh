#!/usr/bin/env bash

set -e

echo "[Energy Hub] Starting..."
echo "[Energy Hub] Version ${ENERGYHUB_VERSION:-unknown}"

exec python3 /app/publisher.py