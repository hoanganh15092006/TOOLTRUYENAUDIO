# 🎙️ TIÊU CHUẨN ĐÁNH GIÁ & KIỂM ĐỊNH AUDIOBOOK DÀI (>20 PHÚT)
*Long-Form Audiobook Director & Sound Engineering Rubric*

---

## 🎯 Mục tiêu cốt lõi
Một tập truyện audio dài hơn 20 phút (thậm chí 45–90 phút) đòi hỏi sự tinh tế vượt trội về nhịp độ và kỹ thuật âm thanh. Người nghe thường đeo tai nghe trong thời gian dài, vì vậy âm thanh phải:
1. **Không gây mỏi tai (Ear Fatigue)** do âm lượng trồi sụt bất thường hoặc tần số quá gắt.
2. **Cuốn hút và có nhịp thở (Pacing & Breath)** thay vì một chuỗi âm thanh máy móc dồn dập.
3. **Phối âm chuẩn phòng thu (Professional Mastering)**: Giọng đọc tách bạch, nhạc nền (BGM) êm dịu, tự động lùi bước khi nhân vật cất giọng.

---

## 📋 4 Tiêu Chuẩn Kiểm Định Bắt Buộc

### 1. Phân Nhịp & Quản Lý Phân Đoạn (Chunking & Pacing for Long-form)
- **Kích thước phân đoạn:** Không bao giờ nạp toàn bộ kịch bản 5.000–10.000 từ vào TTS một lượt. Chia văn bản thành các block tương đương **3–5 phút đọc** (~450–750 từ/chunk).
- **Khoảng lặng tự nhiên (Pacing & Pauses):**
  - Giữa các câu văn thường: `0.3s – 0.5s`.
  - Giữa các đoạn văn/hội thoại đổi lượt: `0.6s – 0.9s`.
  - Giữa các phân cảnh/chương (Scene Transition): `1.2s – 1.8s` (kết hợp tiếng gảy đàn hoặc SFX chuyển cảnh nhẹ).
- **Độ mượt nối file (Seamless Concatenation):** Điểm nối giữa các chunk phải khớp pha, không bị đứt gãy hoặc để lại khoảng trống tĩnh câm quá 2.5s.

### 2. Kỹ Thuật Âm Thanh Chuyên Nghiệp (Audio Mastering & EBU R128)
- **Chuẩn âm lượng tích hợp (Integrated Loudness):**
  - **Mục tiêu:** `-16.0 LUFS` (dung sai `±1.0 LUFS`), đạt chuẩn quốc tế cho Podcasts & Audiobooks (Spotify, Apple Podcasts, Audible, YouTube).
- **Đỉnh thực (True Peak - TP):**
  - Giới hạn tối đa: `<= -1.5 dBTP` để ngăn chặn hiện tượng méo tiếng (inter-sample clipping) khi nén MP3/AAC.
- **Dải động âm lượng (Loudness Range - LRA):**
  - Giới hạn: `<= 11.0 LU`. Giữ âm lượng ổn định từ đầu đến cuối, người nghe không phải chỉnh volume điện thoại liên tục.
- **Dynamic Audio Ducking:**
  - Khi giọng đọc cất lên: Nhạc nền BGM tự động giảm xuống `-22 dB` đến `-26 dB`.
  - Khi giọng đọc tạm dừng (>1.5s): Nhạc nền tự động trồi nhẹ lên `-16 dB` với thời gian release mượt mà (`dropout_transition=1.5s`).
- **Khử nhiễu & Cắt cụt (De-clicking & Zero Artifacts):**
  - Đầu và cuối mỗi file có fade-in/fade-out siêu ngắn (`10ms – 50ms`) để triệt tiêu tiếng "pop/click".

### 3. Hook 60 Giây Đầu & Giữ Chân Người Nghe (Hook & Retention)
- **60 giây đầu tiên:** Phải có mở màn ấn tượng (Intro SFX, tiếng chuông gió/tiếng mưa/tiếng bước chân nhẹ hoặc một câu tóm tắt cao trào kịch tính).
- Tuyệt đối không để mở đầu là 5 giây im lặng hoàn toàn.

### 4. Độ Ổn Định Kỹ Thuật Khi Chạy Dài (Long-run Stability)
- **Xử lý tài nguyên RAM:** Quá trình render video/audio dài >30 phút phải streaming qua disk/temp buffer, không tích lũy buffer trong RAM.
- **Unicode & Ký tự đặc biệt tiếng Việt:** Xử lý triệt để mã hóa UTF-8, loại bỏ các ký tự điều khiển ẩn hoặc emoji có thể làm crash subprocess của FFmpeg.

---

## 📊 Thang Điểm Đánh Giá Tự Động (Scoring Rubric 0–100)

| Hạng mục | Trọng số | Tiêu chí đạt điểm tối đa (Pass) |
| :--- | :---: | :--- |
| **Phân nhịp Chunking & Pauses** | 25% | Đủ các chunk 3-5 phút, có khoảng ngắt cảnh, không nuốt chữ |
| **Mastering (-16 LUFS, TP <= -1.5)** | 35% | Âm lượng tích hợp đạt -16 LUFS (±1.0), True Peak không vỡ |
| **BGM Ducking & Cân bằng** | 20% | BGM không lấn át voiceover, ducking mượt mà |
| **Hook 60s & Intro SFX** | 10% | Mở màn có hiệu ứng hoặc câu dẫn kịch tính trong 60s đầu |
| **Độ mượt & Không Artifact** | 10% | Không có tiếng click, không lỗi giật khung hình |

> **Ngưỡng ĐẠT CHUẨN XUẤT XƯỞNG (Exit Threshold):** Tổng điểm `>= 85/100` và không vi phạm bất kỳ lỗi chí mạng nào (Critical Errors: vỡ tiếng clipping, mất tiếng >3s, lệch sync âm thanh).
