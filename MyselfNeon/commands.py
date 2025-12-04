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
            "🤖 **My Other Bots**\n\n"
            "__Here are some of the other bots and projects I have worked on.__"
            "__Check out the update channel for the latest news!__"
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
            "• Mʏ Nᴀᴍᴇ : Auto Filter™\n"
            "• Mʏ Bᴇsᴛ Fʀɪᴇɴᴅ : Tʜɪs Sᴡᴇᴇᴛɪᴇ ❤️\n" 
            "• Dᴇᴠᴇʟᴏᴘᴇʀ : @MʏsᴇʟғNᴇᴏɴ\n" 
            "• Lɪʙʀᴀʀʏ : Pʏʀᴏɢʀᴀᴍ\n" 
            "• Lᴀɴɢᴜᴀɢᴇ : Pʏᴛʜᴏɴ 𝟹\n" 
            "• DᴀᴛᴀBᴀsᴇ : Mᴏɴɢᴏ DB\n" 
            "• Bᴏᴛ Sᴇʀᴠᴇʀ : Hᴇʀᴏᴋᴜ\n" 
            "• Bᴜɪʟᴅ Sᴛᴀᴛᴜs : ᴠ𝟸.𝟽.𝟷 [Sᴛᴀʙʟᴇ]"
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

# --- TIME COMMAND ---
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
            if new_time < 10: return await message.reply_text("⚠️ Minimum is 10s.")
            await db.set_interval(new_time)
            await message.reply_text(f"✅ Interval set to **{new_time}s**!")
        except ValueError:
            await message.reply_text("⚠️ Invalid number.")
