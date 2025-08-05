from fastapi import FastAPI
from .routes import sample # NOTE: Use relative paths (important for integration testing)

app = FastAPI(title="Core API")

app.include_router(sample.router)