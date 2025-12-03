from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ForceReply
from info import ADMIN
from database import db
# Import url_states from monitor to display status in /check and /stats
from MyselfNeon.monitor import url_states, check_url
import aiohttp

# --- START COMMAND ---
@Client.on_message(filters.command("start") & filters.private & filters.user(ADMIN))
async def start_command(client, message):
    interval = await db.get_interval()
    start_message = (
        "‣ Hᴇʟʟᴏ 𐌽𐌴𐌏𐌽 🇮🇳\n"
        "I ᴀᴍ Lᴀᴛᴇsᴛ Aᴅᴠᴀɴᴄᴇᴅ **Keep-Alive Monitor Bᴏᴛ**.\n"
        "Cᴏᴅᴇᴅ & Dᴇᴠᴇʟᴏᴘᴇᴅ ʙʏ NᴇᴏɴAɴᴜʀᴀɢ.\n"
        f"I ᴄᴀɴ **Trigger** ᴀɴᴅ **Monitor** Yᴏᴜʀ ᴡᴇʙsᴇʀᴠɪᴄᴇs ᴇᴠᴇʀʏ **{interval}** ѕᴇᴄᴏɴᴅs.\n\n"
        "**Commands:**\n"
        "/add `url` - Monitor a new URL\n"
        "/del `url` - Delete a URL\n"
        "/check - Manual check status\n"
        "/time - Set monitor interval"
    )
    await message.reply_text(start_message)

# --- ADD URL ---
@Client.on_message(filters.command("add") & filters.private & filters.user(ADMIN))
async def add_url_command(client, message):
    if len(message.command) < 2:
        return await message.reply_text("⚠️ Usage: `/add https://example.com`")
    
    url = message.command[1]
    if not url.startswith("http"):
        return await message.reply_text("⚠️ Invalid URL. Must start with http or https.")
    
    if await db.is_url_exist(url):
        return await message.reply_text("⚠️ URL is already being monitored.")
    
    await db.add_url(url)
    await message.reply_text(f"✅ Added to monitor: `{url}`")

# --- DELETE URL ---
@Client.on_message(filters.command("del") & filters.private & filters.user(ADMIN))
async def delete_url_command(client, message):
    if len(message.command) < 2:
        return await message.reply_text("⚠️ Usage: `/del https://example.com`")
    
    url = message.command[1]
    
    if not await db.is_url_exist(url):
        return await message.reply_text("⚠️ This URL is not in the database.")
    
    await db.remove_url(url)
    # Remove from local state cache if exists
    if url in url_states:
        del url_states[url]
        
    await message.reply_text(f"🗑 Removed from monitor: `{url}`")

# --- CHECK / STATS ---
@Client.on_message(filters.command(["check", "stats"]) & filters.private & filters.user(ADMIN))
async def stats_command(client, message):
    msg = await message.reply_text("🔄 Checking status of all services...")
    urls = await db.get_urls()
    
    text = "📊 **Current Status Report**\n\n"
    if not urls:
        text += "No URLs found in Database."
    else:
        async with aiohttp.ClientSession() as session:
            for url in urls:
                # Perform a real-time check
                is_online, code = await check_url(session, url)
                icon = "🟢" if is_online else "🔴"
                status_text = "ONLINE" if is_online else f"OFFLINE ({code})"
                text += f"{icon} `{url}`\n   ╚ **{status_text}**\n\n"
                
                # Update local cache while we are at it
                url_states[url] = 'online' if is_online else 'offline'
            
    await msg.edit_text(text)

# --- TIME COMMAND ---
@Client.on_message(filters.command("time") & filters.private & filters.user(ADMIN))
async def time_command(client, message):
    current_interval = await db.get_interval()
    
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Reset to Default (60s)", callback_data="time_reset"),
            InlineKeyboardButton("Change Time", callback_data="time_change")
        ]
    ])
    
    await message.reply_text(
        f"⏱ **Monitoring Interval**\n\nCurrent Interval: **{current_interval} seconds**.",
        reply_markup=buttons
    )

# --- CALLBACK HANDLERS FOR TIME ---
@Client.on_callback_query(filters.regex("time_"))
async def time_callback(client, callback_query):
    data = callback_query.data
    
    if data == "time_reset":
        await db.set_interval(60)
        await callback_query.answer("Reset to 60 seconds!")
        await callback_query.message.edit_text(
            "⏱ **Monitoring Interval**\n\nCurrent Interval: **60 seconds**.\n(Reset Successful)",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Change Time", callback_data="time_change")]])
        )
        
    elif data == "time_change":
        await callback_query.answer()
        # Send a force reply to capture input
        await callback_query.message.reply_text(
            "📝 **Send the new interval in seconds:**",
            reply_markup=ForceReply(selective=True)
        )

# --- CAPTURE TIME INPUT ---
@Client.on_message(filters.reply & filters.private & filters.user(ADMIN))
async def set_time_input(client, message):
    # Check if this reply is for the time change
    if message.reply_to_message.text and "Send the new interval" in message.reply_to_message.text:
        try:
            new_time = int(message.text)
            if new_time < 10:
                return await message.reply_text("⚠️ Minimum interval is 10 seconds.")
            
            await db.set_interval(new_time)
            await message.reply_text(f"✅ **Interval updated to {new_time} seconds!**")
        except ValueError:
            await message.reply_text("⚠️ Please send a valid number.")
