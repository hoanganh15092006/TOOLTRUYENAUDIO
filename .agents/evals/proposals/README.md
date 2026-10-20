# Proposals Directory (Khu vực Đề xuất Nâng cấp Mã nguồn)

Thư mục này chứa các bản thiết kế đề xuất nâng cấp code (Self-Upgrade Proposals) được sinh ra từ Giai đoạn 2 (Evaluator) & Giai đoạn 3 (Self-Upgrade).

## Cấu trúc file đề xuất:
Mỗi đề xuất sẽ được đặt tên theo mẫu:
`upgrade_cycle_<N>_<timestamp>_<topic>.md`

## Định dạng nội dung chuẩn:
1. **Mục tiêu nâng cấp:** Dựa trên các traces & heuristics nào.
2. **Đối chiếu Benchmark:** Những tiêu chí nào trong `benchmark_tests.json` đang chưa đạt.
3. **Mã nguồn đề xuất cải tiến (Unified Diff / Code blocks):** Rõ ràng từng file, từng hàm cần thay đổi.
4. **Kế hoạch kiểm thử hồi quy (Regression Test Plan):** Đảm bảo không làm gãy pipeline hiện tại.
5. **Trạng thái duyệt:** `[PENDING]` (Chờ người dùng xác nhận) -> `[MERGED]` (Đã tích hợp vào code chính).
