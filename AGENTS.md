# VÒNG LẶP TỰ HỌC TỰ THỰC CHIẾN (AUTONOMOUS SELF-LEARNING & EVOLUTION LOOP)

Khi làm việc trong dự án `TOOLTRUYENAUDIO`, trợ lý AI BẮT BUỘC tuân thủ 5 giai đoạn:

## 1. Cơ Chế Thực Thi Lặp Cho Đến Khi Đạt Chuẩn (Max 5 Retries)
- Khi chạy bất kỳ tool/script nào: Phải tự động thử nghiệm và verify kết quả đầu ra.
- Nếu lỗi hoặc kết quả chưa đạt 100%: **TUYỆT ĐỐI KHÔNG** dừng lại hỏi người dùng ngay. Tự phân tích traceback/output, tự tinh chỉnh tham số/thuật toán và chạy lại tối đa 5 lần.
- Chỉ dừng khi Exit Code = 0 và kết quả đạt chuẩn chất lượng (không rỗng, đúng format tiếng Việt).

## 2. Ghi Nhận Vết Thực Thi & Đúc Kết Heuristics
- Sau mỗi lần chạy tool, tự động ghi 1 dòng JSON vào `.agents/experience_memory/execution_traces.jsonl` gồm các trường:
  `timestamp`, `tool_name`, `retry_count`, `approach_and_fixes`, `metrics`, `reflection`.
- Nếu phát hiện mẹo hay hoặc quy tắc xử lý biên: Lập tức ghi vào `.agents/experience_memory/learned_heuristics.md`.

## 3. Thẩm Định & Phản Tư (Evaluator)
- Khi có yêu cầu "Đánh giá và nâng cấp":
  - Đọc lại toàn bộ `execution_traces.jsonl`, `tools_registry.json`, `learned_heuristics.md`.
  - Đối chiếu mã nguồn hiện tại với `.agents/evals/benchmark_tests.json`.
  - Tìm các lỗi từng gây retry nhiều lần để đề xuất đóng gói xử lý triệt để trong code gốc.

## 4. Nâng Cấp An Toàn (Safe Self-Upgrade)
- Xuất đề xuất thay đổi dạng Diff vào `.agents/evals/proposals/proposal_YYYYMMDD_<tool_name>.md`.
- **TUYỆT ĐỐI KHÔNG** tự ý ghi đè vào tool gốc khi chưa có lệnh duyệt ("Duyệt" / "Merge") từ người dùng.
- Sau khi người dùng duyệt, merge code và chạy lại `python -m unittest discover tests`.

## 5. Tự Động Ghi Devlog & Push GitHub (Auto-Sync)
- Tự động sinh `docs/devlogs/devlog_YYYY-MM-DD.md` (4 mục chuẩn) và cập nhật `docs/devlogs/README.md`.
- Sử dụng script `.agents/skills/tool-learner-evaluator/scripts/sync_to_github.py` để tự động kiểm tra an toàn, `git add`, `git commit` và `git push origin <branch>`.
- Nếu có conflict, tự động `git pull --rebase` và push lại, báo cáo hash commit cho người dùng.
