from __future__ import annotations
from typing import List, Dict, Any
from collections import Counter, defaultdict
import re, math

from textblob import TextBlob

SCORING_WEIGHTS = {
    "buzz": 0.35,        # volume + engagement
    "sentiment": 0.20,   # positive chatter
    "form": 0.25,        # from FPL stats
    "fixture": 0.20,     # opponent difficulty
}

# Helper to create a mapping: {player_lower_name: player_dict}
def _player_map_from_bootstrap(fpl_bootstrap: dict) -> dict:
    players = fpl_bootstrap.get("elements", [])
    return { (p["web_name"] or p["second_name"] or p["first_name"]).lower(): p for p in players }

def _team_name_map(fpl_bootstrap: dict) -> dict:
    teams = fpl_bootstrap.get("teams", [])
    return { t["id"]: t for t in teams }

def _extract_player_mentions(posts: List[dict], player_map_keys: List[str]) -> List[str]:
    mentions = []
    for p in posts:
        text = p.get("text", "")
        low = text.lower()
        for name in player_map_keys:
            # simple tokenized contains; avoid short/unreliable matches
            if len(name) >= 4 and re.search(rf"\b{name}\b", low):
                mentions.append(name)
    return mentions

def _buzz_score(eng: dict) -> float:
    # log scale to dampen outliers
    s = eng.get("retweet_count", 0) + eng.get("reply_count", 0) + eng.get("like_count", 0) + eng.get("quote_count", 0)
    return math.log10(1 + s)

def _sentiment_score(text: str) -> float:
    # Normalize from [-1,1] -> [0,1]
    pol = TextBlob(text).sentiment.polarity
    return (pol + 1.0) / 2.0

def _fixture_difficulty(player: dict, fpl_bootstrap: dict) -> float:
    # Use next opponent difficulty from 'fixtures' in bootstrap: element_type/teams not directly hold FDR, so approximate via team strength (1 strong .. 5 weak)
    teams = _team_name_map(fpl_bootstrap)
    team = teams.get(player.get("team"))
    if not team:
        return 0.5
    # team['strength'] (lower = stronger) in old APIs; normalize inverse: 1..5 -> 0..1
    strength = team.get("strength", 3)
    # Favor players from stronger teams (lower strength) facing weaker opposition is not in bootstrap; MVP keep simple:
    return 1 - min(max((strength - 1) / 4, 0), 1)

def _form_score(player: dict) -> float:
    try:
        form = float(player.get("form") or 0.0)  # already 0..~10 ish
    except:
        form = 0.0
    return min(form / 10.0, 1.0)

def generate_recommendations(posts: List[dict], fpl_bootstrap: dict, top_n: int = 10) -> List[Dict[str, Any]]:
    pmap = _player_map_from_bootstrap(fpl_bootstrap)
    keys = list(pmap.keys())
    mentions = _extract_player_mentions(posts, keys)

    # Aggregate buzz & sentiment per player
    agg = defaultdict(lambda: {"mention_count":0, "buzz":0.0, "sentiment_sum":0.0, "samples":0})
    for p in posts:
        text = p.get("text","")
        low = text.lower()
        # compute post-level stats
        sent = _sentiment_score(text)
        buzz = _buzz_score(p)

        for name in keys:
            if len(name) >= 4 and re.search(rf"\b{name}\b", low):
                agg[name]["mention_count"] += 1
                agg[name]["buzz"] += buzz
                agg[name]["sentiment_sum"] += sent
                agg[name]["samples"] += 1

    results = []
    for name, stats in agg.items():
        player = pmap[name]
        form = _form_score(player)
        fixture = _fixture_difficulty(player, fpl_bootstrap)
        buzz = stats["buzz"] / max(stats["samples"], 1)
        sentiment = stats["sentiment_sum"] / max(stats["samples"], 1)

        score = (
            SCORING_WEIGHTS["buzz"] * buzz +
            SCORING_WEIGHTS["sentiment"] * sentiment +
            SCORING_WEIGHTS["form"] * form +
            SCORING_WEIGHTS["fixture"] * fixture
        )
        results.append({
            "player": player["web_name"],
            "team": player["team"],
            "position": player["element_type"],  # 1 GKP, 2 DEF, 3 MID, 4 FWD
            "price": player["now_cost"] / 10.0,
            "form": player.get("form"),
            "score": round(score, 4),
            "components": {
                "buzz": round(buzz, 3),
                "sentiment": round(sentiment, 3),
                "form": round(form, 3),
                "fixture": round(fixture, 3),
            },
            "mentions": stats["mention_count"],
        })

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_n]
