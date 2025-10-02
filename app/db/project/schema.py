from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.db.user.schema import UserBase, User


class ProjectBase(BaseModel):
    name: str
    description: str
    deadline: datetime



class ProjectCreate(ProjectBase):
    owner: int

class Project(ProjectBase):
    id: int
    owner: int
    creation_date: datetime

    class Config:
        from_orm = True
        from_attributes = True # orm mode
        arbitrary_types_allowed = True
