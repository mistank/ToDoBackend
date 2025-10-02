import pytest
import uuid
from datetime import datetime, timedelta
from fastapi import status
from tests.conftest import assert_response


def unique_id():
    """Generiše jedinstveni ID za testove"""
    return uuid.uuid4().hex[:8]


def test_full_workflow(client, test_db):
    """
    Test kompletnog workflow-a:
    1. Registracija korisnika
    2. Login
    3. Kreiranje projekta
    4. Dodavanje korisnika na projekat
    5. Kreiranje taska
    6. Dodavanje korisnika na task
    """
    uid = unique_id()

    user_data = {
        "username": f"workflow_user_{uid}",
        "email": f"workflow_{uid}@example.com",
        "password": "password123",
        "firstName": "Workflow",
        "lastName": "User"
    }
    signup_response = client.post("/signup", json=user_data)
    assert_response(signup_response, 200, "Signup failed")

    user = signup_response.json()["user"]
    token = signup_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    current_user_response = client.get("/current-user", headers=headers)
    assert_response(current_user_response, 200, "Get current user failed")
    assert current_user_response.json()["username"] == f"workflow_user_{uid}"

    project_data = {
        "name": f"Integration_Project_{uid}",
        "owner": user["id"],
        "description": "Integration test project",
        "creation_date": datetime.now().isoformat(),
        "deadline": (datetime.now() + timedelta(days=30)).isoformat()
    }
    project_response = client.post("/projects/", json=project_data)
    assert_response(project_response, 200, "Create project failed")
    project = project_response.json()

    status_response = client.post(f"/status/{project["id"]}", json={"name": f"ToDo_{uid}"})
    assert_response(status_response, 200, "Create status failed")
    status_id = status_response.json()["id"]

    category_response = client.post("/taskCategories/", json={"name": f"Development_{uid}"})
    assert_response(category_response, 200, "Create category failed")
    category_id = category_response.json()["id"]

    user2_data = {
        "username": f"team_member_{uid}",
        "email": f"member_{uid}@example.com",
        "password": "password123",
        "firstName": "Team",
        "lastName": "Member"
    }
    user2_response = client.post("/users/", json=user2_data)
    assert_response(user2_response, 200, "Create second user failed")
    user2 = user2_response.json()

    pur_data = {
        "uid": user2["id"],
        "pid": project["id"],
        "rid": 2
    }
    pur_response = client.post("/projects/add_user/", json=pur_data)
    assert_response(pur_response, 200, "Add user to project failed")

    task_data = {
        "name": f"Integration_Task_{uid}",
        "status_id": status_id,
        "description": "Task for integration testing",
        "deadline": (datetime.now() + timedelta(days=7)).isoformat(),
        "project_id": project["id"],
        "taskCategory_id": category_id,
        "priority": "High"
    }
    task_response = client.post("/tasks/", json=task_data)
    assert_response(task_response, 200, "Create task failed")
    task = task_response.json()

    user_task_data = {
        "uid": user2["id"],
        "tid": task["id"]
    }
    user_task_response = client.post("/tasks/add_user/", json=user_task_data)
    assert_response(user_task_response, 200, "Add user to task failed")

    assert task["project_id"] == project["id"]
    assert task["status_id"] == status_id
    assert task["taskCategory_id"] == category_id
