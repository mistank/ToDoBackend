from pydantic import BaseModel, ConfigDict

class TaskBase(BaseModel):
    name: str
    description: str

class TaskCreate(TaskBase):
    deadline: str
    project: int




class Task(TaskBase):
    class Config:
        from_attributes = True # orm mode
        arbitrary_types_allowed = True
