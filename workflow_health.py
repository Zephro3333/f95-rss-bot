import os
import requests
import base64

REPO = "Zephro3333/f95-rss-bot"
TOKEN = os.getenv("GITHUB_TOKEN")


def auto_heal_workflow(state):
    # simples safety check
    if not state.get("seen"):
        return

    # simulação de detecção leve (podes expandir depois)
    if state.get("last_run_ts", 0) == 0:
        push_recovery_workflow()


def push_recovery_workflow():
    url = f"https://api.github.com/repos/{REPO}/contents/.github/workflows/rss.yml"

    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Accept": "application/vnd.github+json"
    }

    content = """name: F95 Bot

on:
  schedule:
    - cron: '*/5 * * * *'
  workflow_dispatch:

permissions:
  contents: write

jobs:
  bot:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: echo 'auto-heal workflow active'
"""

    payload = {
        "message": "auto-heal: restore workflow",
        "content": base64.b64encode(content.encode()).decode()
    }

    requests.put(url, json=payload, headers=headers)
