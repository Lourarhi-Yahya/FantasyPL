# Simple Dockerfile for FPL Twitter → Telegram bot
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

# Expect env vars at runtime:
# TELEGRAM_BOT_TOKEN, X_BEARER_TOKEN (optional), QUERY_WINDOW_HOURS, TEAM_FILTER
CMD ["python", "app/bot.py"]
