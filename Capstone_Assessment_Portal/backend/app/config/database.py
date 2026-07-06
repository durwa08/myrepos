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


async def ensure_indexes():
    """
    Create required MongoDB indexes during application startup.

    Ensures quiz titles are unique within a category, and category
    names are globally unique, at the database level — guarding
    against race conditions that a pre-check in the service layer
    alone cannot fully prevent.
    """
    quiz_collection = database["quizzes"]
    await quiz_collection.create_index(
        [("title", 1), ("category_id", 1)],
        unique=True,
        name="unique_title_per_category",
    )

    category_collection = database["categories"]
    await category_collection.create_index(
        "name",
        unique=True,
        name="unique_category_name",
    )