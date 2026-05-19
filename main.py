# f95_bot/main.py

from client import fetch_posts, send_to_discord
from state import load_state, save_state, update_heartbeat
from monitor import detect_spike, detect_silent_failure
import time

def run():
    state = load_state()

    posts = fetch_posts()

    if detect_silent_failure(state):
        print("⚠️ Silent failure detected, forcing refresh mode")

    spike = detect_spike(len(posts), state)

    sent = 0

    for post in posts:
        pid = str(post["thread_id"])

        if pid not in state["seen"]:
            send_to_discord(post)
            state["seen"].add(pid)
            sent += 1

    state["last_run_ts"] = int(time.time())
    state["last_sent"] = sent

    if spike:
        state["history_intervals"].append(len(posts))

    update_heartbeat(state)

    save_state(state)

    print(f"OK - sent {sent} posts")


if __name__ == "__main__":
    run()
