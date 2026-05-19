import requests
import os

API_URL = "https://f95zone.to/sam/latest_alpha/latest_data.php?cmd=list&cat=games&page=1&sort=date"
WEBHOOK = os.getenv("DISCORD_WEBHOOK")


def fetch_posts():
    for _ in range(3):
        try:
            r = requests.get(API_URL, timeout=30)
            r.raise_for_status()
            return r.json()["msg"]["data"]
        except Exception as e:
            print("API error retrying:", e)

    return []


def send_to_discord(post):
    embed = {
        "title": post.get("title"),
        "url": f"https://f95zone.to/threads/{post['thread_id']}",
        "color": 65280,
        "image": {"url": post.get("cover", "")},
        "fields": [
            {"name": "Creator", "value": post.get("creator", "N/A"), "inline": True},
            {"name": "Version", "value": post.get("version", "N/A"), "inline": True}
        ]
    }

    requests.post(WEBHOOK, json={"embeds": [embed]})
