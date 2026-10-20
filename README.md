# TOOLTRUYENAUDIO - Hệ Thống Tự Động Hóa Sản Xuất & Đăng Tải Truyện Audio Oneshot 🎧🚀

Hệ thống tự động hóa toàn diện từ A-Z quy trình sáng tác, chuyển thể giọng đọc AI tiếng Việt, dựng video và tự động xuất bản truyện audio Oneshot (truyện ngắn trọn bộ 1 tập duy nhất >30 phút) đa nền tảng (**YouTube Full** + **TikTok Teaser 4 phút**).

---

## ⚡ 1-Click Chạy Ngay (Dành Cho Người Mới Bắt Đầu)

Tool đã tích hợp sẵn script tự động tạo môi trường, cài thư viện và tải trình duyệt Chromium:

1. **Nhấp đúp chuột vào file [`run.bat`](run.bat)** (hoặc mở PowerShell gõ `.\run.ps1`).
2. Script sẽ tự động:
   - 🔍 Kiểm tra Python 3.10+ trên máy tính.
   - 📦 Tự tạo môi trường ảo `.venv` độc lập.
   - 📥 Tự động cài đặt toàn bộ thư viện cần thiết trong `requirements.txt`.
   - 🌐 **Tự động tải & cài đặt Chromium Browser (`playwright install chromium`)** phục vụ tự động đăng TikTok.
   - ⚙️ Tự động tạo file cấu hình `.env` từ `.env.example`.
   - 🚀 Mở Menu tương tác dòng lệnh tiếng Việt trực quan.

---

## 🌟 Các Tính Năng Nổi Bật

### 1. Kịch Bản Oneshot Liền Mạch & Cú Twist Ở Phút Thứ 4 (Cliffhanger)
- **Chuẩn Oneshot trọn bộ:** Trọn vẹn trong một video duy nhất, giải quyết triệt để nút thắt, **tuyệt đối không chia Phần 1, Phần 2, không ngắt chương**.
- **Thuật toán tính độ dài:** Chuẩn tốc độ đọc tiếng Việt ~150 từ/phút:
  * 30 phút -> ~4.500 từ
  * 35 phút -> ~5.250 từ (Mặc định)
  * 60 phút -> ~9.000 từ
- **Kỹ thuật Seamless Multi-Part Generation:** Vượt qua giới hạn Output Token của LLM bằng cách chia truyện thành nhiều giai đoạn nối tiếp mượt mà, truyền ngữ cảnh đuôi vào phần kế tiếp.
- **Điểm móc câu (Hook/Cliffhanger) ở phút 3:45 - 4:00 (Từ thứ 550 - 600):** Đẩy lên cao trào kịch tính, bí mật kinh hoàng hoặc cú bẻ lái cực gắt để khi cắt 4 phút đầu đăng lên TikTok, người xem bị cuốn hút và buộc phải tìm sang kênh YouTube nghe trọn bộ.

### 2. Lựa Chọn 3 Kiểu Cái Kết (Ending Types)
- **[1] Có hậu (Happy Ending - HE):** Kẻ ác đền tội, nhân vật chính vượt qua giông bão, tìm lại tự do, hạnh phúc hoặc tình yêu xứng đáng.
- **[2] Không có hậu / Bi kịch (Sad Ending - SE):** Chia ly, mất mát, sự thật muộn màng, để lại nỗi day dứt, xót xa khôn nguôi cho người nghe.
- **[3] Hờ hững / Kết mở (Open Ending - OE):** Buông bỏ nhẹ nhàng, rời đi thanh thản, kết thúc lạnh nhạt hoặc một câu hỏi mở đầy suy ngẫm.

### 3. Giọng Đọc AI Tiếng Việt & Trộn Nhạc Nền (Audio Ducking)
- **Edge-TTS Neural Voice:** Giọng đọc diễn cảm chất lượng cao (`vi-VN-HoaiMyNeural`, `vi-VN-NamMinhNeural`).
- **Phân mảnh chống lỗi (Chunking):** Tự động chia nhỏ văn bản dài thành các đoạn an toàn tránh timeout, ghép nối âm thanh liền mạch.
- **Audio Ducking:** Tự động loop nhạc nền (BGM) nhẹ nhàng ở mức âm lượng thấp (-24dB) dưới giọng đọc, tạo chiều sâu cho truyện audio.

### 4. Render Video YouTube Full (16:9 - 1920x1080)
- **Tùy chọn ảnh nền:**
  * **Thủ công:** Tự chọn ảnh có sẵn trên máy (tự động căn chỉnh về 16:9).
  * **Tự động bằng AI (Pollinations.ai):** Tự động phân tích tâm trạng, bối cảnh truyện để sinh ảnh nền nghệ thuật cinematic 8K hoàn toàn miễn phí.
- **Tốc độ render siêu tốc:** Sử dụng thuật toán FFmpeg Still-Image Loop, xuất file `output/youtube_full.mp4` trong vài giây mà không tốn tài nguyên RAM.

### 5. Render Video TikTok Teaser (9:16 - 1080x1920 - 4 Phút Đầu)
- **Video nền chuyển động giữ mắt người xem:** Tự động săn và tải video không bản quyền:
  * **Gameplay:** Subway Surfers, Minecraft Parkour, GTA V stunt.
  * **Satisfying:** Cắt xà phòng ASMR, ép thủy lực, nặn đất sét, làm bánh.
- **Xóa sạch âm thanh gốc (-an)** và crop chuẩn khung dọc 9:16.
- **Cắt chuẩn 240 giây** kèm hiệu ứng mờ dần âm thanh (fade-out 3s cuối).
- **Chèn Banner chữ cố định nổi bật:**
  * Dòng 1: `Nghe Full tại YouTube: [Tên Kênh YouTube]`
  * Dòng 2: `Truyện: [Tên Truyện]`

### 6. Tự Động Xuất Bản Đa Nền Tảng (Auto-Upload)
- **YouTube:** Tự động điền Title chuẩn SEO `[FULL] [Tên Truyện] | Truyện Audio Oneshot Trọn Bộ`, mô tả, thẻ tags và thumbnail.
- **TikTok:** Tự động đăng video 4 phút kèm caption dẫn link sang kênh YouTube và bộ hashtag thịnh hành (#truyenaudio #truyenoneshot #kechuyen #truyendemkhuya).

---

## 📁 Cấu Trúc Thư Mục Repository

```text
TOOLTRUYENAUDIO/
├── config/                  # File cấu hình config.yaml, .env, OAuth tokens
├── src/
│   ├── utils/               # FFmpeg wrapper & hệ thống Logger
│   ├── script_gen/          # Sáng tác kịch bản Oneshot, tính từ & cliffhanger
│   ├── tts_engine/          # Chuyển đổi văn bản thành giọng đọc + Audio Mixer
│   ├── media_fetcher/       # Sinh ảnh nền YouTube & tải video nền TikTok
│   ├── video_renderer/      # FFmpeg Render YouTube (16:9) & TikTok (9:16)
│   └── uploaders/           # Module tự động đăng YouTube & TikTok
├── assets/
│   ├── bg_images/           # Kho ảnh nền YouTube
│   ├── bg_videos/           # Kho video nền Gameplay / Satisfying
│   ├── bgm/                 # Nhạc nền truyện audio
│   └── fonts/               # Font chữ Unicode tiếng Việt
├── output/                  # master_audio.mp3, youtube_full.mp4, tiktok_teaser.mp4
├── tests/                   # Bộ kiểm thử toàn diện
├── main.py                  # Menu tương tác dòng lệnh & điều phối pipeline
├── requirements.txt         # Danh sách thư viện Python
├── run.bat                  # Script chạy 1-Click cho Windows
└── run.ps1                  # Script PowerShell
```

---

## 🎮 Hướng Dẫn Sử Dụng Chi Tiết

### 1. Menu Tương Tác Dòng Lệnh
Chỉ cần chạy:
```bash
python main.py
```
Giao diện sẽ lần lượt hỏi các thông tin cần thiết:
1. **Tên kênh YouTube:** Dùng để chèn lên video TikTok và phần mô tả.
2. **Chủ đề truyện:** Nhập tự do (VD: *Trọng sinh báo thù*, *Tổng tài*, *Kinh dị đêm muộn*, *Tình cảm gia đình*...).
3. **Tên truyện:** Nhập tên bạn muốn hoặc bấm Enter để AI tự đặt tên viral.
4. **Thời lượng mục tiêu:** 30, 35, 45 hoặc 60 phút.
5. **Kiểu cái kết:** [1] Có hậu (HE), [2] Bi kịch (SE), [3] Kết mở / Hờ hững (OE).
6. **Ảnh nền YouTube:** [1] Tự chọn ảnh máy tính, [2] AI tự sinh ảnh nền.
7. **Video nền TikTok:** [1] Gameplay, [2] Oddly Satisfying.
8. **Chế độ chạy:** [1] Chạy full & đăng bài, [2] Chỉ dựng video, [3] Chỉ tạo file Audio master.

### 2. Chạy Bằng Lệnh Dòng Lệnh Không Cần Nhập Menu (CLI Flags)
* **Sản xuất trọn bộ truyện 45 phút, kết bi kịch và đăng bài tự động:**
  ```bash
  python main.py --auto --topic "Ngoại tình và quả báo" --duration 45 --ending sad
  ```

* **Chỉ sản xuất video không đăng bài:**
  ```bash
  python main.py --auto --topic "Kinh dị làng quê cổ xưa" --skip-upload
  ```

* **Chỉ tạo kịch bản và audio MP3 master:**
  ```bash
  python main.py --auto --topic "Trọng sinh thành tiểu thư tài phiệt" --only-audio
  ```

---

## ⚙️ Cấu Hình API (.env)

Tạo file `.env` ở thư mục gốc:
```env
# Google Gemini API Key để sáng tác kịch bản truyện
GEMINI_API_KEY=your_gemini_api_key_here

# YouTube Data API v3 (Tùy chọn nếu muốn đăng tự động qua API)
YOUTUBE_API_KEY=your_youtube_api_key_here
```
*(Nếu chưa có GEMINI_API_KEY, hệ thống sẽ tự động kích hoạt bộ giả lập Storyteller mô phỏng sẵn để trải nghiệm toàn bộ quy trình mà không bị gián đoạn).*

---

## 🧪 Kiểm Thử Hệ Thống (Automated Testing)

Chạy toàn bộ 19 bài kiểm thử unit tests & integration tests:
```bash
python -m unittest discover -s tests -v
```
Toàn bộ quy trình từ tính số từ, cắt audio, sinh video 9:16, FFmpeg text overlay đều đạt chuẩn 100% PASS.
