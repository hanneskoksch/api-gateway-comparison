#!/bin/bash
set -e

for gateway in caddy haproxy nginx traefik tyk; do
  echo ""
  echo "==== Testing $gateway ===="
  cd $gateway

  echo "Cleaning up previous containers..."
  docker compose down -v

  echo "Starting new environment..."
  docker compose up -d

  echo "Waiting for containers to be ready..."
  sleep 3

  echo "Running client experiment..."
  python3 ../base/client.py --gateway $gateway --iterations 100

  echo "Stopping environment..."
  docker compose down -v
  cd ..
done