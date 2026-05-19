import time
import hashlib

from f95_bot.client import (
    fetch_posts,
    send_discord,
    send_alert,
    build_embed
)

from f95_bot.state import (
    load_state,
    save_state,
    update_heartbeat
)

# =========================
# CONFIG
# =========================

MAX_SEEN = 5000


# =========================
# HASH SYSTEM
# =========================

def make_hash(post):
    raw = f"{post.get('thread_id')}:{post.get('title')}:{post.get('version')}"
    return hashlib.md5(raw.encode()).hexdigest()


# =========================
# MAIN
# =========================

def run():
    print("🚀 Starting F95 Engine")

    state = load_state()

    seen = set(state.get("seen", []))

    posts = fetch_posts()

    # =========================
    # EMPTY API PROTECTION
    # =========================

    if not posts:
        print("⚠️ Empty API response")

        send_alert(
            "⚠️ F95 API Empty",
            "API returned zero posts."
        )

        return

    # =========================
    # ORDERING
    # =========================

    posts.sort(
        key=lambda x: int(x.get("thread_id", 0)),
        reverse=True
    )

    new_seen = set(seen)

    sent = 0

    # =========================
    # PROCESS POSTS
    # =========================

    for post in posts:

        try:
            post_hash = make_hash(post)

            # anti-duplication
            if post_hash in seen:
                continue

            # send
            send_discord(build_embed(post))

            # mark seen only AFTER successful send
            new_seen.add(post_hash)

            sent += 1

            print(f"✅ Sent: {post.get('title')}")

            # small protection delay
            time.sleep(1)

        except Exception as e:
            print("POST ERROR:", e)

    # =========================
    # CLEAN STATE
    # =========================

    if len(new_seen) > MAX_SEEN:
        new_seen = set(list(new_seen)[-MAX_SEEN:])

    state["seen"] = list(new_seen)

    update_heartbeat(state)

    save_state(state)

    print(f"🎯 Cycle complete | Sent: {sent}")


if __name__ == "__main__":
    run()
