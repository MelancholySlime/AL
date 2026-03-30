# 🌙 Arknights: Endfield – Auto Daily Sign-in

Script tự động điểm danh hàng ngày trên [game.skport.com/endfield/sign-in](https://game.skport.com/endfield/sign-in), chạy bằng **GitHub Actions** lúc **3:00 sáng (GMT+7)** mỗi ngày.

---

## ✨ Tính năng

- ✅ Tự động điểm danh mỗi ngày lúc 3h sáng GMT+7
- 👥 Hỗ trợ **nhiều tài khoản** — mỗi Secret = 1 account
- 🔒 Token lưu trong **GitHub Secrets** — an toàn tuyệt đối
- 📢 Thông báo qua **Discord** hoặc **Telegram** (tuỳ chọn)
- ▶️  Có thể chạy thủ công từ tab **Actions** bất kỳ lúc nào

---

## 🚀 Hướng dẫn cài đặt

### Bước 1 – Lấy Cred & Token từ trình duyệt

1. Đăng nhập vào [game.skport.com/endfield/sign-in](https://game.skport.com/endfield/sign-in)
2. Nhấn **F12** → tab **Console** → dán code sau và nhấn **Enter**:

```javascript
function getCookie(name) {
  const v = `; ${document.cookie}`;
  const p = v.split(`; ${name}=`);
  if (p.length === 2) return p.pop().split(';').shift();
}
console.log('cred  :', getCookie('SK_OAUTH_CRED_KEY'));
console.log('token :', localStorage.getItem('SK_TOKEN_CACHE_KEY'));
```

3. **Copy** 2 giá trị `cred` và `token` ra notepad.

> **Lấy Game ID:** F12 → **Network** → nhấn nút Sign-in → tìm request tới `zonai.skport.com` → xem header `sk-game-role`, format `3_<ID>_<SERVER>` → lấy phần `<ID>`.

---

### Bước 2 – Tạo Secrets trong GitHub

Vào **Settings → Secrets and variables → Actions → New repository secret**

#### Mỗi tài khoản = 1 Secret riêng

| Secret Name | Giá trị (JSON) |
|-------------|----------------|
| `ACCOUNT_1` | JSON của tài khoản 1 |
| `ACCOUNT_2` | JSON của tài khoản 2 |
| `ACCOUNT_3` | ... |

**Format JSON cho mỗi Secret:**

```json
{
  "cred":    "GIÁ_TRỊ_CRED",
  "token":   "GIÁ_TRỊ_TOKEN",
  "game_id": "123456789",
  "server":  "2",
  "lang":    "en",
  "name":    "Tên hiển thị"
}
```

| Field | Mô tả |
|-------|-------|
| `cred` | `SK_OAUTH_CRED_KEY` từ cookie (Bước 1) |
| `token` | `SK_TOKEN_CACHE_KEY` từ localStorage (Bước 1) |
| `game_id` | ID game Endfield (chỉ số) |
| `server` | `"2"` = Asia &nbsp;/&nbsp; `"3"` = Americas/Europe |
| `lang` | `en` / `ja` / `zh_Hant` / `zh_Hans` / `ko` / `ru_RU` |
| `name` | Tên hiển thị tuỳ ý |

#### Thông báo (tuỳ chọn, dùng chung cho tất cả accounts)

| Secret Name | Giá trị |
|-------------|---------|
| `DISCORD_WEBHOOK` | URL Discord Webhook |
| `TELEGRAM_BOT_TOKEN` | Token bot Telegram |
| `TELEGRAM_CHAT_ID` | Chat ID Telegram |

> Để trống nếu không dùng — script tự bỏ qua.

---

### Bước 3 – Push lên GitHub

```bash
git add .
git commit -m "feat: add Endfield auto sign-in"
git push
```

Sau khi push, Actions sẽ **tự chạy lúc 3h sáng GMT+7 mỗi ngày**.  
Chạy thủ công: **Actions → 🌙 Endfield Daily Sign-in → Run workflow**

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
| ✅ Điểm danh thành công! | Điểm danh thành công |
| ℹ️ Đã điểm danh hôm nay rồi! | Bình thường — đã làm rồi |
| ⚠️ Cred/Token hết hạn! | Cần lấy lại token (Bước 1) |
| ❌ Lỗi kết nối | Vấn đề mạng — tự retry sau |

---

## 🔄 Khi Token hết hạn

Token thường hết hạn sau vài tuần. Khi nhận `⚠️ Cred/Token hết hạn!`:

1. Đăng nhập lại vào trang sign-in
2. Lấy lại `cred` và `token` theo **Bước 1**
3. Cập nhật Secret `ACCOUNT_N` tương ứng

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

*Made with 💜 | Inspired by [canaria3406/skport-auto-sign](https://github.com/canaria3406/skport-auto-sign)*
