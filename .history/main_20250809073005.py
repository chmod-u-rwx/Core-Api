from fastapi import FastAPI
from srccore_api.routes import job_crud

app = FastAPI()
app.include_router(job_crud.router)
