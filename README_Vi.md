# 🌙 Arknights: Endfield – Auto Daily Sign-in

Script tự động điểm danh hàng ngày trên [game.skport.com/endfield/sign-in](https://game.skport.com/endfield/sign-in), chạy bằng **GitHub Actions** lúc **3:00 sáng (GMT+7)** mỗi ngày.

---

## ✨ Tính năng

- ✅ Tự động điểm danh mỗi ngày lúc 3h sáng GMT+7
- 👥 Hỗ trợ **nhiều tài khoản** — mỗi Secret = 1 account
- 🔑 Dùng `ACCOUNT_TOKEN` dài hạn (~vài tháng) — không cần renew thường xuyên
- 🔄 **Tự động refresh** `cred` và `signToken` mỗi lần chạy — không bao giờ bị 401
- 🔍 **Tự động detect** Game ID và Server — không cần nhập tay
- 🔒 Token lưu trong **GitHub Secrets** (mã hoá) — không ai thấy được
- 📢 Thông báo qua **Discord** hoặc **Telegram** (tuỳ chọn)

---

## 🚀 Hướng dẫn cài đặt

### Bước 1 – Lấy `ACCOUNT_TOKEN` từ trình duyệt

`ACCOUNT_TOKEN` là cookie dài hạn (~vài tháng) — chỉ cần lấy 1 lần!

**Cách 1: Qua URL (dễ nhất)**

1. Đăng nhập vào [skport.com](https://www.skport.com)
2. Mở tab mới, truy cập URL sau:
   ```
   https://web-api.skport.com/cookie_store/account_token
   ```
3. Trang sẽ hiển thị token của anh — **copy toàn bộ chuỗi**

**Cách 2: Qua DevTools**

1. Đăng nhập vào [skport.com](https://www.skport.com)
2. Nhấn **F12** → tab **Application** (Chrome) hoặc **Storage** (Firefox)
3. Chọn **Cookies** → `https://www.skport.com` (hoặc `.skport.com`)
4. Tìm cookie tên **`ACCOUNT_TOKEN`** → copy giá trị

> ⚠️ **Lưu ý:** `ACCOUNT_TOKEN` khác với `SK_OAUTH_CRED_KEY`. Phải lấy đúng `ACCOUNT_TOKEN`.

---

### Bước 2 – Tạo Secrets trong GitHub

Vào **Settings → Secrets and variables → Actions → New repository secret**

#### Mỗi tài khoản = 1 Secret riêng

| Secret Name | Giá trị (JSON) |
|-------------|----------------|
| `ACCOUNT_1` | JSON của tài khoản 1 |
| `ACCOUNT_2` | JSON của tài khoản 2 |
| ... | ... |

**Format JSON cho mỗi Secret:**

```json
{
  "account_token": "GIÁ_TRỊ_ACCOUNT_TOKEN",
  "lang":          "en",
  "name":          "Yuuki"
}
```

| Field | Mô tả | Bắt buộc |
|-------|-------|----------|
| `account_token` | Token lấy từ Bước 1 | ✅ |
| `lang` | Ngôn ngữ: `en` / `ja` / `zh_Hant` / `zh_Hans` / `ko` / `ru_RU` | ❌ (mặc định `en`) |
| `name` | Tên hiển thị tuỳ ý trong log | ❌ (mặc định `Account N`) |

> 💡 **Không cần nhập Game ID hay Server** — script tự động detect!

---

### Bước 3 – Thiết lập thông báo (tuỳ chọn)

#### Discord

1. Vào server Discord → ⚙️ **Edit Channel** → **Integrations** → **Webhooks** → **New Webhook**
2. Copy Webhook URL
3. Tạo Secret `DISCORD_WEBHOOK` với URL vừa copy

#### Telegram

1. Chat với **[@BotFather](https://t.me/botfather)** → `/newbot` → lấy **Bot Token**
2. Chat với **[@userinfobot](https://t.me/userinfobot)** → lấy **Chat ID** của bạn
3. Tạo 2 Secrets:
   - `TELEGRAM_BOT_TOKEN` = Bot Token
   - `TELEGRAM_CHAT_ID` = Chat ID

| Secret Name | Mô tả |
|-------------|-------|
| `DISCORD_WEBHOOK` | URL Discord Webhook |
| `TELEGRAM_BOT_TOKEN` | Token bot Telegram |
| `TELEGRAM_CHAT_ID` | Chat ID cá nhân hoặc group |

---

### Bước 4 – Push lên GitHub

```bash
git add .
git commit -m "feat: add Endfield auto sign-in"
git push
```

▶️ Chạy thủ công: **Actions → 🌙 Endfield Daily Sign-in → Run workflow**

---

## 📅 Lịch chạy

| Múi giờ | Thời gian |
|---------|-----------|
| **GMT+7** (Việt Nam) | **3:00 sáng** hàng ngày |
| UTC | 20:00 hôm trước |

---

## 💬 Ý nghĩa các thông báo

| Thông báo | Ý nghĩa |
|-----------|---------|
| ✅ Điểm danh thành công! | Thành công, kèm phần thưởng |
| ℹ️ Đã điểm danh hôm nay rồi! | Bình thường |
| ⚠️ ACCOUNT_TOKEN hết hạn! | Lấy lại token (Bước 1) |
| ❌ Không lấy được OAuth code | Kiểm tra ACCOUNT_TOKEN |

---

## 🔄 Khi cần renew token

`ACCOUNT_TOKEN` thường sống **vài tháng**. Khi nhận thông báo `⚠️ ACCOUNT_TOKEN hết hạn!`:

1. Vào `https://web-api.skport.com/cookie_store/account_token`
2. Copy token mới
3. Cập nhật Secret `ACCOUNT_N` tương ứng

---

## 🔒 Về bảo mật

- `ACCOUNT_TOKEN` được lưu trong **GitHub Secrets** (AES-256 encrypted)
- **Không ai trong repo** có thể đọc giá trị Secret — kể cả contributors
- Token chỉ được inject vào môi trường khi workflow chạy, không xuất hiện trong logs

---

## 📁 Cấu trúc project

```
.
├── sign_in.py                   # Script điểm danh chính
├── requirements.txt             # curl-cffi
├── .github/
│   └── workflows/
│       └── sign_in.yml          # GitHub Actions (3h sáng GMT+7)
└── README.md
```

---

*Made with 💜 | Inspired by [nano-shino/EndfieldCheckin](https://github.com/nano-shino/EndfieldCheckin) and [Areha11Fz/ArknightsEndfieldAutoCheckIn](https://github.com/Areha11Fz/ArknightsEndfieldAutoCheckIn)*
