import os
import shutil
import subprocess
import json
import logging
import re
from typing import List, Optional

def setup_logger(name: str = 'TOOLTRUYENAUDIO', level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(level)
        handler = logging.StreamHandler()
        handler.setLevel(level)
        formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] [%(name)s] %(message)s',
            datefmt='%H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger

logger = setup_logger('TOOLTRUYENAUDIO.ffmpeg')

def get_ffmpeg_exe() -> str:
    system_ffmpeg = shutil.which('ffmpeg')
    if system_ffmpeg:
        return system_ffmpeg
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception as e:
        logger.error(f'Failed to locate ffmpeg: {e}')
        raise RuntimeError('FFmpeg executable not found! Please install ffmpeg or imageio-ffmpeg.')

def run_ffmpeg_command(args: List[str], check: bool = True) -> subprocess.CompletedProcess:
    ffmpeg_bin = get_ffmpeg_exe()
    cmd = [ffmpeg_bin] + args
    cmd_str = ' '.join(cmd)
    logger.debug(f'Running FFmpeg: {cmd_str}')
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if check and result.returncode != 0:
        logger.error(f'FFmpeg command failed with code {result.returncode}: {result.stderr[-500:]}')
        raise RuntimeError(f'FFmpeg failed: {result.stderr[-500:]}')
    return result

def get_media_duration(file_path: str) -> float:
    if not os.path.exists(file_path):
        return 0.0
    ffmpeg_bin = get_ffmpeg_exe()
    cmd = [ffmpeg_bin, '-i', file_path, '-f', 'null', '-']
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    match = re.search(r'Duration:\s*(\d+):(\d+):(\d+\.\d+)', res.stderr)
    if match:
        hours, mins, secs = match.groups()
        return int(hours) * 3600 + int(mins) * 60 + float(secs)
    return 0.0

def cut_audio_with_fadeout(input_path: str, output_path: str, duration_seconds: int = 240, fade_seconds: int = 3) -> str:
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    fade_start = max(0, duration_seconds - fade_seconds)
    filter_expr = f'afade=t=out:st={fade_start}:d={fade_seconds}'
    args = [
        '-y',
        '-t', str(duration_seconds),
        '-i', input_path,
        '-af', filter_expr,
        '-c:a', 'libmp3lame',
        '-b:a', '192k',
        output_path
    ]
    run_ffmpeg_command(args)
    logger.info(f'Cut audio exported to: {output_path} (Duration: {duration_seconds}s, Fade: {fade_seconds}s)')
    return output_path
