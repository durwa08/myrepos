"""
Standalone script to create the single admin account.

Run this manually once, after setting up the database, using:
    python -m app.scripts.seed_admin

Prompts for admin username, email, and password on the command line,
asks for password confirmation to catch typos, validates the password
against the same rules used at registration, and inserts the admin
document directly — bypassing the public /auth/register endpoint,
which only ever creates students.

Note: password input is visible on screen (not masked). This is a
deliberate tradeoff for this one-time local setup script, since
getpass.getpass() does not reliably capture input in Git Bash (MINGW64)
on Windows and can silently produce an empty password.
"""

import asyncio
import logging

from app.constants import ADMIN_ROLE, INVALID_PASSWORD_MESSAGE
from app.models.user_model import UserModel
from app.repositories.user_repository import create_user, get_user_by_email
from app.schemas.user_schema import PASSWORD_PATTERN
from app.utils.security import hash_password

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def seed_admin() -> None:
    """
    Create the admin account if one does not already exist for the
    given email.
    """
    username = input("Admin username: ").strip()
    email = input("Admin email: ").strip()
    password = input("Admin password: ").strip()
    confirm_password = input("Confirm admin password: ").strip()

    if password != confirm_password:
        logger.error("Passwords do not match. Please run the script again.")
        return

    if not PASSWORD_PATTERN.match(password):
        logger.error(INVALID_PASSWORD_MESSAGE)
        return

    existing_user = await get_user_by_email(email)
    if existing_user is not None:
        logger.error("A user with email '%s' already exists.", email)
        return

    hashed = hash_password(password)
    admin_user = UserModel(
        username=username,
        email=email,
        hashed_password=hashed,
        role=ADMIN_ROLE,
    )

    created_admin = await create_user(admin_user)
    logger.info("Admin created successfully with id=%s", created_admin["_id"])


if __name__ == "__main__":
    asyncio.run(seed_admin())