# MovieReview Application - FastAPI + PostgreSQL Database

A movie review application built with **FastAPI** and a **PostgreSQL** backend.  
This project demonstrates **clean architecture**, **SQLAlchemy ORM**, **Alembic migrations**, and **dependency injection**.

## 🚀 Features

### Movie Management
- **List Movies**: Paginated listing with filters (title, release year, genre)
- **Get Movie Details**: Retrieve single movie with full details
- **Create Movies**: Add new movies
- **Update Movies**: Edit movie details
- **Delete Movies**: Remove movies
- **Rating Movies**: Rating a movie with a score

## 🏗️ Architecture

The application follows a clean architecture pattern with clear separation of concerns:

```
MovieReview/
├── alembic/ # Database migrations
│ ├── versions/ # Migration scripts
│ └── env.py # Alembic environment config
├── app/
│ ├── controllers/ # API endpoints
│ │ └── movies.py
│ ├── services/ # Business logic
│ │ └── movie_service.py
│ ├── repositories/ # Data access layer
│ │ └── movie_repo.py
│ ├── models/ # SQLAlchemy models
│ │ ├── movie.py
│ │ ├── genre.py
│ │ ├── director.py
│ │ └── rating.py
│ ├── schemas/ # Pydantic request/response schemas
│ │ └── movie.py
│ ├── db/ # Database configuration
│ │ ├── session.py
│ │ └── base.py
│ └── exceptions/ # NotFound & validation errors
│ │ └── errors.py
├── Dockerfile # Docker configuration
├── docker-compose.yml # Docker Compose configuration
├── alembic.ini # Alembic configuration
├── pyproject.toml # Poetry project file
├── poetry.lock # Dependency lock file
└── .env.example # Environment variables template                      # Environment variables (not in git)
```

### Design Patterns

- **Repository Pattern**: Abstracts data access with interfaces and SQL implementations using SqlAlchemy
- **Service Layer**: Encapsulates business logic and validation
- **Dependency Injection**: Services receive dependencies through constructor injection
- **ORM Mapping**: SQLAlchemy for type-safe queries
- **Migration Management**: Alembic for versioned database schema changes
- **Docker**: All dependencies are put within a docker container to make the app portable

## 📋 Requirements

- Docker

### Dependencies - All will be handled by docker
- python-dotenv (environment configuration)
- sqlalchemy (ORM)
- psycopg2 (PostgreSQL driver)
- alembic (database migrations)
- fastapi using uvicorn
- pydantic (making schemas and their validation standard)
  
## 🛠️ Installation & Setup

### Using docker

### 1. Clone the repository
  ```bash
  git clone https://github.com/SinaEhsanzadeh/MovieReview.git
  cd MovieReview
  ```

2. **Create `.env` file in project root**
   See .env.example file.

3. **Configure Environment variables within `docker-compose.yml` file for db service
  - `POSTGRES_USER`
  - `POSTGRES_PASSWORD`
  - `POSTGRES_DB`
  - `ports`
  - `DATABASE_URL`

5. **Start the application** (migrations apply automatically on startup)
   ```bash
   docker compose up --build -d
   ```

6. **Seed initial data into db**
   ```bash
   docker-compose exec db psql -U <username> -d <database name> -f /scripts/seeddb.sql
   ```

7. **Check logs of routers**
   ```bash
   docker-compose logs -f app
   ```
This command streams the application logs in real time, allowing you to monitor router activity and see logs generated after each request.

✅ The application is now ready. You can access all routes via Swagger.

### Database Migrations
Migrations are applied automatically when the app starts. To manually manage migrations:

```bash
#Go within container to use alembic commands
docker compose exec app sh

# Create a new migration after model changes
alembic revision --autogenerate -m "Description of changes"

# Apply all pending migrations
alembic upgrade head

# View migration history
alembic history

# Rollback to previous migration
alembic downgrade -1

#Exit container
exit
```

## 🎮 Usage
### REST API (FastAPI)
Run:
```bash
docker compose up
```
Explore:
- Docs (Swagger): `http://localhost:8000/docs`
- Docs (ReDoc): `http://localhost:8000/redoc`
- Health check: `http://localhost:8000/health`

## ⚙️ Configuration

### Environment Variables
Located in `.env` file (template is like `.env.example`):
- `DATABASE_URL`
Located in `docker-compose.yml` file
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_DB`
- `ports`
- `DATABASE_URL`
  
## 🔧 Development

### Project Structure
- **Controllers**: FastAPI endpoints
- **Service Layer**: Implements business logic and validation
- **Repository Layer**: Abstracts data access with SQL implementation
- **models**: SQLAlchemy ORM models
- **schemas**: Pydantic validation for request/response
- 

## 📝 License
This project is part of a Software Engineering course and is intended for educational purposes.

## 📊 Version History

- **v0.3.0**: phase 3 - Dockerized the application for portabilit
- **v0.2.0**: Phase 2 - Added logging to application routers
- **v0.1.0**: Initial FastAPI + PostgreSQL setup with movies, genres, and CRUD functionality.
