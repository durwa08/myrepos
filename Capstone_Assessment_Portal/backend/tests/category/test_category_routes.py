"""
Test cases for category routes.
"""

from unittest.mock import AsyncMock

from app.main import app
from app.middleware.auth_middleware import get_current_user, require_admin
from app.schemas.category_schema import CategoryResponse
from app.schemas.common_schema import MessageResponse

def test_create_category_route_as_admin(client, mocker):
    """
    Test the create category endpoint returns 201 for an admin user.
    """
    app.dependency_overrides[require_admin] = lambda: {
        "sub": "durwapahariya08@gmail.com",
        "role": "admin",
    }

    mocker.patch(
        "app.api.v1.category_routes.CategoryService.create_category",
        new=AsyncMock(
            return_value=CategoryResponse(
                id="1",
                name="Python",
                created_by="durwapahariya08@gmail.com",
            )
        ),
    )

    response = client.post(
        "/categories",
        json={"name": "Python"},
        headers={"Authorization": "Bearer fake_token"},
    )

    assert response.status_code == 201
    assert response.json()["name"] == "Python"

    app.dependency_overrides.clear()


def test_create_category_route_duplicate(client, mocker):
    """
    Test the create category endpoint returns 400 for a duplicate name.
    """
    from app.exceptions.custom_exceptions import CategoryAlreadyExistsException

    app.dependency_overrides[require_admin] = lambda: {
        "sub": "durwapahariya08@gmail.com",
        "role": "admin",
    }

    mocker.patch(
        "app.api.v1.category_routes.CategoryService.create_category",
        new=AsyncMock(side_effect=CategoryAlreadyExistsException()),
    )

    response = client.post(
        "/categories",
        json={"name": "Python"},
        headers={"Authorization": "Bearer fake_token"},
    )

    assert response.status_code == 400

    app.dependency_overrides.clear()


def test_list_categories_route(client, mocker):
    """
    Test the list categories endpoint returns 200 with a list.
    """
    app.dependency_overrides[get_current_user] = lambda: {
        "sub": "durwa08@gmail.com",
        "role": "student",
    }

    mocker.patch(
        "app.api.v1.category_routes.CategoryService.get_all_categories",
        new=AsyncMock(
            return_value=[
                CategoryResponse(
                    id="1", name="Python", created_by="durwapahariya08@gmail.com"
                )
            ]
        ),
    )

    response = client.get(
        "/categories", headers={"Authorization": "Bearer fake_token"}
    )

    assert response.status_code == 200
    assert response.json()[0]["name"] == "Python"

    app.dependency_overrides.clear()


def test_update_category_route_as_admin(client, mocker):
    """
    Test the update category endpoint returns 200 for an admin user.
    """
    app.dependency_overrides[require_admin] = lambda: {
        "sub": "durwapahariya08@gmail.com",
        "role": "admin",
    }

    mocker.patch(
        "app.api.v1.category_routes.CategoryService.update_category",
        new=AsyncMock(
            return_value=CategoryResponse(
                id="1",
                name="Advanced Python",
                created_by="durwapahariya08@gmail.com",
            )
        ),
    )

    response = client.put(
        "/categories/1",
        json={"name": "Advanced Python"},
        headers={"Authorization": "Bearer fake_token"},
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Advanced Python"

    app.dependency_overrides.clear()


def test_update_category_route_not_found(client, mocker):
    """
    Test the update category endpoint returns 404 for a missing category.
    """
    from app.exceptions.custom_exceptions import CategoryNotFoundException

    app.dependency_overrides[require_admin] = lambda: {
        "sub": "durwapahariya08@gmail.com",
        "role": "admin",
    }

    mocker.patch(
        "app.api.v1.category_routes.CategoryService.update_category",
        new=AsyncMock(side_effect=CategoryNotFoundException()),
    )

    response = client.put(
        "/categories/missing_id",
        json={"name": "Advanced Python"},
        headers={"Authorization": "Bearer fake_token"},
    )

    assert response.status_code == 404

    app.dependency_overrides.clear()


def test_delete_category_route_as_admin(client, mocker):
    """
    Test the delete category endpoint returns 200 with a success message.
    """
    app.dependency_overrides[require_admin] = lambda: {
        "sub": "durwapahariya08@gmail.com",
        "role": "admin",
    }

    mocker.patch(
        "app.api.v1.category_routes.CategoryService.delete_category",
        new=AsyncMock(
            return_value=MessageResponse(message="Category deleted successfully.")
        ),
    )

    response = client.delete(
        "/categories/1", headers={"Authorization": "Bearer fake_token"}
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Category deleted successfully."

    app.dependency_overrides.clear()
    
def test_create_category_route_without_admin_token(client):
    """
    Test the create category endpoint returns 401/403 without admin auth.
    """
    response = client.post("/categories", json={"name": "Python"})

    assert response.status_code in (401, 403)