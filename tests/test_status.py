import pytest
import uuid
from datetime import datetime, timedelta
from fastapi import status
from tests.conftest import assert_response


def unique_id():
    """Generiše jedinstveni ID"""
    return uuid.uuid4().hex[:8]


def unique_name(prefix="Status"):
    """Generiše jedinstveno ime za status"""
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


@pytest.fixture
def test_project(client, test_user, test_db):
    """Fixture za kreiranje test projekta potrebnog za statusе"""
    uid = unique_id()
    project_data = {
        "name": f"StatusTest_Project_{uid}",
        "owner": test_user.id,
        "description": "Test project for status tests",
        "creation_date": datetime.now().isoformat(),
        "deadline": (datetime.now() + timedelta(days=30)).isoformat()
    }
    response = client.post("/projects/", json=project_data)
    assert_response(response, 200, "Failed to create test_project fixture for status tests")
    return response.json()


def test_create_status(client, test_user, test_project, test_db):
    """Test kreiranje novog statusa za projekat"""
    status_name = unique_name("InProgress")
    status_data = {
        "name": status_name
    }
    response = client.post(f"/status/{test_project['id']}", json=status_data)
    assert_response(response, 200, f"Failed to create status '{status_name}'")

    data = response.json()
    assert data["name"] == status_name
    assert "id" in data


def test_get_all_statuses(client, test_user, test_project, test_db):
    """Test dobavljanje svih statusa"""
    created_statuses = []
    for i, prefix in enumerate(["ToDo", "InProgress", "Done"]):
        status_name = unique_name(prefix)
        response = client.post(f"/status/{test_project['id']}", json={"name": status_name})
        assert_response(response, 200, f"Failed to create status {i}")
        created_statuses.append(status_name)

    response = client.get("/status/")
    assert_response(response, 200, "Failed to get all statuses")

    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 3

    status_names = [s["name"] for s in data]
    for created_name in created_statuses:
        assert created_name in status_names


def test_create_duplicate_status(client, test_user, test_project, test_db):
    """Test kreiranje statusa sa već postojećim imenom u istom projektu"""
    status_name = unique_name("Duplicate")
    status_data = {"name": status_name}

    response1 = client.post(f"/status/{test_project['id']}", json=status_data)
    assert_response(response1, 200, "Failed to create first status")

    response2 = client.post(f"/status/{test_project['id']}", json=status_data)
    assert response2.status_code in [400, 500], (
        f"Expected error status for duplicate projectStatus entry, got {response2.status_code}. "
        f"Response: {response2.text}"
    )
