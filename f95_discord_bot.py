import requests
import json
import os
import time
from datetime import datetime

# =========================
# CONFIG
# =========================

API_URL = "https://f95zone.to/sam/latest_alpha/latest_data.php?cmd=list&cat=games&page=1&sort=date"
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK")

STATE_FILE = "last_seen.json"

# comportamento
HEARTBEAT_HOURS = 6
SILENT_FAILURE_THRESHOLD_HOURS = 5

# =========================
# STATE
# =========================

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "seen": [],
        "last_update_ts": 0,
        "last_heartbeat_ts": 0,
        "history_intervals": []
    }


def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f)


# =========================
# DISCORD
# =========================

def send_discord(embed):
    try:
        r = requests.post(WEBHOOK_URL, json={"embeds": [embed]}, timeout=15)
        print("Discord status:", r.status_code)
    except Exception as e:
        print("Discord error:", e)


def send_heartbeat(state):
    now = time.time()

    if now - state["last_heartbeat_ts"] > HEARTBEAT_HOURS * 3600:
        send_discord({
            "title": "🟢 F95 Bot Heartbeat",
            "description": "Bot is running normally.",
            "color": 65280,
            "timestamp": datetime.utcnow().isoformat()
        })

        state["last_heartbeat_ts"] = now


def send_alert(title, msg):
    send_discord({
        "title": title,
        "description": msg,
        "color": 16711680
    })


# =========================
# ADAPTIVE LOGIC
# =========================

def calculate_threshold(state):
    history = state.get("history_intervals", [])

    if len(history) < 3:
        return 3 * 3600  # fallback: 3h

    avg = sum(history) / len(history)

    # fator adaptativo simples
    return avg * 3.5


def update_history(state, interval):
    history = state.get("history_intervals", [])
    history.append(interval)

    # mantém leve (últimos 20 valores)
    state["history_intervals"] = history[-20:]


# =========================
# CORE FETCH
# =========================

def fetch_posts():
    r = requests.get(API_URL, timeout=30)
    r.raise_for_status()
    return r.json()["msg"]["data"]


def build_embed(post):
    return {
        "title": post.get("title", "No title"),
        "url": f"https://f95zone.to/threads/{post['thread_id']}",
        "color": 65280,
        "image": {"url": post.get("cover", "")},
        "fields": [
            {"name": "Creator", "value": post.get("creator", "Unknown"), "inline": True},
            {"name": "Version", "value": post.get("version", "N/A"), "inline": True},
            {"name": "Rating", "value": str(post.get("rating", "0")), "inline": True}
        ],
        "footer": {"text": "F95 Auto Bot"},
        "timestamp": datetime.utcnow().isoformat()
    }


# =========================
# MAIN LOGIC
# =========================

def main():
    print("🚀 Starting F95 bot...")

    state = load_state()
    seen = set(state["seen"])

    now = time.time()

    try:
        posts = fetch_posts()
        print(f"📦 Posts found: {len(posts)}")

        new_seen = set(seen)
        sent = 0
        latest_ts = state["last_update_ts"]

        for post in posts:
            pid = str(post["thread_id"])

            if pid not in seen:
                print("🆕 New post:", post["title"])

                send_discord(build_embed(post))

                new_seen.add(pid)
                sent += 1

        # =========================
        # interval tracking
        # =========================

        if state["last_update_ts"] != 0:
            interval = now - state["last_update_ts"]
            update_history(state, interval)

        state["last_update_ts"] = now

        # =========================
        # silent failure detector
        # =========================

        threshold = calculate_threshold(state)
        time_since_update = now - state["last_update_ts"]

        if time_since_update > SILENT_FAILURE_THRESHOLD_HOURS * 3600:
            send_alert(
                "⚠️ F95 Silent Delay Detected",
                f"No updates for {round(time_since_update/3600, 2)}h"
            )

        if time_since_update > threshold:
            send_alert(
                "🔴 Adaptive Critical Delay",
                f"Delay exceeded adaptive threshold ({round(threshold/3600, 2)}h)"
            )

        # =========================
        # heartbeat
        # =========================

        send_heartbeat(state)

        # =========================
        # save state
        # =========================

        state["seen"] = list(new_seen)
        save_state(state)

        print(f"✅ Done. New posts sent: {sent}")

    except Exception as e:
        send_alert("❌ Bot Crash", str(e))
        print("ERROR:", e)


if __name__ == "__main__":
    main()
    run()
