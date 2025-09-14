from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import ALLOW_ORIGINS
from src.core_api.routes import (
    master_node_route,
    job_route,
    node_routes,
    users_route,
    requests_route
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(job_route.router)
app.include_router(master_node_route.router)
app.include_router(node_routes.router)
app.include_router(users_route.router)
app.include_router(requests_route.router)