# Copyright (c) 2025 AnonymousX1025
# Licensed under the MIT License.
# This file is part of AnonXMusic

import os
import random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from pyrogram import types

from anony import logger


BASE_DIR = Path(__file__).resolve().parent.parent.parent
TEMPLATES = [
    str(BASE_DIR / "assets" / "welcome" / "welcome_blue.png"),
    str(BASE_DIR / "assets" / "welcome" / "welcome_teal.png"),
    str(BASE_DIR / "assets" / "welcome" / "welcome_purple.png"),
    str(BASE_DIR / "assets" / "welcome" / "welcome_red.png"),
]
FONT_PATH = str(BASE_DIR / "anony" / "helpers" / "Raleway-Bold.ttf")


async def generate_welcome(app, user: types.User, chat_id: int) -> str:
    """Generate welcome banner with the newly joined user's profile picture in the center circle."""
    cache_dir = BASE_DIR / "cache"
    cache_dir.mkdir(exist_ok=True)
    out_path = str(cache_dir / f"welcome_{user.id}_{random.randint(1000, 9999)}.png")

    # Pick randomly from the 4 color variations
    existing_templates = [t for t in TEMPLATES if os.path.exists(t)]
    if existing_templates:
        template_path = random.choice(existing_templates)
    else:
        template_path = TEMPLATES[0]

    bg = Image.open(template_path).convert("RGBA")

    # Download user's profile picture if present (try user object, then get_users)
    user_pfp = None
    photo_obj = getattr(user, "photo", None)
    if not photo_obj:
        try:
            full_user = await app.get_users(user.id)
            photo_obj = getattr(full_user, "photo", None)
        except Exception:
            photo_obj = None

    if photo_obj and getattr(photo_obj, "big_file_id", None):
        try:
            downloaded = await app.download_media(photo_obj.big_file_id)
            if downloaded and os.path.exists(downloaded):
                user_pfp = downloaded
        except Exception as e:
            logger.warning(f"Could not download user profile picture: {e}")
            user_pfp = None

    size = 262
    avatar = None
    if user_pfp:
        try:
            avatar = Image.open(user_pfp).convert("RGBA")
            avatar = avatar.resize((size, size), Image.Resampling.LANCZOS)
        except Exception as e:
            logger.warning(f"Failed to process user profile picture: {e}")
            avatar = None

    if not avatar:
        # Fallback stylish avatar with user initial
        avatar = Image.new("RGBA", (size, size), (45, 120, 230, 255))
        draw_av = ImageDraw.Draw(avatar)
        letter = (getattr(user, "first_name", "") or "U")[0].upper()
        try:
            font = ImageFont.truetype(FONT_PATH, 110)
            bbox = draw_av.textbbox((0, 0), letter, font=font)
            w = bbox[2] - bbox[0]
            h = bbox[3] - bbox[1]
            draw_av.text(((size - w) // 2, (size - h) // 2 - 12), letter, fill=(255, 255, 255, 255), font=font)
        except Exception:
            pass

    # High-quality circular mask with anti-aliasing
    mask = Image.new("L", (size * 4, size * 4), 0)
    draw_mask = ImageDraw.Draw(mask)
    draw_mask.ellipse((0, 0, size * 4 - 1, size * 4 - 1), fill=255)
    mask = mask.resize((size, size), Image.Resampling.LANCZOS)

    # Position at center of inner badge: (510, 204)
    x = 510 - size // 2
    y = 204 - size // 2
    bg.paste(avatar, (x, y), mask)

    # Clean inner ring border highlight
    draw = ImageDraw.Draw(bg)
    draw.ellipse((x, y, x + size - 1, y + size - 1), outline=(255, 255, 255, 140), width=2)

    bg.save(out_path, format="PNG")

    # Clean up downloaded user pfp temp file
    if user_pfp and os.path.exists(user_pfp):
        try:
            os.remove(user_pfp)
        except Exception:
            pass

    return out_path
