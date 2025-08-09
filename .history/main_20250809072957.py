from fastapi import FastAPI
from coreroutes import job_crud

app = FastAPI()
app.include_router(job_crud.router)
