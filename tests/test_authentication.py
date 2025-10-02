import pytest
import uuid
from fastapi import status
from tests.conftest import assert_response


def unique_id():
    """Generiše jedinstveni ID za testove"""
    return uuid.uuid4().hex[:8]


def test_current_user(client, auth_headers, test_user):
    """Test da authenticated user može pristupiti svom profilu"""
    response = client.get("/current-user", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "testuser@example.com"
    assert data["firstName"] == "Test"
    assert data["lastName"] == "User"


def test_login(client, test_user):
    """Test login endpoint-a"""
    response = client.post(
        "/login",
        data={"username": "testuser", "password": "testpassword123"}
    )
    assert response.status_code == 200
    response_data = response.json()
    assert "access_token" in response_data
    assert response_data["token_type"] == "bearer"
    assert response_data["user"]["username"] == "testuser"


def test_login_wrong_password(client, test_user):
    """Test login sa pogrešnom lozinkom"""
    response = client.post(
        "/login",
        data={"username": "testuser", "password": "wrongpassword"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Incorrect username or password"


def test_login_nonexistent_user(client, test_db):
    """Test login sa nepostojećim korisnikom"""
    response = client.post(
        "/login",
        data={"username": "nonexistent", "password": "somepassword"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Incorrect username or password"


def test_unauthorized_access(client, test_db):
    """Test da neautorizovani korisnik ne može pristupiti"""
    response = client.get("/current-user")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_invalid_token(client, test_db):
    """Test sa nevažećim tokenom"""
    invalid_headers = {"Authorization": "Bearer invalid_token_here"}
    response = client.get("/current-user", headers=invalid_headers)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_signup(client, test_db):
    """Test registracije novog korisnika"""
    uid = unique_id()
    new_user_data = {
        "username": f"newuser_{uid}",
        "email": f"newuser_{uid}@example.com",
        "password": "newpassword123",
        "firstName": "New",
        "lastName": "User"
    }
    response = client.post("/signup", json=new_user_data)
    assert_response(response, 200, "Signup failed")

    response_data = response.json()
    assert "access_token" in response_data
    assert response_data["user"]["username"] == f"newuser_{uid}"
    assert response_data["user"]["email"] == f"newuser_{uid}@example.com"


def test_signup_duplicate_username(client, test_user):
    """Test registracije sa postojećim username-om"""
    duplicate_user_data = {
        "username": "testuser",  # Already exists
        "email": "different@example.com",
        "password": "password123",
        "firstName": "Another",
        "lastName": "User"
    }
    response = client.post("/signup", json=duplicate_user_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Username already registered"


def test_token_expiration_structure(auth_token):
    """Test da token ima validnu strukturu"""
    assert isinstance(auth_token, str)
    assert len(auth_token) > 0
    # JWT token ima 3 dela odvojena tačkama
    parts = auth_token.split(".")
    assert len(parts) == 3
