import asyncio
import aiohttp
from pyrogram import Client
from info import ADMIN
from database import db

# Dictionary to store the previous state of URLs
url_states = {}

# --- MONITORING & KEEP-ALIVE LOGIC ---
async def check_url(session, url, is_keep_alive=False):
    """
    Checks the status of a URL.
    """
    # MIMIC A REAL BROWSER (Fixes 403 and 429 Errors)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }

    try:
        # Added headers=headers to the request
        async with session.get(url, timeout=15, headers=headers) as response:
            if response.status == 200:
                return True, response.status
            else:
                return False, response.status
    except Exception as e:
        return False, str(e)

async def monitor_task(app: Client):
    print("Started Keep-Alive and Monitoring Service...")
    
    # Initial DB fetch for startup message
    interval = await db.get_interval()
    
    try:
        await app.send_message(ADMIN, f"🤖 **Keep-Alive Monitor Started**\nTriggering services every **{interval} seconds**.")
    except Exception as e:
        print(f"Failed to send startup message: {e}")

    async with aiohttp.ClientSession() as session:
        while True:
            # 1. Fetch current configuration dynamically from DB
            urls = await db.get_urls()
            interval = await db.get_interval()

            # 2. Loop through URLs
            for url in urls:
                is_online, status = await check_url(session, url, is_keep_alive=True)
                
                prev_state = url_states.get(url)

                if is_online:
                    if prev_state == 'offline':
                        await app.send_message(
                            ADMIN,
                            f"✅ **Service Recovered!**\n\n"
                            f"🔗 **URL:** `{url}`\n"
                            f"🟢 **Status:** Back Online ({status})\n"
                            f"⚡ **Action:** Keep-Alive successful."
                        )
                    url_states[url] = 'online'
                else:
                    # Logic to handle specific 429 blocking silently if preferred
                    if status == 429:
                        print(f"Rate Limit (429) hit for {url}. The site is likely UP but blocking bots.")
                    
                    if prev_state != 'offline':
                        await app.send_message(
                            ADMIN,
                            f"❌ **Service is DOWN**\n\n"
                            f"🔗 **URL:** `{url}`\n"
                            f"⚠️ **Error:** `{status}`\n"
                            f"🛠 **Action:** Keep-Alive request failed."
                        )
                        url_states[url] = 'offline'
            
            # 3. Sleep for the dynamic interval
            await asyncio.sleep(interval)
