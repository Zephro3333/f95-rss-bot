import requests
import json
import os
import hashlib
import time

API_URL = "https://f95zone.to/sam/latest_alpha/latest_data.php?cmd=list&cat=games&page=1&sort=date"
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK")
STATE_FILE = "last_seen.json"

# base config
NORMAL_WINDOW = 50
RECOVERY_WINDOW = 150  # anti-delay mode
RECOVERY_THRESHOLD = 10  # se encontrar muitos novos → recovery


def make_hash(post):
    base = f"{post.get('thread_id')}-{post.get('title')}"
    return hashlib.md5(base.encode()).hexdigest()


def load_state():
    if not os.path.exists(STATE_FILE):
        return set()

    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    except:
        return set()


def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(list(state)[-800:], f)


def send_to_discord(post):
    try:
        embed = {
            "title": post.get("title", "No title"),
            "url": f"https://f95zone.to/threads/{post['thread_id']}",
            "color": 65280,
            "image": {"url": post.get("cover", "")},
            "footer": {"text": "F95 Bot - anti-delay mode"}
        }

        r = requests.post(WEBHOOK_URL, json={"embeds": [embed]}, timeout=15)
        return r.status_code == 204

    except Exception as e:
        print("Discord error:", e)
        return False


def fetch_posts():
    r = requests.get(API_URL, timeout=20)
    r.raise_for_status()
    return r.json()["msg"]["data"]


def run():

    print("Fetching API...")

    posts = fetch_posts()

    seen = load_state()
    new_seen = set(seen)

    normal_batch = posts[:NORMAL_WINDOW]

    new_count = 0

    # 1️⃣ normal scan
    for post in normal_batch:
        pid = make_hash(post)

        if pid not in seen:
            ok = send_to_discord(post)

            if ok:
                new_seen.add(pid)
                new_count += 1

    # 2️⃣ anti-delay detector
    recovery_mode = False

    if new_count >= RECOVERY_THRESHOLD:
        recovery_mode = True
        print("⚠ Recovery mode activated (possible missed posts)")

    # 3️⃣ recovery scan (deep scan)
    if recovery_mode:
        for post in posts[:RECOVERY_WINDOW]:
            pid = make_hash(post)

            if pid not in new_seen:
                print("RECOVERY FOUND:", post["title"])

                ok = send_to_discord(post)

                if ok:
                    new_seen.add(pid)
                    new_count += 1

                time.sleep(0.2)  # anti spam / rate limit safety

    save_state(new_seen)

    print(f"Done. Total sent: {new_count}")


if __name__ == "__main__":
    run()
