from pyrogram import Client
from aiohttp import web
from info import API_ID, API_HASH, BOT_TOKEN, PORT

# 1. Initialize the Bot Client
app = Client(
    "uptime_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    plugins=dict(root="MyselfNeon")
)

# 2. Define a simple Web Server to bind to the port
async def web_page(request):
    """
    Returns a simple text response to keep the server alive.
    """
    return web.Response(text="MyselfNeon Monitor Bot is Running!", status=200)

async def start_web_server():
    """
    Initializes and starts the web server on 0.0.0.0:8080
    """
    server = web.Application()
    server.router.add_get("/", web_page)
    
    runner = web.AppRunner(server)
    await runner.setup()
    
    # Binds to 0.0.0.0 and the configured PORT
    await web.TCPSite(runner, "0.0.0.0", PORT).start()
    print(f"Web Server bound to port {PORT}")
