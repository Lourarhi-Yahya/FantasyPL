from __future__ import annotations
import httpx, functools, time
from typing import Dict, Any

BOOTSTRAP = "https://fantasy.premierleague.com/api/bootstrap-static/"
FIXTURES  = "https://fantasy.premierleague.com/api/fixtures/"

def http_get_json(url: str) -> dict:
    with httpx.Client(timeout=30) as client:
        r = client.get(url, headers={"User-Agent": "FPL-Telegram-Bot/1.0"})
        r.raise_for_status()
        return r.json()

class FPLClient:
    def load_bootstrap(self) -> Dict[str, Any]:
        return http_get_json(BOOTSTRAP)

    def load_fixtures(self) -> list[dict]:
        return http_get_json(FIXTURES)
