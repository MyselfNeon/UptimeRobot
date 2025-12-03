import motor.motor_asyncio
from info import DB_URI, DB_NAME

class Database:
    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.col = self.db.urls
        self.config = self.db.config

    def new_url(self, url):
        return dict(url=url)

    async def add_url(self, url):
        url_dict = self.new_url(url)
        await self.col.insert_one(url_dict)

    async def remove_url(self, url):
        await self.col.delete_one({"url": url})

    async def get_urls(self):
        urls = await self.col.find().to_list(length=None)
        return [x["url"] for x in urls]

    async def is_url_exist(self, url):
        url = await self.col.find_one({"url": url})
        return bool(url)
    
    # Configuration (Interval)
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
