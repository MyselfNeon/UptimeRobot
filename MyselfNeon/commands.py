from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ForceReply
from info import AUTH_USERS
from database import db
from MyselfNeon.monitor import url_states, check_url
import aiohttp

async def check_auth(message):
    """
    Checks if the user is in the AUTH_USERS list.
    If not, sends the Access Denied message.
    """
    if message.from_user.id not in AUTH_USERS:
        await message.reply_text(
            "⛔ **ACCESS DENIED** ⛔\n\n"
            "__You are not Authorized to use these Command. Only Admins and Auth Users are Authorized to use these Commands !!__"
        )
        return False
    return True

# --- START COMMAND ---
@Client.on_message(filters.command("start") & filters.private)
async def start_command(client, message):
    # 1. Authorization Check
    if not await check_auth(message):
        return

    interval = await db.get_interval()
    user_name = message.from_user.first_name
    
    text = (
        f"__Hello **{user_name}**__\n"
        "__I am Latest Advanced Keep-Alive__\n"
        "__Monitor Bot, Coded by **@MyselfNeon**__\n"
        f"__I can Trigger and Monitor your Websites every **{interval}** Seconds ⏰.__\n\n"
        "**__My Commands :__**\n"
        "/add (url) - __Monitor a new URL__\n"
        "/del (url) - __Delete an URL__\n"
        "/check - __Manual Check Status__\n"
        "/time - __Set Monitor Interval__"
    )
    
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("🤖 Aʟʟ Bᴏᴛs", callback_data="cb_all_bots"),
         InlineKeyboardButton("😎 Aʙᴏᴜᴛ Mᴇ", callback_data="cb_about_me")]
    ])
    
    await message.reply_text(text, reply_markup=buttons)

# --- CALLBACK HANDLERS (Navigation) ---
@Client.on_callback_query(filters.regex("^cb_"))
async def cb_handler(client, query):
    # Optional: Check auth on button clicks too
    if query.from_user.id not in AUTH_USERS:
        return await query.answer("⛔ Access Denied", show_alert=True)

    data = query.data
    
    if data == "cb_all_bots":
        text = (
            "🤖 **__My Other Bots__**\n\n"
            "Here are some of the other bots and projects I have worked on.\n"
            "Check out the update channel for the latest news!"
        )
        buttons = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("📝 Uᴘᴅᴀᴛᴇs", url="https://t.me/NeonFiles"),
                InlineKeyboardButton("🔙 Bᴀᴄᴋ", callback_data="cb_back")
            ]
        ])
        await query.message.edit_text(text, reply_markup=buttons)
        
    elif data == "cb_about_me":
        text = (
            "<i><b>• Mʏ Nᴀᴍᴇ : <a href='https://t.me/Uptime_oBot'>Uptime Robot</a>\n"
            "• Mʏ Bᴇsᴛ Fʀɪᴇɴᴅ : <a href='tg://settings'>Tʜɪs Sᴡᴇᴇᴛɪᴇ ❤️</a>\n"
            "• Dᴇᴠᴇʟᴏᴘᴇʀ : <a href='https://t.me/MyselfNeon'>@MyselfNeon</a>\n"
            "• Lɪʙʀᴀʀʏ : <a href='https://docs.pyrogram.org/'>Pʏʀᴏɢʀᴀᴍ</a>\n"
            "• Lᴀɴɢᴜᴀɢᴇ : <a href='https://www.python.org/download/releases/3.0/'>Pʏᴛʜᴏɴ 𝟹</a>\n"
            "• DᴀᴛᴀBᴀsᴇ : <a href='https://www.mongodb.com/'>Mᴏɴɢᴏ DB</a>\n"
            "• Bᴏᴛ Sᴇʀᴠᴇʀ : <a href='https://heroku.com'>Hᴇʀᴏᴋᴜ</a>\n"
            "• Bᴜɪʟᴅ Sᴛᴀᴛᴜs : ᴠ𝟸.𝟽 [Sᴛᴀʙʟᴇ]</i></b>"
        )
        buttons = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🫡 Sᴜᴘᴘᴏʀᴛ", url="https://t.me/+o1s-8MppL2syYTI9"),
                InlineKeyboardButton("🛐 Sᴏᴜʀᴄᴇ Cᴏᴅᴇ", url="https://myselfneon.github.io/neon/")
            ],
            [
                InlineKeyboardButton("👨‍💻 Dᴇᴠᴇʟᴏᴘᴇʀ", url="https://t.me/myselfneon"),
                InlineKeyboardButton("🔙 Bᴀᴄᴋ", callback_data="cb_back")
            ]
        ])
        await query.message.edit_text(text, reply_markup=buttons)

    elif data == "cb_back":
        interval = await db.get_interval()
        user_name = query.from_user.first_name
        
        text = (
            f"__Hello **{user_name}**__\n"
            "__I am Latest Advanced Keep-Alive__\n"
            "__Monitor Bot, Coded by **@MyselfNeon**__\n"
            f"__I can Trigger and Monitor your Websites every **{interval}** Seconds ⏰.__\n\n"
            "**__Commands:__**\n"
            "/add (url) - __Monitor a new URL__\n"
            "/del (url) - __Delete an URL__\n"
            "/check - __Manual check Status__\n"
            "/time - __Set monitor Interval__"
        )
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("All Bots", callback_data="cb_all_bots"),
             InlineKeyboardButton("About Me", callback_data="cb_about_me")]
        ])
        await query.message.edit_text(text, reply_markup=buttons)

# --- ADD URL COMMAND ---
@Client.on_message(filters.command("add") & filters.private)
async def add_url_command(client, message):
    if not await check_auth(message):
        return

    if len(message.command) < 2:
        return await message.reply_text("⚠️ **__Usage:** /add https://example.com__")
    
    url = message.command[1]
    if not url.startswith("http"):
        return await message.reply_text("⚠️ **__Invalid URL.**\nMust start with http or https.__")
    
    if await db.is_url_exist(url):
        return await message.reply_text("⚠️ __URL is Already being Monitored.__")
    
    await db.add_url(url)
    await message.reply_text(f"✅ **__Added to Monitor :**\n– {url}__")

# --- DELETE URL COMMAND ---
@Client.on_message(filters.command("del") & filters.private)
async def delete_url_command(client, message):
    if not await check_auth(message):
        return

    if len(message.command) < 2:
        return await message.reply_text("⚠️ **__Usage:** /del https://example.com__")
    
    url = message.command[1]
    if not await db.is_url_exist(url):
        return await message.reply_text("⚠️ __This URL is not in the Database.__")
    
    await db.remove_url(url)
    if url in url_states:
        del url_states[url]
    await message.reply_text(f"🚮 **__Removed from Monitor__** : \n– __{url}__")

# --- STATS COMMAND ---
@Client.on_message(filters.command(["check", "stats"]) & filters.private)
async def stats_command(client, message):
    if not await check_auth(message):
        return

    msg = await message.reply_text("🔄 **__Checking status of all Services...__**")
    urls = await db.get_urls()
    
    text = "📊 **__Current Status Report__**\n\n"
    if not urls:
        text += "__No URLs found in Database.__"
    else:
        async with aiohttp.ClientSession() as session:
            for url in urls:
                is_online, code = await check_url(session, url)
                icon = "🟢" if is_online else "🔴"
                status_text = "ONLINE" if is_online else f"OFFLINE ({code})"
                text += f"{icon} `{url}`\n   ╚ **{status_text}**\n\n"
                url_states[url] = 'online' if is_online else 'offline'
            
    await msg.edit_text(text)

# --- Time Command ---
@Client.on_message(filters.command("time") & filters.private)
async def time_command(client, message):
    if not await check_auth(message):
        return

    current_interval = await db.get_interval()
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("⏰ Cʜᴀɴɢᴇ Tɪᴍᴇ", callback_data="time_change")]
    ])
    await message.reply_text(f"🕓 **__Monitoring Interval__**\➠ __Current Time : **{current_interval}s**__", reply_markup=buttons)

@Client.on_callback_query(filters.regex("time_"))
async def time_callback(client, callback_query):
    # Check Auth on callback
    if callback_query.from_user.id not in AUTH_USERS:
        return await callback_query.answer("⛔ Access Denied", show_alert=True)

    data = callback_query.data
    if data == "time_change":
        await callback_query.answer()
        await callback_query.message.reply_text("📝 **__Send new Interval in Seconds:__**", reply_markup=ForceReply(selective=True))

@Client.on_message(filters.reply & filters.private)
async def set_time_input(client, message):
    if not await check_auth(message):
        return
        
    if message.reply_to_message.text and "Send new interval" in message.reply_to_message.text:
        try:
            new_time = int(message.text)
            if new_time < 10: return await message.reply_text("⚠️ **__Minimum is 10s.__**")
            await db.set_interval(new_time)
            await message.reply_text(f"✅ **__Interval set to {new_time} !__**")
        except ValueError:
            await message.reply_text("⚠️ **__Invalid Number.__**")
