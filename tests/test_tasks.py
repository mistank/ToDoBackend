import pytest
import uuid
from datetime import datetime, timedelta
from fastapi import status
from tests.conftest import assert_response


def unique_id():
    """Generiše jedinstveni ID za testove"""
    return uuid.uuid4().hex[:8]


@pytest.fixture
def test_status(test_db):
    """Fixture za kreiranje test statusa"""
    from app.db.status.model import Status
    uid = unique_id()
    status_obj = Status(name=f"ToDo_{uid}")
    test_db.add(status_obj)
    test_db.commit()
    test_db.refresh(status_obj)
    return status_obj


@pytest.fixture
def test_category(test_db):
    """Fixture za kreiranje test kategorije"""
    from app.db.taskCategory.model import TaskCategory
    uid = unique_id()
    category = TaskCategory(name=f"Development_{uid}")
    test_db.add(category)
    test_db.commit()
    test_db.refresh(category)
    return category


@pytest.fixture
def test_project_for_task(client, test_user, test_db):
    """Fixture za kreiranje projekta za task testove"""
    uid = unique_id()
    project_data = {
        "name": f"Task_Project_{uid}",
        "owner": test_user.id,
        "description": "Project for tasks",
        "creation_date": datetime.now().isoformat(),
        "deadline": (datetime.now() + timedelta(days=30)).isoformat()
    }
    response = client.post("/projects/", json=project_data)
    assert_response(response, 200, "Failed to create test_project_for_task fixture")
    return response.json()


@pytest.fixture
def test_task(client, test_project_for_task, test_status, test_category):
    """Fixture za kreiranje test taska"""
    uid = unique_id()
    task_data = {
        "name": f"Test_Task_{uid}",
        "status_id": test_status.id,
        "description": "Test task description",
        "deadline": (datetime.now() + timedelta(days=7)).isoformat(),
        "project_id": test_project_for_task["id"],
        "taskCategory_id": test_category.id,
        "priority": "High"
    }
    response = client.post("/tasks/", json=task_data)
    assert_response(response, 200, "Failed to create test_task fixture")
    return response.json()


def test_create_task(client, test_project_for_task, test_status, test_category):
    """Test kreiranje novog taska"""
    uid = unique_id()
    task_data = {
        "name": f"New_Task_{uid}",
        "status_id": test_status.id,
        "description": "New task description",
        "deadline": (datetime.now() + timedelta(days=14)).isoformat(),
        "project_id": test_project_for_task["id"],
        "taskCategory_id": test_category.id,
        "priority": "Medium"
    }
    response = client.post("/tasks/", json=task_data)
    assert_response(response, 200, "Failed to create task")

    data = response.json()
    assert data["name"] == f"New_Task_{uid}"
    assert data["priority"] == "Medium"
    assert "id" in data


def test_add_user_to_task(client, test_task, test_user):
    """Test dodavanje korisnika na task"""
    user_task_data = {
        "uid": test_user.id,
        "tid": test_task["id"]
    }
    response = client.post("/tasks/add_user/", json=user_task_data)
    assert_response(response, 200, "Failed to add user to task")

    data = response.json()
    assert data["uid"] == test_user.id
    assert data["tid"] == test_task["id"]


def test_add_user_to_nonexistent_task(client, test_user, test_db):
    """Test dodavanje korisnika na nepostojeći task"""
    user_task_data = {
        "uid": test_user.id,
        "tid": 99999
    }
    response = client.post("/tasks/add_user/", json=user_task_data)
    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


def test_add_nonexistent_user_to_task(client, test_task, test_db):
    """Test dodavanje nepostojećeg korisnika na task"""
    user_task_data = {
        "uid": 99999,
        "tid": test_task["id"]
    }
    response = client.post("/tasks/add_user/", json=user_task_data)
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_task_with_multiple_users(client, test_task, test_user, test_db):
    """Test dodavanje više korisnika na isti task"""
    uid = unique_id()
    user_data = {
        "username": f"taskuser2_{uid}",
        "email": f"taskuser2_{uid}@example.com",
        "password": "password123",
        "firstName": "Task",
        "lastName": "User2"
    }
    user_response = client.post("/users/", json=user_data)
    assert_response(user_response, 200, "Failed to create second user")
    user2_id = user_response.json()["id"]

    user_task_data1 = {
        "uid": test_user.id,
        "tid": test_task["id"]
    }
    response1 = client.post("/tasks/add_user/", json=user_task_data1)
    assert_response(response1, 200, "Failed to add first user to task")

    user_task_data2 = {
        "uid": user2_id,
        "tid": test_task["id"]
    }
    response2 = client.post("/tasks/add_user/", json=user_task_data2)
    assert_response(response2, 200, "Failed to add second user to task")
