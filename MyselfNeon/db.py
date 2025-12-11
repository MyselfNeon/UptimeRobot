# ---------------------------------------------------
# File Name: Database.py
# Author: MyselfNeon
# GitHub: https://github.com/MyselfNeon/
# Telegram: https://t.me/MyelfNeon
# ---------------------------------------------------

import motor.motor_asyncio
import time
from info import DB_URI, DB_NAME

class Database:
    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.col = self.db.urls
        self.config = self.db.config

    def new_url(self, user_id, url):
        return dict(
            user_id=user_id,
            url=url,
            status="Unknown",
            response_time=0,
            last_checked=None,
            uptime_count=0,
            total_checks=0,
            ssl_expiry=None
        )

    async def add_url(self, user_id, url):
        # Adds URL specifically for this user
        url_dict = self.new_url(user_id, url)
        await self.col.insert_one(url_dict)

    async def remove_url(self, user_id, url):
        # Removes URL only if it belongs to this user
        await self.col.delete_one({"user_id": user_id, "url": url})

    async def get_urls(self, user_id):
        # Get only URLs belonging to this specific user
        urls = await self.col.find({"user_id": user_id}).to_list(length=None)
        return [x["url"] for x in urls]

    async def get_all_monitored_datas(self):
        # For the background monitor: Get ALL data
        return await self.col.find().to_list(length=None)

    async def is_url_exist(self, user_id, url):
        found = await self.col.find_one({"user_id": user_id, "url": url})
        return bool(found)
    
    # --- Advanced Stats Updates ---
    async def update_url_status(self, user_id, url, status, response_time, is_up):
        """Updates stats for analytics"""
        update_data = {
            "$set": {
                "status": status,
                "response_time": response_time,
                "last_checked": time.time()
            },
            "$inc": {"total_checks": 1}
        }
        
        if is_up:
            update_data["$inc"]["uptime_count"] = 1
            
        await self.col.update_one(
            {"user_id": user_id, "url": url},
            update_data
        )

    # Configuration (Global Interval)
    async def set_interval(self, seconds):
        await self.config.update_one(
            {"_id": "interval"},
            {"$set": {"value": int(seconds)}},
            upsert=True
        )

    async def get_interval(self):
        config = await self.config.find_one({"_id": "interval"})
        return config["value"] if config else 60

db = Database(DB_URI, DB_NAME)
