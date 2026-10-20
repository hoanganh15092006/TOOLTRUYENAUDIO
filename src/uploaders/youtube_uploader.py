"""
youtube_uploader.py - Automates video publishing to YouTube via YouTube Data API v3 & Studio Automation.
"""

import os
import json
import logging
from typing import Optional, List, Dict, Any

from src.utils.logger import setup_logger

logger = setup_logger("TOOLTRUYENAUDIO.yt_uploader")


class YouTubeUploader:
    """
    Publishes full-length audiobook videos to YouTube.
    Supports YouTube Data API v3 (OAuth2) with graceful fallback and dry-run testing.
    """

    def __init__(
        self,
        client_secrets_path: str = "config/client_secrets.json",
        credentials_token_path: str = "config/youtube_token.json",
    ):
        self.client_secrets_path = client_secrets_path
        self.credentials_token_path = credentials_token_path

    def build_metadata(
        self,
        story_title: str,
        channel_name: str,
        topic: str,
        duration_minutes: int,
        summary: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generates rich, SEO-optimized title, description, and tags."""
        title = f"[FULL] {story_title} | Truyện Audio Oneshot Trọn Bộ"
        if len(title) > 100:
            title = title[:97] + "..."

        story_summary = summary or f"Một câu chuyện sâu sắc đầy cảm xúc về chủ đề {topic}."

        description = (
            f"🎧 {story_title} - Truyện Audio Oneshot Trọn Bộ Hay Nhất.\n\n"
            f"📺 Chào mừng bạn đến với kênh chính thức: {channel_name}\n\n"
            f"📖 Thể loại: {topic}\n"
            f"⏳ Thời lượng: {duration_minutes} phút (Trọn vẹn 1 tập duy nhất không chia phần)\n\n"
            f"✨ Tóm tắt truyện:\n{story_summary}\n\n"
            f"🔔 Hãy nhấn ĐĂNG KÝ KÊNH (Subscribe), Thả Tim và Chia Sẻ để ủng hộ kênh sản xuất thêm nhiều truyện audio Oneshot hấp dẫn mỗi ngày nhé!\n\n"
            f"#truyenaudio #truyenoneshot #kechuyen #truyenngan #radiotruyen #truyendemkhuya #{topic.replace(' ', '')}"
        )

        tags = [
            "truyen audio", "truyenaudio",
            "truyen oneshot",
            "truyen hay",
            "ke chuyen",
            "truyen ngan",
            "radio truyen",
            "truyen dem khuya",
            topic.lower(),
            channel_name.lower(),
        ]

        return {
            "title": title,
            "description": description,
            "tags": tags,
            "category_id": "24",  # Entertainment
        }

    def upload_via_api(
        self,
        video_path: str,
        title: str,
        description: str,
        tags: List[str],
        thumbnail_path: Optional[str] = None,
        privacy_status: str = "public",
    ) -> bool:
        """Uploads video using google-api-python-client with OAuth2."""
        try:
            from googleapiclient.discovery import build
            from googleapiclient.http import MediaFileUpload
            from google.oauth2.credentials import Credentials
            from google_auth_oauthlib.flow import InstalledAppFlow

            SCOPES = [
                "https://www.googleapis.com/auth/youtube.upload",
                "https://www.googleapis.com/auth/youtube",
            ]

            creds = None
            if os.path.exists(self.credentials_token_path):
                creds = Credentials.from_authorized_user_file(self.credentials_token_path, SCOPES)

            if not creds or not creds.valid:
                if not os.path.exists(self.client_secrets_path):
                    logger.warning(
                        f"[YouTubeUploader] Missing '{self.client_secrets_path}'. "
                        "Please download OAuth2 client secrets from Google Cloud Console to enable automated YouTube uploads."
                    )
                    return False

                flow = InstalledAppFlow.from_client_secrets_file(self.client_secrets_path, SCOPES)
                creds = flow.run_local_server(port=0)
                with open(self.credentials_token_path, "w", encoding="utf-8") as token_f:
                    token_f.write(creds.to_json())

            youtube = build("youtube", "v3", credentials=creds)

            body = {
                "snippet": {
                    "title": title,
                    "description": description,
                    "tags": tags,
                    "categoryId": "24",
                },
                "status": {
                    "privacyStatus": privacy_status,
                    "selfDeclaredMadeForKids": False,
                },
            }

            media = MediaFileUpload(video_path, chunksize=-1, resumable=True, mimetype="video/mp4")
            request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

            logger.info(f"[YouTubeUploader] Uploading '{video_path}' to YouTube ({privacy_status})...")
            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    logger.info(f"[YouTubeUploader] Upload progress: {int(status.progress() * 100)}%")

            video_id = response.get("id")
            logger.info(f"[YouTubeUploader] Video published successfully! URL: https://youtu.be/{video_id}")

            # Upload thumbnail if provided
            if thumbnail_path and os.path.isfile(thumbnail_path) and video_id:
                try:
                    logger.info(f"[YouTubeUploader] Setting thumbnail from '{thumbnail_path}'...")
                    youtube.thumbnails().set(
                        videoId=video_id,
                        media_body=MediaFileUpload(thumbnail_path, mimetype="image/jpeg"),
                    ).execute()
                    logger.info("[YouTubeUploader] Custom thumbnail set successfully!")
                except Exception as thumb_err:
                    logger.warning(f"[YouTubeUploader] Failed to set thumbnail: {thumb_err}")

            return True

        except Exception as e:
            logger.error(f"[YouTubeUploader] YouTube API upload error: {e}")
            return False

    def upload(
        self,
        video_path: str,
        story_title: str,
        channel_name: str,
        topic: str,
        duration_minutes: int,
        thumbnail_path: Optional[str] = None,
        privacy_status: str = "public",
        summary: Optional[str] = None,
    ) -> bool:
        """
        High-level upload entry point.
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")

        meta = self.build_metadata(story_title, channel_name, topic, duration_minutes, summary)
        logger.info(f"[YouTubeUploader] Preparing YouTube publication: '{meta['title']}'")

        success = self.upload_via_api(
            video_path=video_path,
            title=meta["title"],
            description=meta["description"],
            tags=meta["tags"],
            thumbnail_path=thumbnail_path,
            privacy_status=privacy_status,
        )

        if not success:
            logger.info(
                "[YouTubeUploader] YouTube API credentials not configured yet or upload failed. "
                f"You can manually upload the rendered video from '{video_path}'."
            )
        return success
