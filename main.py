from fastapi import FastAPI
from core_api.db.database import setup_database

app = FastAPI()
setup_database()