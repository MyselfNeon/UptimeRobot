# --- main.py ---
import sys
import os
import asyncio
import logging
import aiohttp
from pyrogram import idle
from app import app, start_web_server
from info import ADMIN, KEEP_ALIVE_URL

# FORCE logging so Render/Koyeb shows INFO logs
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    force=True
)

logging.info("🔥 Main.py loaded - logging configured")

# Explicitly add current directory to python path
sys.path.append(os.getcwd())

from MyselfNeon.monitor import monitor_task

KEEP_ALIVE_INTERVAL = 300  # 5 minutes
KEEP_ALIVE_TIMEOUT = 15   # seconds

async def keep_alive():
    """Send a request every 300 seconds to keep the bot alive (best-effort)."""
    if not KEEP_ALIVE_URL:
        logging.warning("🚫 KEEP_ALIVE_URL not set — keep-alive disabled.")
        return

    timeout = aiohttp.ClientTimeout(total=KEEP_ALIVE_TIMEOUT)

    logging.info("🌐 KEEP_ALIVE_URL is set. Starting keep-alive system...")

    first_ping_done = False

    while True:
        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(KEEP_ALIVE_URL) as resp:
                    status = resp.status

                    if not first_ping_done:
                        if status == 200:
                            logging.info(
                                "✅ Keep-alive FIRST ping successful. Keep-alive is running."
                            )
                        else:
                            logging.warning(
                                f"⚠️ Keep-alive FIRST ping returned status {status}"
                            )
                        first_ping_done = True

        except asyncio.CancelledError:
            logging.warning("🛑 Keep-alive task cancelled.")
            raise

        except Exception as e:
            if not first_ping_done:
                logging.error(f"❌ Keep-alive FIRST ping FAILED: {e}")
                first_ping_done = True
            else:
                # Stay quiet after first ping unless there's an error
                logging.error(f"❌ Keep-alive error: {e}")

        await asyncio.sleep(KEEP_ALIVE_INTERVAL)

# Start keep-alive safely inside running loop
def start_keep_alive():
    if KEEP_ALIVE_URL:
        logging.info("🔍 KEEP_ALIVE_URL detected. Creating keep-alive task...")
        asyncio.create_task(keep_alive())
        logging.info("🌐 Keep-alive task created.")
    else:
        logging.warning("🚫 KEEP_ALIVE_URL not set. Keep-alive will not start.")

async def start_bot():
    print("Starting Bot...")
    logging.info("🚀 start_bot() called")

    await start_web_server()
    logging.info("🌐 Web server started")

    await app.start()
    logging.info("✅ Bot started successfully")

    if ADMIN != 0:
        print(f"Sending startup message to: {ADMIN}")
        try:
            await app.send_message(
                ADMIN,
                "🎉 **Bot Restarted!**\n"
                "✅ **Monitoring Resumed.**"
            )
            logging.info(f"📩 Startup message sent to ADMIN: {ADMIN}")
        except Exception as e:
            print(f"❌ Failed to send startup message: {e}")
            logging.error(f"❌ Failed to send startup message: {e}")
    else:
        print("⚠️ ADMIN ID is 0. Set 'ADMIN' in env vars.")
        logging.warning("⚠️ ADMIN ID is 0. Startup message skipped.")

    # Start Background Task
    asyncio.create_task(monitor_task(app))
    logging.info("🧠 Monitor task started")

    # Start Keep Alive Task
    start_keep_alive()

    print("Bot is up and running!")
    logging.info("💓 Bot is up and running. Entering idle state.")

    await idle()
    await app.stop()
    logging.info("🛑 Bot stopped")

if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(start_bot())
    except KeyboardInterrupt:
        logging.warning("🛑 KeyboardInterrupt received. Shutting down.")
    except Exception as e:
        print(f"Runtime Error: {e}")
        logging.exception(f"💥 Runtime Error: {e}")