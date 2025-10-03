from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.routers import authentication, user, project, task, status, taskCategory, role
from app.db.database import Base, engine
import uvicorn

Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = ["http://localhost:5173", "http://localhost:4173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "Accept"],
)

@app.get("/openapi.json")
def get_openapi_spec():
    return app.openapi()

app.include_router(authentication.router, tags=["authentication"])
app.include_router(user.router, tags=["user"])
app.include_router(project.router, tags=["project"])
app.include_router(task.router, tags=["task"])
app.include_router(status.router, tags=["status"])
app.include_router(taskCategory.router, tags=["taskCategory"])
app.include_router(role.router, tags=["role"])

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)