from fastapi import FastAPI
from src.core-apiroutes import jobCRUD

app = FastAPI()
app.include_router(jobCRUD.router)
