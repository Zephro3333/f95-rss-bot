# f95_bot/client.py

import requests

API_URL = "https://f95zone.to/sam/latest_alpha/latest_data.php?cmd=list&cat=games&page=1&sort=date"
WEBHOOK = None

def fetch_posts():
    r = requests.get(API_URL, timeout=30)
    r.raise_for_status()
    return r.json()["msg"]["data"]


def send_to_discord(post):
    import os
    global WEBHOOK

    if WEBHOOK is None:
        WEBHOOK = os.getenv("DISCORD_WEBHOOK")

    embed = {
        "title": post.get("title"),
        "url": f"https://f95zone.to/threads/{post['thread_id']}",
        "color": 65280,
        "image": {"url": post.get("cover", "")},
        "fields": [
            {"name": "Creator", "value": post.get("creator", "N/A"), "inline": True},
            {"name": "Version", "value": post.get("version", "N/A"), "inline": True},
        ],
    }

    requests.post(WEBHOOK, json={"embeds": [embed]})
