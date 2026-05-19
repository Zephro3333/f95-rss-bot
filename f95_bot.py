import requests
import os
import time
import json
from datetime import datetime

API_URL = "https://f95zone.to/sam/latest_alpha/latest_data.php?cmd=list&cat=games&page=1&sort=date"
WEBHOOK = os.getenv("DISCORD_WEBHOOK")

STATE_FILE = "state.json"

# =========================
# CONFIG
# =========================

HEARTBEAT_INTERVAL = 6 * 60 * 60  # 6h
MAX_RETRIES = 3


# =========================
# STATE
# =========================

def load_state():
    if not os.path.exists(STATE_FILE):
        return {
            "last_seen_id": 0,
            "last_update_ts": 0,
            "last_heartbeat_ts": 0,
            "history": []
        }

    with open(STATE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


# =========================
# DISCORD
# =========================

def send_discord(embed):
    if not WEBHOOK:
        raise ValueError("DISCORD_WEBHOOK missing")

    try:
        r = requests.post(WEBHOOK, json={"embeds": [embed]}, timeout=15)
        print("Discord:", r.status_code)
    except Exception as e:
        print("Discord error:", e)


# =========================
# LOGGING HELPERS
# =========================

def log_event(title, description, color=3447003):
    send_discord({
        "title": title,
        "description": description,
        "color": color,
        "timestamp": datetime.utcnow().isoformat()
    })


# =========================
# HEARTBEAT
# =========================

def heartbeat(state):
    now = time.time()

    if now - state.get("last_heartbeat_ts", 0) > HEARTBEAT_INTERVAL:
        log_event(
            "🟢 F95 Bot Heartbeat",
            "Bot is running normally."
        )

        state["last_heartbeat_ts"] = now


# =========================
# FETCH (RETRY INTELIGENTE)
# =========================

def fetch_posts():
    delay = 2

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            r = requests.get(API_URL, timeout=30)
            r.raise_for_status()
            return r.json()["msg"]["data"]

        except Exception as e:
            print(f"Fetch attempt {attempt} failed:", e)

            if attempt < MAX_RETRIES:
                time.sleep(delay)
                delay *= 2  # backoff exponencial

    return []


# =========================
# MAIN DISCORD POST
# =========================

def send_post(post):
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

    send_discord(embed)


# =========================
# CORE
# =========================

def run():
    print("🚀 Bot started")

    state = load_state()

    posts = fetch_posts()
    if not posts:
        print("No posts fetched")
        return

    posts.sort(key=lambda x: int(x["thread_id"]), reverse=True)

    last_seen = state["last_seen_id"]
    new_last_seen = last_seen

    sent = 0

    for post in posts:
        pid = int(post["thread_id"])

        if pid <= last_seen:
            continue

        send_post(post)
        sent += 1

        if pid > new_last_seen:
            new_last_seen = pid

    state["last_seen_id"] = new_last_seen
    state["last_update_ts"] = time.time()

    state["history"].append(sent)
    state["history"] = state["history"][-20:]

    # 🟢 heartbeat + logging
    heartbeat(state)

    if sent > 0:
        log_event(
            "📦 Posts sent",
            f"New posts delivered: {sent}",
            color=3066993
        )

    save_state(state)

    print(f"✅ Done - sent {sent}")


if __name__ == "__main__":
    run()

if __name__ == "__main__":
    run()
