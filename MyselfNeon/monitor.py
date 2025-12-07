import asyncio
import aiohttp
from pyrogram import Client
# UPDATED IMPORT: Uses local db.py
from .db import db

# Dictionary to store the previous state of URLs
# Format: {"user_id|url": "online/offline"}
url_states = {}

# --- MONITORING & KEEP-ALIVE LOGIC ---
async def check_url(session, url):
    """
    Checks the status of a URL. Returns (is_online, status_code/error).
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Connection": "keep-alive"
    }
    try:
        async with session.get(url, timeout=10, headers=headers) as response:
            if response.status == 200:
                return True, response.status
            else:
                return False, response.status
    except Exception as e:
        return False, "Error"

async def monitor_task(app: Client):
    print("Started Premium Keep-Alive and Monitoring Service...")
    
    async with aiohttp.ClientSession() as session:
        while True:
            # 1. Fetch ALL monitored URLs from all users
            all_entries = await db.get_all_monitored_datas()
            interval = await db.get_interval()

            for entry in all_entries:
                user_id = entry.get("user_id")
                url = entry.get("url")
                unique_key = f"{user_id}|{url}"

                # --- CHECK 1: Initial Check ---
                is_online, status = await check_url(session, url)

                # --- RETRY LOGIC (Double/Triple Check) ---
                if not is_online:
                    # Retry 2 times with 10s delay
                    for attempt in range(2):
                        await asyncio.sleep(10) # Immediate short wait
                        is_online, status = await check_url(session, url)
                        if is_online:
                            break 

                prev_state = url_states.get(unique_key)

                if is_online:
                    # Recovery Alert
                    if prev_state == 'offline':
                        try:
                            await app.send_message(
                                user_id,
                                f"🟢 **__Service Recovered!__**\n\n"
                                f"🔗 **__URL:__** `{url}`\n"
                                f"⚡ **__Status:__** **Online** (200 OK)\n"
                                f"🥂 **__Note:__** __Your service is back in action.__"
                            )
                        except Exception as e:
                            print(f"Failed to send alert to {user_id}: {e}")
                    
                    url_states[unique_key] = 'online'
                
                else:
                    # Down Alert
                    if prev_state != 'offline':
                        try:
                            await app.send_message(
                                user_id,
                                f"🔴 **__Service is DOWN!__**\n\n"
                                f"🔗 **__URL:__** `{url}`\n"
                                f"⚠️ **__Error:__** `{status}`\n"
                                f"🔄 **__Tries:__** __Failed after 3 attempts.__\n"
                                f"🛠 **__Action:__** __Please check your server manually.__"
                            )
                        except Exception as e:
                            print(f"Failed to send alert to {user_id}: {e}")
                        
                        url_states[unique_key] = 'offline'
            
            # Sleep for the global interval
            await asyncio.sleep(interval)
