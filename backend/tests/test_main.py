"""
Tests for main application endpoints.
"""

import pytest
from fastapi.testclient import TestClient


def test_root_endpoint(client: TestClient):
    """Test root endpoint returns API information."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data
    assert "status" in data
    assert data["status"] == "operational"


def test_health_endpoint(client: TestClient):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_readiness_endpoint(client: TestClient):
    """Test readiness check endpoint."""
    response = client.get("/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"


def test_openapi_docs(client: TestClient):
    """Test that OpenAPI docs are accessible."""
    response = client.get("/docs")
    assert response.status_code == 200


def test_openapi_spec(client: TestClient):
    """Test OpenAPI specification endpoint."""
    response = client.get("/api/v1/openapi.json")
    assert response.status_code == 200
    spec = response.json()
    assert "openapi" in spec
    assert "info" in spec
    assert "paths" in spec
