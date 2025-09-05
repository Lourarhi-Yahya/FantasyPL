from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseModel):
    TELEGRAM_BOT_TOKEN: str | None = os.getenv("TELEGRAM_BOT_TOKEN")
    X_BEARER_TOKEN: str | None = os.getenv("X_BEARER_TOKEN")
    QUERY_WINDOW_HOURS: int = int(os.getenv("QUERY_WINDOW_HOURS", "72"))
    TEAM_FILTER: str | None = os.getenv("TEAM_FILTER")  # e.g., "MCI,ARS,LIV"

SETTINGS = Settings()
