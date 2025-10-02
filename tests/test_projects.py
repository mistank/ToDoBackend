import pytest
import uuid
from datetime import datetime, timedelta
from fastapi import status
from tests.conftest import assert_response


def unique_id():
    """Generiše jedinstveni ID za testove"""
    return uuid.uuid4().hex[:8]


@pytest.fixture
def test_project(client, test_user, test_db):
    """Fixture za kreiranje test projekta"""
    uid = unique_id()
    project_data = {
        "name": f"Test_Project_{uid}",
        "owner": test_user.id,
        "description": "Test project description",
        "creation_date": datetime.now().isoformat(),
        "deadline": (datetime.now() + timedelta(days=30)).isoformat()
    }
    response = client.post("/projects/", json=project_data)
    assert_response(response, 200, "Failed to create test_project fixture")
    return response.json()


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


def test_add_user_to_project(client, test_project, test_db):
    """Test dodavanje korisnika na projekat"""
    uid = unique_id()
    user_data = {
        "username": f"projectuser_{uid}",
        "email": f"projectuser_{uid}@example.com",
        "password": "password123",
        "firstName": "Project",
        "lastName": "User"
    }
    user_response = client.post("/users/", json=user_data)
    assert_response(user_response, 200, "Failed to create user")
    user_id = user_response.json()["id"]

    pur_data = {
        "uid": user_id,
        "pid": test_project["id"],
        "rid": 2  # Default role
    }
    response = client.post("/projects/add_user/", json=pur_data)
    assert_response(response, 200, "Failed to add user to project")

    data = response.json()
    assert data["uid"] == user_id
    assert data["pid"] == test_project["id"]


def test_add_user_to_nonexistent_project(client, test_user):
    """Test dodavanje korisnika na nepostojeći projekat"""
    pur_data = {
        "uid": test_user.id,
        "pid": 99999,
        "rid": 2
    }
    response = client.post("/projects/add_user/", json=pur_data)
    assert response.status_code == 404
    assert response.json()["detail"] == "Project not found"


def test_add_nonexistent_user_to_project(client, test_project):
    """Test dodavanje nepostojećeg korisnika na projekat"""
    pur_data = {
        "uid": 99999,
        "pid": test_project["id"],
        "rid": 2
    }
    response = client.post("/projects/add_user/", json=pur_data)
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"
