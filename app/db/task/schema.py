from datetime import datetime
from datetime import date
from pydantic import BaseModel

from app.db.project.schema import Project
from app.db.status.schema import Status
from app.db.taskCategory.schema import TaskCategory

class TaskBase(BaseModel):
    name: str
    description: str
    deadline: datetime
    project_id: int
    taskCategory_id: int
    status_id: int

class TaskCreate(TaskBase):
    pass


class Task(TaskBase):
    id: int  # Dodato da se uključi ID zadatka
    deadline: datetime
    project: Project
    taskCategory: TaskCategory
    status: Status

    class Config:
        from_orm = True
        from_attributes = True  # Ispravljeno sa orm_mode na from_attributes
        orm_mode = True  # Ispravljeno sa from_attributes na orm_mode
        arbitrary_types_allowed = True
        # json_encoders = {
        #     datetime: lambda v: v.strftime('%d-%m-%Y')
        # }
