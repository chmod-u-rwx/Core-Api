from fastapi import FastAPI
from src.core_api.routes import master_node_route
from src.core_api.routes import job_route

app = FastAPI()
app.include_router(job_route.router)
app.include_router(master_node_route.router)