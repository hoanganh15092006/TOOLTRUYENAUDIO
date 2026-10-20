"""
tiktok_uploader.py - Automates publishing 4-minute teaser videos to TikTok Studio.
Inherited and optimized from TOOLAFILATEVIDEOTIKTOK architecture.
"""

import os
import sys
import time
import logging
from typing import Optional

from playwright.sync_api import (
    sync_playwright,
    Page,
    Locator,
    TimeoutError as PlaywrightTimeoutError,
)

from src.utils.logger import setup_logger

logger = setup_logger("TOOLTRUYENAUDIO.tiktok_uploader")


def _find_file_input(page: Page) -> Optional[Locator]:
    """Locates video file input element across main page DOM and nested iframes."""
    selectors = [
        'input[type="file"][accept*="video"]',
        'input[type="file"]',
    ]
    for sel in selectors:
        try:
            loc = page.locator(sel)
            if loc.count() > 0:
                return loc.first
        except Exception:
            continue

    try:
        for frame in page.frames:
            for sel in selectors:
                try:
                    f_loc = frame.locator(sel)
                    if f_loc.count() > 0:
                        return f_loc.first
                except Exception:
                    continue
    except Exception:
        pass
    return None


def _is_login_page_or_prompt(page: Page) -> bool:
    """Checks if the page is currently at a login redirect."""
    try:
        current_url = page.url.lower()
        if any(term in current_url for term in ["/login", "passport", "signin", "redirect_url"]):
            return True
        login_btn = page.locator('button:has-text("Log in"), button:has-text("Đăng nhập"), a[href*="login"]')
        if login_btn.count() > 0:
            for i in range(login_btn.count()):
                if login_btn.nth(i).is_visible():
                    return True
    except Exception:
        pass
    return False


def _find_caption_element(page: Page, timeout_seconds: int = 30) -> Optional[Locator]:
    """Locates the caption text area."""
    caption_selectors = [
        'div[contenteditable="true"]',
        'div.notranslate[contenteditable="true"]',
        'div[class*="caption"] [contenteditable="true"]',
        'div[class*="editor"] [contenteditable="true"]',
        'div[role="combobox"][contenteditable="true"]',
        'textarea[placeholder*="caption" i]',
        'textarea[placeholder*="description" i]',
        'textarea',
    ]
    start = time.time()
    while time.time() - start < timeout_seconds:
        contexts = [page] + list(getattr(page, "frames", []))
        for ctx in contexts:
            for sel in caption_selectors:
                try:
                    loc = ctx.locator(sel)
                    if loc.count() > 0 and loc.first.is_visible():
                        return loc.first
                except Exception:
                    continue
        time.sleep(1.0)
    return None


def _find_bottom_action_button(page: Page, action: str = "post") -> Optional[Locator]:
    """Finds bottom Post or Save Draft button, avoiding top navigation buttons (y > 200)."""
    if action == "post":
        selectors = [
            'button[data-e2e="post_video_button"]',
            'div.btn-post button',
            'button.btn-post',
            'div[class*="btn-post"] button',
            'button:text-is("Post")',
            'button:text-is("Đăng")',
            'button:text-is("Publish")',
            'div[class*="button-group"] button:text-is("Post")',
            'div[class*="button-group"] button:text-is("Đăng")',
        ]
    else:
        selectors = [
            'button[data-e2e="save_draft_button"]',
            'button:text-is("Save draft")',
            'button:text-is("Lưu nháp")',
            'button:text-is("Lưu làm bản nháp")',
            'div[class*="button-group"] button:text-is("Save draft")',
            'div[class*="button-group"] button:text-is("Lưu nháp")',
        ]

    candidates = []
    contexts = [page] + list(getattr(page, "frames", []))
    for ctx in contexts:
        for sel in selectors:
            try:
                loc = ctx.locator(sel)
                for i in range(loc.count()):
                    btn = loc.nth(i)
                    if btn.is_visible():
                        box = btn.bounding_box()
                        y = box["y"] if box else 0
                        if y > 200:
                            candidates.append((y, btn))
            except Exception:
                continue

    if candidates:
        candidates.sort(key=lambda x: x[0], reverse=True)
        return candidates[0][1]

    for ctx in contexts:
        for sel in selectors:
            try:
                loc = ctx.locator(sel)
                if loc.count() > 0 and loc.first.is_visible():
                    return loc.first
            except Exception:
                continue
    return None


def _handle_confirmation_dialogs(page: Page) -> bool:
    """Handles confirmation popups like 'Post anyway' or copyright notices."""
    dialog_btn_selectors = [
        'div[role="dialog"] button:has-text("Post anyway")',
        'div[role="dialog"] button:has-text("Đăng dù sao đi nữa")',
        'div[role="dialog"] button:has-text("Đăng")',
        'div[role="dialog"] button:has-text("Confirm")',
        'div[role="dialog"] button:has-text("Xác nhận")',
    ]
    contexts = [page] + list(getattr(page, "frames", []))
    for ctx in contexts:
        for sel in dialog_btn_selectors:
            try:
                btn = ctx.locator(sel)
                if btn.count() > 0 and btn.first.is_visible():
                    logger.info(f"[TikTokUploader] Dismissing confirmation dialog button: '{sel}'")
                    btn.first.click()
                    time.sleep(1.5)
                    return True
            except Exception:
                continue
    return False


class TikTokUploader:
    """
    Automates publishing 4-minute teaser video to TikTok Studio.
    """

    def __init__(self, user_data_dir: str = "./config/chrome_profile", headless: bool = False):
        self.user_data_dir = user_data_dir
        self.headless = headless

    def build_caption(self, story_title: str, channel_name: str, duration_minutes: int) -> str:
        """Builds TikTok teaser caption."""
        return (
            f"{story_title} (Phần đầu) - Nghe tiếp cái kết trọn bộ hơn {duration_minutes} phút "
            f"tại kênh YouTube: {channel_name} #truyenaudio #truyenoneshot #kechuyen #truyendemkhuya #radiotruyen"
        )

    def upload(
        self,
        video_path: str,
        story_title: str,
        channel_name: str,
        duration_minutes: int,
        auto_post: bool = True,
        save_draft: bool = False,
        login_timeout: int = 90,
        review_duration: int = 45,
    ) -> bool:
        """Uploads video to TikTok Studio."""
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"TikTok video not found: {video_path}")

        caption = self.build_caption(story_title, channel_name, duration_minutes)
        os.makedirs(self.user_data_dir, exist_ok=True)
        abs_video_path = os.path.abspath(video_path)

        logger.info(f"[TikTokUploader] Launching Playwright Chromium profile: '{self.user_data_dir}'...")

        try:
            with sync_playwright() as playwright:
                context = playwright.chromium.launch_persistent_context(
                    user_data_dir=self.user_data_dir,
                    headless=self.headless,
                    args=["--disable-blink-features=AutomationControlled"],
                )
                page = context.pages[0] if context.pages else context.new_page()
                try:
                    page.set_viewport_size({"width": 1280, "height": 800})
                except Exception:
                    pass

                upload_url = "https://www.tiktok.com/tiktokstudio/upload"
                logger.info(f"[TikTokUploader] Navigating to {upload_url}...")
                try:
                    page.goto(upload_url, wait_until="domcontentloaded", timeout=60000)
                except PlaywrightTimeoutError:
                    pass

                # Wait for login or file input
                start_time = time.time()
                file_input = None
                while time.time() - start_time < login_timeout:
                    if _is_login_page_or_prompt(page):
                        rem = int(login_timeout - (time.time() - start_time))
                        logger.info(f"[TikTokUploader] Login required. Please log in on the browser window ({rem}s left)...")
                        time.sleep(3.0)
                        continue

                    file_input = _find_file_input(page)
                    if file_input:
                        logger.info("[TikTokUploader] Authenticated! Found upload file input.")
                        break
                    time.sleep(2.0)

                if not file_input:
                    logger.error("[TikTokUploader] Timed out waiting for TikTok Studio upload input.")
                    context.close()
                    return False

                # Attach file
                logger.info(f"[TikTokUploader] Attaching video file: '{abs_video_path}'...")
                file_input.set_input_files(abs_video_path)
                time.sleep(3.0)

                # Enter caption
                caption_el = _find_caption_element(page, timeout_seconds=30)
                if caption_el:
                    logger.info(f"[TikTokUploader] Entering caption ({len(caption)} chars)...")
                    caption_el.click()
                    page.keyboard.press("Control+A")
                    page.keyboard.press("Backspace")
                    page.keyboard.type(caption, delay=20)
                    logger.info("[TikTokUploader] Caption entered successfully.")

                # Wait for cover generation to complete
                cover_start = time.time()
                while time.time() - cover_start < 40:
                    try:
                        loading = page.locator('text="Loading...", text="Đang tải...", text="Processing..."')
                        if loading.count() == 0 or not loading.first.is_visible():
                            break
                    except Exception:
                        break
                    time.sleep(2.0)

                # Post or Draft or Review
                if auto_post:
                    logger.info("[TikTokUploader] Auto-post enabled. Searching for bottom Post button...")
                    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    time.sleep(2.0)
                    post_btn = _find_bottom_action_button(page, action="post")
                    if post_btn:
                        post_btn.scroll_into_view_if_needed()
                        post_btn.click()
                        time.sleep(3.0)
                        _handle_confirmation_dialogs(page)
                        logger.info("[TikTokUploader] Post button clicked! Keeping browser open 15s to confirm...")
                        time.sleep(15.0)
                        context.close()
                        return True
                    else:
                        logger.warning("[TikTokUploader] Post button not ready. Holding for manual review.")

                elif save_draft:
                    logger.info("[TikTokUploader] Save Draft enabled...")
                    draft_btn = _find_bottom_action_button(page, action="draft")
                    if draft_btn:
                        draft_btn.click()
                        time.sleep(5.0)
                        logger.info("[TikTokUploader] Saved as Draft!")
                        context.close()
                        return True

                # Review window
                logger.info(f"[TikTokUploader] Upload ready. Keeping browser open for {review_duration}s for manual review...")
                time.sleep(review_duration)
                context.close()
                return True

        except Exception as e:
            logger.error(f"[TikTokUploader] TikTok upload error: {e}")
            return False
