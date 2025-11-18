````markdown
```markdown
# whispered desire - anonymous Telegram whisper bot

A small, minimal Telegram bot that lets users submit anonymous "whispers" (short messages) stored in a local SQLite database.

Features
- /whisper <text> — save an anonymous message
- /mylast — retrieve your most recent whisper (uses a one-way hash of your Telegram user id)
- /start, /help — usage info

Quick start (local)
1. Create a bot and get a token from BotFather.
2. Set environment variable TELEGRAM_BOT_TOKEN with your bot token.
3. Optionally set BOT_SALT and DB_PATH (defaults shown in code).
4. Run:
   ```bash
   export TELEGRAM_BOT_TOKEN="123:ABC..."
   python bot.py
   ```

Run with Docker
1. Build the image:
   ```bash
   docker build -t whispered-desire .
   ```
2. Run and mount a data volume for the DB:
   ```bash
   docker run -e TELEGRAM_BOT_TOKEN="..." -v $(pwd)/data:/data whispered-desire
   ```

Deploy
- Procfile is provided for Heroku-style deployments: `worker: python bot.py`
- The bot reads config from environment variables, making it simple to deploy on most platforms.

Security & Privacy
- Whispers are stored in SQLite at DB_PATH (default: whispers.db).
- The /mylast command is enabled by storing a non-reversible hash of the Telegram user id so users can optionally retrieve their own whispers; the raw Telegram id is not stored in plaintext.
- If you need full anonymity (no way to retrieve a user's own whispers), set the code to store user_hash as NULL (change in save_whisper call) — I can adjust that if you prefer.

Next steps
- Add moderation or admin commands (e.g., delete, list).
- Add message length limits, profanity filters, or rate limiting.
- Add persistence in a managed database if you plan to scale.
```
````