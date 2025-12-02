from pyrogram import Client
from aiohttp import web
from info import API_ID, API_HASH, BOT_TOKEN, PORT

# Initialize the Client
app = Client(
    "uptime_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    # This tells Pyrogram to look for plugins inside the 'MyselfNeon' folder
    plugins=dict(root="MyselfNeon")
)

# Web Server Logic
async def web_page(request):
    return web.Response(text="MyselfNeon Monitor Bot is Running!", status=200)

async def start_web_server():
    server = web.Application()
    server.router.add_get("/", web_page)
    runner = web.AppRunner(server)
    await runner.setup()
    await web.TCPSite(runner, "0.0.0.0", PORT).start()
    print(f"Web Server bound to port {PORT}")
