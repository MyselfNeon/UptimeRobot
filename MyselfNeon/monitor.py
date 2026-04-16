# --- Monitor.py ---
import asyncio
import aiohttp
import time
from datetime import datetime, timedelta, timezone
from pyrogram import Client
from .db import db
from info import STATUS_UPDATE_INTERVAL

# Cache states in memory
state_cache = {}

# ✅ Indian Standard Time
IST = timezone(timedelta(hours=5, minutes=30))

async def smart_check(session, url):
    """
    Strategy: HEAD -> If Error -> GET
    Returns: (is_up, status_code/error, latency_ms)
    """
    timeout = aiohttp.ClientTimeout(total=10)
    start = time.perf_counter()
    try:
        async with session.head(url, timeout=timeout, allow_redirects=True) as response:
            latency = int((time.perf_counter() - start) * 1000)
            status = response.status
            if status == 429: return True, 429, latency 
            if status >= 400: raise ValueError("Force GET")
            return True, status, latency
    except (ValueError, aiohttp.ClientError, asyncio.TimeoutError):
        try:
            start_get = time.perf_counter()
            async with session.get(url, timeout=timeout) as response:
                latency = int((time.perf_counter() - start_get) * 1000)
                status = response.status
                if status == 429: return True, 429, latency
                if 200 <= status < 400: return True, status, latency
                else: return False, status, latency
        except asyncio.TimeoutError: return False, "Timeout", 0
        except aiohttp.ClientConnectorError: return False, "DNS/Connection Error", 0
        except Exception: return False, "Error", 0
    except Exception: return False, "Unknown Error", 0

async def process_entry(app, session, entry):
    user_id = entry['user_id']
    url = entry['url']
    entry_id = entry['_id']
    
    is_up, code, latency = await smart_check(session, url)
    
    if not is_up:
        await asyncio.sleep(1)
        is_up, code, latency = await smart_check(session, url)

    result_data = {
        'is_up': is_up, 'latency': latency, 'code': code,
        'consecutive_failures': entry.get('consecutive_failures', 0),
        'check_interval': entry.get('check_interval', 60),
        'current_status': entry.get('status', 'PENDING') 
    }

    new_status = await db.update_adaptive_result(entry_id, result_data)

    unique_key = f"{user_id}|{url}"
    prev_status = state_cache.get(unique_key, "PENDING")
    
    if new_status != prev_status:
        state_cache[unique_key] = new_status
        if entry.get('alert_mode') != "SILENT":
            await send_alert(app, user_id, url, new_status, code, latency)

async def send_alert(app, user_id, url, status, code, latency):
    icon = {
        "ONLINE": "🟢", "SLOW": "🟡", "DOWN": "🔴", 
        "PAUSED": "⛔️", "RATE-LIMITED": "⚠️"
    }.get(status, "❓")
    
    msg_title = "Service Rate Limited" if status == "RATE-LIMITED" else f"Monitor Alert: {status}"
    
    text = (
        f"{icon} **__{msg_title}__**\n\n"
        f"🔗 **URL:** `{url}`\n"
        f"📝 **__Info:** {code}__\n"
        f"⚡ **__Latency:** {latency}ms__\n"
    )
    if status == "PAUSED": text += "\n💀 **Monitoring paused due to 20 consecutive failures.**"
    elif status == "RATE-LIMITED": text += "\n⏳ **Backing off checks to prevent block.**"

    try: await app.send_message(user_id, text, disable_web_page_preview=True)
    except Exception: pass 

# --- Channel Status Update Feature ---
async def generate_status_text():
    all_monitors = await db.get_all_monitors()
    
    if not all_monitors:
        return "👻 **__No services are currently being monitored.__**"

    text = "🚦 𝙎𝙔𝙎𝙏𝙀𝙈 𝙎𝙏𝘼𝙏𝙐𝙎 **:** 𝙇𝙄𝙑𝙀 🚦\n━━━━━━━━━━━━━━━━━━━━━━━\n\n"

    for entry in all_monitors:
        # Skip private URLs from public channel
        if entry.get('is_public', True) == False:
            continue

        name = entry.get('name', entry['url']) 
        username = entry.get('username') 
        emoji = entry.get('emoji', '❓')
        ping = int(entry.get('response_time', 0))
        status = entry.get('status', 'PENDING')

        # Logic for Bot vs Website
        if username: 
            second_line = f"Bot : {username}"
        else:
            second_line = f"Type : Website"

        # Logic for Status
        if status == "ONLINE": status_display = "🟢 Active ✅"
        elif status in ["DOWN", "PAUSED"]: status_display = "🔴 Paused ⛔"
        elif status == "SLOW": status_display = "🟡 Slow ⚠️"
        else: status_display = f"⚪ {status}"

        # --- BOLD & UNDERLINE FORMATTING ---
        text += (
            f"**__{emoji} {name}__**\n"
            f"**╰┈➤ __{second_line}__**\n"
            f"**╰┈➤ __Ping : {ping} ms__**\n"
            f"**╰┈➤ __Status : {status_display}__**\n\n"
        )

    # --- DATE FORMATTING (IST) ---
    now = datetime.now(IST)
    date_str = now.strftime("%d %b")      # 13 Feb
    time_str = now.strftime("%I:%M %p")   # 11:32 PM
    
    text += "━━━━━━━━━━━━━━━━━━━━━━━\n"
    text += f"**__Last Check: {date_str} at {time_str}__**"
    return text

async def update_channel_message(app):
    # Fetch from DB first
    config = await db.get_status_config()
    
    if config:
        target_channel = config.get("channel_id")
        target_message = config.get("message_id")
    else:
        # No config set in DB yet, exit silently until /setstatus is used
        return

    if target_channel in [0, None] or target_message in [0, None]: 
        return
        
    try:
        text = await generate_status_text()
        await app.edit_message_text(
            chat_id=target_channel,
            message_id=target_message,
            text=text
        )
    except Exception as e:
        pass # Silently fail if message ID is wrong, to prevent spamming logs

async def status_monitor_loop(app):
    print("📢 Status Monitor Loop Started (Dynamic Mode)...")
    await asyncio.sleep(5) 
    await update_channel_message(app)

    while True:
        try:
            try:
                # Use db.status_event now
                await asyncio.wait_for(db.status_event.wait(), timeout=STATUS_UPDATE_INTERVAL)
                db.status_event.clear()
            except asyncio.TimeoutError:
                pass 

            await update_channel_message(app)
            await asyncio.sleep(2) 

        except Exception as e:
            print(f"❌ Status Loop Error: {e}")
            await asyncio.sleep(10)

async def monitor_task(app: Client):
    print("🧠 Starting Intelligent Monitor (HEAD + GET fallback)...")
    await db.ensure_indexes()
    asyncio.create_task(status_monitor_loop(app))
    
    async with aiohttp.ClientSession() as session:
        while True:
            due_urls = await db.get_due_urls()
            if due_urls:
                tasks = [process_entry(app, session, entry) for entry in due_urls]
                await asyncio.gather(*tasks)
            await asyncio.sleep(5)