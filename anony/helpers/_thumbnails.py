# Copyright (c) 2025 AnonymousX1025
# Licensed under the MIT License.
# This file is part of AnonXMusic


import os
import re
import random
import aiohttp
from PIL import (
    Image,
    ImageDraw,
    ImageFilter,
    ImageFont,
    ImageOps,
)

from anony import config, logger
from anony.helpers import Track


COLOR_THEMES = [
    # 1. Crimson Metallic Red (Reference style)
    {"name": "crimson", "primary": (195, 25, 40), "dark": (45, 5, 10), "play_fill": (45, 5, 10)},
    # 2. Midnight Sapphire Blue
    {"name": "sapphire", "primary": (25, 95, 215), "dark": (8, 18, 55), "play_fill": (8, 18, 55)},
    # 3. Neon Violet / Royal Purple
    {"name": "violet", "primary": (155, 35, 225), "dark": (35, 8, 60), "play_fill": (35, 8, 60)},
    # 4. Emerald Jade Green
    {"name": "emerald", "primary": (20, 160, 90), "dark": (5, 40, 22), "play_fill": (5, 40, 22)},
    # 5. Sunset Amber / Copper Gold
    {"name": "amber", "primary": (225, 120, 20), "dark": (60, 28, 6), "play_fill": (60, 28, 6)},
    # 6. Cyberpunk Cyan / Electric Teal
    {"name": "teal", "primary": (15, 165, 205), "dark": (5, 42, 58), "play_fill": (5, 42, 58)},
    # 7. Hot Rose Magenta
    {"name": "magenta", "primary": (215, 30, 120), "dark": (55, 8, 32), "play_fill": (55, 8, 32)},
    # 8. Obsidian Charcoal Noir
    {"name": "noir", "primary": (65, 68, 76), "dark": (18, 18, 22), "play_fill": (18, 18, 22)},
]


def clean_display_text(text: str) -> str:
    if not text:
        return ""
    chars = [
        c
        for c in text
        if ord(c) <= 0x052F
        or (0x0900 <= ord(c) <= 0x097F)
        or ord(c) in (8211, 8212, 8216, 8217, 8220, 8221, 8230)
    ]
    return re.sub(r"\s+", " ", "".join(chars)).strip()


def wrap_title(title: str, font: ImageFont.FreeTypeFont, max_w: int, max_lines: int = 2) -> list[str]:
    words = title.split()
    lines = []
    curr = ""
    for w in words:
        test = f"{curr} {w}".strip()
        dummy = Image.new("RGBA", (1, 1))
        d = ImageDraw.Draw(dummy)
        if d.textlength(test, font=font) <= max_w:
            curr = test
        else:
            if curr:
                lines.append(curr)
            curr = w
            if len(lines) >= max_lines - 1:
                break
    if curr and len(lines) < max_lines:
        lines.append(curr)

    dummy = Image.new("RGBA", (1, 1))
    d = ImageDraw.Draw(dummy)
    if lines:
        while d.textlength(lines[-1] + "...", font=font) > max_w and len(lines[-1]) > 3:
            lines[-1] = lines[-1][:-1]
        if " ".join(lines) != title:
            if not lines[-1].endswith("..."):
                lines[-1] = lines[-1].rstrip(".,- ") + "..."
    return lines or [title[:25]]


def create_metallic_bg(size: tuple[int, int], primary_color: tuple, dark_color: tuple) -> Image.Image:
    w, h = size
    # Low-res radial canvas for smooth gradient
    s_w, s_h = 160, 90
    small = Image.new("RGB", (s_w, s_h), dark_color)
    draw = ImageDraw.Draw(small)

    cx, cy = s_w * 0.45, s_h * 0.45
    max_r = max(s_w, s_h) * 0.95
    steps = 40
    for i in range(steps, 0, -1):
        t = i / steps
        r = int(primary_color[0] * (1 - t) + dark_color[0] * t)
        g = int(primary_color[1] * (1 - t) + dark_color[1] * t)
        b = int(primary_color[2] * (1 - t) + dark_color[2] * t)
        rad_x = max_r * t * 1.3
        rad_y = max_r * t * 0.9
        draw.ellipse((cx - rad_x, cy - rad_y, cx + rad_x, cy + rad_y), fill=(r, g, b))

    # Upscale smoothly to full resolution
    bg = small.resize(size, resample=Image.Resampling.BICUBIC)
    bg = bg.filter(ImageFilter.GaussianBlur(16))

    # Add metallic fine texture
    tile_size = 128
    noise_tile = Image.new("L", (tile_size, tile_size))
    noise_tile.putdata([random.randint(116, 140) for _ in range(tile_size * tile_size)])

    noise_img = Image.new("L", size)
    for x in range(0, w, tile_size):
        for y in range(0, h, tile_size):
            noise_img.paste(noise_tile, (x, y))

    noise_rgba = Image.merge("RGBA", (noise_img, noise_img, noise_img, Image.new("L", size, 32)))
    return Image.alpha_composite(bg.convert("RGBA"), noise_rgba)


class Thumbnail:
    def __init__(self):
        bold_font_path = "anony/helpers/Raleway-Bold.ttf"
        light_font_path = "anony/helpers/Inter-Light.ttf"

        self.font_title = ImageFont.truetype(bold_font_path, 44)
        self.font_sub = ImageFont.truetype(bold_font_path, 36)
        self.font_time = ImageFont.truetype(light_font_path, 22)
        self.session: aiohttp.ClientSession | None = None

    async def start(self) -> None:
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()

    async def close(self) -> None:
        if self.session and not self.session.closed:
            await self.session.close()

    async def save_thumb(self, output_path: str, url: str) -> str:
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        async with self.session.get(url) as resp:
            with open(output_path, "wb") as f:
                f.write(await resp.read())
        return output_path

    async def generate(self, song: Track, size=(1280, 720)) -> str:
        try:
            os.makedirs("cache", exist_ok=True)
            temp = f"cache/temp_{song.id}.jpg"
            output = f"cache/v2_{song.id}.png"
            if os.path.exists(output):
                return output

            # 1. Download original thumbnail with fallback
            raw_img = None
            if getattr(song, "thumbnail", None) and str(song.thumbnail).startswith("http"):
                try:
                    await self.save_thumb(temp, song.thumbnail)
                    raw_img = Image.open(temp).convert("RGBA")
                except Exception as e:
                    logger.warning(f"Could not load thumbnail from URL: {e}")
                    raw_img = None

            if raw_img is None:
                # Elegant dark vinyl/player artwork fallback
                raw_img = Image.new("RGBA", (480, 480), (35, 35, 42, 255))
                d_art = ImageDraw.Draw(raw_img)
                d_art.ellipse((140, 140, 340, 340), fill=(55, 55, 65, 255))
                d_art.polygon([(215, 190), (285, 240), (215, 290)], fill=(255, 255, 255, 240))

            # 2. Pick a vibrant theme (variety of colors)
            theme = COLOR_THEMES[abs(hash(song.id)) % len(COLOR_THEMES)]
            bg = create_metallic_bg(size, theme["primary"], theme["dark"])

            # 3. Album Cover (Square card with rounded corners & shadow)
            cover_size = (460, 460)
            cover_pos = (90, 130)
            cover_radius = 36

            cover = ImageOps.fit(
                raw_img,
                cover_size,
                method=Image.Resampling.LANCZOS,
                centering=(0.5, 0.5),
            )
            mask = Image.new("L", cover_size, 0)
            ImageDraw.Draw(mask).rounded_rectangle(
                (0, 0, cover_size[0], cover_size[1]),
                radius=cover_radius,
                fill=255,
            )
            cover.putalpha(mask)

            # Soft drop shadow
            shadow_layer = Image.new("RGBA", size, (0, 0, 0, 0))
            shadow_mask = Image.new("L", cover_size, 0)
            ImageDraw.Draw(shadow_mask).rounded_rectangle(
                (0, 0, cover_size[0], cover_size[1]),
                radius=cover_radius,
                fill=220,
            )
            shadow_layer.paste(
                (0, 0, 0, 160),
                (cover_pos[0] + 6, cover_pos[1] + 12),
                shadow_mask,
            )
            shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(24))
            bg = Image.alpha_composite(bg, shadow_layer)
            bg.paste(cover, cover_pos, cover)

            # 4. Right Side UI Elements
            overlay = Image.new("RGBA", size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(overlay)

            rx_start = 630
            rx_end = 1180
            bar_w = rx_end - rx_start

            # Title
            raw_title = clean_display_text(song.title) or (song.title or "Unknown Title")
            title_lines = wrap_title(raw_title, self.font_title, bar_w, max_lines=2)
            title_y = 230 if len(title_lines) > 1 else 250
            for i, line in enumerate(title_lines):
                font = self.font_title if i == 0 else self.font_sub
                draw.text(
                    (rx_start, title_y + (i * 52)),
                    line,
                    font=font,
                    fill=(255, 255, 255, 255),
                )

            # Progress Slider
            bar_y = 390
            bar_h = 5
            # Background track
            draw.rounded_rectangle(
                (rx_start, bar_y, rx_end, bar_y + bar_h),
                radius=2,
                fill=(255, 255, 255, 80),
            )

            # Progress fill (~35%)
            progress_ratio = 0.35
            fill_w = int(bar_w * progress_ratio)
            draw.rounded_rectangle(
                (rx_start, bar_y, rx_start + fill_w, bar_y + bar_h),
                radius=2,
                fill=(255, 255, 255, 255),
            )

            # Circular scrubber dot knob
            knob_x = rx_start + fill_w
            knob_y = bar_y + bar_h // 2
            knob_r = 8
            draw.ellipse(
                (knob_x - knob_r, knob_y - knob_r, knob_x + knob_r, knob_y + knob_r),
                fill=(255, 255, 255, 255),
            )

            # Timestamps
            dur_sec = getattr(song, "duration_sec", 0) or 238
            cur_sec = int(dur_sec * progress_ratio)
            cur_str = f"{cur_sec // 60}:{cur_sec % 60:02d}"
            dur_str = song.duration or f"{dur_sec // 60}:{dur_sec % 60:02d}"

            draw.text((rx_start, bar_y + 16), cur_str, font=self.font_time, fill=(240, 240, 240, 230))
            dur_w = draw.textlength(dur_str, font=self.font_time)
            draw.text((rx_end - dur_w, bar_y + 16), dur_str, font=self.font_time, fill=(240, 240, 240, 230))

            # 5. Media Controls Row (5 evenly spaced buttons)
            ctrl_y = 510
            ctrl_gap = bar_w // 4
            c_shuffle_x = rx_start + 20
            c_prev_x = rx_start + ctrl_gap
            c_play_x = rx_start + ctrl_gap * 2
            c_next_x = rx_start + ctrl_gap * 3
            c_repeat_x = rx_end - 20

            # Shuffle (🔀)
            draw.line(
                [(c_shuffle_x - 16, ctrl_y - 10), (c_shuffle_x - 6, ctrl_y - 10), (c_shuffle_x + 6, ctrl_y + 10), (c_shuffle_x + 16, ctrl_y + 10)],
                fill=(255, 255, 255),
                width=3,
            )
            draw.polygon([(c_shuffle_x + 14, ctrl_y + 5), (c_shuffle_x + 22, ctrl_y + 10), (c_shuffle_x + 14, ctrl_y + 15)], fill=(255, 255, 255))
            draw.line(
                [(c_shuffle_x - 16, ctrl_y + 10), (c_shuffle_x - 6, ctrl_y + 10), (c_shuffle_x - 2, ctrl_y + 4)],
                fill=(255, 255, 255),
                width=3,
            )
            draw.line(
                [(c_shuffle_x + 2, ctrl_y - 4), (c_shuffle_x + 6, ctrl_y - 10), (c_shuffle_x + 16, ctrl_y - 10)],
                fill=(255, 255, 255),
                width=3,
            )
            draw.polygon([(c_shuffle_x + 14, ctrl_y - 15), (c_shuffle_x + 22, ctrl_y - 10), (c_shuffle_x + 14, ctrl_y - 5)], fill=(255, 255, 255))

            # Previous (⏮ |◀)
            draw.rounded_rectangle((c_prev_x - 15, ctrl_y - 14, c_prev_x - 11, ctrl_y + 14), radius=1, fill=(255, 255, 255))
            draw.polygon([(c_prev_x + 13, ctrl_y - 14), (c_prev_x - 9, ctrl_y), (c_prev_x + 13, ctrl_y + 14)], fill=(255, 255, 255))

            # Play Button (▶ in solid white circle)
            play_r = 30
            draw.ellipse((c_play_x - play_r, ctrl_y - play_r, c_play_x + play_r, ctrl_y + play_r), fill=(255, 255, 255))
            draw.polygon(
                [(c_play_x - 7, ctrl_y - 12), (c_play_x + 11, ctrl_y), (c_play_x - 7, ctrl_y + 12)],
                fill=theme["play_fill"],
            )

            # Next (⏭ ▶|)
            draw.polygon([(c_next_x - 13, ctrl_y - 14), (c_next_x + 9, ctrl_y), (c_next_x - 13, ctrl_y + 14)], fill=(255, 255, 255))
            draw.rounded_rectangle((c_next_x + 11, ctrl_y - 14, c_next_x + 15, ctrl_y + 14), radius=1, fill=(255, 255, 255))

            # Repeat (🔁)
            draw.rounded_rectangle((c_repeat_x - 16, ctrl_y - 11, c_repeat_x + 16, ctrl_y + 11), radius=5, outline=(255, 255, 255), width=3)
            draw.rectangle((c_repeat_x + 13, ctrl_y - 4, c_repeat_x + 18, ctrl_y + 4), fill=(0, 0, 0, 0))
            draw.polygon([(c_repeat_x + 13, ctrl_y - 16), (c_repeat_x + 21, ctrl_y - 8), (c_repeat_x + 13, ctrl_y)], fill=(255, 255, 255))

            # Composite and save
            bg = Image.alpha_composite(bg, overlay)
            bg.convert("RGB").save(output, "PNG")

            try:
                os.remove(temp)
            except Exception:
                pass
            return output
        except Exception as ex:
            logger.error(f"Failed to generate thumbnail: {ex}")
            return config.DEFAULT_THUMB
