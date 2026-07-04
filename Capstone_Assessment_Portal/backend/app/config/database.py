"""
MongoDB connection setup and index initialization.
"""

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


async def init_indexes():
    """
    Create required MongoDB indexes at application startup.

    Ensures a quiz title is unique within a given category at the
    database level, guarding against race conditions that a
    pre-check in the service layer alone cannot fully prevent.
    """
    await database["quizzes"].create_index(
        [("title", 1), ("category_id", 1)],
        unique=True,
    )