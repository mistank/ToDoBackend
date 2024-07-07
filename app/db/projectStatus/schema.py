from pydantic import BaseModel

from app.db.project.schema import Project
from app.db.status.schema import Status


class ProjectStatusBase(BaseModel):
    status_id: int
    project_id: int

class ProjectStatusCreate(ProjectStatusBase):
    pass

class ProjectStatus(ProjectStatusBase):
    status: Status

    class Config:
        from_orm = True
        orm_mode = True
        from_attributes = True