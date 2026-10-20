"""
image_generator.py - Generates or validates 16:9 YouTube Background Images.
"""

import os
import time
import random
import urllib.parse
import logging
from typing import Optional
import requests
from PIL import Image, ImageDraw

from src.utils.logger import setup_logger

logger = setup_logger("TOOLTRUYENAUDIO.image_gen")


class ImageGenerator:
    """
    Manages YouTube 16:9 (1920x1080) background images.
    Supports manual user image selection or free AI image generation via Pollinations.ai.
    """

    def __init__(self, output_dir: str = "assets/bg_images"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def validate_or_resize_image(self, input_image_path: str, target_size=(1920, 1080)) -> str:
        """Ensures an image exists, fits 16:9 aspect ratio, and is saved in output_dir."""
        if not os.path.isfile(input_image_path):
            raise FileNotFoundError(f"Image file not found: {input_image_path}")

        try:
            with Image.open(input_image_path) as img:
                img_rgb = img.convert("RGB")
                resized = img_rgb.resize(target_size, Image.Resampling.LANCZOS)
                out_path = os.path.join(self.output_dir, f"manual_bg_{int(time.time())}.jpg")
                resized.save(out_path, quality=95)
                logger.info(f"[ImageGen] Validated manual image and resized to {target_size}: {out_path}")
                return out_path
        except Exception as e:
            logger.error(f"[ImageGen] Failed to process image {input_image_path}: {e}")
            raise

    def create_fallback_image(self, topic: str, target_size=(1920, 1080)) -> str:
        """Creates a cinematic gradient background using Pillow for offline use."""
        img = Image.new("RGB", target_size, color=(15, 18, 30))
        draw = ImageDraw.Draw(img)

        # Draw deep subtle gradient bands
        w, h = target_size
        for y in range(h):
            r = int(15 + (y / h) * 25)
            g = int(20 + (y / h) * 20)
            b = int(35 + (y / h) * 45)
            draw.line([(0, y), (w, y)], fill=(r, g, b))

        # Add vignette border
        out_path = os.path.join(self.output_dir, f"fallback_bg_{int(time.time())}.jpg")
        img.save(out_path, quality=95)
        logger.info(f"[ImageGen] Created offline cinematic background: {out_path}")
        return out_path

    def generate_ai_image(self, topic: str, title: Optional[str] = None) -> str:
        """
        Generates an AI background image matching the story mood using Pollinations.ai
        (Free, fast, no API key required).
        """
        prompt_keywords = (
            f"Cinematic atmospheric dramatic lighting, emotional scene, audio book cover, "
            f"story about {topic}, ultra detailed, 8k resolution, masterpiece, trending on artstation, "
            f"dark fantasy, photorealistic cinematic film still, 16:9 aspect ratio, no text, no watermark"
        )
        if title:
            prompt_keywords = f"Cinematic scene for '{title}', {prompt_keywords}"

        encoded_prompt = urllib.parse.quote(prompt_keywords)
        seed = random.randint(1000, 999999)
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1920&height=1080&nologo=true&seed={seed}"

        logger.info(f"[ImageGen] Requesting AI background image from Pollinations.ai...")
        out_path = os.path.join(self.output_dir, f"ai_bg_{int(time.time())}.jpg")

        try:
            resp = requests.get(url, timeout=30)
            if resp.status_code == 200 and len(resp.content) > 10000:
                with open(out_path, "wb") as f:
                    f.write(resp.content)
                logger.info(f"[ImageGen] AI background image saved successfully: {out_path} ({len(resp.content):,} bytes)")
                return out_path
            else:
                logger.warning(f"[ImageGen] Pollinations returned status {resp.status_code}. Using fallback graphic.")
        except Exception as e:
            logger.warning(f"[ImageGen] Failed to download AI image ({e}). Using offline fallback graphic.")

        return self.create_fallback_image(topic)

    def get_youtube_background(self, mode: str, manual_path: Optional[str], topic: str, title: Optional[str]) -> str:
        """Resolves background image based on selected mode ('manual' or 'auto_ai')."""
        if mode == "manual" and manual_path:
            return self.validate_or_resize_image(manual_path)
        return self.generate_ai_image(topic, title)
