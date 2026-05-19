# f95_bot/state.py

import json
import os
import time

STATE_FILE = "state/last_seen.json"


def load_state():
    if not os.path.exists(STATE_FILE):
        return {
            "seen": set(),
            "last_run_ts": 0,
            "last_heartbeat_ts": 0,
            "history_intervals": []
        }

    with open(STATE_FILE, "r") as f:
        data = json.load(f)
        data["seen"] = set(data.get("seen", []))
        return data


def save_state(state):
    state["seen"] = list(state["seen"])

    os.makedirs("state", exist_ok=True)

    with open(STATE_FILE, "w") as f:
        json.dump(state, f)


def update_heartbeat(state):
    state["last_heartbeat_ts"] = int(time.time())
