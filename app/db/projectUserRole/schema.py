from pydantic import BaseModel, ConfigDict


class ProjectUserRoleBase(BaseModel):
    rid: int
    pid: int
    uid: int
class ProjectUserRole(ProjectUserRoleBase):
    class Config:
        from_attributes = True  # orm mode
        arbitrary_types_allowed = True

