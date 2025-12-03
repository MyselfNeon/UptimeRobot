import asyncio
import aiohttp
from pyrogram import Client
from info import ADMIN
from database import db

# Dictionary to store the previous state of URLs
url_states = {}

async def check_url(session, url, is_keep_alive=False):
    try:
        async with session.get(url, timeout=15) as response:
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
