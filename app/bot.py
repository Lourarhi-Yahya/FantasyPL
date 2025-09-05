from __future__ import annotations
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from .config import SETTINGS
from .fpl import FPLClient
from .scraper import collect_posts
from .recommender import generate_recommendations
from .formatter import format_markdown_digest

HELP = (
    "/start - Hello\n"
    "/gw - Get this week's recommendations\n"
    "/help - Show commands"
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hi! I'm your FPL bot. Type /gw for picks.")

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(HELP)

async def gw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.chat.send_action("typing")
    fpl = FPLClient()
    posts = collect_posts()
    bootstrap = fpl.load_bootstrap()
    recs = generate_recommendations(posts, bootstrap, top_n=10)
    await update.message.reply_markdown(format_markdown_digest(recs))

def main():
    token = SETTINGS.TELEGRAM_BOT_TOKEN
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN missing in environment.")
    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("gw", gw))
    app.run_polling()

if __name__ == "__main__":
    main()
