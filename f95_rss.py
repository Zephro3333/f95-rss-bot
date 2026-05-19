name: F95 Discord Bot

on:
  schedule:
    - cron: "*/5 * * * *"
  workflow_dispatch:

permissions:
  contents: write

# =========================
# PREVENT RUN OVERLAPS
# =========================
concurrency:
  group: f95-discord-bot
  cancel-in-progress: true

jobs:
  bot:
    runs-on: ubuntu-latest
    timeout-minutes: 10

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      # =========================
      # SAFE PYTHON SETUP
      # =========================
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install requests feedparser feedgen

      # =========================
      # GUARANTEED STATE FILE
      # =========================
      - name: Ensure state file exists
        run: |
          if [ ! -f last_seen.json ]; then
            echo '{"seen":[],"last_update_ts":0,"last_heartbeat_ts":0,"history_intervals":[]}' > last_seen.json
          fi

      # =========================
      # RUN BOT
      # =========================
      - name: Run bot
        env:
          DISCORD_WEBHOOK: ${{ secrets.DISCORD_WEBHOOK }}
        run: |
          set -e
          echo "🚀 Running bot..."
          python f95_discord_bot.py

      # =========================
      # DEBUG SAFETY (helps silent failures)
      # =========================
      - name: Debug state
        if: always()
        run: |
          echo "==== STATE FILE ===="
          cat last_seen.json || true

      # =========================
      # COMMIT SAFELY (NO RACE CONDITIONS)
      # =========================
      - name: Commit state safely
        run: |
          git config user.name "github-actions"
          git config user.email "github-actions@github.com"

          # IMPORTANT: re-sync before commit (prevents conflicts)
          git pull --rebase origin main || true

          git add last_seen.json

          # only commit if changes exist
          git diff --cached --quiet && echo "No changes" && exit 0

          git commit -m "chore: update bot state [skip ci]"

      # =========================
      # SAFE PUSH WITH RETRIES
      # =========================
      - name: Push changes safely
        run: |
          for i in 1 2 3; do
            git push origin main && break
            echo "⚠️ Push failed, retrying..."
            git pull --rebase origin main || true
            sleep 3
          done

      # =========================
      # FINAL HEALTH CHECK
      # =========================
      - name: Workflow health check
        if: always()
        run: |
          echo "✅ Workflow finished"
