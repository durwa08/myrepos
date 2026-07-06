"""
Shared response schemas used across multiple modules.
"""

from pydantic import BaseModel


class MessageResponse(BaseModel):
    """
    Generic response model for simple success messages.
    """

    message: str