Drawing----------------------------------------------
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
        f"<blockquote>👋 **__Hello {user_name}__**</blockquote>\n\n"
        "🎉 **__Welcome to your Premium Uptime Monitor Bot. __**"
        "**__I am here to Protect your Web Urls from going to Sleep.__**\n\n"
        "⁉️ **__Features I Provide :__**\n"
        "– __I monitor your URLs 24/7 and Alert you Instantly if they go Down.__\n\n"
        "🛠 **__Control Menu :__**\n"
        "<blockquote>– **__Start Monitoring an URL** (/add Url)__\n"
        "– **__Stop Monitoring an URL** (/del Url)__\n"
        "– **__Live Status Dashboard** (/check)__\n"
        "– **__Set Monitor Interval** (/time)__</blockquote>"
    )
    
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("🆘 Sᴜᴘᴘᴏʀᴛ", url="https://t.me/MyselfNeon"),
         InlineKeyboardButton("📢 Uᴘᴅᴀᴛᴇs", url="https://t.me/NeonFiles")]
    ])
    
    await message.reply_text(text, reply_markup=buttons)

# --- Add Url Command ---
@Client.on_message(filters.command("add") & filters.private)
async def add_url_command(client, message):
    user_id = message.from_user.id

    if len(message.command) < 2:
        return await message.reply_text("⚠️ **__Usage:__** `/add https://your-site.com`")
    
    url = message.command[1]
    if not url.startswith("http"):
        return await message.reply_text("⛔ **__Invalid URL !\nMust start with `http://` or `https://`__**")
    
    if await db.is_url_exist(user_id, url):
        return await message.reply_text("⚠️ **__URL Already Exists!__**")
    
    await db.add_url(user_id, url)
    await message.reply_text(
        f"✅ **__New Added !__**\n\n"
        f"🔗 **__URL:** {url}__\n"
        f"🚀 **__Status:__** **__Monitoring Started ...__**"
    )

# --- Delete Url Command ---
@Client.on_message(filters.command("del") & filters.private)
async def delete_url_command(client, message):
    user_id = message.from_user.id

    if len(message.command) < 2:
        return await message.reply_text("⚠️ **__Usage:__** `/del https://your-site.com`")
    
    url = message.command[1]
    if not await db.is_url_exist(user_id, url):
        return await message.reply_text("🤷‍♂️ **__Not Found !__**")
    
    await db.remove_url(user_id, url)
    await message.reply_text(f"🗑 **__Deleted:** {url}__")

# --- Visual Dashboard Command ---
@Client.on_message(filters.command(["check", "stats", "dashboard"]) & filters.private)
async def stats_command(client, message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    
    wait_msg = await message.reply_text("🎨 **__Drawing your Dashboard ...__**")
    
    # 1. Fetch Data
    urls_data = await db.col.find({"user_id": user_id}).to_list(length=None)
    
    if not urls_data:
        return await wait_msg.edit_text("📂 **__List is Empty !\n— Use `/add` to monitor a site.__**")

    # 2. Generate Image
    try:
        photo_file = draw_dashboard(user_name, urls_data)
        
        await message.reply_photo(
            photo=photo_file,
            caption=f"📊 **__Live Status Report__**\n— __Generated for **{user_name}**__",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔄 Refresh", callback_data="ping_all")]
            ])
        )
        await wait_msg.delete()
    except Exception as e:
        await wait_msg.edit_text(f"⚠️ **__Error generating image:__**\n `{e}`")

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
        f"⏱ **__Monitor Interval Settings__**\n\n"
        f"**__Current: {current_time} Seconds__**"
    )
    
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("📝 Cʜᴀɴɢᴇ", callback_data="time_change"),
         InlineKeyboardButton("❌ Cʟᴏsᴇ", callback_data="time_close")]
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
            "⏳ **__Send new interval (seconds):__**",
            reply_markup=ForceReply(selective=True)
        )

# --- Handle Time Input ---
@Client.on_message(filters.reply & filters.user(ADMIN))
async def set_time_input(client, message):
    if message.reply_to_message and "Send new interval" in message.reply_to_message.text:
        try:
            new_time = int(message.text)
            if new_time < 10: 
                return await message.reply_text("⚠️ **__Minimum 10s !__**")
            
            await db.set_interval(new_time)
            await message.reply_text(f"✅ **__Interval set to {new_time}s.__**")
        except ValueError:
            await message.reply_text("⚠️ **__Numbers only.__**")
            
