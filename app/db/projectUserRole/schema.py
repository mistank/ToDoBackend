from pydantic import BaseModel, ConfigDict


class ProjectUserRoleBase(BaseModel):
    pid: int
    uid: int
class ProjectUserRole(ProjectUserRoleBase):
    rid: int

    class Config:
        from_attributes = True  # orm mode
        arbitrary_types_allowed = True

