from fastapi import FastAPI
from routes import jobCRUD

app = FastAPI()
app.include_router(jobCRUD.router)
