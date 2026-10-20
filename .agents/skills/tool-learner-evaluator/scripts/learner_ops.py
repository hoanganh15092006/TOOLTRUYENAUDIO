#!/usr/bin/env python3
"""
learner_ops.py - Utility CLI for the Self-Learning from Experience Loop.
Enables programmatic recording of traces, adding heuristics, and summary reports.
"""

import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[4]  # root of workspace: d:\TOOLTRUYENAUDIO
AGENTS_DIR = BASE_DIR / ".agents"
TRACES_FILE = AGENTS_DIR / "experience_memory" / "execution_traces.jsonl"
HEURISTICS_FILE = AGENTS_DIR / "experience_memory" / "learned_heuristics.md"
BENCHMARKS_FILE = AGENTS_DIR / "evals" / "benchmark_tests.json"
REGISTRY_FILE = AGENTS_DIR / "evals" / "tools_registry.json"


def record_trace(tool_name: str, retry_count: int, approach_and_fixes: str,
                 metrics: dict, reflection: dict):
    """
    Appends a standardized trace record to execution_traces.jsonl.
    Schema matches Phase 2 specifications:
      - timestamp
      - tool_name
      - retry_count
      - approach_and_fixes
      - metrics (runtime, data_size, etc.)
      - reflection (speed, heuristics, edge_cases, early_failures)
    """
    TRACES_FILE.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().isoformat()
    
    entry = {
        "timestamp": timestamp,
        "tool_name": tool_name,
        "retry_count": retry_count,
        "approach_and_fixes": approach_and_fixes,
        "metrics": metrics or {},
        "reflection": reflection or {}
    }
    
    with open(TRACES_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        
    print(f"✅ Đã ghi nhận Trace thành công: [{timestamp}] - {tool_name} (Retries: {retry_count})")
    return entry


def get_status():
    """Summarizes current state of the Self-Learning Loop."""
    traces_count = 0
    if TRACES_FILE.exists():
        with open(TRACES_FILE, "r", encoding="utf-8") as f:
            traces_count = sum(1 for line in f if line.strip())
            
    heuristics_count = 0
    if HEURISTICS_FILE.exists():
        with open(HEURISTICS_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip().startswith("- **[H-"):
                    heuristics_count += 1

    tools_count = 0
    if REGISTRY_FILE.exists():
        with open(REGISTRY_FILE, "r", encoding="utf-8") as f:
            try:
                reg = json.load(f)
                tools_count = len(reg.get("tools", []))
            except Exception:
                pass
                    
    print("=" * 65)
    print("🧠 BÁO CÁO TRẠNG THÁI SELF-LEARNING EXPERIENCE LOOP")
    print("=" * 65)
    print(f"📁 Thư mục lưu trữ: {AGENTS_DIR}")
    print(f"🛠️  Số tool đã đăng ký trong registry: {tools_count}")
    print(f"📊 Tổng số Execution Traces: {traces_count}")
    print(f"💡 Tổng số Heuristics tích lũy: {heuristics_count}")
    print(f"🎯 File benchmark: {BENCHMARKS_FILE.name}")
    print("=" * 65)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Learner Ops Utility")
    subparsers = parser.add_subparsers(dest="command")
    
    # Subcommand: status
    subparsers.add_parser("status", help="Xem báo cáo trạng thái hệ thống tự học")
    
    # Subcommand: record
    rec = subparsers.add_parser("record", help="Ghi nhận trace mới theo chuẩn")
    rec.add_argument("--tool", required=True, help="Tên tool vừa chạy")
    rec.add_argument("--retries", type=int, default=0, help="Số lần retry trước khi thành công")
    rec.add_argument("--fixes", required=True, help="Phương pháp và các bước sửa lỗi qua từng lần thử")
    rec.add_argument("--duration", type=float, default=0.0, help="Thời gian thực thi (giây)")
    rec.add_argument("--size", default="N/A", help="Kích thước dữ liệu xử lý")
    rec.add_argument("--speed", default="FAST", choices=["FAST", "MEDIUM", "SLOW"])
    rec.add_argument("--bottleneck", default="", help="Nguyên nhân gây chậm hoặc lỗi lần đầu")
    rec.add_argument("--heuristic", default="", help="Mẹo/Quy tắc rút ra")

    args = parser.parse_args()
    if args.command == "record":
        metrics = {"execution_time_seconds": args.duration, "data_processed_size": args.size}
        reflection = {
            "speed_rating": args.speed,
            "early_failure_causes": args.bottleneck,
            "heuristics_discovered": args.heuristic
        }
        record_trace(args.tool, args.retries, args.fixes, metrics, reflection)
    elif args.command == "status" or not args.command:
        get_status()
