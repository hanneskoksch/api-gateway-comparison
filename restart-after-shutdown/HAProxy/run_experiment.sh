#!/bin/bash
set -e

echo "Cleaning up previous containers..."
docker compose down -v

echo "Starting new environment..."
docker compose up -d

echo "Waiting for containers to be ready..."
sleep 3

echo "Running client experiment..."
python3 client.py

echo "Stopping environment..."
docker compose down