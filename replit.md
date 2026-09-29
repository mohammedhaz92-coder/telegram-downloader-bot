# Telegram downloader bot

This is a Python Telegram bot (`bot.py`) that polls Telegram for messages; it does not serve a web page. The **Telegram bot** console workflow runs `python bot.py`. Python 3.12 and FFmpeg are provided by `.replit`; Python packages are listed in `requirements.txt`.

To run it, create a new Telegram bot token with BotFather, revoke the token that was previously committed to `bot.py`, and add the new token to Replit Secrets as `BOT_TOKEN`. Never put the token in code, chat, or README. Start or restart the **Telegram bot** workflow after adding the secret. To try the bot, open its Telegram chat, send `/start`, then send a supported media URL and tap a download option.

The bot needs an active workflow to keep polling Telegram. There is no web preview or HTTP port.