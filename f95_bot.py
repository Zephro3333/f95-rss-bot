import requests
import os
import time
import json
from datetime import datetime
from workflow_health import auto_heal_workflow

API_URL = "https://f95zone.to/sam/latest_alpha/latest_data.php?cmd=list&cat=games&page=1&sort=date"
WEBHOOK = os.getenv("DISCORD_WEBHOOK")

STATE_FILE = "state.json"

# =========================
# CONFIG
# =========================

HEARTBEAT_INTERVAL = 4 * 60 * 60
RECOVERY_HOURS = 6
RECOVERY_LIMIT = 20


# =========================
# STATE
# =========================

def load_state():
    if not os.path.exists(STATE_FILE):
        return {
            "seen": [],
            "last_success_ts": 0,
            "last_run_ts": 0,
            "last_heartbeat_ts": 0,
            "history": []
        }

    with open(STATE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


# =========================
# DEDUPE
# =========================

def fingerprint(post):
    return f"{post['thread_id']}:{post.get('version','')}:{post.get('title','')}"


# =========================
# DISCORD
# =========================

def send_discord(embed):
    if not WEBHOOK:
        raise ValueError("Missing DISCORD_WEBHOOK")

    requests.post(WEBHOOK, json={"embeds": [embed]}, timeout=15)


def log(title, desc, color=3447003):
    send_discord({
        "title": title,
        "description": desc,
        "color": color,
        "timestamp": datetime.utcnow().isoformat()
    })


# =========================
# FETCH (RETRY)
# =========================

def fetch_posts():
    delay = 2

    for _ in range(3):
        try:
            r = requests.get(API_URL, timeout=30)
            r.raise_for_status()
            return r.json()["msg"]["data"]
        except Exception as e:
            print("Fetch error:", e)
            time.sleep(delay)
            delay *= 2

    return []


# =========================
# RECOVERY
# =========================

def should_recover(state):
    return time.time() - state.get("last_success_ts", 0) > RECOVERY_HOURS * 3600


def recovery_limit(state, posts):
    spike = sum(state.get("history", [])[-5:]) > 30
    limit = 5 if spike else RECOVERY_LIMIT
    return posts[:limit]


# =========================
# HEARTBEAT
# =========================

def heartbeat(state):
    now = time.time()

    if now - state.get("last_heartbeat_ts", 0) > HEARTBEAT_INTERVAL:
        log("🟢 Heartbeat", "Bot is alive")
        state["last_heartbeat_ts"] = now


# =========================
# WATCHDOG
# =========================

def check_watchdog(state):
    now = time.time()
    if now - state.get("last_run_ts", 0) > 15 * 60:
        log("🚨 CRON ALERT", "Possible GitHub Actions failure", color=16711680)


# =========================
# MAIN
# =========================

def run():
    print("🚀 Bot started")

    state = load_state()

    state["last_run_ts"] = time.time()

    auto_heal_workflow(state)

    posts = fetch_posts()
    if not posts:
        log("❌ Fetch failed", "No data from API", 16711680)
        return

    posts.sort(key=lambda x: int(x["thread_id"]), reverse=True)

    seen = set(state.get("seen", []))
    new_seen = set(seen)

    recovery = should_recover(state)

    if recovery:
        log("🟠 Recovery mode", "Rebuilding state")
        posts = recovery_limit(state, posts)

    sent = 0

    for post in posts:
        fp = fingerprint(post)

        if fp in seen:
            continue

        send_discord({
            "title": post.get("title"),
            "url": f"https://f95zone.to/threads/{post['thread_id']}",
            "color": 65280,
            "image": {"url": post.get("cover", "")},
            "fields": [
                {"name": "Creator", "value": post.get("creator", "N/A"), "inline": True},
                {"name": "Version", "value": post.get("version", "N/A"), "inline": True}
            ],
            "timestamp": datetime.utcnow().isoformat()
        })

        new_seen.add(fp)
        sent += 1

    state["seen"] = list(new_seen)[-500:]
    state["last_success_ts"] = time.time()
    state["history"].append(sent)
    state["history"] = state["history"][-20:]

    heartbeat(state)
    check_watchdog(state)

    save_state(state)

    print(f"✅ Done - sent {sent}")


if __name__ == "__main__":
    run()
