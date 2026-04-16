# --- Commands.py ---
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, BotCommand
from pyrogram.enums import ButtonStyle
from .db import db
from info import ADMIN
import asyncio
import aiohttp
import time

# --- STANDALONE CHECK (Prevents Freezing) ---
async def quick_check(url):
    timeout = aiohttp.ClientTimeout(total=10)
    start = time.perf_counter()
    try:
        async with aiohttp.ClientSession() as session:
            async with session.head(url, timeout=timeout, allow_redirects=True) as response:
                latency = int((time.perf_counter() - start) * 1000)
                if response.status == 429: return True, 429, latency 
                if response.status >= 400: raise ValueError("Force GET")
                return True, response.status, latency
    except:
        try:
            async with aiohttp.ClientSession() as session:
                start_get = time.perf_counter()
                async with session.get(url, timeout=timeout) as response:
                    latency = int((time.perf_counter() - start_get) * 1000)
                    return True, response.status, latency
        except Exception:
            return False, "Error", 0

# --- Helper: Generate Dashboard UI ---
async def get_dashboard(user_id, page=1):
    limit = 6
    urls, total_count = await db.get_urls_paginated(user_id, page, limit)
    
    if not urls and page == 1:
        return "📂 **__List is Empty!__**\n__Use /add to start.__", None
    
    text = f"📊 **__Dashboard (Page {page})__**\n__Total Monitors: {total_count}__\n\n"
    
    for i, data in enumerate(urls):
        idx = (page - 1) * limit + i + 1
        status = data.get('status', 'PENDING')
        s_icon = {
            "ONLINE": "🟢", "DOWN": "🔴", "SLOW": "🟡", 
            "PAUSED": "⛔️", "PENDING": "⏳", "RATE-LIMITED": "⚠️"
        }.get(status, "❓")
        
        resp = data.get('response_time', 0)
        uptime_pct = 0
        if data.get('total_checks', 0) > 0:
            uptime_pct = round((data['uptime_count'] / data['total_checks']) * 100, 1)

        text += (
            f"**__{idx}. `{data['url']}`__**\n"
            f"   **╚** [{s_icon}]({data['url']}) __**{status}** ⚡ {resp}ms 📈 {uptime_pct}%__\n\n"
        )
    
    buttons = []
    nav_row = []
    if page > 1:
        nav_row.append(InlineKeyboardButton("⬅️", callback_data=f"list_page_{page-1}", icon_custom_emoji_id=5258096772776991776, style=ButtonStyle.PRIMARY))
    nav_row.append(InlineKeyboardButton("🔄", callback_data=f"force_refresh_{page}", icon_custom_emoji_id=5258331647358540449, style=ButtonStyle.DANGER))
    if (page * limit) < total_count:
        nav_row.append(InlineKeyboardButton("➡️", callback_data=f"list_page_{page+1}", icon_custom_emoji_id=5258096772776991776, style=ButtonStyle.PRIMARY))
    if nav_row:
        buttons.append(nav_row)
    
    return text, InlineKeyboardMarkup(buttons)

# --- Commands ---
@Client.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message):
    admin_ids = ADMIN if isinstance(ADMIN, list) else [ADMIN]
    
    if message.from_user.id not in admin_ids:
        await message.reply_text(
            "🔒 **__Private Bot__**\n\n"
            "This bot is privately managed. You are not authorized to access the dashboard.\n"
            "__Only the owner can add or manage URLs.__"
        )
        return

    text = (
        "🔗 **__Professional Uptime Monitor__**\n\n"
        "**__I use Adaptive Intelligence Bot to Monitor your Websites 🌐👀__**\n"
        "**__Created By @MyselfNeon 💖__**\n\n"
        "**__Commands:__**\n"
        "__/add url name emoji - Website__\n"
        "__/add url name emoji username - Bot__\n"
        "__( Name can have spaces !! )__\n\n"
        "__/del url – Remove an URL__\n"
        "__/list – View URLs Dashboard__\n"
        "__/setstatus – Change Dynamic Status Target__"
    )
    await message.reply_text(text)

@Client.on_message(filters.command("add") & filters.private & filters.user(ADMIN))
async def add_cmd(client, message):
    args = message.command
    usage_text = "⚠️ **__Usage Bot or Website :__**\n__/add url name emoji__\n__/add url name emoji @username__"

    if len(args) < 4:
        await message.reply_text(usage_text)
        return

    user_id = message.chat.id
    url = args[1]
    
    if args[-1].startswith("@"):
        username = args[-1]
        emoji = args[-2]
        name_parts = args[2:-2]
    else:
        username = None
        emoji = args[-1]
        name_parts = args[2:-1]

    name = " ".join(name_parts)

    if not name or not emoji:
        await message.reply_text(usage_text)
        return
    
    if not url.startswith(("http://", "https://")):
        await message.reply_text("⛔️ **__URL must start with http/https__**")
        return
        
    if await db.is_url_exist(user_id, url):
        await message.reply_text("⚠️ **__URL already exists.__**")
        return
        
    success, inserted_id = await db.add_url(user_id, url, name, emoji, username)
    
    if success:
        type_str = "🤖 Bot" if username else "🌐 Website"
        msg = await message.reply_text(
            f"✅ **__Added:__** `{url}`\n"
            f"📛 **__Name:** {name}__\n"
            f"🎨 **__Icon:__** `{emoji}`\n"
            f"🏷 **__Type:** {type_str}__\n"
            f"**__State: Pending__**"
        )
        
        is_up, code, latency = await quick_check(url)
        
        result_data = {
            'is_up': is_up, 'latency': latency, 'code': code,
            'consecutive_failures': 0, 'check_interval': 60,
            'current_status': 'PENDING'
        }
        new_status = await db.update_adaptive_result(inserted_id, result_data)
        
        icon = {
            "ONLINE": "🟢", "SLOW": "🟡", "DOWN": "🔴", 
            "PAUSED": "⛔️", "RATE-LIMITED": "⚠️"
        }.get(new_status, "❓")
        
        text = (
            f"{icon} **__Monitor Alert: {new_status}__**\n\n"
            f"🔗 **__URL:__** `{url}`\n"
            f"📛 **__Name:** {name}__\n"
            f"📝 **__Info:** {code}__\n"
            f"⚡ **__Latency:** {latency}ms__\n"
        )
        await msg.edit_text(text, disable_web_page_preview=True)
    else:
        await message.reply_text(f"❌ **__Error Adding URL.__**")
        
@Client.on_message(filters.command("addp") & filters.private & filters.user(ADMIN))
async def addp_cmd(client, message):
    args = message.command
    usage_text = "⚠️ **__Usage for Private Monitor:__**\n__/addp url__"

    if len(args) < 2:
        await message.reply_text(usage_text)
        return

    user_id = message.chat.id
    url = args[1]

    if not url.startswith(("http://", "https://")):
        await message.reply_text("⛔️ **__URL must start with http/https__**")
        return
        
    if await db.is_url_exist(user_id, url):
        await message.reply_text("⚠️ **__URL already exists.__**")
        return
        
    # Auto-fill dummy values for the database, but set is_public to False!
    success, inserted_id = await db.add_url(
        user_id=user_id, 
        url=url, 
        name="Private", 
        emoji="🔒", 
        username=None, 
        is_public=False
    )
    
    if success:
        msg = await message.reply_text(
            f"🤫 **__Private URL Added:__** `{url}`\n"
            f"**__State: Pending__**\n"
            f"*(This will monitor normally but hide from the public channel)*"
        )
        
        is_up, code, latency = await quick_check(url)
        
        result_data = {
            'is_up': is_up, 'latency': latency, 'code': code,
            'consecutive_failures': 0, 'check_interval': 60,
            'current_status': 'PENDING'
        }
        new_status = await db.update_adaptive_result(inserted_id, result_data)
        
        icon = {
            "ONLINE": "🟢", "SLOW": "🟡", "DOWN": "🔴", 
            "PAUSED": "⛔️", "RATE-LIMITED": "⚠️"
        }.get(new_status, "❓")
        
        text = (
            f"{icon} **__Private Monitor Alert: {new_status}__**\n\n"
            f"🔗 **__URL:__** `{url}`\n"
            f"📝 **__Info:** {code}__\n"
            f"⚡ **__Latency:** {latency}ms__\n"
            f"🤫 *(Hidden from public status)*"
        )
        await msg.edit_text(text, disable_web_page_preview=True)
    else:
        await message.reply_text(f"❌ **__Error Adding URL.__**")

@Client.on_message(filters.command("del") & filters.private & filters.user(ADMIN))
async def del_cmd(client, message):
    if len(message.command) < 2:
        await message.reply_text("⚠️ **__Usage: /del https://google.com__**")
        return
    await db.remove_url(message.chat.id, message.command[1])
    await message.reply_text("🗑 **__URL Deleted.__**")

@Client.on_message(filters.command(["list", "check", "stats"]) & filters.private & filters.user(ADMIN))
async def list_cmd(client, message):
    text, markup = await get_dashboard(message.chat.id, 1)
    await message.reply_text(text, reply_markup=markup, disable_web_page_preview=True)

# --- Dynamic Status Commands ---
@Client.on_message(filters.command("setstatus") & filters.private & filters.user(ADMIN))
async def set_status_cmd(client, message):
    args = message.command
    
    # Check if the user provided exactly 3 parts
    if len(args) != 3:
        await message.reply_text("⚠️ **__Usage: /setstatus -1001234567 890__**")
        return

    try:
        channel_id = int(args[1])
        msg_id = int(args[2])
        
        # 1. Save to Database
        await db.set_status_config(channel_id, msg_id)
        
        # 2. Instantly trigger the monitor loop! 
        db.status_event.set()
        
        # 3. Send a beautiful success confirmation
        markup = InlineKeyboardMarkup([[
            InlineKeyboardButton("✅ Success", callback_data="status_success", icon_custom_emoji_id=5258503720928288433, style=ButtonStyle.SUCCESS)
        ]])
        await message.reply_text(
            f"✅ **__Dynamic Status Updated Successfully!__**\n\n"
            f"📢 **__Channel ID:__** `{channel_id}`\n"
            f"📌 **__Message ID:__** `{msg_id}`\n\n"
            f"⚡ __Live message pushed & 5-minute cycle restarted!__",
            reply_markup=markup
        )
        
    except ValueError:
        await message.reply_text("⚠️ **__Format incorrect! Channel ID and Message ID must be numbers.__**")

# --- Callbacks ---
@Client.on_callback_query(filters.regex(r"^list_page_(\d+)") & filters.user(ADMIN))
async def page_callback(client, query):
    page = int(query.matches[0].group(1))
    text, markup = await get_dashboard(query.message.chat.id, page)
    try: await query.edit_message_text(text, reply_markup=markup, disable_web_page_preview=True)
    except: await query.answer("Loaded!")

@Client.on_callback_query(filters.regex(r"^force_refresh_(\d+)") & filters.user(ADMIN))
async def force_refresh_callback(client, query):
    page = int(query.matches[0].group(1))
    user_id = query.from_user.id
    await query.answer("🔄 Force Checking...", show_alert=False)
    await db.col.update_many({"user_id": user_id}, {"$set": {"next_check": 0}})
    await asyncio.sleep(2)
    text, markup = await get_dashboard(user_id, page)
    try: await query.edit_message_text(text, reply_markup=markup, disable_web_page_preview=True)
    except: pass

@Client.on_message(filters.command("setcmd") & filters.user(ADMIN))
async def set_commands(client, message):
    commands = [
        BotCommand("start", "🚀 𝘊𝘩𝘦𝘤𝘬 𝘉𝘰𝘵 𝘈𝘭𝘪𝘷𝘦"),
        BotCommand("add", "✅ 𝘈𝘥𝘥 𝘢 𝘕𝘦𝘸 𝘜𝘙𝘓"),
        BotCommand("del", "🚫 𝘋𝘦𝘭𝘦𝘵𝘦 𝘢𝘯 𝘜𝘙𝘓"),
        BotCommand("stats", "⁉️ 𝘊𝘩𝘦𝘤𝘬 𝘚𝘵𝘢𝘵𝘶𝘴 𝘰𝘧 𝘜𝘙𝘓𝘴"),
        BotCommand("setstatus", "📝 𝘚𝘦𝘵 𝘋𝘺𝘯𝘢𝘮𝘪𝘤 𝘊𝘩𝘢𝘯𝘯𝘦𝘭 𝘚𝘵𝘢𝘵𝘶𝘴")
    ]
    try:
        await client.set_bot_commands(commands)
        await message.reply_text(f"✅ **__Success!__**")
    except Exception as e:
        await message.reply_text(f"❌ **Error:** `{e}`")
