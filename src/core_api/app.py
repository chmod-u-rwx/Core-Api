from fastapi import FastAPI
from src.core_api.routes import job_route

app = FastAPI()
app.include_router(job_route.router)
