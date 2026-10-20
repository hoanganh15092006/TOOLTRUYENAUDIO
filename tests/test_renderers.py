import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
"""
test_renderers.py - Unit test suite for YouTube and TikTok video rendering.
"""

import os
import tempfile
import unittest
from PIL import Image

from src.utils.ffmpeg_utils import run_ffmpeg_command, get_media_duration
from src.media_fetcher import ImageGenerator, VideoFetcher
from src.video_renderer import YouTubeRenderer, TikTokRenderer


class TestMediaAndRenderers(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="test_renderer_")
        self.img_gen = ImageGenerator(output_dir=os.path.join(self.temp_dir, "images"))
        self.vid_fetcher = VideoFetcher(output_dir=os.path.join(self.temp_dir, "videos"))

        # Create dummy 16:9 image
        self.image_path = os.path.join(self.temp_dir, "sample_img.jpg")
        img = Image.new("RGB", (1920, 1080), color=(30, 40, 60))
        img.save(self.image_path)

        # Create dummy audio (4 seconds)
        self.audio_path = os.path.join(self.temp_dir, "sample_audio.mp3")
        run_ffmpeg_command([
            "-y", "-f", "lavfi", "-i", "aevalsrc='0.1*sin(2*PI*440*t)':s=44100:d=4",
            "-c:a", "libmp3lame", self.audio_path
        ])

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_image_generator_fallback(self):
        fallback = self.img_gen.create_fallback_image(topic="Kinh dị")
        self.assertTrue(os.path.exists(fallback))
        with Image.open(fallback) as im:
            self.assertEqual(im.size, (1920, 1080))

    def test_youtube_renderer(self):
        yt_out = os.path.join(self.temp_dir, "yt_test.mp4")
        renderer = YouTubeRenderer(output_path=yt_out)
        out = renderer.render(image_path=self.image_path, audio_path=self.audio_path)
        self.assertTrue(os.path.exists(out))
        dur = get_media_duration(out)
        self.assertAlmostEqual(dur, 4.0, delta=0.5)

    def test_video_fetcher_synthetic(self):
        bg_out = os.path.join(self.temp_dir, "synthetic_bg.mp4")
        self.vid_fetcher._generate_synthetic_satisfying_video(bg_out, duration_seconds=2)
        self.assertTrue(os.path.exists(bg_out))
        dur = get_media_duration(bg_out)
        self.assertAlmostEqual(dur, 2.0, delta=0.5)

    def test_tiktok_renderer(self):
        bg_video = os.path.join(self.temp_dir, "bg_vertical.mp4")
        self.vid_fetcher._generate_synthetic_satisfying_video(bg_video, duration_seconds=3)

        tk_out = os.path.join(self.temp_dir, "tiktok_test.mp4")
        renderer = TikTokRenderer(output_path=tk_out)
        out = renderer.render(
            bg_video_path=bg_video,
            master_audio_path=self.audio_path,
            channel_name="Kênh Test",
            story_title="Truyện Ngắn Hay",
            duration_seconds=3,
            fade_seconds=1,
        )
        self.assertTrue(os.path.exists(out))
        dur = get_media_duration(out)
        self.assertAlmostEqual(dur, 3.0, delta=0.5)


if __name__ == "__main__":
    unittest.main()

