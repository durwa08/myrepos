"""
API routes for category management.

Create, update, and delete operations are restricted to administrators.
Listing categories is available to any authenticated user.
"""

from fastapi import APIRouter, Depends, status

from app.middleware.auth_middleware import get_current_user, require_admin
from app.schemas.category_schema import (
    CategoryCreateRequest,
    CategoryResponse,
    CategoryUpdateRequest,
)
from app.services.category_service import CategoryService

router = APIRouter(prefix="/categories", tags=["Categories"])
category_service = CategoryService()


@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    request: CategoryCreateRequest,
    current_user: dict = Depends(require_admin),
):
    """
    Create a new category.

    Only administrators are authorized to create categories.
    """
    result = await category_service.create_category(
        request,
        admin_id=current_user["sub"],
    )
    return result


@router.get("", response_model=list[CategoryResponse])
async def list_categories(current_user: dict = Depends(get_current_user)):
    """
    Retrieve all available categories.

    Accessible to any authenticated user.
    """
    result = await category_service.get_all_categories()
    return result


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: str,
    current_user: dict = Depends(get_current_user),
):
    """
    Retrieve a category by its identifier.

    Accessible to any authenticated user.
    """
    result = await category_service.get_category_by_id(category_id)
    return result


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: str,
    request: CategoryUpdateRequest,
    current_user: dict = Depends(require_admin),
):
    """
    Update an existing category.

    Only administrators are authorized to update categories.
    """
    result = await category_service.update_category(category_id, request)
    return result


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: str,
    current_user: dict = Depends(require_admin),
):
    """
    Delete a category.

    Only administrators are authorized to delete categories.
    """
    await category_service.delete_category(category_id)