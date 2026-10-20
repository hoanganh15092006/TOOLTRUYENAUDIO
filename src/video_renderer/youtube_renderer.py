"""
youtube_renderer.py - High-speed FFmpeg renderer for full-length YouTube Audiobooks (>30 mins).
"""

import os
import logging
from src.utils.ffmpeg_utils import run_ffmpeg_command, get_media_duration
from src.utils.logger import setup_logger

logger = setup_logger("TOOLTRUYENAUDIO.yt_renderer")


class YouTubeRenderer:
    """
    Renders the full YouTube video (16:9, 1920x1080) using a single still image
    and master audio. Executes in seconds regardless of audio duration.
    """

    def __init__(self, output_path: str = "output/youtube_full.mp4"):
        self.output_path = output_path

    def render(self, image_path: str, audio_path: str, output_path: str = None) -> str:
        """
        Renders 16:9 full-length YouTube video.
        """
        target_output = output_path or self.output_path
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Background image not found: {image_path}")
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        os.makedirs(os.path.dirname(os.path.abspath(target_output)), exist_ok=True)
        audio_duration = get_media_duration(audio_path)
        logger.info(
            f"[YouTubeRenderer] Rendering YouTube video ({audio_duration:.1f}s) to '{target_output}'..."
        )

        args = [
            "-y",
            "-loop", "1",
            "-i", image_path,
            "-i", audio_path,
            "-c:v", "libx264",
            "-tune", "stillimage",
            "-c:a", "aac",
            "-b:a", "192k",
            "-pix_fmt", "yuv420p",
            "-shortest",
            target_output,
        ]

        run_ffmpeg_command(args)
        final_duration = get_media_duration(target_output)
        logger.info(
            f"[YouTubeRenderer] YouTube full video ready! Output: '{target_output}' "
            f"(Duration: {final_duration:.1f}s, Size: {os.path.getsize(target_output):,} bytes)"
        )
        return target_output
