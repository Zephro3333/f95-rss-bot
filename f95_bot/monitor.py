# f95_bot/monitor.py

import time

SPIKE_THRESHOLD = 15
SILENT_THRESHOLD = 5 * 60 * 60  # 5h


def detect_spike(current_count, state):
    history = state.get("history_intervals", [])

    if len(history) < 5:
        return False

    avg = sum(history[-5:]) / 5

    return current_count > avg + SPIKE_THRESHOLD


def detect_silent_failure(state):
    last = state.get("last_heartbeat_ts", 0)

    if last == 0:
        return False

    return (time.time() - last) > SILENT_THRESHOLD
