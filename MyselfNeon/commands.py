# --------------------------------------------------
# File Name: Commands.py
# Author: MyselfNeon
# GitHub: https://github.com/MyselfNeon/
# Telegram: https://t.me/MyelfNeon
# ---------------------------------------------------

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ForceReply
from .db import db
from info import ADMIN

# --- Start Command ---
@Client.on_message(filters.command("start") & filters.private)
async def start_command(client, message):
    # Use chat.first_name to be safe across callbacks/commands
    user_name = message.chat.first_name
    
    text = (
        f">👋 **__Hello {user_name}__**\n\n"
        "🎉 **__Welcome to your Premium Uptime Monitor Bot.__**\n"
        "**__I am here to Protect your Web Urls from going to Sleep.__**\n\n"
        "⁉️ **__Features I Provide :__**\n"
        "– __I monitor your URLs 24/7 and Alert you Instantly if they go Down.__\n\n"
        "🛠 **__Control Menu :__**\n"
        "> **__Start Monitoring:__** `/add Url`\n"
        "> **__Stop Monitoring:__** `/del Url`\n"
        "> **__Live Dashboard:__** `/check`\n"
        "> **__Set Interval:__** `/time`"
    )
    
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("🆘 Sᴜᴘᴘᴏʀᴛ", url="https://t.me/MyselfNeon"),
         InlineKeyboardButton("📢 Uᴘᴅᴀᴛᴇs", url="https://t.me/NeonFiles")]
    ])
    
    await message.reply_text(text, reply_markup=buttons)

# --- Add Url Command ---
@Client.on_message(filters.command("add") & filters.private)
async def add_url_command(client, message):
    user_id = message.chat.id # Fixed: Use chat.id

    if len(message.command) < 2:
        return await message.reply_text("⚠️ **__Usage:__** `/add https://your-site.com`")
    
    url = message.command[1]
    if not url.startswith("http"):
        return await message.reply_text("⛔ **__Invalid URL!__**\n__Must start with `http://` or `https://`__")
    
    if await db.is_url_exist(user_id, url):
        return await message.reply_text("⚠️ **__URL Already Exists!__**")
    
    await db.add_url(user_id, url)
    await message.reply_text(
        f"✅ **__New Added!__**\n\n"
        f"🔗 **__URL:__** `{url}`\n"
        f"🚀 **__Status:__** **__Monitoring Started...__**"
    )

# --- Delete Url Command ---
@Client.on_message(filters.command("del") & filters.private)
async def delete_url_command(client, message):
    user_id = message.chat.id # Fixed: Use chat.id

    if len(message.command) < 2:
        return await message.reply_text("⚠️ **__Usage:__** `/del https://your-site.com`")
    
    url = message.command[1]
    if not await db.is_url_exist(user_id, url):
        return await message.reply_text("🤷‍♂️ **__Not Found!__**")
    
    await db.remove_url(user_id, url)
    await message.reply_text(f"🗑 **__Deleted:__** `{url}`")

# --- Stats / Dashboard Command ---
@Client.on_message(filters.command(["check", "stats", "dashboard", "list"]) & filters.private)
async def stats_command(client, message):
    # CRITICAL FIX: Use message.chat.id instead of message.from_user.id
    # When triggered by callback, from_user is the BOT. chat.id is YOU.
    user_id = message.chat.id
    user_name = message.chat.first_name
    
    wait_msg = await message.reply_text("🔄 **__Fetching Data...__**")
    
    urls_data = await db.col.find({"user_id": user_id}).to_list(length=None)
    
    if not urls_data:
        return await wait_msg.edit_text("📂 **__List is Empty!__**\n__Use__ `/add` __to monitor a site.__")
    
    text = f"📊 **__Your Monitoring Dashboard__**\n__User: {user_name}__\n\n"
    
    for index, data in enumerate(urls_data):
        url = data.get('url', 'Unknown')
        status = data.get('status', 'Unknown')
        latency = data.get('response_time', 0)
        
        # Calculate Uptime Percentage
        total = data.get('total_checks', 1)
        up_count = data.get('uptime_count', 0)
        percentage = round((up_count / total) * 100, 2) if total > 0 else 0
        
        # Formatting
        is_online = status == 200
        icon = "🟢" if is_online else "🔴"
        status_text = "Online" if is_online else f"Offline ({status})"
        
        text += (
            f"**{index + 1}.** `{url}`\n"
            f"   **╚ Status:** {status_text} {icon}\n"
            f"   **╚ Ping:** `{latency}ms` ⚡\n"
            f"   **╚ Uptime:** `{percentage}%` 📈\n\n"
        )
    
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Refresh Stats", callback_data="ping_all")]
    ])
    
    await wait_msg.edit_text(text, reply_markup=buttons, disable_web_page_preview=True)

# --- Refresh Callback ---
@Client.on_callback_query(filters.regex("ping_all"))
async def ping_all_callback(client, query):
    await query.answer("🔄 Refreshing...")
    # Pass the message attached to the button (query.message)
    # Since we switched to chat.id above, this will now work correctly!
    await stats_command(client, query.message)

# --- Time Command ---
@Client.on_message(filters.command("time") & filters.private)
async def time_command(client, message):
    if message.chat.id != ADMIN:
        return await message.reply_text("⛔ **__Access Denied!__**\n__This command is for Admins only.__")

    current_time = await db.get_interval()
    
    text = (
        f"⏱ **__Monitor Interval Settings__**\n\n"
        f"**__Current: {current_time} Seconds__**"
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
            "⏳ **__Send new interval (seconds):__**",
            reply_markup=ForceReply(selective=True)
        )

# --- Handle Time Input ---
@Client.on_message(filters.reply & filters.private)
async def set_time_input(client, message):
    if message.chat.id != ADMIN:
        return

    if message.reply_to_message and "Send new interval" in message.reply_to_message.text:
        try:
            new_time = int(message.text)
            if new_time < 10: 
                return await message.reply_text("⚠️ **__Minimum 10s!__**")
            
            await db.set_interval(new_time)
            await message.reply_text(f"✅ **__Interval set to {new_time}s.__**")
        except ValueError:
            await message.reply_text("⚠️ **__Numbers only.__**")
