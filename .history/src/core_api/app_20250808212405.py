from fastapi import FastAPI
from ..models import jobInfo
from routes import jobCRUD # NOTE: Use relative paths (important for integration testing)

app = FastAPI

app.include_router(jobCRUD.router)
