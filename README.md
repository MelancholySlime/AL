# 🌙 Arknights: Endfield – Auto Daily Sign-in

Automatically checks in daily on [game.skport.com/endfield/sign-in](https://game.skport.com/endfield/sign-in) via **GitHub Actions** every day at **3:00 AM (GMT+7)**.

---

## ✨ Features

- ⚙️ Automated daily check-in via **GitHub Actions**
- 👥 **Multi-account** support — one Secret per account
- 📢 Notifications via **Discord** and **Telegram**

---

## 🚀 Setup Guide

### Step 1 – Get Your `ACCOUNT_TOKEN`

`ACCOUNT_TOKEN` is a long-lived cookie (~several months). You only need to grab it once.

**Method 1: Via URL (easiest)**

1. Log into [skport.com](https://www.skport.com)
2. Open a new tab and navigate to:
   ```
   https://web-api.skport.com/cookie_store/account_token
   ```
3. The page will display your token — **copy the entire string**

**Method 2: Via DevTools**

1. Log into [skport.com](https://www.skport.com)
2. Press **F12** → **Application** tab (Chrome) or **Storage** tab (Firefox)
3. Go to **Cookies** → `https://www.skport.com` (or `.skport.com`)
4. Find the cookie named **`ACCOUNT_TOKEN`** → copy its value

> ⚠️ **Note:** `ACCOUNT_TOKEN` is different from `SK_OAUTH_CRED_KEY`. Make sure you copy the correct one.

---

### Step 2 – Add Secrets to GitHub

Go to **Settings → Secrets and variables → Actions → New repository secret**

#### One Secret per account

| Secret Name | Value |
|-------------|-------|
| `ACCOUNT_1` | JSON for account 1 |
| `ACCOUNT_2` | JSON for account 2 |
| `ACCOUNT_3` | ... |

**JSON format for each Secret:**

```json
{
  "account_token": "YOUR_ACCOUNT_TOKEN",
  "lang":          "en",
  "name":          "Yuuki"
}
```

| Field | Description | Required |
|-------|-------------|----------|
| `account_token` | Token from Step 1 | ✅ |
| `lang` | Language: `en` / `ja` / `zh_Hant` / `zh_Hans` / `ko` / `ru_RU` | ❌ (default `en`) |
| `name` | Display name shown in logs | ❌ (default `Account N`) |

> 💡 **No need to enter Game ID or Server** — the script detects them automatically!

---

### Step 3 – Set Up Notifications (Optional)

#### Discord

1. Go to your Discord server → ⚙️ **Edit Channel** → **Integrations** → **Webhooks** → **New Webhook**
2. Copy the Webhook URL
3. Create a Secret named `DISCORD_WEBHOOK` with that URL

**Example notification:**
```
📋 Endfield Sign-in Report
────────────────────────────────
[Yuuki] ✅ Check-in successful! (Day 12) | Reward: Module Component x1
[Aurora] ℹ️  Already checked in today!
```

#### Telegram

1. Chat with **[@BotFather](https://t.me/botfather)** → `/newbot` → get your **Bot Token**
2. Chat with **[@userinfobot](https://t.me/userinfobot)** → get your **Chat ID**
3. Create 2 Secrets:

| Secret Name | Value |
|-------------|-------|
| `DISCORD_WEBHOOK` | Discord Webhook URL |
| `TELEGRAM_BOT_TOKEN` | Bot Token from BotFather |
| `TELEGRAM_CHAT_ID` | Your personal or group Chat ID |

> **Note for Telegram:** You must send at least one message to the bot before it can message you. Find your bot by username → click **Start**.

---

### Step 4 – Push to GitHub

```bash
git add .
git commit -m "feat: add Endfield auto sign-in"
git push
```

▶️ **Manual run:** Actions → 🌙 Endfield Daily Sign-in → **Run workflow**

---

## 📅 Schedule

| Timezone | Time |
|----------|------|
| **GMT+7** (Vietnam / Jakarta) | **3:00 AM** daily |
| UTC | 20:00 (previous day) |

---

## 💬 Status Messages

| Message | Meaning |
|---------|---------|
| ✅ Check-in successful! | Successfully checked in, includes reward info |
| ℹ️ Already checked in today! | Normal — already done for today |
| ⚠️ ACCOUNT_TOKEN expired! | Need to refresh token (Step 1) |
| ❌ Failed to get OAuth code | Invalid `ACCOUNT_TOKEN` |

---

## 🔄 When to Renew Your Token

`ACCOUNT_TOKEN` typically lasts **several months**. When you receive `⚠️ ACCOUNT_TOKEN expired!`:

1. Visit `https://web-api.skport.com/cookie_store/account_token`
2. Copy the new token
3. Update the corresponding `ACCOUNT_N` Secret

---

## 🔒 Security

- `ACCOUNT_TOKEN` is stored in **GitHub Secrets** (AES-256 encrypted)
- **No one in the repository** can read Secret values — including contributors
- Tokens are only injected into the environment at runtime and never appear in logs

---

## 📁 Project Structure

```
.
├── sign_in.py                   # Main sign-in script
├── requirements.txt             # curl-cffi
├── .github/
│   └── workflows/
│       └── sign_in.yml          # GitHub Actions workflow
└── README.md
```

---

*Made with 💜 | Inspired by [nano-shino/EndfieldCheckin](https://github.com/nano-shino/EndfieldCheckin) and [Areha11Fz/ArknightsEndfieldAutoCheckIn](https://github.com/Areha11Fz/ArknightsEndfieldAutoCheckIn)*
