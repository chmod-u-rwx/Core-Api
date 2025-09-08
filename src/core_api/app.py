from fastapi import FastAPI
from src.core_api.routes import master_node_route, job_route, node_routes, users_route

app = FastAPI()
app.include_router(job_route.router)
app.include_router(master_node_route.router)
app.include_router(node_routes.router)
app.include_router(users_route.router)