from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ForceReply
# UPDATED IMPORT: Uses local db.py
from .db import db
from MyselfNeon.monitor import check_url
import aiohttp

# --- START COMMAND ---
@Client.on_message(filters.command("start") & filters.private)
async def start_command(client, message):
    user_name = message.from_user.first_name
    
    text = (
        f"👋 **__Hello {user_name}!__**\n\n"
        "🤖 **__I am your Premium Keep-Alive Monitor.__**\n"
        "✨ **__I will keep your projects active 24/7 with zero downtime.__**\n\n"
        "🛠 **__My Commands:__**\n"
        "🔸 `/add` __<url>__ - **__Add a URL to Monitor__**\n"
        "🔸 `/del` __<url>__ - **__Remove a URL__**\n"
        "🔸 `/check` - **__View Your Dashboard__**\n"
    )
    
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Aᴅᴅ Uʀʟ", switch_inline_query_current_chat="/add "),
         InlineKeyboardButton("🗑 Dᴇʟ Uʀʟ", switch_inline_query_current_chat="/del ")],
        [InlineKeyboardButton("🆘 Sᴜᴘᴘᴏʀᴛ", url="https://t.me/MyselfNeon"),
         InlineKeyboardButton("📢 Uᴘᴅᴀᴛᴇs", url="https://t.me/NeonFiles")]
    ])
    
    await message.reply_text(text, reply_markup=buttons)

# --- ADD URL COMMAND ---
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
        f"✅ **__Successfully Added!__**\n\n"
        f"🔗 **__URL:__** `{url}`\n"
        f"🚀 **__Status:__** __Monitoring Started...__"
    )

# --- DELETE URL COMMAND ---
@Client.on_message(filters.command("del") & filters.private)
async def delete_url_command(client, message):
    user_id = message.from_user.id

    if len(message.command) < 2:
        return await message.reply_text("⚠️ **__Usage Error:__**\n\n__Please use:__ `/del https://your-site.com`")
    
    url = message.command[1]
    if not await db.is_url_exist(user_id, url):
        return await message.reply_text("🤷‍♂️ **__Not Found!__**\n__You are not monitoring this URL.__")
    
    await db.remove_url(user_id, url)
    await message.reply_text(f"🗑 **__Deleted Successfully!__**\n\n🔗 **__URL:__** `{url}` has been removed.")

# --- STATS / CHECK COMMAND ---
@Client.on_message(filters.command(["check", "stats", "list"]) & filters.private)
async def stats_command(client, message):
    user_id = message.from_user.id
    
    # Send waiting message
    wait_msg = await message.reply_text("🔄 **__Fetching your Dashboard... Please wait.__**")
    
    urls = await db.get_urls(user_id)
    
    if not urls:
        return await wait_msg.edit_text(
            "📂 **__Your List is Empty!__**\n\n__Use__ `/add` __to start monitoring your projects.__"
        )
    
    text = f"📊 **__Your Monitoring Dashboard__**\n__User: {message.from_user.first_name}__\n\n"
    
    async with aiohttp.ClientSession() as session:
        for index, url in enumerate(urls):
            is_online, code = await check_url(session, url)
            
            if is_online:
                status_icon = "🟢"
                status_text = "Online"
            else:
                status_icon = "🔴"
                status_text = f"Offline ({code})"
            
            text += (
                f"**{index + 1}.** `{url}`\n"
                f"   ╚ **Status:** {status_text} {status_icon}\n\n"
            )
    
    # Add Refresh Button
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Rᴇғʀᴇsʜ Sᴛᴀᴛᴜs", callback_data="refresh_stats")],
        [InlineKeyboardButton("✖️ Cʟᴏsᴇ", callback_data="close_msg")]
    ])
    
    await wait_msg.edit_text(text, reply_markup=buttons, disable_web_page_preview=True)

# --- CALLBACK HANDLERS (Refresh & Close) ---
@Client.on_callback_query(filters.regex("refresh_stats"))
async def refresh_stats(client, query):
    user_id = query.from_user.id
    await query.answer("🔄 Refreshing...", show_alert=False)
    
    urls = await db.get_urls(user_id)
    if not urls:
        return await query.message.edit_text("📂 **__Your List is Empty!__**")

    text = f"📊 **__Your Monitoring Dashboard__**\n__User: {query.from_user.first_name}__\n\n"
    
    async with aiohttp.ClientSession() as session:
        for index, url in enumerate(urls):
            is_online, code = await check_url(session, url)
            if is_online:
                status_icon = "🟢"
                status_text = "Online"
            else:
                status_icon = "🔴"
                status_text = f"Offline ({code})"
            
            text += f"**{index + 1}.** `{url}`\n   ╚ **Status:** {status_text} {status_icon}\n\n"
            
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Rᴇғʀᴇsʜ Sᴛᴀᴛᴜs", callback_data="refresh_stats")],
        [InlineKeyboardButton("✖️ Cʟᴏsᴇ", callback_data="close_msg")]
    ])
    
    try:
        await query.message.edit_text(text, reply_markup=buttons, disable_web_page_preview=True)
    except:
        pass

@Client.on_callback_query(filters.regex("close_msg"))
async def close_msg(client, query):
    await query.message.delete()
