#!/usr/bin/env python3
"""
Arknights: Endfield - Auto Daily Sign-in Script
================================================
Tự động điểm danh hàng ngày trên game.skport.com/endfield/sign-in

Mỗi GitHub Secret ACCOUNT_N = 1 tài khoản (JSON đơn giản):
  { "account_token": "...", "lang": "en", "name": "Yuuki" }

- account_token  : Lấy từ cookie ACCOUNT_TOKEN trên skport.com (dài hạn, ~vài tháng)
- Game ID / server: Tự động detect qua API, không cần nhập tay
- cred / signToken: Tự động refresh mỗi lần chạy → không bao giờ bị 401 nữa

References:
  https://github.com/nano-shino/EndfieldCheckin
  https://github.com/Areha11Fz/ArknightsEndfieldAutoCheckIn
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

from curl_cffi import requests

# ─────────────────────────────────────────────
#  CONSTANTS
# ─────────────────────────────────────────────

APP_CODE         = "6eb76d4e13aa36e6"
PLATFORM         = "3"
VNAME            = "1.0.0"
ENDFIELD_GAME_ID = "3"      # App type, không phải role ID

URL_GRANT        = "https://as.gryphline.com/user/oauth2/v2/grant"
URL_GEN_CRED     = "https://zonai.skport.com/web/v1/user/auth/generate_cred_by_code"
URL_REFRESH      = "https://zonai.skport.com/web/v1/auth/refresh"
URL_BINDING      = "https://zonai.skport.com/api/v1/game/player/binding"
URL_ATTENDANCE   = "https://zonai.skport.com/web/v1/game/endfield/attendance"

# ─────────────────────────────────────────────
#  LOAD ACCOUNTS
#  Mỗi Secret ACCOUNT_N chứa JSON:
#  {
#    "account_token": "ACCOUNT_TOKEN cookie từ skport.com",
#    "lang":          "en",       // tuỳ chọn, mặc định "en"
#    "name":          "Yuuki"     // tên hiển thị tuỳ ý
#  }
# ─────────────────────────────────────────────

def load_accounts() -> list[dict]:
    accounts = []
    for i in range(1, 21):
        raw = os.environ.get(f"ACCOUNT_{i}", "").strip()
        if not raw:
            continue
        try:
            acc = json.loads(raw)
        except json.JSONDecodeError as e:
            print(f"  [WARN] ACCOUNT_{i} không phải JSON hợp lệ: {e} — bỏ qua")
            continue

        if not acc.get("account_token", "").strip():
            print(f"  [WARN] ACCOUNT_{i} thiếu 'account_token' — bỏ qua")
            continue

        acc.setdefault("lang", "en")
        acc.setdefault("name", f"Account {i}")
        accounts.append(acc)

    return accounts


# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────

def mask_id(game_id: str) -> str:
    """Hiển thị nửa đầu ID, che nửa sau bằng ● để bảo mật."""
    n = len(game_id)
    show = (n + 1) // 2
    return game_id[:show] + "●" * (n - show)


def make_headers(cred: str, lang: str, timestamp: str, sign: str = "") -> dict:
    h = {
        "cred":        cred,
        "platform":    PLATFORM,
        "vname":       VNAME,
        "timestamp":   timestamp,
        "sk-language": lang,
    }
    if sign:
        h["sign"] = sign
    return h


# ─────────────────────────────────────────────
#  SIGNING (HMAC-SHA256 → MD5)
#  Giống GAS: computeHmacSha256Signature + computeDigest MD5
# ─────────────────────────────────────────────

def compute_sign(path: str, body: str, timestamp: str, sign_token: str) -> str:
    header_obj = {
        "platform":  PLATFORM,
        "timestamp": timestamp,
        "dId":       "",
        "vName":     VNAME,
    }
    sign_string = path + body + timestamp + json.dumps(header_obj, separators=(",", ":"))

    hmac_hex = hmac.new(
        sign_token.encode("utf-8"),
        sign_string.encode("utf-8"),
        hashlib.sha256,
    ).digest().hex()

    return hashlib.md5(hmac_hex.encode("utf-8")).hexdigest()


# ─────────────────────────────────────────────
#  AUTH FLOW (3 bước, chạy mỗi lần → tự refresh)
# ─────────────────────────────────────────────

def get_oauth_code(account_token: str) -> str | None:
    """Bước 1: ACCOUNT_TOKEN → OAuth code (tạm thời)."""
    payload = {"token": account_token, "appCode": APP_CODE, "type": 0}
    try:
        r = requests.post(URL_GRANT, json=payload, timeout=20, impersonate="chrome")
        data = r.json()
        if data.get("status") == 0 and data.get("data", {}).get("code"):
            return data["data"]["code"]
        print(f"    [Auth-1] GRANT thất bại: {data}")
    except Exception as e:
        print(f"    [Auth-1] Lỗi: {e}")
    return None


def get_cred(oauth_code: str) -> str | None:
    """Bước 2: OAuth code → cred (session identifier)."""
    payload = {"kind": 1, "code": oauth_code}
    try:
        r = requests.post(URL_GEN_CRED, json=payload, timeout=20, impersonate="chrome")
        data = r.json()
        if data.get("code") == 0 and data.get("data", {}).get("cred"):
            return data["data"]["cred"]
        print(f"    [Auth-2] GEN_CRED thất bại: {data}")
    except Exception as e:
        print(f"    [Auth-2] Lỗi: {e}")
    return None


def get_sign_token(cred: str, lang: str) -> str | None:
    """Bước 3: cred → signToken (dùng để ký request, refresh mỗi lần chạy)."""
    timestamp = str(int(time.time()))
    headers = make_headers(cred, lang, timestamp)
    try:
        r = requests.get(URL_REFRESH, headers=headers, timeout=20, impersonate="chrome")
        data = r.json()
        if data.get("code") == 0 and data.get("data", {}).get("token"):
            return data["data"]["token"]
        print(f"    [Auth-3] REFRESH thất bại: {data}")
    except Exception as e:
        print(f"    [Auth-3] Lỗi: {e}")
    return None


# ─────────────────────────────────────────────
#  GAME ROLE AUTO-DETECT
# ─────────────────────────────────────────────

def get_game_roles(cred: str, sign_token: str, lang: str) -> list[str]:
    """Tự động lấy tất cả game roles Endfield của account."""
    path = "/api/v1/game/player/binding"
    timestamp = str(int(time.time()))
    sign = compute_sign(path, "", timestamp, sign_token)
    headers = make_headers(cred, lang, timestamp, sign)

    try:
        r = requests.get(URL_BINDING, headers=headers, timeout=20, impersonate="chrome")
        data = r.json()
        roles = []
        if data.get("code") == 0:
            for app in data.get("data", {}).get("list", []):
                if app.get("appCode") == "endfield":
                    for binding in app.get("bindingList", []):
                        for role in binding.get("roles", []):
                            roles.append(
                                f"{ENDFIELD_GAME_ID}_{role['roleId']}_{role['serverId']}"
                            )
        return roles
    except Exception as e:
        print(f"    [Binding] Lỗi: {e}")
        return []


# ─────────────────────────────────────────────
#  ATTENDANCE
# ─────────────────────────────────────────────

def send_attendance(cred: str, sign_token: str, game_role: str, lang: str) -> dict:
    """Gửi yêu cầu điểm danh cho 1 game role."""
    path = "/web/v1/game/endfield/attendance"
    timestamp = str(int(time.time()))
    sign = compute_sign(path, "", timestamp, sign_token)
    headers = make_headers(cred, lang, timestamp, sign)
    headers["Content-Type"] = "application/json"
    headers["sk-game-role"] = game_role

    r = requests.post(URL_ATTENDANCE, headers=headers, timeout=20, impersonate="chrome")
    return r.json()


def parse_response(data: dict, name: str, role_id: str) -> str:
    code = data.get("code")
    msg  = data.get("message", "Unknown")

    if code == 0:
        # Điểm danh thành công — parse phần thưởng nếu có
        reward_str = ""
        d = data.get("data") or {}
        if d.get("reward"):
            rw = d["reward"]
            reward_str = f" | Phần thưởng: {rw.get('name', '?')} x{rw.get('count', '?')}"
        elif d.get("awardIds") and d.get("resourceInfoMap"):
            items = []
            for entry in d["awardIds"]:
                info = d["resourceInfoMap"].get(entry.get("id", ""), {})
                if info:
                    items.append(f"{info.get('name','?')} x{info.get('count','?')}")
            if items:
                reward_str = f" | Phần thưởng: {', '.join(items)}"
        day = d.get("signInCount", "?")
        return f"[{name}] ✅ Điểm danh thành công! (Ngày {day}){reward_str}"

    elif code in (1001, 10001) or "already" in msg.lower() or "again" in msg.lower():
        return f"[{name}] ℹ️  Đã điểm danh hôm nay rồi!"

    elif code == 10002:
        return (
            f"[{name}] ⚠️  ACCOUNT_TOKEN hết hạn!\n"
            f"  → Lấy lại tại: skport.com → F12 → Application → Cookies → ACCOUNT_TOKEN\n"
            f"  → Cập nhật Secret ACCOUNT_N tương ứng."
        )
    else:
        return f"[{name}] ℹ️  {msg} (code={code}, role={role_id})"


# ─────────────────────────────────────────────
#  PER-ACCOUNT SIGN-IN
# ─────────────────────────────────────────────

def do_sign_in(acc: dict) -> list[str]:
    """Thực hiện toàn bộ flow cho 1 tài khoản, trả về list kết quả."""
    account_token = acc["account_token"].strip()
    lang          = acc.get("lang", "en").strip()
    name          = acc.get("name", "Player").strip()

    # 1. Auth flow
    oauth_code = get_oauth_code(account_token)
    if not oauth_code:
        return [f"[{name}] ❌ Không lấy được OAuth code — kiểm tra ACCOUNT_TOKEN!"]

    cred = get_cred(oauth_code)
    if not cred:
        return [f"[{name}] ❌ Không lấy được cred từ OAuth code!"]

    sign_token = get_sign_token(cred, lang)
    if not sign_token:
        return [f"[{name}] ❌ Không refresh được signToken!"]

    # 2. Auto-detect game roles
    roles = get_game_roles(cred, sign_token, lang)
    if not roles:
        return [f"[{name}] ⚠️  Không tìm thấy game role Endfield nào trong account này!"]

    # 3. Điểm danh từng role
    results = []
    for role in roles:
        parts  = role.split("_")  # "3_<roleId>_<serverId>"
        role_id = parts[1] if len(parts) >= 2 else role
        mask   = mask_id(role_id)
        print(f"  → Role: {mask}")

        try:
            data = send_attendance(cred, sign_token, role, lang)
            result = parse_response(data, name, mask)
        except Exception as e:
            result = f"[{name}] ❌ Lỗi kết nối: {e}"

        print(f"    {result}")
        results.append(result)
        time.sleep(1)

    return results


# ─────────────────────────────────────────────
#  NOTIFICATION
# ─────────────────────────────────────────────

def send_discord(webhook: str, message: str) -> None:
    if not webhook:
        return
    payload = {
        "username":   "Endfield Sign-in Bot",
        "avatar_url": "https://static.skport.com/asset/game/endfield_740c9ea5dd44bf4a3e6932c595e30a26.png",
        "content":    message,
    }
    try:
        r = requests.post(webhook, json=payload, timeout=10, impersonate="chrome")
        if r.status_code not in (200, 204):
            print(f"  [Discord] HTTP {r.status_code}")
    except Exception as e:
        print(f"  [Discord] {e}")


def send_telegram(bot_token: str, chat_id: str, message: str) -> None:
    if not (bot_token and chat_id):
        return
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    try:
        r = requests.post(
            url,
            json={"chat_id": chat_id, "text": message, "parse_mode": "HTML"},
            timeout=10,
            impersonate="chrome",
        )
        if not r.ok:
            print(f"  [Telegram] {r.text[:200]}")
    except Exception as e:
        print(f"  [Telegram] {e}")


# ─────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────

def main() -> None:
    print("=" * 52)
    print("  🌙 Arknights: Endfield – Auto Daily Sign-in")
    print("=" * 52)

    discord_webhook    = os.environ.get("DISCORD_WEBHOOK", "").strip()
    telegram_bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    telegram_chat_id   = os.environ.get("TELEGRAM_CHAT_ID", "").strip()

    accounts = load_accounts()

    if not accounts:
        msg = (
            "❌ Không tìm thấy tài khoản nào!\n"
            'Tạo Secret ACCOUNT_1: {"account_token":"...","lang":"en","name":"Yuuki"}'
        )
        print(msg)
        send_discord(discord_webhook, msg)
        send_telegram(telegram_bot_token, telegram_chat_id, msg)
        return

    print(f"\nTìm thấy {len(accounts)} tài khoản.\n")

    all_results = []
    for acc in accounts:
        name = acc.get("name", "Player")
        print(f"{'─' * 40}")
        print(f"→ Tài khoản: {name}")
        results = do_sign_in(acc)
        all_results.extend(results)
        print()

    summary      = "\n".join(all_results)
    full_message = f"📋 Endfield Sign-in Report\n{'─' * 32}\n{summary}"

    print("=" * 52)
    print(full_message)

    send_discord(discord_webhook, full_message)
    send_telegram(telegram_bot_token, telegram_chat_id, full_message)

    print("\n✅ Hoàn thành!")


if __name__ == "__main__":
    main()
