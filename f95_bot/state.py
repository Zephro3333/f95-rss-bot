import json
import os
import time

STATE_FILE = "state/last_seen.json"


# =========================
# LOAD
# =========================

def load_state():

    os.makedirs("state", exist_ok=True)

    if not os.path.exists(STATE_FILE):

        return {
            "seen": [],
            "last_run_ts": 0
        }

    try:

        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    except Exception:

        return {
            "seen": [],
            "last_run_ts": 0
        }


# =========================
# SAVE
# =========================

def save_state(state):

    os.makedirs("state", exist_ok=True)

    with open(STATE_FILE, "w", encoding="utf-8") as f:

        json.dump(
            state,
            f,
            indent=2,
            ensure_ascii=False
        )


# =========================
# HEARTBEAT
# =========================

def update_heartbeat(state):

    state["last_run_ts"] = int(time.time())
