import pytest
import uuid
from datetime import datetime, timedelta
from fastapi import status
from tests.conftest import assert_response


def unique_id():
    """Generiše jedinstveni ID za testove"""
    return uuid.uuid4().hex[:8]

def test_create_project(client, test_user, test_db):
    """Test kreiranje novog projekta"""
    uid = unique_id()
    project_data = {
        "name": f"New_Project_{uid}",
        "owner": test_user.id,
        "description": "New project description",
        "creation_date": datetime.now().isoformat(),
        "deadline": (datetime.now() + timedelta(days=60)).isoformat()
    }
    response = client.post("/projects/", json=project_data)
    assert_response(response, 200, "Failed to create project")

    data = response.json()
    assert data["name"] == f"New_Project_{uid}"
    assert data["owner"] == test_user.id
    assert "id" in data


def test_create_project_duplicate_name(client, test_user, test_db):
    """Test kreiranje projekta sa već postojećim imenom"""
    uid = unique_id()
    project_name = f"Duplicate_Project_{uid}"

    project_data1 = {
        "name": project_name,
        "owner": test_user.id,
        "description": "First project",
        "creation_date": datetime.now().isoformat(),
        "deadline": (datetime.now() + timedelta(days=30)).isoformat()
    }
    response1 = client.post("/projects/", json=project_data1)
    assert_response(response1, 200, "Failed to create first project")

    project_data2 = {
        "name": project_name,  # Isto ime
        "owner": test_user.id,
        "description": "Another description",
        "creation_date": datetime.now().isoformat(),
        "deadline": (datetime.now() + timedelta(days=30)).isoformat()
    }
    response2 = client.post("/projects/", json=project_data2)
    assert response2.status_code in [400, 409, 500], (
        f"Expected error for duplicate project name, got {response2.status_code}. "
        f"Response: {response2.text}"
    )
