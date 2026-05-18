import requests
import json
import os

# API do F95
API_URL = "https://f95zone.to/sam/latest_alpha/latest_data.php?cmd=list&cat=games&page=1&sort=date"

# webhook vindo dos GitHub Secrets
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK")

# ficheiro para guardar posts já enviados
STATE_FILE = "last_seen.json"


# carregar posts antigos
if os.path.exists(STATE_FILE):
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        seen = set(json.load(f))
else:
    seen = set()


def send_to_discord(post):

    embed = {
        "title": post.get("title", "No title"),
        "url": f"https://f95zone.to/threads/{post['thread_id']}",
        "color": 65280,

        # imagem do jogo
        "image": {
            "url": post.get("cover", "")
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
            "text": "F95 Discord Bot"
        }
    }

    payload = {
        "embeds": [embed]
    }

    r = requests.post(WEBHOOK_URL, json=payload)

    print("Discord status:", r.status_code)


print("A ir buscar API...")

try:
    response = requests.get(API_URL, timeout=30)
    response.raise_for_status()

    json_data = response.json()

    posts = json_data["msg"]["data"]

    print("Posts encontrados:", len(posts))

    new_seen = set(seen)

    sent = 0

    for post in posts:

        pid = str(post["thread_id"])

        # evita repetir posts antigos
        if pid not in seen:

            print("Novo post:", post["title"])

            send_to_discord(post)

            new_seen.add(pid)

            sent += 1

    # guardar estado
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(list(new_seen), f)

    print(f"OK - enviados {sent} novos posts")

except Exception as e:
    print("ERRO:", e)