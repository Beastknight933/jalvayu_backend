<div align="center">

# 🌏 Jalvayu — Climate Digital Twin Backend

**Enterprise-grade backend for India's National Climate Digital Twin Platform**

This platform ingests raw climate data (NetCDF, GeoTIFF), processes it using Celery workers, models it via a custom Machine Learning engine, and simulates Digital Twin states in real-time, delivering the results to a separate frontend via secure REST and WebSocket APIs.

## Architecture Highlights

- **Framework:** FastAPI (Python 3.11)
- **Database:** PostgreSQL (with PostGIS for spatial data)
- **Caching & Broker:** Redis
- **Task Queue:** Celery
- **Security:** JWT Authentication, slowapi Rate Limiting, Nginx Reverse Proxy
- **Observability:** Prometheus metrics (`/metrics` on internal port `9090`)

[![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15_(PostGIS)-336791?logo=postgresql&logoColor=white)](https://www.postgresql.org)
[![Redis](https://img.shields.io/badge/Redis-7-DC382D?logo=redis&logoColor=white)](https://redis.io)
[![Celery](https://img.shields.io/badge/Celery-5.4-37814A?logo=celery&logoColor=white)](https://docs.celeryq.dev)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

*Ingest raw climate data (NetCDF, GeoTIFF) → Process with async pipelines → Model with ML → Simulate Digital Twin states → Serve via REST & WebSocket APIs*

</div>

---

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Getting Started](#getting-started)
  - [1. Clone the Repository](#1-clone-the-repository)
  - [2. Environment Configuration](#2-environment-configuration)
  - [3. Start with Docker (Recommended)](#3-start-with-docker-recommended)
  - [4. Start without Docker (Manual)](#4-start-without-docker-manual)
- [Accessing the Application](#accessing-the-application)
- [API Documentation](#api-documentation)
- [API Endpoints Reference](#api-endpoints-reference)
- [Database Management](#database-management)
- [Background Workers (Celery)](#background-workers-celery)
- [Running Tests](#running-tests)
- [Code Quality & Linting](#code-quality--linting)
- [Production Deployment](#production-deployment)
  - [Render + Supabase](#render--supabase)
  - [Docker Compose Production](#docker-compose-production)
- [Environment Variables Reference](#environment-variables-reference)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

---

## Architecture Overview

```
                                    ┌──────────────────────────────────┐
                                    │          Frontend (Next.js)      │
                                    └──────────┬──────────┬────────────┘
                                               │ REST     │ WebSocket
                                    ┌──────────▼──────────▼────────────┐
                                    │   Nginx Reverse Proxy (Prod)     │
                                    └──────────┬───────────────────────┘
                                               │
                                    ┌──────────▼───────────────────────┐
                                    │     FastAPI Application          │
                                    │  ┌─────────────────────────┐     │
                                    │  │  API Layer (Controllers) │     │
                                    │  ├─────────────────────────┤     │
                                    │  │  Service Layer (Logic)   │     │
                                    │  ├─────────────────────────┤     │
                                    │  │  Repository Layer (Data) │     │
                                    │  └─────────────────────────┘     │
                                    └──┬──────────┬──────────┬─────────┘
                                       │          │          │
                          ┌────────────▼─┐  ┌─────▼────┐  ┌─▼──────────┐
                          │  PostgreSQL   │  │  Redis   │  │  Celery    │
                          │  (PostGIS)    │  │  Cache   │  │  Workers   │
                          │  Supabase     │  │  Broker  │  │            │
                          └──────────────┘  └──────────┘  └────────────┘
                                                             │
                                              ┌──────────────▼────────────┐
                                              │   Background Pipelines    │
                                              │  • Data Ingestion (IMD)   │
                                              │  • ML Training            │
                                              │  • Simulation Execution   │
                                              └───────────────────────────┘
```

---

## Tech Stack

| Component | Technology | Purpose |
|---|---|---|
| **Framework** | FastAPI 0.111 | Async REST API + WebSocket server |
| **Language** | Python 3.12 | Runtime |
| **Database** | PostgreSQL 15 + PostGIS 3.3 | Relational data + geospatial queries |
| **Managed DB** | Supabase | Cloud PostgreSQL provider |
| **ORM** | SQLAlchemy 2.0 (async) + asyncpg | Async database access |
| **Migrations** | Alembic | Database schema versioning |
| **Caching** | Redis 7 | Response caching + Digital Twin state |
| **Task Queue** | Celery 5.4 + Redis broker | Background data ingestion & ML training |
| **Auth** | JWT (RS256) via python-jose | Stateless authentication |
| **Geospatial** | GeoAlchemy2 + PostGIS | Spatial data types and queries |
| **ML** | TensorFlow 2.16 + XGBoost | Climate prediction models |
| **Observability** | Loguru + Prometheus | Structured logging + metrics |
| **Containerization** | Docker + Docker Compose | Development & production environments |
| **Reverse Proxy** | Nginx | Production load balancing + security headers |
| **CI/CD** | GitHub Actions | Automated testing and deployment |

---

## Project Structure

```
jalvayu_backend/
├── app/                              # Application source code
│   ├── main.py                       # FastAPI application factory
│   ├── api/                          # API layer
│   │   ├── core/                     # Standardized response schemas
│   │   │   └── responses.py          # APIResponse, APIPaginatedResponse
│   │   ├── dependencies.py           # Dependency injection (DB session, auth)
│   │   ├── middlewares/              # Request pipeline
│   │   │   ├── logging.py            # Request/response logging
│   │   │   ├── rate_limit.py         # slowapi rate limiter
│   │   │   └── request_id.py         # X-Request-ID correlation
│   │   ├── v1/                       # Versioned API routes
│   │   │   ├── auth/router.py        # POST /register, /login, GET /me
│   │   │   ├── climate/router.py     # CRUD for climate datasets
│   │   │   ├── processing/router.py  # Data ingestion pipeline triggers
│   │   │   ├── ml/router.py          # ML model registry & training
│   │   │   ├── twin/router.py        # Digital Twin state & simulation
│   │   │   ├── health/router.py      # System health checks
│   │   │   └── metrics/router.py     # System metrics (CPU, memory)
│   │   └── websockets/               # Real-time dashboard feeds
│   │       ├── router.py             # WebSocket endpoint
│   │       └── manager.py            # Connection manager
│   ├── core/                         # Application configuration
│   │   ├── config.py                 # Pydantic Settings (loads .env)
│   │   ├── security.py               # JWT token create/verify, password hashing
│   │   ├── exceptions.py             # Custom exception hierarchy
│   │   ├── handlers.py               # Global exception handlers
│   │   ├── logging.py                # Loguru centralized logging
│   │   └── metrics.py                # Prometheus counters & histograms
│   ├── models/                       # SQLAlchemy ORM models
│   │   ├── user.py                   # User, UserRole
│   │   ├── climate.py                # ClimateDataset, DatasetVersion, ClimateMetadata
│   │   ├── observation.py            # ObservationMetadata
│   │   ├── processing.py             # ProcessingJob, ValidationReport, ImportHistory
│   │   ├── ml.py                     # ModelRegistry, TrainingRun, EvaluationReport
│   │   └── twin.py                   # SimulationRun, SimulationSnapshot, ForecastHistory
│   ├── schemas/                      # Pydantic request/response DTOs
│   ├── repositories/                 # Database access layer (generic CRUD)
│   ├── services/                     # Business logic layer
│   ├── db/                           # Database infrastructure
│   │   ├── base.py                   # DeclarativeBase with UUID PKs, timestamps
│   │   └── session.py                # Async engine & session factory
│   ├── digital_twin/                 # Digital Twin engine
│   │   ├── engine.py                 # Unified facade (state, forecast, simulate, replay)
│   │   ├── cache/service.py          # Redis caching for Twin states
│   │   ├── forecasting/service.py    # ML-backed operational forecasts
│   │   ├── simulation/scenario.py    # What-if scenario engine
│   │   └── replay/service.py         # Historical state playback
│   ├── ml/                           # Machine Learning subsystem
│   │   ├── models/base.py            # Abstract ClimateModel interface
│   │   ├── models/xgboost_impl.py    # XGBoost implementation
│   │   ├── registry/manager.py       # Model lifecycle management
│   │   └── pipelines/core.py         # Training pipeline orchestration
│   ├── data/                         # Data ingestion & storage
│   │   ├── storage.py                # Storage abstraction (local disk / S3)
│   │   ├── downloaders/              # Source-specific data fetchers
│   │   ├── parsers/                  # NetCDF/GeoTIFF parsers
│   │   ├── validators/               # Data integrity validation
│   │   └── pipelines/orchestrator.py # Ingestion pipeline orchestrator
│   └── workers/                      # Celery background tasks
│       ├── celery_app.py             # Celery application config
│       └── tasks/                    # Task definitions
│           ├── data_ingestion.py     # Climate data ingestion task
│           └── ml_tasks.py           # ML model training task
├── alembic/                          # Database migrations
│   ├── env.py                        # Alembic async configuration
│   └── versions/                     # Migration scripts
├── tests/                            # Test suite
│   ├── conftest.py                   # Fixtures (async client, test DB)
│   └── api/                          # API endpoint tests
├── scripts/                          # Utility scripts
│   └── backup.sh                     # PostgreSQL & asset backup utility
├── nginx/                            # Reverse proxy config
│   └── nginx.conf                    # Nginx config (security headers, WebSocket, gzip)
├── .github/workflows/                # CI/CD pipelines
│   ├── ci.yml                        # Lint + test on PR
│   └── cd.yml                        # Deploy on merge to main
├── .env                              # Environment variables (gitignored)
├── .env.example                      # Template for .env
├── Dockerfile                        # Development container
├── Dockerfile.prod                   # Multi-stage production container
├── docker-compose.yml                # Development stack (API + DB + Redis + Celery)
├── docker-compose.prod.yml           # Production stack (+ Nginx + Prometheus)
├── requirements.txt                  # Python production dependencies
├── requirements-dev.txt              # Python development dependencies
├── alembic.ini                       # Alembic configuration
└── pytest.ini                        # Pytest configuration
```

---

## Prerequisites

### For Docker Setup (Recommended)

| Tool | Version | Installation |
|---|---|---|
| **Docker** | ≥ 24.0 | [docs.docker.com/get-docker](https://docs.docker.com/get-docker/) |
| **Docker Compose** | ≥ 2.20 | Included with Docker Desktop |
| **Git** | ≥ 2.40 | [git-scm.com](https://git-scm.com/) |

### For Manual Setup (Without Docker)

| Tool | Version | Installation |
|---|---|---|
| **Python** | 3.12.x | [python.org/downloads](https://www.python.org/downloads/) |
| **PostgreSQL** | ≥ 15 with PostGIS | [postgresql.org](https://www.postgresql.org/download/) + [postgis.net](https://postgis.net/install/) |
| **Redis** | ≥ 7.0 | [redis.io/download](https://redis.io/download) |
| **GDAL** | ≥ 3.6 | `apt install gdal-bin libgdal-dev` (Linux) or via conda |
| **Git** | ≥ 2.40 | [git-scm.com](https://git-scm.com/) |

---

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/Beastknight933/jalvayu_backend.git
cd jalvayu_backend
```

### 2. Environment Configuration

The project uses a `.env` file for all configuration. A ready-to-use `.env` file with development defaults is already included.

**Quick verification:**

```bash
# Check that .env exists
ls .env

# If .env is missing, create it from the template:
cp .env.example .env
```

**The `.env` file contains:**

- Database connection settings (defaults to Docker Compose service names)
- Redis connection settings
- JWT authentication keys (development dummy keys included)
- Celery broker configuration
- External API keys (placeholder values)
- Data storage paths

> ⚠️ **Important:** The included `.env` uses development-only JWT keys. For production, generate proper RS256 keys:
>
> ```bash
> # Generate a 2048-bit RSA private key
> openssl genrsa -out private_key.pem 2048
>
> # Extract the public key
> openssl rsa -in private_key.pem -outform PEM -pubout -out public_key.pem
>
> # Then copy the contents into .env, replacing newlines with \n:
> # PRIVATE_KEY="-----BEGIN RSA PRIVATE KEY-----\nMIIEpAIB...\n-----END RSA PRIVATE KEY-----"
> # PUBLIC_KEY="-----BEGIN PUBLIC KEY-----\nMIIBIjAN...\n-----END PUBLIC KEY-----"
> ```

### 3. Start with Docker (Recommended)

This is the simplest way to get the entire stack running. Docker Compose will start:

- **API server** (FastAPI on port 8000)
- **PostgreSQL 15 + PostGIS** (on port 5432)
- **Redis 7** (on port 6379)
- **Celery Worker** (background task processing)

```bash
# Build and start all services
docker-compose up --build
```

**What happens on first boot:**

1. Docker builds the API image (installs Python 3.12, system libs for GDAL/PostGIS, pip dependencies)
2. PostgreSQL starts with a `climatedb` database and PostGIS extensions
3. Redis starts as the caching layer and Celery broker
4. The FastAPI server starts on `http://localhost:8000` with hot-reload enabled
5. A Celery worker connects to Redis and begins listening for background tasks

**First-time database setup (run once after the containers are up):**

```bash
# Run Alembic migrations to create all database tables
docker-compose exec api alembic upgrade head
```

**Useful Docker Compose commands:**

```bash
# Start in detached mode (background)
docker-compose up -d --build

# View logs for all services
docker-compose logs -f

# View logs for a specific service
docker-compose logs -f api
docker-compose logs -f celery_worker
docker-compose logs -f db

# Stop all services
docker-compose down

# Stop and remove all data (fresh start)
docker-compose down -v

# Restart only the API (after code changes, though hot-reload handles most cases)
docker-compose restart api

# Open a shell inside the API container
docker-compose exec api bash

# Open a PostgreSQL shell
docker-compose exec db psql -U postgres -d climatedb

# Open a Redis CLI
docker-compose exec redis redis-cli
```

### 4. Start without Docker (Manual)

If you prefer to run services natively:

#### Step 4a: Set Up Python Environment

```bash
# Create a virtual environment
python -m venv venv

# Activate it
# On Linux/macOS:
source venv/bin/activate
# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# On Windows (CMD):
venv\Scripts\activate.bat

# Install production dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt
```

#### Step 4b: Set Up PostgreSQL

```bash
# Start PostgreSQL (method varies by OS)
# On macOS (Homebrew):
brew services start postgresql@15

# On Ubuntu:
sudo systemctl start postgresql

# Create the database
psql -U postgres -c "CREATE DATABASE climatedb;"

# Enable PostGIS extension
psql -U postgres -d climatedb -c "CREATE EXTENSION IF NOT EXISTS postgis;"
```

#### Step 4c: Update `.env` for Local Services

Edit `.env` and change the host values from Docker service names to `localhost`:

```env
# Change these from Docker service names to localhost:
POSTGRES_SERVER=localhost
REDIS_HOST=localhost
CELERY_BROKER_URL="redis://localhost:6379/0"
CELERY_RESULT_BACKEND="redis://localhost:6379/0"
```

#### Step 4d: Set Up Redis

```bash
# On macOS (Homebrew):
brew services start redis

# On Ubuntu:
sudo systemctl start redis-server

# Verify Redis is running
redis-cli ping
# Should return: PONG
```

#### Step 4e: Run Database Migrations

```bash
# Apply all migrations to create tables
alembic upgrade head

# Check current migration state
alembic current
```

#### Step 4f: Start the API Server

```bash
# Development mode with hot-reload
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Or with specific log level
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --log-level debug
```

#### Step 4g: Start the Celery Worker (separate terminal)

```bash
# Activate the virtual environment in the new terminal first, then:
celery -A app.workers.celery_app worker --loglevel=info

# With auto-reload for development (requires watchdog):
pip install watchdog
celery -A app.workers.celery_app worker --loglevel=info --autoreload
```

---

## Accessing the Application

Once the server is running, you can access:

| Resource | URL |
|---|---|
| **API Base URL** | `http://localhost:8000` |
| **Interactive API Docs (Swagger UI)** | `http://localhost:8000/docs` |
| **Alternative API Docs (ReDoc)** | `http://localhost:8000/redoc` |
| **OpenAPI JSON Schema** | `http://localhost:8000/api/v1/openapi.json` |
| **Health Check** | `http://localhost:8000/api/v1/health` |
| **WebSocket Endpoint** | `ws://localhost:8000/api/v1/ws/{client_id}` |

---

## API Documentation

The API is fully documented via **Swagger UI** (auto-generated from FastAPI type annotations).

**Quick test flow:**

```bash
# 1. Check health
curl http://localhost:8000/api/v1/health

# 2. Register a user
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "scientist@jalvayu.in",
    "password": "SecureP@ss123",
    "password_confirm": "SecureP@ss123",
    "first_name": "Aarav",
    "last_name": "Sharma"
  }'

# 3. Login to get a JWT token
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=scientist@jalvayu.in&password=SecureP@ss123"

# 4. Use the token for authenticated requests (replace <TOKEN>)
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer <TOKEN>"

# 5. Create a climate dataset (authenticated)
curl -X POST http://localhost:8000/api/v1/climate/ \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "IMD Gridded Rainfall 0.25°",
    "description": "Daily gridded rainfall data from IMD at 0.25x0.25 degree resolution",
    "source": "IMD",
    "source_url": "https://www.imdpune.gov.in/cmpg/Griddata/Rainfall_25_Bin.html"
  }'

# 6. List all climate datasets
curl http://localhost:8000/api/v1/climate/
```

---

## API Endpoints Reference

### Authentication (`/api/v1/auth`)

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/register` | ❌ | Register a new user account |
| `POST` | `/login` | ❌ | OAuth2 login, returns JWT access + refresh tokens |
| `GET` | `/me` | ✅ | Get current authenticated user profile |

### Climate Datasets (`/api/v1/climate`)

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/` | ✅ | Register a new climate dataset |
| `GET` | `/` | ❌ | List all datasets (paginated) |
| `GET` | `/{dataset_id}` | ❌ | Get dataset details by ID |
| `POST` | `/versions` | ✅ | Add a version to a dataset |
| `POST` | `/{dataset_id}/upload` | ✅ | Upload dataset file (NetCDF, GeoTIFF, etc.) |

### Data Processing (`/api/v1/processing`)

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/ingest` | ✅ | Trigger async data ingestion pipeline |
| `GET` | `/jobs/{job_id}` | ❌ | Check ingestion job status |

### Machine Learning (`/api/v1/ml`)

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/models` | ✅ | Register a new ML model |
| `GET` | `/models` | ❌ | List registered models (paginated) |
| `POST` | `/models/{model_id}/train` | ✅ | Trigger async model training |

### Digital Twin (`/api/v1/twin`)

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `GET` | `/state` | ❌ | Get current climate state (Redis-cached) |
| `POST` | `/simulate` | ✅ | Start a what-if scenario simulation |

### System (`/api/v1/health`, `/api/v1/metrics`)

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `GET` | `/health` | ❌ | System health check (DB status) |
| `GET` | `/metrics` | ✅ | System metrics (CPU, memory) |

### WebSocket (`/api/v1/ws`)

| Protocol | Endpoint | Description |
|---|---|---|
| `WS` | `/ws/{client_id}` | Real-time dashboard updates (ping/pong keepalive) |

---

## Database Management

### Alembic Migrations

```bash
# With Docker:
docker-compose exec api alembic upgrade head      # Apply all migrations
docker-compose exec api alembic downgrade -1       # Rollback last migration
docker-compose exec api alembic current            # Show current migration
docker-compose exec api alembic history            # Show migration history

# Auto-generate a new migration after model changes:
docker-compose exec api alembic revision --autogenerate -m "Add new_column to users"

# Without Docker (in activated venv):
alembic upgrade head
alembic downgrade -1
alembic revision --autogenerate -m "Description of changes"
```

### Direct Database Access

```bash
# Via Docker:
docker-compose exec db psql -U postgres -d climatedb

# Useful psql commands:
\dt                    # List all tables
\d+ users              # Describe users table with details
\d+ climate_datasets   # Describe climate_datasets table
SELECT * FROM users;   # Query users
```

### Database Schema

The system uses **16 tables** across 5 domains:

| Domain | Tables |
|---|---|
| **Auth** | `users` |
| **Climate** | `climate_datasets`, `dataset_versions`, `climate_metadata`, `observation_metadata` |
| **Processing** | `processing_jobs`, `validation_reports`, `import_history` |
| **ML** | `model_registry`, `training_runs`, `evaluation_reports`, `prediction_runs`, `prediction_results` |
| **Digital Twin** | `simulation_runs`, `simulation_snapshots`, `forecast_history` |

---

## Background Workers (Celery)

Celery handles long-running tasks asynchronously:

| Task | Trigger | Description |
|---|---|---|
| `ingest_climate_dataset` | `POST /api/v1/processing/ingest` | Download → Validate → Store climate data |
| `train_model_task` | `POST /api/v1/ml/models/{id}/train` | Execute ML training pipeline |

### Monitoring Celery Workers

```bash
# Check worker status
docker-compose exec celery_worker celery -A app.workers.celery_app inspect active

# Check registered tasks
docker-compose exec celery_worker celery -A app.workers.celery_app inspect registered

# Check queue lengths
docker-compose exec redis redis-cli LLEN celery
```

---

## Running Tests

```bash
# With Docker:
docker-compose exec api pytest -v

# Without Docker (in activated venv):
pytest -v

# Run with coverage report
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/api/test_auth.py -v

# Run tests matching a pattern
pytest -k "test_register" -v
```

**Test Configuration** (from `pytest.ini`):

- Async mode: `auto` (no need for `@pytest.mark.asyncio`)
- Coverage: enabled by default (`--cov=app`)
- Test database: in-memory SQLite (`aiosqlite`)

---

## Code Quality & Linting

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Format code with Black
black app/ tests/

# Sort imports with isort
isort app/ tests/

# Lint with Ruff (fast Python linter)
ruff check app/

# Type check with mypy
mypy app/

# Run all pre-commit hooks
pre-commit run --all-files
```

---

## Production Deployment

### Render + Supabase

This is the recommended deployment stack for the Jalvayu platform:

1. **Supabase** — Provision a PostgreSQL database instance
   - Enable the PostGIS extension from the Supabase dashboard
   - Copy the connection pooler string for `SQLALCHEMY_DATABASE_URI`

2. **Render** — Create a Web Service
   - Connect to this GitHub repository
   - Render will auto-detect `Dockerfile.prod` for building
   - Set environment variables in the Render dashboard (see [Environment Variables Reference](#environment-variables-reference))

3. **GitHub Actions** — CI/CD is pre-configured
   - `.github/workflows/ci.yml` — Runs linting + tests on every PR
   - `.github/workflows/cd.yml` — Deploys to Render on merge to `main`

**Required GitHub Secrets:**

```
POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB
RENDER_DEPLOY_HOOK
VERCEL_DEPLOY_HOOK  (for frontend redeployment)
```

### Docker Compose Production

For self-hosted production deployments:

```bash
# Start the production stack (API + Celery + Nginx + Prometheus)
docker-compose -f docker-compose.prod.yml up -d --build
```

**Production stack includes:**

- Multi-stage Dockerfile (`Dockerfile.prod`) — smaller image, non-root user
- Nginx reverse proxy with security headers, gzip, and 500MB upload limit
- Prometheus metrics collector
- 4G memory limit for API, 8G for Celery workers
- Auto-restart on failure

### Generating Production JWT Keys

```bash
# Generate RS256 key pair
openssl genrsa -out private_key.pem 2048
openssl rsa -in private_key.pem -outform PEM -pubout -out public_key.pem

# Convert to single-line for environment variables
awk 'NF {sub(/\r/, ""); printf "%s\\n",$0;}' private_key.pem
awk 'NF {sub(/\r/, ""); printf "%s\\n",$0;}' public_key.pem
```

### Database Backups

A backup utility is included for production:

```bash
# Manual backup
docker-compose exec api bash scripts/backup.sh

# Schedule daily backups via cron (on the host):
# 0 2 * * * cd /path/to/jalvayu_backend && docker-compose exec -T api bash scripts/backup.sh
```

The script:

- Dumps the PostgreSQL database (compressed `.sql.gz`)
- Archives ML models and processed data (`.tar.gz`)
- Maintains a 7-day retention policy

---

## Environment Variables Reference

| Variable | Required | Default | Description |
|---|---|---|---|
| `PROJECT_NAME` | ❌ | `Climate Digital Twin API` | Application name shown in docs |
| `API_V1_STR` | ❌ | `/api/v1` | API version prefix |
| `ENVIRONMENT` | ❌ | `development` | `development`, `testing`, `staging`, `production` |
| **Database** | | | |
| `POSTGRES_SERVER` | ✅ | — | Database host (`db` for Docker, `localhost` for manual) |
| `POSTGRES_USER` | ✅ | — | Database user |
| `POSTGRES_PASSWORD` | ✅ | — | Database password |
| `POSTGRES_DB` | ✅ | — | Database name |
| `POSTGRES_PORT` | ❌ | `5432` | Database port |
| `SQLALCHEMY_DATABASE_URI` | ❌ | Auto-built | Full connection string (overrides individual fields) |
| **Redis** | | | |
| `REDIS_HOST` | ✅ | — | Redis host (`redis` for Docker) |
| `REDIS_PORT` | ❌ | `6379` | Redis port |
| **Authentication** | | | |
| `PRIVATE_KEY` | ✅ | — | RS256 private key (PEM, `\n` escaped) |
| `PUBLIC_KEY` | ✅ | — | RS256 public key (PEM, `\n` escaped) |
| `ALGORITHM` | ❌ | `RS256` | JWT signing algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | ❌ | `30` | Access token TTL |
| `REFRESH_TOKEN_EXPIRE_DAYS` | ❌ | `7` | Refresh token TTL |
| **Celery** | | | |
| `CELERY_BROKER_URL` | ✅ | — | Redis URL for Celery broker |
| `CELERY_RESULT_BACKEND` | ✅ | — | Redis URL for Celery results |
| **External APIs** | | | |
| `IMD_API_URL` | ❌ | — | IMD data endpoint |
| `IMD_API_KEY` | ❌ | — | IMD API key |
| `ISRO_BHUVAN_URL` | ❌ | — | Bhuvan geospatial endpoint |
| `ISRO_API_KEY` | ❌ | — | ISRO/Bhuvan API key |
| **Storage** | | | |
| `DATA_STORAGE_BASE_PATH` | ❌ | `/app/data` | Root path for data storage |
| `STORAGE_BACKEND` | ❌ | `local` | `local` or `s3` |
| `S3_BUCKET_NAME` | ❌ | — | S3 bucket (when `STORAGE_BACKEND=s3`) |
| `AWS_ACCESS_KEY_ID` | ❌ | — | AWS credentials |
| `AWS_SECRET_ACCESS_KEY` | ❌ | — | AWS credentials |

---

## Troubleshooting

### Common Issues

<details>
<summary><strong>❌ Docker: "Port 5432 already in use"</strong></summary>

Another PostgreSQL instance is running on your machine.

```bash
# Option 1: Stop the local PostgreSQL
sudo systemctl stop postgresql    # Linux
brew services stop postgresql@15  # macOS

# Option 2: Change the exposed port in docker-compose.yml
# Change "5432:5432" to "5433:5432"
```

</details>

<details>
<summary><strong>❌ Docker: "Port 6379 already in use"</strong></summary>

Another Redis instance is running.

```bash
# Stop local Redis
sudo systemctl stop redis-server  # Linux
brew services stop redis          # macOS
```

</details>

<details>
<summary><strong>❌ "SQLALCHEMY_DATABASE_URI validation error"</strong></summary>

The `.env` file is missing or has incorrect database credentials.

```bash
# Verify .env exists
ls -la .env

# If missing, create from template
cp .env.example .env
```

</details>

<details>
<summary><strong>❌ Alembic: "Target database is not up to date"</strong></summary>

```bash
# Apply pending migrations
docker-compose exec api alembic upgrade head

# If the database is out of sync, stamp the current state
docker-compose exec api alembic stamp head
```

</details>

<details>
<summary><strong>❌ Celery: "Connection refused" to Redis</strong></summary>

Ensure Redis is running and the `CELERY_BROKER_URL` in `.env` matches your setup.

```bash
# Check if Redis is reachable
docker-compose exec redis redis-cli ping   # Docker
redis-cli ping                             # Manual setup
```

</details>

<details>
<summary><strong>❌ "Module not found" errors when running locally</strong></summary>

Ensure you've activated the virtual environment and installed all dependencies.

```bash
source venv/bin/activate          # or .\venv\Scripts\Activate.ps1 on Windows
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

</details>

<details>
<summary><strong>❌ Windows: GDAL/PostGIS build errors</strong></summary>

GDAL can be difficult to install on Windows. The recommended approach is to use Docker, or install via conda:

```bash
conda install -c conda-forge gdal geopandas rasterio
```

</details>

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Install dev dependencies: `pip install -r requirements-dev.txt`
4. Install pre-commit hooks: `pre-commit install`
5. Make changes and run tests: `pytest -v`
6. Run linting: `ruff check app/ && black --check app/`
7. Commit with conventional commits: `git commit -m "feat: add new endpoint"`
8. Push and open a Pull Request

---

<div align="center">

**Built for India's climate resilience 🇮🇳**

*Jalvayu — जलवायु — Climate*

</div>
