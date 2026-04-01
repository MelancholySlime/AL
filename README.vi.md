# 🌙 Arknights: Endfield – Tự Động Điểm Danh Hàng Ngày

Tự động điểm danh hàng ngày trên [game.skport.com/endfield/sign-in](https://game.skport.com/endfield/sign-in) thông qua **GitHub Actions** vào lúc **3:00 sáng (GMT+7)** mỗi ngày.

---

## ✨ Tính năng

- ⚙️ Tự động điểm danh hàng ngày qua **GitHub Actions**
- 👥 Hỗ trợ **nhiều tài khoản** — mỗi Secret = 1 account
- 📢 Thông báo qua **Discord** và **Telegram**

---

## 🚀 Hướng dẫn cài đặt

### Bước 1 – Lấy `ACCOUNT_TOKEN`

`ACCOUNT_TOKEN` là cookie dài hạn (~vài tháng) — chỉ cần lấy một lần!

**Cách 1: Qua URL (dễ nhất)**

1. Đăng nhập vào [skport.com](https://www.skport.com)
2. Mở tab mới, truy cập URL sau:
   ```
   https://web-api.skport.com/cookie_store/account_token
   ```
3. Trang sẽ hiển thị token của bạn — **copy toàn bộ chuỗi**

**Cách 2: Qua DevTools**

1. Đăng nhập vào [skport.com](https://www.skport.com)
2. Nhấn **F12** → tab **Application** (Chrome) hoặc **Storage** (Firefox)
3. Chọn **Cookies** → `https://www.skport.com` (hoặc `.skport.com`)
4. Tìm cookie tên **`ACCOUNT_TOKEN`** → copy giá trị

> ⚠️ **Lưu ý:** `ACCOUNT_TOKEN` khác với `SK_OAUTH_CRED_KEY`. Đảm bảo copy đúng loại.

---

### Bước 2 – Thêm Secrets vào GitHub

Vào **Settings → Secrets and variables → Actions → New repository secret**

#### Mỗi tài khoản = 1 Secret riêng

| Tên Secret | Giá trị |
|------------|---------|
| `ACCOUNT_1` | JSON của tài khoản 1 |
| `ACCOUNT_2` | JSON của tài khoản 2 |
| `ACCOUNT_3` | ... |

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
| `name` | Tên hiển thị trong log | ❌ (mặc định `Account N`) |

> 💡 **Không cần nhập Game ID hay Server** — script tự động detect!

---

### Bước 3 – Thiết lập thông báo (tuỳ chọn)

#### Discord

1. Vào Discord server → ⚙️ **Edit Channel** → **Integrations** → **Webhooks** → **New Webhook**
2. Copy Webhook URL
3. Tạo Secret tên `DISCORD_WEBHOOK` với URL vừa copy

**Ví dụ thông báo nhận được:**
```
📋 Endfield Sign-in Report
────────────────────────────────
[Yuuki] ✅ Điểm danh thành công! (Ngày 12) | Phần thưởng: Module Component x1
[Aurora] ℹ️  Đã điểm danh hôm nay rồi!
```

#### Telegram

1. Chat với **[@BotFather](https://t.me/botfather)** → `/newbot` → lấy **Bot Token**
2. Chat với **[@userinfobot](https://t.me/userinfobot)** → lấy **Chat ID** của bạn
3. Tạo 2 Secrets:

| Tên Secret | Giá trị |
|------------|---------|
| `DISCORD_WEBHOOK` | URL Discord Webhook |
| `TELEGRAM_BOT_TOKEN` | Bot Token từ BotFather |
| `TELEGRAM_CHAT_ID` | Chat ID cá nhân hoặc group |

> **Lưu ý Telegram:** Phải nhắn tin cho bot ít nhất 1 lần trước khi bot có thể nhắn lại. Tìm bot theo username → nhấn **Start**.

---

### Bước 4 – Push lên GitHub

```bash
git add .
git commit -m "feat: add Endfield auto sign-in"
git push
```

▶️ **Chạy thủ công:** Actions → 🌙 Endfield Daily Sign-in → **Run workflow**

---

## 📅 Lịch chạy

| Múi giờ | Thời gian |
|---------|-----------|
| **GMT+7** (Việt Nam) | **3:00 sáng** hàng ngày |
| UTC | 20:00 hôm trước |

---

## 💬 Ý nghĩa thông báo

| Thông báo | Ý nghĩa |
|-----------|---------|
| ✅ Điểm danh thành công! | Thành công, kèm thông tin phần thưởng |
| ℹ️ Đã điểm danh hôm nay rồi! | Bình thường — đã làm rồi |
| ⚠️ ACCOUNT_TOKEN hết hạn! | Cần lấy lại token (Bước 1) |
| ❌ Không lấy được OAuth code | `ACCOUNT_TOKEN` không hợp lệ |

---

## 🔄 Khi cần renew token

`ACCOUNT_TOKEN` thường sống **vài tháng**. Khi nhận `⚠️ ACCOUNT_TOKEN hết hạn!`:

1. Vào `https://web-api.skport.com/cookie_store/account_token`
2. Copy token mới
3. Cập nhật Secret `ACCOUNT_N` tương ứng

---

## 🔒 Bảo mật

- `ACCOUNT_TOKEN` lưu trong **GitHub Secrets** (mã hoá AES-256)
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
│       └── sign_in.yml          # GitHub Actions workflow
└── README.md
```

---

*Made with 💜 | Tham khảo từ [nano-shino/EndfieldCheckin](https://github.com/nano-shino/EndfieldCheckin) và [Areha11Fz/ArknightsEndfieldAutoCheckIn](https://github.com/Areha11Fz/ArknightsEndfieldAutoCheckIn)*
