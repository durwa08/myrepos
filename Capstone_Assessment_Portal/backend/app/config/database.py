from motor.motor_asyncio import AsyncIOMotorClient

from app.config.settings import settings

client = AsyncIOMotorClient(settings.mongo_uri)
database = client[settings.database_name]


def get_database():
    """
    Return the MongoDB database instance.

    Other modules should use this function instead of importing
    the database object directly. This simplifies testing and
    keeps database access centralized.
    """
    return database


async def ensure_indexes():
    """
    Create required MongoDB indexes during application startup.
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