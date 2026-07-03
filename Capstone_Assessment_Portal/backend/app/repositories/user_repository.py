from app.config.database import get_database
from app.models.user_model import UserModel
from bson import ObjectId


database = get_database()
user_collection = database["users"]


async def get_user_by_email(email: str) -> dict | None:
    """
    Retrieve a user by email.

    Used for checking duplicate registrations and finding users during login.
    """
    user = await user_collection.find_one({"email": email})
    return user


async def create_user(user: UserModel) -> dict:
    """
    Create a new user in the database.

    The password is expected to be hashed before this function is called.
    MongoDB generates the _id automatically, and the created document is
    fetched again before being returned.
    """
    user_dict = user.model_dump(by_alias=True, exclude={"id"})

    result = await user_collection.insert_one(user_dict)

    created_user = await user_collection.find_one({"_id": result.inserted_id})
    return created_user


def serialize_user(user: dict) -> dict:
    """
    Convert a MongoDB user document into the response format.

    Converts the MongoDB ObjectId to a string for API responses.
    """
    return {
        "id": str(user["_id"]),
        "username": user["username"],
        "email": user["email"],
        "role": user["role"],
    }