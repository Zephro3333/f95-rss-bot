import requests
from feedgen.feed import FeedGenerator

URL = "https://f95zone.to/sam/latest_alpha/latest_data.php?cmd=rss&cat=games"
BASE = "https://f95zone.to"


def fetch():
    r = requests.get(URL, timeout=30)
    feed = r.json() if URL.endswith("json") else None
    return None


def fetch_rss():
    import feedparser
    return feedparser.parse(URL).entries


def build():
    fg = FeedGenerator()
    fg.title("F95 AUTO FEED")
    fg.link(href=BASE)
    fg.description("Auto RSS bot")
    fg.language("en")

    entries = fetch_rss()

    for e in entries[:30]:

        title = getattr(e, "title", "no title")
        link = getattr(e, "link", BASE)

        img = ""
        if hasattr(e, "media_content"):
            try:
                img = e.media_content[0]["url"]
            except:
                pass

        entry = fg.add_entry()
        entry.title(title)
        entry.link(href=link)
        entry.description(f"<img src='{img}'><br>{title}")

    fg.rss_file("f95_feed.xml")


if __name__ == "__main__":
    build()