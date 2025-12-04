#!/bin/bash
set -e

# create results directories
RESULTS_DIR="./results/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$RESULTS_DIR"
mkdir -p "$RESULTS_DIR/fixed"
mkdir -p "$RESULTS_DIR/10-seconds"


run_hey() {
  local numberOfRequests=$1
  local concurrency=$2
  local mode=${3:-""}

  echo "Running hey with $numberOfRequests requests and concurrency $concurrency..."

  if [ "$mode" == "csv" ]; then
    hey -t 0 -n $numberOfRequests -c $concurrency -o csv "http://localhost:8080/" \
      > "../$RESULTS_DIR/fixed/${gw}_http_${numberOfRequests}_${concurrency}.csv" 2>&1
  else
    hey -t 0 -n $numberOfRequests -c $concurrency "http://localhost:8080/" \
      > "../$RESULTS_DIR/fixed/${gw}_http_${numberOfRequests}_${concurrency}.txt" 2>&1
  fi

  sleep 2
}


run_hey_for_10_sec() {
  local concurrency=$1
  local mode=${2:-""}

  echo "Running hey for 10 sec with concurrency $concurrency..."

  if [ "$mode" == "csv" ]; then
    hey -c $concurrency -z 10s -o csv "http://localhost:8080/" \
      > "../$RESULTS_DIR/10-seconds/${gw}_http_10s_${concurrency}.csv" 2>&1
  else
    hey -c $concurrency -z 10s "http://localhost:8080/" \
      > "../$RESULTS_DIR/10-seconds/${gw}_http_10s_${concurrency}.txt" 2>&1
  fi

  sleep 2
}

for gw in haproxy nginx traefik tyk; do
  cd $gw

  echo ""
  echo "==== Starting experiment for $gw ===="

  echo "Cleaning up previous containers..."
  docker compose down -v

  echo "Starting new environment..."
  docker compose up --build -d

  echo "Waiting for containers to be ready..."
  sleep 5

  echo "Running client experiment..."

  # predefined request/concurrency combinations
  run_hey 5000 1 csv
  run_hey 5000 10 csv
  run_hey 20000 10 csv
  run_hey 20000 50 csv
  run_hey 50000 50 csv
  run_hey 100000 50 csv


  # successively increasing concurrency for 10 seconds each to show influence of concurrency
  run_hey_for_10_sec 1 csv
  run_hey_for_10_sec 2 csv
  run_hey_for_10_sec 4 csv
  run_hey_for_10_sec 8 csv
  run_hey_for_10_sec 16 csv
  run_hey_for_10_sec 32 csv
  run_hey_for_10_sec 64 csv

  echo "Stopping environment..."
  docker compose down -v

  cd ..
done

echo "✅ Experiment complete."