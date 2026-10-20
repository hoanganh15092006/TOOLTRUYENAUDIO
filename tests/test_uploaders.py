import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
"""
test_uploaders.py - Unit test suite for YouTube and TikTok Uploaders.
"""

import os
import unittest
from unittest.mock import MagicMock, patch

from src.uploaders import YouTubeUploader, TikTokUploader
from src.uploaders.tiktok_uploader import (
    _find_file_input,
    _is_login_page_or_prompt,
    _find_caption_element,
    _find_bottom_action_button,
)


class TestUploaders(unittest.TestCase):
    def test_youtube_metadata_builder(self):
        uploader = YouTubeUploader()
        meta = uploader.build_metadata(
            story_title="Trọng Sinh Báo Thù",
            channel_name="Góc Truyện Audio",
            topic="Hào môn thế gia",
            duration_minutes=35,
            summary="Một câu chuyện đầy kịch tính.",
        )
        self.assertIn("[FULL] Trọng Sinh Báo Thù", meta["title"])
        self.assertIn("Góc Truyện Audio", meta["description"])
        self.assertIn("truyenaudio", meta["tags"])
        self.assertEqual(meta["category_id"], "24")

    def test_tiktok_caption_builder(self):
        uploader = TikTokUploader()
        caption = uploader.build_caption(
            story_title="Trọng Sinh Báo Thù",
            channel_name="Góc Truyện Audio",
            duration_minutes=35,
        )
        self.assertIn("Trọng Sinh Báo Thù (Phần đầu)", caption)
        self.assertIn("hơn 35 phút", caption)
        self.assertIn("Góc Truyện Audio", caption)
        self.assertIn("#truyenaudio", caption)

    def test_tiktok_missing_video_raises(self):
        uploader = TikTokUploader()
        with self.assertRaises(FileNotFoundError):
            uploader.upload("does_not_exist_abc.mp4", "Title", "Channel", 35)

    def test_tiktok_is_login_page(self):
        page = MagicMock()
        page.url = "https://www.tiktok.com/login"
        self.assertTrue(_is_login_page_or_prompt(page))

        page.url = "https://www.tiktok.com/tiktokstudio/upload"
        page.locator.return_value.count.return_value = 0
        self.assertFalse(_is_login_page_or_prompt(page))

    def test_tiktok_find_file_input(self):
        page = MagicMock()
        mock_input = MagicMock()
        page.locator.return_value.count.return_value = 1
        page.locator.return_value.first = mock_input
        found = _find_file_input(page)
        self.assertEqual(found, mock_input)


if __name__ == "__main__":
    unittest.main()

