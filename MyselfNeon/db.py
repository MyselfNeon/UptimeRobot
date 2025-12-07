import motor.motor_asyncio
from info import DB_URI, DB_NAME

class Database:
    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.col = self.db.urls
        self.config = self.db.config

    def new_url(self, user_id, url):
        return dict(user_id=user_id, url=url)

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
        # For the background monitor: Get ALL data (user_id and url)
        return await self.col.find().to_list(length=None)

    async def is_url_exist(self, user_id, url):
        # Check if URL exists for this specific user
        found = await self.col.find_one({"user_id": user_id, "url": url})
        return bool(found)
    
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
