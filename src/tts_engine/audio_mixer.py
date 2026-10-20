"""
audio_mixer.py - Professional audio ducking and background music overlay for audiobooks.
"""

import os
import glob
import random
import logging
from typing import Optional

from src.utils.ffmpeg_utils import run_ffmpeg_command, get_media_duration

logger = logging.getLogger("TOOLTRUYENAUDIO.audio_mixer")


class AudioMixer:
    """
    Mixes voiceover narration with ambient background music (BGM).
    Applies audio ducking (lowering BGM volume) and loops BGM seamlessly
    to match the full length of the narrative audio.
    """

    def __init__(self, bgm_dir: str = "assets/bgm", default_bgm_volume_db: float = -24.0):
        self.bgm_dir = bgm_dir
        self.default_bgm_volume_db = default_bgm_volume_db

    def find_bgm_track(self, explicit_path: Optional[str] = None) -> Optional[str]:
        """Finds an explicit BGM track or picks a random track from assets/bgm."""
        if explicit_path and os.path.isfile(explicit_path):
            return explicit_path

        if os.path.isdir(self.bgm_dir):
            patterns = ["*.mp3", "*.wav", "*.m4a", "*.aac"]
            candidates = []
            for pat in patterns:
                candidates.extend(glob.glob(os.path.join(self.bgm_dir, pat)))
            if candidates:
                chosen = random.choice(candidates)
                logger.info(f"[AudioMixer] Selected BGM track: {chosen}")
                return chosen

        logger.info("[AudioMixer] No BGM tracks found in assets/bgm/. Generating ambient soundscape or pure voice.")
        return None

    def create_ambient_bgm_track(self, output_path: str, duration_seconds: int = 120) -> str:
        """Synthesizes a warm, low-frequency ambient drone tone for background depth if no BGM exists."""
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        # Synthesizes subtle soothing 110Hz + 220Hz harmonic drone
        filter_expr = "aevalsrc='0.02*sin(2*PI*110*t)+0.01*sin(2*PI*220*t)':s=44100:d={}".format(duration_seconds)
        args = [
            "-y",
            "-f", "lavfi",
            "-i", filter_expr,
            "-c:a", "libmp3lame",
            "-b:a", "128k",
            output_path,
        ]
        run_ffmpeg_command(args)
        return output_path

    def mix(
        self,
        voice_path: str,
        output_path: str,
        bgm_path: Optional[str] = None,
        bgm_volume_db: Optional[float] = None,
    ) -> str:
        """
        Mixes speech voiceover with looping BGM at ducked volume.
        Duration will match voice_path exactly.
        """
        if not os.path.exists(voice_path):
            raise FileNotFoundError(f"Voiceover audio not found: {voice_path}")

        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        volume_db = bgm_volume_db if bgm_volume_db is not None else self.default_bgm_volume_db

        active_bgm = self.find_bgm_track(bgm_path)

        if not active_bgm:
            # Generate default ambient track
            temp_bgm = os.path.join(os.path.dirname(output_path), "temp_ambient_bgm.mp3")
            try:
                active_bgm = self.create_ambient_bgm_track(temp_bgm, duration_seconds=60)
            except Exception as e:
                logger.warning(f"[AudioMixer] Could not generate ambient BGM ({e}). Using pure voice.")
                active_bgm = None

        if not active_bgm or not os.path.exists(active_bgm):
            import shutil
            shutil.copy2(voice_path, output_path)
            logger.info(f"[AudioMixer] Exported master audio (voice only): {output_path}")
            return output_path

        voice_duration = get_media_duration(voice_path)
        logger.info(
            f"[AudioMixer] Mixing speech ({voice_duration:.1f}s) with BGM '{os.path.basename(active_bgm)}' at {volume_db}dB..."
        )

        # Looping BGM and mix with speech
        filter_complex = (
            f"[1:a]volume={volume_db}dB[bgm_ducked];"
            f"[0:a][bgm_ducked]amix=inputs=2:duration=first:dropout_transition=2[out]"
        )

        args = [
            "-y",
            "-i", voice_path,
            "-stream_loop", "-1",
            "-i", active_bgm,
            "-filter_complex", filter_complex,
            "-map", "[out]",
            "-c:a", "libmp3lame",
            "-b:a", "192k",
            output_path,
        ]

        run_ffmpeg_command(args)
        final_duration = get_media_duration(output_path)
        logger.info(f"[AudioMixer] Master audio successfully generated: {output_path} (Duration: {final_duration:.1f}s)")
        return output_path
