# Audio Evals Proposals (Khu vực Đề xuất Cải tiến Kỹ thuật Audio)

Thư mục này lưu trữ các bản thiết kế đề xuất nâng cấp bộ lọc âm thanh, mastering EBU R128, thuật toán ducking và logic chia chunk cho các tập truyện dài (>20 phút).

## Cấu trúc đề xuất:
- `proposal_YYYYMMDD_audio_<topic>.md`
- Mỗi đề xuất bao gồm:
  1. **Vấn đề âm thanh phát hiện qua audit** (ví dụ: lệch LUFS, clipping, tràn RAM khi render file dài).
  2. **Giải pháp kỹ thuật âm thanh đề xuất** (tham số FFmpeg, pydub, thuật toán xử lý).
  3. **Diff code rõ ràng.**
  4. **Kết quả kiểm thử sau khi áp dụng.**
