"""
tiktok_renderer.py - Renders 4-minute vertical 9:16 TikTok teaser with eye-catching overlay banners.
"""

import os
import glob
import logging
from typing import Optional

from src.utils.ffmpeg_utils import run_ffmpeg_command, cut_audio_with_fadeout, get_media_duration
from src.utils.logger import setup_logger

logger = setup_logger("TOOLTRUYENAUDIO.tiktok_renderer")


class TikTokRenderer:
    """
    Renders the 4-minute (240s) TikTok teaser video:
      - 9:16 vertical resolution (1080x1920).
      - Mute background gameplay / satisfying footage.
      - First 4 minutes of the master story audio (with cliffhanger at min ~3:45-4:00).
      - Fixed, crystal-clear overlay banners promoting the full YouTube channel and Story Title.
    """

    def __init__(
        self,
        output_path: str = "output/tiktok_teaser.mp4",
        fonts_dir: str = "assets/fonts",
    ):
        self.output_path = output_path
        self.fonts_dir = fonts_dir

    def _resolve_font_file(self) -> str:
        """Finds a valid TrueType font supporting Vietnamese diacritics."""
        # 1. Custom font in assets/fonts
        if os.path.isdir(self.fonts_dir):
            fonts = glob.glob(os.path.join(self.fonts_dir, "*.ttf")) + glob.glob(os.path.join(self.fonts_dir, "*.otf"))
            if fonts:
                return fonts[0]

        # 2. Windows system fonts with full Vietnamese Unicode support
        system_fonts = [
            "C:/Windows/Fonts/arial.ttf",
            "C:/Windows/Fonts/segoeui.ttf",
            "C:/Windows/Fonts/calibri.ttf",
            "C:/Windows/Fonts/tahoma.ttf",
        ]
        for sf in system_fonts:
            if os.path.exists(sf):
                return sf

        return "Arial"

    def _escape_drawtext(self, text: str) -> str:
        """Escapes special characters for FFmpeg drawtext filter."""
        text = text.replace("\\", "\\\\")
        text = text.replace("'", "\\'")
        text = text.replace(":", "\\:")
        text = text.replace("%", "\\%")
        return text

    def render(
        self,
        bg_video_path: str,
        master_audio_path: str,
        channel_name: str,
        story_title: str,
        output_path: Optional[str] = None,
        duration_seconds: int = 240,
        fade_seconds: int = 3,
    ) -> str:
        """
        Renders the 4-minute TikTok teaser video.
        """
        final_output = output_path or self.output_path
        if not os.path.exists(bg_video_path):
            raise FileNotFoundError(f"Background video not found: {bg_video_path}")
        if not os.path.exists(master_audio_path):
            raise FileNotFoundError(f"Master audio not found: {master_audio_path}")

        os.makedirs(os.path.dirname(os.path.abspath(final_output)), exist_ok=True)

        # 1. Cut the first duration_seconds with fade-out
        cut_audio_temp = os.path.join(os.path.dirname(final_output), f"temp_cut_{duration_seconds}s.mp3")
        logger.info(f"[TikTokRenderer] Extracting first {duration_seconds}s from master audio...")
        cut_audio_with_fadeout(
            input_path=master_audio_path,
            output_path=cut_audio_temp,
            duration_seconds=duration_seconds,
            fade_seconds=fade_seconds,
        )

        font_file = self._resolve_font_file()
        font_path_escaped = font_file.replace("\\", "/").replace(":", "\\:")

        safe_channel = self._escape_drawtext(f"Nghe Full tai YouTube: {channel_name}")
        safe_title = self._escape_drawtext(f"Truyen: {story_title}")

        # Two stacked banners in upper third of 9:16 screen (prominent & visible on TikTok)
        vf_filter = (
            f"drawtext=fontfile='{font_path_escaped}':text='{safe_channel}':"
            f"fontsize=46:fontcolor=white:x=(w-text_w)/2:y=h*0.16:"
            f"box=1:boxcolor=black@0.70:boxborderw=20,"
            f"drawtext=fontfile='{font_path_escaped}':text='{safe_title}':"
            f"fontsize=40:fontcolor=yellow:x=(w-text_w)/2:y=h*0.23:"
            f"box=1:boxcolor=black@0.70:boxborderw=18"
        )

        logger.info(f"[TikTokRenderer] Rendering 4-minute TikTok teaser to '{final_output}'...")

        args = [
            "-y",
            "-i", bg_video_path,
            "-i", cut_audio_temp,
            "-t", str(duration_seconds),
            "-vf", vf_filter,
            "-c:v", "libx264",
            "-preset", "fast",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            final_output,
        ]

        run_ffmpeg_command(args)

        # Remove temp cut audio
        try:
            if os.path.exists(cut_audio_temp):
                os.remove(cut_audio_temp)
        except Exception:
            pass

        final_dur = get_media_duration(final_output)
        logger.info(
            f"[TikTokRenderer] TikTok teaser ready: '{final_output}' "
            f"(Duration: {final_dur:.1f}s, Size: {os.path.getsize(final_output):,} bytes)"
        )
        return final_output
