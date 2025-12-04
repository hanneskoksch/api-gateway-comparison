import subprocess
import time
import os
from pathlib import Path
import requests


def now_ms():
    return int(time.time() * 1000)


def docker_compose_cmd(args):
    """Run docker compose command"""
    result = subprocess.run(["docker", "compose"] +
                            args, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[WARN] Docker compose command failed: {' '.join(args)}")
        print(result.stderr.strip())
    return result


def ensure_results_dir(results_dir):
    os.makedirs(results_dir, exist_ok=True)


def apply_gateway_config_change(gateway: str):
    """
    Updates config file inside the gateway's bind mount (echo-a --> echo-b or vice versa)
    and triggers a live reload.
    """
    print(f"[INFO] Applying dynamic config change for {gateway}...")

    mode = os.environ['MODE']

    if gateway == "haproxy":
        cfg_path = Path(f"../haproxy/{mode}/haproxy.cfg")
        text = cfg_path.read_text()
        if "echo-a" in text:
            text = text.replace("echo-a", "echo-b")
        else:
            text = text.replace("echo-b", "echo-a")
        cfg_path.write_text(text)
        print("[INFO] Rewritten haproxy.cfg, sending USR2 to reload")
        docker_compose_cmd(["exec", "gateway", "kill", "-USR2", "1"])

    elif gateway == "nginx":
        cfg_path = Path(f"../nginx/{mode}/nginx.conf")
        text = cfg_path.read_text()
        if "echo-a" in text:
            text = text.replace("echo-a", "echo-b")
        else:
            text = text.replace("echo-b", "echo-a")
        cfg_path.write_text(text)
        print("[INFO] Rewritten nginx.conf, sending HUP to reload")
        docker_compose_cmd(["exec", "gateway", "kill", "-HUP", "1"])

    elif gateway == "caddy":
        cfg_path = Path(f"../caddy/{mode}/Caddyfile")
        text = cfg_path.read_text()
        if "echo-a" in text:
            text = text.replace("echo-a", "echo-b")
        else:
            text = text.replace("echo-b", "echo-a")
        cfg_path.write_text(text)
        print("[INFO] Rewritten Caddyfile, reloading Caddy")
        docker_compose_cmd(["exec", "gateway", "caddy",
                           "reload", "--config", f"/etc/caddy/Caddyfile"])

    elif gateway == "traefik":
        cfg_path = Path(f"../traefik/dynamic_conf_{mode}/dynamic_conf.yml")
        text = cfg_path.read_text()
        if "echo-a" in text:
            text = text.replace("echo-a", "echo-b")
        else:
            text = text.replace("echo-b", "echo-a")
        cfg_path.write_text(text)
        print("[INFO] Rewritten Traefik dynamic.yml")

    elif gateway == "tyk":
        cfg_path = Path(f"../tyk/{mode}/apps/echo-service-api.json")
        text = cfg_path.read_text()
        if "echo-a" in text:
            text = text.replace("echo-a", "echo-b")
        else:
            text = text.replace("echo-b", "echo-a")
        cfg_path.write_text(text)
        print("[INFO] Rewritten Tyk API definition, calling Admin API for reload")

        # Admin API call: http://<gateway_host>:8080/tyk/reload
        try:
            resp = requests.get(
                "http://localhost:8080/tyk/reload",
                headers={"x-tyk-authorization": "12345"},
                timeout=5,
            )
            if resp.status_code == 200:
                print("[INFO] Tyk successfully reloaded APIs.")
            else:
                print(
                    f"[WARN] Reload request failed: {resp.status_code} {resp.text}")
        except requests.RequestException as e:
            print(f"[ERROR] Could not contact Tyk Admin API: {e}")

    else:
        print(f"[WARN] Unknown gateway '{gateway}', skipping config change")
