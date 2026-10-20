#!/usr/bin/env python3
"""
main.py - Central CLI Interactive Menu & Full Pipeline Orchestrator for TOOLTRUYENAUDIO.
Automates end-to-end production of Oneshot Audiobooks (>30m) for YouTube and 4-minute teaser for TikTok.
"""

import os
import sys
import yaml
import argparse
import logging
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Ensure root directory is on PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.utils.logger import setup_logger
from src.script_gen import StoryScriptGenerator
from src.tts_engine import TTSEngine, AudioMixer
from src.media_fetcher import ImageGenerator, VideoFetcher
from src.video_renderer import YouTubeRenderer, TikTokRenderer
from src.uploaders import YouTubeUploader, TikTokUploader

logger = setup_logger("TOOLTRUYENAUDIO.main")
load_dotenv()


def load_config(config_path: str = "config/config.yaml") -> Dict[str, Any]:
    """Loads configuration with sensible fallbacks."""
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            logger.warning(f"Failed to read {config_path}: {e}")
    return {}


def interactive_menu(cfg: Dict[str, Any]) -> Dict[str, Any]:
    """Renders interactive CLI questionnaire in Vietnamese."""
    print("\n" + "=" * 75)
    print("   🎧 HỆ THỐNG TỰ ĐỘNG SẢN XUẤT TRUYỆN AUDIO ONESHOT (YOUTUBE + TIKTOK)")
    print("=" * 75)

    default_channel = cfg.get("channel", {}).get("youtube_channel_name", "Góc Truyện Audio")
    default_topic = cfg.get("channel", {}).get("default_topic", "Trọng sinh báo thù giới thượng lưu")
    default_duration = cfg.get("script", {}).get("target_duration_minutes", 35)

    # 1. Tên kênh YouTube
    print(f"\n[1] TÊN KÊNH YOUTUBE CỦA BẠN")
    val = input(f"   Nhập tên kênh (Mặc định: '{default_channel}'): ").strip()
    channel_name = val if val else default_channel

    # 2. Chủ đề / Ý tưởng truyện
    print(f"\n[2] CHỦ ĐỀ / Ý TƯỞNG TRUYỆN (VD: Tổng tài, kinh dị đêm khuya, trọng sinh, ngoại tình...)")
    val = input(f"   Nhập chủ đề (Mặc định: '{default_topic}'): ").strip()
    story_topic = val if val else default_topic

    # 3. Tên truyện
    print(f"\n[3] TÊN TRUYỆN (STORY TITLE)")
    val = input("   Nhập tên truyện cụ thể (hoặc nhấn [ENTER] để AI tự đặt tên siêu viral): ").strip()
    story_title = val if val else None

    # 4. Thời lượng mục tiêu
    print(f"\n[4] THỜI LƯỢNG MỤC TIÊU CHO AUDIO YOUTUBE")
    val = input(f"   Nhập số phút mong muốn (VD: 30, 35, 45, 60 - Mặc định: {default_duration}): ").strip()
    try:
        duration_minutes = int(val) if val else default_duration
    except ValueError:
        duration_minutes = default_duration

    # 5. Kiểu cái kết
    print(f"\n[5] KIỂU CÁI KẾT (ENDING TYPE)")
    print("   [1] Có hậu (Happy Ending - HE) - Nhân quả báo ứng, hạnh phúc trọn vẹn")
    print("   [2] Không có hậu / Bi kịch (Sad Ending - SE) - Day dứt, chia ly, xót xa")
    print("   [3] Hờ hững / Kết mở (Open Ending - OE) - Buông bỏ, lạnh nhạt, câu hỏi mở")
    val = input("   Chọn [1/2/3] (Mặc định 1): ").strip()
    ending_map = {"1": "happy", "2": "sad", "3": "open"}
    ending_type = ending_map.get(val, "happy")

    # 6. Chế độ Ảnh nền YouTube
    print(f"\n[6] ẢNH NỀN YOUTUBE (16:9 - 1920x1080)")
    print("   [1] Tự chọn file ảnh có sẵn trên máy (manual)")
    print("   [2] Để Tool tự tạo ảnh nền AI khớp 100% nội dung truyện (auto_ai)")
    val = input("   Chọn [1/2] (Mặc định 2): ").strip()
    bg_image_mode = "manual" if val == "1" else "auto_ai"
    manual_image_path = None
    if bg_image_mode == "manual":
        manual_image_path = input("   Nhập đường dẫn file ảnh (.jpg/.png): ").strip()

    # 7. Loại Video nền TikTok (4 phút)
    print(f"\n[7] LOẠI VIDEO NỀN TIKTOK (Giữ chân người xem)")
    print("   [1] Gameplay (Subway Surfers, Minecraft Parkour, GTA V stunt)")
    print("   [2] Oddly Satisfying (Cắt xà phòng, ép thủy lực, nặn đất sét, làm bánh)")
    val = input("   Chọn [1/2] (Mặc định 1): ").strip()
    tiktok_bg_category = "satisfying" if val == "2" else "gameplay"

    # 8. Chế độ thực thi
    print(f"\n[8] CHẾ ĐỘ THỰC THI")
    print("   [1] Tự Động Hoàn Toàn (Viết truyện -> Đọc Audio -> Render Video -> ĐĂNG BÀI)")
    print("   [2] Chỉ Sản Xuất Video (Tạo YouTube Full + TikTok Teaser, KHÔNG đăng bài)")
    print("   [3] Chỉ tạo Kịch Bản & File Master Audio (mp3)")
    val = input("   Chọn [1/2/3] (Mặc định 1): ").strip()
    pipeline_mode = val if val in ["1", "2", "3"] else "1"

    return {
        "channel_name": channel_name,
        "story_topic": story_topic,
        "story_title": story_title,
        "duration_minutes": duration_minutes,
        "ending_type": ending_type,
        "bg_image_mode": bg_image_mode,
        "manual_image_path": manual_image_path,
        "tiktok_bg_category": tiktok_bg_category,
        "pipeline_mode": pipeline_mode,
    }


def run_full_pipeline(
    channel_name: str,
    story_topic: str,
    story_title: Optional[str] = None,
    duration_minutes: int = 35,
    ending_type: str = "happy",
    bg_image_mode: str = "auto_ai",
    manual_image_path: Optional[str] = None,
    tiktok_bg_category: str = "gameplay",
    skip_upload: bool = False,
    only_audio: bool = False,
    headless: bool = False,
    voice: str = "vi-VN-HoaiMyNeural",
) -> Dict[str, Any]:
    """
    Executes the complete production and multi-platform publishing pipeline.
    """
    print("\n" + "=" * 75)
    print(f"🚀 BẮT ĐẦU PIPELINE SẢN XUẤT TRUYỆN AUDIO ONESHOT")
    print(f"   Kênh YouTube : {channel_name}")
    print(f"   Chủ đề       : {story_topic}")
    print(f"   Thời lượng   : {duration_minutes} phút (~{duration_minutes * 150} từ)")
    print(f"   Cái kết      : {ending_type.upper()}")
    print("=" * 75 + "\n")

    # -------------------------------------------------------------------------
    # STAGE 1: TẠO KỊCH BẢN ONESHOT (Gemini Multi-Part Generation)
    # -------------------------------------------------------------------------
    logger.info(">>> [GIAI ĐOẠN 1/5] Sáng tác kịch bản Oneshot chuyên sâu...")
    script_gen = StoryScriptGenerator()
    script_data = script_gen.generate_oneshot_script(
        topic=story_topic,
        title=story_title,
        target_duration_minutes=duration_minutes,
        ending_type=ending_type,
    )
    final_title = script_data["title"]
    logger.info(f"[*] Tiêu đề truyện: '{final_title}' ({script_data['total_words']} từ)")

    # -------------------------------------------------------------------------
    # STAGE 2: VIETNAMESE TTS & AUDIO MIXER (Audio Ducking BGM)
    # -------------------------------------------------------------------------
    logger.info(">>> [GIAI ĐOẠN 2/5] Chuyển thể giọng đọc AI (Edge-TTS) & Trộn BGM...")
    tts_engine = TTSEngine(voice=voice)
    os.makedirs("output", exist_ok=True)
    raw_voice_path = "output/temp_raw_voice.mp3"
    master_audio_path = "output/master_audio.mp3"

    tts_engine.synthesize(script_data["full_script"], raw_voice_path)

    audio_mixer = AudioMixer(bgm_dir="assets/bgm", default_bgm_volume_db=-24.0)
    audio_mixer.mix(voice_path=raw_voice_path, output_path=master_audio_path)
    logger.info(f"[*] File Master Audio sẵn sàng: '{master_audio_path}'")

    if only_audio:
        print("\n[SUCCESS] Pipeline kết thúc ở chế độ chỉ tạo Audio. File: output/master_audio.mp3\n")
        return {"title": final_title, "audio": master_audio_path, "master_audio": master_audio_path}

    # -------------------------------------------------------------------------
    # STAGE 3: RENDER VIDEO YOUTUBE (Full Oneshot > 30 mins)
    # -------------------------------------------------------------------------
    logger.info(">>> [GIAI ĐOẠN 3/5] Chuẩn bị ảnh nền & Render Video YouTube 16:9...")
    img_gen = ImageGenerator(output_dir="assets/bg_images")
    yt_bg_image = img_gen.get_youtube_background(
        mode=bg_image_mode,
        manual_path=manual_image_path,
        topic=story_topic,
        title=final_title,
    )

    yt_renderer = YouTubeRenderer(output_path="output/youtube_full.mp4")
    youtube_video_path = yt_renderer.render(image_path=yt_bg_image, audio_path=master_audio_path)
    logger.info(f"[*] Video YouTube xuất bản xong: '{youtube_video_path}'")

    # -------------------------------------------------------------------------
    # STAGE 4: TẢI VIDEO NỀN & RENDER VIDEO TIKTOK (4 phút kèm Overlay)
    # -------------------------------------------------------------------------
    logger.info(">>> [GIAI ĐOẠN 4/5] Chuẩn bị Video nền 9:16 & Render TikTok Teaser (4 phút)...")
    video_fetcher = VideoFetcher(output_dir="assets/bg_videos")
    bg_video_path = video_fetcher.fetch_and_prepare(
        category=tiktok_bg_category,
        target_duration_seconds=240,
        output_filename="prepared_bg_4min.mp4",
    )

    tiktok_renderer = TikTokRenderer(output_path="output/tiktok_teaser.mp4", fonts_dir="assets/fonts")
    tiktok_video_path = tiktok_renderer.render(
        bg_video_path=bg_video_path,
        master_audio_path=master_audio_path,
        channel_name=channel_name,
        story_title=final_title,
        duration_seconds=240,
        fade_seconds=3,
    )
    logger.info(f"[*] Video TikTok Teaser 4 phút sẵn sàng: '{tiktok_video_path}'")

    # -------------------------------------------------------------------------
    # STAGE 5: TỰ ĐỘNG ĐĂNG BÀI (YOUTUBE & TIKTOK)
    # -------------------------------------------------------------------------
    if skip_upload:
        logger.info(">>> [GIAI ĐOẠN 5/5] Bỏ qua đăng bài theo yêu cầu.")
    else:
        logger.info(">>> [GIAI ĐOẠN 5/5] Tiến hành tự động đăng video lên YouTube & TikTok...")

        # 1. Đăng YouTube
        try:
            yt_uploader = YouTubeUploader()
            yt_uploader.upload(
                video_path=youtube_video_path,
                story_title=final_title,
                channel_name=channel_name,
                topic=story_topic,
                duration_minutes=duration_minutes,
                thumbnail_path=yt_bg_image,
                privacy_status="public",
                summary=script_data.get("cliffhanger_snippet"),
            )
        except Exception as yt_err:
            logger.error(f"[Upload] YouTube upload error: {yt_err}")

        # 2. Đăng TikTok
        try:
            tk_uploader = TikTokUploader(headless=headless)
            tk_uploader.upload(
                video_path=tiktok_video_path,
                story_title=final_title,
                channel_name=channel_name,
                duration_minutes=duration_minutes,
                auto_post=True,
            )
        except Exception as tk_err:
            logger.error(f"[Upload] TikTok upload error: {tk_err}")

    print("\n" + "=" * 75)
    print("🎉 HOÀN THÀNH TOÀN BỘ QUY TRÌNH!")
    print(f"   1. Tiêu đề      : {final_title}")
    print(f"   2. Master Audio : {master_audio_path}")
    print(f"   3. YouTube Full : {youtube_video_path}")
    print(f"   4. TikTok Teaser: {tiktok_video_path}")
    print("=" * 75 + "\n")

    return {
        "title": final_title,
        "master_audio": master_audio_path,
        "youtube_video": youtube_video_path,
        "tiktok_video": tiktok_video_path,
    }


def main():
    parser = argparse.ArgumentParser(description="TOOLTRUYENAUDIO - Automated Oneshot Audiobook Production")
    parser.add_argument("--auto", action="store_true", help="Run automatically without interactive prompts")
    parser.add_argument("--channel-name", help="YouTube Channel Name")
    parser.add_argument("--topic", help="Story Topic / Idea")
    parser.add_argument("--title", help="Explicit Story Title")
    parser.add_argument("--duration", type=int, default=35, help="Target duration in minutes (default 35)")
    parser.add_argument("--ending", choices=["happy", "sad", "open"], default="happy", help="Ending type")
    parser.add_argument("--bg-image-mode", choices=["auto_ai", "manual"], default="auto_ai")
    parser.add_argument("--manual-image", help="Path to manual background image")
    parser.add_argument("--tiktok-bg", choices=["gameplay", "satisfying"], default="gameplay")
    parser.add_argument("--skip-upload", action="store_true", help="Skip YouTube and TikTok upload")
    parser.add_argument("--only-audio", action="store_true", help="Stop after generating master audio")
    parser.add_argument("--headless", action="store_true", help="Run browser upload headlessly")
    parser.add_argument("--voice", default="vi-VN-HoaiMyNeural", help="Edge-TTS Voice")

    args = parser.parse_args()
    cfg = load_config()

    if not args.auto and len(sys.argv) == 1:
        # Launch Interactive Terminal Menu
        menu_choices = interactive_menu(cfg)
        pipeline_mode = menu_choices["pipeline_mode"]

        run_full_pipeline(
            channel_name=menu_choices["channel_name"],
            story_topic=menu_choices["story_topic"],
            story_title=menu_choices["story_title"],
            duration_minutes=menu_choices["duration_minutes"],
            ending_type=menu_choices["ending_type"],
            bg_image_mode=menu_choices["bg_image_mode"],
            manual_image_path=menu_choices["manual_image_path"],
            tiktok_bg_category=menu_choices["tiktok_bg_category"],
            skip_upload=(pipeline_mode == "2"),
            only_audio=(pipeline_mode == "3"),
            headless=False,
            voice=cfg.get("tts", {}).get("voice", "vi-VN-HoaiMyNeural"),
        )
    else:
        # CLI Argument Execution
        channel_name = args.channel_name or cfg.get("channel", {}).get("youtube_channel_name", "Góc Truyện Audio")
        story_topic = args.topic or cfg.get("channel", {}).get("default_topic", "Trọng sinh báo thù giới thượng lưu")

        run_full_pipeline(
            channel_name=channel_name,
            story_topic=story_topic,
            story_title=args.title,
            duration_minutes=args.duration,
            ending_type=args.ending,
            bg_image_mode=args.bg_image_mode,
            manual_image_path=args.manual_image,
            tiktok_bg_category=args.tiktok_bg,
            skip_upload=args.skip_upload,
            only_audio=args.only_audio,
            headless=args.headless,
            voice=args.voice,
        )


if __name__ == "__main__":
    main()
