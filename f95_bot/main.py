from f95_bot.client import fetch_posts, send_to_discord
from f95_bot.state import load_state, save_state, update_heartbeat


def run():
    state = load_state()

    posts = fetch_posts()

    if not posts:
        print("No posts fetched")
        return

    # ordenar do mais recente → mais antigo
    posts.sort(key=lambda x: int(x["thread_id"]), reverse=True)

    last_seen = state.get("last_seen_id", 0)

    new_last_seen = last_seen
    sent = 0

    for post in posts:
        pid = int(post["thread_id"])

        # ZERO LOSS: já processado
        if pid <= last_seen:
            continue

        send_to_discord(post)
        sent += 1

        if pid > new_last_seen:
            new_last_seen = pid

    state["last_seen_id"] = new_last_seen

    state["history"].append(sent)
    state["history"] = state["history"][-20:]

    update_heartbeat(state)
    save_state(state)

    print(f"ZERO LOSS MODE - sent {sent} posts")


if __name__ == "__main__":
    run()
