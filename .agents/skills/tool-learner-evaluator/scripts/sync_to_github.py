#!/usr/bin/env python3
"""
sync_to_github.py - Automates Devlog creation, TOC updates, git staging, committing, and pushing to GitHub.
Includes conflict resolution with `git pull --rebase` and safe credential checks.
"""

import os
import sys
import subprocess
import argparse
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[4]  # d:\TOOLTRUYENAUDIO
DEVLOGS_DIR = BASE_DIR / "docs" / "devlogs"
DEVLOGS_README = DEVLOGS_DIR / "README.md"
SENSITIVE_PATTERNS = [".env", "client_secrets.json", "youtube_token.json", "cookies.txt"]


def run_git_cmd(cmd_list, check=True):
    """Executes a git command and returns stdout and exitcode."""
    res = subprocess.run(cmd_list, cwd=str(BASE_DIR), capture_output=True, text=True, encoding="utf-8")
    if check and res.returncode != 0:
        raise RuntimeError(f"Git command failed: {' '.join(cmd_list)}\nStderr: {res.stderr}\nStdout: {res.stdout}")
    return res


def get_current_branch() -> str:
    """Returns the current active branch name."""
    res = run_git_cmd(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    return res.stdout.strip() or "main"


def verify_no_sensitive_files():
    """Double checks that sensitive files are NOT staged for commit."""
    res = run_git_cmd(["git", "status", "--porcelain"])
    staged_or_untracked = res.stdout.splitlines()
    for line in staged_or_untracked:
        for sensitive in SENSITIVE_PATTERNS:
            if sensitive in line:
                raise ValueError(f"⚠️ CẢNH BÁO NGUY HIỂM: Phát hiện file nhạy cảm '{sensitive}' trong git status: {line}")
    print("🔒 Đã kiểm tra an toàn: Không có file nhạy cảm (.env, credentials) nào bị stage.")


def create_devlog(tool_name: str, context: str, heuristics: str, changelog: str, benchmark: str) -> Path:
    """Generates a standardized Devlog markdown file with 4 sections."""
    DEVLOGS_DIR.mkdir(parents=True, exist_ok=True)
    today_str = datetime.now().strftime("%Y-%m-%d")
    devlog_path = DEVLOGS_DIR / f"devlog_{today_str}.md"
    
    # If already exists for today, append or create with topic suffix
    if devlog_path.exists():
        timestamp_slug = datetime.now().strftime("%H%M%S")
        devlog_path = DEVLOGS_DIR / f"devlog_{today_str}_{timestamp_slug}.md"

    content = f"""# Devlog: {today_str} - Tiến hóa và Tối ưu {tool_name}

## 1. Bối cảnh & Vấn đề thực tế (Context)
{context}

## 2. Bài học rút ra (Learned Heuristics)
{heuristics}

## 3. Thay đổi kỹ thuật (Changelog & Technical Improvements)
{changelog}

## 4. Benchmark & Hiệu năng
{benchmark}
"""
    with open(devlog_path, "w", encoding="utf-8") as f:
        f.write(content)
        
    print(f"📝 Đã tạo file Devlog thành công: {devlog_path.name}")
    update_devlogs_index(devlog_path.name, f"Tiến hóa & nâng cấp {tool_name}", tool_name)
    return devlog_path


def update_devlogs_index(filename: str, title: str, tool_name: str):
    """Updates docs/devlogs/README.md table with the new entry."""
    if not DEVLOGS_README.exists():
        return
        
    date_str = filename.replace("devlog_", "").replace(".md", "")
    new_row = f"| [{date_str}](./{filename}) | {title} | {tool_name} | Cycle (Auto) | Đã Sync |\n"
    
    with open(DEVLOGS_README, "r", encoding="utf-8") as f:
        content = f.read()

    # Append to table if not already present
    if filename not in content:
        content += new_row
        with open(DEVLOGS_README, "w", encoding="utf-8") as f:
            f.write(content)
        print("📑 Đã cập nhật mục lục tại docs/devlogs/README.md")


def sync_to_github(tool_name: str, extra_paths: list = None, message_override: str = None) -> bool:
    """Stages files, commits, and pushes to remote with auto-rebase fallback."""
    branch = get_current_branch()
    today_str = datetime.now().strftime("%Y-%m-%d")
    commit_msg = message_override or f"feat(tool-evolution): upgrade {tool_name} and update devlog [{today_str}]"
    
    verify_no_sensitive_files()
    
    # 1. Git add
    stage_targets = ["docs/devlogs/", ".agents/", "AGENTS.md"]
    if extra_paths:
        stage_targets.extend(extra_paths)
        
    print(f"📦 Đang stage các thư mục/tệp: {', '.join(stage_targets)}...")
    for target in stage_targets:
        if (BASE_DIR / target).exists():
            run_git_cmd(["git", "add", target])
            
    # Check if there is anything to commit
    res_status = run_git_cmd(["git", "status", "--porcelain"])
    if not res_status.stdout.strip():
        print("ℹ️ Không có thay đổi mới nào cần commit.")
        return True

    # 2. Git commit
    print(f"💬 Đang commit với thông điệp: \"{commit_msg}\"...")
    run_git_cmd(["git", "commit", "-m", commit_msg])
    
    # 3. Git push with pull --rebase on conflict
    print(f"🚀 Đang đẩy code lên remote GitHub (origin/{branch})...")
    push_res = run_git_cmd(["git", "push", "origin", branch], check=False)
    
    if push_res.returncode != 0:
        print("⚠️ Push bị từ chối do có thay đổi mới trên remote. Tiến hành 'git pull --rebase origin {branch}'...")
        rebase_res = run_git_cmd(["git", "pull", "--rebase", "origin", branch], check=False)
        if rebase_res.returncode != 0:
            print(f"❌ Xung đột (Conflict) khi rebase:\n{rebase_res.stderr}\nVui lòng kiểm tra thủ công.")
            return False
        # Retry push after rebase
        push_retry = run_git_cmd(["git", "push", "origin", branch])
        if push_retry.returncode != 0:
            print(f"❌ Lỗi khi push lại sau rebase: {push_retry.stderr}")
            return False

    # Get latest commit hash
    rev_res = run_git_cmd(["git", "rev-parse", "--short", "HEAD"])
    commit_hash = rev_res.stdout.strip()
    remote_res = run_git_cmd(["git", "remote", "get-url", "origin"])
    remote_url = remote_res.stdout.strip().replace(".git", "")
    
    print("=" * 65)
    print("🎉 ĐỒNG BỘ GITHUB THÀNH CÔNG!")
    print(f"🔗 Commit Hash : {commit_hash}")
    print(f"🌿 Nhánh       : {branch}")
    print(f"🌐 Repository  : {remote_url}")
    print(f"📌 Link commit : {remote_url}/commit/{commit_hash}")
    print("=" * 65)
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Git Auto-Sync & Devlog Generator")
    parser.add_argument("--tool", default="system-evolution", help="Tên tool vừa được tối ưu")
    parser.add_argument("--context", default="Tự động kiểm định và cập nhật cấu trúc hệ thống.", help="Nội dung bối cảnh")
    parser.add_argument("--heuristics", default="Áp dụng quy tắc ngón tay cái và autonomous loop.", help="Bài học rút ra")
    parser.add_argument("--changelog", default="Cập nhật cấu trúc tri thức và registry.", help="Thay đổi kỹ thuật")
    parser.add_argument("--benchmark", default="Chạy toàn bộ unit tests đạt chuẩn.", help="Kết quả benchmark")
    parser.add_argument("--skip-devlog", action="store_true", help="Chỉ push git mà không sinh devlog mới")
    parser.add_argument("--add-path", action="append", default=[], help="File bổ sung cần git add")
    parser.add_argument("--message", default=None, help="Thông điệp commit tùy chỉnh")

    args = parser.parse_args()

    if not args.skip_devlog:
        create_devlog(args.tool, args.context, args.heuristics, args.changelog, args.benchmark)

    sync_to_github(args.tool, extra_paths=args.add_path, message_override=args.message)
