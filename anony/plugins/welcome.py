import asyncio
import html
import os
from pyrogram import enums, filters, types

from anony import app, logger
from anony.helpers import buttons, generate_welcome


async def _auto_delete_message(msg: types.Message, delay: int = 3):
    await asyncio.sleep(delay)
    try:
        await msg.delete()
        logger.info(f"Auto-deleted welcome message {msg.id} in chat {msg.chat.id}")
    except Exception as e:
        logger.debug(f"Could not auto-delete welcome message: {e}")


@app.on_message(filters.new_chat_members, group=5)
async def _welcome_member(_, message: types.Message):
    if not message.chat:
        return

    logger.info(f"new_chat_members triggered in chat {message.chat.id} ({message.chat.title})")

    for member in message.new_chat_members:
        if member.id == app.id:
            continue

        try:
            logger.info(f"Generating welcome banner for member {member.id} ({member.first_name}) in {message.chat.id}")
            photo = await generate_welcome(app, member, message.chat.id)
            username = f"@{member.username}" if member.username else "-"
            chat_title = html.escape(message.chat.title or "Group")
            text = (
                f"<blockquote><b>𝐖ᴇʟᴄᴏᴍᴇ 𝐓ᴏ {chat_title}\n"
                f"  𝐍ᴀᴍᴇ ✧ {member.mention}\n"
                f"  𝐈ᴅ ✧ {member.id}\n"
                f"  𝐔sᴇʀɴᴀᴍᴇ ✧ {username}</b></blockquote>"
            )
            key = types.InlineKeyboardMarkup(
                [
                    [
                        buttons.ikb(
                            text="add me",
                            url=f"https://t.me/{app.username}?startgroup=true",
                            style=enums.ButtonStyle.SUCCESS,
                        )
                    ]
                ]
            )
            welcome_msg = await message.reply_photo(
                photo=photo,
                caption=text,
                reply_markup=key,
            )
            logger.info(f"Welcome message sent to {member.id} in {message.chat.id}. Auto-deleting in 3 seconds...")
            try:
                os.remove(photo)
            except Exception:
                pass

            # Auto-delete welcome message in 3 seconds as requested
            asyncio.create_task(_auto_delete_message(welcome_msg, 3))
        except Exception as e:
            logger.exception(f"Error sending welcome message for member {member.id}: {e}")

