from fastapi import FastAPI
from routes import job_crud

app = FastAPI()
app.include_router(job_crud.router)
