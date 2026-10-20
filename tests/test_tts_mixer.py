import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
"""
test_tts_mixer.py - Unit test suite for TTS Engine and Audio Mixer.
"""

import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from src.tts_engine import TTSEngine, AudioMixer


class TestTTSAndMixer(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="test_tts_")
        self.engine = TTSEngine(voice="vi-VN-HoaiMyNeural")
        self.mixer = AudioMixer(bgm_dir=self.temp_dir)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_split_text_into_chunks(self):
        long_para = "Câu chuyện bắt đầu vào một buổi chiều mưa gió. " * 50
        chunks = self.engine._split_text_into_chunks(long_para, max_chars=500)
        self.assertTrue(len(chunks) > 1)
        for c in chunks:
            self.assertTrue(len(c) <= 600)

    def test_create_ambient_bgm_track(self):
        out_bgm = os.path.join(self.temp_dir, "ambient.mp3")
        self.mixer.create_ambient_bgm_track(out_bgm, duration_seconds=2)
        self.assertTrue(os.path.exists(out_bgm))
        self.assertTrue(os.path.getsize(out_bgm) > 1000)

    def test_mix_speech_and_bgm(self):
        # Create synthetic voice and bgm using ffmpeg lavfi
        from src.utils.ffmpeg_utils import run_ffmpeg_command, get_media_duration
        voice_path = os.path.join(self.temp_dir, "voice.mp3")
        bgm_path = os.path.join(self.temp_dir, "bgm.mp3")
        master_out = os.path.join(self.temp_dir, "master.mp3")

        # 3 seconds voice
        run_ffmpeg_command([
            "-y", "-f", "lavfi", "-i", "aevalsrc='0.1*sin(2*PI*440*t)':s=44100:d=3",
            "-c:a", "libmp3lame", voice_path
        ])
        # 2 seconds BGM (will loop)
        run_ffmpeg_command([
            "-y", "-f", "lavfi", "-i", "aevalsrc='0.05*sin(2*PI*220*t)':s=44100:d=2",
            "-c:a", "libmp3lame", bgm_path
        ])

        mixed = self.mixer.mix(voice_path=voice_path, output_path=master_out, bgm_path=bgm_path, bgm_volume_db=-20.0)
        self.assertTrue(os.path.exists(mixed))
        dur = get_media_duration(mixed)
        # Duration must match voice duration (~3s)
        self.assertAlmostEqual(dur, 3.0, delta=0.5)


if __name__ == "__main__":
    unittest.main()

