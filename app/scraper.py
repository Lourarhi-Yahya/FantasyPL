from __future__ import annotations
import os, subprocess, json, datetime as dt
from typing import List, Dict, Any
import httpx
from .config import SETTINGS

# Basic query set for FPL chatter
DEFAULT_QUERIES = [
    "FPL",
    "Fantasy Premier League",
    "#FPL",
    "#FPLCommunity",
    "captain pick FPL",
    "injury FPL",
]

def _since_time_iso(hours: int) -> str:
    return (dt.datetime.utcnow() - dt.timedelta(hours=hours)).isoformat(timespec="seconds") + "Z"

def _scrape_with_x_api() -> list[dict]:
    # Minimal X API v2 recent search (you need Elevated access).
    headers = {"Authorization": f"Bearer {SETTINGS.X_BEARER_TOKEN}"}
    all_posts = []
    since = _since_time_iso(SETTINGS.QUERY_WINDOW_HOURS)
    for q in DEFAULT_QUERIES:
        params = {
            "query": q + " -is:retweet lang:en",
            "max_results": 50,
            "start_time": since,
            "tweet.fields": "created_at,lang,public_metrics",
        }
        r = httpx.get("https://api.twitter.com/2/tweets/search/recent", params=params, headers=headers, timeout=30)
        r.raise_for_status()
        data = r.json().get("data", [])
        for t in data:
            all_posts.append({
                "text": t.get("text", ""),
                "created_at": t.get("created_at"),
                "retweet_count": t.get("public_metrics", {}).get("retweet_count", 0),
                "reply_count": t.get("public_metrics", {}).get("reply_count", 0),
                "like_count": t.get("public_metrics", {}).get("like_count", 0),
                "quote_count": t.get("public_metrics", {}).get("quote_count", 0),
            })
    return all_posts

def _scrape_with_snscrape() -> list[dict]:
    # Uses snscrape CLI. No login, best-effort. May break.
    # Example query: posts from last N hours, English, excluding retweets.
    since = _since_time_iso(SETTINGS.QUERY_WINDOW_HOURS)
    results: list[dict] = []
    for q in DEFAULT_QUERIES:
        query = f'{q} lang:en since:{since[:10]}'  # snscrape supports `since:YYYY-MM-DD`
        cmd = ["snscrape", "--jsonl", "twitter-search", query]
        try:
            proc = subprocess.run(cmd, capture_output=True, check=True, text=True, timeout=60)
            for line in proc.stdout.splitlines():
                j = json.loads(line)
                results.append({
                    "text": j.get("rawContent") or j.get("content") or "",
                    "created_at": j.get("date"),
                    "retweet_count": j.get("retweetCount", 0),
                    "reply_count": j.get("replyCount", 0),
                    "like_count": j.get("likeCount", 0),
                    "quote_count": j.get("quoteCount", 0),
                })
        except Exception as e:
            # Fallback to empty set if snscrape fails
            pass
    return results

def collect_posts() -> list[dict]:
    if SETTINGS.X_BEARER_TOKEN:
        return _scrape_with_x_api()
    return _scrape_with_snscrape()
