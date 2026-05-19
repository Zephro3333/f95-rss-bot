import requests
import os
import time
import json
from datetime import datetime

API_URL = "https://f95zone.to/sam/latest_alpha/latest_data.php?cmd=list&cat=games&page=1&sort=date"
WEBHOOK = os.getenv("DISCORD_WEBHOOK")

STATE_FILE = "state.json"


# =========================
# STATE
# =========================

def load_state():
    if not os.path.exists(STATE_FILE):
        return {
            "last_seen_id": 0,
            "last_update_ts": 0,
            "history": []
        }

    with open(STATE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


# =========================
# FETCH
# =========================

def fetch_posts():
    try:
        r = requests.get(API_URL, timeout=30)
        r.raise_for_status()
        return r.json()["msg"]["data"]
    except Exception as e:
        print("Fetch error:", e)
        return []


# =========================
# DISCORD
# =========================

def send_discord(post):
    if not WEBHOOK:
        raise ValueError("DISCORD_WEBHOOK missing")

    embed = {
        "title": post.get("title", "No title"),
        "url": f"https://f95zone.to/threads/{post['thread_id']}",
        "color": 65280,
        "image": {"url": post.get("cover", "")},
        "fields": [
            {"name": "Creator", "value": post.get("creator", "N/A"), "inline": True},
            {"name": "Version", "value": post.get("version", "N/A"), "inline": True}
        ],
        "timestamp": datetime.utcnow().isoformat()
    }

    r = requests.post(WEBHOOK, json={"embeds": [embed]}, timeout=15)
    print("Discord:", r.status_code)


# =========================
# CORE LOGIC
# =========================

def run():
    print("🚀 F95 Bot starting...")

    state = load_state()

    posts = fetch_posts()
    if not posts:
        print("No posts found")
        return

    posts.sort(key=lambda x: int(x["thread_id"]), reverse=True)

    last_seen = state["last_seen_id"]
    new_last_seen = last_seen

    sent = 0

    for post in posts:
        pid = int(post["thread_id"])

        if pid <= last_seen:
            continue

        send_discord(post)
        sent += 1

        if pid > new_last_seen:
            new_last_seen = pid

    state["last_seen_id"] = new_last_seen
    state["last_update_ts"] = time.time()

    state["history"].append(sent)
    state["history"] = state["history"][-20:]

    save_state(state)

    print(f"✅ Done - sent {sent} posts")


if __name__ == "__main__":
    run()
