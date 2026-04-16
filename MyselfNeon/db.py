# --- Database.py ---
import motor.motor_asyncio
import time
import asyncio
from info import DB_URI, DB_NAME

class Database:
    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.col = self.db.urls
        self.config = self.db.config
        # Fix: Create Event inside init to ensure loop exists
        self.status_event = asyncio.Event()

    async def ensure_indexes(self):
        await self.col.create_index([("next_check", 1), ("status", 1)])
        await self.col.create_index([("user_id", 1)])

    # --- NEW: Dynamic Status Config ---
    async def set_status_config(self, channel_id, message_id):
        await self.config.update_one(
            {"_id": "status_target"},
            {"$set": {"channel_id": channel_id, "message_id": message_id}},
            upsert=True
        )

    async def get_status_config(self):
        config = await self.config.find_one({"_id": "status_target"})
        return config if config else None

    def new_url(self, user_id, url, name, emoji, username=None, is_public=True):
        return dict(
            user_id=user_id,
            url=url,
            name=name,           
            emoji=emoji,         
            username=username,
            is_public=is_public,
            status="PENDING",
            last_code="200",
            response_time=0,
            uptime_count=0,
            total_checks=0,
            consecutive_failures=0,
            next_check=time.time(),
            check_interval=60,
            alert_mode="ON",
            added_at=time.time()
        )

    async def add_url(self, user_id, url, name, emoji, username=None, is_public=True):
        url_dict = self.new_url(user_id, url, name, emoji, username, is_public)
        result = await self.col.insert_one(url_dict)
        return True, result.inserted_id

    async def remove_url(self, user_id, url):
        await self.col.delete_one({"user_id": user_id, "url": url})

    async def is_url_exist(self, user_id, url):
        found = await self.col.find_one({"user_id": user_id, "url": url})
        return bool(found)

    async def get_urls_paginated(self, user_id, page=1, limit=6):
        skip = (page - 1) * limit
        cursor = self.col.find({"user_id": user_id}).skip(skip).limit(limit)
        urls = await cursor.to_list(length=limit)
        total_count = await self.col.count_documents({"user_id": user_id})
        return urls, total_count

    async def get_due_urls(self):
        now = time.time()
        return await self.col.find({
            "$or": [
                {"next_check": {"$lte": now}, "status": {"$ne": "PAUSED"}},
                {"next_check": 0}
            ]
        }).to_list(length=None)

    async def get_all_monitors(self):
        return await self.col.find({}).to_list(length=None)

    async def update_adaptive_result(self, _id, result_data):
        now = time.time()
        is_up = result_data['is_up']
        latency = result_data['latency']
        code = result_data['code']
        current_fails = result_data['consecutive_failures']
        current_interval = result_data['check_interval']
        current_status = result_data.get('current_status', 'PENDING')

        if current_status == "PAUSED":
            if is_up:
                pass 
            else:
                await self.col.update_one(
                    {"_id": _id}, 
                    {
                        "$set": {
                            "last_code": str(code),
                            "response_time": latency,
                            "last_checked": now,
                            "next_check": now 
                        },
                        "$inc": {"total_checks": 1}
                    }
                )
                return "PAUSED"

        update_query = {
            "$set": {
                "last_code": str(code),
                "response_time": latency,
                "last_checked": now,
            },
            "$inc": {"total_checks": 1}
        }

        if code == 429:
            new_status = "RATE-LIMITED"
            new_interval = min(current_interval * 2, 600)
            update_query["$set"]["check_interval"] = int(new_interval)
            update_query["$set"]["status"] = new_status
        elif is_up:
            new_status = "SLOW" if latency > 1500 else "ONLINE"
            update_query["$set"]["consecutive_failures"] = 0
            update_query["$inc"]["uptime_count"] = 1
            new_interval = min(current_interval * 1.5, 300) 
            if current_interval < 60: new_interval = 60
            update_query["$set"]["check_interval"] = int(new_interval)
            update_query["$set"]["status"] = new_status
        else:
            new_fails = current_fails + 1
            update_query["$set"]["consecutive_failures"] = new_fails
            if new_fails >= 20:
                update_query["$set"]["status"] = "PAUSED"
                update_query["$set"]["check_interval"] = 0
            else:
                update_query["$set"]["status"] = "DOWN"
                new_interval = max(current_interval / 2, 30)
                update_query["$set"]["check_interval"] = int(new_interval)

        if update_query["$set"]["status"] != "PAUSED":
            update_query["$set"]["next_check"] = now + update_query["$set"]["check_interval"]

        await self.col.update_one({"_id": _id}, update_query)
        
        final_status = update_query["$set"]["status"]
        if final_status != current_status:
            self.status_event.set() # Trigger Event
            
        return final_status

db = Database(DB_URI, DB_NAME)