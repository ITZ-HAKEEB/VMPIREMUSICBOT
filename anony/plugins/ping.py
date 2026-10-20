import os
import time
import psutil

from pyrogram import filters, types
from anony import app, anon, boot, config, lang
from anony.helpers import buttons


@app.on_message(filters.command(["alive", "ping"]) & ~app.bl_users)
@lang.language()
async def _ping(_, m: types.Message):
    start = time.time()
    sent = await m.reply_text(m.lang["pinging"])
    uptime_sec = int(time.time() - boot)
    days = uptime_sec // 86400
    hours = (uptime_sec // 3600) % 24
    minutes = (uptime_sec // 60) % 60
    seconds = uptime_sec % 60
    uptime = (
        f"{days}ᴅ:{hours}ʜ:{minutes}ᴍ:{seconds}s"
        if days > 0
        else f"{hours}ʜ:{minutes}ᴍ:{seconds}s"
    )

    latency = round((time.time() - start) * 1000, 3)
    try:
        pytgcalls = round(await anon.ping(), 3)
    except Exception:
        pytgcalls = 0.0

    bot_mention = app.me.mention if getattr(app, "me", None) else "Bot"
    ram = round(psutil.virtual_memory().percent, 1)
    cpu = round(psutil.cpu_percent(interval=0), 1)
    disk = round(psutil.disk_usage("/").percent, 1)

    ping_img = config.PING_IMG or (
        "assets/ping.png"
        if os.path.exists("assets/ping.png")
        else ("assets/ping.jpg" if os.path.exists("assets/ping.jpg") else "https://files.catbox.moe/xmcz1p.jpg")
    )

    caption = (
        f"🏓 ᴩᴏɴɢ : {latency}ᴍs\n\n"
        f"{bot_mention}♪ sʏsᴛᴇᴍ sᴛᴀᴛs :\n\n"
        f"↬ ᴜᴩᴛɪᴍᴇ : {uptime}\n"
        f"↬ ʀᴀᴍ : {ram}%\n"
        f"↬ ᴄᴩᴜ : {cpu}%\n"
        f"↬ ᴅɪsᴋ : {disk}%\n"
        f"↬ ᴩʏ-ᴛɢᴄᴀʟʟs : {pytgcalls}ᴍs"
    )

    await sent.edit_media(
        media=types.InputMediaPhoto(
            media=ping_img,
            caption=caption,
        ),
        reply_markup=buttons.ping_markup(m.lang["support"]),
    )
