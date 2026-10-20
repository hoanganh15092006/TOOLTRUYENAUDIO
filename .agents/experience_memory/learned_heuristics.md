# SỔ TAY KINH NGHIỆM VÀ QUY TẮC RÚT RA (LEARNED HEURISTICS)
*Hệ thống tri thức tự tích lũy qua các lần chạy thực tế của TOOLTRUYENAUDIO*

---

## 📌 Tổng quan vòng đời học tập (Self-Learning Status)
- **Chu kỳ hiện tại:** Chu kỳ 0 (Khởi tạo hệ thống)
- **Số lượng traces đã ghi:** 1
- **Trạng thái:** Sẵn sàng ghi nhận kinh nghiệm thực chiến

---

## 🧠 Danh mục Heuristics theo Module

### 1. Module Kịch bản (`src/script_gen`)
- **[H-SG-01] Quản lý Token & Đoạn dài:** Với kịch bản >30 phút (~5.000 - 7.000 từ), không nên prompt AI tạo một lần. Cần chia theo hồi (Hồi 1 - Giới thiệu/Biến cố, Hồi 2 - Xung đột cao trào, Hồi 3 - Giải quyết/Cái kết) để giữ giọng văn mạch lạc và không bị đứt đoạn giữa chừng.
- **[H-SG-02] Định dạng văn bản cho TTS:** Cần loại bỏ toàn bộ emoji, ký tự đặc biệt lạ (`*`, `~`, `_`), các chỉ dẫn hành động trong ngoặc `(thở dài)`, `[nhếch mép]` trước khi đẩy vào engine đọc âm thanh để tránh lỗi đọc vấp hoặc phát âm ký tự vô nghĩa.

### 2. Module Đọc giọng nói & Phối âm (`src/tts_engine`)
- **[H-TTS-01] Xử lý giới hạn ký tự Edge-TTS:** Mỗi khối văn bản gửi vào Edge-TTS tối ưu nhất nên nằm trong khoảng 300 - 600 từ. Cắt câu theo dấu chấm `.` hoặc xuống dòng `\n` để ngắt nghỉ tự nhiên.
- **[H-TTS-02] Retry Exponential Backoff:** Khi mạng chập chờn hoặc Microsoft Edge-TTS bị rate-limit, cần retry 3 lần với delay tăng dần (1s, 3s, 7s) trước khi báo lỗi.
- **[H-MIX-01] Chuẩn hóa âm lượng (Loudness Normalization):** Giọng đọc (Voiceover) nên ở mức `-14 LUFS` đến `-16 LUFS`. Nhạc nền (BGM) phải luôn hạ âm lượng xuống `-22 dB` đến `-26 dB` so với giọng đọc và áp dụng `ducking` nhẹ khi có tiếng nói.

### 3. Module Video Renderer (`src/video_renderer`)
- **[H-VID-01] FFmpeg Video Dài (>30 phút YouTube):** Dùng static image + audio dài cần sử dụng preset `-tune stillimage -c:v libx264 -preset veryfast -pix_fmt yuv420p` để render cực nhanh và không ngốn RAM.
- **[H-VID-02] TikTok 4 phút (Sub + Video dọc 9:16):** Video nền gameplay hoặc satisfying cần loop mượt mà, scale crop `crop=ih*(9/16):ih` và render phụ đề dạng Karaoke/Word-by-word với font việt hóa rõ ràng (Arial/Montserrat Bold, viền đen dày để nổi trên nền chuyển động).

### 4. Xử lý File & Hệ thống trên Windows
- **[H-SYS-01] Đường dẫn Windows (Path Delimiter & Unicode):** Luôn dùng `pathlib.Path` hoặc `os.path.join` chuẩn hóa utf-8. Tránh hardcode dấu `\` hoặc tên file tiếng Việt có dấu trong command line gọi subprocess của FFmpeg.
- **[H-SYS-02] Dọn dẹp Temp Files:** Các file audio chunks hoặc thumbnail tạm phải được gom trong thư mục `output/temp/` và tự động dọn dẹp sau khi render xong để tránh phình dung lượng ổ cứng.

---

## 📈 Lịch sử các Chu kỳ Tự nâng cấp (Upgrade Cycles)
| Chu kỳ | Ngày | Module tác động | Mô tả tóm tắt | Trạng thái |
| :--- | :--- | :--- | :--- | :--- |
| `Cycle 0` | 2026-10-21 | Toàn hệ thống | Khởi tạo cấu trúc Self-Learning, Benchmark và Traces | ✅ Hoàn thành |
