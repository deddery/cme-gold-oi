"""Telegram notification helper shared by the CME and COT flows."""
from __future__ import annotations

import os
import urllib.parse
import urllib.request


def send_telegram(message: str) -> None:
    token, chat_id = os.getenv("TELEGRAM_BOT_TOKEN"), os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        print("Telegram secrets absent: dashboard updated without notification")
        return
    body = urllib.parse.urlencode({"chat_id": chat_id, "text": message, "parse_mode": "HTML"}).encode()
    request = urllib.request.Request(f"https://api.telegram.org/bot{token}/sendMessage", data=body, method="POST")
    with urllib.request.urlopen(request, timeout=30) as response:
        if response.status != 200:
            raise RuntimeError(f"Telegram returned HTTP {response.status}")
