from pyrogram import Client, filters
import motor.motor_asyncio
from info import DB_URI, DB_NAME

# --- TEMPORARY RECOVERY COMMAND ---
@Client.on_message(filters.command("recover") & filters.private)
async def recover_database(client, message):
    user_id = message.from_user.id
    
    # Send status message
    status_msg = await message.reply_text("🕵️ **__Scanning database for lost URLs...__**")
    
    try:
        # Connect to Database directly
        cli = motor.motor_asyncio.AsyncIOMotorClient(DB_URI)
        db = cli[DB_NAME]
        col = db.urls
        
        # 1. Find URLs that have NO owner (orphaned data from old version)
        query = {"user_id": {"$exists": False}}
        old_count = await col.count_documents(query)
        
        if old_count == 0:
            return await status_msg.edit_text("🤷‍♂️ **__No old URLs found.__**\n__Everything seems up to date.__")
        
        # 2. Update them to belong to YOU
        await col.update_many(
            query, 
            {"$set": {"user_id": user_id}}
        )
        
        await status_msg.edit_text(
            f"✅ **__Recovery Successful!__**\n\n"
            f"🔄 **__Recovered:__** {old_count} URLs\n"
            f"👤 **__Assigned to:__** {message.from_user.first_name}\n\n"
            f"👉 __You can now use__ `/check` __to see them.__"
        )
        
    except Exception as e:
        await status_msg.edit_text(f"❌ **__Error during recovery:__**\n`{e}`")
