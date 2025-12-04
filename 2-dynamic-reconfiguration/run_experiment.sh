#!/bin/bash
set -e

for gw in haproxy nginx traefik tyk; do
  cd $gw

  ## HTTP Experiment
  echo ""
  echo "==== Starting HTTP experiment for $gw ===="
  export MODE=http

  echo "Cleaning up previous containers..."
  docker compose down -v

  echo "Starting new environment..."
  docker compose up --build -d

  echo "Waiting for containers to be ready..."
  sleep 5

  echo "Running client experiment..."
  python3 ../base/client_http.py --gateway $gw --iterations 100

  echo "Stopping environment..."
  docker compose down -v


  ## GRPC Experiment
  echo ""
  echo "==== Starting gRPC experiment for $gw ===="
  export MODE=grpc

  echo "Cleaning up previous containers..."
  docker compose down -v

  echo "Starting new environment..."
  docker compose up --build -d 

  echo "Waiting for containers to be ready..."
  sleep 5

  echo "Running client experiment..."
  python3 ../base/client_grpc.py --gateway $gw --iterations 100

  echo "Stopping environment..."
  docker compose down -v
  
  cd ..
done

echo "✅ All experiments complete."