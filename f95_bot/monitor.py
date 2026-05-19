import time
import statistics

SILENT_LIMIT = 5 * 60 * 60  # 5h
SPIKE_THRESHOLD = 15


def detect_silent_failure(state):
    last = state.get("last_heartbeat_ts", 0)
    return last and (time.time() - last > SILENT_LIMIT)


def detect_spike(current, state):
    history = state.get("history", [])

    if len(history) < 5:
        return False

    baseline = statistics.median(history[-10:])

    return current > baseline + SPIKE_THRESHOLD
