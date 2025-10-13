import subprocess
import requests
import time
import csv
import os

# === Experiment parameters ===
ITERATIONS = 100
SLEEP_BETWEEN_RUNS = 2  # Seconds between iterations
TARGET_URL = "http://localhost:8080"
RESULTS_FILE = "results/measurements.csv"
SIGNALS = ["SIGTERM", "SIGKILL"]  # both variants
CHECK_INTERVAL = 0.05  # Seconds between pings

os.makedirs("results", exist_ok=True)

# === Helper functions ===

def now_ms():
    """Current timestamp in milliseconds as int"""
    return int(time.time() * 1000)

def docker_cmd(args):
    """Run a docker command and return result"""
    result = subprocess.run(["docker"] + args, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[WARN] Docker command failed: {' '.join(args)}")
        print(result.stderr.strip())
    return result

def ping():
    """Return True if gateway responds with HTTP 200"""
    try:
        r = requests.get(TARGET_URL, timeout=1)
        return r.status_code == 200
    except Exception:
        return False

def wait_until_down():
    """Wait until gateway is no longer reachable"""
    while ping():
        time.sleep(CHECK_INTERVAL)
    return now_ms()

def wait_until_up():
    """Wait until gateway responds again"""
    while not ping():
        time.sleep(CHECK_INTERVAL)
    return now_ms()

def run_experiment(signal_type, iterations=ITERATIONS):
    """Run experiment for a given signal type"""
    print(f"\n=== Starting experiment: {signal_type} ===")
    results = []

    for i in range(1, iterations + 1):
        print(f"\nIteration {i}/{iterations} ({signal_type})")

        # 1. Kill gateway and record timestamp
        kill_ts = now_ms()
        docker_cmd(["kill", f"--signal={signal_type}", "gateway"])

        # 2. Wait until it's actually down (no responses)
        down_ts = wait_until_down()

        # 3. Restart gateway
        docker_cmd(["start", "gateway"])

        # 4. Wait until it's back up
        up_ts = wait_until_up()

        # 5. Calculate downtime in milliseconds
        downtime_from_kill = up_ts - kill_ts
        downtime_from_down = up_ts - down_ts

        results.append([
            i,
            signal_type,
            kill_ts,
            down_ts,
            up_ts,
            downtime_from_kill,
            downtime_from_down
        ])

        print(
            f"[OK] Downtime from kill: {downtime_from_kill} ms | "
            f"from down: {downtime_from_down} ms"
        )

        time.sleep(SLEEP_BETWEEN_RUNS)

    return results

def main():
    print("Starting restart experiments for gateway container...")
    all_results = []

    for sig in SIGNALS:
        results = run_experiment(sig, ITERATIONS)
        all_results.extend(results)

    # Save all results
    with open(RESULTS_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "iteration",
            "signal",
            "kill_ts_ms",
            "down_ts_ms",
            "up_ts_ms",
            "downtime_from_kill_ms",
            "downtime_from_down_ms"
        ])
        writer.writerows(all_results)

    print(f"\n✅ Results written to {RESULTS_FILE}")

if __name__ == "__main__":
    main()