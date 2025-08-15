from fastapi import FastAPI
from src.core-routes import jobCRUD

app = FastAPI()
app.include_router(jobCRUD.router)
