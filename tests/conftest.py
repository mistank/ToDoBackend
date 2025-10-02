import pytest
import os
from datetime import timedelta
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from dotenv import load_dotenv

from app.main import app
from app.db.database import Base
from app.routers.authentication import get_db, get_password_hash, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from app.db.user.model import User
from app.db.permission.model import Permission
from app.db.role.model import Role
from app.db.status.model import Status
from app.db.taskCategory.model import TaskCategory
from app.db.project.model import Project
from app.db.task.model import Task
from app.db.projectUserRole.model import ProjectUserRole
from app.db.userTask.model import UserTask
from app.db.resetToken.model import ResetToken
from app.db.projectStatus.model import ProjectStatus

load_dotenv()

SQLALCHEMY_TEST_DATABASE_URL = os.getenv("SQLALCHEMY_TEST_DATABASE_URL")


def assert_response(response, expected_status=200, message=""):
    """
    Helper funkcija koja proverava status code i prikazuje response body ako test padne.
    """
    try:
        assert response.status_code == expected_status, (
            f"{message}\n"
            f"Expected status: {expected_status}\n"
            f"Actual status: {response.status_code}\n"
            f"Response body: {response.text}\n"
            f"Response JSON: {response.json() if response.text else 'No content'}"
        )
    except Exception as e:
        print(f"\n{'='*80}")
        print(f"TEST FAILED: {message}")
        print(f"{'='*80}")
        print(f"Status Code: {response.status_code}")
        print(f"Expected: {expected_status}")
        print(f"Response Text: {response.text}")
        print(f"{'='*80}\n")
        raise


@pytest.fixture(scope="function")
def test_db():
    """
    Creates a MySQL test database with all tables.
    Koristi production MySQL server ali kreira izolovane test podatke.
    Database tables su očišćene nakon svakog testa.
    """
    engine = create_engine(
        SQLALCHEMY_TEST_DATABASE_URL,
        pool_pre_ping=True,
        echo=False
    )

    Base.metadata.create_all(bind=engine)

    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.rollback()

        db.execute(text("SET FOREIGN_KEY_CHECKS = 0"))

        for table in reversed(Base.metadata.sorted_tables):
            if table.name not in ["permission", "role"]:
                db.execute(text(f"TRUNCATE TABLE {table.name}"))

        db.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
        db.commit()

        db.close()
        engine.dispose()


@pytest.fixture(scope="function")
def client(test_db):
    """
    FastAPI TestClient that uses the test database.
    Overrides the get_db dependency to use test_db instead of production database.
    """
    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_user(client, test_db):
    """
    Creates a test user in the database and returns the user object.
    User has standard permission (permission_id=2).

    IMPORTANT: Depends on 'client' first to ensure same test_db instance is used.
    """
    permission = test_db.query(Permission).filter(Permission.id == 2).first()
    if not permission:
        permission = Permission(id=2, name="user")
        test_db.add(permission)
        test_db.commit()
        test_db.refresh(permission)

    hashed_password = get_password_hash("testpassword123")
    user = User(
        firstName="Test",
        lastName="User",
        username="testuser",
        email="testuser@example.com",
        hashed_password=hashed_password,
        is_active=True,
        permission_id=2
    )

    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)

    return user


@pytest.fixture(scope="function")
def auth_token(test_user):
    """
    Generates a valid JWT token for the test user.
    Token expires in 30 minutes (ACCESS_TOKEN_EXPIRE_MINUTES).
    """
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(
        data={"sub": test_user.username},
        expires_delta=access_token_expires
    )
    return token


@pytest.fixture(scope="function")
def auth_headers(auth_token):
    """
    Returns a headers dictionary with Authorization header containing the JWT token.
    Ready to use in HTTP requests: client.get("/endpoint", headers=auth_headers)
    """
    return {
        "Authorization": f"Bearer {auth_token}"
    }
