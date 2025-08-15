from fastapi import FastAPI
from ..models.job_info import jobModel
from ..models import job_info
from src.core_api.routes import job_crud # NOTE: Use relative paths (important for integration testing)

app = FastAPI

app.include_router(job_crud.router)
