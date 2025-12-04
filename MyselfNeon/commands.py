from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ForceReply
from info import AUTH_USERS
from database import db
from MyselfNeon.monitor import url_states, check_url
import aiohttp

# --- AUTHORIZATION CHECK ---
async def check_auth(message):
    """
    Checks if the user is in the AUTH_USERS list.
    If not, sends the Access Denied message.
    """
    if message.from_user.id not in AUTH_USERS:
        await message.reply_text(
            "⛔ **ACCESS DENIED** ⛔\n\n"
            "You are not authorized to use this command. Only Admins and Auth Users are authorized to use the Commands !!"
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
        f"__Hello **{user_name}**__\n\n"
        "__I am Latest Advanced **Keep-Alive Monitor Bot**__"
        "__Coded by **@MyselfNeon**.__ "
        f"__I can **Trigger** and **Monitor** Your Webservices every **{interval}** seconds.__\n\n"
        "**Commands:**\n"
        "/add {url} - __Monitor a New URL__\n"
        "/del {url} - __Delete an URL__\n"
        "/check - __Manual check Status__\n"
        "/time - __Set Monitor Interval__"
    )
    
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("🤖 Aʟʟ Bᴏᴛs", callback_data="cb_all_bots"),
         InlineKeyboardButton("😎 Aʙᴏᴜᴛ Mᴇ", callback_data="cb_about_me")]
    ])
    
    await message.reply_text(text, reply_markup=buttons)

# --- CALLBACK HANDLERS (Navigation) ---
# Note: Callbacks also need auth check if you want to prevent clicking buttons
@Client.on_callback_query(filters.regex("^cb_"))
async def cb_handler(client, query):
    # Optional: Check auth on button clicks too
    if query.from_user.id not in AUTH_USERS:
        return await query.answer("⛔ Access Denied", show_alert=True)

    data = query.data
    
    if data == "cb_all_bots":
        text = (
            "🤖 **__My Other Bots__**\n\n"
            "**__Here are some of the other Bots and Projects I have worked on.__** "
            "**__Check the Update Channel for the Latest News !__**"
        )
        buttons = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🍟 Uᴘᴅᴀᴛᴇs", url="https://t.me/NeonFiles"),
                InlineKeyboardButton("⬅️ Bᴀᴄᴋ", callback_data="cb_back")
            ]
        ])
        await query.message.edit_text(text, reply_markup=buttons)
        
    elif data == "cb_about_me":
        text = (
            "<b><i>• Mʏ Nᴀᴍᴇ : <a href='https://t.me/Uptime_oBot'>Uptime RoBot</a>\n"
            "• Mʏ Bᴇsᴛ Fʀɪᴇɴᴅ : <a href='tg://settings'>Tʜɪs Sᴡᴇᴇᴛɪᴇ ❤️</a>\n"
            "• Dᴇᴠᴇʟᴏᴘᴇʀ : <a href='https://t.me/MyselfNeon'>@MyselfNeon</a>\n"
            "• Lɪʙʀᴀʀʏ : <a href='https://docs.pyrogram.org/'>Pʏʀᴏɢʀᴀᴍ</a>\n"
            "• Lᴀɴɢᴜᴀɢᴇ : <a href='https://www.python.org/download/releases/3.0/'>Pʏᴛʜᴏɴ 𝟹</a>\n"
            "• DᴀᴛᴀBᴀsᴇ : <a href='https://www.mongodb.com/'>Mᴏɴɢᴏ DB</a>\n"
            "• Bᴏᴛ Sᴇʀᴠᴇʀ : <a href='https://heroku.com'>Hᴇʀᴏᴋᴜ</a>\n"
            "• Bᴜɪʟᴅ Sᴛᴀᴛᴜs : ᴠ𝟸.0 [Sᴛᴀʙʟᴇ]</i></b>"
        )
        buttons = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🚨 Sᴜᴘᴘᴏʀᴛ", url="https://t.me/support"),
                InlineKeyboardButton("⁉️ Sᴏᴜʀᴄᴇ Cᴏᴅᴇ", url="https://myselfneon.github.io/neon/")
            ],
            [
                InlineKeyboardButton("👨‍💻 Dᴇᴠᴇʟᴏᴘᴇʀ", url="https://t.me/myselfneon"),
                InlineKeyboardButton("⬅️ Bᴀᴄᴋ", callback_data="cb_back")
            ]
        ])
        await query.message.edit_text(text, reply_markup=buttons)

    elif data == "cb_back":
        interval = await db.get_interval()
        user_name = query.from_user.first_name
        
        text = (
            f"__Hello **{user_name}**\n\n"
            "__I am Latest Advanced **Keep-Alive Monitor Bot**__"
            "__Coded by **@MyselfNeon**.__ "
            f"__I can **Trigger** and **Monitor**oBo'r Webservices every **{interval}** seconds.__\n\n"
            "**Commands:**\n"
            "/add {url} - __Monitor a New URL__\n"
            "/del {url} - __Delete an URL__\n"
            "/check - __Manual check Status__\n"
            "/time - __Set Monitor Interval__"
        )
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("🤖 Aʟʟ Bᴏᴛs", callback_data="cb_all_bots"),
             InlineKeyboardButton("😎 Aʙᴏᴜᴛ Mᴇ", callback_data="cb_about_me")]
        ])
        await query.message.edit_text(text, reply_markup=buttons)

# --- ADD URL COMMAND ---
@Client.on_message(filters.command("add") & filters.private)
async def add_url_command(client, message):
    if not await check_auth(message):
        return

    if len(message.command) < 2:
        return await message.reply_text("⚠️ **__Usage:** \n– /add https://example.com__")
    
    url = message.command[1]
    if not url.startswith("http"):
        return await message.reply_text("⚠️ **__Invalid URL.** \n– Must start with http or https.__")
    
    if await db.is_url_exist(url):
        return await message.reply_text("⚠️ __URL is already being Monitored.__")
    
    await db.add_url(url)
    await message.reply_text(f"✅ **__Added to Monitor:** \n– {url}__")

# --- DELETE URL COMMAND ---
@Client.on_message(filters.command("del") & filters.private)
async def delete_url_command(client, message):
    if not await check_auth(message):
        return

    if len(message.command) < 2:
        return await message.reply_text("⚠️ **__Usage:** \n– /del https://example.com__")
    
    url = message.command[1]
    if not await db.is_url_exist(url):
        return await message.reply_text("⚠️ __This URL is not in the Database.__")
    
    await db.remove_url(url)
    if url in url_states:
        del url_states[url]
    await message.reply_text(f"🚮 **__Removed from Monitor:** \n– {url}__")

# --- STATS COMMAND ---
@Client.on_message(filters.command(["check", "stats"]) & filters.private)
async def stats_command(client, message):
    if not await check_auth(message):
        return

    msg = await message.reply_text("🔄 **__Checking Status of all Services...__**")
    urls = await db.get_urls()
    
    text = "📊 **__Current Status Report__**\n\n"
    if not urls:
        text += "– __No URLs found in Database.__"
    else:
        async with aiohttp.ClientSession() as session:
            for index, url in enumerate(urls):
                is_online, code = await check_url(session, url)
                
                # Determine status text and icon
                if is_online:
                    status_text = "ONLINE"
                    icon = "🟢"
                else:
                    status_text = f"OFFLINE ({code})" if isinstance(code, int) and code not in (429, 200) else "OFFLINE"
                    icon = "🔴"
                
                # Format the line as requested: 01. url \n   ╚ STATUS ICON
                text += f"{index + 1:02d}. `{url}`\n   ╚ {status_text} {icon}\n\n"
                
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
    await message.reply_text(f"⏱ **__Monitoring Interval__**\n\n__– **Current Time :__ {current_interval}s**", reply_markup=buttons)

@Client.on_callback_query(filters.regex("time_"))
async def time_callback(client, callback_query):
    # Check Auth on callback
    if callback_query.from_user.id not in AUTH_USERS:
        return await callback_query.answer("⛔ Access Denied", show_alert=True)

    data = callback_query.data
    if data == "time_change":
        await callback_query.answer()
        await callback_query.message.reply_text("📝 **Send new interval in seconds:**", reply_markup=ForceReply(selective=True))

@Client.on_message(filters.reply & filters.private)
async def set_time_input(client, message):
    if not await check_auth(message):
        return
        
    if message.reply_to_message.text and "Send new interval" in message.reply_to_message.text:
        try:
            new_time = int(message.text)
            if new_time < 10: return await message.reply_text("⚠️ **__Minimum is 10s.__**")
            await db.set_interval(new_time)
            await message.reply_text(f"✅ **__Interval set to {new_time}s !__**")
        except ValueError:
            await message.reply_text("⚠️ **__Invalid Number.__**")
