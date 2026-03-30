# 🌙 Arknights: Endfield – Auto Daily Sign-in

Script tự động điểm danh hàng ngày trên [game.skport.com/endfield/sign-in](https://game.skport.com/endfield/sign-in), chạy bằng **GitHub Actions** lúc **3:00 sáng (GMT+7)** mỗi ngày.

---

## ✨ Tính năng

- ✅ Tự động điểm danh mỗi ngày lúc 3h sáng
- 👥 Hỗ trợ **nhiều tài khoản** cùng lúc
- 🔑 Chỉ cần **1 GitHub Secret duy nhất** – dễ quản lý
- 📢 Thông báo kết quả qua **Discord** hoặc **Telegram** (tuỳ chọn)
- ▶️  Có thể chạy thủ công từ tab **Actions**

---

## 🚀 Hướng dẫn cài đặt

### Bước 1 – Lấy Token từ trình duyệt

1. Đăng nhập vào [game.skport.com/endfield/sign-in](https://game.skport.com/endfield/sign-in)
2. Nhấn **F12** → chọn tab **Console**
3. Dán đoạn code sau và nhấn **Enter**:

```javascript
function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
}

console.log('=== Copy các giá trị này ===');
console.log('cred  :', getCookie('SK_OAUTH_CRED_KEY') || 'NOT FOUND');
console.log('token :', localStorage.getItem('SK_TOKEN_CACHE_KEY') || 'NOT FOUND');
```

4. **Copy** 2 giá trị `cred` và `token` ra notepad.

> **Lấy Game ID:** F12 → tab **Network** → nhấn nút Sign-in trên trang → tìm request tới `zonai.skport.com` → xem header `sk-game-role`, format là `3_<ID>_<SERVER>` → lấy phần `<ID>`.

---

### Bước 2 – Tạo nội dung JSON cho Secret

Sao chép template JSON bên dưới, điền thông tin của bạn vào:

#### 1 tài khoản

```json
{
  "accounts": [
    {
      "cred":    "GIÁ_TRỊ_CRED_CỦA_BẠN",
      "token":   "GIÁ_TRỊ_TOKEN_CỦA_BẠN",
      "game_id": "123456789",
      "server":  "2",
      "lang":    "en",
      "name":    "Tên của bạn"
    }
  ],
  "discord_webhook":    "",
  "telegram_bot_token": "",
  "telegram_chat_id":   ""
}
```

#### Nhiều tài khoản

```json
{
  "accounts": [
    {
      "cred":    "CRED_ACC_1",
      "token":   "TOKEN_ACC_1",
      "game_id": "111111111",
      "server":  "2",
      "lang":    "en",
      "name":    "Tài khoản 1"
    },
    {
      "cred":    "CRED_ACC_2",
      "token":   "TOKEN_ACC_2",
      "game_id": "222222222",
      "server":  "3",
      "lang":    "en",
      "name":    "Tài khoản 2"
    }
  ],
  "discord_webhook":    "https://discord.com/api/webhooks/...",
  "telegram_bot_token": "",
  "telegram_chat_id":   ""
}
```

**Giải thích các trường:**

| Trường | Mô tả |
|--------|-------|
| `cred` | Giá trị `SK_OAUTH_CRED_KEY` lấy từ cookie |
| `token` | Giá trị `SK_TOKEN_CACHE_KEY` lấy từ localStorage |
| `game_id` | ID game Endfield của bạn (chỉ số) |
| `server` | `"2"` = Asia &nbsp;/&nbsp; `"3"` = Americas/Europe |
| `lang` | `en` / `ja` / `zh_Hant` / `zh_Hans` / `ko` / `ru_RU` |
| `name` | Tên hiển thị tuỳ ý |
| `discord_webhook` | *(tuỳ chọn)* Để rỗng `""` nếu không dùng |
| `telegram_bot_token` | *(tuỳ chọn)* Để rỗng `""` nếu không dùng |
| `telegram_chat_id` | *(tuỳ chọn)* Để rỗng `""` nếu không dùng |

---

### Bước 3 – Thêm Secret vào GitHub

1. Vào repo GitHub → **Settings** → **Secrets and variables** → **Actions**
2. Nhấn **New repository secret**
3. **Name**: `ENDFIELD_CONFIG`
4. **Secret**: Dán toàn bộ nội dung JSON từ Bước 2 vào đây
5. Nhấn **Add secret**

> Chỉ cần **1 secret duy nhất** là xong! ✨

---

### Bước 4 – Push lên GitHub

```bash
git init
git add .
git commit -m "feat: add Endfield auto sign-in"
git remote add origin https://github.com/<username>/<repo>.git
git push -u origin main
```

Workflow sẽ **tự động chạy mỗi ngày lúc 3h sáng (GMT+7)**.  
Chạy thủ công: **Actions** → **🌙 Endfield Daily Sign-in** → **Run workflow**.

---

## 📅 Lịch chạy

| Múi giờ | Thời gian |
|---------|-----------|
| GMT+7 (Việt Nam) | **3:00 sáng** hàng ngày |
| UTC | 20:00 (hôm trước) hàng ngày |

---

## 🔄 Khi Token hết hạn

Nếu nhận được thông báo `⚠️ Token hết hạn`:
1. Đăng nhập lại vào trang sign-in
2. Lấy lại `cred` và `token` theo **Bước 1**
3. Cập nhật Secret `ENDFIELD_CONFIG` với giá trị mới

---

## 📁 Cấu trúc project

```
.
├── sign_in.py                   # Script điểm danh chính
├── requirements.txt             # Python dependencies
├── .github/
│   └── workflows/
│       └── sign_in.yml          # GitHub Actions (3h sáng GMT+7)
└── README.md
```

---

## ⚠️ Lưu ý

- Token có thể **hết hạn** sau vài tuần – cần cập nhật thủ công.
- Sử dụng script này **tự chịu rủi ro** – có thể vi phạm ToS của game.
- **Không** chia sẻ nội dung Secret với bất kỳ ai.

---

*Made with 💜 | Inspired by [canaria3406/skport-auto-sign](https://github.com/canaria3406/skport-auto-sign)*
