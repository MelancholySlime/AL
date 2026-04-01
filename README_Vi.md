# 🌙 Arknights: Endfield – Tự động điểm danh

Tự động điểm danh hàng ngày trên [Arknights: Endfield](https://game.skport.com/endfield/sign-in) qua **GitHub Actions** — chạy lúc **3:00 sáng (GMT+7)** mỗi ngày.

---

## ✨ Tính năng

- ✅ Tự động điểm danh hàng ngày qua GitHub Actions
- 👥 Hỗ trợ nhiều tài khoản — mỗi Secret = 1 account
- 📢 Thông báo qua Discord (tuỳ chọn)

---

## 🚀 Cài đặt

### Bước 1 — Lấy `ACCOUNT_TOKEN`

1. Đăng nhập vào [skport.com](https://www.skport.com)
2. Mở tab mới, truy cập:
   ```
   https://web-api.skport.com/cookie_store/account_token
   ```
3. **Copy toàn bộ chuỗi** hiển thị trên trang

> Cách khác: **F12 → Application → Cookies → `.skport.com` → `ACCOUNT_TOKEN`**

---

### Bước 2 — Tạo Secrets trong GitHub

Vào **Settings → Secrets and variables → Actions → New repository secret**

#### Tài khoản (mỗi Secret = 1 account)

| Secret | Giá trị |
|--------|---------|
| `ACCOUNT_1` | JSON tài khoản 1 |
| `ACCOUNT_2` | JSON tài khoản 2 |

**Format JSON:**
```json
{
  "account_token": "TOKEN_VỪA_COPY",
  "lang": "en",
  "name": "Tên hiển thị"
}
```

| Field | Mô tả | Bắt buộc |
|-------|-------|----------|
| `account_token` | Token từ Bước 1 | ✅ |
| `lang` | Ngôn ngữ: `en` / `ja` / `ko` / `zh_Hans` / `zh_Hant` / `ru_RU` | ❌ mặc định `en` |
| `name` | Tên hiển thị trong log | ❌ |

> Game ID và Server được **tự động detect** — không cần nhập tay.

#### Discord (tuỳ chọn)

| Secret | Giá trị |
|--------|---------|
| `DISCORD_WEBHOOK` | URL Discord Webhook |

**Tạo webhook:** Discord → ⚙️ Edit Channel → Integrations → Webhooks → New Webhook → Copy URL

---

### Bước 3 — Push & Chạy

```bash
git add .
git commit -m "feat: Endfield auto sign-in"
git push
```

Chạy thủ công: **Actions → 🌙 Endfield Daily Sign-in → Run workflow**

---

## 🔄 Khi Token hết hạn

`ACCOUNT_TOKEN` thường sống **vài tháng**. Khi thấy `⚠️ ACCOUNT_TOKEN hết hạn!`:

1. Vào `https://web-api.skport.com/cookie_store/account_token`
2. Copy token mới → cập nhật Secret `ACCOUNT_N`

---

## 📅 Lịch chạy

| Múi giờ | Thời gian |
|---------|-----------|
| GMT+7 (Việt Nam) | **3:00 sáng** hàng ngày |
| UTC | 20:00 hôm trước |

---

*Made with 💜 · [README (English)](README.md)*
