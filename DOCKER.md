# Docker Setup

## Pokretanje sa Docker Compose

### Preduslov
- Instaliran Docker i Docker Compose

### Koraci

1. Kopiraj `.env.example` u `.env` i podesi environment varijable:
```bash
cp .env.example .env
```

2. Pokreni kontejnere:
```bash
docker-compose up -d
```

3. Proveri status:
```bash
docker-compose ps
```

4. API je dostupan na `http://localhost:8000`

### Korisne komande

Zaustavi kontejnere:
```bash
docker-compose down
```

Zaustavi i obriši volumes (briše bazu podataka):
```bash
docker-compose down -v
```

Pregledaj logove:
```bash
docker-compose logs -f app
docker-compose logs -f db
```

Uđi u kontejner:
```bash
docker-compose exec app bash
docker-compose exec db mysql -u root -p
```

Restartuj aplikaciju:
```bash
docker-compose restart app
```

Build bez cache:
```bash
docker-compose build --no-cache
```

## Pokretanje samo Backend-a (bez MySQL-a)

Ako vec imas MySQL instancu koja radi:

```bash
docker build -t todo-backend .
docker run -p 8000:8000 --env-file .env todo-backend
```

## Development Mode

Za development sa automatskim reload-om, izmeni `docker-compose.yml` CMD liniju:
```yaml
command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Production

Za produkciju, ukloni `volumes` mapiranje iz `docker-compose.yml` i postavi:
```yaml
command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```
