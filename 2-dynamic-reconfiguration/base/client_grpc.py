import argparse
import grpc
import time
import csv
import os
# import random
import proto.echo_pb2 as echo_pb2
import proto.echo_pb2_grpc as echo_pb2_grpc
from utils import now_ms, ensure_results_dir, apply_gateway_config_change


# CLI arguments
parser = argparse.ArgumentParser(
    description="Gateway testing and measurement client for Scenario 2: gRPC dynamic configuration switch")
parser.add_argument("--gateway", required=True,
                    help="Gateway name (e.g. haproxy, caddy, traefik, tyk)")
parser.add_argument("--iterations", type=int, default=30,
                    help="Number of experiment iterations per signal")
args = parser.parse_args()


# Experiment parameters
ITERATIONS = args.iterations
SLEEP_BETWEEN_RUNS = 2  # seconds between iterations
CHECK_INTERVAL = 0.05  # seconds between pings determine density/accuracy of results
SWITCH_DELAY = 3  # seconds until config change
# total runtime per iteration in seconds (must be greater than SWITCH_DELAY)
RUN_TIME = 6
TARGET_HOST = "localhost:8080"
RESULTS_DIR = "../results"
RESULTS_FILE = os.path.join(
    RESULTS_DIR, f"grpc_dynamic_switch_{args.gateway}.csv")


def run_unary_experiment(gateway):
    ensure_results_dir(RESULTS_DIR)
    print(f"Running gRPC unary dynamic switch for {gateway}")

    all_results = []

    for i in range(1, ITERATIONS + 1):
        print(f"\n--- gRPC unary iteration {i}/{ITERATIONS} ---")

        start_ts = now_ms()
        switch_ts = start_ts + int(SWITCH_DELAY * 1000)
        switched = False
        iteration_results = []

        with grpc.insecure_channel(TARGET_HOST) as channel:
            stub = echo_pb2_grpc.EchoStub(channel)

            while (now_ms() - start_ts) < RUN_TIME * 1000:
                t = now_ms()
                try:
                    resp = stub.Ping(echo_pb2.EchoRequest(message="ping"))
                    text = resp.message
                    success = True
                except Exception:
                    text = "ERROR"
                    success = False

                # Mark whether this request was before or after the switch
                phase = "before" if not switched else "after"
                iteration_results.append([i, t, text, success, phase])

                # Trigger config change
                if not switched and now_ms() >= switch_ts:
                    print("[INFO] Triggering config change / reload")
                    switch_event_ts = now_ms()
                    apply_gateway_config_change(gateway)
                    switched = True
                    # Explicitly log switch event
                    iteration_results.append(
                        [i, switch_event_ts, "SWITCH_EVENT", True, "event"])

                time.sleep(CHECK_INTERVAL)

        all_results.extend(iteration_results)
        time.sleep(SLEEP_BETWEEN_RUNS)
        # random sleep time to test tyk config change reload interval
        # time.sleep(random.uniform(1, 4))

    # save results
    with open(RESULTS_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "iteration",
            "timestamp_ms",
            "response",
            "success",
            "phase"
        ])
        writer.writerows(all_results)

    print(f"✅ Results saved to {RESULTS_FILE}")


if __name__ == "__main__":
    run_unary_experiment(args.gateway)
