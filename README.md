# MDplus Hub

A containerized web application for molecular dynamics backmapping using the GLIMPS machine learning approach from the mdplus package.

![Molecule Viewer](docs/images/molecule-viewer.png)

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

## Tutorial: GLIMPS Backmapping Workflow

This tutorial demonstrates the complete GLIMPS backmapping workflow using the provided example files:
- **Atomistic structure**: `backend/tests/examples/b2ar_prepared.pdb` (Beta-2 adrenergic receptor)
- **Coarse-grained structure**: `backend/tests/examples/cg_output/b2ar_cg.pdb`

### Step 1: Start the Application

```bash
docker compose up --build
```

Wait for all services to be ready, then open http://localhost:3000

### Step 2: Create an Account

1. Click **Register** on the login page
2. Enter your email, name, and password
3. Click **Create Account**
4. You'll be redirected to the dashboard

### Step 3: Create a New Project

1. From the Dashboard, click **New Project**
2. Enter a project name (e.g., "B2AR Backmapping Demo")
3. Optionally add a description
4. Click **Create Project**
5. Click on your new project to open it

### Step 4: Upload Molecules

You need to upload both the atomistic (all-atom) and coarse-grained structures.

#### Upload the Atomistic Structure:
1. In the **Molecules** tab, click **Upload Molecule**
2. Click the upload area or drag and drop `backend/tests/examples/b2ar_prepared.pdb`
3. Set **Molecule Type** to **Atomistic**
4. Enter a name (e.g., "B2AR Atomistic")
5. Click **Upload**

#### Upload the Coarse-Grained Structure:
1. Click **Upload Molecule** again
2. Upload `backend/tests/examples/cg_output/b2ar_cg.pdb`
3. Set **Molecule Type** to **Coarse-Grained**
4. Enter a name (e.g., "B2AR CG")
5. Click **Upload**

Both molecules should now appear in the list. You can click **View** to visualize them in the 3D viewer.

### Step 5: Create a GLIMPS Model

1. Switch to the **Models** tab
2. Click **New Model**
3. Enter a model name (e.g., "B2AR GLIMPS Model")
4. Optionally add a description
5. Click **Create Model**

The model will appear as "Untrained" in the list.

### Step 6: Train the Model

1. Click the **Train** button next to your untrained model
2. In the training dialog:
   - Select **B2AR CG** as the Coarse-Grained Molecule
   - Select **B2AR Atomistic** as the Atomistic Molecule
3. Configure GLIMPS options (optional):
   - **PCA**: Enable for dimensionality reduction
   - **Refine**: Enable to improve output geometry with elastic network minimization
   - **Shave**: Enable for terminal atom position calculation
   - **Triangulate**: Alternative to MLR step (disables PCA and Shave)
4. Click **Start Training**

The training job will be queued. Switch to the **Jobs** tab to monitor progress.

### Step 7: Monitor Training Progress

1. Go to the **Jobs** tab
2. You'll see your training job with its status:
   - **Pending** → **Running** → **Completed**
3. Once completed, the model status changes to "Trained"

### Step 8: Run Inference (Backmapping)

Now you can use your trained model to backmap a coarse-grained structure:

1. Go back to the **Models** tab
2. Click the **Inference** button next to your trained model
3. Select the **Coarse-Grained molecule** you want to backmap (e.g., "B2AR CG")
4. Click **Run Inference**

### Step 9: View the Backmapped Result

1. Go to the **Jobs** tab to monitor the inference job
2. Once completed, a new backmapped molecule is automatically created
3. Go to the **Molecules** tab
4. Find the new molecule with type **Backmapped**
5. Click **View** to visualize the backmapped atomistic structure

### Step 10: Compare Structures

Use the 3D viewer to compare:
- Original atomistic structure (B2AR Atomistic)
- Coarse-grained representation (B2AR CG)
- Backmapped result (automatically generated)

### Summary

| Step | Action | Result |
|------|--------|--------|
| 1 | Upload atomistic PDB | Reference structure for training |
| 2 | Upload coarse-grained PDB | Input for training & inference |
| 3 | Create model | Empty GLIMPS model |
| 4 | Train model | Model learns CG→atomistic mapping |
| 5 | Run inference | Backmap CG to atomistic resolution |
| 6 | View result | Compare original vs backmapped |

### Tips

- **Training time** depends on molecule size; B2AR takes ~30-60 seconds
- **Multiple frames**: Upload trajectory files for better model training
- **Export**: Download backmapped structures for further MD simulations
- **Job history**: All jobs are saved and can be reviewed in the Jobs page

## References

- Louison, K., et al. (2021). "GLIMPS: A Machine Learning Approach to Resolution Transformation for Multiscale Modeling." *Journal of Chemical Theory and Computation*. https://doi.org/10.1021/acs.jctc.1c00735

## License

MIT
