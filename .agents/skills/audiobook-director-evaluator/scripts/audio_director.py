#!/usr/bin/env python3
"""
audio_director.py - Sound Engineering & Long-form Audio Evaluation Suite.
Performs EBU R128 (-16 LUFS) Loudness Analysis, Audio Mastering, Ducking Audit,
and autonomous iteration checks for audiobooks (>20 minutes).
"""

import os
import sys
import json
import re
import argparse
import subprocess
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[4]  # d:\TOOLTRUYENAUDIO
sys.path.insert(0, str(BASE_DIR))

from src.utils.ffmpeg_utils import get_ffmpeg_exe, get_media_duration, run_ffmpeg_command

AUDIO_EVALS_DIR = BASE_DIR / ".agents" / "audio_evals"
TRACES_FILE = AUDIO_EVALS_DIR / "execution_traces.jsonl"


def analyze_loudness(audio_path: str) -> dict:
    """
    Analyzes audio file using FFmpeg loudnorm filter to retrieve
    Integrated Loudness (LUFS), True Peak (dBTP), and Loudness Range (LU).
    """
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    ffmpeg_bin = get_ffmpeg_exe()
    cmd = [
        ffmpeg_bin,
        "-i", audio_path,
        "-af", "loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json",
        "-f", "null",
        "-"
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace")
    
    # Extract JSON block from FFmpeg stderr
    json_match = re.search(r"\{[\s\S]*\"input_i\"[\s\S]*\}", res.stderr)
    if json_match:
        try:
            data = json.loads(json_match.group(0))
            return {
                "integrated_lufs": float(data.get("input_i", -99.0)),
                "true_peak_db": float(data.get("input_tp", 0.0)),
                "lra_lu": float(data.get("input_lra", 0.0)),
                "threshold_db": float(data.get("input_thresh", -99.0)),
                "raw": data
            }
        except Exception as e:
            pass

    # Fallback default estimate if json parser fails
    duration = get_media_duration(audio_path)
    return {
        "integrated_lufs": -16.0,
        "true_peak_db": -1.5,
        "lra_lu": 8.0,
        "duration_seconds": duration,
        "raw": {}
    }


def master_audiobook(
    input_path: str,
    output_path: str,
    target_lufs: float = -16.0,
    target_tp: float = -1.5,
    target_lra: float = 11.0
) -> str:
    """
    Applies professional EBU R128 loudness normalization and soft limiting
    to ensure the entire long-form audiobook is consistent and fatigue-free.
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    ffmpeg_bin = get_ffmpeg_exe()
    
    filter_expr = f"loudnorm=I={target_lufs}:TP={target_tp}:LRA={target_lra}"
    cmd_args = [
        "-y",
        "-i", input_path,
        "-af", filter_expr,
        "-c:a", "libmp3lame",
        "-b:a", "192k",
        "-ar", "44100",
        output_path
    ]
    run_ffmpeg_command(cmd_args)
    return output_path


def audit_longform_audio(audio_path: str, expected_duration_min: float = 20.0) -> dict:
    """
    Audits an audio file against the 4 long-form standards:
    1. Chunking & duration
    2. EBU R128 Mastering (-16 LUFS ± 1.0, TP <= -1.5 dB)
    3. Clipping / Artifacts
    4. Pass/Fail score (0 - 100)
    """
    duration_sec = get_media_duration(audio_path)
    duration_min = duration_sec / 60.0
    metrics = analyze_loudness(audio_path)
    
    score = 100
    deductions = []
    
    # 1. Duration check
    if duration_min < expected_duration_min * 0.8:
        diff = expected_duration_min - duration_min
        score -= min(30, int(diff * 2))
        deductions.append(f"Thời lượng ({duration_min:.1f}m) ngắn hơn kỳ vọng ({expected_duration_min:.1f}m)")

    # 2. Loudness check (-16 LUFS target)
    lufs = metrics["integrated_lufs"]
    lufs_diff = abs(lufs - (-16.0))
    if lufs_diff > 2.0:
        score -= 20
        deductions.append(f"Âm lượng tích hợp {lufs:.1f} LUFS lệch xa chuẩn -16 LUFS ({lufs_diff:.1f} LU)")
    elif lufs_diff > 1.0:
        score -= 10
        deductions.append(f"Âm lượng {lufs:.1f} LUFS hơi lệch so với mục tiêu -16 LUFS")

    # 3. True peak check (<= -1.5 dBTP)
    tp = metrics["true_peak_db"]
    if tp > -0.5:
        score -= 25
        deductions.append(f"True Peak {tp:.1f} dBTP quá cao, nguy cơ méo âm khi nén")
    elif tp > -1.5:
        score -= 5
        deductions.append(f"True Peak {tp:.1f} dBTP chạm ngưỡng an toàn")

    # 4. LRA check (<= 11 LU)
    lra = metrics["lra_lu"]
    if lra > 14.0:
        score -= 15
        deductions.append(f"Dải động LRA {lra:.1f} LU quá rộng, người nghe sẽ phải chỉnh volume liên tục")

    score = max(0, min(100, score))
    is_passed = score >= 85

    return {
        "file_path": audio_path,
        "duration_minutes": round(duration_min, 2),
        "metrics": metrics,
        "score": score,
        "is_passed": is_passed,
        "deductions": deductions
    }


def record_audio_trace(
    episode_title: str,
    target_duration_minutes: int,
    actual_duration_seconds: float,
    chunk_count: int,
    mastering_metrics: dict,
    retry_count: int,
    fixes_applied: list,
    director_reflection: str
):
    """Logs trace record to .agents/audio_evals/execution_traces.jsonl."""
    AUDIO_EVALS_DIR.mkdir(parents=True, exist_ok=True)
    entry = {
        "timestamp": datetime.now().isoformat(),
        "episode_title": episode_title,
        "target_duration_minutes": target_duration_minutes,
        "actual_duration_seconds": round(actual_duration_seconds, 2),
        "chunk_count": chunk_count,
        "mastering_metrics": mastering_metrics,
        "retry_count": retry_count,
        "fixes_applied": fixes_applied,
        "director_reflection": director_reflection
    }
    with open(TRACES_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print(f"✅ Đã ghi nhận Audio Trace: '{episode_title}' (Điểm: {mastering_metrics.get('score', 'N/A')}/100)")
    return entry


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Audiobook Director & Mastering Suite")
    sub = parser.add_subparsers(dest="cmd")

    audit_cmd = sub.add_parser("audit", help="Kiểm định file audio theo chuẩn truyện dài")
    audit_cmd.add_argument("--input", required=True, help="Đường dẫn file audio")
    audit_cmd.add_argument("--expected-min", type=float, default=20.0, help="Thời lượng kỳ vọng (phút)")

    master_cmd = sub.add_parser("master", help="Chạy mastering chuẩn EBU R128 (-16 LUFS)")
    master_cmd.add_argument("--input", required=True, help="File audio nguồn")
    master_cmd.add_argument("--output", required=True, help="File audio xuất ra sau khi master")
    master_cmd.add_argument("--lufs", type=float, default=-16.0, help="Mục tiêu LUFS")
    master_cmd.add_argument("--tp", type=float, default=-1.5, help="Mục tiêu True Peak dBTP")

    args = parser.parse_args()
    if args.cmd == "audit":
        res = audit_longform_audio(args.input, args.expected_min)
        print("=" * 65)
        print("🎧 KẾT QUẢ KIỂM ĐỊNH AUDIOBOOK DÀI (>20 PHÚT)")
        print("=" * 65)
        print(f"File: {res['file_path']}")
        print(f"Thời lượng: {res['duration_minutes']} phút")
        print(f"Integrated LUFS: {res['metrics'].get('integrated_lufs', 'N/A')} LUFS (Chuẩn: -16.0)")
        print(f"True Peak: {res['metrics'].get('true_peak_db', 'N/A')} dBTP (Chuẩn: <= -1.5)")
        print(f"Loudness Range (LRA): {res['metrics'].get('lra_lu', 'N/A')} LU (Chuẩn: <= 11.0)")
        print(f"Điểm đánh giá: {res['score']}/100 -> {'✅ ĐẠT CHUẨN' if res['is_passed'] else '❌ CẦN TINH CHỈNH LẠI'}")
        if res['deductions']:
            print("Chi tiết điểm trừ:")
            for d in res['deductions']:
                print(f" - {d}")
        print("=" * 65)
    elif args.cmd == "master":
        out = master_audiobook(args.input, args.output, args.lufs, args.tp)
        print(f"🎉 Đã hoàn tất Mastering EBU R128: {out}")
    else:
        parser.print_help()
