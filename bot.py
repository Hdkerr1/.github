#!/usr/bin/env python3
# whispered desire - simple anonymous whisper Telegram bot

"""
whispered desire - simple anonymous whisper Telegram bot

Usage:
- Set TELEGRAM_BOT_TOKEN in environment before running.
- Optional: DB_PATH (default: whispers.db) and BOT_SALT (default: random constant).
"""
import os
import sqlite3
import hashlib
import logging
from datetime import datetime

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("whispered-desire")

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
DB_PATH = os.environ.get("DB_PATH", "whispers.db")
BOT_SALT = os.environ.get("BOT_SALT", "whispered-desire-default-salt")

def ensure_db(path: str):
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS whispers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL,
            user_hash TEXT
        )
        """
    )
    conn.commit()
    conn.close()

def user_hash_from_id(user_id: int) -> str:
    h = hashlib.sha256(f"{BOT_SALT}:{user_id}".encode("utf-8")).hexdigest()
    return h

def save_whisper(path: str, content: str, user_hash: str | None = None) -> int:
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    created_at = datetime.utcnow().isoformat() + "Z"
    cur.execute(
        "INSERT INTO whispers (content, created_at, user_hash) VALUES (?, ?, ?)",
        (content, created_at, user_hash),
    )
    rowid = cur.lastrowid
    conn.commit()
    conn.close()
    return rowid

def get_last_for_user(path: str, user_hash: str):
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.execute(
        "SELECT id, content, created_at FROM whispers WHERE user_hash = ? ORDER BY id DESC LIMIT 1",
        (user_hash,),
    )
    row = cur.fetchone()
    conn.close()
    return row


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome to whispered desire.\n\n"
        "Commands:\n"
        "/whisper <text> - send an anonymous whisper\n"
        "/mylast - show your last whisper (uses a non-reversible hash so you can retrieve your own whisper)\n"
        "/help - show this message"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start_command(update, context)


async def whisper_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Accept text following command
    text = " ".join(context.args).strip()
    if not text:
        # If user replied to a message with /whisper, allow content from replied message
        if update.message.reply_to_message and update.message.reply_to_message.text:
            text = update.message.reply_to_message.text.strip()
    if not text:
        await update.message.reply_text(
            "Please provide the text of your whisper. Usage:\n/whisper I have a secret..."
        )
        return

    user = update.effective_user
    uhash = user_hash_from_id(user.id) if user else None
    whisper_id = save_whisper(DB_PATH, text, uhash)
    await update.message.reply_text(
        f"Your whisper has been saved anonymously (id #{whisper_id}). "
        "Use /mylast to retrieve your most recent whisper."
    )


async def mylast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not user:
        await update.message.reply_text("Unable to determine your user identity.")
        return
    uhash = user_hash_from_id(user.id)
    row = get_last_for_user(DB_PATH, uhash)
    if not row:
        await update.message.reply_text("You have no saved whispers.")
        return
    whisper_id, content, created_at = row
    await update.message.reply_text(
        f"Your last whisper (id #{whisper_id}, saved {created_at}):\n\n{content}"
    )


def main():
    if not TELEGRAM_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN environment variable is not set. Exiting.")
        return

    ensure_db(DB_PATH)

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("whisper", whisper_command))
    app.add_handler(CommandHandler("mylast", mylast_command))

    logger.info("Starting whispered desire bot...")
    app.run_polling()


if __name__ == "__main__":
    main()
