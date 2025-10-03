# ToDoBackend - FastAPI Project Management API

![Tests](https://github.com/yourusername/ToDoBackend/actions/workflows/test-and-build.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.12-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111.0-green.svg)
![MySQL](https://img.shields.io/badge/MySQL-8.0-orange.svg)

RESTful API za upravljanje projektima, taskovima i korisnicima, napravljen sa FastAPI i MySQL bazom.

##  Features

-  **User Management** - Registracija, autentikacija, JWT tokens
-  **Project Management** - Kreiranje i upravljanje projektima
-  **Task Management** - Taskovi sa statusima, kategorijama i prioritetima
-  **Team Collaboration** - Dodavanje korisnika na projekte i taskove
-  **Authentication** - JWT-based autentikacija sa permission sistemom
-  **Status Tracking** - Custom statusi za svaki projekat
-  **Categories** - Kategorizacija taskova

##  Tech Stack

- **Framework:** FastAPI 0.111.0
- **Database:** MySQL 8.0
- **ORM:** SQLAlchemy 2.0
- **Authentication:** JWT (PyJWT)
- **Password Hashing:** Bcrypt
- **Testing:** Pytest + MySQL test database
- **Validation:** Pydantic v2

##  Installation

### Prerequisites

- Python 3.12+
- MySQL 8.0+
- pip

### Setup

1. **Clone repository**
```bash
git clone https://github.com/yourusername/ToDoBackend.git
cd ToDoBackend
```

2. **Create virtual environment**
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# ili
.venv\Scripts\activate  # Windows
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**

Kreiraj `.env` fajl:
```env
SQLALCHEMY_DATABASE_URL=mysql+pymysql://user:password@localhost:3306/defaultdb
SQLALCHEMY_TEST_DATABASE_URL=mysql+pymysql://user:password@localhost:3306/test_default_db
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

5. **Run application**
```bash
uvicorn app.main:app --reload
```

API će biti dostupan na: `http://localhost:8000`

##  API Documentation

Automatski generisana dokumentacija:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### Main Endpoints

#### Authentication
```
POST   /signup         - Registracija novog korisnika
POST   /login          - Login i JWT token
GET    /current-user   - Informacije o trenutnom korisniku
```

#### Users
```
GET    /users/         - Lista svih korisnika
GET    /users/{id}     - Jedan korisnik
POST   /users/         - Kreiranje korisnika
PUT    /users/{id}     - Ažuriranje korisnika
DELETE /users/{id}     - Brisanje korisnika
GET    /search-users/  - Pretraga korisnika
```

#### Projects
```
GET    /projects/      - Lista projekata
POST   /projects/      - Kreiranje projekta
POST   /projects/add_user/  - Dodavanje korisnika na projekat
```

#### Tasks
```
GET    /tasks/         - Lista taskova
POST   /tasks/         - Kreiranje taska
POST   /tasks/add_user/  - Dodavanje korisnika na task
```

#### Status
```
POST   /status/{project_id}  - Kreiranje statusa za projekat
GET    /status/              - Lista svih statusa
GET    /statuses_from_project/{project_id}  - Statusi projekta
```

##  Testing

Aplikacija ima kompletan test suite sa MySQL test bazom.

### Run Tests

```bash
# Svi testovi
pytest -v

# Sa coverage
pytest --cov=app --cov-report=html
open htmlcov/index.html

# Jedan test modul
pytest tests/test_users.py -v

# Debug mode
pytest -v -s
```

### Test Coverage

-  Authentication tests
-  User CRUD operations
-  Project management
-  Task management
-  Status operations
-  Integration tests

##  Database Schema

### Main Tables

- **user** - Korisnici sa permissions
- **project** - Projekti
- **task** - Taskovi sa prioritetom
- **status** - Statusi
- **taskCategory** - Kategorije taskova
- **role** - Role za projekte
- **permission** - User permissions (admin/user)

### Relations

- **projectUserRole** - Many-to-many: projekti ↔ korisnici
- **userTask** - Many-to-many: taskovi ↔ korisnici
- **projectStatus** - Many-to-many: projekti ↔ statusi

##  Exception Handling

Aplikacija koristi centralizovan exception handling sistem:

-  Konzistentni HTTP status kodovi
-  Automatski rollback na greške
-  Custom poruke za IntegrityError
-  Logging svih grešaka

##  CI/CD

GitHub Actions automatski pokreće:

-  Pytest testove sa MySQL
-  Code linting (flake8)
-  Code formatting check (Black)
-  Coverage reports
-  Build validation

Konfiguracija: [.github/workflows/README.md](.github/workflows/README.md)

##  Project Structure

```
ToDoBackend/
├── app/
│   ├── main.py              # FastAPI app
│   ├── exceptions.py        # Centralizovan exception handling
│   ├── db/
│   │   ├── database.py      # Database konfiguracija
│   │   ├── user/            # User model, schema, CRUD
│   │   ├── project/         # Project model, schema, CRUD
│   │   ├── task/            # Task model, schema, CRUD
│   │   ├── status/          # Status model, schema, CRUD
│   │   └── ...
│   └── routers/
│       ├── authentication.py
│       ├── user.py
│       ├── project.py
│       └── ...
├── tests/
│   ├── conftest.py          # Pytest fixtures
│   ├── test_authentication.py
│   ├── test_users.py
│   └── ...
├── .github/
│   └── workflows/
│       ├── test-and-build.yml
│       └── deploy.yml
├── requirements.txt
├── .env
└── README.md
```
