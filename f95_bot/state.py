import json
import os
import time

STATE_FILE = "state/last_seen.json"


def load_state():
    if not os.path.exists(STATE_FILE):
        return {
            "seen": [],
            "last_heartbeat_ts": 0,
            "last_run_ts": 0,
            "history": []
        }

    with open(STATE_FILE, "r") as f:
        return json.load(f)


def save_state(state):
    os.makedirs("state", exist_ok=True)

    with open(STATE_FILE, "w") as f:
        json.dump(state, f)


def update_heartbeat(state):
    state["last_heartbeat_ts"] = int(time.time())
