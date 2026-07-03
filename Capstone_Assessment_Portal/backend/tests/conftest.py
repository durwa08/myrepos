"""
Shared pytest fixtures available to all test modules.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client() -> TestClient:
    """
    Provide a FastAPI TestClient for making requests against the app
    in route-level tests, without starting a real server.
    """
    return TestClient(app)