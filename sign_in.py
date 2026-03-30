#!/usr/bin/env python3
"""
Arknights: Endfield - Auto Daily Sign-in Script
================================================
Tự động điểm danh hàng ngày trên game.skport.com/endfield/sign-in

Chỉ cần 1 GitHub Secret duy nhất: ENDFIELD_CONFIG (JSON)
Xem README.md để biết cách cấu hình.
"""

import os
import sys
import json
import hmac
import hashlib
import time

# curl_cffi giả lập TLS fingerprint của Chrome → bypass Cloudflare 403
from curl_cffi import requests

# ─────────────────────────────────────────────
#  CONSTANTS
# ─────────────────────────────────────────────

SIGN_IN_URL  = "https://zonai.skport.com/web/v1/game/endfield/attendance"
SIGN_IN_PATH = "/web/v1/game/endfield/attendance"

BASE_HEADERS = {
    "Accept":           "*/*",
    "Accept-Encoding":  "gzip, deflate, br, zstd",
    "Content-Type":     "application/json",
    "User-Agent":       "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:135.0) Gecko/20100101 Firefox/135.0",
    "Referer":          "https://game.skport.com/",
    "platform":         "3",
    "vName":            "1.0.0",
    "Origin":           "https://game.skport.com",
    "Connection":       "keep-alive",
    "Sec-Fetch-Dest":   "empty",
    "Sec-Fetch-Mode":   "cors",
    "Sec-Fetch-Site":   "same-site",
    "Priority":         "u=0",
}

# ─────────────────────────────────────────────
#  LOAD CONFIG from single JSON secret
# ─────────────────────────────────────────────

def load_config() -> dict:
    """
    Đọc toàn bộ config từ biến môi trường ENDFIELD_CONFIG (JSON string).

    Cấu trúc JSON:
    {
      "accounts": [
        {
          "cred":    "SK_OAUTH_CRED_KEY value",
          "token":   "SK_TOKEN_CACHE_KEY value",
          "game_id": "123456789",
          "server":  "2",
          "lang":    "en",
          "name":    "Player 1"
        }
      ],
      "discord_webhook":    "https://discord.com/api/webhooks/...",
      "telegram_bot_token": "...",
      "telegram_chat_id":   "..."
    }
    """
    raw = os.environ.get("ENDFIELD_CONFIG", "").strip()
    if not raw:
        print("❌ Biến môi trường ENDFIELD_CONFIG chưa được đặt!")
        print("   Vui lòng tạo Secret ENDFIELD_CONFIG trong GitHub Secrets.")
        sys.exit(1)

    try:
        config = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"❌ ENDFIELD_CONFIG không phải JSON hợp lệ: {e}")
        sys.exit(1)

    return config


# ─────────────────────────────────────────────
#  SIGNING LOGIC (HMAC-SHA256 → MD5)
# ─────────────────────────────────────────────

def generate_sign(path: str, method: str, headers: dict, query: str, body: str, token: str) -> str:
    """
    Tái tạo đúng logic signing của trang gốc (JS → Python):
      stringToSign = path + (GET ? query : body)
                   + timestamp
                   + JSON.stringify({ platform, timestamp, dId, vName })
      sign = MD5( HEX( HMAC-SHA256(stringToSign, token) ) )
    """
    string_to_sign = path + (query if method.upper() == "GET" else body)

    timestamp = headers.get("timestamp", "")
    if timestamp:
        string_to_sign += str(timestamp)

    header_obj = {}
    for key in ["platform", "timestamp", "dId", "vName"]:
        if key in headers:
            header_obj[key] = headers[key]
        elif key == "dId":
            header_obj[key] = ""

    string_to_sign += json.dumps(header_obj, separators=(",", ":"))

    hmac_bytes = hmac.new(
        token.encode("utf-8"),
        string_to_sign.encode("utf-8"),
        hashlib.sha256,
    ).digest()
    hmac_hex = hmac_bytes.hex()

    return hashlib.md5(hmac_hex.encode("utf-8")).hexdigest()


# ─────────────────────────────────────────────
#  SIGN-IN FUNCTION
# ─────────────────────────────────────────────

def do_sign_in(account: dict) -> str:
    """Điểm danh cho một tài khoản, trả về chuỗi kết quả."""
    cred    = account.get("cred", "")
    token   = account.get("token", "")
    game_id = account.get("game_id", "")
    server  = account.get("server", "2")
    lang    = account.get("lang", "en")
    name    = account.get("name", "Player")

    if not (cred and token and game_id):
        return f"[{name}] ❌ Thiếu cred / token / game_id trong config!"

    timestamp = str(int(time.time()))

    headers = {
        **BASE_HEADERS,
        "cred":          cred,
        "sk-game-role":  f"3_{game_id}_{server}",
        "sk-language":   lang,
        "timestamp":     timestamp,
    }
    headers["sign"] = generate_sign(SIGN_IN_PATH, "POST", headers, "", "", token)

    try:
        # impersonate="chrome" → gửi đúng TLS fingerprint của Chrome, bypass Cloudflare
        resp = requests.post(
            SIGN_IN_URL,
            headers=headers,
            timeout=30,
            impersonate="chrome",
        )
        data = resp.json()
    except Exception as e:
        return f"[{name}] ❌ Request error: {e}"

    if resp.status_code == 403:
        return f"[{name}] ❌ 403 Forbidden – cred có thể đã hết hạn, hãy lấy lại token!"
    if resp.status_code != 200:
        return f"[{name}] ❌ HTTP {resp.status_code}: {resp.text[:200]}"

    code    = data.get("code")
    message = data.get("message", "Unknown")

    if code == 10000:
        return (
            f"[{name}] ⚠️  Token hết hạn!\n"
            f"  → Vui lòng cập nhật 'cred' và 'token' trong ENDFIELD_CONFIG."
        )
    elif message == "OK":
        return f"[{name}] ✅ Điểm danh thành công!"
    else:
        return f"[{name}] ℹ️  {message} (code={code})"


# ─────────────────────────────────────────────
#  NOTIFICATION
# ─────────────────────────────────────────────

def send_discord(webhook: str, message: str) -> None:
    if not webhook:
        return
    payload = {
        "username":   "Endfield Sign-in Bot",
        "avatar_url": "https://i.imgur.com/TguAOiA.png",
        "content":    message,
    }
    try:
        r = requests.post(webhook, json=payload, timeout=10, impersonate="chrome")
        if r.status_code not in (200, 204):
            print(f"  [Discord] Warning: HTTP {r.status_code}")
    except Exception as e:
        print(f"  [Discord] Error: {e}")


def send_telegram(bot_token: str, chat_id: str, message: str) -> None:
    if not (bot_token and chat_id):
        return
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "HTML"}
    try:
        r = requests.post(url, json=payload, timeout=10, impersonate="chrome")
        if not r.ok:
            print(f"  [Telegram] Warning: {r.text[:200]}")
    except Exception as e:
        print(f"  [Telegram] Error: {e}")


# ─────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────

def main() -> None:
    print("=" * 52)
    print("  🌙 Arknights: Endfield – Auto Daily Sign-in")
    print("=" * 52)

    config   = load_config()
    accounts = config.get("accounts", [])

    discord_webhook    = config.get("discord_webhook", "")
    telegram_bot_token = config.get("telegram_bot_token", "")
    telegram_chat_id   = config.get("telegram_chat_id", "")

    if not accounts:
        msg = (
            "❌ Không tìm thấy tài khoản nào trong ENDFIELD_CONFIG!\n"
            "Kiểm tra lại key 'accounts' trong JSON."
        )
        print(msg)
        send_discord(discord_webhook, msg)
        send_telegram(telegram_bot_token, telegram_chat_id, msg)
        return

    results = []
    for acc in accounts:
        name = acc.get("name", "Player")
        print(f"\n→ Đang điểm danh: {name} (ID: {acc.get('game_id', '?')})")
        result = do_sign_in(acc)
        print(f"  {result}")
        results.append(result)
        time.sleep(1)  # tránh rate limit

    summary      = "\n".join(results)
    full_message = f"📋 Endfield Sign-in Report\n{'─' * 32}\n{summary}"

    print(f"\n{'─' * 52}")
    print(full_message)

    send_discord(discord_webhook, full_message)
    send_telegram(telegram_bot_token, telegram_chat_id, full_message)

    print("\n✅ Hoàn thành!")


if __name__ == "__main__":
    main()
