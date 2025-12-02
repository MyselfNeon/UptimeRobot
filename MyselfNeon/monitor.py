import asyncio
import aiohttp
from pyrogram import Client, filters
from info import URLS, ADMIN, CHECK_INTERVAL

# Dictionary to store the previous state of URLs to avoid spamming
# Format: {'url': 'online'} or {'url': 'offline'}
url_states = {}

# --- MONITORING LOGIC ---

async def check_url(session, url):
    """
    Checks the status of a URL.
    Returns: (is_online: bool, status_code: int/str)
    """
    try:
        # Use a longer timeout for the check
        async with session.get(url, timeout=15) as response:
            if response.status == 200:
                return True, response.status
            else:
                return False, response.status
    except Exception as e:
        return False, str(e)

async def monitor_task(app: Client):
    """
    Background task that loops forever checking URLs.
    """
    print("Started Monitoring Service...")
    
    try:
        # Send a startup message to the admin
        await app.send_message(ADMIN, "🤖 **Uptime Monitor Started**\nI am now actively watching your services.")
    except Exception as e:
        print(f"Failed to send startup message: {e}")

    async with aiohttp.ClientSession() as session:
        while True:
            for url in URLS:
                is_online, status = await check_url(session, url)
                
                prev_state = url_states.get(url)

                if is_online:
                    # Notify recovery only if it was previously offline
                    if prev_state == 'offline':
                        await app.send_message(
                            ADMIN,
                            f"✅ **Service Recovered!**\n\n"
                            f"🔗 **URL:** `{url}`\n"
                            f"🟢 **Status:** Online ({status})"
                        )
                    url_states[url] = 'online'
                
                else:
                    # If it is currently offline
                    print(f"URL {url} is DOWN. Status: {status}")
                    
                    if prev_state != 'offline':
                        # Try to 'wake it up' immediately (Trigger)
                        retry_online, retry_status = await check_url(session, url)
                        
                        if retry_online:
                            # Notify: Successfully revived
                            await app.send_message(
                                ADMIN,
                                f"⚠️ **Service Hiccough Detected**\n\n"
                                f"🔗 **URL:** `{url}`\n"
                                f"⚡️ **Action:** Triggered/Retried immediately.\n"
                                f"✅ **Result:** Service is back Online!"
                            )
                            url_states[url] = 'online'
                        else:
                            # Notify: Down and revival failed
                            await app.send_message(
                                ADMIN,
                                f"❌ **Service is DOWN**\n\n"
                                f"🔗 **URL:** `{url}`\n"
                                f"⚠️ **Error:** `{status}`\n"
                                f"🛠 **Action:** Attempted to trigger/revive but failed."
                            )
                            url_states[url] = 'offline'
            
            # Wait for the next interval
            await asyncio.sleep(CHECK_INTERVAL)

# --- COMMAND HANDLERS ---

# Handles the /start command with the requested styled text
@Client.on_message(filters.command("start") & filters.private & filters.user(ADMIN))
async def start_command(client, message):
    """
    Greets the admin with a stylized message about the bot's monitoring function.
    """
    # Using the requested style and adapting the content to Uptime Monitoring
    start_message = (
        "<blockquote>‣ Hᴇʟʟᴏ\n"
        "I ᴀᴍ Lᴀᴛᴇsᴛ Aᴅᴠᴀɴᴄᴇᴅ **Uptime Monitor Bᴏᴛ**.\n"
        "Cᴏᴅᴇᴅ & Dᴇᴠᴇʟᴏᴘᴇᴅ ʙʏ NᴇᴏɴAɴᴜʀᴀɢ.\n"
        "I ᴄᴀɴ **Monitor** ᴀɴᴅ **Auto-Revive** Yᴏᴜʀ ᴡᴇʙsᴇʀᴠɪᴄᴇs.\n"
        "Uѕᴇ /stats ғᴏʀ ᴀ ᴄᴜʀʀᴇɴᴛ ʀᴇᴘᴏʀᴛ.</blockquote>"
    )
    await message.reply_text(start_message)

# Handles the /stats command
@Client.on_message(filters.command("stats") & filters.private & filters.user(ADMIN))
async def stats_command(client, message):
    """
    Provides a manual status report for all monitored URLs.
    """
    text = "📊 **Current Status Report**\n\n"
    if not URLS:
        text += "No URLs configured in `info.py`."
    else:
        for url in URLS:
            state = url_states.get(url, "Unknown")
            icon = "🟢" if state == "online" else "🔴"
            text += f"{icon} `{url}` : **{state.upper()}**\n"
            
    await message.reply_text(text)
