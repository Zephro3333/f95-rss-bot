from client import fetch_posts, send_to_discord
from state import load_state, save_state, update_heartbeat
from monitor import detect_silent_failure, detect_spike
import time


def run():
    state = load_state()

    posts = fetch_posts()

    # silent failure detection
    if detect_silent_failure(state):
        print("⚠️ Silent failure detected")

    seen = set(state.get("seen", []))

    sent = 0

    for post in posts:
        pid = str(post["thread_id"])

        if pid not in seen:
            send_to_discord(post)
            seen.add(pid)
            sent += 1

    # update state safely
    state["seen"] = list(seen)

    state["last_run_ts"] = int(time.time())

    state["history"].append(len(posts))
    state["history"] = state["history"][-20:]  # limita memória

    update_heartbeat(state)

    save_state(state)

    print(f"OK - sent {sent} posts")


if __name__ == "__main__":
    run()
