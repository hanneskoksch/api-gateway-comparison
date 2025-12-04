import subprocess
import requests
import time
import csv
import os
import argparse

# CLI arguments
parser = argparse.ArgumentParser(
    description="Gateway testing and measurement client for Scenario 1: Restart after shutdown with kill signals SIGTERM and SIGKILL")
parser.add_argument("--gateway", required=True,
                    help="Name of the gateway container (e.g. haproxy, traefik, tyk)")
parser.add_argument("--iterations", type=int, default=30,
                    help="Number of experiment iterations per signal")
args = parser.parse_args()

# Experiment parameters
ITERATIONS = args.iterations
SLEEP_BETWEEN_RUNS = 2  # seconds between iterations
TARGET_URL = "http://localhost:8080"
RESULTS_DIR = "../results"
RESULTS_FILE = os.path.join(RESULTS_DIR, f"measurements_{args.gateway}.csv")
SIGNALS = ["SIGTERM", "SIGKILL"]
CHECK_INTERVAL = 0.05  # seconds between pings determine density/accuracy of results

# Create results directory
os.makedirs(RESULTS_DIR, exist_ok=True)


def now_ms():
    """Return current time in milliseconds."""
    return int(time.time() * 1000)


def docker_cmd(args_list):
    """Run a docker command and return result"""
    result = subprocess.run(["docker"] + args_list,
                            capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[WARN] Docker command failed: {' '.join(args_list)}")
        print(result.stderr.strip())
    return result


def ping(iteration: int):
    """Return True if gateway responds with HTTP 200."""
    try:
        r = requests.get(TARGET_URL + "?iteration=" +
                         str(iteration), timeout=1)
        return r.status_code == 200
    except Exception:
        return False


def wait_until_down(iteration: int):
    """Wait until gateway is no longer reachable (no responses)."""
    while ping(iteration):
        time.sleep(CHECK_INTERVAL)
    return now_ms()


def wait_until_up(iteration: int):
    """Wait until gateway responds again."""
    while not ping(iteration):
        time.sleep(CHECK_INTERVAL)
    return now_ms()


def wait_until_exited(gateway):
    """Wait until the gateway container has exited."""
    while True:
        result = subprocess.run(["docker", "inspect", "-f", "{{.State.Running}}", gateway],
                                capture_output=True, text=True)
        if "false" in result.stdout:
            return now_ms()
        time.sleep(CHECK_INTERVAL)


def run_experiment(gateway, signal_type, iterations):
    """Run experiment for a given signal type"""
    print(f"\nStarting experiment: {gateway} / {signal_type}")
    results = []

    for i in range(1, iterations + 1):
        print(f"\nIteration {i}/{iterations} ({signal_type})")

        # 1. Kill gateway and record timestamp
        print(
            f"[INFO] Sending {signal_type} to gateway container '{gateway}'...")
        docker_cmd(["kill", f"--signal={signal_type}", gateway])

        # 2. Wait until it's actually down (no responses)
        down_ts = wait_until_down(i)
        # Also wait until container has exited
        wait_until_exited(gateway)

        # 3. Restart gateway
        print(f"[INFO] Restarting gateway container '{gateway}'...")
        docker_cmd(["start", gateway])

        print(f"[INFO] Waiting for gateway to come back up...")
        # 4. Wait until it's back up
        up_ts = wait_until_up(i)
        print(f"[INFO] Gateway is back up.")

        # 5. Compute durations
        downtime = up_ts - down_ts

        results.append([
            i, gateway, signal_type, down_ts, up_ts,
            downtime
        ])

        print(
            f"[OK] Downtime: {downtime} ms"
        )

        time.sleep(SLEEP_BETWEEN_RUNS)

    return results


def main():
    all_results = []
    for signal in SIGNALS:
        results = run_experiment(args.gateway, signal, ITERATIONS)
        all_results.extend(results)

    with open(RESULTS_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "iteration",
            "gateway",
            "signal",
            "down_ts_ms",
            "up_ts_ms",
            "downtime_ms"
        ])
        writer.writerows(all_results)

    print(f"\n✅ Results written to {RESULTS_FILE}")


if __name__ == "__main__":
    main()
