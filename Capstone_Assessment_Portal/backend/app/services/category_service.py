"""
Service layer for category management.

Contains the business logic for creating, retrieving,
updating, and deleting categories.
"""

from app.exceptions.custom_exceptions import (
    CategoryAlreadyExistsException,
    CategoryNotFoundException,
)
from app.models.category_model import CategoryModel
from app.repositories.category_repository import (
    create_category,
    delete_category,
    get_category_by_id,
    get_category_by_name,
    list_categories,
    serialize_category,
    update_category,
)
from app.schemas.category_schema import (
    CategoryCreateRequest,
    CategoryResponse,
    CategoryUpdateRequest,
)


class CategoryService:
    """Service class for category-related business operations."""

    async def create_category(
        self,
        request: CategoryCreateRequest,
        admin_id: str,
    ) -> CategoryResponse:
        """
        Create a new category after validating that the name is unique.
        """
        existing = await get_category_by_name(request.name)
        if existing is not None:
            raise CategoryAlreadyExistsException()

        new_category = CategoryModel(
            name=request.name,
            created_by=admin_id,
        )

        created = await create_category(new_category)
        result = CategoryResponse(**serialize_category(created))
        return result

    async def get_all_categories(self) -> list[CategoryResponse]:
        """
        Retrieve all available categories.
        """
        categories = await list_categories()
        result = [
            CategoryResponse(**serialize_category(category))
            for category in categories
        ]
        return result

    async def get_category_by_id(self, category_id: str) -> CategoryResponse:
        """
        Retrieve a category by its identifier.
        """
        category = await get_category_by_id(category_id)
        if category is None:
            raise CategoryNotFoundException()

        result = CategoryResponse(**serialize_category(category))
        return result

    async def update_category(
        self,
        category_id: str,
        request: CategoryUpdateRequest,
    ) -> CategoryResponse:
        """
        Update an existing category.
        """
        existing = await get_category_by_id(category_id)
        if existing is None:
            raise CategoryNotFoundException()

        updated = await update_category(category_id, request.name)
        result = CategoryResponse(**serialize_category(updated))
        return result

    async def delete_category(self, category_id: str) -> None:
        """
        Delete an existing category.
        """
        deleted = await delete_category(category_id)
        if not deleted:
            raise CategoryNotFoundException()