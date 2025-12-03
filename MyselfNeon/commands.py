from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ForceReply
from pyrogram.errors import UserNotParticipant
from info import ADMIN, FORCE_SUB
from database import db
from MyselfNeon.monitor import url_states, check_url
import aiohttp

# --- FORCE SUBSCRIBE CHECK ---
async def is_subscribed(client, message):
    if not FORCE_SUB:
        return True
    try:
        chat_id = int(FORCE_SUB) if str(FORCE_SUB).lstrip('-').isdigit() else FORCE_SUB
        await client.get_chat_member(chat_id, message.from_user.id)
        return True
    except UserNotParticipant:
        return False
    except Exception as e:
        print(f"Force Sub Error: {e}")
        return True

async def force_sub_decorator(client, message):
    """
    Returns True if user is subscribed, False if not.
    If False, sends the Access Denied message.
    """
    if not await is_subscribed(client, message):
        try:
            chat_id = int(FORCE_SUB) if str(FORCE_SUB).lstrip('-').isdigit() else FORCE_SUB
            invite_link = await client.export_chat_invite_link(chat_id)
        except:
            invite_link = "https://t.me/NeonFiles"

        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔗 JOIN CHANNEL TO AUTHORIZE", url=invite_link)],
            [InlineKeyboardButton("🔄 TRY AGAIN", url=f"https://t.me/{client.me.username}?start=start")]
        ])
        
        await message.reply_text(
            f"⛔ **ACCESS DENIED** ⛔\n\n"
            f"You are not authorized to use this command. Join the update channel to authorize yourself.",
            reply_markup=buttons
        )
        return False
    return True

# --- START COMMAND ---
@Client.on_message(filters.command("start") & filters.private)
async def start_command(client, message):
    if not await force_sub_decorator(client, message):
        return

    interval = await db.get_interval()
    # CHANGED: Dynamic Name
    user_name = message.from_user.first_name
    
    text = (
        f"‣ Hᴇʟʟᴏ {user_name} 🇮🇳\n"
        "I ᴀᴍ Lᴀᴛᴇsᴛ Aᴅᴠᴀɴᴄᴇᴅ **Keep-Alive Monitor Bᴏᴛ**.\n"
        "Cᴏᴅᴇᴅ & Dᴇᴠᴇʟᴏᴘᴇᴅ ʙʏ NᴇᴏɴAɴᴜʀᴀɢ.\n"
        f"I ᴄᴀɴ **Trigger** ᴀɴᴅ **Monitor** Yᴏᴜʀ ᴡᴇʙsᴇʀᴠɪᴄᴇs ᴇᴠᴇʀʏ **{interval}** ѕᴇᴄᴏɴᴅs.\n\n"
        "**Commands:**\n"
        "/add `url` - Monitor a new URL\n"
        "/del `url` - Delete a URL\n"
        "/check - Manual check status\n"
        "/time - Set monitor interval"
    )
    
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("All Bots", callback_data="cb_all_bots"),
         InlineKeyboardButton("About Me", callback_data="cb_about_me")]
    ])
    
    await message.reply_text(text, reply_markup=buttons)

# --- CALLBACK HANDLERS (NAVIGATION) ---
@Client.on_callback_query(filters.regex("^cb_"))
async def cb_handler(client, query):
    data = query.data
    
    if data == "cb_all_bots":
        text = (
            "🤖 **My Other Bots**\n\n"
            "Here are some of the other bots and projects I have worked on.\n"
            "Check out the update channel for the latest news!"
        )
        buttons = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("UPDATE CHANNEL", url="https://t.me/NeonFiles"),
                InlineKeyboardButton("BACK", callback_data="cb_back")
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
                InlineKeyboardButton("SUPPORT", url="https://t.me/support"),
                InlineKeyboardButton("SOURCE CODE", url="https://myselfneon.github.io/neon/")
            ],
            [
                InlineKeyboardButton("DEVELOPER", url="https://t.me/myselfneon"),
                InlineKeyboardButton("BACK", callback_data="cb_back")
            ]
        ])
        await query.message.edit_text(text, reply_markup=buttons)

    elif data == "cb_back":
        interval = await db.get_interval()
        # CHANGED: Dynamic Name for Back Button
        user_name = query.from_user.first_name
        
        text = (
            f"‣ Hᴇʟʟᴏ {user_name} 🇮🇳\n"
            "I ᴀᴍ Lᴀᴛᴇsᴛ Aᴅᴠᴀɴᴄᴇᴅ **Keep-Alive Monitor Bᴏᴛ**.\n"
            "Cᴏᴅᴇᴅ & Dᴇᴠᴇʟᴏᴘᴇᴅ ʙʏ NᴇᴏɴAɴᴜʀᴀɢ.\n"
            f"I ᴄᴀɴ **Trigger** ᴀɴᴅ **Monitor** Yᴏᴜʀ ᴡᴇʙsᴇʀᴠɪᴄᴇs ᴇᴠᴇʀʏ **{interval}** ѕᴇᴄᴏɴᴅs.\n\n"
            "**Commands:**\n"
            "/add `url` - Monitor a new URL\n"
            "/del `url` - Delete a URL\n"
            "/check - Manual check status\n"
            "/time - Set monitor interval"
        )
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("All Bots", callback_data="cb_all_bots"),
             InlineKeyboardButton("About Me", callback_data="cb_about_me")]
        ])
        await query.message.edit_text(text, reply_markup=buttons)

# --- MONITORING COMMANDS ---

@Client.on_message(filters.command("add") & filters.private & filters.user(ADMIN))
async def add_url_command(client, message):
    if not await force_sub_decorator(client, message):
        return

    if len(message.command) < 2:
        return await message.reply_text("⚠️ Usage: `/add https://example.com`")
    
    url = message.command[1]
    if not url.startswith("http"):
        return await message.reply_text("⚠️ Invalid URL. Must start with http or https.")
    
    if await db.is_url_exist(url):
        return await message.reply_text("⚠️ URL is already being monitored.")
    
    await db.add_url(url)
    await message.reply_text(f"✅ Added to monitor: `{url}`")

@Client.on_message(filters.command("del") & filters.private & filters.user(ADMIN))
async def delete_url_command(client, message):
    if not await force_sub_decorator(client, message):
        return

    if len(message.command) < 2:
        return await message.reply_text("⚠️ Usage: `/del https://example.com`")
    
    url = message.command[1]
    if not await db.is_url_exist(url):
        return await message.reply_text("⚠️ This URL is not in the database.")
    
    await db.remove_url(url)
    if url in url_states:
        del url_states[url]
    await message.reply_text(f"🗑 Removed from monitor: `{url}`")

@Client.on_message(filters.command(["check", "stats"]) & filters.private & filters.user(ADMIN))
async def stats_command(client, message):
    if not await force_sub_decorator(client, message):
        return

    msg = await message.reply_text("🔄 Checking status of all services...")
    urls = await db.get_urls()
    
    text = "📊 **Current Status Report**\n\n"
    if not urls:
        text += "No URLs found in Database."
    else:
        async with aiohttp.ClientSession() as session:
            for url in urls:
                is_online, code = await check_url(session, url)
                icon = "🟢" if is_online else "🔴"
                status_text = "ONLINE" if is_online else f"OFFLINE ({code})"
                text += f"{icon} `{url}`\n   ╚ **{status_text}**\n\n"
                url_states[url] = 'online' if is_online else 'offline'
            
    await msg.edit_text(text)

# --- TIME COMMAND & HANDLERS ---
@Client.on_message(filters.command("time") & filters.private & filters.user(ADMIN))
async def time_command(client, message):
    if not await force_sub_decorator(client, message):
        return

    current_interval = await db.get_interval()
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("CHANGE TIME", callback_data="time_change")]
    ])
    await message.reply_text(f"⏱ **Monitoring Interval**\nCurrent: **{current_interval}s**", reply_markup=buttons)

@Client.on_callback_query(filters.regex("time_"))
async def time_callback(client, callback_query):
    data = callback_query.data
    if data == "time_change":
        await callback_query.answer()
        await callback_query.message.reply_text("📝 **Send new interval in seconds:**", reply_markup=ForceReply(selective=True))

@Client.on_message(filters.reply & filters.private & filters.user(ADMIN))
async def set_time_input(client, message):
    if not await force_sub_decorator(client, message):
        return

    if message.reply_to_message.text and "Send new interval" in message.reply_to_message.text:
        try:
            new_time = int(message.text)
            if new_time < 10: return await message.reply_text("⚠️ Minimum is 10s.")
            await db.set_interval(new_time)
            await message.reply_text(f"✅ Interval set to **{new_time}s**!")
        except ValueError:
            await message.reply_text("⚠️ Invalid number.")
