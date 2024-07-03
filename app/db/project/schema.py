from pydantic import BaseModel, ConfigDict

from app.db.user.schema import UserBase


class ProjectBase(BaseModel):
    name: str
    description: str
    deadline: str



class ProjectCreate(ProjectBase):
    owner: int

class Project(ProjectBase):
    id : int

    class Config:
        from_attributes = True # orm mode
        arbitrary_types_allowed = True
