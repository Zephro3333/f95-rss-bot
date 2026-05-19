import requests
import json
import os
import time

API_URL = "https://f95zone.to/sam/latest_alpha/latest_data.php?cmd=list&cat=games&page=1&sort=date"
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK")
STATE_FILE = "last_seen.json"

# load state safely
def load_state():
    try:
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return set(json.load(f))
    except:
        pass
    return set()

def save_state(state):
    try:
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(list(state)[-500:], f)
    except Exception as e:
        print("STATE SAVE ERROR:", e)

seen = load_state()


def send_to_discord(post):
    try:
        embed = {
            "title": post.get("title", "No title"),
            "url": f"https://f95zone.to/threads/{post['thread_id']}",
            "color": 65280,
            "image": {"url": post.get("cover", "")},
            "fields": [
                {"name": "Creator", "value": post.get("creator", "Unknown"), "inline": True},
                {"name": "Version", "value": post.get("version", "N/A"), "inline": True},
                {"name": "Rating", "value": str(post.get("rating", "0")), "inline": True}
            ],
            "footer": {"text": "F95 Bot - stable mode"}
        }

        r = requests.post(WEBHOOK_URL, json={"embeds": [embed]}, timeout=15)
        print("Discord status:", r.status_code)

        return r.status_code == 204

    except Exception as e:
        print("DISCORD ERROR:", e)
        return False


def fetch_posts():
    try:
        r = requests.get(API_URL, timeout=20)
        r.raise_for_status()
        return r.json()["msg"]["data"]
    except Exception as e:
        print("API ERROR:", e)
        return []


def run():
    global seen

    print("Checking API...")

    posts = fetch_posts()
    if not posts:
        print("No data received")
        return

    new_count = 0

    for post in posts:
        pid = str(post["thread_id"])

        if pid not in seen:
            print("NEW:", post["title"])

            success = send_to_discord(post)

            if success:
                seen.add(pid)
                new_count += 1

                # save incrementally (prevents data loss)
                save_state(seen)

    print(f"Done. New posts sent: {new_count}")


if __name__ == "__main__":
    run()
if __name__ == "__main__":
    build()
