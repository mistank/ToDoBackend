# ToDoBackend Test Suite

Kompletna test suite za FastAPI ToDoBackend aplikaciju.

## Struktura Testova

```

├── conftest.py              # Pytest fixtures (test_db, client, test_user, auth_token, auth_headers)
├── test_authentication.py   # Testovi za login, signup, JWT tokens
├── test_users.py           # Testovi za user CRUD operacije
├── test_projects.py        # Testovi za project management
├── test_tasks.py           # Testovi za task management
├── test_status.py          # Testovi za status operacije
├── test_categories.py      # Testovi za task kategorije
├── test_roles.py           # Testovi za role management
├── test_integration.py     # End-to-end integration testovi
└── README.md              # Ova dokumentacija
```

## Pokretanje Testova

### Svi testovi
```bash
pytest  -v
```

### Specifični test fajl
```bash
pytest test_authentication.py -v
pytest test_users.py -v
pytest test_projects.py -v
```

### Pojedinačan test
```bash
pytest test_authentication.py::test_login -v
```

### Sa coverage izveštajem
```bash
pytest  --cov=app --cov-report=html
```

### Brzi testovi (bez verbose output-a)
```bash
pytest 
```

### Testovi sa detaljnim output-om
```bash
pytest  -v -s
```

## Fixtures

### Glavni Fixtures (iz conftest.py)

#### `test_db`
- **Tip**: MySQL test baza
- **Scope**: function (svež za svaki test)
- **Opis**: Kreira MySQL test bazu sa svim tabelama i čisti podatke nakon testa
- **Korišćenje**: Automatski se ubrizgava preko `client` fixture-a

#### `client`
- **Tip**: FastAPI TestClient
- **Scope**: function
- **Opis**: HTTP klijent za slanje zahteva ka API-ju sa override-ovanom test bazom
- **Korišćenje**:
  ```python
  def test_example(client):
      response = client.get("/users/")
      assert response.status_code == 200
  ```

#### `test_user`
- **Tip**: User model objekat
- **Scope**: function
- **Credentials**:
  - username: `testuser`
  - password: `testpassword123`
  - email: `testuser@example.com`
- **Opis**: Kreiran test korisnik u bazi
- **Korišćenje**:
  ```python
  def test_example(client, test_user):
      response = client.get(f"/users/{test_user.id}")
  ```

#### `auth_token`
- **Tip**: JWT token string
- **Scope**: function
- **Opis**: Validan JWT token za `test_user`
- **Expiration**: 30 minuta
- **Korišćenje**:
  ```python
  def test_example(client, auth_token):
      headers = {"Authorization": f"Bearer {auth_token}"}
      response = client.get("/current-user", headers=headers)
  ```

#### `auth_headers`
- **Tip**: Dictionary
- **Scope**: function
- **Opis**: Headers dictionary sa Authorization header
- **Format**: `{"Authorization": "Bearer {token}"}`
- **Korišćenje**:
  ```python
  def test_example(client, auth_headers):
      response = client.get("/current-user", headers=auth_headers)
  ```

### Custom Fixtures (specifični za test fajlove)

#### `test_project` (test_projects.py)
- Kreiran test projekat

#### `test_status` (test_tasks.py)
- Kreiran test status za taskove

#### `test_category` (test_tasks.py)
- Kreirana test kategorija za taskove

#### `test_task` (test_tasks.py)
- Kreiran test task

## Test Coverage

Za generisanje coverage izveštaja:

```bash
# HTML izveštaj
pytest  --cov=app --cov-report=html
open htmlcov/index.html

# Terminal izveštaj
pytest  --cov=app --cov-report=term

# XML izveštaj (za CI/CD)
pytest  --cov=app --cov-report=xml
```

## Konfiguracija Baze

Testovi koriste MySQL test bazu definisanu u `.env`:

```env
SQLALCHEMY_TEST_DATABASE_URL=mysql+pymysql://user:pass@host:port/test_defaultdb
```

**Napomena**: Test baza koristi `TRUNCATE TABLE` nakon svakog testa za čišćenje podataka.

## Test Kategorije

### Authentication Tests (`test_authentication.py`)
- ✓ Login sa validnim credentials
- ✓ Login sa pogrešnom lozinkom
- ✓ Login nepostojećeg korisnika
- ✓ Signup novog korisnika
- ✓ Signup sa dupliciranim username-om
- ✓ Current user endpoint
- ✓ Unauthorized pristup
- ✓ Invalid token

### User Tests (`test_users.py`)
- ✓ CRUD operacije (Create, Read, Update, Delete)
- ✓ Paginacija
- ✓ Validacija email duplikata
- ✓ Pretraga korisnika

### Project Tests (`test_projects.py`)
- ✓ Kreiranje projekta
- ✓ Dodavanje korisnika na projekat
- ✓ Validacija unique imena projekta

### Task Tests (`test_tasks.py`)
- ✓ Kreiranje taska
- ✓ Dodavanje korisnika na task
- ✓ Task sa više korisnika
- ✓ Validacija foreign keys

### Integration Tests (`test_integration.py`)
- ✓ Kompletan workflow (signup → login → project → task)
- ✓ Projekat sa više taskova
- ✓ Korisnik na više taskova

## Debugging Testova

### Prikaz print statements
```bash
pytest  -v -s
```

### Zaustavljanje na prvoj grešci
```bash
pytest  -x
```

### Pokretanje samo failed testova
```bash
pytest  --lf
```

### Detaljni traceback
```bash
pytest  -v --tb=long
```

## Primer Test Pisanja

### Osnovno (sa debug helper funkcijom)

```python
import pytest
from fastapi import status
from tests.conftest import assert_response

def test_create_user(client, test_db):
    """Test kreiranje novog korisnika"""
    user_data = {
        "username": "newuser",
        "email": "new@example.com",
        "password": "password123",
        "firstName": "New",
        "lastName": "User"
    }
    response = client.post("/users/", json=user_data)

    # Koristi assert_response - automatski prikazuje response body ako padne
    assert_response(response, 200, "Failed to create user")

    # Dodatne provere
    data = response.json()
    assert data["username"] == "newuser"
    assert data["email"] == "new@example.com"
    assert "id" in data

def test_protected_endpoint(client, auth_headers):
    """Test protected endpoint sa autentikacijom"""
    response = client.get("/current-user", headers=auth_headers)

    # Prikaži response ako test padne
    assert_response(response, 200, "Failed to get current user")
    assert response.json()["username"] == "testuser"
```

### Debug Helper - assert_response()

**Zašto koristiti:**
Umesto standardnog:
```python
assert response.status_code == 200  # Ako padne: "AssertionError: assert 400 == 200"
```

Koristi:
```python
assert_response(response, 200, "Creating user")
# Ako padne, prikazuje:
# ================================================================================
# TEST FAILED: Creating user
# ================================================================================
# Status Code: 400
# Expected: 200
# Response Text: {"detail":"Email already registered"}
# ================================================================================
```

**Primeri korišćenja:**

```python
# Osnovno
assert_response(response, 200)

# Sa custom porukom
assert_response(response, 200, "User creation failed")

# Za error response
assert_response(response, 400, "Should return 400 for duplicate email")

# Višestruke provere
response1 = client.post("/users/", json=data)
assert_response(response1, 200, "Create user failed")

response2 = client.get(f"/users/{user_id}")
assert_response(response2, 200, f"Get user {user_id} failed")
```

**Pogledajte `test_example_debug.py` za detaljne primere!**

## 📚 Dodatne Informacije

- [Pytest dokumentacija](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [SQLAlchemy Testing](https://docs.sqlalchemy.org/en/20/orm/session_transaction.html#joining-a-session-into-an-external-transaction-such-as-for-test-suites)
