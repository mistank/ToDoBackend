from functools import partial
from datetime import datetime

import pytz
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.csrf import csrf_protect
from app.db import permission
from app.routers import authentication, user, project, task, status, taskCategory, role
import uvicorn

app = FastAPI()

origins = [
    "http://localhost:5173",
    "http://localhost:4173",
    "https://mistank.github.io/ToDoFrontend/login",
    "https://mistank.github.io/ToDoFrontend",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Your existing routes and other configurations

@app.get("/openapi.json")
def get_openapi_spec():
    return app.openapi()

# Uključivanje rutera
app.include_router(authentication.router,tags=["authentication"])
app.include_router(user.router,tags=["user"])
app.include_router(project.router,tags=["project"])
app.include_router(task.router,tags=["task"])
app.include_router(status.router,tags=["status"])
app.include_router(taskCategory.router,tags=["taskCategory"])
app.include_router(role.router,tags=["role"])

#zastita od csrf napada kroz generisanje csrf tokena
# app.middleware("http")(partial(csrf_protect,exclude =["/login"]))


# Pokretanje aplikacije sa uvicorn serverom
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)