# ---------------------------------------------------
# File Name: Commands.py
# Author: MyselfNeon
# GitHub: https://github.com/MyselfNeon/
# Telegram: https://t.me/MyelfNeon
# ---------------------------------------------------

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ForceReply
from .db import db
from .image_gen import draw_dashboard
from info import ADMIN
import aiohttp

# --- Start Command ---
@Client.on_message(filters.command("start") & filters.private)
async def start_command(client, message):
    user_name = message.from_user.first_name
    
    text = (
        f"<blockquote>👋 **Hello {user_name}**</blockquote>\n\n"
        "🎉 **Welcome to your Premium Uptime Monitor.**\n"
        "**I protect your URLs from sleeping.**\n\n"
        "⁉️ **Features:**\n"
        "– __Real-time Monitoring & Latency Tracking__\n"
        "– __Visual Dashboard Reports__\n\n"
        "🛠 **Controls:**\n"
        "<blockquote>– `/add Url` – Start Monitoring\n"
        "– `/del Url` – Stop Monitoring\n"
        "– `/check` – Visual Dashboard\n"
        "– `/time` – Set Interval (Admin)</blockquote>"
    )
    
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("🆘 Support", url="https://t.me/MyselfNeon"),
         InlineKeyboardButton("📢 Updates", url="https://t.me/NeonFiles")]
    ])
    
    await message.reply_text(text, reply_markup=buttons)

# --- Add Url Command ---
@Client.on_message(filters.command("add") & filters.private)
async def add_url_command(client, message):
    user_id = message.from_user.id

    if len(message.command) < 2:
        return await message.reply_text("⚠️ **Usage:** `/add https://your-site.com`")
    
    url = message.command[1]
    if not url.startswith("http"):
        return await message.reply_text("⛔ **Invalid URL!** Must start with `http://` or `https://`")
    
    if await db.is_url_exist(user_id, url):
        return await message.reply_text("⚠️ **Already Exists!**")
    
    await db.add_url(user_id, url)
    await message.reply_text(
        f"✅ **Added!**\n\n"
        f"🔗 **URL:** `{url}`\n"
        f"🚀 **Status:** Monitoring Started..."
    )

# --- Delete Url Command ---
@Client.on_message(filters.command("del") & filters.private)
async def delete_url_command(client, message):
    user_id = message.from_user.id

    if len(message.command) < 2:
        return await message.reply_text("⚠️ **Usage:** `/del https://your-site.com`")
    
    url = message.command[1]
    if not await db.is_url_exist(user_id, url):
        return await message.reply_text("🤷‍♂️ **Not Found!**")
    
    await db.remove_url(user_id, url)
    await message.reply_text(f"🗑 **Deleted:** `{url}`")

# --- Visual Dashboard Command ---
@Client.on_message(filters.command(["check", "stats", "dashboard"]) & filters.private)
async def stats_command(client, message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    
    wait_msg = await message.reply_text("🎨 **Drawing your Dashboard...**")
    
    # 1. Fetch Data
    urls_data = await db.col.find({"user_id": user_id}).to_list(length=None)
    
    if not urls_data:
        return await wait_msg.edit_text("📂 **List is Empty!**\nUse `/add` to monitor a site.")

    # 2. Generate Image
    try:
        photo_file = draw_dashboard(user_name, urls_data)
        
        await message.reply_photo(
            photo=photo_file,
            caption=f"📊 **Live Status Report**\n__Generated for {user_name}__",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔄 Refresh", callback_data="ping_all")]
            ])
        )
        await wait_msg.delete()
    except Exception as e:
        await wait_msg.edit_text(f"⚠️ **Error generating image:** `{e}`")

# --- Refresh Callback ---
@Client.on_callback_query(filters.regex("ping_all"))
async def ping_all_callback(client, query):
    # Just re-trigger the stats command logic
    await query.answer("🔄 Refreshing...")
    # Ideally, call the function directly or ask user to run command
    # For now, we just acknowledge. Real refresh requires re-generating image.
    await stats_command(client, query.message)

# --- Time Command (Admin Only) ---
@Client.on_message(filters.command("time") & filters.user(ADMIN))
async def time_command(client, message):
    current_time = await db.get_interval()
    
    text = (
        f"⏱ **Monitor Interval Settings**\n\n"
        f"**Current:** {current_time} Seconds"
    )
    
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("📝 Change", callback_data="time_change"),
         InlineKeyboardButton("❌ Close", callback_data="time_close")]
    ])
    
    await message.reply_text(text, reply_markup=buttons)

@Client.on_callback_query(filters.regex("^time_"))
async def time_callbacks(client, query):
    if query.from_user.id != ADMIN:
        return await query.answer("❌ Admin only!", show_alert=True)

    data = query.data
    
    if data == "time_close":
        await query.message.delete()
        
    elif data == "time_change":
        await query.answer()
        await query.message.reply_text(
            "⏳ **Send new interval (seconds):**",
            reply_markup=ForceReply(selective=True)
        )

# --- Handle Time Input ---
@Client.on_message(filters.reply & filters.user(ADMIN))
async def set_time_input(client, message):
    if message.reply_to_message and "Send new interval" in message.reply_to_message.text:
        try:
            new_time = int(message.text)
            if new_time < 10: 
                return await message.reply_text("⚠️ **Minimum 10s!**")
            
            await db.set_interval(new_time)
            await message.reply_text(f"✅ **Interval set to {new_time}s.**")
        except ValueError:
            await message.reply_text("⚠️ **Numbers only.**")
            
