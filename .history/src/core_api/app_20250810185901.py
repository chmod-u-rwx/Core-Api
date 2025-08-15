from fastapi import FastAPI
from .routes import job_crud # NOTE: Use relative paths (important for integration testing)

app = FastAPI()

app.include_router(job_crud.router)
