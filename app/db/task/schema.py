from pydantic import BaseModel, ConfigDict
from app.db.taskCategory.schema import TaskCategory

class TaskBase(BaseModel):
    name: str
    description: str

class TaskCreate(TaskBase):
    deadline: str
    project: int
    taskCategory: int

class Task(TaskBase):
    class Config:
        from_attributes = True # orm mode
        arbitrary_types_allowed = True
