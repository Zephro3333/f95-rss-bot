import requests
import os
from datetime import datetime

API_URL = "https://f95zone.to/sam/latest_alpha/latest_data.php?cmd=list&cat=games&page=1&sort=date"

WEBHOOK = os.getenv("DISCORD_WEBHOOK")


# =========================
# FETCH
# =========================

def fetch_posts():

    for attempt in range(3):

        try:
            r = requests.get(API_URL, timeout=30)

            r.raise_for_status()

            data = r.json()

            posts = data.get("msg", {}).get("data", [])

            print(f"📦 API posts: {len(posts)}")

            return posts

        except Exception as e:

            print(f"Fetch retry {attempt+1}/3:", e)

    return []


# =========================
# DISCORD
# =========================

def send_discord(embed):

    try:

        r = requests.post(
            WEBHOOK,
            json={"embeds": [embed]},
            timeout=20
        )

        print("Discord status:", r.status_code)

        return r.status_code == 204

    except Exception as e:

        print("Discord error:", e)

        return False


# =========================
# ALERTS
# =========================

def send_alert(title, description):

    embed = {
        "title": title,
        "description": description,
        "color": 16711680,
        "timestamp": datetime.utcnow().isoformat()
    }

    send_discord(embed)


# =========================
# EMBED BUILDER
# =========================

def build_embed(post):

    cover = post.get("cover") or ""

    return {
        "title": post.get("title", "Unknown Title"),
        "url": f"https://f95zone.to/threads/{post.get('thread_id')}",
        "color": 65280,

        "image": {
            "url": cover
        },

        "fields": [
            {
                "name": "Creator",
                "value": post.get("creator", "Unknown"),
                "inline": True
            },
            {
                "name": "Version",
                "value": post.get("version", "N/A"),
                "inline": True
            },
            {
                "name": "Rating",
                "value": str(post.get("rating", "0")),
                "inline": True
            }
        ],

        "footer": {
            "text": "F95 Auto Bot"
        },

        "timestamp": datetime.utcnow().isoformat()
    }
