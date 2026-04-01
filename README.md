# 🌙 Arknights: Endfield – Auto Daily Sign-in

Automated daily sign-in for [Arknights: Endfield](https://game.skport.com/endfield/sign-in) via **GitHub Actions** — runs every day at **3:00 AM (GMT+7)**.

---

## ✨ Features

- ✅ Automated daily sign-in via GitHub Actions
- 👥 Multi-account support — one Secret per account
- 📢 Discord notification (optional)

---

## 🚀 Setup

### Step 1 — Get your `ACCOUNT_TOKEN`

1. Log in to [skport.com](https://www.skport.com)
2. Open a new tab and visit:
   ```
   https://web-api.skport.com/cookie_store/account_token
   ```
3. Copy the token value shown on the page

> Alternatively: **F12 → Application → Cookies → `.skport.com` → `ACCOUNT_TOKEN`**

---

### Step 2 — Add GitHub Secrets

Go to **Settings → Secrets and variables → Actions → New repository secret**

#### Account secrets (one per account)

| Secret | Value |
|--------|-------|
| `ACCOUNT_1` | JSON for account 1 |
| `ACCOUNT_2` | JSON for account 2 |

**JSON format:**
```json
{
  "account_token": "YOUR_ACCOUNT_TOKEN",
  "lang": "en",
  "name": "Display Name"
}
```

| Field | Description | Required |
|-------|-------------|----------|
| `account_token` | Token from Step 1 | ✅ |
| `lang` | Language: `en` / `ja` / `ko` / `zh_Hans` / `zh_Hant` / `ru_RU` | ❌ default `en` |
| `name` | Display name in logs | ❌ |

> Game ID and server are **auto-detected** — no manual input needed.

#### Discord notification (optional)

| Secret | Value |
|--------|-------|
| `DISCORD_WEBHOOK` | Your Discord Webhook URL |

**How to get a webhook:** Discord server → ⚙️ Edit Channel → Integrations → Webhooks → New Webhook → Copy URL

---

### Step 3 — Push & Run

```bash
git add .
git commit -m "feat: Endfield auto sign-in"
git push
```

To run manually: **Actions → 🌙 Endfield Daily Sign-in → Run workflow**

---

## 🔄 Token Renewal

`ACCOUNT_TOKEN` typically lasts **several months**. When you see `⚠️ ACCOUNT_TOKEN expired`:

1. Visit `https://web-api.skport.com/cookie_store/account_token`
2. Copy the new token
3. Update the corresponding `ACCOUNT_N` secret

---

## 📅 Schedule

| Timezone | Time |
|----------|------|
| GMT+7 (Vietnam/Bangkok) | **3:00 AM** daily |
| UTC | 8:00 PM (previous day) |

---

*Made with 💜 · [README (Tiếng Việt)](README_Vi.md) · References: [nano-shino/EndfieldCheckin](https://github.com/nano-shino/EndfieldCheckin), [Areha11Fz/ArknightsEndfieldAutoCheckIn](https://github.com/Areha11Fz/ArknightsEndfieldAutoCheckIn)*
