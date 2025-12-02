import asyncio
import aiohttp
from pyrogram import Client, filters
from info import URLS, ADMIN, CHECK_INTERVAL

# Dictionary to store the previous state of URLs to avoid spamming
# Format: {'url': 'online'} or {'url': 'offline'}
url_states = {}

# --- MONITORING & KEEP-ALIVE LOGIC ---
async def check_url(session, url, is_keep_alive=False):
    """
    Checks the status of a URL.
    is_keep_alive: If True, this is the routine check to keep the service awake.
    Returns: (is_online: bool, status_code: int/str)
    """
    try:
        # Use a reasonable timeout for the check
        async with session.get(url, timeout=15) as response:
            if response.status == 200:
                return True, response.status
            else:
                # If we get a response (e.g., 404, 500, etc.) but not 200, it's still an error
                return False, response.status
    except Exception as e:
        # If we get an exception (e.g., connection refused, timeout), the service is truly down
        return False, str(e)

async def monitor_task(app: Client):
    """
    Background task that loops forever, checking (and triggering) URLs.
    """
    print("Started Keep-Alive and Monitoring Service...")
    
    try:
        # Send a startup message to the admin
        await app.send_message(ADMIN, "🤖 **Keep-Alive Monitor Started**\nI am now triggering all services every **{} seconds** to prevent sleeping.".format(CHECK_INTERVAL))
    except Exception as e:
        print(f"Failed to send startup message: {e}")

    async with aiohttp.ClientSession() as session:
        while True:
            for url in URLS:
                # --- STEP 1: Always Trigger / Keep Alive ---
                # This request is sent on every interval, fulfilling the "click them at that time" requirement.
                is_online, status = await check_url(session, url, is_keep_alive=True)
                
                prev_state = url_states.get(url)

                if is_online:
                    # Case A: Service is 200 OK.
                    if prev_state == 'offline':
                        # Notify only if it just recovered
                        await app.send_message(
                            ADMIN,
                            f"✅ **Service Recovered!**\n\n"
                            f"🔗 **URL:** `{url}`\n"
                            f"🟢 **Status:** Back Online ({status})\n"
                            f"⚡ **Action:** Keep-Alive successful."
                        )
                    url_states[url] = 'online'
                
                else:
                    # Case B: Service is DOWN (Error status or Exception)
                    if prev_state != 'offline':
                        # Notify immediately only on the first failure detection
                        await app.send_message(
                            ADMIN,
                            f"❌ **Service is DOWN**\n\n"
                            f"🔗 **URL:** `{url}`\n"
                            f"⚠️ **Error:** `{status}`\n"
                            f"🛠 **Action:** A Keep-Alive request was sent, but the service failed to respond with 200 OK. Requires manual check."
                        )
                        url_states[url] = 'offline'
            
            # Wait for the next interval
            await asyncio.sleep(CHECK_INTERVAL)

# --- COMMAND HANDLERS ---
# (Commands remain the same)

# Handles the /start command with the requested styled text
@Client.on_message(filters.command("start") & filters.private & filters.user(ADMIN))
async def start_command(client, message):
    """
    Greets the admin with a stylized message about the bot's monitoring function.
    """
    start_message = (
        "‣ Hᴇʟʟᴏ 𐌽𐌴𐌏𐌽 🇮🇳\n"
        "I ᴀᴍ Lᴀᴛᴇsᴛ Aᴅᴠᴀɴᴄᴇᴅ **Keep-Alive Monitor Bᴏᴛ**.\n"
        "Cᴏᴅᴇᴅ & Dᴇᴠᴇʟᴏᴘᴇᴅ ʙʏ NᴇᴏɴAɴᴜʀᴀɢ.\n"
        "I ᴄᴀɴ **Trigger** ᴀɴᴅ **Monitor** Yᴏᴜʀ ᴡᴇʙsᴇʀᴠɪᴄᴇs ᴇᴠᴇʀʏ **{}** ѕᴇᴄᴏɴᴅs.\n"
        "Uѕᴇ /stats ғᴏʀ ᴀ ᴄᴜʀʀᴇɴᴛ ʀᴇᴘᴏʀᴛ.".format(CHECK_INTERVAL)
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
            state = url_states.get(url, "Unknown (Not Checked Yet)")
            icon = "🟢" if state == "online" else "🔴"
            text += f"{icon} **__{url} – {state.upper()}__**\n"
            
    await message.reply_text(text)
