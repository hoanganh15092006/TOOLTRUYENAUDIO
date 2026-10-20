import os
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from main import run_full_pipeline
from src.utils.ffmpeg_utils import run_ffmpeg_command

class TestPipelineE2E(unittest.TestCase):
    @patch("src.tts_engine.TTSEngine.synthesize")
    @patch("src.uploaders.YouTubeUploader.upload")
    @patch("src.uploaders.TikTokUploader.upload")
    def test_pipeline_dry_run(self, mock_tk, mock_yt, mock_tts):
        def fake_synth(text, out):
            os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
            run_ffmpeg_command([
                "-y", "-f", "lavfi", "-i", "aevalsrc='0.1*sin(2*PI*440*t)':s=44100:d=1",
                "-c:a", "libmp3lame", out
            ])
        mock_tts.side_effect = fake_synth
        mock_yt.return_value = True
        mock_tk.return_value = True

        res = run_full_pipeline(
            channel_name="Góc Truyện Audio Test",
            story_topic="Trọng sinh báo thù",
            story_title="Hào Môn Sóng Gió",
            duration_minutes=1,
            ending_type="happy",
            bg_image_mode="auto_ai",
            tiktok_bg_category="gameplay",
            skip_upload=True,
            only_audio=True,
        )
        self.assertEqual(res["title"], "Hào Môn Sóng Gió")
        self.assertIn("master_audio", res)

if __name__ == "__main__":
    unittest.main()
