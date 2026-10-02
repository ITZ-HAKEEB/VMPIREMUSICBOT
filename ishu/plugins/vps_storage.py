import time
from pyrogram import filters, types
from ishu import app, config

VPS_URL = "http://162.35.187.203:8000"

def get_progress_bar(used: float, total: float, length: int = 10) -> str:
    if total <= 0:
        return "░" * length
    ratio = min(max(used / total, 0.0), 1.0)
    filled = int(round(ratio * length))
    return "█" * filled + "░" * (length - filled)

async def fetch_vps_stats() -> dict | None:
    def _fetch():
        import urllib.request, json as _json
        req = urllib.request.Request(f"{VPS_URL}/stats", headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=4) as resp:
            if resp.status == 200:
                return _json.loads(resp.read().decode())
        return None
    try:
        import asyncio
        return await asyncio.to_thread(_fetch)
    except Exception:
        return None

def format_vps_text(data: dict | None) -> str:
    if not data:
        return (
            "⚠️ **1 TB VPS Storage Status**\n\n"
            "🔴 **Server Status:** Offline or Unreachable\n"
            f"🌐 **Server Host:** `{VPS_URL}`\n\n"
            "Please verify that the VPS storage engine service is running."
        )

    disk_total = data.get("disk_total_gb", 0)
    disk_used = data.get("disk_used_gb", 0)
    disk_free = data.get("disk_free_gb", 0)
    cached_count = data.get("cached_songs_count", 0)
    tg_sync = data.get("telegram_sync") or {}

    bar = get_progress_bar(disk_used, disk_total, length=10)
    free_pct = (disk_free / disk_total * 100) if disk_total > 0 else 0

    sync_status = tg_sync.get("status", "idle")
    total_db = tg_sync.get("total_in_db", 0)
    downloaded = tg_sync.get("downloaded", 0)
    current_song = tg_sync.get("current_song", "None")
    spm = tg_sync.get("download_speed_songs_per_min", 0.0)
    est_hours = tg_sync.get("estimated_hours_remaining", 0.0)

    sync_icon = "🟢" if sync_status == "running" else ("✅" if sync_status == "completed" else "⚪")

    text = (
        "⚡ **1 TB VPS Music Storage & Song CDN Status**\n\n"
        f"🌐 **Server Status:** 🟢 **ONLINE** (`162.35.187.203:8000`)\n\n"
        f"💾 **Storage Capacity:**\n"
        f" • **Disk Space:** `[{bar}]`\n"
        f" • **Used:** `{disk_used:.2f} GB` / `{disk_total:.2f} GB`\n"
        f" • **Free:** `{disk_free:.2f} GB` ({free_pct:.1f}% free)\n\n"
        f"🎵 **Song Store Count:**\n"
        f" • **Total Cached Songs on VPS:** `{cached_count:,}` songs\n"
        f" • **Voice Chat Stream Latency:** `< 50 ms (Instant)`\n\n"
        f"🔄 **Telegram Dump Synchronization:**\n"
        f" • **Sync Status:** {sync_icon} **{sync_status.capitalize()}**\n"
        f" • **Dump Progress:** `{downloaded:,}` / `{total_db:,}` songs\n"
    )

    if current_song and current_song != "None":
        text += f" • **Current Syncing:** `{current_song[:35]}`\n"
    if spm > 0:
        text += f" • **Download Speed:** `~{spm} songs/min`\n"
    if est_hours > 0:
        text += f" • **Est. Time Remaining:** `~{est_hours} hours`\n"

    text += (
        f"\n🕒 _Last Checked: {time.strftime('%H:%M:%S UTC', time.gmtime())}_\n"
        f"✨ _All connected fleet bots stream directly from this 1 TB cache._"
    )
    return text

def get_vps_buttons() -> types.InlineKeyboardMarkup:
    return types.InlineKeyboardMarkup(
        [
            [
                types.InlineKeyboardButton("🔄 Refresh Status", callback_data="refresh_vps_stats"),
                types.InlineKeyboardButton("🗑 Close", callback_data="close"),
            ]
        ]
    )

@app.on_message(filters.command(["vps", "storage", "vpsstats", "vpsstatus", "storedsongs"]) & ~app.bl_users)
async def vps_command(_, m: types.Message):
    sent = await m.reply_text("⚡ *Checking 1 TB VPS Storage & Sync Status...*")
    data = await fetch_vps_stats()
    text = format_vps_text(data)
    await sent.edit_text(text, reply_markup=get_vps_buttons())

@app.on_callback_query(filters.regex("^refresh_vps_stats$"))
async def refresh_vps_callback(_, query: types.CallbackQuery):
    await query.answer("Fetching live VPS stats...")
    data = await fetch_vps_stats()
    text = format_vps_text(data)
    try:
        await query.message.edit_text(text, reply_markup=get_vps_buttons())
    except Exception:
        pass
