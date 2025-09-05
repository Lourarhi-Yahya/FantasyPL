# Deploy Options

## Option A — Render (free worker)
1) Create a new repo from this project.
2) Add `render.yaml` to the repository root (already included here).
3) In Render, "New +" → "Blueprint" → connect repo → confirm.
4) Set environment variables in Render dashboard:
   - TELEGRAM_BOT_TOKEN (required)
   - X_BEARER_TOKEN (optional, recommended)
   - QUERY_WINDOW_HOURS (default 72)
   - TEAM_FILTER (optional)
5) Deploy. The worker will run long-polling and serve Telegram.

## Option B — Railway (Dockerfile)
1) Push repo to GitHub.
2) On Railway: "New Project" → "Deploy from GitHub".
3) Railway detects the Dockerfile. Set env vars in project settings.
4) Deploy the service (it runs the bot process).

## Option C — Fly.io
1) Install flyctl, run `fly launch --no-deploy` (or use provided fly.toml).
2) `fly secrets set TELEGRAM_BOT_TOKEN=... X_BEARER_TOKEN=...`
3) `fly deploy`

## Option D — VPS (Ubuntu)
```bash
sudo apt update && sudo apt install -y python3-pip git
git clone <your-repo-url> fpl-bot && cd fpl-bot
pip install -r requirements.txt
cp .env.example .env   # fill tokens
python app/bot.py
```
Use `tmux`/`screen` or systemd to keep it running.

## Webhooks vs Polling
This bot uses **long polling** which is reliable on most PaaS/VPS without HTTPS config.
If you prefer **webhooks**, we can add a small FastAPI server and set Telegram webhook URL.
