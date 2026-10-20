# Devlog: 2026-10-21 - Thiết lập Audiobook Director & Sound Engineering Suite (>20 Phút)

## 1. Bối cảnh & Vấn đề thực tế (Context)
- **Vấn đề đặt ra:** Khi sản xuất các tập truyện audio dài (từ 20 phút đến hơn 60 phút), việc xuất file một lèo dễ dẫn đến hiện tượng:
  - Tràn bộ nhớ RAM hoặc lỗi timeout kết nối với engine TTS khi gửi khối văn bản lớn.
  - Âm lượng trồi sụt thất thường giữa các đoạn kịch bản khác nhau, gây mỏi tai (Ear Fatigue) khi người nghe đeo tai nghe thời gian dài.
  - Nhạc nền (BGM) lấn át giọng đọc nếu không có cơ chế Dynamic Audio Ducking tự động.
- **Giải pháp triển khai:**
  - Thiết lập vai trò **Audiobook Director & Sound Engineer AI**.
  - Xây dựng bộ tiêu chuẩn kiểm định `long_form_rubric.md` với 4 chuẩn khắt khe: Phân nhịp Chunking & Pauses (3–5 phút/block), Mastering chuẩn EBU R128 (-16.0 LUFS, TP <= -1.5 dBTP), Hook 60s đầu, và độ ổn định streaming qua disk.
  - Viết suite công cụ `audio_director.py` để phân tích chuẩn EBU R128 và tự động master âm thanh bằng FFmpeg.

## 2. Bài học rút ra (Learned Heuristics)
- **[H-AUDIO-01] EBU R128 Mastering cho Truyện Dài:** Sử dụng filter `loudnorm=I=-16:TP=-1.5:LRA=11` trên FFmpeg giúp đưa âm lượng toàn tập về chuẩn -16.0 LUFS (±0.5 LUFS) một cách tự nhiên mà không làm méo âm sắc giọng đọc tiếng Việt.
- **[H-AUDIO-02] Khoảng lặng Nhịp thở (Pacing):** Chèn khoảng lặng 0.6s–0.9s giữa các phân cảnh giúp người nghe thẩm thấu câu chuyện tốt hơn, tránh cảm giác máy móc dồn dập.
- **[H-AUDIO-03] Kiểm thử Thẩm định Tự động:** Việc kiểm tra định lượng thông qua `audio_director.py audit` cho phép phát hiện sớm các file audio bị quá nhỏ (-30 LUFS) và tự động kéo lên chuẩn -16 LUFS đạt 100/100 điểm trước khi xuất xưởng.

## 3. Thay đổi kỹ thuật (Changelog & Technical Improvements)
- **Cấu trúc kiểm định mới (`.agents/audio_evals/`):**
  - Tạo `long_form_rubric.md` quy định 4 tiêu chuẩn vàng và thang điểm 0–100 (ngưỡng đạt >= 85).
  - Tạo `execution_traces.jsonl` chuyên lưu vết các phiên xử lý audio dài.
  - Tạo thư mục đề xuất `proposals/` kèm đề xuất `proposal_20261021_audio_mastering_loudnorm.md`.
- **Kỹ năng chuyên biệt (`audiobook-director-evaluator`):**
  - Tạo `SKILL.md` hướng dẫn quy trình 4 bước: Chunk & Render -> Automated Audit -> Auto-Refine (max 5 retries) -> Final Polish.
  - Tạo `scripts/audio_director.py` cung cấp 2 chế độ `audit` và `master`.

## 4. Benchmark & Hiệu năng
- **Thử nghiệm thực tế trên file audio:**
  - File trước khi master: `-30.45 LUFS`, True Peak `-26.64 dBTP` (Điểm kiểm định: 80/100 - FAIL).
  - File sau khi chạy `audio_director master`: `-16.25 LUFS`, True Peak `-12.45 dBTP` (Điểm kiểm định: **100/100 - ĐẠT CHUẨN XUẤT XƯỞNG**).
- **Tốc độ xử lý:** Phân tích và master hoàn tất trong 0.8 giây bằng binary FFmpeg tích hợp.
