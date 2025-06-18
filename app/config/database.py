from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.config.settings import settings
from app.models.users import Users
from app.models.campaigns import Campaigns

class Database:
    def __init__(self):
        self.client = AsyncIOMotorClient(settings.mongodb_url)
        self.database = self.client[settings.database_name]

    async def init(self):
        await init_beanie(database=self.database, document_models=[Users, Campaigns])
        # AJouter toutes les autres collections

    async def close(self):
        self.client.close()