"""
video_fetcher.py - Auto-fetches and pre-processes 9:16 muted background videos for TikTok.
"""

import os
import glob
import random
import logging
from typing import Optional, List

from src.utils.ffmpeg_utils import run_ffmpeg_command, get_media_duration
from src.utils.logger import setup_logger

logger = setup_logger("TOOLTRUYENAUDIO.video_fetcher")


class VideoFetcher:
    """
    Downloads or generates engaging, mute background videos for TikTok (9:16, 1080x1920).
    Supports Gameplay (Subway Surfers, Minecraft) and Oddly Satisfying (Soap cutting, Hydraulic press).
    """

    GAMEPLAY_QUERIES = [
        "Subway Surfers no copyright gameplay shorts",
        "Minecraft Parkour gameplay no copyright shorts",
        "GTA V stunt race gameplay no copyright shorts",
    ]

    SATISFYING_QUERIES = [
        "soap cutting ASMR satisfying shorts",
        "hydraulic press satisfying shorts",
        "kinetic sand satisfying ASMR",
        "clay sculpting oddly satisfying",
    ]

    def __init__(self, output_dir: str = "assets/bg_videos"):
        self.output_dir = output_dir
        self.raw_dir = os.path.join(output_dir, "raw")
        os.makedirs(self.raw_dir, exist_ok=True)

    def _generate_synthetic_satisfying_video(self, output_path: str, duration_seconds: int = 240) -> str:
        """Generates a smooth, colorful geometric satisfying video using FFmpeg lavfi."""
        logger.info(f"[VideoFetcher] Generating synthetic satisfying vertical background ({duration_seconds}s)...")
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

        # Uses mandelbrot fractal zoom animation rendered directly in 1080x1920 at 30fps
        filter_expr = (
            f"mandelbrot=size=1080x1920:rate=30,"
            f"hue=s=sin(2*PI*t/10):H=2*PI*t/15,"
            f"format=yuv420p"
        )
        args = [
            "-y",
            "-f", "lavfi",
            "-i", filter_expr,
            "-t", str(duration_seconds),
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-an",
            output_path,
        ]
        run_ffmpeg_command(args)
        logger.info(f"[VideoFetcher] Generated synthetic satisfying video: {output_path}")
        return output_path

    def _download_candidate_video(self, query: str, output_template: str) -> Optional[str]:
        """Downloads a short video using yt-dlp."""
        try:
            import yt_dlp
            ydl_opts = {
                "format": "bestvideo[ext=mp4][height<=1080]/best[ext=mp4]/best",
                "outtmpl": output_template,
                "quiet": True,
                "no_warnings": True,
                "max_filesize": 100 * 1024 * 1024,  # Max 100MB
            }
            search_query = f"ytsearch2:{query}"
            logger.info(f"[VideoFetcher] Searching and downloading background video: '{query}'...")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(search_query, download=True)
                if "entries" in info and len(info["entries"]) > 0:
                    entry = info["entries"][0]
                    expected_file = ydl.prepare_filename(entry)
                    if os.path.exists(expected_file):
                        return expected_file
        except Exception as e:
            logger.warning(f"[VideoFetcher] yt-dlp download failed ({e}). Will use cached or synthetic fallback.")
        return None

    def fetch_and_prepare(
        self,
        category: str = "gameplay",
        target_duration_seconds: int = 240,
        output_filename: str = "prepared_bg_4min.mp4",
    ) -> str:
        """
        Fetches, mutes, crops to 9:16 vertical (1080x1920), and loops/trims to
        exact target_duration_seconds.
        """
        final_output = os.path.join(self.output_dir, output_filename)
        os.makedirs(os.path.dirname(os.path.abspath(final_output)), exist_ok=True)

        # Check existing raw clips in assets/bg_videos/raw
        existing_raw = glob.glob(os.path.join(self.raw_dir, "*.mp4"))
        raw_clip = None

        if existing_raw:
            raw_clip = random.choice(existing_raw)
            logger.info(f"[VideoFetcher] Reusing existing cached video: {raw_clip}")
        else:
            query_pool = self.GAMEPLAY_QUERIES if category == "gameplay" else self.SATISFYING_QUERIES
            chosen_query = random.choice(query_pool)
            out_tmpl = os.path.join(self.raw_dir, f"{category}_%(id)s.%(ext)s")
            raw_clip = self._download_candidate_video(chosen_query, out_tmpl)

        # If download fails or no raw video, synthesize one
        if not raw_clip or not os.path.exists(raw_clip):
            return self._generate_synthetic_satisfying_video(final_output, target_duration_seconds)

        # Process raw video: Strip audio, scale/crop to 9:16 (1080x1920), loop to exact target duration
        raw_duration = get_media_duration(raw_clip)
        logger.info(f"[VideoFetcher] Processing raw video '{os.path.basename(raw_clip)}' (duration: {raw_duration:.1f}s)...")

        # Video filter: Scale & center-crop to 1080x1920
        vf_filter = (
            "scale=1080:1920:force_original_aspect_ratio=increase,"
            "crop=1080:1920,"
            "setsar=1,"
            "fps=30"
        )

        args = [
            "-y",
            "-stream_loop", "-1",  # Loop indefinitely until target duration reached
            "-i", raw_clip,
            "-t", str(target_duration_seconds),
            "-vf", vf_filter,
            "-c:v", "libx264",
            "-preset", "fast",
            "-pix_fmt", "yuv420p",
            "-an",  # Strip original audio completely
            final_output,
        ]

        run_ffmpeg_command(args)
        logger.info(f"[VideoFetcher] Prepared 9:16 mute background video ready: {final_output}")
        return final_output
