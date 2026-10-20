"""
prompts.py - Prompt templates for Oneshot Audio Story Generation.
"""

SYSTEM_STORYTELLER_PROMPT = """Bạn là một tác giả viết truyện audio chuyên nghiệp hàng đầu tại Việt Nam, chuyên sáng tác các tác phẩm Oneshot (truyện ngắn trọn bộ trong một tập duy nhất).
Văn phong của bạn giàu cảm xúc, sử dụng từ ngữ gợi hình, gợi cảm, nhịp điệu tự nhiên, cực kỳ phù hợp cho người đọc diễn cảm (TTS / Voice Talent).

QUY TẮC BẮT BUỘC:
1. KHÔNG chia chương, KHÔNG đánh số "Phần 1", "Chương 2", "Hồi 3" hay bất kỳ tiêu đề phụ nào. Toàn bộ câu chuyện phải là dòng văn xuôi tự sự liền mạch từ đầu tới cuối.
2. Viết bằng tiếng Việt chuẩn, tự nhiên, câu cú mượt mà, lời thoại có hồn, miêu tả tâm lý nhân vật sâu sắc.
3. Độ dài phải đạt đủ số lượng từ được yêu cầu trong từng giai đoạn.
4. Đảm bảo toàn bộ câu chuyện là ONESHOT trọn vẹn trong một tập, giải quyết dứt điểm các mâu thuẫn chính.
"""

def get_title_prompt(topic: str) -> str:
    return f"""Dựa vào chủ đề truyện: "{topic}", hãy sáng tác 1 tiêu đề truyện audio Oneshot thật giật gân, hấp dẫn, đậm chất drama hoặc lôi cuốn người nghe (dưới 15 từ).
Chỉ trả về DUY NHẤT tiêu đề câu chuyện, không thêm dấu ngoặc kép, không thêm lời chào hay giải thích nào khác.
Ví dụ: Trọng Sinh Thành Tiểu Thư Bị Bỏ Rơi, Tôi Khiến Cả Hào Môn Phải Trả Giá
Tiêu đề:"""

def get_part_1_prompt(topic: str, title: str, target_words: int) -> str:
    return f"""Chủ đề: {topic}
Tên truyện: {title}
Yêu cầu nhiệm vụ: Viết PHẦN 1 của câu chuyện (độ dài khoảng {target_words} từ).

CẤU TRÚC ĐẶC BIỆT BẮT BUỘC CHO PHẦN 1:
- Từ từ đầu đến từ thứ ~500: Giới thiệu hoàn cảnh, nhân vật chính, không gian bối cảnh và mâu thuẫn ngấm ngầm đang dần nảy sinh.
- ĐÚNG Ở KHOẢNG TỪ THỨ 550 - 600 (Tương ứng phút thứ 3:45 - 4:00 của bản audio): Đẩy ngay lên một CÚ TWIST / CLIFFHANGER CỰC GẮT (Ví dụ: phát hiện bí mật kinh hoàng, kẻ phản bội lộ mặt, vụ tai nạn chấn động, một lời tuyên bố tàn nhẫn khiến cục diện đảo lộn hoàn toàn).
- Từ thứ 600 đến {target_words}: Nối tiếp phản ứng bàng hoàng, dồn nén cảm xúc ngay sau cú twist đó và mở ra ngã rẽ gay cấn tiếp theo.

LƯU Ý QUAN TRỌNG:
- Tuyệt đối KHÔNG viết tiêu đề như "Phần 1" hay "Mở đầu". Bắt đầu ngay bằng câu chuyện.
- Viết đủ tối thiểu {int(target_words * 0.9)} từ.
"""

def get_middle_part_prompt(topic: str, title: str, part_num: int, target_words: int, previous_summary: str, previous_tail: str) -> str:
    return f"""Chủ đề: {topic}
Tên truyện: {title}
Tóm tắt diễn biến trước đó: {previous_summary}
Đoạn cuối của phần trước vừa kết thúc như sau:
\"...{previous_tail}\"

Yêu cầu nhiệm vụ:
Viết tiếp nối liền mạch giai đoạn tiếp theo của câu chuyện (độ dài khoảng {target_words} từ).
- Bắt nhịp ngay lập tức với cảm xúc và hành động ở câu cuối của phần trước mà không bị ngắt quãng.
- Đẩy cao mâu thuẫn, đào sâu đấu tranh tâm lý, hé lộ thêm các tình tiết bất ngờ và đẩy câu chuyện đến đỉnh điểm của cao trào trước khi hạ màn.
- TUYỆT ĐỐI KHÔNG xuất hiện tiêu đề phụ, không ghi "Phần {part_num}" hay "Chương {part_num}".
- Viết đủ tối thiểu {int(target_words * 0.9)} từ.
"""

def get_final_part_prompt(topic: str, title: str, target_words: int, ending_type: str, previous_summary: str, previous_tail: str) -> str:
    ending_instruction = ""
    if ending_type == "happy":
        ending_instruction = "KẾT THÚC CÓ HẬU (Happy Ending - HE): Kẻ xấu, kẻ phản bội phải trả giá xứng đáng theo luật nhân quả. Nhân vật chính vượt qua mọi đau thương, tìm lại được sự thanh thản, tự do, danh dự hoặc tình yêu chân thành trọn vẹn. Để lại cảm xúc thỏa mãn, ấm lòng cho người nghe."
    elif ending_type == "sad":
        ending_instruction = "KẾT THÚC KHÔNG CÓ HẬU / BI KỊCH (Sad Ending - SE): Chia ly, mất mát không thể bù đắp, người ở lại ôm nỗi day dứt khôn nguôi, sự thật được hé lộ khi mọi thứ đã quá muộn màng. Để lại dư âm nghẹn ngào, xót xa sâu sắc cho người nghe."
    else:  # open
        ending_instruction = "KẾT THÚC HỜ HỮNG / MỞ (Open/Indifferent Ending - OE): Kết thúc lưng chừng, buông bỏ nhẹ nhàng, nhân vật quay lưng bước đi không thù hận cũng không tha thứ. Một kết cục lạnh nhạt hoặc để lại câu hỏi mở đầy suy ngẫm cho người nghe."

    return f"""Chủ đề: {topic}
Tên truyện: {title}
Tóm tắt diễn biến trước đó: {previous_summary}
Đoạn cuối của phần trước vừa kết thúc như sau:
\"...{previous_tail}\"

Yêu cầu nhiệm vụ:
Viết PHẦN KẾT THÚC HẠ MÀN cho toàn bộ câu chuyện Oneshot này (độ dài khoảng {target_words} từ).
CHỈ ĐẠO KẾT THÚC BẮT BUỘC:
{ending_instruction}

LƯU Ý:
- Khép lại trọn vẹn mọi nút thắt của câu chuyện trong tập này.
- Tuyệt đối KHÔNG viết tiêu đề "Phần kết" hay "Hồi kết".
- Viết sâu sắc, câu kết lắng đọng cảm xúc người nghe.
"""
