import asyncio
from pyrogram import idle
from app import app, start_web_server
from MyselfNeon.plugins.monitor import monitor_task

async def start_bot():
    print("Starting Bot...")
    
    # 1. Start the Web Server (Fixes Port Scanning Errors)
    await start_web_server()
    
    # 2. Start the Telegram Client
    await app.start()
    
    # 3. Start the Background Monitoring Task
    asyncio.create_task(monitor_task(app))
    
    print("Bot is up and running!")
    await idle()
    
    await app.stop()
    print("Bot Stopped.")

if __name__ == "__main__":
    # We use asyncio.run to manage the event loop cleanly
    try:
        # Get the event loop
        loop = asyncio.get_event_loop()
        loop.run_until_complete(start_bot())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Runtime Error: {e}")
