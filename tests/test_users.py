import uuid
from tests.conftest import assert_response


def unique_id():
    """Generiše jedinstveni ID za testove"""
    return uuid.uuid4().hex[:8]


def test_create_user(client, test_db):
    """Test kreiranje novog korisnika"""
    uid = unique_id()
    user_data = {
        "username": f"johndoe",
        "email": f"johndoe@example.com",
        "password": "password123",
        "firstName": "John",
        "lastName": "Doe"
    }
    response = client.post("/users/", json=user_data)
    assert_response(response, 200, "Failed to create user")

    data = response.json()
    assert data["username"] == "johndoe"
    assert data["email"] == "johndoe@example.com"
    assert "id" in data


def test_create_user_duplicate_email(client, test_user):
    """Test kreiranje korisnika sa već postojećim emailom"""
    user_data = {
        "username": "different",
        "email": "testuser@example.com",
        "password": "password123",
        "firstName": "John",
        "lastName": "Doe"
    }
    response = client.post("/users/", json=user_data)
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"


def test_read_users(client, test_user):
    """Test dobavljanje liste svih korisnika"""
    response = client.get("/users/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_read_user_by_id(client, test_user):
    """Test dobavljanje korisnika po ID-u"""
    random_id = uuid.uuid4().hex[:8]
    response = client.post("/users/", json={
        "username": f"test_user_{random_id}",
        "email": f"test_{random_id}@example.com",
        "password": "password123",
        "firstName": "John",
        "lastName": "Doe"
    })
    assert response.status_code == 200
    user_id = response.json()["id"]
    get_response = client.get(f"/users/{user_id}")
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["id"] == user_id
    assert data["username"] == f"test_user_{random_id}"


def test_read_user_not_found(client, test_db):
    """Test dobavljanje nepostojećeg korisnika"""
    response = client.get("/users/99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_update_user(client, test_user):
    """Test ažuriranje korisnika"""
    update_data = {
        "username": "johndoe",
        "email": "newemail@example.com",
        "firstName": "Updated",
        "lastName": "Name"
    }
    response = client.put(f"/users/{test_user.username}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "newemail@example.com"
    assert data["firstName"] == "Updated"


def test_update_user_not_found(client, test_db):
    """Test ažuriranje nepostojećeg korisnika"""
    update_data = {
        "username": "nonexistent",
        "email": "test@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    response = client.put("/users/nonexistent", json=update_data)
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_delete_user(client, test_user):
    """Test brisanje korisnika"""
    random_id = uuid.uuid4().hex[:8]
    response = client.post("/users/", json={
        "username": f"test_user_{random_id}",
        "email": f"test_{random_id}@example.com",
        "password": "password123",
        "firstName": "John",
        "lastName": "Doe"
    })
    assert response.status_code == 200
    user_id = response.json()["id"]
    response = client.delete(f"/users/{user_id}")
    assert response.status_code == 200
    response = client.get(f"/users/{user_id}")
    assert response.status_code == 404


def test_delete_user_not_found(client, test_db):
    """Test brisanje nepostojećeg korisnika"""
    response = client.delete("/users/99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_read_users_pagination(client, test_user, test_db):
    """Test paginacija za listu korisnika"""
    uid = unique_id()
    for i in range(5):
        user_data = {
            "username": f"user_{uid}_{i}",
            "email": f"user_{uid}_{i}@example.com",
            "password": "password123",
            "firstName": f"User{i}",
            "lastName": "Test",
        }
        response = client.post("/users/", json=user_data)
        assert_response(response, 200, f"Failed to create user {i}")

    response = client.get("/users/?skip=0&limit=3")
    assert_response(response, 200, "Failed to get users with pagination")
    data = response.json()
    assert len(data) <= 3
