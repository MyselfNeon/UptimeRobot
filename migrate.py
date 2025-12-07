import asyncio
import motor.motor_asyncio
# Import config directly to ensure connection
from info import DB_URI, DB_NAME

# --- CONFIGURATION ---
# REPLACE THIS WITH YOUR NUMERIC ID
MY_USER_ID = 841851780 
# ---------------------

async def migrate_data():
    print("⏳ Connecting to Database...")
    client = motor.motor_asyncio.AsyncIOMotorClient(DB_URI)
    db = client[DB_NAME]
    col = db.urls

    print("🔍 Searching for old orphaned URLs...")
    
    # Update all documents that DO NOT have a 'user_id' field
    result = await col.update_many(
        {"user_id": {"$exists": False}},  # Condition: Old data
        {"$set": {"user_id": MY_USER_ID}} # Action: Assign to you
    )

    print(f"✅ Migration Complete!")
    print(f"📊 Modified {result.modified_count} URLs.")
    print("👉 You can now delete this script and restart your bot.")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(migrate_data())
