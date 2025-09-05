# FPL Twitter (X) → Weekly Recommendations → Telegram Bot

An MVP that:
1) Collects public posts about Fantasy Premier League (search queries/hashtags) using **one of two options**:
   - **Preferred (compliant)**: X API (v2+). You need a developer account + bearer token.
   - **Fallback (no-key, best-effort)**: `snscrape` to fetch recent public posts. (Heads‑up: scraping can break and may conflict with site terms; use the official API when possible.)
2) Pulls live FPL data from the public **FPL API** (e.g., `https://fantasy.premierleague.com/api/bootstrap-static/`).
3) Scores players weekly by combining: buzz (volume/sentiment), recent form, xGI/xGC, price changes, fixtures.
4) Publishes a digest to a **Telegram bot** on demand (`/gw`) or on a weekly schedule.

## Quickstart (local)

### 0) Requirements
- Python 3.10+
- (Optional) Docker & Docker Compose
- A Telegram bot token (create via @BotFather)

### 1) Clone & Install
```bash
pip install -r requirements.txt
cp .env.example .env
# then fill TELEGRAM_BOT_TOKEN and (optionally) X_BEARER_TOKEN
```

### 2) Run
- One-off recommendation run & print to console:
```bash
python main.py once
```
- Start the Telegram bot:
```bash
python app/bot.py
```

### 3) Schedule (cron example)
Use cron or a worker to run weekly (e.g., Thursday 09:00 UTC):
```
0 9 * * 4 /usr/bin/python /path/to/main.py weekly >> /var/log/fpl_bot.log 2>&1
```

## Docker (optional)
```bash
docker compose up --build
```

## Structure
```
app/
  config.py            # env handling & constants
  scraper.py           # X API OR snscrape
  fpl.py               # FPL endpoints helpers
  recommender.py       # scoring logic
  formatter.py         # text/markdown/telegram formatting
  bot.py               # Telegram bot commands
main.py                # CLI entry: once / weekly
requirements.txt
.env.example
docker-compose.yml
```

## Notes
- **Compliance**: Prefer the official X API for stability and terms compliance.
- **FPL API**: Public read endpoints only.
- **MVP**: Scoring is intentionally simple and explainable; tweak `SCORING_WEIGHTS` and heuristics.
- **Next**: Persist to a DB (e.g., SQLite/Postgres), add web dashboard, improve NER for player matching.
