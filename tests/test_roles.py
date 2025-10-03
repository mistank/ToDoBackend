import pytest
import uuid
from fastapi import status
from tests.conftest import assert_response


def unique_name(prefix="Role"):
    """Generiše jedinstveno ime za role"""
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


def test_create_role(client, test_db):
    """Test kreiranje nove role"""
    role_name = unique_name("Developer")
    role_data = {
        "name": role_name
    }
    response = client.post("/roles/", json=role_data)
    assert_response(response, 200, f"Failed to create role '{role_name}'")

    data = response.json()
    assert data["name"] == role_name
    assert "id" in data
