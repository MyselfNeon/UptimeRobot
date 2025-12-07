# ---------------------------------------------------
# File Name: Commands.py
# Author: MyselfNeon
# GitHub: https://github.com/MyselfNeon/
# Telegram: https://t.me/MyelfNeon
# ---------------------------------------------------

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ForceReply
from .db import db
from MyselfNeon.monitor import check_url
import aiohttp

# --- Start Command ---
@Client.on_message(filters.command("start") & filters.private)
async def start_command(client, message):
    user_name = message.from_user.first_name
    
    # Premium Welcome Message
    text = (
        f"👋 **__Hello {user_name}__**\n\n"
        "🎉 **__Welcome to your Premium Uptime Monitor Bot. __**"
        "**__I am here to Protect your Web Urls from going to Sleep.__**\n\n"
        "⁉️ **__Features I Provide :__**\n"
        "– __I monitor your URLs 24/7 and Alert you Instantly if they go Down.__\n\n"
        "🛠 **__Control Menu :__**\n"
        "– **__Start Monitoring an URL** (/add Url)__\n"
        "– **__Stop Monitoring an URL** (/del Url)__\n"
        "– **__Live Status Dashboard** (/check)__\n"
        "– **__Set Monitor Interval** (/time)__"
    )
    
    # Removed the confusing Add/Del buttons. Kept Support/Updates for a clean look.
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
        return await message.reply_text("⚠️ **__Usage Error:__**\n\n__Please use:__ `/add https://your-site.com`")
    
    url = message.command[1]
    if not url.startswith("http"):
        return await message.reply_text("⛔ **__Invalid URL!__**\n__Ensure it starts with `http://` or `https://`__")
    
    if await db.is_url_exist(user_id, url):
        return await message.reply_text("⚠️ **__Already Exists!__**\n__This URL is already in your monitoring list.__")
    
    await db.add_url(user_id, url)
    await message.reply_text(
        f"✅ **__Successfully Added !!__**\n\n"
        f"🔗 **__URL:__** `{url}`\n"
        f"🚀 **__Status:__** __Monitoring Started...__"
    )

# --- Delete Url Command ---
@Client.on_message(filters.command("del") & filters.private)
async def delete_url_command(client, message):
    user_id = message.from_user.id

    if len(message.command) < 2:
        return await message.reply_text("⚠️ **__Usage Error:__**\n\n__Please use:__ `/del https://your-site.com`")
    
    url = message.command[1]
    if not await db.is_url_exist(user_id, url):
        return await message.reply_text("🤷‍♂️ **__Not Found!__**\n__You are not monitoring this URL.__")
    
    await db.remove_url(user_id, url)
    await message.reply_text(f"🛃 **__Deleted Successfully!__**\n\n🔗 **__URL:__** `{url}` has been removed.")

# --- Check / Dashboard Command ---
@Client.on_message(filters.command(["check", "stats", "list"]) & filters.private)
async def stats_command(client, message):
    user_id = message.from_user.id
    
    wait_msg = await message.reply_text("🔄 **__Connecting to Dashboard...__**")
    
    urls = await db.get_urls(user_id)
    if not urls:
        return await wait_msg.edit_text("📂 **__Your List is Empty!__**\n__Use__ `/add` __to add a website.__")
    
    text = f"📊 **__Your Monitoring Dashboard__**\n__User: {message.from_user.first_name}__\n\n"
    
    async with aiohttp.ClientSession() as session:
        for index, url in enumerate(urls):
            is_online, code = await check_url(session, url)
            status_icon = "🟢" if is_online else "🔴"
            status_text = "Online" if is_online else f"Offline ({code})"
            
            text += f"**{index + 1}.** `{url}`\n   ╚ **Status:** {status_text} {status_icon}\n\n"
    
    # New Single "Ping All" Button
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔔 Pɪɴɢ Aʟʟ Uʀʟs", callback_data="ping_all")]
    ])
    
    await wait_msg.edit_text(text, reply_markup=buttons, disable_web_page_preview=True)

# --- Ping All Callback ---
@Client.on_callback_query(filters.regex("ping_all"))
async def ping_all_callback(client, query):
    user_id = query.from_user.id
    await query.answer("⚡ Pinging all your URLs...", show_alert=False)
    
    urls = await db.get_urls(user_id)
    if not urls:
        return await query.message.edit_text("📂 **__No URLs to ping.__**")

    # Re-check all URLs manually
    text = f"📊 **__Manual Ping Results__**\n__User: {query.from_user.first_name}__\n\n"
    
    async with aiohttp.ClientSession() as session:
        for index, url in enumerate(urls):
            is_online, code = await check_url(session, url)
            status_icon = "🟢" if is_online else "🔴"
            status_text = "Online" if is_online else f"Offline ({code})"
            
            text += f"**{index + 1}.** `{url}`\n   ╚ **Status:** {status_text} {status_icon}\n\n"

    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔔 Pɪɴɢ Aʟʟ Uʀʟs", callback_data="ping_all")]
    ])
    
    await query.message.edit_text(text, reply_markup=buttons, disable_web_page_preview=True)


# --- Time Command ---
@Client.on_message(filters.command("time") & filters.private)
async def time_command(client, message):
    # Fetch current global interval
    current_time = await db.get_interval()
    
    text = (
        f"⏱ **__Monitor Interval Settings__**\n\n"
        f"**__Current Set Interval:__ {current_time} Seconds**\n"
        f"**__Status:__ Active**"
    )
    
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("📝 Cʜᴀɴɢᴇ", callback_data="time_change"),
         InlineKeyboardButton("❌ Cʟᴏsᴇ", callback_data="time_close")]
    ])
    
    await message.reply_text(text, reply_markup=buttons)

@Client.on_callback_query(filters.regex("^time_"))
async def time_callbacks(client, query):
    data = query.data
    
    if data == "time_close":
        await query.message.delete()
        
    elif data == "time_change":
        await query.answer()
        # Force Reply to ask for input
        await query.message.reply_text(
            "⏳ **__Send the new interval time in seconds.__**\n"
            "__(Example: 60 for 1 minute)__",
            reply_markup=ForceReply(selective=True)
        )

# --- HANDLE TIME INPUT ---
@Client.on_message(filters.reply & filters.private)
async def set_time_input(client, message):
    # Check if the reply is to our Time prompt
    if message.reply_to_message and message.reply_to_message.text and "Send the new interval" in message.reply_to_message.text:
        try:
            new_time = int(message.text)
            if new_time < 10: 
                return await message.reply_text("⚠️ **__Too Fast! Minimum interval is 10 seconds.__**")
            
            await db.set_interval(new_time)
            await message.reply_text(f"✅ **__Success! Monitoring interval set to {new_time}s.__**")
        except ValueError:
            await message.reply_text("⚠️ **__Invalid input. Please send a number.__**")
