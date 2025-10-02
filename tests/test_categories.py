import pytest
import uuid
from fastapi import status
from tests.conftest import assert_response


def unique_name(prefix="Category"):
    """Generiše jedinstveno ime za kategoriju"""
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


def test_create_category(client, test_db):
    """Test kreiranje nove kategorije"""
    category_name = unique_name("BugFix")
    category_data = {
        "name": category_name
    }
    response = client.post("/taskCategories/", json=category_data)
    assert_response(response, 200, f"Failed to create category '{category_name}'")

    data = response.json()
    assert data["name"] == category_name
    assert "id" in data


def test_get_all_categories(client, test_db):
    """Test dobavljanje svih kategorija"""
    # Kreiranje nekoliko kategorija sa jedinstvenim imenima
    created_categories = []
    for i in range(3):
        category_name = unique_name(f"GetAll{i}")
        response = client.post("/taskCategories/", json={"name": category_name})
        assert_response(response, 200, f"Failed to create category {i}")
        created_categories.append(category_name)

    response = client.get("/taskCategories/")
    assert_response(response, 200, "Failed to get all categories")

    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 3

    category_names = [cat["name"] for cat in data]
    for created_name in created_categories:
        assert created_name in category_names


def test_create_duplicate_category(client, test_db):
    """Test kreiranje kategorije sa već postojećim imenom"""
    category_name = unique_name("Duplicate")
    category_data = {"name": category_name}

    response1 = client.post("/taskCategories/", json=category_data)
    assert_response(response1, 200, "Failed to create first category")

    response2 = client.post("/taskCategories/", json=category_data)
    assert response2.status_code in [400, 409, 500], (
        f"Expected error status for duplicate, got {response2.status_code}. "
        f"Response: {response2.text}"
    )


def test_get_category_by_id(client, test_db):
    """Test dobavljanje kategorije po ID-u"""
    category_name = unique_name("Feature")
    category_data = {"name": category_name}
    create_response = client.post("/taskCategories/", json=category_data)
    assert_response(create_response, 200, "Failed to create category")

    category_id = create_response.json()["id"]

    response = client.get(f"/taskCategories/{category_id}")
    assert_response(response, 200, f"Failed to get category with id {category_id}")

    data = response.json()
    assert data["id"] == category_id
    assert data["name"] == category_name
