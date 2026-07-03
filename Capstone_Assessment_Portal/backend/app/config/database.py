from motor.motor_asyncio import AsyncIOMotorClient
from app.config.settings import settings  


client = AsyncIOMotorClient(settings.mongo_uri)


database = client[settings.database_name]


def get_database():
    """
    Return the MongoDB database instance.

    Other files should call this instead of importing the database directly.
    This makes it easier to mock the database in tests.
    """
    return database