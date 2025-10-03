# GitHub Actions CI/CD

Automatski testovi i deployment za ToDoBackend projekat.

##  Workflows

### 1. **Test and Build** (`test-and-build.yml`)

Automatski se pokreće na svaki push i pull request.

**Šta radi:**
-  Podiže MySQL test bazu
-  Instalira dependencies
-  Pokreće sve pytest testove
-  Generiše coverage report
-  Proverava code formatting (Black)
-  Linting sa flake8
-  Proverava da li aplikacija može da se pokrene

**Trigeri:**
- Push na `main`, `master`, ili `develop` branch
- Pull request na `main`, `master`, ili `develop` branch

**Status badge:**
```markdown
![Tests](https://github.com/yourusername/ToDoBackend/actions/workflows/test-and-build.yml/badge.svg)
```

---

### 2. **Deploy to Production** (`deploy.yml`)

Automatski deployment nakon uspešnih testova.

**Šta radi:**
-  Deployment na production server (potrebna konfiguracija)
- Notifikacije o deployment-u

**Trigeri:**
- Push na `main` ili `master` branch
- Git tags (`v*`)

**Napomena:** Deployment je trenutno onemogućen - potrebno je konfigurisati SSH pristup.

---

##  Konfiguracija

### Secrets (GitHub Repository Settings → Secrets)

Za deployment, dodaj sledeće secrets varijable:

```
DEPLOY_HOST      # Hostname servera
DEPLOY_USER      # SSH username
DEPLOY_KEY       # SSH private key
```

### Environment Variables

CI koristi sledeće env variables:

```env
SQLALCHEMY_DATABASE_URL=mysql+pymysql://root:testpassword@127.0.0.1:3306/test_default_db
SQLALCHEMY_TEST_DATABASE_URL=mysql+pymysql://root:testpassword@127.0.0.1:3306/test_default_db
SECRET_KEY=test-secret-key-for-github-actions
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

---

##  Debugging Failed Workflows

### 1. Pregled logova

```
GitHub → Actions → Failed workflow → Click on failed job
```

### 2. Česte greške

####  MySQL connection timeout
**Uzrok:** MySQL servis nije spreman.

**Rešenje:** Workflow već ima `Wait for MySQL` step.

####  Test failures
**Uzrok:** Testovi padaju u CI okruženju.

**Rešenje:**
```bash
# Lokalno testiraj sa istim env variablama kao CI
export SQLALCHEMY_TEST_DATABASE_URL="mysql+pymysql://root:password@localhost:3306/test_default_db"
pytest tests/ -v
```

####  Missing dependencies
**Uzrok:** `requirements.txt` nije ažuriran.

**Rešenje:**
```bash
pip freeze > requirements.txt
git add requirements.txt
git commit -m "Update dependencies"
```

---

##  Lokalno Testiranje CI

### 1. Instalacija Act (GitHub Actions lokalno)

```bash
# macOS
brew install act

# Windows
choco install act-cli
```

### 2. Pokretanje workflow-a lokalno

```bash
# Test workflow
act push -j test

# Build workflow
act push -j build

# Svi jobs
act push
```

---

## Deployment Options

### Option 1: SSH Deployment (trenutno disabled)

Uncomment deployment step u `deploy.yml` i konfiguriši secrets.

### Option 2: Docker Deployment

```yaml
- name: Build Docker image
  run: docker build -t todobackend:latest .

- name: Push to registry
  run: docker push yourusername/todobackend:latest
```

### Option 3: Platform as a Service

- **Heroku:** `heroku git:remote -a your-app`
- **Railway:** GitHub integration
- **Render:** Auto-deploy from GitHub
- **Fly.io:** `fly deploy`

---

##  Coverage Reports

Coverage reports se automatski upload-uju na Codecov (ako je konfigurisan).

**Setup:**
1. Kreiraj account na [codecov.io](https://codecov.io)
2. Povezati GitHub repo
3. Badge će automatski raditi


