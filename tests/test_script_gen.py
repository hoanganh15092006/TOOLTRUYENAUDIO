import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
"""
test_script_gen.py - Unit test suite for StoryScriptGenerator and Ending Types.
"""

import unittest
from unittest.mock import MagicMock, patch
from src.script_gen import StoryScriptGenerator


class TestStoryScriptGenerator(unittest.TestCase):
    def setUp(self):
        self.generator = StoryScriptGenerator(api_key=None)

    def test_title_generation(self):
        title = self.generator.generate_title("Tổng tài và cô gái nghèo")
        self.assertTrue(len(title) > 5)
        self.assertNotIn('"', title)

    def test_word_count_calculation_and_parts(self):
        # 35 minutes target -> ~5,250 words -> 5 parts
        res = self.generator.generate_oneshot_script(
            topic="Kinh dị ngôi nhà hoang",
            target_duration_minutes=35,
            ending_type="happy",
        )
        self.assertEqual(res["target_duration_minutes"], 35)
        self.assertEqual(res["ending_type"], "happy")
        self.assertTrue(res["total_words"] > 0)
        self.assertIn("full_script", res)
        self.assertTrue(len(res["cliffhanger_snippet"]) > 0)

    def test_ending_types_happy(self):
        res = self.generator.generate_oneshot_script(
            topic="Báo thù gia tộc",
            target_duration_minutes=10,
            ending_type="happy",
        )
        self.assertEqual(res["ending_type"], "happy")

    def test_ending_types_sad(self):
        res = self.generator.generate_oneshot_script(
            topic="Mối tình đầu dang dở",
            target_duration_minutes=10,
            ending_type="sad",
        )
        self.assertEqual(res["ending_type"], "sad")

    def test_ending_types_open(self):
        res = self.generator.generate_oneshot_script(
            topic="Rời khỏi thành phố",
            target_duration_minutes=10,
            ending_type="open",
        )
        self.assertEqual(res["ending_type"], "open")

    def test_clean_story_text_removes_headers(self):
        dirty = "Chương 1: Mở đầu\nNgày xưa có một cô bé.\n**Phần 2: Biến cố**\nMọi chuyện thay đổi.\n---"
        cleaned = self.generator._clean_story_text(dirty)
        self.assertNotIn("Chương 1", cleaned)
        self.assertNotIn("**Phần 2", cleaned)
        self.assertNotIn("---", cleaned)
        self.assertIn("Ngày xưa có một cô bé.", cleaned)


if __name__ == "__main__":
    unittest.main()

