# ---------------------------------------------------
# File Name: Monitor.py
# Author: MyselfNeon
# GitHub: https://github.com/MyselfNeon/
# Telegram: https://t.me/MyelfNeon
# ---------------------------------------------------

import asyncio
import aiohttp
import time
import ssl
import certifi
import socket
from pyrogram import Client
from datetime import datetime
from urllib.parse import urlparse
from .db import db

# Cache to prevent spamming the same alert
# Format: {"user_id|url": "online"}
url_states = {}

async def get_ssl_expiry(url):
    """Check SSL Certificate Expiry Date"""
    try:
        parsed = urlparse(url)
        hostname = parsed.netloc
        context = ssl.create_default_context(cafile=certifi.where())
        conn = context.wrap_socket(socket.socket(socket.AF_INET), server_hostname=hostname)
        conn.settimeout(3.0)
        conn.connect((hostname, 443))
        ssl_info = conn.getpeercert()
        # Parse date
        expire_date = datetime.strptime(ssl_info['notAfter'], r'%b %d %H:%M:%S %Y %Z')
        days_left = (expire_date - datetime.now()).days
        conn.close()
        return days_left
    except:
        return None

async def advanced_check(session, url):
    """
    Returns: (is_online, status_code, latency_ms)
    """
    start_time = time.perf_counter()
    try:
        async with session.get(url, timeout=15) as response:
            latency = (time.perf_counter() - start_time) * 1000 # to ms
            return True, response.status, int(latency)
    except Exception as e:
        return False, "Timeout/Error", 0

async def process_url(app, session, entry):
    """Process a single URL independently"""
    user_id = entry.get("user_id")
    url = entry.get("url")
    unique_key = f"{user_id}|{url}"
    
    # 1. Check Status
    is_online, code, latency = await advanced_check(session, url)
    
    # 2. Retry Logic (Smart Filtering)
    if not is_online:
        await asyncio.sleep(2)
        is_online, code, latency = await advanced_check(session, url)

    # 3. Update Database with Stats
    await db.update_url_status(user_id, url, code, latency, is_online)

    # 4. Handle Alerts
    prev_state = url_states.get(unique_key, "online") # Default to online to avoid startup spam
    
    if is_online:
        if prev_state == 'offline':
            # RECOVERY ALERT
            try:
                await app.send_message(
                    user_id,
                    f"🟢 **Service Recovered!**\n\n"
                    f"🔗 **URL:** `{url}`\n"
                    f"⚡ **Latency:** `{latency}ms`\n"
                    f"✅ **Status:** Back Online (200 OK)"
                )
            except Exception as e:
                print(f"Failed to alert {user_id}: {e}")

        url_states[unique_key] = 'online'
    else:
        if prev_state != 'offline':
            # DOWN ALERT
            try:
                await app.send_message(
                    user_id,
                    f"🔴 **Service DOWN!**\n\n"
                    f"🔗 **URL:** `{url}`\n"
                    f"⚠️ **Error:** `{code}`\n"
                    f"📉 **Latency:** `0ms`\n"
                    f"🛠 Please check your server immediately."
                )
            except Exception as e:
                print(f"Failed to alert {user_id}: {e}")

            url_states[unique_key] = 'offline'

async def monitor_task(app: Client):
    print("🚀 Started High-Performance Monitoring Engine...")
    
    async with aiohttp.ClientSession() as session:
        while True:
            all_entries = await db.get_all_monitored_datas()
            interval = await db.get_interval()

            # CONCURRENT EXECUTION
            tasks = [process_url(app, session, entry) for entry in all_entries]
            
            # Run all checks simultaneously
            if tasks:
                await asyncio.gather(*tasks)
            
            await asyncio.sleep(interval)
            
