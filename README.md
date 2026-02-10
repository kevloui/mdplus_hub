# MDplus Hub

A containerized web application for molecular dynamics backmapping using the GLIMPS machine learning approach from the mdplus package.

## Features

- **GLIMPS Backmapping**: Transform coarse-grained molecular structures to atomistic resolution
- **3D Molecular Visualization**: Interactive viewer powered by Mol*
- **Project Management**: Organize molecules and models in projects
- **Background Processing**: ARQ-based job queue for training and inference
- **Real-time Updates**: WebSocket-based job progress tracking
- **Collaboration**: Share projects with team members

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Next.js 14, TypeScript, Tailwind CSS, shadcn/ui, Mol* |
| Backend | FastAPI, Python 3.12, SQLAlchemy, Alembic |
| Database | PostgreSQL 16 |
| Queue | Redis 7, ARQ |
| Auth | NextAuth.js (Email + Google + GitHub OAuth) |
| Container | Docker, docker-compose |

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Git

### Development Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/mdplus_hub.git
cd mdplus_hub
```

2. Copy environment file:
```bash
cp .env.example .env
```

3. Start the development environment:
```bash
make dev
```

Or without make:
```bash
docker-compose up --build
```

4. Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/api/docs

### Running Migrations

```bash
make migrate
```

### Running Tests

```bash
make test
```

## Project Structure

```
mdplus_hub/
├── backend/                 # FastAPI backend
│   ├── src/
│   │   ├── api/            # API endpoints
│   │   ├── core/           # Security, exceptions
│   │   ├── domain/         # Entities, services
│   │   ├── glimps/         # GLIMPS adapter, parsers
│   │   ├── infrastructure/ # Database, storage
│   │   └── workers/        # ARQ background tasks
│   ├── tests/
│   └── alembic/            # Database migrations
├── frontend/               # Next.js frontend
│   └── src/
│       ├── app/           # App router pages
│       ├── components/    # UI components
│       ├── lib/           # Utilities, API client
│       └── stores/        # Zustand state
├── docker/                # Dockerfiles
└── docker-compose.yml     # Development orchestration
```

## API Overview

| Endpoint | Description |
|----------|-------------|
| `POST /api/v1/auth/register` | User registration |
| `POST /api/v1/auth/login` | Email login |
| `GET /api/v1/projects` | List projects |
| `POST /api/v1/projects` | Create project |
| `POST /api/v1/models/{id}/train` | Start training job |
| `POST /api/v1/models/{id}/inference` | Run inference |
| `GET /api/v1/jobs` | List jobs |
| `WS /ws/jobs/{id}` | Job progress stream |

## Environment Variables

See `.env.example` for all available configuration options.

Key variables:
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `SECRET_KEY`: JWT signing key
- `NEXTAUTH_SECRET`: NextAuth.js secret
- `GOOGLE_CLIENT_ID/SECRET`: Google OAuth credentials
- `GITHUB_CLIENT_ID/SECRET`: GitHub OAuth credentials

## License

MIT
