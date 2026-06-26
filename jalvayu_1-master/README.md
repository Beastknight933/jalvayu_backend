# Climate Digital Twin Backend

An enterprise-grade, FastAPI-powered backend for India's National Climate Digital Twin.

This platform ingests raw climate data (NetCDF, GeoTIFF), processes it using Celery workers, models it via a custom Machine Learning engine, and simulates Digital Twin states in real-time, delivering the results to a separate frontend via secure REST and WebSocket APIs.

## Architecture Highlights
- **Framework:** FastAPI (Python 3.11)
- **Database:** PostgreSQL (with PostGIS for spatial data)
- **Caching & Broker:** Redis
- **Task Queue:** Celery
- **Security:** JWT Authentication, slowapi Rate Limiting, Nginx Reverse Proxy
- **Observability:** Prometheus metrics (`/metrics` on internal port `9090`)

## Local Development (Docker)

1. Clone the repository.
2. Build and start the development environment:
   ```bash
   docker-compose up --build
   ```
3. The API will be available at `http://localhost:8000`. 
4. API Documentation (Swagger) is available at `http://localhost:8000/api/v1/docs`.

## Production Deployment (Vercel + Render + Supabase)

This repository is configured for Continuous Deployment via GitHub Actions (`.github/workflows/cd.yml`).

### Requirements:
1. **Supabase:** Provision a PostgreSQL instance. Set `SUPABASE_DB_*` secrets in GitHub.
2. **Render:** Connect the repository to a Render Web Service. The `Dockerfile.prod` will be used to build the image. Set `RENDER_DEPLOY_HOOK` in GitHub.
3. **Vercel:** Connect the separate frontend repository to Vercel. Set `VERCEL_DEPLOY_HOOK` in GitHub to ensure the frontend redeploys when the backend API changes.

### Environment Variables
Configure the following in your Render environment dashboard:
- `ENVIRONMENT=production`
- `POSTGRES_SERVER` (Supabase DB Host)
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_DB`
- `REDIS_URL`
- `PRIVATE_KEY` / `PUBLIC_KEY` (RS256 keys for JWT)

## Testing
Tests are written with `pytest` using async clients and an in-memory SQLite database (`aiosqlite`) by default.
Run tests locally via:
```bash
pytest -v
```

## Maintenance & Backups
A bash utility is provided for automated daily backups of the PostgreSQL database and processed climate assets.
Schedule `scripts/backup.sh` via a cronjob on your production persistent storage volume.
