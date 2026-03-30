#!/usr/bin/env python3
"""
Arknights: Endfield - Auto Daily Sign-in Script
================================================
Tự động điểm danh hàng ngày trên game.skport.com/endfield/sign-in

Mỗi GitHub Secret ACCOUNT_N = 1 tài khoản (JSON)
Xem README.md để biết cách cấu hình.
"""

import os
import sys
import json
import hmac
import hashlib
import time

# Fix UTF-8 output trên Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

# curl_cffi giả lập TLS fingerprint Chrome → bypass TencentEdgeOne 40x
from curl_cffi import requests

# ─────────────────────────────────────────────
#  CONSTANTS
# ─────────────────────────────────────────────

SIGN_IN_URL  = "https://zonai.skport.com/web/v1/game/endfield/attendance"
SIGN_IN_PATH = "/web/v1/game/endfield/attendance"

BASE_HEADERS = {
    "Accept":          "*/*",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Content-Type":    "application/json",
    "User-Agent":      "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:135.0) Gecko/20100101 Firefox/135.0",
    "Referer":         "https://game.skport.com/",
    "platform":        "3",
    "vName":           "1.0.0",
    "Origin":          "https://game.skport.com",
    "Connection":      "keep-alive",
    "Sec-Fetch-Dest":  "empty",
    "Sec-Fetch-Mode":  "cors",
    "Sec-Fetch-Site":  "same-site",
    "Priority":        "u=0",
}

# ─────────────────────────────────────────────
#  LOAD ACCOUNTS
#  Mỗi Secret ACCOUNT_N chứa 1 JSON tài khoản:
#  {
#    "cred":    "SK_OAUTH_CRED_KEY",
#    "token":   "SK_TOKEN_CACHE_KEY",
#    "game_id": "123456789",
#    "server":  "2",          // 2=Asia  3=EU/Americas
#    "lang":    "en",
#    "name":    "Tên hiển thị"
#  }
# ─────────────────────────────────────────────

def load_accounts() -> list[dict]:
    accounts = []
    for i in range(1, 21):          # Hỗ trợ tối đa 20 tài khoản
        raw = os.environ.get(f"ACCOUNT_{i}", "").strip()
        if not raw:
            continue               # Bỏ qua slot trống, tiếp tục dò

        try:
            acc = json.loads(raw)
        except json.JSONDecodeError as e:
            print(f"  [WARN] ACCOUNT_{i} không phải JSON hợp lệ: {e} — bỏ qua")
            continue

        # Validate bắt buộc
        missing = [k for k in ("cred", "token", "game_id") if not acc.get(k, "").strip()]
        if missing:
            print(f"  [WARN] ACCOUNT_{i} thiếu field: {missing} — bỏ qua")
            continue

        acc.setdefault("server", "2")
        acc.setdefault("lang",   "en")
        acc.setdefault("name",   f"Account {i}")
        accounts.append(acc)

    return accounts

# ─────────────────────────────────────────────
#  SIGNING LOGIC
# ─────────────────────────────────────────────

def generate_sign(path: str, method: str, headers: dict,
                  query: str, body: str, token: str) -> str:
    string_to_sign = path + (query if method.upper() == "GET" else body)

    ts = headers.get("timestamp", "")
    if ts:
        string_to_sign += ts

    header_obj = {}
    for key in ["platform", "timestamp", "dId", "vName"]:
        if key in headers:
            header_obj[key] = headers[key]
        elif key == "dId":
            header_obj[key] = ""

    string_to_sign += json.dumps(header_obj, separators=(",", ":"))

    hmac_hex = hmac.new(
        token.encode("utf-8"),
        string_to_sign.encode("utf-8"),
        hashlib.sha256,
    ).digest().hex()

    return hashlib.md5(hmac_hex.encode("utf-8")).hexdigest()


# ─────────────────────────────────────────────
#  SIGN-IN
# ─────────────────────────────────────────────

def do_sign_in(acc: dict) -> str:
    cred    = acc["cred"].strip()
    token   = acc["token"].strip()
    game_id = acc["game_id"].strip()
    server  = acc.get("server", "2").strip()
    lang    = acc.get("lang",   "en").strip()
    name    = acc.get("name",   "Player").strip()

    timestamp = str(int(time.time()))

    headers = {
        **BASE_HEADERS,
        "cred":         cred,
        "sk-game-role": f"3_{game_id}_{server}",
        "sk-language":  lang,
        "timestamp":    timestamp,
    }
    headers["sign"] = generate_sign(SIGN_IN_PATH, "POST", headers, "", "", token)

    try:
        resp = requests.post(
            SIGN_IN_URL,
            headers=headers,
            timeout=30,
            impersonate="chrome",
        )
    except Exception as e:
        return f"[{name}] ❌ Lỗi kết nối: {e}"

    try:
        data = resp.json()
    except Exception:
        return f"[{name}] ❌ HTTP {resp.status_code} — Response không phải JSON: {resp.text[:200]}"

    code    = data.get("code")
    message = data.get("message", "Unknown")

    # HTTP 401 hoặc code 10000 = cred/token hết hạn
    if resp.status_code == 401 or code == 10000:
        return (
            f"[{name}] ⚠️  Cred/Token hết hạn! (HTTP {resp.status_code})\n"
            f"  → Lấy lại: game.skport.com/endfield/sign-in → F12 → Console\n"
            f"  → Cập nhật Secret ACCOUNT_N tương ứng."
        )
    # HTTP 403 + code 10001 = đã điểm danh hôm nay
    elif code == 10001:
        return f"[{name}] ℹ️  Đã điểm danh hôm nay rồi!"
    elif message == "OK":
        return f"[{name}] ✅ Điểm danh thành công!"
    else:
        return f"[{name}] ℹ️  {message} (code={code}, HTTP {resp.status_code})"


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

    # Thông báo chung (tuỳ chọn)
    discord_webhook    = os.environ.get("DISCORD_WEBHOOK", "").strip()
    telegram_bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    telegram_chat_id   = os.environ.get("TELEGRAM_CHAT_ID", "").strip()

    accounts = load_accounts()

    if not accounts:
        msg = (
            "❌ Không tìm thấy tài khoản nào!\n"
            "Hãy tạo Secret ACCOUNT_1 (và ACCOUNT_2, ...) trong GitHub Secrets.\n"
            'Format: {"cred":"...","token":"...","game_id":"...","server":"2","lang":"en","name":"..."}'
        )
        print(msg)
        send_discord(discord_webhook, msg)
        send_telegram(telegram_bot_token, telegram_chat_id, msg)
        return

    print(f"\nTìm thấy {len(accounts)} tài khoản.\n")

    results = []
    for acc in accounts:
        name = acc.get("name", "Player")
        print(f"→ Đang điểm danh: {name} (ID: {acc.get('game_id', '?')})")
        result = do_sign_in(acc)
        print(f"  {result}\n")
        results.append(result)
        time.sleep(1.5)     # Tránh rate limit

    summary      = "\n".join(results)
    full_message = f"📋 Endfield Sign-in Report\n{'─' * 32}\n{summary}"

    print("─" * 52)
    print(full_message)

    send_discord(discord_webhook, full_message)
    send_telegram(telegram_bot_token, telegram_chat_id, full_message)

    print("\n✅ Hoàn thành!")


if __name__ == "__main__":
    main()
