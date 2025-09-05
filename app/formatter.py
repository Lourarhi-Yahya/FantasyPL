from __future__ import annotations
from typing import List, Dict, Any

POS = {1: "GKP", 2: "DEF", 3: "MID", 4: "FWD"}

def format_markdown_digest(recs: List[Dict[str, Any]]) -> str:
    lines = ["*FPL Weekly Recommendations (MVP)*\n"]
    for i, r in enumerate(recs, 1):
        lines.append(f"*{i}. {r['player']}* — {POS.get(r['position'],'?')} — £{r['price']:.1f}")
        c = r["components"]
        lines.append(f"  Score: *{r['score']}*  | Mentions: {r['mentions']}")
        lines.append(f"  Buzz {c['buzz']} · Sent {c['sentiment']} · Form {c['form']} · Fixture {c['fixture']}\n")
    return "\n".join(lines) if recs else "_No recommendations yet. Try later._"
