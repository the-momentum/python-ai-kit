# API

A FastAPI application with PostgreSQL database support, containerized with Docker.

## Prerequisites

- Docker and Docker Compose
- [just](https://github.com/casey/just) command runner (e.g. `uv tool install rust-just`)
- Python 3.12+ (for local development)

## Setup

1. **Create environment file**
   ```bash
   cp ./config/.env.example ./config/.env
   # Edit .env file with your configuration
   ```

## Running the Application

### Docker (Recommended)

```bash
# Start services
just run

# Create migration
docker compose exec app uv run alembic revision --autogenerate -m "Description"

# Run migrations
docker compose exec app uv run alembic upgrade head
```

Run `just` without arguments to see all available commands (build, up, stop, down, test, migrations).

### Local Development

```bash
# Install dependencies
uv sync

# Start PostgreSQL locally

# Create migration
just create-migration "Description"

# Run migrations
just migrate

# Start development server
uv run fastapi run app/main.py --reload
```

### Access the application
- API: http://localhost:8000
- Swagger: http://localhost:8000/docs

---

This project was generated from the [Python AI Kit](https://github.com/the-momentum/python-ai-kit).
