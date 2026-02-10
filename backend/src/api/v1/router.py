from fastapi import APIRouter

from src.api.v1.endpoints import auth, jobs, models, molecules, projects

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(molecules.router, prefix="/molecules", tags=["molecules"])
api_router.include_router(models.router, prefix="/models", tags=["models"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
