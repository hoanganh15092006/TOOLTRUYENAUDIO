"""
synthesizer.py - High-volume chunked Vietnamese TTS using Edge-TTS with async batching.
"""

import os
import sys
import asyncio
import tempfile
import logging
from typing import List, Optional

logger = logging.getLogger("TOOLTRUYENAUDIO.tts")


class TTSEngine:
    """
    Extensible TTS Engine. Supports Edge-TTS with multi-chunk parallel/serial
    synthesis for long-form stories (>30 minutes) without timeouts.
    """

    def __init__(
        self,
        voice: str = "vi-VN-HoaiMyNeural",
        rate: str = "+0%",
        pitch: str = "+0Hz",
    ):
        self.voice = voice
        self.rate = rate
        self.pitch = pitch

    def _split_text_into_chunks(self, text: str, max_chars: int = 1500) -> List[str]:
        """Splits long text by paragraph or sentence boundaries below max_chars."""
        paragraphs = text.split("\n")
        chunks = []
        current = []
        current_len = 0

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            if current_len + len(para) > max_chars:
                if current:
                    chunks.append("\n".join(current))
                    current = []
                    current_len = 0
            # If a single paragraph is longer than max_chars, split by sentences
            if len(para) > max_chars:
                import re
                sentences = re.split(r"(?<=[.?!…])\s+", para)
                sub_current = []
                sub_len = 0
                for s in sentences:
                    if sub_len + len(s) > max_chars:
                        if sub_current:
                            chunks.append(" ".join(sub_current))
                            sub_current = []
                            sub_len = 0
                    sub_current.append(s)
                    sub_len += len(s)
                if sub_current:
                    chunks.append(" ".join(sub_current))
            else:
                current.append(para)
                current_len += len(para)

        if current:
            chunks.append("\n".join(current))

        return [c for c in chunks if c.strip()]

    async def _synthesize_chunk_async(self, text: str, output_path: str) -> bool:
        """Synthesizes a single chunk using edge-tts Communicate."""
        import edge_tts
        max_retries = 3
        for attempt in range(1, max_retries + 1):
            try:
                communicate = edge_tts.Communicate(
                    text=text,
                    voice=self.voice,
                    rate=self.rate,
                    pitch=self.pitch,
                )
                await communicate.save(output_path)
                if os.path.exists(output_path) and os.path.getsize(output_path) > 500:
                    return True
            except Exception as e:
                logger.warning(f"[TTS] Chunk synthesis attempt {attempt} failed: {e}")
                await asyncio.sleep(1.5)
        return False

    def synthesize(self, text: str, output_path: str) -> str:
        """
        Synthesizes the complete script to output_path.
        Automatically chunks text and merges audio clips seamlessly.
        """
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        chunks = self._split_text_into_chunks(text)
        logger.info(f"[TTS] Split script into {len(chunks)} chunks for voice '{self.voice}'")

        temp_dir = tempfile.mkdtemp(prefix="tts_chunks_")
        temp_files: List[str] = []

        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            for idx, chunk in enumerate(chunks, start=1):
                chunk_file = os.path.join(temp_dir, f"chunk_{idx:04d}.mp3")
                logger.info(f"[TTS] Synthesizing chunk {idx}/{len(chunks)} ({len(chunk.split())} words)...")
                success = loop.run_until_complete(self._synthesize_chunk_async(chunk, chunk_file))
                if not success or not os.path.exists(chunk_file):
                    raise RuntimeError(f"Failed to synthesize TTS chunk {idx}")
                temp_files.append(chunk_file)

            loop.close()

            # Concatenate chunks using ffmpeg concat demuxer
            concat_list_file = os.path.join(temp_dir, "concat_list.txt")
            with open(concat_list_file, "w", encoding="utf-8") as f:
                for tf in temp_files:
                    norm_path = tf.replace("\\", "/")
                    f.write(f"file '{norm_path}'\n")

            from src.utils.ffmpeg_utils import run_ffmpeg_command
            concat_args = [
                "-y",
                "-f", "concat",
                "-safe", "0",
                "-i", concat_list_file,
                "-c", "copy",
                output_path,
            ]
            run_ffmpeg_command(concat_args)
            logger.info(f"[TTS] Master voice synthesis complete: {output_path} ({os.path.getsize(output_path):,} bytes)")
            return output_path

        finally:
            # Clean up temp files
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
