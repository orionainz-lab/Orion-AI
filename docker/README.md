# Docker Directory

**Purpose**: Container orchestration and configuration

## Structure

Docker and Docker Compose configurations:

```
docker/
├── docker-compose.yml      # Main orchestration file
├── temporal/              # Temporal server configuration
├── postgresql/            # Supabase PostgreSQL config
└── workers/              # Worker service configs
```

## Services

- **Temporal Server**: Workflow execution engine
- **PostgreSQL**: Database with pgvector extension
- **Temporal Workers**: Workflow/activity workers
- **API Server**: FastAPI backend

## Usage

```bash
# Start all services
docker-compose -f docker/docker-compose.yml up -d

# View logs
docker-compose -f docker/docker-compose.yml logs -f

# Stop services
docker-compose -f docker/docker-compose.yml down
```

## Coding Standards

- Multi-stage builds for smaller images
- Health checks for all services
- No secrets in images (use environment variables)
- Docker Compose for local development

---

**Phase**: 1 - Infrastructure  
**Status**: Awaiting Docker configuration
