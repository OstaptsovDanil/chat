from fastapi import FastAPI

from src.database.base import SessionDep
from src.routers import routers

app = FastAPI()

for router in routers:
    app.include_router(router)
