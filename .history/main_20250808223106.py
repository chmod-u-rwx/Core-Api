from fastapi import FastAPI
from src.coreeroutes import jobCRUD

app = FastAPI()
app.include_router(jobCRUD.router)
