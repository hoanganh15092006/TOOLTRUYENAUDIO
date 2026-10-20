"""
generator.py - Multi-part seamless Oneshot Audio Story Script Generator with Gemini LLM.
"""

import os
import re
import math
import logging
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

from .prompts import (
    SYSTEM_STORYTELLER_PROMPT,
    get_title_prompt,
    get_part_1_prompt,
    get_middle_part_prompt,
    get_final_part_prompt,
)

logger = logging.getLogger("TOOLTRUYENAUDIO.script_gen")
load_dotenv()


class StoryScriptGenerator:
    """
    Generates dynamic-length Oneshot stories using seamless multi-part generation.
    Enforces a powerful cliffhanger at minute 3:45 - 4:00 (word 550-600) and
    respects the chosen ending type (Happy, Sad, Open).
    """

    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-2.5-flash"):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model_name = model_name
        self.client = None

        if self.api_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=self.api_key)
                logger.info(f"[ScriptGen] Initialized Google GenAI client (model: {self.model_name})")
            except Exception as e:
                logger.warning(f"[ScriptGen] Failed to initialize Google GenAI client: {e}. Fallback mode active.")
        else:
            logger.warning("[ScriptGen] No GEMINI_API_KEY provided. Fallback mock storyteller active.")

    def _call_llm(self, prompt: str) -> str:
        """Helper to invoke LLM with system context."""
        if not self.client:
            return self._generate_fallback_text(prompt)

        try:
            full_prompt = f"{SYSTEM_STORYTELLER_PROMPT}\n\n{prompt}"
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=full_prompt,
            )
            text = response.text or ""
            return self._clean_story_text(text)
        except Exception as exc:
            logger.error(f"[ScriptGen] LLM generation error: {exc}. Using fallback narrative.")
            return self._generate_fallback_text(prompt)

    def _clean_story_text(self, text: str) -> str:
        """Removes chapter markers, markdown hashes, and meta headers."""
        lines = []
        for line in text.splitlines():
            stripped = line.strip()
            # Remove chapter or part titles
            if re.match(r"^(Chương|Phần|Hồi|Tập|Mở đầu|Kết thúc|Tiết tử)\s*\d*[:\-–\.]?", stripped, re.IGNORECASE):
                continue
            if stripped.startswith("#") or stripped.startswith("---") or stripped.startswith("==="):
                continue
            if stripped.startswith("**Phần") or stripped.startswith("**Chương"):
                continue
            lines.append(line)
        cleaned = "\n".join(lines).strip()
        # Remove markdown bold/italics markers to ensure natural text for TTS
        cleaned = re.sub(r"\*\*([^*]+)\*\*", r"\1", cleaned)
        cleaned = re.sub(r"\*([^*]+)\*", r"\1", cleaned)
        return cleaned

    def generate_title(self, topic: str) -> str:
        """Generates an engaging, click-worthy title for the story topic."""
        prompt = get_title_prompt(topic)
        title = self._call_llm(prompt).strip()
        title = title.replace('"', '').replace("'", "").strip()
        if not title or len(title) < 5:
            title = f"Góc Khuất Cuộc Đời: {topic.title()}"
        logger.info(f"[ScriptGen] Generated Story Title: '{title}'")
        return title

    def generate_oneshot_script(
        self,
        topic: str,
        title: Optional[str] = None,
        target_duration_minutes: int = 35,
        ending_type: str = "happy",
    ) -> Dict[str, Any]:
        """
        Generates a complete Oneshot audio script for the specified duration and ending.

        Args:
            topic: Story subject/genre.
            title: Story title (if None, auto-generated).
            target_duration_minutes: Target duration (default: 35 minutes).
            ending_type: 'happy', 'sad', or 'open'.

        Returns:
            Dict containing full script, parts, title, word count, cliffhanger snippet.
        """
        if not title:
            title = self.generate_title(topic)

        ending_type = ending_type.lower()
        if ending_type not in ["happy", "sad", "open"]:
            ending_type = "happy"

        words_per_minute = 150
        target_words = target_duration_minutes * words_per_minute
        logger.info(
            f"[ScriptGen] Target Duration: {target_duration_minutes}m | Target Words: ~{target_words} | Ending: {ending_type}"
        )

        # Calculate number of generation parts
        part_word_limit = 1200
        num_parts = max(1, math.ceil(target_words / part_word_limit))
        words_per_part = math.ceil(target_words / num_parts)

        logger.info(f"[ScriptGen] Generating story across {num_parts} seamless parts (~{words_per_part} words/part)...")

        parts_content: List[str] = []

        # Part 1: Opening & Cliffhanger at minute 3:45 - 4:00 (word 550-600)
        logger.info("[ScriptGen] [Part 1/{}]: Crafting introduction & 4-minute cliffhanger...".format(num_parts))
        part1_prompt = get_part_1_prompt(topic, title, words_per_part)
        part1_text = self._call_llm(part1_prompt)
        parts_content.append(part1_text)

        # Middle parts (if num_parts > 2)
        for i in range(1, num_parts - 1):
            logger.info(f"[ScriptGen] [Part {i + 1}/{num_parts}]: Continuing narrative development...")
            prev_tail = " ".join(parts_content[-1].split()[-120:])
            summary = f"Chuyện về '{title}', mâu thuẫn đang dâng cao kịch tính."
            mid_prompt = get_middle_part_prompt(
                topic, title, i + 1, words_per_part, summary, prev_tail
            )
            mid_text = self._call_llm(mid_prompt)
            parts_content.append(mid_text)

        # Final Part: Climax & Resolution adhering strictly to ending_type
        if num_parts > 1:
            logger.info(f"[ScriptGen] [Part {num_parts}/{num_parts}]: Delivering climax and '{ending_type}' ending...")
            prev_tail = " ".join(parts_content[-1].split()[-120:])
            summary = f"Giai đoạn cuối của '{title}', tiến tới giải quyết toàn bộ nút thắt."
            final_prompt = get_final_part_prompt(
                topic, title, words_per_part, ending_type, summary, prev_tail
            )
            final_text = self._call_llm(final_prompt)
            parts_content.append(final_text)

        full_script = "\n\n".join(parts_content).strip()
        word_list = full_script.split()
        actual_words = len(word_list)

        # Extract cliffhanger snippet around words 550-600
        cliffhanger_words = word_list[500:650] if len(word_list) >= 650 else word_list[-150:]
        cliffhanger_snippet = " ".join(cliffhanger_words)

        logger.info(
            f"[ScriptGen] Oneshot script complete! Total words: {actual_words} "
            f"(~{actual_words / words_per_minute:.1f} audio minutes)"
        )

        return {
            "title": title,
            "topic": topic,
            "target_duration_minutes": target_duration_minutes,
            "estimated_audio_duration_minutes": round(actual_words / words_per_minute, 1),
            "ending_type": ending_type,
            "total_words": actual_words,
            "full_script": full_script,
            "cliffhanger_snippet": cliffhanger_snippet,
            "parts_count": len(parts_content),
        }

    def _generate_fallback_text(self, prompt: str) -> str:
        """Rich synthetic Vietnamese story generator for testing/offline fallback."""
        if "tiêu đề" in prompt.lower():
            return "Nước Mắt Hào Môn: Ngày Trở Về Của Kẻ Bị Bỏ Rơi"

        is_happy = "có hậu" in prompt.lower() or "happy" in prompt.lower()
        is_sad = "không có hậu" in prompt.lower() or "bi kịch" in prompt.lower()

        text_chunk = """
Đêm hôm đó, thành phố chìm trong cơn mưa rào xối xả, từng giọt nước đập dồn dập vào ô cửa kính của căn biệt thự cổ kính nằm nép mình bên sườn đồi. Trong căn phòng khách rộng lớn, ánh đèn chùm pha lê hắt xuống những vệt sáng lạnh lẽo. Thanh Mai ngồi lặng lẽ bên tách trà hoa cúc đã nguội ngắt từ lâu, đôi mắt cô sâu thẳm nhìn về phía chiếc đồng hồ quả lắc đang điểm từng nhịp khô khốc.

Cô nhớ lại năm năm trước, khi cô rời khỏi nơi này với hai bàn tay trắng, mang theo nỗi oan ức nghẹn ngào mà không một ai chịu lắng nghe. Gia đình họ Trần khi ấy đã coi cô như một vết nhơ, xua đuổi cô không chút thương xót giữa đêm đông lạnh giá. Nhưng cuộc đời vốn là một ván cờ đầy bất ngờ. Sau năm năm bươn chải nơi đất khách quê người, trải qua biết bao cay đắng tủi nhục, cô đã trở về, không còn là cô gái ngây thơ dễ bị ức hiếp của ngày xưa nữa. Giờ đây, cô đứng ở vị trí mà bất kỳ ai cũng phải ngước nhìn, nắm trong tay số phận của tập đoàn từng đẩy cô vào bước đường cùng.

Đúng lúc này, tiếng bước chân vội vã vang lên trên hành lang lát đá cẩm thạch. Cánh cửa gỗ lim nặng nề bật mở, người đàn ông ấy bước vào trong bộ âu phục ướt đẫm nước mưa. Khuôn mặt anh ta tái nhợt, đôi mắt đỏ ngầu nhìn cô đầy bàng hoàng. Chính là anh – người từng thề non hẹn biển rồi nhẫn tâm ký vào tờ đơn đoạn tuyệt năm nào. Anh ta run rẩy tiến lại gần, giọng nghẹn lại: "Thanh Mai... thật sự là em sao? Cả gia đình này sắp sụp đổ rồi, em có thể nương tay một lần được không?"

Thanh Mai khẽ cười, một nụ cười lạnh lùng đến tê tái: "Nương tay? Khi các người dồn mẹ con tôi vào ngõ cụt năm ấy, có ai từng nghĩ đến hai chữ nương tay hay chưa?" Căn phòng rơi vào sự im lặng nghẹt thở, chỉ còn tiếng sấm chớp rền vang ngoài trời như báo hiệu một cơn bão táp sắp ập xuống hào môn này.
"""
        if is_happy:
            text_chunk += """
Sau tất cả những âm mưu toan tính và những ân oán chất chồng suốt ngần ấy năm, sự thật cuối cùng cũng được đưa ra ánh sáng trước sự chứng kiến của mọi người. Kẻ thủ ác phải cúi đầu nhận tội trước pháp luật, nhận lấy sự trừng phạt thích đáng theo quy luật nhân quả không thể chối cãi. Đứng trước ngôi mộ của mẹ trên ngọn đồi ngát hương hoa dại, Thanh Mai khẽ mỉm cười nhẹ nhõm. Ánh bình minh rạng rỡ xuyên qua từng tán lá, xua tan đi màn đêm tăm tối. Cô hít một hơi thật sâu, nắm chặt tay người tri kỷ đã luôn đồng hành cùng cô qua bão giông. Một chương mới bình yên, hạnh phúc và trọn vẹn đã chính thức mở ra trong cuộc đời cô.
"""
        elif is_sad:
            text_chunk += """
Thế nhưng, khi bức màn bí mật cuối cùng được hé lộ, Thanh Mai mới bàng hoàng nhận ra sự thật cay đắng tột cùng mà bấy lâu nay cô không hề hay biết. Người mà cô ôm mối hận thù suốt năm năm qua lại chính là người đã âm thầm hy sinh tất cả, gánh chịu mọi điều tiếng nhục nhã để đổi lấy sự an toàn cho cô. Trong ngăn kéo bàn làm việc của anh là tập hồ sơ bệnh án giai đoạn cuối và bức thư từ biệt chưa kịp gửi. Tiếng còi xe cấp cứu xé toạc màn đêm mưa gió, nhưng tất cả đã quá muộn màng. Nắm lấy bàn tay lạnh ngắt của anh lần cuối, những giọt nước mắt hối hận muộn màng của Thanh Mai rơi xuống, để lại một khoảng trống vĩnh viễn không bao giờ có thể lấp đầy trong trái tim cô.
"""
        else:
            text_chunk += """
Khi màn đêm buông xuống, Thanh Mai đứng trên ban công tầng cao nhìn xuống dòng xe cộ tấp nập của thành phố hoa lệ. Những ân oán năm xưa, những tổn thương và toan tính giờ đây bỗng trở nên thật nhỏ bé và hư vô. Cô không chọn cách trả thù tàn nhẫn, cũng không chọn cách tha thứ dễ dàng. Cô đặt chiếc nhẫn năm xưa lên mặt bàn, kéo chiếc vali nhỏ và bước ra khỏi cánh cửa lớn mà không một lần ngoảnh lại. Gió đêm lướt nhẹ qua mái tóc, cuốn đi tất cả những vương vấn của một thời dĩ vãng. Cuộc sống vẫn tiếp diễn, và câu trả lời cho tương lai sẽ do chính thời gian định đoạt.
"""
        # Duplicate to meet length expectation for testing
        return (text_chunk.strip() + "\n\n") * 3
