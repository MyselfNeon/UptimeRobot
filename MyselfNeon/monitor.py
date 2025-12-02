import asyncio
import aiohttp
from pyrogram import Client, filters
from info import URLS, ADMIN, CHECK_INTERVAL

# Dictionary to store the previous state of URLs to avoid spamming
# Format: {'url': 'online'} or {'url': 'offline'}
url_states = {}

async def check_url(session, url):
    """
    Checks the status of a URL.
    Returns: (is_online: bool, status_code: int/str)
    """
    try:
        async with session.get(url, timeout=10) as response:
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
    
    # Send a startup message
    try:
        await app.send_message(ADMIN, "🤖 **Uptime Monitor Started**\nI am now watching your services.")
    except Exception as e:
        print(f"Failed to send startup message: {e}")

    async with aiohttp.ClientSession() as session:
        while True:
            for url in URLS:
                is_online, status = await check_url(session, url)
                
                # Determine previous state (default to None if first run)
                prev_state = url_states.get(url)

                if is_online:
                    # If it was previously offline, notify recovery
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
                    
                    # Logic: It's down. "Trigger" it implies we just tried to GET it. 
                    # If the first check failed, we try one more 'force' trigger immediately.
                    
                    if prev_state != 'offline':
                        # Try to "Make it alive" (Retry connection immediately)
                        retry_online, retry_status = await check_url(session, url)
                        
                        if retry_online:
                            await app.send_message(
                                ADMIN,
                                f"⚠️ **Service Hiccough Detected**\n\n"
                                f"🔗 **URL:** `{url}`\n"
                                f"🔻 **Initial:** Offline\n"
                                f"⚡️ **Action:** Triggered/Retried immediately.\n"
                                f"✅ **Result:** Service is back Online!"
                            )
                            url_states[url] = 'online'
                        else:
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

# We need a way to start this task. 
# Since this is a plugin file, we can hook into the 'start' command 
# or simply expose the function to be called by main.py.
# However, to keep main.py clean, we can use a startup hook here if using Pyrogram v2.1+,
# but the most reliable way across versions is creating a simple start command 
# or calling this function from main.py.
# 
# BELOW: A command to check status manually
@Client.on_message(filters.command("stats") & filters.user(ADMIN))
async def stats_command(client, message):
    text = "📊 **Current Status Report**\n\n"
    for url in URLS:
        state = url_states.get(url, "Unknown")
        icon = "🟢" if state == "online" else "🔴"
        text += f"{icon} `{url}` : **{state.upper()}**\n"
    await message.reply_text(text)
