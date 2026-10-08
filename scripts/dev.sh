#!/usr/bin/env bash
# Quick local dev helper script for CloudModX

set -e

echo "=== Starting CloudModX Local Stack (Docker Compose) ==="
docker compose up --build
